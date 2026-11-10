"""Fund-linked impact distribution and traceable project-paper examples."""
import json,sys,argparse,math,os
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 root=Path('/root/gzk_jc');sys.path.insert(0,str(root/'data/runs/shared/patent_unified/patent_unified_20261030_v1/deps'))
 if sys.version_info[:2]!=(3,13):os.execv('/root/anaconda3/bin/python',['/root/anaconda3/bin/python',__file__,*sys.argv[1:]])
 import duckdb
 c=duckdb.connect(str(root/'data/runs/shared/innovation_dashboard/chain_fill_20261110_v1/metrics_v2/analysis.duckdb'),read_only=True)
 rows={}
 for cat in ['all',*[f'AI{i}' for i in range(1,8)]]:
  filt='' if cat=='all' else f" AND list_contains(f.categories,'{cat}')"
  papers=c.execute('SELECT f.paper_id,f.title,f.year,coalesce(v.citations_3y,0),f.categories FROM funded_paper f LEFT JOIN citation_per_paper v USING(paper_id) WHERE f.year<=2022'+filt).fetchall()
  annual=[];topids=set();cit=0;topcit=0
  for y in range(2017,2023):
   ps=sorted([r for r in papers if r[2]==y],key=lambda r:-r[3]);n=len(ps);threshold=ps[max(0,math.ceil(n*.1)-1)][3] if n else 0
   high=[r for r in ps if r[3]>=threshold and r[3]>0];total=sum(r[3] for r in ps);hc=sum(r[3] for r in high)
   topids.update(r[0] for r in high);cit+=total;topcit+=hc
   annual.append(dict(year=y,papers=n,high=len(high),threshold=threshold,citations=total,high_citations=hc,share=round(hc/total*100,1) if total else None))
  cases=[]
  for r in sorted(papers,key=lambda r:-r[3]):
   grants=c.execute('select distinct p.grant_no,p.title,p.institution,p.approval_year from project_paper pp join projects p using(project_id) where pp.paper_id=? order by p.approval_year,p.grant_no',[r[0]]).fetchall()
   if not grants:continue
   cases.append(dict(paper_id=r[0],title=r[1],year=r[2],citations_3y=r[3],grants=[dict(number=g[0],title=g[1],institution=g[2],year=g[3]) for g in grants]))
   if len(cases)>=4:break
  rows[cat]=dict(papers=len(papers),high_papers=len(topids),paper_share=round(len(topids)/len(papers)*100,1) if papers else 0,citation_share=round(topcit/cit*100,1) if cit else 0,annual=annual,cases=cases)
 data=dict(categories=rows,years=list(range(2017,2023)),method='Within each publication year and selected funded-paper cohort, rank by citations in years 1–3; retain top decile with tied positive counts. Not a worldwide top-decile ranking. Cases ordered by observed 3-year citations; fund links are registered/matched relationships, not causal attribution.')
 a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print({k:{f:v[f] for f in ['papers','high_papers','paper_share','citation_share']} for k,v in rows.items()})
if __name__=='__main__':main()
