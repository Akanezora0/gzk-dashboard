"""Publish current accepted inventories for Dashboard; read receipts, never edit source DBs."""
from pathlib import Path
import csv,json,hashlib
from gzk.paths import ROOT
OUT=ROOT/'data/outputs/shared/ui_handoff/cursor_20260924/analysis_public/chain-analysis/v1'
SOURCES=[]
def read(rel,csv_mode=False):
 p=ROOT/rel;b=p.read_bytes();SOURCES.append({'path':rel,'sha256':hashlib.sha256(b).hexdigest()})
 return list(csv.DictReader(b.decode('utf-8-sig').splitlines())) if csv_mode else json.loads(b)
def build():
 paper=read('data/outputs/shared/paper_inventory/paper_unified_20261030_v1/quality.json')
 patent=read('data/outputs/shared/patent_inventory/patent_unified_20261030_v1/质量回执.json')
 relation=read('data/outputs/shared/innovation_relations/innovation_relations_20261102_v1/quality.json')
 assert paper['duplicate_master_ids']==0 and paper['legacy_missing_from_ai']==0
 assert patent['status']=='verified' and relation['verified'] and all(x['passed'] for x in relation['checks'])
 c=relation['counts'];pr=paper['relations'];pc=patent['counts']
 assert c['project_scope']==pr['ai_fund_project'] and c['project_paper']==pr['project_paper']
 assert c['paper_scope']==paper['ai_papers'] and c['patent']==pc['ai_patent']
 assert sum(n for _,n in paper['years_ai'])==paper['ai_papers']
 py=read('data/outputs/shared/patent_inventory/patent_unified_20261030_v1/AI专利_年份分布.csv',True)
 fy=read('data/outputs/shared/innovation_relations/innovation_relations_20261102_v1/annual_project_coverage.csv',True)
 assert sum(int(r['publication_year_count'] or 0) for r in py)==pc['ai_patent']
 assert sum(int(r['projects']) for r in fy if r['is_ai']=='True')==c['project_scope']
 rows=[]
 def row(id,name,kind,count,unit,scope,description):
  rows.append(dict(id=id,name=name,kind=kind,count=count,unit=unit,scope=scope,description=description,status='已规范入库',verified_at='2026-11-03',source='统一规范库',note=description))
 row('unified_paper','跨来源规范论文','论文',paper['total_papers'],'篇','全领域 · 跨来源去重','统一论文身份，保留各来源互补字段及原始观察')
 row('unified_fund','基金工作身份','基金',c['project'],'个','全领域 · 项目与资助编号','含文献中识别的资助编号身份，已连接项目资料与来源证据')
 row('cn_patent_base','全国专利公开文献','专利',pc['national_master'],'条','全领域 · 全国目录','按公开号去重的全国专利规范主目录')
 row('unified_ai_paper','AI—LLM论文','论文',paper['ai_papers'],'篇','人工智能 · 统一研究集合','广泛规则及同义表达筛选，合入既有AI集合和AI基金关联论文')
 row('unified_ai_fund','AI基金项目','基金',c['project_scope'],'项','人工智能 · 主项目集','固定主项目及完整登记成果，批准年与执行年分别保留')
 row('unified_ai_patent','AI专利公开文献','专利',c['patent'],'条','人工智能 · AI包与智慧芽','按公开号合并去重，保留文本、主体和专利日期')
 rels=[('project_outcome','AI基金登记成果','条','人工智能 · 全部登记成果'),('project_paper','基金—论文关系','对','全领域'),('project_person','基金—人员来源记录','条','全领域'),('paper_authorship','论文—作者来源记录','条','AI论文来源观察'),('person_organization_observation','人员—机构观察','条','全领域'),('citation_edge','论文引用关系','对','关联库'),('patent_paper_link_all','专利—论文规范关系','对','已匹配关系'),('project_patent','基金—专利关系','条','关联库'),('funding_continuity','负责人资助接续候选','条','全领域 · 含姓名机构匹配'),('cfrr_patent_paper_evidence','CFRR专利—论文来源记录','条','外部论文ID来源记录')]
 for key,label,unit,scope in rels:row('relation_'+key,label,'关系',c[key],unit,scope,label+'；'+scope)
 row('relation_ai_project_paper','AI基金—论文关系','关系',pr['ai_project_paper'],'对','人工智能 · 主项目集','已统一项目与论文身份的关系对')
 audit=read('data/runs/llm/innovation/relations_review_20261103_v1/relations_year_audit.json')
 assert audit['fund_paper_summary'][0]['relations']==pr['ai_project_paper']
 result=dict(fund_paper_summary=audit['fund_paper_summary'][0],fund_paper_years=audit['fund_paper_year'],version='current-inventory-20261103-v1',as_of='2026-11-03',datasets=rows,counts=dict(papers=paper['total_papers'],ai_papers=paper['ai_papers'],fund_identities=c['project'],ai_funds=c['project_scope'],national_patents=pc['national_master'],ai_patents=c['patent'],ai_applications=c['patent_application'],ai_fund_papers=pr['ai_project_paper'],**c),years=dict(paper=[dict(year=y,count=n) for y,n in paper['years_ai']],patent=[dict(year=int(r['year']) if r['year'] else None,count=int(r['application_year_count'] or 0),publication_count=int(r['publication_year_count'] or 0)) for r in py],fund=[dict(year=int(r['approval_year']) if r['approval_year'] else None,count=int(r['projects'])) for r in fy if r['is_ai']=='True']),paper_types=[dict(name=k,count=v) for k,v in paper['publication_types']],paper_fields=paper['ai_fields'],sources=[{'version':paper['version']},{'version':'patent_unified_20261030_v1'},{'version':relation['version']}])
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/'current-inventory.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')))
 manifest=OUT.parents[2]/'verification/current_inventory_20261103';manifest.mkdir(parents=True,exist_ok=True)
 (manifest/'sources.json').write_text(json.dumps(dict(inputs=SOURCES,output_sha256=hashlib.sha256((OUT/'current-inventory.json').read_bytes()).hexdigest(),checks='passed'),ensure_ascii=False,indent=2))
 print(json.dumps(dict(status='verified',datasets=len(rows),papers=paper['total_papers'],ai_papers=paper['ai_papers']),ensure_ascii=False))
 return result
if __name__=='__main__':build()
