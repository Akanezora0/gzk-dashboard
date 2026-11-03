<script setup>
import {computed,ref,watch,nextTick,onMounted,onBeforeUnmount} from 'vue'
import {treeLayout,treeColors,labelLines,shortWorkLabel,relationCurve} from '../technologyTreeLayout'
import {safeUrl} from '../shared'
import '../evolution-tree.css'
const props=defineProps({tree:Object,chronology:Object,entries:Array,selected:String,selectedEvent:String})
const emit=defineEmits(['select','survey'])
const shell=ref(null),detail=ref(null),scroller=ref(null),zoom=ref(1),hover=ref(''),highlight=ref(''),detailsOpen=ref(false),search=ref('')
const layout=computed(()=>treeLayout(props.tree,props.chronology))
const selectedPoint=computed(()=>layout.value.points.find(p=>p.id===props.selectedEvent)||layout.value.points.find(p=>p.topic_id===props.selected))
const active=computed(()=>layout.value.points.find(p=>p.id===hover.value)||selectedPoint.value)
const linked=computed(()=>new Set(layout.value.edges.filter(e=>e.source===active.value?.id||e.target===active.value?.id).flatMap(e=>[e.source,e.target])))
const relations=computed(()=>layout.value.edges.filter(e=>e.source===selectedPoint.value?.id||e.target===selectedPoint.value?.id))
const entry=computed(()=>props.entries?.find(e=>e.topic_id===selectedPoint.value?.topic_id&&e.route==='B'))
const topic=computed(()=>props.tree.nodes.find(n=>n.id===selectedPoint.value?.topic_id))
const matches=computed(()=>new Set(layout.value.points.filter(p=>[p.topic_label,p.label,p.title].join(' ').toLowerCase().includes(search.value.toLowerCase())).map(p=>p.id)))
function branch(c){const root=c.trunk?c.x:(c.x<740?739:924);const base=layout.value.height-85;return `M${root},${base} C${root},${base-60} ${c.x},${base-100} ${c.x},${base-165} L${c.x},65`}
function choose(p){emit('select',p);detailsOpen.value=true}
function closeDetails(restoreFocus=false){
 detailsOpen.value=false
 if(restoreFocus&&selectedPoint.value)nextTick(()=>document.getElementById('tree-'+selectedPoint.value.id)?.focus({preventScroll:true}))
}
function onOutsidePointer(event){
 if(!detailsOpen.value||detail.value?.contains(event.target)||document.querySelector('.survey-overlay'))return
 // A different node should replace the open detail without dismissing its click.
 const node=event.target instanceof Element?event.target.closest('.tree-topic-node'):null
 if(node&&shell.value?.contains(node))return
 closeDetails()
}
function onDetailKey(event){
 // The article dialog handles its own Escape; only dismiss the top open surface.
 if(event.key!=='Escape'||!detailsOpen.value||document.querySelector('.survey-overlay'))return
 closeDetails(true)
}
onMounted(()=>{document.addEventListener('pointerdown',onOutsidePointer,true);document.addEventListener('keydown',onDetailKey)})
onBeforeUnmount(()=>{document.removeEventListener('pointerdown',onOutsidePointer,true);document.removeEventListener('keydown',onDetailKey)})
async function openSelectedSurvey(){if(document.fullscreenElement)await document.exitFullscreen?.();emit('survey',selectedPoint.value.topic_id)}
function locate(){const p=layout.value.points.find(x=>matches.value.has(x.id));if(p){choose(p);nextTick(()=>document.getElementById('tree-'+p.id)?.scrollIntoView({block:'center',behavior:'smooth'}))}}
async function fullscreen(){if(document.fullscreenElement)await document.exitFullscreen?.();else await shell.value?.requestFullscreen?.()}
function changeZoom(n){zoom.value=Math.max(.8,Math.min(1.6,zoom.value+n))}
function clear(){search.value='';highlight.value='';zoom.value=1;detailsOpen.value=false;hover.value=''}
watch(()=>props.selectedEvent,()=>{if(props.selectedEvent)detailsOpen.value=true})
const categoryLabel=id=>props.tree.nodes.find(n=>n.id===id)?.label||id
</script>
<template><div ref="shell" class="evolution-tree">
<div class="tree-toolbar"><div class="tree-legend"><button v-for="c in layout.categories" :key="c.id" :class="{active:highlight===c.id}" :style="{'--branch-color':c.tone}" @click="highlight=highlight===c.id?'':c.id"><i></i>{{c.label}}</button></div><div class="tree-tools"><label><input v-model="search" placeholder="定位技术关键词" aria-label="定位技术关键词" @keydown.enter="locate"/><button @click="locate">定位</button></label><button @click="changeZoom(-.15)" aria-label="缩小技术树">−</button><button @click="changeZoom(.15)" aria-label="放大技术树">＋</button><button @click="clear">全树</button><button @click="fullscreen">全屏</button></div></div>
<div class="tree-reading-key"><span><i class="branch-swatch"></i>彩色枝干 · 技术分类</span><span><i class="edge-swatch"></i>节点连线 · 技术联系</span><span class="tree-time-direction">时间自下而上 ↑</span></div>
<div class="tree-canvas-area"><div ref="scroller" class="tree-scroll"><svg class="evolution-tree-svg" :viewBox="`0 0 ${layout.width} ${layout.height}`" :style="{width:zoom*100+'%',minWidth:zoom*1060+'px'}" role="img" aria-label="人工智能全景技术演进树，时间从下向上，基础模型与算力位于主干">
<defs><linearGradient id="tree-paper" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fffcf8"/><stop offset="1" stop-color="#fff"/></linearGradient></defs>
<rect :width="layout.width" :height="layout.height" fill="url(#tree-paper)"/>
<g v-for="b in layout.bands" :key="b.year"><line x1="78" :x2="layout.width-14" :y1="b.y-9" :y2="b.y-9" stroke="#e3dce1" stroke-dasharray="3 7"/><text x="14" :y="b.y+22" fill="#857686" font-size="16" font-weight="700">{{b.year===2016?'≤ 2016':b.year}}</text></g>
<g class="tree-branches"><path v-for="c in layout.categories" :key="c.id" :d="branch(c)" fill="none" :stroke="c.tone" :stroke-width="c.trunk?22:9" :opacity="highlight?(highlight===c.id?.34:.045):(c.trunk?.19:.12)" stroke-linecap="round"/><g v-for="c in layout.categories" :key="'heading-'+c.id"><rect :x="c.x-84" y="16" width="168" height="56" rx="9" :fill="c.tone" :opacity="c.trunk?.15:.08"/><text v-for="(line,i) in labelLines(c.label,10)" :key="i" :x="c.x" :y="39+i*20" text-anchor="middle" :fill="c.tone" font-size="15" font-weight="750">{{line}}</text></g></g>
<g class="tree-evidence-edges"><path v-for="e in layout.edges" :key="e.id" :d="relationCurve(e)" fill="none" :stroke="e.from.tone" :stroke-width="hover&&(e.source===hover||e.target===hover)?3:1.6" :stroke-dasharray="e.kind==='shared_work'?'3 5':null" :opacity="hover?(e.source===hover||e.target===hover?.92:.035):.42"><title>{{e.from.topic_label}} → {{e.to.topic_label}}：{{e.label}}</title></path></g>
<g v-for="p in layout.points" :key="p.id" :id="'tree-'+p.id" class="tree-topic-node" :class="{selected:selectedPoint?.id===p.id,related:hover&&linked.has(p.id)}" :opacity="(highlight&&highlight!==p.category_id)||(search&&!matches.has(p.id))?.26:1" tabindex="0" role="button" :aria-expanded="detailsOpen&&selectedPoint?.id===p.id" :aria-label="`${p.year} ${p.topic_label} ${p.label}`" @mouseenter="hover=p.id" @mouseleave="hover=''" @click="choose(p)" @keydown.enter="choose(p)" @keydown.space.prevent="choose(p)">
<rect :x="p.x-p.w/2" :y="p.y-p.h/2" :width="p.w" :height="p.h" rx="9" fill="white" :stroke="p.tone" :stroke-width="selectedPoint?.id===p.id?2.6:1.1"/><rect :x="p.x-p.w/2" :y="p.y-p.h/2" :width="p.w" :height="p.h" rx="9" :fill="p.tone" :opacity="selectedPoint?.id===p.id?.15:.065"/><rect :x="p.x-p.w/2" :y="p.y-15" width="3" height="30" rx="2" :fill="p.tone"/>
<text v-for="(line,i) in p.lines.slice(0,2)" :key="i" :x="p.x" :y="p.y-(p.lines.length>1?12:4)+i*16" text-anchor="middle" font-size="13.5" font-weight="700" fill="#354353">{{line}}{{i===1&&p.lines.length>2?'…':''}}</text><text :x="p.x" :y="p.y+23" text-anchor="middle" font-size="11" :fill="p.tone">{{p.year}} · {{shortWorkLabel(p.label)}}</text><title>{{p.topic_label}}\n{{p.year}} · {{p.title}}</title></g>
<g class="tree-root"><path :d="`M710,${layout.height-38} Q715,${layout.height-85} 739,${layout.height-85} M880,${layout.height-38} Q900,${layout.height-85} 924,${layout.height-85}`" fill="none" stroke="#b3a18d" stroke-width="17" stroke-linecap="round"/><rect x="503" :y="layout.height-53" width="495" height="46" rx="23" fill="#f4efe8" stroke="#e7dbd2"/><text x="750" :y="layout.height-24" text-anchor="middle" font-size="18" font-weight="700" fill="#84695e">基础模型与架构　·　AI 算力与运行优化</text></g>
</svg></div>
<aside v-if="detailsOpen&&selectedPoint" ref="detail" class="tree-node-detail" :style="{'--branch-color':selectedPoint.tone}" aria-label="技术节点详情"><div class="tree-detail-top"><span>{{categoryLabel(selectedPoint.category_id)}}</span><button aria-label="收起节点详情" @click="closeDetails(true)">×</button></div><p class="tree-detail-year">{{selectedPoint.year}}<small>{{topic?.level2}}</small></p><h3>{{selectedPoint.topic_label}}</h3><p class="tree-definition">{{topic?.source?.cells?.C}}</p><button class="tree-survey-open" :disabled="!entry?.ready_for_dashboard" @click="openSelectedSurvey"><span>{{entry?.ready_for_dashboard?'阅读技术综述':'综述整理中'}}</span><small v-if="entry?.ready_for_dashboard">{{entry.actual_references}} 篇引用文献 ↗</small></button><a class="tree-source-paper" :href="safeUrl(selectedPoint.url)" target="_blank" rel="noopener"><span>代表成果 ↗</span><b>{{selectedPoint.title}}</b></a><p v-if="selectedPoint.authors?.length" class="tree-people">{{selectedPoint.authors.join(' · ')}}</p><p v-if="selectedPoint.institutions?.length" class="tree-people">{{selectedPoint.institutions.join(' · ')}}</p><div v-if="relations.length" class="tree-relation-list"><h4>相关技术联系</h4><a v-for="e in relations" :key="e.id" :href="safeUrl(e.source_url)" target="_blank" rel="noopener"><b>{{e.from.topic_label}} · {{e.to.topic_label}}</b><span>{{e.label}} ↗</span></a></div></aside></div>
</div></template>
