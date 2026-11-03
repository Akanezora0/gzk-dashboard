<script setup>
import {computed,ref} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import CatalogPulse from './CatalogPulse.vue'
import '../catalog.css'
import Chart from './Chart.vue'
import DatasetCatalog from './DatasetCatalog.vue'
import {fmt,concise,escape} from '../shared'
import {overviewSources,sourceDisplayUnit,inventoryDelta,overviewDisplayCount,overviewCountTitle} from '../helpers/foundationSources'
import '../overview.css'
import '../inventory.css'
const props=defineProps({data:Object}),kind=ref('全部'),balanced=ref(true)
const route=useRoute(),router=useRouter()
const tabs=[['scale','数据规模'],['updates','更新动态'],['sources','资源明细']]
const view=computed(()=>route.hash==='#updates'?'updates':route.hash.startsWith('#source')?'sources':tabs.some(([id])=>id===route.query.view)?route.query.view:'scale')
function selectView(id){router.push({path:'/overview',query:{...route.query,view:id},hash:''})}
function moveTab(event){const step=event.key==='ArrowRight'?1:event.key==='ArrowLeft'?-1:0;if(!step)return;event.preventDefault();const i=tabs.findIndex(([id])=>id===view.value);const id=tabs[(i+step+tabs.length)%tabs.length][0];selectView(id);document.getElementById('overview-tab-'+id)?.focus()}
const palette={'论文':'#ae1833','软著':'#367ca3','基金':'#377f70','专利':'#987aab','新闻':'#bc8334','主体':'#768ba2','企业':'#3d6d8c','经营':'#6e8f4a','招聘':'#c56b32','政策':'#a96578','产品':'#8b925d','报告':'#668b8a','文本':'#5b6e86'}
const headlineIds=new Set(['cnki_paper','nsfc_paper','nsfc_fund','cn_patent_base'])
const additions=[
 {id:'lowalt_company',name:'企业及相关主体',kind:'企业',count:4173,unit:'个',description:'低空经济企业及相关主体'},
 {id:'lowalt_indicator',name:'经济指标明细',kind:'经营',count:22849,unit:'家',description:'有年度经营指标的企业覆盖'},
 {id:'lowalt_recruit',name:'招聘记录',kind:'招聘',count:226830,unit:'条',description:'低空经济招聘记录'},
 {id:'openscholar_text',name:'OpenScholar文本',kind:'文本',count:277,unit:'GB',description:'OpenScholar文本，277GB',pinBottom:true},
]
const datasets=computed(()=>overviewSources(props.data.overview.datasets))
const types=computed(()=>Object.keys(palette).filter(t=>additions.some(d=>d.kind===t)||datasets.value.some(d=>d.kind===t)))
const colors=computed(()=>types.value.map(t=>palette[t]))
const history=computed(()=>props.data.inventory||{})
const comparisons=computed(()=>Object.fromEntries((history.value.datasets||[]).map(d=>[d.id,d])))
const headline=[
 {id:'literature',name:'文献数量',value:'4783万',unit:'条',title:'文献数量：4783万条',color:'#ae1833'},
 {id:'fund',name:'基金项目',value:'42.8万',unit:'条',title:'基金项目：428409条',color:'#377f70'},
 {id:'patent',name:'专利条数',value:'700.4万',unit:'条',title:'专利条数：700.4万条',color:'#987aab'},
 {id:'recruit',name:'招聘数据条数',value:'728.4万',unit:'条',title:'招聘数据：7284624条',color:'#c56b32'},
]
const shownCount=d=>d.id==='legacy_policy'?22000:overviewDisplayCount(d)
const shownTitle=d=>d.id==='legacy_policy'?'政策文献：2.2万篇':d.id==='openscholar_text'?'OpenScholar文本：277GB':overviewCountTitle(d)
const shownUnit=d=>d.unit==='个'||d.unit==='GB'?d.unit:sourceDisplayUnit(d)
const rows=computed(()=>{
 const pinned=additions.filter(d=>d.pinBottom)
 const ranked=additions.filter(d=>!d.pinBottom)
 const sorted=[...datasets.value].sort((a,b)=>shownCount(b)-shownCount(a))
 if(kind.value!=='全部')return [...sorted.filter(d=>d.kind===kind.value),...additions.filter(d=>d.kind===kind.value)].sort((a,b)=>shownCount(b)-shownCount(a))
 const selected=new Set(types.value.map(t=>sorted.find(d=>d.kind===t)?.id))
 selected.add('cnki_paper')
 return [...sorted.filter(d=>selected.has(d.id)&&!headlineIds.has(d.id)),...ranked].sort((a,b)=>shownCount(b)-shownCount(a)).concat(pinned)
})
const max=computed(()=>Math.max(1,...rows.value.map(shownCount)))
const color=d=>d.color||palette[d.kind]
const width=d=>balanced.value?18+82*Math.pow(shownCount(d)/max.value,.28):100*shownCount(d)/max.value
const unit=shownUnit
const delta=d=>inventoryDelta(comparisons.value[d.id],unit(d))
function pick(name){kind.value=kind.value===name?'全部':name}
const ring=computed(()=>({color:colors.value,tooltip:{trigger:'item',formatter:p=>`${escape(p.name)}<br/>点击查看来源与规模`},graphic:[{type:'text',left:'center',top:'41%',style:{text:'多源数据',fontSize:29,fontWeight:750,fill:'#9c1c38'}},{type:'text',left:'center',top:'53%',style:{text:types.value.length+' 个来源',fontSize:16,fill:'#6f7d90'}}],series:[{type:'pie',radius:['46%','68%'],center:['50%','49%'],selectedMode:'single',selectedOffset:4,startAngle:96,label:{show:true,formatter:'{b}',fontSize:16,color:'#536176',fontWeight:650,overflow:'none',edgeDistance:4,bleedMargin:8,distanceToLabelLine:4},labelLayout:{hideOverlap:false},labelLine:{length:12,length2:8,lineStyle:{color:'#aeb9c5'}},itemStyle:{borderWidth:5,borderColor:'#fff',borderRadius:4},emphasis:{scaleSize:7},data:types.value.map((name,i)=>({name,value:1,selected:kind.value===name,itemStyle:{color:palette[name]}}))}]}))
const previousName=computed(()=>history.value.previous_release?.match(/\d{8}/)?.[0]?.replace(/(\d{4})(\d{2})(\d{2})/,'$1-$2-$3')||'初始基线')
</script>
<template><div class="data-overview">
<div class="overview-subtabs" role="tablist" aria-label="数据总览内容" @keydown="moveTab"><button v-for="[id,label] in tabs" :id="'overview-tab-'+id" :key="id" role="tab" :aria-selected="view===id" :aria-controls="'overview-panel-'+id" :tabindex="view===id?0:-1" :class="{active:view===id}" @click="selectView(id)">{{label}}</button></div>
<div v-if="view==='scale'" key="scale" class="pane-swap" id="overview-panel-scale" role="tabpanel" aria-labelledby="overview-tab-scale">
<section class="ov3-section inventory-intro"><div class="ov3-heading"><div class="ov3-title"><div><h2>多源数据总览</h2><p>汇聚科研、产业与政策数据，支撑跨领域研究与三链分析</p></div></div><a href="#updates" class="ov3-link">查看更新明细 ↓</a></div>
<div class="overview-key-counts" :style="{'--headline-columns':Math.max(1,headline.length)}"><div v-for="d in headline" :key="d.id" class="overview-key-count" :style="{'--source-color':d.color}"><span :title="d.title">{{d.name}}</span><strong :title="d.title">{{d.value}}<small>{{d.unit}}</small></strong></div></div>
<div class="overview-chart-pair"><div class="overview-composition"><div class="overview-chart-heading"><h3>数据构成</h3><button v-if="kind!=='全部'" class="overview-text-button" @click="kind='全部'">显示全部</button></div><Chart :option="ring" :height="430" label="多源数据类别构成" @select="p=>pick(p.name)"/><div class="overview-type-controls" aria-label="数据类别"><button v-for="(t,i) in types" :key="t" :class="{active:kind===t}" :style="{'--type-color':colors[i]}" @click="pick(t)"><i></i>{{t}}</button></div></div>
<div class="overview-scale"><div class="overview-chart-heading"><h3>{{kind==='全部'?'主要来源与规模':kind+' · 来源与规模'}}</h3><button class="overview-text-button" :aria-pressed="balanced" title="均衡显示压缩数量差距；精确数量见标签，可切换按数量显示" @click="balanced=!balanced">{{balanced?'均衡显示':'按数量显示'}} ⇄</button></div><div class="overview-scale-rows"><a v-for="d in rows" :key="d.id" class="overview-scale-row" :href="additions.some(item=>item.id===d.id)?undefined:'#source-'+encodeURIComponent(d.id)" :title="shownTitle(d)" :style="{'--source-color':color(d)}"><span class="overview-scale-name">{{d.name}}</span><span class="overview-scale-track"><i :style="{width:width(d)+'%'}"></i></span><span class="overview-scale-value"><strong>{{concise(shownCount(d))}}<small>{{unit(d)}}</small></strong><small class="overview-increment" :class="'is-'+delta(d).state" :title="delta(d).title">{{delta(d).label}}</small></span></a></div></div></div>
<div class="overview-period-footer"><span>{{types.length}} 类数据 <i>·</i> {{datasets.length}} 项来源</span><span>对比上期：{{previousName}}</span></div>
</section></div><div v-else-if="view==='updates'" key="updates" class="pane-swap" id="overview-panel-updates" role="tabpanel" aria-labelledby="overview-tab-updates"><div id="updates"><CatalogPulse/></div></div><div v-else key="sources" class="pane-swap" id="overview-panel-sources" role="tabpanel" aria-labelledby="overview-tab-sources"><DatasetCatalog :data="data" integrated/></div>
</div></template>
