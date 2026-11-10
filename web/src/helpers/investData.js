/* 布局动画沿用验收快照；对照与贡献使用独立统计口径的分析指标。 */
import {ref,onScopeDispose} from 'vue'
const BASE='/chain-analysis/v1/'
const cache={}
async function payload(file,id){
 if(!cache[file])cache[file]=fetch(BASE+file).then(r=>{if(!r.ok)throw new Error(file);return r.text()}).then(t=>new DOMParser().parseFromString(t,'text/html')).catch(e=>{delete cache[file];throw e})
 const doc=await cache[file];return JSON.parse(doc.querySelector(`script#${id}`)?.textContent||'null')
}
export const ORDER=['AI1','AI2','AI3','AI4','AI5','AI6','AI7']
/* 与网站辅助色一致的七大方向配色 */
export const PALETTE={AI1:'#a21535',AI2:'#2c64a0',AI3:'#23806e',AI4:'#8a8a8f',AI5:'#b2772a',AI6:'#6f4a94',AI7:'#c47a8a'}
const metricSeries=['active_funding_wan','active_projects','funded_papers','funded_patents','all_papers','all_patents','paper_citations','mean_citations_3y','enterprise_patents']
const numeric=v=>typeof v==='number'&&Number.isFinite(v)&&v>=0
function validateMetrics(d){
 if(!Array.isArray(d?.years)||!d.years.length||!Array.isArray(d.categories)||!d.all)throw new Error('analysis-metrics')
 if(!ORDER.every(id=>d.categories.some(c=>c.id===id)))throw new Error('analysis-metrics categories')
 for(const row of [...d.categories,d.all]){
  if(!numeric(row.totals?.approved_funding_wan)||!numeric(row.totals?.project_count))throw new Error('analysis-metrics totals')
  for(const key of metricSeries){
   const values=row.series?.[key]
   if(!Array.isArray(values)||values.length!==d.years.length||values.some(v=>v!==null&&!numeric(v)))throw new Error('analysis-metrics '+key)
  }
 }
 return d
}
export async function loadAnalysisMetrics(){
 const file='analysis-metrics.json'
 if(!cache[file])cache[file]=fetch(BASE+file).then(r=>{if(!r.ok)throw new Error(file);return r.json()}).then(validateMetrics).catch(e=>{delete cache[file];throw e})
 return cache[file]
}
export function useAnalysisMetrics(){
 const metrics=ref(null),error=ref(false),loading=ref(false)
 let active=true
 onScopeDispose(()=>{active=false})
 async function load(){
  if(loading.value)return
  loading.value=true;error.value=false
  try{const d=await loadAnalysisMetrics();if(active)metrics.value=d}catch{if(active)error.value=true}finally{if(active)loading.value=false}
 }
 load()
 return {metrics,error,loading,load}
}
export function useInvestData(){
 const curves=ref(null),terms=ref(null),error=ref(false)
 async function load(){
  error.value=false
  try{
   const [c,f,o,metrics]=await Promise.all([payload('curves.html','data'),payload('funding-terms.html','data'),payload('output-terms.html','data'),loadAnalysisMetrics()])
   if(!c?.years?.length||!c?.layers?.length)throw new Error('curves')
   curves.value={years:c.years,layers:Object.fromEntries(c.layers.map(l=>[l.id,l])),metrics}
   // 技术点动画的论文、专利为累计值，转成当年新增；不参与新指标计算。
   const diff=fr=>fr.map((x,i)=>({year:x.year,values:x.values.map((v,j)=>Math.max(0,v-(i?fr[i-1].values[j]:0)))}))
   terms.value={list:f.terms,funding:f.views[0].frames,papers:diff(o.views[0].frames),patents:diff(o.views[1].frames)}
  }catch{error.value=true}
 }
 load()
 return {curves,terms,error,load}
}
export const fmt=n=>Math.round(n||0).toLocaleString('en-US')
