<script setup>
/* 产业链案例 · 智谱：概览 → 科研承接 → 产品应用 → 经营观察 → 证据索引 */
import {computed,ref,onMounted,onBeforeUnmount,nextTick} from 'vue'
import {sources,evidence,routes,products,finance,mixLabels,sourceIndex} from '../../helpers/caseZhipu'
import {safeUrl} from '../../shared'

const sections=[['overview','案例概览'],['research','科研承接'],['products','产品应用'],['economics','经营观察'],['evidence','证据索引']]
const activeSec=ref('overview')
function go(id){document.getElementById('zc-'+id)?.scrollIntoView({behavior:'smooth',block:'start'})}
let io
onMounted(()=>{io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)activeSec.value=e.target.id.slice(3)}),{rootMargin:'-30% 0px -60% 0px'});sections.forEach(([id])=>{const el=document.getElementById('zc-'+id);el&&io.observe(el)});document.addEventListener('keydown',onKey)})
onBeforeUnmount(()=>{io?.disconnect();document.removeEventListener('keydown',onKey)})

/* 证据抽屉 */
const open=ref(null),drawer=ref(null)
function show(id){open.value=evidence[id];nextTick(()=>drawer.value?.querySelector('button')?.focus())}
function onKey(e){if(e.key==='Escape'&&open.value)open.value=null}

/* 科研承接 */
const route=ref(routes[0])

/* 经营观察 */
const period=ref('half')
const F=computed(()=>finance[period.value])
const mixColors=['#a21535','#2c64a0','#b2772a','#c9c2c7']
const mix=computed(()=>{const s=F.value.mix.reduce((a,b)=>a+b,0);let a0=-Math.PI/2;return F.value.mix.map((v,i)=>{const a1=a0+v/s*Math.PI*2,r=62,R=86,large=a1-a0>Math.PI?1:0,p=(rr,a)=>[100+rr*Math.cos(a),100+rr*Math.sin(a)];const [x0,y0]=p(R,a0),[x1,y1]=p(R,a1),[x2,y2]=p(r,a1),[x3,y3]=p(r,a0);const d=`M${x0},${y0} A${R},${R} 0 ${large} 1 ${x1},${y1} L${x2},${y2} A${r},${r} 0 ${large} 0 ${x3},${y3}Z`;a0=a1;return {d,c:mixColors[i],v,pct:v/s*100,label:mixLabels[i]}})})
const trend=computed(()=>{const t=F.value.trend,max=Math.ceil(Math.max(...t.revenue,...t.rd)/5)*5,W=460,H=220,L=40,B=190,T=16,gw=(W-L-10)/t.labels.length,bw=t.labels.length===3?30:42
 return {W,H,L,B,ticks:[0,.2,.4,.6,.8,1].map(k=>({v:Math.round(max*k),y:B-(B-T)*k})),groups:t.labels.map((lab,i)=>{const cx=L+gw*(i+.5),h=v=>v/max*(B-T);return {lab,cx,bars:[{x:cx-bw-3,h:h(t.revenue[i]),v:t.revenue[i],c:'#a21535'},{x:cx+3,h:h(t.rd[i]),v:t.rd[i],c:'#d2b49f'}],bw}})}})
const fmt2=v=>v.toFixed(2)
</script>

<template><div class="zc">
 <!-- 案例头部 -->
 <header class="zc-top">
  <div class="zc-id"><span class="zc-logo" aria-hidden="true">智</span><div><p class="zc-kicker">产业链案例 · 人工智能 · 模型研发与平台供给</p><h3>智谱：从基础研究到产业应用</h3><p class="zc-entity">北京智谱华章科技股份有限公司 · 资料整理 2026-11-06</p></div></div>
  <nav class="zc-nav" aria-label="案例章节"><button v-for="([id,l],i) in sections" :key="id" :class="{on:activeSec===id}" @click="go(id)"><i>{{String(i+1).padStart(2,'0')}}</i>{{l}}</button></nav>
 </header>

 <!-- 01 概览 -->
 <section id="zc-overview" class="zc-sec">
  <div class="zc-hero">
   <div class="zc-hero-copy">
    <p class="zc-lead">以 <b>GLM</b> 与 <b>P-Tuning v2</b> 两篇基金支持的论文为线索，追踪方法如何进入企业专利与模型研发，再经产品与行业任务形成付费服务。</p>
    <div class="zc-metrics">
     <div><strong>2<small>条</small></strong><span>研究方法路线</span><em>GLM · P-Tuning v2</em></div>
     <div><strong>3<small>件</small></strong><span>方法承接专利</span><em>摘要 · 问答 · 检索</em></div>
     <div><strong>4<small>类</small></strong><span>产品与行业任务</span><em>对话 · 编程 · 办公 · 金融</em></div>
     <div><strong>86.5<small>%</small></strong><span>API 收入占比</span><em>2026 上半年</em></div>
    </div>
    <button class="zc-link" @click="show('case')">案例范围与口径 ↗</button>
   </div>
   <div class="zc-chain" aria-label="案例链条：基金项目、论文方法、企业研发、产品服务、行业任务、经营表现">
    <div v-for="(s,i) in [{k:'研究起点',n:[['基金项目','61825602 · 61836013'],['论文方法','GLM · P-Tuning v2']]},{k:'企业研发',n:[['企业专利','摘要 · 问答 · 检索'],['模型与适配','ChatGLM · 任务微调']]},{k:'产业应用',n:[['产品服务','清言 · CodeGeeX'],['行业任务','办公 · 金融'],['经营表现','收入 · 研发']]}]" :key="s.k" class="zc-stage">
     <span class="zc-stage-k">{{s.k}}</span>
     <div class="zc-stage-n"><template v-for="(n,j) in s.n" :key="n[0]"><i v-if="j" aria-hidden="true">→</i><div><b>{{n[0]}}</b><small>{{n[1]}}</small></div></template></div>
     <span v-if="i<2" class="zc-down">{{['论文致谢 · 专利说明书 · 官方实现','技术报告 · 产品资料 · 企业披露'][i]}}</span>
    </div>
   </div>
  </div>
 </section>

 <!-- 02 科研承接 -->
 <section id="zc-research" class="zc-sec">
  <header class="zc-sh"><b>02</b><div><h4>科研承接：方法进入企业研发</h4><p>从论文致谢回溯基金，在专利说明书与官方代码中找到方法的使用位置</p></div></header>
  <div class="zc-seg" role="tablist" aria-label="研究方法"><button v-for="r in routes" :key="r.id" role="tab" :aria-selected="route.id===r.id" :class="{on:route.id===r.id}" @click="route=r"><b>{{r.label}}</b><small>{{r.sub}}</small></button></div>
  <div :key="route.id" class="zc-route pane-swap">
   <div class="zc-route-head"><div><h5>{{route.title}}</h5><p>{{route.lead}}</p></div><span class="zc-tag">{{route.tag}}</span></div>
   <div class="zc-flow">
    <button class="zc-node fund" @click="show(route.fundEv)"><small>国家自然科学基金</small><strong>{{route.fund.join(' · ')}}</strong><span>论文致谢列示</span><i>↗</i></button>
    <span class="zc-arrow"><em>资助</em></span>
    <button class="zc-node paper" @click="show(route.paperEv)"><small>基金支持论文</small><strong>{{route.paper}}</strong><span>{{route.paperSub}}</span><i>↗</i></button>
    <span class="zc-fork" aria-hidden="true"></span>
    <div class="zc-branches"><button v-for="b in route.branches" :key="b.ev" class="zc-node branch" @click="show(b.ev)"><small>{{b.label}}</small><strong>{{b.title}}</strong><span>{{b.sub}}</span><i>↗</i></button></div>
   </div>
   <div class="zc-steps"><div><b>基金 → 论文</b>论文致谢列示资助编号</div><div><b>论文 → 企业研发</b>专利说明书与官方代码采用该方法</div><div><b>研发 → 产品应用</b>模型报告、产品资料与企业披露</div></div>
  </div>
 </section>

 <!-- 03 产品应用 -->
 <section id="zc-products" class="zc-sec">
  <header class="zc-sh"><b>03</b><div><h4>产品应用：模型能力进入具体任务</h4><p>智谱提供模型与平台能力，应用软件与开发工具完成集成，办公、编程与金融用户在具体任务中使用</p></div></header>
  <div class="zc-products">
   <article v-for="p in products" :key="p.id" class="zc-prod">
    <div class="zc-prod-top"><span class="zc-icon" :class="p.icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path v-if="p.icon==='chat'" d="M5 4H19V16H10L5 20V4ZM8 8H16M8 12H13"/><path v-else-if="p.icon==='code'" d="M8 7L3 12L8 17M16 7L21 12L16 17M14 4L10 20"/><path v-else-if="p.icon==='doc'" d="M6 3H18V21H6ZM9 8H15M9 12H15M9 16H13"/><path v-else d="M3 9L12 4L21 9M4 10H20M5 20H19M7 11V17M12 11V17M17 11V17"/></svg></span><span class="zc-tag soft">{{p.tag}}</span></div>
    <h5>{{p.name}}</h5><p class="zc-prod-sub">{{p.sub}}</p>
    <div class="zc-task"><template v-for="(f,i) in p.flow" :key="f"><i v-if="i">→</i><span>{{f}}</span></template></div>
    <p class="zc-prod-obs"><b v-if="p.big">{{p.big}}</b>{{p.text}}</p>
    <footer><span>{{p.note}}</span><button @click="show(p.id)">查看依据 ↗</button></footer>
   </article>
  </div>
 </section>

 <!-- 04 经营观察 -->
 <section id="zc-economics" class="zc-sec">
  <header class="zc-sh"><b>04</b><div><h4>经营观察：付费服务与持续研发</h4><p>智谱集团 · 人民币亿元 · {{F.note}}</p></div>
   <div class="zc-period" role="group" aria-label="观察期"><button v-for="(v,k) in finance" :key="k" :class="{on:period===k}" :aria-pressed="period===k" @click="period=k">{{v.label}}</button></div></header>
  <p class="zc-elead" v-html="F.lead"></p>
  <div class="zc-fin">
   <div class="zc-fin-kpi"><div><span>营业收入</span><strong>{{fmt2(F.revenue)}}<small>亿元</small></strong></div><div><span>API 模型调用收入</span><strong>{{fmt2(F.api)}}<small>亿元</small></strong><em>占收入 {{F.share}}%</em></div><div><span>研发开支</span><strong>{{fmt2(F.rd)}}<small>亿元</small></strong></div><div><span>集团毛利</span><strong>{{fmt2(F.gross)}}<small>亿元</small></strong></div><div><span>集团净亏损</span><strong>{{fmt2(F.loss)}}<small>亿元</small></strong></div></div>
   <div class="zc-charts">
    <div class="zc-card"><div class="zc-card-h"><b>{{period==='half'?'半年同期：':'年度趋势：'}}收入与研发投入</b><span class="zc-legend"><i style="background:#a21535"></i>营业收入<i style="background:#d2b49f"></i>研发开支</span></div>
     <svg :viewBox="`0 0 ${trend.W} ${trend.H}`" width="100%" role="img" aria-label="收入与研发开支柱状图">
      <g v-for="t in trend.ticks" :key="t.v"><line :x1="trend.L" :x2="trend.W-10" :y1="t.y" :y2="t.y" stroke="#efe8e5" :stroke-dasharray="t.v?'3 4':''"/><text :x="trend.L-8" :y="t.y+4" font-size="11" fill="#9a9296" text-anchor="end">{{t.v}}</text></g>
      <g v-for="g in trend.groups" :key="g.lab"><g v-for="b in g.bars" :key="b.c"><rect class="zc-bar" :x="b.x" :y="trend.B-b.h" :width="g.bw" :height="b.h" rx="2" :fill="b.c"/><text :x="b.x+g.bw/2" :y="trend.B-b.h-6" font-size="11.5" font-weight="700" text-anchor="middle" fill="#3d3a3c">{{b.v.toFixed(2)}}</text></g><text :x="g.cx" :y="trend.B+20" font-size="12" text-anchor="middle" fill="#5d575b">{{g.lab}}</text></g>
     </svg></div>
    <div class="zc-card"><div class="zc-card-h"><b>{{F.label}}收入结构</b><span>按业务类型</span></div>
     <div class="zc-mix"><svg viewBox="0 0 200 200" class="zc-donut" role="img" :aria-label="`API 收入占比 ${F.share}%`"><path v-for="m in mix" :key="m.label" :d="m.d" :fill="m.c"/><text x="100" y="98" text-anchor="middle" font-size="28" font-weight="800" fill="#a21535">{{F.share}}%</text><text x="100" y="120" text-anchor="middle" font-size="11.5" fill="#7a7378">API 收入占比</text></svg>
      <ul><li v-for="m in mix" :key="m.label"><i :style="{background:m.c}"></i><span>{{m.label}}</span><b>{{m.v.toFixed(2)}}</b><em>{{m.pct.toFixed(1)}}%</em></li></ul></div></div>
   </div>
   <button class="zc-link" @click="show('finance')">财报来源与口径 ↗</button>
  </div>
 </section>

 <!-- 05 证据索引 -->
 <section id="zc-evidence" class="zc-sec last">
  <header class="zc-sh"><b>05</b><div><h4>证据索引</h4><p>每一步联系都对应原文位置，可直接打开核对</p></div></header>
  <div class="zc-sources"><div v-for="s in sourceIndex" :key="s.id" class="zc-src"><span>{{s.id}}</span><div><b>{{s.title}}</b><p>{{s.desc}}</p></div><div class="zc-src-links"><a v-for="r in s.refs" :key="r" :href="safeUrl(sources[r].url)" target="_blank" rel="noopener">{{sources[r].title.split(' · ')[0]}} ↗</a></div></div></div>
  <p class="zc-next"><b>后续测度</b>补充任务完成时间、质量、调用成本与人工复核投入，建立对照，测算具体任务中的净收益。</p>
 </section>

 <!-- 证据抽屉 -->
 <Teleport to="body"><Transition name="zc-dr"><div v-if="open" class="zc-overlay" @click.self="open=null"><aside ref="drawer" class="zc-drawer" role="dialog" aria-modal="true" :aria-label="open.title">
  <div class="zc-dr-h"><div><span>{{open.kind}}</span><h4>{{open.title}}</h4></div><button aria-label="关闭" @click="open=null">×</button></div>
  <p class="zc-claim">{{open.claim}}</p>
  <p class="zc-dr-k">原文依据</p>
  <a v-for="r in open.refs" :key="r" class="zc-dr-src" :href="safeUrl(sources[r].url)" target="_blank" rel="noopener"><b>{{sources[r].title}} ↗</b><small>{{sources[r].location}}</small></a>
 </aside></div></Transition></Teleport>
</div></template>

<style scoped>
.zc{display:flex;flex-direction:column;gap:22px}
.zc-top{position:sticky;top:76px;z-index:5;display:flex;justify-content:space-between;align-items:center;gap:20px;padding:16px 22px;background:rgba(255,255,255,.96);backdrop-filter:blur(10px);border:1px solid #e6dfdb;border-radius:4px}
.zc-id{display:flex;align-items:center;gap:14px}
.zc-logo{display:grid;place-items:center;width:44px;height:44px;border-radius:4px;background:#a21535;color:#fff;font-size:20px;font-weight:800}
.zc-kicker{margin:0;font-size:12px;color:#8a8286;letter-spacing:.5px}
.zc-id h3{margin:2px 0;font-size:21px;font-weight:750;color:#232930}
.zc-entity{margin:0;font-size:12px;color:#9a9296}
.zc-nav{display:flex;gap:4px;padding:4px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.zc-nav button{display:inline-flex;align-items:baseline;gap:6px;padding:7px 12px;border:0;border-radius:3px;background:none;font:inherit;font-size:13.5px;font-weight:600;color:#6a6468;cursor:pointer;white-space:nowrap}
.zc-nav i{font-style:normal;font-size:11px;color:#b0a6a9}
.zc-nav button.on{background:#a21535;color:#fff}.zc-nav button.on i{color:#f2c4cc}
.zc-sec{scroll-margin-top:170px;padding:26px 28px 28px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.zc-sh{display:flex;align-items:flex-start;gap:14px;margin-bottom:18px}
.zc-sh>b{font-size:15px;font-weight:800;color:#a21535;padding-top:4px}
.zc-sh>div:not(.zc-period){flex:1}
.zc-sh h4{margin:0;font-size:21px;font-weight:750;color:#232930}
.zc-sh p{margin:4px 0 0;font-size:13.5px;color:#7a7378;line-height:1.6}
.zc-hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:28px;align-items:stretch}
.zc-lead{margin:0 0 20px;font-size:18px;font-weight:600;line-height:1.8;color:#2f2b2d}.zc-lead b{color:#a21535}
.zc-metrics{display:grid;grid-template-columns:repeat(2,1fr);border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.zc-metrics>div{padding:14px 18px;display:flex;flex-direction:column}
.zc-metrics>div:nth-child(even){border-left:1px solid #ece5e1}.zc-metrics>div:nth-child(n+3){border-top:1px solid #ece5e1}
.zc-metrics strong{font-size:30px;font-weight:800;color:#a21535;line-height:1.2;font-variant-numeric:tabular-nums}.zc-metrics strong small{margin-left:4px;font-size:13px;font-weight:600;color:#7a7378}
.zc-metrics span{font-size:13.5px;font-weight:650;color:#2f2b2d}.zc-metrics em{font-style:normal;font-size:12px;color:#9a9296}
.zc-link{margin-top:14px;padding:0;border:0;background:none;font:inherit;font-size:13.5px;font-weight:600;color:#a21535;cursor:pointer}
.zc-chain{position:relative;display:flex;flex-direction:column;justify-content:center;gap:4px;padding:24px 26px;border-radius:4px;background:linear-gradient(140deg,#8c1c32,#5f1326);color:#fff;overflow:hidden}
.zc-chain::before{content:"";position:absolute;inset:0;background-image:linear-gradient(#ffffff08 1px,transparent 1px),linear-gradient(90deg,#ffffff08 1px,transparent 1px);background-size:28px 28px}
.zc-stage{position:relative;display:grid;grid-template-columns:72px 1fr;gap:12px;align-items:center}
.zc-stage-k{font-size:12px;letter-spacing:1px;color:#f0c6d0}
.zc-stage-n{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.zc-stage-n i{font-style:normal;color:#e6a9b7}
.zc-stage-n>div{padding:8px 12px;border:1px solid #ffffff3d;border-radius:3px;background:#ffffff12}
.zc-stage-n b{display:block;font-size:13.5px}.zc-stage-n small{display:block;font-size:11px;opacity:.75}
.zc-stage:first-child .zc-stage-n>div:last-child{background:#fff4f2;color:#7b2236;border-color:#fff4f2}
.zc-down{grid-column:2;margin:6px 0 8px;font-size:11.5px;color:#e3b5c1}.zc-down::before{content:"↓ "}
.zc-seg{display:inline-flex;margin-bottom:16px;border:1px solid #e3dad6;border-radius:3px;overflow:hidden}
.zc-seg button{display:flex;flex-direction:column;align-items:flex-start;padding:9px 20px;border:0;border-left:1px solid #e3dad6;background:#fff;font:inherit;cursor:pointer;text-align:left}
.zc-seg button:first-child{border-left:0}
.zc-seg b{font-size:15px;color:#2f2b2d}.zc-seg small{font-size:12px;color:#8a8286}
.zc-seg button.on{background:#a21535}.zc-seg button.on b,.zc-seg button.on small{color:#fff}
.zc-route{padding:20px 22px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.zc-route-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;padding-bottom:16px;margin-bottom:20px;border-bottom:1px solid #ece5e1}
.zc-route-head h5{margin:0;font-size:18px;font-weight:750}.zc-route-head p{margin:4px 0 0;font-size:13.5px;color:#7a7378}
.zc-tag{flex:none;padding:3px 9px;border:1px solid #e9c3cb;border-radius:2px;background:#fff7f8;font-size:12px;color:#a21535}
.zc-tag.soft{border-color:#e3dad6;background:#f8f5f4;color:#6a6468}
.zc-flow{display:grid;grid-template-columns:minmax(0,.8fr) 56px minmax(0,.95fr) 44px minmax(0,1.35fr);align-items:center}
.zc-node{position:relative;display:block;width:100%;padding:18px 20px;border:1px solid #e3d6d9;border-radius:4px;background:#fff;font:inherit;text-align:left;cursor:pointer;transition:border-color .2s,box-shadow .2s}
.zc-node:hover{border-color:#c99aa4;box-shadow:0 6px 18px -10px rgba(162,21,53,.4)}
.zc-node small{display:block;margin-bottom:6px;font-size:12px;color:#8a7b83}
.zc-node strong{display:block;font-size:18px;font-weight:750;color:#74182b;line-height:1.4}
.zc-node span{display:block;margin-top:6px;font-size:12.5px;line-height:1.6;color:#7a7378}
.zc-node>i{position:absolute;right:12px;top:10px;font-style:normal;color:#c39aa5}
.zc-node.fund strong{font-variant-numeric:tabular-nums}
.zc-node.paper{background:#fbf2f4;border-color:#e9c3cb}.zc-node.paper strong{font-size:22px;color:#a21535}
.zc-node.branch strong{font-size:15.5px;color:#2f2b2d}
.zc-arrow{position:relative;height:2px;margin:0 6px;background:#d8a2af}
.zc-arrow::after{content:"";position:absolute;right:-1px;top:-4px;border-left:7px solid #c48998;border-top:5px solid transparent;border-bottom:5px solid transparent}
.zc-arrow em{position:absolute;top:-20px;left:50%;transform:translateX(-50%);font-style:normal;font-size:11px;color:#a07383}
.zc-fork{position:relative;align-self:stretch;margin:48px 0}
.zc-fork::before{content:"";position:absolute;left:0;top:50%;width:50%;height:2px;background:#d8a2af}
.zc-fork::after{content:"";position:absolute;left:50%;top:0;bottom:0;width:50%;border:2px solid #d8a2af;border-right:0;border-radius:6px 0 0 6px}
.zc-branches{display:grid;gap:12px}
.zc-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:20px}
.zc-steps>div{padding-left:12px;border-left:2px solid #e3c7ce;font-size:12.5px;line-height:1.6;color:#7a7378}.zc-steps b{display:block;font-size:13px;color:#5b3a47}
.zc-products{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.zc-prod{display:flex;flex-direction:column;padding:20px 22px 14px;border:1px solid #ece5e1;border-radius:4px}
.zc-prod-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.zc-icon{display:grid;place-items:center;width:38px;height:38px;border-radius:4px;background:#f8ecef;color:#a21535}
.zc-icon svg{width:22px;height:22px}
.zc-icon.code{background:#edf2f8;color:#2c64a0}.zc-icon.doc{background:#eef5f2;color:#23806e}.zc-icon.bank{background:#faf3e8;color:#b2772a}
.zc-prod h5{margin:0;font-size:19px;font-weight:750}.zc-prod-sub{margin:4px 0 0;font-size:13px;color:#7a7378}
.zc-task{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin:14px 0}
.zc-task span{padding:4px 9px;border-radius:2px;background:#f6f2f1;font-size:12px;color:#5d575b}.zc-task i{font-style:normal;color:#c0b1b6}
.zc-prod-obs{flex:1;margin:0;font-size:14px;line-height:1.75;color:#3d3a3c}.zc-prod-obs b{margin-right:6px;font-size:24px;font-weight:800;color:#a21535}
.zc-prod footer{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:14px;padding-top:12px;border-top:1px solid #f0eae7;font-size:12px;color:#9a9296}
.zc-prod footer button,.zc-src-links a{padding:0;border:0;background:none;font:inherit;font-size:12.5px;font-weight:600;color:#a21535;cursor:pointer;text-decoration:none;white-space:nowrap}
.zc-period{flex:none;align-self:center;display:inline-flex;padding:3px;border-radius:4px;background:#f4f0ef}
.zc-period button{padding:7px 14px;border:0;border-radius:3px;background:none;font:inherit;font-size:13px;color:#6a6468;cursor:pointer}
.zc-period button.on{background:#fff;color:#a21535;font-weight:700;box-shadow:0 2px 6px rgba(80,30,40,.1)}
.zc-elead{margin:-4px 0 16px;font-size:16.5px;font-weight:600;line-height:1.75;color:#2f2b2d}.zc-elead :deep(b){color:#a21535}
.zc-fin-kpi{display:grid;grid-template-columns:repeat(5,1fr);margin-bottom:16px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.zc-fin-kpi>div{padding:14px 18px;border-left:1px solid #ece5e1}.zc-fin-kpi>div:first-child{border-left:0}
.zc-fin-kpi span{display:block;font-size:12.5px;color:#7a7378}
.zc-fin-kpi strong{display:block;font-size:26px;font-weight:800;color:#2f2b2d;line-height:1.3;font-variant-numeric:tabular-nums}.zc-fin-kpi strong small{margin-left:4px;font-size:12px;font-weight:500;color:#7a7378}
.zc-fin-kpi em{font-style:normal;font-size:12px;font-weight:700;color:#a21535}
.zc-charts{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,1fr);gap:16px}
.zc-card{padding:16px 18px;border:1px solid #ece5e1;border-radius:4px}
.zc-card-h{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:8px}.zc-card-h b{font-size:15px}.zc-card-h>span{font-size:12px;color:#9a9296}
.zc-legend{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:#7a7378}.zc-legend i{width:10px;height:10px;border-radius:2px;margin-left:8px}
.zc-bar{transition:height .5s,y .5s}
.zc-mix{display:grid;grid-template-columns:180px 1fr;gap:18px;align-items:center}
.zc-donut{width:180px;height:180px}
.zc-mix ul{margin:0;padding:0;list-style:none}
.zc-mix li{display:grid;grid-template-columns:12px 1fr auto 52px;gap:8px;align-items:center;padding:9px 0;border-bottom:1px solid #f0eae7;font-size:13px;color:#5d575b}.zc-mix li:last-child{border-bottom:0}
.zc-mix li i{width:10px;height:10px;border-radius:2px}.zc-mix li b{font-variant-numeric:tabular-nums;color:#2f2b2d}.zc-mix li em{font-style:normal;text-align:right;color:#9a9296;font-variant-numeric:tabular-nums}
.zc-sources{border:1px solid #ece5e1;border-radius:4px}
.zc-src{display:grid;grid-template-columns:44px minmax(0,1fr) auto;gap:16px;align-items:center;padding:14px 20px;border-top:1px solid #f0eae7}.zc-src:first-child{border-top:0}
.zc-src>span{font-size:12px;font-weight:700;color:#b08a96}
.zc-src b{font-size:14px}.zc-src p{margin:2px 0 0;font-size:12.5px;color:#7a7378}
.zc-src-links{display:flex;flex-wrap:wrap;gap:6px 14px;justify-content:flex-end}
.zc-next{margin:16px 0 0;padding:14px 18px;border-left:3px solid #a21535;background:#fbf5f6;font-size:13.5px;line-height:1.7;color:#4a4448}.zc-next b{margin-right:10px;color:#a21535}
.zc-overlay{position:fixed;inset:0;z-index:80;background:rgba(40,19,30,.35);display:flex;justify-content:flex-end}
.zc-drawer{width:min(460px,100%);height:100%;overflow:auto;padding:24px 26px;background:#fff;box-shadow:-20px 0 60px -30px rgba(40,10,20,.5)}
.zc-dr-h{display:flex;justify-content:space-between;gap:16px;padding-bottom:16px;margin-bottom:16px;border-bottom:1px solid #f0eae7}
.zc-dr-h span{font-size:12px;font-weight:700;color:#a21535;letter-spacing:1px}.zc-dr-h h4{margin:4px 0 0;font-size:20px}
.zc-dr-h button{flex:none;width:32px;height:32px;border:1px solid #e3d6d9;border-radius:50%;background:#fff;font-size:18px;line-height:1;cursor:pointer}
.zc-claim{margin:0 0 18px;font-size:14.5px;line-height:1.9;color:#2f2b2d}
.zc-dr-k{margin:0 0 8px;font-size:12px;font-weight:700;color:#a21535}
.zc-dr-src{display:block;margin-bottom:8px;padding:12px 14px;border:1px solid #ece5e1;border-radius:4px;text-decoration:none;color:inherit}
.zc-dr-src:hover{border-color:#d7b8bf;background:#fdf9fa}
.zc-dr-src b{display:block;font-size:13px;color:#a21535}.zc-dr-src small{display:block;margin-top:4px;font-size:12px;line-height:1.6;color:#7a7378}
.zc-dr-enter-active,.zc-dr-leave-active{transition:opacity .2s}.zc-dr-enter-active .zc-drawer,.zc-dr-leave-active .zc-drawer{transition:transform .25s}
.zc-dr-enter-from,.zc-dr-leave-to{opacity:0}.zc-dr-enter-from .zc-drawer,.zc-dr-leave-to .zc-drawer{transform:translateX(30px)}
@media(max-width:1100px){.zc-top{position:static;flex-direction:column;align-items:flex-start}.zc-nav{flex-wrap:wrap}.zc-hero,.zc-charts{grid-template-columns:1fr}.zc-fin-kpi{grid-template-columns:repeat(3,1fr)}.zc-fin-kpi>div:nth-child(4){border-left:0}.zc-fin-kpi>div:nth-child(n+4){border-top:1px solid #ece5e1}}
@media(max-width:760px){.zc-sec{padding:20px 16px}.zc-flow{grid-template-columns:1fr;gap:10px}.zc-arrow{width:2px;height:22px;margin:0 auto}.zc-arrow::after{right:-4px;top:auto;bottom:-1px;border-top:7px solid #c48998;border-left:5px solid transparent;border-right:5px solid transparent;border-bottom:0}.zc-arrow em{top:2px;left:12px;transform:none}.zc-fork{display:none}.zc-steps,.zc-products{grid-template-columns:1fr}.zc-fin-kpi{grid-template-columns:1fr 1fr}.zc-fin-kpi>div{border-left:0!important;border-top:1px solid #ece5e1}.zc-fin-kpi>div:first-child{border-top:0}.zc-mix{grid-template-columns:1fr;justify-items:center}.zc-mix ul{width:100%}.zc-src{grid-template-columns:36px 1fr}.zc-src-links{grid-column:2;justify-content:flex-start}.zc-route-head{flex-direction:column}.zc-lead{font-size:16px}.zc-stage{grid-template-columns:1fr}.zc-down{grid-column:1}}
@media(prefers-reduced-motion:reduce){.zc-bar,.zc-dr-enter-active,.zc-dr-leave-active,.zc-drawer{transition:none!important}}
</style>
