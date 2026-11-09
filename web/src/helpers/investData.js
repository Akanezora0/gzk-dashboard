/* 投入与产出：读取已验收的快照（curves / funding-terms / output-terms），只读，不重新估计 */
import {ref} from 'vue'
const BASE='/chain-analysis/v1/'
const cache={}
async function payload(file,id){
 if(!cache[file])cache[file]=fetch(BASE+file).then(r=>{if(!r.ok)throw new Error(file);return r.text()}).then(t=>{const doc=new DOMParser().parseFromString(t,'text/html');return doc})
 const doc=await cache[file];return JSON.parse(doc.querySelector(`script#${id}`)?.textContent||'null')
}
export const ORDER=['AI1','AI2','AI3','AI4','AI5','AI6','AI7']
/* 与网站辅助色一致的七大方向配色 */
export const PALETTE={AI1:'#a21535',AI2:'#2c64a0',AI3:'#23806e',AI4:'#8a8a8f',AI5:'#b2772a',AI6:'#6f4a94',AI7:'#c47a8a'}
export function useInvestData(){
 const curves=ref(null),terms=ref(null),error=ref(false)
 async function load(){
  error.value=false
  try{
   const [c,f,o]=await Promise.all([payload('curves.html','data'),payload('funding-terms.html','data'),payload('output-terms.html','data')])
   if(!c?.years?.length||!c?.layers?.length)throw new Error('curves')
   curves.value={years:c.years,layers:Object.fromEntries(c.layers.map(l=>[l.id,l]))}
   // 论文、专利为年度累计值，转为当年新增
   const diff=fr=>fr.map((x,i)=>({year:x.year,values:x.values.map((v,j)=>Math.max(0,v-(i?fr[i-1].values[j]:0)))}))
   terms.value={list:f.terms,funding:f.views[0].frames,papers:diff(o.views[0].frames),patents:diff(o.views[1].frames)}
  }catch{error.value=true}
 }
 load()
 return {curves,terms,error,load}
}
export const fmt=n=>Math.round(n||0).toLocaleString('en-US')
