<script setup>
import {computed,ref,watch,nextTick,onMounted,onBeforeUnmount} from 'vue'
import {horizontalLayout,horizontalCurve,treeColors,labelLines} from '../technologyTreeLayout'
import {safeUrl} from '../shared'
import '../evolution-tree.css'
const props=defineProps({tree:Object,chronology:Object,entries:Array,selected:String,selectedEvent:String})
const emit=defineEmits(['select','survey'])
const shell=ref(null),detail=ref(null),scroller=ref(null),hover=ref(''),highlight=ref(''),detailsOpen=ref(false),search=ref('')
const layout=computed(()=>horizontalLayout(props.tree,props.chronology))
const yearLabel=y=>y===2016?'≤ 2016':String(y)

/* ---------- 选择、详情与悬停 ---------- */
const selectedPoint=computed(()=>layout.value.points.find(p=>p.id===props.selectedEvent)||layout.value.points.find(p=>p.topic_id===props.selected))
const active=computed(()=>layout.value.points.find(p=>p.id===hover.value)||selectedPoint.value)
const linked=computed(()=>new Set(layout.value.edges.filter(e=>e.source===active.value?.id||e.target===active.value?.id).flatMap(e=>[e.source,e.target])))
const relations=computed(()=>layout.value.edges.filter(e=>e.source===selectedPoint.value?.id||e.target===selectedPoint.value?.id))
const entry=computed(()=>props.entries?.find(e=>e.topic_id===selectedPoint.value?.topic_id&&e.route==='B'))
const topic=computed(()=>props.tree.nodes.find(n=>n.id===selectedPoint.value?.topic_id))
const matches=computed(()=>new Set(layout.value.points.filter(p=>[p.topic_label,p.label,p.title].join(' ').toLowerCase().includes(search.value.toLowerCase())).map(p=>p.id)))
const categoryLabel=id=>props.tree.nodes.find(n=>n.id===id)?.label||id
const nodeTitle=p=>{const l=labelLines(p.label,11);return l[0]+(l.length>1?'…':'')}
const nodeSub=p=>{const t=String(p.topic_label).replace(/（[^）]*）/g,'');return t.length>11?t.slice(0,10)+'…':t}
function choose(p){stop();emit('select',p);detailsOpen.value=true;scrollToX(p.x+p.w/2)}
function closeDetails(restoreFocus=false){detailsOpen.value=false;if(restoreFocus&&selectedPoint.value)nextTick(()=>document.getElementById('tree-'+selectedPoint.value.id)?.focus({preventScroll:true}))}
function onOutsidePointer(event){
 if(!detailsOpen.value||detail.value?.contains(event.target)||document.querySelector('.survey-overlay'))return
 const node=event.target instanceof Element?event.target.closest('.tree-topic-node'):null
 if(node&&shell.value?.contains(node))return
 closeDetails()
}
function onDetailKey(event){if(event.key!=='Escape'||!detailsOpen.value||document.querySelector('.survey-overlay'))return;closeDetails(true)}
async function openSelectedSurvey(){if(document.fullscreenElement)await document.exitFullscreen?.();emit('survey',selectedPoint.value.topic_id)}
function locate(){const p=layout.value.points.find(x=>matches.value.has(x.id));if(p)choose(p)}
async function fullscreen(){if(document.fullscreenElement)await document.exitFullscreen?.();else await shell.value?.requestFullscreen?.()}
watch(()=>props.selectedEvent,id=>{if(!id)return;detailsOpen.value=true;const p=layout.value.points.find(x=>x.id===id);if(p){stop();nextTick(()=>scrollToX(p.x+p.w/2))}})

/* ---------- 横向滚动与全景条 ---------- */
const viewW=ref(1),scrollX=ref(0)
function measure(){const el=scroller.value;if(!el)return;viewW.value=el.clientWidth;scrollX.value=el.scrollLeft}
function scrollToX(x,smooth=true){const el=scroller.value;if(!el)return;el.scrollTo({left:Math.max(0,x-el.clientWidth/2),behavior:smooth&&!reduced()?'smooth':'auto'})}
const reduced=()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches
const mini=ref(null)
const miniWin=computed(()=>({left:100*scrollX.value/layout.value.width+'%',width:Math.min(100,100*viewW.value/layout.value.width)+'%'}))
function miniJump(event){const r=mini.value.getBoundingClientRect();scrollToX((event.clientX-r.left)/r.width*layout.value.width,false)}
let dragging=false
function miniDown(e){stop();dragging=true;miniJump(e);mini.value.setPointerCapture?.(e.pointerId)}
function miniMove(e){if(dragging)miniJump(e)}
function miniUp(){dragging=false}
let ro
onMounted(()=>{document.addEventListener('pointerdown',onOutsidePointer,true);document.addEventListener('keydown',onDetailKey);ro=new ResizeObserver(measure);scroller.value&&ro.observe(scroller.value);measure()})
onBeforeUnmount(()=>{document.removeEventListener('pointerdown',onOutsidePointer,true);document.removeEventListener('keydown',onDetailKey);ro?.disconnect();stop()})

/* ---------- 按年播放 ---------- */
const lastIndex=computed(()=>layout.value.years.length-1)
const shownIndex=ref(-1) // -1 表示全部显示
const playing=ref(false)
let timer
const shownYear=computed(()=>shownIndex.value<0?null:layout.value.years[shownIndex.value])
const isFuture=p=>shownYear.value!==null&&p.yearKey>shownYear.value
const isCurrent=p=>shownYear.value!==null&&p.yearKey===shownYear.value
function goYear(i){shownIndex.value=Math.max(0,Math.min(lastIndex.value,i));const L=layout.value;scrollToX(L.left+(shownIndex.value+.5)*L.colW)}
function step(){if(shownIndex.value>=lastIndex.value){stop();return}goYear(shownIndex.value+1)}
function play(){if(playing.value){stop();return}if(shownIndex.value<0||shownIndex.value>=lastIndex.value)goYear(0);playing.value=true;timer=setInterval(step,reduced()?600:1700)}
function stop(){playing.value=false;clearInterval(timer)}
function prev(){stop();goYear((shownIndex.value<0?lastIndex.value:shownIndex.value)-1)}
function next(){stop();goYear((shownIndex.value<0?-1:shownIndex.value)+1)}
function showAll(){stop();shownIndex.value=-1;search.value='';highlight.value='';detailsOpen.value=false;hover.value=''}
function pickYear(i){stop();goYear(i)}
</script>

<template><div ref="shell" class="evolution-tree h-tree">
<div class="tree-toolbar">
 <div class="tree-legend"><button v-for="l in layout.lanes" :key="l.id" :class="{active:highlight===l.id}" :style="{'--branch-color':l.tone}" @click="highlight=highlight===l.id?'':l.id"><i></i>{{l.label}}</button></div>
 <div class="tree-tools"><button class="tree-play" :class="{on:playing}" @click="play">{{playing?'❚❚ 暂停':'▶ 按年播放'}}</button><button @click="prev" aria-label="上一年">‹ 上一年</button><button @click="next" aria-label="下一年">下一年 ›</button><button @click="showAll">全部显示</button><label><input v-model="search" placeholder="定位技术关键词" aria-label="定位技术关键词" @keydown.enter="locate"/><button @click="locate">定位</button></label><button @click="fullscreen">全屏</button></div>
</div>
<div class="tree-canvas-area">
 <div class="h-lanes" aria-hidden="true" :style="{height:layout.height-layout.axisH+'px'}"><div v-for="l in layout.lanes" :key="l.id" :style="{height:l.h+'px','--c':l.tone}"><span>{{l.label}}</span></div></div>
 <div ref="scroller" class="tree-scroll h-scroll" @scroll="measure">
 <svg class="evolution-tree-svg" :width="layout.width" :height="layout.height" :viewBox="`0 0 ${layout.width} ${layout.height}`" role="img" aria-label="人工智能技术演进树，横轴为年份，纵向为七类技术方向">
  <g><rect v-for="(l,i) in layout.lanes" :key="l.id" x="0" :y="l.y" :width="layout.width" :height="l.h" :fill="i%2?'#fbf7f4':'#fffcf9'"/></g>
  <g><line v-for="(y,i) in layout.years" :key="'g'+y" :x1="layout.left+i*layout.colW" :x2="layout.left+i*layout.colW" y1="0" :y2="layout.height-layout.axisH" stroke="#ece4df" stroke-dasharray="3 6"/></g>
  <rect v-if="shownYear!==null" class="h-current-col" :x="layout.left+shownIndex*layout.colW" y="0" :width="layout.colW" :height="layout.height-layout.axisH"/>
  <g class="h-axis"><line :x1="layout.left-12" :x2="layout.width-12" :y1="layout.height-30" :y2="layout.height-30"/><path :d="`M${layout.width-22},${layout.height-35} L${layout.width-11},${layout.height-30} L${layout.width-22},${layout.height-25}`"/>
   <g v-for="(y,i) in layout.years" :key="'a'+y" :class="{on:shownYear===y}" @click="pickYear(i)"><line :x1="layout.left+(i+.5)*layout.colW" :x2="layout.left+(i+.5)*layout.colW" :y1="layout.height-34" :y2="layout.height-26"/><text :x="layout.left+(i+.5)*layout.colW" :y="layout.height-8">{{yearLabel(y)}}</text></g></g>
  <g class="tree-evidence-edges"><path v-for="e in layout.edges" :key="e.id" :d="horizontalCurve(e)" fill="none" :stroke="e.from.tone" :stroke-width="hover&&(e.source===hover||e.target===hover)?2.8:1.5" :stroke-dasharray="e.kind==='shared_work'?'3 5':null" :opacity="isFuture(e.to)||isFuture(e.from)?.06:hover?(e.source===hover||e.target===hover?.92:.06):.45" class="h-edge"><title>{{e.from.topic_label}} → {{e.to.topic_label}}：{{e.label}}</title></path></g>
  <g v-for="p in layout.points" :key="p.id" :id="'tree-'+p.id" class="tree-topic-node h-node" :class="{selected:selectedPoint?.id===p.id,related:hover&&linked.has(p.id),future:isFuture(p),current:isCurrent(p)}" :opacity="isFuture(p)?.18:(highlight&&highlight!==p.category_id)||(search&&!matches.has(p.id))?.25:1" tabindex="0" role="button" :aria-expanded="detailsOpen&&selectedPoint?.id===p.id" :aria-label="`${p.year} ${p.topic_label} ${p.label}`" @mouseenter="hover=p.id" @mouseleave="hover=''" @click="choose(p)" @keydown.enter="choose(p)" @keydown.space.prevent="choose(p)">
   <rect :x="p.x" :y="p.y" :width="p.w" :height="p.h" rx="3" fill="#fff" :stroke="p.tone" :stroke-width="selectedPoint?.id===p.id||isCurrent(p)?2:1"/><rect :x="p.x" :y="p.y" :width="p.w" :height="p.h" rx="3" :fill="p.tone" :opacity="selectedPoint?.id===p.id?.14:.04"/><rect :x="p.x" :y="p.y" width="3" :height="p.h" :fill="p.tone"/>
   <text :x="p.x+12" :y="p.y+19" font-size="13" font-weight="700" fill="#2f353b">{{nodeTitle(p)}}</text><text :x="p.x+12" :y="p.y+35" font-size="11" :fill="p.tone">{{p.year}} · {{nodeSub(p)}}</text><title>{{p.topic_label}}\n{{p.year}} · {{p.title}}</title></g>
 </svg></div>
 <aside v-if="detailsOpen&&selectedPoint" ref="detail" class="tree-node-detail" :style="{'--branch-color':selectedPoint.tone}" aria-label="技术节点详情"><div class="tree-detail-top"><span>{{categoryLabel(selectedPoint.category_id)}}</span><button aria-label="收起节点详情" @click="closeDetails(true)">×</button></div><p class="tree-detail-year">{{selectedPoint.year}}<small>{{topic?.level2}}</small></p><h3>{{selectedPoint.topic_label}}</h3><p class="tree-definition">{{topic?.source?.cells?.C}}</p><button class="tree-survey-open" :disabled="!entry?.ready_for_dashboard" @click="openSelectedSurvey"><span>{{entry?.ready_for_dashboard?'阅读技术综述':'综述整理中'}}</span><small v-if="entry?.ready_for_dashboard">{{entry.actual_references}} 篇引用文献 ↗</small></button><a class="tree-source-paper" :href="safeUrl(selectedPoint.url)" target="_blank" rel="noopener"><span>代表成果 ↗</span><b>{{selectedPoint.title}}</b></a><p v-if="selectedPoint.authors?.length" class="tree-people">{{selectedPoint.authors.join(' · ')}}</p><p v-if="selectedPoint.institutions?.length" class="tree-people">{{selectedPoint.institutions.join(' · ')}}</p><div v-if="relations.length" class="tree-relation-list"><h4>相关技术联系</h4><a v-for="e in relations" :key="e.id" :href="safeUrl(e.source_url)" target="_blank" rel="noopener"><b>{{e.from.topic_label}} · {{e.to.topic_label}}</b><span>{{e.label}} ↗</span></a></div></aside>
</div>
<div class="h-overview">
 <span>全景</span>
 <div ref="mini" class="h-mini" role="slider" aria-label="拖动查看技术树不同年份" :aria-valuenow="Math.round(scrollX)" @pointerdown="miniDown" @pointermove="miniMove" @pointerup="miniUp" @pointercancel="miniUp">
  <i v-for="p in layout.points" :key="'m'+p.id" :style="{left:100*p.x/layout.width+'%',top:100*p.y/layout.height+'%',width:100*p.w/layout.width+'%',background:p.tone,opacity:isFuture(p)?.2:.85}"></i>
  <b class="h-mini-win" :style="miniWin"></b>
 </div>
 <div class="h-years"><button v-for="(y,i) in layout.years" :key="'p'+y" :class="{on:shownYear===y}" @click="pickYear(i)">{{y===2016?'≤16':String(y).slice(2)}}</button></div>
</div>
<p class="h-hint">横向滚动或拖动全景框查看各年份；按年播放时视窗随年份推进，当年新增技术依次点亮；点击节点查看详情与综述。</p>
</div></template>
