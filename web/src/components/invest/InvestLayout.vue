<script setup>
/* 方向与技术点布局：01 总览（经费、成果并排动画）→ 02 结构（三组份额条）→ 03 细节（70 技术点） */
import {computed,ref,onMounted,onBeforeUnmount} from 'vue'
import {ORDER,PALETTE,fmt} from '../../helpers/investData'
const props=defineProps({curves:Object,terms:Object})
const Y=computed(()=>props.curves.years),L=computed(()=>props.curves.layers)
const last=computed(()=>Y.value.length-1)

/* 年份播放（01 与 03 各自一条时间轴；01 的两图同步） */
function player(){
 const i=ref(0),on=ref(false);let t
 const stop=()=>{clearInterval(t);on.value=false}
 const play=()=>{if(on.value){stop();return}if(i.value>=last.value)i.value=0;on.value=true;t=setInterval(()=>{if(i.value<last.value)i.value++;else stop()},1100)}
 const seek=k=>{stop();i.value=k}
 return {i,on,play,stop,seek}
}
const A=player(),T=player()
const root=ref(null),termEl=ref(null);let io
const reduced=()=>window.matchMedia('(prefers-reduced-motion: reduce)').matches
onMounted(()=>{
 A.i.value=last.value;T.i.value=last.value
 if(reduced()||!('IntersectionObserver' in window))return
 io=new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting)return;const p=e.target===root.value?A:T;p.i.value=0;p.play();io.unobserve(e.target)}),{threshold:.35})
 root.value&&io.observe(root.value);termEl.value&&io.observe(termEl.value)
})
onBeforeUnmount(()=>{A.stop();T.stop();io?.disconnect()})

/* 01 总览 */
const outKind=ref('papers')
const shade=t=>{const a=[246,233,236],b=[162,21,53];return 'rgb('+a.map((v,k)=>Math.round(v+(b[k]-v)*t)).join(',')+')'}
function panel(k){
 const yi=A.i.value,vals=ORDER.map(id=>({id,v:L.value[id][k][yi]})),tt=vals.reduce((a,b)=>a+b.v,0)
 const cum=ORDER.reduce((a,id)=>a+L.value[id][k].slice(0,yi+1).reduce((x,y)=>x+y,0),0)
 return {tt,cum,tiles:vals.sort((a,b)=>b.v-a.v).map((x,j)=>{const sh=tt?x.v/tt:0;return {...x,name:L.value[x.id].name,sh,big:j<2,bg:shade(Math.min(1,.12+sh*1.9)),dark:sh>.2}})}
}
const fundPanel=computed(()=>panel('funding')),outPanel=computed(()=>panel(outKind.value))
const unit=k=>k==='papers'?'篇':'件'
const share=(k,ids)=>{const t=(a)=>a.reduce((x,y)=>x+y,0);const all=t(ORDER.map(id=>t(L.value[id][k]))),part=t(ids.map(id=>t(L.value[id][k])));return Math.round(part/all*100)}
const lead1=computed(()=>({f:share('funding',['AI2','AI5']),p:share('papers',['AI2','AI5'])}))

/* 02 结构 */
function rows(k){return Y.value.map((y,i)=>{const tt=ORDER.reduce((a,id)=>a+L.value[id][k][i],0);let x=0;return {y,empty:!tt,segs:ORDER.map(id=>{const w=tt?L.value[id][k][i]/tt:0,s={id,x,w};x+=w;return s})}})}
const struct=computed(()=>[['funding','在研经费'],['papers','基金支持论文'],['patents','基金支持专利']].map(([k,t])=>({k,t,rows:rows(k)})))
const hl=ref(null)
const yShare=(k,id,i)=>{const tt=ORDER.reduce((a,x)=>a+L.value[x][k][i],0);return tt?L.value[id][k][i]/tt*100:0}
const lead2=computed(()=>{const i0=Y.value.indexOf(2021),i1=last.value;return {a0:Math.round(yShare('papers','AI1',i0)),a1:Math.round(yShare('papers','AI1',i1)),d0:Math.round(yShare('papers','AI6',i0)),d1:Math.round(yShare('papers','AI6',i1))}})

/* 03 细节：70 技术点 */
const termKind=ref('funding')
const cols=computed(()=>{
 const tr=props.terms;if(!tr)return []
 const fr=tr[termKind.value],yi=Math.min(T.i.value,fr.length-1),mx=tr.list.map((_,j)=>Math.max(...fr.map(f=>f.values[j]))||1)
 return ORDER.map(id=>({id,name:L.value[id].name,items:tr.list.map((t,j)=>({t,j})).filter(x=>x.t.category===id).map(({t,j})=>{const r=fr[yi].values[j]/mx[j],a=r>0?.15+.85*r:0;return {id:t.id,name:t.name.replace(/（[^）]*）/g,''),full:t.name,a,v:fr[yi].values[j]}})}))
})
const hex=a=>Math.round(a*255).toString(16).padStart(2,'0')
const termUnit=computed(()=>({funding:'万元',papers:'篇',patents:'件'})[termKind.value])
</script>

<template><div class="il">
 <section ref="root" class="il-sec">
  <header><b>01</b><h3>总览：经费与成果投向哪些方向</h3><span>2017—2022 年立项项目 · 跨方向分摊计入</span></header>
  <p class="il-lead"><em>模型训练、适配与推理</em>和<em>知识增强与 AI 应用</em>是投入与产出最集中的两个方向，合计约占经费的 <em>{{lead1.f}}%</em>、论文的 <em>{{lead1.p}}%</em>。</p>
  <div class="il-two">
   <div v-for="(pn,k) in [{p:fundPanel,key:'funding'},{p:outPanel,key:outKind}]" :key="k" class="il-panel">
    <div class="il-ph">
     <div><h4>{{k===0?'经费投入':'成果产出'}}<span v-if="k===1" class="il-seg"><button :class="{on:outKind==='papers'}" @click="outKind='papers'">论文</button><button :class="{on:outKind==='patents'}" @click="outKind='patents'">专利</button></span></h4><small>{{k===0?'在研项目批准经费':'基金支持的'+(outKind==='papers'?'论文':'专利')}}</small></div>
     <div class="il-yr"><strong>{{Y[A.i.value]}}</strong><span v-if="k===0">在研经费 {{(pn.p.tt/1e4).toFixed(2)}} 亿元</span><span v-else>累计 {{fmt(pn.p.cum)}} {{unit(outKind)}}</span></div>
    </div>
    <TransitionGroup tag="div" name="il-tile" class="il-tiles">
     <div v-for="t in pn.p.tiles" :key="t.id" class="il-tile" :class="{big:t.big,dark:t.dark}" :style="{background:t.bg}">
      <b>{{t.name}}</b><span>{{(t.sh*100).toFixed(1)}}%<small>{{k===0?(t.v/1e4).toFixed(2)+' 亿元':fmt(t.v)+' '+unit(outKind)}}</small></span>
     </div>
    </TransitionGroup>
   </div>
  </div>
  <div class="il-play"><button class="il-pbtn" :aria-label="A.on.value?'暂停':'播放'" @click="A.play">{{A.on.value?'❚❚':'▶'}}</button>
   <div class="il-track"><i :style="{width:A.i.value/last*100+'%'}"></i><button v-for="(y,k) in Y" :key="y" :class="{on:k===A.i.value,past:k<A.i.value}" :style="{left:k/last*100+'%'}" @click="A.seek(k)"><em></em><span>{{y}}</span></button></div></div>
  <p class="il-note">两图共用一条时间轴、同步推进；色块越深，该方向当年占比越高。</p>
 </section>

 <section class="il-sec">
  <header><b>02</b><h3>结构：各方向份额如何变化</h3><span>每行一年，条宽为该方向占当年的比例</span></header>
  <p class="il-lead">经费结构基本稳定；成果结构中，<em>基础模型与架构</em>的论文占比由 2021 年的 {{lead2.a0}}% 升至 <em>{{lead2.a1}}%</em>，<em>数据与知识服务</em>由 {{lead2.d0}}% 升至 <em>{{lead2.d1}}%</em>。</p>
  <div class="il-three">
   <div v-for="s in struct" :key="s.k" class="il-panel white">
    <div class="il-ph"><div><h4>{{s.t}}</h4><small>各年七大方向占比</small></div></div>
    <div class="il-rows">
     <div v-for="(r,i) in s.rows" :key="r.y" class="il-row" :class="{dim:hl!==null&&hl!==i}" @mouseenter="hl=i" @mouseleave="hl=null">
      <span>{{r.y}}</span>
      <div v-if="r.empty" class="il-bar empty">立项起始年</div>
      <div v-else class="il-bar"><i v-for="g in r.segs" :key="g.id" :style="{width:g.w*100+'%',background:PALETTE[g.id]}" :title="`${L[g.id].name} ${(g.w*100).toFixed(1)}%`"><b v-if="g.w>.09">{{Math.round(g.w*100)}}%</b></i></div>
     </div>
    </div>
   </div>
  </div>
  <div class="il-legend"><span v-for="id in ORDER" :key="id"><i :style="{background:PALETTE[id]}"></i>{{L[id].name}}</span></div>
 </section>

 <section ref="termEl" class="il-sec last">
  <header><b>03</b><h3>细节：70 个技术点的{{termKind==='funding'?'投入':'产出'}}</h3><span>按七大方向分列 · 每个技术点按自身峰值着色</span></header>
  <p class="il-lead">在研经费中，<em>上下文学习</em>、<em>AI 芯片与 GPU</em>等技术点较早获得支持；<em>Transformer</em>、<em>混合专家</em>、<em>视觉语言模型</em>等在 2023 年后集中出现。</p>
  <div class="il-panel white">
   <div class="il-ph"><div class="il-seg big"><button :class="{on:termKind==='funding'}" @click="termKind='funding'">经费</button><button :class="{on:termKind==='papers'}" @click="termKind='papers'">论文</button><button :class="{on:termKind==='patents'}" @click="termKind='patents'">专利</button></div>
    <div class="il-yr"><strong>{{Y[T.i.value]}}</strong><span>{{termKind==='funding'?'执行年份 · 在研经费':'当年新增'+(termKind==='papers'?'论文':'专利')}}</span></div></div>
   <div class="il-terms">
    <div v-for="c in cols" :key="c.id" class="il-col"><h5 :style="{color:PALETTE[c.id],borderColor:PALETTE[c.id]}">{{c.name}}</h5>
     <div v-for="t in c.items" :key="t.id" class="il-term" :class="{dark:t.a>.55}" :style="{background:t.a>0?PALETTE[c.id]+hex(t.a):'#f4efed'}" :title="`${t.full} · ${Y[T.i.value]} 年 ${fmt(t.v)} ${termUnit}`">{{t.name}}</div></div>
   </div>
   <div class="il-play inner"><button class="il-pbtn" :aria-label="T.on.value?'暂停':'播放'" @click="T.play">{{T.on.value?'❚❚':'▶'}}</button>
    <div class="il-track"><i :style="{width:T.i.value/last*100+'%'}"></i><button v-for="(y,k) in Y" :key="y" :class="{on:k===T.i.value,past:k<T.i.value}" :style="{left:k/last*100+'%'}" @click="T.seek(k)"><em></em><span>{{y}}</span></button></div></div>
  </div>
 </section>
</div></template>

<style scoped>
.il-sec{margin-bottom:40px}.il-sec.last{margin-bottom:8px}
.il-sec>header{display:flex;align-items:baseline;gap:12px;flex-wrap:wrap}
.il-sec>header b{font-size:15px;font-weight:800;color:#a21535;font-variant-numeric:tabular-nums}
.il-sec>header h3{margin:0;font-size:21px;font-weight:750;color:#232930}
.il-sec>header span{font-size:13.5px;color:#8a8286}
.il-lead{margin:8px 0 16px;font-size:16px;font-weight:600;line-height:1.75;color:#2f2b2d}
.il-lead em{font-style:normal;color:#a21535}
.il-two{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.il-three{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.il-panel{border:1px solid #ece5e1;border-radius:4px;padding:16px 18px;background:#fcfaf9;min-width:0}
.il-panel.white{background:#fff}
.il-ph{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:12px}
.il-ph h4{margin:0;font-size:16px;font-weight:750;display:flex;align-items:center;gap:8px}
.il-ph small{display:block;margin-top:3px;font-size:12px;color:#8a8286}
.il-yr{text-align:right}.il-yr strong{font-size:30px;font-weight:800;color:#a21535;line-height:1;font-variant-numeric:tabular-nums}.il-yr span{display:block;margin-top:4px;font-size:12px;color:#7a7378}
.il-seg{display:inline-flex;border:1px solid #e3dad6;border-radius:3px;overflow:hidden;background:#fff}
.il-seg button{padding:3px 10px;border:0;border-left:1px solid #e3dad6;background:none;font:inherit;font-size:12.5px;font-weight:500;color:#5d575b;cursor:pointer}
.il-seg button:first-child{border-left:0}.il-seg button.on{background:#a21535;color:#fff}
.il-seg.big button{padding:5px 14px;font-size:13px}
.il-tiles{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));grid-auto-rows:minmax(64px,auto);gap:6px}
.il-tile{display:flex;flex-direction:column;justify-content:space-between;padding:9px 11px;border-radius:3px;color:#2f2b2d;transition:background .6s}
.il-tile.big{grid-row:span 2}.il-tile.dark{color:#fff}
.il-tile b{font-size:13px;font-weight:750;line-height:1.35;overflow-wrap:anywhere}
.il-tile span{font-size:15px;font-weight:750;font-variant-numeric:tabular-nums}
.il-tile small{margin-left:4px;font-size:11px;font-weight:500;opacity:.85}
.il-tile-move{transition:transform .6s cubic-bezier(.4,0,.2,1)}
.il-play{display:flex;align-items:center;gap:14px;margin-top:16px}
.il-play.inner{margin-top:14px}
.il-pbtn{flex:none;width:30px;height:30px;border:0;border-radius:50%;background:#a21535;color:#fff;font-size:11px;cursor:pointer}
.il-track{position:relative;flex:1;height:30px;margin:0 8px}
.il-track::before{content:"";position:absolute;left:0;right:0;top:7px;height:3px;border-radius:2px;background:#eadfe1}
.il-track>i{position:absolute;left:0;top:7px;height:3px;border-radius:2px;background:#a21535;transition:width .4s}
.il-track button{position:absolute;top:0;transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:3px;padding:0;border:0;background:none;font:inherit;cursor:pointer}
.il-track em{width:9px;height:9px;margin-top:4px;border-radius:50%;background:#fff;border:2px solid #d9c3c8}
.il-track button.past em{border-color:#a21535;background:#a21535}
.il-track button.on em{width:13px;height:13px;margin-top:2px;border:3px solid #a21535;background:#fff}
.il-track span{font-size:11px;color:#9a9296}.il-track button.on span{color:#a21535;font-weight:750}
.il-note{margin:6px 0 0;font-size:12.5px;color:#9a9296}
.il-rows{display:flex;flex-direction:column;gap:6px}
.il-row{display:grid;grid-template-columns:38px 1fr;align-items:center;gap:8px;transition:opacity .2s}
.il-row.dim{opacity:.4}
.il-row>span{font-size:11.5px;color:#7a7378;text-align:right;font-variant-numeric:tabular-nums}
.il-bar{display:flex;height:22px;border-radius:2px;overflow:hidden;gap:1.5px}
.il-bar i{display:flex;align-items:center;justify-content:center;min-width:0}
.il-bar b{font-size:10.5px;font-weight:700;color:#fff}
.il-bar.empty{align-items:center;padding-left:8px;background:#f4efed;font-size:11px;color:#a9a1a4}
.il-legend{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:12px;font-size:12.5px;color:#5d575b}
.il-legend i{display:inline-block;width:12px;height:12px;margin-right:6px;vertical-align:-2px;border-radius:2px}
.il-terms{display:grid;grid-template-columns:repeat(7,minmax(0,1fr));gap:10px}
.il-col h5{margin:0 0 6px;padding-bottom:4px;border-bottom:2px solid;font-size:12px;font-weight:750;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.il-term{margin-bottom:3px;padding:4px 7px;border-radius:2px;font-size:11.5px;color:#3d3a3c;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transition:background .6s,color .6s}
.il-term.dark{color:#fff}
@media(max-width:1100px){.il-three{grid-template-columns:1fr}.il-terms{grid-template-columns:repeat(4,minmax(0,1fr))}}
@media(max-width:760px){.il-two{grid-template-columns:minmax(0,1fr)}.il-ph{flex-wrap:wrap}.il-tile span{font-size:13.5px}.il-terms{grid-template-columns:repeat(2,minmax(0,1fr))}.il-track span{font-size:9.5px}.il-lead{font-size:14.5px}}
@media(prefers-reduced-motion:reduce){.il-tile,.il-tile-move,.il-term,.il-track>i{transition:none}}
</style>
