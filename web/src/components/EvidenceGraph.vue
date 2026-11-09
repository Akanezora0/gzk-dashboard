<script setup>
/*
 * 交互证据图（SVG + d3-force）
 * 连线：起点色 → 终点色渐变，叠加沿关系方向流动的光点；技术主题按所属大类着色。
 * 交互：拖动节点、滚轮缩放、拖动空白处平移、悬停聚焦相邻关系、点击节点或连线查看依据。
 */
import {ref,shallowRef,computed,watch,onMounted,onBeforeUnmount,nextTick} from 'vue'
import {forceSimulation,forceLink,forceManyBody,forceX,forceY,forceCollide} from 'd3-force'
import {treeColors} from '../technologyTreeLayout'
const props=defineProps({graph:Object,allLabels:Boolean,height:{type:Number,default:540},typeLabels:Object,selectedId:String})
const emit=defineEmits(['select'])

const typeColor={fund:'#a21535',paper:'#2c64a0',patent:'#23806e',technology:'#6f4a94',institution:'#b2772a',company:'#b2772a'}
const normType=t=>['tech','tech_point','technology'].includes(t)?'technology':t
const isTech=n=>normType(n.type)==='technology'
const colorOf=n=>isTech(n)?(treeColors[String(n.id).slice(0,3)]||typeColor.technology):(typeColor[n.type]||'#64748b')
const short=(t,n)=>t.length>n?t.slice(0,n-1)+'…':t
const textW=t=>[...t].reduce((w,c)=>w+(/[\u0000-\u00ff]/.test(c)?7.4:12.8),0)

const box=ref(null),W=ref(900)
const nodes=shallowRef([]),links=shallowRef([]),tick=ref(0)
const view=ref({k:1,x:0,y:0})
const hover=ref(null),tip=ref(null)
let sim=null,ro=null
const buildId=ref(0)
const uid=Math.random().toString(36).slice(2,8)

const deg=computed(()=>{const d=new Map();links.value.forEach(l=>{d.set(l.source.id,(d.get(l.source.id)||0)+1);d.set(l.target.id,(d.get(l.target.id)||0)+1)});return d})
const rOf=n=>isTech(n)?9+Math.min(9,(deg.value.get(n.id)||1)*2.2):normType(n.type)==='fund'?7:5.5

function build(){
 sim?.stop()
 const g=props.graph
 if(!g?.nodes?.length){nodes.value=[];links.value=[];return}
 const ns=g.nodes.map(n=>({...n,raw:n})),byId=new Map(ns.map(n=>[n.id,n]))
 const ls=(g.edges||[]).filter(e=>byId.has(e.source)&&byId.has(e.target)).map(e=>({...e,raw:e,source:byId.get(e.source),target:byId.get(e.target)}))
 const d=new Map();ls.forEach(l=>{d.set(l.source.id,(d.get(l.source.id)||0)+1);d.set(l.target.id,(d.get(l.target.id)||0)+1)})
 const r=n=>isTech(n)?9+Math.min(9,(d.get(n.id)||1)*2.2):normType(n.type)==='fund'?7:5.5
 const w=W.value,h=props.height
 sim=forceSimulation(ns)
  .force('link',forceLink(ls).id(n=>n.id).distance(l=>isTech(l.source)||isTech(l.target)?64:52).strength(.9))
  .force('charge',forceManyBody().strength(n=>isTech(n)?-260:-120))
  .force('x',forceX(w/2).strength(w<640?.16:.07)).force('y',forceY(h/2).strength(w<640?.03:.09))
  .force('collide',forceCollide(n=>r(n)+(isTech(n)?40:12)).iterations(3))
  .stop()
 for(let i=0;i<360;i++)sim.tick()
 sim.on('tick',()=>tick.value++)
 ns.forEach((n,i)=>{n.delay=(isTech(n)?.1:.35)+i*.012})
 // 连线在两端节点都弹出后再画出
 ls.forEach(l=>{l.delay=Math.max(l.source.delay,l.target.delay)+.45})
 nodes.value=ns;links.value=ls;buildId.value++
 fit()
}
function fit(){
 const ns=nodes.value;if(!ns.length)return
 const xs=ns.map(n=>n.x),ys=ns.map(n=>n.y)
 const x0=Math.min(...xs)-70,x1=Math.max(...xs)+70,y0=Math.min(...ys)-40,y1=Math.max(...ys)+60
 const k=Math.min(1.6,W.value/(x1-x0),(props.height-40)/(y1-y0))
 view.value={k,x:(W.value-(x1-x0)*k)/2-x0*k,y:20+((props.height-40)-(y1-y0)*k)/2-y0*k}
}
defineExpose({reset:fit})

/* 连线几何：在节点边缘处截断，带弧度 */
function geom(l){
 tick.value
 const s=l.source,t=l.target,dx=t.x-s.x,dy=t.y-s.y,d=Math.hypot(dx,dy)||1,rs=rOf(s)+2,rt=rOf(t)+6
 const sx=s.x+dx/d*rs,sy=s.y+dy/d*rs,tx=t.x-dx/d*rt,ty=t.y-dy/d*rt
 const mx=(sx+tx)/2-dy*.16,my=(sy+ty)/2+dx*.16
 return {p:`M${sx},${sy} Q${mx},${my} ${tx},${ty}`,sx,sy,tx,ty,ang:Math.atan2(ty-my,tx-mx)*180/Math.PI}
}
const edgeList=computed(()=>{tick.value;return links.value.map((l,i)=>({l,i,g:geom(l),cs:colorOf(l.source),ct:colorOf(l.target),fund:l.kind==='source_project_id'}))})

/* 悬停聚焦 */
const adj=computed(()=>{const m=new Map();links.value.forEach(l=>{(m.get(l.source.id)||m.set(l.source.id,new Set()).get(l.source.id)).add(l.target.id);(m.get(l.target.id)||m.set(l.target.id,new Set()).get(l.target.id)).add(l.source.id)});return m})
const focusId=computed(()=>hover.value||props.selectedId||null)
const nodeDim=n=>focusId.value&&n.id!==focusId.value&&!adj.value.get(focusId.value)?.has(n.id)
const edgeDim=l=>focusId.value&&l.source.id!==focusId.value&&l.target.id!==focusId.value
const showLabel=n=>isTech(n)||props.allLabels||hover.value===n.id||props.selectedId===n.id

/* 交互：平移、缩放、拖动节点 */
let drag=null
function toWorld(e){const r=box.value.getBoundingClientRect(),v=view.value;return [(e.clientX-r.left-v.x)/v.k,(e.clientY-r.top-v.y)/v.k]}
function onWheel(e){
 e.preventDefault()
 const r=box.value.getBoundingClientRect(),px=e.clientX-r.left,py=e.clientY-r.top,v=view.value
 const k=Math.max(.4,Math.min(3,v.k*Math.exp(-e.deltaY*.0015)))
 view.value={k,x:px-(px-v.x)*k/v.k,y:py-(py-v.y)*k/v.k}
}
function downBg(e){drag={mode:'pan',sx:e.clientX,sy:e.clientY,v:{...view.value},moved:false};box.value.setPointerCapture(e.pointerId)}
function downNode(e,n){
 e.stopPropagation();drag={mode:'node',n,moved:false};box.value.setPointerCapture(e.pointerId)
 n.fx=n.x;n.fy=n.y;sim.alphaTarget(.25).restart()
}
function move(e){
 if(!drag)return
 if(drag.mode==='pan'){const dx=e.clientX-drag.sx,dy=e.clientY-drag.sy;if(Math.abs(dx)+Math.abs(dy)>3)drag.moved=true;view.value={...drag.v,x:drag.v.x+dx,y:drag.v.y+dy}}
 else{const [x,y]=toWorld(e);if(Math.hypot(x-drag.n.x,y-drag.n.y)>2)drag.moved=true;drag.n.fx=x;drag.n.fy=y}
}
function up(){
 if(!drag)return
 if(drag.mode==='node'){sim.alphaTarget(0);drag.n.fx=null;drag.n.fy=null;if(!drag.moved)emit('select',{kind:'node',item:drag.n.raw})}
 else if(!drag.moved)emit('select',null)
 drag=null
}
function enterNode(e,n){hover.value=n.id;showTip(e,`<span style="color:${colorOf(n)}">${props.typeLabels?.[n.type]||n.type}${n.year?' · '+n.year:''}</span><b>${esc(n.label)}</b>`)}
function enterEdge(e,l){showTip(e,`<span style="color:${colorOf(l.target)}">${esc(l.source.label.length>18?l.source.label.slice(0,17)+'…':l.source.label)} →</span><b>${esc(l.label||'关系')}</b>`)}
function showTip(e,html){const r=box.value.getBoundingClientRect();tip.value={x:e.clientX-r.left,y:e.clientY-r.top,html}}
function leave(){hover.value=null;tip.value=null}
const esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c])

watch(()=>props.graph,()=>nextTick(build))
onMounted(()=>{
 W.value=box.value.clientWidth||900
 ro=new ResizeObserver(([e])=>{const w=Math.round(e.contentRect.width);if(w&&Math.abs(w-W.value)>8){W.value=w;fit()}});ro.observe(box.value)
 build()
})
onBeforeUnmount(()=>{sim?.stop();ro?.disconnect()})
</script>

<template>
<div ref="box" class="egraph" :style="{height:height+'px'}" @wheel="onWheel" @pointerdown="downBg" @pointermove="move" @pointerup="up" @pointercancel="up" @pointerleave="tip=null">
 <svg :width="W" :height="height" role="img" aria-label="交互证据图">
  <defs>
   <filter :id="'sh'+uid" x="-60%" y="-60%" width="220%" height="220%"><feDropShadow dx="0" dy="1.5" stdDeviation="2.2" flood-color="#3c1c26" flood-opacity=".18"/></filter>
   <linearGradient v-for="e in edgeList" :id="'eg'+uid+e.i" :key="'g'+e.i" gradientUnits="userSpaceOnUse" :x1="e.g.sx" :y1="e.g.sy" :x2="e.g.tx" :y2="e.g.ty"><stop offset="0" :stop-color="e.fund?'#a21535':e.cs"/><stop offset="1" :stop-color="e.ct"/></linearGradient>
  </defs>
  <g :transform="`translate(${view.x},${view.y}) scale(${view.k})`">
   <g class="eg-edges">
    <g v-for="e in edgeList" :key="buildId+'e'+e.i" :style="{'--d':e.l.delay+'s'}" class="eg-edge" :class="{dim:edgeDim(e.l),on:!!focusId&&!edgeDim(e.l)}" @pointerenter="enterEdge($event,e.l)" @pointerleave="leave" @pointerdown.stop @click.stop="emit('select',{kind:'edge',item:e.l.raw})">
     <path class="eg-hit" :d="e.g.p"/>
     <path class="eg-line" :d="e.g.p" pathLength="1" :stroke="`url(#eg${uid}${e.i})`"/>
     <g class="eg-flow-wrap"><path class="eg-flow" :d="e.g.p" :stroke="e.ct" :style="{animationDelay:(-(e.i%9)*.18)+'s'}"/></g>
     <path class="eg-arrow" d="M0,0 L-8,-4 L-6,0 L-8,4Z" :fill="e.ct" :transform="`translate(${e.g.tx},${e.g.ty}) rotate(${e.g.ang})`"/>
    </g>
   </g>
   <g class="eg-nodes">
    <g v-for="n in nodes" :key="buildId+n.id" class="eg-node" :class="{dim:nodeDim(n),sel:selectedId===n.id,tech:isTech(n)}" :transform="`translate(${n.x},${n.y})`" @pointerdown="downNode($event,n)" @pointerenter="enterNode($event,n)" @pointerleave="leave">
     <g class="eg-pop" :style="{animationDelay:n.delay+'s'}">
      <circle v-if="isTech(n)" class="eg-ring" :r="rOf(n)+4" :stroke="colorOf(n)"/>
      <circle v-if="selectedId===n.id" :r="rOf(n)+7" fill="none" :stroke="colorOf(n)" stroke-width="2"/>
      <circle class="eg-dot" :r="rOf(n)" :fill="colorOf(n)" :filter="`url(#sh${uid})`"/>
      <circle v-if="isTech(n)" :r="rOf(n)*.36" fill="#fff" opacity=".88"/>
      <template v-if="showLabel(n)">
       <template v-if="isTech(n)">
        <rect :x="-(textW(short(n.label,12))/2+9)" :y="rOf(n)+6" :width="textW(short(n.label,12))+18" height="20" rx="10" fill="#fff" :stroke="colorOf(n)" stroke-opacity=".35" :filter="`url(#sh${uid})`"/>
        <text class="eg-label tech" :y="rOf(n)+20" :fill="colorOf(n)">{{short(n.label,12)}}</text>
       </template>
       <text v-else class="eg-label" :y="rOf(n)+15">{{short(n.label,hover===n.id?26:16)}}</text>
      </template>
     </g>
    </g>
   </g>
  </g>
 </svg>
 <div v-if="tip" class="eg-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div>
</div>
</template>

<style scoped>
.egraph{position:relative;overflow:hidden;cursor:grab;touch-action:none;user-select:none}
.egraph:active{cursor:grabbing}
svg{display:block}
.eg-hit{fill:none;stroke:transparent;stroke-width:12;cursor:pointer}
.eg-line{fill:none;stroke-width:2.4;stroke-opacity:.5;stroke-dasharray:1;stroke-dashoffset:1;animation:egdraw .7s cubic-bezier(.4,0,.2,1) var(--d,0s) forwards;transition:stroke-opacity .2s,stroke-width .2s}
.eg-flow-wrap{opacity:0;animation:egfade .4s ease-out calc(var(--d,0s) + .6s) forwards}
.eg-flow{fill:none;stroke-width:2.6;stroke-linecap:round;stroke-dasharray:2 32;stroke-opacity:.9;animation:egflow 1.6s linear infinite;pointer-events:none}
.eg-arrow{opacity:0;pointer-events:none;animation:egarrow .3s ease-out calc(var(--d,0s) + .55s) forwards}
.eg-edge{transition:opacity .2s}
.eg-edge.dim{opacity:.1}
.eg-edge.on .eg-line,.eg-edge:hover .eg-line{stroke-opacity:.9;stroke-width:3.2}
.eg-node{cursor:pointer;transition:opacity .2s}
.eg-node.dim{opacity:.18}
.eg-ring{fill:none;stroke-width:1.5;stroke-opacity:.26}
.eg-dot{stroke:#fff;stroke-width:2.2;transition:transform .2s}
.eg-node:hover .eg-dot{transform:scale(1.18)}
.eg-pop{transform-box:fill-box;transform-origin:center;animation:egpop .6s cubic-bezier(.3,1.5,.5,1) both}
.eg-label{font-size:11.5px;fill:#4a4448;text-anchor:middle;paint-order:stroke;stroke:#fdfcfb;stroke-width:3.5px;stroke-linejoin:round;pointer-events:none}
.eg-label.tech{font-size:12.5px;font-weight:650;stroke:none}
.eg-tip{position:absolute;z-index:3;transform:translate(14px,14px);max-width:300px;padding:8px 12px;border:1px solid #e4dcd8;border-radius:4px;background:#fff;box-shadow:0 10px 28px -14px rgba(60,28,38,.35);font-size:12px;line-height:1.5;pointer-events:none}
.eg-tip :deep(span){display:block}
.eg-tip :deep(b){display:block;font-size:13px;color:#2f2b2d;font-weight:650}
@keyframes egflow{to{stroke-dashoffset:-34}}
@keyframes egdraw{to{stroke-dashoffset:0}}
@keyframes egfade{to{opacity:1}}
@keyframes egarrow{to{opacity:.8}}
@keyframes egpop{from{transform:scale(0);opacity:0}to{transform:scale(1);opacity:1}}
@media(prefers-reduced-motion:reduce){.eg-flow{animation:none;display:none}.eg-pop{animation:none}.eg-line{animation:none;stroke-dasharray:none;stroke-dashoffset:0}.eg-arrow{animation:none;opacity:.8}}
</style>
