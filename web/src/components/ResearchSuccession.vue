<script setup>
import {computed,ref} from 'vue'
import {useTip,fmt,toggleFullscreen,typeGroup,TYPE_NAME,TYPE_SHORT,TYPE_COLOR} from '../helpers/strengthTip.js'
const props=defineProps({dataset:Object})
const emit=defineEmits(['explore'])
const {tip,show,move,hide}=useTip()
const root=ref(null),picked=ref(null)
const records=computed(()=>Array.isArray(props.dataset?.continuity)?props.dataset.continuity:[])
const ORDER=['青年','地区','面上','重点等']
const flows=computed(()=>{const c=new Map();for(const r of records.value){const k=typeGroup(r.earlier_project_type)+'>'+typeGroup(r.later_project_type);c.set(k,(c.get(k)||0)+1)}
  return [...c].map(([k,n])=>{const [a,b]=k.split('>');return {a,b,n}})})
const out=t=>flows.value.filter(f=>f.a===t).reduce((s,f)=>s+f.n,0),inn=t=>flows.value.filter(f=>f.b===t).reduce((s,f)=>s+f.n,0)
const flowN=(a,b)=>flows.value.find(f=>f.a===a&&f.b===b)?.n||0
const pct=(a,b)=>out(a)?Math.round(flowN(a,b)/out(a)*100):0
const overlapPct=t=>{const rs=records.value.filter(r=>typeGroup(r.earlier_project_type)===t);return rs.length?Math.round(rs.filter(r=>String(r.execution_windows_overlap)==='true'||r.execution_windows_overlap===true).length/rs.length*100):0}
const sameInst=computed(()=>records.value.length?Math.round(records.value.filter(r=>r.same_institution_name===true||String(r.same_institution_name)==='true').length/records.value.length*100):0)
const people=computed(()=>new Set(records.value.map(r=>r.person_id)).size)
// Sankey geometry
const LX=128,RX=372,TOP=20,K=1.6,GAP=14,NW=14
const sankey=computed(()=>{const posL={},posR={};let yl=TOP,yr=TOP
  for(const t of ORDER){const o=out(t),i=inn(t);if(o){posL[t]={y:yl,h:o*K};yl+=o*K+GAP}if(i){posR[t]={y:yr,h:i*K};yr+=i*K+GAP}}
  const ol={},or={};ORDER.forEach(t=>{ol[t]=0;or[t]=0})
  const sorted=[...flows.value].sort((p,q)=>ORDER.indexOf(p.a)-ORDER.indexOf(q.a)||ORDER.indexOf(p.b)-ORDER.indexOf(q.b))
  const links=sorted.map(f=>{const h=f.n*K,y0=posL[f.a].y+ol[f.a],y1=posR[f.b].y+or[f.b];ol[f.a]+=h;or[f.b]+=h;const mx=(LX+NW+RX)/2
    const key=(f.a==='青年'&&f.b==='面上')||(f.a==='面上'&&f.b==='重点等'),mm=f.a==='面上'&&f.b==='面上'
    return {...f,h,y0,y1,mx,key,mm,d:`M${LX+NW},${y0} C${mx},${y0} ${mx},${y1} ${RX},${y1} L${RX},${y1+h} C${mx},${y1+h} ${mx},${y0+h} ${LX+NW},${y0+h} Z`,
      fill:key||mm?TYPE_COLOR[f.a]:'#cfc8c1',op:key?.85:mm?.35:.25}})
  return {posL,posR,links,height:Math.max(yl,yr)+10}})
const link=(a,b)=>sankey.value.links.find(l=>l.a===a&&l.b===b)
// Representative cases joined to verified records (years, types, institution come from the data)
const cases=computed(()=>{const list=props.dataset?.strength?.cases||[];const groups=[]
  for(const c of list){const r=records.value.find(x=>x.person_name===c.person_name&&Number(x.earlier_approval_year)===c.earlier_year&&Number(x.later_approval_year)===c.later_year);if(!r)continue
    let g=groups.find(z=>z.name===c.group);if(!g){g={name:c.group,rows:[]};groups.push(g)}
    let row=g.rows.find(z=>z.person===c.person_name);if(!row){row={person:c.person_name,org:r.earlier_institution,steps:[],records:[]};g.rows.push(row)}
    if(!row.steps.length)row.steps.push({t:typeGroup(r.earlier_project_type),y:r.earlier_approval_year,topic:c.earlier_topic,title:r.earlier_project_title,grant:r.earlier_grant_no})
    row.steps.push({t:typeGroup(r.later_project_type),y:r.later_approval_year,topic:c.later_topic,title:r.later_project_title,grant:r.later_grant_no});row.records.push(r)}
  return groups})
function flowTip(e,l){const names=records.value.filter(r=>typeGroup(r.earlier_project_type)===l.a&&typeGroup(r.later_project_type)===l.b).slice(0,4).map(r=>r.person_name).join('、')
  show(e,`<b>${TYPE_NAME[l.a]} → ${TYPE_NAME[l.b]}</b><br>${l.n} 条接续（占该起点 ${pct(l.a,l.b)}%）<br><span style="color:#78716c">如：${names}</span>`)}
</script>
<template>
  <section class="rs-page" ref="root">
    <header class="rs-head"><span class="rs-no">04</span><h3>负责人接续</h3><span class="rs-sub">{{records.length}} 条经官方身份核验的前后项目接续（{{people}} 人）</span>
      <div class="rs-tools"><button class="rs-btn" @click="toggleFullscreen(root)">全屏 / 退出</button></div></header>
    <div v-if="!records.length" class="rs-empty">接续记录暂未读取。</div>
    <div v-else class="rs-succ">
      <div class="rs-succ-left">
        <h4>接到什么项目</h4>
        <p class="rs-lead">青年 → 面上是主通道；面上项目有三分之一转向联合、重大等</p>
        <svg class="rs-svg" :viewBox="`0 0 520 ${sankey.height}`" role="img" aria-label="前后项目类型流向">
          <g v-for="l in sankey.links" :key="l.a+l.b" class="rs-hit" @mouseenter="flowTip($event,l)" @mousemove="move" @mouseleave="hide"><path :d="l.d" :fill="l.fill" :opacity="l.op"/></g>
          <template v-for="t in ORDER" :key="t">
            <g v-if="sankey.posL[t]"><rect :x="LX" :y="sankey.posL[t].y" :width="NW" :height="sankey.posL[t].h" rx="3" :fill="TYPE_COLOR[t]"/>
              <text v-if="sankey.posL[t].h>10" :x="LX-16" :y="sankey.posL[t].y+sankey.posL[t].h/2+6" font-size="16" font-weight="500" text-anchor="end" fill="#2a2a2a">{{t==='重点等'?'联合等':TYPE_SHORT[t]=='青年'?'青年项目':TYPE_SHORT[t]=='地区'?'地区项目':'面上项目'}}</text></g>
            <g v-if="sankey.posR[t]"><rect :x="RX" :y="sankey.posR[t].y" :width="NW" :height="sankey.posR[t].h" rx="3" :fill="TYPE_COLOR[t]"/>
              <text v-if="sankey.posR[t].h>10" :x="RX+NW+16" :y="sankey.posR[t].y+sankey.posR[t].h/2+6" font-size="16" font-weight="500" fill="#2a2a2a">{{t==='重点等'?'联合·重大等':TYPE_SHORT[t]=='青年'?'青年项目':TYPE_SHORT[t]=='地区'?'地区项目':'面上项目'}}</text></g>
          </template>
          <g v-if="link('青年','面上')" pointer-events="none"><text :x="link('青年','面上').mx" :y="(link('青年','面上').y0+link('青年','面上').y1)/2+link('青年','面上').h/2+4" font-size="28" font-weight="700" text-anchor="middle" fill="#7a0a1c">{{pct('青年','面上')}}%</text>
            <text :x="link('青年','面上').mx" :y="(link('青年','面上').y0+link('青年','面上').y1)/2+link('青年','面上').h/2+26" font-size="14" text-anchor="middle" fill="#7a0a1c">{{flowN('青年','面上')}} / {{out('青年')}} 位青年项目负责人</text></g>
          <g v-if="link('面上','面上')" pointer-events="none"><text :x="link('面上','面上').mx" :y="(link('面上','面上').y0+link('面上','面上').y1)/2+link('面上','面上').h/2+6" font-size="15" font-weight="700" text-anchor="middle" fill="#7a0a1c">面上 → 面上 {{flowN('面上','面上')}}</text></g>
          <g v-if="link('面上','重点等')" pointer-events="none"><text :x="link('面上','重点等').mx" :y="(link('面上','重点等').y0+link('面上','重点等').y1)/2+link('面上','重点等').h/2" font-size="28" font-weight="700" text-anchor="middle" fill="#fff">{{pct('面上','重点等')}}%</text>
            <text :x="link('面上','重点等').mx" :y="(link('面上','重点等').y0+link('面上','重点等').y1)/2+link('面上','重点等').h/2+22" font-size="14" text-anchor="middle" fill="#fff">{{flowN('面上','重点等')}} / {{out('面上')}}</text></g>
        </svg>
      </div>
      <div class="rs-succ-right">
        <h4>代表案例</h4>
        <p class="rs-lead">同一位负责人，前后项目围绕同一研究问题深化或拓展</p>
        <div v-for="g in cases" :key="g.name" class="rs-case-group">
          <p class="rs-case-gname">{{g.name}}</p>
          <button v-for="row in g.rows" :key="row.person" class="rs-case" :class="{on:picked===row}" @click="picked=picked===row?null:row">
            <span class="who"><b :class="{hl:row.person==='李晓旭'}">{{row.person}}</b><small>{{row.org}}</small></span>
            <span class="steps" :class="{three:row.steps.length>2}">
              <template v-for="(s,i) in row.steps" :key="i"><i v-if="i" class="rib" :style="{background:TYPE_COLOR[row.steps[i-1].t]}"></i>
                <span class="pill"><em :style="{background:TYPE_COLOR[s.t],color:s.t==='青年'?'#7a0a1c':'#fff'}">{{TYPE_SHORT[s.t]}} {{s.y}}</em>{{s.topic}}</span></template>
            </span>
          </button>
        </div>
        <div v-if="picked" class="rs-case-detail">
          <p class="k">{{picked.person}} · {{picked.org}}</p>
          <ol><li v-for="(s,i) in picked.steps" :key="i"><b>{{s.y}} 批准 · {{TYPE_NAME[s.t]}}</b><span>{{s.title}}</span><small>批准号 {{s.grant}}</small></li></ol>
          <p class="k">依据：前后项目的 NSFC 官方负责人身份一致；研究主题据项目题名概括。</p>
          <button v-if="picked.person==='李晓旭'" class="rs-btn on" @click="emit('explore','李晓旭')">查看项目与论文证据 →</button>
        </div>
      </div>
    </div>
    <div class="rs-keys" v-if="records.length">
      <div><strong>{{pct('青年','面上')}}%</strong><span>青年项目接续到面上项目<small>{{flowN('青年','面上')}} / {{out('青年')}}</small></span></div>
      <div><strong>{{overlapPct('青年')}}%</strong><span>青年项目与下一项执行期重叠<small>面上项目为 {{overlapPct('面上')}}%</small></span></div>
      <div><strong>{{pct('面上','重点等')}}%</strong><span>面上项目接续到联合、重大等<small>{{flowN('面上','重点等')}} / {{out('面上')}}</small></span></div>
      <div><strong>{{sameInst}}%</strong><span>在同一机构内接续<small>同名依托单位</small></span></div>
    </div>
    <div class="rs-take"><p>青年项目负责人九成接到面上项目，面上项目三分之一转入联合、重点等项目；代表案例中，前后项目围绕同一研究问题深化或拓展，{{sameInst}}% 的接续发生在原机构，研究力量沿“人—机构”稳定延续。</p></div>
    <p class="rs-foot">接续依据为前后项目的官方负责人身份，不代表整体获批率或师承关系；“联合·重大等”含联合基金、重大研究计划、重点项目与数学天元基金。</p>
    <div v-if="tip.show" class="rs-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div>
  </section>
</template>
<style scoped>
.rs-succ{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:36px}
.rs-succ h4{font-size:22px;margin:0;font-weight:700}
.rs-lead{font-size:16px;color:var(--rs-red);font-weight:500;margin:6px 0 16px}
.rs-succ-right{border-left:1px solid var(--rs-line);padding-left:36px}
.rs-case-gname{font-size:14px;font-weight:700;color:var(--rs-muted);letter-spacing:1px;margin:14px 0 6px}
.rs-case{display:grid;grid-template-columns:110px minmax(0,1fr);align-items:center;gap:14px;width:100%;text-align:left;background:none;border:0;border-radius:12px;padding:8px 8px;cursor:pointer;font-family:inherit}
.rs-case:hover,.rs-case.on{background:#f7f5f2}
.who b{display:block;font-size:17px;color:var(--rs-ink)}.who b.hl{color:var(--rs-red)}
.who small{font-size:12.5px;color:var(--rs-muted)}
.steps{display:flex;flex-direction:column;align-items:flex-start;gap:0;min-width:0}
.pill{display:inline-flex;align-items:center;gap:9px;border:1px solid var(--rs-line);background:#fff;border-radius:20px;padding:4px 14px 4px 4px;font-size:15px;color:var(--rs-ink);white-space:nowrap;max-width:100%;overflow:hidden;text-overflow:ellipsis}
.pill em{font-style:normal;font-size:13px;font-weight:700;border-radius:14px;padding:4px 10px;flex:none}

.rib{display:block;width:3px;height:10px;margin-left:34px;opacity:.6}

.rs-case-detail{margin-top:12px;background:#f7f5f2;border-radius:12px;padding:16px 18px}
.rs-case-detail ol{margin:6px 0 8px;padding-left:20px}
.rs-case-detail li{margin:6px 0;font-size:14.5px}
.rs-case-detail li b{display:block}.rs-case-detail li span{display:block;color:var(--rs-ink-2)}.rs-case-detail li small{color:var(--rs-muted)}
.rs-case-detail .k{font-size:13px;color:var(--rs-muted);margin:0 0 4px}
.rs-keys{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:20px;border-top:1px solid var(--rs-line);margin-top:24px;padding-top:22px}
.rs-keys div{display:flex;align-items:center;gap:12px}
.rs-keys strong{font-size:40px;font-weight:750;color:var(--rs-red);line-height:1}
.rs-keys span{font-size:15px;font-weight:500;color:var(--rs-ink);line-height:1.4}
.rs-keys small{display:block;font-size:14px;color:var(--rs-muted);font-weight:400}
@media(max-width:1200px){.rs-succ{grid-template-columns:1fr}.rs-succ-right{border-left:0;padding-left:0}.rs-keys{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:700px){.rs-keys{grid-template-columns:1fr}.rs-keys strong{font-size:32px;min-width:84px}.rs-case{grid-template-columns:1fr}}
</style>
