<script setup>
import {ref,computed,watch,defineAsyncComponent} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import EvidenceHub from './EvidenceHub.vue'
import InvestmentOutcomes from './InvestmentOutcomes.vue'
import ResearchLandscape from './ResearchLandscape.vue'
const ResearchContinuity=defineAsyncComponent(()=>import('./ResearchContinuity.vue'))
defineProps({data:Object})
const route=useRoute(),router=useRouter()
// Additional analysis modules are registered here after their data are ready.
const modules=[{id:'evidence',label:'原始证据链',caption:'关系与依据'},{id:'investment',label:'投入与产出',caption:'布局与成果'},{id:'strength',label:'研究力量',caption:'机构与接续'}]
const active=computed(()=>modules.some(x=>x.id===route.query.module)?route.query.module:'evidence')
const strengthView=computed(()=>route.query.view==='continuity'?'continuity':'landscape')
const dataset=ref(null),loadError=ref(''),loading=ref(false)
function choose(id){router.push({path:route.path,query:{...route.query,domain:'ai',module:id,view:undefined}})}
function chooseView(view){router.replace({query:{...route.query,view}})}
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
      <header class="analysis-heading"><div><p class="analysis-kicker">人工智能 · 研究力量</p><h2>从机构版图，看到研究的持续积累</h2><p>沿时间追踪代表性成果，再回到基金项目、负责人和论文，查看研究如何接续。</p></div></header>
      <div class="strength-tabs" role="tablist" aria-label="研究力量视图"><button role="tab" :aria-selected="strengthView==='landscape'" :class="{active:strengthView==='landscape'}" @click="chooseView('landscape')">研究力量版图</button><button role="tab" :aria-selected="strengthView==='continuity'" :class="{active:strengthView==='continuity'}" @click="chooseView('continuity')">基金研究接续</button></div>
      <div v-if="loadError" class="analysis-loading">{{loadError}} <button @click="load">重新读取</button></div>
      <div v-else-if="!dataset" class="analysis-loading">正在整理机构与成果脉络…</div>
      <ResearchLandscape v-else-if="strengthView==='landscape'" :dataset="dataset" @explore="chooseView('continuity')"/>
      <ResearchContinuity v-else :dataset="dataset"/>
    </template>
  </section>
</template>
<style scoped>
.analysis-modules{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin:6px 0 30px}.analysis-modules button{display:flex;align-items:center;gap:16px;text-align:left;padding:19px 22px;border:1px solid #e3dfd9;border-radius:12px;background:#fff;color:#68635f;cursor:pointer;transition:border-color .2s,box-shadow .2s}.analysis-modules button.active{border-color:#ae0d28;box-shadow:inset 0 -3px #ae0d28;color:#ae0d28}.module-no{font-size:15px;font-weight:700;opacity:.65}.analysis-modules b{display:block;font-size:21px;letter-spacing:.4px}.analysis-modules small{display:block;font-size:13px;color:#8c8580;margin-top:6px}.module-arrow{margin-left:auto;font-size:23px}.analysis-modules button:not(.active):hover{border-color:#b6ada7}.analysis-heading{margin:32px 0 23px}.analysis-kicker{font-size:13px!important;color:#ae0d28!important;font-weight:600;letter-spacing:1.4px}.analysis-heading h2{font-size:32px;color:#2d2a28;margin:10px 0 12px;line-height:1.45}.analysis-heading p{font-size:16px;color:#817a74;line-height:1.8;margin:0}.strength-tabs{display:flex;gap:30px;border-bottom:1px solid #ded9d4;margin-bottom:26px}.strength-tabs button{background:none;border:0;border-bottom:3px solid transparent;padding:12px 3px 15px;font-size:17px;color:#7c756f;cursor:pointer}.strength-tabs button.active{color:#ae0d28;border-color:#ae0d28;font-weight:700}.analysis-loading{padding:80px;text-align:center;background:white;border-radius:12px;color:#6b6560}button:focus-visible{outline:3px solid #ac6b7a;outline-offset:4px}@media(max-width:700px){.analysis-modules{gap:7px;margin-bottom:22px}.analysis-modules button{padding:12px 9px;gap:7px}.analysis-modules b{font-size:15px}.analysis-modules small{font-size:11px}.module-no,.module-arrow{display:none}.analysis-heading h2{font-size:25px}.analysis-heading p{font-size:14px}.strength-tabs{gap:22px}.analysis-loading{padding:45px 15px}}
</style>
<style>
.workspace:has(.ai-chain-workspace[data-module="strength"]),.workspace:has(.ai-chain-workspace[data-module="investment"]){width:min(1520px,calc(100% - 80px));max-width:1520px}
@media(max-width:700px){.workspace:has(.ai-chain-workspace[data-module="strength"]),.workspace:has(.ai-chain-workspace[data-module="investment"]){width:calc(100% - 32px)}}
</style>
