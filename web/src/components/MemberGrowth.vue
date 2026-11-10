<script setup>
/* 05 项目参与人成长为负责人：左侧“参与项目类型 → 首次负责项目类型”流向，右侧代表案例 */
import {computed,ref} from 'vue'
import {useSurface} from '../helpers/useSurface'
import {useTip,fmt,emph,TYPE_NAME,TYPE_SHORT,TYPE_COLOR} from '../helpers/strengthTip.js'
import {useMemberGrowth} from '../helpers/memberGrowth.js'
const emit=defineEmits(['all'])
const {data,error}=useMemberGrowth()
const {tip,show,move,hide}=useTip()
const picked=ref(null),dialog=ref(null)
useSurface(computed(()=>!!picked.value),{element:dialog,close:()=>picked.value=null,modal:true})
const S=computed(()=>data.value?.summary||{}),cases=computed(()=>data.value?.cases||[])
const ORDER=['青年','地区','面上','重点等']
const n=computed(()=>cases.value.length)
const pct=(a,b)=>b?Math.round(a/b*100):0
const sameInst=computed(()=>pct(S.value.same_institution,n.value))
const share=computed(()=>((S.value.people||0)/(S.value.ai_participants||1)*100).toFixed(1))
const laterYouth=computed(()=>pct(cases.value.filter(c=>c.later_group==='青年').length,n.value))
const laterGeneral=computed(()=>pct(cases.value.filter(c=>c.later_group==='面上').length,n.value))
const within2=computed(()=>pct(cases.value.filter(c=>c.gap<=2).length,n.value))
const meanGap=computed(()=>n.value?(cases.value.reduce((t,c)=>t+(c.gap||0),0)/n.value).toFixed(1):'—')
const takeText=computed(()=>`${fmt(S.value.people)} 位人工智能基金项目参与人此后担任项目负责人，占参与人 ${share.value}%；从参与到负责平均间隔 ${meanGap.value} 年，${sameInst.value}% 在同一单位成长。`)
// 流向：左侧参与的项目类型，右侧首次负责的项目类型
const flows=computed(()=>{const m=new Map();for(const c of cases.value){const k=c.early_group+'>'+c.later_group;m.set(k,(m.get(k)||0)+1)}return [...m].map(([k,v])=>{const [a,b]=k.split('>');return {a,b,n:v}})})
const out=t=>flows.value.filter(f=>f.a===t).reduce((s,f)=>s+f.n,0),inn=t=>flows.value.filter(f=>f.b===t).reduce((s,f)=>s+f.n,0)
const LX=128,RX=372,TOP=20,GAP=14,NW=14,K=computed(()=>360/Math.max(1,n.value))
const sankey=computed(()=>{const k=K.value,posL={},posR={};let yl=TOP,yr=TOP
 for(const t of ORDER){const o=out(t),i=inn(t);if(o){posL[t]={y:yl,h:o*k};yl+=o*k+GAP}if(i){posR[t]={y:yr,h:i*k};yr+=i*k+GAP}}
 const ol={},or={};ORDER.forEach(t=>{ol[t]=0;or[t]=0})
 const links=[...flows.value].sort((p,q)=>ORDER.indexOf(p.a)-ORDER.indexOf(q.a)||ORDER.indexOf(p.b)-ORDER.indexOf(q.b)).map(f=>{const h=f.n*k,y0=posL[f.a].y+ol[f.a],y1=posR[f.b].y+or[f.b];ol[f.a]+=h;or[f.b]+=h;const mx=(LX+NW+RX)/2
  const key=f.n/n.value>=.1
  return {...f,h,y0,y1,mx,key,d:`M${LX+NW},${y0} C${mx},${y0} ${mx},${y1} ${RX},${y1} L${RX},${y1+h} C${mx},${y1+h} ${mx},${y0+h} ${LX+NW},${y0+h} Z`,fill:key?TYPE_COLOR[f.b]:'#cfc8c1',op:key?.75:.3}})
 return {posL,posR,links,height:Math.max(yl,yr)+10}})
const labelL=t=>t==='重点等'?'联合·重大等':TYPE_SHORT[t]+'项目',labelR=labelL
const top=computed(()=>sankey.value.links.filter(l=>l.key))
function flowTip(e,l){const names=cases.value.filter(c=>c.early_group===l.a&&c.later_group===l.b).slice(0,4).map(c=>c.person_name).join('、')
 show(e,`<b>参与${TYPE_NAME[l.a]} → 负责${TYPE_NAME[l.b]}</b><br>${l.n} 人（占全部 ${pct(l.n,n.value)}%）<br><span style="color:#78716c">如：${names}</span>`)}
// 代表案例：人工选取有代表性的成长路径（含中国人民大学），按首次负责年份排序
const FEATURED=['张静','连德富','叶翰嘉','张伟楠','况琨','李戈','苏航','桂韬']
const featured=computed(()=>FEATURED.map(nm=>cases.value.find(c=>c.person_name===nm)).filter(Boolean))
const amount=c=>c.later_amount?`${c.later_amount}${c.later_unit||''}`:''
</script>
<template>
 <section class="rs-page">
  <header class="rs-head"><span class="rs-no">05</span><h3>项目参与人成长为负责人</h3></header>
  <div v-if="error" class="rs-empty">{{error}}</div>
  <div v-else-if="!data" class="rs-empty">正在读取成长案例…</div>
  <template v-else>
   <p class="rs-lead soft" v-html="emph(takeText)"></p>
   <div class="mg">
    <div class="mg-left">
     <h4>从参与到负责</h4>
     <p class="mg-lead">左侧为曾参与的项目类型，右侧为首次负责的项目类型</p>
     <svg class="rs-svg" :viewBox="`0 0 520 ${sankey.height}`" role="img" aria-label="参与项目类型到首次负责项目类型的流向">
      <g v-for="l in sankey.links" :key="l.a+l.b" class="rs-hit" @mouseenter="flowTip($event,l)" @mousemove="move" @mouseleave="hide"><path :d="l.d" :fill="l.fill" :opacity="l.op"/></g>
      <text :x="LX+NW/2" y="12" font-size="13" text-anchor="middle" fill="#78716c">参与</text><text :x="RX+NW/2" y="12" font-size="13" text-anchor="middle" fill="#78716c">负责</text>
      <template v-for="t in ORDER" :key="t">
       <g v-if="sankey.posL[t]"><rect :x="LX" :y="sankey.posL[t].y" :width="NW" :height="sankey.posL[t].h" rx="3" :fill="TYPE_COLOR[t]"/>
        <text v-if="sankey.posL[t].h>9" :x="LX-14" :y="sankey.posL[t].y+sankey.posL[t].h/2+5" font-size="15" text-anchor="end" fill="#2a2a2a">{{labelL(t)}}</text></g>
       <g v-if="sankey.posR[t]"><rect :x="RX" :y="sankey.posR[t].y" :width="NW" :height="sankey.posR[t].h" rx="3" :fill="TYPE_COLOR[t]"/>
        <text v-if="sankey.posR[t].h>9" :x="RX+NW+14" :y="sankey.posR[t].y+sankey.posR[t].h/2+5" font-size="15" fill="#2a2a2a">{{labelR(t)}}</text></g>
      </template>
      <g v-for="l in top" :key="'lb'+l.a+l.b" pointer-events="none" :fill="l.b==='青年'?'#7a0a1c':'#fff'"><text :x="l.mx" :y="(l.y0+l.y1)/2+l.h/2+(l.h>60?-2:4)" :font-size="l.h>60?28:22" font-weight="700" text-anchor="middle">{{pct(l.n,n)}}%</text>
       <text v-if="l.h>40" :x="l.mx" :y="(l.y0+l.y1)/2+l.h/2+20" font-size="13" text-anchor="middle">{{fmt(l.n)}} / {{fmt(n)}} 人 · 参与{{labelL(l.a)}}</text></g>
     </svg>
     <div class="rs-keys">
      <div><strong>{{fmt(S.people)}}</strong><span>参与后担任项目负责人<small>人工智能基金参与人 {{fmt(S.ai_participants)}} 人</small></span></div>
      <div><strong>{{meanGap}}<em>年</em></strong><span>从参与到负责的平均间隔<small>{{within2}}% 在 2 年内</small></span></div>
      <div><strong>{{laterYouth}}%</strong><span>首次负责青年科学基金<small>面上项目 {{laterGeneral}}%</small></span></div>
      <div><strong>{{sameInst}}%</strong><span>在同一单位成长<small>{{fmt(S.same_institution)}} 人</small></span></div>
     </div>
    </div>
    <div class="mg-right">
     <h4>代表案例</h4>
     <p class="mg-lead">参与他人主持的项目后，独立承担人工智能基金项目</p>
     <button v-for="c in featured" :key="c.person_id" type="button" class="mg-case" :class="{on:picked===c}" @click="picked=c">
      <span class="who"><b>{{c.person_name}}</b><small>{{c.later_inst}}</small></span>
      <span class="steps">
       <span class="pill"><em class="part">参与 {{c.early_year}}</em><span class="topic" :title="c.early_title">{{c.early_title}}</span></span>
       <i class="rib"></i>
       <span class="pill"><em :style="{background:TYPE_COLOR[c.later_group],color:c.later_group==='青年'?'#7a0a1c':'#fff'}">负责 {{TYPE_SHORT[c.later_group]}} {{c.later_year}}</em><span class="topic" :title="c.later_title">{{c.later_title}}</span></span>
      </span>
     </button>
     <button type="button" class="rs-btn mg-all" @click="emit('all')">查看全部 {{fmt(n)}} 个成长案例 →</button>
    </div>
   </div>
  </template>
  <Teleport to="body"><div v-if="picked" class="rs-modal-mask" @click.self="picked=null">
   <div ref="dialog" class="rs-modal" role="dialog" aria-modal="true" :aria-label="`${picked.person_name}的成长路径`">
    <button class="rs-modal-x" aria-label="关闭" @click="picked=null">×</button>
    <p class="rs-modal-who"><b>{{picked.person_name}}</b><span>{{picked.later_inst}}</span></p>
    <ol class="rs-modal-steps">
     <li><em class="part">{{picked.early_year}} · 参与{{picked.early_type}}</em><b>{{picked.early_title}}</b><small>批准号 {{picked.early_grant}} · 负责人 {{picked.early_pi}} · {{picked.early_inst}}</small></li>
     <li><em :style="{background:TYPE_COLOR[picked.later_group],color:picked.later_group==='青年'?'#7a0a1c':'#fff'}">{{picked.later_year}} · 负责{{picked.later_type}}</em><b>{{picked.later_title}}</b><small>批准号 {{picked.later_grant}}{{amount(picked)?' · '+amount(picked):''}} · {{picked.later_inst}}</small></li>
    </ol>
    <p class="mg-gap">间隔 {{picked.gap}} 年 · {{picked.early_inst===picked.later_inst?'同一单位':'更换单位'}}</p>
   </div></div></Teleport>
  <div v-if="tip.show" class="rs-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div>
 </section>
</template>
<style scoped>
.mg{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:36px}
.mg h4{font-size:22px;margin:0;font-weight:700}
.mg-lead{font-size:16px;color:var(--rs-red);font-weight:500;margin:6px 0 16px}
.mg-right{border-left:1px solid var(--rs-line);padding-left:36px;display:flex;flex-direction:column;gap:4px}
.mg-case{display:grid;grid-template-columns:120px minmax(0,1fr);align-items:center;gap:14px;width:100%;text-align:left;background:none;border:0;border-radius:12px;padding:8px;cursor:pointer;font-family:inherit}
.mg-case:hover,.mg-case.on{background:#f7f5f2}
.who b{display:block;font-size:17px;color:var(--rs-ink)}.who small{font-size:12.5px;color:var(--rs-muted)}
.steps{display:flex;flex-direction:column;align-items:flex-start;min-width:0}
.pill{display:inline-flex;align-items:center;gap:9px;border:1px solid var(--rs-line);background:#fff;border-radius:20px;padding:3px 14px 3px 4px;font-size:14.5px;color:var(--rs-ink);white-space:nowrap;max-width:100%;overflow:hidden}
.topic{overflow:hidden;text-overflow:ellipsis;min-width:0}
.pill em,.rs-modal-steps em{font-style:normal;font-size:12.5px;font-weight:700;border-radius:14px;padding:3px 10px;flex:none}
em.part{background:#fff;color:#57534e;border:1px dashed #bfb6ae}
.rib{display:block;width:3px;height:6px;margin-left:34px;background:#d9737f;opacity:.6}
.mg-all{align-self:flex-start;margin-top:10px}
.rs-keys{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:18px}
.rs-keys>div{background:#faf7f5;border:1px solid #efe8e4;border-radius:12px;padding:14px 16px;display:flex;flex-direction:column;gap:4px}
.rs-keys strong{font-size:34px;font-weight:750;color:var(--rs-red);line-height:1.1;font-variant-numeric:tabular-nums}.rs-keys strong em{font-style:normal;font-size:16px;margin-left:3px}
.rs-keys span{font-size:15px;font-weight:600;color:var(--rs-ink);line-height:1.45}.rs-keys small{display:block;font-size:13px;color:var(--rs-muted);font-weight:400}
.mg-gap{margin:0;font-size:14px;color:#78716c}
.rs-modal-mask{position:fixed;inset:0;z-index:80;background:rgba(40,30,28,.32);display:grid;place-items:center;padding:16px}
.rs-modal{position:relative;width:min(760px,100%);max-height:88vh;overflow-y:auto;background:#fff;border-radius:16px;box-shadow:0 20px 60px rgba(40,20,20,.25);padding:28px 30px 26px}
.rs-modal-x{position:absolute;right:14px;top:12px;width:34px;height:34px;border-radius:50%;border:0;background:#f5f3f0;font-size:20px;cursor:pointer;color:#57534e}
.rs-modal-who{margin:0 0 16px;display:flex;align-items:baseline;gap:12px}.rs-modal-who b{font-size:24px}.rs-modal-who span{color:#78716c;font-size:15px}
.rs-modal-steps{list-style:none;margin:0 0 14px;padding:0 0 0 18px;border-left:2px solid #f0b7bf;display:grid;gap:16px}
.rs-modal-steps li{position:relative}.rs-modal-steps li::before{content:"";position:absolute;left:-25px;top:6px;width:12px;height:12px;border-radius:50%;background:#ae0d28;border:2px solid #fff}
.rs-modal-steps em{display:inline-block;margin-bottom:6px}
.rs-modal-steps b{display:block;font-size:16px;line-height:1.5;color:#2a2a2a}.rs-modal-steps small{color:#78716c;font-size:13px}
@media(max-width:1100px){.mg{grid-template-columns:1fr}.mg-right{border-left:0;padding-left:0}}
@media(max-width:700px){.mg-case{grid-template-columns:1fr}}
</style>
