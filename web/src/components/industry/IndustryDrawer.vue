<script setup>
/* 领域数据 · 企业／产品／经济共用详情抽屉：企业档案（概况、产品、专利、经济指标）与产品详情 */
import {ref,computed,watch} from 'vue'
import {useSurface} from '../../helpers/useSurface'
import {useCompanies,useProducts,useEconomy,loadPatents,companyOf,roleName,metricName,amount} from '../../helpers/industryData'
import {fmt,safeUrl} from '../../shared'
// open: {kind:'company',id,tab?} | {kind:'product',id}
const props=defineProps({open:Object})
const emit=defineEmits(['close','open'])
const surface=ref(null)
useSurface(computed(()=>!!props.open),{element:surface,close:()=>emit('close'),modal:true})
const {data:C}=useCompanies(),{data:P}=useProducts(),{data:E}=useEconomy()
const tab=ref('profile'),patents=ref(null),patentOpen=ref(null)
const company=computed(()=>props.open?.kind==='company'&&C.value?companyOf(props.open.id):null)
const product=computed(()=>props.open?.kind==='product'&&P.value?P.value.byId.get(props.open.id):null)
watch(()=>props.open,o=>{tab.value=o?.tab||'profile';patents.value=null;patentOpen.value=null},{immediate:true})
watch([company,tab],async([c,t])=>{if(c&&t==='patents'&&patents.value==null&&c.cid){patents.value='loading';try{patents.value=await loadPatents(c.cid)}catch{patents.value=[]}}})
const tabs=[['profile','企业概况'],['products','产品与模型'],['patents','专利'],['economy','经济指标']]
const facts=computed(()=>{const c=company.value;return c?[['所属行业',c.industry],['注册地区',[c.province,c.city].filter(Boolean).join(' · ')],['产业角色',c.roles.map(roleName).join(' / ')],['统一社会信用代码',c.credit||'—']]:[]})
const techNames=ids=>(ids||[]).map(id=>C.value?.tech.get(id)).filter(Boolean)
const companyProducts=computed(()=>company.value&&P.value?(P.value.byOwner.get(company.value.cid)||[]):[])
const econ=computed(()=>{
 const c=company.value,e=E.value;if(!c||!e)return []
 const m=e.latest.get(c.id);if(!m)return []
 return e.categories.map(g=>({...g,rows:e.metrics.filter(x=>x.category===g.id&&m.has(x.id)).map(x=>({m:x,r:m.get(x.id),s:e.sources[m.get(x.id).source]}))})).filter(g=>g.rows.length)
})
const owners=computed(()=>product.value&&P.value?product.value.owners.map((id,i)=>{const o=P.value.ownerMap.get(id);return {id,name:o?.name||product.value.ownerNames[i]||id,meta:[o?.province,o?.industry].filter(Boolean).join(' · '),company:o?.companyId}}):[])
</script>
<template>
 <Teleport to="body"><div v-if="open" class="ind-overlay" @click.self="emit('close')"><aside ref="surface" class="ind-drawer" role="dialog" aria-modal="true" :aria-label="company?.name||product?.name||'详情'">
  <header class="ind-dr-h"><div><span>{{open.kind==='company'?'企业档案':'产品与模型'}}</span><h4>{{company?.name||product?.name||'正在读取…'}}</h4></div><button aria-label="关闭" @click="emit('close')">×</button></header>
  <template v-if="company">
   <nav class="ind-dr-tabs" role="tablist"><button v-for="[id,l] in tabs" :key="id" role="tab" :aria-selected="tab===id" :class="{active:tab===id}" @click="tab=id">{{l}}<small v-if="id==='products'&&company.cov.products"> {{fmt(company.cov.products)}}</small><small v-if="id==='patents'&&company.cov.patents"> {{fmt(company.cov.patents)}}</small></button></nav>
   <template v-if="tab==='profile'">
    <dl class="ind-facts"><div v-for="[k,v] in facts" :key="k"><dt>{{k}}</dt><dd>{{v||'—'}}</dd></div></dl>
    <div class="ind-dr-stats"><div><strong>{{fmt(company.cov.products)}}</strong><span>产品与模型 · 项</span></div><div><strong>{{fmt(company.cov.patents)}}</strong><span>累计专利 · 件</span></div><div><strong>{{fmt(company.cov.jobsDeduplicated||0)}}</strong><span>招聘岗位 · 去重</span></div></div>
    <template v-if="company.desc"><p class="ind-dr-k">企业简介</p><p class="ind-dr-p">{{company.desc}}</p></template>
    <template v-if="techNames(company.tech).length"><p class="ind-dr-k">涉及技术点</p><div class="ind-chips"><span v-for="t in techNames(company.tech).slice(0,24)" :key="t.id">{{t.name}}</span></div></template>
    <template v-if="company.sources.length"><p class="ind-dr-k">企业资料</p><a v-for="(u,i) in company.sources" :key="u" class="ind-dr-src" :href="safeUrl(u)" target="_blank" rel="noopener"><b>企业公开资料 {{i+1}} ↗</b><small>{{u}}</small></a></template>
   </template>
   <template v-else-if="tab==='products'">
    <p v-if="!P" class="ind-dr-p">正在读取产品目录…</p>
    <p v-else-if="!companyProducts.length" class="ind-dr-p">暂无关联产品。</p>
    <button v-for="p in companyProducts.slice(0,40)" :key="p.id" class="ind-dr-item" @click="emit('open',{kind:'product',id:p.id})"><b>{{p.name}}</b><small>{{techNames(p.tech).map(t=>t.name).join(' · ')||p.uses.join(' · ')}}</small></button>
    <p v-if="companyProducts.length>40" class="ind-dr-note">展示前 40 项，共 {{fmt(companyProducts.length)}} 项</p>
   </template>
   <template v-else-if="tab==='patents'">
    <div class="ind-dr-stats two"><div><strong>{{fmt(company.cov.patents)}}</strong><span>累计专利 · 件</span></div><div><strong>{{fmt(company.cov.labeledPatents)}}</strong><span>关联技术点的专利 · 件</span></div></div>
    <p class="ind-dr-k">专利选览</p>
    <p v-if="patents==='loading'" class="ind-dr-p">正在读取专利…</p>
    <p v-else-if="!patents?.length" class="ind-dr-p">暂无专利选览。</p>
    <template v-for="(p,i) in Array.isArray(patents)?patents:[]" :key="p.publication||i">
     <button class="ind-dr-item" :aria-expanded="patentOpen===i" @click="patentOpen=patentOpen===i?null:i"><b>{{p.title}}</b><small>{{p.application}} · {{p.applicationDate}}<template v-if="p.type"> · {{p.type}}</template></small></button>
     <div v-if="patentOpen===i" class="ind-dr-patent"><dl class="ind-facts"><div><dt>公开（公告）号</dt><dd>{{p.publication||'—'}}</dd></div><div><dt>公开日期</dt><dd>{{p.publicationDate||'—'}}</dd></div><div class="full"><dt>申请人</dt><dd>{{p.applicant||'—'}}</dd></div></dl><div v-if="p.technologies?.length" class="ind-chips"><span v-for="t in p.technologies" :key="t">{{t}}</span></div><p v-if="p.abstract" class="ind-dr-p">{{p.abstract}}</p><a v-if="p.url" class="text-button" :href="safeUrl(p.url)" target="_blank" rel="noopener">查看专利原文 ↗</a></div>
    </template>
    <p class="ind-dr-note">企业及关联公司专利 · 专利资料日期 {{C?.patentDate}}</p>
   </template>
   <template v-else>
    <p v-if="!E" class="ind-dr-p">正在读取经济指标…</p>
    <p v-else-if="!econ.length" class="ind-dr-p">暂无经济指标。</p>
    <section v-for="g in econ" :key="g.id" class="ind-dr-econ"><p class="ind-dr-k">{{g.name}}</p>
     <div v-for="x in g.rows" :key="x.m.id" class="ind-dr-metric"><div><b>{{x.m.name}}</b><small>{{x.r.year}} 年 · {{x.r.scope}}<template v-if="x.r.entity&&x.r.entity!==company.name"> · {{x.r.entity}}</template></small><a v-if="x.s?.url" :href="safeUrl(x.s.url)" target="_blank" rel="noopener">{{x.s.title}}<template v-if="x.s.location"> · {{x.s.location}}</template> ↗</a></div><strong>{{amount(x.r.value,x.m.unit)}}<small>{{x.m.unit}}</small></strong></div>
    </section>
    <p v-if="econ.length" class="ind-dr-note">金额为人民币亿元；每项指标取最近年度</p>
   </template>
  </template>
  <template v-else-if="product">
   <div class="ind-chips"><span v-for="u in product.uses" :key="u" class="lead">{{u}}</span></div>
   <p class="ind-dr-p">{{product.desc||'产品资料见下方来源。'}}</p>
   <p class="ind-dr-k">企业与机构</p>
   <component :is="o.company?'button':'div'" v-for="o in owners" :key="o.id" class="ind-dr-item" @click="o.company&&emit('open',{kind:'company',id:o.company})"><b>{{o.name}}<template v-if="o.company"> →</template></b><small>{{o.meta}}</small></component>
   <template v-if="product.versions.length"><p class="ind-dr-k">产品版本</p><div class="ind-chips"><span v-for="v in product.versions" :key="v">{{v}}</span></div></template>
   <template v-if="techNames(product.tech).length"><p class="ind-dr-k">专业技术</p><div v-for="t in techNames(product.tech)" :key="t.id" class="ind-dr-tech"><b>{{t.name}}</b><small>{{t.level1}} / {{t.level2}}</small></div></template>
   <template v-if="product.sources.length"><p class="ind-dr-k">产品资料</p><a v-for="s in product.sources" :key="s.url" class="ind-dr-src" :href="safeUrl(s.url)" target="_blank" rel="noopener"><b>{{s.title||'产品公开资料'}} ↗</b><small v-if="s.date">{{s.date}}</small></a></template>
  </template>
 </aside></div></Teleport>
</template>
