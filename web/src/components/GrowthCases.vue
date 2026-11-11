<script setup>
/* 06 全部案例 · 参与人成长案例：按首次负责项目的依托单位分组，与“负责人进阶案例”同一展示方式 */
import {computed,ref,watch,nextTick} from 'vue'
import ProjectTimeline from './ProjectTimeline.vue'
import {useSurface} from '../helpers/useSurface'
import {useTip,fmt,typeGroup,TYPE_NAME,TYPE_COLOR,BASIS} from '../helpers/strengthTip.js'
import {useMemberGrowth} from '../helpers/memberGrowth.js'
const props=defineProps({dataset:Object})
const {data,error}=useMemberGrowth()
const {tip,show,move,hide}=useTip()
const cases=computed(()=>data.value?.cases||[])
// 研究团队数据中已有的项目执行期与关联论文，用于补充时间轴
const graph=computed(()=>props.dataset?.graph||{})
const nodes=computed(()=>new Map((graph.value.project_nodes||[]).map(p=>[p.project_id,p])))
const paperMap=computed(()=>new Map((graph.value.paper_nodes||[]).map(p=>[p.paper_id,p])))
const edges=computed(()=>{const m=new Map();for(const e of graph.value.project_paper_edges||[]){if(!m.has(e.project_id))m.set(e.project_id,[]);m.get(e.project_id).push(e)}return m})
const LEAD=['中国人民大学','清华大学','北京大学','中国科学院自动化研究所','浙江大学','上海交通大学','复旦大学','南京大学','中国科学技术大学','中国科学院计算技术研究所']
const institutions=computed(()=>{const c=new Map();for(const x of cases.value)c.set(x.later_inst,(c.get(x.later_inst)||0)+1);return LEAD.filter(n=>c.has(n)).map(name=>({name,count:c.get(name)}))})
const org=ref(LEAD[0]),query=ref(''),page=ref(0),selected=ref(null),drawer=ref(null),closeBtn=ref(null),drawerSurface=ref(null)
const PAGE=10
const people=computed(()=>{const q=query.value.trim()
 const list=q?cases.value.filter(c=>[c.person_name,c.later_inst,c.early_inst,c.early_title,c.later_title].some(v=>String(v||'').includes(q))):cases.value.filter(c=>c.later_inst===org.value)
 return [...list].sort((a,b)=>a.early_year-b.early_year||a.later_year-b.later_year||String(a.person_name).localeCompare(String(b.person_name),'zh-CN'))})
const pages=computed(()=>Math.max(1,Math.ceil(people.value.length/PAGE)))
const visible=computed(()=>people.value.slice(page.value*PAGE,(page.value+1)*PAGE))
watch([org,query],()=>{page.value=0;selected.value=null;drawer.value=null})
// 项目：参与项目与首次负责项目，可用时补执行期
const proj=(c,kind)=>{const id=kind==='early'?c.early_id:c.later_id,n=nodes.value.get(id)||{}
 return {project_id:id,grant_no:c[kind+'_grant'],title:c[kind+'_title'],approval_year:c[kind+'_year'],project_type:c[kind+'_type'],institution:c[kind+'_inst'],
  principal_investigator:kind==='early'?c.early_pi:c.person_name,start_date:n.start_date,end_date:n.end_date,amount:kind==='later'&&c.later_amount?`${c.later_amount}${c.later_unit||''}`:(n.amount_raw?`${n.amount_raw}${n.amount_unit||''}`:''),role:kind==='early'?'参与':'负责'}}
const yearsOf=s=>Number(String(s||'').slice(0,4))||null
// 图形
const YEARS=Array.from({length:11},(_,i)=>2016+i),YW=56,X=y=>300+(y-2016)*YW,ROW=50,R0=40,PERSON=100
const rows=computed(()=>visible.value.map((c,i)=>{const y=R0+i*PERSON,e=proj(c,'early'),l=proj(c,'later');return {c,y,mid:y+ROW/2,items:[{p:e,y:y+6},{p:l,y:y+ROW+2}]}}))
const H=computed(()=>R0+Math.max(1,rows.value.length)*PERSON+10)
const instY=computed(()=>rows.value.length?(rows.value[0].mid+rows.value.at(-1).mid)/2:R0)
const hl=computed(()=>drawer.value?.person_id||selected.value?.c?.person_id||'')
function bar(p){const s=yearsOf(p.start_date),e=yearsOf(p.end_date);return s&&e?{x:X(Math.max(2016,s)),w:Math.max(10,X(Math.min(2026,e)+1)-X(Math.max(2016,s)))}:null}
function dots(p,y){const byYear=new Map();for(const e of edges.value.get(p.project_id)||[]){const q=paperMap.value.get(e.paper_id);if(!q||!q.publication_year)continue;if(!byYear.has(q.publication_year))byYear.set(q.publication_year,[]);byYear.get(q.publication_year).push(q)}
 const out=[];for(const [yr,list] of byYear){list.slice(0,8).forEach((q,k)=>{const col=k%4,row=Math.floor(k/4);out.push({q,cx:X(yr)+10+col*10,cy:y+(list.length<=4?12:7+row*10)})})}return out}
function pick(c,p){selected.value={c,p};hide()}
function openDrawer(c){drawer.value=c;selected.value=null;nextTick(()=>closeBtn.value?.focus())}
useSurface(computed(()=>!!drawer.value),{element:drawerSurface,close:()=>drawer.value=null})
const drawerProjects=computed(()=>drawer.value?[proj(drawer.value,'early'),proj(drawer.value,'later')]:[])
const drawerPapers=computed(()=>drawerProjects.value.flatMap(p=>(edges.value.get(p.project_id)||[]).map(e=>({p,q:paperMap.value.get(e.paper_id),e}))).filter(x=>x.q).sort((a,b)=>a.q.publication_year-b.q.publication_year))
const stats=computed(()=>({people:people.value.length,same:people.value.filter(c=>c.early_inst===c.later_inst).length,gap:people.value.length?(people.value.reduce((t,c)=>t+c.gap,0)/people.value.length).toFixed(1):'—'}))
</script>
<template><div class="gc">
 <div v-if="error" class="rs-empty">{{error}}</div>
 <div v-else-if="!data" class="rs-empty">正在读取成长案例…</div>
 <template v-else>
  <div class="rs-ev-bar">
   <div class="rs-ev-orgs"><button v-for="o in institutions" :key="o.name" class="rs-chip" :class="{on:!query&&org===o.name}" @click="query='';org=o.name">{{o.name}} {{o.count}} 人</button></div>
   <input v-model="query" class="rs-ev-search" type="search" placeholder="搜索全部 1,007 人" aria-label="搜索成长案例">
  </div>
  <div class="rs-ev" :style="{minHeight:drawer?'720px':null}">
   <div class="rs-ev-graph">
    <div class="rs-ev-axis"><svg class="rs-svg" viewBox="0 0 940 40"><text x="40" y="26" font-size="15" fill="#78716c">机构</text><text x="150" y="26" font-size="15" fill="#78716c">成长人员</text>
     <text v-for="y in YEARS" :key="y" :x="X(y)+YW/2" y="26" font-size="15" fill="#78716c" text-anchor="middle">{{y}}</text></svg></div>
    <div class="rs-ev-rows">
     <svg class="rs-svg" :viewBox="`0 0 940 ${H}`" role="img" :aria-label="`${query?'搜索结果':org}的参与人成长时间线`">
      <line v-for="y in YEARS" :key="'g'+y" :x1="X(y)" :x2="X(y)" y1="20" :y2="H" stroke="#efebe6"/>
      <template v-if="!query&&rows.length"><path v-for="r in rows" :key="'t'+r.c.person_id" :d="`M80,${instY} C110,${instY} 110,${r.mid} 140,${r.mid}`" fill="none" :stroke="r.c.person_id===hl?'#ae0d28':'#d6d0c9'" :stroke-width="r.c.person_id===hl?2.5:1.2"/>
       <circle cx="60" :cy="instY" r="20" fill="#2a2a2a"/><text x="60" :y="instY+44" font-size="14" font-weight="700" text-anchor="middle" fill="#2a2a2a">{{org.length>6?org.slice(0,6)+'…':org}}</text></template>
      <g v-for="r in rows" :key="r.c.person_id">
       <g class="rs-hit" @click="openDrawer(r.c)"><rect x="140" :y="r.mid-18" width="100" height="46" fill="transparent"/>
        <circle cx="152" :cy="r.mid" r="7" :fill="r.c.person_id===hl?'#ae0d28':'#fff'" :stroke="r.c.person_id===hl?'#ae0d28':'#57534e'" stroke-width="2"/>
        <text x="166" :y="r.mid+6" font-size="17" font-weight="700" :fill="r.c.person_id===hl?'#ae0d28':'#2a2a2a'">{{r.c.person_name}}</text>
        <text x="166" :y="r.mid+26" font-size="12" fill="#78716c">{{query?r.c.later_inst.slice(0,8):'查看 →'}}</text></g>
       <g v-for="(it,k) in r.items" :key="k">
        <path :d="`M240,${r.mid} C265,${r.mid} 265,${it.y+12} ${X(it.p.approval_year)-4},${it.y+12}`" fill="none" :stroke="r.c.person_id===hl?'#ae0d28':'#d6d0c9'" :stroke-width="r.c.person_id===hl?2:1.1"/>
        <circle v-for="(d,j) in dots(it.p,it.y)" :key="'d'+j" class="rs-hit" :cx="d.cx" :cy="d.cy" r="4.6" :fill="r.c.person_id===hl?'#2f5f7a':'#9dbdd0'" @mouseenter="show($event,`<b>${d.q.title}</b><br>${d.q.publication_year}${d.q.venue?' · '+d.q.venue:''}`)" @mousemove="move" @mouseleave="hide"/>
        <rect v-if="bar(it.p)" :x="bar(it.p).x" :y="it.y+8" :width="bar(it.p).w" height="8" rx="4" :fill="k?'#f0b7bf':'#ece7e2'"/>
        <path class="rs-hit" :d="`M${X(it.p.approval_year)+8},${it.y+2} l10,10 l-10,10 l-10,-10 Z`" :fill="k?(r.c.person_id===hl?'#ae0d28':'#d9737f'):'#fff'" :stroke="k?'none':'#a8a29e'" stroke-width="1.6" stroke-dasharray="2 2"
         @mouseenter="show($event,`<b>${it.p.title}</b><br>${it.p.role} · ${it.p.grant_no} · ${TYPE_NAME[typeGroup(it.p.project_type)]} · ${it.p.approval_year} 批准${k?'':'<br>负责人 '+it.p.principal_investigator}`)" @mousemove="move" @mouseleave="hide" @click="pick(r.c,it.p)"/>
       </g>
       <path :d="`M${X(r.c.early_year)+8},${r.items[0].y+22} C${X(r.c.early_year)+8},${r.items[1].y+12} ${X(r.c.later_year)-40},${r.items[1].y+12} ${X(r.c.later_year)-2},${r.items[1].y+12}`" fill="none" stroke="#ae0d28" stroke-width="2" stroke-dasharray="5 4"/>
      </g>
     </svg>
    </div>
    <div class="rs-ev-legend"><span><i class="dm hollow"></i>参与的项目</span><span><i class="dm"></i>首次负责的项目</span><span><i class="bar"></i>执行期</span><span><i class="pd"></i>关联论文（按发表年）</span><span><i class="dash"></i>参与 → 负责</span></div>
    <div v-if="pages>1" class="people-pages"><button class="rs-chip" :disabled="page===0" @click="page--">上一组</button><span>{{page*PAGE+1}}—{{Math.min((page+1)*PAGE,people.length)}} / {{fmt(people.length)}} 位成长人员</span><button class="rs-chip" :disabled="page>=pages-1" @click="page++">下一组</button></div>
   </div>
   <aside class="rs-ev-panel">
    <template v-if="!selected">
     <span class="tag">{{query?'搜索结果':org}}</span>
     <p class="rs-ev-stat"><b>{{fmt(stats.people)}}</b> 人参与后担任负责人</p>
     <p class="k">{{fmt(stats.same)}} 人在同一单位成长 · 平均间隔 {{stats.gap}} 年</p>
     <p class="k">点击人员姓名查看成长路径与项目介绍，点击菱形查看单个项目。</p>
    </template>
    <template v-else>
     <span class="tag">{{selected.p.role}}的项目</span><h4>{{selected.p.title}}</h4>
     <dl><dt>批准号</dt><dd>{{selected.p.grant_no}}</dd><dt>类型</dt><dd>{{selected.p.project_type}}</dd><dt>批准年</dt><dd>{{selected.p.approval_year}}</dd><dt>负责人</dt><dd>{{selected.p.principal_investigator}}</dd><dt>单位</dt><dd>{{selected.p.institution}}</dd><dt v-if="selected.p.amount">经费</dt><dd v-if="selected.p.amount">{{selected.p.amount}}</dd></dl>
     <button class="rs-btn on" @click="openDrawer(selected.c)">查看 {{selected.c.person_name}} 的成长路径 →</button>
    </template>
   </aside>
   <div v-if="drawer" ref="drawerSurface" class="rs-drawer" role="dialog" :aria-label="`${drawer.person_name}的成长路径`">
    <button ref="closeBtn" class="rs-close" aria-label="关闭" @click="drawer=null">×</button>
    <header><b>{{drawer.person_name}}</b><span>{{drawer.later_inst}}{{drawer.early_inst===drawer.later_inst?' · 同一单位成长':` · 原参与单位 ${drawer.early_inst}`}}</span></header>
    <div class="chips"><span class="ghost">{{drawer.early_year}} 参与 {{TYPE_NAME[drawer.early_group]}}</span><i>→</i><span :class="drawer.later_group==='青年'?'soft':''">{{drawer.later_year}} 负责 {{TYPE_NAME[drawer.later_group]}}</span><em>间隔 {{drawer.gap}} 年</em></div>
    <ProjectTimeline :projects="drawerProjects" :papers="drawerPapers.map(x=>x.q)"/>
    <div class="plist"><article v-for="p in drawerProjects" :key="p.project_id"><b>{{p.approval_year}} · {{p.role}} · {{p.project_type}}</b><span>{{p.title}}</span><small>批准号 {{p.grant_no}} · 负责人 {{p.principal_investigator}} · {{p.institution}}{{p.amount?' · '+p.amount:''}}{{yearsOf(p.start_date)?` · 执行 ${yearsOf(p.start_date)}—${yearsOf(p.end_date)}`:''}}</small></article></div>
    <template v-if="drawerPapers.length"><h5 class="ph">关联论文（{{drawerPapers.length}}）</h5>
     <ul class="papers"><li v-for="x in drawerPapers" :key="x.p.grant_no+x.q.paper_id"><b>{{x.q.publication_year}}</b><span>{{x.q.title}}<small>{{x.q.venue}} · {{x.p.role}}的项目 · {{(x.e.bases||[]).map(b=>BASIS[b]||b).join('；')}}</small></span></li></ul></template>
   </div>
  </div>
 </template>
 <div v-if="tip.show" class="rs-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div>
</div></template>
<style scoped>
.people-pages{display:flex;justify-content:center;align-items:center;gap:14px;margin:10px 0;font-size:13px;color:var(--rs-muted)}.people-pages button:disabled{opacity:.4;cursor:default}
.rs-ev-bar{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:14px}
.rs-ev-orgs{display:flex;gap:10px;flex-wrap:wrap}
.rs-ev{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:20px;position:relative}
.rs-ev-graph{border:1px solid var(--rs-line);border-radius:12px;background:#fbfaf8;padding:6px 10px 10px;min-width:0}
.rs-ev-rows{max-height:600px;overflow-y:auto}
.rs-ev-legend{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13px;color:var(--rs-ink-2);padding:8px 6px 0}
.rs-ev-legend span{display:inline-flex;align-items:center;gap:6px}
.rs-ev-legend .dm{width:10px;height:10px;background:#d9737f;transform:rotate(45deg)}.rs-ev-legend .dm.hollow{background:#fff;border:1.5px dashed #a8a29e}
.rs-ev-legend .bar{width:24px;height:7px;border-radius:4px;background:#ece7e2}
.rs-ev-legend .pd{width:9px;height:9px;border-radius:50%;background:#2f5f7a}
.rs-ev-legend .dash{width:26px;border-top:2px dashed #ae0d28}
.rs-ev-panel{border:1px solid var(--rs-line);border-radius:12px;padding:20px 22px;background:#fff;align-self:start}
.rs-ev-panel h4{font-size:19px;margin:6px 0 8px;line-height:1.45}
.rs-ev-panel .k{font-size:13.5px;color:var(--rs-muted);line-height:1.7;margin:6px 0}
.rs-ev-stat{font-size:16px;margin:18px 0 4px}.rs-ev-stat b{font-size:24px;color:var(--rs-red)}
.rs-ev-panel dl{display:grid;grid-template-columns:62px 1fr;gap:6px 10px;font-size:14px;margin:10px 0}
.rs-ev-panel dt{color:var(--rs-muted)}.rs-ev-panel dd{margin:0}
.tag{display:inline-block;font-size:12.5px;font-weight:700;color:var(--rs-red);background:var(--rs-red-wash);border-radius:12px;padding:2px 10px}
.rs-drawer{position:absolute;left:250px;right:0;top:0;bottom:0;min-height:600px;overflow-y:auto;background:#fff;border:1px solid var(--rs-line);border-radius:14px;box-shadow:0 14px 40px rgba(40,20,20,.16);padding:26px 30px;z-index:6}
.rs-drawer header b{font-size:28px}.rs-drawer header span{font-size:16px;color:var(--rs-ink-2);margin-left:14px}
.rs-drawer .chips{display:flex;align-items:center;flex-wrap:wrap;gap:10px;margin:14px 0}
.rs-drawer .chips span{background:var(--rs-red);color:#fff;border-radius:16px;padding:5px 14px;font-size:14px}.rs-drawer .chips span.soft{background:var(--rs-red-soft);color:var(--rs-red-deep)}
.rs-drawer .chips span.ghost{background:#fff;color:var(--rs-ink-2);border:1px dashed #bfb6ae}
.rs-drawer .chips i{font-style:normal;color:var(--rs-red);font-size:18px}.rs-drawer .chips em{font-style:normal;font-size:13px;color:var(--rs-muted)}
.rs-drawer .plist{display:grid;gap:10px;margin:8px 0}
.rs-drawer .plist article{background:#faf8f6;border:1px solid var(--rs-line);border-radius:12px;padding:14px 16px}
.rs-drawer .plist article b{display:block;font-size:14px;color:var(--rs-red)}.rs-drawer .plist article span{display:block;font-size:15.5px;margin:3px 0}.rs-drawer .plist article small{color:var(--rs-muted)}
.rs-drawer .ph{font-size:16px;margin:16px 0 6px}
.rs-drawer .papers{list-style:none;padding:0;margin:0;font-size:14px}
.rs-drawer .papers li{display:grid;grid-template-columns:52px 1fr;gap:10px;padding:8px 0;border-bottom:1px solid var(--rs-grid)}
.rs-drawer .papers li b{color:var(--rs-blue)}.rs-drawer .papers li small{display:block;color:var(--rs-muted)}
.rs-close{position:absolute;right:16px;top:14px;width:34px;height:34px;border-radius:50%;border:0;background:#f5f3f0;font-size:20px;cursor:pointer;color:var(--rs-ink-2)}
@media(max-width:1200px){.rs-ev{grid-template-columns:1fr}.rs-drawer{left:0}}
@media(max-width:700px){.rs-ev-search{width:100%}.rs-ev-graph{overflow-x:auto}.rs-ev-graph .rs-svg{min-width:720px}}
</style>
