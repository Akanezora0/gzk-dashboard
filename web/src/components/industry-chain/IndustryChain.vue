<script setup>
/* 短链条分析 · 03 产业链分析：证据全景、产品代际演进，以及按分析对象联动的产品应用、经济社会价值和技术链路 */
import {ref,computed,onMounted,onBeforeUnmount} from 'vue'
import IcAtlas from './IcAtlas.vue'
import IcEvolution from './IcEvolution.vue'
import IcApplications from './IcApplications.vue'
import IcValue from './IcValue.vue'
import IcChain from './IcChain.vue'
import IcDetail from './IcDetail.vue'
import IndustryDrawer from '../industry/IndustryDrawer.vue'
import {useAtlas,useEvolution,useChainIndex,fmtN} from '../../helpers/industryChain.js'
import {useCompanies,useProducts,companyOf} from '../../helpers/industryData.js'
import '../../industry.css'
import '../../industry-chain.css'
const props=defineProps({fundAi:Number})
const {atlas}=useAtlas(),evolution=useEvolution(),{index}=useChainIndex()
const {data:dashCompanies}=useCompanies(),{data:dashProducts}=useProducts()
const error=ref('')
useAtlas().ready?.catch(e=>error.value=e.message)

/* 名称与精选主体 */
const featuredIds=computed(()=>new Set((atlas.value?.featured||[]).flatMap(f=>f.products)))
const featuredOrder=computed(()=>(atlas.value?.featured||[]).map(f=>f.companyId))
const featuredRank=computed(()=>new Map(featuredOrder.value.map((id,i)=>[id,i])))
const featuredProducts=computed(()=>Object.fromEntries((atlas.value?.featured||[]).map(f=>[f.companyId,f.products])))
const shortName=id=>atlas.value?.featured.find(f=>f.companyId===id)?.shortName||index.value?.companies.get(id)?.short||index.value?.companies.get(id)?.name||atlas.value?.companies?.[id]?.name||evolution.value?.names?.[id]||id
const companyIndex=id=>index.value?.companies.get(id)

/* 分析对象 */
const kind=ref('technology'),tech=ref('T006'),company=ref('cmp_a92a7a82a356224ae15b')
const groups=computed(()=>(atlas.value?.categories||[]).map(c=>({name:c.name,techs:atlas.value.technologies.filter(t=>t.level1===c.name)})))
const scope=computed(()=>{
 const I=index.value;if(!I||!atlas.value)return null
 if(kind.value==='company'){
  const c=I.companies.get(company.value);if(!c)return null
  const products=c.productIds.map(id=>I.productMap.get(id)).filter(Boolean)
  return {key:'c:'+c.id,id:c.id,isCompany:true,title:shortName(c.id),products,companies:[c]}
 }
 const t=atlas.value.techMap.get(tech.value),products=I.byTech.get(tech.value)||[]
 const ids=[...new Set(products.flatMap(p=>p.companyIds))].filter(id=>I.companies.has(id))
 return {key:'t:'+tech.value,id:tech.value,isCompany:false,title:t?.name||'技术点',products,companies:ids.map(id=>I.companies.get(id))}
})
const query=ref(''),suggestOpen=ref(false)
const suggestions=computed(()=>{
 const I=index.value;if(!I)return []
 const q=query.value.trim().toLowerCase()
 const list=[...I.companies.values()].filter(c=>c.productIds.length&&(!q||c.name.toLowerCase().includes(q)||(c.short||'').toLowerCase().includes(q)))
 return list.sort((a,b)=>(featuredRank.value.get(a.id)??999)-(featuredRank.value.get(b.id)??999)||b.productIds.length-a.productIds.length).slice(0,8)
})
function pickCompany(c){company.value=c.id;kind.value='company';query.value='';suggestOpen.value=false}
function setKind(k){kind.value=k}
let blurTimer=0
function closeSuggest(){clearTimeout(blurTimer);blurTimer=setTimeout(()=>suggestOpen.value=false,160)}

/* 吸顶条：避开站点顶栏 */
const barTop=ref(0)
function measure(){barTop.value=document.querySelector('.site-bar')?.offsetHeight||0}
onMounted(()=>{measure();window.addEventListener('resize',measure)})
onBeforeUnmount(()=>window.removeEventListener('resize',measure))

/* 详情：企业、产品沿用领域数据抽屉；其余用本模块抽屉 */
const drawer=ref(null),detail=ref(null)
function open(o){
 if(!o)return
 if(o.kind==='analyse'){drawer.value=null;detail.value=null;tech.value=o.id;kind.value='technology';document.getElementById('ic-target')?.scrollIntoView({behavior:'smooth',block:'start'});return}
 if(o.kind==='company'){if(dashCompanies.value&&companyOf(o.id)){detail.value=null;drawer.value={kind:'company',id:o.id};return}detail.value={kind:'company',id:o.id};drawer.value=null;return}
 if(o.kind==='product'){if(!dashProducts.value||dashProducts.value.byId.has(o.id)){detail.value=null;drawer.value={kind:'product',id:o.id}}return}
 drawer.value=null;detail.value=o
}
</script>
<template>
 <div class="ic-stack">
  <div v-if="error" class="analysis-loading">产业链数据暂时无法读取：{{error}}</div>
  <div v-else-if="!atlas" class="analysis-loading">正在整理产业链证据…</div>
  <template v-else>
   <IcAtlas :atlas="atlas" :fund-ai="fundAi" @open="open"/>
   <IcEvolution v-if="evolution" :evolution="evolution" :tech-map="atlas.techMap" @open="open"/>
   <div id="ic-target" class="ic-target" :style="{top:barTop+'px'}">
    <span class="ic-label">分析对象</span>
    <div class="rs-seg" role="group" aria-label="分析入口"><button :class="{on:kind==='technology'}" :aria-pressed="kind==='technology'" @click="setKind('technology')">从技术点出发</button><button :class="{on:kind==='company'}" :aria-pressed="kind==='company'" @click="setKind('company')">从企业出发</button></div>
    <select v-if="kind==='technology'" v-model="tech" class="ic-target-sel" aria-label="选择技术点"><optgroup v-for="g in groups" :key="g.name" :label="g.name"><option v-for="t in g.techs" :key="t.id" :value="t.id">{{t.name}}</option></optgroup></select>
    <div v-else class="ic-search">
     <input v-model="query" :placeholder="shortName(company)" aria-label="输入企业或机构名称" @focus="suggestOpen=true" @blur="closeSuggest" @keydown.enter="suggestions[0]&&pickCompany(suggestions[0])">
     <div v-if="suggestOpen&&suggestions.length" class="ic-suggest"><button v-for="c in suggestions" :key="c.id" @mousedown.prevent="pickCompany(c)"><span>{{c.short||c.name}}</span><small>{{c.category}} · {{fmtN(c.productIds.length)}} 项产品</small></button></div>
    </div>
    <small class="ic-target-note">03—05 随分析对象联动</small>
   </div>
   <template v-if="scope">
    <IcApplications :scope="scope" :tech-map="atlas.techMap" :categories="atlas.categories" :industries="index.industries" :featured-ids="featuredIds" :short-name="shortName" @open="open"/>
    <IcValue :scope="scope" :featured-rank="featuredRank" :short-name="shortName" @open="open"/>
    <IcChain :scope="scope" :tech-map="atlas.techMap" :featured-order="featuredOrder" :featured-products="featuredProducts" :short-name="shortName" :company-of="companyIndex" @open="open"/>
   </template>
   <div v-else class="analysis-loading">正在读取产品与企业关联…</div>
  </template>
  <IndustryDrawer :open="drawer" @close="drawer=null" @open="o=>drawer=o"/>
  <IcDetail :open="detail" :atlas="atlas" :index="index" :evolution="evolution" :short-name="shortName" @close="detail=null" @open="open"/>
 </div>
</template>
