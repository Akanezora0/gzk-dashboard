<script setup>
import {computed,ref} from 'vue'
import {useTip,fmt,toggleFullscreen} from '../helpers/strengthTip.js'
const props=defineProps({dataset:Object})
const {tip,show,move,hide}=useTip()
const root=ref(null),active=ref('')
const S=computed(()=>props.dataset?.strength||{})
const metric=label=>(S.value.metrics||[]).find(m=>m.label===label)?.value
const Y=230
const nodes=[{k:'机构',x:100,r:56},{k:'人员',x:400,r:56},{k:'基金项目',x:720,r:84,hl:true},{k:'论文',x:1040,r:62},{k:'专利',x:1340,r:56}]
const links=computed(()=>[
  {id:'po',a:0,b:1,n:metric('人员—机构观察'),u:'条',name:'人员—机构',how:'人员署名单位的来源观察',note:'来源观察条数，不等于独立人数'},
  {id:'fp',a:1,b:2,n:metric('基金—人员来源记录'),u:'条',name:'基金—人员',how:'NSFC 官方负责人与成员记录',note:'来源记录条数，不等于独立人数'},
  {id:'fl',a:2,b:3,n:metric('基金—论文关系'),u:'对',name:'基金—论文',how:'成果登记与论文资助标注',note:'全库关系，包含 AI 子集'},
  {id:'pp',a:3,b:4,n:metric('已接通专利—论文关系'),u:'对',name:'专利—论文',how:'规范化匹配专利引用的论文',note:'规范化匹配关系'},
].map(l=>{const A=nodes[l.a],B=nodes[l.b];const w=l.n?Math.max(4,(Math.log10(l.n)-3.6)*7):4;return {...l,x0:A.x+A.r,x1:B.x-B.r,w,mx:(A.x+A.r+B.x-B.r)/2}}))
const cite=computed(()=>metric('论文引用关系'))
const citeW=computed(()=>cite.value?(Math.log10(cite.value)-3.6)*7:4)
const funnel=computed(()=>[
  {n:metric('AI基金项目'),u:'项',t:'AI 基金项目'},
  {n:metric('AI基金登记成果关系'),u:'条',t:'AI 项目登记成果关系'},
  {n:S.value.scope?.projects,u:`项 · ${fmt(S.value.scope?.institutions)} 家`,t:`${S.value.scope?.years?.[0]||2017}—${S.value.scope?.years?.[1]||2021} 年机构分析`},
  {n:(props.dataset?.continuity||[]).length,u:'条',t:'官方身份核验的负责人接续'}])
function linkTip(e,l){active.value=l.id;show(e,`<b>${l.name}</b>　${fmt(l.n)} ${l.u}<br>建立方式：${l.how}<br><span style="color:#78716c">${l.note}</span>`)}
function off(){active.value='';hide()}
</script>
<template>
  <section class="rs-page" ref="root">
    <header class="rs-head"><span class="rs-no">01</span><h3>数据底座</h3><span class="rs-sub">线越粗，关系条数越多</span>
      <div class="rs-tools"><button class="rs-btn" @click="toggleFullscreen(root)">全屏 / 退出</button></div></header>
    <div v-if="!S.metrics" class="rs-empty">数据底座指标尚未生成，请在服务器运行 build_ai_chain.py 更新研究力量数据。</div>
    <template v-else>
    <div class="rs-scroll"><svg class="rs-svg" viewBox="0 125 1440 370" role="img" aria-label="基金、人员、机构、论文、专利之间的关联关系与条数">
      <g v-for="l in links" :key="l.id" class="rs-hit" @mouseenter="linkTip($event,l)" @mousemove="move" @mouseleave="off">
        <rect :x="l.x0" :y="Y-Math.max(l.w,26)/2" :width="l.x1-l.x0" :height="Math.max(l.w,26)" fill="transparent"/>
        <rect :x="l.x0" :y="Y-l.w/2" :width="l.x1-l.x0" :height="l.w" :fill="l.a===1||l.a===2?'#d9737f':'#bdb5ad'" :opacity="active&&active!==l.id?.35:.9"/>
        <text :x="l.mx" :y="Y-l.w/2-46" font-size="30" font-weight="700" text-anchor="middle" fill="#2a2a2a">{{fmt(l.n)}}</text>
        <text :x="l.mx" :y="Y-l.w/2-20" font-size="16" text-anchor="middle" fill="#57534e">{{l.u}} · {{l.name}}</text>
        <text :x="l.mx" :y="Y+l.w/2+32" font-size="15" text-anchor="middle" fill="#78716c">{{l.how}}</text>
      </g>
      <g class="rs-hit" @mouseenter="show($event,`<b>论文引用</b>　${fmt(cite)} 对<br>关联库中的论文引用对`)" @mousemove="move" @mouseleave="hide">
        <path :d="`M${nodes[3].x-30},${Y+nodes[3].r-6} C${nodes[3].x-125},${Y+245} ${nodes[3].x+125},${Y+245} ${nodes[3].x+30},${Y+nodes[3].r-6}`" fill="none" stroke="#bdb5ad" :stroke-width="citeW" opacity=".55" stroke-linecap="round"/>
        <text :x="nodes[3].x+100" :y="Y+170" font-size="30" font-weight="700" fill="#2a2a2a">{{fmt(cite)}}</text>
        <text :x="nodes[3].x+100" :y="Y+196" font-size="16" fill="#57534e">对 · 论文引用</text>
      </g>
      <g v-for="n in nodes" :key="n.k">
        <circle :cx="n.x" :cy="Y" :r="n.r" :fill="n.hl?'#ae0d28':'#fff'" :stroke="n.hl?'#ae0d28':'#2a2a2a'" stroke-width="2"/>
        <text :x="n.x" :y="Y+8" :font-size="n.hl?26:22" font-weight="700" text-anchor="middle" :fill="n.hl?'#fff':'#2a2a2a'">{{n.k}}</text>
      </g>
    </svg></div>
    <div class="rs-funnel">
      <span class="rs-funnel-title">AI 领域分析范围</span>
      <div class="rs-funnel-row">
        <div v-for="(f,i) in funnel" :key="i" class="rs-funnel-cell"><strong>{{fmt(f.n)}}</strong><em>{{f.u}}</em><span>{{f.t}}</span><i v-if="i<funnel.length-1">›</i></div>
      </div>
    </div>
    <div class="rs-take"><p>以基金项目为枢纽，人员、机构、论文、专利之间的每一条关系都可追溯到来源；AI 领域 2 万余个项目及其成果，是研究力量分析的数据基础。</p></div>
    <p class="rs-foot">关系条数是记录对数，不等于独立人数或论文数；全库指标包含全部学科，AI 样本是其中的子集。</p>
    </template>
    <div v-if="tip.show" class="rs-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div>
  </section>
</template>
<style scoped>
.rs-funnel{border-top:1px solid var(--rs-line);margin-top:6px;padding-top:22px}
.rs-funnel-title{font-size:17px;font-weight:700;color:var(--rs-red)}
.rs-funnel-row{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px;margin-top:10px}
.rs-funnel-cell{position:relative;padding-left:8px}
.rs-funnel-cell strong{font-size:42px;font-weight:750;color:var(--rs-red);line-height:1.2}
.rs-funnel-cell em{font-style:normal;font-size:16px;color:var(--rs-muted);margin-left:6px}
.rs-funnel-cell span{display:block;font-size:16px;color:var(--rs-ink-2);margin-top:2px}
.rs-funnel-cell i{position:absolute;right:4px;top:12px;font-style:normal;font-size:36px;color:var(--rs-faint)}
@media(max-width:900px){.rs-funnel-row{grid-template-columns:repeat(2,minmax(0,1fr))}.rs-funnel-cell strong{font-size:30px}.rs-funnel-cell i{display:none}}
</style>
