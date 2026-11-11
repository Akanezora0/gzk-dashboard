<script setup>
import ChainRelations from './ChainRelations.vue'
import {ref,computed,watch,onMounted,nextTick} from 'vue'
import {useRoute} from 'vue-router'
import EvidenceGraph from './EvidenceGraph.vue'
import {loadEvidenceGraphs,selectEvidenceGraph,evidenceSummary} from '../evidenceGraphData'
import {api,fmt,colors,kindLabel,safeUrl,escape} from '../shared'
const props=defineProps({data:Object,dataset:Object}),route=useRoute()
const chain=ref(route.query.chain||({fund_paper:'fund_paper',patent:'patent_tech',contribution:'paper_tech'})[route.query.tab]||'mixed'),scope=ref('ai'),limit=ref(20),summary=ref(null),summaryError=ref(''),graph=ref(null),loading=ref(false),error=ref(''),selected=ref(null),step=ref(0),chart=ref(null),graphShell=ref(null),allLabels=ref(false)
watch(()=>route.query.chain,v=>{if(v){chain.value=v;nextTick(()=>graphShell.value?.scrollIntoView({block:'start',behavior:'smooth'}))}})
function explore(id){chain.value=id;nextTick(()=>graphShell.value?.scrollIntoView({block:'start',behavior:'smooth'}))}
if(chain.value==='paper_network') chain.value='mixed'
const chainTabs=[['mixed','多链关系'],['fund_paper','基金—论文—技术'],['paper_tech','论文—技术'],['patent_tech','专利—技术'],['fund_patent','基金—专利—技术'],['tech_product','技术—产品—企业'],['company_economy','企业—经济指标']]
// 产业链证据：逐条关系数据接入前以占位展示
const industryTabs={tech_product:{title:'技术—产品—企业',text:'6,212 项产品经 66 个技术点与 2,702 家企业相连，逐条关系依据接入后在此展开。'},company_economy:{title:'企业—经济指标',text:'1,303 家企业的 11,769 条经济指标记录，企业与指标、披露来源的关系图接入后在此展开。'}}
const industryTab=computed(()=>industryTabs[chain.value]||null)
const typeLabels={...kindLabel,fund:'基金项目',paper:'论文',patent:'专利',tech_point:'技术主题',technology:'技术主题',tech:'技术主题',institution:'机构',company:'企业'}
const typeColor={fund:'#a21535',paper:'#2c64a0',patent:'#23806e',tech_point:'#8B63AA',technology:'#8B63AA',tech:'#8B63AA',institution:'#D18A23',company:'#D18A23'}
const fieldLabels={proj_no:'批准号',proj_school:'依托单位',proj_author:'项目负责人',title:'标题',name:'名称',project_id:'项目编号',project_no:'项目编号',fund_id:'基金编号',paper_id:'论文标识',year:'年份',authors:'作者',institution:'机构',applicant:'申请主体',patent_number:'专利号',namespace:'来源类别',term_id:'技术编号',definition:'技术定义',source_row:'来源行',row_number:'来源行',source:'来源',abstract:'摘要',first_claim:'独立权利要求',evidence_excerpt:'原文摘录',review_summary:'既有原文核验摘要',source_file:'来源文件',topic_id:'技术编号',scope:'筛选范围',url:'原文链接',region:'机构地域'}
const category=ref('all'),nodeBudget=ref(90),poolOffset=ref(0),graphBundle=ref(null)
const graphCategories=computed(()=>graphBundle.value?.categories||[])
const availableCategories=computed(()=>new Set(graphBundle.value?.graphs?.[chain.value]?.meta?.category_coverage||[]))
const canExpand=computed(()=>graph.value?.meta?.has_more&&nodeBudget.value<330)
function expandGraph(){nodeBudget.value=Math.min(330,nodeBudget.value+60)}
function nextSample(){poolOffset.value+=graph.value?.meta?.selected_bundles||1;nodeBudget.value=90}
function sourceDetails(e){const p=e.source_locator;if(!p)return '';if(Array.isArray(p))return p.map(v=>v.source_path||v.table||v.file||'').filter(Boolean).join(' · ');return [p.table,p.paper_id||p.application_id,p.location].filter(Boolean).join(' · ')}
let sequence=0,summarySeq=0
async function fetchGraph(){const seq=++sequence;if(industryTabs[chain.value]){graph.value=null;selected.value=null;loading.value=false;error.value='';return}loading.value=true;error.value='';graph.value=null;selected.value=null;try{
 let d
 if(scope.value==='ai'){
  const bundle=await loadEvidenceGraphs();if(seq!==sequence)return;graphBundle.value=bundle
  d=selectEvidenceGraph(bundle.graphs[chain.value],category.value,nodeBudget.value,poolOffset.value)
 }else d=await api('/api/llm/graph?'+new URLSearchParams({chain:chain.value,scope:scope.value,limit:String(limit.value)}))
 if(seq===sequence){graph.value=d;const n=d.nodes?.find(n=>n.id===route.query.node);if(n)selected.value={kind:'node',item:n}}
 }catch(e){if(seq===sequence)error.value=e.message}finally{if(seq===sequence)loading.value=false}}
async function fetchSummary(){const seq=++summarySeq;summary.value=null;try{const value=scope.value==='ai'?evidenceSummary(await loadEvidenceGraphs()):await api('/api/llm/chain-summary?scope='+scope.value);if(seq===summarySeq){summary.value=value;summaryError.value=''}}catch(e){if(seq===summarySeq)summaryError.value=e.message}}
watch([chain,scope],()=>{category.value='all';nodeBudget.value=90;poolOffset.value=0;fetchGraph()})
watch(category,()=>{nodeBudget.value=90;poolOffset.value=0;fetchGraph()})
watch([nodeBudget,limit,poolOffset],fetchGraph)
watch(scope,fetchSummary)
onMounted(()=>{fetchSummary();fetchGraph()})
const nodeTypes=computed(()=>[...new Set((graph.value?.nodes||[]).map(n=>n.type))])
const normType=t=>['tech','tech_point','technology'].includes(t)?'technology':t
function onSelect(p){if(!p.data?.raw)return;selected.value=p.dataType==='edge'?{kind:'edge',item:p.data.raw}:{kind:'node',item:p.data.raw}}
const neighbors=computed(()=>selected.value?.kind==='node'?(graph.value?.edges||[]).filter(e=>e.source===selected.value.item.id||e.target===selected.value.item.id):[])
const nodeName=id=>graph.value?.nodes?.find(n=>n.id===id)?.label||id
const selectedFields=computed(()=>selected.value?.kind==='node'?Object.entries(selected.value.item.fields||{}).filter(([k,v])=>['批准号','依托单位','负责人','作者','机构','DOI','申请号','主IPC分类号','申请人','论文','作者（节选）','论文署名机构','技术组','技术编号','批准年','申请年','proj_no','proj_school','proj_author','公开号','发明人','技术大类','身份核对'].includes(k)&&v!==null&&v!==''&&v!==undefined):[])
const readableSource=s=>s&&!/^(?:\/|data\/|[A-Z]:\\)/.test(s)
function display(v){if(typeof v==='string')v=({matched_existing_canonical_paper:'已对应论文统一标识',unmatched_preserved:'保留原文身份，尚未对应统一标识',ambiguous_identity_hold:'保留原文身份，统一标识有歧义'})[v]||v;if(Array.isArray(v))return v.map(x=>typeof x==='object'?(x.name||x.label||JSON.stringify(x)):x).join(' · ');if(typeof v==='object')return JSON.stringify(v);return String(v)}
const selectedStep=computed(()=>summary.value?.pipeline?.[step.value])
const chainDescription=c=>({fund_paper:`项目编号关联成果论文 · ${fmt(c.triples||0)} 组基金—论文—技术组合`,paper_tech:'从论文标题、摘要连接技术主题',patent_tech:'从专利公开文本连接技术主题',fund_patent:'基金与专利成果关联研究'})[c.id]
const currentEdges=computed(()=>props.data.currentInventory?.counts.ai_fund_papers??props.data.study.contribution.source_metrics.fund_paper_edges)
const displayedChains=computed(()=>(summary.value?.chains||[]).map(c=>c.id==='fund_paper'?{...c,count:currentEdges.value}:c))
const counts=computed(()=>props.data.currentInventory?.counts||{})
const chainCount=id=>summary.value?.chains?.find(c=>c.id===id)?.count
const processSteps=computed(()=>[
 {title:'多源汇聚',text:'基金项目、成果论文与专利资料汇入研究底座，保留来源与时间。',sourceLabel:'成果来源',source:'基金 · 论文 · 专利'},
 {title:'直接映射',text:'以原始项目编号连接基金与成果论文，形成资助关联。',sourceLabel:'已建关系',source:fmt(currentEdges.value)+' 条资助关联'},
 {title:'技术识别',text:'从题名、摘要及公开文本识别技术内容，形成主题候选关联。',sourceLabel:'识别依据',source:'共同词表 · 原文片段'},
 {title:'核对与汇流',text:'核对实体和文本依据，让多条成果链在共同技术主题中交汇。',sourceLabel:'探索入口',source:'交互证据图'},
 {title:'贡献研究',text:'结合成果、技术覆盖与引用，研究基金支撑范围及技术影响。',sourceLabel:'分析维度',source:'支撑范围 · 影响力度'}])
const pipelineDescriptions=['依据技术词典界定主题、关键词与研究范围。','按来源整理成果记录，归并标识并保留原始依据。','以项目编号连接基金与论文，以技术词表连接论文和专利。','核对原始文本、发表时间及署名信息，建立可追溯的关系。','沿技术脉络组织成果，联接企业、产品与政策研究。']
async function fullScreen(){if(!document.fullscreenElement)await graphShell.value?.requestFullscreen?.();else await document.exitFullscreen?.();await nextTick();setTimeout(()=>chart.value?.reset?.(),120)}
const activeTitle=computed(()=>chainTabs.find(c=>c[0]===chain.value)?.[1]||chain.value)
const scopeLabel=computed(()=>({llm:'LLM 明确命中',ai:'AI 宽口径',context:'前史 / 语境关联'})[scope.value])
</script>
<template><div class="evidence-v2">
<div v-if="summaryError" class="notice error">{{summaryError}} <button @click="fetchSummary">重试</button></div>
<ChainRelations v-if="dataset" :dataset="dataset" :inventory="data?.currentInventory"/>
<section ref="graphShell" class="ev-graph">
 <header class="ev-graph-head">
  <div><h3>交互证据图</h3></div>
  <div class="ev-graph-actions"><button @click="allLabels=!allLabels">{{allLabels?'收起标签':'显示全部标签'}}</button><button @click="chart?.reset()">重置视图</button><button @click="fullScreen">全屏</button></div>
 </header>
 <nav class="ev-chains" role="tablist" aria-label="证据链类型">
  <button v-for="[id,label] in chainTabs" :key="id" role="tab" :aria-selected="chain===id" :class="{active:chain===id}" @click="chain=id">{{label}}</button>
 </nav>
 <div v-if="scope==='ai'&&!industryTab" class="ev-filterbar">
  <div class="ev-category-filters" aria-label="按技术大类筛选">
   <button :class="{active:category==='all'}" :aria-pressed="category==='all'" @click="category='all'">全部技术</button>
   <button v-for="c in graphCategories" :key="c.id" :class="{active:category===c.id}" :aria-pressed="category===c.id" :disabled="!availableCategories.has(c.id)" @click="category=c.id">{{c.name}}</button>
  </div>
  <button v-if="canExpand" class="ev-expand" @click="expandGraph">展开更多</button>
  <button v-else-if="graph?.meta?.has_more" class="ev-expand" @click="nextSample">换一组</button>
  <button v-else-if="nodeBudget>90" class="ev-expand" @click="nodeBudget=90">收起</button>
 </div>
 <div class="ev-graph-body">
  <div class="ev-canvas">
   <div v-if="graph?.nodes?.length" class="ev-legend"><span v-for="t in nodeTypes" :key="t"><i :class="{multi:normType(t)==='technology'}" :style="{'--c':typeColor[t]||'#64748b'}"></i>{{normType(t)==='technology'?'技术主题（按大类着色）':(typeLabels[t]||t)}}</span><span v-if="graph.edges.some(e=>['source_project_id','registered_patent_outcome'].includes(e.kind))" class="ev-legend-edge"><i class="line red"></i>项目成果关联</span><span class="ev-legend-edge"><i class="line"></i>{{chain==='paper_network'?'原文确认使用':'技术主题 / 原文关系'}}</span></div>
   <div v-if="industryTab" class="ev-empty pending ev-industry"><svg viewBox="0 0 120 60" aria-hidden="true"><circle cx="16" cy="30" r="7"/><circle cx="60" cy="14" r="7"/><circle cx="60" cy="46" r="7"/><rect x="88" y="21" width="28" height="18" rx="4"/><path d="M23 30 53 15M23 30 53 45M67 14 88 28M67 46 88 32"/></svg><b>{{industryTab.title}}</b><p>{{industryTab.text}}</p><router-link class="text-button" :to="{path:'/data',query:{type:chain==='tech_product'?'product':'economy'}}">查看领域数据 →</router-link></div>
   <div v-else-if="loading" class="ev-empty"><span class="ev-spin"></span>正在读取 {{activeTitle}}…</div>
   <div v-else-if="error" class="ev-empty"><p>{{error}}</p><button class="button" @click="fetchGraph">重试</button></div>
   <template v-else-if="graph?.nodes?.length"><EvidenceGraph ref="chart" :graph="graph" :all-labels="allLabels" :height="540" :type-labels="typeLabels" :selected-id="selected?.kind==='node'?selected.item.id:null" @select="p=>selected=p"/></template>
   <div v-else class="ev-empty pending"><svg viewBox="0 0 120 60" aria-hidden="true"><circle cx="16" cy="30" r="7"/><circle cx="60" cy="14" r="7"/><circle cx="60" cy="46" r="7"/><rect x="88" y="21" width="28" height="18" rx="4"/><path d="M23 30 53 15M23 30 53 45M67 14 88 28M67 46 88 32"/></svg><b>当前筛选暂无关系</b><p>可切换技术大类或查看其他链路。</p></div>
   
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
     <dl><dt>核对状态</dt><dd>{{({snippet_reviewed:'题名 / 原文片段已核对',rule_candidate:'关键词规则识别',source_link:'项目成果登记 / 明示资助关联',registered_outcome_identity_match:'登记成果题名与发明人唯一对应申请',prior_review_local_text_sha256_verified:'既有原文核验 · 本地文本校验通过',prior_original_document_review_no_local_snapshot:'既有原文核验记录',primary_source_checked_demo_seed:'代表论文原文已核对'})[selected.item.status]||selected.item.status}}</dd></dl>
     <div v-for="(e,i) in selected.item.evidence||[]" :key="i" class="ev-quote"><strong>{{fieldLabels[e.field]||e.field||'原文依据'}}<em v-if="e.keyword">{{e.keyword}}</em></strong><p>{{e.snippet||'原文依据'}}</p><small v-if="e.source" class="ev-evidence-source">{{e.source}}<template v-if="sourceDetails(e)"> · {{sourceDetails(e)}}</template></small><a v-if="e.url" :href="safeUrl(e.url)" target="_blank" rel="noopener">查看依据原文 ↗</a></div>
    </template>
   </template>
   <template v-else>
    <h4 class="ev-insp-title">节点与关系详情</h4>
    <p class="ev-insp-lead">点击图中的节点或连线，查看来源、匹配字段与原文片段。</p>
    <ul class="ev-insp-tips"><li><b>基金项目</b>来自 NSFC 项目登记与明示资助记录</li><li><b>论文 / 专利</b>从题名、摘要与公开文本识别技术主题；专利成果按登记信息核对</li><li><b>技术主题</b>沿用人工智能共同技术词表，文本命中表示主题关联</li></ul>
   </template>
  </aside>
 </div>
</section>
</div></template>
<style scoped>
.ev-filterbar{display:flex;gap:12px;align-items:center;justify-content:space-between;padding:12px 22px;border-bottom:1px solid #eee8e5;background:#fdfbf9}
.ev-category-filters{display:flex;flex-wrap:wrap;gap:6px}
.ev-category-filters button,.ev-expand{border:1px solid #e7ded9;border-radius:4px;background:#fff;padding:5px 9px;color:#6c6066;font-size:12px;cursor:pointer}
.ev-category-filters button.active{background:#a21535;border-color:#a21535;color:#fff}
.ev-category-filters button:disabled{opacity:.4;cursor:default}
.ev-expand{white-space:nowrap;color:#a21535}
.ev-evidence-source{display:block;color:#82777c;font-size:11px;line-height:1.6;margin-bottom:6px;overflow-wrap:anywhere}
@media(max-width:720px){.ev-filterbar{padding:10px 12px;align-items:flex-start}}
</style>
