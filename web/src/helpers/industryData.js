/* 领域数据 · 企业／产品／经济：静态数据读取与共用格式（数据：snapshot/public/industry/v1，scripts/build_industry_panels.py 生成） */
import {ref} from 'vue'
import {fmt,concise,chartBase,escape} from '../shared'

const base='/industry/v1/'
const cache=new Map()
function load(name){
 if(!cache.has(name))cache.set(name,fetch(base+name).then(r=>{if(!r.ok)throw new Error(`读取失败（${r.status}）`);return r.json()}).catch(e=>{cache.delete(name);throw e}))
 return cache.get(name)
}

// 企业名录（企业、技术点、专利技术归集）
const companyState={data:ref(null),error:ref('')}
let companyIndex=null
export function useCompanies(){
 if(!companyState.data.value&&!companyState.error.value)load('companies.json').then(d=>{
  const byId=new Map(d.companies.map(c=>[c.id,c])),byCid=new Map(d.companies.filter(c=>c.cid).map(c=>[c.cid,c]))
  const tech=new Map(d.technologies.map(t=>[t.id,t]))
  companyIndex={byId,byCid,tech}
  companyState.data.value=Object.freeze({...d,byId,byCid,tech})
 }).catch(e=>companyState.error.value=e.message)
 return companyState
}
export const companyOf=id=>companyIndex?.byId.get(id)||companyIndex?.byCid.get(id)||null

// 产品目录
const productState={data:ref(null),error:ref('')}
export function useProducts(){
 if(!productState.data.value&&!productState.error.value)load('products.json').then(d=>{
  const owners=new Map(d.owners.map(o=>[o.id,o])),byOwner=new Map()
  for(const p of d.products)for(const o of p.owners){if(!byOwner.has(o))byOwner.set(o,[]);byOwner.get(o).push(p)}
  productState.data.value=Object.freeze({...d,ownerMap:owners,byOwner,byId:new Map(d.products.map(p=>[p.id,p]))})
 }).catch(e=>productState.error.value=e.message)
 return productState
}

// 经济指标：每家企业、每项指标取最近年度
const economyState={data:ref(null),error:ref('')}
export function useEconomy(){
 if(!economyState.data.value&&!economyState.error.value)load('economics.json').then(d=>{
  const latest=new Map()
  for(const [companyId,year,metric,value,scope,entity,source] of d.finance){
   if(!latest.has(companyId))latest.set(companyId,new Map())
   const m=latest.get(companyId),prev=m.get(metric)
   if(!prev||year>prev.year)m.set(metric,{metric,year,value,scope,entity,source})
  }
  const metrics=new Map(d.metrics.map(m=>[m.id,m]))
  const categories=d.categories.filter(g=>d.metrics.some(m=>m.category===g.id))
  economyState.data.value=Object.freeze({...d,latest,metricMap:metrics,categories})
 }).catch(e=>economyState.error.value=e.message)
 return economyState
}

// 专利选览：按企业编号分片读取
export function loadPatents(cid){
 const shard=[...cid].reduce((s,ch)=>s+ch.charCodeAt(0),0)%32
 return load(`patents/${shard}.json`).then(d=>d[cid]||[])
}

export const roleName=r=>r==='上层应用企业'?'应用企业':r
export const roleShort=r=>({大模型提供商:'大模型',算力提供商:'算力',存储提供商:'存储',上层应用企业:'应用'})[r]||r
export const ROLES=['大模型提供商','算力提供商','存储提供商','上层应用企业']
export const metricName=(m)=>m?.id==='CAPEX_CASH'?'资本性支出':m?.name||''
export function amount(v,unit){if(v==null||!Number.isFinite(v))return '—';if(unit==='人')return fmt(Math.round(v));const a=Math.abs(v);return a>=1000?fmt(Math.round(v)):a>=1?String(+v.toFixed(a>=100?1:2)):String(+v.toPrecision(3))}

export function countBy(rows,key){
 const m=new Map()
 for(const r of rows){const ks=key(r);for(const k of Array.isArray(ks)?ks:[ks]){if(k==null||k==='')continue;m.set(k,(m.get(k)||0)+1)}}
 return [...m].map(([name,count])=>({name,count})).sort((a,b)=>b.count-a.count||String(a.name).localeCompare(String(b.name),'zh-CN'))
}
export function quantile(values,p){const a=values.filter(Number.isFinite).sort((x,y)=>x-y);if(!a.length)return null;const x=(a.length-1)*p,i=Math.floor(x);return a[i]+(a[Math.ceil(x)]-a[i])*(x-i)}

// 与领域数据其他标签一致的横向条形图；active 项高亮，点击用于筛选
export function barChart(items,{color,label='企业数',unit='家',active='',limit=8,format=fmt,axis=concise}={}){
 const values=(items||[]).slice(0,limit).reverse()
 return {...chartBase,grid:{left:10,right:58,top:10,bottom:22,containLabel:true},
  tooltip:{trigger:'item',confine:true,formatter:p=>`${escape(p.name)}<br/>${p.marker} ${escape(label)}：<b>${format(p.value)}</b> ${unit}`},
  xAxis:{type:'value',minInterval:format===fmt?1:0,axisLabel:{fontSize:12,formatter:axis},splitLine:{lineStyle:{color:'#edf0f4',type:'dashed'}}},
  yAxis:{type:'category',data:values.map(v=>v.name),axisLabel:{fontSize:13,width:150,overflow:'truncate',color:'#394354'},axisTick:{show:false},axisLine:{show:false}},
  series:[{name:label,type:'bar',barMaxWidth:18,cursor:'pointer',label:{show:true,position:'right',fontSize:12.5,color:'#465367',formatter:p=>format(p.value)},
   data:values.map(v=>({name:v.name,value:v.count,id:v.id,itemStyle:{color,opacity:active&&active!==v.name?.35:1,borderRadius:[0,4,4,0]}}))}]}
}
