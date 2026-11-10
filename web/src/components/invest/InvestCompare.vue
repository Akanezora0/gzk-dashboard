<script setup>
/* 七类卡片与展开表保留原布局；总额和均值只读取明确口径的统计字段。 */
import {computed,ref} from 'vue'
import {ORDER,PALETTE,fmt} from '../../helpers/investData'
const props=defineProps({curves:Object})
const M=computed(()=>props.curves.metrics)
const Y=computed(()=>M.value.years)
const L=computed(()=>Object.fromEntries(M.value.categories.map(c=>[c.id,{...c,funding:c.series.active_funding_wan,papers:c.series.funded_papers,patents:c.series.funded_patents}])))
const sel=ref(ORDER[0])
const known=v=>typeof v==='number'&&Number.isFinite(v)
const show=v=>known(v)?fmt(v):'—'
const decimal=v=>known(v)?v.toFixed(2):'—'
const peak=a=>Math.max(0,...a.filter(known))
const stat=id=>{const t=L.value[id].totals;return {f:t.approved_funding_wan,p:t.funded_papers,t:t.funded_patents,projects:t.project_count}}
function smooth(p){if(!p.length)return '';let d=`M${p[0][0]},${p[0][1]}`;for(let i=1;i<p.length;i++){const [a,b]=p[i-1],[c,e]=p[i],m=(a+c)/2;d+=` C${m},${b} ${m},${e} ${c},${e}`}return d}
const PAPER='#3f6f9e',PATENT='#b2772a'
function niceMax(v){if(!(v>0))return 1;const e=10**Math.floor(Math.log10(v)),n=v/e;return (n<=1?1:n<=2?2:n<=2.5?2.5:n<=5?5:10)*e}
const short=v=>v>=1e4?`${+(v/1e4).toFixed(v>=1e5?0:1)}万`:fmt(v)
/* 上：在研经费（面积，万元）与在研项目数（点线，项）；下：论文、专利两个区带，浅色为全库同方向、深色为其中的基金关联成果，同一平方根刻度 */
function chart(id,w,h,big){
 const l=L.value[id],s=l.series,x0=big?58:6,x1=w-(big?50:6)
 const X=i=>x0+i*(x1-x0)/Math.max(1,Y.value.length-1)
 const Z=big?{top:30,base:170,axis:183,out:[198,400]}:{top:6,base:72,axis:81,out:[90,166]}
 const mf=niceMax(peak(s.active_funding_wan)),mj=niceMax(peak(s.active_projects))
 const fy=v=>Z.base-(v||0)/mf*(Z.base-Z.top),jy=v=>Z.base-(v||0)/mj*(Z.base-Z.top)
 const f=s.active_funding_wan.map((v,i)=>[X(i),fy(v)]),j=s.active_projects.map((v,i)=>[X(i),jy(v)])
 const [o0,o1]=Z.out,om=niceMax(Math.max(peak(s.all_papers),peak(s.all_patents))),OY=v=>o0+Math.sqrt(Math.max(0,v||0)/om)*(o1-o0)
 const pts=a=>a.map((v,i)=>[X(i),OY(v)]),area=a=>`${smooth(pts(a))} L${x1},${o0} L${x0},${o0}Z`
 const out={y0:o0,y1:o1,papAll:area(s.all_papers),papFund:area(s.funded_papers),patAll:smooth(pts(s.all_patents)),patFund:smooth(pts(s.funded_patents)),ticks:[om,om/4,om/25].map(v=>({v,y:OY(v)}))}
 const pk=Math.max(0,s.active_funding_wan.indexOf(peak(s.active_funding_wan)))
 const anchor=i=>X(i)<w*.25?'start':X(i)>w*.75?'end':'middle'
 return {w,h,x0,x1,Z,fund:`${smooth(f)} L${x1},${Z.base} L${x0},${Z.base}Z`,proj:smooth(j),dots:j,
  fTicks:[mf,mf/2].map(v=>({v,y:fy(v)})),jTicks:[mj,mj/2].map(v=>({v,y:jy(v)})),
  out,
  ticks:Y.value.map((y,i)=>({x:X(i),y})),pk:{x:X(pk),y:f[pk][1],v:peak(s.active_funding_wan),yr:Y.value[pk],anchor:anchor(pk)}}
}
const rows=computed(()=>{const out=[];for(let i=0;i<ORDER.length;i+=2)out.push(ORDER.slice(i,i+2));return out})
const big=computed(()=>sel.value?chart(sel.value,620,436,true):null)
const bars=a=>{const m=peak(a)||1;return a.map(v=>({v,missing:!known(v),height:known(v)?(v>0?Math.max(2,v/m*24):0):0}))}
const metricRows=computed(()=>{
 if(!sel.value)return []
 const l=L.value[sel.value],c=PALETTE[sel.value],s=l.series,t=l.totals
 const item=(n,u,key,color,total,vu,dec=false)=>({n,u,bars:bars(s[key]),c:color,v:dec?decimal(total):show(total),vu})
 return [
  {g:'投入',gc:c,items:[
   {n:'在研经费',u:'万元',bars:bars(s.active_funding_wan),c,v:decimal(peak(s.active_funding_wan)/1e4),vu:'亿元 · 年度峰值'},
   item('在研项目数','项','active_projects',c,peak(s.active_projects),'项 · 年度峰值')]},
  {g:'论文',gc:'#3f6f9e',items:[
   item('基金关联论文','篇','funded_papers','#3f6f9e',t.funded_papers,'篇'),
   item('新增引证记录','次 · 按引证年','paper_citations','#3f6f9e',t.paper_citations,'次'),
   item('三年篇均被引','次 · 按发表年','mean_citations_3y','#3f6f9e',t.mean_citations_3y,'次 · 成熟队列',true),
   item('全库同方向论文','篇','all_papers','#8299b0',t.all_papers,'篇')]},
  {g:'专利',gc:'#b2772a',items:[
   item('基金关联专利','件','funded_patents','#b2772a',t.funded_patents,'件'),
   item('企业参与专利','件','enterprise_patents','#b2772a',t.enterprise_patents,'件'),
   item('全库同方向专利','件','all_patents','#c8a575',t.all_patents,'件')]}
 ]
})
const citationCoverage=computed(()=>L.value[sel.value]?.coverage?.citation_eligible_papers)
function toggle(id){sel.value=sel.value===id?'':id}
</script>

<template><div class="ic">
 <header class="ic-head"><h3>七大技术方向基金投入与论文专利产出</h3></header>
 <p class="ic-lead">在研经费与在研项目数展示各方向逐年的基金投入，论文、专利同时给出全库同方向规模与其中的基金关联成果。</p>
 <div class="ic-grid">
  <template v-for="(r,ri) in rows" :key="ri">
   <button v-for="id in r" :key="id" type="button" class="ic-card" :class="{on:sel===id}" :aria-expanded="sel===id" :style="{'--c':PALETTE[id]}" @click="toggle(id)">
    <div class="ic-chart"><h4><i></i>{{L[id].name}}</h4>
     <svg viewBox="0 0 420 170" width="100%" aria-hidden="true"><template v-for="g in [chart(id,420,170,false)]" :key="id">
      <path :d="g.fund" :fill="PALETTE[id]" opacity=".8"/><path :d="g.proj" fill="none" :stroke="PALETTE[id]" stroke-width="1.6" stroke-dasharray="1 0"/><circle v-for="(d,k) in g.dots" :key="k" :cx="d[0]" :cy="d[1]" r="2.2" fill="#fff" :stroke="PALETTE[id]" stroke-width="1.4"/>
      <path :d="g.out.papAll" :fill="PAPER" opacity=".18"/><path :d="g.out.papFund" :fill="PAPER" opacity=".85"/>
      <path :d="g.out.patAll" fill="none" :stroke="PATENT" stroke-width="1.4" stroke-dasharray="4 3"/><path :d="g.out.patFund" fill="none" :stroke="PATENT" stroke-width="1.8"/>
      <line :x1="g.x0" :x2="g.x1" :y1="g.Z.base" :y2="g.Z.base" stroke="#cfc6c2"/>
      <text v-for="(t,k) in g.ticks" v-show="k%2===0" :key="t.y" :x="t.x" :y="g.Z.axis" font-size="10" font-weight="700" fill="#7a7378" text-anchor="middle" dominant-baseline="middle">{{String(t.y).slice(2)}}</text></template></svg></div>
    <div class="ic-kv"><div><span>项目批准经费</span><strong>{{(stat(id).f/1e4).toFixed(1)}}<small>亿元</small></strong></div><div><span>基金关联论文</span><strong>{{show(stat(id).p)}}<small>篇</small></strong></div><div><span>基金关联专利</span><strong>{{show(stat(id).t)}}<small>件</small></strong></div>
     <div class="eff"><span>覆盖项目</span><strong>{{show(stat(id).projects)}}<small>项</small></strong></div></div>
   </button>
   <div v-if="ri===rows.length-1&&r.length===1" class="ic-card note"><b>读图方式</b><span>横轴为年份；上方面积为在研经费，点线为在研项目数</span><span>下方面积为论文：浅色全库同方向、深色基金关联</span><span>下方虚线为全库同方向专利，实线为基金关联专利</span></div>
   <div v-if="r.includes(sel)" class="ic-detail" :class="{right:r.indexOf(sel)===1}" :style="{'--c':PALETTE[sel]}">
    <div class="ic-big"><div class="ic-dh"><b>{{L[sel].name}}</b></div>
     <div class="ic-legend"><span><i class="a"></i>在研经费</span><span><i class="pj"></i>在研项目数</span><span><i class="pa"></i>全库同方向论文</span><span><i class="pf"></i>基金关联论文</span><span><i class="ta"></i>全库同方向专利</span><span><i class="tf"></i>基金关联专利</span></div>
     <svg :viewBox="`0 0 ${big.w} ${big.h}`" width="100%" role="img" :aria-label="`${L[sel].name}的基金投入与论文专利产出`">
      <g font-size="10.5" fill="#9a9296">
       <template v-for="t in big.fTicks" :key="'f'+t.v"><line :x1="big.x0" :x2="big.x1" :y1="t.y" :y2="t.y" stroke="#efe8e4" stroke-dasharray="3 3"/><text :x="big.x0-6" :y="t.y" text-anchor="end" dominant-baseline="middle">{{t.v>=1e4?`${+(t.v/1e4).toFixed(2)}亿`:`${fmt(t.v)}万`}}</text></template>
       <text v-for="t in big.jTicks" :key="'j'+t.v" :x="big.x1+6" :y="t.y" dominant-baseline="middle" :fill="PALETTE[sel]">{{fmt(t.v)}}项</text>
       <template v-for="t in big.out.ticks" :key="'o'+t.v"><line :x1="big.x0" :x2="big.x1" :y1="t.y" :y2="t.y" stroke="#efe8e4" stroke-dasharray="3 3"/><text :x="big.x0-6" :y="t.y" text-anchor="end" dominant-baseline="middle">{{short(t.v)}}</text></template>
      </g>
      <path :d="big.fund" :fill="PALETTE[sel]" opacity=".8"/>
      <path :d="big.proj" fill="none" :stroke="PALETTE[sel]" stroke-width="2"/><circle v-for="(d,k) in big.dots" :key="k" :cx="d[0]" :cy="d[1]" r="3.4" fill="#fff" :stroke="PALETTE[sel]" stroke-width="2"/>
      <path :d="big.out.papAll" :fill="PAPER" opacity=".18"/><path :d="big.out.papFund" :fill="PAPER" opacity=".85"/>
      <path :d="big.out.patAll" fill="none" :stroke="PATENT" stroke-width="2" stroke-dasharray="6 4"/><path :d="big.out.patFund" fill="none" :stroke="PATENT" stroke-width="2.6"/>
      <line :x1="big.x0" :x2="big.x1" :y1="big.Z.base" :y2="big.Z.base" stroke="#cfc6c2"/>
      <text v-for="t in big.ticks" :key="t.y" :x="t.x" :y="big.Z.axis" font-size="11.5" font-weight="700" fill="#7a7378" text-anchor="middle" dominant-baseline="middle">{{t.y}}</text>
      <text x="0" :y="big.Z.top+8" font-size="13" font-weight="750" :fill="PALETTE[sel]">投入</text>
      <text x="0" :y="big.out.y0+16" font-size="13" font-weight="750" fill="#5d575b">产出</text>
      <text :x="big.pk.x" :y="Math.max(12,big.pk.y-9)" font-size="12.5" font-weight="750" :text-anchor="big.pk.anchor" :fill="PALETTE[sel]">经费峰值 {{(big.pk.v/1e4).toFixed(2)}} 亿元 · {{big.pk.yr}}</text>
     </svg>
     <p class="ic-note">经费与项目数按执行年份统计；产出区论文与专利共用平方根刻度：面积为论文（浅色全库同方向、深色基金关联），虚线、实线分别为全库同方向专利与基金关联专利。</p></div>
    <div class="ic-table" tabindex="0" aria-label="逐年指标，可横向滚动"><div class="ic-dh"><b>逐年指标</b></div>
     <table><thead><tr><th></th><th></th><th><div class="ic-yrs"><span v-for="y in Y" :key="y">{{String(y).slice(2)}}</span></div></th><th class="r">期间汇总 / 峰值</th></tr></thead>
      <tbody><template v-for="g in metricRows" :key="g.g"><tr v-for="(m,k) in g.items" :key="m.n">
       <td v-if="k===0" class="g" :rowspan="g.items.length" :style="{background:g.gc}">{{g.g}}</td>
       <td class="l">{{m.n}}<small>{{m.u}}</small></td>
       <td><div v-if="m.bars" class="ic-sp"><i v-for="(b,j) in m.bars" :key="j" :class="{missing:b.missing}" :style="{height:b.height+'px',background:m.c}"></i></div><div v-else class="ic-sp pend">{{m.pending||'待补充'}}</div></td>
       <td class="v">{{m.v??'—'}}<small v-if="m.v&&m.v!=='—'">{{m.vu}}</small></td></tr></template></tbody></table></div>
   </div>
  </template>
 </div>
 
</div></template>

<style scoped>
.ic-data-note{margin:12px 0 0;font-size:12px;line-height:1.7;color:#8a8286}.ic-sp i.missing{height:5px!important;background:transparent!important;border-bottom:1px dashed #cbbfc2}
.ic-head{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.ic-head h3{margin:0;font-size:21px;font-weight:750;color:#232930;padding-left:14px;border-left:4px solid #a21535;line-height:1.2}
.ic-head span{font-size:13.5px;color:#8a8286}
.ic-lead{margin:10px 0 14px;font-size:16px;font-weight:600;line-height:1.75;color:#2f2b2d}.ic-lead em{font-style:normal;color:#a21535}
.ic-legend{display:flex;flex-wrap:wrap;align-items:center;gap:8px 18px;margin:0 0 16px;font-size:12.5px;color:#5d575b}
.ic-legend i{display:inline-block;width:20px;height:10px;margin-right:6px;vertical-align:-1px;border-radius:2px}
.ic-legend i.a{background:var(--c);opacity:.8}.ic-legend i.pj{width:18px;height:0;border-top:2px solid var(--c);border-radius:0;position:relative}.ic-legend i.pa{background:#3f6f9e;opacity:.18}.ic-legend i.pf{background:#3f6f9e;opacity:.85}.ic-legend i.ta{height:0;border-top:2px dashed #b2772a;border-radius:0}.ic-legend i.tf{height:0;border-top:3px solid #b2772a;border-radius:0}.ic-note{margin:8px 0 0;font-size:12px;color:#8a8286}.ic-legend i.b{background:var(--c);opacity:.28}.ic-legend i.c{height:0;border-top:2px solid #b2772a;border-radius:0}.ic-legend i.d{height:0;border-top:2px dashed #2f2b2d;opacity:.6;border-radius:0}.ic-legend i.e{height:0;border-top:2px dotted #7a7378;border-radius:0}
.ic-legend em{margin-left:5px;padding:0 5px;font-style:normal;font-size:11px;color:#9a9296;border:1px dashed #cbbfc2;border-radius:2px}
.ic-hint{margin-left:auto;color:#9a9296}
.ic-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.ic-card{display:grid;grid-template-columns:minmax(0,1fr) 212px;gap:18px;align-items:center;padding:16px 20px 14px;border:1px solid #ece5e1;border-radius:4px;background:#fff;font:inherit;text-align:left;color:inherit;cursor:pointer;transition:border-color .2s,box-shadow .2s}
.ic-card:hover{border-color:#d9c3c8}
.ic-card.on{border-color:#a21535;box-shadow:0 0 0 1px #a21535}
.ic-card:focus-visible{outline:2px solid #a21535;outline-offset:2px}
.ic-chart h4{display:flex;align-items:center;gap:8px;margin:0 0 6px;font-size:16px;font-weight:750;color:#2f2b2d}
.ic-chart h4 i{width:10px;height:10px;border-radius:50%;background:var(--c)}
.ic-kv{display:flex;flex-direction:column}
.ic-kv>div{display:flex;justify-content:space-between;align-items:baseline;padding:6px 0;border-bottom:1px dashed #efe8e4;font-size:12.5px;color:#7a7378}
.ic-kv>div:last-child{border-bottom:0}
.ic-kv strong{font-size:18px;font-weight:800;color:#2f2b2d;font-variant-numeric:tabular-nums}
.ic-kv small{margin-left:3px;font-size:11.5px;font-weight:500;color:#7a7378}
.ic-kv .eff{flex-direction:column;align-items:flex-start;gap:2px}.ic-kv .eff strong{color:#a21535}
.ic-card.note{grid-template-columns:1fr;align-content:center;gap:4px;background:#fcfaf9;cursor:default;font-size:13px;line-height:1.8;color:#5d575b}
.ic-card.note b{font-size:15px;color:#2f2b2d}
.ic-detail{position:relative;grid-column:1/-1;display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:26px;padding:20px 22px;border:1px solid #e9c3cb;border-radius:4px;background:#fffafa}
.ic-detail::before{content:"";position:absolute;top:-9px;left:25%;width:16px;height:16px;background:#fffafa;border-left:1px solid #e9c3cb;border-top:1px solid #e9c3cb;transform:rotate(45deg)}
.ic-detail.right::before{left:75%}
.ic-big{display:flex;flex-direction:column;min-width:0}.ic-big>svg{display:block;flex:none;margin-block:auto}.ic-dh{display:flex;align-items:baseline;gap:10px;margin-bottom:6px}.ic-dh b{font-size:16.5px;font-weight:750}.ic-dh span{font-size:12.5px;color:#9a9296}
.ic-table{min-width:0;overflow-x:auto}.ic-scroll-hint{display:none}
.ic-table table{width:100%;border-collapse:collapse;font-size:13px}
.ic-table th{padding:4px 0;font-size:12px;font-weight:500;color:#8a8286}.ic-table th.r{text-align:right}
.ic-yrs{display:flex;justify-content:space-between;padding:0 10px}
.ic-table td{padding:5px 0;border-top:1px solid #f1ebe8;vertical-align:middle}
.ic-table td.g{width:22px;writing-mode:vertical-rl;text-align:center;letter-spacing:2px;font-size:11.5px;font-weight:700;color:#fff}
.ic-table td.l{width:112px;padding-left:10px;font-weight:650;color:#3d3a3c}.ic-table td.l small{display:block;font-size:11px;font-weight:400;color:#9a9296}
.ic-table td.v{width:98px;text-align:right;font-weight:750;color:#2f2b2d;font-variant-numeric:tabular-nums}.ic-table td.v small{display:block;font-size:11px;font-weight:500;color:#9a9296}
.ic-sp{display:flex;align-items:flex-end;gap:4px;height:26px;padding:0 10px}.ic-sp i{flex:1;border-radius:2px 2px 0 0}
.ic-sp.pend{align-items:center;justify-content:center;margin:0 10px;padding:0;border:1px dashed #ddd3cf;border-radius:3px;background:repeating-linear-gradient(135deg,#fff 0 6px,#f6f2f1 6px 12px);font-size:11.5px;color:#9a9296}
@media(max-width:1180px){.ic-card{grid-template-columns:1fr}.ic-detail{grid-template-columns:minmax(0,1fr)}}
@media(max-width:760px){.ic-table table{min-width:490px}.ic-scroll-hint{display:block;margin:0 0 8px;font-size:11px;color:#9a9296}.ic-grid{grid-template-columns:1fr}.ic-detail::before{display:none}.ic-hint{margin-left:0}.ic-lead{font-size:14.5px}}
</style>
