<script setup>
/* 投入产出对照：每个技术大类一张卡片（中线以上投入、以下产出），每行两张；点击展开该方向的完整指标 */
import {computed,ref} from 'vue'
import {ORDER,PALETTE,fmt} from '../../helpers/investData'
const props=defineProps({curves:Object})
const Y=computed(()=>props.curves.years),L=computed(()=>props.curves.layers)
const sel=ref('AI2')
const sum=a=>a.reduce((x,y)=>x+y,0)
const stat=id=>{const l=L.value[id],f=sum(l.funding),p=sum(l.papers),t=sum(l.patents);return {f,p,t,pp:p/(f/1000),tp:t/(f/1000)}}
function smooth(p){let d=`M${p[0][0]},${p[0][1]}`;for(let i=1;i<p.length;i++){const [a,b]=p[i-1],[c,e]=p[i],m=(a+c)/2;d+=` C${m},${b} ${m},${e} ${c},${e}`}return d}
function chart(id,w,h,big){
 const l=L.value[id],x0=big?46:4,x1=w-(big?16:4),mid=h*(big?.52:.5),up=mid-(big?40:6),dn=h-mid-(big?24:6)
 const X=i=>x0+i*(x1-x0)/(Y.value.length-1)
 const mf=Math.max(...l.funding)||1,mp=Math.max(...l.papers)||1,mt=Math.max(...l.patents)||1
 const f=l.funding.map((v,i)=>[X(i),mid-4-v/mf*up]),p=l.papers.map((v,i)=>[X(i),mid+4+v/mp*dn]),t=l.patents.map((v,i)=>[X(i),mid+4+v/mt*dn*.8])
 const pk=l.funding.indexOf(mf),pp=l.papers.indexOf(mp)
 return {w,h,mid,x0,x1,up,dn,fund:`${smooth(f)} L${x1},${mid-4} L${x0},${mid-4}Z`,pap:`${smooth(p)} L${x1},${mid+4} L${x0},${mid+4}Z`,pat:smooth(t),
  ticks:Y.value.map((y,i)=>({x:X(i),y})),pk:{x:X(pk),y:f[pk][1],v:mf,yr:Y.value[pk]},pp:{x:X(pp),y:p[pp][1],v:mp,yr:Y.value[pp]}}
}
const rows=computed(()=>{const out=[];for(let i=0;i<ORDER.length;i+=2)out.push(ORDER.slice(i,i+2));return out})
const selStat=computed(()=>stat(sel.value))
const big=computed(()=>chart(sel.value,620,330,true))
const bars=a=>{const m=Math.max(...a)||1;return a.map(v=>Math.max(2,v/m*24))}
const metricRows=computed(()=>{const l=L.value[sel.value],c=PALETTE[sel.value],s=selStat.value;return [
 {g:'投入',gc:c,items:[{n:'在研经费',u:'万元',bars:bars(l.funding),c,v:(s.f/1e4).toFixed(2),vu:'亿元'},{n:'在研项目数',u:'项'}]},
 {g:'论文',gc:'#3f6f9e',items:[{n:'基金支持论文',u:'篇',bars:bars(l.papers),c:'#3f6f9e',v:fmt(s.p),vu:'篇'},{n:'篇均被引',u:'次'},{n:'期刊影响因子',u:'中位数'},{n:'全库同方向论文',u:'篇'}]},
 {g:'专利',gc:'#b2772a',items:[{n:'基金支持专利',u:'件',bars:bars(l.patents),c:'#b2772a',v:fmt(s.t),vu:'件'},{n:'企业认领',u:'件'},{n:'关联产品',u:'件'}]}]})
const lead=computed(()=>{
 const tot=k=>Y.value.map((_,i)=>ORDER.reduce((a,id)=>a+L.value[id][k][i],0))
 const f=tot('funding'),p=tot('papers'),fy=Y.value[f.indexOf(Math.max(...f))],py=Y.value[p.indexOf(Math.max(...p))]
 const eff=ORDER.map(id=>({id,v:stat(id).pp})).sort((a,b)=>b.v-a.v).slice(0,2)
 return {fy,lag:py-fy,eff}
})
function toggle(id){sel.value=sel.value===id?'':id}
</script>

<template><div class="ic">
 <header class="ic-head"><h3>七大技术方向的投入与产出</h3><span>2017—2022 年立项项目 · 按执行与发表、申请年份</span></header>
 <p class="ic-lead">在研经费在 <em>{{lead.fy}} 年</em>前后达到峰值，关联论文峰值滞后约 <em>{{lead.lag}} 年</em>；<em>{{L[lead.eff[0].id].name}}</em>、<em>{{L[lead.eff[1].id].name}}</em>每千万元经费的论文产出最高，分别为 {{lead.eff[0].v.toFixed(1)}} 篇和 {{lead.eff[1].v.toFixed(1)}} 篇。</p>
 <div class="ic-legend"><span><i class="a"></i>在研经费（中线以上）</span><span><i class="b"></i>基金支持论文（中线以下）</span><span><i class="c"></i>基金支持专利</span><span><i class="d"></i>在研项目数<em>待补</em></span><span><i class="e"></i>全库同方向论文 / 专利<em>待补</em></span><span class="ic-hint">点击卡片展开该方向的完整指标</span></div>
 <div class="ic-grid">
  <template v-for="(r,ri) in rows" :key="ri">
   <button v-for="id in r" :key="id" type="button" class="ic-card" :class="{on:sel===id}" :aria-expanded="sel===id" :style="{'--c':PALETTE[id]}" @click="toggle(id)">
    <div class="ic-chart"><h4><i></i>{{L[id].name}}</h4>
     <svg :viewBox="`0 0 420 150`" width="100%" aria-hidden="true"><template v-for="g in [chart(id,420,150,false)]" :key="id">
      <path :d="g.fund" :fill="PALETTE[id]" opacity=".85"/><path :d="g.pap" :fill="PALETTE[id]" opacity=".28"/><path :d="g.pat" fill="none" stroke="#b2772a" stroke-width="1.8"/>
      <line :x1="g.x0" :x2="g.x1" :y1="g.mid" :y2="g.mid" stroke="#cfc6c2"/>
      <text v-for="(t,k) in g.ticks" v-show="k%2===0" :key="t.y" :x="t.x" :y="g.mid+4" font-size="10" font-weight="700" fill="#7a7378" text-anchor="middle" dominant-baseline="middle" paint-order="stroke" stroke="#fff" stroke-width="4">{{String(t.y).slice(2)}}</text></template></svg></div>
    <div class="ic-kv"><div><span>在研经费</span><strong>{{(stat(id).f/1e4).toFixed(1)}}<small>亿元</small></strong></div><div><span>基金支持论文</span><strong>{{fmt(stat(id).p)}}<small>篇</small></strong></div><div><span>基金支持专利</span><strong>{{fmt(stat(id).t)}}<small>件</small></strong></div>
     <div class="eff"><span>每千万元经费产出</span><strong>{{stat(id).pp.toFixed(1)}}<small>篇论文</small>　{{stat(id).tp.toFixed(1)}}<small>件专利</small></strong></div></div>
   </button>
   <div v-if="ri===rows.length-1&&r.length===1" class="ic-card note"><b>读图方式</b><span>横轴为年份，中线以上为投入、以下为产出</span><span>每个方向按自身峰值缩放，看的是变化节奏</span><span>2024 年后回落是因为 2017—2022 年立项项目陆续结题</span></div>
   <div v-if="r.includes(sel)" class="ic-detail" :class="{right:r.indexOf(sel)===1}" :style="{'--c':PALETTE[sel]}">
    <div class="ic-big"><div class="ic-dh"><b>{{L[sel].name}}</b><span>再次点击卡片收起</span></div>
     <svg :viewBox="`0 0 ${big.w} ${big.h}`" width="100%" role="img" :aria-label="`${L[sel].name}的投入与产出`">
      <path :d="big.fund" :fill="PALETTE[sel]" opacity=".85"/><path :d="big.pap" :fill="PALETTE[sel]" opacity=".28"/><path :d="big.pat" fill="none" stroke="#b2772a" stroke-width="2.4"/>
      <line :x1="big.x0" :x2="big.x1" :y1="big.mid" :y2="big.mid" stroke="#cfc6c2"/>
      <text v-for="t in big.ticks" :key="t.y" :x="t.x" :y="big.mid+4" font-size="11.5" font-weight="700" fill="#7a7378" text-anchor="middle" dominant-baseline="middle" paint-order="stroke" stroke="#fff" stroke-width="4">{{t.y}}</text>
      <text x="0" :y="big.mid-big.up/2" font-size="13" font-weight="750" :fill="PALETTE[sel]">投入</text><text x="0" :y="big.mid+big.dn/2" font-size="13" font-weight="750" fill="#5d575b">产出</text>
      <text :x="big.pk.x" :y="big.pk.y-9" font-size="12.5" font-weight="750" text-anchor="middle" :fill="PALETTE[sel]">经费峰值 {{(big.pk.v/1e4).toFixed(2)}} 亿元 · {{big.pk.yr}}</text>
      <text :x="big.pp.x" :y="big.pp.y+17" font-size="12.5" font-weight="750" text-anchor="middle" fill="#5d575b">论文峰值 {{fmt(big.pp.v)}} 篇 · {{big.pp.yr}}</text>
     </svg></div>
    <div class="ic-table"><div class="ic-dh"><b>逐年指标</b><span>柱高为该指标在各年的相对大小</span></div>
     <table><thead><tr><th></th><th></th><th><div class="ic-yrs"><span v-for="y in Y" :key="y">{{String(y).slice(2)}}</span></div></th><th class="r">{{Y[0]}}—{{Y.at(-1)}}</th></tr></thead>
      <tbody><template v-for="g in metricRows" :key="g.g"><tr v-for="(m,k) in g.items" :key="m.n">
       <td v-if="k===0" class="g" :rowspan="g.items.length" :style="{background:g.gc}">{{g.g}}</td>
       <td class="l">{{m.n}}<small>{{m.u}}</small></td>
       <td><div v-if="m.bars" class="ic-sp"><i v-for="(b,j) in m.bars" :key="j" :style="{height:b+'px',background:m.c}"></i></div><div v-else class="ic-sp pend">数据补充中</div></td>
       <td class="v">{{m.v||'—'}}<small v-if="m.v">{{m.vu}}</small></td></tr></template></tbody></table></div>
   </div>
  </template>
 </div>
</div></template>

<style scoped>
.ic-head{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.ic-head h3{margin:0;font-size:21px;font-weight:750;color:#232930;padding-left:14px;border-left:4px solid #a21535;line-height:1.2}
.ic-head span{font-size:13.5px;color:#8a8286}
.ic-lead{margin:10px 0 14px;font-size:16px;font-weight:600;line-height:1.75;color:#2f2b2d}.ic-lead em{font-style:normal;color:#a21535}
.ic-legend{display:flex;flex-wrap:wrap;align-items:center;gap:8px 18px;margin:0 0 16px;font-size:12.5px;color:#5d575b}
.ic-legend i{display:inline-block;width:20px;height:10px;margin-right:6px;vertical-align:-1px;border-radius:2px}
.ic-legend i.a{background:#2c64a0;opacity:.85}.ic-legend i.b{background:#2c64a0;opacity:.28}.ic-legend i.c{height:0;border-top:2px solid #b2772a;border-radius:0}.ic-legend i.d{height:0;border-top:2px dashed #2f2b2d;opacity:.6;border-radius:0}.ic-legend i.e{height:0;border-top:2px dotted #7a7378;border-radius:0}
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
.ic-dh{display:flex;align-items:baseline;gap:10px;margin-bottom:6px}.ic-dh b{font-size:16.5px;font-weight:750}.ic-dh span{font-size:12.5px;color:#9a9296}
.ic-table table{width:100%;border-collapse:collapse;font-size:13px}
.ic-table th{padding:4px 0;font-size:12px;font-weight:500;color:#8a8286}.ic-table th.r{text-align:right}
.ic-yrs{display:flex;justify-content:space-between;padding:0 10px}
.ic-table td{padding:5px 0;border-top:1px solid #f1ebe8;vertical-align:middle}
.ic-table td.g{width:22px;writing-mode:vertical-rl;text-align:center;letter-spacing:2px;font-size:11.5px;font-weight:700;color:#fff}
.ic-table td.l{width:112px;padding-left:10px;font-weight:650;color:#3d3a3c}.ic-table td.l small{display:block;font-size:11px;font-weight:400;color:#9a9296}
.ic-table td.v{width:78px;text-align:right;font-weight:750;color:#2f2b2d;font-variant-numeric:tabular-nums}.ic-table td.v small{display:block;font-size:11px;font-weight:500;color:#9a9296}
.ic-sp{display:flex;align-items:flex-end;gap:4px;height:26px;padding:0 10px}.ic-sp i{flex:1;border-radius:2px 2px 0 0}
.ic-sp.pend{align-items:center;justify-content:center;margin:0 10px;padding:0;border:1px dashed #ddd3cf;border-radius:3px;background:repeating-linear-gradient(135deg,#fff 0 6px,#f6f2f1 6px 12px);font-size:11.5px;color:#9a9296}
@media(max-width:1180px){.ic-card{grid-template-columns:1fr}.ic-detail{grid-template-columns:1fr}}
@media(max-width:760px){.ic-grid{grid-template-columns:1fr}.ic-detail::before{display:none}.ic-hint{margin-left:0}.ic-lead{font-size:14.5px}}
</style>
