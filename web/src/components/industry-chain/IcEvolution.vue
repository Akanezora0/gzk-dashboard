<script setup>
/* 产业链分析 02 · 产品代际演进：按企业展开产品版本时间轴，同色为同一系列；点击版本查看能力、技术点与相关专利 */
import {computed} from 'vue'
import {useTip} from '../../helpers/strengthTip.js'
import {arr,clip} from '../../helpers/industryChain.js'
const props=defineProps({evolution:Object,techMap:Object})
const emit=defineEmits(['open'])
const {tip,show,move,hide}=useTip()
const tones=['#86507f','#6f68a6','#3f8a80','#c0753f','#4d679d','#a8506b','#5b8c5f','#9c8a3c']
const series=computed(()=>arr(props.evolution?.series))
const color=s=>tones[series.value.indexOf(s)%tones.length]
const yearOf=v=>{const m=String(v.releaseDate||'').match(/^(\d{4})/);return m?Number(m[1]):null}
const dateOf=v=>{const d=String(v.releaseDate||'').match(/^(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?/);if(!d)return '';if(v.datePrecision==='year'||!d[2])return d[1];if(v.datePrecision==='month'||!d[3])return `${d[1]}.${d[2]}`;return `${d[1]}.${d[2]}.${d[3]}`}
const model=computed(()=>{
 const groups=new Map()
 series.value.forEach(s=>arr(s.companyIds).forEach(cid=>{if(!groups.has(cid))groups.set(cid,{cid,series:[],items:[]});const g=groups.get(cid);g.series.push(s);arr(s.versions).forEach(v=>g.items.push({s,v}))}))
 const rows=[...groups.values()]
 const years=rows.flatMap(r=>r.items.map(x=>yearOf(x.v)).filter(Boolean)),start=Math.min(2022,...years),end=Math.max(2026,...years)
 const cols=Array.from({length:end-start+1},(_,i)=>start+i)
 rows.forEach(r=>{r.cells=cols.map(y=>r.items.filter(x=>yearOf(x.v)===y).sort((a,b)=>String(a.v.releaseDate).localeCompare(String(b.v.releaseDate))))})
 return {rows,cols,versions:rows.reduce((n,r)=>n+r.items.length,0)}
})
const name=cid=>props.evolution?.names?.[cid]||cid
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))
function tipFor(e,x){
 const cap=arr(x.v.capabilities)[0]?.text,techs=arr(x.v.technologies).map(t=>props.techMap?.get(t.technologyId)?.name||t.name).filter(Boolean)
 show(e,`<span class="ic-tip-k">${esc(name(x.s.companyIds?.[0]))} · ${esc(x.s.name)}</span><b class="ic-tip-t">${esc(x.v.label)}</b><p>${esc(dateOf(x.v))} 发布${cap?'；'+esc(clip(cap,90)):''}</p>${techs.length?`<span class="ic-tip-f">${esc(techs.slice(0,4).join(' · '))}</span>`:''}`)
}
</script>
<template>
 <section class="rs-page ic-sec">
  <header class="rs-head"><span class="rs-no">02</span><h3>产品代际演进</h3></header>
  <p class="rs-lead soft">{{model.rows.length}} 家企业的 {{series.length}} 个产品系列、{{model.versions}} 个版本，沿时间呈现模型与产品的迭代；同色为同一系列。</p>
  <div class="ic-tl-scroll"><div class="ic-tl" :style="{'--cols':model.cols.length}">
   <div class="ic-tl-head"><span>企业</span><span v-for="y in model.cols" :key="y">{{y}}</span></div>
   <div v-for="r in model.rows" :key="r.cid" class="ic-tl-row">
    <button class="ic-tl-co" @click="emit('open',{kind:'company',id:r.cid})"><b>{{name(r.cid)}}</b><small>{{r.series.length}} 个系列 · {{r.items.length}} 个版本</small></button>
    <div v-for="(cell,i) in r.cells" :key="i" class="ic-tl-cell">
     <button v-for="x in cell" :key="x.v.id" class="ic-chip" :style="{'--c':color(x.s)}" @mouseenter="tipFor($event,x)" @mousemove="move" @mouseleave="hide" @focus="tipFor($event,x)" @blur="hide" @click="hide();emit('open',{kind:'version',series:x.s.id,version:x.v.id})"><b>{{x.v.label}}</b><small>{{dateOf(x.v)}}</small></button>
    </div>
   </div>
  </div></div>
  <div class="ic-series"><span v-for="s in series" :key="s.id" :style="{'--c':color(s)}"><i></i>{{name(s.companyIds?.[0])}} · {{s.name}}</span></div>
  <Teleport to="body"><div v-if="tip.show" class="rs-tip ic-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div></Teleport>
 </section>
</template>
