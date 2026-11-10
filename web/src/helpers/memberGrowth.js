/* 项目参与人 → 项目负责人：member-growth.json（Codex 由基金中心关联库生成），模块内缓存 */
import {ref} from 'vue'
import {typeGroup} from './strengthTip.js'
let cache=null
export function useMemberGrowth(){
 const data=ref(null),error=ref('')
 cache??=fetch('/chain-analysis/v1/member-growth.json').then(r=>{if(!r.ok)throw new Error('member-growth');return r.json()}).then(d=>{
  if(!d?.summary||!Array.isArray(d.cases))throw new Error('member-growth')
  d.cases.forEach(c=>{c.early_group=typeGroup(c.early_type);c.later_group=typeGroup(c.later_type)});return d}).catch(e=>{cache=null;throw e})
 cache.then(d=>data.value=d,()=>error.value='成长案例暂未读取。')
 return {data,error}
}
