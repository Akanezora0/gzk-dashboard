#!/usr/bin/env python3
"""Read-only innovation-chain aggregation. Writes only a new output directory.
Usage: python manage.py run dashboard/cursor_ui/scripts/build_innovation_metrics.py --output data/runs/shared/innovation_dashboard/chain_fill_20261110_v1
No imputation of approval amounts or years. Counts are unique within each direction;
multidirectional works may occur in multiple direction views. Funding is fractional.
"""
from __future__ import annotations
import argparse, json, sys, os, re, time, hashlib
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path('/root/gzk_jc'));ap.add_argument('--output',type=Path,required=True);ap.add_argument('--resume',action='store_true');args=ap.parse_args()
 root=args.root.resolve();out=args.output.resolve()
 try: import duckdb
 except ImportError:
  deps=root/'data/runs/shared/patent_unified/patent_unified_20261030_v1/deps'
  if sys.version_info[:2]!=(3,13):os.execv('/root/anaconda3/bin/python',['/root/anaconda3/bin/python',__file__,*sys.argv[1:]])
  sys.path.insert(0,str(deps));import duckdb
 out.mkdir(parents=True,exist_ok=True)
 db=out/'analysis.duckdb'
 if db.exists() and not args.resume:raise SystemExit('Use a new output directory; refusing to replace analysis database')
 con=duckdb.connect(str(db),config={'threads':2,'memory_limit':'12GB','preserve_insertion_order':False})
 con.execute('SET temp_directory=?',[str(out/'spill')])
 paths={'f':'data/warehouse/shared/nsfc/releases/nsfc_mac_20261105_v1/funds.duckdb','r':'data/warehouse/shared/innovation/releases/innovation_relations_20261102_v1/relations.duckdb','p':'data/warehouse/shared/papers/releases/paper_unified_20261030_v1/papers.duckdb','t':'data/warehouse/shared/patent/releases/patent_unified_20261030_v1/patents.duckdb'}
 for n,p in paths.items():con.execute(f"ATTACH '{root/p}' AS {n} (READ_ONLY)")
 def q(sql):
  # Resume only completed materialized stages in this dedicated run directory.
  match=re.match(r'CREATE TABLE (\w+) AS|CREATE TABLE (\w+)\(',sql)
  if match:
   name=next(v for v in match.groups() if v)
   if con.execute('SELECT count(*) FROM information_schema.tables WHERE table_catalog=current_database() AND table_name=?',[name]).fetchone()[0]:return con.execute('SELECT 1')
  match=re.match(r'ALTER TABLE (\w+) ADD COLUMN (\w+)',sql)
  if match and con.execute('SELECT count(*) FROM information_schema.columns WHERE table_catalog=current_database() AND table_name=? AND column_name=?',list(match.groups())).fetchone()[0]:return con.execute('SELECT 1')
  match=re.match(r'UPDATE (\w+) SET categories=',sql)
  if match and con.execute(f'SELECT count(*) FROM {match.group(1)} WHERE categories IS NULL').fetchone()[0]==0:return con.execute('SELECT 1')
  return con.execute(sql)
 def log(msg):print(time.strftime('%H:%M:%S'),msg,flush=True)
 def scalar(sql):return q(sql).fetchone()[0]
 # Shared own-content broad seven-direction rules: applied identically to reference
 # works and grant-associated works. Titles, abstracts and keywords, no assignment
 # inherited merely from a linked project or from a different taxonomy version.
 rules={
 'AI1':r'foundation models?|large language models?|language modeling|generative (adversarial )?(models?|networks?)|diffusion models?|variational autoencod|representation learning|graph neural|convolutional neural|recurrent neural|spiking neural|self[- ]attention|transformer|大语言模型|语言大模型|语言建模|生成对抗|扩散模型|变分自编码|基础模型|预训练模型|表征学习|表示学习|图神经网络|卷积神经网络|循环神经网络|脉冲神经网络|自注意力|网络架构|神经网络结构',
 'AI2':r'machine learning|deep learning|reinforcement learning|transfer learning|domain adaptation|few[- ]shot|zero[- ]shot|meta[- ]learning|self[- ]supervised|semi[- ]supervised|unsupervised|contrastive learning|multi[- ]task learning|active learning|continual learning|online learning|gradient descent|training (algorithm|strateg|method)|learning (algorithm|theory|method)|fine[- ]tun|pre[- ]train|chain[- ]of[- ]thought|in[- ]context learning|support vector|random forest|ensemble learning|metric learning|机器学习|深度学习|强化学习|迁移学习|领域适应|域适应|小样本|少样本|零样本|元学习|自监督|半监督|无监督|对比学习|多任务学习|主动学习|持续学习|增量学习|在线学习|梯度下降|学习算法|学习理论|训练方法|预训练|微调|思维链|上下文学习|支持向量机|随机森林|集成学习|度量学习',
 'AI3':r'\bgpus?\b|\bnpus?\b|ai (chip|accelerator)|model compression|knowledge distillation|model quantiz|network pruning|efficient (inference|training|attention)|light[- ]?weight (model|network)|distributed (training|learning|inference)|edge (ai|intelligence|inference|learning|computing)|on[- ]device (inference|learning)|flashattention|pagedattention|硬件加速|AI芯片|神经网络处理器|学习加速器|模型压缩|知识蒸馏|模型量化|网络剪枝|模型剪枝|轻量级神经网络|分布式训练|分布式学习|分布式推理|推理加速|训练加速|边缘智能|边缘推理|边缘计算|端侧推理|算力调度|计算资源分配',
 'AI4':r'cloud computing|cloud[- ]edge|cloud (platform|service|resource)|cloud[- ]based|mlops|llmops|model as a service|model hosting|inference api|(machine|deep|federated) learning platform|ai platform|云计算|云平台|云服务|云资源|云边协同|云边端|云端模型|智算平台|模型服务|模型托管|推理服务|机器学习平台|深度学习平台|模型开发平台|人工智能平台|模型运维|模型部署',
 'AI5':r'computer vision|image (recognition|classification|segmentation|processing|generation|restoration|enhancement|retrieval)|object (detection|recognition|tracking)|semantic segmentation|scene understanding|visual (recognition|tracking|question|understanding)|point cloud|natural language|machine translation|question answering|dialog(ue)? (systems?|generation)|text (classification|generation|summar|understanding|mining)|named entity|sentiment analysis|speech (recognition|synthesis|enhancement|separation)|recommend(er|ation) system|autonomous driving|embodied (ai|intelligence)|retrieval[- ]augmented|tool (use|calling)|计算机视觉|图像(识别|分类|分割|处理|生成|增强|复原|重建|检索)|目标(检测|识别|跟踪)|语义分割|场景理解|视觉(识别|跟踪|理解|问答)|人脸识别|行为识别|点云|自然语言|机器翻译|问答|对话系统|文本(分类|生成|摘要|理解|挖掘)|命名实体|情感分析|语音(识别|合成|增强|分离)|代码生成|推荐系统|智能推荐|自动驾驶|具身智能|机器人(学习|感知|导航)|智能体|智能控制|自主导航|检索增强|工具调用|知识增强',
 'AI6':r'training data|data (annotation|labeling|augmentation|curation|cleaning)|synthetic data|dataset (construction|quality)|knowledge (graph|base|engineering|representation)|vector (database|index)|federated learning|differential privacy|privacy[- ]preserving|secure multiparty|训练数据|数据(标注|增强|清洗|治理)|合成数据|数据集(构建|建设|质量)|知识(图谱|库|工程|表示|组织|发现)|向量数据库|向量索引|联邦学习|差分隐私|隐私计算|隐私保护|安全聚合',
 'AI7':r'adversarial (attack|example|robust|defen)|model (evaluation|safety|security|risk)|benchmark|fairness|explainab|interpretability|hallucination|out[- ]of[- ]distribution|robust (learning|classification|model)|模型(评测|评价|安全|风险|公平|隐私)|能力评测|基准测试|对抗(攻击|样本|防御|鲁棒)|可解释|幻觉|事实一致性|分布外|鲁棒(学习|分类|模型)|生成内容水印|提示注入|越狱攻击'
 }
 names={'AI1':'基础模型与架构','AI2':'模型训练、适配与推理','AI3':'AI算力与运行优化','AI4':'AI云与平台服务','AI5':'知识增强与AI应用','AI6':'数据与知识服务','AI7':'模型评测与安全'}
 ai=r'artificial intelligence|machine learning|deep learning|neural|language model|transformer|reinforcement learning|federated learning|support vector|random forest|computer vision|智能|机器学习|深度学习|神经|语言模型|强化学习|联邦学习|支持向量机|随机森林|视觉|知识图谱|模型'
 # Guard ambiguous hardware/cloud/privacy/safety and transformer electrical homonyms.
 def lit(s):return "'"+s.replace("'","''")+"'"
 def expr(text):
  tests=[]
  for cid,pattern in rules.items():
   cond=f'regexp_matches({text},{lit(pattern)})'
   if cid in ['AI3','AI4','AI6','AI7']:cond+=f' AND regexp_matches({text},{lit(ai)})'
   if cid=='AI1':cond+=f" AND NOT (regexp_matches({text},'power transformer|transformer winding|电力变压器|变压器绕组|热扩散|thermal diffusion') AND NOT regexp_matches({text},'attention|neural|深度学习|神经|注意力'))"
   tests.append(f'CASE WHEN {cond} THEN {lit(cid)} END')
  return 'list_filter(['+','.join(tests)+'], x -> x IS NOT NULL)'
 norm="regexp_replace(lower(coalesce(title,'')), '[^a-z0-9一-龥]', '', 'g')"
 # Freeze inputs for safe restart: completed tables are reusable only with the
 # same releases, classification rules and query contract.
 fingerprint={'contract':'innovation_metrics_v2','sources':{k:{'path':v,'bytes':(root/v).stat().st_size,'mtime_ns':(root/v).stat().st_mtime_ns} for k,v in paths.items()},'rules_sha256':hashlib.sha256(json.dumps({'rules':rules,'ai_context':ai},sort_keys=True,ensure_ascii=False).encode()).hexdigest()}
 manifest=out/'input_fingerprint.json'
 if manifest.exists():
  if json.loads(manifest.read_text())!=fingerprint:raise SystemExit('Input versions changed; use a new output directory')
 else:manifest.write_text(json.dumps(fingerprint,ensure_ascii=False,indent=2)+'\n')
 log('Preparing current project cohort and source relations')
 q("CREATE TABLE projects AS SELECT *, try_cast(substr(start_date,1,4) AS INTEGER) start_year, try_cast(substr(end_date,1,4) AS INTEGER) end_year, amount_cny_fen/1000000.0 funding_wan, lower(concat_ws(' ',title,keywords_zh,abstract_zh,abstract_en)) txt FROM f.ai_project WHERE approval_year BETWEEN 2017 AND 2025")
 q('ALTER TABLE projects ADD COLUMN categories VARCHAR[]');q('UPDATE projects SET categories='+expr('txt'))
 q('CREATE TABLE project_classes AS SELECT project_id,unnest(categories) category_id,1.0/len(categories) weight FROM projects WHERE len(categories)>0')
 q('CREATE TABLE project_paper AS SELECT DISTINCT rp.project_id,rp.paper_id FROM r.project_paper rp JOIN projects p USING(project_id)')
 q('CREATE TABLE project_patent AS SELECT DISTINCT rp.project_id,rp.application_id FROM r.project_patent rp JOIN projects p USING(project_id)')
 # Only newly registered paper records: match exact normalized title to the AI
 # canonical corpus, require a uniquely matched identity and author corroboration.
 q("CREATE TABLE new_papers AS SELECT *,"+norm+" title_key FROM f.ai_fund_outcome WHERE link_status='source_registered' AND outcome_type='paper'")
 q("CREATE TABLE new_paper_candidates AS SELECT n.source_record_id,n.project_id,n.title,n.authors_raw,n.publication_year original_year,p.paper_id,p.publication_year,p.authors_json FROM new_papers n JOIN p.ai_paper p ON n.title_key="+norm.replace('title,','p.title,')+" WHERE length(n.title_key)>=16")
 candidates={}
 for row in q('select * from new_paper_candidates').fetchall():candidates.setdefault(row[0],[]).append(row)
 matched=[];rejected=[]
 def author_tokens(s):
  return set(t.lower() for t in re.findall(r'[A-Za-z]{3,}|[\u4e00-\u9fff]{2,}',s or '') if t.lower() not in {'name','author','null','family','given','raw','orcid'})
 for sid,rows in candidates.items():
  valid=[]
  for row in rows:
   _,pid,title,authors,oy,paper,year,pauth=row
   tokens=author_tokens(authors)&author_tokens(pauth)
   if (any(re.search(r'[\u4e00-\u9fff]',t) for t in tokens) or len(tokens)>=2) and (not oy or not re.fullmatch(r'\d{4}',str(oy)) or int(oy)==year):valid.append(row)
  ids={r[6-1] for r in valid}
  if len(ids)==1:matched.append(valid[0])
  else:rejected.append({'source_record_id':sid,'candidate_count':len(rows),'accepted_count':len(ids)})
 q('CREATE TABLE supplemental_paper_links(source_record_id VARCHAR,project_id VARCHAR,paper_id VARCHAR,basis VARCHAR)')
 q('DELETE FROM supplemental_paper_links')
 if matched:con.executemany('insert into supplemental_paper_links values(?,?,?,?)',[(r[0],r[1],r[5],'normalized_exact_title_author_year_unique_ai_identity') for r in matched])
 q('INSERT INTO project_paper SELECT DISTINCT s.project_id,s.paper_id FROM supplemental_paper_links s JOIN projects p USING(project_id) ANTI JOIN project_paper pp ON pp.project_id=s.project_id AND pp.paper_id=s.paper_id')
 # Registered patent strings require title AND inventor corroboration, unique application.
 q("CREATE TABLE new_patent_candidates AS SELECT n.source_record_id,n.project_id,n.authors_raw,p.application_id,p.inventor_names FROM f.ai_fund_outcome n JOIN r.patent p ON regexp_replace(lower(n.title),'[^a-z0-9一-龥]','','g')="+norm.replace('title,','p.title,')+" WHERE n.link_status='source_registered' AND n.outcome_type='patent' AND length(n.title)>10")
 pc={}
 for row in q('select * from new_patent_candidates').fetchall():
  if author_tokens(row[2])&author_tokens(row[4]):pc.setdefault((row[0],row[1]),set()).add(row[3])
 q('CREATE TABLE supplemental_patent_links(source_record_id VARCHAR,project_id VARCHAR,application_id VARCHAR,basis VARCHAR)')
 vals=[(sid,pid,next(iter(ids)),'normalized_exact_title_inventor_unique_application') for (sid,pid),ids in pc.items() if len(ids)==1]
 q('DELETE FROM supplemental_patent_links')
 if vals:con.executemany('insert into supplemental_patent_links values(?,?,?,?)',vals)
 q('INSERT INTO project_patent SELECT DISTINCT s.project_id,s.application_id FROM supplemental_patent_links s JOIN projects p USING(project_id) ANTI JOIN project_patent pp ON pp.project_id=s.project_id AND pp.application_id=s.application_id')
 log('Classifying paper reference set and fund-associated works using shared rules')
 q("CREATE TABLE paper_reference AS SELECT paper_id,title,publication_year AS year,lower(concat_ws(' ',title,keywords_json,substr(abstract,1,4000))) txt FROM p.ai_paper WHERE publication_year BETWEEN 2017 AND 2025")
 q('ALTER TABLE paper_reference ADD COLUMN categories VARCHAR[]');q('UPDATE paper_reference SET categories='+expr('txt'))
 log('Materializing canonical identities before reading paper text')
 q('CREATE TABLE linked_catalog AS SELECT p.paper_id,p.title,p.publication_year FROM p.paper_catalog p SEMI JOIN project_paper pp USING(paper_id)')
 q("CREATE TABLE linked_paper AS SELECT p.paper_id,coalesce(e.publication_year,a.publication_year,p.publication_year) AS year,p.title,lower(concat_ws(' ',p.title,coalesce(e.keywords_json,a.keywords_json),substr(coalesce(e.abstract,a.abstract),1,4000))) txt FROM linked_catalog p LEFT JOIN p.ai_paper a USING(paper_id) LEFT JOIN p.paper_enrichment e USING(paper_id)")
 q('ALTER TABLE linked_paper ADD COLUMN categories VARCHAR[]');q('UPDATE linked_paper SET categories='+expr('txt'))
 q('CREATE TABLE funded_paper AS SELECT * FROM linked_paper p WHERE year BETWEEN 2017 AND 2025 AND EXISTS(SELECT 1 FROM project_paper pp JOIN projects pr USING(project_id) WHERE pp.paper_id=p.paper_id AND p.year>=coalesce(pr.start_year,pr.approval_year))')
 log('Classifying patent reference set; one record per application')
 q("CREATE TABLE patent_representative AS SELECT publication_id FROM t.ai_patent WHERE application_id IS NOT NULL AND year(application_date) BETWEEN 2017 AND 2025 QUALIFY row_number() OVER(PARTITION BY application_id ORDER BY has_patsnap DESC,length(coalesce(abstract,'')) DESC,publication_date,publication_id)=1")
 q("CREATE TABLE patent_reference AS SELECT application_id,year(application_date) AS year,title,lower(concat_ws(' ',title,substr(abstract,1,4000),substr(first_claim,1,2000))) txt,regexp_matches(lower(coalesce(applicant_types,'')||' '||coalesce(current_owner_types,'')),'企业|公司|company|corporation') enterprise FROM t.ai_patent SEMI JOIN patent_representative USING(publication_id)")
 q('ALTER TABLE patent_reference ADD COLUMN categories VARCHAR[]');q('UPDATE patent_reference SET categories='+expr('txt'))
 q('CREATE TABLE funded_patent AS SELECT * FROM patent_reference p WHERE EXISTS(SELECT 1 FROM project_patent pp JOIN projects pr USING(project_id) WHERE pp.application_id=p.application_id AND p.year>=coalesce(pr.start_year,pr.approval_year))')
 log('Computing citations to the same paper cohort (citing years through 2025)')
 q('CREATE TABLE fund_citation AS SELECT e.* FROM r.citation_edge e JOIN funded_paper p ON e.cited_paper_id=p.paper_id WHERE e.citing_year BETWEEN 2017 AND 2025 AND e.citing_year>=p.year')
 q('CREATE TABLE citation_per_paper AS SELECT p.paper_id,p.year,count(e.citation_edge_id) citations,count(e.citation_edge_id) FILTER(WHERE e.citing_year BETWEEN p.year+1 AND p.year+3) citations_3y,count(e.citation_edge_id) FILTER(WHERE e.citing_year>=p.year+4) later_citations FROM funded_paper p LEFT JOIN fund_citation e ON e.cited_paper_id=p.paper_id GROUP BY p.paper_id,p.year')
 q('CREATE TABLE patent_cited AS SELECT DISTINCT link.paper_id,pa.application_id,year(pa.application_date) application_year FROM r.patent_paper_link_all link JOIN r.patent pa USING(publication_id) JOIN funded_paper fp USING(paper_id) WHERE year(pa.application_date) BETWEEN fp.year AND 2025')
 years=list(range(2017,2026));results=[]
 def where(cid,col='categories'):return '' if cid=='all' else f' WHERE list_contains({col},{lit(cid)})'
 def arr(sql,default=0):
  d=dict(q(sql).fetchall());return [d.get(y,default) for y in years]
 def n(sql):return scalar(sql) or 0
 for cid in ['all',*names]:
  flt=where(cid)
  q('CREATE OR REPLACE TEMP VIEW ps AS SELECT * FROM projects'+flt)
  q('CREATE OR REPLACE TEMP VIEW papers AS SELECT * FROM funded_paper'+flt)
  q('CREATE OR REPLACE TEMP VIEW patents AS SELECT * FROM funded_patent'+flt)
  weight='1.0' if cid=='all' else '1.0/len(p.categories)'
  active=[q(f'SELECT coalesce(sum(funding_wan*{weight}),0),count(*) FROM ps p WHERE start_year<={y} AND end_year>={y}').fetchone() for y in years]
  approved=n(f'SELECT sum(funding_wan*{weight}) FROM ps p')
  citations='SELECT e.* FROM fund_citation e SEMI JOIN papers p ON e.cited_paper_id=p.paper_id'
  q('CREATE OR REPLACE TEMP VIEW cites AS '+citations)
  q('CREATE OR REPLACE TEMP VIEW cited_stats AS SELECT c.* FROM citation_per_paper c JOIN papers p USING(paper_id)')
  q('CREATE OR REPLACE TEMP VIEW tech_cites AS SELECT pc.* FROM patent_cited pc SEMI JOIN papers p USING(paper_id)')
  means=arr('SELECT year,avg(citations_3y) FROM cited_stats WHERE year<=2022 GROUP BY year',None)
  s={'active_funding_wan':[round(a[0],3) for a in active],'active_projects':[a[1] for a in active],
   'funded_papers':arr('SELECT year,count(*) FROM papers GROUP BY year'),'funded_patents':arr('SELECT year,count(*) FROM patents GROUP BY year'),
   'all_papers':arr('SELECT year,count(*) FROM (SELECT paper_id,year FROM paper_reference'+flt+' UNION SELECT paper_id,year FROM papers) GROUP BY year'),'all_patents':arr('SELECT year,count(*) FROM patent_reference'+flt+' GROUP BY year'),
   'paper_citations':arr('SELECT citing_year,count(*) FROM cites GROUP BY citing_year'),'mean_citations_3y':[round(v,3) if v is not None else None for v in means],
   'enterprise_patents':arr('SELECT year,count(*) FROM patents WHERE enterprise GROUP BY year')}
  eligible=n('SELECT count(*) FROM cited_stats WHERE year<=2022')
  totals={'approved_funding_wan':round(approved,3),'project_count':n('SELECT count(*) FROM ps'),'funded_papers':n('SELECT count(*) FROM papers'),'funded_patents':n('SELECT count(*) FROM patents'),
   'all_papers':sum(s['all_papers']),'all_patents':sum(s['all_patents']),'paper_citations':n('SELECT count(*) FROM cites'),'cited_papers':n('SELECT count(*) FROM cited_stats WHERE citations>0'),
   'mean_citations_3y':round(n('SELECT avg(citations_3y) FROM cited_stats WHERE year<=2022'),3) if eligible else None,
   'enterprise_patents':n('SELECT count(*) FROM patents WHERE enterprise'),'patent_cited_papers':n('SELECT count(distinct paper_id) FROM tech_cites'),'citing_patent_applications':n('SELECT count(distinct application_id) FROM tech_cites'),
   'papers_cited_after_3y':n('SELECT count(*) FROM cited_stats WHERE year<=2021 AND later_citations>0'),'papers_eligible_after_3y':n('SELECT count(*) FROM cited_stats WHERE year<=2021')}
  coverage={'citation_eligible_papers':eligible,'projects_with_amount':n('SELECT count(*) FROM ps WHERE funding_wan IS NOT NULL'),'projects_with_execution_years':n('SELECT count(*) FROM ps WHERE start_year IS NOT NULL AND end_year IS NOT NULL')}
  results.append({'id':cid,'name':names.get(cid,'全部方向'),'series':s,'totals':totals,'coverage':coverage,'notes':['项目批准经费跨方向等额分摊；成果在方向内去重，可跨方向出现。','篇均被引：2017—2022年论文发表后1—3年在本地引文库的引用次数，包含零引证论文。']})
 log('Validating partitions and publishing aggregate snapshot')
 assert all(len(v)==9 for item in results for v in item['series'].values())
 assert n('SELECT count(*) FROM projects')==n('SELECT count(distinct project_id) FROM projects')
 assert n('SELECT count(*) FROM funded_paper')==n('SELECT count(distinct paper_id) FROM funded_paper')
 assert n('SELECT count(*) FROM funded_patent')==n('SELECT count(distinct application_id) FROM funded_patent')
 unclassified_funding=n('SELECT sum(funding_wan) FROM projects WHERE len(categories)=0')
 assert abs(sum(item['totals']['approved_funding_wan'] for item in results[1:])+unclassified_funding-results[0]['totals']['approved_funding_wan'])<.1
 for row in results:
  for key in ('funded_papers','funded_patents','paper_citations','enterprise_patents'):
   assert sum(row['series'][key])==row['totals'][key],(row['id'],key)
  assert row['totals']['enterprise_patents']<=row['totals']['funded_patents']
  assert row['totals']['cited_papers']<=row['totals']['funded_papers']
 assert n('SELECT count(*) FROM fund_citation')==n('SELECT count(distinct citation_edge_id) FROM fund_citation')
 # Same source classification means reference numerator is a true subset wherever
 # the canonical paper belongs to the provider's AI reference selection.
 quality={'projects':results[0]['totals']['project_count'],'all_ai_projects':n('SELECT count(*) FROM f.ai_project'),
  'unclassified_funding_wan':unclassified_funding,'unclassified_projects':n('SELECT count(*) FROM projects WHERE len(categories)=0'),'unclassified_papers':n('SELECT count(*) FROM funded_paper WHERE len(categories)=0'),'unclassified_patents':n('SELECT count(*) FROM funded_patent WHERE len(categories)=0'),
  'linked_papers_missing_year':n('SELECT count(*) FROM linked_paper WHERE year IS NULL'),'supplemental_paper_links':n('SELECT count(*) FROM supplemental_paper_links'),'supplemental_patent_links':n('SELECT count(*) FROM supplemental_patent_links'),
  'annual_projects':q('SELECT approval_year,count(*),count(funding_wan) FROM projects GROUP BY 1 ORDER BY 1').fetchall(),
  'paper_link_total':n('SELECT count(*) FROM project_paper'),'project_patent_link_total':n('SELECT count(*) FROM project_patent'),
  'method':'own title + keywords + first 4000 abstract characters; patent first-claim first 2000; guarded broad rules, not inheritance',
  'citation_scope':'local canonical citation edges; citing years 2017–2025; publication cohort 2017–2025; 3-year averages only publication2017–2022',
  'funding_scope':'approved 2017–2025 known-year AI project cohort; active stock uses actual execution years, never completion date as approval year'}
 data={'version':'innovation_dashboard_20261110_v1','as_of':'2026-11-10','years':years,'cohort':{'label':'2017—2025年立项项目 · 成果观察至2025年','project_count':quality['projects'],'approved_funding_wan':results[0]['totals']['approved_funding_wan']},'all':results[0],'categories':results[1:],'representative_progress':[],
  'unavailable':{'journal_if':'尚无逐期刊逐年授权影响因子表','product_links':'尚无可核验的专利—产品关联','patent_transfers':'尚无结构化转让许可事件'},'methodology':quality,'source_versions':paths,'input_fingerprint':fingerprint}
 for name,value in [('analysis-metrics.json',data),('quality.json',quality),('classification_rules.json',{'version':'own_text_broad_seven_20261110_v1','rules':rules,'ai_context':ai}),('identity_match_review.json',{'rejected_paper_candidates':rejected})]:
  tmp=out/(name+'.tmp');tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n');tmp.replace(out/name)
 con.execute('CHECKPOINT');con.close()
 log(json.dumps({'all':results[0],'quality':quality},ensure_ascii=False))
if __name__=='__main__':main()
