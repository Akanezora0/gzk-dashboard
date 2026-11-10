<script setup>
/* 基金贡献度沿用四段布局；全部范围使用服务端独立去重汇总。 */
import {computed,ref,watch} from 'vue'
import Chart from './Chart.vue'
import {fmt,chartBase} from '../shared'
import {treeColors} from '../technologyTreeLayout'
import {ORDER,useAnalysisMetrics} from '../helpers/investData'
const props=defineProps({data:Object})
const emit=defineEmits(['explore'])
const {metrics,error:loadError,loading,load}=useAnalysisMetrics()
const detail=ref(null)
fetch('/chain-analysis/v1/contribution-detail.json').then(r=>{if(!r.ok)throw new Error('detail');return r.json()}).then(d=>detail.value=d).catch(()=>{})
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
const meanChart=computed(()=>{const o=smallChart('mean_citations_3y','三年篇均被引',tone.value,'次');if(!o)return null;o.xAxis.data=years.value.filter(y=>y<=2022).map(String);o.series[0].data=series.value.mean_citations_3y.slice(0,o.xAxis.data.length);o.tooltip.valueFormatter=v=>decimal(v)+' 次';return o})
const impact=computed(()=>detail.value?.categories?.[cat.value])
const impactChart=computed(()=>impact.value&&({...chartBase,grid:{top:16,right:12,bottom:26,left:30,containLabel:true},tooltip:{trigger:'axis',valueFormatter:v=>v+'%'},xAxis:{type:'category',data:impact.value.annual.map(r=>String(r.year)),...axis},yAxis:{type:'value',max:100,...axis,...split},series:[{type:'bar',data:impact.value.annual.map(r=>r.share),barMaxWidth:22,itemStyle:{color:tone.value,borderRadius:[3,3,0,0]}}]}))
const examples=computed(()=>impact.value?.cases||[])
const activePaper=ref(0)
watch(cat,()=>activePaper.value=0)
const featured=computed(()=>examples.value[activePaper.value])
const titles={
 'A Comprehensive Survey on Transfer Learning':'迁移学习：知识如何跨任务复用',
 'Object Detection With Deep Learning: A Review':'深度学习目标检测综述',
 'Informer: Beyond Efficient Transformer for Long Sequence Time-Series Forecasting':'Informer：长序列时间序列预测',
 'Knowledge Distillation: A Survey':'知识蒸馏综述',
 'CSWin Transformer: A General Vision Transformer Backbone with Cross-Shaped Windows':'CSWin Transformer：十字窗口视觉骨干网络',
 'SpectralFormer: Rethinking Hyperspectral Image Classification With Transformers':'SpectralFormer：高光谱图像分类',
 'Identifying Medical Diagnoses and Treatable Diseases by Image-Based Deep Learning':'图像深度学习用于疾病诊断',
 'Deep Learning for Generic Object Detection: A Survey':'通用目标检测的深度学习综述',
 'Communication-efficient federated learning via knowledge distillation':'知识蒸馏支持通信高效的联邦学习',
 'UniXcoder: Unified Cross-Modal Pre-training for Code Representation':'UniXcoder：代码表示的跨模态预训练',
 'Decentralized Edge Intelligence: A Dynamic Resource Allocation Framework for Hierarchical Federated Learning':'分层联邦学习的动态资源分配',
 'When Federated Learning Meets Blockchain: A New Distributed Learning Paradigm':'联邦学习与区块链的分布式学习',
 'Boost Precision Agriculture with Unmanned Aerial Vehicle Remote Sensing and Edge Intelligence: A Survey':'无人机遥感与边缘智能支持精准农业',
 'Universal artificial intelligence platform for collaborative management of cataracts':'白内障协同管理的人工智能平台',
 'Controllable Multi-Interest Framework for Recommendation':'推荐系统的可控多兴趣框架',
 'Object detection in optical remote sensing images: A survey and a new benchmark':'光学遥感目标检测：综述与基准',
 'A survey on federated learning: challenges and applications':'联邦学习的挑战与应用综述',
 'Medical image segmentation using deep learning: A survey':'医学图像分割的深度学习综述',
 'A Survey of Deep Learning-Based Object Detection':'深度学习目标检测综述',
 'Remote Sensing Image Scene Classification Meets Deep Learning: Challenges, Methods, Benchmarks, and Opportunities':'遥感场景分类：方法、基准与挑战',
 'CA-Net: Comprehensive Attention Convolutional Neural Networks for Explainable Medical Image Segmentation':'CA-Net：可解释的医学图像分割',
 'Learning Intents behind Interactions with Knowledge Graph for Recommendation':'知识图谱推荐中的交互意图学习',
}
const readable=e=>titles[e.title]||e.title
const institutions=computed(()=>[...new Set((featured.value?.grants||[]).map(g=>g.institution).filter(Boolean))])
const grantYears=computed(()=>[...new Set((featured.value?.grants||[]).map(g=>g.year).filter(Boolean))].sort().join(' / '))

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
  <header><b>01</b><div><h3>支撑范围 · 投入与成果规模</h3></div></header>
  <div class="fc-grid">
   <div class="fc-tiles"><article v-for="k in productivity" :key="k.label"><span>{{k.label}}</span><strong>{{k.value}}<small>{{k.unit}}</small></strong><em>{{k.note}}</em></article></div>
   <div class="fc-chart"><Chart v-if="productivityChart" :option="productivityChart" :height="300" label="在研经费与关联论文、专利逐年产出"/></div>
  </div>
  
 </section>

 <section class="fc-sec" :style="{'--c':tone}">
  <header><b>02</b><div><h3>学术影响</h3></div><span class="fc-basis">论文引证年度 <b>{{period}}</b></span></header>
  <div class="fc-cards">
   <article><span>新增引证记录</span><strong>{{show(totals.paper_citations)}}<small>次</small></strong><em>按引用论文年份统计关联成果的引证</em><div class="fc-mini"><Chart v-if="citationChart" :option="citationChart" :height="150" label="按引证发生年份的新增引证记录"/></div></article>
   <article><span>三年篇均被引</span><strong>{{decimal(totals.mean_citations_3y)}}<small>次</small></strong><em>2017—2022 年发表队列 · 发表后第 1—3 年</em><div class="fc-mini"><Chart v-if="meanChart" :option="meanChart" :height="150" label="各发表年度论文的三年篇均被引"/></div></article>
   <article class="pending"><span>期刊影响因子</span><strong>—</strong><em>关联论文发表期刊的年度影响因子中位数与分布</em><mark>待补充</mark></article>
   <article><span>高被引组的引证份额</span><strong>{{impact?.citation_share ?? '—'}}<small>%</small></strong><em>基金关联论文内，按发表年选取三年被引前10%（含并列）</em><div class="fc-mini"><Chart v-if="impactChart" :option="impactChart" :height="150" label="各发表年高被引组占三年引证的比例"/></div></article>
  </div>

 </section>

 <section class="fc-sec" :style="{'--c':tone}">
  <header><b>03</b><div><h3>基金支持的高影响成果</h3></div></header>
  <div v-if="impact" class="fc-impact-overview">
   <div class="fc-impact-message"><span class="fc-eyebrow">成果的影响分布</span><h4>关键成果，持续获得后续研究关注</h4><p>{{show(impact.high_papers)}} 篇论文进入各发表年度的高被引组，在 {{show(impact.papers)}} 篇基金关联论文中形成集中的学术影响。</p></div>
   <div class="fc-share-bars">
    <div><span>高被引组 · 论文份额</span><strong>{{impact.paper_share}}<small>%</small></strong><div class="fc-share-track"><i :style="{width:impact.paper_share+'%'}"></i></div></div>
    <div><span>高被引组 · 三年引证份额</span><strong>{{impact.citation_share}}<small>%</small></strong><div class="fc-share-track"><i :style="{width:impact.citation_share+'%'}"></i></div></div>
   </div>
  </div>
  <div v-if="featured" class="fc-showcase">
   <nav class="fc-work-list" aria-label="代表成果选择">
    <div class="fc-work-label">代表成果 <span>{{examples.length}} 项</span></div>
    <button v-for="(e,i) in examples" :key="e.paper_id" :class="{chosen:activePaper===i}" :aria-pressed="activePaper===i" @click="activePaper=i">
     <span class="fc-work-index">{{String(i+1).padStart(2,'0')}}</span>
     <span class="fc-work-text"><b>{{readable(e)}}</b><small>{{e.year}} 年 · 三年被引 {{show(e.citations_3y)}} 次</small></span><span class="fc-work-arrow" aria-hidden="true">↗</span>
    </button>
   </nav>
   <article class="fc-feature" :key="featured.paper_id">
    <div class="fc-feature-heading"><div><span class="fc-eyebrow">基金关联成果</span><h4>{{readable(featured)}}</h4><p class="fc-original-title">{{featured.title}}</p></div><div class="fc-cite-number"><strong>{{show(featured.citations_3y)}}</strong><span>三年被引 / 次</span></div></div>
    <div class="fc-research-route">
     <div><span class="fc-route-dot"></span><small>关联项目批准</small><b>{{grantYears || '—'}}</b><p>{{featured.grants.length}} 项基金项目</p></div>
     <div><span class="fc-route-dot"></span><small>研究成果发表</small><b>{{featured.year}}</b><p>论文发表</p></div>
     <div><span class="fc-route-dot"></span><small>后续引证观察</small><b>{{featured.year+1}}—{{featured.year+3}}</b><p>{{show(featured.citations_3y)}} 次论文引证</p></div>
    </div>
    <div class="fc-support-heading"><h5>关联基金支持</h5><span>{{institutions.join(' · ')}}</span></div>
    <div class="fc-projects"><details v-for="g in featured.grants" :key="g.number"><summary><span class="fc-project-year">{{g.year || '—'}}</span><span class="fc-project-name">{{g.title}}<small>{{g.institution}}</small></span><span class="fc-project-toggle" aria-hidden="true">＋</span></summary><p>基金批准号 <b>{{g.number}}</b> · {{g.year || '—'}} 年批准</p></details></div>
   </article>
  </div>
 </section>
 
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
.fc-mini{margin:auto -6px -8px;padding-top:12px}.fc-audit{margin-top:16px;padding:12px 16px;background:#faf7f6;color:#74676c;font-size:13px;line-height:1.7}.fc-audit b{color:#a21535}.fc-case-title{margin:24px 0 14px;font-size:18px}.fc-examples{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.fc-examples article{padding:18px;border:1px solid #ece5e1;border-left:3px solid var(--c);border-radius:4px}.fc-examples span{font-size:12px;color:#8b7d82}.fc-examples h4{margin:8px 0;font-size:19px}.fc-examples p{font-size:14px;line-height:1.7;color:#665e62}.fc-examples a{font-size:13px;color:#a21535;margin-right:16px}
@media(max-width:1100px){.fc-cards{grid-template-columns:repeat(2,1fr)}.fc-grid,.fc-grid.narrow{grid-template-columns:1fr}}
@media(max-width:600px){.fc-sec{padding:20px 16px}.fc-cards,.fc-tiles{grid-template-columns:1fr}.fc-sec>header{flex-wrap:wrap}.fc-tiles strong,.fc-cards strong{font-size:24px}}
.fc-finding{padding:18px 22px;background:#faf6f7;border-left:3px solid var(--c);margin-bottom:20px}.fc-finding strong{font-size:22px;color:var(--c)}.fc-finding p{font-size:14px;line-height:1.8;margin:8px 0 0;color:#665e62}.fc-grants{margin-top:16px;border-top:1px solid #eee5e7}.fc-grants>div{padding:12px 0}.fc-grants b{font-size:13px;color:var(--c)}.fc-grants p{margin:5px 0}.fc-examples h4{overflow-wrap:anywhere;line-height:1.5}@media(max-width:600px){.fc-examples{grid-template-columns:1fr}}

.fc-impact-overview{display:grid;grid-template-columns:1fr 1fr;gap:48px;padding:8px 0 28px;margin-bottom:28px;border-bottom:1px solid #eee7e4;align-items:center}
.fc-eyebrow{font-size:12px;color:var(--c);font-weight:650;letter-spacing:1px}
.fc-impact-message h4{font-size:23px;line-height:1.45;margin:10px 0;color:#232930}
.fc-impact-message p{font-size:14px;line-height:1.85;color:#7a7378;margin:0;max-width:520px}
.fc-share-bars{display:grid;gap:18px}.fc-share-bars>div{display:grid;grid-template-columns:1fr auto;align-items:baseline;gap:8px}
.fc-share-bars span{font-size:13px;color:#665e62}.fc-share-bars strong{font-size:24px;color:var(--c);font-variant-numeric:tabular-nums}.fc-share-bars small{font-size:13px;margin-left:3px}
.fc-share-track{grid-column:1/-1;height:9px;background:#f1ece9;border-radius:8px;overflow:hidden}.fc-share-track i{display:block;height:100%;background:var(--c);border-radius:8px;transition:width .25s ease}
.fc-showcase{display:grid;grid-template-columns:minmax(220px,0.8fr) minmax(0,2fr);gap:28px}
.fc-work-label{font-size:13px;font-weight:650;color:#665e62;padding:0 12px 12px;display:flex;justify-content:space-between}.fc-work-label span{font-weight:400;color:#94888d}
.fc-work-list button{width:100%;display:flex;align-items:flex-start;gap:12px;padding:18px 12px;margin-bottom:8px;border:1px solid transparent;background:#faf8f7;text-align:left;font:inherit;border-radius:6px;cursor:pointer;color:#514b4e;transition:background .2s,border-color .2s}
.fc-work-list button:hover{border-color:#d6c9cd}.fc-work-list button.chosen{background:color-mix(in srgb,var(--c) 7%,white);border-color:color-mix(in srgb,var(--c) 35%,white);color:var(--c)}
.fc-work-list button:focus-visible{outline:2px solid var(--c);outline-offset:2px}.fc-work-index{font-size:12px;opacity:.6;margin-top:3px}.fc-work-text{flex:1;min-width:0}.fc-work-text b{display:block;font-size:15px;line-height:1.65;font-weight:650}.fc-work-text small{display:block;font-size:12px;color:#847a7f;margin-top:9px}.fc-work-arrow{font-size:17px;opacity:.65}
.fc-feature{min-width:0;border:1px solid #e9e1de;border-radius:6px;padding:26px 28px;animation:fcFeatureIn .22s ease}
.fc-feature-heading{display:flex;align-items:flex-start;gap:24px}.fc-feature-heading>div:first-child{flex:1;min-width:0}.fc-feature-heading h4{font-size:24px;line-height:1.5;margin:9px 0;color:#232930}.fc-original-title{font-size:13px;color:#93888d;line-height:1.7;margin:0;overflow-wrap:anywhere}
.fc-cite-number{flex:none;text-align:right;padding:5px 0 0 20px;border-left:1px solid #ece4e1}.fc-cite-number strong{display:block;font-size:36px;line-height:1.2;color:var(--c);font-variant-numeric:tabular-nums}.fc-cite-number span{display:block;font-size:12px;color:#8a7f84;margin-top:8px}
.fc-research-route{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;margin:28px 0;padding:20px 16px 14px;background:#faf8f7;border-radius:4px}.fc-research-route>div{position:relative;min-width:0;padding:18px 12px 0;border-top:2px solid #dfcbd1}.fc-route-dot{position:absolute;top:-6px;left:12px;width:10px;height:10px;border-radius:50%;background:var(--c);box-shadow:0 0 0 4px #faf8f7}.fc-research-route small{font-size:12px;color:#8b7e84}.fc-research-route b{display:block;font-size:20px;color:#4c4147;margin-top:8px;line-height:1.5}.fc-research-route p{font-size:12px;color:#8b7e84;margin:6px 0}
.fc-support-heading{display:flex;justify-content:space-between;align-items:baseline;gap:16px;margin-bottom:10px}.fc-support-heading h5{font-size:14px;margin:0;color:#4c4147;flex:none}.fc-support-heading>span{font-size:12px;line-height:1.6;color:#8a7f84;text-align:right}
.fc-projects details{border-top:1px solid #eee7e4;padding:12px 0}.fc-projects summary{display:flex;align-items:flex-start;gap:14px;cursor:pointer;list-style:none}.fc-projects summary::-webkit-details-marker{display:none}.fc-project-year{font-size:13px;color:var(--c);font-weight:650;padding-top:3px}.fc-project-name{flex:1;font-size:14px;line-height:1.7;color:#51464c}.fc-project-name small{display:block;font-size:12px;color:#93888d;margin-top:3px}.fc-project-toggle{color:#a79b9f}.fc-projects details[open] .fc-project-toggle{transform:rotate(45deg)}.fc-projects details>p{font-size:12px;color:#887a81;padding:8px 14px;margin:10px 0 0;background:#faf8f7;line-height:1.8}.fc-projects details>p b{color:var(--c)}
@keyframes fcFeatureIn{from{opacity:.5;transform:translateY(3px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:1000px){.fc-showcase{grid-template-columns:1fr}.fc-work-list{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.fc-work-label{grid-column:1/-1}.fc-work-list button{margin:0}.fc-impact-overview{gap:24px}}
@media(max-width:600px){.fc-impact-overview{grid-template-columns:1fr}.fc-feature{padding:18px 16px}.fc-feature-heading{flex-direction:column}.fc-cite-number{text-align:left;padding:0;border:0}.fc-feature-heading h4{font-size:21px}.fc-research-route{padding:18px 4px 8px}.fc-research-route>div{padding-left:6px;padding-right:6px}.fc-research-route b{font-size:15px}.fc-support-heading{flex-direction:column;gap:6px}.fc-support-heading>span{text-align:left}}
@media(prefers-reduced-motion:reduce){.fc-feature{animation:none}.fc-share-track i{transition:none}}
</style>
