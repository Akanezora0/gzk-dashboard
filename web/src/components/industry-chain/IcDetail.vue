<script setup>
/* 产业链分析 · 详情抽屉：技术大类、技术点、专利、经济指标、基金编号、产品版本及名录外主体（企业、产品沿用领域数据的抽屉） */
import {ref,computed,watch} from 'vue'
import {useSurface} from '../../helpers/useSurface'
import {safeUrl} from '../../shared'
import {arr,fmtN,companyExtra,companyValue,metricRows,compactValue,period,metricTitle,sourcesOf,recentRows} from '../../helpers/industryChain.js'
const props=defineProps({open:Object,atlas:Object,index:Object,evolution:Object,shortName:Function})
const emit=defineEmits(['close','open'])
const surface=ref(null)
useSurface(computed(()=>!!props.open),{element:surface,close:()=>emit('close'),modal:true})
const extra=ref(null),econ=ref(null)
const o=computed(()=>props.open||{})
const techMap=computed(()=>props.atlas?.techMap||new Map())
watch(()=>props.open,async v=>{
 extra.value=null;econ.value=null
 if(!v)return
 if(v.kind==='patents'||v.kind==='company')extra.value=await companyExtra(v.id)||{patents:[],related:[]}
 if(v.kind==='metrics'||v.kind==='company'){const c=company.value;const pack=await companyValue(v.id);econ.value=c?recentRows(metricRows(c,pack)):[]}
},{immediate:true})
const company=computed(()=>{const id=o.value.id;if(!id)return null;const a=props.atlas?.companies?.[id],i=props.index?.companies.get(id);return a||i?{id,name:a?.name||i?.name,category:a?.category||i?.category,labeledPatents:a?.coverage?.labeledPatents??i?.labeledPatents,jobs:a?.coverage?.jobsDeduplicated??i?.jobs,revenueSeries:a?.revenueSeries,productIds:i?.productIds||a?.productIds||[]}:{id,name:props.shortName(id)}})
const cat=computed(()=>o.value.kind==='category'?props.atlas.categories[o.value.index]:null)
const catTechs=computed(()=>cat.value?props.atlas.technologies.filter(t=>t.level1===cat.value.name):[])
const tech=computed(()=>o.value.kind==='tech'?techMap.value.get(o.value.id):null)
const techProducts=computed(()=>tech.value&&props.index?(props.index.byTech.get(tech.value.id)||[]):[])
const series=computed(()=>o.value.kind==='version'?arr(props.evolution?.series).find(s=>s.id===o.value.series):null)
const version=computed(()=>series.value?arr(series.value.versions).find(v=>v.id===o.value.version):null)
const versionPatents=computed(()=>{if(!series.value||!version.value)return [];const ids=new Set(arr(version.value.technologies).map(t=>t.technologyId)),seen=new Set();return arr(series.value.patentLinks).filter(p=>arr(p.technologyIds).some(id=>ids.has(id))).filter(p=>{const k=p.patentKey||p.applicationNumber;if(seen.has(k))return false;seen.add(k);return true})})
const evoSource=id=>props.evolution?.sources?.[id]
const funding=computed(()=>o.value.kind==='funding'?arr(props.atlas?.funding).filter(f=>!o.value.id||f.companyId===o.value.id):[])
const row=computed(()=>o.value.kind==='metric'?o.value.row:null)
const relation=r=>({related_entity:'关联企业',segment:'业务分部',product:'产品口径',group:'集团口径'}[r]||'')
const title=computed(()=>{const k=o.value.kind;return k==='category'?cat.value?.name:k==='tech'?tech.value?.name:k==='version'?version.value?.label:k==='metric'?metricTitle(row.value):k==='patent'?o.value.patent?.title:k==='funding'?(o.value.id?props.shortName(o.value.id)+' · 基金编号':'国家自然科学基金'):company.value?.name})
const kindName={category:'技术大类',tech:'技术点',version:'产品版本',metric:'经济指标',metrics:'经济指标',patent:'专利',patents:'相关专利',funding:'科学基金',company:'企业与机构'}
const matchName=m=>({direct:'直接对应',semantic:'语义对应',nearest:'近似归类'}[m]||'技术关联')
const patentOpen=ref(null)
</script>
<template>
 <Teleport to="body"><div v-if="open" class="ind-overlay" @click.self="emit('close')"><aside ref="surface" class="ind-drawer ic-drawer" role="dialog" aria-modal="true" :aria-label="title||'详情'">
  <header class="ind-dr-h"><div><span>{{kindName[o.kind]}}</span><h4>{{title||'正在读取…'}}</h4></div><button aria-label="关闭" @click="emit('close')">×</button></header>

  <template v-if="cat">
   <p class="ind-dr-p">{{cat.description}}</p>
   <p class="ind-dr-k">技术点 · {{catTechs.length}} 项</p>
   <button v-for="t in catTechs" :key="t.id" class="ind-dr-item" @click="emit('open',{kind:'tech',id:t.id})"><b>{{t.name}}</b><small>{{t.level2}} · {{fmtN(t.products)}} 项产品 · {{fmtN(t.patents)}} 件专利</small></button>
  </template>

  <template v-else-if="tech">
   <div class="ind-chips"><span class="lead">{{tech.level1}}</span><span>{{tech.level2}}</span></div>
   <p class="ind-dr-p">{{tech.definition}}</p>
   <button class="ind-dr-item" @click="emit('open',{kind:'analyse',id:tech.id})"><b>作为分析对象查看产品、经营与链路 →</b></button>
   <div class="ind-dr-stats"><div><strong>{{fmtN(tech.products)}}</strong><span>关联产品 · 项</span></div><div><strong>{{fmtN(tech.companies)}}</strong><span>提供主体 · 家</span></div><div><strong>{{fmtN(tech.patents)}}</strong><span>匹配专利 · 件</span></div></div>
   <p class="ind-dr-k">关联产品</p>
   <p v-if="!index" class="ind-dr-p">正在读取产品目录…</p>
   <button v-for="p in techProducts.slice(0,30)" :key="p.id" class="ind-dr-item" @click="emit('open',{kind:'product',id:p.id})"><b>{{p.name}}</b><small>{{p.companyIds.map(shortName).join(' / ')}}</small></button>
   <p v-if="techProducts.length>30" class="ind-dr-note">展示前 30 项，共 {{fmtN(techProducts.length)}} 项</p>
  </template>

  <template v-else-if="version">
   <p class="ind-dr-p">{{shortName(series.companyIds?.[0])}} · {{series.name}}　{{version.releaseDate}}</p>
   <p v-if="series.summary" class="ind-dr-p">{{series.summary}}</p>
   <p class="ind-dr-k">版本能力</p>
   <ul class="ic-dr-list"><li v-for="(c,i) in arr(version.capabilities)" :key="i">{{c.text}}</li></ul>
   <template v-if="arr(version.technologies).length"><p class="ind-dr-k">技术点</p>
    <div v-for="t in version.technologies" :key="t.technologyId" class="ic-dr-tech"><button @click="emit('open',{kind:'tech',id:t.technologyId})">{{techMap.get(t.technologyId)?.name||t.name}} ↗</button><p>{{t.mechanism||t.evidence}}</p></div>
   </template>
   <template v-if="versionPatents.length"><p class="ind-dr-k">相关专利</p>
    <button v-for="p in versionPatents" :key="p.patentKey||p.applicationNumber" class="ind-dr-item" @click="emit('open',{kind:'patent',patent:p})"><b>{{p.title}}</b><small>{{p.applicationNumber}} · {{p.applicationDate}} · {{matchName(p.matchType)}}</small></button>
   </template>
   <template v-if="arr(version.sourceIds).length"><p class="ind-dr-k">版本来源</p>
    <a v-for="id in version.sourceIds.filter(evoSource)" :key="id" class="ind-dr-src" :href="safeUrl(evoSource(id).url)" target="_blank" rel="noopener"><b>{{evoSource(id).title}} ↗</b><small v-if="evoSource(id).date||evoSource(id).location">{{[evoSource(id).date,evoSource(id).location].filter(Boolean).join(' · ')}}</small></a>
   </template>
   <button v-for="id in arr(version.productIds)" :key="id" class="ind-dr-item" @click="emit('open',{kind:'product',id})"><b>产品资料 →</b><small>{{id}}</small></button>
  </template>

  <template v-else-if="o.kind==='patent'">
   <dl class="ind-facts"><div><dt>申请号</dt><dd>{{o.patent.applicationNumber||'—'}}</dd></div><div><dt>公开号</dt><dd>{{o.patent.publicationNumber||'—'}}</dd></div><div><dt>申请日期</dt><dd>{{o.patent.applicationDate||'—'}}</dd></div><div><dt>公开日期</dt><dd>{{o.patent.publicationDate||'—'}}</dd></div><div class="full"><dt>申请人</dt><dd>{{o.patent.applicants||(o.patent.companyId&&shortName(o.patent.companyId))||'—'}}</dd></div></dl>
   <div class="ind-chips"><span class="lead">{{matchName(o.patent.matchType)}}</span><span v-for="id in arr(o.patent.technologyIds)" :key="id">{{techMap.get(id)?.name||id}}</span></div>
   <p v-if="o.patent.abstract" class="ind-dr-p">{{o.patent.abstract}}</p>
   <button v-if="o.patent.companyId" class="ind-dr-item" @click="emit('open',{kind:'company',id:o.patent.companyId})"><b>{{shortName(o.patent.companyId)}} →</b><small>专利归集主体</small></button>
  </template>

  <template v-else-if="o.kind==='patents'">
   <div class="ind-dr-stats two"><div><strong>{{fmtN(company?.labeledPatents)}}</strong><span>技术挂钩专利 · 件</span></div><div><strong>{{fmtN(extra?.patents?.length)}}</strong><span>专利样例 · 件</span></div></div>
   <p class="ind-dr-k">专利样例</p>
   <p v-if="!extra" class="ind-dr-p">正在读取…</p>
   <template v-for="(p,i) in extra?.patents||[]" :key="p.patentKey||i">
    <button class="ind-dr-item" :aria-expanded="patentOpen===i" @click="patentOpen=patentOpen===i?null:i"><b>{{p.title}}</b><small>{{p.applicationNumber}} · {{p.applicationDate}}</small></button>
    <div v-if="patentOpen===i" class="ind-dr-patent"><dl class="ind-facts"><div><dt>公开号</dt><dd>{{p.publicationNumber||'—'}}</dd></div><div><dt>公开日期</dt><dd>{{p.publicationDate||'—'}}</dd></div><div class="full"><dt>申请人</dt><dd>{{p.applicants||'—'}}</dd></div></dl><p v-if="p.abstract" class="ind-dr-p">{{p.abstract}}</p></div>
   </template>
   <button class="ind-dr-item" @click="emit('open',{kind:'company',id:o.id})"><b>企业档案 →</b><small>{{company?.name}}</small></button>
  </template>

  <template v-else-if="o.kind==='metrics'">
   <p v-if="!econ" class="ind-dr-p">正在读取经济指标…</p>
   <p v-else-if="!econ.length" class="ind-dr-p">暂无经济指标。</p>
   <button v-for="r in econ||[]" :key="r.id+r.period" class="ind-dr-item ic-dr-metric" @click="emit('open',{kind:'metric',row:r})"><span><b>{{metricTitle(r)}}</b><small>{{period(r)}}<template v-if="r.reportingEntity"> · {{r.reportingEntity}}</template></small></span><strong>{{compactValue(r)}}</strong></button>
  </template>

  <template v-else-if="row">
   <div class="ic-dr-value"><strong>{{compactValue(row)}}</strong><span>{{period(row)}}</span></div>
   <dl class="ind-facts"><div class="full"><dt>披露主体</dt><dd>{{row.reportingEntity||shortName(row.companyId)}}</dd></div><div v-if="row.scope||row.reportingScope" class="full"><dt>披露范围</dt><dd>{{row.reportingScope||row.scope}}</dd></div><div v-if="relation(row.entityRelation)"><dt>主体关系</dt><dd>{{relation(row.entityRelation)}}</dd></div><div v-if="row.category"><dt>指标类别</dt><dd>{{row.category}}</dd></div></dl>
   <template v-if="sourcesOf(row).length"><p class="ind-dr-k">资料来源</p><a v-for="(s,i) in sourcesOf(row)" :key="i" class="ind-dr-src" :href="safeUrl(s.url)" target="_blank" rel="noopener"><b>{{s.title||'公开资料'}} ↗</b><small v-if="s.location||s.date">{{[s.date,s.location].filter(Boolean).join(' · ')}}</small></a></template>
   <button v-if="row.companyId" class="ind-dr-item" @click="emit('open',{kind:'company',id:row.companyId})"><b>{{shortName(row.companyId)}} →</b><small>企业档案</small></button>
  </template>

  <template v-else-if="o.kind==='funding'">
   <p v-if="!o.id" class="ind-dr-p">依据论文致谢中的基金编号与作者署名，把国家自然科学基金支持的研究关联到企业与机构。</p>
   <section v-for="f in funding" :key="f.companyId" class="ic-dr-fund">
    <p class="ind-dr-k">{{f.shortName}}<template v-if="arr(f.projectNumbers).length"> · {{f.projectNumbers.join('、')}}</template></p>
    <div v-for="p in arr(f.papers)" :key="p.paper" class="ind-dr-item"><b>{{p.paper}}<template v-if="p.year"> · {{p.year}}</template></b><small v-if="arr(p.projectNumbers).length">基金编号 {{p.projectNumbers.join('、')}}</small><small v-if="p.relationship">{{p.relationship}}</small><small v-if="p.quote">致谢原文：{{p.quote}}</small><a v-if="p.sourceUrl" :href="safeUrl(p.sourceUrl)" target="_blank" rel="noopener">论文原文<template v-if="p.location"> · {{p.location}}</template> ↗</a></div>
   </section>
  </template>

  <template v-else-if="o.kind==='company'">
   <div class="ind-dr-stats"><div><strong>{{fmtN(company?.productIds?.length)}}</strong><span>产品与服务 · 项</span></div><div><strong>{{fmtN(company?.labeledPatents)}}</strong><span>技术挂钩专利 · 件</span></div><div><strong>{{fmtN(company?.jobs)}}</strong><span>招聘记录 · 去重</span></div></div>
   <template v-if="company?.productIds?.length"><p class="ind-dr-k">产品与服务</p><button v-for="id in company.productIds.slice(0,20)" :key="id" class="ind-dr-item" @click="emit('open',{kind:'product',id})"><b>{{index?.productMap.get(id)?.name||id}}</b></button></template>
   <template v-if="econ?.length"><p class="ind-dr-k">经济指标</p><button v-for="r in econ.slice(0,8)" :key="r.id+r.period" class="ind-dr-item ic-dr-metric" @click="emit('open',{kind:'metric',row:r})"><span><b>{{metricTitle(r)}}</b><small>{{period(r)}}</small></span><strong>{{compactValue(r)}}</strong></button></template>
   <template v-if="extra?.related?.length"><p class="ind-dr-k">关联企业</p><div v-for="r in extra.related" :key="r.name" class="ind-dr-tech"><b>{{r.name}}</b><small>{{r.relation}}</small></div></template>
  </template>
 </aside></div></Teleport>
</template>
