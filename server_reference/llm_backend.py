"""Serve a separate LLM preview without modifying any producer or database."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import html
import re
import json
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from gzk.paths import path, data_root

CONFIG = json.loads(Path(__file__).with_name('config.json').read_text())
NAMES = {
    'nsfc_fund': '基金项目', 'nsfc_paper': '基金资助论文',
    'cnki_paper': '中文期刊文献', 'legacy_patent': '专利',
    'legacy_software': '软件著作权', 'legacy_product': '载体产品',
    'legacy_news': '产业新闻', 'legacy_policy': '既有政策',
    'ai_policy': 'AI政策文本', 'ai_company': '企业候选', 'ai_report': '行业报告',
}
NOTES = {
    'nsfc_fund': '项目批准年1986–2019；近期项目缺口明显。零命中不代表没有LLM基金。',
    'nsfc_paper': '资助成果来源，不是领域全部论文；与中文文献库尚未跨源消歧。',
    'cnki_paper': '按来源URL识别，含应用、治理研究与简讯；未作专家相关性审核。',
    'legacy_patent': '从低空预选交付复用的候选，不代表全国或完整LLM专利集合。',
    'legacy_software': '软件登记词命中，不证明采用了对应技术。',
    'legacy_product': '低空载体产品交付；现代语言模型产品需另补。',
    'legacy_news': '原低空交付范围；逻辑记录计数，转载尚未归并。',
    'legacy_policy': '原低空交付；与新政策库尚未跨源归并。',
    'ai_policy': '标题或正文命中；包括通知及团体规定，非全部正式行政政策。',
    'ai_company': '主要命中交付方的分类依据；不是已确认的LLM企业数量。',
    'ai_report': '按文件SHA归并；检索文件名及已提取的前三页，不是全文审核。',
}


def read_json(file: Path):
    return json.loads(file.read_text(encoding='utf-8'))


def sha(file: Path):
    return hashlib.sha256(file.read_bytes()).hexdigest()


def safe_data_file(value: str) -> Path:
    p = Path(value).resolve()
    if not p.is_relative_to(data_root().resolve()) or not p.is_file():
        raise HTTPException(409, '产物路径不可用或超出项目数据目录')
    return p


def db_connect(file: Path):
    db = sqlite3.connect(file.resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA query_only=ON')
    return db


@lru_cache(maxsize=1)
def fixed_assets():
    root = path(CONFIG['snapshot'])
    receipt = read_json(root / 'receipt.json')
    if receipt.get('status') != 'complete' or receipt.get('sample_only'):
        raise RuntimeError('Only a completed, full-scan candidate snapshot can be displayed')
    for filename, key in [('summary.json', 'summary_sha256'), ('dashboard.json', 'dashboard_sha256')]:
        if sha(root / filename) != receipt[key]:
            raise RuntimeError('Snapshot receipt mismatch: ' + filename)
    summary, domain = read_json(root / 'summary.json'), read_json(root / 'dashboard.json')
    tree = read_json(path(CONFIG.get('domain_tree', CONFIG['tree'])))
    if tree['keyword_sha256'] != domain['keyword_sha256']:
        raise RuntimeError('Tree and candidate snapshot use different keywords')
    policy = read_json(path(CONFIG['policy']) / 'exports/quality.json')
    milestones = read_json(path(CONFIG['milestones']))
    milestone_receipt = read_json(path(CONFIG['milestones']).with_name('receipt.json'))
    if sha(path(CONFIG['milestones'])) != milestone_receipt['milestones_sha256']:
        raise RuntimeError('Milestone receipt mismatch')
    if milestones.get('keyword_version') not in (tree['keyword_version'], None):
        raise RuntimeError('Milestone vocabulary version differs from the accepted tree')
    return summary, domain, tree, policy, milestones


def foundation_patent_source():
    """Read the accepted cross-domain receipt; do not scan or mutate its database."""
    name = CONFIG.get('foundation_patent_receipt')
    if not name:
        return None
    file = path(name)
    if sha(file) != CONFIG.get('foundation_patent_sha256'):
        raise HTTPException(409, '全国专利交付回执校验不一致')
    receipt = read_json(file)
    counts = receipt.get('summary', {})
    keys = ('scanned', 'accepted', 'rejected', 'unique_publication_ids', 'duplicate_publication_observations')
    valid = all(type(counts.get(k)) is int and counts[k] >= 0 for k in keys)
    if (not valid or receipt.get('database_loaded') is not True or receipt.get('sample_only') is not False
            or receipt.get('tier') != 'base'
            or counts['scanned'] != counts['accepted'] + counts['rejected']
            or counts['accepted'] != counts['unique_publication_ids'] + counts['duplicate_publication_observations']):
        raise HTTPException(409, '全国专利交付尚未通过数量对账')
    return dict(id='cn_patent_base', name='全国专利公开文献', kind='专利',
                count=counts['unique_publication_ids'], unit='条', scope='跨领域 · 中国专利',
                status='已规范入库', source=str(Path(name).parent), evidence=name,
                source_sha256=CONFIG['foundation_patent_sha256'], verified_at='2026-09-21',
                note='按公开标识归并；申请、授权及同族不是同一计量单位，未外推为完整全国覆盖。')


def overview(summary, policy):
    """Counts come from existing full-scan receipts, never from UI constants."""
    selected = [
        ('nsfc_paper', 'papers.csv', '基金资助论文条目', '论文', '篇/条', '跨领域 · NSFC', '已接收原件', '期刊与会议成果；与其他论文来源可能重叠。'),
        ('cnki_paper', 'ods_papers_00基本信息表.csv', '中文期刊文献条目', '论文', '条', '跨领域 · 中文期刊', '已接收原件', '总目录与57学科表不重复相加。'),
        ('legacy_software', '软件著作.csv', '软件著作权', '软著', '条', '低空预选交付', '已接收原件', '登记信息；不是全行业软著库。'),
        ('nsfc_fund', 'projs.csv', '基金项目', '基金', '项', '跨领域 · NSFC', '已接收原件', '批准年1986–2019，2020以后缺失。'),
        ('legacy_patent', '专利文件.csv', '专利基础记录', '专利', '条', '低空预选交付', '已接收原件', '原始记录与规范库加载量分开；引文待规范化。'),
        ('legacy_news', '产业新闻.csv', '产业新闻', '新闻', '条', '低空预选交付', '已接收原件', '64,332为逻辑记录；不采用旧物理文本行数。'),
        ('ai_company', '补充-ai_companies_master_20260907_1707.xlsx', 'AI企业候选', '主体', '家/条', 'AI候选交付', '已接收原件', '企业名与来源ID唯一，领域归属待审核。'),
        ('legacy_policy', '低空经济政策_13733条_原始数据csv.csv', '既有政策文献', '政策', '篇/条', '低空交付', '已接收原件', '与AI政策库未跨源去重。'),
        ('legacy_product', '低空载体产品.csv', '载体产品', '产品', '条', '低空交付', '已接收原件', '无人机等载体产品，不是LLM产品数。'),
        ('ai_report', 'files.json', 'AI与跨行业报告文件', '报告', '份', 'AI及跨行业交付', '已验收文件', 'PDF文件实例数，含重复副本；不是独立报告数。'),
    ]
    datasets = []
    for namespace, basename, name, kind, unit, scope, status, note in selected:
        row = next(x for x in summary['source_statistics'] if x['namespace'] == namespace and Path(x['path']).name == basename)
        datasets.append(dict(id=namespace, name=name, kind=kind, count=row['eligible_rows'], unit=unit,
                             scope=scope, status=status, note=note, source=row['path'], verified_at='2026-09-17',
                             evidence=CONFIG['snapshot'] + '/summary.json', source_sha256=row['sha256']))
    datasets += [dict(id='policy_central', name='AI中央政策文本', kind='政策', count=policy['central_records'], unit='条', scope='中央交付', status='已规范入库', source=CONFIG['policy'], note='来源内记录；并非全部中央政策。'),
                 dict(id='policy_local', name='AI地方政策文本', kind='政策', count=policy['local_unique_urls'], unit='篇', scope='31省级地区', status='已规范入库', source=CONFIG['policy'], note='按原文URL去重；联合发文的地区记录另计。')]
    legacy = read_json(path(CONFIG['legacy_inventory']))
    for filename, name, kind, unit in [('专利申请主体.csv', '专利申请主体', '主体', '条'),
                                       ('科研单位.csv', '科研单位', '主体', '家/条'),
                                       ('产品厂家单位.csv', '产品厂商', '主体', '家/条'),
                                       ('科研项目.csv', '专题科研项目', '基金', '项/条')]:
        row = next(x for x in legacy if Path(x['path']).name == filename)
        datasets.append(dict(id=filename[:-4], name=name, kind=kind, count=row['rows'], unit=unit,
                             scope='低空交付', status='已接收原件', source=row['path'],
                             evidence=CONFIG['legacy_inventory'], verified_at=row['counted_at'],
                             note='来源内原始条目；与其他主体/基金来源可能重叠。'))
    national = foundation_patent_source()
    if national:
        datasets.append(national)
    report_metrics = CONFIG.get('legacy_report_metrics')
    if report_metrics:
        file = path(report_metrics)
        if sha(file) != CONFIG.get('legacy_report_metrics_sha256'):
            raise HTTPException(409, '既有行业报告指标校验不一致')
        report = read_json(file)['metrics']['industry_report_pdf']
        if type(report['value']) is not int or report['value'] < 0:
            raise HTTPException(409, '既有行业报告数量无效')
        datasets.append(dict(id='legacy_industry_report', name='行业报告资料', kind='报告',
                             count=report['value'], unit='份', scope='低空专题报告交付', status='已接收原件',
                             source='data/raw/low_altitude/reports_dai', evidence=report_metrics,
                             source_sha256=CONFIG['legacy_report_metrics_sha256'], verified_at='2026-09-22',
                             note='历史MD5口径：reports_dai及delivery_0413/低空经济资料的465个PDF实例去重为395；含少量政策等材料，未重新全文核验。'))
    return dict(datasets=datasets, headline=[dict(label=x['name'], value=x['count'], unit=x['unit'], note=x['scope']) for x in datasets[:4]],
                dataset_count=len(datasets), type_count=len({x['kind'] for x in datasets}),
                source_date='2026-09-21' if national else '2026-09-17', scope_note='项目已持有的多领域资产，兼含领域交付；不同来源、观察单位与处理层次不直接相加为唯一实体总量。')


def survey_state(tree):
    folder = path(CONFIG['survey_batch'])
    index = read_json(folder / 'survey_index.json')
    status = read_json(folder / 'status.json')
    if index['keyword_sha256'] != tree['keyword_sha256'] or index['technology_tree']['sha256'] != sha(path(CONFIG['tree'])):
        raise HTTPException(409, '双线综述与当前词表版本不一致')
    allowed = ['topic_id', 'route', 'status', 'ready_for_dashboard', 'actual_references', 'reference_coverage', 'source_version', 'semantic_check_status', 'expert_reviewed']
    entries = [{k: v for k, v in x.items() if k in allowed} for x in index['entries']]
    counter = Counter(x['status'] for x in entries)
    run = status.get('status', 'unknown')
    note = {'budget_paused': '额度保护已暂停：余额查询未通过或达到保护阈值，请查看运行入口。',
            'running': '后台生成中，页面每60秒读取最新状态。', 'completed': '本轮队列已结束；逐项覆盖与失败状态单独列示。'}.get(run, '按最新运行回执显示。')
    return dict(entries=entries, batch_id=index['batch_id'], updated_at=index['updated_at'], run_status=run, run_note=note,
                counts=dict(total=len(entries), ready=sum(x['ready_for_dashboard'] for x in entries), coverage=counter['coverage_pending'],
                            pending=counter['pending'], failed=counter['failed'] + counter['blocked'], by_status=dict(counter)),
                expert_reviewed=False)


@lru_cache(maxsize=1)
def explicit_years():
    with db_connect(path(CONFIG['snapshot']) / 'candidates.sqlite3') as db:
        return [dict(x) for x in db.execute('SELECT namespace,year,SUM(ai) AS ai_candidates,SUM(llm_core) AS llm_explicit_candidates,SUM(llm_contextual) AS llm_context_candidates FROM entity GROUP BY namespace,year ORDER BY namespace,year')]


def bootstrap():
    summary, domain, domain_tree, policy, old_milestones = fixed_assets()
    tree = read_json(path(CONFIG['tree']))
    study = study_views()
    milestones = dict(old_milestones, milestones=study['milestones'])
    metrics = [dict(m, name=NAMES[m['namespace']], note=NOTES[m['namespace']]) for m in domain['metrics']]
    return dict(updated_at=datetime.now(timezone.utc).isoformat(), release=CONFIG['release'],
                overview=overview(summary, policy), inventory=inventory_state(overview(summary, policy)),
                domain=dict(metrics=metrics, years=explicit_years(), topic_counts=domain['technology_tree_counts'],
                            funnel=domain['fund_paper_funnel'], version=summary['batch'], source_date=summary['generated_at'],
                            note='来源内规则候选，明确LLM与前史关联分开；未完成跨源消歧及专家审核。'),
                tree=tree, survey=survey_state(tree), milestones=milestones['milestones'],
                study=study, chronology=chronology_views(), domain_tree=domain_tree,
                milestone_scope=milestones.get('scope_note'),
                policy=dict(central_count=policy['central_records'], local_unique_count=policy['local_unique_urls'],
                            region_count=policy['local_regions'], region_records=policy['local_region_observations'],
                            by_region=[dict(name=k, count=v) for k, v in sorted(policy['region_counts'].items(), key=lambda kv: -kv[1])],
                            by_year=[dict(year=int(k), count=v) for k, v in sorted(policy['local_years'].items()) if k.isdigit()],
                            note='地方按原文链接去重；联合发文分别计入地区。2026仅标年份的21条保留，截止日未核准。'),
                provenance=dict(snapshot=summary['batch'], keyword_version=tree['keyword_version'], keyword_sha256=tree['keyword_sha256'],
                                counts_checked_at='2026-09-17', survey_refresh_seconds=60, milestone_version=milestones.get('schema_version'), domain_keyword_sha256=domain_tree['keyword_sha256'],
                                publication='独立LLM预览，不改写上游冻结产物的发布标记', expert_reviewed=False))


def survey_article(topic_id: str, route: str):
    index = read_json(path(CONFIG['survey_batch']) / 'survey_index.json')
    entry = next((e for e in index['entries'] if e['topic_id'] == topic_id and e['route'] == route), None)
    if not entry:
        raise HTTPException(404, '未找到该技术主题或路线')
    if not entry.get('dashboard_bundle_path'):
        raise HTTPException(409, '该路线尚无可阅读成稿')
    if not entry.get('ready_for_dashboard'):
        raise HTTPException(409, '该路线尚未达到完整综述的展示条件；背景稿和覆盖待补稿保留在批次入口')
    bundle_file = safe_data_file(entry['dashboard_bundle_path'])
    if sha(bundle_file) != entry.get('dashboard_bundle_sha256'):
        raise HTTPException(409, '展示包校验不一致，等待生产器完成写入')
    bundle = read_json(bundle_file)
    if bundle['topic_id'] != topic_id or bundle['route'] != route:
        raise HTTPException(409, '展示包主题或路线不一致')
    article_path = safe_data_file(entry.get('article_path') or entry.get('background_article_path'))
    article_sha = bundle.get('article_sha256') or bundle.get('background_article_sha256')
    if sha(article_path) != article_sha:
        raise HTTPException(409, '正文校验不一致')
    references_path = safe_data_file(entry['references_path'])
    if sha(references_path) != bundle.get('references_sha256'):
        raise HTTPException(409, '书目校验不一致')
    timeline = bundle.get('timeline', {})
    if isinstance(timeline, dict) and timeline.get('path'):
        f = safe_data_file(timeline['path'])
        timeline = read_json(f) if sha(f) == timeline.get('sha256') else {'status': 'timeline_integrity_mismatch'}
    return dict(title=bundle['title'], content_md=bundle['content_md'], references=bundle['references'],
                timeline=timeline, sections=bundle.get('sections', []), source_version=entry.get('source_version'),
                coverage=entry.get('reference_coverage', {}), status=entry['status'], ready_for_dashboard=entry['ready_for_dashboard'],
                expert_reviewed=False, total_references=entry['actual_references'], article_sha256=article_sha)


app = FastAPI(title='基础研究支撑经济发展 · LLM展示API', version='1.0')


@app.get('/api/health')
def health():
    return dict(status='ok', domain='llm', release=CONFIG['release'])


@app.get('/api/llm/bootstrap')
def get_bootstrap():
    return bootstrap()


@app.get('/api/llm/survey/{topic_id}/{route}')
def get_survey(topic_id: str, route: str):
    return survey_article(topic_id, route)


@lru_cache(maxsize=1)
def research_views():
    file = path(CONFIG['research_views'])
    receipt = read_json(file.with_name('receipt.json'))
    if receipt.get('status') != 'verified' or sha(file) != receipt['research_views_sha256']:
        raise HTTPException(409, '研究图表与证据图快照校验失败')
    result = read_json(file)
    if result['keyword_sha256'] != fixed_assets()[2]['keyword_sha256']:
        raise HTTPException(409, '研究图表词表版本不一致')
    source_receipt = read_json(path(CONFIG['snapshot']) / 'receipt.json')
    if result['source_database_sha256'] != source_receipt['database_sha256']:
        raise HTTPException(409, '研究图表数据快照版本不一致')
    return result


@lru_cache(maxsize=1)
def study_views():
    file = path(CONFIG['study_views'])
    receipt = read_json(file.with_name('receipt.json'))
    if receipt.get('status') != 'verified' or sha(file) != receipt['study_views_sha256']:
        raise HTTPException(409, '研究展示回执不一致')
    result = read_json(file)
    if result['keyword_sha256'] != read_json(path(CONFIG['tree']))['keyword_sha256']:
        raise HTTPException(409, '展示词典版本不一致')
    for key in ('research_views', 'milestones', 'tree'):
        if sha(path(CONFIG[key])) != receipt['input_sha256'][key]:
            raise HTTPException(409, '研究展示输入版本不一致：' + key)
    return result


@lru_cache(maxsize=1)
def chronology_views():
    file = path(CONFIG['chronology'])
    receipt = read_json(file.with_name('chronology_receipt.json'))
    if receipt.get('status') != 'verified' or sha(file) != receipt['chronology_sha256']:
        raise HTTPException(409, '技术时间图回执不一致')
    result = read_json(file)
    for key in ('tree', 'study_views'):
        if sha(path(CONFIG[key])) != receipt['input_sha256'][key]:
            raise HTTPException(409, '技术时间图输入版本不一致：' + key)
    if result['keyword_sha256'] != read_json(path(CONFIG['tree']))['keyword_sha256']:
        raise HTTPException(409, '技术时间图词典版本不一致')
    return result


@app.get('/api/llm/study')
def get_study():
    return study_views()


@lru_cache(maxsize=1)
def inventory_artifact():
    folder = path(CONFIG['inventory'])
    receipt = read_json(folder / 'receipt.json')
    if receipt.get('status') != 'verified' or sha(folder / 'comparison.json') != receipt['comparison_sha256'] or sha(folder / 'snapshot.json') != receipt['snapshot_sha256']:
        raise HTTPException(409, '数据总览快照校验未通过')
    return read_json(folder / 'comparison.json')


def inventory_state(current):
    result = inventory_artifact()
    live = {r['id']:(r['count'],r['unit'],r['scope']) for r in current['datasets']}
    fixed = {r['id']:(r['count'],r['unit'],r['scope']) for r in result['datasets']}
    if live != fixed or result['current_release'] != CONFIG['release']:
        raise HTTPException(409, '数据总览比较快照与当前来源不一致')
    return result


def batch_coverage(batch):
    # Shared storage alone does not establish cross-domain research coverage.
    if (batch.get('source') == 'china_patent_delivery' and batch.get('domain') == 'shared'
            and batch.get('batch') == 'cn_patents_20260921_v1'):
        return 'foundation'
    if batch.get('domain') in ('llm', 'low_altitude') or batch.get('source') in {
            'listed_ai', 'patent_ai', 'policy_ai', 'reports_ai', 'crossref_llm'}:
        return 'domain'
    return 'unknown'


@app.get('/api/llm/catalog-activity')
def catalog_activity():
    # Read small intake manifests, never scan raw assets or infer new records from a poll.
    names = {'reports_ai':'AI及跨行业报告', 'reports_2026':'2026行业报告',
      'listed_ai':'上市公司AI资料', 'patent_ai':'AI专利统计资料', 'policy_ai':'AI政策统计资料',
      'yaoyuan_central_policy':'中央政策文本', 'pkulaw_local_policy':'地方政策文本',
      'crossref_llm':'Crossref论文样本', 'crossref_funded':'Crossref资助论文样本',
      'arxiv':'arXiv文献样本', 'github':'GitHub仓库样本', 'hf_models':'Hugging Face模型样本',
      'hf_datasets':'Hugging Face数据集样本', 'nsf':'NSF项目样本',
      'survey_public_sources':'公开文献与综述证据', 'acl_arxiv_survey':'RAG公开文献',
      'keyword_workbook':'技术关键词表', 'openscholar_retriever':'OpenScholar检索模型',
      'openscholar_s2':'OpenScholar文献检索资料', 'china_patent_delivery':'全国专利公开文献'}
    events = []
    for f in sorted(path('data/catalog/batches').glob('*.json')):
        try:
            b = read_json(f)
        except (ValueError, OSError):
            continue
        if b.get('status') != 'raw_registered':
            continue
        loaded = b.get('database_loaded') is True
        status = 'loaded' if loaded else 'received'
        records = b.get('loaded_policy_records', b.get('loaded_records')) if loaded else None
        receipt = b.get('database_load_receipt') or b.get('normalization_receipt')
        # published = this release actually consumes the accepted policy database.
        published = loaded and receipt and str(receipt).startswith(CONFIG['policy'] + '/')
        if loaded and receipt == CONFIG.get('foundation_patent_receipt'):
            records = foundation_patent_source()['count']
            published = True
        if published:
            status = 'published'
        events.append(dict(id=f.stem, title=names.get(b.get('source'), b.get('source','数据交付')),
            date=b.get('registered_at') or b.get('created_at'),
            status=status, coverage_scope=batch_coverage(b), label={'received':'原件已接收','loaded':'已规范入库','published':'已用于展示'}[status],
            files=b.get('file_count'), records=records, unit='条',
            detail='已完成原件接收' if not loaded else '已形成规范数据交付',
            evidence=str(f.relative_to(path('data').parent)), batch=b.get('batch'), loaded=loaded))
    events.sort(key=lambda x: x['date'] or '', reverse=True)
    return dict(checked_at=datetime.now(timezone.utc).isoformat(),
       counts=dict(batches=len(events),received=len(events),loaded=sum(e['loaded'] for e in events)),
       events=events)


@app.get('/api/llm/analytics')
def analytics(namespace: str = 'cnki_paper', scope: str = 'llm'):
    if namespace not in NAMES or scope not in ('llm', 'ai', 'context'):
        raise HTTPException(400, '未知来源或筛选口径')
    return research_views()['analytics'][namespace + ':' + scope]


@app.get('/api/llm/chain-summary')
def chain_summary(scope: str = 'ai'):
    if scope not in ('llm', 'ai', 'context'):
        raise HTTPException(400, '未知筛选口径')
    return research_views()['summaries'][scope]


@app.get('/api/llm/graph')
def graph(chain: str = 'paper_tech', scope: str = 'ai', limit: int = Query(20, ge=5, le=60)):
    if chain == 'mixed':
        return study_views()['mixed_graph']
    if scope == 'ai' and chain in study_views()['graphs']:
        reviewed = study_views()['graphs'][chain]
        record_type = 'patent' if chain == 'patent_tech' else 'paper'
        chosen = {n['id'] for n in reviewed['nodes'] if n['type'] == record_type}
        chosen = set(sorted(chosen)[:limit])
        edges = [e for e in reviewed['edges'] if e['source'] in chosen or e['target'] in chosen]
        ids = {e[k] for e in edges for k in ('source', 'target')}
        nodes = [n for n in reviewed['nodes'] if n['id'] in ids]
        return dict(nodes=nodes, edges=edges, meta=dict(reviewed['meta'], nodes=len(nodes), edges=len(edges), sample_records=len(chosen), sample_limit=limit))
    if chain not in ('fund_paper', 'paper_tech', 'patent_tech', 'fund_patent', 'paper_network') or scope not in ('llm', 'ai', 'context'):
        raise HTTPException(400, '未知链路或筛选口径')
    source = research_views()['graphs'][chain + ':' + scope]
    chosen = set(source['sample_units'][:limit])
    if chain == 'paper_network':
        edges = [e for e in source['edges'] if e['source'] in chosen and e['target'] in chosen]
    else:
        edges = [e for e in source['edges'] if e['source'] in chosen or e['target'] in chosen]
    node_ids = chosen | {e[k] for e in edges for k in ('source', 'target')}
    nodes = [n for n in source['nodes'] if n['id'] in node_ids]
    return dict(nodes=nodes, edges=edges, meta=dict(source['meta'], nodes=len(nodes), edges=len(edges), sample_limit=limit, sample_records=len(chosen)))


@app.get('/api/llm/records')
def records(namespace: str = 'cnki_paper', scope: str = 'llm', q: str = Query('', max_length=100),
            limit: int = Query(20, ge=1, le=50), offset: int = Query(0, ge=0, le=300000)):
    if namespace not in NAMES or scope not in ('llm', 'ai', 'context'):
        raise HTTPException(400, '未知来源或筛选口径')
    column = {'llm': 'llm_core', 'ai': 'ai', 'context': 'llm_contextual'}[scope]
    where = f'namespace=? AND {column}=1'
    params = [namespace]
    if q:
        where += " AND title LIKE ? ESCAPE '\\'"
        params.append('%' + q.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_') + '%')
    with db_connect(path(CONFIG['snapshot']) / 'candidates.sqlite3') as db:
        total = db.execute('SELECT COUNT(*) FROM entity WHERE ' + where, params).fetchone()[0]
        rows = []
        selected = list(db.execute('SELECT * FROM entity WHERE ' + where + ' ORDER BY year DESC,uid LIMIT ? OFFSET ?', params + [limit, offset]))
        matches_by_id = {x['uid']: [] for x in selected}
        if selected:
            marks = ','.join('?' for _ in selected)
            for m in db.execute('SELECT uid,field,keyword,term_id,snippet,source_file,row_number FROM match_evidence WHERE uid IN (' + marks + ')', list(matches_by_id)):
                if len(matches_by_id[m['uid']]) < 8:
                    matches_by_id[m['uid']].append({k: m[k] for k in m.keys() if k != 'uid'})
        for x in selected:
            meta = json.loads(x['metadata_json'])
            matches = matches_by_id[x['uid']]
            rows.append(dict(id=x['uid'], title=x['title'], year=x['year'], source=NAMES[namespace], source_id=x['source_id'],
                             url=x['source_id'] if x['source_id'].startswith(('https://', 'http://')) else None,
                             authors=re.sub(r'<[^>]*>', '', html.unescape(meta.get('author') or '')) or None, institution=meta.get('author_institution'),
                             subject=meta.get('申请人') or meta.get('企业名称') or meta.get('proj_school') or meta.get('dependUnit') or meta.get('制定机关'),
                             matched_terms=list(dict.fromkeys(m['keyword'] for m in matches)), evidence=matches,
                             doi=x['doi'], source_scope=x['source_scope'], expert_reviewed=False))
    return dict(rows=rows, total=total, offset=offset, limit=limit, namespace=namespace, scope=scope, version=CONFIG['snapshot'].split('/')[-1])


from gzk.dashboard.llm.low_altitude_proxy import install_low_altitude
install_low_altitude(app, path(CONFIG['low_altitude_web']))


web_root = path(CONFIG['web'])
if (web_root / 'assets').is_dir():
    app.mount('/assets', StaticFiles(directory=web_root / 'assets'), name='assets')


@app.get('/{spa_path:path}')
def frontend(spa_path: str):
    if spa_path.startswith('api/'):
        raise HTTPException(404, '未知API')
    candidate = (web_root / spa_path).resolve()
    if candidate.is_relative_to(web_root.resolve()) and candidate.is_file():
        return FileResponse(candidate)
    if (web_root / 'index.html').is_file():
        return FileResponse(web_root / 'index.html')
    raise HTTPException(503, '请先运行 python manage.py dashboard llm-build')


def main():
    import uvicorn
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=5174)
    parser.add_argument('--host', default='0.0.0.0')
    args = parser.parse_args()
    fixed_assets()
    research_views()
    study_views()
    chronology_views()
    uvicorn.run('gzk.dashboard.llm.backend:app', host=args.host, port=args.port, reload=False)


if __name__ == '__main__':
    main()
