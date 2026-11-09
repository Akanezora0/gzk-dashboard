<script setup>
import {computed,ref,onMounted,onBeforeUnmount} from 'vue'
import {homeIcons} from '../helpers/homeIcons'
import HomeIcon from './HomeIcon.vue'

const props=defineProps({data:Object})
function exploreBelow(){
  document.getElementById('about')?.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'})
}

/* 首屏高度：扣除系统标题与主导航 */
const mastheadHeight=ref(260)
let mastheadObserver,revealObserver
const root=ref(null)
onMounted(()=>{
  const elements=['.research-header','.research-nav'].map(selector=>document.querySelector(selector)).filter(Boolean)
  const measure=()=>{mastheadHeight.value=elements.reduce((height,element)=>height+element.getBoundingClientRect().height,0)}
  mastheadObserver=new ResizeObserver(measure)
  elements.forEach(element=>mastheadObserver.observe(element))
  measure()
  /* 滚动进入视口时淡入 */
  const targets=root.value?.querySelectorAll('.reveal')||[]
  if(!('IntersectionObserver' in window)){targets.forEach(el=>el.classList.add('in'));return}
  revealObserver=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.classList.add('in');revealObserver.unobserve(entry.target)}}),{rootMargin:'0px 0px -12% 0px'})
  targets.forEach(el=>revealObserver.observe(el))
})
onBeforeUnmount(()=>{mastheadObserver?.disconnect();revealObserver?.disconnect()})

/* ---------- 首屏主视觉：从一个源点出发，知识沿多条路径扩散到技术、产业与社会 ---------- */
const ART_W=1200,ART_H=760,OX=70,OY=560
const bez=(p0,p1,p2,p3,t)=>{const u=1-t;return u*u*u*p0+3*u*u*t*p1+3*u*t*t*p2+t*t*t*p3}
const threads=Array.from({length:28},(_,k)=>{
  const s=k/27
  const ey=-30+s*(ART_H+80)
  const c1=[OX+300,OY-70+k*2.5],c2=[560+k*7,ey+(k%3-1)*36],end=[ART_W+40,ey]
  const d=`M ${OX} ${OY} C ${c1[0]} ${c1[1]}, ${c2[0]} ${c2[1]}, ${end[0]} ${end[1]}`
  const at=t=>[bez(OX,c1[0],c2[0],end[0],t),bez(OY,c1[1],c2[1],end[1],t)]
  return {k,d,at,opacity:.14+.32*Math.sin(Math.PI*s)}
})
const nodes=[]
threads.forEach(({k,at})=>{[.34,.52,.7,.86].forEach((t,j)=>{if((k*7+j*3)%4===0){const [x,y]=at(t);nodes.push({x,y,r:j===0?1.6:1.6+j*.55,key:k+'-'+j,delay:((k+j)%7)*.6})}})})
const pulses=threads.filter(t=>t.k%5===2).map((t,i)=>({d:t.d,key:'p'+t.k,delay:i*1.1}))
const stages=[{x:330,label:'科学'},{x:540,label:'技术'},{x:750,label:'产业'},{x:960,label:'社会'}]

/* ---------- 内容 ---------- */
const tones={red:'#a21535',blue:'#2c64a0',plum:'#6f4a94',gold:'#b2772a',teal:'#23806e'}
const chain=[
  {label:'基金资助',sub:'资助布局与投入',icon:'fund',tone:tones.red},
  {label:'科学研究',sub:'论文与知识积累',icon:'science',tone:tones.blue},
  {label:'技术发展',sub:'专利与技术突破',icon:'tech',tone:tones.plum},
  {label:'产业应用',sub:'企业、产品与市场',icon:'industry',tone:tones.gold},
  {label:'经济社会价值',sub:'增长、就业与公共服务',icon:'society',tone:tones.teal},
]
const siteLinks=[['/overview','数据总览'],['/data?domain=ai','领域数据'],['/evolution?domain=ai','技术演进'],['/chain?domain=ai','创新链分析'],['/cases','案例专题']]
const platformLinks=[['平台简介','https://brain.ruc.edu.cn/jggk/ptjj/index.htm'],['交叉研究','https://brain.ruc.edu.cn/jcyj/index.htm'],['云端平台','https://brain.ruc.edu.cn/ydpt/index.htm'],['学术交流','https://brain.ruc.edu.cn/xsjl/index.htm'],['联系我们','https://brain.ruc.edu.cn/lxwm/index.htm']]
const casePath=[{title:'科研支持',text:'基金、机构与团队',icon:'grant',tone:'#f2c4cc'},{title:'关键成果',text:'方法、论文与专利',icon:'paper',tone:'#f2c4cc'},{title:'技术应用',text:'后续研发与产品',icon:'tech',tone:'#f2c4cc'},{title:'发展表现',text:'产业与社会影响',icon:'growth',tone:'#f2c4cc'}]
const uses=[
  {num:'01',title:'科学价值',icon:'science',tone:tones.red,question:'哪些基础研究成为后续创新的源头？',text:'追踪代表成果、引用联系与方法复用，刻画知识积累与技术突破。',tags:['研究贡献','学术影响','技术扩散']},
  {num:'02',title:'经济效益',icon:'growth',tone:tones.red,question:'科研成果如何转化为产业动能？',text:'连接技术采用、产品发展与企业经营，追踪成果从知识走向应用。',tags:['产品创新','技术采用','经营表现']},
  {num:'03',title:'政策与资源配置',icon:'policy',tone:tones.red,question:'资助与政策如何塑造创新格局？',text:'结合资助布局、研究团队与政策实施，比较方向、机构与地区差异。',tags:['资助布局','人才接续','政策作用']},
  {num:'04',title:'社会影响',icon:'society',tone:tones.red,question:'创新为经济社会带来哪些改变？',text:'结合应用场景与公开资料，研究就业、技能需求与公共服务的变化。',tags:['就业变化','技能需求','公共服务']},
]
</script>

<template>
<div ref="root" class="project-home" :style="{'--home-masthead-height':mastheadHeight+'px'}">
  <svg class="home-icon-masks" aria-hidden="true" focusable="false"><defs>
    <mask v-for="(g,key) in homeIcons" :id="`home-icon-cut-${key}`" :key="key" maskUnits="userSpaceOnUse" x="0" y="0" width="24" height="24">
      <rect width="24" height="24" fill="#fff"/>
      <path v-if="g.cut" :d="g.cut" fill="none" stroke="#000" stroke-width="1.7" stroke-linecap="square"/>
      <path v-if="g.cutFill" :d="g.cutFill" fill="#000"/>
    </mask>
  </defs></svg>
  <section class="home-hero" aria-labelledby="home-title">
    <div class="home-hero-art" aria-hidden="true">
      <svg :viewBox="`0 0 ${ART_W} ${ART_H}`" preserveAspectRatio="xMinYMid slice">
        <defs>
          <linearGradient id="hero-thread" x1="0" y1="0" x2="1" y2="0"><stop stop-color="#ffd9c9" stop-opacity=".95"/><stop offset=".5" stop-color="#f3a9a0"/><stop offset="1" stop-color="#ffe8d8" stop-opacity=".6"/></linearGradient>
          <radialGradient id="hero-origin"><stop stop-color="#ffd2c2" stop-opacity=".55"/><stop offset=".35" stop-color="#e2697f" stop-opacity=".22"/><stop offset="1" stop-color="#e2697f" stop-opacity="0"/></radialGradient>
        </defs>
        <circle :cx="OX" :cy="OY" r="340" fill="url(#hero-origin)"/>
        <g class="hero-stages">
          <g v-for="s in stages" :key="s.label"><line :x1="s.x" :x2="s.x" y1="70" :y2="ART_H" /><text :x="s.x+10" y="88">{{s.label}}</text></g>
        </g>
        <g fill="none" stroke="url(#hero-thread)" stroke-width="1">
          <path v-for="t in threads" :key="t.k" :d="t.d" :opacity="t.opacity"/>
        </g>
        <g class="hero-pulses" fill="none"><path v-for="p in pulses" :key="p.key" :d="p.d" pathLength="100" :style="{animationDelay:p.delay+'s'}"/></g>
        <g class="hero-nodes"><circle v-for="n in nodes" :key="n.key" :cx="n.x" :cy="n.y" :r="n.r" :style="{animationDelay:n.delay+'s'}"/></g>
        <g class="hero-origin">
          <circle class="ripple" :cx="OX" :cy="OY" r="16"/><circle class="ripple r2" :cx="OX" :cy="OY" r="16"/>
          <circle :cx="OX" :cy="OY" r="6" fill="#fff4ec"/>
          <text :x="OX+18" :y="OY+34">基础研究</text>
        </g>
      </svg>
    </div>
    <div class="home-wrap home-hero-content">
      <p class="home-eyebrow light">国家自然科学基金委员会专项项目</p>
      <h1 id="home-title">从基础研究出发<br/>理解创新的价值</h1>
      <p class="home-hero-description">贯通创新链、产业链与政策链，构建基础研究全链条数据系统，<br class="desktop-break"/>为评估基础研究的科学、经济与社会价值提供数据与证据。</p>
      <div class="home-hero-actions"><a class="home-cta light" href="#about" @click.prevent="exploreBelow">了解研究详情 <span aria-hidden="true">↓</span></a><router-link class="home-cta outline" to="/overview">进入数据总览 <span aria-hidden="true">↗</span></router-link></div>
      <div class="home-hero-bottom"><span>基础研究全链条数据系统构建与集成</span><span>中国人民大学 · 基础研究与中国式现代化发展战略研究中心</span></div>
    </div>
  </section>

  <div class="home-scroll-cue">
    <button type="button" class="home-scroll-button" aria-label="向下浏览项目介绍" @click="exploreBelow">
      <svg viewBox="0 0 28 30" fill="none" aria-hidden="true"><path d="M14 4v18M7 16l7 7 7-7"/><path class="cue-echo" d="m9 23 5 5 5-5"/></svg>
    </button>
  </div>

  <section id="about" class="home-wrap home-section">
    <div class="home-about">
      <div class="reveal"><p class="home-eyebrow">项目概览</p><h2>让基础研究的价值<br/>可追溯、可度量、可评估。</h2></div>
      <div class="home-about-copy reveal"><p class="home-lead">基础研究是创新的源头。它的价值往往要经过知识积累、技术突破与产业应用的长链条才逐步显现，相关线索分散在基金、论文、专利、企业、产品与政策之中。</p><p>项目依托国家自然科学基金委员会专项项目《基础研究全链条数据系统构建与集成》，由中国人民大学基础研究与中国式现代化发展战略研究中心联合国家治理大数据和人工智能创新平台建设，打通多源数据，建立从资助投入到经济社会价值的证据链条。</p></div>
    </div>
    <div class="home-chain reveal" aria-label="全链条：基金资助、科学研究、技术发展、产业应用、经济社会价值">
      <div class="home-chain-head"><span>基础研究全链条</span><span>从资助投入到经济社会价值</span></div>
      <ol class="home-flow">
        <li v-for="(c,i) in chain" :key="c.label" :style="{'--i':i}"><em>{{String(i+1).padStart(2,'0')}}</em><i class="home-flow-dot" aria-hidden="true"></i><strong>{{c.label}}</strong><small>{{c.sub}}</small></li>
      </ol>
      <div class="home-flow-chains">
        <span class="innovation">创新链</span><span class="industry">产业链</span><span class="policy">政策链贯穿全过程</span>
      </div>
    </div>
  </section>

  <section id="approach" class="home-method-section">
    <div class="home-wrap home-section">
      <div class="home-section-heading reveal"><div><p class="home-eyebrow">研究框架</p><h2>以技术主题连接<br/>科研供给与产业需求。</h2></div><p>以共同技术词表组织技术主题，向上追溯科研支撑，向下追踪产品与产业应用，把分散的数据连成可核查的发展脉络。</p></div>
      <div class="home-frame reveal">
        <div class="home-frame-row supply"><span class="home-frame-label"><b>科研供给</b><small>向上追溯科研支撑</small></span><ul><li v-for="t in ['基金资助','论文成果','专利技术']" :key="t">{{t}}</li></ul></div>
        <div class="home-frame-link up" aria-hidden="true"><i></i><i></i><i></i></div>
        <div class="home-frame-core"><span class="home-frame-label"><b>技术主题</b><small>共同技术词表 · 技术点</small></span><p>以技术点为单元，汇聚并对齐多源数据</p></div>
        <div class="home-frame-link down" aria-hidden="true"><i></i><i></i><i></i></div>
        <div class="home-frame-row demand"><span class="home-frame-label"><b>产业需求</b><small>向下追踪产品与产业应用</small></span><ul><li v-for="t in ['企业主体','产品与服务','产业应用']" :key="t">{{t}}</li></ul></div>
      </div>
    </div>
  </section>

  <section class="home-case-section"><div class="home-case-glow" aria-hidden="true"></div><svg class="home-case-art" viewBox="0 0 800 400" preserveAspectRatio="xMaxYMid slice" aria-hidden="true"><path v-for="i in 14" :key="i" :d="`M ${-40+i*6} ${420} C ${260+i*10} ${330-i*14}, ${470+i*8} ${40+i*10}, 860 ${-20+i*26}`"/></svg><div class="home-wrap home-case-content">
    <div class="reveal"><p class="home-eyebrow light">案例研究</p><h2>批量抽取优质案例，<br/>呈现基础研究的贡献路径。</h2><p>以技术、企业或产品为线索，按统一结构组织科研支持、关键成果、技术应用与发展表现，实现优质案例的批量抽取、核查与比较。</p><router-link class="home-cta outline" to="/chain?domain=ai">查看创新链分析 <span aria-hidden="true">↗</span></router-link></div>
    <div class="home-case-panel reveal">
      <p class="home-case-kicker">一个案例的四个层次</p>
      <ol class="home-case-path"><li v-for="(item,i) in casePath" :key="item.title" :style="{'--i':i,'--tone':item.tone}"><span class="home-case-node"><HomeIcon :name="item.icon"/></span><em>0{{i+1}}</em><h3>{{item.title}}</h3><p>{{item.text}}</p></li></ol>
    </div>
  </div></section>

  <section id="evaluation" class="home-wrap home-section home-evaluation">
    <div class="home-section-heading reveal"><div><p class="home-eyebrow">评估维度</p><h2>面向多维评估，<br/>回答基础研究的价值之问。</h2></div><p>以统一的数据底座与创新链分析为基础，围绕具体问题组织样本、指标与证据。</p></div>
    <div class="home-evaluation-grid"><article v-for="(use,i) in uses" :key="use.num" class="reveal" :style="{'--i':i,'--tone':use.tone}">
      <div class="home-use-head"><span class="home-use-icon"><HomeIcon :name="use.icon"/></span><span class="home-use-num">{{use.num}}</span></div>
      <h3>{{use.title}}</h3><h4>{{use.question}}</h4><p>{{use.text}}</p>
      <ul><li v-for="t in use.tags" :key="t">{{t}}</li></ul>
    </article></div>
  </section>

  <section class="home-platform" aria-labelledby="home-platform-title">
    <div class="home-platform-art" aria-hidden="true"><svg viewBox="0 0 1200 420" preserveAspectRatio="xMaxYMid slice"><path v-for="i in 18" :key="i" :d="`M ${-80+i*5} 460 C ${300+i*14} ${340-i*12}, ${620+i*10} ${60+i*10}, 1280 ${-40+i*24}`"/></svg></div>
    <div class="home-wrap home-platform-content">
      <div class="home-platform-intro">
        <p class="home-eyebrow light">建设平台</p>
        <h2 id="home-platform-title">中国人民大学<br/>国家治理大数据和人工智能创新平台</h2>
        <p>平台以构建“智慧治理生态系统”为使命，以“整体提升社会科学服务国家治理能力”为目标，依托大数据与人工智能技术，汇聚交叉研究团队与子实验室，连接政府、科研机构、企业与公众，开展学术研究、应用研究与政策咨询。</p>
        <a class="home-cta light" href="https://brain.ruc.edu.cn" target="_blank" rel="noopener">了解更多 <span aria-hidden="true">↗</span></a>
      </div>
      <div class="home-platform-links">
        <div><h3>系统导航</h3><ul>
          <li v-for="[to,label] in siteLinks" :key="to"><router-link :to="to">{{label}}</router-link></li>
        </ul></div>
        <div><h3>平台栏目</h3><ul>
          <li v-for="[label,href] in platformLinks" :key="label"><a :href="href" target="_blank" rel="noopener">{{label}}</a></li>
        </ul></div>
        <div><h3>联系方式</h3><ul class="contact">
          <li><small>地址</small>中国人民大学公共教学一楼三层 1301</li>
          <li><small>邮箱</small><a href="mailto:brain@ruc.edu.cn">brain@ruc.edu.cn</a></li>
          <li><small>官网</small><a href="https://brain.ruc.edu.cn" target="_blank" rel="noopener">brain.ruc.edu.cn</a></li>
        </ul></div>
      </div>
    </div>
    <div class="home-wrap home-platform-bottom"><span>基础研究数据与评估系统 · 中国人民大学 · 国家自然科学基金委员会</span><span>国家自然科学基金委员会专项项目 · 基础研究全链条数据系统构建与集成</span></div>
  </section>
</div>
</template>
