"""领域数据 · 企业／产品／经济：从同事交付的 industry-panels 页面抽取数据，生成静态 JSON。

用法：
  python scripts/build_industry_panels.py <解压目录> snapshot/public/industry/v1
解压目录内含 index.html（企业与专利）、products.html（产品）、economics.html（经济指标），
每页以 <script id="page-data" type="application/json"> 内嵌数据。
"""
import json, re, sys, pathlib

src, out = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)

def page(name):
    html = (src / name).read_text(encoding='utf-8')
    m = re.search(r'<script id="page-data" type="application/json">(.*?)</script>', html, re.S)
    return json.loads(m.group(1))

idx, prd, eco = page('index.html'), page('products.html'), page('economics.html')
dump = lambda name, obj: (out / name).write_text(json.dumps(obj, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

COV = ['products', 'patents', 'labeledPatents', 'economics', 'jobs', 'jobsDeduplicated', 'subsidiaries', 'technologies']
econ_ids = {f['companyId'] for f in eco['finance']}
companies = [{
    'id': c['id'], 'cid': c.get('canonicalId'), 'name': c['name'], 'credit': c.get('creditCode') or '',
    'industry': c.get('industry') or '行业未列明', 'province': c.get('province') or '地区未列明', 'city': c.get('city') or '',
    'roles': c.get('roles') or [], 'type': c.get('type') or '', 'category': c.get('category') or '',
    'desc': c.get('description') or '', 'sources': c.get('sources') or [],
    'cov': {k: (c.get('coverage') or {}).get(k, 0) for k in COV}, 'tech': c.get('technologyIds') or [],
    'econ': c['id'] in econ_ids,
} for c in idx['companies']]
pos = {c['cid']: i for i, c in enumerate(companies) if c['cid']}
tech_owners = {}
for cid, tid, n in idx['patentTechnology']:
    if cid in pos: tech_owners.setdefault(tid, set()).add(pos[cid])
techs = [{k: t.get(k) for k in ('id', 'name', 'level1', 'level2', 'definition', 'patents', 'products', 'companies')} for t in idx['technologies']]
dump('companies.json', {
    'date': idx.get('sourceDate'), 'patentDate': idx.get('patentDate'),
    'companies': companies, 'technologies': techs,
    # 技术点 → 拥有该技术点专利的企业（companies 下标）
    'patentTech': {t: sorted(ix) for t, ix in tech_owners.items()},
})
# 专利按企业编号分片（字符编码和 mod 32），企业详情按需读取
SHARDS = 32
shard = lambda k: sum(ord(ch) for ch in k) % SHARDS
parts = [{} for _ in range(SHARDS)]
for k, v in idx['patents'].items():
    parts[shard(k)][k] = [{x: p.get(x) for x in ('title', 'application', 'publication', 'applicationDate', 'publicationDate', 'applicant', 'company', 'type', 'abstract', 'url', 'technologies')} for p in v]
    for p in parts[shard(k)][k]:
        if p['abstract']: p['abstract'] = re.sub(r'\s*[（(]macrodatas\.cn[)）]\s*$', '', p['abstract']).strip()
(out / 'patents').mkdir(exist_ok=True)
for i, part in enumerate(parts):
    (out / 'patents' / f'{i}.json').write_text(json.dumps(part, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
owners = [{k: o.get(k) for k in ('id', 'companyId', 'name', 'province', 'industry')} for o in prd['owners']]
products = [{
    'id': p['id'], 'name': p['name'], 'owners': p.get('companyIds') or [], 'ownerNames': p.get('companyNames') or [],
    'tech': p.get('technologyIds') or [], 'versions': p.get('versions') or [], 'desc': p.get('description') or '',
    'sources': p.get('sources') or [], 'roles': p.get('roles') or [], 'uses': p.get('uses') or [],
} for p in prd['products']]
dump('products.json', {'date': prd.get('sourceDate'), 'owners': owners, 'products': products})
dump('economics.json', {
    'date': eco.get('sourceDate'), 'definition': eco.get('financeDefinition'),
    'categories': eco['economicCategories'], 'metrics': eco['economicMetrics'],
    'finance': [[f['companyId'], f['year'], f['metric'], f['value'], f.get('scope') or '', f.get('entity') or '', f.get('source')] for f in eco['finance']],
    'sources': eco['sources'],
})
for f in sorted(out.glob('*.json')):
    print(f.name, round(f.stat().st_size / 1e6, 2), 'MB')
print('companies', len(companies), 'products', len(products), 'finance', len(eco['finance']))
