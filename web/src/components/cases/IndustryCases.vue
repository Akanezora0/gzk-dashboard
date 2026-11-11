<script setup>
/* 产业链案例：六环节总览（四家企业）→ 点击进入详情；详情上下均可返回总览 */
import {computed,nextTick} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import ZhipuCase from './ZhipuCase.vue'
import IndustryCaseDetail from './IndustryCaseDetail.vue'
import {industryStages,industryCases,industryDetails,industrySources} from '../../helpers/caseIndustry'
const route=useRoute(),router=useRouter()
const current=computed(()=>industryCases.find(c=>c.id===route.query.case)||null)
const others=computed(()=>industryCases.filter(c=>c.id!==current.value?.id))
function scrollTop(){nextTick(()=>document.querySelector('.ic-root')?.scrollIntoView({behavior:'smooth',block:'start'}))}
function openCase(id){router.push({query:{...route.query,case:id}});scrollTop()}
function back(){router.push({query:{...route.query,case:undefined}});scrollTop()}
const lines=s=>String(s||'').split('\n')
</script>

<template><div class="ic-root">
 <!-- 总览：每个案例一行，沿六个环节展开 -->
 <section v-if="!current" class="ic-board-wrap">
  <header class="ic-head"><div><h3>企业案例总览</h3><p>四家企业沿基金、论文、专利承接、产品、应用与经济社会价值六个环节展开，点击案例查看详情。</p></div><span class="ic-hint">左右滑动查看完整链条 →</span></header>
  <div class="ic-board" tabindex="0" role="region" aria-label="基金、论文、专利承接、产品、应用、经济社会价值六环节案例链条">
   <div class="ic-grid ic-stages"><span class="ic-label">案例</span><b v-for="s in industryStages" :key="s">{{s}}</b></div>
   <button v-for="(c,i) in industryCases" :key="c.id" type="button" class="ic-grid ic-row" :aria-label="`查看${c.name}案例详情`" @click="openCase(c.id)">
    <span class="ic-name"><em>CASE {{String(i+1).padStart(2,'0')}}</em><strong>{{c.name}}</strong><small>{{c.product}}</small><i>查看详情 →</i></span>
    <span v-for="(cell,k) in c.cells" :key="k" class="ic-cell" :class="{last:k===c.cells.length-1}"><strong><template v-for="(l,j) in lines(cell.h)" :key="j">{{l}}<br v-if="j<lines(cell.h).length-1"/></template></strong><small><template v-for="(l,j) in lines(cell.p)" :key="j">{{l}}<br v-if="j<lines(cell.p).length-1"/></template></small></span>
   </button>
  </div>
 </section>

 <!-- 详情 -->
 <template v-else>
  <nav class="ic-bar" aria-label="案例导航">
   <button type="button" class="ic-back" @click="back">← 返回案例总览</button>
   <div class="ic-switch"><span>其他案例</span><button v-for="c in others" :key="c.id" type="button" @click="openCase(c.id)">{{c.name}}</button></div>
  </nav>
  <div :key="current.id" class="pane-swap">
   <ZhipuCase v-if="current.id==='zhipu'"/>
   <IndustryCaseDetail v-else :case-id="current.id" :detail="industryDetails[current.id]" :source="industrySources[current.id]"/>
  </div>
  <nav class="ic-bar bottom" aria-label="案例导航">
   <button type="button" class="ic-back" @click="back">← 返回案例总览</button>
   <div class="ic-switch"><span>其他案例</span><button v-for="c in others" :key="c.id" type="button" @click="openCase(c.id)">{{c.name}}</button></div>
  </nav>
 </template>
</div></template>

<style scoped>
.ic-root{display:flex;flex-direction:column;gap:18px;scroll-margin-top:96px}
.ic-board-wrap{padding:28px 30px 26px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.ic-head{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;margin-bottom:18px}
.ic-head h3{margin:0;font-size:21px;font-weight:750;color:#232930;padding-left:14px;border-left:4px solid #a21535;line-height:1.2}
.ic-head p{margin:10px 0 0;font-size:14.5px;color:#5d575b}
.ic-hint{display:none;font-size:12.5px;color:#8a8286;white-space:nowrap}
.ic-board{overflow-x:auto;padding:2px 2px 6px}
.ic-grid{display:grid;grid-template-columns:132px repeat(5,minmax(0,1fr)) minmax(0,1.2fr);column-gap:30px;min-width:1120px;padding:0 20px}
.ic-stages{align-items:center;margin-bottom:12px}
.ic-label{font-size:12.5px;color:#8a8286}
.ic-stages b{position:relative;padding:9px 0;text-align:center;font-size:17px;font-weight:750;color:#a21535;border-bottom:3px solid #a21535}
.ic-stages b:not(:last-child)::after,.ic-cell:not(.last)::after{content:"";position:absolute;top:50%;right:-25px;width:20px;height:2px;background:#c9a0ab}
.ic-stages b:not(:last-child)::before,.ic-cell:not(.last)::before{content:"";position:absolute;top:50%;right:-29px;transform:translateY(-50%);border-left:7px solid #c9a0ab;border-top:5px solid transparent;border-bottom:5px solid transparent;margin-top:1px}
.ic-stages b:not(:last-child)::after{background:#a21535}.ic-stages b:not(:last-child)::before{border-left-color:#a21535}
.ic-row{width:100%;align-items:center;margin:0 0 12px;padding-top:20px;padding-bottom:20px;min-height:124px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9;font:inherit;text-align:left;color:inherit;cursor:pointer;transition:border-color .18s,background .18s,box-shadow .18s}
.ic-row:last-child{margin-bottom:0}
.ic-row:hover{border-color:#d9b3bd;background:#fff;box-shadow:0 8px 22px rgba(120,30,50,.06)}
.ic-row:focus-visible{outline:3px solid #ac6b7a;outline-offset:3px}
.ic-name{display:flex;flex-direction:column;gap:2px;padding-right:14px;border-right:1px solid #ece5e1}
.ic-name em{font-style:normal;font-size:11px;font-weight:700;letter-spacing:1px;color:#b9aeb1}
.ic-name strong{font-size:19px;font-weight:750;color:#232930}
.ic-name small{font-size:12.5px;color:#8a8286}
.ic-name i{margin-top:8px;font-style:normal;font-size:12.5px;font-weight:650;color:#a21535}
.ic-cell{position:relative;display:flex;flex-direction:column;gap:6px;text-align:center;min-width:0}
.ic-cell strong{font-size:14.5px;font-weight:700;line-height:1.55;color:#3d3a3c;overflow-wrap:anywhere}
.ic-cell small{font-size:12.5px;line-height:1.65;color:#8a8286;overflow-wrap:anywhere}
.ic-cell.last strong{color:#a21535}
.ic-bar{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;padding:12px 18px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.ic-back{padding:8px 16px;border:1px solid #a21535;border-radius:4px;background:#fff;font:inherit;font-size:14px;font-weight:650;color:#a21535;cursor:pointer;transition:background .18s,color .18s}
.ic-back:hover{background:#a21535;color:#fff}
.ic-switch{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.ic-switch span{font-size:13px;color:#8a8286;margin-right:4px}
.ic-switch button{padding:6px 14px;border:1px solid #e6dfdb;border-radius:4px;background:#fcfaf9;font:inherit;font-size:13.5px;color:#3d3a3c;cursor:pointer}
.ic-switch button:hover{border-color:#a21535;color:#a21535}
@media(max-width:1260px){.ic-hint{display:block}}
@media(max-width:760px){.ic-board-wrap{padding:20px 16px}.ic-head{flex-direction:column;align-items:flex-start}.ic-bar{padding:10px 12px}}
</style>
