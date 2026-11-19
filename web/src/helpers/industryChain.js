/* 短链条分析 · 产业链分析：数据读取、索引与经营指标格式
   数据：snapshot/public/industry-chain/v1（scripts/build_industry_chain.py 由同事交付的产业链展示页生成）
   经营指标的去重、取值与期间规则沿用原展示页。 */
import {shallowRef} from 'vue'

const base='/industry-chain/v1/'
const cache=new Map()
export function load(name){
 if(!cache.has(name))cache.set(name,fetch(base+name).then(r=>{if(!r.ok)throw new Error(`读取失败（${r.status}）`);return r.json()}).catch(e=>{cache.delete(name);throw e}))
 return cache.get(name)
}
export const arr=v=>Array.isArray(v)?v:[]
export const fmtN=v=>v==null||v===''||!Number.isFinite(Number(v))?'—':Number(v).toLocaleString('zh-CN')
export const clip=(v,n=30)=>{const s=String(v??'');return s.length>n?s.slice(0,n-1)+'…':s}

// 企业配色（与原展示页同序，按 dashboard 色调略压饱和度）
export const companyColors=['#86507f','#3f8a80','#c0753f','#6f68a6','#a8506b','#9c8a3c','#4d679d']
export const categoryColors=['#86507f','#5f7ea4','#ad7d55','#5b8c88','#9a4d69','#7a70a2','#9b778c']

/* ---------- 证据全景与产品代际 ---------- */
const atlasState=shallowRef(null)
let atlasPromise=null
export function useAtlas(){
 if(!atlasPromise)atlasPromise=load('atlas.json').then(d=>{
  const techMap=new Map(d.technologies.map(t=>[t.id,t]))
  const catIndex=new Map(d.categories.map((c,i)=>[c.name,i]))
  atlasState.value=Object.freeze({...d,techMap,catIndex})
 }).catch(e=>{atlasPromise=null;throw e})
 return {atlas:atlasState,ready:atlasPromise}
}
const evoState=shallowRef(null)
export function useEvolution(){if(!evoState.value)load('evolution.json').then(d=>evoState.value=Object.freeze(d)).catch(()=>{});return evoState}

/* ---------- 链条分析索引 ---------- */
const indexState=shallowRef(null)
let indexPromise=null
export function useChainIndex(){
 if(!indexPromise)indexPromise=load('analysis.json').then(d=>{
  const ids=d.companyIds
  const companies=new Map(ids.map((id,i)=>[id,{id,...d.companies[i],productIds:[]}]))
  const products=d.products.map(([id,name,owners,techs,chunk])=>{const p={id,name,companyIds:owners.map(i=>ids[i]),technologyIds:techs.map(n=>'T'+String(n).padStart(3,'0')),chunk};p.companyIds.forEach(cid=>companies.get(cid)?.productIds.push(id));return p})
  const productMap=new Map(products.map(p=>[p.id,p])),byTech=new Map()
  for(const p of products)for(const t of p.technologyIds){if(!byTech.has(t))byTech.set(t,[]);byTech.get(t).push(p)}
  indexState.value=Object.freeze({products,productMap,companies,byTech,industries:d.industries||{}})
 }).catch(e=>{indexPromise=null;throw e})
 return {index:indexState,ready:indexPromise}
}
// 产品简介按分片读取
const intros=new Map()
export async function productIntros(list){
 const chunks=[...new Set(list.map(p=>p.chunk))].filter(c=>c!=null)
 await Promise.all(chunks.map(async c=>{const name=`products/${String(c).padStart(3,'0')}.json`;const d=await load(name);for(const [id,t] of Object.entries(d))intros.set(id,t)}))
 return intros
}
export const introOf=id=>intros.get(id)
// 主体经营指标、专利样例与归档关系按主体编号分片读取
export async function companyValue(id){const d=await load(`value/${id.slice(-2)}.json`).catch(()=>({}));return d[id]||null}
export async function companyExtra(id){const d=await load(`company/${id.slice(-1)}.json`).catch(()=>({}));return d[id]||null}
export const techPatents=()=>load('tech-patents.json')

/* ---------- 经营指标（沿用原展示页规则） ---------- */
export const hasValue=v=>(typeof v==='number'||typeof v==='string')&&String(v).trim()!==''&&Number.isFinite(Number(v))
export function hasObservation(row){
 if(row.displayEligible===false||row.valueType==='missing')return false
 return hasValue(row.value)||[row.displayValue,row.textValue,row.value].some(v=>typeof v==='string'&&v.trim()&&!/^(未取得|未披露|暂无数据|待补|—|-)$/.test(v.trim()))
}
const comparator=row=>({gt:'>',gte:'≥','>=':'≥',lt:'<',lte:'≤','<=':'≤',eq:'','=':'',approx:'≈'}[row.comparator||'']??String(row.comparator||''))
export function period(row){
 const raw=String(row.period||'')
 const h=raw.match(/^(20\d{2})\s*H([12])$/i);if(h)return `${h[1]} ${h[2]==='1'?'上半年':'下半年'}`
 if(/^20\d{2}$/.test(raw))return raw+' 年'
 return raw||(row.year!=null?`${row.year} 年`:'')
}
function parts(row){
 let value=row.value,cmp=comparator(row)
 if(typeof value==='string'&&!hasValue(value)){const m=value.trim().match(/^(>=|<=|>|<|≥|≤|≈|约|超过|不少于)\s*([+-]?\d+(?:\.\d+)?)$/);if(m){cmp=cmp||m[1];value=m[2]}}
 return {value,unit:row.unit,currency:row.currency,cmp}
}
const qualified=(row,text)=>{const c=comparator(row);text=String(text);return c&&!/^\s*(>=|<=|>|<|≥|≤|≈|约|超过|不少于)/.test(text)?c+text:text}
const currencyName=c=>({CNY:'',RMB:'',USD:'美元',HKD:'港元',EUR:'欧元',JPY:'日元'}[c]??c??'')
// 紧凑显示：元／万元自动换算为亿元，外币标注币种
export function compactValue(row){
 if(row.displayValue)return qualified(row,row.displayValue)
 if(row.textValue)return qualified(row,row.textValue)
 const p=parts(row);if(!hasValue(p.value))return String(p.value??'—')
 let n=Number(p.value),u=(p.unit||'').replace('（原币）','')
 if(u==='元'&&Math.abs(n)>=1e8){n/=1e8;u='亿元'}
 else if(u==='万元'&&Math.abs(n)>=1e4){n/=1e4;u='亿元'}
 else if(u==='元'&&Math.abs(n)>=1e4){n/=1e4;u='万元'}
 const cur=currencyName(p.currency)
 return p.cmp+n.toLocaleString('zh-CN',{maximumFractionDigits:2})+(u?(u==='%'?'':' ')+u:'')+(cur&&!u.includes(cur)?' '+cur:'')
}
export function sourcesOf(row){
 const list=arr(row.sources).map(s=>({title:s.title||s.sourceTitle,url:s.url||s.sourceUrl,location:s.location||s.sourceLocator,date:s.date||s.sourceDate}))
 if(row.sourceTitle||row.sourceUrl)list.unshift({title:row.sourceTitle||'经济资料',url:row.sourceUrl,location:row.sourceLocator,date:row.sourceDate})
 const seen=new Set();return list.filter(s=>{const k=[s.url,s.title,s.location].join('|');if(seen.has(k))return false;seen.add(k);return true})
}
export const reporterOf=(row,fallback)=>row.reportingEntity||fallback||''
// 展示指标 + 年度指标合并去重（同一观测优先保留展示指标）
export function metricRows(company,pack){
 if(!pack)return []
 const pub=arr(pack.indicators).map(r=>({...r,name:r.name||r.metric||'经济指标'}))
 const rev=arr(pack.revenueSeries).filter(r=>hasValue(r.value)).map(r=>({...r,id:r.id||`${company.id}|${r.year}|REV`,name:r.metric||'营业收入',metricId:'REV',period:r.period||String(r.year),isRevenue:true}))
 const annual=arr(pack.annual).map(r=>({...r,name:r.name||r.metricLabel||{revenue:'营业收入',employees:'员工总数',rd_employees:'研发人员数'}[r.metric]||r.metric}))
 const metricKey=r=>{const raw=String(r.metricId||r.metric||r.standardName||r.name||'').trim().toLowerCase();return {rev:'revenue','营业收入':'revenue','员工总数':'employees','研发人员数':'rd_employees'}[raw]||raw}
 const periodKey=r=>{const raw=String(r.period||r.year||'').replace(/\s+/g,'').toLowerCase();const y=raw.match(/^(20\d{2})(?:年|年度|全年)?$/);return y?y[1]:raw.replace(/^(20\d{2})年?上半年$/,'$1h1').replace(/^(20\d{2})年?下半年$/,'$1h2')}
 const scopeKey=r=>{const raw=String(r.scopeClass||r.scope||'').trim().toLowerCase();return {consolidated:'target_consolidated','合并口径':'target_consolidated',standalone:'target_standalone','单体口径':'target_standalone'}[raw]||raw}
 const ids=new Set(),sem=new Set()
 return [...pub,...rev,...annual].filter(hasObservation).filter(r=>{
  const p=periodKey(r),rep=reporterOf(r,company.name).trim(),id=r.observationKey||r.id
  const stable=id?JSON.stringify([id,p,rep]):null,semantic=JSON.stringify([metricKey(r),p,rep,scopeKey(r)])
  if(stable&&ids.has(stable)||sem.has(semantic))return false
  if(stable)ids.add(stable);sem.add(semantic);return true
 }).map(r=>({...r,companyId:company.id}))
}
export const isLabor=r=>['employees','rd_employees'].includes(r.metricId||r.metric)||/人员|员工|薪酬|职工|雇员/.test((r.category||'')+' '+r.name)
export const isSocial=r=>/应用成效|运营规模|用户|客户|使用量|日均生成|自动化率|累计使用/.test((r.category||'')+' '+r.name)&&!isLabor(r)&&sourcesOf(r).length>0
export function periodRank(r){const t=String(r.period||r.year||''),y=Number(t.match(/20\d{2}/)?.[0]||r.year||0),m=t.match(/20\d{2}[-年](\d{1,2})/);return y*100+(m?Number(m[1]):/H1|上半年/i.test(t)?6:12)}
export function recentRows(rows){const seen=new Set();return rows.slice().sort((a,b)=>periodRank(b)-periodRank(a)).filter(r=>{const k=[r.companyId,r.metric||r.metricId||r.name,r.reportingEntity,r.scope].join('|');if(seen.has(k))return false;seen.add(k);return true})}
// 证据全景：经济指标列取首选指标
export function headline(company,econ){
 const pack={indicators:econ?.indicators,revenueSeries:company.revenueSeries}
 const rows=metricRows(company,pack),pref=econ?.preferredIndicatorId
 rows.sort((a,b)=>Number(b.id===pref)-Number(a.id===pref)||Number(!!b.isRevenue)-Number(!!a.isRevenue)||periodRank(b)-periodRank(a))
 return rows.find(r=>r.eligibleForHeadline!==false)||rows[0]||null
}
// 名称简写：去掉“关联集团·”等前缀
export const metricTitle=r=>String(r.name||'').replace(/^关联集团[·・]/,'')
