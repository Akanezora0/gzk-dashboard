export function validYear(value){
 const match=String(value??'').match(/^(19|20)\d{2}/);return match?Number(match[0]):null
}
export function projectTimeline(projects=[],papers=[]){
 const rows=[...projects].sort((a,b)=>(validYear(a.approval_year)??9999)-(validYear(b.approval_year)??9999)||String(a.grant_no).localeCompare(String(b.grant_no)))
 const years=rows.flatMap(p=>[validYear(p.approval_year),validYear(p.start_date),validYear(p.end_date)]).filter(y=>y!==null)
 const paperCounts=new Map();const seen=new Set()
 for(const p of papers){const y=validYear(p.publication_year);const id=p.paper_id||p.doi;if(y===null||!id||seen.has(id))continue;seen.add(id);years.push(y);paperCounts.set(y,(paperCounts.get(y)||0)+1)}
 if(!years.length)return {rows:[],years:[],paperCounts:[]}
 const min=Math.min(...years),max=Math.max(...years),span=max-min+1
 const x=y=>40+(y-min)/span*880
 return {rows:rows.map(p=>{const start=validYear(p.start_date),end=validYear(p.end_date),approval=validYear(p.approval_year);return {...p,start,end,approval,bar:start!==null&&end!==null&&end>=start?{x:x(start),width:x(end+1)-x(start)}:null,approvalX:approval===null?null:x(approval)+440/span}}),years:Array.from({length:span},(_,i)=>({year:min+i,x:x(min+i)+440/span})),paperCounts:[...paperCounts].sort((a,b)=>a[0]-b[0]).map(([year,count])=>({year,count,x:x(year)+440/span})),axisY:rows.length*54+22,height:rows.length*54+82}
}
