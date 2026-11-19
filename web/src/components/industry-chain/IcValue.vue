<script setup>
/* 产业链分析 04 · 经济社会价值：企业经营、劳动力需求与应用成效（按企业分页读取年度指标） */
import {ref,computed,watch} from 'vue'
import {fmtN,companyValue,metricRows,isLabor,isSocial,recentRows,periodRank,compactValue,period,metricTitle,reporterOf} from '../../helpers/industryChain.js'
const props=defineProps({scope:Object,featuredRank:Object,shortName:Function})
const emit=defineEmits(['open'])
const CO_PAGE=6,FIN_PAGE=11,SOC_PAGE=6,JOB_PAGE=4
const coPage=ref(0),metric=ref(''),year=ref(''),fp=ref(0),lp=ref(0),sp=ref(0),packs=ref(new Map()),loading=ref(false)
watch(()=>props.scope?.key,()=>{coPage.value=0;metric.value='';year.value=''})
watch([coPage,metric,year],()=>{fp.value=0;lp.value=0;sp.value=0})
const ranked=computed(()=>props.scope.companies.slice().sort((a,b)=>(props.featuredRank.get(a.id)??999)-(props.featuredRank.get(b.id)??999)||b.jobs-a.jobs||a.name.localeCompare(b.name,'zh-CN')))
const coPages=computed(()=>Math.max(1,Math.ceil(ranked.value.length/CO_PAGE)))
const pageCos=computed(()=>ranked.value.slice(coPage.value*CO_PAGE,(coPage.value+1)*CO_PAGE))
watch(pageCos,async list=>{
 const todo=list.filter(c=>c.value&&!packs.value.has(c.id));if(!todo.length)return
 loading.value=true
 const got=await Promise.all(todo.map(c=>companyValue(c.id).then(p=>[c.id,p])))
 const next=new Map(packs.value);got.forEach(([id,p])=>next.set(id,p));packs.value=next;loading.value=false
},{immediate:true})
const rows=computed(()=>pageCos.value.flatMap(c=>metricRows(c,packs.value.get(c.id))))
const financial=computed(()=>rows.value.filter(r=>!isLabor(r)&&!isSocial(r)))
const yearOf=r=>String(r.year||String(r.period||'').match(/20\d{2}/)?.[0]||'')
const years=computed(()=>[...new Set(financial.value.map(yearOf).filter(Boolean))].sort().reverse())
const metrics=computed(()=>[...new Set(financial.value.map(metricTitle))].sort((a,b)=>a.localeCompare(b,'zh-CN')))
const finRows=computed(()=>{const f=financial.value.filter(r=>(!year.value||yearOf(r)===year.value)&&(!metric.value||metricTitle(r)===metric.value));return year.value?f.sort((a,b)=>periodRank(b)-periodRank(a)):recentRows(f)})
const slice=(list,p,n)=>list.slice(p*n,(p+1)*n)
const pagesOf=(list,n)=>Math.max(1,Math.ceil(list.length/n))
const finCovered=computed(()=>new Set([...financial.value.map(r=>r.companyId),...pageCos.value.filter(c=>c.rev).map(c=>c.id)]).size)
const labor=computed(()=>rows.value.filter(isLabor))
const laborList=computed(()=>pageCos.value.filter(c=>c.jobs>0||labor.value.some(r=>r.companyId===c.id)).sort((a,b)=>b.jobs-a.jobs))
const laborOf=c=>recentRows(labor.value.filter(r=>r.companyId===c.id)).slice(0,2)
const maxJobs=computed(()=>Math.max(1,...laborList.value.map(c=>c.jobs)))
const social=computed(()=>recentRows(rows.value.filter(isSocial)))
const pageJobs=computed(()=>pageCos.value.reduce((s,c)=>s+c.jobs,0))
const pageNotices=computed(()=>pageCos.value.reduce((s,c)=>s+(c.notices||0),0))
const kpis=computed(()=>{const cs=props.scope.companies;return [[fmtN(cs.length),'家',props.scope.isCompany?'分析主体':'关联产品企业'],[fmtN(cs.filter(c=>c.value).length),'家','经济指标覆盖'],[fmtN(cs.reduce((s,c)=>s+c.jobs,0)),'条','招聘记录 · 去重'],[fmtN(cs.reduce((s,c)=>s+(c.notices||0),0)),'条','企业公告关联']]})
const years6=computed(()=>props.scope.isCompany?(pageCos.value[0]?.years||[]).filter(y=>Number.isFinite(Number(y.value))).slice(-6):[])
const maxYear=computed(()=>Math.max(1,...years6.value.map(y=>Number(y.value))))
const sub=r=>`${props.shortName(r.companyId)} · ${period(r)}`
</script>
<template>
 <section class="rs-page ic-sec">
  <header class="rs-head"><span class="rs-no">04</span><h3>经济社会价值</h3></header>
  <p class="rs-lead soft">从企业经营、劳动力需求与应用成效三方面，观察{{scope.title}}相关企业形成的经济社会价值。</p>
  <div class="ic-kpis"><div v-for="[v,u,l] in kpis" :key="l"><strong>{{v}}<small>{{u}}</small></strong><span>{{l}}</span></div></div>
  <div v-if="scope.companies.length>1" class="ic-cobar">
   <div class="ic-cochips"><button v-for="c in pageCos" :key="c.id" @click="emit('open',{kind:'company',id:c.id})">{{shortName(c.id)}}</button></div>
   <nav v-if="coPages>1" class="ic-pager" aria-label="企业分页"><span>{{coPage+1}} / {{coPages}} · {{fmtN(ranked.length)}} 家</span><button :disabled="coPage===0" aria-label="上一组企业" @click="coPage--">←</button><button :disabled="coPage>=coPages-1" aria-label="下一组企业" @click="coPage++">→</button></nav>
  </div>
  <div class="ic-vgrid">
   <article class="ic-vcard">
    <header><h4>经营表现</h4><span>{{fmtN(finCovered)}} 家企业有指标</span></header>
    <div class="ic-filter-row tight">
     <select v-model="metric" aria-label="经营指标"><option value="">全部经营指标</option><option v-for="m in metrics" :key="m" :value="m">{{m}}</option></select>
     <select v-model="year" aria-label="观察期"><option value="">各指标最近披露</option><option v-for="y in years" :key="y" :value="y">{{y}} 年</option></select>
    </div>
    <div class="ic-mlist">
     <button v-for="r in slice(finRows,fp,FIN_PAGE)" :key="r.id+r.companyId+r.period" class="ic-mrow" @click="emit('open',{kind:'metric',row:r})"><span><b>{{metricTitle(r)}}</b><small>{{sub(r)}}</small></span><strong>{{compactValue(r)}}</strong></button>
     <p v-if="!finRows.length" class="ic-empty">{{loading?'正在读取年度指标…':'本组企业暂无经营指标。'}}</p>
    </div>
    <nav v-if="pagesOf(finRows,FIN_PAGE)>1" class="ic-pager small"><span>{{fp+1}} / {{pagesOf(finRows,FIN_PAGE)}}</span><button :disabled="fp===0" aria-label="上一页" @click="fp--">←</button><button :disabled="fp>=pagesOf(finRows,FIN_PAGE)-1" aria-label="下一页" @click="fp++">→</button></nav>
    <footer class="ic-vfoot"><div><strong>{{fmtN(pageNotices)}}</strong><span>企业公告关联</span></div><div><strong>{{fmtN(pageCos.filter(c=>c.notices).length)}}</strong><span>招投标关联主体</span></div></footer>
   </article>
   <div class="ic-vcol">
    <article class="ic-vcard">
     <header><h4>应用成效与服务覆盖</h4><span>{{social.length}} 项披露指标</span></header>
     <div class="ic-mlist">
      <button v-for="r in slice(social,sp,SOC_PAGE)" :key="r.id+r.companyId" class="ic-mrow" @click="emit('open',{kind:'metric',row:r})"><span><b>{{metricTitle(r)}}</b><small>{{sub(r)}}</small></span><strong>{{compactValue(r)}}</strong></button>
      <p v-if="!social.length" class="ic-empty">{{loading?'正在读取年度指标…':'本组企业暂无应用成效指标。'}}</p>
     </div>
     <nav v-if="pagesOf(social,SOC_PAGE)>1" class="ic-pager small"><span>{{sp+1}} / {{pagesOf(social,SOC_PAGE)}}</span><button :disabled="sp===0" aria-label="上一页" @click="sp--">←</button><button :disabled="sp>=pagesOf(social,SOC_PAGE)-1" aria-label="下一页" @click="sp++">→</button></nav>
    </article>
    <article class="ic-vcard">
     <header><h4>劳动力需求</h4><span>招聘 2014—2025</span></header>
     <div class="ic-mini"><div><strong>{{fmtN(pageJobs)}}</strong><span>招聘记录 · 去重</span></div><div><strong>{{fmtN(pageCos.filter(c=>c.jobs>0).length)}}</strong><span>招聘关联主体</span></div><div><strong>{{fmtN(pageCos.filter(c=>c.staff).length)}}</strong><span>人员指标主体</span></div></div>
     <div class="ic-jobs">
      <div v-for="c in slice(laborList,lp,JOB_PAGE)" :key="c.id" class="ic-job">
       <button @click="emit('open',{kind:'company',id:c.id})">{{shortName(c.id)}}</button><i><em :style="{width:Math.max(1.5,c.jobs/maxJobs*100)+'%'}"></em></i><b>{{fmtN(c.jobs)}}</b>
       <button v-for="r in laborOf(c)" :key="r.id" class="ic-job-m" @click="emit('open',{kind:'metric',row:r})">{{metricTitle(r)}} <b>{{compactValue(r)}}</b><small>{{period(r)}}</small></button>
      </div>
      <p v-if="!laborList.length" class="ic-empty">本组企业暂无招聘记录。</p>
     </div>
     <nav v-if="pagesOf(laborList,JOB_PAGE)>1" class="ic-pager small"><span>{{lp+1}} / {{pagesOf(laborList,JOB_PAGE)}}</span><button :disabled="lp===0" aria-label="上一页" @click="lp--">←</button><button :disabled="lp>=pagesOf(laborList,JOB_PAGE)-1" aria-label="下一页" @click="lp++">→</button></nav>
     <div v-if="years6.length" class="ic-years"><span v-for="y in years6" :key="y.year"><b>{{fmtN(y.value)}}</b><i :style="{height:Math.max(3,y.value/maxYear*56)+'px'}"></i><small>{{y.year}}</small></span></div>
    </article>
   </div>
  </div>
 </section>
</template>
