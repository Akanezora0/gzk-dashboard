<script setup>
/* 领域数据 · 产品：产品全景（技术大类、技术点）与产品目录（数据：industry/v1，2026-11-11） */
import {ref,computed,watch} from 'vue'
import Chart from '../Chart.vue'
import CountValue from '../CountValue.vue'
import IndustryDrawer from './IndustryDrawer.vue'
import {useCompanies,useProducts,countBy,barChart} from '../../helpers/industryData'
import {fmt} from '../../shared'
import '../../industry.css'
const emit=defineEmits(['go'])
const tone='#678147'
const {data:C}=useCompanies(),{data:P,error}=useProducts()
const tech=id=>C.value?.tech.get(id)
const all=computed(()=>P.value?.products||[])
const q=ref(''),category=ref('all'),techId=ref('all'),province=ref('all'),use=ref('all')
const categories=computed(()=>[...new Set((C.value?.technologies||[]).map(t=>t.level1))])
const techOptions=computed(()=>(C.value?.technologies||[]).filter(t=>category.value==='all'||t.level1===category.value))
const provinces=computed(()=>P.value?countBy(P.value.owners,o=>o.province).map(x=>x.name):[])
const uses=computed(()=>countBy(all.value,p=>p.uses))
const rows=computed(()=>{const s=q.value.trim().toLowerCase(),om=P.value?.ownerMap;return all.value.filter(p=>(!s||(p.name+' '+p.ownerNames.join(' ')+' '+p.desc).toLowerCase().includes(s))&&(use.value==='all'||p.uses.includes(use.value))&&(techId.value==='all'||p.tech.includes(techId.value))&&(category.value==='all'||p.tech.some(id=>tech(id)?.level1===category.value))&&(province.value==='all'||p.owners.some(id=>om?.get(id)?.province===province.value)))})
watch(category,()=>{if(techId.value!=='all'&&tech(techId.value)?.level1!==category.value)techId.value='all'})
const dirty=computed(()=>q.value||[category,techId,province,use].some(r=>r.value!=='all'))
function reset(){q.value='';category.value=techId.value=province.value=use.value='all'}
const hero=computed(()=>{const a=all.value;return {total:a.length,owners:new Set(a.flatMap(p=>p.owners)).size,linked:a.filter(p=>p.tech.length).length,techs:new Set(a.flatMap(p=>p.tech)).size}})
const strip=computed(()=>{const r=rows.value;return [{label:'当前产品与模型',value:r.length,unit:'项'},...uses.value.map(u=>({label:u.name.replace(/^AI/,'AI '),value:r.filter(p=>p.uses.includes(u.name)).length,unit:'项'})),{label:'关联企业与机构',value:new Set(r.flatMap(p=>p.owners)).size,unit:'家'},{label:'覆盖技术点',value:new Set(r.flatMap(p=>p.tech)).size,unit:'个'}]})
const catCounts=computed(()=>countBy(rows.value,p=>[...new Set(p.tech.map(id=>tech(id)?.level1).filter(Boolean))]))
const techCounts=computed(()=>countBy(rows.value,p=>p.tech).map(x=>({...x,id:x.name,name:tech(x.name)?.name||x.name})))
const expanded=ref('')
const panels=computed(()=>[
 {key:'category',title:'技术大类 · 关联产品数',option:barChart(catCounts.value,{color:tone,label:'产品',unit:'项',active:category.value==='all'?'':category.value})},
 {key:'tech',title:'技术点 · 产品覆盖前 10 位',option:barChart(techCounts.value,{color:'#2c64a0',label:'产品',unit:'项',limit:10,active:techId.value==='all'?'':tech(techId.value)?.name})}])
function pick(key,p){if(!p?.name)return;if(key==='category')category.value=category.value===p.name?'all':p.name;else{const id=p.data?.id;techId.value=techId.value===id?'all':id}}
const sort=ref('default'),page=ref(0),size=12
const ordered=computed(()=>sort.value==='name'?[...rows.value].sort((a,b)=>a.name.localeCompare(b.name,'zh-CN')):sort.value==='tech'?[...rows.value].sort((a,b)=>b.tech.length-a.tech.length||a.name.localeCompare(b.name,'zh-CN')):rows.value)
const pages=computed(()=>Math.max(1,Math.ceil(ordered.value.length/size)))
const shown=computed(()=>ordered.value.slice(page.value*size,(page.value+1)*size))
watch([rows,sort],()=>page.value=0)
const open=ref(null)
</script>
<template>
 <section class="ai-data-hero" :style="{'--hero-color':tone}">
  <div class="ai-hero-main"><span class="ai-hero-tag">领域数据 · 应用载体</span><h3 class="ai-hero-title">人工智能产品与模型</h3>
   <p class="ai-hero-desc">{{fmt(hero.total)}} 项模型、平台、工具与应用产品，连接 {{fmt(hero.owners)}} 家企业与机构，按 70 个关键技术点标注专业技术。</p>
   <ul class="ai-hero-bullets"><li>{{fmt(hero.linked)}} 项产品关联技术点，覆盖 {{hero.techs}} 个技术点</li><li>每项产品保留公开资料来源与发布日期</li></ul></div>
  <div class="ai-hero-highlights">
   <div class="ai-highlight"><strong><CountValue :value="hero.total"/><small>项</small></strong><span>产品与模型</span></div>
   <button type="button" class="ai-highlight link" @click="emit('go','company')"><strong><CountValue :value="hero.owners"/><small>家</small></strong><span>关联企业与机构</span></button>
   <div class="ai-highlight"><strong><CountValue :value="hero.linked"/><small>项</small></strong><span>关联技术点的产品</span></div>
   <div class="ai-highlight"><strong><CountValue :value="hero.techs"/><small>个</small></strong><span>覆盖技术点</span></div>
  </div>
 </section>
 <div v-if="error" class="notice error">{{error}}</div>
 <div v-else-if="!P||!C" class="domain-loading" role="status">正在读取产品目录…</div>
 <template v-else>
  <section class="panel ind-filter" aria-label="筛选">
   <label class="ind-field grow"><span>关键词</span><input v-model="q" placeholder="产品、企业或功能描述" aria-label="按关键词筛选产品"/></label>
   <label class="ind-field"><span>技术大类</span><select v-model="category"><option value="all">全部大类</option><option v-for="c in categories" :key="c" :value="c">{{c}}</option></select></label>
   <label class="ind-field"><span>技术点</span><select v-model="techId"><option value="all">全部技术点</option><option v-for="t in techOptions" :key="t.id" :value="t.id">{{t.name}}</option></select></label>
   <label class="ind-field"><span>企业地区</span><select v-model="province"><option value="all">全部地区</option><option v-for="p in provinces" :key="p" :value="p">{{p}}</option></select></label>
   <label class="ind-field"><span>产品用途</span><select v-model="use"><option value="all">全部用途</option><option v-for="u in uses" :key="u.name" :value="u.name">{{u.name}}</option></select></label>
   <button class="text-button ind-reset" :disabled="!dirty" @click="reset">重置筛选</button>
   <p class="ind-caption">{{fmt(rows.length)}} 项产品 · 点击图表条目可筛选</p>
  </section>
  <div class="ai-kpi-strip fit" :style="{'--n':strip.length}"><article v-for="(k,i) in strip" :key="k.label" :class="{lead:i===0}"><strong><CountValue :value="k.value"/><small>{{k.unit}}</small></strong><span>{{k.label}}</span></article></div>
  <div class="charts-grid equal domain-main-charts domain-chart-grid" :class="{'has-expanded':expanded}">
   <section v-for="p in panels" :key="p.key" class="panel" :class="{'chart-expanded':expanded===p.key}">
    <div class="panel-heading"><h3>{{p.title}}</h3><div class="chart-controls"><button class="chart-expand" @click="expanded=expanded===p.key?'':p.key">{{expanded===p.key?'收起':'展开'}}</button></div></div>
    <Chart :option="p.option" :height="expanded===p.key?380:300" :label="p.title" @select="pick(p.key,$event)"/>
   </section>
  </div>
  <section class="panel records-panel ind-records">
   <div class="panel-heading"><h3>产品目录</h3><label class="ind-sort"><span>排序</span><select v-model="sort"><option value="default">综合展示</option><option value="tech">按技术点数量</option><option value="name">按产品名称</option></select></label></div>
   <div class="ind-cards"><button v-for="p in shown" :key="p.id" class="ind-card" @click="open={kind:'product',id:p.id}">
    <span class="ind-card-top"><b>{{p.name}}</b><em v-for="u in p.uses" :key="u">{{u}}</em></span>
    <small class="ind-card-owner">{{p.ownerNames.join(' · ')||'—'}}</small>
    <span class="ind-card-desc">{{p.desc||'产品资料见详情来源。'}}</span>
    <span class="ind-chips"><span v-for="id in p.tech.slice(0,3)" :key="id">{{tech(id)?.name}}</span><span v-if="p.tech.length>3">+{{p.tech.length-3}}</span></span>
    <i>查看 →</i></button>
    <p v-if="!shown.length" class="ind-empty">暂无匹配产品</p></div>
   <div class="pagination"><span>共 {{fmt(ordered.length)}} 项产品 · 第 {{page+1}} / {{pages}} 页</span><div><button :disabled="page===0" @click="page--">上一页</button><button :disabled="page>=pages-1" @click="page++">下一页</button></div></div>
  </section>
 </template>
 <IndustryDrawer :open="open" @close="open=null" @open="open=$event"/>
</template>
