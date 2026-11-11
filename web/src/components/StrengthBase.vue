<script setup>
/* 01 聚焦机构成长与人员培育：基金项目 → 人员 → 机构，标注全库与人工智能领域；论文、专利两环见“关联与依据” */
import {computed,ref} from 'vue'
import {useTip,fmt} from '../helpers/strengthTip.js'
import {useMemberGrowth} from '../helpers/memberGrowth.js'
const props=defineProps({dataset:Object,inventory:Object})
const {tip,show,move,hide}=useTip()
const active=ref('')
const {data:growth}=useMemberGrowth()
const S=computed(()=>props.dataset?.strength||{})
const C=computed(()=>props.inventory?.counts||{})
const metric=label=>(S.value.metrics||[]).find(m=>m.label===label)?.value
const wan=n=>n==null?'—':n>=1e8?(n/1e8).toFixed(2).replace(/0$/,'')+' 亿':n>=1e7?Math.round(n/1e4).toLocaleString('en-US')+' 万':(n/1e4).toFixed(1)+' 万'
const Y=170
const tones={org:'#6b5a52',per:'#8c6a3a',fund:'#a21535',pap:'#2c64a0',pat:'#23806e'}
const nodes=computed(()=>[
 {k:'fund',n:'基金项目',x:250,r:80,all:C.value.fund_identities?wan(C.value.fund_identities)+'项':'',ai:`${fmt(metric('AI基金项目'))} 项`,aiN:'AI 基金项目',hub:true},
 {k:'per',n:'人员',x:680,r:58,ai:`${fmt((props.dataset?.continuity||[]).length)} 位进阶`,aiN:growth.value?`负责人进阶 · 另有 ${fmt(growth.value.cases.length)} 位参与人成长`:'负责人前后项目进阶'},
 {k:'org',n:'机构',x:1110,r:58,ai:`${fmt(S.value.scope?.institutions)} 家`,aiN:`${S.value.scope?.years?.[0]||2017}—${S.value.scope?.years?.[1]||2021} 年承担 AI 项目`}])
const links=computed(()=>{const N=nodes.value;return [
 {id:'fp',a:0,b:1,n:metric('基金—人员来源记录'),u:'条',name:'基金—人员',how:'NSFC 官方负责人与成员记录'},
 {id:'po',a:1,b:2,n:metric('人员—机构观察'),u:'条',name:'人员—机构',how:'人员署名单位的来源观察'},
].map(l=>{const A=N[l.a],B=N[l.b],dir=B.x>A.x?1:-1,x0=A.x+dir*(A.r+3),x1=B.x-dir*(B.r+4),xe=x1-dir*16;return {...l,dir,x0,x1,xe,mx:(x0+x1)/2,ca:tones[A.k],cb:tones[B.k]}})})
const cite=computed(()=>metric('论文引用关系'))
const pillW=t=>[...String(t)].reduce((w,c)=>w+(/[\x00-\xff]/.test(c)?10.5:18),0)+40
function linkTip(e,l){active.value=l.id;show(e,`<b>${l.name}</b>　${fmt(l.n)} ${l.u}<br>建立方式：${l.how}${l.ai?`<br>其中 AI 项目登记成果 ${fmt(l.ai)} 条`:''}`)}
function off(){active.value='';hide()}
</script>
<template>
  <section class="rs-page">
    <header class="rs-head"><span class="rs-no">01</span><h3>聚焦机构成长与人员培育</h3></header>
    <p class="rs-lead soft">创新链从基金项目出发，落到承担项目的人员与机构：基金项目培养负责人与参与人，人员在依托单位中积累并带动机构成长。</p>
    <div v-if="!S.metrics" class="rs-empty">关系指标尚未生成，请在服务器运行 build_ai_chain.py 更新研究团队数据。</div>
    <template v-else>
    <div class="sb-legend"><span><i class="all"></i>全库</span><span><i class="ai"></i>人工智能领域 · 本页研究对象</span></div>
    <div class="rs-scroll"><svg class="rs-svg sb-svg" viewBox="0 0 1360 380" role="img" aria-label="基金项目、人员、机构之间的关联关系，全库与人工智能领域">
      <defs><linearGradient v-for="l in links" :key="'g'+l.id" :id="'sbg'+l.id" gradientUnits="userSpaceOnUse" :x1="l.x0" :x2="l.x1" y1="0" y2="0"><stop offset="0" :stop-color="l.ca" stop-opacity=".6"/><stop offset="1" :stop-color="l.cb" stop-opacity=".85"/></linearGradient></defs>
      <g v-for="l in links" :key="l.id" class="rs-hit" :opacity="active&&active!==l.id?.4:1" @mouseenter="linkTip($event,l)" @mousemove="move" @mouseleave="off">
        <rect :x="Math.min(l.x0,l.x1)" :y="Y-26" :width="Math.abs(l.x1-l.x0)" height="52" fill="transparent"/>
        <path :d="`M${l.x0},${Y-7} L${l.xe},${Y-7} L${l.xe},${Y-12} L${l.x1},${Y} L${l.xe},${Y+12} L${l.xe},${Y+7} L${l.x0},${Y+7} Z`" :fill="`url(#sbg${l.id})`" stroke-linejoin="round"/>
        <line class="rs-flow sb-flow" :x1="l.x0+l.dir*10" :x2="l.xe-l.dir*6" :y1="Y" :y2="Y" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 22"/>
        <text :x="l.mx" :y="Y-40" font-size="25" font-weight="750" text-anchor="middle" fill="#2a2a2a">{{fmt(l.n)}}</text>
        <text :x="l.mx" :y="Y-19" font-size="13" text-anchor="middle" fill="#78716c">{{l.u}} · {{l.name}}</text>
        <g v-if="l.ai"><rect :x="l.mx-pillW(`AI ${fmt(l.ai)} 条`)/2" :y="Y+20" :width="pillW(`AI ${fmt(l.ai)} 条`)" height="34" rx="17" fill="#a21535"/>
          <text :x="l.mx" :y="Y+43" font-size="17" font-weight="800" text-anchor="middle" fill="#fff">AI {{fmt(l.ai)}} 条</text>
          <text :x="l.mx" :y="Y+72" font-size="12.5" text-anchor="middle" fill="#8a8286">AI 项目登记成果</text></g>
      </g>
      <circle class="rs-pulse sb-pulse" :cx="nodes[0].x" :cy="Y" r="84" fill="none" stroke="#a21535" stroke-width="2" pointer-events="none"/>
      <g v-for="n in nodes" :key="n.k">
        <circle v-if="n.hub" :cx="n.x" :cy="Y" :r="n.r+14" fill="#a21535" opacity=".07"/>
        <circle :cx="n.x" :cy="Y" :r="n.r" :fill="n.hub?'#a21535':'#fff'" :stroke="n.hub?'none':tones[n.k]" stroke-width="2.5"/>
        <text :x="n.x" :y="n.all?Y-2:Y+8" :font-size="n.hub?25:21" font-weight="750" text-anchor="middle" :fill="n.hub?'#fff':'#2a2a2a'">{{n.n}}</text>
        <text v-if="n.all" :x="n.x" :y="Y+22" font-size="13" text-anchor="middle" :fill="n.hub?'#ffd9e0':'#78716c'">全库 {{n.all}}</text>
        <g v-if="n.ai"><rect :x="n.x-pillW('AI '+n.ai)/2" :y="Y+n.r+16" :width="pillW('AI '+n.ai)" height="36" rx="18" :fill="n.hub?'#7e0f28':'#fbeef1'" stroke="#a21535" :stroke-opacity="n.hub?0:.5" stroke-width="1.5"/>
          <text :x="n.x" :y="Y+n.r+41" font-size="18" font-weight="800" text-anchor="middle" :fill="n.hub?'#fff':'#a21535'">AI {{n.ai}}</text>
          <text :x="n.x" :y="Y+n.r+72" font-size="12.5" text-anchor="middle" fill="#8a8286">{{n.aiN}}</text></g>
      </g>
    </svg></div>
    </template>
    <div v-if="tip.show" class="rs-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div>
  </section>
</template>
<style scoped>
.sb-legend{display:flex;gap:24px;margin:-4px 0 6px;font-size:13.5px;color:var(--rs-muted)}
.sb-legend i{display:inline-block;width:22px;height:13px;margin-right:8px;vertical-align:-2px;border-radius:2px}
.sb-legend i.all{background:#2a2a2a}.sb-legend i.ai{background:#a21535;border-radius:7px}
.sb-flow{animation-duration:1.4s}
.sb-pulse{animation-name:sb-pulse}
@keyframes sb-pulse{0%{r:80;opacity:.35}100%{r:112;opacity:0}}
</style>
