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
  <PolicyCases v-else/>
 </div>
</div></template>
<style scoped>
.chain-modules.two{grid-template-columns:repeat(2,1fr)}
</style>
