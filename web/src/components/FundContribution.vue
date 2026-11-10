<script setup>
/* 基金贡献度沿用四段布局；全部范围使用服务端独立去重汇总。 */
import {computed,ref} from 'vue'
import Chart from './Chart.vue'
import {fmt,chartBase} from '../shared'
import {treeColors} from '../technologyTreeLayout'
import {ORDER,useAnalysisMetrics} from '../helpers/investData'
const props=defineProps({data:Object})
const emit=defineEmits(['explore'])
const {metrics,error:loadError,loading,load}=useAnalysisMetrics()
const order=ORDER,cat=ref('all')
const catNames=computed(()=>Object.fromEntries((metrics.value?.categories||[]).map(c=>[c.id,c.name])))
const tone=computed(()=>cat.value==='all'?'#a21535':treeColors[cat.value])
const selected=computed(()=>cat.value==='all'?metrics.value?.all:metrics.value?.categories.find(c=>c.id===cat.value))
const years=computed(()=>metrics.value?.years||[])
const series=computed(()=>selected.value?.series)
const totals=computed(()=>selected.value?.totals||{})
const known=v=>typeof v==='number'&&Number.isFinite(v)
const show=v=>known(v)?fmt(Math.round(v)):'—'
const decimal=v=>known(v)?v.toFixed(2):'—'
const period=computed(()=>years.value.length?`${years.value[0]}—${years.value.at(-1)}`:'')
const productivity=computed(()=>{
 if(!selected.value)return []
 const t=totals.value,f=t.approved_funding_wan
 return [
  {label:'项目批准经费',value:known(f)?(f/1e4).toFixed(f/1e4>=10?1:2):'—',unit:'亿元',note:'每个项目的批准经费计入一次'},
  {label:'关联论文',value:show(t.funded_papers),unit:'篇',note:`${period.value} 年发表`},
  {label:'关联专利',value:show(t.funded_patents),unit:'件',note:`${period.value} 年申请 · 按申请号计`},
  {label:'覆盖项目',value:show(t.project_count),unit:'项',note:metrics.value.cohort.label},
 ]
})
const axis={axisLine:{lineStyle:{color:'#dcd5d1'}},axisTick:{show:false},axisLabel:{color:'#7a7378',fontSize:12}}
const split={splitLine:{lineStyle:{color:'#efe9e6',type:'dashed'}}}
const productivityChart=computed(()=>series.value&&({...chartBase,
 grid:{top:46,right:56,bottom:30,left:56,containLabel:true},
 legend:{top:0,left:0,itemWidth:14,itemHeight:8,textStyle:{fontSize:13,color:'#5d575b'}},
 tooltip:{trigger:'axis',confine:true,valueFormatter:v=>show(v)},
 xAxis:{type:'category',data:years.value.map(String),...axis},
 yAxis:[{type:'value',name:'万元',nameTextStyle:{color:'#9a9296',fontSize:12},...axis,...split},{type:'value',name:'篇 / 件',nameTextStyle:{color:'#9a9296',fontSize:12},...axis,splitLine:{show:false}}],
 series:[
  {name:'在研经费',type:'bar',barMaxWidth:30,itemStyle:{color:tone.value,opacity:.18,borderRadius:[3,3,0,0]},emphasis:{itemStyle:{opacity:.32}},data:series.value.active_funding_wan},
  {name:'论文',type:'line',yAxisIndex:1,smooth:.25,symbolSize:6,lineStyle:{width:2.4,color:tone.value},itemStyle:{color:tone.value},data:series.value.funded_papers},
  {name:'专利',type:'line',yAxisIndex:1,smooth:.25,symbolSize:6,lineStyle:{width:2,type:[6,4],color:'#b2772a'},itemStyle:{color:'#b2772a'},data:series.value.funded_patents},
 ]}))
function smallChart(key,name,color,unit){return series.value&&({...chartBase,
 grid:{top:16,right:12,bottom:26,left:44,containLabel:true},tooltip:{trigger:'axis',confine:true,valueFormatter:v=>show(v)+' '+unit},
 xAxis:{type:'category',data:years.value.map(String),...axis},yAxis:{type:'value',...axis,...split},
 series:[{name,type:'bar',barMaxWidth:22,itemStyle:{color,borderRadius:[3,3,0,0]},data:series.value[key]}]})}
const patentChart=computed(()=>smallChart('funded_patents','专利申请','#b2772a','件'))
const citationChart=computed(()=>smallChart('paper_citations','新增引证记录',tone.value,'次'))
const citationCoverage=computed(()=>selected.value?.coverage?.citation_eligible_papers)

/* 代表成果的公开时间按技术点去重；既不累计同主题事件，也不将其解释为技术起源。 */
const progress=computed(()=>{
 const supplied=metrics.value?.representative_progress
 const events=supplied?.length?supplied:(props.data?.chronology?.events||[])
 const first=new Map()
 for(const e of events){
  const topic=e.topic_id,year=Number(e.first_public_year??e.year),category=e.category_id||String(topic||'').split('.')[0]
  if(!topic||!Number.isInteger(year)||!order.includes(category))continue
  if(!first.has(topic)||year<first.get(topic).year)first.set(topic,{topic,year,category})
 }
 return [...first.values()]
})
const births=computed(()=>{
 const ys=years.value,chosen=progress.value.filter(e=>cat.value==='all'||e.category===cat.value)
 const byCat=order.map(id=>({id,data:ys.map(y=>progress.value.filter(e=>e.category===id&&e.year===y).length)}))
 const perYear=ys.map(y=>chosen.filter(e=>e.year===y).length),since=perYear.reduce((a,b)=>a+b,0)
 return {ys,byCat,since,avg:ys.length?(since/ys.length).toFixed(1):'—',recent:perYear.slice(-3).reduce((a,b)=>a+b,0),early:perYear.slice(0,3).reduce((a,b)=>a+b,0),earlyPeriod:ys.length?`${ys[0]}—${ys[Math.min(2,ys.length-1)]}`:'',recentPeriod:ys.length?`${ys[Math.max(0,ys.length-3)]}—${ys.at(-1)}`:''}
})
const birthChart=computed(()=>({...chartBase,
 grid:{top:16,right:12,bottom:26,left:36,containLabel:true},tooltip:{trigger:'axis',confine:true},
 xAxis:{type:'category',data:births.value.ys.map(String),...axis},yAxis:{type:'value',minInterval:1,...axis,...split},
 series:births.value.byCat.filter(s=>cat.value==='all'||s.id===cat.value).map(s=>({name:catNames.value[s.id]||s.id,type:'bar',stack:'b',barMaxWidth:22,itemStyle:{color:treeColors[s.id]},data:s.data}))}))
</script>

<template><div class="fc">
 <div class="fc-filter" role="tablist" aria-label="技术大类">
  <span>技术大类</span>
  <button role="tab" :aria-selected="cat==='all'" :class="{active:cat==='all'}" @click="cat='all'">全部 7 类</button>
  <button v-for="id in order" :key="id" role="tab" :aria-selected="cat===id" :class="{active:cat===id}" :style="{'--c':treeColors[id]}" @click="cat=id"><i></i>{{catNames[id]||id}}</button>
 </div>
 <div v-if="loadError" class="notice error">投入与成果指标读取失败 <button @click="load">重试</button></div>
 <div v-else-if="loading&&!metrics" class="fc-loading">正在读取投入与成果指标…</div>
 <template v-if="metrics">
 <section class="fc-sec" :style="{'--c':tone}">
  <header><b>01</b><div><h3>支撑范围 · 投入与成果规模</h3><p>{{metrics.cohort.label}} · 批准经费与关联成果</p></div></header>
  <div class="fc-grid">
   <div class="fc-tiles"><article v-for="k in productivity" :key="k.label"><span>{{k.label}}</span><strong>{{k.value}}<small>{{k.unit}}</small></strong><em>{{k.note}}</em></article></div>
   <div class="fc-chart"><Chart v-if="productivityChart" :option="productivityChart" :height="300" label="在研经费与关联论文、专利逐年产出"/></div>
  </div>
  <p class="fc-note">图中在研经费表示各年执行项目的支持存量；上方批准经费按项目计入一次。</p>
 </section>

 <section class="fc-sec" :style="{'--c':tone}">
  <header><b>02</b><div><h3>学术影响</h3><p>关联论文的本地引证记录与三年观察结果</p></div><span class="fc-basis">论文引证年度 <b>{{period}}</b></span></header>
  <div class="fc-cards">
   <article><span>新增引证记录</span><strong>{{show(totals.paper_citations)}}<small>次</small></strong><em>按引用论文年份统计关联成果的引证</em><div class="fc-mini"><Chart v-if="citationChart" :option="citationChart" :height="150" label="按引证发生年份的新增引证记录"/></div></article>
   <article><span>三年篇均被引</span><strong>{{decimal(totals.mean_citations_3y)}}<small>次</small></strong><em>2017—2022 年发表队列 · 发表后第 1—3 年</em><em>队列分母 {{show(citationCoverage)}} 篇论文</em></article>
   <article class="pending"><span>期刊影响因子</span><strong>—</strong><em>关联论文发表期刊的年度影响因子中位数与分布</em><mark>待补充</mark></article>
   <article><span>被专利引用论文</span><strong>{{show(totals.patent_cited_papers)}}<small>篇</small></strong><em>涉及 {{show(totals.citing_patent_applications)}} 件专利申请</em><em>截至2025年申请的专利 · 当前引用关系库</em></article>
  </div>
  <p class="fc-note">本地引文库 · 论文引证观察截至 2025 年；2023—2025 年发表队列待后续观察。</p>
 </section>

 <section class="fc-sec" :style="{'--c':tone}">
  <header><b>03</b><div><h3>技术应用</h3><p>基金关联专利的申请规模与企业参与</p></div><button class="fc-link" @click="emit('explore','fund_patent')">查看基金—专利证据 →</button></header>
  <div class="fc-cards">
   <article class="wide"><span>专利申请数量</span><strong>{{show(totals.funded_patents)}}<small>件</small></strong><div class="fc-mini"><Chart v-if="patentChart" :option="patentChart" :height="150" label="逐年基金关联专利申请"/></div></article>
   <article><span>企业参与专利</span><strong>{{show(totals.enterprise_patents)}}<small>件</small></strong><em>基金关联专利中，申请人或当前持有人含企业的申请</em></article>
   <article class="pending"><span>与产品挂钩</span><strong>—</strong><em>可对应到具体产品或服务的专利数量</em><mark>待补充</mark></article>
   <article class="pending"><span>转让与许可</span><strong>—</strong><em>有转让、许可记录及发生时间的专利数量</em><mark>待补充</mark></article>
  </div>
  <p class="fc-note">企业参与按关联专利的申请人及当前持有人识别。</p>
 </section>

 <section class="fc-sec" :style="{'--c':tone}">
  <header><b>04</b><div><h3>代表性技术进展</h3><p>按技术点去重后的代表成果首次公开年份</p></div><router-link class="fc-link" to="/evolution">技术演进 →</router-link></header>
  <div class="fc-grid narrow">
   <div class="fc-tiles col">
    <article><span>代表性技术点 · {{period}}</span><strong>{{births.since}}<small>项</small></strong><em>每个技术点计入一次，年均 {{births.avg}} 项</em></article>
    <article><span>近三年代表性进展</span><strong>{{births.recent}}<small>项 · {{births.recentPeriod}}</small></strong><em>{{births.earlyPeriod}} 年为 {{births.early}} 项</em></article>
    <article class="pending"><span>基金论文首涉时间差</span><strong>—</strong><em>逐技术核对资助论文与代表成果的首次公开时间</em><mark>待补充</mark></article>
   </div>
   <div class="fc-chart"><Chart :option="birthChart" :height="280" label="按技术点去重后的逐年代表成果数量"/></div>
  </div>
 </section>
 <p class="fc-note fc-asof">数据截至 {{String(metrics.as_of).slice(0,10)}}；全部范围使用独立去重汇总。</p>
 </template>
</div></template>

<style scoped>
.fc-note{margin:14px 0 0;font-size:12px;line-height:1.7;color:#8a8286}.fc-asof{margin:0}.fc-loading{padding:60px 20px;text-align:center;color:#8a8286}
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
