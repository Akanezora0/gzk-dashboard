<script setup>
/* 产业链分析 05 · 技术、产品与专利链路：技术点经产品和专利连接企业；或从企业展开技术点、产品、专利、关联企业与经营指标 */
import {ref,computed,watch} from 'vue'
import {useTip,textWidth,toggleFullscreen} from '../../helpers/strengthTip.js'
import {arr,fmtN,clip,techPatents,companyExtra,companyValue,metricRows,compactValue,period,metricTitle,introOf,productIntros} from '../../helpers/industryChain.js'
const props=defineProps({scope:Object,techMap:Object,featuredOrder:Array,featuredProducts:Object,shortName:Function,companyOf:Function})
const emit=defineEmits(['open'])
const {tip,show,move,hide}=useTip()
const box=ref(null),patents=ref(null),extra=ref(null),econ=ref([]),hover=ref(null),tick=ref(0)
watch(()=>props.scope?.key,async()=>{
 hover.value=null;patents.value=null;extra.value=null;econ.value=[]
 const s=props.scope
 if(!s.isCompany){const all=await techPatents().catch(()=>({}));patents.value=all[s.id]||{total:0,patents:[]}}
 else{const [x,v]=await Promise.all([companyExtra(s.id),companyValue(s.id)]);extra.value=x||{patents:[],related:[]};const c=s.companies[0];econ.value=c?metricRows(c,v).slice(0,3):[]}
 productIntros(products.value).then(()=>tick.value++).catch(()=>{})
},{immediate:true})
const preferred=computed(()=>new Set(props.featuredOrder))
// 技术点模式：优先精选主体，每家取 1 项，最多 3 项
const products=computed(()=>{
 const s=props.scope
 if(s.isCompany){const pref=arr(props.featuredProducts?.[s.id]);const rank=p=>{const i=pref.indexOf(p.id);return i<0?pref.length:i};return s.products.slice().sort((a,b)=>rank(a)-rank(b)).slice(0,3)}
 const ranked=s.products.slice().sort((a,b)=>Number(b.companyIds.some(id=>preferred.value.has(id)))-Number(a.companyIds.some(id=>preferred.value.has(id))))
 const seen=new Set(),out=[]
 for(const p of ranked){const o=p.companyIds.find(id=>preferred.value.has(id))||p.companyIds[0];if(!seen.has(o)){out.push(p);seen.add(o)}if(out.length===3)break}
 for(const p of ranked){if(out.length===3)break;if(!out.includes(p))out.push(p)}
 return out
})
const techs=computed(()=>{
 if(!props.scope.isCompany)return []
 const groups=products.value.map(p=>[...new Set(arr(p.technologyIds))].filter(id=>props.techMap.has(id))),sel=[]
 for(let r=0;r<Math.max(0,...groups.map(g=>g.length))&&sel.length<6;r++)for(const g of groups){if(g[r]&&!sel.includes(g[r]))sel.push(g[r]);if(sel.length===6)break}
 return sel.map(id=>props.techMap.get(id))
})
const allTechCount=computed(()=>new Set(props.scope.products.flatMap(p=>arr(p.technologyIds).filter(id=>props.techMap.has(id)))).size)
const ownerOf=p=>p.companyIds.find(id=>preferred.value.has(id))||p.companyIds[0]
const G={green:'#3f8a80',violet:'#7a6aa2',slate:'#5f7392',amber:'#ad7d55'}
const fit=(t,w,size)=>Math.min(size,size*w/Math.max(1,textWidth(t,size)))
// 布局
const model=computed(()=>{
 tick.value
 const s=props.scope,nodes=[],edges=[],heads=[]
 const node=(n)=>{nodes.push(n);return n}
 if(!s.isCompany){
  const t=props.techMap.get(s.id),focus=node({key:'focus',x:20,y:206,w:230,h:68,title:t?.name||s.title,sub:t?.level1||'',main:true,open:{kind:'tech',id:s.id},tip:['专业技术点',t?.name,t?.definition]})
  heads.push({x:330,y:30,t:'产品路径',n:`${fmtN(s.products.length)} 项相关产品中的 ${products.value.length} 项`},{x:780,y:30,t:'关联企业',n:'产品所属主体与专利归集主体'},{x:330,y:262,t:'专利路径',n:`${fmtN(patents.value?.total||0)} 件匹配专利中的 ${Math.min(3,arr(patents.value?.patents).length)} 件`})
  products.value.forEach((p,i)=>{
   const y=52+i*62,n=node({key:'p'+i,x:330,y,w:300,h:46,title:p.name,color:G.green,open:{kind:'product',id:p.id},tip:['产品与服务',p.name,introOf(p.id)||'']})
   edges.push({a:'focus',b:n.key,d:`M250,240 C290,240 290,${y+23} 330,${y+23}`,color:G.green})
   const o=ownerOf(p);if(o){const c=node({key:'pc'+i,x:780,y,w:240,h:46,title:props.shortName(o),sub:props.companyOf(o)?.category||'',color:G.slate,open:{kind:'company',id:o},tip:['产品提供主体',props.shortName(o),'']});edges.push({a:n.key,b:c.key,d:`M630,${y+23} H780`,color:G.green})}
  })
  arr(patents.value?.patents).slice(0,3).forEach((p,i)=>{
   const y=284+i*62,n=node({key:'t'+i,x:330,y,w:300,h:46,title:p.title,color:G.violet,dashed:p.matchType==='nearest',open:{kind:'patent',patent:p},tip:['专利 · '+({direct:'直接对应',semantic:'语义对应',nearest:"相近技术"}[p.matchType]||'技术关联'),p.title,clip(p.abstract,120)]})
   edges.push({a:'focus',b:n.key,d:`M250,240 C290,240 290,${y+23} 330,${y+23}`,color:G.violet,dashed:p.matchType==='nearest'})
   if(p.companyId){const c=node({key:'tc'+i,x:780,y,w:240,h:46,title:props.shortName(p.companyId),sub:'专利归集主体',color:G.slate,open:{kind:'company',id:p.companyId},tip:['专利归集主体',props.shortName(p.companyId),p.applicants||'']});edges.push({a:n.key,b:c.key,d:`M630,${y+23} H780`,color:G.violet})}
  })
  return {nodes,edges,heads,h:480,focus}
 }
 const c=s.companies[0]
 node({key:'focus',x:20,y:150,w:230,h:68,title:props.shortName(s.id),sub:c?.category||'',main:true,open:{kind:'company',id:s.id},tip:['分析主体',c?.name||s.title,'技术关联由该主体产品的技术映射汇总。']})
 heads.push({x:330,y:30,t:'技术点',n:`${fmtN(allTechCount.value)} 项中的 ${techs.value.length} 项`},{x:780,y:30,t:'产品与服务',n:`${fmtN(s.products.length)} 项中的 ${products.value.length} 项`})
 const tStep=techs.value.length>1?Math.min(52,250/(techs.value.length-1)):0
 techs.value.forEach((t,i)=>{
  const y=52+i*tStep,n=node({key:'ct'+t.id,x:330,y,w:300,h:38,title:t.name,color:G.violet,open:{kind:'tech',id:t.id},tip:[t.level1,t.name,t.definition]})
  edges.push({a:'focus',b:n.key,d:`M250,184 C290,184 290,${y+19} 330,${y+19}`,color:G.violet})
  products.value.forEach((p,j)=>{if(arr(p.technologyIds).includes(t.id))edges.push({a:n.key,b:'cp'+j,d:`M630,${y+19} C705,${y+19} 705,${75+j*100} 780,${75+j*100}`,color:G.green})})
 })
 products.value.forEach((p,j)=>node({key:'cp'+j,x:780,y:52+j*100,w:300,h:46,title:p.name,color:G.green,open:{kind:'product',id:p.id},tip:['产品与服务',p.name,introOf(p.id)||'']}))
 const ex=extra.value||{patents:[],related:[]}
 heads.push({x:20,y:376,t:'关联企业',n:`${fmtN(ex.relatedTotal||0)} 条已归档关系`},{x:420,y:376,t:'相关专利',n:`${fmtN(c?.labeledPatents||0)} 件已挂钩技术`},{x:820,y:376,t:'经济指标',n:'按指标与观察期披露'})
 const lower=(key,x,i)=>edges.push({a:'focus',b:key,d:`M135,218 V${352+i*0} H${x+150} V${398+i*58}`,color:'#c9bfc2',soft:true})
 arr(ex.related).slice(0,3).forEach((r,i)=>{const k='cr'+i;node({key:k,x:20,y:398+i*58,w:330,h:44,title:r.name,sub:r.relation||'',color:G.slate,open:r.companyId?{kind:'company',id:r.companyId}:null,tip:['关联企业',r.name,r.relation||'']});lower(k,20,i)})
 arr(ex.patents).slice(0,3).forEach((p,i)=>{const k='ck'+i;node({key:k,x:420,y:398+i*58,w:330,h:44,title:p.title,sub:p.applicationNumber||'',color:G.violet,open:{kind:'patent',patent:p},tip:['专利',p.title,clip(p.abstract,120)]});lower(k,420,i)})
 econ.value.forEach((r,i)=>{const k='ce'+i;node({key:k,x:820,y:398+i*58,w:330,h:44,title:metricTitle(r),sub:`${compactValue(r)} · ${period(r)}`,color:G.amber,open:{kind:'metric',row:r},tip:['经济指标',metricTitle(r),`${compactValue(r)} · ${period(r)}`]});lower(k,820,i)})
 return {nodes,edges,heads,h:590}
})
const linked=computed(()=>{const k=hover.value;if(!k)return null;const set=new Set([k]);model.value.edges.forEach(e=>{if(e.a===k||e.b===k){set.add(e.a);set.add(e.b)}});return set})
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))
function enter(e,n){hover.value=n.key;const [k,t,b]=n.tip||[];show(e,`<span class="ic-tip-k">${esc(k)}</span><b class="ic-tip-t">${esc(t)}</b>${b?`<p>${esc(clip(b,140))}</p>`:''}`)}
function leave(){hover.value=null;hide()}
</script>
<template>
 <section class="rs-page ic-sec">
  <header class="rs-head"><span class="rs-no">05</span><h3>技术、产品与专利链路</h3></header>
  <p class="rs-lead soft"><template v-if="!scope.isCompany">{{scope.title}}分别经产品与专利连接到企业，形成从技术到产业主体的两条路径。</template><template v-else>{{shortName(scope.id)}}从产品的技术映射展开，连接技术点、产品与服务，并延伸到关联企业、相关专利和经济指标。</template></p>
  <div ref="box" class="ic-board">
   <div class="ic-tools"><span class="ic-tools-t">{{scope.isCompany?'企业链路':'技术链路'}} · {{scope.title}}</span><span class="ic-grow"></span><button class="rs-btn" @click="toggleFullscreen(box)">全屏</button></div>
   <div class="rs-scroll ic-gwrap"><svg class="ic-graph ic-chain" :class="{focus:!!linked}" :viewBox="`0 0 1180 ${model.h}`" role="img" :aria-label="`${scope.title}的技术、产品与专利链路`" @mouseleave="leave">
    <g v-for="h in model.heads" :key="h.t" class="ic-chead"><text :x="h.x" :y="h.y" class="t">{{h.t}}</text><text :x="h.x" :y="h.y+18" class="n">{{h.n}}</text></g>
    <g class="ic-edges"><path v-for="(e,i) in model.edges" :key="i" :d="e.d" :stroke="e.color" :class="{on:linked&&linked.has(e.a)&&linked.has(e.b),soft:e.soft}" :stroke-dasharray="e.dashed||e.soft?'4 4':null"/></g>
    <g v-for="n in model.nodes" :key="n.key" class="ic-node" :class="{main:n.main,dim:linked&&!linked.has(n.key),link:!!n.open}" :style="{'--c':n.color||'#a21535'}" :role="n.open?'button':null" :tabindex="n.open?0:null" :aria-label="n.title" @mouseenter="enter($event,n)" @mousemove="move" @mouseleave="leave" @click="n.open&&emit('open',n.open)" @keydown.enter="n.open&&emit('open',n.open)">
     <rect :x="n.x" :y="n.y" :width="n.w" :height="n.h" rx="4"/>
     <circle v-if="!n.main" :cx="n.x+14" :cy="n.y+n.h/2-(n.sub?7:0)" r="3.5" :fill="n.color"/>
     <text :x="n.main?n.x+n.w/2:n.x+26" :y="n.y+n.h/2+(n.sub?-3:5)" :text-anchor="n.main?'middle':'start'" :font-size="fit(n.title,n.w-(n.main?24:40),n.main?16:13.5)" font-weight="700">{{n.title}}</text>
     <text v-if="n.sub" :x="n.main?n.x+n.w/2:n.x+26" :y="n.y+n.h/2+15" :text-anchor="n.main?'middle':'start'" font-size="11.5" class="sub">{{clip(n.sub,34)}}</text>
    </g>
    <text v-if="!products.length" x="330" y="80" font-size="14" fill="#8a8286">该技术点下没有已采纳产品</text>
   </svg></div>
   <div class="ic-legend"><span><i class="g"></i>产品路径</span><span><i class="v"></i>专利路径</span><span><i class="dash"></i>相近技术专利 · 关联主体</span></div>
  </div>
  <Teleport to="body"><div v-if="tip.show" class="rs-tip ic-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div></Teleport>
 </section>
</template>
