<script setup>
import {computed,ref,watch,nextTick} from 'vue'
import {useTip,fmt,toggleFullscreen,typeGroup,TYPE_NAME,BASIS} from '../helpers/strengthTip.js'
const props=defineProps({dataset:Object,person:{type:String,default:''}})
const {tip,show,move,hide}=useTip()
const root=ref(null),closeBtn=ref(null)
const graph=computed(()=>props.dataset?.graph||{})
const records=computed(()=>Array.isArray(props.dataset?.continuity)?props.dataset.continuity:[])
const detail=computed(()=>props.dataset?.caseDetail||{})
const projects=computed(()=>graph.value.project_nodes||[])
const papers=computed(()=>new Map((graph.value.paper_nodes||[]).map(p=>[p.paper_id,p])))
const edgesByProject=computed(()=>{const m=new Map();for(const e of graph.value.project_paper_edges||[]){if(!m.has(e.project_id))m.set(e.project_id,[]);m.get(e.project_id).push(e)}return m})
const pid=p=>p.project_id||`NSFC:${p.grant_no}`
const PREF=['清华大学','北京邮电大学','南京工业大学','兰州理工大学']
const institutions=computed(()=>[...new Set(projects.value.map(p=>p.institution).filter(Boolean))].sort((a,b)=>PREF.indexOf(a)-PREF.indexOf(b)).map(n=>({name:n,count:projects.value.filter(p=>p.institution===n).length})))
const org=ref('兰州理工大学'),query=ref(''),selected=ref(null),drawer=ref('')
watch(()=>props.person,v=>{if(v){const p=projects.value.find(x=>x.principal_investigator===v);if(p){org.value=p.institution;drawer.value=v}}},{immediate:true})
// person identity: only through verified continuity person_id, never by name alone
const verified=computed(()=>{const m=new Map();for(const r of records.value){m.set(r.earlier_project_id,r.person_id);m.set(r.later_project_id,r.person_id)}return m})
const pairs=computed(()=>records.value.map(r=>[r.earlier_project_id,r.later_project_id,r]))
const people=computed(()=>{const g=new Map();for(const p of projects.value.filter(x=>x.institution===org.value)){const v=verified.value.get(pid(p));const id=v||pid(p)
    if(!g.has(id))g.set(id,{id,name:p.principal_investigator||'负责人待补充',verified:!!v,projects:[]});g.get(id).projects.push(p)}
  const q=query.value.trim()
  return [...g.values()].map(x=>({...x,projects:x.projects.sort((a,b)=>a.approval_year-b.approval_year)}))
    .filter(x=>!q||x.name.includes(q)).sort((a,b)=>(b.verified-a.verified)||(b.projects.length-a.projects.length)||a.name.localeCompare(b.name,'zh-CN'))})
const X=y=>360+(y-2017)*62,ROW=56,R0=70
const layout=computed(()=>{const out=[],mids=new Map();let i=0;for(const person of people.value){const start=i;for(const p of person.projects){out.push({p,person,y:R0+i*ROW});i++}mids.set(person.id,R0+((start+i-1)/2)*ROW)}return {rows:out,mids}})
const rows=computed(()=>layout.value.rows)
const mid=p=>layout.value.mids.get(p.id)??R0
const H=computed(()=>R0+Math.max(rows.value.length,1)*ROW+10)
const instY=computed(()=>people.value.length?(mid(people.value[0])+mid(people.value.at(-1)))/2:R0)
const showTree=computed(()=>people.value.length<=16)
const dots=r=>{const byYear=new Map();for(const e of edgesByProject.value.get(pid(r.p))||[]){const q=papers.value.get(e.paper_id);if(!q)continue;if(!byYear.has(q.publication_year))byYear.set(q.publication_year,[]);byYear.get(q.publication_year).push({q,e})}
  const out=[];for(const [yr,list] of byYear){list.forEach((it,k)=>{const per=4,col=k%per,row=Math.floor(k/per);out.push({...it,cx:X(yr)+(Number(yr)===Number(r.p.approval_year)?28:12)+col*10,cy:r.y-14+row*10+(list.length<=per?14:0)})})}return out}
const arcs=computed(()=>{const pos=new Map(rows.value.map(r=>[pid(r.p),r]));return pairs.value.filter(([a,b])=>pos.has(a)&&pos.has(b)).map(([a,b,rec])=>{const A=pos.get(a),B=pos.get(b);return {d:`M${X(A.p.approval_year)+8},${A.y+10} C${X(A.p.approval_year)+8},${B.y} ${X(B.p.approval_year)-60},${B.y} ${X(B.p.approval_year)-2},${B.y}`,rec,lx:(X(A.p.approval_year)+X(B.p.approval_year))/2,ly:B.y-8}})})
const hlPerson=computed(()=>drawer.value||(selected.value?.person)||'')
const stats=computed(()=>{const ps=projects.value.filter(p=>p.institution===org.value);const es=ps.flatMap(p=>edgesByProject.value.get(pid(p))||[]);return {projects:ps.length,papers:new Set(es.map(e=>e.paper_id)).size,edges:es.length}})
function pick(kind,obj,person){selected.value={kind,...obj,person};hide()}
function changeOrg(n){org.value=n;query.value='';selected.value=null;drawer.value=''}
function openDrawer(name){drawer.value=name;selected.value=null;nextTick(()=>closeBtn.value?.focus())}
const drawerPerson=computed(()=>people.value.find(p=>p.name===drawer.value)||null)
const drawerCase=computed(()=>{if(!drawerPerson.value)return null;const grants=new Set(drawerPerson.value.projects.map(p=>String(p.grant_no)));const dp=(detail.value.projects||[]).filter(p=>grants.has(String(p.grant_no)));return dp.length?{projects:dp,papers:(detail.value.papers||[]).filter(p=>dp.some(x=>p.project_id===`NSFC:${x.grant_no}`)),summary:detail.value.project_continuity?.display_summary||''}:null})
const drawerPapers=computed(()=>{if(!drawerPerson.value)return [];return drawerPerson.value.projects.flatMap(p=>(edgesByProject.value.get(pid(p))||[]).map(e=>({p,q:papers.value.get(e.paper_id),e}))).filter(x=>x.q).sort((a,b)=>a.q.publication_year-b.q.publication_year)})
const DX=t=>40+(t-2019)*118
const yearsOf=s=>Number(String(s||'').slice(0,4))
const venueOf=paperId=>papers.value.get(paperId)?.venue||''
</script>
<template>
  <section class="rs-page" ref="root" @keydown.esc="drawer=''">
    <header class="rs-head"><span class="rs-no">05</span><h3>接续证据</h3><span class="rs-sub">机构 → 负责人 → 项目 → 论文，每条关系可查来源</span>
      <div class="rs-tools"><button class="rs-btn" @click="toggleFullscreen(root)">全屏 / 退出</button></div></header>
    <div v-if="!projects.length" class="rs-empty">机构项目与论文关系暂未读取。</div>
    <template v-else>
    <div class="rs-ev-bar">
      <div class="rs-ev-orgs"><button v-for="o in institutions" :key="o.name" class="rs-chip" :class="{on:org===o.name}" @click="changeOrg(o.name)">{{o.name}} {{o.count}} 项</button></div>
      <input v-model="query" class="rs-ev-search" type="search" placeholder="搜索负责人" aria-label="搜索负责人">
    </div>
    <div class="rs-ev" :style="{minHeight:drawerPerson?(drawerCase?'860px':'720px'):null}">
      <div class="rs-ev-graph">
        <div class="rs-ev-axis"><svg class="rs-svg" viewBox="0 0 940 40"><text x="40" y="26" font-size="15" fill="#78716c">机构</text><text x="168" y="26" font-size="15" fill="#78716c">负责人</text>
          <text v-for="y in 9" :key="y" :x="X(2016+y)+31" y="26" font-size="15" fill="#78716c" text-anchor="middle">{{2016+y}}</text></svg></div>
        <div class="rs-ev-rows">
        <svg class="rs-svg" :viewBox="`0 0 940 ${H}`" role="img" :aria-label="`${org}的项目与论文时间线`">
          <line v-for="y in 10" :key="'g'+y" :x1="X(2016+y)" :x2="X(2016+y)" y1="40" :y2="H" stroke="#efebe6"/>
          <template v-if="showTree"><path v-for="p in people" :key="'t'+p.id" :d="`M80,${instY} C120,${instY} 120,${mid(p)} 156,${mid(p)}`" fill="none" :stroke="p.name===hlPerson?'#ae0d28':'#d6d0c9'" :stroke-width="p.name===hlPerson?2.5:1.2"/>
            <circle cx="60" :cy="instY" r="20" fill="#2a2a2a"/><text x="60" :y="instY+44" font-size="14" font-weight="700" text-anchor="middle" fill="#2a2a2a">{{org.length>6?org.slice(0,6)+'…':org}}</text></template>
          <g v-for="r in rows" :key="pid(r.p)">
            <path :d="`M250,${mid(r.person)} C290,${mid(r.person)} 290,${r.y} ${X(r.p.approval_year)-2},${r.y}`" fill="none" :stroke="r.person.name===hlPerson?'#ae0d28':'#d6d0c9'" :stroke-width="r.person.name===hlPerson?2.2:1.1"/>
            <rect :x="X(yearsOf(r.p.start_date)||r.p.approval_year+1)" :y="r.y-4" :width="Math.max(10,X((yearsOf(r.p.end_date)||r.p.approval_year+3)+1)-X(yearsOf(r.p.start_date)||r.p.approval_year+1))" height="8" rx="4" :fill="r.person.name===hlPerson?'#f0b7bf':'#ece7e2'"/>
            <path class="rs-hit" :d="`M${X(r.p.approval_year)+8},${r.y-10} l10,10 l-10,10 l-10,-10 Z`" :fill="r.person.name===hlPerson?'#ae0d28':'#d9737f'" @mouseenter="show($event,`<b>${r.p.title}</b><br>${r.p.grant_no} · ${TYPE_NAME[typeGroup(r.p.project_type)]} · ${r.p.approval_year} 批准`)" @mousemove="move" @mouseleave="hide" @click="pick('project',r.p,r.person.name)"/>
            <circle v-for="(d,k) in dots(r)" :key="k" class="rs-hit" :cx="d.cx" :cy="d.cy" r="4.6" :fill="r.person.name===hlPerson?'#2f5f7a':'#9dbdd0'" @mouseenter="show($event,`<b>${d.q.title}</b><br>${d.q.publication_year}${d.q.venue?' · '+d.q.venue:''}`)" @mousemove="move" @mouseleave="hide" @click="pick('paper',{...d.q,bases:d.e.bases,project:r.p},r.person.name)"/>
          </g>
          <g v-for="(a,i) in arcs" :key="'a'+i"><path :d="a.d" fill="none" stroke="#ae0d28" stroke-width="2" stroke-dasharray="5 4"/><text :x="a.lx" :y="a.ly" font-size="12.5" font-weight="700" fill="#ae0d28" text-anchor="middle">负责人接续</text></g>
          <g v-for="p in people" :key="'n'+p.id" class="rs-hit" @click="openDrawer(p.name)" @mouseenter="show($event,`<b>${p.name}</b> · ${p.projects.length} 个项目<br>${p.verified?'官方负责人身份核验':'按项目负责人字段列示'}<br>点击查看项目与论文`)" @mousemove="move" @mouseleave="hide">
            <rect x="150" :y="mid(p)-16" width="100" height="32" fill="transparent"/>
            <circle cx="162" :cy="mid(p)" r="7" :fill="p.name===hlPerson?'#ae0d28':(p.verified?'#2a2a2a':'#fff')" :stroke="p.name===hlPerson?'#ae0d28':'#57534e'" stroke-width="2"/>
            <text x="176" :y="mid(p)+6" font-size="17" :font-weight="p.name===hlPerson||p.verified?700:400" :fill="p.name===hlPerson?'#ae0d28':'#2a2a2a'">{{p.name}}</text></g>
        </svg></div>
        <div class="rs-ev-legend"><span><i class="dm"></i>项目批准</span><span><i class="bar"></i>执行期</span><span><i class="pd"></i>关联论文（按发表年）</span><span><i class="dash"></i>同一负责人接续</span><span><i class="pv"></i>官方身份核验的负责人</span></div>
      </div>
      <aside class="rs-ev-panel">
        <template v-if="!selected">
          <h4>关系证据</h4><p class="k">点击负责人、项目或论文查看依据</p>
          <div class="rs-ev-stat"><b>{{stats.projects}}</b> 个项目 · <b>{{fmt(stats.papers)}}</b> 篇论文</div>
          <p class="k">{{fmt(stats.edges)}} 条项目—论文关系（2017—2025 年有发表年份的论文）</p>
          <p class="k">负责人与项目：NSFC 项目负责人字段；跨项目的同一人仅依据官方身份核验的接续记录。</p>
        </template>
        <template v-else-if="selected.kind==='project'">
          <span class="tag">项目</span><h4>{{selected.title}}</h4>
          <dl><dt>批准号</dt><dd>{{selected.grant_no}}</dd><dt>类型</dt><dd>{{selected.project_type}}</dd><dt>批准年</dt><dd>{{selected.approval_year}}</dd><dt>执行期</dt><dd>{{String(selected.start_date).slice(0,10)}} 至 {{String(selected.end_date).slice(0,10)}}</dd><dt>负责人</dt><dd>{{selected.principal_investigator}}</dd><dt v-if="selected.amount_raw">经费</dt><dd v-if="selected.amount_raw">{{selected.amount_raw}} {{selected.amount_unit}}</dd></dl>
          <p class="k">依据：NSFC 项目记录{{verified.get(pid(selected))?'；负责人身份经官方来源 ID 核验':''}}</p>
          <button class="rs-btn on" @click="openDrawer(selected.person)">查看 {{selected.person}} 的项目与论文 →</button>
        </template>
        <template v-else>
          <span class="tag blue">论文</span><h4>{{selected.title}}</h4>
          <dl><dt>发表年</dt><dd>{{selected.publication_year}}</dd><dt v-if="selected.venue">刊会</dt><dd v-if="selected.venue">{{selected.venue}}</dd><dt>关联项目</dt><dd>{{selected.project.grant_no}} · {{selected.project.principal_investigator}}</dd></dl>
          <p class="k">依据：{{(selected.bases||[]).map(b=>BASIS[b]||b).join('；')}}</p>
          <a v-if="selected.doi_url||selected.doi" :href="selected.doi_url||`https://doi.org/${selected.doi}`" target="_blank" rel="noopener">DOI ↗</a>
        </template>
      </aside>
      <div v-if="drawerPerson" class="rs-drawer" role="dialog" :aria-label="`${drawerPerson.name}的接续详情`">
        <button ref="closeBtn" class="rs-close" aria-label="关闭" @click="drawer=''">×</button>
        <header><b>{{drawerPerson.name}}</b><span>{{org}}<template v-if="drawerCase&&detail.case"> · {{String(detail.case).split('：').at(-1).replace(/研究$/,'')}}</template></span></header>
        <div class="chips"><template v-for="(p,i) in drawerPerson.projects" :key="pid(p)"><i v-if="i">→</i><span :class="typeGroup(p.project_type)==='青年'?'soft':''">{{TYPE_NAME[typeGroup(p.project_type)]}} {{p.grant_no}} · {{p.approval_year}} 批准</span></template></div>
        <template v-if="drawerCase">
          <p v-if="drawerCase.summary" class="sum">{{drawerCase.summary}}</p>
          <svg class="rs-svg" viewBox="0 0 960 150">
            <g v-for="(p,i) in drawerCase.projects" :key="p.grant_no"><rect :x="DX(yearsOf(p.start_date)||2020)" :y="20+i*28" :width="DX((yearsOf(p.end_date)||2022)+1)-DX(yearsOf(p.start_date)||2020)" height="16" rx="8" :fill="i?'#ae0d28':'#f0b7bf'"/>
              <text :x="DX(yearsOf(p.start_date)||2020)+14" :y="33+i*28" font-size="13" :fill="i?'#fff':'#7a0a1c'">{{typeGroup(p.project_type)==='青年'?'青年项目':'面上项目'}}执行期 {{yearsOf(p.start_date)}}—{{yearsOf(p.end_date)}}</text></g>
            <rect :x="DX(2019)" y="86" :width="DX(2026)-DX(2019)" height="8" rx="4" fill="#57534e"/>
            <text v-for="y in 7" :key="y" :x="DX(2018+y)+59" y="122" font-size="13" fill="#78716c" text-anchor="middle">{{2018+y}}</text>
            <circle v-for="pp in drawerCase.papers" :key="pp.paper_id" :cx="DX(pp.publication_year)+59" cy="90" r="9" fill="#2f5f7a" stroke="#fff" stroke-width="3"/>
          </svg>
          <div class="goals"><div v-for="p in drawerCase.projects" :key="p.grant_no"><b>{{typeGroup(p.project_type)==='青年'?'青年项目':'面上项目'}}目标（据项目摘要）</b><ul><li v-for="(m,i) in (p.planned_methods||[]).slice(0,4)" :key="i">{{m}}</li></ul></div></div>
          <div class="cards"><article v-for="pp in drawerCase.papers" :key="pp.paper_id"><p class="y">{{pp.publication_year}} <small>{{venueOf(pp.paper_id)}}</small></p><h5>{{pp.short_title}}</h5><p>{{pp.summary_sentence}}</p><span>{{pp.research_branch}}</span><a v-if="pp.primary_url" :href="pp.primary_url" target="_blank" rel="noopener">原文依据 ↗</a></article></div>
          <p class="k">两期项目共登记关联论文 {{drawerPapers.length}} 篇；卡片为经原文核验的代表成果。论文之间不表示逐篇技术继承。</p>
        </template>
        <template v-else>
          <div class="plist"><article v-for="p in drawerPerson.projects" :key="pid(p)"><b>{{p.approval_year}} · {{TYPE_NAME[typeGroup(p.project_type)]}}</b><span>{{p.title}}</span><small>{{p.grant_no}} · 执行 {{String(p.start_date).slice(0,4)}}—{{String(p.end_date).slice(0,4)}}</small></article></div>
          <h5 class="ph">论文明细（{{drawerPapers.length}}）</h5>
          <ul class="papers"><li v-for="x in drawerPapers" :key="x.p.grant_no+x.q.paper_id"><b>{{x.q.publication_year}}</b><span>{{x.q.title}}<small>{{x.q.venue}} · {{(x.e.bases||[]).map(b=>BASIS[b]||b).join('；')}}</small></span></li><li v-if="!drawerPapers.length" class="none">2017—2025 年暂无有发表年份的关联论文</li></ul>
        </template>
      </div>
    </div>
    </template>
    <div v-if="tip.show" class="rs-tip" :style="{left:tip.x+'px',top:tip.y+'px'}" v-html="tip.html"></div>
  </section>
</template>
<style scoped>
.rs-ev-bar{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:14px}
.rs-ev-orgs{display:flex;gap:10px;flex-wrap:wrap}
.rs-chip{border:1px solid var(--rs-line);background:#fff;border-radius:18px;padding:6px 16px;font-size:14px;color:var(--rs-ink-2);cursor:pointer;font-family:inherit}
.rs-chip.on{background:var(--rs-ink);color:#fff;border-color:var(--rs-ink)}
.rs-ev-search{border:1px solid var(--rs-line);border-radius:18px;padding:7px 14px;font-size:14px;width:200px;font-family:inherit}
.rs-ev{display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:20px;position:relative}
.rs-ev-graph{border:1px solid var(--rs-line);border-radius:12px;background:#fbfaf8;padding:6px 10px 10px;min-width:0}
.rs-ev-rows{max-height:600px;overflow-y:auto}
.rs-ev-legend{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13px;color:var(--rs-ink-2);padding:8px 6px 0}
.rs-ev-legend span{display:inline-flex;align-items:center;gap:6px}
.rs-ev-legend .dm{width:10px;height:10px;background:#d9737f;transform:rotate(45deg)}
.rs-ev-legend .bar{width:24px;height:7px;border-radius:4px;background:#ece7e2}
.rs-ev-legend .pd{width:9px;height:9px;border-radius:50%;background:#2f5f7a}
.rs-ev-legend .dash{width:26px;border-top:2px dashed #ae0d28}
.rs-ev-legend .pv{width:10px;height:10px;border-radius:50%;background:#2a2a2a}
.rs-ev-panel{border:1px solid var(--rs-line);border-radius:12px;padding:20px 22px;background:#fff;align-self:start}
.rs-ev-panel h4{font-size:19px;margin:6px 0 8px;line-height:1.45}
.rs-ev-panel .k{font-size:13.5px;color:var(--rs-muted);line-height:1.7;margin:6px 0}
.rs-ev-stat{font-size:16px;margin:18px 0 4px}.rs-ev-stat b{font-size:24px;color:var(--rs-red)}
.rs-ev-panel dl{display:grid;grid-template-columns:62px 1fr;gap:6px 10px;font-size:14px;margin:10px 0}
.rs-ev-panel dt{color:var(--rs-muted)}.rs-ev-panel dd{margin:0}
.rs-ev-panel a{color:var(--rs-red);font-weight:600;text-decoration:none}
.tag{display:inline-block;font-size:12.5px;font-weight:700;color:var(--rs-red);background:var(--rs-red-wash);border-radius:12px;padding:2px 10px}.tag.blue{color:var(--rs-blue);background:#eaf1f5}
.rs-drawer{position:absolute;left:250px;right:0;top:0;bottom:0;min-height:600px;overflow-y:auto;background:#fff;border:1px solid var(--rs-line);border-radius:14px;box-shadow:0 14px 40px rgba(40,20,20,.16);padding:26px 30px;z-index:6}
.rs-drawer header b{font-size:28px}.rs-drawer header span{font-size:16px;color:var(--rs-ink-2);margin-left:14px}
.rs-drawer .chips{display:flex;align-items:center;flex-wrap:wrap;gap:10px;margin:14px 0}
.rs-drawer .chips span{background:var(--rs-red);color:#fff;border-radius:16px;padding:5px 14px;font-size:14px}.rs-drawer .chips span.soft{background:var(--rs-red-soft);color:var(--rs-red-deep)}
.rs-drawer .chips i{font-style:normal;color:var(--rs-red);font-size:18px}
.rs-drawer .sum{font-size:15px;color:var(--rs-ink-2);line-height:1.7;margin:4px 0 6px}
.rs-drawer .goals{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin:6px 0 14px}
.rs-drawer .goals b{font-size:14px;color:var(--rs-red)}
.rs-drawer .goals ul{margin:6px 0 0;padding-left:18px;font-size:14px;line-height:1.7;color:var(--rs-ink-2)}
.rs-drawer .cards{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}
.rs-drawer article{background:#faf8f6;border:1px solid var(--rs-line);border-radius:12px;padding:14px 16px}
.rs-drawer article .y{font-size:20px;font-weight:700;color:var(--rs-blue);margin:0}.rs-drawer article .y small{display:block;font-size:12px;color:var(--rs-muted);font-weight:400;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rs-drawer article h5{font-size:16.5px;margin:8px 0 6px}
.rs-drawer article p{font-size:13.5px;color:var(--rs-ink-2);line-height:1.6;margin:0 0 8px}
.rs-drawer article span{display:inline-block;font-size:12px;color:var(--rs-blue);border:1px solid var(--rs-blue-3);border-radius:10px;padding:1px 8px;margin-bottom:6px}
.rs-drawer article a{display:block;font-size:13px;color:var(--rs-red);text-decoration:none}
.rs-drawer .k{font-size:13px;color:var(--rs-muted);margin-top:12px}
.rs-drawer .plist{display:grid;gap:10px;margin:8px 0}
.rs-drawer .plist article b{display:block;font-size:14px;color:var(--rs-red)}.rs-drawer .plist article span{display:block;font-size:15px}.rs-drawer .plist article small{color:var(--rs-muted)}
.rs-drawer .ph{font-size:16px;margin:16px 0 6px}
.rs-drawer .papers{list-style:none;padding:0;margin:0;font-size:14px}
.rs-drawer .papers li{display:grid;grid-template-columns:52px 1fr;gap:10px;padding:8px 0;border-bottom:1px solid var(--rs-grid)}
.rs-drawer .papers li b{color:var(--rs-blue)}.rs-drawer .papers li small{display:block;color:var(--rs-muted)}
.rs-drawer .papers li.none{display:block;color:var(--rs-muted)}
.rs-close{position:absolute;right:16px;top:14px;width:34px;height:34px;border-radius:50%;border:0;background:#f5f3f0;font-size:20px;cursor:pointer;color:var(--rs-ink-2)}
@media(max-width:1200px){.rs-ev{grid-template-columns:1fr}.rs-drawer{left:0}.rs-drawer .cards{grid-template-columns:1fr 1fr}}
@media(max-width:700px){.rs-drawer .cards,.rs-drawer .goals{grid-template-columns:1fr}.rs-ev-search{width:100%}}
</style>
