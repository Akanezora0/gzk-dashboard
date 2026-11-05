<script setup>
import {computed,ref,watch} from 'vue'
import Chart from './Chart.vue'
import CountValue from './CountValue.vue'
import {fmt,concise,chartBase,colors} from '../shared'
const props=defineProps({inventory:Object,type:String,tone:String})
const c=computed(()=>props.inventory.counts)
const config=computed(()=>({
 paper:{title:'人工智能论文统一库',description:'融合多源论文目录、基金成果与引文，形成统一论文身份和可追溯的来源记录。',total:c.value.ai_papers,unit:'篇',year:'发表年份',cards:[['含 DOI 的论文',props.inventory.paper_fields.doi,'篇'],['含摘要的论文',props.inventory.paper_fields.abstract,'篇'],['基金—论文关联',c.value.ai_fund_papers,'对']],relations:[['AI基金关联论文',props.inventory.fund_paper_summary.papers,'篇'],['关联基金项目',props.inventory.fund_paper_summary.projects,'项'],['论文—作者来源记录',c.value.paper_authorship,'条'],['论文引用关系 · 关联库',c.value.citation_edge,'对']]},
 fund:{title:'人工智能基金与成果关联',description:'以基金项目为中心，连接登记成果、人员与机构，保留项目批准和执行时间。',total:c.value.ai_funds,unit:'项',year:'批准年份',cards:[['登记成果关系',c.value.project_outcome,'条'],['项目—论文关系',c.value.ai_fund_papers,'对'],['已有论文关联项目',props.inventory.fund_paper_summary.projects,'项']],relations:[['基金—人员来源记录 · 全库',c.value.project_person,'条'],['基金—论文关系 · 全库',c.value.project_paper,'对'],['基金—专利关系 · 全库',c.value.project_patent,'条'],['负责人接续候选 · 全领域',c.value.funding_continuity,'条']]},
 patent:{title:'人工智能专利统一库',description:'合并 AI 专利包与智慧芽深度资料，按公开号统一身份，连接申请、主体和论文引用。',total:c.value.ai_patents,unit:'条公开文献',year:'申请年份',cards:[['规范申请身份',c.value.ai_applications,'件'],['非专利引文原串',c.value.patent_npl_evidence,'段'],['专利—论文规范关系',c.value.patent_paper_link_all,'对']],relations:[['专利—机构来源关系',c.value.patent_organization,'条'],['专利—发明人来源关系',c.value.patent_person,'条'],['CFRR专利—论文来源记录',c.value.cfrr_patent_paper_evidence,'条'],['已匹配规范论文关系',c.value.patent_paper_link_all,'对']]}
}[props.type]))
const expanded=ref('')
watch(()=>props.type,()=>expanded.value='')
const years=computed(()=>props.inventory.years[props.type].filter(r=>r.year>=2017&&r.year<=2026))
const span=computed(()=>years.value.length?`${years.value[0].year}—${years.value.at(-1).year}`:'—')
const highlights=computed(()=>[['数据总量',config.value.total,config.value.unit],...config.value.cards])
const strip=computed(()=>[
 {label:'数据总量',value:config.value.total,unit:config.value.unit},
 {label:'年度展示',value:span.value,text:true},
 {label:'数据状态',value:'已接入',text:true},
 ...config.value.cards.slice(0,2).map(([label,value,unit])=>({label,value,unit}))
])
const bullets=computed(()=>props.type==='paper'?['按来源合并论文身份，保留 DOI、摘要、作者及资助信息',`发表年份按年展示 ${span.value}`]:props.type==='fund'?['连接项目、论文成果、负责人及承担机构',`批准年份按年展示 ${span.value}`]:['按公开号合并去重，保留申请、公开及引文信息',`申请年份按年展示 ${span.value}`])
const insight=computed(()=>props.type==='paper'?`已关联 ${fmt(props.inventory.fund_paper_summary.projects)} 项基金项目，形成 ${fmt(c.value.ai_fund_papers)} 对项目—论文关系。`:props.type==='fund'?`${fmt(props.inventory.fund_paper_summary.projects)} 项项目已有论文关联，支持按项目追踪成果积累。`:`形成 ${fmt(c.value.ai_applications)} 个规范申请身份，可沿申请、公开及引文继续追踪。`)
const tools={right:4,top:0,feature:{restore:{title:'重置图表'},saveAsImage:{title:'保存图表',pixelRatio:2,backgroundColor:'#fff'}}}
function trend(values,name){return {...chartBase,toolbox:tools,grid:{left:14,right:24,top:32,bottom:26,containLabel:true},tooltip:{trigger:'axis'},xAxis:{type:'category',boundaryGap:false,data:years.value.map(r=>String(r.year)),axisLabel:{interval:0,rotate:45,fontSize:13},axisTick:{show:false},axisLine:{lineStyle:{color:'#d8dfe7'}}},yAxis:{type:'value',minInterval:1,axisLabel:{formatter:concise},splitLine:{lineStyle:{color:'#edf0f4',type:'dashed'}}},series:[{name,type:'line',smooth:true,symbol:'circle',symbolSize:7,data:values,itemStyle:{color:props.tone},lineStyle:{width:2.5},areaStyle:{color:props.tone+'14'}}]}}
const left=computed(()=>trend(years.value.map(r=>r.count),props.type==='fund'?'项目数':props.type==='paper'?'论文数':'公开记录数'))
const typeNames={journal:'期刊论文',conference:'会议论文',preprint:'预印本',unknown:'其他记录'}
const structure=computed(()=>props.type==='paper'?props.inventory.paper_types.map(r=>({name:typeNames[r.name]||r.name,value:r.count})):props.type==='fund'?[{name:'已有论文关联',value:props.inventory.fund_paper_summary.projects},{name:'其他项目',value:c.value.ai_funds-props.inventory.fund_paper_summary.projects}]:[])
const right=computed(()=>props.type==='patent'?trend(years.value.map(r=>r.publication_count),'公开记录数'):{...chartBase,tooltip:{trigger:'item',formatter:'{b}<br/>{c} · {d}%'},legend:{bottom:0,left:'center'},series:[{type:'pie',radius:['43%','65%'],center:['50%','43%'],label:{formatter:p=>`${p.name}\n${fmt(p.value)}`,fontSize:13,lineHeight:21},itemStyle:{borderWidth:3,borderColor:'#fff'},data:structure.value.map((r,i)=>({...r,itemStyle:{color:colors[i]}}))}]})
const rightTitle=computed(()=>props.type==='paper'?'文献类型构成':props.type==='fund'?'项目成果关联情况':'公开年份分布')
const panels=computed(()=>[{key:'years',title:config.value.year+'分布',option:left.value,note:props.type==='patent'?'按公开记录的申请年统计':props.type==='fund'?'按项目批准年统计':'按论文发表年统计'},{key:'structure',title:rightTitle.value,option:right.value,note:props.type==='patent'?'按公开记录的公开年统计':props.type==='fund'?'按项目是否已建立论文关联分组':'统一论文身份 · 文献类型'}])
</script>
<template><div class="current-domain">
 <section class="ai-data-hero" :style="{'--hero-color':tone}">
  <div class="ai-hero-main"><span class="ai-hero-tag">领域数据 · {{type==='paper'?'研究成果':type==='fund'?'基础研究资助':'技术创新'}}</span><h3 class="ai-hero-title">{{config.title}}</h3><p class="ai-hero-desc">{{config.description}}</p><ul class="ai-hero-bullets"><li v-for="item in bullets" :key="item">{{item}}</li></ul><p class="ai-hero-insight">{{insight}}</p></div>
  <div class="ai-hero-highlights"><article class="ai-highlight" v-for="[label,value,unit] in highlights" :key="label"><strong><CountValue :value="value"/><small>{{unit}}</small></strong><span>{{label}}</span></article></div>
 </section>
 <div class="ai-kpi-strip"><article v-for="(k,i) in strip" :key="k.label" :class="{lead:i===0}"><strong v-if="k.text" class="text">{{k.value}}</strong><strong v-else><CountValue :value="Number(k.value)"/><small v-if="k.unit">{{k.unit}}</small></strong><span>{{k.label}}</span></article></div>
 <div class="charts-grid equal domain-main-charts domain-chart-grid" :class="{'has-expanded':expanded}">
  <section v-for="p in panels" :key="type+p.key" class="panel" :class="{'chart-expanded':expanded===p.key}"><div class="panel-heading"><h3>{{p.title}}</h3><button class="chart-expand" @click="expanded=expanded===p.key?'':p.key">{{expanded===p.key?'收起':'展开'}}</button></div><Chart :option="p.option" :height="expanded===p.key?350:280" :label="p.title"/><p class="chart-note">{{p.note}}</p></section>
 </div>
</div></template>
<style scoped>
.current-domain{margin-top:22px}.current-domain .ai-highlight strong{flex-wrap:wrap;white-space:normal;overflow-wrap:anywhere}.current-domain .ai-kpi-strip strong{overflow-wrap:anywhere}@media(max-width:1100px){.current-domain .ai-kpi-strip{grid-template-columns:repeat(3,minmax(0,1fr))}}@media(max-width:600px){.current-domain .ai-kpi-strip{grid-template-columns:1fr 1fr}}
</style>
