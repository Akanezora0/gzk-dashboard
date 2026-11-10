<script setup>
/* 02 机构参与：机构与项目双向流图共用一条年份轴，经费并入年份轴；下方为首次承担机构的后续论文产出 */
import {useYearPlayback} from '../helpers/useYearPlayback'
import {computed} from 'vue'
import {useTip,fmt} from '../helpers/strengthTip.js'
const props=defineProps({dataset:Object})
const {tip,show,move,hide}=useTip()
const S=computed(()=>props.dataset?.strength||{})
const split=computed(()=>S.value.split||[])
const annual=computed(()=>S.value.annual||[])
const {year:shown,playing,play}=useYearPlayback(2017,2021)

const X=y=>270+(y-2017)*190
const IT=50,IH=160,AXY=250,PT=290,PH=170
const tot=r=>(r.retained_institutions||0)+(r.entered_institutions||0),totP=r=>(r.retained_projects||0)+(r.entered_projects||0)
const first=computed(()=>split.value[0]||{}),last=computed(()=>split.value.at(-1)||{})
const maxI=computed(()=>Math.max(...split.value.map(tot),1)*1.06),maxP=computed(()=>Math.max(...split.value.map(totP),1)*1.06)
function smooth(p){let d=`M${p[0][0]},${p[0][1]}`;for(let i=1;i<p.length;i++){const [a,b]=p[i-1],[c,e]=p[i],m=(a+c)/2;d+=` C${m},${b} ${m},${e} ${c},${e}`}return d}
function area(top,base){return smooth(top)+` L${top.at(-1)[0]},${base} L${top[0][0]},${base} Z`}
const P=computed(()=>{
 const r=split.value;if(!r.length)return null
 const iBase=IT+IH,pBase=PT
 const ik=r.map(x=>[X(x.year),iBase-x.retained_institutions/maxI.value*IH]),it=r.map(x=>[X(x.year),iBase-tot(x)/maxI.value*IH])
 const pk=r.map(x=>[X(x.year),pBase+x.retained_projects/maxP.value*PH]),pt=r.map(x=>[X(x.year),pBase+totP(x)/maxP.value*PH])
 return {ik,it,pk,pt,iBase,pBase,iKeep:area(ik,iBase),iAll:area(it,iBase),pKeep:area(pk,pBase),pAll:area(pt,pBase)}
})
const clipW=computed(()=>X(shown.value)+(shown.value>=2021?60:95))
const pct=(a,b)=>b?Math.round(a/b*100):0
const growthI=computed(()=>pct(tot(last.value)-tot(first.value),tot(first.value)))
const growthP=computed(()=>pct(totP(last.value)-totP(first.value),totP(first.value)))
const fund0=computed(()=>annual.value[0]?.amount_yi),fund1=computed(()=>annual.value.at(-1)?.amount_yi)
const growthF=computed(()=>fund0.value?Math.round((fund1.value/fund0.value-1)*100):0)
const funding=computed(()=>S.value.retained_2021||[])
const fundShare=computed(()=>{const a=funding.value.find(r=>r.present_2017),s=funding.value.reduce((x,r)=>x+r.amount_yi,0);return a&&s?Math.round(a.amount_yi/s*100):null})
const projShare=computed(()=>pct(last.value.retained_projects,totP(last.value)))
const top10=computed(()=>[annual.value[0]?.top10_amount_pct,annual.value.at(-1)?.top10_amount_pct].map(v=>v==null?null:Math.round(v)))

/* 首次承担 AI 项目的机构：按首次年份分组，统计窗口内有相关论文的年数 */
const C=computed(()=>S.value.cohort||{})
const cohortYears=computed(()=>{
 const ci=props.dataset?.focus?.cohort_institutions||{},w=C.value.window||[2022,2025],out={}
 for(const v of Object.values(ci)){const n=Object.entries(v.years||{}).filter(([y,c])=>c>0&&+y>=w[0]&&+y<=w[1]).length;const k=v.first;(out[k]=out[k]||[0,0,0,0,0])[4-Math.min(4,n)]++}
 return Object.entries(out).map(([y,v])=>({year:+y,v,n:v.reduce((a,b)=>a+b,0),two:v[0]+v[1]+v[2]})).sort((a,b)=>a.year-b.year)
})
const CC=['#1f4f80','#4f7fae','#8fb0d0','#cfdcea','#ebe6e3'],CL=['4 年','3 年','2 年','1 年','暂未发表']
const BH=2.7,CB=726
function yearTip(e,r){const a=annual.value.find(x=>x.year===r.year);show(e,`<b>${r.year} 年</b><br>机构 ${fmt(tot(r))} 家（既有 ${r.retained_institutions} · 新进入 ${r.entered_institutions}）<br>项目 ${fmt(totP(r))} 项（既有 ${fmt(r.retained_projects)} · 新进入 ${r.entered_projects}）${a?`<br>批准经费 ${a.amount_yi.toFixed(2)} 亿元 · 前十机构经费占比 ${a.top10_amount_pct}%`:''}`)}
function cohortTip(e,c){show(e,`<b>${c.year} 年首次承担 AI 项目 · ${c.n} 家机构</b><br>${(C.value.window||[2022,2025]).join('—')} 年发表相关论文的年数：<br>${c.v.map((n,i)=>`${CL[i]} ${n} 家机构`).join(' · ')}<br>持续产出率 ${Math.round(c.two/c.n*100)}%（${c.two} 家机构至少两年发表）`)}
</script>
<template>
  <section class="rs-page">
    <header class="rs-head"><span class="rs-no">02</span><h3>机构参与</h3>
      <div class="rs-tools"><button class="rs-btn" :class="{on:playing}" @click="play">{{playing?'Ⅱ 暂停':shown>=2021?'▶ 重播':'▶ 播放'}}</button></div></header>
    <div v-if="!P" class="rs-empty">机构参与数据尚未生成，请在服务器运行 build_ai_chain.py 更新研究团队数据。</div>
    <template v-else>
    <p class="rs-lead">机构数增加 <b>{{growthI}}%</b>，项目与经费增加约 <b>{{(Math.min(growthP,growthF)/100).toFixed(1)}} 倍</b>：资助在持续扩面的同时，<b>既有机构承担更多项目</b>，新进入机构大多保持产出。</p>
    <div class="st-kpis">
      <div class="st-group">规模增长<small>{{first.year}}—{{last.year}} 年</small></div>
      <div><span>承担机构</span><strong>{{tot(first)}} → {{tot(last)}}<em>家机构</em></strong><small>增加 {{growthI}}%</small></div>
      <div><span>年度批准项目</span><strong>{{fmt(totP(first))}} → {{fmt(totP(last))}}<em>项</em></strong><small>增加 {{growthP}}%</small></div>
      <div><span>年度批准经费</span><strong>{{fund0?.toFixed(2)}} → {{fund1?.toFixed(2)}}<em>亿元</em></strong><small>增加 {{growthF}}%</small></div>
      <div class="st-group">结构变化<small>{{last.year}} 年</small></div>
      <div><span>既有机构承担的项目占比</span><strong>{{projShare}}%</strong><small>2017 年已承担 AI 项目的机构</small></div>
      <div><span>既有机构承担的经费占比</span><strong>{{fundShare}}%</strong><small>前十机构经费占比 {{top10[0]}}% → {{top10[1]}}%</small></div>
      <div><span>首次承担机构的持续产出率</span><strong class="blue">{{Math.round(C.at_least_two/C.institutions*100)}}%</strong><small>{{C.at_least_two}} / {{C.institutions}} 家机构 · {{(C.window||[2022,2025]).join('—')}} 年至少两年发表论文</small></div>
    </div>
    <div class="rs-scroll"><svg class="rs-svg st-svg" viewBox="0 0 1300 760" role="img" aria-label="既有机构与新进入机构的机构数、项目数、年度经费，以及首次承担机构的后续论文产出">
      <defs><clipPath id="st-clip"><rect x="0" y="0" :width="clipW" height="480"/></clipPath></defs>
      <line v-for="r in split" :key="'v'+r.year" :x1="X(r.year)" :x2="X(r.year)" y1="30" y2="740" stroke="#efe9e6" stroke-dasharray="3 4"/>
      <text x="0" :y="IT+80" font-size="18" font-weight="750" fill="#2a2a2a">机构</text><text x="0" :y="IT+101" font-size="12.5" fill="#8a8286">每年承担项目的机构数</text>
      <text x="0" :y="AXY-4" font-size="18" font-weight="750" fill="#2a2a2a">经费</text><text x="0" :y="AXY+17" font-size="12.5" fill="#8a8286">年度批准经费</text>
      <text x="0" :y="PT+90" font-size="18" font-weight="750" fill="#2a2a2a">项目</text><text x="0" :y="PT+111" font-size="12.5" fill="#8a8286">每年批准的项目数</text>
      <g clip-path="url(#st-clip)">
        <path :d="P.iAll" fill="#efc3cc"/><path :d="P.iKeep" fill="#a21535"/>
        <path :d="P.pAll" fill="#efc3cc"/><path :d="P.pKeep" fill="#a21535"/>
        <text v-for="(r,i) in split" :key="'avg'+r.year" :x="i===0?X(r.year)+10:i===split.length-1?X(r.year)-10:X(r.year)" :y="PT+28" font-size="13" font-weight="700" fill="#fff" fill-opacity=".92" :text-anchor="i===0?'start':i===split.length-1?'end':'middle'">机构均 {{(totP(r)/tot(r)).toFixed(1)}} 项</text>
      </g>
      <text :x="X(2017)" :y="P.it[0][1]-12" font-size="18" font-weight="750" fill="#2a2a2a">{{tot(first)}} 家</text>
      <text :x="X(2017)" :y="P.pt[0][1]+24" font-size="18" font-weight="750" fill="#2a2a2a">{{fmt(totP(first))}} 项</text>
      <g v-if="shown>=2021" class="st-end">
        <text :x="X(2021)" :y="P.it.at(-1)[1]-12" font-size="18" font-weight="750" text-anchor="end" fill="#2a2a2a">{{tot(last)}} 家</text>
        <text :x="X(2021)" :y="P.pt.at(-1)[1]+24" font-size="18" font-weight="750" text-anchor="end" fill="#2a2a2a">{{fmt(totP(last))}} 项</text>
        <text :x="X(2021)+16" :y="(P.ik.at(-1)[1]+P.iBase)/2+5" font-size="14" font-weight="700" fill="#a21535">既有机构 {{last.retained_institutions}} 家</text>
        <text :x="X(2021)+16" :y="(P.ik.at(-1)[1]+P.it.at(-1)[1])/2+5" font-size="14" font-weight="700" fill="#c76b80">新进入 {{last.entered_institutions}} 家</text>
        <text :x="X(2021)+16" :y="(P.pk.at(-1)[1]+P.pBase)/2+5" font-size="14" font-weight="700" fill="#a21535">既有机构 {{fmt(last.retained_projects)}} 项</text>
        <text :x="X(2021)+16" :y="(P.pk.at(-1)[1]+P.pt.at(-1)[1])/2+5" font-size="14" font-weight="700" fill="#c76b80">新进入 {{last.entered_projects}} 项</text>
      </g>
      <!-- 年份 + 经费轴 -->
      <line :x1="X(2017)+52" :x2="X(2021)-52" :y1="AXY" :y2="AXY" stroke="#a21535" stroke-opacity=".22" stroke-width="2" stroke-dasharray="2 4"/>
      <g v-for="(a,i) in annual" :key="'f'+a.year" :opacity="a.year<=shown?1:.35">
        <rect :x="X(a.year)-50" :y="AXY-21" width="100" height="42" rx="21" fill="#fff" stroke="#a21535" :stroke-opacity=".25+i*.15" stroke-width="1.5"/>
        <text :x="X(a.year)" :y="AXY-4" font-size="12" font-weight="700" text-anchor="middle" fill="#7a7378">{{a.year}}</text>
        <text :x="X(a.year)" :y="AXY+14" font-size="15.5" font-weight="800" text-anchor="middle" fill="#a21535">{{a.amount_yi.toFixed(2)}} 亿</text>
      </g>
      <g v-if="top10[0]!=null"><text :x="X(2021)+70" :y="AXY-6" font-size="12.5" fill="#7a7378">前十机构经费占比</text><text :x="X(2021)+70" :y="AXY+15" font-size="16" font-weight="800" fill="#2a2a2a">{{top10[0]}}% → {{top10[1]}}%</text></g>
      <rect v-for="r in split" :key="'h'+r.year" class="rs-hit" :x="X(r.year)-90" y="30" width="180" height="440" fill="transparent" @mouseenter="yearTip($event,r)" @mousemove="move" @mouseleave="hide"/>
      <!-- 首次承担机构的后续论文 -->
      <line x1="0" x2="1300" y1="500" y2="500" stroke="#ece5e1"/>
      <text x="0" y="550" font-size="18" font-weight="750" fill="#2a2a2a">首次承担机构</text>
      <text x="0" y="571" font-size="12.5" fill="#8a8286">按首次承担 AI 项目的年份分组</text>
      <text x="0" y="589" font-size="12.5" fill="#8a8286">颜色：{{(C.window||[2022,2025]).join('—')}} 年发表相关论文的年数</text>
      <text x="0" y="607" font-size="12.5" fill="#8a8286">持续产出率：其中至少两年发表论文的机构占比</text>
      <text :x="X(2017)" :y="CB+20" font-size="12.5" text-anchor="middle" fill="#b0a7aa">2017 年为基准年</text>
      <g v-for="c in cohortYears" :key="'c'+c.year" class="rs-hit" @mouseenter="cohortTip($event,c)" @mousemove="move" @mouseleave="hide">
        <template v-for="(n,k) in c.v" :key="k"><rect :x="X(c.year)-46" :y="CB-c.v.slice(0,k+1).reduce((a,b)=>a+b,0)*BH" width="92" :height="n*BH" :fill="CC[k]"/>
          <text v-if="n>=8" :x="X(c.year)" :y="CB-c.v.slice(0,k).reduce((a,b)=>a+b,0)*BH-n*BH/2+4" font-size="11.5" font-weight="700" text-anchor="middle" :fill="k<2?'#fff':'#3d4c5c'">{{n}}</text></template>
        <text :x="X(c.year)" :y="CB-c.n*BH-30" font-size="24" font-weight="800" text-anchor="middle" fill="#1f4f80">{{Math.round(c.two/c.n*100)}}%</text>
        <text :x="X(c.year)" :y="CB-c.n*BH-12" font-size="12" text-anchor="middle" fill="#5d575b">持续产出率</text>
        <text :x="X(c.year)" :y="CB+20" font-size="12.5" font-weight="700" text-anchor="middle" fill="#3d3a3c">{{c.year}} 年首次承担 · {{c.n}} 家机构</text>
      </g>
      <g v-for="(t,k) in CL" :key="'l'+k"><rect :x="X(2021)+70" :y="CB-118+k*22" width="12" height="12" rx="2" :fill="CC[k]"/><text :x="X(2021)+88" :y="CB-107+k*22" font-size="12.5" fill="#6a6468">{{t}}</text></g>
    </svg></div>
    </template>
    <div v-if="tip.show" class="rs-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div>
  </section>
</template>
<style scoped>
.st-kpis{display:grid;grid-template-columns:132px repeat(3,1fr);margin:0 0 18px;border:1px solid #ece5e1;border-radius:6px;background:#fcfaf9}
.st-kpis>div{padding:15px 22px;border-left:1px solid #ece5e1}
.st-kpis>div:nth-child(n+5){border-top:1px solid #ece5e1}
.st-kpis>.st-group{border-left:0;display:flex;flex-direction:column;justify-content:center;font-size:15px;font-weight:750;color:var(--rs-ink);background:#f6f1ef}
.st-kpis>.st-group small{margin-top:2px;font-weight:500;white-space:nowrap}
.st-kpis span{display:block;font-size:13px;color:var(--rs-muted)}
.st-kpis strong{display:flex;align-items:baseline;gap:6px;margin:3px 0 2px;font-size:27px;font-weight:800;line-height:1.25;color:#a21535;font-variant-numeric:tabular-nums;white-space:nowrap}
.st-kpis strong em{font-style:normal;font-size:14px;font-weight:600;color:var(--rs-ink-2)}
.st-kpis strong.blue{color:#1f4f80}
.st-kpis small{display:block;font-size:12.5px;color:var(--rs-ink-2);line-height:1.5}
.st-svg{min-width:760px}
.st-end{animation:st-in .5s ease both}
@keyframes st-in{from{opacity:0}to{opacity:1}}
@media(max-width:1100px){.st-kpis{grid-template-columns:1fr 1fr 1fr}.st-kpis>.st-group{grid-column:1/-1;flex-direction:row;gap:10px;align-items:baseline;padding:10px 22px}.st-kpis>div:nth-child(2),.st-kpis>div:nth-child(6){border-left:0}.st-kpis>div{border-top:1px solid #ece5e1}.st-kpis>div:first-child{border-top:0}}
@media(max-width:600px){.st-kpis{grid-template-columns:1fr}.st-kpis>div{border-left:0!important}.st-kpis strong{font-size:23px}}
</style>
