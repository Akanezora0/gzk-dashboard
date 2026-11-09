<script setup>
/*
 * 基金贡献度：按技术大类观察基金投入后的生产力、学术影响、技术应用与新技术诞生。
 * 已有数据：在研经费与年度论文、专利（curves.html 快照）；新技术点首次公开年份（技术演进词表）；论文引用关系规模。
 * 暂缺数据以占位卡呈现，指标定义集中在 pendingMetrics，后续补数后替换为实际数值。
 */
import {computed,ref,onMounted,onBeforeUnmount} from 'vue'
import Chart from './Chart.vue'
import {fmt,chartBase} from '../shared'
import {treeColors} from '../technologyTreeLayout'
const props=defineProps({data:Object})
const emit=defineEmits(['explore'])

const order=['AI1','AI2','AI3','AI4','AI5','AI6','AI7']
const catNames=computed(()=>Object.fromEntries((props.data?.tree?.nodes||[]).filter(n=>n.node_type==='category').map(n=>[n.id,n.label])))
const cat=ref('all')
const tone=computed(()=>cat.value==='all'?'#a21535':treeColors[cat.value])

/* 在研经费、年度论文与专利（2017—2022 年立项项目，跨类别分摊） */
const curves=ref(null),loadError=ref(false)
const controller=new AbortController()
async function load(){
 loadError.value=false
 try{
  const r=await fetch('/chain-analysis/v1/curves.html',{signal:controller.signal});if(!r.ok)throw new Error()
  const doc=new DOMParser().parseFromString(await r.text(),'text/html')
  const d=JSON.parse(doc.querySelector('script#data')?.textContent||'null')
  if(!d?.years?.length||!d?.layers?.length)throw new Error()
  curves.value=d
 }catch(e){if(e.name!=='AbortError')loadError.value=true}
}
onMounted(load);onBeforeUnmount(()=>controller.abort())
const years=computed(()=>curves.value?.years||[])
const series=computed(()=>{
 const d=curves.value;if(!d)return null
 const pick=d.layers.filter(l=>cat.value==='all'||l.id===cat.value)
 const sum=k=>d.years.map((_,i)=>pick.reduce((s,l)=>s+l[k][i],0))
 return {funding:sum('funding'),papers:sum('papers'),patents:sum('patents')}
})
const total=k=>series.value?series.value[k].reduce((a,b)=>a+b,0):null
const productivity=computed(()=>{
 if(!series.value)return []
 const f=total('funding'),p=total('papers'),t=total('patents')
 return [
  {label:'在研经费规模',value:(f/1e4).toFixed(f/1e4>=10?1:2),unit:'亿元',note:'执行期内逐年计入'},
  {label:'关联论文',value:fmt(Math.round(p)),unit:'篇',note:'2017—2025 年发表'},
  {label:'关联专利',value:fmt(Math.round(t)),unit:'件',note:'2017—2025 年申请'},
  {label:'每千万元经费产出',value:(p/(f/1000)).toFixed(1),unit:'篇论文',note:`专利 ${(t/(f/1000)).toFixed(1)} 件`},
 ]
})
const axis={axisLine:{lineStyle:{color:'#dcd5d1'}},axisTick:{show:false},axisLabel:{color:'#7a7378',fontSize:12}}
const split={splitLine:{lineStyle:{color:'#efe9e6',type:'dashed'}}}
const productivityChart=computed(()=>series.value&&({...chartBase,
 grid:{top:46,right:56,bottom:30,left:56,containLabel:true},
 legend:{top:0,left:0,itemWidth:14,itemHeight:8,textStyle:{fontSize:13,color:'#5d575b'}},
 tooltip:{trigger:'axis',confine:true,valueFormatter:v=>fmt(Math.round(v))},
 xAxis:{type:'category',data:years.value.map(String),...axis},
 yAxis:[{type:'value',name:'万元',nameTextStyle:{color:'#9a9296',fontSize:12},...axis,...split},{type:'value',name:'篇 / 件',nameTextStyle:{color:'#9a9296',fontSize:12},...axis,splitLine:{show:false}}],
 series:[
  {name:'在研经费',type:'bar',barMaxWidth:30,itemStyle:{color:tone.value,opacity:.18,borderRadius:[3,3,0,0]},emphasis:{itemStyle:{opacity:.32}},data:series.value.funding},
  {name:'论文',type:'line',yAxisIndex:1,smooth:.25,symbolSize:6,lineStyle:{width:2.4,color:tone.value},itemStyle:{color:tone.value},data:series.value.papers},
  {name:'专利',type:'line',yAxisIndex:1,smooth:.25,symbolSize:6,lineStyle:{width:2,type:[6,4],color:'#b2772a'},itemStyle:{color:'#b2772a'},data:series.value.patents},
 ]}))
const patentChart=computed(()=>series.value&&({...chartBase,
 grid:{top:16,right:12,bottom:26,left:44,containLabel:true},tooltip:{trigger:'axis',confine:true,valueFormatter:v=>fmt(Math.round(v))+' 件'},
 xAxis:{type:'category',data:years.value.map(String),...axis},yAxis:{type:'value',...axis,...split},
 series:[{name:'专利申请',type:'bar',barMaxWidth:22,itemStyle:{color:'#b2772a',borderRadius:[3,3,0,0]},data:series.value.patents}]}))

/* 新技术诞生：技术演进词表中各技术点代表成果的首次公开年份 */
const births=computed(()=>{
 const ev=(props.data?.chronology?.events||[]).filter(e=>cat.value==='all'||e.category_id===cat.value)
 const first=new Map();ev.forEach(e=>{const y=Number(e.year);if(!first.has(e.topic_id)||first.get(e.topic_id)>y)first.set(e.topic_id,y)})
 const ys=[];for(let y=2017;y<=2025;y++)ys.push(y)
 const byCat=order.map(id=>({id,data:ys.map(y=>(props.data?.chronology?.events||[]).filter(e=>e.category_id===id&&Number(e.year)===y).length)}))
 const perYear=ys.map(y=>ev.filter(e=>Number(e.year)===y).length)
 const since=perYear.reduce((a,b)=>a+b,0),recent=perYear.slice(-3).reduce((a,b)=>a+b,0),early=perYear.slice(0,3).reduce((a,b)=>a+b,0)
 const topicsSince=[...first.values()].filter(y=>y>=2017).length
 return {ys,byCat,perYear,since,topicsSince,avg:(since/ys.length).toFixed(1),recent,early}
})
const birthChart=computed(()=>({...chartBase,
 grid:{top:16,right:12,bottom:26,left:36,containLabel:true},tooltip:{trigger:'axis',confine:true},
 xAxis:{type:'category',data:births.value.ys.map(String),...axis},yAxis:{type:'value',minInterval:1,...axis,...split},
 series:births.value.byCat.filter(s=>cat.value==='all'||s.id===cat.value).map(s=>({name:catNames.value[s.id]||s.id,type:'bar',stack:'b',barMaxWidth:22,itemStyle:{color:treeColors[s.id]},data:s.data}))}))

const citations=computed(()=>props.data?.currentInventory?.counts?.citation_edge)
</script>

<template><div class="fc">
 <div class="fc-filter" role="tablist" aria-label="技术大类">
  <span>技术大类</span>
  <button role="tab" :aria-selected="cat==='all'" :class="{active:cat==='all'}" @click="cat='all'">全部 7 类</button>
  <button v-for="id in order" :key="id" role="tab" :aria-selected="cat===id" :class="{active:cat===id}" :style="{'--c':treeColors[id]}" @click="cat=id"><i></i>{{catNames[id]||id}}</button>
 </div>

 <div v-if="loadError" class="notice error">经费与产出数据读取失败 <button @click="load">重试</button></div>

 <section class="fc-sec" :style="{'--c':tone}">
  <header><b>01</b><div><h3>支撑范围 · 投入后的生产力</h3><p>2017—2022 年立项项目的在研经费，与其关联论文、专利的逐年产出</p></div></header>
  <div class="fc-grid">
   <div class="fc-tiles"><article v-for="k in productivity" :key="k.label"><span>{{k.label}}</span><strong>{{k.value}}<small>{{k.unit}}</small></strong><em>{{k.note}}</em></article></div>
   <div class="fc-chart"><Chart v-if="productivityChart" :option="productivityChart" :height="300" label="在研经费与论文、专利逐年产出"/></div>
  </div>
 </section>

 <section class="fc-sec" :style="{'--c':tone}">
  <header><b>02</b><div><h3>学术影响</h3><p>关联论文的被引与发表质量</p></div><span class="fc-basis" v-if="citations">引用关系库 <b>{{fmt(citations)}}</b> 对</span></header>
  <div class="fc-cards">
   <article class="pending"><span>年度被引次数</span><div class="fc-skeleton"><i v-for="i in 9" :key="i" :style="{height:(18+i*7)+'%'}"></i></div><em>按发表年份汇总关联论文的被引次数</em><mark>数据补充中</mark></article>
   <article class="pending"><span>篇均被引</span><strong>—</strong><em>与同年份、同领域论文对比的相对影响</em><mark>数据补充中</mark></article>
   <article class="pending"><span>期刊影响因子</span><strong>—</strong><em>关联论文发表期刊的影响因子中位数与分布</em><mark>数据补充中</mark></article>
   <article class="pending"><span>高被引论文</span><strong>—</strong><em>进入同领域前 1% 被引的论文数量</em><mark>数据补充中</mark></article>
  </div>
 </section>

 <section class="fc-sec" :style="{'--c':tone}">
  <header><b>03</b><div><h3>技术应用</h3><p>专利产出及其在企业与产品中的落地</p></div><button class="fc-link" @click="emit('explore','patent_tech')">查看专利—技术证据 →</button></header>
  <div class="fc-cards">
   <article class="wide"><span>专利申请数量</span><strong>{{fmt(Math.round(total('patents')||0))}}<small>件</small></strong><div class="fc-mini"><Chart v-if="patentChart" :option="patentChart" :height="150" label="逐年专利申请"/></div></article>
   <article class="pending"><span>企业认领专利</span><strong>—</strong><em>专利权人为企业或由企业受让的专利数量</em><mark>数据补充中</mark></article>
   <article class="pending"><span>与产品挂钩</span><strong>—</strong><em>可对应到具体产品或服务的专利数量</em><mark>数据补充中</mark></article>
   <article class="pending"><span>转让与许可</span><strong>—</strong><em>发生转让、许可等转化行为的专利数量</em><mark>数据补充中</mark></article>
  </div>
 </section>

 <section class="fc-sec" :style="{'--c':tone}">
  <header><b>04</b><div><h3>新技术诞生</h3><p>技术演进词表中各技术点代表成果的首次公开年份</p></div><router-link class="fc-link" to="/evolution">技术演进 →</router-link></header>
  <div class="fc-grid narrow">
   <div class="fc-tiles col">
    <article><span>新技术诞生量 · 2017—2025</span><strong>{{births.since}}<small>项</small></strong><em>按技术点代表成果计，年均 {{births.avg}} 项</em></article>
    <article><span>诞生速度</span><strong>{{births.recent}}<small>项 / 近三年</small></strong><em>2017—2019 年为 {{births.early}} 项</em></article>
    <article class="pending"><span>基金资助论文率先涉及</span><strong>—</strong><em>新技术点首次出现在基金资助论文中的时间差</em><mark>数据补充中</mark></article>
   </div>
   <div class="fc-chart"><Chart :option="birthChart" :height="280" label="逐年新技术点数量"/></div>
  </div>
 </section>
</div></template>

<style scoped>
.fc{display:flex;flex-direction:column;gap:22px}
.fc-filter{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.fc-filter>span{margin-right:6px;font-size:13px;letter-spacing:1px;color:#8a8286}
.fc-filter button{display:inline-flex;align-items:center;gap:7px;padding:7px 13px;border:1px solid #e4dcd8;border-radius:3px;background:#fff;font:inherit;font-size:14px;color:#5d575b;cursor:pointer;transition:border-color .2s,color .2s,background .2s}
.fc-filter button i{width:8px;height:8px;border-radius:50%;background:var(--c)}
.fc-filter button:hover:not(.active){border-color:#cdbfc3;color:#2f2b2d}
.fc-filter button.active{border-color:var(--c,#a21535);color:var(--c,#a21535);background:color-mix(in srgb,var(--c,#a21535) 6%,#fff);font-weight:650}
.fc-sec{background:#fff;border:1px solid #e6dfdb;border-radius:4px;padding:26px 28px 28px}
.fc-sec>header{display:flex;align-items:flex-start;gap:16px;margin-bottom:20px}
.fc-sec>header>b{font-size:15px;font-weight:800;color:var(--c);padding-top:4px;font-variant-numeric:tabular-nums}
.fc-sec>header>div{flex:1}
.fc-sec h3{margin:0;font-size:20px;font-weight:700;color:#232930}
.fc-sec header p{margin:4px 0 0;font-size:13.5px;color:#7a7378}
.fc-basis{font-size:13px;color:#7a7378;padding-top:6px}.fc-basis b{color:#2f2b2d;font-variant-numeric:tabular-nums}
.fc-link{flex:none;padding:7px 0;background:none;border:0;font:inherit;font-size:14px;font-weight:600;color:#a21535;cursor:pointer;text-decoration:none}
.fc-grid{display:grid;grid-template-columns:minmax(260px,.9fr) 2fr;gap:24px;align-items:stretch}
.fc-grid.narrow{grid-template-columns:minmax(240px,.7fr) 2fr}
.fc-tiles{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.fc-tiles.col{grid-template-columns:1fr}
.fc-tiles article,.fc-cards article{position:relative;display:flex;flex-direction:column;gap:4px;padding:16px 18px;border:1px solid #ece5e1;border-radius:3px;background:#fcfaf9}
.fc-tiles article::before,.fc-cards article:not(.pending)::before{content:"";position:absolute;left:-1px;top:14px;bottom:14px;width:3px;background:var(--c)}
.fc-tiles span,.fc-cards span{font-size:13px;color:#7a7378}
.fc-tiles strong,.fc-cards strong{font-size:28px;font-weight:750;line-height:1.2;color:#232930;font-variant-numeric:tabular-nums}
.fc-tiles small,.fc-cards small{margin-left:5px;font-size:13px;font-weight:500;color:#7a7378}
.fc-tiles em,.fc-cards em{font-style:normal;font-size:12.5px;color:#9a9296;line-height:1.5}
.fc-chart{min-width:0}
.fc-cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
.fc-cards article.wide{grid-column:span 1}
.fc-cards article.pending{background:repeating-linear-gradient(135deg,#fff 0 8px,#faf7f6 8px 16px);border-style:dashed;border-color:#ddd3cf}
.fc-cards article.pending strong{color:#c4babd}
.fc-tiles article.pending{background:repeating-linear-gradient(135deg,#fff 0 8px,#faf7f6 8px 16px);border-style:dashed}
.fc-tiles article.pending::before{display:none}
.fc-tiles article.pending strong{color:#c4babd}
mark{align-self:flex-start;margin-top:6px;padding:2px 8px;border-radius:2px;background:#f3eeec;color:#8a8286;font-size:12px}
.fc-skeleton{display:flex;align-items:flex-end;gap:5px;height:44px;margin:4px 0 2px}
.fc-skeleton i{flex:1;background:#ece5e2;border-radius:2px 2px 0 0}
.fc-mini{margin:0 -6px -8px}
@media(max-width:1100px){.fc-cards{grid-template-columns:repeat(2,1fr)}.fc-grid,.fc-grid.narrow{grid-template-columns:1fr}}
@media(max-width:600px){.fc-sec{padding:20px 16px}.fc-cards,.fc-tiles{grid-template-columns:1fr}.fc-sec>header{flex-wrap:wrap}.fc-tiles strong,.fc-cards strong{font-size:24px}}
</style>
