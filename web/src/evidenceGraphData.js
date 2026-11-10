// The pool contains complete evidence chains. Display budgets never split a chain.
let bundlePromise
export function loadEvidenceGraphs(){
 if(!bundlePromise)bundlePromise=fetch('/chain-analysis/v1/evidence-graphs.json').then(async r=>{
  if(!r.ok)throw new Error(`证据图读取失败（${r.status}）`)
  const value=await r.json()
  if(value.meta?.schema_version!==1||!value.graphs)throw new Error('证据图数据格式不完整')
  return value
 }).catch(e=>{bundlePromise=null;throw e})
 return bundlePromise
}

export function selectEvidenceGraph(source,category='all',nodeBudget=90,offset=0){
 if(!source)return {nodes:[],edges:[],meta:{has_more:false}}
 const nodeMap=new Map(source.nodes.map(n=>[n.id,n])),edgeMap=new Map(source.edges.map(e=>[e.id,e]))
 const eligible=(source.bundles||[]).filter(b=>category==='all'||b.category_ids.includes(category))
 const categories=new Map()
 for(const b of eligible){
  const isMethod=b.edge_ids.some(id=>edgeMap.get(id)?.kind==='actual_resource_use')
  const cat=isMethod?'methods':(category==='all'?b.category_ids[0]||'other':category)
  if(!categories.has(cat))categories.set(cat,new Map())
  const groups=categories.get(cat)
  const kind=b.node_ids.some(id=>nodeMap.get(id)?.type==='patent')?'patent':'paper'
  const key=(b.term_id||'method')+':'+kind
  if(!groups.has(key))groups.set(key,[])
  groups.get(key).push(b)
 }
 // Round-robin over categories, then terms and outcome kinds within each category.
 const queues=[...categories.entries()].sort(([a],[b])=>a.localeCompare(b)).map(([,groups])=>{
  const parts=[...groups.values()],queue=[]
  for(let i=0;parts.some(p=>i<p.length);i++)for(const part of parts)if(part[i])queue.push(part[i])
  return queue
 })
 const ordered=[]
 for(let i=0;queues.some(q=>i<q.length);i++)for(const queue of queues)if(queue[i])ordered.push(queue[i])
 const start=ordered.length?offset%ordered.length:0
 const windowOrder=ordered.slice(start).concat(ordered.slice(0,start))
 const nodeIds=new Set(),edgeIds=new Set();let selected=0
 for(const b of windowOrder){
  const fresh=b.node_ids.filter(id=>!nodeIds.has(id))
  if(nodeIds.size+fresh.length>nodeBudget)continue
  for(const id of b.node_ids)nodeIds.add(id)
  for(const id of b.edge_ids)edgeIds.add(id)
  selected++
 }
 return {nodes:source.nodes.filter(n=>nodeIds.has(n.id)),edges:source.edges.filter(e=>edgeIds.has(e.id)),meta:{...source.meta,nodes:nodeIds.size,edges:edgeIds.size,category,offset:start,selected_bundles:selected,eligible_bundles:eligible.length,node_budget:nodeBudget,has_more:selected<eligible.length}}
}

export function evidenceSummary(bundle){
 const counts=bundle.meta.population_counts,stats=bundle.meta.scan_stats
 const matches=type=>Object.values(stats[type]?.matching_records_by_term||{}).reduce((a,b)=>a+b,0)
 return {chains:[{id:'fund_paper',count:counts.ai_fund_paper_edges},{id:'fund_patent',count:counts.ai_fund_patent_relation_rows},{id:'paper_tech',count:matches('paper')},{id:'patent_tech',count:matches('patent')},{id:'paper_network',count:counts.accepted_method_use_edges}],pipeline:[]}
}
