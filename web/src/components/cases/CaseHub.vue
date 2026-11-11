<script setup>
/* 长链条分析：企业长链条 / 政策长链条 */
import {computed} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import PageHero from '../PageHero.vue'
import IndustryCases from './IndustryCases.vue'
import '../../chain-page.css'
defineProps({data:Object})
const route=useRoute(),router=useRouter()
const hero={title:'从基金资助到经济社会价值的长链条分析',lead:'把创新链与产业链连成一条并纳入政策链，沿基金、论文、专利、产品、应用与经济效益追踪代表性企业，观察政策工具在各环节的作用。'}
const topics=[
 {id:'industry',label:'企业长链条',caption:'基金 → 论文 → 专利 → 产品 → 应用 → 经济效益'},
 {id:'policy',label:'政策长链条',caption:'政策工具 → 技术定位 → 实施影响'}]
const active=computed(()=>topics.find(t=>t.id===route.query.topic)||topics[0])
function choose(id){router.replace({query:{...route.query,topic:id,case:undefined}})}
const policyPlan=[
 {n:'01',t:'政策文本解构',d:'按层级、发布时间、地域与作用对象整理政策文本，识别支持、规范与限制类工具。'},
 {n:'02',t:'技术定位',d:'将政策条款对应到人工智能共同技术词表，观察政策关注的技术方向与变化。'},
 {n:'03',t:'实施影响',d:'结合基金布局、企业与产品数据，比较政策出台前后相关技术方向的投入与产出。'}]
</script>
<template><div class="case-hub">
 <PageHero :title="hero.title" :lead="hero.lead">
  <template #tabs><nav class="chain-modules two" role="tablist" aria-label="长链条分析">
   <button v-for="(t,i) in topics" :key="t.id" role="tab" :aria-selected="active.id===t.id" :class="{active:active.id===t.id}" @click="choose(t.id)">
    <i>{{String(i+1).padStart(2,'0')}}</i>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path v-if="t.id==='industry'" d="M3 21V11l5 3V11l5 3V4h8v17Z"/><path v-else d="M3 9 12 4l9 5ZM5 10v8M10 10v8M14 10v8M19 10v8M3 20h18"/></svg>
    <span><b>{{t.label}}</b><small>{{t.caption}}</small></span>
   </button></nav></template>
 </PageHero>
 <div :key="active.id" class="pane-swap">
  <IndustryCases v-if="active.id==='industry'"/>
  <section v-else class="policy-plan">
   <header><h3>政策长链条</h3><p>以人工智能领域为示范，围绕政策工具、技术定位与实施影响组织研究。</p></header>
   <div class="pp-grid"><article v-for="p in policyPlan" :key="p.n"><b>{{p.n}}</b><h4>{{p.t}}</h4><p>{{p.d}}</p></article></div>
   <div class="pp-foot"><span>政策文本已纳入数据底座，可在领域数据中按层级与时间检索。</span><router-link to="/data?type=policy&domain=ai">查看政策数据 →</router-link></div>
  </section>
 </div>
</div></template>
<style scoped>
.chain-modules.two{grid-template-columns:repeat(2,1fr)}
.policy-plan{padding:28px 30px 30px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.policy-plan h3{margin:0;font-size:21px;font-weight:750;color:#232930;padding-left:14px;border-left:4px solid #a21535;line-height:1.2}
.policy-plan header p{margin:10px 0 20px;font-size:15px;color:#5d575b}
.pp-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.pp-grid article{padding:20px 22px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.pp-grid b{font-size:14px;font-weight:800;color:#a21535}
.pp-grid h4{margin:8px 0;font-size:17px;font-weight:750}
.pp-grid p{margin:0;font-size:13.5px;line-height:1.75;color:#6a6468}
.pp-foot{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-top:18px;padding:14px 18px;border-radius:4px;background:#fbf5f6;font-size:13.5px;color:#5d575b}
.pp-foot a{font-weight:650;color:#a21535;text-decoration:none;white-space:nowrap}
@media(max-width:760px){.pp-grid{grid-template-columns:1fr}.pp-foot{flex-direction:column;align-items:flex-start}.policy-plan{padding:20px 16px}}
</style>
