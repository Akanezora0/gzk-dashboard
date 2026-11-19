<script setup>
/* 长链条案例 · 政策案例：总览（三环节 × 两个案例）→ 点击进入详情；与企业案例同一交互
   内容来自耀元交付的政策案例（296 城城市面板 2013—2025 与人工智能产业政策实证分析） */
import {computed,nextTick} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import PolicyInnovation from './PolicyInnovation.vue'
import PolicyEconomy from './PolicyEconomy.vue'
const route=useRoute(),router=useRouter()
const stages=[
 {t:'政策文本采集与量化',d:'自动化批量采集目标政策，按层级、发布时间、地域与主题等维度整理政策文本，利用大语言模型进行文本量化评分，识别政策的倾向性与可靠性。'},
 {t:'因果分析建模',d:'对应政策文本解构结果，配套完成被解释变量匹配、控制变量设计与采集，系统科学性构建因果分析模型。'},
 {t:'政策效应评估',d:'结合基金布局投入、企业运营、技术专利等数据，评价政策对经济效益与技术创新的影响效应。'}]
const cases=[
 {id:'innovation',name:'政策实施与技术创新',sub:'政策文本 × 专利数据',status:'实证结果',cells:[
  {h:'1,913 篇政策 · 296 城',p:'2013—2025 年 · 累计篇数与评分'},
  {h:'双向固定效应 · CSDID',p:'3,222 个城市年度观测'},
  {h:'0.160***',p:'政策实施后关键词专利产出提升',key:true}]},
 {id:'economy',name:'政策实施与经济效益',sub:'政策文本 × 企业运营数据',status:'研究中',cells:[
  {h:'政策文本与企业匹配',p:'政策与企业运营数据'},
  {h:'经营表现因果模型',p:'收入、利润与投入'},
  {h:'经济效益评估',p:'研究中',muted:true}]}]
const current=computed(()=>cases.find(c=>c.id===route.query.case)||null)
const others=computed(()=>cases.filter(c=>c.id!==current.value?.id))
function scrollTop(){nextTick(()=>document.querySelector('.pc-root')?.scrollIntoView({behavior:'smooth',block:'start'}))}
function openCase(id){router.push({query:{...route.query,case:id}});scrollTop()}
function back(){router.push({query:{...route.query,case:undefined}});scrollTop()}
</script>

<template><div class="pc-root">
 <section v-if="!current" class="pc-wrap">
  <header class="pc-head"><h3>政策案例总览</h3><p>以人工智能和大模型领域为示范，围绕政策文本采集与量化、因果分析建模、政策效应评估组织政策长链条案例，点击案例查看详情。</p></header>
  <div class="pc-board" tabindex="0" role="region" aria-label="政策文本采集与量化、因果分析建模、政策效应评估三个环节的政策案例">
   <div class="pc-grid pc-stages"><span class="pc-label">案例</span><div v-for="(s,i) in stages" :key="s.t" class="pc-stage"><b><i>{{String(i+1).padStart(2,'0')}}</i>{{s.t}}</b><p>{{s.d}}</p></div></div>
   <button v-for="(c,i) in cases" :key="c.id" type="button" class="pc-grid pc-row" :aria-label="`查看${c.name}案例详情`" @click="openCase(c.id)">
    <span class="pc-name"><em>CASE {{String(i+1).padStart(2,'0')}}<small :class="{muted:c.status==='研究中'}">{{c.status}}</small></em><strong>{{c.name}}</strong><small>{{c.sub}}</small><i>查看详情 →</i></span>
    <span v-for="(cell,k) in c.cells" :key="k" class="pc-cell" :class="{last:k===c.cells.length-1,key:cell.key,muted:cell.muted}"><strong>{{cell.h}}</strong><small>{{cell.p}}</small></span>
   </button>
  </div>
 </section>
 <template v-else>
  <nav class="pc-bar" aria-label="案例导航"><button type="button" class="pc-back" @click="back">← 返回案例总览</button><div class="pc-switch"><span>其他案例</span><button v-for="c in others" :key="c.id" type="button" @click="openCase(c.id)">{{c.name}}</button></div></nav>
  <div :key="current.id" class="pane-swap"><PolicyInnovation v-if="current.id==='innovation'"/><PolicyEconomy v-else/></div>
  <nav class="pc-bar" aria-label="案例导航"><button type="button" class="pc-back" @click="back">← 返回案例总览</button><div class="pc-switch"><span>其他案例</span><button v-for="c in others" :key="c.id" type="button" @click="openCase(c.id)">{{c.name}}</button></div></nav>
 </template>
</div></template>

<style scoped>
.pc-root{display:flex;flex-direction:column;gap:18px;scroll-margin-top:96px}
.pc-wrap{padding:28px 30px 26px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.pc-head{margin-bottom:18px}
.pc-head h3{margin:0;font-size:21px;font-weight:750;color:#232930;padding-left:14px;border-left:4px solid #a21535;line-height:1.2}
.pc-head p{margin:10px 0 0;font-size:14.5px;color:#5d575b}
.pc-board{overflow-x:auto;padding:2px 2px 6px}
.pc-grid{display:grid;grid-template-columns:200px repeat(3,minmax(0,1fr));column-gap:40px;min-width:980px;padding:0 20px}
.pc-stages{align-items:start;margin-bottom:14px}
.pc-label{padding-top:10px;font-size:12.5px;color:#8a8286}
.pc-stage{position:relative}
.pc-stage b{display:flex;align-items:baseline;justify-content:center;gap:8px;padding:9px 0;font-size:17px;font-weight:750;color:#a21535;border-bottom:3px solid #a21535}
.pc-stage b i{font-style:normal;font-size:12px;color:#c98a98}
.pc-stage p{margin:10px 0 0;font-size:12.5px;line-height:1.75;color:#7a7378}
.pc-stage:not(:last-child)::after,.pc-cell:not(.last)::after{content:"";position:absolute;right:-33px;width:26px;height:2px;background:#c9a0ab}
.pc-stage:not(:last-child)::after{top:21px;background:#a21535}
.pc-stage:not(:last-child)::before,.pc-cell:not(.last)::before{content:"";position:absolute;right:-37px;border-left:7px solid #c9a0ab;border-top:5px solid transparent;border-bottom:5px solid transparent}
.pc-stage:not(:last-child)::before{top:17px;border-left-color:#a21535}
.pc-cell:not(.last)::after{top:50%}.pc-cell:not(.last)::before{top:50%;transform:translateY(-50%);margin-top:1px}
.pc-row{width:100%;align-items:center;margin:0 0 12px;padding-top:20px;padding-bottom:20px;min-height:116px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9;font:inherit;text-align:left;color:inherit;cursor:pointer;transition:border-color .18s,background .18s,box-shadow .18s}
.pc-row:last-child{margin-bottom:0}
.pc-row:hover{border-color:#d9b3bd;background:#fff;box-shadow:0 8px 22px rgba(120,30,50,.06)}
.pc-row:focus-visible{outline:3px solid #ac6b7a;outline-offset:3px}
.pc-name{display:flex;flex-direction:column;gap:2px;padding-right:14px;border-right:1px solid #ece5e1}
.pc-name em{display:flex;align-items:center;gap:8px;font-style:normal;font-size:11px;font-weight:700;letter-spacing:1px;color:#b9aeb1}
.pc-name em small{padding:1px 6px;border-radius:2px;background:#fbeef1;font-size:11px;letter-spacing:0;color:#a21535}
.pc-name em small.muted{background:#f2eeec;color:#7a7378}
.pc-name strong{font-size:18px;font-weight:750;color:#232930}
.pc-name>small{font-size:12.5px;color:#8a8286}
.pc-name i{margin-top:8px;font-style:normal;font-size:12.5px;font-weight:650;color:#a21535}
.pc-cell{position:relative;display:flex;flex-direction:column;gap:6px;text-align:center;min-width:0}
.pc-cell strong{font-size:15px;font-weight:700;line-height:1.55;color:#3d3a3c}
.pc-cell small{font-size:12.5px;line-height:1.65;color:#8a8286}
.pc-cell.key strong{font-size:26px;font-weight:800;color:#a21535;line-height:1.2}
.pc-cell.muted strong{color:#8a8286}
.pc-bar{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;padding:12px 18px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.pc-back{padding:8px 16px;border:1px solid #a21535;border-radius:4px;background:#fff;font:inherit;font-size:14px;font-weight:650;color:#a21535;cursor:pointer;transition:background .18s,color .18s}
.pc-back:hover{background:#a21535;color:#fff}
.pc-switch{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.pc-switch span{font-size:13px;color:#8a8286;margin-right:4px}
.pc-switch button{padding:6px 14px;border:1px solid #e6dfdb;border-radius:4px;background:#fcfaf9;font:inherit;font-size:13.5px;color:#3d3a3c;cursor:pointer}
.pc-switch button:hover{border-color:#a21535;color:#a21535}
@media(max-width:760px){.pc-wrap{padding:20px 16px}.pc-bar{padding:10px 12px}}
</style>
