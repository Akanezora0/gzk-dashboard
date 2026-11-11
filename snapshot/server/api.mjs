import fs from 'node:fs/promises'
import {readFileSync} from 'node:fs'
import path from 'node:path'
import {gunzipSync} from 'node:zlib'
import {contribution} from './contribution.mjs'
export function canonical(url) {
 const u=new URL(url,'http://localhost');u.searchParams.sort()
 return u.pathname+(u.searchParams.size?'?'+u.searchParams.toString():'')
}
const lowerAscii=s=>String(s??'').replace(/[A-Z]/g,c=>c.toLowerCase())
// 展示整理：去掉知网题名尾部的“附视频”等标记；按领域相关度排序，重复题名后置（技术词表命中 > 核心词 > 泛化词，题名命中 > 关键词 > 摘要），同分按年份新到旧
const TERM_WEIGHT=id=>id==='core'?6:/^T\d/.test(String(id))?5:id==='context'?1.5:1
const FIELD_WEIGHT={title:3,keywords:2,abstract:1}
function cleanRecord(r){if(typeof r.title==='string')r.title=r.title.replace(/\s*附视频\s*$/,'').replace(/\s{2,}/g,' ').trim()}
function rankByRelevance(list){
 const score=r=>(r.evidence||[]).reduce((s,e)=>s+TERM_WEIGHT(e.term_id)*(FIELD_WEIGHT[e.field]||1),0)+(r.matched_terms||[]).length
 // 重复题名（同题名同年份）排到末尾，总数不变
 const seen=new Map(),dup=r=>{const k=`${r.title}|${r.year}`,n=seen.get(k)||0;seen.set(k,n+1);return n}
 const keyed=list.map((r,i)=>({r,i,d:dup(r),s:score(r),y:Number(r.year)||0}))
 keyed.sort((a,b)=>a.d-b.d||b.s-a.s||b.y-a.y||a.i-b.i)
 keyed.forEach((k,i)=>{list[i]=k.r})
}
const invalid=message=>({status:400,body:{error:message}})
export function createSnapshotApi(root) {
 const index=JSON.parse(readFileSync(path.join(root,'api/index.json'),'utf8')).responses
 const manifest=JSON.parse(readFileSync(path.join(root,'records/manifest.json'),'utf8'))
 let cachedNamespace,cachedRows,pendingRows,contributionRows,contributionMeta,contributionLoad
 // Keep one source collection in memory. All other namespace shards stay compressed on disk.
 async function rows(namespace) {
  if(namespace===cachedNamespace&&cachedRows)return cachedRows
  while(pendingRows){await pendingRows;if(namespace===cachedNamespace&&cachedRows)return cachedRows}
  if(namespace===cachedNamespace&&cachedRows)return cachedRows
  const spec=manifest.namespaces.find(n=>n.namespace===namespace)
  if(!spec)return null
  const loading=(async()=>{
   cachedRows=null;cachedNamespace=null
   const result=[]
   for(const part of spec.parts){const raw=gunzipSync(await fs.readFile(path.join(root,'records',part.file))).toString('utf8');for(const line of raw.split('\n'))if(line)result.push(JSON.parse(line))}
   result.forEach(cleanRecord);rankByRelevance(result)
   cachedNamespace=namespace;cachedRows=result;return result
  })()
  pendingRows=loading
  try{return await loading}finally{if(pendingRows===loading)pendingRows=null}
 }
 return async input=>{
  const u=new URL(input,'http://localhost'),q=u.searchParams
  if(u.pathname==='/api/llm/records') {
   const namespace=q.get('namespace')||'cnki_paper',scope=q.get('scope')||'llm'
   if(scope!=='ai')return {status:422,body:{error:'Snapshot record projection covers scope=ai; use live mode for other scopes.'}}
   const offset=Number(q.get('offset')||0),limit=Number(q.get('limit')||20),term=q.get('q')||''
   if(!Number.isInteger(offset)||offset<0||offset>300000||!Number.isInteger(limit)||limit<1||limit>50||term.length>100)return invalid('Invalid pagination or query')
   const all=await rows(namespace);if(!all)return invalid('Unknown namespace')
   const needle=lowerAscii(term),filtered=needle?all.filter(r=>lowerAscii(r.title).includes(needle)):all
   return {status:200,body:{rows:filtered.slice(offset,offset+limit),total:filtered.length,offset,limit,namespace,scope,version:manifest.source_version}}
  }
  if(u.pathname==='/api/low-altitude/contribution') {
   if(!contributionLoad)contributionLoad=Promise.all([fs.readFile(path.join(root,'contribution/rows.json.gz')),fs.readFile(path.join(root,'contribution/metadata.json'),'utf8')]).then(([raw,meta])=>{contributionRows=JSON.parse(gunzipSync(raw));contributionMeta=JSON.parse(meta)}).catch(error=>{contributionLoad=null;throw error})
   await contributionLoad
   return {status:200,body:contribution(contributionRows,contributionMeta,q)}
  }
  if(u.pathname==='/api/llm/analytics'){if(!q.has('scope'))q.set('scope','llm');if(!q.has('namespace'))q.set('namespace','cnki_paper')}
  if(u.pathname==='/api/llm/chain-summary'&&!q.has('scope'))q.set('scope','ai')
  if(u.pathname==='/api/llm/graph'){if(!q.has('scope'))q.set('scope','ai');if(!q.has('chain'))q.set('chain','paper_tech');if(!q.has('limit'))q.set('limit','20')}
  if(u.pathname==='/api/low-altitude/chain'){
   if(q.get('aggregate')==='true'){q.set('chain_type','aggregate_overview');q.set('limit','30')}
   if(q.get('chain_type')==='aggregate_overview')q.set('aggregate','true')
  }
  const entry=index[canonical(u)]
  if(!entry)return {status:404,body:{error:'This API/query is not in the current display snapshot',path:canonical(u)}}
  return {status:entry.status,body:JSON.parse(await fs.readFile(path.join(root,'api',entry.file),'utf8'))}
 }
}
