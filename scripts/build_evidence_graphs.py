#!/usr/bin/env python3
"""Build bounded, traceable AI evidence-graph pools from read-only warehouse releases.

All totals refer to the named release and observation scope. Technology links are
keyword candidates, never evidence of adoption. Method-use links are exclusively
accepted records from resource_use_evidence, with unresolved identities retained
as separate provenance nodes. No network calls or production database writes.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

VERSION = 'chain_fill_20261110_v1'
REL = 'data/warehouse/shared/innovation/releases/innovation_relations_20261102_v1/relations.duckdb'
FUNDS = 'data/warehouse/shared/nsfc/releases/nsfc_mac_20261105_v1/funds.duckdb'
PAPERS = 'data/warehouse/shared/papers/releases/paper_unified_20261030_v1/papers.duckdb'
PATENTS = 'data/warehouse/shared/patent/releases/patent_unified_20261030_v1/patents.duckdb'
CONFIG = 'retrieval/technology_point/config/ai_keywords_7class_20261109_v6.json'
DEPS = 'data/runs/shared/patent_unified/patent_unified_20261030_v1/deps'
AI_CONTEXT = re.compile(r'neural|deep.learning|machine.learning|language.model|artificial.intelligence|attention|transformer|diffusion.model|reinforcement.learning|神经|深度学习|机器学习|语言模型|人工智能|注意力|强化学习|模型训练|大模型|智能体|知识图谱|计算机视觉', re.I)
POWER = re.compile(r'power.transformer|voltage.transformer|distribution.transformer|变压器|变电', re.I)
AMBIGUOUS = {'transformer','moe','bpe','mllm','vlm','sft','lora','dpo','icl','cot','gpu','npu','rdma','infiniband','nvlink','aidc','maas','rag','asr','tts','vla','benchmarking','quantization','deduplication','synthetic data','data augmentation','data cleaning','model deployment','model monitoring','parallel storage','resource orchestration','code generation','code completion','task planning','action feedback','tool use','diffusion model','world model','scaling laws','data annotation','data labeling'}
FIELD_NAMES = {'title':'题名','abstract':'摘要','first_claim':'独立权利要求','project_id':'项目编号','evidence_excerpt':'原文摘录','review_summary':'既有原文核验摘要'}

def rows(c, sql, params=None):
    cur=c.execute(sql, params or []); keys=[x[0] for x in cur.description]
    return [dict(zip(keys,r)) for r in cur.fetchall()]

def parse(value, default=None):
    try:return json.loads(value) if isinstance(value,str) else (value if value is not None else default)
    except (ValueError,TypeError):return default

def text(value):
    return re.sub(r'\s+', ' ', str(value or '')).strip()

def digest(value):return hashlib.sha256(str(value).encode()).hexdigest()[:20]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def url_doi(doi):return 'https://doi.org/'+doi if doi else None

def compact_names(value):
    value=parse(value, value)
    if isinstance(value,list):
        return '；'.join(text(x.get('name') or x.get('display_name') or x.get('family') or '') if isinstance(x,dict) else text(x) for x in value[:12])
    return text(value)[:400]

class Matcher:
    def __init__(self, terms):
        self.terms={t['term_id']:t for t in terms}; self.by_alias=defaultdict(list)
        for t in terms:
            for a in [t['name'], *t.get('aliases',[])]:
                self.by_alias[a.casefold()].append(t['term_id'])
        # Letter/digit boundaries protect acronym aliases; Chinese aliases remain substring matches.
        def pattern(a):
            p=re.escape(a).replace(r'\ ',r'[\s\-]+')
            return (r'(?<![A-Za-z0-9])'+p+r'(?![A-Za-z0-9])') if re.search('[A-Za-z]',a) else p
        self.lookup={re.sub(r'[\s\-]+',' ',a):(a,ids) for a,ids in self.by_alias.items()}
        def trie_pattern(aliases):
            trie={}
            for alias in aliases:
                node=trie
                for char in alias:node=node.setdefault(char,{})
                node['']=None
            def render(node):
                options=[]
                for char,child in node.items():
                    if char=='':options.append(r'(?![A-Za-z0-9])' if re.search('[A-Za-z]',aliases[0]) else '')
                    else:options.append((r'[\s\-]+' if char==' ' else re.escape(char))+render(child))
                return '(?:'+'|'.join(options)+')' if len(options)>1 else options[0]
            return render(trie)
        latin=[a for a in self.by_alias if re.search('[A-Za-z]',a)]
        chinese=[a for a in self.by_alias if not re.search('[A-Za-z]',a)]
        self.fast=re.compile(r'(?<![A-Za-z0-9])'+trie_pattern(latin)+'|'+trie_pattern(chinese),re.I)
    def match(self, record):
        found={}
        for field in ('title','abstract','first_claim'):
            raw=text(record.get(field))
            if not raw:continue
            for m in self.fast.finditer(raw):
                key=re.sub(r'[\s\-]+',' ',m.group().casefold())
                alias,ids=self.lookup[key]
                local=raw[max(0,m.start()-190):m.end()+190]
                if alias in AMBIGUOUS and not AI_CONTEXT.search(local+' '+text(record.get('title'))):continue
                if alias=='transformer' and POWER.search(local):continue
                for tid in ids:
                    if tid in found:continue
                    found[tid]={'field':field,'keyword':m.group(),'snippet':raw[max(0,m.start()-100):m.end()+180], 'excerpt_kind':'source_text'}
        return found

class Graph:
    def __init__(self):self.nodes={}; self.edges={}; self.bundles=[]
    def add(self, nodes, edges, category_ids, term_id=None):
        self.nodes.update({n['id']:n for n in nodes});self.edges.update({e['id']:e for e in edges})
        self.bundles.append({'id':digest('|'.join(e['id'] for e in edges)), 'category_ids':sorted(set(category_ids)), 'term_id':term_id, 'node_ids':[n['id'] for n in nodes], 'edge_ids':[e['id'] for e in edges]})
    def result(self):
        return {'nodes':list(self.nodes.values()),'edges':list(self.edges.values()),'bundles':self.bundles,'meta':{'nodes':len(self.nodes),'edges':len(self.edges),'bundles':len(self.bundles),'category_coverage':sorted({c for b in self.bundles for c in b['category_ids']})}}


def build(args):
    root=args.root.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(root/DEPS));import duckdb
    cfg=json.loads((root/CONFIG).read_text());matcher=Matcher(cfg['terms']);c=duckdb.connect(':memory:')
    c.execute('set threads=2');c.execute("set memory_limit='2GB'");c.execute('set preserve_insertion_order=false')
    for name,path in [('r',REL),('f',FUNDS),('p',PAPERS),('t',PATENTS)]:c.execute(f"attach '{str(root/path).replace(chr(39),chr(39)*2)}' as {name} (read_only)")
    terms=matcher.terms
    term_nodes={tid:{'id':tid,'type':'technology','label':t['name'],'category_ids':[t['category_id']], 'source':'人工智能共同技术词表', 'fields':{'技术编号':tid,'技术组':t['level2'],'技术大类':t['level1']}, 'provenance':{'file':CONFIG,'version':cfg['version']}} for tid,t in terms.items()}
    funds={r['project_id']:r for r in rows(c,'select project_id,grant_no,title,approval_year,institution,principal_investigator from f.ai_project')}
    latest_fund_ids=set(funds)
    # Relation release may retain entities outside the refreshed master; preserve its own identity.
    for r in rows(c,'select project_id,grant_no,title,approval_year,institution,principal_investigator from r.project where is_ai'):
        funds.setdefault(r['project_id'],r)
    paper_links=defaultdict(list)
    for r in rows(c,'select project_id,paper_id,bases from r.project_paper where is_ai'):
        paper_links[r['paper_id']].append(r)
    patent_links=defaultdict(list)
    for r in rows(c,'select pp.* from r.project_patent pp join r.project q using(project_id) where q.is_ai'):
        patent_links[r['application_id']].append(r)
    print(json.dumps({'stage':'source_links_loaded','paper_links':sum(map(len,paper_links.values())),'patent_links':sum(map(len,patent_links.values()))}),flush=True)
    counts={
        'ai_funds_latest':c.execute('select count(*) from f.ai_project').fetchone()[0],
        'ai_funds_relation_release':c.execute('select count(*) from r.project where is_ai').fetchone()[0],
        'ai_fund_paper_edges':sum(map(len,paper_links.values())),
        'ai_fund_unique_papers':len(paper_links),
        'ai_fund_patent_relation_rows':sum(map(len,patent_links.values())),
        'ai_fund_patent_applications':len(patent_links),
        'ai_papers_catalog':c.execute('select count(*) from p.ai_paper').fetchone()[0],
        'ai_patent_publications':c.execute('select count(*) from t.ai_patent').fetchone()[0],
        'accepted_method_use_edges':c.execute('select count(*) from r.resource_use_evidence where accepted_existing_actual_use_evidence').fetchone()[0]}
    paper_sql='''select q.paper_id as entity_id,coalesce(p.title,q.title) as title,coalesce(p.publication_year,q.publication_year) as year,p.abstract,coalesce(p.doi,q.doi) as doi,p.authors_json,coalesce(p.preferred_source,'基金成果登记') as preferred_source,coalesce(p.primary_observation_id,q.primary_observation_id) as primary_observation_id,
       case when p.paper_id is not null then 'ai_paper' else 'relation_paper' end as text_table
       from r.paper q join (select distinct paper_id from r.project_paper where is_ai) linked using(paper_id)
       left join p.ai_paper p on p.paper_id=q.paper_id'''
    patent_sql='''select * from (select t.application_id as entity_id,t.publication_id,t.title,year(t.application_date) as year,t.abstract,t.first_claim,
       t.applicant_names,t.inventor_names,t.ipc_main,t.ai_source_file_sha256,t.ai_source_row,t.patsnap_source_file_sha256,t.patsnap_source_row,
       row_number() over(partition by t.application_id order by case when t.publication_id=q.publication_id then 0 else 1 end,t.publication_date desc,t.publication_id) as pick
       from t.ai_patent t join (select application_id,min(publication_id) as publication_id from r.project_patent group by 1) q using(application_id)) where pick=1'''
    print(json.dumps({'stage':'population_counts_loaded'}),flush=True)
    pools={};scan_stats={}
    for kind,sql in [('paper',paper_sql),('patent',patent_sql)]:
        print(json.dumps({'stage':'query_start','kind':kind}),flush=True)
        cur=c.execute(sql);print(json.dumps({'stage':'query_ready','kind':kind}),flush=True);keys=[x[0] for x in cur.description];pool=defaultdict(list);matched=Counter();cat_records=Counter();scanned=0
        while batch:=cur.fetchmany(1500):
            if scanned and scanned%30000==0:print(json.dumps({'stage':'scan','kind':kind,'records':scanned}),flush=True)
            for raw in batch:
                record=dict(zip(keys,raw));scanned+=1;hits=matcher.match(record)
                for cat in {terms[tid]['category_id'] for tid in hits}:cat_records[cat]+=1
                for tid,evidence in hits.items():
                    matched[tid]+=1
                    # Prefer title evidence, then recent publication; deterministic tie-break.
                    score=(evidence['field']=='title',min(record.get('year') or 0,2026),digest(record['entity_id']))
                    candidates=pool[tid];candidates.append((score,record,evidence));candidates.sort(key=lambda x:x[0],reverse=True)
                    if len(candidates)>args.per_term:candidates.pop()
        pools[kind]=pool;scan_stats[kind]={'scanned_records':scanned,'matching_records_by_category':dict(cat_records),'matching_records_by_term':dict(matched),'retained_bundles':sum(map(len,pool.values()))}
        print(json.dumps({'stage':kind, 'scanned':scanned,'matched_terms':len(pool),'pool_bundles':sum(map(len,pool.values()))}),flush=True)
    # Resolve evidence only for sampled project/paper pairs, keeping the original locator.
    selected_pairs=set()
    def choose_project(kind,record,tid):
        links=(paper_links if kind=='paper' else patent_links)[record['entity_id']]
        return sorted(links,key=lambda x:digest(x['project_id']))[0]
    for tid,choices in pools['paper'].items():
        for _,record,_ in choices:selected_pairs.add((choose_project('paper',record,tid)['project_id'],record['entity_id']))
    c.execute('create temp table sampled_pair(project_id varchar,paper_id varchar)')
    if selected_pairs:c.executemany('insert into sampled_pair values (?,?)',sorted(selected_pairs))
    paper_evidence={}
    for r in rows(c,'''select e.* from r.project_paper_evidence e join sampled_pair s using(project_id,paper_id)
          qualify row_number() over(partition by e.project_id,e.paper_id order by e.basis,e.source_evidence_id)=1'''):
        paper_evidence[(r['project_id'],r['paper_id'])]=r
    selected_patent_records={choose_project('patent',r,tid)['source_record_id'] for tid,choices in pools['patent'].items() for _,r,_ in choices}
    c.execute('create temp table sampled_outcome(source_record_id varchar)')
    if selected_patent_records:c.executemany('insert into sampled_outcome values (?)',[(s,) for s in sorted(selected_patent_records)])
    patent_evidence={r['source_record_id']:r for r in rows(c,'''select o.project_id,o.source_record_id,o.title,o.authors_raw,o.source_locator,o.relation_locator from r.ai_fund_outcome o join sampled_outcome s using(source_record_id)''')}
    def fund_node(pid):
        r=funds[pid]
        return {'id':'fund:'+pid,'type':'fund','label':r['title'] or r['grant_no'],'year':r['approval_year'],'source':'NSFC 项目登记', 'fields':{'批准号':r['grant_no'],'依托单位':r['institution'],'负责人':r['principal_investigator']},'provenance':{'database':FUNDS if pid in latest_fund_ids else REL,'table':'ai_project' if pid in latest_fund_ids else 'project','project_id':pid}}
    def record_node(kind,r):
        if kind=='paper':
            return {'id':'paper:'+r['entity_id'],'type':'paper','label':r['title'],'year':r['year'],'url':url_doi(r['doi']),'source':'论文统一库 · '+text(r['preferred_source']), 'fields':{'DOI':r['doi'],'作者（节选）':compact_names(r['authors_json'])}, 'provenance':{'database':PAPERS if r['text_table']=='ai_paper' else REL,'table':'ai_paper' if r['text_table']=='ai_paper' else 'paper','paper_id':r['entity_id'],'primary_observation_id':r['primary_observation_id']}}
        return {'id':'patent:'+r['entity_id'],'type':'patent','label':r['title'],'year':r['year'],'url':'https://patents.google.com/patent/'+r['publication_id']+'/zh','source':'专利统一库', 'fields':{'申请号':r['entity_id'],'公开号':r['publication_id'],'申请人':r['applicant_names'],'发明人':r['inventor_names'],'主IPC分类号':r['ipc_main']},'provenance':{'database':PATENTS,'table':'ai_patent','application_id':r['entity_id'],'publication_id':r['publication_id'],'ai_source_file_sha256':r['ai_source_file_sha256'],'ai_source_row':r['ai_source_row'],'patsnap_source_file_sha256':r['patsnap_source_file_sha256'],'patsnap_source_row':r['patsnap_source_row']}}
    graphs={k:Graph() for k in ('mixed','fund_paper','paper_tech','patent_tech','fund_patent','paper_network')}
    for kind,pool in pools.items():
        for tid in sorted(pool):
            cat=terms[tid]['category_id'];tn=term_nodes[tid]
            for _,record,evidence in pool[tid]:
                rn=record_node(kind,record);link=choose_project(kind,record,tid);fn=fund_node(link['project_id'])
                tech_edge={'id':digest(rn['id']+'|'+tid),'source':rn['id'],'target':tid,'label':'文本涉及技术主题','kind':'keyword_topic','status':'rule_candidate','category_ids':[cat],'evidence':[{**evidence,'source':'论文统一库' if kind=='paper' else '专利统一库','source_locator':rn['provenance'],'url':rn.get('url')}]}
                if kind=='paper':
                    ev=paper_evidence.get((link['project_id'],record['entity_id']),{})
                    fund_edge={'id':digest(fn['id']+'|'+rn['id']),'source':fn['id'],'target':rn['id'],'label':'项目关联论文成果','kind':'source_project_id','status':'source_link','evidence':[{'field':'project_id','snippet':funds[link['project_id']]['grant_no'],'excerpt_kind':'source_field','source':'NSFC 成果登记 / 明示资助记录','basis':ev.get('basis') or link['bases'],'source_locator':parse(ev.get('source_locator'),{}),'source_evidence_id':ev.get('source_evidence_id')}]}
                    target='fund_paper'
                else:
                    ev=patent_evidence.get(link['source_record_id'],{})
                    fund_edge={'id':digest(fn['id']+'|'+rn['id']),'source':fn['id'],'target':rn['id'],'label':'项目登记专利成果','kind':'registered_patent_outcome','status':'registered_outcome_identity_match','evidence':[{'field':'登记成果题名','snippet':ev.get('title') or record['title'],'excerpt_kind':'source_field','source':'NSFC 项目成果登记','source_locator':parse(ev.get('source_locator'),{}),'relation_locator':parse(ev.get('relation_locator'),[]),'source_record_id':link['source_record_id']},{'field':'成果作者 / 专利发明人','snippet':text(ev.get('authors_raw'))+' / '+text(record['inventor_names']),'excerpt_kind':'source_field','source':'项目成果登记与专利统一库','basis':link['basis'],'source_locator':{'database':REL,'table':'project_patent','project_id':link['project_id'],'application_id':record['entity_id'],'source_record_id':link['source_record_id']}}]}
                    target='fund_patent'
                graphs[kind+'_tech'].add([rn,tn],[tech_edge],[cat],tid)
                graphs[target].add([fn,rn,tn],[fund_edge,tech_edge],[cat],tid)
                graphs['mixed'].add([fn,rn,tn],[fund_edge,tech_edge],[cat],tid)
    method_issues=[];method_hashes={};method_statuses=Counter()
    for r in rows(c,'select * from r.resource_use_evidence where accepted_existing_actual_use_evidence order by source_year,using_year,use_evidence_id'):
        loc=parse(r['source_locator'],{});source_row=parse(r['source_row_json'],{})
        source_path=loc.get('original_text_path');expected_hash=loc.get('original_text_sha256')
        if source_path and expected_hash:
            local=root/'data'/str(source_path).split('/data/',1)[-1] if '/data/' in source_path else Path(source_path)
            if not local.is_file() or sha(local)!=expected_hash:raise ValueError('Method evidence local hash mismatch: '+r['use_evidence_id'])
            method_hashes[r['use_evidence_id']]=expected_hash
        ns=[]
        for side in ('source','using'):
            pid=r[side+'_paper_id'];identity=r[side+'_identity_key'];title=r[side+'_title'];canonical=bool(pid)
            doi=pid[4:] if pid and pid.startswith('doi:') else None
            n={'id':'paper:'+pid if canonical else 'paper-evidence:'+identity,'type':'paper','label':title,'year':r[side+'_year'],'url':url_doi(doi) or (loc.get('original_url') if side=='using' else None),'source':'已核验原文方法关系','fields':{'DOI':doi,'身份核对':r[side+'_mapping_status']},'provenance':{'database':REL,'table':'resource_use_evidence','identity_key':identity,'paper_id':pid,'identity_mapping_status':r[side+'_mapping_status']}}
            ns.append(n)
            if not canonical:method_issues.append({'use_evidence_id':r['use_evidence_id'],'side':side,'status':r[side+'_mapping_status']})
        hits=matcher.match({'title':r['source_title']+' '+r['using_title'],'abstract':r['evidence_excerpt'] or ''})
        cats=sorted({terms[t]['category_id'] for t in hits})
        quote=r['evidence_excerpt'];method_statuses[r['evidence_status']]+=1
        e={'id':'use:'+r['use_evidence_id'],'source':ns[0]['id'],'target':ns[1]['id'],'label':{'algorithm_component':'算法组件采用','research_tool_component':'工具框架采用','baseline_reproduction_infrastructure':'复现比较基线','dataset_training_and_evaluation':'训练与评测数据使用','evaluation_measure_used':'评测指标使用','official_implementation_baseline':'官方实现用作基线','pretrained_checkpoint_adaptation':'预训练资源适配'}.get(r['use_type'],'原文确认的资源使用'),'kind':'actual_resource_use','status':r['evidence_status'],'category_ids':cats,'use_type':r['use_type'],'evidence':[{'field':'evidence_excerpt' if quote else 'review_summary','snippet':quote or r['evidence_summary'],'excerpt_kind':'source_text' if quote else 'prior_review_summary','source':'既有原文核验记录','url':loc.get('original_url'),'source_locator':loc,'summary':r['evidence_summary']}]}
        graphs['paper_network'].add(ns,[e],cats)
        graphs['mixed'].add(ns,[e],cats)
    payload={'meta':{'schema_version':1,'version':VERSION,'built_at':datetime.now(timezone.utc).isoformat(),'keyword_version':cfg['version'],'keyword_sha256':sha(root/CONFIG),'keyword_count':len(terms),'sources':{'relations':REL,'funds':FUNDS,'papers':PAPERS,'patents':PATENTS,'keywords':CONFIG},'population_counts':counts,'observation_scope':{'technology_graphs':'成果自身题名、摘要、独立权利要求命中共同词表；候选池来自关系库内AI项目已关联的论文与专利','method_graph':'resource_use_evidence中accepted_existing_actual_use_evidence=true的全部既有核验记录；未匹配身份独立保留','macro_micro':'宏观最新基金主表与本关系版本的微观成果观察范围不同；未用图中节点数代替全库统计'},'matching_policy':{'status':'rule_candidate','fields':['title','abstract','first_claim'],'ambiguous_alias_context_required':sorted(AMBIGUOUS),'transformer_power_excluded':True,'unmatched_terms_not_filled':True},'pool_per_term':args.per_term,'scan_stats':scan_stats,'method_evidence':{'accepted':counts['accepted_method_use_edges'],'verified_local_text_hashes':len(method_hashes),'status_counts':dict(method_statuses),'unresolved_identities':method_issues}},'categories':[{'id':x['category_id'],'name':x['name']} for x in cfg['categories']],'graphs':{k:g.result() for k,g in graphs.items()}}
    issues=[]
    for name,g in payload['graphs'].items():
        nids={n['id'] for n in g['nodes']};eids={e['id'] for e in g['edges']}
        if len(nids)!=len(g['nodes']) or len(eids)!=len(g['edges']):issues.append(name+': duplicate ids')
        for e in g['edges']:
            if e['source'] not in nids or e['target'] not in nids:issues.append(name+': orphan edge')
            if not e.get('evidence') or any(not v.get('snippet') or not v.get('source_locator') for v in e['evidence']):issues.append(name+': evidence gap '+e['id'])
        for b in g['bundles']:
            if not set(b['node_ids'])<=nids or not set(b['edge_ids'])<=eids:issues.append(name+': orphan bundle')
    if issues:raise ValueError('\n'.join(issues))
    (out/'evidence-graphs.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':'))+'\n')
    qa={'version':VERSION,'passed':True,'graph_counts':{k:g['meta'] for k,g in payload['graphs'].items()},'population_counts':counts,'method_local_hashes_checked':len(method_hashes),'method_unresolved_endpoint_count':len(method_issues),'json_bytes':(out/'evidence-graphs.json').stat().st_size,'missing_paper_terms':sorted(set(terms)-set(pools['paper'])),'missing_patent_terms':sorted(set(terms)-set(pools['patent']))}
    (out/'evidence-graphs-quality.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n');print(json.dumps(qa,ensure_ascii=False),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--per-term',type=int,default=8)
    args=ap.parse_args();build(args)
