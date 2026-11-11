<script setup>
/* 领域数据 · 招聘：大语言模型产业链企业招聘岗位（来源：《大语言模型企业招聘数据清洗流程》） */
import {computed,ref} from 'vue'
import Chart from './Chart.vue'
import CountValue from './CountValue.vue'
import {fmt,chartBase} from '../shared'
import R from '../../content/recruit.json'
const S=R.summary,Y=R.years
const tone='#B2772A',LLM='#AE0D28'
const highlights=[['岗位记录',S.raw,'条'],['去重岗位',S.dedup,'条'],['大模型岗位',S.llm_dedup,'条 · 去重'],['有效工资岗位',S.wage_valid,'条']]
const strip=[{label:'岗位发布年份',value:`${S.years[0]}—${S.years[1]}`,text:true},{label:'有招聘记录企业',value:S.firms_with_postings,unit:'家'},{label:'工商匹配',value:`${S.registry_match}%`,text:true},{label:'技能词典',value:S.skills,unit:'类'},{label:'有效工资覆盖',value:`${S.wage_cov}%`,text:true}]
const expanded=ref('')
const yrs=Y.map(r=>String(r.year))
const axis={type:'category',data:yrs,axisTick:{show:false},axisLabel:{color:'#6b7280'}}
const val=(name,fmtr)=>({type:'value',name,nameTextStyle:{color:'#8a8286',fontSize:12},splitLine:{lineStyle:{color:'#eee8e4'}},axisLabel:{color:'#8a8286',formatter:fmtr}})
const wan=v=>v>=1e4?`${v/1e4}万`:v
const demand={...chartBase,color:[tone,LLM,'#2877B0'],legend:{top:0,left:'center'},grid:{left:10,right:10,top:44,bottom:6,containLabel:true},
 tooltip:{trigger:'axis',confine:true,formatter:ps=>`${ps[0].axisValue}<br/>`+ps.map(p=>`${p.marker} ${p.seriesName} ${p.seriesIndex===2?p.value+'%':fmt(p.value)+' 条'}`).join('<br/>')},
 xAxis:axis,yAxis:[val('岗位数',wan),{...val('占比',v=>v+'%'),splitLine:{show:false}}],
 series:[{name:'去重岗位',type:'bar',barMaxWidth:26,data:Y.map(r=>r.dedup)},{name:'大模型岗位',type:'bar',barMaxWidth:26,barGap:'-100%',data:Y.map(r=>r.llm)},
  {name:'大模型岗位占比',type:'line',yAxisIndex:1,smooth:true,symbolSize:7,data:Y.map(r=>r.llm_share),label:{show:true,position:'top',fontSize:11,color:'#2877B0',formatter:p=>p.dataIndex>=Y.length-2?p.value+'%':''}}]}
const wage={...chartBase,color:[tone,'#2877B0'],legend:{top:0,left:'center'},grid:{left:10,right:10,top:44,bottom:6,containLabel:true},
 tooltip:{trigger:'axis',confine:true,formatter:ps=>`${ps[0].axisValue}<br/>`+ps.map(p=>`${p.marker} ${p.seriesName} ${p.seriesIndex?p.value+'%':fmt(p.value)+' 元'}`).join('<br/>')},
 xAxis:axis,yAxis:[val('元/月',v=>fmt(v)),{...val('本科及以上',v=>v+'%'),min:0,max:100,splitLine:{show:false}}],
 series:[{name:'月薪中位数',type:'line',smooth:true,symbolSize:7,areaStyle:{opacity:.12},data:Y.map(r=>r.wage_median)},{name:'本科及以上比例',type:'line',yAxisIndex:1,smooth:true,symbolSize:7,lineStyle:{type:'dashed'},data:Y.map(r=>r.bachelor_share)}]}
const skillView=ref('all')
const skillViews=[['all','全部技能'],['llm','大模型判定技能'],['aux','辅助画像技能']]
const skills=computed(()=>R.skills.filter(s=>skillView.value==='all'||(skillView.value==='llm')===s.llm_judge).sort((a,b)=>b.dedup-a.dedup).slice(0,12).reverse())
const skillChart=computed(()=>({...chartBase,grid:{left:10,right:70,top:10,bottom:6,containLabel:true},tooltip:{trigger:'item',confine:true,formatter:p=>{const s=skills.value[p.dataIndex];return `${s.name}<br/>去重岗位 ${fmt(s.dedup)} 条<br/>全部岗位 ${fmt(s.hits)} 条<br/>${s.llm_judge?'大模型判定技能':'辅助画像技能'}`}},
 xAxis:{type:'value',splitLine:{lineStyle:{color:'#eee8e4'}},axisLabel:{color:'#8a8286',formatter:wan}},yAxis:{type:'category',data:skills.value.map(s=>s.name),axisTick:{show:false},axisLabel:{color:'#394354'}},
 series:[{type:'bar',barMaxWidth:16,data:skills.value.map(s=>({value:s.dedup,itemStyle:{color:s.llm_judge?LLM:tone}})),label:{show:true,position:'right',fontSize:12,color:'#465367',formatter:p=>fmt(p.value)}}]}))
const panels=computed(()=>[{key:'demand',title:'去重岗位与大模型岗位 · 年度',option:demand},{key:'wage',title:'月薪中位数与本科及以上比例 · 年度',option:wage},{key:'skills',title:'技能命中 · 去重岗位',option:skillChart.value,full:true,toggle:true}])
</script>
<template>
 <section class="ai-data-hero" :style="{'--hero-color':tone}">
  <div class="ai-hero-main"><span class="ai-hero-tag">领域数据 · 劳动力需求</span><h3 class="ai-hero-title">大语言模型企业招聘</h3>
   <p class="ai-hero-desc">大语言模型产业链 {{fmt(S.firms)}} 家企业的招聘岗位，覆盖 {{S.years[0]}}—{{S.years[1]}} 年，识别薪资、学历、经验与 {{S.skills}} 类技能。</p>
   <ul class="ai-hero-bullets"><li>同一岗位 30 天内重复发布按一条计，去重后 {{fmt(S.dedup)}} 条</li><li>大模型岗位按核心模型、RAG、智能体、训练与部署等 12 类技能识别</li></ul></div>
  <div class="ai-hero-highlights"><div v-for="[l,v,h] in highlights" :key="l" class="ai-highlight"><strong><CountValue :value="v"/><small>{{h}}</small></strong><span>{{l}}</span></div></div>
 </section>
 <div class="ai-kpi-strip fit" :style="{'--n':strip.length}"><article v-for="(k,i) in strip" :key="k.label" :class="{lead:i===0}"><strong v-if="k.text" class="text">{{k.value}}</strong><strong v-else><CountValue :value="k.value"/><small>{{k.unit}}</small></strong><span>{{k.label}}</span></article></div>
 <div class="charts-grid equal domain-main-charts domain-chart-grid" :class="{'has-expanded':expanded}">
  <section v-for="p in panels" :key="p.key" class="panel" :class="{'chart-expanded':expanded===p.key,'wide-chart':p.full}">
   <div class="panel-heading"><h3>{{p.title}}</h3><div class="chart-controls">
    <div v-if="p.toggle" class="recruit-toggle" role="group" aria-label="技能范围"><button v-for="[id,l] in skillViews" :key="id" :class="{active:skillView===id}" :aria-pressed="skillView===id" @click="skillView=id">{{l}}</button></div>
    <button class="chart-expand" :aria-label="`${expanded===p.key?'收起':'展开'}${p.title}`" @click="expanded=expanded===p.key?'':p.key">{{expanded===p.key?'收起':'展开'}}</button></div></div>
   <Chart :option="p.option" :height="p.key==='skills'?(expanded==='skills'?440:380):(expanded===p.key?350:280)" :label="p.title"/>
  </section>
 </div>
</template>
<style scoped>
.recruit-toggle{display:inline-flex;gap:4px;margin-right:8px}
.recruit-toggle button{border:1px solid #e3dcd8;background:#fff;border-radius:4px;padding:4px 10px;font:inherit;font-size:12.5px;color:#5d575b;cursor:pointer}
.recruit-toggle button.active{border-color:#AE0D28;color:#AE0D28;background:#fbeef1}
@media(max-width:700px){.recruit-toggle{flex-wrap:wrap}}
</style>
