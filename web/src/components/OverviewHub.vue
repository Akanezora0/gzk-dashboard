<script setup>
import {computed,ref} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import CatalogPulse from './CatalogPulse.vue'
import '../catalog.css'
import Chart from './Chart.vue'
import DatasetCatalog from './DatasetCatalog.vue'
import {fmt,concise,escape} from '../shared'
import {overviewHeadline,overviewSources,sourceDisplayUnit,inventoryDelta,overviewDisplayCount,overviewCountTitle} from '../helpers/foundationSources'
import '../overview.css'
import '../inventory.css'
import '../overview-dash.css'
const props=defineProps({data:Object}),kind=ref('全部'),balanced=ref(true)
const route=useRoute(),router=useRouter()
const tabs=[['scale','数据规模'],['updates','更新动态'],['sources','资源明细']]
const view=computed(()=>route.hash==='#updates'?'updates':route.hash.startsWith('#source')?'sources':tabs.some(([id])=>id===route.query.view)?route.query.view:'scale')
function selectView(id){router.push({path:'/overview',query:{...route.query,view:id},hash:''})}
function moveTab(event){const step=event.key==='ArrowRight'?1:event.key==='ArrowLeft'?-1:0;if(!step)return;event.preventDefault();const i=tabs.findIndex(([id])=>id===view.value);const id=tabs[(i+step+tabs.length)%tabs.length][0];selectView(id);document.getElementById('overview-tab-'+id)?.focus()}
const palette={'论文':'#ae1833','软著':'#367ca3','基金':'#377f70','专利':'#987aab','新闻':'#bc8334','主体':'#768ba2','企业':'#3d6d8c','经营':'#6e8f4a','招聘':'#c56b32','政策':'#a96578','产品':'#8b925d','报告':'#668b8a','文本':'#5b6e86'}
const headlineIds=new Set(['unified_paper','unified_fund','cn_patent_base'])
const additions=[
 {id:'lowalt_company',name:'企业及相关主体',kind:'企业',count:4173,unit:'个',description:'低空经济企业及相关主体'},
 {id:'lowalt_indicator',name:'经济指标明细',kind:'经营',count:22849,unit:'家',description:'有年度经营指标的企业覆盖'},
 {id:'lowalt_recruit',name:'招聘记录',kind:'招聘',count:226830,unit:'条',description:'低空经济招聘记录'},
 {id:'openscholar_text',name:'OpenScholar文本',kind:'文本',count:277,unit:'GB',description:'OpenScholar文本，277GB',pinBottom:true},
 {id:'fund_projects',name:'基金项目',kind:'基金',count:428409,unit:'条',description:'基金项目记录',core:true},
 {id:'recruit_all',name:'招聘数据',kind:'招聘',count:7284624,unit:'条',description:'企业招聘信息',core:true},
]
const datasets=computed(()=>overviewSources(props.data.overview.datasets).filter(d=>d.kind!=='关系'))
const types=computed(()=>Object.keys(palette).filter(t=>additions.some(d=>d.kind===t)||datasets.value.some(d=>d.kind===t)))
const colors=computed(()=>types.value.map(t=>palette[t]))
const history=computed(()=>props.data.inventory||{})
const comparisons=computed(()=>Object.fromEntries((history.value.datasets||[]).map(d=>[d.id,d])))
const headline=computed(()=>overviewHeadline(props.data))
const shownCount=d=>overviewDisplayCount(d)
const shownTitle=d=>d.id==='openscholar_text'?'OpenScholar文本：277GB':overviewCountTitle(d)
const shownUnit=d=>d.unit==='个'||d.unit==='GB'?d.unit:sourceDisplayUnit(d)
const coreIds=['unified_paper','fund_projects','cn_patent_base','recruit_all']
const isCore=d=>coreIds.includes(d.id)
const rows=computed(()=>{
 const all=[...datasets.value.filter(d=>d.id!=='unified_fund'),...additions]
 const byCount=(a,b)=>shownCount(b)-shownCount(a)
 if(kind.value!=='全部')return all.filter(d=>d.kind===kind.value&&!isCore(d)).sort(byCount)
 const core=coreIds.map(id=>all.find(d=>d.id===id)).filter(Boolean)
 const coreKinds=new Set(core.map(d=>d.kind))
 const rest=all.filter(d=>!isCore(d)&&!d.pinBottom)
 const picked=types.value.map(t=>rest.filter(d=>d.kind===t).sort(byCount)[0]).filter(Boolean)
 const cnki=rest.find(d=>d.id==='cnki_paper')
 if(cnki&&!picked.includes(cnki))picked.push(cnki)
 return [...picked,...additions.filter(d=>d.pinBottom)].sort(byCount)
})
const max=computed(()=>Math.max(1,...rows.value.map(shownCount)))
const color=d=>d.color||palette[d.kind]
const width=d=>balanced.value?18+82*Math.pow(shownCount(d)/max.value,.28):100*shownCount(d)/max.value
const unit=shownUnit
const delta=d=>inventoryDelta(comparisons.value[d.id],unit(d))
function pick(name){kind.value=kind.value===name?'全部':name}
const ring=computed(()=>({color:colors.value,tooltip:{trigger:'item',formatter:p=>`${escape(p.name)}<br/>点击查看来源与规模`},graphic:[{type:'text',left:'center',top:'41%',style:{text:'多源数据',fontSize:29,fontWeight:750,fill:'#9c1c38'}},{type:'text',left:'center',top:'53%',style:{text:types.value.length+' 个来源',fontSize:16,fill:'#6f7d90'}}],series:[{type:'pie',radius:['46%','68%'],center:['50%','49%'],selectedMode:'single',selectedOffset:4,startAngle:96,label:{show:true,formatter:'{b}',fontSize:16,color:'#536176',fontWeight:650,overflow:'none',edgeDistance:4,bleedMargin:8,distanceToLabelLine:4},labelLayout:{hideOverlap:false},labelLine:{length:12,length2:8,lineStyle:{color:'#aeb9c5'}},itemStyle:{borderWidth:5,borderColor:'#fff',borderRadius:4},emphasis:{scaleSize:7},data:types.value.map((name,i)=>({name,value:1,selected:kind.value===name,itemStyle:{color:palette[name]}}))}]}))
const previousName=computed(()=>history.value.previous_release?.match(/\d{8}/)?.[0]?.replace(/(\d{4})(\d{2})(\d{2})/,'$1-$2-$3')||'初始基线')
/* ---------- 数据规模面板：全领域多源数据 ---------- */
import HomeIcon from './HomeIcon.vue'
const cur=computed(()=>props.data.currentInventory||{})
const cc=computed(()=>cur.value.counts||{})
const heroSub={literature:'跨来源去重论文',fund:'基金项目记录',patent:'全国公开文献 · 按公开号去重',recruit:'企业招聘信息'}
const kindSources=computed(()=>{const m={};[...datasets.value,...additions].forEach(d=>{(m[d.kind]||(m[d.kind]=[])).push(d)});return m})
const ring2=computed(()=>({tooltip:{trigger:'item',formatter:p=>`${escape(p.name)}<br/>${p.value} 项来源 · 点击筛选`},
 graphic:[{type:'text',left:'center',top:'38%',style:{text:String(types.value.length),fontSize:64,fontWeight:800,fill:'#9c1c38',align:'center'}},{type:'text',left:'center',top:'56%',style:{text:'类数据',fontSize:20,fontWeight:600,fill:'#5d6878',align:'center'}}],
 series:[{type:'pie',radius:['48%','74%'],center:['50%','50%'],startAngle:96,selectedMode:'single',selectedOffset:5,label:{show:true,formatter:'{b}',fontSize:15,color:'#4a5566',fontWeight:650},labelLine:{length:10,length2:8,lineStyle:{color:'#c3c9d2'}},itemStyle:{borderColor:'#fff',borderWidth:4,borderRadius:4},emphasis:{scaleSize:6},
  data:types.value.map(k=>({name:k,value:(kindSources.value[k]||[]).length||1,selected:kind.value===k,itemStyle:{color:palette[k]}}))}]}))
/* 实体与关系：横向主干 + 编号连线 */
/* 布局按阅读顺序：上方回环为 1，第一行 2、3，其下 4、5，底部 6 */
const SW=800,SH=400,NR=40
const entities=computed(()=>{const c=cc.value;return [
 {id:'patent',name:'专利',icon:'patent',value:c.national_patents,color:'#2c64a0',x:90,y:125},
 {id:'paper',name:'论文',icon:'paper',value:c.papers,color:'#a21535',x:300,y:125},
 {id:'org',name:'机构',icon:'org',value:c.organization,color:'#23806e',x:540,y:125},
 {id:'person',name:'人员',icon:'person',value:c.person,color:'#6f4a94',x:740,y:125},
 {id:'fund',name:'基金项目',icon:'grant',value:c.project,color:'#b2772a',x:515,y:285},
]})
const cubic=(p)=>{const t=.5,u=.5;return [u*u*u*p[0]+3*u*u*t*p[2]+3*u*t*t*p[4]+t*t*t*p[6],u*u*u*p[1]+3*u*u*t*p[3]+3*u*t*t*p[5]+t*t*t*p[7]]}
const curve=(p)=>{const [bx,by]=cubic(p);return {path:`M ${p[0]} ${p[1]} C ${p[2]} ${p[3]}, ${p[4]} ${p[5]}, ${p[6]} ${p[7]}`,bx,by}}
const line=(x1,y1,x2,y2)=>({path:`M ${x1} ${y1} L ${x2} ${y2}`,bx:(x1+x2)/2,by:(y1+y2)/2})
const relations=computed(()=>{const c=cc.value;const E=Object.fromEntries(entities.value.map(e=>[e.id,e]));const P=E.paper,T=E.patent,O=E.org,H=E.person,F=E.fund;return [
 {n:1,name:'论文引用',value:c.citation_edge,note:'论文之间的引用连接',color:'#a21535',...curve([P.x-20,P.y-28,P.x-62,P.y-118,P.x+62,P.y-118,P.x+20,P.y-28])},
 {n:2,name:'专利—论文来源记录',value:c.cfrr_patent_paper_evidence,note:'专利引用科学文献的记录',color:'#2c64a0',...line(T.x+NR,T.y,P.x-NR,P.y)},
 {n:3,name:'人员—机构',value:c.person_organization_observation,note:'研究人员的机构归属观察',color:'#23806e',...line(O.x+NR,O.y,H.x-NR,H.y)},
 {n:4,name:'基金—论文',value:c.project_paper,note:'基金项目与资助成果的连接',color:'#b2772a',...curve([P.x+NR,P.y,P.x+120,P.y,F.x-45,F.y-105,F.x-24,F.y-24])},
 {n:5,name:'基金—人员',value:c.project_person,note:'项目负责人与成员记录',color:'#6f4a94',...curve([H.x-26,H.y+22,H.x-90,H.y+70,F.x+75,F.y-75,F.x+24,F.y-24])},
 {n:6,name:'基金—专利',value:c.project_patent,note:'基金项目与专利成果的连接',color:'#5d6f86',...curve([T.x,T.y+112,T.x,T.y+205,F.x-120,F.y+60,F.x-NR,F.y])},
]})
const relWidth=v=>1.2+Math.log10(Math.max(10,v||10))/2
const activeRel=ref(0)
</script>
<template><div class="data-overview">
<div class="domain-switch ovd-switch" aria-label="数据总览内容"><span>数据视图</span><div role="tablist" aria-label="数据总览内容" @keydown="moveTab"><button v-for="[id,label] in tabs" :id="'overview-tab-'+id" :key="id" role="tab" :aria-selected="view===id" :aria-controls="'overview-panel-'+id" :tabindex="view===id?0:-1" :class="{active:view===id}" @click="selectView(id)">{{label}}</button></div><small>{{types.length}} 类数据 · {{datasets.length}} 项来源 · 统计更新 {{data.currentInventory.as_of}}</small></div>
<div v-if="view==='scale'" key="scale" class="pane-swap ovd hero-light" id="overview-panel-scale" role="tabpanel" aria-labelledby="overview-tab-scale">
<section class="ovd-hero"><div class="ovd-hero-art" aria-hidden="true"><svg viewBox="0 0 800 300" preserveAspectRatio="xMaxYMid slice"><path v-for="i in 16" :key="i" :d="`M ${-60+i*4} ${330} C ${250+i*12} ${250-i*10}, ${470+i*9} ${30+i*9}, 860 ${-30+i*20}`"/></svg></div>
 <div class="ovd-hero-head"><div><p class="ovd-eyebrow">多源数据总览</p><h2>全领域、多来源的<br/>基础研究数据底座</h2><p class="ovd-hero-lead">汇聚论文、基金、专利、企业、政策等多源数据，持续规范入库与更新</p></div><div class="ovd-hero-meta"><div><strong>{{types.length}}</strong><span>类数据</span></div><div><strong>{{datasets.length}}</strong><span>项来源</span></div><div><strong class="date">{{data.currentInventory.as_of}}</strong><span>统计更新</span></div><a href="#updates" class="ovd-hero-link" @click.prevent="selectView('updates')">查看更新动态 <span aria-hidden="true">→</span></a></div></div>
 
</section>

<section class="ovd-card ovd-composition"><header class="ovd-card-head"><div><h3>核心数据与来源构成</h3><p>四类核心数据规模，以及 {{types.length}} 类数据的主要来源，点击类别筛选来源</p></div><button v-if="kind!=='全部'" class="overview-text-button" @click="kind='全部'">显示全部</button></header>
 <div class="ovd-core"><div v-for="d in headline" :key="d.id" class="ovd-core-item" :style="{'--c':d.color}"><span>{{d.name}}</span><strong :title="d.title">{{d.value}}<small>{{d.unit}}</small></strong><em>{{heroSub[d.id]}}</em></div></div>
 <div class="ovd-comp-grid"><div class="ovd-ring"><Chart :option="ring2" :height="480" label="多源数据类别构成" @select="p=>pick(p.name)"/></div>
 <div class="ovd-rows"><div class="ovd-rows-head"><h4>{{kind==='全部'?'主要来源与规模':kind+' · 来源与规模'}}</h4><button class="overview-text-button" :aria-pressed="balanced" @click="balanced=!balanced">{{balanced?'均衡显示':'按数量显示'}} ⇄</button></div>
  <a v-for="d in rows" :key="d.id" class="ovd-row" :href="additions.some(item=>item.id===d.id)?undefined:'#source-'+encodeURIComponent(d.id)" :title="shownTitle(d)" :style="{'--c':color(d)}"><span class="ovd-row-name"><i></i>{{d.name}}</span><span class="ovd-row-track"><b :style="{width:width(d)+'%'}"></b></span><strong>{{concise(shownCount(d))}}<small>{{unit(d)}}</small></strong></a></div></div>
</section>




</div><div v-else-if="view==='updates'" key="updates" class="pane-swap" id="overview-panel-updates" role="tabpanel" aria-labelledby="overview-tab-updates"><div id="updates"><CatalogPulse/></div></div><div v-else key="sources" class="pane-swap" id="overview-panel-sources" role="tabpanel" aria-labelledby="overview-tab-sources"><DatasetCatalog :data="data" integrated/></div>
</div></template>
