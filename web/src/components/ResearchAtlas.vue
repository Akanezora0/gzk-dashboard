<script setup>
import {useSurface} from '../helpers/useSurface'
import {useYearPlayback} from '../helpers/useYearPlayback'
import {computed,ref,onBeforeUnmount,nextTick} from 'vue'
import {useTip,fmt,textWidth,toggleFullscreen,emph} from '../helpers/strengthTip.js'
const props=defineProps({dataset:Object})
const {tip,show,move,hide}=useTip()
const root=ref(null),closeBtn=ref(null)
const L=computed(()=>props.dataset?.landscape||{})
const annual=computed(()=>props.dataset?.strength?.annual||[])
const detailSurface=ref(null)
const region=ref('all'),focus=ref(''),picked=ref(null)
const {year,playing,play,pause,seek}=useYearPlayback(2017,2026)
useSurface(computed(()=>!!picked.value),{element:detailSurface,close:()=>picked.value=null})
const X0=290,YW=106,XT=t=>X0+(t-2017)*YW,XM=(y,m)=>XT(y+((m||6)-0.5)/12)
const LH=52,GG=14,TOP=92
const COL={cn:'#ae0d28',intl:'#2f5f7a'}
const groups=computed(()=>(L.value.groups||[]).filter(g=>region.value==='all'||g.region===region.value))
const layout=computed(()=>{let y=TOP;const lanes=[],bands=[];
  for(const g of groups.value){const y0=y;for(const l of g.lanes){lanes.push({...l,region:g.region,y:y+LH/2+4});y+=LH}bands.push({...g,y0,y1:y});y+=GG}
  return {lanes,bands,end:y-GG}})
const laneById=computed(()=>Object.fromEntries(layout.value.lanes.map(l=>[l.id,l])))
const events=computed(()=>{const lastEnd={};
  return (L.value.events||[]).filter(e=>laneById.value[e.org]).map(e=>{const lane=laneById.value[e.org];const x=XM(e.year,e.month);const fs=e.key?15:13.5;const w=textWidth(e.label,fs);
    const below=lastEnd[e.org]!==undefined&&x-w/2<lastEnd[e.org]+6;if(!below)lastEnd[e.org]=x+w/2
    return {...e,x,y:lane.y,fs,below,color:COL[lane.region],lane:lane.name}})})
const flows=computed(()=>(L.value.connections||[]).filter(c=>laneById.value[c.source]&&laneById.value[c.target]).map(c=>{
  const merge=c.kind==='merge',x=XT(c.year)-(merge?6:0),y0=laneById.value[c.source].y,y1=laneById.value[c.target].y,span=Math.abs(y1-y0)>LH*1.5?36:(merge?64:84),x0=x-span
  return {...c,merge,d:`M${x0},${y0} C${x0+span*.6},${y0} ${x-span*.5},${y1} ${x},${y1}`,x0,y0,x,y1}}))
const notes=computed(()=>(L.value.notes||[]).filter(n=>laneById.value[n.org]).map(n=>({...n,x:XT(n.year),y:laneById.value[n.org].y,pill:n.org==='brain'})))
const H=computed(()=>layout.value.end+130)
const yearsAxis=Array.from({length:10},(_,i)=>2017+i)
const nsfc=computed(()=>annual.value.map(a=>({...a,h:a.amount_yi/Math.max(...annual.value.map(z=>z.amount_yi),1)*42})))
const visible=e=>e.year+(e.month||6)/12<=year.value+1
function open(e){picked.value=e;hide();nextTick(()=>closeBtn.value?.focus())}
function evTip(ev,e){show(ev,`<b>${e.label}</b> · ${e.lane}<br>${e.year}.${e.month} · ${e.description}<br><span style="color:#78716c">${e.open?'开源 / 开放权重':'闭源 / 论文 / 事件'}${e.url?' · 点击查看来源':''}</span>`)}
</script>
<template>
  <section class="rs-page" ref="root" @keydown.esc="picked=null">
    <header class="rs-head"><span class="rs-no">03</span><h3>研究力量版图</h3>
      <div class="rs-tools">
        <div class="rs-seg" role="group" aria-label="机构范围"><button :class="{on:region==='all'}" @click="region='all'">全部</button><button :class="{on:region==='cn'}" @click="region='cn'">中国</button><button :class="{on:region==='intl'}" @click="region='intl'">国际</button></div>
        <button class="rs-btn" :class="{on:playing}" @click="play">{{playing?'Ⅱ 暂停':year>=2026?'▶ 重播':'▶ 播放'}}</button>
        <label class="rs-year">至 <b>{{year}}</b> 年<input type="range" min="2017" max="2026"  :value="year" @input="seek($event.target.value)" aria-label="显示到年份"></label></div></header>
    <div v-if="!L.groups" class="rs-empty">版图数据为旧格式，请在服务器运行 build_ai_chain.py 更新研究力量数据。</div>
    <template v-else>
    <div class="rs-legend">
      <span><i class="dot" style="background:#ae0d28"></i>中国机构</span><span><i class="dot" style="background:#2f5f7a"></i>国际机构</span>
      <span><i class="dot" style="background:#57534e"></i>开源 / 开放权重</span><span><i class="dot ring"></i>闭源 / 论文 / 事件</span>
      <span><i class="dot halo"></i>标志性成果</span><span><i class="dash"></i>人才流动与机构衍生</span>
    </div>
    <div class="rs-scroll"><svg class="rs-svg rs-atlas" :viewBox="`0 0 1370 ${H}`" role="img" aria-label="中外主要 AI 机构的里程碑成果与人才流动" :class="{focusing:!!focus}">
      <g v-for="(e,i) in L.eras" :key="'era'+i" class="rs-hit" @mouseenter="show($event,`<b>${e.label}</b>（${e.start}—${e.end-1}）<br>${e.description}`)" @mousemove="move" @mouseleave="hide">
        <rect :x="XT(e.start)+2" y="0" :width="XT(e.end)-XT(e.start)-4" height="34" rx="8" :fill="i%2?'#fff':'#efebe6'" :stroke="i%2?'#e8e4df':'none'"/>
        <text :x="(XT(e.start)+XT(e.end))/2" y="22" font-size="14.5" font-weight="700" fill="#57534e" text-anchor="middle">{{e.label}}</text></g>
      <text v-for="y in yearsAxis" :key="'yr'+y" :x="XT(y+.5)" y="66" font-size="15" font-weight="700" text-anchor="middle" :fill="y<=year?'#78716c':'#d6d0c9'">{{y}}</text>
      <g v-for="b in layout.bands" :key="b.id">
        <rect v-if="b.id.endsWith('inst')||b.id.endsWith('firm')&&b.region==='intl'" x="84" :y="b.y0" width="1276" :height="b.y1-b.y0" rx="10" fill="#faf8f6"/>
        <rect x="70" :y="b.y0+2" width="4" :height="b.y1-b.y0-4" rx="2" :fill="COL[b.region]"/>
        <text :x="56" :y="(b.y0+b.y1)/2" font-size="12.5" font-weight="700" text-anchor="middle" :fill="COL[b.region]" :transform="`rotate(-90 56 ${(b.y0+b.y1)/2})`">{{b.label}}</text></g>
      <line v-for="y in 11" :key="'g'+y" :x1="XT(2016+y)" :x2="XT(2016+y)" :y1="TOP-14" :y2="layout.end" stroke="#e9e5e0"/>
      <rect v-if="year<2026" :x="XT(year+1)" :y="TOP-14" :width="XT(2027)-XT(year+1)" :height="layout.end-TOP+14" fill="#f7f5f2" opacity=".55"/>
      <g v-for="l in layout.lanes" :key="l.id" class="rs-lane" :class="{on:focus===l.id}" @mouseenter="focus=l.id" @mouseleave="focus=''">
        <rect x="84" :y="l.y-LH/2-4" width="1276" :height="LH" fill="transparent"/>
        <text x="96" :y="l.y-1" font-size="16.5" font-weight="700" fill="#2a2a2a">{{l.name}}</text>
        <text x="96" :y="l.y+16" font-size="12.5" fill="#78716c">{{l.note}}</text>
        <g v-if="l.nsfc"><rect :x="96" :y="l.y+22" width="0" height="0" fill="none"/><text :x="284" :y="l.y+16" font-size="12" font-weight="700" fill="#ae0d28" text-anchor="end">NSFC · {{l.nsfc.projects}} 项</text></g>
        <line :x1="XT(l.start)" :x2="l.end?XT(l.end):XT(2027)-6" :y1="l.y" :y2="l.y" :stroke="COL[l.region]" stroke-width="2.2" opacity=".3" stroke-linecap="round"/>
        <circle v-if="l.start>2017" :cx="XT(l.start)" :cy="l.y" r="3.5" :fill="COL[l.region]" opacity=".6"/>
        <g v-for="e in events.filter(z=>z.org===l.id)" :key="e.id" class="rs-hit" :opacity="visible(e)?1:.12" @mouseenter="evTip($event,e)" @mousemove="move" @mouseleave="hide" @click="open(e)">
          <circle v-if="e.key" :cx="e.x" :cy="e.y" r="13" :fill="e.color" opacity=".16"/>
          <circle :cx="e.x" :cy="e.y" :r="e.key?7:5.2" :fill="e.open?e.color:'#fff'" :stroke="e.color" stroke-width="2"/>
          <text :x="e.x" :y="e.below?e.y+23:e.y-12" :font-size="e.fs" :font-weight="e.key?700:500" :fill="e.key?e.color:'#2a2a2a'" text-anchor="middle">{{e.label}}</text>
        </g>
      </g>
      <g v-for="f in flows" :key="f.id" class="rs-hit" :opacity="f.year<=year+1?1:.15" @mouseenter="show($event,`<b>${f.label}</b><br>${f.description}`)" @mousemove="move" @mouseleave="hide" @click="f.url&&open({label:f.label,lane:'机构关系',year:Math.floor(f.year),month:'',description:f.description,url:f.url,flow:true})">
        <path :d="f.d" fill="none" :stroke="f.merge?'#2f5f7a':'#ae0d28'" stroke-width="1.7" :stroke-dasharray="f.merge?'':'4 3'"/>
        <path :d="f.d" fill="none" stroke="transparent" stroke-width="10"/>
        <circle :cx="f.x0" :cy="f.y0" r="2.8" :fill="f.merge?'#2f5f7a':'#ae0d28'"/>
        <text :x="f.x-8" :y="f.y1+17" font-size="12.5" :fill="f.merge?'#2f5f7a':'#ae0d28'" text-anchor="end">{{f.label}}</text></g>
      <g v-for="(n,i) in notes" :key="'n'+i">
        <template v-if="n.pill"><rect :x="n.x" :y="n.y-15" :width="XT(2027)-12-n.x" height="30" rx="15" fill="#fbeef0"/><text :x="n.x+14" :y="n.y+5" :textLength="XT(2027)-40-n.x" lengthAdjust="spacingAndGlyphs" font-size="13.5" font-weight="500" fill="#ae0d28">{{n.text.replace('OpenAI 人才外溢：','OpenAI 人才外溢 → ')}}</text></template>
        <text v-else :x="n.x-8" :y="n.y+5" font-size="12.5" fill="#ae0d28" text-anchor="end">{{n.text}}</text></g>
      <g v-if="nsfc.length" :transform="`translate(0,${layout.end+22})`">
        <rect x="84" y="0" width="1276" height="84" rx="10" fill="#fbeef0"/>
        <text x="96" y="30" font-size="15" font-weight="700" fill="#ae0d28">本项目数据</text>
        <text x="96" y="50" font-size="12" fill="#57534e">NSFC 人工智能项目</text>
        <text x="96" y="66" font-size="12" fill="#57534e">年度批准经费（亿元）</text>
        <g v-for="a in nsfc" :key="a.year" class="rs-hit" @mouseenter="show($event,`<b>${a.year} 年 NSFC AI 项目</b><br>批准经费 ${a.amount_yi.toFixed(2)} 亿元 · ${fmt(a.projects)} 项 · ${a.institutions} 家机构`)" @mousemove="move" @mouseleave="hide">
          <rect :x="XT(a.year)+20" :y="74-a.h" :width="YW-40" :height="a.h" rx="4" fill="#ae0d28" opacity=".85"/>
          <text :x="XT(a.year)+YW/2" :y="68-a.h" font-size="13" font-weight="700" fill="#7a0a1c" text-anchor="middle">{{a.amount_yi.toFixed(2)}}</text></g>
        <text :x="XT(2022)+10" y="70" font-size="12" fill="#a8a29e">2022 年后补录中</text>
        <text :x="XT(2023.3)" y="34" font-size="14.5" font-weight="700" fill="#ae0d28">承担机构 {{nsfc[0].institutions}} → {{nsfc.at(-1).institutions}} 家 · 项目 {{fmt(nsfc[0].projects)}} → {{fmt(nsfc.at(-1).projects)}} 项</text>
        <text :x="XT(2023.3)" y="56" font-size="12.5" fill="#57534e">清华、中科院自动化所、鹏城实验室均在资助名单中</text>
      </g>
    </svg></div>
    <aside v-if="picked" class="rs-atlas-card" ref="detailSurface" role="dialog" aria-label="成果详情">
      <button ref="closeBtn" class="rs-close" aria-label="关闭" @click="picked=null">×</button>
      <p class="k">{{picked.lane}}<template v-if="picked.month"> · {{picked.year}}.{{picked.month}}</template></p>
      <h4>{{picked.label}}</h4>
      <p>{{picked.description}}</p>
      <p v-if="!picked.flow" class="k">{{picked.open?'开源 / 开放权重':'闭源 / 论文 / 事件'}}</p>
      <a v-if="picked.url" :href="picked.url" target="_blank" rel="noopener">查看来源 ↗</a>
    </aside>
    <div class="rs-take"><span class="rs-take-tag">结论</span><p>前沿成果的产出从企业研究院与高校并行，转向少数企业实验室主导，人才外溢催生了 Anthropic、Mistral 等新力量；中国以清华等高校和国家实验室为源头，经衍生企业与开源模型在 2023 年后快速跟进。</p></div>
    </template>
    <div v-if="tip.show" class="rs-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div>
  </section>
</template>
<style scoped>
.rs-legend{display:flex;flex-wrap:wrap;gap:8px 22px;font-size:13.5px;color:var(--rs-ink-2);margin:0 0 10px}
.rs-legend span{display:inline-flex;align-items:center;gap:7px}
.rs-legend .dot{width:11px;height:11px;border-radius:50%;display:inline-block}
.rs-legend .ring{border:2px solid #57534e;background:#fff;width:10px;height:10px}
.rs-legend .halo{background:#57534e;box-shadow:0 0 0 5px rgba(87,83,78,.18)}
.rs-legend .dash{width:30px;border-top:2px dashed #ae0d28}
.rs-year{display:inline-flex;align-items:center;gap:8px;font-size:14px;color:var(--rs-ink-2)}
.rs-year input{width:120px;accent-color:#ae0d28}
.rs-scroll>.rs-atlas{min-width:1000px}
.rs-lane{transition:opacity .15s}
.rs-atlas.focusing .rs-lane:not(.on){opacity:.3}
.rs-atlas-card{position:absolute;right:34px;top:150px;width:320px;background:#fff;border:1px solid var(--rs-line);border-radius:12px;box-shadow:0 12px 34px rgba(40,20,20,.14);padding:20px 22px;z-index:5}
.rs-atlas-card h4{font-size:22px;margin:4px 0 8px}
.rs-atlas-card p{font-size:14.5px;line-height:1.7;margin:0 0 8px;color:var(--rs-ink-2)}
.rs-atlas-card .k{font-size:13px;color:var(--rs-muted)}
.rs-atlas-card a{color:var(--rs-red);font-weight:600;text-decoration:none}
.rs-close{position:absolute;right:12px;top:10px;width:30px;height:30px;border-radius:50%;border:0;background:#f5f3f0;font-size:19px;cursor:pointer;color:var(--rs-ink-2)}
@media(prefers-reduced-motion:reduce){.rs-lane{transition:none}}
</style>
