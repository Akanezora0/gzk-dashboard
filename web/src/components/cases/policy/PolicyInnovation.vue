<script setup>
/* 政策案例一 · 政策实施与技术创新（耀元交付：296 城城市面板 2013—2025 与人工智能产业政策实证分析）
   结构对齐企业案例详情：顶部吸附章节导航 → 各章节白卡；图表点击放大 */
import {ref,computed,onMounted,onBeforeUnmount} from 'vue'
import data from './policy-case-data.json'
import PolicyFigure from './PolicyFigure.vue'

const sections=[['overview','案例概览'],['design','研究设计'],['descriptive','描述性分析'],['results','核心结果'],['dynamics','动态检验'],['chain','产业链差异'],['outlook','不足与展望']]
const activeSec=ref('overview'),zoomed=ref(null)
function go(id){document.getElementById('pi-'+id)?.scrollIntoView({behavior:'smooth',block:'start'})}
let io
onMounted(()=>{io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)activeSec.value=e.target.id.slice(3)}),{rootMargin:'-30% 0px -60% 0px'});sections.forEach(([id])=>{const el=document.getElementById('pi-'+id);el&&io.observe(el)})})
const onKey=e=>{if(e.key==='Escape')zoomed.value=null}
onMounted(()=>document.addEventListener('keydown',onKey))
onBeforeUnmount(()=>{io?.disconnect();document.removeEventListener('keydown',onKey)})

const fig=n=>`/policy-cases/assets/charts/${n}.svg`
const csv=n=>`/policy-cases/data/${n}.csv`

/* 描述性分析：三组图 */
const galleries=[
 {id:'time',label:'时间演进',sub:'政策数量 · 覆盖 · 专利',figs:[
  {f:'policy-evolution',t:'年度政策篇数与评分',c:'柱形为累计和新增政策篇数，折线为新增政策篇均评分；年度新增按累计值差分计算。'},
  {f:'diffusion-patents',t:'政策扩散与关键词专利时间序列',c:'依次为政策覆盖、年度专利总量与分组城市均值；专利总量与城市均值取 ln(1+x)。'}],
  reads:[['政策覆盖继续扩展','2025 年有政策记录的城市增至 <b>155 城</b>，其中 <b>25 城</b>首次出现正值；当年政策净增 <b>628 篇</b>，高于 2024 年的 374 篇。'],
   ['专利计数集中于近年','2023—2025 年分别为 <b>2,238、8,470、12,521 件</b>，占全期 99.75%。']]},
 {id:'space',label:'空间分布',sub:'城市政策 · 专利集聚',figs:[
  {f:'city-policy-spatial-themed',t:'城市累计政策的空间分布',c:'统一色阶比较 2018、2025 年城市累计政策篇数与评分；灰色为样本外地区，白色为零值。'},
  {f:'city-patent-spatial-themed',t:'关键词专利产出的城市空间分布',c:'2023—2025 年城市专利数量；柱形比较各年专利最多的十个城市的份额。'}],
  reads:[['城市间政策记录存在差异','2025 年累计政策篇数居前的城市为<b>北京（156）、上海（149）、重庆（114）</b>，累计评分同时受政策数量与单篇评分影响。'],
   ['专利集中度回落','当年前十城市份额从 2023 年的 <b>80.8%</b> 变为 2024 年的 <b>79.3%</b> 和 2025 年的 <b>73.3%</b>，专利产出向更多城市扩散。']]},
 {id:'structure',label:'省域与产业链',sub:'省域政策 · 环节变化',figs:[
  {f:'province-policy-spatial-themed',t:'按省域汇总的样本城市政策',c:'按省域汇总省内样本城市的累计政策篇数与评分，对比 2018 年和 2025 年。'},
  {f:'chain-trends',t:'产业链分段政策与关键词专利',c:'按上游、中游、下游展示累计政策篇数与年度专利总量；专利总量取 ln(1+x)。'}],
  reads:[['省域政策规模各异','政策数量与评分按省内样本城市汇总，各地区精确数值见下方分地区统计。'],
   ['各产业链环节同时受到政策关注','截至 2025 年，上、中、下游累计政策记录分别为 <b>681、839、1,356 篇</b>，同一政策可同时涉及多个环节。']]}]
const gallery=ref(galleries[0])

/* 分地区与省域 */
const R=data.regional
const pct=v=>(v*100).toFixed(2)+'%'
const nf=v=>Number(v).toLocaleString('en-US')
const east=R.regions.find(r=>r.region==='东部')
const provMetric=ref('policy')
const provRows=computed(()=>{const k=provMetric.value==='policy'?'policyCumulative2025':'patents2025';return R.rankings[k].slice(0,6)})
const provUnit=computed(()=>provMetric.value==='policy'?'篇':'件')
const provTop5=computed(()=>R.concentration[provMetric.value==='policy'?'policyCumulative2025':'patents2025'].top5)
const regionOf=Object.fromEntries(R.regions.flatMap(r=>r.provinces.map(p=>[p,r.region])))
const showAll=ref(false)

/* 产业链 */
const P=data.patentChainTotals
const chainParts=[['上游',P.upstream,'#506f84'],['中游',P.midstream,'#c9a26a'],['下游',P.downstream,'#a21535']]
</script>

<template><div class="pi">
 <header class="zc-top">
  <div class="zc-id"><span class="zc-logo" aria-hidden="true">政</span><div><h3>政策实施与技术创新</h3><p class="zc-entity">政策文本 × 专利数据 · 296 城 · 2013—2025 年</p></div></div>
  <nav class="zc-nav" aria-label="案例章节"><button v-for="([id,l],i) in sections" :key="id" :class="{on:activeSec===id}" @click="go(id)"><i>{{String(i+1).padStart(2,'0')}}</i>{{l}}</button></nav>
 </header>

 <!-- 01 案例概览 -->
 <section id="pi-overview" class="zc-sec">
  <div class="zc-hero">
   <div class="pi-hero-copy">
    <p class="zc-lead">利用人工智能和大模型政策文本以及城市专利面板数据，评价政策对<b>技术创新</b>的影响效应：政策实施后，样本城市的关键词专利产出显著提升。</p>
    <div class="pi-key">
     <div class="pi-key-main"><span>政策实施的影响效应</span><strong>0.160<sup>***</sup></strong><em>95% 置信区间 [0.076, 0.244] · 1% 水平显著</em></div>
     <p>二元政策实施模型得到正向估计：相关政策有助于提高样本城市的关键词专利产出，对技术创新具有促进作用。</p>
    </div>
    <div class="zc-metrics four">
     <div><strong>296<small>城</small></strong><span>城市样本</span></div>
     <div><strong>13<small>年</small></strong><span>2013—2025</span></div>
     <div><strong>3,848<small>个</small></strong><span>城市年度观测</span></div>
     <div><strong>3,222<small>个</small></strong><span>基准回归观测</span></div>
    </div>
   </div>
   <div class="zc-chain" aria-label="研究设计：政策文本结构化、城市年度匹配、测度技术创新、识别政策影响">
    <div v-for="(s,i) in [{k:'政策文本',n:[['政策文本结构化','出台年份 · 作用地域'],['累计篇数与评分','大语言模型量化评分']]},{k:'面板构建',n:[['城市年度匹配','城市代码 × 年份'],['测度技术创新','关键词专利 · 上中下游']]},{k:'效应识别',n:[['双向固定效应','城市聚类标准误'],['动态双重差分','CSDID · 安慰剂 · 替代样本']]}]" :key="s.k" class="zc-stage">
     <span class="zc-stage-k">{{s.k}}</span>
     <div class="zc-stage-n"><template v-for="(n,j) in s.n" :key="n[0]"><i v-if="j" aria-hidden="true">→</i><div><b>{{n[0]}}</b><small>{{n[1]}}</small></div></template></div>
     <span v-if="i<2" class="zc-down">{{['296 城连续观察面板','政策实施前后专利变化'][i]}}</span>
    </div>
   </div>
  </div>
 </section>

 <!-- 02 研究设计 -->
 <section id="pi-design" class="zc-sec">
  <header class="zc-sh"><b>02</b><div><h4>研究设计：把政策文本接入城市创新面板</h4></div></header>
  <div class="pi-design">
   <div class="pi-def">
    <h5>如何定义政策实施</h5>
    <p>从某城市累计目标政策篇数首次为正的当年起，政策实施指标 <b>D = 1</b>，此前为 0。利用各城市首次出台政策的时间差异，比较政策实施前后的专利变化。</p>
    <dl class="pi-set"><div><dt>匹配单位</dt><dd>城市 × 年份</dd></div><div><dt>被解释变量</dt><dd>关键词专利件数，取 ln(1+x)</dd></div><div><dt>控制变量</dt><dd>五项城市层面控制</dd></div><div><dt>固定效应</dt><dd>城市、年份</dd></div><div><dt>标准误</dt><dd>按城市聚类</dd></div></dl>
   </div>
   <div class="pi-formula">
    <div class="pi-eq" aria-label="回归模型：ln(1+专利) = β D + γ X + α + λ + ε">
     <span>ln(1 + 专利<sub>it</sub>)</span><span class="op">=</span><span><i>β</i> D<sub>it</sub></span><span class="op">+</span><span><i>γ</i> X<sub>it</sub></span><span class="op">+</span><span><i>α</i><sub>i</sub></span><span class="op">+</span><span><i>λ</i><sub>t</sub></span><span class="op">+</span><span><i>ε</i><sub>it</sub></span>
    </div>
    <dl class="pi-sym">
     <div><dt>专利<sub>it</sub></dt><dd>城市 i 在年份 t 的关键词专利件数</dd></div>
     <div><dt>D<sub>it</sub></dt><dd>政策实施指标，<i>β</i> 为政策效应</dd></div>
     <div><dt>X<sub>it</sub></dt><dd>五项控制变量，<i>γ</i> 为对应系数</dd></div>
     <div><dt><i>α</i><sub>i</sub> · <i>λ</i><sub>t</sub></dt><dd>城市与年份固定效应</dd></div>
     <div><dt><i>ε</i><sub>it</sub></dt><dd>误差项</dd></div>
    </dl>
   </div>
  </div>
 </section>

 <!-- 03 描述性分析 -->
 <section id="pi-descriptive" class="zc-sec">
  <header class="zc-sh"><b>03</b><div><h4>描述性分析：政策扩散与创新产出的时空分布</h4></div></header>
  <div class="pi-kpi">
   <div><span>截至 2025 年累计政策</span><strong>1,913<small>篇</small></strong><em>2025 年净增 628 篇</em></div>
   <div><span>有政策记录的城市</span><strong>155<small>/ 296 城</small></strong><em>覆盖率 52.36%</em></div>
   <div><span>2013—2025 年关键词专利</span><strong>23,287<small>件</small></strong><em>2025 年度 12,521 件</em></div>
   <div><span>2025 年前十城市专利占比</span><strong>73.3<small>%</small></strong><em>2023 年为 80.8%</em></div>
  </div>
  <div class="zc-seg" role="tablist" aria-label="描述性分析组图"><button v-for="g in galleries" :key="g.id" role="tab" :aria-selected="gallery.id===g.id" :class="{on:gallery.id===g.id}" @click="gallery=g"><b>{{g.label}}</b><small>{{g.sub}}</small></button></div>
  <div :key="gallery.id" class="pane-swap">
   <div class="pi-figs"><PolicyFigure v-for="f in gallery.figs" :key="f.f" :src="fig(f.f)" :title="f.t" :caption="f.c" @zoom="zoomed=$event"/></div>
   <div class="pi-reads"><div v-for="r in gallery.reads" :key="r[0]"><h5>{{r[0]}}</h5><p v-html="r[1]"></p></div></div>
  </div>

  <div class="pi-sub"><h5>分地区统计</h5><span>296 个样本城市；政策为 2025 年累计值，专利为 2025 年年度值</span><a :href="csv('four-region-summary')" download>下载 CSV</a></div>
  <div class="pi-table"><table>
   <thead><tr><th>地区</th><th class="r">样本城市</th><th>有政策城市 · 覆盖率</th><th>累计政策 · 样本份额</th><th>年度专利 · 样本份额</th></tr></thead>
   <tbody><tr v-for="r in R.regions" :key="r.region"><th>{{r.region}}</th><td class="r">{{r.sampleCityCount}} 城</td>
    <td><b>{{r.citiesWithPolicy2025}} 城</b><small>{{pct(r.citiesWithPolicy2025Share)}}</small></td>
    <td><div class="pi-cellbar"><b>{{nf(r.policyCumulative2025)}} 篇</b><small>{{pct(r.policyCumulative2025Share)}}</small><i><em :style="{width:r.policyCumulative2025Share*100+'%'}"></em></i></div></td>
    <td><div class="pi-cellbar blue"><b>{{nf(r.patents2025)}} 件</b><small>{{pct(r.patents2025Share)}}</small><i><em :style="{width:r.patents2025Share*100+'%'}"></em></i></div></td></tr></tbody>
   <tfoot><tr><th>合计</th><td class="r">296 城</td><td>155 城 · 52.36%</td><td>1,913 篇</td><td>12,521 件</td></tr></tfoot>
  </table></div>
  <p class="pi-reading"><b>政策与专利均呈空间集中：</b>东部占样本累计政策的 <b>{{pct(east.policyCumulative2025Share)}}</b>，占 2025 年度专利的 <b>{{pct(east.patents2025Share)}}</b>；该地区 {{east.sampleCityCount}} 个样本城市中，{{east.citiesWithPolicy2025}} 城已有政策记录。</p>

  <div class="pi-sub"><h5>省域分布</h5><span>前六省级单元 · 前五合计 {{nf(provTop5.count)}} {{provUnit}}，占样本 {{pct(provTop5.share)}}</span>
   <div class="pi-mini-seg" role="group" aria-label="省域指标"><button :class="{on:provMetric==='policy'}" @click="provMetric='policy'">累计政策</button><button :class="{on:provMetric==='patent'}" @click="provMetric='patent'">2025 年专利</button></div></div>
  <div class="pi-prov" :class="{blue:provMetric==='patent'}">
   <div v-for="r in provRows" :key="r.province"><span>{{r.province}}</span><i><em :style="{width:r.value/provRows[0].value*100+'%'}"></em></i><b>{{nf(r.value)}} {{provUnit}}</b><small>{{pct(r.share)}}</small></div>
  </div>
  <button class="pi-more" :aria-expanded="showAll" @click="showAll=!showAll">{{showAll?'收起':'展开'}} 31 省完整统计 <span>{{showAll?'−':'+'}}</span></button>
  <div v-if="showAll" class="pi-all pane-swap">
   <p class="pi-reading"><b>结果解读：</b>广东样本城市的累计政策合计 <b>339 篇</b>，位居首位；北京 2025 年专利 <b>3,028 件</b>，数量最多。两类指标的前列地区不同，反映政策记录规模与专利产出分布的差异。</p>
   <div class="pi-table"><table>
    <thead><tr><th>省级单元</th><th>地区</th><th class="r">样本城市</th><th class="r">有政策城市</th><th class="r">2025 累计政策（篇）</th><th class="r">2025 专利（件）</th><th class="r">2013—2025 专利（件）</th></tr></thead>
    <tbody><tr v-for="r in R.provinces" :key="r.province"><th>{{r.province}}</th><td>{{regionOf[r.province]}}</td><td class="r">{{r.sampleCityCount}}</td><td class="r">{{r.citiesWithPolicy2025}}</td><td class="r">{{nf(r.policyCumulative2025)}}</td><td class="r">{{nf(r.patents2025)}}</td><td class="r">{{nf(r.patents2013to2025)}}</td></tr></tbody>
   </table></div>
   <dl class="pi-map"><div v-for="r in R.regions" :key="r.region"><dt>{{r.region}}</dt><dd>{{r.provinces.join('、')}}</dd></div></dl>
   <a class="pi-dl" :href="csv('regional-summary')" download>下载完整省域统计 CSV</a>
  </div>
 </section>

 <!-- 04 核心结果 -->
 <section id="pi-results" class="zc-sec">
  <header class="zc-sh"><b>04</b><div><h4>核心结果：政策实施后的创新响应为正</h4></div><a class="pi-dl" :href="csv('regression-results')" download>下载结果数据</a></header>
  <div class="pi-split">
   <div class="pi-copy">
    <span class="zc-tag">双向固定效应</span>
    <h5>替代样本下正向估计仍然保留，结果稳健</h5>
    <p>纳入五项控制后，政策实施系数为 <b>0.160</b>，在 1% 水平显著。剔除四个直辖市、剔除 2025 年后，估计系数分别为 <b>0.162</b> 和 <b>0.137</b>，置信区间均高于零。</p>
    <p>两种样本调整下估计方向和显著性保持一致，主要结果对样本范围的变化较为稳定。</p>
   </div>
   <PolicyFigure :src="fig('baseline-robustness')" title="基准与稳健性估计" caption="圆点为政策实施系数，横线为 95% 置信区间，虚线为零值。" @zoom="zoomed=$event"/>
  </div>
  <details class="pi-details"><summary>基准回归与政策强度结果<span aria-hidden="true">+</span></summary>
   <div class="pi-details-body">
    <p>二元模型观察“是否实施政策”，数量和评分强度模型进一步观察政策积累程度。二元模型的政策实施系数在 1% 水平显著，支持政策实施促进创新；两项强度交互项也为正，分别在 5% 和 10% 水平显著，政策积累与创新响应存在正向联系。</p>
    <p>从政策实施前的情况看，二元模型的事前联合检验在 5% 水平未拒绝，两种强度模型存在显著事前差异，强度结果作为补充关联证据。</p>
    <div class="pi-table"><table>
     <thead><tr><th>政策变量</th><th class="r">系数</th><th class="r">城市聚类标准误</th><th class="r">事前联合检验 p 值</th><th>结果解读</th></tr></thead>
     <tbody><tr><th>二元政策实施 D</th><td class="r num">0.160***</td><td class="r">0.043</td><td class="r">0.10059</td><td>5% 水平未拒绝事前联合检验</td></tr>
      <tr><th>D × 数量强度</th><td class="r num">0.072**</td><td class="r">0.033</td><td class="r">0.00281</td><td>存在显著事前差异</td></tr>
      <tr><th>D × 评分强度</th><td class="r num">0.074*</td><td class="r">0.042</td><td class="r">0.00259</td><td>存在显著事前差异</td></tr></tbody>
    </table></div>
    <p class="pi-foot">每个规格 N = 3,222，城市数 296；*、**、*** 对应 10%、5%、1% 显著性水平。</p>
   </div>
  </details>
 </section>

 <!-- 05 动态检验 -->
 <section id="pi-dynamics" class="zc-sec">
  <header class="zc-sh"><b>05</b><div><h4>动态检验：创新响应何时出现</h4><p>2013—2025 年观察期，对照组包含始终未发文及比较时点尚未发文的城市。</p></div></header>
  <div class="pi-split wide">
   <PolicyFigure :src="fig('csdid-event-study-themed')" title="分组时期双重差分 · CSDID" caption="三角形为各期估计值，竖线为 95% 置信区间；−1 为基期，≤−5 与 ≥+5 合并两端时期。" @zoom="zoomed=$event"/>
   <div class="pi-phases">
    <div><span class="zc-tag soft">政策前</span><h5>未拒绝事前联合检验</h5><p>事前联合检验 p = <b>0.442</b>，为平行趋势假设提供支持。</p></div>
    <div><span class="zc-tag">政策后</span><h5>较长期合并期呈正向响应</h5><p>0—4 期置信区间均跨零；≥+5 合并期置信区间高于零，创新响应需要时间积累。</p></div>
   </div>
  </div>
  <div class="pi-checks">
   <details class="pi-details"><summary><span><b>传统事件研究</b><small>二元政策事前检验 p = 0.10059</small></span><span aria-hidden="true">+</span></summary>
    <div class="pi-details-body"><p>传统二元政策模型在政策后的估计逐渐升高，创新响应随时间推移逐步显现。政策前联合检验 p = <b>0.10059</b>，在 5% 水平未拒绝，支持政策前走势可比。</p>
     <PolicyFigure :src="fig('twfe-event-study-themed')" title="传统双向固定效应事件研究" caption="以发文前一年为参照，圆点为估计值，误差线为 95% 置信区间。" @zoom="zoomed=$event"/></div></details>
   <details class="pi-details"><summary><span><b>随机置换安慰剂</b><small>二元政策经验 p = 0.002</small></span><span aria-hidden="true">+</span></summary>
    <div class="pi-details-body"><p>随机置换处理安排，三个模型各 500 次有效置换，二元、篇数、评分模型经验 p 值分别为 0.002、0.040、0.100。随机打乱政策安排后很少出现与二元模型实际结果同样极端的估计，对主结果形成支持。</p>
     <PolicyFigure :src="fig('placebo-test-themed')" title="随机置换安慰剂检验" caption="直方图为 500 次随机置换的系数分布，虚线为实际估计，灰线为零值。" @zoom="zoomed=$event"/></div></details>
  </div>
 </section>

 <!-- 06 产业链差异 -->
 <section id="pi-chain" class="zc-sec">
  <header class="zc-sh"><b>06</b><div><h4>产业链差异：沿产业链观察政策与创新的联系</h4></div></header>
  <div class="pi-split">
   <PolicyFigure :src="fig('chain-effects')" title="各环节政策与总体关键词专利" caption="圆点与横线为系数及 95% 置信区间；因变量均为总体关键词专利。" @zoom="zoomed=$event"/>
   <div class="pi-copy">
    <h5>分环节政策均得到正向估计</h5>
    <p>上游、中游、下游政策对应的总体关键词专利估计系数分别为 <b>0.541、0.363、0.257</b>，均在 1% 水平显著。三个环节的政策均与城市创新的提升相联系，上游政策的点估计较高。</p>
    <button class="zc-link" @click="zoomed={src:fig('chain-original-themed'),title:'产业链政策和专利的分项估计'}">查看完整分项估计图 ↗</button>
    <dl class="pi-criteria"><div><dt>上游</dt><dd>算力硬件、计算基础设施、训练数据与语料</dd></div><div><dt>中游</dt><dd>模型架构、训练、微调、推理优化与评测</dd></div><div><dt>下游</dt><dd>问答、检索增强、智能体和行业应用</dd></div></dl>
   </div>
  </div>
  <div class="pi-spill">
   <h5>产业链溢出：从跨环节关联理解政策传导</h5>
   <p class="pi-spill-lead">一类环节政策的正向关联也出现在其他环节的专利产出中，可从技术供给、成果转化和需求反馈理解溢出路径。</p>
   <div class="pi-spill-grid">
    <article><span>上游 · 供给传导</span><h6>上游支持向中下游扩散</h6><p>上游政策对应的中游、下游专利均得到正向估计，与创新产出的联系延伸到后续环节。</p><p class="mech"><b>传导机制</b>研发条件与技术供给改善，为中下游提供技术支撑，降低后续研发门槛。</p></article>
    <article><span>中游 · 承接扩散</span><h6>中游连接上下游创新</h6><p>中游政策与上游、下游专利均呈正向关联，呈现中游与产业链两端的创新联动。</p><p class="mech"><b>传导机制</b>技术整合与成果转化承接上游供给，推动技术向下游应用扩散。</p></article>
    <article><span>下游 · 需求反馈</span><h6>下游需求向前端反馈</h6><p>下游政策与中游专利的正向联系较清晰，与上游专利的关联相对较弱。</p><p class="mech"><b>传导机制</b>需求与应用场景拓展推动中游技术改进，并向上游研发提出新需求。</p></article>
   </div>
  </div>
  <div class="pi-comp">
   <div><h5>关键词专利主要分布在下游</h5><p>2013—2025 年共 <b>{{nf(P.total)}}</b> 件，下游占 <b>81.28%</b>，中游次之。</p></div>
   <div><div class="pi-stack"><span v-for="c in chainParts" :key="c[0]" :style="{width:c[1]/P.total*100+'%',background:c[2]}"></span></div>
    <div class="pi-stack-l"><span v-for="c in chainParts" :key="c[0]"><i :style="{background:c[2]}"></i>{{c[0]}} <b>{{nf(c[1])}}</b><small>{{(c[1]/P.total*100).toFixed(2)}}%</small></span></div></div>
  </div>
 </section>

 <!-- 07 不足与展望 -->
 <section id="pi-outlook" class="zc-sec">
  <header class="zc-sh"><b>07</b><div><h4>不足与展望：后续完善方向</h4><p>政策出台与目标专利创新之间具有较稳定的正向联系；政策执行、支持积累与产业链传导将结合更完整的数据继续深化。</p></div></header>
  <div class="pi-outlook">
   <article><b>01</b><h5>数据覆盖与零值核验</h5><p>区分真实零值与未匹配记录，完善近期专利覆盖，核验控制变量的补录、插补与统计口径。</p></article>
   <article><b>02</b><h5>政策执行与评分口径</h5><p>刻画政策执行范围、实际投入与持续落实过程，统一政策文本量化评分的标准、权重与适用口径。</p></article>
   <article><b>03</b><h5>识别设定与传导机制</h5><p>统一并透明呈现关键样本与估计设定，结合技术关联证据检验政策作用与产业链传导机制。</p></article>
  </div>
 </section>

 <Teleport to="body"><div v-if="zoomed" class="pi-lightbox" role="dialog" aria-modal="true" :aria-label="zoomed.title" @click.self="zoomed=null">
  <div class="pi-lb"><header><b>{{zoomed.title}}</b><a :href="zoomed.src" download>下载图表</a><button aria-label="关闭" @click="zoomed=null">×</button></header><div class="pi-lb-body"><img :src="zoomed.src" :alt="zoomed.title"></div></div>
 </div></Teleport>
</div></template>

<style scoped>
.pi{display:flex;flex-direction:column;gap:18px}
/* 与企业案例（智谱）相同的骨架 */
.zc-top{position:sticky;top:77px;z-index:5;display:flex;justify-content:space-between;align-items:center;gap:20px;padding:16px 22px;background:rgba(255,255,255,.96);backdrop-filter:blur(10px);border:1px solid #e6dfdb;border-radius:4px}
.zc-id{display:flex;align-items:center;gap:14px}
.zc-logo{display:grid;place-items:center;flex:none;width:44px;height:44px;border-radius:4px;background:#a21535;color:#fff;font-size:20px;font-weight:800}
.zc-id h3{margin:2px 0;font-size:21px;font-weight:750;color:#232930}
.zc-entity{margin:0;font-size:12px;color:#9a9296}
.zc-nav{display:flex;gap:2px;padding:4px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.zc-nav button{display:inline-flex;align-items:baseline;gap:5px;padding:7px 10px;border:0;border-radius:3px;background:none;font:inherit;font-size:13.5px;font-weight:600;color:#6a6468;cursor:pointer;white-space:nowrap;transition:background .18s,color .18s}
.zc-nav button:hover{color:#a21535}
.zc-nav i{font-style:normal;font-size:11px;color:#b0a6a9}
.zc-nav button.on{background:#a21535;color:#fff}.zc-nav button.on i{color:#f2c4cc}
.zc-sec{scroll-margin-top:170px;padding:26px 28px 28px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.zc-sh{display:flex;align-items:flex-start;gap:14px;margin-bottom:18px}
.zc-sh>b{font-size:15px;font-weight:800;color:#a21535;padding-top:4px}
.zc-sh>div{flex:1}
.zc-sh h4{margin:0;font-size:21px;font-weight:750;color:#232930}
.zc-sh p{margin:4px 0 0;font-size:13.5px;color:#7a7378;line-height:1.6}
.zc-hero{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:28px;align-items:stretch}
.zc-lead{margin:0 0 18px;font-size:18px;font-weight:600;line-height:1.8;color:#2f2b2d}
.zc-lead b{color:#a21535}
.zc-metrics{display:grid;grid-template-columns:repeat(2,1fr);border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.zc-metrics.four{grid-template-columns:repeat(4,1fr)}
.zc-metrics>div{padding:12px 16px;display:flex;flex-direction:column}
.zc-metrics>div+div{border-left:1px solid #ece5e1}
.zc-metrics strong{font-size:24px;font-weight:800;color:#2f2b2d;line-height:1.25;font-variant-numeric:tabular-nums}
.zc-metrics strong small{margin-left:3px;font-size:12.5px;font-weight:600;color:#7a7378}
.zc-metrics span{font-size:12.5px;color:#7a7378}
.zc-chain{position:relative;display:flex;flex-direction:column;justify-content:center;gap:4px;padding:24px 26px;border-radius:4px;background:linear-gradient(140deg,#8c1c32,#5f1326);color:#fff;overflow:hidden}
.zc-chain::before{content:"";position:absolute;inset:0;background-image:linear-gradient(#ffffff08 1px,transparent 1px),linear-gradient(90deg,#ffffff08 1px,transparent 1px);background-size:28px 28px;pointer-events:none}
.zc-stage{position:relative;display:grid;grid-template-columns:72px 1fr;gap:12px;align-items:center}
.zc-stage-k{font-size:12px;letter-spacing:1px;color:#f0c6d0}
.zc-stage-n{display:flex;flex-wrap:wrap;gap:8px;align-items:center}
.zc-stage-n i{font-style:normal;color:#e6a9b7}
.zc-stage-n>div{padding:8px 12px;border:1px solid #ffffff3d;border-radius:3px;background:#ffffff12;transition:background .2s}
.zc-stage-n>div:hover{background:#ffffff24}
.zc-stage-n b{display:block;font-size:13.5px}
.zc-stage-n small{display:block;font-size:11px;opacity:.75}
.zc-stage:last-child .zc-stage-n>div:first-child{background:#fff4f2;color:#7b2236;border-color:#fff4f2}
.zc-down{grid-column:2;margin:6px 0 8px;font-size:11.5px;color:#e3b5c1}
.zc-down::before{content:"↓ "}
.zc-seg{display:inline-flex;margin-bottom:16px;border:1px solid #e3dad6;border-radius:3px;overflow:hidden}
.zc-seg button{display:flex;flex-direction:column;align-items:flex-start;padding:9px 20px;border:0;border-left:1px solid #e3dad6;background:#fff;font:inherit;cursor:pointer;text-align:left;transition:background .18s}
.zc-seg button:first-child{border-left:0}
.zc-seg button:hover:not(.on){background:#fcf7f8}
.zc-seg b{font-size:15px;color:#2f2b2d}.zc-seg small{font-size:12px;color:#8a8286}
.zc-seg button.on{background:#a21535}.zc-seg button.on b,.zc-seg button.on small{color:#fff}
.zc-tag{display:inline-block;padding:3px 9px;border:1px solid #e9c3cb;border-radius:2px;background:#fff7f8;font-size:12px;color:#a21535}
.zc-tag.soft{border-color:#e3dad6;background:#f8f5f4;color:#6a6468}
.zc-link{margin-top:6px;padding:0;border:0;background:none;font:inherit;font-size:13.5px;font-weight:600;color:#a21535;cursor:pointer}
/* 概览 */
.pi-hero-copy{display:flex;flex-direction:column}
.pi-key{display:grid;grid-template-columns:auto 1fr;gap:22px;align-items:center;margin-bottom:14px;padding:16px 20px;border:1px solid #efd6db;border-radius:4px;background:#fdf8f9}
.pi-key-main span{display:block;font-size:12.5px;color:#7a7378}
.pi-key-main strong{display:block;font-size:42px;font-weight:800;line-height:1.1;color:#a21535;font-variant-numeric:tabular-nums}
.pi-key-main sup{font-size:18px;margin-left:2px}
.pi-key-main em{font-style:normal;font-size:12px;color:#8a8286}
.pi-key p{margin:0;font-size:13.5px;line-height:1.75;color:#4b4649}
/* 研究设计 */
.pi-design{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:20px;align-items:stretch}
.pi-def{padding:20px 22px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.pi-def h5,.pi-copy h5,.pi-reads h5,.pi-phases h5,.pi-spill h5,.pi-comp h5,.pi-outlook h5{margin:0 0 8px;font-size:16.5px;font-weight:750;color:#232930}
.pi-def p{margin:0;font-size:14.5px;line-height:1.85;color:#4b4649}
.pi-def b{color:#a21535}
.pi-set{margin:16px 0 0;border-top:1px solid #ece5e1}
.pi-set div{display:grid;grid-template-columns:86px 1fr;gap:10px;padding:8px 0;border-bottom:1px dashed #e8e0dd;font-size:13.5px}
.pi-set dt{color:#8a8286}.pi-set dd{margin:0;font-weight:600;color:#2f2b2d}
.pi-formula{display:flex;flex-direction:column;gap:14px;padding:20px 22px;border:1px solid #ece5e1;border-radius:4px}
.pi-eq{display:flex;flex-wrap:wrap;justify-content:center;align-items:baseline;gap:6px 10px;padding:18px 12px;border-radius:4px;background:#faf6f5;font-family:"Cambria Math","STIX Two Math","Times New Roman",serif;font-size:21px;color:#2f2b2d}
.pi-eq .op{color:#a21535}
.pi-eq sub,.pi-sym sub{font-size:.62em}
.pi-sym{display:grid;grid-template-columns:1fr;gap:0;margin:0;border-top:1px solid #ece5e1}
.pi-sym div{display:grid;grid-template-columns:96px 1fr;gap:10px;align-items:baseline;padding:8px 0;border-bottom:1px dashed #e8e0dd}
.pi-sym dt{font-family:"Cambria Math","Times New Roman",serif;font-size:15.5px;color:#a21535}
.pi-sym dd{margin:0;font-size:13px;color:#5d575b}
/* 指标条 */
.pi-kpi{display:grid;grid-template-columns:repeat(4,1fr);margin-bottom:20px;border:1px solid #ece5e1;border-radius:4px}
.pi-kpi>div{position:relative;padding:16px 20px}
.pi-kpi>div+div{border-left:1px solid #ece5e1}
.pi-kpi>div::before{content:"";position:absolute;top:-1px;left:20px;width:30px;height:3px;border-radius:2px;background:#a21535;transition:width .45s}
.pi-kpi>div:hover::before{width:54px}
.pi-kpi span{display:block;font-size:12.5px;color:#7a7378}
.pi-kpi strong{display:block;margin:2px 0;font-size:27px;font-weight:800;color:#2f2b2d;font-variant-numeric:tabular-nums}
.pi-kpi strong small{margin-left:3px;font-size:13px;font-weight:600;color:#7a7378}
.pi-kpi em{font-style:normal;font-size:12px;color:#9a9296}
/* 图组 */
.pi-figs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}
.pi-reads{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:16px}
.pi-reads>div{padding:14px 18px;border-radius:4px;background:#fcfaf9;border:1px solid #f0e9e6}
.pi-reads h5{font-size:15px;margin-bottom:4px}
.pi-reads p,.pi-copy p,.pi-phases p,.pi-details-body p{margin:0;font-size:14px;line-height:1.85;color:#4b4649}
.pi-reads :deep(b),.pi-copy b,.pi-phases b,.pi-reading b,.pi-details-body b,.pi-comp b{color:#a21535}
/* 地区 */
.pi-sub{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin:30px 0 12px;padding-top:22px;border-top:1px solid #f0e9e6}
.pi-sub h5{margin:0;font-size:17px;font-weight:750;color:#232930}
.pi-sub>span{font-size:13px;color:#8a8286}
.pi-sub a,.pi-dl{margin-left:auto;font-size:13px;font-weight:600;color:#a21535;text-decoration:none}
.zc-sh .pi-dl{flex:none;padding-top:6px}
.pi-table{overflow-x:auto;border:1px solid #ece5e1;border-radius:4px}
.pi-table table{width:100%;border-collapse:collapse;min-width:640px;font-size:14px}
.pi-table th,.pi-table td{padding:11px 16px;text-align:left;border-bottom:1px solid #f2ecea;white-space:nowrap}
.pi-table thead th{font-size:12.5px;font-weight:650;color:#7a7378;background:#faf7f6}
.pi-table tbody th{font-weight:700;color:#2f2b2d}
.pi-table tbody tr{transition:background .15s}.pi-table tbody tr:hover{background:#fcf7f8}
.pi-table tfoot th,.pi-table tfoot td{font-size:13px;color:#6a6468;background:#faf7f6;border-bottom:0}
.pi-table .r{text-align:right;font-variant-numeric:tabular-nums}
.pi-table .num{font-weight:700;color:#a21535}
.pi-table td b{font-weight:700;color:#2f2b2d}
.pi-table td small{margin-left:8px;font-size:12px;color:#9a9296}
.pi-cellbar{display:grid;grid-template-columns:auto 1fr;gap:2px 8px;align-items:baseline;min-width:170px}
.pi-cellbar i{grid-column:1/-1;height:5px;border-radius:3px;background:#f3eeeb;overflow:hidden}
.pi-cellbar em{display:block;height:100%;background:#a21535}
.pi-cellbar.blue em{background:#506f84}
.pi-reading{margin:12px 0 0;font-size:14px;line-height:1.8;color:#4b4649}
.pi-mini-seg{display:inline-flex;margin-left:auto;border:1px solid #e3dad6;border-radius:3px;overflow:hidden}
.pi-mini-seg button{padding:5px 14px;border:0;background:#fff;font:inherit;font-size:13px;color:#5d575b;cursor:pointer}
.pi-mini-seg button+button{border-left:1px solid #e3dad6}
.pi-mini-seg button.on{background:#a21535;color:#fff}
.pi-prov{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 36px}
.pi-prov>div{display:grid;grid-template-columns:96px 1fr auto 58px;gap:12px;align-items:center;font-size:14px}
.pi-prov span{color:#2f2b2d}
.pi-prov i{height:7px;border-radius:4px;background:#f3eeeb;overflow:hidden}
.pi-prov em{display:block;height:100%;background:#a21535;transition:width .5s}
.pi-prov.blue em{background:#506f84}
.pi-prov b{font-variant-numeric:tabular-nums;color:#2f2b2d}
.pi-prov small{text-align:right;font-size:12px;color:#9a9296}
.pi-more{display:flex;justify-content:space-between;width:100%;margin-top:18px;padding:12px 16px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9;font:inherit;font-size:14px;font-weight:600;color:#4b4649;cursor:pointer}
.pi-more:hover{border-color:#d9b3bd;color:#a21535}
.pi-all{display:flex;flex-direction:column;gap:14px;margin-top:14px}
.pi-map{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 24px;margin:0}
.pi-map div{display:grid;grid-template-columns:44px 1fr;gap:8px;font-size:13px}
.pi-map dt{font-weight:700;color:#a21535}.pi-map dd{margin:0;color:#5d575b}
/* 结果 */
.pi-split{display:grid;grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:24px;align-items:center}
.pi-split.wide{grid-template-columns:minmax(0,1.35fr) minmax(0,.65fr)}
.pi-copy{display:flex;flex-direction:column;gap:10px;align-items:flex-start}
.pi-copy h5{margin:4px 0 0;font-size:18px}
.pi-details{margin-top:18px;border:1px solid #ece5e1;border-radius:4px;background:#fff}
.pi-details summary{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:13px 18px;font-size:14.5px;font-weight:650;color:#2f2b2d;cursor:pointer;list-style:none;transition:color .18s}
.pi-details summary::-webkit-details-marker{display:none}
.pi-details summary:hover{color:#a21535}
.pi-details summary>span:last-child{font-size:18px;font-weight:400;color:#a21535}
.pi-details[open] summary>span:last-child{transform:rotate(45deg)}
.pi-details summary small{display:block;font-size:12.5px;font-weight:500;color:#8a8286}
.pi-details-body{display:flex;flex-direction:column;gap:12px;padding:4px 18px 18px;border-top:1px solid #f2ecea;padding-top:14px}
.pi-foot{font-size:12.5px!important;color:#8a8286!important}
.pi-phases{display:flex;flex-direction:column;gap:14px}
.pi-phases>div{padding:16px 18px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.pi-phases h5{margin:8px 0 6px}
.pi-checks{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;align-items:start}
.pi-checks .pi-details{margin-top:18px}
/* 产业链 */
.pi-criteria{display:flex;flex-direction:column;gap:0;width:100%;margin:8px 0 0;border-top:1px solid #f0e9e6}
.pi-criteria div{display:grid;grid-template-columns:44px 1fr;gap:10px;padding:9px 0;border-bottom:1px solid #f0e9e6;font-size:13.5px}
.pi-criteria dt{font-weight:750;color:#a21535}.pi-criteria dd{margin:0;color:#4b4649}
.pi-spill{margin-top:24px;padding-top:22px;border-top:1px solid #f0e9e6}
.pi-spill-lead{margin:0 0 14px;font-size:14px;color:#5d575b}
.pi-spill-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.pi-spill-grid article{position:relative;padding:18px 20px;border:1px solid #ece5e1;border-radius:4px;background:#fff;transition:transform .3s,box-shadow .3s,border-color .2s}
.pi-spill-grid article::before{content:"";position:absolute;top:-1px;left:20px;width:30px;height:3px;border-radius:2px;background:#a21535;transition:width .45s}
.pi-spill-grid article:hover{transform:translateY(-3px);border-color:#e7c5cc;box-shadow:0 16px 28px -22px rgba(80,20,35,.5)}
.pi-spill-grid article:hover::before{width:54px}
.pi-spill-grid span{font-size:12px;font-weight:650;color:#a21535}
.pi-spill-grid h6{margin:4px 0 8px;font-size:15.5px;font-weight:750;color:#232930}
.pi-spill-grid p{margin:0;font-size:13.5px;line-height:1.75;color:#4b4649}
.pi-spill-grid .mech{margin-top:10px;padding-top:10px;border-top:1px dashed #ece5e1;color:#6a6468}
.pi-spill-grid .mech b{display:block;font-size:12px;color:#8a8286;margin-bottom:2px}
.pi-comp{display:grid;grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:24px;align-items:center;margin-top:18px;padding:18px 20px;border-radius:4px;background:#fcfaf9;border:1px solid #f0e9e6}
.pi-comp p{margin:0;font-size:13.5px;color:#5d575b}
.pi-stack{display:flex;height:14px;border-radius:3px;overflow:hidden;gap:2px}
.pi-stack-l{display:flex;justify-content:space-between;margin-top:8px;font-size:13px;color:#5d575b}
.pi-stack-l i{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:5px}
.pi-stack-l b{margin-left:4px;color:#2f2b2d}.pi-stack-l small{margin-left:6px;color:#9a9296}
/* 展望 */
.pi-outlook{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.pi-outlook article{padding:20px 22px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.pi-outlook b{font-size:14px;font-weight:800;color:#a21535}
.pi-outlook h5{margin:6px 0 8px}
.pi-outlook p{margin:0;font-size:13.5px;line-height:1.8;color:#5d575b}
/* 放大 */
.pi-lightbox{position:fixed;inset:0;z-index:200;display:grid;place-items:center;padding:28px;background:rgba(32,18,22,.55);backdrop-filter:blur(3px)}
.pi-lb{display:flex;flex-direction:column;width:min(1200px,100%);max-height:100%;background:#fff;border-radius:6px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.3)}
.pi-lb header{display:flex;align-items:center;gap:16px;padding:14px 20px;border-bottom:1px solid #ece5e1}
.pi-lb header b{flex:1;font-size:16px;color:#232930}
.pi-lb header a{font-size:13px;font-weight:600;color:#a21535;text-decoration:none}
.pi-lb header button{border:0;background:none;font-size:26px;line-height:1;color:#6a6468;cursor:pointer}
.pi-lb-body{overflow:auto;padding:18px}
.pi-lb-body img{display:block;width:100%;height:auto}
@media(max-width:1100px){.zc-top{position:static;flex-direction:column;align-items:flex-start}.zc-nav{flex-wrap:wrap}.zc-hero,.pi-design,.pi-split,.pi-split.wide,.pi-comp{grid-template-columns:1fr}}
@media(max-width:760px){.zc-sec{padding:20px 16px}.zc-lead{font-size:16px}.zc-stage{grid-template-columns:1fr}.zc-down{grid-column:1}.zc-metrics.four,.pi-kpi{grid-template-columns:1fr 1fr}.zc-metrics.four>div:nth-child(3),.pi-kpi>div:nth-child(3){border-left:0}.zc-metrics.four>div:nth-child(n+3),.pi-kpi>div:nth-child(n+3){border-top:1px solid #ece5e1}.pi-figs,.pi-reads,.pi-checks,.pi-spill-grid,.pi-outlook,.pi-prov,.pi-map,.pi-sym{grid-template-columns:1fr}.pi-key{grid-template-columns:1fr;gap:8px}.zc-seg{display:flex;width:100%}.zc-seg button{flex:1;padding:8px 10px}.pi-prov>div{grid-template-columns:80px 1fr auto}.pi-prov small{display:none}.pi-eq{font-size:17px}}
</style>
