<script setup>
/* 产业链分析 01 · 证据全景：开头六环节规模，下接六列证据图（科学基金 → 企业与机构 → 技术大类 → 产品与服务 → 相关专利 → 经济指标） */
import {ref,computed,onBeforeUnmount} from 'vue'
import {useTip,textWidth,toggleFullscreen} from '../../helpers/strengthTip.js'
import {companyColors,categoryColors,headline,compactValue,period,metricTitle,fmtN,clip} from '../../helpers/industryChain.js'
const props=defineProps({atlas:Object,fundAi:Number})
const emit=defineEmits(['open'])
const {tip,show,move,hide}=useTip()
const A=computed(()=>props.atlas)

/* ---------- 开头：六环节规模 ---------- */
const wan=n=>n>=1e4?(n/1e4).toFixed(1).replace(/\.0$/,'')+' 万':fmtN(n)
const flow=computed(()=>{const c=A.value.counts;return [
 {k:'fund',n:'基金项目',v:props.fundAi?fmtN(props.fundAi):'—',u:'项人工智能基金',hub:true,tone:'#a21535'},
 {k:'co',n:'企业与机构',v:fmtN(c.companies),u:`精选 ${A.value.featured.length} 家展示`,tone:companyColors[0]},
 {k:'cat',n:'技术大类',v:'7 类',u:'80 个技术点',tone:companyColors[1]},
 {k:'prod',n:'产品与服务',v:fmtN(c.products),u:'项已采纳产品',tone:companyColors[2]},
 {k:'pat',n:'相关专利',v:wan(c.labeledPatents),u:'件已挂钩技术',tone:companyColors[3]},
 {k:'eco',n:'经济指标',v:wan(c.annualValues),u:'条年度指标',tone:companyColors[4]}]})
const FX=[110,338,566,794,1022,1250],FY=118
const flowLinks=computed(()=>flow.value.slice(1).map((b,i)=>{const a=flow.value[i],x0=FX[i]+(a.hub?66:58)+6,x1=FX[i+1]-64,xe=x1-14;return {id:a.k+b.k,x0,x1,xe,ca:a.tone,cb:b.tone}}))

/* ---------- 证据图 ---------- */
const board=ref(null)
const filters=ref({category:'all',tech:'all',scope:'all'})
const groups=computed(()=>A.value.categories.map(c=>({name:c.name,techs:A.value.technologies.filter(t=>t.level1===c.name)})))
const inScope=(c,s)=>s==='all'||(s==='enterprise'?c.entityScope==='enterprise':c.entityScope!=='enterprise')
const usesFilter=ids=>(filters.value.tech==='all'||ids.includes(filters.value.tech))&&(filters.value.category==='all'||ids.some(id=>A.value.techMap.get(id)?.level1===filters.value.category))
function featureProducts(f,i){
 const list=f.products.map(id=>A.value.products[id]).filter(Boolean)
 return list.filter(p=>usesFilter(p.technologyIds||[])).slice(0,i<3?3:2)
}
const W=1200,TOP=60,RH=96
const X={fund:[0,132],co:[172,330],cat:[372,566],prod:[606,800],pat:[842,972],eco:[1014,1200]}
const rows=computed(()=>{
 const out=[]
 A.value.featured.forEach((f,i)=>{
  const c=A.value.companies[f.companyId];if(!c||!inScope(c,filters.value.scope)||!usesFilter(c.technologyIds||[]))return
  out.push({f,c,i,color:companyColors[i%companyColors.length],products:featureProducts(f,i),eco:headline(c,A.value.economics[c.id]),fund:A.value.funding.find(x=>x.companyId===c.id)})
 })
 return out.map((r,k)=>({...r,k,y:TOP+k*RH,cy:TOP+k*RH+RH/2-4}))
})
const H=computed(()=>TOP+Math.max(7,rows.value.length)*RH+8)
const catCY=i=>TOP+i*RH+RH/2-4
const fundCY=computed(()=>(TOP+H.value-8)/2)
function prodBoxes(r){const n=r.products.length,h=n>2?26:n===2?34:40,gap=n>2?4:8,total=n*h+(n-1)*gap;return r.products.map((p,j)=>({p,y:r.cy-total/2+j*(h+gap),h}))}
const catOf=id=>A.value.catIndex.get(A.value.techMap.get(id)?.level1)
const curve=(x0,y0,x1,y1)=>{const m=(x0+x1)/2;return `M${x0},${y0} C${m},${y0} ${m},${y1} ${x1},${y1}`}
const BX=X.prod[0]-10 /* 产品组括线所在 x */
const model=computed(()=>{
 const edges=[],brackets=[]
 rows.value.forEach(r=>{
  const o=r.c.id,boxes=prodBoxes(r)
  /* 基金 → 企业：共用一条主干，分叉到各主体 */
  if(r.fund)edges.push({id:'f'+o,owner:o,d:`M${X.fund[1]},${fundCY.value} H152 V${r.cy} H${X.co[0]}`,color:r.color,dashed:!r.fund.projectNumbers?.length,trunk:true})
  /* 企业 → 技术大类、技术大类 → 产品组：每对只画一条平滑曲线 */
  const cats=new Map()
  boxes.forEach(({p})=>(p.technologyIds||[]).forEach(t=>{const i=catOf(t);if(i==null)return;if(!cats.has(i))cats.set(i,new Set());cats.get(i).add(p.id)}))
  cats.forEach((pids,i)=>{
   edges.push({id:`cc${o}${i}`,owner:o,cat:i,d:curve(X.co[1],r.cy,X.cat[0],catCY(i)),color:r.color})
   edges.push({id:`cp${o}${i}`,owner:o,cat:i,products:[...pids],d:curve(X.cat[1],catCY(i),BX,r.cy),color:r.color})
  })
  /* 产品组括线 */
  if(boxes.length){const y0=boxes[0].y+boxes[0].h/2,y1=boxes[boxes.length-1].y+boxes[boxes.length-1].h/2
   brackets.push({id:'b'+o,owner:o,color:r.color,d:`M${BX},${y0} V${y1} `+boxes.map(b=>`M${BX},${b.y+b.h/2} H${X.prod[0]}`).join(' ')})}
  edges.push({id:'pp'+o,owner:o,d:`M${X.prod[1]},${r.cy} H${X.pat[0]}`,color:r.color})
  if(r.eco)edges.push({id:'pe'+o,owner:o,d:`M${X.pat[1]},${r.cy} H${X.eco[0]}`,color:r.color})
 })
 return {edges,brackets}
})

/* 悬停：企业、产品、技术大类（展开技术点）、技术点 */
const hover=ref(null),expanded=ref(null)
let closeTimer=0
const panel=computed(()=>{
 const i=expanded.value;if(i==null)return null
 const g=groups.value[i],step=30,h=58+g.techs.length*step,y=Math.max(TOP-6,Math.min(catCY(i)-30,H.value-h-4))
 const used=new Map()
 rows.value.forEach(r=>prodBoxes(r).forEach(({p,y:py,h:ph})=>(p.technologyIds||[]).forEach(t=>{if(catOf(t)!==i)return;if(!used.has(t))used.set(t,[]);used.get(t).push({r,py:py+ph/2,p})})))
 const leaves=g.techs.map((t,j)=>({t,y:y+48+j*step,links:used.get(t.id)||[]}))
 return {i,g,y,h,leaves}
})
const linked=computed(()=>{
 const h=hover.value;if(!h)return null
 const nodes=new Set(),edges=new Set()
 const addOwner=o=>{model.value.edges.forEach(e=>{if(e.owner===o){edges.add(e.id);if(e.cat!=null)nodes.add('cat'+e.cat);(e.products||[]).forEach(id=>nodes.add('p'+id))}});model.value.brackets.forEach(b=>{if(b.owner===o)edges.add(b.id)});rows.value.find(r=>r.c.id===o)?.products.forEach(p=>nodes.add('p'+p.id));nodes.add('co'+o);nodes.add('pat'+o);nodes.add('eco'+o);nodes.add('fund')}
 if(h.type==='company'||h.type==='product'||h.type==='pat'||h.type==='eco')addOwner(h.owner)
 if(h.type==='cat'){nodes.add('cat'+h.i);model.value.edges.forEach(e=>{if(e.cat===h.i){edges.add(e.id);edges.add('b'+e.owner);nodes.add('co'+e.owner);(e.products||[]).forEach(id=>nodes.add('p'+id))}})}
 if(h.type==='leaf'){nodes.add('cat'+h.cat);nodes.add('leaf'+h.id);rows.value.forEach(r=>{const ps=r.products.filter(p=>p.technologyIds?.includes(h.id));if(!ps.length)return;nodes.add('co'+r.c.id);edges.add('b'+r.c.id);ps.forEach(p=>nodes.add('p'+p.id));edges.add(`cc${r.c.id}${h.cat}`);edges.add(`cp${r.c.id}${h.cat}`)})}
 if(h.type==='fund'){nodes.add('fund');model.value.edges.forEach(e=>{if(e.id.startsWith('f')){edges.add(e.id);nodes.add('co'+e.owner)}})}
 return {nodes,edges}
})
const dim=key=>linked.value&&!linked.value.nodes.has(key)
const edgeOn=id=>linked.value?.edges.has(id)
const fundLabel=computed(()=>{
 const h=hover.value;if(!h||!['company','product','pat','eco'].includes(h.type))return null
 const r=rows.value.find(x=>x.c.id===h.owner),nums=r?.fund?.projectNumbers||[];if(!nums.length)return null
 const lh=34+nums.length*21,above=r.cy<fundCY.value,y=above?fundCY.value-36-lh-10:fundCY.value+36+10
 return {nums,y,h:lh,color:r.color}
})
function enter(e,h,html){clearTimeout(closeTimer);hover.value=h;show(e,html)}
function leave(){hover.value=null;hide()}
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))
const card=(kind,title,body,foot)=>`<span class="ic-tip-k">${esc(kind)}</span><b class="ic-tip-t">${esc(title)}</b>${body?`<p>${esc(body)}</p>`:''}${foot?`<span class="ic-tip-f">${foot}</span>`:''}`
const companyTip=(e,r)=>enter(e,{type:'company',owner:r.c.id},card(r.c.entityScope==='enterprise'?'企业':'科研机构',r.f.shortName||r.c.name,clip(r.f.description||r.c.businessSummary,120),`${fmtN(r.c.coverage.products)} 项产品 · ${fmtN(r.c.coverage.labeledPatents)} 件技术挂钩专利${r.fund?.projectNumbers?.length?` · ${r.fund.projectNumbers.length} 个基金编号`:''}`))
const productTip=(e,r,p)=>enter(e,{type:'product',owner:r.c.id},card('产品与服务 · '+(r.f.shortName||r.c.name),p.name,clip(p.intro,110),(p.technologyIds||[]).slice(0,3).map(id=>A.value.techMap.get(id)?.name).filter(Boolean).join(' · ')))
const catTip=i=>{clearTimeout(closeTimer);expanded.value=i;hover.value={type:'cat',i};hide()}
const leafTip=(e,t,i)=>enter(e,{type:'leaf',id:t.id,cat:i},card(t.level1+' · '+t.level2,t.name,t.definition,`${fmtN(t.products)} 项产品 · ${fmtN(t.patents)} 件专利`))
const patTip=(e,r)=>enter(e,{type:'pat',owner:r.c.id},card('相关专利',`${fmtN(r.c.coverage.labeledPatents)} 件`,`${r.f.shortName||r.c.name}及关联公司专利中已挂钩技术点的部分；归集专利 ${fmtN(r.c.coverage.patents)} 件。`))
const ecoTip=(e,r)=>enter(e,{type:'eco',owner:r.c.id},card('经济指标',metricTitle(r.eco),`${compactValue(r.eco)} · ${period(r.eco)}${r.eco.reportingEntity?' · '+r.eco.reportingEntity:''}`))
const fundTip=e=>enter(e,{type:'fund'},card('科学基金','国家自然科学基金','依据论文致谢中的基金编号与作者署名，关联到企业和机构的研究。',`${rows.value.filter(r=>r.fund?.projectNumbers?.length).length} 家精选主体核得基金编号`))
function leaveCat(){closeTimer=setTimeout(()=>{expanded.value=null;if(hover.value?.type==='cat'||hover.value?.type==='leaf')hover.value=null},220)}
onBeforeUnmount(()=>clearTimeout(closeTimer))
function reset(){filters.value={category:'all',tech:'all',scope:'all'};hover.value=null;expanded.value=null}
function setTech(v){filters.value={...filters.value,tech:v,category:v==='all'?filters.value.category:'all'}}
function setCat(v){filters.value={...filters.value,category:v,tech:'all'}}
const fit=(t,w,size)=>Math.min(size,size*w/Math.max(1,textWidth(t,size)))
const ecoTitle=r=>r.eco?metricTitle(r.eco)+(period(r.eco)?' · '+period(r.eco):''):''
</script>
<template>
 <section class="rs-page ic-sec">
  <header class="rs-head"><span class="rs-no">01</span><h3>产业链证据全景</h3></header>
  <p class="rs-lead soft">以技术为纽带，把科学基金、企业与机构、技术大类、产品与服务、相关专利和经济指标连成六个环节；7 家精选主体呈现从基金项目到企业经营的完整证据。</p>
  <div class="rs-scroll"><svg class="rs-svg ic-flow" viewBox="0 0 1360 262" role="img" aria-label="产业链六个环节的数据规模">
   <defs><linearGradient v-for="l in flowLinks" :key="'g'+l.id" :id="'icg'+l.id" gradientUnits="userSpaceOnUse" :x1="l.x0" :x2="l.x1" y1="0" y2="0"><stop offset="0" :stop-color="l.ca" stop-opacity=".55"/><stop offset="1" :stop-color="l.cb" stop-opacity=".85"/></linearGradient></defs>
   <g v-for="l in flowLinks" :key="l.id">
    <path :d="`M${l.x0},${FY-5} L${l.xe},${FY-5} L${l.xe},${FY-10} L${l.x1},${FY} L${l.xe},${FY+10} L${l.xe},${FY+5} L${l.x0},${FY+5} Z`" :fill="`url(#icg${l.id})`"/>
    <line class="rs-flow" :x1="l.x0+8" :x2="l.xe-6" :y1="FY" :y2="FY" stroke="#fff" stroke-width="4" stroke-linecap="round" stroke-dasharray="2 22"/>
   </g>
   <circle class="rs-pulse ic-pulse" :cx="FX[0]" :cy="FY" r="66" fill="none" stroke="#a21535" stroke-width="2"/>
   <g v-for="(n,i) in flow" :key="n.k" class="ic-fnode">
    <circle v-if="n.hub" :cx="FX[i]" :cy="FY" r="80" fill="#a21535" opacity=".07"/>
    <circle :cx="FX[i]" :cy="FY" :r="n.hub?66:58" :fill="n.hub?'#a21535':'#fff'" :stroke="n.hub?'none':n.tone" stroke-width="2.5"/>
    <text :x="FX[i]" :y="FY+7" :font-size="n.hub?21:19" font-weight="750" text-anchor="middle" :fill="n.hub?'#fff':'#2a2a2a'">{{n.n}}</text>
    <text :x="FX[i]" :y="FY+(n.hub?108:100)" font-size="25" font-weight="780" text-anchor="middle" fill="#2a2a2a">{{n.v}}</text>
    <text :x="FX[i]" :y="FY+(n.hub?131:123)" font-size="13.5" text-anchor="middle" fill="#78716c">{{n.u}}</text>
   </g>
  </svg></div>

  <div ref="board" class="ic-board">
   <div class="ic-tools">
    <select :value="filters.category" aria-label="技术大类" @change="setCat($event.target.value)"><option value="all">全部技术大类</option><option v-for="c in A.categories" :key="c.name" :value="c.name">{{c.name}}</option></select>
    <select :value="filters.tech" aria-label="技术点" @change="setTech($event.target.value)"><option value="all">全部 80 个技术点</option><optgroup v-for="g in groups" :key="g.name" :label="g.name"><option v-for="t in g.techs" :key="t.id" :value="t.id">{{t.name}}</option></optgroup></select>
    <select v-model="filters.scope" aria-label="主体类型"><option value="all">全部主体</option><option value="enterprise">企业</option><option value="institution">研究机构</option></select>
    <span class="ic-grow"></span>
    <button class="rs-btn" @click="reset">重置视图</button>
    <button class="rs-btn" @click="toggleFullscreen(board)">全屏</button>
   </div>
   <div class="rs-scroll ic-gwrap"><svg class="ic-graph" :class="{focus:!!linked}" :viewBox="`-4 0 ${W+8} ${H}`" role="img" aria-label="科学基金、企业与机构、技术大类、产品与服务、相关专利和经济指标的关联图" @mouseleave="leave">
    <g class="ic-heads">
     <g v-for="[k,t] in [['fund','科学基金'],['co','企业与机构'],['cat','技术大类'],['prod','产品与服务'],['pat','相关专利'],['eco','经济指标']]" :key="k">
      <text :x="(X[k][0]+X[k][1])/2" y="22" text-anchor="middle">{{t}}</text>
      <line :x1="X[k][0]" :x2="X[k][1]" y1="34" y2="34"/>
     </g>
    </g>
    <g class="ic-edges">
     <path v-for="e in model.edges" :key="e.id" :d="e.d" :stroke="e.trunk?'#c9bcc0':e.color" :class="{on:edgeOn(e.id),trunk:e.trunk}" :stroke-dasharray="e.dashed?'4 4':null"/>
     <path v-for="b in model.brackets" :key="b.id" class="bracket" :d="b.d" :stroke="b.color" :class="{on:edgeOn(b.id)}"/>
    </g>
    <g class="ic-node fund" :class="{dim:dim('fund')}" role="button" tabindex="0" aria-label="国家自然科学基金" @mouseenter="fundTip($event)" @mousemove="move" @mouseleave="leave" @click="emit('open',{kind:'funding'})" @keydown.enter="emit('open',{kind:'funding'})">
     <rect :x="X.fund[0]" :y="fundCY-34" :width="X.fund[1]-X.fund[0]" height="68" rx="4" fill="#a21535"/>
     <text :x="(X.fund[0]+X.fund[1])/2" :y="fundCY-4" text-anchor="middle" fill="#fff" font-size="14.5" font-weight="750">国家自然科学基金</text>
     <text class="sub" :x="(X.fund[0]+X.fund[1])/2" :y="fundCY+17" text-anchor="middle" font-size="12">论文项目号关联</text>
    </g>
    <g v-if="fundLabel" class="ic-fundnums">
     <rect :x="X.fund[0]" :y="fundLabel.y" :width="X.fund[1]-X.fund[0]" :height="fundLabel.h" rx="4" fill="#fff" :stroke="fundLabel.color" stroke-width="1.3"/>
     <text :x="(X.fund[0]+X.fund[1])/2" :y="fundLabel.y+21" text-anchor="middle" font-size="12" fill="#8a8286">基金编号</text>
     <text v-for="(n,j) in fundLabel.nums" :key="n" :x="(X.fund[0]+X.fund[1])/2" :y="fundLabel.y+42+j*21" text-anchor="middle" font-size="14.5" font-weight="700" fill="#a21535">{{n}}</text>
    </g>
    <g v-for="(c,i) in A.categories" :key="c.name" class="ic-node cat" :class="{dim:dim('cat'+i)}" role="button" tabindex="0" :aria-label="c.name" @mouseenter="catTip(i)" @mouseleave="leaveCat" @focus="catTip(i)" @click="emit('open',{kind:'category',index:i})" @keydown.enter="emit('open',{kind:'category',index:i})">
     <rect :x="X.cat[0]" :y="catCY(i)-28" :width="X.cat[1]-X.cat[0]" height="56" rx="4"/>
     <circle :cx="X.cat[0]+16" :cy="catCY(i)" r="4" :fill="categoryColors[i]"/>
     <text :x="(X.cat[0]+X.cat[1])/2+6" :y="catCY(i)+5" text-anchor="middle" :font-size="fit(c.name,150,14.5)" font-weight="700">{{c.name}}</text>
    </g>
    <g v-for="r in rows" :key="r.c.id">
     <g class="ic-node co" :class="{dim:dim('co'+r.c.id)}" :style="{'--c':r.color}" role="button" tabindex="0" :aria-label="r.f.shortName" @mouseenter="companyTip($event,r)" @mousemove="move" @mouseleave="leave" @click="emit('open',{kind:'company',id:r.c.id})" @keydown.enter="emit('open',{kind:'company',id:r.c.id})">
      <rect :x="X.co[0]" :y="r.cy-30" :width="X.co[1]-X.co[0]" height="60" rx="4"/>
      <circle :cx="X.co[0]+15" :cy="r.cy-8" r="4.5" :fill="r.color"/>
      <text :x="X.co[0]+28" :y="r.cy-3" :font-size="fit(r.f.shortName,118,15)" font-weight="750">{{r.f.shortName}}</text>
      <text :x="X.co[0]+28" :y="r.cy+17" font-size="11.5" fill="#8a8286">{{r.c.entityScope==='enterprise'?r.c.category:'科研机构'}}</text>
     </g>
     <g v-for="b in prodBoxes(r)" :key="b.p.id" class="ic-node prod" :class="{dim:dim('p'+b.p.id)}" :style="{'--c':r.color}" role="button" tabindex="0" :aria-label="b.p.name" @mouseenter="productTip($event,r,b.p)" @mousemove="move" @mouseleave="leave" @click="emit('open',{kind:'product',id:b.p.id})" @keydown.enter="emit('open',{kind:'product',id:b.p.id})">
      <rect :x="X.prod[0]" :y="b.y" :width="X.prod[1]-X.prod[0]" :height="b.h" rx="3"/>
      <text :x="(X.prod[0]+X.prod[1])/2" :y="b.y+b.h/2+4.5" text-anchor="middle" :font-size="fit(b.p.name,172,b.h<30?12.5:13.5)" font-weight="650">{{b.p.name}}</text>
     </g>
     <g class="ic-node pat" :class="{dim:dim('pat'+r.c.id)}" role="button" tabindex="0" :aria-label="`${r.f.shortName}相关专利`" @mouseenter="patTip($event,r)" @mousemove="move" @mouseleave="leave" @click="emit('open',{kind:'patents',id:r.c.id})" @keydown.enter="emit('open',{kind:'patents',id:r.c.id})">
      <rect :x="X.pat[0]" :y="r.cy-28" :width="X.pat[1]-X.pat[0]" height="56" rx="4"/>
      <text :x="(X.pat[0]+X.pat[1])/2" :y="r.cy-1" text-anchor="middle" font-size="16.5" font-weight="760">{{fmtN(r.c.coverage.labeledPatents)}} 件</text>
      <text :x="(X.pat[0]+X.pat[1])/2" :y="r.cy+17" text-anchor="middle" font-size="11.5" fill="#8a8286">技术挂钩专利</text>
     </g>
     <g v-if="r.eco" class="ic-node eco" :class="{dim:dim('eco'+r.c.id)}" role="button" tabindex="0" :aria-label="`${r.f.shortName}经济指标`" @mouseenter="ecoTip($event,r)" @mousemove="move" @mouseleave="leave" @click="emit('open',{kind:'metrics',id:r.c.id})" @keydown.enter="emit('open',{kind:'metrics',id:r.c.id})">
      <rect :x="X.eco[0]" :y="r.cy-28" :width="X.eco[1]-X.eco[0]" height="56" rx="4"/>
      <text :x="(X.eco[0]+X.eco[1])/2" :y="r.cy-7" text-anchor="middle" :font-size="fit(ecoTitle(r),164,11.5)" fill="#8a8286">{{ecoTitle(r)}}</text>
      <text :x="(X.eco[0]+X.eco[1])/2" :y="r.cy+15" text-anchor="middle" class="val" :font-size="fit(compactValue(r.eco),164,16.5)" font-weight="780">{{compactValue(r.eco)}}</text>
     </g>
    </g>
    <text v-if="!rows.length" :x="X.co[0]" y="110" font-size="15" fill="#8a8286">当前筛选下没有精选主体，可在下方“分析对象”按技术点查看全部关联产品。</text>
    <g v-if="panel" class="ic-panel" @mouseenter="catTip(panel.i)" @mouseleave="leaveCat">
     <rect class="ic-panel-bg" :x="X.cat[0]-6" :y="panel.y" :width="X.cat[1]-X.cat[0]+12" :height="panel.h" rx="6" :stroke="categoryColors[panel.i]"/>
     <g class="ic-panel-links"><template v-for="l in panel.leaves" :key="l.t.id"><path v-for="(k,j) in l.links" :key="j" :d="curve(X.cat[1]+6,l.y,X.prod[0],k.py)" :stroke="k.r.color" :class="{on:hover?.type==='leaf'&&hover.id===l.t.id}"/></template></g>
     <g class="ic-node cat open" role="button" tabindex="0" @click="emit('open',{kind:'category',index:panel.i})" @keydown.enter="emit('open',{kind:'category',index:panel.i})">
      <circle :cx="X.cat[0]+14" :cy="panel.y+24" r="4" :fill="categoryColors[panel.i]"/>
      <text :x="X.cat[0]+26" :y="panel.y+29" font-size="14.5" font-weight="750">{{panel.g.name}}</text>
     </g>
     <g v-for="l in panel.leaves" :key="l.t.id" class="ic-node leaf" :class="{dim:hover?.type==='leaf'&&hover.id!==l.t.id,has:l.links.length}" role="button" tabindex="0" :aria-label="l.t.name" @mouseenter="leafTip($event,l.t,panel.i)" @mousemove="move" @click="emit('open',{kind:'tech',id:l.t.id})" @keydown.enter="emit('open',{kind:'tech',id:l.t.id})">
      <rect :x="X.cat[0]+4" :y="l.y-12" :width="X.cat[1]-X.cat[0]-8" height="24" rx="3"/>
      <text :x="X.cat[0]+14" :y="l.y+4.5" :font-size="fit(l.t.name,166,12.5)">{{l.t.name}}</text>
     </g>
    </g>
   </svg></div>
   <div class="ic-legend"><span><i></i>来源记录关联</span><span><i class="dash"></i>机构层面关联</span></div>
  </div>
  <Teleport to="body"><div v-if="tip.show" class="rs-tip ic-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div></Teleport>
 </section>
</template>
