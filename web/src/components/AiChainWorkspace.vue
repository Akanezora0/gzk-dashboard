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
import '../chain-page.css'
import PageHero from './PageHero.vue'
import {fmt} from '../shared'
const props=defineProps({data:Object})
const route=useRoute(),router=useRouter()
// Additional analysis modules are registered here after their data are ready.
const modules=[
 {id:'evidence',label:'关联与依据',caption:'基金、论文、专利与技术的关联依据',title:'基金、成果与技术的关联依据',lead:'以项目编号和原文片段连接基金项目、论文、专利与技术主题，每条关系都可追溯到来源。'},
 {id:'investment',label:'投入与产出',caption:'经费布局与论文、专利产出',title:'基金投入与成果产出',lead:'按年份和技术方向，观察人工智能基金项目的经费投入，以及论文、专利成果的积累与基金贡献。'},
 {id:'strength',label:'研究团队',caption:'承担机构与负责人接续',title:'研究团队的格局与接续',lead:'从承担机构、项目负责人与成果关系出发，观察人工智能基础研究团队如何形成、扩展与延续。'}]
const active=computed(()=>modules.some(x=>x.id===route.query.module)?route.query.module:'evidence')
const activeModule=computed(()=>modules.find(m=>m.id===active.value))
// 研究团队：先总体（数据底座、机构参与、版图），再人员接续，最后可下钻到项目与论文证据
const strengthViews=[{id:'overview',label:'总体格局',caption:'已建立关系 · 机构参与 · 研究团队版图'},{id:'continuity',label:'接续与证据',caption:'负责人接续 · 项目与论文证据'}]
const strengthView=computed(()=>['continuity','evidence'].includes(route.query.view)?'continuity':'overview')
const evidencePerson=ref('')
const dataset=ref(null),loadError=ref(''),loading=ref(false)
function choose(id){router.push({path:route.path,query:{...route.query,domain:'ai',module:id,view:undefined}})}
function toEvidence(chain){router.push({path:route.path,query:{domain:'ai',module:'evidence',chain}})}
function chooseView(view){router.replace({query:{...route.query,view}})}
function explore(name){evidencePerson.value=name||'';nextTick(()=>document.getElementById('rs-evidence')?.scrollIntoView({behavior:'smooth',block:'start'}))}
async function load(){if(dataset.value||loading.value)return;loading.value=true;loadError.value='';try{const r=await fetch('/chain-analysis/v1/research.json');if(!r.ok)throw new Error('读取失败');dataset.value=await r.json()}catch{loadError.value='研究团队数据暂时无法读取，请重试。'}finally{loading.value=false}}
watch(active,v=>{if(v==='strength')load()},{immediate:true})
</script>
<template>
  <section class="ai-chain-workspace" :data-module="active">
    <PageHero eyebrow="创新链分析" :title="activeModule.title" :lead="activeModule.lead">
      <template #tabs><nav class="chain-modules" role="tablist" aria-label="分析模块">
        <button v-for="(m,i) in modules" :key="m.id" role="tab" :aria-selected="active===m.id" :class="{active:active===m.id}" @click="choose(m.id)">
          <i>{{String(i+1).padStart(2,'0')}}</i>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <template v-if="m.id==='evidence'"><rect x="3" y="3" width="6" height="6" rx="1.5"/><rect x="15" y="15" width="6" height="6" rx="1.5"/><path d="M9 6h7a2 2 0 0 1 2 2v7M6 9v7a2 2 0 0 0 2 2h7"/></template>
            <template v-else-if="m.id==='investment'"><path d="M4 3v17h17M8 15v-4M13 15V7M18 15V4"/></template>
            <template v-else><circle cx="9" cy="8" r="3"/><path d="M3 20v-2a6 6 0 0 1 12 0v2M16 5a3 3 0 0 1 0 6M18 14a5 5 0 0 1 3 4v2"/></template>
          </svg>
          <span><b>{{m.label}}</b><small>{{m.caption}}</small></span>
        </button>
      </nav></template>
    </PageHero>
    <div :key="active" class="pane-swap">
    <EvidenceHub v-if="active==='evidence'" :data="data"/>
    <InvestmentOutcomes v-else-if="active==='investment'" :data="data" @explore="toEvidence"/>
    <template v-else>
      <nav class="strength-views view-tabs" role="tablist" aria-label="研究团队视图"><template v-for="(v,i) in strengthViews" :key="v.id"><button role="tab" :aria-selected="strengthView===v.id" :class="{active:strengthView===v.id}" :title="v.caption" @click="chooseView(v.id)">{{v.label}}</button></template></nav>
      <div v-if="loadError" class="analysis-loading">{{loadError}} <button @click="load">重新读取</button></div>
      <div v-else-if="!dataset" class="analysis-loading">正在整理机构与成果脉络…</div>
      <div v-else-if="strengthView==='overview'" class="strength-stack pane-swap" :key="strengthView"><StrengthBase :dataset="dataset" :inventory="data?.currentInventory"/><StrengthTrend :dataset="dataset"/><ResearchAtlas :dataset="dataset"/></div>
      <div v-else class="strength-stack pane-swap" :key="strengthView"><ResearchSuccession :dataset="dataset" @explore="explore"/><EvidenceExplorer id="rs-evidence" :dataset="dataset" :person="evidencePerson"/></div>
    </template>
    </div>
  </section>
</template>
<style scoped>
/* Compact module rail: distinct from the primary pills and view underline tabs. */
.analysis-modules{display:flex;align-items:center;gap:24px;margin:6px 0 26px;padding:10px 0;border-bottom:1px solid #e6e1dc}
.module-label{flex:none;font-size:12px;letter-spacing:1.2px;color:#918982}
.module-links{display:flex;align-items:center;gap:8px}
.analysis-modules button{position:relative;display:flex;align-items:center;gap:9px;min-height:40px;padding:8px 18px;border:0;border-radius:4px;background:transparent;color:#726e69;font:inherit;font-size:16px;line-height:24px;cursor:pointer;transition:background .18s,color .18s}
.analysis-modules button::before{content:"";position:absolute;left:0;top:11px;bottom:11px;width:3px;border-radius:2px;background:transparent}
.analysis-modules button.active{background:#f1ece9;color:#a90d2b;font-weight:650}
.analysis-modules button.active::before{background:#ae0d28}
.analysis-modules button:not(.active):hover{background:#f1eeeb;color:#403a36}
.analysis-modules svg{width:18px;height:18px;flex:none}
.analysis-modules button span{white-space:nowrap}
.analysis-heading{margin:32px 0 23px}.analysis-kicker{font-size:13px!important;color:#ae0d28!important;font-weight:600;letter-spacing:1.4px}.analysis-heading h2{font-size:32px;color:#2d2a28;margin:10px 0 12px;line-height:1.45}.analysis-heading p{font-size:16px;color:#817a74;line-height:1.8;margin:0}.strength-views{display:flex;align-items:center;gap:22px;margin:2px 0 20px;padding:0 4px}.strength-views button{position:relative;background:none;border:0;padding:6px 0;font-family:inherit;font-size:17px;color:#8c8580;cursor:pointer;transition:color .2s}.strength-views button:hover{color:#57534e}.strength-views button.active{color:#ae0d28;font-weight:700}.strength-views button.active::after{content:"";position:absolute;left:0;right:0;bottom:-2px;height:2px;border-radius:2px;background:#ae0d28}.sv-sep{width:1px;height:16px;background:#d9d3cd}.strength-stack{display:flex;flex-direction:column;gap:28px}.analysis-loading{padding:80px;text-align:center;background:white;border-radius:12px;color:#6b6560}button:focus-visible{outline:3px solid #ac6b7a;outline-offset:4px}@media(max-width:700px){.analysis-modules{gap:0;margin-bottom:20px;padding:8px 0}.module-label{display:none}.module-links{width:100%;gap:4px}.analysis-modules button{flex:1;justify-content:center;padding:8px 6px;gap:6px;font-size:14px}.analysis-modules svg{width:16px;height:16px}.analysis-heading h2{font-size:25px}.analysis-heading p{font-size:14px}.analysis-loading{padding:45px 15px}}
</style>
