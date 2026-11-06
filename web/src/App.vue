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
import EvolutionHub from './components/EvolutionHub.vue'
const route=useRoute(), router=useRouter(), data=ref(null), error=ref(''), loading=ref(false), updated=ref(''), viewSettled=ref(false)
provide('viewSettled', viewSettled)
const stageKey=computed(()=>domain.value==='lowalt'&&!['home','overview'].includes(route.name)?'lowalt':String(route.name))
const nav=[['home','首页'],['overview','数据总览'],['data','领域数据'],['evolution','技术演进'],['chain','证据链'],['cases','案例专题']]
const domain=computed(()=>['ai','lowalt'].includes(route.query.domain)?route.query.domain:sessionStorage.getItem('gzk-research-domain')==='lowalt'?'lowalt':'ai')
const activeNav=computed(()=>Math.max(0,nav.findIndex(([id])=>id===route.name)))
const navIcons=['M3 11l9-8 9 8 M5 9v12h5v-7h4v7h5V9','M3 5c0-3 18-3 18 0s-18 3-18 0v7c0 3 18 3 18 0V5 M3 12v7c0 3 18 3 18 0v-7','M4 20h17 M5 16h3v-5H5z M11 16h3V6h-3z M17 16h3V3h-3z','M3 20h18 M4 15l5-6 5 3 6-9 M18 3h3v3','M8 7h8 M7 8v8 M16 8l-7 8 M17 8v8 M4 4h6v6H4z M14 4h6v6h-6z M4 16h6v6H4z M14 16h6v6h-6z','M3 7h18v14H3z M8 7V3h8v4 M3 12h18 M10 12v3h4v-3']
function navTo(id){return {path:'/'+id,query:['home','overview'].includes(id)?{}:{domain:domain.value}}}
function selectDomain(value){if(domain.value!==value)router.push({path:route.path,query:{domain:value}})}
async function load(){loading.value=true;try{const [base,current]=await Promise.all([api('/api/llm/bootstrap'),api('/chain-analysis/v1/current-inventory.json')]);data.value=applyCurrentInventory(base,current);updated.value=new Date().toLocaleTimeString('zh-CN',{hour12:false});error.value=''}catch(e){error.value=e.message}finally{loading.value=false}}
let timer,settleToken=0
function settleView(){viewSettled.value=false;const token=++settleToken;nextTick(()=>requestAnimationFrame(()=>setTimeout(()=>{if(token===settleToken)viewSettled.value=true},70)))}
watch(stageKey,settleView)
onMounted(()=>{settleView();load();timer=setInterval(load,60000)});onBeforeUnmount(()=>clearInterval(timer))
</script>
<template><div class="dashboard-shell" :class="{'landing-shell':route.name==='home'}"><header class="research-header">
  <svg class="masthead-lines" viewBox="0 0 1600 200" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><g fill="none" stroke="currentColor"><path d="M0 130C180 100 130 20 310 50S610 170 840 90s340-70 760 30"/><path d="M0 165C220 40 330 160 510 90S1000 130 1120 45s360 30 480-30"/><path d="M0 70L170 140 290 54 430 115 605 70M1010 150l160-95 180 85 140-70 110 40"/></g><g fill="currentColor"><circle cx="170" cy="140" r="3"/><circle cx="290" cy="54" r="4"/><circle cx="430" cy="115" r="3"/><circle cx="1170" cy="55" r="4"/><circle cx="1350" cy="140" r="3"/><circle cx="1490" cy="70" r="3"/></g></svg>
  <div class="research-heading"><div class="masthead-caption"><span></span>基础研究 · 多源数据 · 多维评估<span></span></div><h1>基础研究数据与评估系统</h1></div>
  <div class="research-actions"><button @click="load" :disabled="loading" :title="'上次刷新 '+updated" aria-label="刷新展示状态"><svg viewBox="0 0 24 24" :class="{spinning:loading}" aria-hidden="true"><path d="M20 10a8 8 0 1 0-1 7 M20 3v7h-7"/></svg>{{loading?'读取中':'刷新数据'}}</button></div>
</header>
<nav class="research-nav" aria-label="主导航"><div class="nav-track"><span class="nav-indicator" :style="{transform:`translateX(${activeNav*100}%)`}" aria-hidden="true"></span><router-link v-for="([id,label],i) in nav" :key="id" :to="navTo(id)" :class="{active:route.name===id}"><svg viewBox="0 0 24 24" aria-hidden="true"><path :d="navIcons[i]"/></svg><span>{{label}}</span></router-link></div></nav><main class="workspace" :class="{'home-workspace':route.name==='home'}"><div v-if="error && route.name!=='home'" class="notice error">{{error}} <button @click="load">重新连接</button></div><HomePage v-if="route.name==='home'" :data="data"/><template v-else-if="data"><div v-if="route.name!=='overview'" class="domain-switch" aria-label="研究领域"><span>研究领域</span><div role="tablist" aria-label="选择研究领域"><button role="tab" :aria-selected="domain==='lowalt'" :class="{active:domain==='lowalt'}" @click="selectDomain('lowalt')">低空经济</button><button role="tab" :aria-selected="domain==='ai'" :class="{active:domain==='ai'}" @click="selectDomain('ai')">人工智能</button></div><small>{{domain==='ai'?'大语言模型与生成式人工智能':'低空经济与应用场景'}}</small></div><div :key="stageKey" class="view-stage view-enter"><OverviewHub v-if="route.name==='overview'" :data="data"/><LowAltitudeEmbed v-else-if="domain==='lowalt'" :page="String(route.name)"/><DomainHub v-else-if="route.name==='data'" :data="data"/><EvidenceHub v-else-if="route.name==='chain'" :data="data"/><EvolutionHub v-else-if="route.name==='evolution'" :bootstrap="data"/><template v-else><div class="page-heading"><div><h2>案例专题 <span class="title-badge">筹备中</span></h2><p>围绕技术、企业与政策，组织创新链、产业链与政策链的专题研究。</p></div></div><div class="two-columns"><section class="panel case-pending"><div class="section-number">01</div><h3>产业链 · 企业与产品</h3><p>追踪企业、产品与产业联系，研究技术应用和经济表现。</p><ul><li>企业与产品清单、标识及时间</li><li>论文 / 专利与技术采用证据</li><li>关注度、招聘与经济模型结果</li></ul><span class="status-badge amber">专题筹备中</span></section><section class="panel case-pending"><div class="section-number">02</div><h3>政策链 · 政策工具与影响</h3><p>结合政策时间、地域与作用对象，研究政策工具及其与创新、产业的互动。</p><ul><li>政策层级、支持与限制类型</li><li>政策文本解构与技术定位</li><li>政策工具及影响评估结果</li></ul><router-link to="/data?type=policy" class="button">查看已有政策数据 →</router-link></section></div></template></div></template><div v-else-if="!error" class="empty-state">正在读取数据基座与研究成果…</div></main><footer v-if="route.name!=='home'" class="page-footer"><div class="page-footer-inner"><div class="page-footer-main"><div class="page-footer-brand"><b>基础研究数据与评估系统</b><span>国家自然科学基金委员会专项项目 · 基础研究全链条数据系统构建与集成</span></div><nav class="page-footer-nav" aria-label="页尾导航"><router-link v-for="[id,label] in nav" :key="id" :to="navTo(id)">{{label}}</router-link></nav></div><div class="page-footer-meta"><span>中国人民大学 · 国家治理大数据和人工智能创新平台</span><span><a href="mailto:brain@ruc.edu.cn">brain@ruc.edu.cn</a><i aria-hidden="true">·</i><a href="https://brain.ruc.edu.cn" target="_blank" rel="noopener">brain.ruc.edu.cn ↗</a></span></div></div></footer></div></template>
