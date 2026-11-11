<script setup>
import {useSurface} from '../helpers/useSurface'
import {ref,computed,onMounted,onBeforeUnmount,watch,nextTick} from 'vue'
import {useRoute} from 'vue-router'
import {marked} from 'marked'
import TechnologyEvolutionTree from './TechnologyEvolutionTree.vue'
import FeaturedTechnologyTimeline from './FeaturedTechnologyTimeline.vue'
import PageHero from './PageHero.vue'
import InvestCompare from './invest/InvestCompare.vue'
import {useInvestData} from '../helpers/investData'
import {safeUrl} from '../shared'
const props=defineProps({bootstrap:Object}),route=useRoute()
// 完整技术树（80 个技术点）在 evolution.json；读完再渲染，避免先显示首屏接口里的旧树。结果在模块内缓存，再次进入直接显示。
let cachedExtension=null,pendingExtension=null
function fetchExtension(){
 if(cachedExtension)return Promise.resolve(cachedExtension)
 pendingExtension??=fetch('/evolution/v1/evolution.json').then(async response=>{
  if(!response.ok)throw new Error('技术演进更新暂时无法载入，请刷新页面重试。')
  const extra=await response.json()
  if(!extra.tree?.nodes||!extra.chronology?.events||!Array.isArray(extra.survey_additions))throw new Error('技术演进更新暂时无法载入，请刷新页面重试。')
  return cachedExtension=extra
 }).finally(()=>{pendingExtension=null})
 return pendingExtension
}
const extension=ref(cachedExtension),extensionError=ref(''),extensionReady=ref(!!cachedExtension)
const data=computed(()=>{
 const base=props.bootstrap,extra=extension.value
 if(!extra)return base
 const entries=new Map((base.survey?.entries||[]).map(e=>[e.topic_id+':'+e.route,e]))
 for(const e of extra.survey_additions)entries.set(e.topic_id+':'+e.route,e)
 return {...base,tree:extra.tree,chronology:extra.chronology,survey:{...base.survey,entries:[...entries.values()]}}
})
let alive=true
onBeforeUnmount(()=>{alive=false})
async function loadExtension(){
 try{const extra=await fetchExtension();if(!alive)return;extension.value=extra}
 catch(error){if(alive)extensionError.value=error.message}
 finally{if(alive){extensionReady.value=true;await nextTick();selectFromRoute()}}
}
const {curves:investCurves,error:investError,load:investLoad}=useInvestData()
const topics=computed(()=>data.value.tree.nodes.filter(n=>n.node_type==='technology'))
const groups=computed(()=>data.value.tree.nodes.filter(n=>n.node_type==='category'))
const milestones=computed(()=>data.value.chronology?.events||[])
const entries=computed(()=>data.value.survey.entries.filter(e=>e.route==='B'))
const ready=computed(()=>entries.value.filter(e=>e.ready_for_dashboard).length)
const selectedTopic=ref(''),selectedMilestone=ref(''),groupFilter=ref('all'),topicSearch=ref(''),topicPage=ref(1)
const short=(s,n=75)=>String(s||'').length>n?String(s).slice(0,n)+'…':String(s||'')
const entryFor=(topic,which)=>entries.value.find(e=>e.topic_id===topic&&e.route===which)
const statusLabel=e=>e?.ready_for_dashboard?'阅读综述':'整理中'
const topicDetail=computed(()=>topics.value.find(t=>t.id===selectedTopic.value))
const activeMilestone=computed(()=>milestones.value.find(m=>m.id===selectedMilestone.value)||milestones.value.find(m=>m.topic_id===selectedTopic.value))
const filteredTopics=computed(()=>topics.value.filter(t=>(groupFilter.value==='all'||t.category_id===groupFilter.value)&&(!topicSearch.value||[t.label,...(t.aliases||[])].join(' ').toLowerCase().includes(topicSearch.value.toLowerCase()))))
const pagedTopics=computed(()=>filteredTopics.value.slice((topicPage.value-1)*12,topicPage.value*12))
watch([groupFilter,topicSearch],()=>topicPage.value=1)
const activeRelations=computed(()=>{const m=activeMilestone.value;if(!m)return [];return (data.value.chronology.edges||[]).filter(e=>e.source===m.id||e.target===m.id).map(e=>({...e,from:milestones.value.find(m=>m.id===e.source)?.topic_label,to:milestones.value.find(m=>m.id===e.target)?.topic_label}))})
function pickMilestone(m){selectedMilestone.value=m.id;selectedTopic.value=m.topic_id}
function pickTopic(t){selectedTopic.value=t.id;selectedMilestone.value=milestones.value.find(m=>m.topic_id===t.id)?.id||''}
function selectFromRoute(){if(route.query.search)topicSearch.value=String(route.query.search);groupFilter.value=groups.value.some(g=>g.id===route.query.group)?route.query.group:'all';const m=milestones.value.find(m=>m.id===route.query.milestone);const t=topics.value.find(t=>t.id===route.query.topic);if(m)pickMilestone(m);else if(t)pickTopic(t);else {selectedTopic.value='';selectedMilestone.value=''}}
onMounted(()=>{selectFromRoute();loadExtension()})

watch(()=>[route.query.group,route.query.topic,route.query.milestone],selectFromRoute)
const surveyOpen=ref(false), surveyLoading=ref(false), surveyError=ref(''), surveyData=ref(null), surveyRoute=ref('B'), referenceSearch=ref(''), surveyTab=ref('article')
async function openSurvey(topic,which){selectedTopic.value=topic;surveyRoute.value=which;surveyOpen.value=true;surveyLoading.value=true;surveyError.value='';surveyData.value=null;surveyTab.value='article';referenceSearch.value='';try{const r=await fetch(entryFor(topic,which)?.dashboard_bundle_url||`/api/llm/survey/${encodeURIComponent(topic)}/${which}`);if(!r.ok)throw new Error('综述暂时无法打开，请稍后重试。');surveyData.value=await r.json()}catch(e){surveyError.value=e.message}finally{surveyLoading.value=false}}
function closeSurvey(){surveyOpen.value=false}
const surveyElement=ref(null)
useSurface(surveyOpen,{element:surveyElement,close:closeSurvey,modal:true})
const refs=computed(()=>surveyData.value?.references||[])
const filteredRefs=computed(()=>refs.value.map((r,i)=>({...r,index:i+1})).filter(r=>JSON.stringify(r).toLowerCase().includes(referenceSearch.value.toLowerCase())))
function escapeHtml(s){return String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]))}
const renderedArticle=computed(()=>{const raw=(surveyData.value?.content_md||surveyData.value?.survey_md||'').replace(/<a\s+id=["'][\w-]+["']\s*>\s*<\/a>/gi,'');const html=marked.parse(escapeHtml(raw),{gfm:true,breaks:false});const doc=new DOMParser().parseFromString(html,'text/html');doc.querySelectorAll('a').forEach(a=>{a.href=safeUrl(a.getAttribute('href'));a.target='_blank';a.rel='noopener noreferrer'});doc.querySelectorAll('img').forEach(i=>{const span=doc.createElement('span');span.textContent=i.alt;i.replaceWith(span)});doc.querySelectorAll('h1,h2,h3').forEach((h,i)=>h.id='section-'+i);const walker=doc.createTreeWalker(doc.body,NodeFilter.SHOW_TEXT);const textNodes=[];while(walker.nextNode()){if(!walker.currentNode.parentElement.closest('a,button,code,pre'))textNodes.push(walker.currentNode)};for(const text of textNodes){const pattern=/\[(\d{1,3})\]/g;const matches=[...text.textContent.matchAll(pattern)].filter(m=>Number(m[1])<=refs.value.length&&Number(m[1])>0);if(!matches.length)continue;const fragment=doc.createDocumentFragment();let end=0;for(const m of matches){fragment.append(text.textContent.slice(end,m.index));const b=doc.createElement('button');b.className='inline-citation';b.dataset.ref=m[1];b.textContent=m[0];b.title='查看参考文献 '+m[1];fragment.append(b);end=m.index+m[0].length}fragment.append(text.textContent.slice(end));text.replaceWith(fragment)};return doc.body.innerHTML})
const articleToc=computed(()=>{const doc=new DOMParser().parseFromString(renderedArticle.value,'text/html');return [...doc.querySelectorAll('h1,h2')].map(h=>({id:h.id,text:h.textContent}))})
const highlightedReference=ref(null)
async function onArticleClick(event){const b=event.target.closest('[data-ref]');if(!b)return;highlightedReference.value=Number(b.dataset.ref);referenceSearch.value='';surveyTab.value='references';await nextTick();document.getElementById('reference-'+b.dataset.ref)?.scrollIntoView({block:'center',behavior:'smooth'})}
function goLibrary(){document.querySelector('.tech-library')?.scrollIntoView({behavior:'smooth',block:'start'})}
function goSection(id){document.getElementById(id)?.scrollIntoView({behavior:'smooth',block:'start'})}
</script>
<template><div class="evolution-page">
<div v-if="!extensionReady" class="empty-state evolution-loading">正在读取技术演进数据…</div>
<template v-else>
<PageHero class="evolution-hero" title="人工智能技术演进与研究综述" lead="以共同技术词表组织 7 个技术方向、80 个技术点，沿时间梳理代表方法与跨方向联系，并为每个技术点提供可读综述" :stats="[{value:groups.length,label:'技术方向'},{value:topics.length,label:'技术点'},{value:ready,label:'篇综述'}]" :action="{label:'浏览综述库'}" @action="goLibrary"/>
<p v-if="extensionError" role="status" class="chart-note">{{extensionError}}</p>
<section class="panel evolution-tree-panel"><div class="panel-heading"><div><h3>人工智能技术演进树</h3></div></div><TechnologyEvolutionTree :tree="data.tree" :chronology="data.chronology" :entries="entries" :selected="selectedTopic" :selected-event="selectedMilestone" @select="pickMilestone" @survey="id=>openSurvey(id,'B')"/></section>
<section class="panel featured-tech-panel"><div class="panel-heading"><h3>关键技术里程碑</h3></div><FeaturedTechnologyTimeline :tree="data.tree" :chronology="data.chronology" :entries="entries" @survey="id=>openSurvey(id,'B')"/></section>
    <section class="panel tech-library"><div class="panel-title"><div><h3>技术点与综述</h3></div><label class="search-box"><span>⌕</span><input v-model="topicSearch" placeholder="查找技术词、别名" aria-label="查找技术主题"/></label></div><div class="group-tabs"><button :class="{active:groupFilter==='all'}" @click="groupFilter='all'">全部 {{topics.length}}</button><button v-for="g in groups" :key="g.id" :class="{active:groupFilter===g.id}" @click="groupFilter=g.id">{{g.label}}</button></div><div :key="groupFilter+':'+topicPage" class="topic-grid pane-swap"><article v-for="t in pagedTopics" :key="t.id" class="topic-card" :class="{selected:selectedTopic===t.id}"><button class="topic-title" @click="pickTopic(t)"><span>{{t.id}} · {{t.level2}}</span><h4>{{t.label}}</h4><p>{{short(t.aliases?.join(' · '),75)}}</p></button><div class="topic-routes"><button v-for="which in ['B']" :key="which" :class="{available:entryFor(t.id,which)?.ready_for_dashboard}" :disabled="!entryFor(t.id,which)?.ready_for_dashboard" @click="openSurvey(t.id,which)"><span>{{statusLabel(entryFor(t.id,which))}}</span><small v-if="entryFor(t.id,which)?.actual_references">{{entryFor(t.id,which).actual_references}} 篇引用文献</small><span v-if="entryFor(t.id,which)?.ready_for_dashboard">↗</span></button></div></article></div><div class="pagination" style="justify-content:flex-end"><div><button :disabled="topicPage===1" @click="topicPage--">上一页</button><span>{{topicPage}} / {{Math.max(1,Math.ceil(filteredTopics.length/12))}}</span><button :disabled="topicPage*12>=filteredTopics.length" @click="topicPage++">下一页</button></div></div><p v-if="!filteredTopics.length" class="empty-state">没有找到符合筛选的技术主题。</p></section>
<section class="panel evolution-invest-panel"><p v-if="investError" class="empty-state">投入与产出数据暂时无法读取 <button @click="investLoad">重新读取</button></p><p v-else-if="!investCurves" class="empty-state">正在读取投入与产出数据…</p><InvestCompare v-else :curves="investCurves"/></section>
</template>
  <Teleport to="body"><div v-if="surveyOpen" class="survey-overlay" @click.self="closeSurvey"><section class="survey-modal" ref="surveyElement" role="dialog" aria-modal="true" aria-labelledby="survey-title"><header class="survey-modal-header"><div><span class="eyebrow">TECHNICAL SURVEY</span><h2 id="survey-title">{{surveyData?.title||topicDetail?.label+' · 技术演进综述'}}</h2></div><button class="close-button" aria-label="关闭综述" @click="closeSurvey">×</button></header><div class="survey-meta"><span>技术演进综述</span><span v-if="refs.length">{{refs.length}} 篇引用文献</span></div><div class="survey-tabs"><button :class="{active:surveyTab==='article'}" @click="surveyTab='article'">综述正文</button><button :class="{active:surveyTab==='references'}" @click="surveyTab='references'">参考文献 {{refs.length||''}}</button></div><div v-if="surveyLoading" class="empty-state">正在载入完整综述…</div><div v-else-if="surveyError" class="empty-state">{{surveyError}}</div><div v-else-if="surveyTab==='article'" class="survey-reading-layout pane-swap"><aside class="survey-toc"><span>文章目录</span><button v-for="s in articleToc" :key="s.id" @click="goSection(s.id)">{{short(s.text,42)}}</button></aside><article class="survey-prose" @click="onArticleClick" v-html="renderedArticle"></article></div><section v-else class="references-pane"><label class="search-box"><span>⌕</span><input v-model="referenceSearch" placeholder="搜索标题、作者或年份" aria-label="搜索参考文献"/></label><p class="chart-note">{{filteredRefs.length}} / {{refs.length}} 篇引用文献</p><article v-for="r in filteredRefs" :key="r.index" :id="'reference-'+r.index" class="reference-item" :class="{highlighted:highlightedReference===r.index}"><b>{{String(r.index).padStart(2,'0')}}</b><div><h4><a v-if="r.url||r.doi" :href="safeUrl(r.url||(String(r.doi).startsWith('http')?r.doi:'https://doi.org/'+r.doi))" target="_blank" rel="noopener">{{r.title||r.paper_title||'未提供标题'}} ↗</a><span v-else>{{r.title||r.paper_title||'未提供标题'}}</span></h4><p>{{r.year||'年份未提供'}} · {{Array.isArray(r.authors)?r.authors.map(a=>typeof a==='object'?a.name:a).join(', '):r.authors||''}}</p><small>{{r.venue||r.journal||''}}</small></div></article></section></section></div></Teleport>
</div></template>
<style scoped>
.evolution-loading{min-height:60vh;display:grid;place-items:center}
.evolution-hero :deep(.page-hero-head){flex-wrap:wrap}
.evolution-hero :deep(.page-hero-head>div:first-child){flex:1 1 700px;min-width:0}
.evolution-hero :deep(h2){white-space:nowrap}
@media(max-width:1050px){.evolution-hero :deep(.page-hero-head>div:first-child){flex:auto}}
@media(max-width:600px){.evolution-hero :deep(h2){font-size:clamp(16px,4.5vw,26px)}}
</style>
