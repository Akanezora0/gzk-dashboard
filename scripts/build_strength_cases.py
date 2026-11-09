"""Expand the research evidence view from the read-only relation warehouse.
Run on the research server via manage.py run; snapshot is a published derivative.
"""
from pathlib import Path
from collections import Counter
import json, sys, hashlib, argparse

def enrich(payload, root, config_path=None):
    config_path = config_path or Path(__file__).with_name('strength_cases.json')
    config = json.loads(config_path.read_text())
    sys.path.insert(0, str(root/'data/runs/shared/patent_unified/patent_unified_20261030_v1/deps'))
    import duckdb
    db=root/'data/warehouse/shared/innovation/releases/innovation_relations_20261102_v1/relations.duckdb'
    c=duckdb.connect(str(db),read_only=True)
    c.execute("SET threads=2; SET memory_limit='2GB'")
    def rows(sql,args=None):
        q=c.execute(sql,args or []);names=[x[0] for x in q.description];return [dict(zip(names,r)) for r in q.fetchall()]
    orgs=config['institutions']
    c.execute('create temp table selected_projects as select * from project where is_ai and approval_year between 2017 and 2025 and institution in ('+','.join('?' for _ in orgs)+')',orgs)
    ps=rows('select project_id,grant_no,title,approval_year,project_type,institution,principal_investigator,start_date,end_date,completion_year as completion_year_in_library,is_ai,amount_raw,amount_unit,amount_cny_fen,abstract_zh,keywords_zh from selected_projects order by institution,approval_year,grant_no')
    es=rows('''select e.project_id,e.paper_id,e.evidence_count,e.bases,true as is_ai_project,p.approval_year as project_approval_year,a.publication_year as paper_publication_year,a.publication_year<p.approval_year as paper_year_before_project_approval_year,'project_paper' as source_table from project_paper e join selected_projects p using(project_id) join paper a using(paper_id) where a.publication_year between 2017 and 2025 order by e.project_id,e.paper_id''')
    papers=rows('''select distinct a.* from paper a join project_paper e using(paper_id) join selected_projects p using(project_id) where a.publication_year between 2017 and 2025 order by a.paper_id''')
    for p in papers:
        if p.get('doi'):p['doi_url']='https://doi.org/'+p['doi']
    hosts=rows("select distinct o.organization_id,o.canonical_name from organization o join project_organization_unique e using(organization_id) join selected_projects p using(project_id) where e.role='host'")
    org_map={o['canonical_name']:o['organization_id'] for o in hosts}
    pids={p['project_id'] for p in ps};paperids={p['paper_id'] for p in papers}
    assert len(pids)==len(ps) and len(paperids)==len(papers)
    assert len({(e['project_id'],e['paper_id']) for e in es})==len(es)
    assert all(e['project_id'] in pids and e['paper_id'] in paperids for e in es)
    payload['graph']=dict(project_nodes=ps,paper_nodes=papers,project_paper_edges=es,
      organization_nodes=[{'organization_id':org_map.get(o,o),'canonical_name':o} for o in orgs],
      institution_project_edges=[{'organization_id':org_map.get(p['institution'],p['institution']),'project_id':p['project_id'],'role':'host'} for p in ps],
      coverage_by_institution=[{'institution':o,'projects':sum(p['institution']==o for p in ps)} for o in orgs])
    chosen=[];profiles=[]
    for case in config['cases']:
        matches=[r for r in payload['continuity'] if r['person_name']==case['person_name'] and r['earlier_institution']==case['institution']]
        assert matches,case['person_name']
        assert len({r['person_id'] for r in matches})==1,case['person_name']
        profiles.append({**case,'person_id':matches[0]['person_id']})
        for i,r in enumerate(sorted(matches,key=lambda r:r['earlier_approval_year'])):
            assert r['earlier_project_id'] in pids and r['later_project_id'] in pids
            chosen.append({**case,'person_id':r['person_id'],'earlier_year':r['earlier_approval_year'],'later_year':r['later_approval_year'],
              'earlier_topic':case['headline'].split(' → ')[i],'later_topic':case['headline'].split(' → ')[i+1]})
    payload['strength']['cases']=chosen
    payload['strength']['case_profiles']=profiles
    payload['strength']['evidence_institution_order']=orgs
    payload['version']='ai-chain-curated-cases-20261109'
    payload['evidenceScope']={'project_years':[2017,2025],'paper_years':[2017,2025],'institutions':len(orgs),'projects':len(ps),'papers':len(papers),'relations':len(es)}
    c.close()
    return payload,{'database':str(db.relative_to(root)),'config_sha256':hashlib.sha256(config_path.read_bytes()).hexdigest(),'counts':payload['evidenceScope'],'cases':len(profiles),'checks':'passed'}

def main():
    from gzk.paths import ROOT
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    payload,meta=enrich(json.loads(a.input.read_text()),ROOT)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')))
    a.output.with_suffix('.provenance.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
    print(json.dumps(meta,ensure_ascii=False))
if __name__=='__main__':
    # Warehouse DuckDB wheel is pinned to Python 3.13; manage.py uses 3.12.
    if sys.version_info[:2] != (3,13):
        import subprocess, shutil
        raise SystemExit(subprocess.call([shutil.which('python'),str(Path(__file__).resolve()),*sys.argv[1:]]))
    main()
