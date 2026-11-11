<script setup>
/* 领域数据 · 经济：企业经济表现，13 项标准指标，每家企业每项指标取最近年度（数据：industry/v1，2026-11-11） */
import {ref,computed,watch} from 'vue'
import Chart from '../Chart.vue'
import CountValue from '../CountValue.vue'
import IndustryFilters from './IndustryFilters.vue'
import IndustryDrawer from './IndustryDrawer.vue'
import {useCompanies,useEconomy,countBy,barChart,metricName,amount,quantile} from '../../helpers/industryData'
import {fmt} from '../../shared'
import '../../industry.css'
const tone='#B2772A'
const {data:C}=useCompanies(),{data:E,error}=useEconomy()
const filter=ref({q:'',industry:'all',province:'all',role:'all'})
const category=ref('all'),metric=ref('all')
const covered=computed(()=>C.value&&E.value?C.value.companies.filter(c=>E.value.latest.has(c.id)):[])
const rows=computed(()=>{const f=filter.value,q=f.q.trim().toLowerCase();return covered.value.filter(c=>(!q||c.name.toLowerCase().includes(q))&&(f.industry==='all'||c.industry===f.industry)&&(f.province==='all'||c.province===f.province)&&(f.role==='all'||c.roles.includes(f.role)))})
const has=(c,ids)=>{const m=E.value.latest.get(c.id);return ids.some(id=>m?.has(id))}
const idsOf=g=>E.value.metrics.filter(m=>g==='all'||m.category===g).map(m=>m.id)
const hero=computed(()=>{if(!E.value)return {total:0,metrics:13,rd:0,people:0};const a=covered.value;return {total:a.length,metrics:E.value.metrics.length,rd:a.filter(c=>has(c,idsOf('rd_investment'))).length,people:a.filter(c=>has(c,idsOf('workforce'))).length}})
const cats=computed(()=>E.value?[{id:'all',name:'经济指标全景',count:rows.value.length},...E.value.categories.map(g=>({...g,count:rows.value.filter(c=>has(c,idsOf(g.id))).length}))]:[])
const metricOptions=computed(()=>E.value?E.value.metrics.filter(m=>category.value==='all'||m.category===category.value):[])
watch(category,()=>metric.value='all')
const selected=computed(()=>metric.value==='all'?null:E.value.metricMap.get(metric.value))
const value=(c,id)=>E.value.latest.get(c.id)?.get(id)
// 当前指标覆盖的企业
const scoped=computed(()=>{if(!E.value)return [];const ids=selected.value?[selected.value.id]:idsOf(category.value);return rows.value.filter(c=>has(c,ids))})
const stats=computed(()=>{const m=selected.value;if(!m)return null;const v=scoped.value.map(c=>value(c,m.id).value);return [{label:metricName(m),value:scoped.value.length,unit:'家企业'},{label:'中位数',value:amount(quantile(v,.5),m.unit),unit:m.unit,text:true},{label:'25% 分位数',value:amount(quantile(v,.25),m.unit),unit:m.unit,text:true},{label:'75% 分位数',value:amount(quantile(v,.75),m.unit),unit:m.unit,text:true},{label:'合计',value:amount(v.reduce((s,x)=>s+x,0),m.unit),unit:m.unit,text:true}]})
const expanded=ref('')
const panels=computed(()=>{
 const m=selected.value
 if(!m)return [{key:'industry',title:'行业分布 · 有指标企业数',option:barChart(countBy(scoped.value,c=>c.industry),{color:tone,active:filter.value.industry==='all'?'':filter.value.industry})},{key:'province',title:'地区分布 · 有指标企业数',option:barChart(countBy(scoped.value,c=>c.province),{color:'#2c64a0',limit:10,active:filter.value.province==='all'?'':filter.value.province})}]
 const top=[...scoped.value].sort((a,b)=>value(b,m.id).value-value(a,m.id).value).slice(0,10).map(c=>({name:c.name,count:value(c,m.id).value,id:c.id}))
 const groups=countBy(scoped.value,c=>c.industry).slice(0,8).map(g=>({name:g.name,count:quantile(scoped.value.filter(c=>c.industry===g.name).map(c=>value(c,m.id).value),.5)})).sort((a,b)=>b.count-a.count)
 const f=v=>amount(v,m.unit)
 return [{key:'top',title:`${metricName(m)} · 前 10 位企业`,option:barChart(top,{color:tone,label:metricName(m),unit:m.unit,limit:10,format:f,axis:f}),company:true},{key:'industry',title:`${metricName(m)} · 行业中位数`,option:barChart(groups,{color:'#2c64a0',label:'中位数',unit:m.unit,format:f,axis:f,active:filter.value.industry==='all'?'':filter.value.industry})}]
})
function pick(p,key){if(!p?.name)return;if(key==='top'){open.value={kind:'company',id:p.data.id,tab:'economy'};return}filter.value={...filter.value,[key]:filter.value[key]===p.name?'all':p.name}}
const OVERVIEW=['REV','NET_PROFIT','RD_EXPENSE','ASSETS','OPERATING_CF','EMPLOYEES']
const columns=computed(()=>E.value?(selected.value?[selected.value]:category.value==='all'?OVERVIEW.map(id=>E.value.metricMap.get(id)):metricOptions.value):[])
const ordered=computed(()=>{const key=selected.value?.id||(category.value==='all'?'REV':columns.value[0]?.id);return [...scoped.value].sort((a,b)=>(value(b,key)?.value??-Infinity)-(value(a,key)?.value??-Infinity)||a.name.localeCompare(b.name,'zh-CN'))})
const page=ref(0),size=15
const pages=computed(()=>Math.max(1,Math.ceil(ordered.value.length/size)))
const shown=computed(()=>ordered.value.slice(page.value*size,(page.value+1)*size))
watch([filter,category,metric],()=>page.value=0)
const open=ref(null)
</script>
<template>
 <section class="ai-data-hero" :style="{'--hero-color':tone}">
  <div class="ai-hero-main"><span class="ai-hero-tag">领域数据 · 经济表现</span><h3 class="ai-hero-title">企业经济指标</h3>
   <p class="ai-hero-desc">{{fmt(hero.total)}} 家人工智能企业的收入、利润、资产、现金流、研发投入与人员等 {{hero.metrics}} 项标准指标，每项指标取最近年度数据。</p>
   <ul class="ai-hero-bullets"><li>来源为年报、招股书、交易所与债券市场公告等公开披露</li><li>金额为人民币亿元，人员为人；每个数值列明所属年份与披露范围</li></ul></div>
  <div class="ai-hero-highlights">
   <div class="ai-highlight"><strong><CountValue :value="hero.total"/><small>家</small></strong><span>有经济指标的企业</span></div>
   <div class="ai-highlight"><strong><CountValue :value="hero.metrics"/><small>项</small></strong><span>标准经济指标</span></div>
   <div class="ai-highlight"><strong><CountValue :value="hero.rd"/><small>家</small></strong><span>研发投入企业</span></div>
   <div class="ai-highlight"><strong><CountValue :value="hero.people"/><small>家</small></strong><span>人员数据企业</span></div>
  </div>
 </section>
 <div v-if="error" class="notice error">{{error}}</div>
 <div v-else-if="!E||!C" class="domain-loading" role="status">正在读取经济指标…</div>
 <template v-else>
  <IndustryFilters v-model="filter" :companies="covered" :caption="`${fmt(rows.length)} 家企业 · 当前指标覆盖 ${fmt(scoped.length)} 家`"/>
  <div class="ind-cats" role="group" aria-label="指标大类"><button v-for="g in cats" :key="g.id" :class="{active:category===g.id}" :aria-pressed="category===g.id" @click="category=g.id"><span>{{g.name}}</span><b>{{fmt(g.count)}}<small> 家</small></b></button></div>
  <div class="ind-metric-bar"><label class="ind-field"><span>标准指标</span><select v-model="metric"><option value="all">{{category==='all'?'全部标准指标':'该大类全部指标'}}</option><option v-for="m in metricOptions" :key="m.id" :value="m.id">{{metricName(m)}}</option></select></label><small>每项指标取最近年度，所属年份随数值列示</small></div>
  <div v-if="stats" class="ai-kpi-strip fit" :style="{'--n':stats.length}"><article v-for="(k,i) in stats" :key="k.label" :class="{lead:i===0}"><strong v-if="k.text" class="text">{{k.value}}<small>{{k.unit}}</small></strong><strong v-else><CountValue :value="k.value"/><small>{{k.unit}}</small></strong><span>{{k.label}}</span></article></div>
  <div class="charts-grid equal domain-main-charts domain-chart-grid" :class="{'has-expanded':expanded}">
   <section v-for="p in panels" :key="p.key+(selected?.id||'')" class="panel" :class="{'chart-expanded':expanded===p.key}">
    <div class="panel-heading"><h3>{{p.title}}</h3><div class="chart-controls"><button class="chart-expand" @click="expanded=expanded===p.key?'':p.key">{{expanded===p.key?'收起':'展开'}}</button></div></div>
    <Chart :option="p.option" :height="expanded===p.key?380:300" :label="p.title" @select="pick($event,p.key)"/>
   </section>
  </div>
  <section class="panel records-panel ind-records">
   <div class="panel-heading"><h3>企业经济指标</h3><span class="ind-unit">{{selected?`${metricName(selected)} · 按数值从高到低`:category==='all'?'按营业收入从高到低':'按首列指标从高到低'}}</span></div>
   <div class="table-scroll"><table class="data-table record-table ind-table"><thead><tr><th>企业名称</th><th>注册地区</th><th v-for="m in columns" :key="m.id" class="num">{{metricName(m)}}<small>{{m.unit}}</small></th></tr></thead><tbody>
    <tr v-for="c in shown" :key="c.id"><td><button class="ind-name" @click="open={kind:'company',id:c.id,tab:'economy'}">{{c.name}}</button></td><td class="nowrap">{{c.province}}</td>
     <td v-for="m in columns" :key="m.id" class="num"><template v-if="value(c,m.id)"><b :class="{neg:value(c,m.id).value<0}">{{amount(value(c,m.id).value,m.unit)}}</b><small>{{value(c,m.id).year}} 年</small></template><span v-else class="ind-dash">—</span></td></tr>
    <tr v-if="!shown.length"><td :colspan="columns.length+2" class="ind-empty">暂无匹配企业</td></tr>
   </tbody></table></div>
   <div class="pagination"><span>共 {{fmt(ordered.length)}} 家企业 · 第 {{page+1}} / {{pages}} 页</span><div><button :disabled="page===0" @click="page--">上一页</button><button :disabled="page>=pages-1" @click="page++">下一页</button></div></div>
  </section>
 </template>
 <IndustryDrawer :open="open" @close="open=null" @open="open=$event"/>
</template>
