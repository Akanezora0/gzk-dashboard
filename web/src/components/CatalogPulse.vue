<script setup>
import {computed,ref,watch,nextTick,onMounted,onBeforeUnmount} from 'vue'
import {fmt,escape} from '../shared'
import Chart from './Chart.vue'
import {activityDate,activitySeries,activityTitle,parseActivityLedger} from '../helpers/catalogActivity'
import activityLedgerUrl from '../../content/catalog-activity.json?url'
const activity=ref(null),loading=ref(false),error=ref(''),stage=ref('all'),mode=ref('weekly'),selectedDate=ref(''),page=ref(1)
let generation=0
const pageSize=12
const calendarScroll=ref(null)
const stages=[['all','全部动态'],['received','原件接收'],['loaded','规范入库'],['published','展示更新']]
const events=computed(()=>activity.value?.events||[])
const counts=computed(()=>events.value.reduce((out,e)=>({batches:out.batches+e.receivedBatches,loaded:out.loaded+e.loadedBatches,published:out.published+e.publishedBatches}),{batches:0,loaded:0,published:0}))
const endDate=computed(()=>activityDate(new Date()))
const series=computed(()=>{
 const value=activitySeries(events.value,endDate.value,activity.value?.calendar?.weeks||32)
 const split=activity.value?.calendar?.colorSplitDate||''
 return {...value,splitDate:split,maxBefore:Math.max(1,...value.days.filter(d=>d.date<=split).map(d=>d.count)),maxAfter:Math.max(1,...value.days.filter(d=>d.date>split).map(d=>d.count))}
})
const lastWeek=computed(()=>series.value.days.slice(-7).reduce((n,d)=>n+d.count,0))
const filtered=computed(()=>events.value.filter(e=>{
 const stageOk=stage.value==='all'||(stage.value==='received'?e.receivedBatches>0:stage.value==='loaded'?e.loaded:e.status===stage.value)
 return stageOk&&(!selectedDate.value||activityDate(e.date)===selectedDate.value)
}))
const pages=computed(()=>Math.max(1,Math.ceil(filtered.value.length/pageSize)))
const visible=computed(()=>filtered.value.slice((page.value-1)*pageSize,page.value*pageSize))
watch([stage,selectedDate],()=>page.value=1)
watch(pages,n=>page.value=Math.min(page.value,n))
watch([endDate,()=>Boolean(activity.value)],async()=>{await nextTick();const el=calendarScroll.value;if(el)el.scrollLeft=el.scrollWidth},{flush:'post'})
const stageLabel=event=>event.label||stages.find(([id])=>id===event.status)?.[1]||'数据更新'
const eventDate=value=>(activityDate(value)||'—').replaceAll('-','/')
function pickDate(date){selectedDate.value=selectedDate.value===date?'':date;page.value=1}
const cellLevel=day=>{
 if(!day.count) return 0
 const max=day.date<=(series.value.splitDate||'2026-10-10')?series.value.maxBefore:series.value.maxAfter
 return Math.max(1,Math.ceil(4*Math.sqrt(day.count/Math.max(1,max))))
}
const selectionLabel=computed(()=>selectedDate.value?selectedDate.value.replaceAll('-','/'):'')
const monthLabels=computed(()=>{
 let previous=''
 return Array.from({length:series.value.columns},(_,i)=>{const d=series.value.calendar[i*7],month=d.date.slice(0,7);if(month===previous)return '';previous=month;return Number(month.slice(5))+'月'})
})
const trend=computed(()=>{
 const rows=mode.value==='weekly'?series.value.weekly:series.value.days,cumulative=mode.value==='cumulative',name=cumulative?'累计接收批次':'接收批次'
 return {grid:{left:50,right:22,top:20,bottom:40},tooltip:{trigger:'axis',formatter:ps=>`${escape(ps[0].axisValue)}${mode.value==='weekly'?' 当周':''}<br/>${name}：${fmt(ps[0].value)} 批`},xAxis:{type:'category',data:rows.map(d=>d.date),axisTick:{show:false},axisLine:{lineStyle:{color:'#ddd7da'}},axisLabel:{color:'#738092',fontSize:12,formatter:value=>value.slice(5).replace('-','/'),showMinLabel:true,showMaxLabel:true}},yAxis:{type:'value',minInterval:1,axisLabel:{color:'#738092'},splitLine:{lineStyle:{color:'#eee7ea',type:'dashed'}}},series:[{name,type:cumulative?'line':'bar',data:rows.map(d=>cumulative?d.cumulative:d.count),barMaxWidth:mode.value==='weekly'?12:16,itemStyle:{color:'#b4233c',borderRadius:[3,3,0,0]},symbol:'circle',symbolSize:6,showSymbol:cumulative,lineStyle:{width:2.5,color:'#b4233c'},areaStyle:cumulative?{color:'#b4233c18'}:undefined}]}
})
async function refresh(){
 if(loading.value)return
 const id=++generation;loading.value=true
 try{const response=await fetch(activityLedgerUrl,{cache:'no-store'});if(!response.ok)throw new Error('读取失败');const result=parseActivityLedger(await response.json());if(id===generation){activity.value=result;error.value=''}}
 catch{if(id===generation)error.value='暂时无法读取更新记录，请稍后重试。'}
 finally{if(id===generation)loading.value=false}
}
onMounted(refresh)
onBeforeUnmount(()=>{generation++})
</script>
<template>
<section v-if="activity?.latestRelease" class="panel current-release-panel"><div class="panel-heading"><h3>最新规范库交付</h3><span>{{activity.latestRelease.asOf}} · 展示已同步</span></div><div class="current-release-grid"><article v-for="card in activity.latestRelease.cards" :key="card.title"><span>{{card.title}}</span><strong>{{fmt(card.value)}} <small>{{card.unit}}</small></strong><p>{{card.detail}}</p></article></div></section>
<section class="panel catalog-pulse" aria-label="数据批次更新">
 <div class="panel-heading"><h3>数据更新动态</h3><button class="catalog-refresh" :disabled="loading" :title="activity?.updatedAt?'台账更新：'+activity.updatedAt:'读取更新记录'" @click="refresh"><svg viewBox="0 0 24 24" :class="{spinning:loading}" aria-hidden="true"><path d="M20 10a8 8 0 1 0-1 7M20 3v7h-7"/></svg>{{loading?'读取中':'刷新'}}</button></div>
 <template v-if="activity">
 <div class="catalog-stage-counts">
  <div><span>累计接收</span><strong>{{fmt(counts.batches)}}</strong><small>批</small></div>
  <div><span>近7日接收</span><strong>{{fmt(lastWeek)}}</strong><small>批</small></div>
  <div><span>已规范入库</span><strong>{{fmt(counts.loaded)}}</strong><small>批</small></div>
  <div><span>已用于展示</span><strong>{{fmt(counts.published)}}</strong><small>批</small></div>
 </div>
 <div class="activity-visuals">
  <section class="activity-calendar" aria-label="数据接收活动日历">
   <div class="activity-viz-heading"><div><h4>数据接收活动</h4><span>{{series.activeDays}} 个活跃日 · {{series.total}} 批接收</span></div></div>
   <div ref="calendarScroll" class="activity-calendar-scroll">
    <div class="activity-calendar-grid" :style="{'--weeks':series.columns}">
     <div class="activity-months"><span v-for="(month,i) in monthLabels" :key="i">{{month}}</span></div>
     <div class="activity-weekdays"><span v-for="day in ['一','二','三','四','五','六','日']" :key="day">{{day}}</span></div>
     <div class="activity-days"><button v-for="day in series.calendar" :key="day.date" class="activity-square" :class="['level-'+cellLevel(day),{padding:day.padding,selected:selectedDate===day.date,today:day.date===endDate}]" :disabled="day.padding" :tabindex="day.padding?-1:0" :style="{gridColumn:day.week+1,gridRow:day.weekday+1}" :title="`${day.date} · 接收 ${day.count} 批`" :aria-label="`${day.date} 接收 ${day.count} 批，查看明细`" :aria-pressed="selectedDate===day.date" @click="pickDate(day.date)"></button></div>
    </div>
   </div>
   <p class="activity-hint">点击查看更新明细</p>
  </section>
  <section class="activity-trend" aria-label="接收批次趋势"><div class="activity-viz-heading"><h4>接收批次趋势</h4><div class="activity-controls"><button v-for="[id,label] in [['daily','每日'],['weekly','每周'],['cumulative','累计']]" :key="id" :class="{active:mode===id}" :aria-pressed="mode===id" @click="mode=id">{{label}}</button></div></div><Chart :option="trend" :height="215" label="按展示台账日期汇总的批次趋势"/></section>
 </div>
 </template>
 <div class="activity-detail-heading"><h4>更新明细 <small>{{fmt(filtered.length)}} 条</small></h4><button v-if="selectionLabel" class="activity-date-filter" @click="selectedDate=''">{{selectionLabel}} <span aria-hidden="true">×</span><span class="sr-only">清除时间筛选</span></button></div>
 <div class="catalog-event-filters" aria-label="更新类型"><button v-for="[id,label] in stages" :key="id" :class="{active:stage===id}" :aria-pressed="stage===id" @click="stage=id">{{label}}</button></div>
 <p v-if="error" class="catalog-activity-error" role="status">{{error}}</p>
 <p v-if="loading&&!activity" class="catalog-activity-empty">正在读取批次更新…</p>
 <ol v-else-if="visible.length" class="catalog-events">
  <li v-for="event in visible" :key="event.id" :class="'stage-'+event.status"><span class="catalog-event-dot" aria-hidden="true"></span><time :datetime="event.date">{{eventDate(event.date)}}</time><div class="catalog-event-main"><div><strong>{{activityTitle(event)}}</strong><span class="catalog-event-label">{{stageLabel(event)}}</span></div><p v-if="event.detail">{{event.detail}}</p></div><div class="catalog-event-count"><span v-if="event.presentBatches"><b>{{fmt(event.presentBatches)}}</b> 批</span><span v-else-if="event.records!==null&&event.records!==undefined"><b>{{fmt(event.records)}}</b> {{event.unit||'条'}}</span><small v-if="event.files!==null&&event.files!==undefined">{{fmt(event.files)}} 份文件</small></div></li>
 </ol>
 <p v-else-if="activity" class="catalog-activity-empty">{{selectedDate?'这一天没有符合筛选条件的更新记录。':stage==='all'?'暂无数据更新记录。':'此类更新暂未登记。'}}</p>
 <div v-if="pages>1" class="activity-pagination"><span>第 {{page}} / {{pages}} 页 · 共 {{fmt(filtered.length)}} 条</span><button :disabled="page===1" @click="page--">上一页</button><button :disabled="page===pages" @click="page++">下一页</button></div>
</section>
</template>

<style scoped>.current-release-panel{margin-bottom:24px}.current-release-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px}.current-release-grid article{display:grid;gap:8px}.current-release-grid span,.current-release-grid p{color:#748091;font-size:14px;margin:0}.current-release-grid strong{font-size:24px;color:#ae1833}.current-release-grid small{font-size:13px;font-weight:400}@media(max-width:700px){.current-release-grid{grid-template-columns:1fr}}</style>
