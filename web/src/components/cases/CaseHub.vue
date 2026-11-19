<script setup>
/* 长链条案例：企业案例 / 政策案例 */
import {computed} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import PageHero from '../PageHero.vue'
import IndustryCases from './IndustryCases.vue'
import PolicyCases from './policy/PolicyCases.vue'
import '../../chain-page.css'
defineProps({data:Object})
const route=useRoute(),router=useRouter()
const hero={title:'从基金资助到经济社会价值的长链条案例',lead:'把创新链与产业链连成一条并纳入政策链，选取代表性企业与政策，完整呈现基础研究从基金资助到经济社会价值的路径。'}
const topics=[
 {id:'industry',label:'企业案例',caption:'基金 → 论文 → 专利承接 → 产品 → 应用 → 经济社会价值'},
 {id:'policy',label:'政策案例',caption:'政策文本采集与量化 → 因果分析建模 → 政策效应评估'}]
const active=computed(()=>topics.find(t=>t.id===route.query.topic)||topics[0])
function choose(id){router.replace({query:{...route.query,topic:id,case:undefined}})}
const policyPlan=[
 {n:'01',t:'政策文本采集与量化',d:'自动化批量采集目标政策，按层级、发布时间、地域与主题等维度整理政策文本，利用大语言模型进行文本量化评分，识别政策的倾向性与可靠性。'},
 {n:'02',t:'因果分析建模',d:'对应政策文本解构结果，配套完成被解释变量匹配、控制变量设计与采集，系统科学性构建因果分析模型。'},
 {n:'03',t:'政策效应评估',d:'结合基金布局投入、企业运营、技术专利等数据，评价政策对经济效益与技术创新的影响效应。'}]
</script>
<template><div class="case-hub">
 <PageHero :title="hero.title" :lead="hero.lead">
  <template #tabs><nav class="chain-modules two" role="tablist" aria-label="长链条案例">
   <button v-for="(t,i) in topics" :key="t.id" role="tab" :aria-selected="active.id===t.id" :class="{active:active.id===t.id}" @click="choose(t.id)">
    <i>{{String(i+1).padStart(2,'0')}}</i>
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path v-if="t.id==='industry'" d="M3 21V11l5 3V11l5 3V4h8v17Z"/><path v-else d="M3 9 12 4l9 5ZM5 10v8M10 10v8M14 10v8M19 10v8M3 20h18"/></svg>
    <span><b>{{t.label}}</b><small>{{t.caption}}</small></span>
   </button></nav></template>
 </PageHero>
 <div :key="active.id" class="pane-swap">
  <IndustryCases v-if="active.id==='industry'"/>
  <template v-else>
   <section class="policy-plan">
    <header><h3>政策案例</h3><p>以人工智能和大模型领域为示范，围绕政策文本采集与量化、因果分析建模、政策效应评估组织政策长链条案例。</p></header>
    <div class="pp-grid"><article v-for="p in policyPlan" :key="p.n"><b>{{p.n}}</b><h4>{{p.t}}</h4><p>{{p.d}}</p></article></div>
   </section>
   <PolicyCases class="policy-cases-wrap"/>
  </template>
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
.policy-cases-wrap{display:block;margin-top:24px}
@media(max-width:760px){.pp-grid{grid-template-columns:1fr}.policy-plan{padding:20px 16px}}
</style>
