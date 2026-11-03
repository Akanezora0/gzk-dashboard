<script setup>
import {computed,ref,onBeforeUnmount} from 'vue'
import {useTip,fmt,toggleFullscreen} from '../helpers/strengthTip.js'
const props=defineProps({dataset:Object})
const {tip,show,move,hide}=useTip()
const root=ref(null)
const S=computed(()=>props.dataset?.strength||{})
const split=computed(()=>S.value.split||[])
const annual=computed(()=>S.value.annual||[])
const years=computed(()=>split.value.map(r=>r.year))
const AX=290,X=y=>200+(y-2017)*170,KO=0.6,KP=0.13,G=16
const shown=ref(2021),playing=ref(false);let timer=null
const clipW=computed(()=>X(shown.value)+(shown.value>=2021?90:85))
function play(){if(playing.value){stop();return}shown.value=2017;playing.value=true;timer=setInterval(()=>{if(shown.value>=2021)stop();else shown.value++},900)}
function stop(){clearInterval(timer);playing.value=false;shown.value=2021}
onBeforeUnmount(()=>clearInterval(timer))
function band(inner,outer,dir){
  const pts=split.value.map((r,i)=>[X(r.year),inner[i],outer[i]])
  if(!pts.length)return ''
  const ex=[[X(2017)-40,pts[0][1],pts[0][2]],...pts,[X(2021)+40,pts.at(-1)[1],pts.at(-1)[2]]]
  let d=`M${ex[0][0]},${AX+dir*ex[0][1]}`
  for(let i=1;i<ex.length;i++){const m=(ex[i-1][0]+ex[i][0])/2;d+=` C${m},${AX+dir*ex[i-1][1]} ${m},${AX+dir*ex[i][1]} ${ex[i][0]},${AX+dir*ex[i][1]}`}
  d+=` L${ex.at(-1)[0]},${AX+dir*ex.at(-1)[2]}`
  for(let i=ex.length-2;i>=0;i--){const m=(ex[i+1][0]+ex[i][0])/2;d+=` C${m},${AX+dir*ex[i+1][2]} ${m},${AX+dir*ex[i][2]} ${ex[i][0]},${AX+dir*ex[i][2]}`}
  return d+' Z'}
const oOld=computed(()=>split.value.map(r=>r.retained_institutions*KO)),oNew=computed(()=>split.value.map(r=>r.entered_institutions*KO))
const pOld=computed(()=>split.value.map(r=>r.retained_projects*KP)),pNew=computed(()=>split.value.map(r=>r.entered_projects*KP))
const paths=computed(()=>({
  b1:band(split.value.map(()=>G),oOld.value.map(v=>v+G),-1),
  b2:band(oOld.value.map(v=>v+G+2),oOld.value.map((v,i)=>v+G+2+oNew.value[i]),-1),
  b3:band(split.value.map(()=>G),pOld.value.map(v=>v+G),1),
  b4:band(pOld.value.map(v=>v+G+2),pOld.value.map((v,i)=>v+G+2+pNew.value[i]),1)}))
const last=computed(()=>split.value.at(-1)||{}),first=computed(()=>split.value[0]||{})
const lastI=computed(()=>split.value.length-1)
const tot=r=>(r.retained_institutions||0)+(r.entered_institutions||0),totP=r=>(r.retained_projects||0)+(r.entered_projects||0)
const funding=computed(()=>S.value.retained_2021||[])
const fundShare=computed(()=>{const a=funding.value.find(r=>r.present_2017),s=funding.value.reduce((x,r)=>x+r.amount_yi,0);return a&&s?Math.round(a.amount_yi/s*100):null})
const projShare=computed(()=>totP(last.value)?Math.round(last.value.retained_projects/totP(last.value)*100):null)
const growth=computed(()=>tot(first.value)?Math.round((tot(last.value)/tot(first.value)-1)*100):null)
const C=computed(()=>S.value.cohort||{})
const steps=computed(()=>[[C.value.institutions,'首次进入的机构'],[C.value.with_any,'后续有相关论文'],[C.value.at_least_two,'至少两年有论文'],[C.value.all_four,'四年都有论文']])
function yearTip(e,r,i){const a=annual.value.find(x=>x.year===r.year);show(e,`<b>${r.year} 年</b><br>机构 ${fmt(tot(r))} 家（既有 ${r.retained_institutions} · 新进入 ${r.entered_institutions}）<br>项目 ${fmt(totP(r))} 项（既有 ${fmt(r.retained_projects)} · 新进入 ${r.entered_projects}）${a?`<br>批准经费 ${a.amount_yi.toFixed(2)} 亿元 · 前十机构份额 ${a.top10_amount_pct}%`:''}`)}
</script>
<template>
  <section class="rs-page" ref="root">
    <header class="rs-head"><span class="rs-no">02</span><h3>机构参与</h3><span class="rs-sub">AI 基金项目，2017—2021 年批准</span>
      <div class="rs-tools"><button class="rs-btn" :class="{on:playing}" @click="play">{{playing?'停止':'▶ 按年播放'}}</button><button class="rs-btn" @click="toggleFullscreen(root)">全屏 / 退出</button></div></header>
    <div v-if="!split.length" class="rs-empty">机构参与数据尚未生成，请在服务器运行 build_ai_chain.py 更新研究力量数据。</div>
    <div v-else class="rs-trend">
      <div class="rs-scroll rs-fit"><svg class="rs-svg" viewBox="0 0 1100 660" role="img" aria-label="既有机构与新进入机构的机构数和项目数">
        <defs><clipPath id="rs-trend-clip"><rect x="0" y="0" :width="clipW" height="660"/></clipPath></defs>
        <text x="0" :y="AX-140" font-size="26" font-weight="700" fill="#2a2a2a">机构</text>
        <text x="0" :y="AX-114" font-size="15" fill="#78716c">每年承担项目</text><text x="0" :y="AX-95" font-size="15" fill="#78716c">的机构数</text>
        <text x="0" :y="AX+120" font-size="26" font-weight="700" fill="#2a2a2a">项目</text>
        <text x="0" :y="AX+146" font-size="15" fill="#78716c">每年批准的</text><text x="0" :y="AX+165" font-size="15" fill="#78716c">项目数</text>
        <g clip-path="url(#rs-trend-clip)">
          <path :d="paths.b1" fill="#ae0d28"/><path :d="paths.b2" fill="#f0b7bf"/>
          <path :d="paths.b3" fill="#ae0d28"/><path :d="paths.b4" fill="#f0b7bf"/>
          <text :x="X(2017)" :y="AX-oOld[0]-G-14" font-size="26" font-weight="700" text-anchor="middle" fill="#2a2a2a">{{tot(first)}} 家</text>
          <text :x="X(2017)" :y="AX+pOld[0]+G+32" font-size="26" font-weight="700" text-anchor="middle" fill="#2a2a2a">{{fmt(totP(first))}} 项</text>
        </g>
        <template v-if="shown>=2021">
          <text :x="X(2021)" :y="AX-oOld[lastI]-oNew[lastI]-G-14" font-size="26" font-weight="700" text-anchor="middle" fill="#2a2a2a">{{tot(last)}} 家</text>
          <text :x="X(2021)" :y="AX+pOld[lastI]+pNew[lastI]+G+32" font-size="26" font-weight="700" text-anchor="middle" fill="#2a2a2a">{{fmt(totP(last))}} 项</text>
          <text :x="X(2021)+52" :y="AX-G-oOld[lastI]/2+6" font-size="19" font-weight="700" fill="#ae0d28">既有机构 {{last.retained_institutions}} 家</text>
          <text :x="X(2021)+52" :y="AX-G-oOld[lastI]-oNew[lastI]/2+6" font-size="19" font-weight="700" fill="#d9737f">新进入 {{last.entered_institutions}} 家</text>
          <text :x="X(2021)+52" :y="AX+G+pOld[lastI]/2+6" font-size="19" font-weight="700" fill="#ae0d28">既有机构 {{fmt(last.retained_projects)}} 项</text>
          <text :x="X(2021)+52" :y="AX+G+pOld[lastI]+pNew[lastI]/2+6" font-size="19" font-weight="700" fill="#d9737f">新进入 {{last.entered_projects}} 项</text>
          <text v-if="fundShare" :x="X(2021)+52" :y="AX+G+pOld[lastI]/2+30" font-size="18" fill="#57534e">经费占 {{fundShare}}%</text>
        </template>
        <text v-for="r in split" :key="'y'+r.year" :x="X(r.year)" :y="AX+6" font-size="17" font-weight="700" text-anchor="middle" :fill="r.year<=shown?'#57534e':'#d6d0c9'">{{r.year}}</text>
        <text x="0" y="640" font-size="18" fill="#78716c">年度批准经费</text>
        <text v-for="a in annual" :key="'a'+a.year" :x="X(a.year)" y="640" font-size="20" font-weight="700" text-anchor="middle" :fill="a.year<=shown?'#57534e':'#d6d0c9'">{{a.amount_yi.toFixed(2)}} 亿</text>
        <rect v-for="(r,i) in split" :key="'h'+r.year" class="rs-hit" :x="X(r.year)-80" y="20" width="160" height="600" fill="transparent" @mouseenter="yearTip($event,r,i)" @mousemove="move" @mouseleave="hide"/>
      </svg></div>
      <aside class="rs-stay">
        <h4>新进入的机构，留下来了吗？</h4>
        <p>{{C.entry_years?.[0]}}—{{C.entry_years?.[1]}} 年首次进入的机构，此后 4 年的论文</p>
        <div v-for="(s,i) in steps" :key="i" class="rs-stay-row">
          <div class="rs-stay-bar"><i :style="{width:(s[0]/(C.institutions||1)*100)+'%',background:i===0?'#d3e2ec':i===2?'#2f5f7a':'#5b8aa5'}"></i><em v-if="i>0">{{Math.round(s[0]/(C.institutions||1)*100)}}%</em></div>
          <div class="rs-stay-num"><strong :class="{first:i===0}">{{s[0]}}</strong><span>家</span><b>{{s[1]}}</b></div>
        </div>
      </aside>
    </div>
    <div class="rs-take"><p>资助呈现“稳定主体＋持续扩面”：参与机构增加 {{growth!==null?`${growth}%`:'六成'}}，{{last.year}} 年 {{projShare}}% 的项目、{{fundShare}}% 的经费仍由既有机构承担；首次进入的 {{C.institutions}} 家机构中，{{C.at_least_two}} 家在后续至少两年持续产出论文。</p></div>
    <p class="rs-foot">既有：2017 年已有 AI 项目的机构；新进入：2017 年无 AI 项目的机构。右侧“首次进入”按全部历史 AI 项目确定，两种口径不同。近期立项仍在补录，图中只画到 2021 年。</p>
    <div v-if="tip.show" class="rs-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div>
  </section>
</template>
<style scoped>
.rs-fit>.rs-svg{min-width:560px}
.rs-trend{display:grid;grid-template-columns:minmax(0,1fr) 290px;gap:34px;align-items:start}
.rs-stay{border-left:1px solid var(--rs-line);padding-left:30px;padding-top:6px}
.rs-stay h4{font-size:21px;margin:0 0 4px;font-weight:700}
.rs-stay>p{font-size:14px;color:var(--rs-muted);margin:0 0 26px}
.rs-stay-row{margin-bottom:26px}
.rs-stay-bar{display:flex;align-items:center;gap:10px;height:30px}
.rs-stay-bar i{display:block;height:30px;border-radius:5px}
.rs-stay-bar em{font-style:normal;font-weight:700;font-size:17px;color:var(--rs-blue)}
.rs-stay-num{margin-top:6px;display:flex;align-items:baseline;gap:6px}
.rs-stay-num strong{font-size:34px;font-weight:750;color:var(--rs-blue);line-height:1.1}
.rs-stay-num strong.first{color:var(--rs-ink)}
.rs-stay-num span{font-size:15px;color:var(--rs-muted)}
.rs-stay-num b{font-size:16px;font-weight:500;color:var(--rs-ink-2);margin-left:6px}
@media(max-width:1100px){.rs-trend{grid-template-columns:1fr}.rs-stay{border-left:0;padding-left:0;border-top:1px solid var(--rs-line);padding-top:20px}}
</style>
