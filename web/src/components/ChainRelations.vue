<script setup>
/* 关联与依据 · 已建立的链条关系：创新链（基金—论文—专利）与产业链（基金—产品—产业—经济社会价值）；未接入环节以虚线占位 */
import {computed} from 'vue'
import {useTip,fmt} from '../helpers/strengthTip.js'
const props=defineProps({dataset:Object,inventory:Object})
const {tip,show,move,hide}=useTip()
const C=computed(()=>props.inventory?.counts||{})
const metric=label=>(props.dataset?.strength?.metrics||[]).find(m=>m.label===label)?.value
const wan=n=>n==null?'':n>=1e8?(n/1e8).toFixed(2).replace(/0$/,'')+' 亿':n>=1e7?Math.round(n/1e4).toLocaleString('en-US')+' 万':(n/1e4).toFixed(1)+' 万'
const tones={fund:'#a21535',pap:'#2c64a0',pat:'#23806e',prod:'#b2772a',ind:'#6f4a94',eco:'#6b5a52'}
const R1=118,R2=318,XS=[250,610,970],XS2=[250,490,730,970]
const rows=computed(()=>[
 {y:R1,label:'创新链',sub:'基金 · 论文 · 专利',nodes:[
  {k:'fund',n:'基金项目',x:XS[0],all:C.value.fund_identities&&`全库 ${wan(C.value.fund_identities)}项`,ai:`AI ${fmt(metric('AI基金项目'))} 项`,hub:true},
  {k:'pap',n:'论文',x:XS[1],all:C.value.papers&&`全库 ${wan(C.value.papers)}篇`,ai:C.value.ai_papers&&`AI ${wan(C.value.ai_papers)}篇`},
  {k:'pat',n:'专利',x:XS[2],all:C.value.national_patents&&`全库 ${wan(C.value.national_patents)}件`,ai:C.value.ai_patents&&`AI ${wan(C.value.ai_patents)}件`}],
  links:[{a:0,b:1,n:metric('基金—论文关系'),u:'对 · 基金—论文',how:'成果登记与论文资助标注',ai:metric('AI基金登记成果关系')},{a:1,b:2,n:metric('已接通专利—论文关系'),u:'对 · 专利引用论文',how:'规范化匹配专利引用的论文'}]},
 {y:R2,label:'产业链',sub:'基金 · 产品 · 产业 · 经济社会价值',nodes:[
  {k:'fund',n:'基金项目',x:XS2[0],all:'经技术主题连接',ai:'80 个技术点',hub:true},
  {k:'prod',n:'产品',x:XS2[1],all:'产品与软著',ph:true},
  {k:'ind',n:'产业',x:XS2[2],all:'AI 企业名录',ai:'27,075 家'},
  {k:'eco',n:'经济社会价值',x:XS2[3],all:'营收、就业等',ph:true}],
  links:[{a:0,b:1,ph:true,u:'技术—产品'},{a:1,b:2,ph:true,u:'产品—企业'},{a:2,b:3,ph:true,u:'企业—经济指标'}]}
].map(r=>({...r,links:r.links.map(l=>{const A=r.nodes[l.a],B=r.nodes[l.b],x0=A.x+(A.hub?58:50)+4,x1=B.x-54,xe=x1-16;return {...l,x0,x1,xe,mx:(x0+x1)/2,ca:tones[A.k],cb:tones[B.k],id:A.k+B.k+r.y}})})))
const pillW=t=>[...String(t)].reduce((w,c)=>w+(/[\x00-\xff]/.test(c)?9:15.5),0)+30
function linkTip(e,l){if(l.ph)show(e,`<b>${l.u}</b><br>关系数据接入中`);else show(e,`<b>${l.u.split(' · ')[1]}</b>　${fmt(l.n)} 对<br>建立方式：${l.how}${l.ai?`<br>其中 AI 项目登记成果 ${fmt(l.ai)} 条`:''}`)}
</script>
<template>
 <section class="ev-graph chain-rel">
  <header class="ev-graph-head"><div><h3>已建立的链条关系</h3><p>领域数据经共同技术词表连接后形成的链条；红色标签为人工智能领域，虚线为数据接入中的环节</p></div></header>
  <div class="rs-scroll"><svg class="rs-svg chain-rel-svg" viewBox="0 0 1100 430" role="img" aria-label="创新链与产业链已建立的关联关系">
   <defs><linearGradient v-for="l in rows.flatMap(r=>r.links).filter(l=>!l.ph)" :key="'g'+l.id" :id="'crg'+l.id" gradientUnits="userSpaceOnUse" :x1="l.x0" :x2="l.x1" y1="0" y2="0"><stop offset="0" :stop-color="l.ca" stop-opacity=".6"/><stop offset="1" :stop-color="l.cb" stop-opacity=".85"/></linearGradient></defs>
   <g v-for="r in rows" :key="r.y">
    <text x="0" :y="r.y-4" font-size="19" font-weight="750" fill="#2a2a2a">{{r.label}}</text>
    <text x="0" :y="r.y+18" font-size="12.5" fill="#8a8286">{{r.sub}}</text>
    <g v-for="l in r.links" :key="l.id" class="rs-hit" @mouseenter="linkTip($event,l)" @mousemove="move" @mouseleave="hide">
     <rect :x="l.x0" :y="r.y-26" :width="l.x1-l.x0" height="52" fill="transparent"/>
     <template v-if="!l.ph"><path :d="`M${l.x0},${r.y-6} L${l.xe},${r.y-6} L${l.xe},${r.y-11} L${l.x1},${r.y} L${l.xe},${r.y+11} L${l.xe},${r.y+6} L${l.x0},${r.y+6} Z`" :fill="`url(#crg${l.id})`"/>
      <line class="rs-flow" :x1="l.x0+10" :x2="l.xe-6" :y1="r.y" :y2="r.y" stroke="#fff" stroke-width="4.5" stroke-linecap="round" stroke-dasharray="2 22"/>
      <text :x="l.mx" :y="r.y-36" font-size="23" font-weight="750" text-anchor="middle" fill="#2a2a2a">{{fmt(l.n)}}</text>
      <text :x="l.mx" :y="r.y-17" font-size="12.5" text-anchor="middle" fill="#78716c">{{l.u}}</text>
      <template v-if="l.ai"><rect :x="l.mx-pillW(`AI ${fmt(l.ai)} 条`)/2" :y="r.y+18" :width="pillW(`AI ${fmt(l.ai)} 条`)" height="30" rx="15" fill="#a21535"/><text :x="l.mx" :y="r.y+38" font-size="15" font-weight="800" text-anchor="middle" fill="#fff">AI {{fmt(l.ai)}} 条</text></template></template>
     <template v-else><line :x1="l.x0" :x2="l.x1-4" :y1="r.y" :y2="r.y" stroke="#cfc8c1" stroke-width="3" stroke-dasharray="7 7"/><path :d="`M${l.x1-12},${r.y-7} L${l.x1},${r.y} L${l.x1-12},${r.y+7}`" fill="none" stroke="#cfc8c1" stroke-width="3"/>
      <text :x="l.mx" :y="r.y-17" font-size="13" font-weight="650" text-anchor="middle" fill="#a8a29e">待接入</text><text :x="l.mx" :y="r.y+26" font-size="12" text-anchor="middle" fill="#a8a29e">{{l.u}}</text></template>
    </g>
    <g v-for="n in r.nodes" :key="n.k+r.y">
     <circle v-if="n.hub" :cx="n.x" :cy="r.y" r="70" fill="#a21535" opacity=".07"/>
     <circle :cx="n.x" :cy="r.y" :r="n.hub?58:50" :fill="n.hub?'#a21535':'#fff'" :stroke="n.hub?'none':n.ph?'#c9c2bb':tones[n.k]" stroke-width="2.5" :stroke-dasharray="n.ph?'6 5':null"/>
     <text :x="n.x" :y="r.y-2" :font-size="n.n.length>4?14.5:n.hub?21:19" font-weight="750" text-anchor="middle" :fill="n.hub?'#fff':n.ph?'#8a8286':'#2a2a2a'">{{n.n}}</text>
     <text :x="n.x" :y="r.y+19" font-size="12" text-anchor="middle" :fill="n.hub?'#ffd9e0':'#78716c'">{{n.all}}</text>
     <g v-if="n.ai||n.ph"><rect :x="n.x-pillW(n.ai||'待补充')/2" :y="r.y+(n.hub?70:62)" :width="pillW(n.ai||'待补充')" height="30" rx="15" :fill="n.ph?'#f3f0ed':n.hub?'#7e0f28':'#fbeef1'" :stroke="n.ph?'none':'#a21535'" :stroke-opacity="n.hub?0:.5"/>
      <text :x="n.x" :y="r.y+(n.hub?90:82)" font-size="15" font-weight="800" text-anchor="middle" :fill="n.ph?'#a8a29e':n.hub?'#fff':'#a21535'">{{n.ai||'待补充'}}</text></g>
    </g>
   </g>
  </svg></div>
  <div v-if="tip.show" class="rs-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div>
 </section>
</template>
<style scoped>
.chain-rel{margin-bottom:18px}
.chain-rel-svg{max-width:1100px;margin:0 auto}
</style>
