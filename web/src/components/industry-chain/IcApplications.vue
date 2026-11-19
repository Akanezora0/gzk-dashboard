<script setup>
/* 产业链分析 03 · 产品与行业应用：分析对象关联的产品，按技术方向、应用行业与名称筛选 */
import {ref,computed,watch} from 'vue'
import {arr,fmtN,productIntros,introOf} from '../../helpers/industryChain.js'
const props=defineProps({scope:Object,techMap:Object,categories:Array,industries:Object,featuredIds:Object,shortName:Function})
const emit=defineEmits(['open'])
const PAGE=9
const cat=ref(''),industry=ref(''),query=ref(''),page=ref(0),introTick=ref(0)
watch(()=>props.scope?.key,()=>{cat.value='';industry.value='';query.value='';page.value=0})
watch([cat,industry,query],()=>page.value=0)
const catsOf=p=>[...new Set(arr(p.technologyIds).map(id=>props.techMap.get(id)?.level1).filter(Boolean))]
const indOf=p=>arr(props.industries?.[p.id])
const directions=computed(()=>{const m=new Map();props.scope.products.forEach(p=>catsOf(p).forEach(n=>m.set(n,(m.get(n)||0)+1)));return props.categories.map((c,i)=>({name:c.name,i,n:m.get(c.name)||0})).filter(d=>d.n).sort((a,b)=>b.n-a.n)})
const maxDir=computed(()=>Math.max(1,...directions.value.map(d=>d.n)))
const industryRows=computed(()=>{const m=new Map();props.scope.products.forEach(p=>indOf(p).forEach(n=>m.set(n,(m.get(n)||0)+1)));return [...m].sort((a,b)=>b[1]-a[1])})
const techCount=computed(()=>new Set(props.scope.products.flatMap(p=>arr(p.technologyIds).filter(id=>props.techMap.has(id)))).size)
const filtered=computed(()=>{
 const q=query.value.trim().toLowerCase()
 return props.scope.products.filter(p=>(!cat.value||catsOf(p).includes(cat.value))&&(!industry.value||indOf(p).includes(industry.value))&&(!q||[p.name,...p.companyIds.map(props.shortName)].join(' ').toLowerCase().includes(q)))
  .sort((a,b)=>Number(props.featuredIds.has(b.id))-Number(props.featuredIds.has(a.id))||a.name.localeCompare(b.name,'zh-CN'))
})
const pages=computed(()=>Math.max(1,Math.ceil(filtered.value.length/PAGE)))
const visible=computed(()=>filtered.value.slice(page.value*PAGE,(page.value+1)*PAGE))
watch(visible,v=>{productIntros(v).then(()=>introTick.value++).catch(()=>{})},{immediate:true})
const intro=p=>{introTick.value;const t=introOf(p.id);return t||''}
const kpis=computed(()=>[[fmtN(props.scope.products.length),'项','产品与服务'],[fmtN(props.scope.companies.length),'家',props.scope.isCompany?'产品提供主体':'关联产品企业'],[fmtN(techCount.value),'项','关联技术点'],[fmtN(directions.value.length),'类','技术方向']])
const tone=['#86507f','#5f7ea4','#ad7d55','#5b8c88','#9a4d69','#7a70a2','#9b778c']
</script>
<template>
 <section class="rs-page ic-sec">
  <header class="rs-head"><span class="rs-no">03</span><h3>产品与行业应用</h3></header>
  <p class="rs-lead soft">{{scope.title}}关联 {{fmtN(scope.products.length)}} 项产品与服务，由 {{fmtN(scope.companies.length)}} 家{{scope.isCompany?'主体':'企业与机构'}}提供<template v-if="directions[0]">，集中在{{directions[0].name}}方向</template>。</p>
  <div class="ic-kpis"><div v-for="[v,u,l] in kpis" :key="l"><strong>{{v}}<small>{{u}}</small></strong><span>{{l}}</span></div></div>
  <div class="ic-dirs">
   <span class="ic-label">技术方向</span>
   <div class="ic-dir-list">
    <button v-for="d in directions" :key="d.name" class="ic-dir" :class="{on:cat===d.name}" :aria-pressed="cat===d.name" :style="{'--c':tone[d.i]}" @click="cat=cat===d.name?'':d.name">
     <span>{{d.name}}</span><b>{{fmtN(d.n)}}</b><i><em :style="{width:d.n/maxDir*100+'%'}"></em></i>
    </button>
   </div>
  </div>
  <div class="ic-filter-row">
   <select v-if="industryRows.length" v-model="industry" aria-label="应用行业"><option value="">全部行业</option><option v-for="[n,c] in industryRows" :key="n" :value="n">{{n}} · {{c}}</option></select>
   <input v-model="query" type="search" placeholder="查找产品或企业" aria-label="查找产品或企业">
   <span class="ic-count">{{fmtN(filtered.length)}} 项产品<template v-if="cat"> · {{cat}} <button class="ic-clear" @click="cat=''">清除</button></template></span>
  </div>
  <div v-if="visible.length" class="ic-cards">
   <article v-for="p in visible" :key="p.id" class="ic-card">
    <button class="ic-card-t" @click="emit('open',{kind:'product',id:p.id})">{{p.name}}<span>↗</span></button>
    <div class="ic-owners"><button v-for="cid in p.companyIds.slice(0,3)" :key="cid" @click="emit('open',{kind:'company',id:cid})">{{shortName(cid)}}</button></div>
    <p>{{intro(p)||'　'}}</p>
    <div class="ic-tags"><button v-for="id in arr(p.technologyIds).filter(id=>techMap.has(id)).slice(0,4)" :key="id" @click="emit('open',{kind:'tech',id})">{{techMap.get(id).name}}</button><span v-if="indOf(p).length" class="ind">{{indOf(p)[0]}}</span></div>
   </article>
  </div>
  <p v-else class="ic-empty">没有符合筛选条件的产品。</p>
  <nav v-if="pages>1" class="ic-pager" aria-label="产品分页"><span>{{page+1}} / {{pages}}</span><button :disabled="page===0" aria-label="上一页" @click="page--">←</button><button :disabled="page>=pages-1" aria-label="下一页" @click="page++">→</button></nav>
 </section>
</template>
