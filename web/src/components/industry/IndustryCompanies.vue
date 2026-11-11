<script setup>
/* 领域数据 · 企业：企业全景（行业、地区、产业角色）、企业名录与专利布局（数据：industry/v1，2026-11-11） */
import {ref,computed,watch} from 'vue'
import Chart from '../Chart.vue'
import CountValue from '../CountValue.vue'
import IndustryFilters from './IndustryFilters.vue'
import IndustryDrawer from './IndustryDrawer.vue'
import {useCompanies,countBy,barChart,roleName,roleShort,ROLES} from '../../helpers/industryData'
import {fmt} from '../../shared'
import '../../industry.css'
const emit=defineEmits(['go'])
const tone='#7563A8'
const {data,error}=useCompanies()
const all=computed(()=>data.value?.companies||[])
const filter=ref({q:'',industry:'all',province:'all',role:'all'})
const rows=computed(()=>{const f=filter.value,q=f.q.trim().toLowerCase();return all.value.filter(c=>(!q||c.name.toLowerCase().includes(q))&&(f.industry==='all'||c.industry===f.industry)&&(f.province==='all'||c.province===f.province)&&(f.role==='all'||c.roles.includes(f.role)))})
const hero=computed(()=>{const a=all.value;return {total:a.length,products:a.filter(c=>c.cov.products>0).length,patents:a.filter(c=>c.cov.patents>0).length,economy:a.filter(c=>c.econ).length,industries:countBy(a,c=>c.industry).filter(x=>x.name!=='行业未列明').length,provinces:countBy(a,c=>c.province).length}})
const strip=computed(()=>{const r=rows.value,roles=countBy(r,c=>c.roles);return [{label:'当前企业与机构',value:r.length,unit:'家'},...ROLES.map(x=>({label:roleName(x),value:roles.find(v=>v.name===x)?.count||0,unit:'家'})),{label:'注册地区',value:countBy(r,c=>c.province).length,unit:'个'}]})
const expanded=ref('')
const panels=computed(()=>[
 {key:'industry',title:'行业分布 · 前 8 位',option:barChart(countBy(rows.value,c=>c.industry),{color:tone,active:filter.value.industry==='all'?'':filter.value.industry})},
 {key:'province',title:'地区分布 · 前 10 位',option:barChart(countBy(rows.value,c=>c.province),{color:'#2c64a0',limit:10,active:filter.value.province==='all'?'':filter.value.province})}])
function pick(key,p){if(!p?.name)return;filter.value={...filter.value,[key]:filter.value[key]===p.name?'all':p.name}}
// 企业名录
const sort=ref('products'),page=ref(0),size=15
const ordered=computed(()=>[...rows.value].sort((a,b)=>sort.value==='name'?a.name.localeCompare(b.name,'zh-CN'):(b.cov[sort.value]||0)-(a.cov[sort.value]||0)||a.name.localeCompare(b.name,'zh-CN')))
const pages=computed(()=>Math.max(1,Math.ceil(ordered.value.length/size)))
const shown=computed(()=>ordered.value.slice(page.value*size,(page.value+1)*size))
watch([filter,sort],()=>page.value=0)
// 专利布局
const patentTech=ref('all')
const techOwners=computed(()=>{const d=data.value;if(!d)return [];const ids=new Set(rows.value.map(c=>c.id));return Object.entries(d.patentTech).map(([id,ix])=>({id,name:d.tech.get(id)?.name||id,count:ix.filter(i=>ids.has(d.companies[i].id)).length})).filter(x=>x.count).sort((a,b)=>b.count-a.count)})
const patentRows=computed(()=>{let r=rows.value.filter(c=>c.cov.patents>0);if(patentTech.value!=='all'){const d=data.value,set=new Set((d.patentTech[patentTech.value]||[]).map(i=>d.companies[i].id));r=r.filter(c=>set.has(c.id))}return [...r].sort((a,b)=>b.cov.patents-a.cov.patents)})
const patentPanel=computed(()=>barChart(techOwners.value,{color:'#23806e',label:'拥有相关专利的企业',active:patentTech.value==='all'?'':data.value?.tech.get(patentTech.value)?.name,limit:10}))
function pickTech(p){const id=p?.data?.id;if(id)patentTech.value=patentTech.value===id?'all':id}
const open=ref(null)
</script>
<template>
 <section class="ai-data-hero" :style="{'--hero-color':tone}">
  <div class="ai-hero-main"><span class="ai-hero-tag">领域数据 · 创新主体</span><h3 class="ai-hero-title">人工智能企业与机构</h3>
   <p class="ai-hero-desc">覆盖大模型、算力、存储与产业应用的 {{fmt(hero.total)}} 家企业与机构，按统一企业编号连接产品、专利、招聘与经济指标。</p>
   <ul class="ai-hero-bullets"><li>按国民经济行业分类 {{hero.industries}} 个门类、{{hero.provinces}} 个注册地区归集</li><li>专利按企业及关联公司归集，标注 70 个关键技术点</li></ul></div>
  <div class="ai-hero-highlights">
   <div class="ai-highlight"><strong><CountValue :value="hero.total"/><small>家</small></strong><span>企业与机构</span></div>
   <button type="button" class="ai-highlight link" @click="emit('go','product')"><strong><CountValue :value="hero.products"/><small>家</small></strong><span>关联产品的企业</span></button>
   <div class="ai-highlight"><strong><CountValue :value="hero.patents"/><small>家</small></strong><span>拥有专利的企业</span></div>
   <button type="button" class="ai-highlight link" @click="emit('go','economy')"><strong><CountValue :value="hero.economy"/><small>家</small></strong><span>有经济指标的企业</span></button>
  </div>
 </section>
 <div v-if="error" class="notice error">{{error}}</div>
 <div v-else-if="!data" class="domain-loading" role="status">正在读取企业名录…</div>
 <template v-else>
  <IndustryFilters v-model="filter" :companies="all" :caption="`${fmt(rows.length)} 家企业与机构 · 点击图表条目可筛选`"/>
  <div class="ai-kpi-strip fit" :style="{'--n':strip.length}"><article v-for="(k,i) in strip" :key="k.label" :class="{lead:i===0}"><strong><CountValue :value="k.value"/><small>{{k.unit}}</small></strong><span>{{k.label}}</span></article></div>
  <div class="charts-grid equal domain-main-charts domain-chart-grid" :class="{'has-expanded':expanded}">
   <section v-for="p in panels" :key="p.key" class="panel" :class="{'chart-expanded':expanded===p.key}">
    <div class="panel-heading"><h3>{{p.title}}</h3><div class="chart-controls"><button class="chart-expand" @click="expanded=expanded===p.key?'':p.key">{{expanded===p.key?'收起':'展开'}}</button></div></div>
    <Chart :option="p.option" :height="expanded===p.key?380:300" :label="p.title" @select="pick(p.key,$event)"/>
   </section>
  </div>
  <section class="panel records-panel ind-records">
   <div class="panel-heading"><h3>企业名录</h3><label class="ind-sort"><span>排序</span><select v-model="sort"><option value="products">按产品数量</option><option value="patents">按专利数量</option><option value="name">按企业名称</option></select></label></div>
   <div class="table-scroll"><table class="data-table record-table ind-table"><thead><tr><th>企业名称</th><th>产业角色</th><th>所属行业</th><th>注册地区</th><th class="num">产品</th><th class="num">专利</th></tr></thead><tbody>
    <tr v-for="c in shown" :key="c.id"><td><button class="ind-name" @click="open={kind:'company',id:c.id}">{{c.name}}</button></td><td class="ind-roles"><span v-for="r in c.roles" :key="r">{{roleShort(r)}}</span></td><td>{{c.industry}}</td><td class="nowrap">{{c.province}}</td><td class="num"><button v-if="c.cov.products" class="ind-num" @click="open={kind:'company',id:c.id,tab:'products'}">{{fmt(c.cov.products)}}</button><span v-else>0</span></td><td class="num"><button v-if="c.cov.patents" class="ind-num" @click="open={kind:'company',id:c.id,tab:'patents'}">{{fmt(c.cov.patents)}}</button><span v-else>0</span></td></tr>
    <tr v-if="!shown.length"><td colspan="6" class="ind-empty">暂无匹配企业</td></tr>
   </tbody></table></div>
   <div class="pagination"><span>共 {{fmt(ordered.length)}} 家企业 · 第 {{page+1}} / {{pages}} 页</span><div><button :disabled="page===0" @click="page--">上一页</button><button :disabled="page>=pages-1" @click="page++">下一页</button></div></div>
  </section>
  <div class="ind-section-head"><h3>企业专利布局</h3><p>{{fmt(patentRows.length)}} 家企业拥有{{patentTech==='all'?'':` “${data.tech.get(patentTech)?.name}” 相关`}}专利 · 企业及关联公司</p></div>
  <div class="charts-grid equal domain-main-charts domain-chart-grid">
   <section class="panel"><div class="panel-heading"><h3>专利技术点 · 拥有专利的企业数</h3><div class="chart-controls"><button v-if="patentTech!=='all'" class="chart-expand" @click="patentTech='all'">全部技术点</button></div></div>
    <Chart :option="patentPanel" :height="360" label="专利技术点分布" @select="pickTech"/></section>
   <section class="panel"><div class="panel-heading"><h3>专利布局领先企业</h3><span class="ind-unit">专利数量 · 件</span></div>
    <ol class="ind-rank"><li v-for="(c,i) in patentRows.slice(0,10)" :key="c.id"><i>{{i+1}}</i><button class="ind-name" @click="open={kind:'company',id:c.id,tab:'patents'}">{{c.name}}</button><b>{{fmt(c.cov.patents)}}</b></li><li v-if="!patentRows.length" class="ind-empty">暂无匹配企业</li></ol></section>
  </div>
 </template>
 <IndustryDrawer :open="open" @close="open=null" @open="open=$event"/>
</template>
