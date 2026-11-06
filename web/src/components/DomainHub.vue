<script setup>
import {ref,computed,watch,onBeforeUnmount,provide,nextTick} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import Chart from './Chart.vue'
import CurrentDomainInventory from './CurrentDomainInventory.vue'
import CountValue from './CountValue.vue'
import '../domain.css'
import '../domain_delta.css'
import {api,fmt,concise,chartBase,colors,safeUrl,escape} from '../shared'
import {presentSource} from '../helpers/foundationSources'
import {groupAiYears,EARLY_YEAR_BUCKET,aiYearLabel} from '../helpers/aiYearBuckets'

const props=defineProps({data:Object}),route=useRoute(),router=useRouter()
const tabs=[['paper','论文'],['fund','基金'],['patent','专利'],['software','软著'],['policy','政策'],['news','新闻'],['report','报告'],['company','企业'],['product','产品']]
const profiles={
 paper:{primary:'cnki_paper',color:'#AE0D28',title:'论文与研究成果',year:'发表年份',unit:'条',recordTitle:'文献题录',person:'作者',charts:['years','topics','ranking','secondary']},
 fund:{primary:'nsfc_fund',color:'#AD6E20',title:'基础研究资助',year:'批准年份',unit:'项',recordTitle:'基金项目',person:'依托单位',rankTitle:'依托单位 · 项目数',charts:['years','ranking','topics']},
 patent:{primary:'legacy_patent',color:'#2877B0',title:'专利与技术创新',year:'申请年份',unit:'条',recordTitle:'专利公开记录',person:'申请主体',rankTitle:'申请主体 · 公开记录数',charts:['years','ranking','topics']},
 software:{primary:'legacy_software',color:'#278771',title:'软件著作权',year:'登记年份',unit:'条',recordTitle:'软件著作权登记',person:'登记单位',rankTitle:'登记单位 · 记录数',charts:['years','ranking','topics']},
 policy:{primary:'ai_policy',color:'#8B63AA',title:'政策与创新环境',year:'公布年份',unit:'条',recordTitle:'政策文本',person:'制定机关',rankTitle:'中央与地方构成',charts:['years','ranking','secondary']},
 news:{primary:'legacy_news',color:'#BD7245',title:'产业动态',year:'发布年份',unit:'条',recordTitle:'产业新闻',rankTitle:'新闻来源 · 记录数',charts:['years','ranking']},
 report:{primary:'ai_report',color:'#437B87',title:'行业研究',unit:'份',recordTitle:'行业报告',rankTitle:'报告类别构成',charts:['topics','ranking']},
 company:{primary:'ai_company',color:'#7563A8',title:'企业与创新主体',unit:'条',recordTitle:'企业名录',rankTitle:'企业省份分布 · 前 10 位',charts:['ranking']},
 product:{primary:'legacy_product',color:'#678147',title:'产品与应用载体',unit:'条',recordTitle:'产品名录',rankTitle:'厂商标识与产品记录',charts:[]},
}
const validType=v=>Object.hasOwn(profiles,String(v))?String(v):'paper'
const type=ref(validType(route.query.type||route.query.tab))
const profile=computed(()=>profiles[type.value])
const hasCurrent=computed(()=>Boolean(props.data.currentInventory&&['paper','fund','patent'].includes(type.value)))
const metricList=computed(()=>(props.data?.domain?.metrics||[]).map(presentSource))
const normalize=m=>m.kind==='copyright'?'software':m.kind
const sources=computed(()=>metricList.value.filter(m=>normalize(m)===type.value).sort((a,b)=>Number(b.namespace===profile.value.primary)-Number(a.namespace===profile.value.primary)))
const namespace=computed(()=>sources.value.find(m=>m.namespace===profile.value.primary)?.namespace||sources.value[0]?.namespace||'')
const current=computed(()=>sources.value.find(m=>m.namespace===namespace.value))
const sourceViews=ref({}),loading=ref(false),errors=ref({})
const analytics=computed(()=>sourceViews.value[namespace.value]||null)
const secondaryNamespace=computed(()=>type.value==='paper'?'nsfc_paper':type.value==='policy'?'legacy_policy':'')
const secondary=computed(()=>sourceViews.value[secondaryNamespace.value]||null)
const expandedChart=ref('')
const recordNamespace=ref(''),recordQuery=ref(''),query=ref(''),offset=ref(0),rows=ref([]),total=ref(0),recordsLoading=ref(false),recordError=ref(''),expanded=ref(null)
const recordsSection=ref(null)
const recordSource=computed(()=>sources.value.find(m=>m.namespace===recordNamespace.value))
let analyticsRequest=0,recordRequest=0

async function loadAnalytics(){
 const request=++analyticsRequest,requested=sources.value.map(m=>m.namespace)
 sourceViews.value={};errors.value={};loading.value=Boolean(requested.length)
 if(!requested.length)return
 const results=await Promise.allSettled(requested.map(ns=>api('/api/llm/analytics?'+new URLSearchParams({namespace:ns,scope:'ai'}))))
 if(request!==analyticsRequest)return
 const views={},issues={}
 results.forEach((result,i)=>{if(result.status==='fulfilled')views[requested[i]]=result.value;else issues[requested[i]]=result.reason?.message||'读取失败'})
 sourceViews.value=views;errors.value=issues;loading.value=false
}
async function loadRecords(){
 const request=++recordRequest,ns=recordNamespace.value
 rows.value=[];total.value=0;recordError.value='';expanded.value=null
 if(!ns||!sources.value.some(m=>m.namespace===ns)){recordsLoading.value=false;return}
 recordsLoading.value=true
 try{
  const d=await api('/api/llm/records?'+new URLSearchParams({namespace:ns,scope:'ai',q:query.value,offset:String(offset.value),limit:'10'}))
  if(request===recordRequest){rows.value=d.rows||[];total.value=d.total||0}
 }catch(e){if(request===recordRequest)recordError.value=e.message}
 finally{if(request===recordRequest)recordsLoading.value=false}
}
function selectType(id){if(id===type.value)return;type.value=id;router.replace({path:'/data',query:{type:id}})}
function search(){const next=recordQuery.value.trim();if(query.value===next&&offset.value===0)loadRecords();else{query.value=next;offset.value=0}}
function selectRecordSource(ns,scroll=false){recordNamespace.value=ns;offset.value=0;expanded.value=null;if(scroll)recordsSection.value?.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'})}
watch(()=>route.query.type||route.query.tab,v=>{type.value=validType(v)})
watch(()=>`${type.value}:${sources.value.map(m=>m.namespace).join(',')}`,()=>{
 ++recordRequest;rows.value=[];total.value=0;recordError.value='';expanded.value=null;expandedChart.value=''
 recordQuery.value='';query.value='';offset.value=0
 const requested=String(route.query.namespace||'')
 recordNamespace.value=sources.value.some(m=>m.namespace===requested)?requested:namespace.value
 loadAnalytics()
},{immediate:true,flush:'sync'})
watch([type,recordNamespace,query,offset],loadRecords,{immediate:true,flush:'post'})
onBeforeUnmount(()=>{analyticsRequest++;recordRequest++})

const field=(view,name)=>view?.fields?.find(f=>f.name===name)?.available??null
const rankCount=(view,name)=>view?.ranking?.items?.find(r=>r.name===name)?.count??null
const yearRange=view=>{const ys=(view?.years||[]).map(x=>x.year).filter(Boolean);return ys.length?`${Math.min(...ys)}—${Math.max(...ys)}`:'—'}
// 耀元政策规范库 v3 展示口径；与 8,563 未跨源去重的历史候选分开标明。
const policyPresent={total:8563,central:631,local:7932,regions:31,aiLabel:'AI／大模型政策收录',legacyLabel:'历史政策AI相关候选'}
const sourceLabel=ns=>({cnki_paper:'中文期刊文献',nsfc_paper:'国自然资助论文',ai_policy:policyPresent.aiLabel,legacy_policy:policyPresent.legacyLabel})[ns]||sources.value.find(m=>m.namespace===ns)?.name||''
const sourceCards=computed(()=>sources.value.map(m=>{
 const view=sourceViews.value[m.namespace]
 const facts=m.namespace==='cnki_paper'?[['作者信息',field(view,'作者')],['机构信息',field(view,'作者机构')]]:
 m.namespace==='nsfc_paper'?[['含项目标识',field(view,'来源项目ID')],['含DOI标识',field(view,'DOI')]]:
 m.namespace==='ai_policy'?[['中央政策',policyPresent.central],['地方独立政策',policyPresent.local]]:
 [['制定机关',field(view,'制定机关')],['文号记录',field(view,'文号')]]
 const total=m.namespace==='ai_policy'?policyPresent.total:(view?.total??m.ai_candidates)
 return {namespace:m.namespace,name:sourceLabel(m.namespace),total,years:yearRange(view),facts,error:errors.value[m.namespace]}
}))
const kpis=computed(()=>{
 const a=analytics.value,n=(label,value,unit='条',detail='')=>({label,value,unit,detail}),span={label:profile.value.year,value:yearRange(a),text:true,detail:'记录时间范围'}
 if(!a)return []
 switch(type.value){
  case 'fund':return [n('基金项目候选',a.total,'项'),span,n('含批准号项目',field(a,'批准号'),'项'),n('涉及技术主题',a.topic_count,'项')]
  case 'patent':return [n('专利公开候选',a.total),span,n('含专利引文记录',field(a,'专利引证')),n('含非专利引文记录',field(a,'非专利引文'))]
  case 'software':return [n('软著候选记录',a.total),span,n('含工商标识记录',field(a,'工商来源ID')),n('涉及技术主题',a.topic_count,'项')]
  case 'news':return [n('产业新闻候选',a.total),span,n('含来源信息',field(a,'来源')),n('含相关主体信息',field(a,'相关方'))]
  case 'report':return [n('行业报告候选',a.total,'份'),n('AI专题报告',rankCount(a,'AI专题报告'),'份'),n('跨行业报告',rankCount(a,'跨行业报告'),'份'),n('涉及技术主题',a.topic_count,'项')]
  case 'company':return [n('企业名录候选',a.total),n('含省份信息',field(a,'省份')),n('含工商来源标识',field(a,'天眼查ID'))]
  case 'product':return [n('产品候选记录',a.total),n('含产品型号',field(a,'产品型号')),n('含厂商代码',field(a,'厂商代码'))]
  default:return []
 }
})
const chartTools={right:4,top:0,feature:{restore:{title:'重置图表'},saveAsImage:{title:'保存图表',pixelRatio:2,backgroundColor:'#fff'}}}
function yearChart(view,color=profile.value.color){const years=groupAiYears(view?.years||[]);return {...chartBase,toolbox:chartTools,
 grid:{left:14,right:24,top:28,bottom:22,containLabel:true},
 tooltip:{trigger:'axis',confine:true,axisPointer:{type:'line'},formatter:ps=>`${escape(aiYearLabel(ps[0]?.axisValue))}<br/>${ps.map(p=>`${p.marker} ${escape(p.seriesName)}：<b>${fmt(p.value)}</b>`).join('<br/>')}`},
 xAxis:{type:'category',boundaryGap:false,data:years.map(y=>String(y.year)),axisLabel:{fontSize:13,color:'#546175',interval:0,hideOverlap:false,showMinLabel:true,showMaxLabel:true,rotate:50,margin:13,lineHeight:18,formatter:value=>value===EARLY_YEAR_BUCKET?'2016年之前':value},axisLine:{lineStyle:{color:'#d8dfe7'}},axisTick:{show:false}},
 yAxis:{type:'value',minInterval:1,axisLabel:{fontSize:13,formatter:concise},splitLine:{lineStyle:{color:'#edf0f4',type:'dashed'}}},
 series:[{name:'记录数',type:'line',smooth:true,symbol:'circle',symbolSize:7,itemStyle:{color},areaStyle:{color:color+'14'},lineStyle:{width:2.5,color},emphasis:{focus:'series'},data:years.map(y=>y.count)}]}}
function horizontalChart(items,{color=profile.value.color,topic=false,label='记录数',limit=8}={}){
 const values=(items||[]).slice(0,limit).reverse()
 return {...chartBase,grid:{left:topic?133:146,right:49,top:14,bottom:27},
 tooltip:{trigger:'item',confine:true,formatter:p=>`${escape(p.name)}<br/>${p.marker} ${escape(label)}：<b>${fmt(p.value)}</b>${topic?'<br/>点击查看技术演进':''}`},
 xAxis:{type:'value',minInterval:1,axisLabel:{fontSize:12,formatter:concise},splitLine:{lineStyle:{color:'#edf0f4',type:'dashed'}}},
 yAxis:{type:'category',data:values.map(v=>v.name),axisLabel:{fontSize:13,width:topic?121:134,overflow:'truncate'},axisTick:{show:false},axisLine:{show:false}},
 series:[{name:label,type:'bar',barMaxWidth:20,cursor:topic?'pointer':'default',label:{show:true,position:'right',fontSize:13,color:'#465367',formatter:p=>fmt(p.value)},emphasis:{focus:'self'},data:values.map((v,i)=>({name:v.name,value:v.count,topicId:topic?v.id:undefined,itemStyle:{color:topic?colors[(values.length-i-1)%colors.length]:color,borderRadius:[0,4,4,0]}}))}]}
}
function compositionChart(items){return {...chartBase,tooltip:{trigger:'item',confine:true,formatter:p=>`${escape(p.name)}<br/>${p.marker} ${fmt(p.value)} ${profile.value.unit} · ${p.percent}%`},legend:{bottom:0,left:'center',textStyle:{fontSize:14,color:'#526073'}},series:[{type:'pie',radius:['43%','66%'],center:['50%','44%'],label:{show:true,formatter:p=>`${escape(p.name)}\n${fmt(p.value)}`,fontSize:13,lineHeight:20},labelLine:{length:12,length2:8},itemStyle:{borderColor:'#fff',borderWidth:3},emphasis:{scaleSize:5},data:(items||[]).map((r,i)=>({name:r.name,value:r.count,itemStyle:{color:colors[(i+1)%colors.length]}}))}]}}
const chartPanels=computed(()=>{
 const a=analytics.value;if(!a)return []
 return profile.value.charts.filter(key=>!hasCurrent.value||['topics','ranking'].includes(key)).flatMap(key=>{
  if(key==='years')return a.years?.length?[{key,title:`${profile.value.year}分布`,subtitle:current.value?.name,option:yearChart(a)}]:[]
  if(key==='topics')return a.topics?.length?[{key,title:'技术主题分布',subtitle:`${current.value?.name} · ${hasCurrent.value?'专题来源样本 · ':''}词表匹配`,option:horizontalChart(a.topics,{topic:true,label:'候选记录'}),topic:true}]:[]
  if(key==='ranking'){
   if(type.value==='policy'){
    const items=[{name:'中央政策',count:policyPresent.central},{name:'地方独立政策',count:policyPresent.local}]
    return [{key,title:profile.value.rankTitle||'中央与地方构成',subtitle:policyPresent.aiLabel,option:compositionChart(items)}]
   }
   if(!a.ranking?.items?.length)return []
   const pie=type.value==='report',limit=type.value==='company'?10:8
   return [{key,title:profile.value.rankTitle||'期刊分布 · 前 8 位',subtitle:pie?'':`${hasCurrent.value?current.value?.name+' · 专题来源样本 · ':''}前 ${Math.min(limit,a.ranking.items.length)} 位`,option:pie?compositionChart(a.ranking.items):horizontalChart(a.ranking.items,{label:type.value==='fund'?'项目数':'记录数',limit}),full:type.value==='company'}]
  }
  if(key==='secondary'&&secondary.value){
   const b=secondary.value
   return [{key,title:type.value==='paper'?'国自然资助论文 · 成果类型':`${policyPresent.legacyLabel} · 制定机关`,subtitle:sourceLabel(secondaryNamespace.value),option:type.value==='paper'?compositionChart(b.ranking?.items):horizontalChart(b.ranking?.items,{color:'#A76B89',label:'政策记录'})}]
  }
  return []
 })
})
function openTopic(p){
 const id=p.data?.topicId;if(!id)return
 const topic=(props.data.tree?.nodes||[]).find(t=>t.legacy_topic_ids?.includes(id))
 const milestone=props.data.milestones?.find(m=>m.legacy_topic_id===id)
 router.push({path:'/evolution',query:topic||milestone?{topic:topic?.id||milestone.topic_id}:{search:p.name}})
}
const newsTopics=computed(()=>type.value==='news'?(analytics.value?.topics||[]).slice(0,8):[])
const policyTrend=computed(()=>yearChart({years:props.data.policy?.by_year||[]},'#278771'))
const policyRegions=computed(()=>horizontalChart(props.data.policy?.by_region||[],{color:'#438995',label:'地区记录',limit:10}))
const personColumn=computed(()=>profile.value.person&&!(type.value==='policy'&&recordNamespace.value==='ai_policy'))
const showYear=computed(()=>Boolean(profile.value.year))
const recordColspan=computed(()=>2+Number(showYear.value)+Number(Boolean(personColumn.value)))
function person(r){const value=type.value==='paper'?(r.authors||r.institution):r.subject;return Array.isArray(value)?value.join(' · '):value||'—'}
const fieldLabels={title:'标题',year:'年份',doi:'DOI',authors:'作者',institution:'机构',abstract:'摘要',funding:'资助信息',url:'原文链接',patent_number:'专利号',name:'名称',reason:'分类依据',keywords:'关键词',subject:'主题',body:'正文',content:'正文',description:'描述',classification_reason:'分类依据'}
const paneReady=ref(false)
provide('viewSettled', paneReady)
let paneToken=0
function armPane(){paneReady.value=false;const token=++paneToken;nextTick(()=>requestAnimationFrame(()=>setTimeout(()=>{if(token===paneToken)paneReady.value=true},90)))}
watch(type, armPane, {immediate:true})
function metricOf(ns){return metricList.value.find(m=>m.namespace===ns)}
function metricCandidates(ns){return ns==='ai_policy'?policyPresent.total:metricOf(ns)?.ai_candidates}
function tabCount(id){const counts=props.data.currentInventory?.counts;const current={paper:counts?.ai_papers,fund:counts?.ai_funds,patent:counts?.ai_patents}[id];if(current!=null)return concise(current);const n=metricCandidates(profiles[id].primary);return typeof n==='number'?concise(n):''}
const brief=computed(()=>{
 const a=analytics.value,p=profile.value,span=yearRange(a)
 const topics=a?.topic_count,top=(a?.topics||[]).slice(0,2).map(t=>t.name)
 const insight=top.length>=2?`${top[0]}与${top[1]}是当前词表匹配记录较多的技术主题。`:topics?`词表匹配涉及 ${fmt(topics)} 个技术主题。`:''
 const yearNote=p.charts?.includes('years')?'年份分布中，2016 年前合并显示，2016 年起按年展开':''
 const chip=(label,value,hint,typeId)=>({label,value,hint,type:typeId,numeric:typeof value==='number'})
 const m=ns=>metricCandidates(ns)
 const tiles=[],add=(label,value,unit='',text=false)=>{if(value!=null&&value!=='')tiles.push({label,value,unit,text})}
 let tag='领域数据 · '+p.title,title=p.title,desc='',bullets=[],highlights=[]
 if(type.value==='paper'){
  tag='领域数据 · 研究成果';title='论文与研究成果'
  desc=`论文按来源分别计数。中文期刊文献 ${fmt(m('cnki_paper'))} 条，保留题名、作者与期刊信息；国自然资助论文 ${fmt(m('nsfc_paper'))} 篇，为基金项目关联的成果记录。`
  bullets=['两类来源不能相加为唯一论文总数',yearNote]
  highlights=[chip('中文期刊文献',m('cnki_paper'),'条'),chip('国自然资助论文',m('nsfc_paper'),'篇'),chip('基金项目',m('nsfc_fund'),'项','fund'),chip('技术主题',topics,'项')]
  add('中文期刊文献',m('cnki_paper'),'条');add('国自然资助论文',m('nsfc_paper'),'篇');if(span&&span!=='—')add('时间范围',span,'',true);add('技术主题',topics,'项');add('作者信息',field(sourceViews.value.cnki_paper,'作者'),'条')
 }else if(type.value==='fund'){
  tag='领域数据 · 基础研究资助';title='国自然基金项目'
  desc=`人工智能相关国自然基金项目 ${fmt(a?.total??m('nsfc_fund'))} 项，按项目目录计数，保留批准号、依托单位与项目负责人。`
  bullets=[span!=='—'?`批准年份覆盖 ${span}`:'',yearNote].filter(Boolean)
  highlights=[chip('基金项目',a?.total??m('nsfc_fund'),'项'),chip('资助论文',m('nsfc_paper'),'篇','paper'),chip('技术主题',topics,'项'),chip('含批准号',field(a,'批准号'),'项')]
 }else if(type.value==='patent'){
  tag='领域数据 · 技术创新';title='专利公开记录'
  desc=`人工智能领域专利公开候选 ${fmt(a?.total??m('legacy_patent'))} 条，保留申请号、申请人与 IPC 分类。本页为领域候选，不是全库专利库存。`
  bullets=[field(a,'专利引证')!=null?`含专利引文记录 ${fmt(field(a,'专利引证'))} 条`:'',yearNote].filter(Boolean)
  highlights=[chip('专利公开候选',a?.total??m('legacy_patent'),'条'),chip('软件著作权',m('legacy_software'),'条','software'),chip('技术主题',topics,'项'),chip('专利引文',field(a,'专利引证'),'条')]
 }else if(type.value==='software'){
  tag='领域数据 · 软件著作权';title='软件著作权'
  desc=`软件著作权登记候选 ${fmt(a?.total??m('legacy_software'))} 条，保留登记单位与工商来源标识。`
  bullets=[span!=='—'?`登记年份覆盖 ${span}`:'',yearNote].filter(Boolean)
  highlights=[chip('软著登记',a?.total??m('legacy_software'),'条'),chip('专利公开候选',m('legacy_patent'),'条','patent'),chip('技术主题',topics,'项'),chip('登记单位',field(a,'登记单位'),'条')]
 }else if(type.value==='policy'){
  tag='领域数据 · 政策环境';title='政策与创新环境'
  desc=`政策文本按来源分列。${policyPresent.aiLabel} ${fmt(policyPresent.total)} 篇，为耀元人工智能／大模型政策累计来源收录量，尚未逐篇确认实质相关性；${policyPresent.legacyLabel} ${fmt(m('legacy_policy'))} 篇，与前者尚未跨来源去重，不能直接相加。`
  bullets=[`中央政策 ${fmt(policyPresent.central)} 篇，地方独立政策 ${fmt(policyPresent.local)} 篇`,`覆盖 ${fmt(policyPresent.regions)} 个省级地区`,'产业新闻与行业报告仍是历史规则候选数，并非全部原始资料数量']
  highlights=[chip(policyPresent.aiLabel,policyPresent.total,'篇'),chip(policyPresent.legacyLabel,m('legacy_policy'),'篇'),chip('产业新闻',m('legacy_news'),'条','news'),chip('行业报告',m('ai_report'),'份','report')]
 }else if(type.value==='news'){
  tag='领域数据 · 资讯动态';title='产业新闻'
  desc=`已汇聚 ${fmt(a?.total??m('legacy_news'))} 条产业新闻，保留来源与相关主体，可与政策文本、行业报告对照阅读。`
  bullets=[field(a,'来源')!=null?`含来源信息 ${fmt(field(a,'来源'))} 条`:'',field(a,'相关方')!=null?`含相关主体信息 ${fmt(field(a,'相关方'))} 条`:''].filter(Boolean)
  highlights=[chip('产业新闻',a?.total??m('legacy_news'),'条'),chip(policyPresent.aiLabel,m('ai_policy'),'篇','policy'),chip('行业报告',m('ai_report'),'份','report'),chip('技术主题',topics,'项')]
 }else if(type.value==='report'){
  tag='领域数据 · 行业研究';title='行业研究报告'
  desc=`行业报告 PDF ${fmt(a?.total??m('ai_report'))} 份，其中 AI 专题报告 ${fmt(rankCount(a,'AI专题报告'))} 份，跨行业报告 ${fmt(rankCount(a,'跨行业报告'))} 份。`
  bullets=['按文件内容归入专题或跨行业']
  highlights=[chip('行业报告',a?.total??m('ai_report'),'份'),chip(policyPresent.aiLabel,m('ai_policy'),'篇','policy'),chip('产业新闻',m('legacy_news'),'条','news'),chip('技术主题',topics,'项')]
 }else if(type.value==='company'){
  tag='领域数据 · 创新主体';title='人工智能企业'
  desc=`人工智能企业候选名录 ${fmt(a?.total??m('ai_company'))} 家，保留省份与工商来源标识。`
  bullets=[field(a,'省份')!=null?`含省份信息 ${fmt(field(a,'省份'))} 条`:'']
  highlights=[chip('企业名录',a?.total??m('ai_company'),'条'),chip('专利公开候选',m('legacy_patent'),'条','patent'),chip('软著登记',m('legacy_software'),'条','software'),chip('含省份信息',field(a,'省份'),'条')]
 }else{
  tag='领域数据 · 应用载体';title='产品与应用载体'
  desc=`产品候选记录 ${fmt(a?.total??m('legacy_product'))} 条，保留产品型号与厂商代码。`
  bullets=['当前为已接入的产品目录记录','厂商代码见下方列表']
  highlights=[chip('产品记录',a?.total??m('legacy_product'),'条'),chip('专利公开候选',m('legacy_patent'),'条','patent'),chip('企业名录',m('ai_company'),'家','company'),chip('含产品型号',field(a,'产品型号'),'条')]
 }
 if(type.value!=='paper'){
  add('数据总量',type.value==='policy'?policyPresent.total:(a?.total??m(p.primary)),p.unit);if(span&&span!=='—')add('时间范围',span,'',true)
  for(const k of kpis.value){if(tiles.length>=6)break;if(String(k.label).includes('候选')||k.label===p.year)continue;add(k.label,k.value,k.text?'':k.unit,!!k.text)}
 }
 highlights=highlights.filter(h=>h.value!=null&&h.value!=='')
 bullets=bullets.filter(Boolean)
 return {tag,title,desc,bullets,insight:['paper','fund','patent','software','news','report'].includes(type.value)?insight:'',highlights,strip:tiles.slice(0,6)}
})
</script>

<template>
 <div class="domain-page domain-v6" :style="{'--domain-tone':profile.color}">
  <div class="type-tabs" aria-label="数据类别"><button v-for="[id,label] in tabs" :key="id" :class="{active:type===id}" :aria-pressed="type===id" @click="selectType(id)"><span>{{label}}</span><small v-if="tabCount(id)">{{tabCount(id)}}</small></button></div>

  <div :key="type" class="pane-swap">
  <CurrentDomainInventory v-if="hasCurrent" :inventory="data.currentInventory" :type="type" :tone="profile.color"/>
  <section v-if="brief&&!hasCurrent" class="ai-data-hero" :style="{'--hero-color':profile.color}">
   <div class="ai-hero-main"><span class="ai-hero-tag">{{brief.tag}}</span><h3 class="ai-hero-title">{{brief.title}}</h3><p class="ai-hero-desc">{{brief.desc}}</p><ul v-if="brief.bullets.length" class="ai-hero-bullets"><li v-for="item in brief.bullets" :key="item">{{item}}</li></ul><p v-if="brief.insight" class="ai-hero-insight">{{brief.insight}}</p></div>
   <div class="ai-hero-highlights"><button v-for="h in brief.highlights" :key="h.label" type="button" class="ai-highlight" :class="{link:h.type&&h.type!==type}" @click="h.type&&h.type!==type&&selectType(h.type)"><strong><CountValue v-if="h.numeric" :value="h.value"/><span v-else>{{h.value}}</span><small v-if="h.hint">{{h.hint}}</small></strong><span>{{h.label}}</span></button></div>
  </section>
  <div v-if="brief?.strip?.length>=3&&!hasCurrent" class="ai-kpi-strip fit" :style="{'--n':brief.strip.length}"><article v-for="(k,i) in brief.strip" :key="k.label" :class="{lead:i===0}"><strong v-if="k.text" class="text">{{k.value}}</strong><strong v-else><CountValue v-if="k.value!=null" :value="Number(k.value)"/><span v-else>—</span><small v-if="k.unit">{{k.unit}}</small></strong><span>{{k.label}}</span></article></div>
  <div v-if="loading" class="domain-loading" role="status">正在读取{{profile.title}}…</div>
  <template v-else>
   <div v-if="sources.length>1&&!hasCurrent" class="domain-source-grid">
    <article v-for="s in sourceCards" :key="s.namespace" class="domain-source-card">
     <div class="domain-source-top"><h3>{{s.name}}</h3><span>领域候选</span></div>
     <div class="domain-source-total"><strong><CountValue v-if="s.total!=null" :value="s.total"/><span v-else>—</span></strong><span>条</span><small>{{s.years}}</small></div>
     <dl><div v-for="[label,value] in s.facts" :key="label"><dt>{{label}}</dt><dd>{{fmt(value)}}<small>条</small></dd></div></dl>
     <button class="text-button" @click="selectRecordSource(s.namespace,true)">浏览来源记录 →</button>
     <p v-if="s.error" class="notice error">{{s.error}} <button @click="loadAnalytics">重试</button></p>
    </article>
   </div>
   <div v-if="errors[namespace]&&sources.length<2" class="notice error">{{errors[namespace]}} <button @click="loadAnalytics">重试</button></div>
   <div v-if="kpis.length&&!brief" class="kpi-grid domain-kpis" :class="{'three-kpis':kpis.length===3}">
    <article v-for="(k,i) in kpis" :key="`${type}:${k.label}`" class="kpi" :style="{'--tone':colors[i%colors.length]}"><span>{{k.label}}</span><strong v-if="k.text" class="smaller">{{k.value}}</strong><strong v-else><CountValue v-if="k.value!=null" :value="k.value"/><span v-else>—</span><small>{{k.unit}}</small></strong><p v-if="k.detail">{{k.detail}}</p></article>
   </div>
   <div v-if="chartPanels.length" class="charts-grid equal domain-main-charts domain-chart-grid" :class="{'has-expanded':expandedChart}">
    <section v-for="p in chartPanels" :key="`${type}:${p.key}`" class="panel" :class="{'chart-expanded':expandedChart===p.key,'wide-chart':p.full}">
     <div class="panel-heading"><h3>{{p.title}}</h3><div class="chart-controls"><button class="chart-expand" :aria-label="`${expandedChart===p.key?'收起':'展开'}${p.title}`" @click="expandedChart=expandedChart===p.key?'':p.key">{{expandedChart===p.key?'收起':'展开'}}</button></div></div>
     <Chart :key="`${type}:${namespace}:${p.key}`" :option="p.option" :height="expandedChart===p.key?350:280" :label="p.title" @select="p.topic&&openTopic($event)"/>
     <p v-if="p.subtitle||p.topic" class="chart-note">{{p.subtitle}}<span v-if="p.topic"> · 点击查看演进</span></p>
    </section>
   </div>
   <section v-if="newsTopics.length" class="panel domain-topic-strip"><div class="panel-heading"><h3>新闻中的技术主题</h3><span>词表匹配</span></div><div class="domain-topic-chips"><button v-for="t in newsTopics" :key="t.id" @click="openTopic({name:t.name,data:{topicId:t.id}})"><span>{{t.name}}</span><b>{{fmt(t.count)}}</b></button></div></section>
   <section v-if="type==='product'&&analytics?.ranking?.items?.length" class="panel domain-product-manufacturers"><div class="panel-heading"><h3>厂商标识与产品记录</h3></div><div v-for="r in analytics.ranking.items" :key="r.name" class="domain-manufacturer-row"><span>厂商来源代码</span><code>{{r.name}}</code><b>{{fmt(r.count)}} 条产品记录</b></div></section>
   <div v-if="!sources.length" class="notice">此类数据正在整理。</div>
  </template>

  <section v-if="type==='policy'" class="panel domain-policy-library">
   <div class="panel-heading"><h3>政策原文库</h3><span>中央与地方交付</span></div>
   <div class="summary-strip"><span><b>{{fmt(policyPresent.central)}}</b> 中央政策</span><span><b>{{fmt(policyPresent.local)}}</b> 地方独立政策</span><span><b>{{fmt(policyPresent.regions)}}</b> 省级地区</span></div>
   <div class="policy-chart-grid"><div><h4>地方政策公布年份</h4><Chart :option="policyTrend" :height="270" label="地方政策原文库公布年份分布"/></div><div><h4>地区政策记录 · 前 10 位</h4><Chart :option="policyRegions" :height="280" label="地方政策原文库地区记录分布"/></div></div>
  </section>

  <section ref="recordsSection" class="panel records-panel domain-records">
   <div class="panel-heading"><h3>{{profile.recordTitle}}{{hasCurrent?' · 来源记录检索':'检索'}}</h3><form class="search-box" @submit.prevent="search"><input v-model="recordQuery" placeholder="输入标题或关键词" aria-label="检索记录"/><button class="button" type="submit">检索</button></form></div>
   <div v-if="sources.length>1" class="domain-record-source-tabs" aria-label="检索记录来源"><button v-for="s in sources" :key="s.namespace" :class="{active:recordNamespace===s.namespace}" :aria-pressed="recordNamespace===s.namespace" @click="selectRecordSource(s.namespace)">{{sourceLabel(s.namespace)}}</button></div>
   <div v-if="recordsLoading" class="empty-state compact">正在读取记录…</div>
   <div v-else-if="recordError" class="notice error">{{recordError}} <button @click="loadRecords">重试</button></div>
   <div v-else-if="!rows.length" class="empty-state compact">暂无匹配记录。</div>
   <div v-else class="table-scroll"><table class="data-table record-table"><thead><tr><th>{{type==='paper'?'论文题名':type==='company'?'企业名称':type==='product'?'产品名称':'标题 / 名称'}}</th><th v-if="showYear">{{profile.year}}</th><th v-if="personColumn">{{profile.person}}</th><th>原文依据</th></tr></thead><tbody>
    <template v-for="(r,i) in rows" :key="r.id||i"><tr><td><a v-if="r.url" :href="safeUrl(r.url)" target="_blank" rel="noopener">{{r.title}} ↗</a><b v-else>{{r.title||'—'}}</b><small v-if="type==='patent'" class="table-sub">公开公告号 · {{r.source_id}}</small><small v-else-if="type==='company'" class="table-sub">来源编号 · {{r.source_id}}</small></td><td v-if="showYear">{{r.year||'—'}}</td><td v-if="personColumn">{{person(r)}}</td><td><button class="text-button" :aria-expanded="expanded===i" @click="expanded=expanded===i?null:i">{{expanded===i?'收起':'查看'}} {{r.evidence?.length||0}} 项</button></td></tr>
     <tr v-if="expanded===i" class="expanded-row"><td :colspan="recordColspan"><div v-for="(e,j) in (r.evidence||[]).slice(0,8)" :key="j" class="evidence-record"><div><b>{{e.keyword||'匹配依据'}}</b><span>{{fieldLabels[e.field]||'原文匹配'}}</span></div><p>{{e.snippet||'—'}}</p></div><p v-if="!r.evidence?.length">暂无可展示片段。</p></td></tr>
    </template>
   </tbody></table></div>
   <div class="pagination"><span>{{recordSource?.name}} · 共 {{fmt(total)}} 条<span v-if="total"> · 第 {{Math.floor(offset/10)+1}} 页</span></span><div><button :disabled="!offset||recordsLoading" @click="offset=Math.max(0,offset-10)">上一页</button><button :disabled="offset+10>=total||recordsLoading" @click="offset+=10">下一页</button></div></div>
  </section>
  </div>
 </div>
</template>
<style scoped>@media(max-width:700px){.domain-page.domain-v6>.type-tabs{flex-wrap:wrap}}</style>
