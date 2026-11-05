<script setup>
import {computed,ref,onMounted,onBeforeUnmount} from 'vue'
import {overviewHeadline} from '../helpers/foundationSources'

const props=defineProps({data:Object})
function exploreBelow(){
  document.getElementById('about')?.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'})
}
const mastheadHeight=ref(260)
let mastheadObserver
onMounted(()=>{
  const elements=['.research-header','.research-nav'].map(selector=>document.querySelector(selector)).filter(Boolean)
  const measure=()=>{mastheadHeight.value=elements.reduce((height,element)=>height+element.getBoundingClientRect().height,0)}
  mastheadObserver=new ResizeObserver(measure)
  elements.forEach(element=>mastheadObserver.observe(element))
  measure()
})
onBeforeUnmount(()=>mastheadObserver?.disconnect())
const headline=computed(()=>overviewHeadline(props.data))
const resourceGroups=[
  {num:'01',title:'科研投入与知识成果',items:'基金项目 · 学术论文 · 专利 · 软件著作权',text:'追溯研究由谁支持、形成了哪些成果，以及成果之间的联系。',to:'/data?domain=ai&type=fund'},
  {num:'02',title:'产业活动与应用需求',items:'企业 · 产品 · 招聘 · 经营信息',text:'观察技术进入哪些产品和场景，连接应用需求与产业活动。',to:'/data?domain=ai&type=company'},
  {num:'03',title:'政策环境与发展动态',items:'政策文献 · 产业新闻 · 行业报告',text:'结合时间、地域与作用对象，理解技术发展所处的环境。',to:'/data?domain=ai&type=policy'},
]
const steps=[
  {num:'01',title:'拆解技术',text:'与领域专家一起确定核心技术、分支和关键节点，让一个大领域变成可研究的具体问题。'},
  {num:'02',title:'汇聚资料',text:'围绕技术点整理基金、论文、专利和应用资料，在共同的主题下连接分散的数据。'},
  {num:'03',title:'梳理脉络',text:'结合技术综述与代表成果，看清方法如何演变、知识如何积累、研究如何接续。'},
  {num:'04',title:'开展评估',text:'提取典型案例，比较不同发展路径，结合投入、成果和应用表现开展多维分析。'},
]
const uses=[
  {num:'01',title:'科学与技术价值',question:'哪些研究成为后续创新的基础？',text:'结合代表成果、引用联系和方法复用，观察知识积累、技术突破与跨方向传播。',tags:'研究贡献 / 学术影响 / 技术扩散'},
  {num:'02',title:'经济与产业效益',question:'科研成果如何进入产业活动？',text:'连接技术采用、产品发展和企业经营，研究创新成果从知识走向应用的路径。',tags:'产品创新 / 技术采用 / 经营表现'},
  {num:'03',title:'政策与资源配置',question:'支持如何作用于研究和应用？',text:'结合资助布局、研究力量和政策实施，比较不同方向、机构与地区的发展变化。',tags:'资助布局 / 人才接续 / 政策作用'},
  {num:'04',title:'社会影响与公共价值',question:'创新为经济社会带来哪些变化？',text:'结合应用场景和公开资料，拓展对就业、技能需求与公共服务等问题的研究。',tags:'就业变化 / 技能需求 / 公共服务'},
]
</script>

<template>
<div class="project-home" :style="{'--home-masthead-height':mastheadHeight+'px'}">
  <section class="home-hero" aria-labelledby="home-title">
    <div class="home-hero-art" aria-hidden="true">
      <svg viewBox="0 0 1000 760" preserveAspectRatio="xMidYMid slice">
        <defs>
          <linearGradient id="home-thread" x1="0" y1="1" x2="1" y2="0"><stop stop-color="#bd294b"/><stop offset=".55" stop-color="#f2b6aa"/><stop offset="1" stop-color="#fff4de"/></linearGradient>
          <radialGradient id="home-light"><stop stop-color="#ce677a" stop-opacity=".19"/><stop offset="1" stop-color="#ce677a" stop-opacity="0"/></radialGradient>
        </defs>
        <ellipse cx="610" cy="365" rx="530" ry="350" fill="url(#home-light)"/>
        <g fill="none" stroke="url(#home-thread)" stroke-width="1">
          <path v-for="i in 32" :key="'a'+i" :d="`M ${-130+i*5} ${660+i*3} C ${170+i*4} ${600-i*12}, ${400+i*3} ${-80+i*8}, 1100 ${110+i*16}`" :opacity=".10+i*.012"/>
          <path v-for="i in 12" :key="'b'+i" :d="`M ${250+i*15} 830 C ${860-i*12} ${600-i*7}, ${210+i*16} ${170+i*6}, 1100 ${80+i*12}`" opacity=".11"/>
        </g>
        <g fill="#ffe9d3"><circle cx="410" cy="329" r="4"/><circle cx="668" cy="276" r="3"/><circle cx="830" cy="384" r="4"/><circle cx="580" cy="493" r="2.5"/></g>
        <g fill="none" stroke="#f0c5b9" opacity=".25"><circle cx="410" cy="329" r="11"/><circle cx="830" cy="384" r="12"/></g>
      </svg>
    </div>
    <div class="home-wrap home-hero-content">
      <p class="home-eyebrow light">国家自然科学基金委员会专项项目</p>
      <h1 id="home-title">从基础研究出发<br/>理解创新的价值<span>。</span></h1>
      <p class="home-hero-description">连接科研投入、知识成果与实际应用，<br class="desktop-break"/>为理解基础研究的科学、经济和社会价值提供数据与证据。</p>
      <div class="home-hero-actions"><router-link class="home-cta primary" to="/overview">探索数据资源 <span aria-hidden="true">↗</span></router-link><a class="home-cta outline" href="#approach">了解研究思路 <span aria-hidden="true">↓</span></a></div>
      <div class="home-hero-bottom"><span>基础研究全链条数据系统构建与集成</span><a href="#about">向下探索 <span aria-hidden="true">↓</span></a></div>
    </div>
  </section>

  <div class="home-scroll-cue">
    <button type="button" class="home-scroll-button" aria-label="向下浏览项目介绍" @click="exploreBelow">
      <svg viewBox="0 0 28 30" fill="none" aria-hidden="true"><path d="M14 4v18M7 16l7 7 7-7"/><path class="cue-echo" d="m9 23 5 5 5-5"/></svg>
    </button>
  </div>

  <section id="about" class="home-wrap home-about home-section">
    <div><p class="home-eyebrow">项目缘起</p><h2>研究的价值，<br/>在长链条中逐步显现。</h2></div>
    <div class="home-about-copy"><p class="home-lead">一项基础研究，可能在多年之后成为新技术、新产品或新应用的起点。理解这种作用，需要把分散在不同阶段、不同主体中的线索连接起来。</p><p>依托国家自然科学基金委员会专项项目《基础研究全链条数据系统构建与集成》，中国人民大学基础研究与中国式现代化发展战略研究中心联合国家治理大数据和人工智能创新平台，建设跨领域的研究数据库与评估工具，探索基础研究支撑经济社会发展的作用机制。</p></div>
    <div class="home-chain" aria-label="研究主线：基金资助、科学研究、技术发展、产业应用、经济社会价值"><div v-for="(label,i) in ['基金资助','科学研究','技术发展','产业应用','经济社会价值']" :key="label"><small>0{{i+1}}</small><strong>{{label}}</strong><span v-if="i<4" aria-hidden="true">→</span></div></div>
  </section>

  <section id="approach" class="home-method-section">
    <div class="home-wrap home-section">
      <div class="home-section-heading"><div><p class="home-eyebrow">研究思路</p><h2>以技术点为线索，<br/>把数据连成可理解的发展脉络。</h2></div><p>从一个具体技术出发，向前寻找科研支持，向后追踪应用。既看总体变化，也能深入到一项成果、一个团队和一个案例。</p></div>
      <div class="home-method-grid"><article v-for="step in steps" :key="step.num"><span class="home-step-num">{{step.num}}</span><h3>{{step.title}}</h3><p>{{step.text}}</p></article></div>
      <div class="home-domains">
        <router-link to="/evolution?domain=ai"><div><small>人工智能</small><h3>从模型架构到技术应用</h3><p>7 大类 · 29 技术组 · 70 技术点</p></div><span aria-hidden="true">↗</span></router-link>
        <router-link to="/evolution?domain=lowalt"><div><small>低空经济</small><h3>从关键技术到应用场景</h3><p>6 大类 · 33 技术点</p></div><span aria-hidden="true">↗</span></router-link>
      </div>
      <p class="home-method-caption">以共同方法组织数据，为不同领域配置技术词典、研究问题与评估维度。</p>
    </div>
  </section>

  <section id="resources" class="home-wrap home-section">
    <div class="home-section-heading"><div><p class="home-eyebrow">数据基础</p><h2>汇聚多源资料，<br/>支撑多角度研究。</h2></div><router-link class="home-text-link" to="/overview">查看数据库全貌 <span aria-hidden="true">→</span></router-link></div>
    <div v-if="headline.length" class="home-data-strip"><div v-for="item in headline" :key="item.id"><span>{{item.name}}</span><strong>{{item.value}}<small>{{item.unit}}</small></strong></div></div>
    <p v-else class="home-data-placeholder">基金、论文、专利与产业资料，持续汇聚于共同的数据基础。</p>
    <div class="home-resources"><router-link v-for="group in resourceGroups" :key="group.num" :to="group.to"><div class="home-resource-top"><span>{{group.num}}</span><span aria-hidden="true">↗</span></div><h3>{{group.title}}</h3><p class="home-resource-items">{{group.items}}</p><p>{{group.text}}</p></router-link></div>
  </section>

  <section class="home-case-section"><div class="home-wrap home-case-content">
    <div><p class="home-eyebrow light">案例研究</p><h2>从一条线索，<br/>走向一组有依据的案例。</h2><p>围绕技术、企业或产品，按统一结构组织科研支持、关键成果与应用资料，为批量抽取、核查和比较优质案例提供基础。</p><router-link class="home-cta outline" to="/chain?domain=ai">探索关联证据 <span aria-hidden="true">↗</span></router-link></div>
    <div class="home-case-path"><p class="home-case-kicker">一个案例，可以这样展开</p><div v-for="(item,i) in [['科研支持','哪些基金、机构与团队参与了研究'],['关键成果','形成了什么方法、论文或专利'],['技术应用','如何进入后续研发与产品应用'],['发展表现','结合时间与情境，研究其后续影响']]" :key="item[0]"><span>0{{i+1}}</span><article><h3>{{item[0]}}</h3><p>{{item[1]}}</p></article></div></div>
  </div></section>

  <section id="evaluation" class="home-wrap home-section home-evaluation">
    <div class="home-section-heading"><div><p class="home-eyebrow">评估用途</p><h2>同一数据基础，<br/>回答不同的价值问题。</h2></div><p>从科学贡献到经济社会影响，围绕具体问题组织样本、指标与证据，为多维度评估提供支撑。</p></div>
    <div class="home-evaluation-grid"><article v-for="use in uses" :key="use.num"><span>{{use.num}}</span><h3>{{use.title}}</h3><h4>{{use.question}}</h4><p>{{use.text}}</p><small>{{use.tags}}</small></article></div>
    <div class="home-bottom-cta"><div><h3>从数据出发，深入一个研究问题。</h3><p>浏览专题资料、技术演进和研究分析。</p></div><router-link class="home-cta primary" to="/data?domain=ai">进入领域数据 <span aria-hidden="true">↗</span></router-link></div>
  </section>
</div>
</template>
