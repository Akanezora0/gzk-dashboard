<script setup>
import {ref,computed,watch,onMounted,nextTick} from 'vue'
import {useRoute} from 'vue-router'
import Chart from './Chart.vue'
import {api,fmt,colors,kindLabel,safeUrl,escape} from '../shared'
const props=defineProps({data:Object}),route=useRoute()
const chain=ref(route.query.chain||({fund_paper:'fund_paper',patent:'patent_tech',contribution:'paper_tech'})[route.query.tab]||'mixed'),scope=ref('ai'),limit=ref(20),summary=ref(null),summaryError=ref(''),graph=ref(null),loading=ref(false),error=ref(''),selected=ref(null),step=ref(0),chart=ref(null),graphShell=ref(null),allLabels=ref(false)
watch(()=>route.query.chain,v=>{if(v){chain.value=v;nextTick(()=>graphShell.value?.scrollIntoView({block:'start',behavior:'smooth'}))}})
function explore(id){chain.value=id;nextTick(()=>graphShell.value?.scrollIntoView({block:'start',behavior:'smooth'}))}
const chainTabs=[['mixed','多链关系'],['fund_paper','基金—论文—技术'],['paper_tech','论文—技术'],['patent_tech','专利—技术'],['fund_patent','基金—专利—技术'],['paper_network','论文间方法关联']]
const typeLabels={...kindLabel,fund:'基金项目',paper:'论文',patent:'专利',tech_point:'技术主题',technology:'技术主题',tech:'技术主题',institution:'机构',company:'企业'}
const typeColor={fund:'#AE0D28',paper:'#2877B0',patent:'#278771',tech_point:'#8B63AA',technology:'#8B63AA',tech:'#8B63AA',institution:'#D18A23',company:'#D18A23'}
const fieldLabels={proj_no:'批准号',proj_school:'依托单位',proj_author:'项目负责人',title:'标题',name:'名称',project_id:'项目编号',project_no:'项目编号',fund_id:'基金编号',paper_id:'论文标识',year:'年份',authors:'作者',institution:'机构',applicant:'申请主体',patent_number:'专利号',namespace:'来源类别',term_id:'技术编号',definition:'技术定义',source_row:'来源行',row_number:'来源行',source:'来源',source_file:'来源文件',topic_id:'技术编号',scope:'筛选范围',url:'原文链接',region:'机构地域'}
let sequence=0,summarySeq=0
async function fetchGraph(){const seq=++sequence;loading.value=true;error.value='';graph.value=null;selected.value=null;try{const d=await api('/api/llm/graph?'+new URLSearchParams({chain:chain.value,scope:scope.value,limit:String(limit.value)}));if(seq===sequence){graph.value=d;const n=d.nodes?.find(n=>n.id===route.query.node);if(n)selected.value={kind:'node',item:n}}}catch(e){if(seq===sequence)error.value=e.message}finally{if(seq===sequence)loading.value=false}}
async function fetchSummary(){const seq=++summarySeq;summary.value=null;try{const value=await api('/api/llm/chain-summary?scope='+scope.value);if(seq===summarySeq){summary.value=value;summaryError.value=''}}catch(e){if(seq===summarySeq)summaryError.value=e.message}}
watch([chain,scope,limit],fetchGraph)
watch(scope,fetchSummary)
onMounted(()=>{fetchSummary();fetchGraph()})
const nodeTypes=computed(()=>[...new Set((graph.value?.nodes||[]).map(n=>n.type))])
/* 证据图：力导向布局；节点按类型着色、按连接数调整大小，连线随来源类型着色并带弧度 */
const normType=t=>['tech','tech_point','technology'].includes(t)?'technology':t
const graphHeight=520
const short=(t,n)=>t.length>n?t.slice(0,n-1)+'…':t
const degree=computed(()=>{const d=new Map();(graph.value?.edges||[]).forEach(e=>{d.set(e.source,(d.get(e.source)||0)+1);d.set(e.target,(d.get(e.target)||0)+1)});return d})
const baseSize={technology:22,fund:15,paper:12,patent:12}
const graphOption=computed(()=>{
 const g=graph.value,n=g?.nodes?.length||0
 return {animationDurationUpdate:500,
  tooltip:{confine:true,backgroundColor:'#fff',borderColor:'#e4dcd8',padding:[8,12],textStyle:{color:'#2f2b2d',fontSize:13},extraCssText:'box-shadow:0 10px 28px -14px rgba(60,28,38,.35);max-width:320px;white-space:normal',formatter:p=>p.dataType==='edge'?`<b>${escape(p.data.label||'关系')}</b>`:`<span style="color:${typeColor[p.data.raw.type]||'#64748b'};font-size:12px">${escape(typeLabels[p.data.raw.type]||p.data.raw.type)}${p.data.raw.year?' · '+p.data.raw.year:''}</span><br/><b>${escape(p.data.fullLabel)}</b>`},
  series:[{type:'graph',layout:'force',roam:true,draggable:true,scaleLimit:{min:.4,max:3},zoom:n>60?.75:n>30?.88:1,labelLayout:{hideOverlap:true},
   left:40,right:40,top:56,bottom:30,
   force:{repulsion:n>60?150:n>30?190:300,edgeLength:[60,105],gravity:.14,friction:.55,layoutAnimation:true},
   data:(g?.nodes||[]).map(node=>{
    const t=normType(node.type),color=typeColor[node.type]||'#64748b',deg=degree.value.get(node.id)||1
    const size=(baseSize[t]||12)+Math.min(14,(deg-1)*(t==='technology'?3:2))
    const showLabel=t==='technology'||allLabels.value||chain.value==='paper_network'
    return {id:node.id,name:node.label,fullLabel:node.label,raw:node,symbolSize:size,
     itemStyle:{color:t==='technology'?{type:'radial',x:.35,y:.35,r:.75,colorStops:[{offset:0,color:'#a98bc4'},{offset:1,color:color}]}:color,borderColor:'#fff',borderWidth:t==='technology'?2.5:2,shadowBlur:t==='technology'?14:8,shadowColor:color+(t==='technology'?'66':'44')},
     label:{show:showLabel,position:'bottom',distance:5,color:t==='technology'?'#4b3a63':'#4a4448',fontSize:t==='technology'?12.5:11.5,fontWeight:t==='technology'?650:400,textBorderColor:'#fdfcfb',textBorderWidth:3,formatter:()=>short(node.label,t==='technology'?12:16)},
     emphasis:{scale:1.25,label:{show:true,color:'#232930',fontWeight:650,formatter:()=>short(node.label,24)}}}
   }),
   links:(g?.edges||[]).map(e=>{const src=(g.nodes.find(x=>x.id===e.source)||{}).type;const fundEdge=e.kind==='source_project_id';const color=fundEdge?'#a21535':(typeColor[src]||'#9aa3b2');return {...e,raw:e,lineStyle:{color,width:fundEdge?1.8:1.3,opacity:fundEdge?.6:.45,curveness:.2}}}),
   edgeSymbol:['none','arrow'],edgeSymbolSize:[0,6],
   emphasis:{focus:'adjacency',lineStyle:{width:2.6,opacity:.95}},blur:{itemStyle:{opacity:.15},lineStyle:{opacity:.05},label:{opacity:.2}}}]}
})
function onSelect(p){if(!p.data?.raw)return;selected.value=p.dataType==='edge'?{kind:'edge',item:p.data.raw}:{kind:'node',item:p.data.raw}}
const neighbors=computed(()=>selected.value?.kind==='node'?(graph.value?.edges||[]).filter(e=>e.source===selected.value.item.id||e.target===selected.value.item.id):[])
const nodeName=id=>graph.value?.nodes?.find(n=>n.id===id)?.label||id
const selectedFields=computed(()=>selected.value?.kind==='node'?Object.entries(selected.value.item.fields||{}).filter(([k,v])=>['批准号','依托单位','负责人','作者','机构','DOI','申请号','主IPC分类号','申请人','论文','作者（节选）','论文署名机构','技术组','技术编号','批准年','申请年','proj_no','proj_school','proj_author'].includes(k)&&v!==null&&v!==''&&v!==undefined):[])
const readableSource=s=>s&&!/^(?:\/|data\/|[A-Z]:\\)/.test(s)
function display(v){if(Array.isArray(v))return v.map(x=>typeof x==='object'?(x.name||x.label||JSON.stringify(x)):x).join(' · ');if(typeof v==='object')return JSON.stringify(v);return String(v)}
const selectedStep=computed(()=>summary.value?.pipeline?.[step.value])
const chainDescription=c=>({fund_paper:`项目编号关联成果论文 · ${fmt(c.triples||0)} 组基金—论文—技术组合`,paper_tech:'从论文标题、摘要连接技术主题',patent_tech:'从专利公开文本连接技术主题',fund_patent:'基金与专利成果关联研究'})[c.id]
const currentEdges=computed(()=>props.data.currentInventory?.counts.ai_fund_papers??props.data.study.contribution.source_metrics.fund_paper_edges)
const displayedChains=computed(()=>(summary.value?.chains||[]).map(c=>c.id==='fund_paper'?{...c,count:currentEdges.value}:c))
const counts=computed(()=>props.data.currentInventory?.counts||{})
const chainCount=id=>summary.value?.chains?.find(c=>c.id===id)?.count
const flowSteps=computed(()=>[
 {title:'多源汇聚',text:'基金项目、成果论文与专利汇入研究底座，保留来源与时间。',stats:[{v:fmt(counts.value.ai_funds),u:'AI 基金项目'},{v:counts.value.ai_papers?(counts.value.ai_papers/1e4).toFixed(1)+'万':'—',u:'AI 论文'},{v:counts.value.ai_patents?(counts.value.ai_patents/1e4).toFixed(1)+'万':'—',u:'AI 专利'}]},
 {title:'直接映射',text:'以原始项目编号连接基金与成果论文，形成资助关联。',stats:[{v:fmt(currentEdges.value),u:'基金—论文资助关联',big:true,chain:'fund_paper'}]},
 {title:'技术识别',text:'从题名、摘要及公开文本识别技术内容，连接到共同技术词表。',stats:[{v:fmt(chainCount('paper_tech')),u:'论文—技术',chain:'paper_tech'},{v:fmt(chainCount('patent_tech')),u:'专利—技术',chain:'patent_tech'}]},
 {title:'核对与汇流',text:'核对实体与原文依据，让多条成果链在共同技术主题中交汇。',stats:[{v:'交互证据图',u:'查看多链关系 ↓',chain:'mixed',link:true}]},
 {title:'贡献研究',text:'结合成果、引用与技术覆盖，研究基金的支撑范围与影响。',stats:[{v:'基金贡献度',u:'投入与产出 →',to:{query:{domain:'ai',module:'investment',analysis:'contribution'}},link:true}]}])
const processSteps=computed(()=>[
 {title:'多源汇聚',text:'基金项目、成果论文与专利资料汇入研究底座，保留来源与时间。',sourceLabel:'成果来源',source:'基金 · 论文 · 专利'},
 {title:'直接映射',text:'以原始项目编号连接基金与成果论文，形成资助关联。',sourceLabel:'已建关系',source:fmt(currentEdges.value)+' 条资助关联'},
 {title:'技术识别',text:'从题名、摘要及公开文本识别技术内容，形成主题候选关联。',sourceLabel:'识别依据',source:'共同词表 · 原文片段'},
 {title:'核对与汇流',text:'核对实体和文本依据，让多条成果链在共同技术主题中交汇。',sourceLabel:'探索入口',source:'交互证据图'},
 {title:'贡献研究',text:'结合成果、技术覆盖与引用，研究基金支撑范围及技术影响。',sourceLabel:'分析维度',source:'支撑范围 · 影响力度'}])
const pipelineDescriptions=['依据技术词典界定主题、关键词与研究范围。','按来源整理成果记录，归并标识并保留原始依据。','以项目编号连接基金与论文，以技术词表连接论文和专利。','核对原始文本、发表时间及署名信息，建立可追溯的关系。','沿技术脉络组织成果，联接企业、产品与政策研究。']
async function fullScreen(){if(!document.fullscreenElement)await graphShell.value?.requestFullscreen?.();else await document.exitFullscreen?.();await nextTick();chart.value?.resize()}
const activeTitle=computed(()=>chainTabs.find(c=>c[0]===chain.value)?.[1]||chain.value)
const scopeLabel=computed(()=>({llm:'LLM 明确命中',ai:'AI 宽口径',context:'前史 / 语境关联'})[scope.value])
</script>
<template><div class="evidence-v2">
<div v-if="summaryError" class="notice error">{{summaryError}} <button @click="fetchSummary">重试</button></div>
<section class="ev-flow">
 <header><h3>证据构建流程</h3><span>从多源成果到基金贡献研究</span></header>
 <ol>
  <li v-for="(f,i) in flowSteps" :key="f.title">
   <div class="ev-step-head"><b>{{String(i+1).padStart(2,'0')}}</b><h4>{{f.title}}</h4></div>
   <p>{{f.text}}</p>
  </li>
 </ol>
</section>
<section ref="graphShell" class="ev-graph">
 <header class="ev-graph-head">
  <div><h3>交互证据图</h3><p>{{graph?.meta?.scope_label||'人工智能 · 关系样本'}} · {{graph?.meta?.nodes??0}} 个节点 · {{graph?.meta?.edges??0}} 条关系</p></div>
  <div class="ev-graph-actions"><button @click="allLabels=!allLabels">{{allLabels?'收起标签':'显示全部标签'}}</button><button @click="chart?.reset()">重置视图</button><button @click="fullScreen">全屏</button></div>
 </header>
 <nav class="ev-chains" role="tablist" aria-label="证据链类型">
  <button v-for="[id,label] in chainTabs" :key="id" role="tab" :aria-selected="chain===id" :class="{active:chain===id,pending:id==='fund_patent'}" @click="chain=id">{{label}}<small v-if="id==='fund_patent'">待补充</small></button>
 </nav>
 <div class="ev-graph-body">
  <div class="ev-canvas">
   <div v-if="graph?.nodes?.length" class="ev-legend"><span v-for="t in nodeTypes" :key="t"><i :class="{big:normType(t)==='technology'}" :style="{'--c':typeColor[t]||'#64748b'}"></i>{{typeLabels[t]||t}}</span><span class="ev-legend-edge"><i class="line red"></i>项目编号资助关系</span><span class="ev-legend-edge"><i class="line"></i>原文识别关系</span></div>
   <div v-if="loading" class="ev-empty"><span class="ev-spin"></span>正在读取 {{activeTitle}}…</div>
   <div v-else-if="error" class="ev-empty"><p>{{error}}</p><button class="button" @click="fetchGraph">重试</button></div>
   <template v-else-if="graph?.nodes?.length"><Chart ref="chart" :option="graphOption" :height="graphHeight" @select="onSelect"/></template>
   <div v-else class="ev-empty pending"><svg viewBox="0 0 120 60" aria-hidden="true"><circle cx="16" cy="30" r="7"/><circle cx="60" cy="14" r="7"/><circle cx="60" cy="46" r="7"/><rect x="88" y="21" width="28" height="18" rx="4"/><path d="M23 30 53 15M23 30 53 45M67 14 88 28M67 46 88 32"/></svg><b>{{activeTitle}}关联整理中</b><p v-if="chain==='fund_patent'">以基金项目编号、负责人与专利申请人、发明人对应，建立基金—专利—技术三段链路。</p><p v-else>该链路的样本关系正在补充。</p></div>
   <p class="ev-hint">悬停查看名称 · 滚轮缩放 · 点击节点或连线查看原文依据</p>
  </div>
  <aside class="ev-inspector">
   <template v-if="selected">
    <div class="ev-insp-top"><span :style="{'--c':selected.kind==='node'?(typeColor[selected.item.type]||'#64748b'):'#a21535'}">{{selected.kind==='node'?(typeLabels[selected.item.type]||selected.item.type):'关系依据'}}</span><button @click="selected=null" aria-label="关闭详情">×</button></div>
    <h4>{{selected.item.label}}</h4>
    <template v-if="selected.kind==='node'">
     <dl><template v-if="selected.item.year"><dt>年份</dt><dd>{{selected.item.year}}</dd></template><template v-if="readableSource(selected.item.source)"><dt>来源</dt><dd>{{selected.item.source}}</dd></template><template v-for="[k,v] in selectedFields" :key="k"><dt>{{fieldLabels[k]||k}}</dt><dd>{{display(v)}}</dd></template><template v-if="selected.item.url"><dt>原文</dt><dd><a :href="safeUrl(selected.item.url)" target="_blank" rel="noopener">查看原文 ↗</a></dd></template></dl>
     <h5 v-if="neighbors.length">相邻关系 · {{neighbors.length}}</h5>
     <button v-for="e in neighbors.slice(0,10)" :key="e.id" class="ev-edge" @click="selected={kind:'edge',item:e}"><span>{{e.label}}</span><small>{{nodeName(e.source===selected.item.id?e.target:e.source)}}</small></button>
    </template>
    <template v-else>
     <div class="ev-pair"><span>{{nodeName(selected.item.source)}}</span><i>↓</i><span>{{nodeName(selected.item.target)}}</span></div>
     <dl><dt>核对状态</dt><dd>{{({snippet_reviewed:'题名 / 原文片段已核对',rule_candidate:'关键词规则识别',source_link:'来源项目编号关联',primary_source_checked_demo_seed:'代表论文原文已核对'})[selected.item.status]||selected.item.status}}</dd></dl>
     <div v-for="(e,i) in selected.item.evidence||[]" :key="i" class="ev-quote"><strong>{{fieldLabels[e.field]||e.field||'原文依据'}}<em v-if="e.keyword">{{e.keyword}}</em></strong><p>{{e.snippet||'原文依据'}}</p><a v-if="e.url" :href="safeUrl(e.url)" target="_blank" rel="noopener">查看依据原文 ↗</a></div>
    </template>
   </template>
   <template v-else>
    <h4 class="ev-insp-title">节点与关系详情</h4>
    <p class="ev-insp-lead">点击图中的节点或连线，查看来源、匹配字段与原文片段。</p>
    <ul class="ev-insp-tips"><li><b>基金项目</b>来自 NSFC 项目原件，以项目编号连接成果论文</li><li><b>论文 / 专利</b>从题名、摘要与公开文本识别技术主题</li><li><b>技术主题</b>沿用人工智能共同技术词表</li></ul>
   </template>
  </aside>
 </div>
</section>
</div></template>