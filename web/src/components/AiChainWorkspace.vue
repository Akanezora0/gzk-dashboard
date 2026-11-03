<script setup>
import {ref,computed,watch,nextTick,defineAsyncComponent} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import EvidenceHub from './EvidenceHub.vue'
import InvestmentOutcomes from './InvestmentOutcomes.vue'
import StrengthBase from './StrengthBase.vue'
import StrengthTrend from './StrengthTrend.vue'
import ResearchAtlas from './ResearchAtlas.vue'
import ResearchSuccession from './ResearchSuccession.vue'
const EvidenceExplorer=defineAsyncComponent(()=>import('./EvidenceExplorer.vue'))
import '../strength.css'
defineProps({data:Object})
const route=useRoute(),router=useRouter()
// Additional analysis modules are registered here after their data are ready.
const modules=[{id:'evidence',label:'原始证据链',caption:'关系与依据'},{id:'investment',label:'投入与产出',caption:'布局与成果'},{id:'strength',label:'研究力量',caption:'机构与接续'}]
const active=computed(()=>modules.some(x=>x.id===route.query.module)?route.query.module:'evidence')
// 研究力量：先总体（数据底座、机构参与、版图），再人员接续，最后可下钻到项目与论文证据
const strengthViews=[{id:'overview',label:'总体格局',caption:'数据底座 · 机构参与 · 研究力量版图'},{id:'continuity',label:'接续与证据',caption:'负责人接续 · 项目与论文证据'}]
const strengthView=computed(()=>['continuity','evidence'].includes(route.query.view)?'continuity':'overview')
const evidencePerson=ref('')
const dataset=ref(null),loadError=ref(''),loading=ref(false)
function choose(id){router.push({path:route.path,query:{...route.query,domain:'ai',module:id,view:undefined}})}
function chooseView(view){router.replace({query:{...route.query,view}})}
function explore(name){evidencePerson.value=name||'';nextTick(()=>document.getElementById('rs-evidence')?.scrollIntoView({behavior:'smooth',block:'start'}))}
async function load(){if(dataset.value||loading.value)return;loading.value=true;loadError.value='';try{const r=await fetch('/chain-analysis/v1/research.json');if(!r.ok)throw new Error('读取失败');dataset.value=await r.json()}catch{loadError.value='研究力量数据暂时无法读取，请重试。'}finally{loading.value=false}}
watch(active,v=>{if(v==='strength')load()},{immediate:true})
</script>
<template>
  <section class="ai-chain-workspace" :data-module="active">
    <nav class="analysis-modules" aria-label="人工智能分析模块">
      <button v-for="(m,i) in modules" :key="m.id" :class="{active:active===m.id}" :aria-current="active===m.id?'page':undefined" @click="choose(m.id)"><span class="module-no">0{{i+1}}</span><span><b>{{m.label}}</b><small>{{m.caption}}</small></span><span class="module-arrow">↗</span></button>
    </nav>
    <EvidenceHub v-if="active==='evidence'" :data="data"/>
    <InvestmentOutcomes v-else-if="active==='investment'"/>
    <template v-else>
      <div class="strength-switch" role="tablist" aria-label="研究力量视图"><button v-for="(v,i) in strengthViews" :key="v.id" role="tab" :aria-selected="strengthView===v.id" :class="{active:strengthView===v.id}" @click="chooseView(v.id)"><span class="sw-no">0{{i+1}}</span><span class="sw-text"><b>{{v.label}}</b><em>{{v.caption}}</em></span></button></div>
      <div v-if="loadError" class="analysis-loading">{{loadError}} <button @click="load">重新读取</button></div>
      <div v-else-if="!dataset" class="analysis-loading">正在整理机构与成果脉络…</div>
      <div v-else-if="strengthView==='overview'" class="strength-stack"><StrengthBase :dataset="dataset"/><StrengthTrend :dataset="dataset"/><ResearchAtlas :dataset="dataset"/></div>
      <div v-else class="strength-stack"><ResearchSuccession :dataset="dataset" @explore="explore"/><EvidenceExplorer id="rs-evidence" :dataset="dataset" :person="evidencePerson"/></div>
    </template>
  </section>
</template>
<style scoped>
.analysis-modules{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:6px 0 30px}.analysis-modules button{display:flex;align-items:center;gap:16px;text-align:left;padding:19px 22px;border:1px solid #e3dfd9;border-radius:12px;background:#fff;color:#68635f;cursor:pointer;transition:border-color .2s,box-shadow .2s}.analysis-modules button.active{border-color:#ae0d28;box-shadow:inset 0 -3px #ae0d28;color:#ae0d28}.module-no{font-size:15px;font-weight:700;opacity:.65}.analysis-modules b{display:block;font-size:21px;letter-spacing:.4px}.analysis-modules small{display:block;font-size:13px;color:#8c8580;margin-top:6px}.module-arrow{margin-left:auto;font-size:23px}.analysis-modules button:not(.active):hover{border-color:#b6ada7}.analysis-heading{margin:32px 0 23px}.analysis-kicker{font-size:13px!important;color:#ae0d28!important;font-weight:600;letter-spacing:1.4px}.analysis-heading h2{font-size:32px;color:#2d2a28;margin:10px 0 12px;line-height:1.45}.analysis-heading p{font-size:16px;color:#817a74;line-height:1.8;margin:0}.strength-switch{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;padding:6px;margin:4px 0 26px;background:#efebe6;border-radius:16px}.strength-switch button{display:flex;align-items:center;gap:16px;border:0;background:transparent;border-radius:12px;padding:14px 22px;text-align:left;cursor:pointer;font-family:inherit;color:#78716c;transition:background .2s,box-shadow .2s,color .2s}.strength-switch button:hover:not(.active){background:rgba(255,255,255,.55)}.strength-switch button.active{background:#fff;box-shadow:0 2px 10px rgba(60,30,30,.08);color:#2a2a2a}.sw-no{flex:none;width:38px;height:38px;border-radius:50%;display:grid;place-items:center;font-size:14px;font-weight:700;background:#e3ded8;color:#8c8580}.strength-switch button.active .sw-no{background:#ae0d28;color:#fff}.sw-text b{display:block;font-size:18px;font-weight:700}.strength-switch button.active .sw-text b{color:#ae0d28}.sw-text em{display:block;font-style:normal;font-size:13px;color:#a59d97;margin-top:2px}@media(max-width:700px){.strength-switch{grid-template-columns:1fr}.strength-switch button{padding:10px 14px}}.strength-stack{display:flex;flex-direction:column;gap:28px}.analysis-loading{padding:80px;text-align:center;background:white;border-radius:12px;color:#6b6560}button:focus-visible{outline:3px solid #ac6b7a;outline-offset:4px}@media(max-width:700px){.analysis-modules{gap:7px;margin-bottom:22px}.analysis-modules button{padding:12px 9px;gap:7px}.analysis-modules b{font-size:15px}.analysis-modules small{font-size:11px}.module-no,.module-arrow{display:none}.analysis-heading h2{font-size:25px}.analysis-heading p{font-size:14px}.analysis-loading{padding:45px 15px}}
</style>

