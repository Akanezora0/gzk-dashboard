<script setup>
import {ref,computed,onMounted,onBeforeUnmount,provide,watch,nextTick} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import {api} from './shared'
import {applyCurrentInventory} from './helpers/currentInventory'
import './study.css'
import './inventory.css'
import HomePage from './components/HomePage.vue'
import './home.css'
import OverviewHub from './components/OverviewHub.vue'
import DomainHub from './components/DataWorkspace.vue'
import LowAltitudeEmbed from './components/LowAltitudeEmbed.vue'
import EvidenceHub from './components/AiChainWorkspace.vue'
import CaseHub from './components/cases/CaseHub.vue'
import AssessHub from './components/AssessHub.vue'
import EvolutionHub from './components/EvolutionHub.vue'
const route=useRoute(), router=useRouter(), data=ref(null), error=ref(''), loading=ref(false), updated=ref(''), viewSettled=ref(false)
provide('viewSettled', viewSettled)
const stageKey=computed(()=>domain.value==='lowalt'&&!['home','overview','assess'].includes(route.name)?'lowalt':String(route.name))
const nav=[['home','首页'],['overview','数据总览'],['data','领域数据'],['evolution','技术演进'],['chain','创新链分析'],['cases','案例专题'],['assess','评估']]
const domain=computed(()=>['ai','lowalt'].includes(route.query.domain)?route.query.domain:sessionStorage.getItem('gzk-research-domain')==='lowalt'?'lowalt':'ai')
const activeNav=computed(()=>Math.max(0,nav.findIndex(([id])=>id===route.name)))
const navIcons=['M3 11l9-8 9 8 M5 9v12h5v-7h4v7h5V9','M3 5c0-3 18-3 18 0s-18 3-18 0v7c0 3 18 3 18 0V5 M3 12v7c0 3 18 3 18 0v-7','M4 20h17 M5 16h3v-5H5z M11 16h3V6h-3z M17 16h3V3h-3z','M3 20h18 M4 15l5-6 5 3 6-9 M18 3h3v3','M8 7h8 M7 8v8 M16 8l-7 8 M17 8v8 M4 4h6v6H4z M14 4h6v6h-6z M4 16h6v6H4z M14 16h6v6h-6z','M3 7h18v14H3z M8 7V3h8v4 M3 12h18 M10 12v3h4v-3','M4 20V10 M10 20V4 M16 20v-7 M3 20h18 M18 7l3-3 M21 7V4h-3']
function navTo(id){return {path:'/'+id,query:['home','overview','assess'].includes(id)?{}:{domain:domain.value}}}
function selectDomain(value){if(domain.value!==value)router.push({path:route.path,query:{domain:value}})}
async function load(){loading.value=true;try{const [base,current]=await Promise.all([api('/api/llm/bootstrap'),api('/chain-analysis/v1/current-inventory.json')]);data.value=applyCurrentInventory(base,current);updated.value=new Date().toLocaleTimeString('zh-CN',{hour12:false});error.value=''}catch(e){error.value=e.message}finally{loading.value=false}}
let timer,settleToken=0
function settleView(){viewSettled.value=false;const token=++settleToken;nextTick(()=>requestAnimationFrame(()=>setTimeout(()=>{if(token===settleToken)viewSettled.value=true},70)))}
watch(stageKey,settleView)
onMounted(()=>{settleView();load();timer=setInterval(load,60000)});onBeforeUnmount(()=>clearInterval(timer))
</script>
<template><div class="dashboard-shell" :class="{'landing-shell':route.name==='home'}"><header class="site-strip"><div class="site-inner"><span>国家自然科学基金委员会专项项目 · 基础研究全链条数据系统构建与集成</span><span class="site-strip-r"><span class="site-org">中国人民大学</span><button @click="load" :disabled="loading" :title="'上次刷新 '+updated" aria-label="刷新展示状态"><svg viewBox="0 0 24 24" :class="{spinning:loading}" aria-hidden="true"><path d="M20 10a8 8 0 1 0-1 7 M20 3v7h-7"/></svg>{{loading?'读取中':'刷新数据'}}</button></span></div></header>
<nav class="site-bar" aria-label="主导航"><div class="site-inner"><router-link to="/home" class="site-brand" aria-label="基础研究数据与评估系统 · 首页"><i aria-hidden="true"></i><b>基础研究数据与评估系统</b></router-link><div class="site-nav" :style="{'--n':nav.length}"><span class="site-ind" :class="{off:!nav.some(([id])=>id===route.name)}" :style="{transform:`translateX(${activeNav*100}%)`}" aria-hidden="true"></span><router-link v-for="([id,label],i) in nav" :key="id" :to="navTo(id)" :class="{active:route.name===id}"><svg viewBox="0 0 24 24" aria-hidden="true"><path :d="navIcons[i]"/></svg><span>{{label}}</span></router-link></div></div></nav><main class="workspace" :class="{'home-workspace':route.name==='home'}"><div v-if="error && route.name!=='home'" class="notice error">{{error}} <button @click="load">重新连接</button></div><HomePage v-if="route.name==='home'" :data="data"/><template v-else-if="data"><div v-if="!['overview','assess'].includes(route.name)" class="domain-switch" aria-label="研究领域"><span>研究领域</span><div role="tablist" aria-label="选择研究领域"><button role="tab" :aria-selected="domain==='lowalt'" :class="{active:domain==='lowalt'}" @click="selectDomain('lowalt')">低空经济</button><button role="tab" :aria-selected="domain==='ai'" :class="{active:domain==='ai'}" @click="selectDomain('ai')">人工智能</button></div><small>{{domain==='ai'?'大语言模型与生成式人工智能':'低空经济与应用场景'}}</small></div><div :key="stageKey" class="view-stage view-enter"><OverviewHub v-if="route.name==='overview'" :data="data"/><AssessHub v-else-if="route.name==='assess'"/><LowAltitudeEmbed v-else-if="domain==='lowalt'" :page="String(route.name)"/><DomainHub v-else-if="route.name==='data'" :data="data"/><EvidenceHub v-else-if="route.name==='chain'" :data="data"/><EvolutionHub v-else-if="route.name==='evolution'" :bootstrap="data"/><CaseHub v-else :data="data"/></div></template><div v-else-if="!error" class="empty-state">正在读取数据基座与研究成果…</div></main><footer v-if="route.name!=='home'" class="page-footer"><div class="page-footer-inner"><div class="page-footer-main"><div class="page-footer-brand"><b>基础研究数据与评估系统</b><span>国家自然科学基金委员会专项项目<br/>基础研究全链条数据系统构建与集成</span></div><div class="page-footer-col"><h4>系统导航</h4><ul class="nav-list"><li v-for="[id,label] in nav" :key="id"><router-link :to="navTo(id)">{{label}}</router-link></li></ul></div><div class="page-footer-col"><h4>建设平台</h4><ul><li><a href="https://brain.ruc.edu.cn" target="_blank" rel="noopener">国家治理大数据和人工智能创新平台</a></li><li><a href="mailto:brain@ruc.edu.cn">brain@ruc.edu.cn</a></li><li><a href="https://brain.ruc.edu.cn" target="_blank" rel="noopener">brain.ruc.edu.cn</a></li></ul></div></div><div class="page-footer-meta"><span>基础研究数据与评估系统 · 中国人民大学 · 国家自然科学基金委员会</span><span>中国人民大学公共教学一楼三层 1301</span></div></div></footer></div></template>
