"""Publish the confirmed 80-topic evolution view without changing research cohorts.

Run through manage.py in the research workspace. Inputs are immutable versioned
lexicon, previous evolution data, and the checked survey publication index.
"""
import argparse
import copy
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

LABELS = {
 'R01':'Mamba','R02':'Mamba-2','R03':'Kimi Linear','R04':'线性注意力',
 'R05':'World Models','R06':'Genie','R07':'Genie 3','R08':'MDLM','R09':'LLaDA',
 'R10':'Engram','R11':'mHC','R12':'上下文工程','R13':'RAGEN','R14':'Agent Lightning',
 'R15':'SWE-RL','R16':'Qwen3','R18':'DeepSeek-V3','R19':'DistServe','R20':'Mooncake',
 'R21':'长程智能体运行框架','R22':'Harness Engineering','R23':'长程应用开发框架',
 'R24':'MCP','R25':'A2A','R26':'A2A 基金会项目','R27':'Agent Skills',
 'R28':'Agent Skills 基金会项目','R29':'OSWorld','R30':'Computer Use',
 'R31':'Gemini Deep Research','R32':'Deep Research','R33':'SWE-agent',
 'R34':'Claude Code','R35':'AutoGen','R36':'Magentic-One','R37':'MemGPT',
 'R38':'A-MEM','R39':'Mem0','R40':'AgentDojo','R41':'长程任务能力评测',
 'R42':'π0','R43':'DeepSeekMath','R44':'DeepSeek-R1','R45':'原生稀疏注意力',
 'R46':'DeepSeek-V2','R47':'GraphRAG','R48':'OpenAI o1','R49':'Sora','R50':'4o 图像生成',
}
FEATURED = {
 'R06':('世界模型','学习环境与交互规律','从视频学习环境表示、潜在动作与动态变化，生成可交互环境。','让模型能够模拟行动带来的环境变化，为交互学习提供支撑。'),
 'R22':('Harness','智能体运行环境与反馈','围绕工具、运行环境、任务约束和反馈回路组织智能体执行过程。','把模型能力组织为可持续运行、可检查和可迭代的任务系统。'),
 'R13':('智能体强化学习','从多轮交互中学习','通过智能体与环境的多轮交互和奖励反馈，训练任务决策与执行策略。','推动智能体在复杂任务中改进规划、工具使用与执行能力。'),
 'R36':('多智能体协作','分工、协调与共同执行','由多个智能体分担任务，通过协调机制组织规划、工具操作与结果核查。','使复杂任务可以由具有不同职责的智能体共同完成。'),
 'R38':('智能体长期记忆','积累经验并持续调用','对交互经验进行组织、连接和检索，使记忆随任务过程更新。','支持智能体跨任务复用经验、保持上下文并形成持续积累。'),
}

def read(p): return json.loads(Path(p).read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def urlkey(u): return str(u).replace('http://','https://').rstrip('/')

def build(lexicon_path,tree_path,chronology_path,survey_index_path,output):
 assert not output.exists(), 'Use a fresh output directory'
 lex=read(lexicon_path); old_tree=read(tree_path); old_chron=read(chronology_path); surveys=read(survey_index_path)
 terms={t['topic_id']:t for t in lex['terms']}
 old_ids={n['id'] for n in old_tree['nodes'] if n['node_type']=='technology'}
 added=set(terms)-old_ids
 assert len(terms)==80 and len(added)==10 and len(old_ids)==70
 entries=[e for e in surveys['entries'] if e['route']=='B']
 assert {e['topic_id'] for e in entries}==added and all(e['ready_for_dashboard'] for e in entries)
 tree=copy.deepcopy(old_tree)
 for tid in sorted(added):
  t=terms[tid]
  tree['nodes'].append(dict(id=tid,keyword_id=t['keyword_id'],parent_id=t['parent_id'],category_id=t['category_id'],node_type='technology',level=3,label=t['name'],level2=t['level2'],definition=t['definition'],aliases=t['aliases'],survey_enabled=True))
 tree.update(keyword_version=lex['version'],keyword_sha256=sha(lexicon_path),counts=dict(categories=7,groups=29,topics=80))
 events=copy.deepcopy(old_chron['events']); edges=copy.deepcopy(old_chron['edges'])
 seen={(urlkey(e.get('url')),e.get('first_public_date')):e['id'] for e in events}
 by_source={}; merges=[]
 def add(source_id,spec,topic_ids):
  source=lex['sources'][source_id]; date=spec.get('date',source['date']); key=(urlkey(source['url']),date)
  if key in seen:
   by_source[source_id]=seen[key];merges.append(dict(source_id=source_id,existing_event=seen[key]));return
  tid=next((tid for tid in topic_ids if tid in added),topic_ids[0]);t=terms[tid]
  label=LABELS.get(source_id,t['name'])
  if spec.get('event_id')=='EV5-R27-open':label='Agent Skills 开放标准'
  event_id='evolution_v6_'+spec.get('event_id',source_id)
  event=dict(id=event_id,topic_id=tid,topic_label=t['name'],label=label,year=int(date[:4]),first_public_date=date,
    category_id=t['category_id'],group=t['category_id'],group_id=t['parent_id'],title=source['title'],url=source['url'],
    summary=spec.get('description') or source.get('verification_note') or t['definition'],
    date_role='representative_work_publication',date_basis=spec.get('event_type',source.get('date_kind','公开日期')),
    source_id=source_id,related_topic_ids=[x for x in topic_ids if x!=tid],source_urls=[source['url']],
    review_status='existing_lexicon_source_checked',evidence_note=source.get('verification_note',''),
    verification_scope=source.get('read_scope'),checked_at=source.get('checked_at'),
    featured=source_id in FEATURED,primary_for_topic=not any(e['topic_id']==tid for e in events))
  events.append(event);seen[key]=event_id;by_source[source_id]=event_id
 for spec in lex['events']:add(spec['source_id'],spec,spec['topic_ids'])
 # Preserve earlier research seeds: recent additions are not technology origin claims.
 for tid in sorted(added):
  for seed in terms[tid].get('seed_metadata',[]):
   sid=seed['evidence_id']
   if sid not in by_source:add(sid,{},[tid])
 # Resolve curated relationship endpoints against preserved events and source IDs.
 relation_path=Path(__file__).with_name('evolution_recent_relations.json')
 curated=read(relation_path)
 event_by_id={e['id']:e for e in events}
 # A source may have several release events; prefer its first publication.
 source_first={}
 for event in sorted(events,key=lambda e:e.get('first_public_date','')):
  if event.get('source_id'):source_first.setdefault(event['source_id'],event['id'])
 pairs={(e['source'],e['target']) for e in edges}
 for index,spec in enumerate(curated['relations'],1):
  src=source_first.get(spec['source'],spec['source']);dst=source_first.get(spec['target'],spec['target'])
  assert src in event_by_id and dst in event_by_id, spec
  assert src!=dst and (src,dst) not in pairs, spec
  assert event_by_id[src]['year']<=event_by_id[dst]['year'], spec
  evidence=lex['sources'][spec['evidence_source']]
  edges.append(dict(id=f'recent_relation_{index:02d}',source=src,target=dst,
   kind=spec['kind'],label=spec['label'],source_url=evidence['url'],
   evidence_note=spec['evidence_note'],evidence_source=spec['evidence_source'],
   interpretation='research_direction_synthesis' if spec['kind']=='research_direction' else 'source_supported',
   relation_version=curated['version']))
  pairs.add((src,dst))
 events.sort(key=lambda e:(e.get('first_public_date') or str(e['year']),e['id']))
 additions=[];stories={}
 for sid,(name,note,innovation,impact) in FEATURED.items():
  eid=by_source[sid];additions.append(dict(id=eid,name=name,note=note));stories[eid]=dict(innovation=innovation,impact=impact)
 chron=dict(old_chron,events=events,edges=edges,topic_count=80,work_count=len({urlkey(e['url']) for e in events}),
   keyword_sha256=sha(lexicon_path),featured_additions=additions,featured_stories=stories,
   year_semantics='代表成果的公开年份；论文、技术报告与官方发布按原来源日期记录。',
   created_at=datetime.now(timezone.utc).isoformat())
 ids={e['id'] for e in events};topics={e['topic_id'] for e in events}
 assert len(ids)==len(events) and topics==set(terms)
 assert all(e['source'] in ids and e['target'] in ids for e in edges)
 assert all(0 < e['year'] <= 2026 for e in events)
 assert [n for n in tree['nodes'] if n['id'] not in added]==old_tree['nodes']
 assert all(next(x for x in events if x['id']==e['id'])==e for e in old_chron['events'])
 version='evolution80-20261110-v3'
 result=dict(version=version,tree=tree,chronology=chron,survey_additions=entries,
   source_versions=dict(lexicon=lex['version'],survey=surveys['batch_id']),
   input_sha256={str(p):sha(p) for p in [lexicon_path,tree_path,chronology_path,survey_index_path,relation_path]})
 write(output/'evolution.json',result)
 quality=dict(passed=True,version=version,topics=len(terms),new_topics=sorted(added),surveys_added=len(entries),
   chronology_events=len(events),old_events_preserved=len(old_chron['events']),old_relations_preserved=len(old_chron['edges']),new_relations=len(curated['relations']),total_relations=len(edges),
   featured_added=len(additions),last_year=max(e['year'] for e in events),deduplicated=merges,
   output_sha256=sha(output/'evolution.json'))
 write(output/'quality.json',quality)
 print(json.dumps(quality,ensure_ascii=False))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 for key in ['lexicon','tree','chronology','survey-index','output']:p.add_argument('--'+key,type=Path,required=True)
 a=p.parse_args();build(a.lexicon,a.tree,a.chronology,a.survey_index,a.output)
