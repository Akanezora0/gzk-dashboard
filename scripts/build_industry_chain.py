#!/usr/bin/env python3
"""短链条分析 · 产业链分析：把刘洁交付的产业链展示页（单文件 HTML，内嵌 gzip 数据）
整理为 Dashboard 读取的静态 JSON。

用法：
  python3 scripts/build_industry_chain.py <industry-chain-cards-YYYYMMDD.html> [--out snapshot/public/industry-chain/v1]

输出（均为紧凑 JSON）：
  atlas.json          证据全景：技术大类与技术点、7 家精选主体、精选产品、经济指标摘要、基金编号
  evolution.json      产品代际演进
  analysis.json       链条分析索引：全部产品（技术点、提供主体）与主体摘要（招聘、经营、公告覆盖）
  products/NNN.json   产品简介分片（每片 400 项）
  value/XX.json       主体经营指标分片（按主体编号末两位十六进制分片）
  tech-patents.json   各技术点专利样例与匹配总量
  company/X.json      “从企业出发”所需的主体专利样例与已归档企业关系（按编号末位分 16 片）
只做字段整理与分片，不重新计算原数据中的统计值。
"""
import argparse, base64, gzip, json, os, re, sys
from collections import defaultdict

VISIBLE = ['cmp_a92a7a82a356224ae15b', 'cmp_fe9884ac1201b19a2c43', 'cmp_26ee22c3f4ab573dd16d', 'cmp_5f07f35f9dea807bd2b5',
           'cmp_9ffee8a52d757b830aa9', 'cmp_827c3fa4b6824b65e5fb', 'cmp_652c5cdfe219a112458f']
CATEGORY_DESC = {
    '基础模型与架构': '模型如何表示和组织信息：从 Transformer、注意力机制到多模态、扩散与混合专家架构。',
    '模型训练、适配与推理': '模型如何学习、对齐与完成任务：预训练、微调、反馈学习、推理和上下文管理。',
    'AI算力与运行优化': '支撑模型运行的硬件、计算系统与效率技术，涵盖芯片、集群、并行调度和推理加速。',
    'AI云与平台服务': '面向开发与交付的云端能力，包括 GPU 云、模型训练运维、模型服务和智能体开发平台。',
    '知识增强与AI应用': '将模型能力用于检索、工具调用及具体任务，包括智能体、代码、视觉、语音与内容生成。',
    '数据与知识服务': '构建和管理模型所需的数据与知识，包括训练数据、数据治理、标注、知识图谱和向量数据库。',
    '模型评测与安全': '衡量模型能力与可靠性，识别攻击、隐私和可追溯风险，涵盖偏好评测、幻觉、防护和水印。'}
ECON_KEEP = ['id', 'metricId', 'metric', 'name', 'standardName', 'value', 'displayValue', 'textValue', 'unit', 'currency', 'comparator',
             'originalValue', 'originalUnit', 'originalCurrency', 'year', 'period', 'scope', 'scopeClass', 'reportingScope',
             'reportingEntity', 'entityRelation', 'category', 'categoryId', 'isRevenue', 'displayEligible', 'eligibleForHeadline',
             'valueType', 'observationKey', 'sourceTitle', 'sourceUrl', 'sourceLocator', 'sourceDate', 'sourceId', 'sources', 'metricLabel']
PATENT_KEEP = ['patentKey', 'title', 'applicationNumber', 'publicationNumber', 'applicationDate', 'publicationDate', 'applicants',
               'companyId', 'matchType', 'matchTypeName', 'abstract', 'technologyIds']


def load_vfs(html_path):
    html = open(html_path, encoding='utf-8').read()
    raw = re.search(r'id="chain-embedded-data">(.*?)</script>', html, re.S)
    if not raw:
        sys.exit('未找到内嵌数据 chain-embedded-data')
    files = {}
    for key, value in json.loads(raw.group(1)).items():
        if isinstance(value, list) and value and isinstance(value[0], str):
            blob = base64.b64decode(value[0])
            try:
                blob = gzip.decompress(blob)
            except OSError:
                pass
            files[key] = json.loads(blob)
        else:
            files[key] = value
    return files


def pick(row, keys):
    return {k: row[k] for k in keys if k in row and row[k] not in (None, '', [], {})}


def clip(text, n):
    text = str(text or '').strip()
    return text if len(text) <= n else text[:n - 1] + '…'


def intro(product, applications):
    app = applications.get(product['id']) or {}
    scen = '；'.join(x if isinstance(x, str) else (x.get('scenario') or x.get('text') or x.get('description') or '') for x in app.get('scenarios') or [])
    if scen:
        return clip(scen, 200)
    parts = [re.split(r'产品边界[：:]', str(x))[0].strip() for x in product.get('functions') or []]
    return clip('；'.join(p for p in parts if p), 200)


def write(out, name, data):
    path = os.path.join(out, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    return os.path.getsize(path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('html')
    ap.add_argument('--out', default='snapshot/public/industry-chain/v1')
    args = ap.parse_args()
    fs = load_vfs(args.html)
    boot, manifest = fs['boot.json'], fs['manifest.json']
    # 合并启动分片（与原页面 readBoot 相同的规则）
    for part in manifest.get('bootParts', []):
        records = fs[part['path']]['records']
        target = part['target']
        if target == 'companies': boot['companies']['companies'].extend(records)
        elif target == 'products': boot['graph']['products'].extend(records)
        elif target == 'valueCompanies': boot['chainValue']['companyMetrics'].update(records)
        else: boot['economicDisplay']['companies'].update(records)
    companies = {c['id']: c for c in boot['companies']['companies']}
    products = {p['id']: p for p in boot['graph']['products']}
    # 产品详情分片补充功能说明与来源
    for key, path in manifest['chunks'].items():
        pack = fs[path]
        for p in pack.get('products', []):
            products[p['id']].update(p)
        for c in pack.get('companies', []):
            companies[c['id']].update(c)
    techs = boot['graph']['technologies']
    summary = boot['summary']
    applications = boot['chainValue'].get('productApplications', {})
    featured_rows = [dict(f, companyId=f.get('companyId') or f.get('id')) for f in boot['featured']['entities']]
    featured = [f for f in featured_rows if f['companyId'] in VISIBLE]
    out = args.out
    sizes = {}

    # 1. atlas.json
    feat_products = set()
    for f in featured:
        ids = [p['id'] if isinstance(p, dict) else p for p in f.get('products', [])]
        if not ids: ids = companies[f['companyId']].get('productIds', [])
        feat_products.update(i for i in ids if i in products)
    econ_display = boot['economicDisplay']['companies']
    metric = {m['id']: m for m in summary['metrics']}
    atlas = {
        'asOf': summary.get('asOf'),
        'counts': {'companies': metric['companies']['value'], 'products': metric['products']['value'],
                   'labeledPatents': metric['labeledPatents']['value'], 'annualValues': metric['annualValues']['value'],
                   'technologies': len(techs)},
        'categories': [{'name': c['name'], 'count': c['count'], 'description': CATEGORY_DESC.get(c['name'], '')} for c in summary['technologyCategories']],
        'technologies': [pick(t, ['id', 'name', 'level1', 'level2', 'definition', 'patents', 'products', 'companies']) for t in techs],
        'featured': [{'companyId': f['companyId'], 'shortName': f.get('shortName'), 'description': f.get('description'),
                      'products': [p['id'] if isinstance(p, dict) else p for p in f.get('products', [])], 'sources': f.get('sources', [])} for f in featured],
        'companies': {cid: {**pick(companies[cid], ['id', 'name', 'category', 'entityScope', 'businessSummary', 'productIds', 'technologyIds', 'revenueSeries']),
                            'coverage': pick(companies[cid].get('coverage', {}), ['products', 'patents', 'labeledPatents', 'jobsDeduplicated'])}
                      for cid in VISIBLE},
        'products': {pid: {**pick(products[pid], ['id', 'name', 'companyIds', 'technologyIds', 'sources']), 'intro': intro(products[pid], applications)} for pid in feat_products},
        'economics': {cid: {'note': econ_display[cid].get('note'), 'preferredIndicatorId': econ_display[cid].get('preferredIndicatorId'),
                            'indicators': [pick(r, ECON_KEEP) for r in econ_display[cid].get('indicators', [])]} for cid in VISIBLE if cid in econ_display},
        'funding': [pick(r, ['companyId', 'shortName', 'projectNumbers', 'papers', 'relationship']) for r in boot['fundLinks']['companies'] if r['companyId'] in VISIBLE],
    }
    for r in atlas['funding']:
        r['papers'] = [pick(p, ['paper', 'year', 'projectNumbers', 'relationship', 'sourceUrl', 'quote', 'location']) for p in r.get('papers', [])]
    sizes['atlas.json'] = write(out, 'atlas.json', atlas)

    # 2. evolution.json
    evo = boot['productEvolution']
    names = {}
    for s in evo['series']:
        for cid in s.get('companyIds', []):
            f = next((x for x in featured_rows if x['companyId'] == cid), None)
            names[cid] = (f or {}).get('shortName') or companies.get(cid, {}).get('name', cid)
    sizes['evolution.json'] = write(out, 'evolution.json', {'series': evo['series'], 'sources': evo.get('sources', {}), 'names': names})

    # 3. analysis.json + product intro chunks
    ordered = sorted(products.values(), key=lambda p: p['id'])
    chunk_of = {}
    for i in range(0, len(ordered), 400):
        part = ordered[i:i + 400]
        n = f'{i // 400:03d}'
        sizes[f'products/{n}.json'] = write(out, f'products/{n}.json', {p['id']: intro(p, applications) for p in part})
        for p in part: chunk_of[p['id']] = n
    value = boot['chainValue']['companyMetrics']
    referenced = set(VISIBLE)
    for p in ordered: referenced.update(p.get('companyIds', []))
    case_years = {}
    for c in boot['caseData']['cases']:
        for cid in c.get('subjectIds', []):
            case_years[cid] = [{'year': r['year'], 'value': r.get('dedupRecords', r.get('dedupCandidateRecords'))} for r in c.get('recruitmentYears', [])]
    short = {f['companyId']: f.get('shortName') for f in featured_rows}
    comp_rows = {}
    for cid in sorted(referenced):
        c = companies.get(cid)
        if not c: continue
        v = value.get(cid, {})
        row = {'name': c['name'], 'category': c.get('category'), 'scope': c.get('entityScope'),
               'jobs': (c.get('coverage') or {}).get('jobsDeduplicated') or 0,
               'labeledPatents': (c.get('coverage') or {}).get('labeledPatents') or 0,
               'products': c.get('productIds', [])}
        if short.get(cid): row['short'] = short[cid]
        if v.get('annualCount') or cid in econ_display: row['value'] = 1
        mc = v.get('metricCounts') or {}
        if mc.get('revenue'): row['rev'] = 1
        if mc.get('employees') or mc.get('rd_employees'): row['staff'] = 1
        proc = (v.get('procurement') or {}).get('notices')
        if proc: row['notices'] = proc
        if cid in case_years: row['years'] = case_years[cid]
        comp_rows[cid] = row
    comp_ids = list(comp_rows)
    comp_index = {cid: i for i, cid in enumerate(comp_ids)}
    analysis = {
        # 产品：[编号, 名称, 提供主体序号, 技术点编号（去掉 T 前缀）, 简介分片]
        'products': [[p['id'], p['name'], [comp_index[c] for c in p.get('companyIds', []) if c in comp_index],
                      [int(t[1:]) for t in p.get('technologyIds', []) if re.fullmatch(r'T\d+', t)], int(chunk_of[p['id']])] for p in ordered],
        'companyIds': comp_ids,
        'companies': [{k: v for k, v in comp_rows[cid].items() if k != 'products'} for cid in comp_ids],
        'industries': {pid: a.get('industries', []) for pid, a in applications.items()},
    }
    sizes['analysis.json'] = write(out, 'analysis.json', analysis)

    # 4. value/X.json：经营指标（经济展示指标 + 年度指标）
    by_part = defaultdict(dict)
    sources = boot['chainValue'].get('sources', {})
    for key, path in manifest['chunks'].items():
        if key.startswith('value:'):
            pack = fs[path]
            sources.update(pack.get('valueSources', {}))
            for cid, m in pack['companyMetrics'].items():
                value.setdefault(cid, {}).update(m)
    for cid in comp_rows:
        annual = [pick(r, ECON_KEEP) for r in (value.get(cid) or {}).get('annual', [])]
        published = [pick(r, ECON_KEEP) for r in econ_display.get(cid, {}).get('indicators', [])]
        rev = companies[cid].get('revenueSeries') or []
        if not (annual or published or rev): continue
        for r in annual:
            if r.get('sourceId') in sources and not r.get('sourceUrl'):
                s = sources[r['sourceId']]
                r['sourceTitle'] = r.get('sourceTitle') or s.get('title') or s.get('sourceTitle')
                r['sourceUrl'] = s.get('url') or s.get('sourceUrl')
                r['sourceLocator'] = r.get('sourceLocator') or s.get('location') or s.get('sourceLocator')
        by_part[cid[-2:]][cid] = {'annual': annual, 'indicators': published, 'revenueSeries': rev,
                                  'preferred': econ_display.get(cid, {}).get('preferredIndicatorId')}
    for k, rows in by_part.items():
        sizes[f'value/{k}.json'] = write(out, f'value/{k}.json', rows)

    # 5. tech-patents.json
    analysis_src = fs['chain-analysis.json']
    tp = {}
    for tid, pack in analysis_src['technologyPatents'].items():
        tp[tid] = {'total': pack.get('totalPatents'), 'patents': [dict(pick(p, PATENT_KEEP), abstract=clip(p.get('abstract'), 260),
                                                                           patentKey=p.get('patentKey') or p.get('patent_key'))
                                                                      for p in pack.get('patents', [])[:6]]}
    sizes['tech-patents.json'] = write(out, 'tech-patents.json', tp)

    # 6. company/X.json：主体专利样例 + 已归档企业关系
    relations = dict(analysis_src['companyRelations'])
    for key, path in manifest.get('analysisChunks', {}).items():
        relations.update(fs[path].get('companyRelations', {}))
    comp_part = defaultdict(dict)
    for cid in comp_rows:
        cp = analysis_src['companyPatents'].get(cid) or {}
        rel = relations.get(cid) or {}
        patents = [dict(pick(p, PATENT_KEEP), abstract=clip(p.get('abstract'), 260), patentKey=p.get('patentKey') or p.get('patent_key'))
                   for p in cp.get('patents', [])[:6]]
        related = [{'name': r.get('name') or r.get('companyName') or r.get('relatedName'), 'relation': r.get('relation') or r.get('relationshipType'),
                    'companyId': r.get('companyId') or r.get('relatedCompanyId')} for r in rel.get('related', [])[:6]]
        if patents or related:
            comp_part[cid[-1]][cid] = {'patents': patents, 'labeled': cp.get('labeledPatents'), 'related': related,
                                       'relatedTotal': rel.get('totalCount', len(related))}
    for k, rows in comp_part.items():
        sizes[f'company/{k}.json'] = write(out, f'company/{k}.json', rows)

    total = sum(sizes.values())
    print(json.dumps({'files': len(sizes), 'bytes': total, 'largest': sorted(sizes.items(), key=lambda x: -x[1])[:6]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
