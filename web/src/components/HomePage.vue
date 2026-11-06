<script setup>
import {computed,ref,onMounted,onBeforeUnmount} from 'vue'
import {overviewHeadline} from '../helpers/foundationSources'

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
const headline=computed(()=>overviewHeadline(props.data))

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
const icons={
  fund:'M7 4l5 7 5-7M12 11v9M8 13.5h8M8 17h8',
  science:'M9 3h6M10 3v6l-5.2 9.1A2 2 0 0 0 6.5 21h11a2 2 0 0 0 1.7-2.9L14 9V3M7.6 15h8.8',
  tech:'M7 7h10v10H7zM10 10h4v4h-4zM9.5 3v4M14.5 3v4M9.5 17v4M14.5 17v4M3 9.5h4M3 14.5h4M17 9.5h4M17 14.5h4',
  industry:'M3 21V11l5 3v-3l5 3V7l8 4v10zM3 21h18M7 17.5h2M12 17.5h2M17 17.5h2',
  society:'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM3.5 9h17M3.5 15h17M12 3c2.4 2.5 3.6 5.5 3.6 9s-1.2 6.5-3.6 9c-2.4-2.5-3.6-5.5-3.6-9S9.6 5.5 12 3z',
  split:'M4 5h16M8 12h12M12 19h8M4 5v14M4 12h4M4 19h8',
  gather:'M12 4c4.4 0 8 1.3 8 3s-3.6 3-8 3-8-1.3-8-3 3.6-3 8-3zM4 7v10c0 1.7 3.6 3 8 3s8-1.3 8-3V7M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3',
  trace:'M6 3v12M18 9a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM6 21a3 3 0 1 0 0-6 3 3 0 0 0 0 6zM18 9a9 9 0 0 1-9 9',
  assess:'M4 20V11M10 20V5M16 20v-7M3 20h18M20 4l-4 4',
  growth:'M3 17l6-6 4 4 8-8M15 7h6v6',
  policy:'M3 21h18M5 21v-9M9.7 21v-9M14.3 21v-9M19 21v-9M2.5 9.5 12 4l9.5 5.5z',
  people:'M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8zM2 21c0-3.9 3.1-7 7-7s7 3.1 7 7M16 3.3a4 4 0 0 1 0 7.4M18 14.4c2.4.9 4 3.3 4 6.6',
}
const chain=[
  {label:'基金资助',sub:'资助布局与投入',icon:'fund',tone:tones.red},
  {label:'科学研究',sub:'论文与知识积累',icon:'science',tone:tones.blue},
  {label:'技术发展',sub:'专利与技术突破',icon:'tech',tone:tones.plum},
  {label:'产业应用',sub:'企业、产品与市场',icon:'industry',tone:tones.gold},
  {label:'经济社会价值',sub:'增长、就业与公共服务',icon:'society',tone:tones.teal},
]
const steps=[
  {num:'01',title:'技术拆解',icon:'split',tone:tones.red,text:'联合领域专家构建技术词表，将领域拆解为技术类别与技术点。'},
  {num:'02',title:'数据汇聚',icon:'gather',tone:tones.blue,text:'围绕技术点关联基金、论文、专利、企业与政策等多源数据。'},
  {num:'03',title:'脉络梳理',icon:'trace',tone:tones.plum,text:'结合技术综述与代表成果，梳理技术演进与知识传承。'},
  {num:'04',title:'价值评估',icon:'assess',tone:tones.teal,text:'抽取典型案例，开展科学、经济、政策与社会多维评估。'},
]
const domains=[
  {to:'/evolution?domain=ai',name:'人工智能',tone:tones.red,title:'从模型架构到技术应用',stats:[['7','大类'],['29','技术组'],['70','技术点']]},
  {to:'/evolution?domain=lowalt',name:'低空经济',tone:tones.blue,title:'从关键技术到应用场景',stats:[['6','大类'],['33','技术点']]},
]
const resourceGroups=[
  {num:'01',title:'创新链数据',icon:'science',tone:tones.red,items:['基金项目','学术论文','专利','软件著作权'],text:'刻画科研投入、知识成果及其相互联系。',to:'/data?domain=ai&type=fund'},
  {num:'02',title:'产业链数据',icon:'industry',tone:tones.gold,items:['企业','产品','招聘','经营信息'],text:'追踪技术进入产品、企业与市场的过程。',to:'/data?domain=ai&type=company'},
  {num:'03',title:'政策链数据',icon:'policy',tone:tones.blue,items:['政策文献','产业新闻','行业报告'],text:'呈现技术发展所处的政策与产业环境。',to:'/data?domain=ai&type=policy'},
]
const casePath=[{title:'科研支持',text:'基金、机构与团队',icon:'fund',tone:'#e2677f'},{title:'关键成果',text:'方法、论文与专利',icon:'science',tone:'#7aa9de'},{title:'技术应用',text:'后续研发与产品',icon:'tech',tone:'#b597dc'},{title:'发展表现',text:'产业与社会影响',icon:'growth',tone:'#e5b86a'}]
const uses=[
  {num:'01',title:'科学价值',icon:'science',tone:tones.blue,question:'哪些基础研究成为后续创新的源头？',text:'追踪代表成果、引用联系与方法复用，刻画知识积累与技术突破。',tags:['研究贡献','学术影响','技术扩散']},
  {num:'02',title:'经济效益',icon:'growth',tone:tones.gold,question:'科研成果如何转化为产业动能？',text:'连接技术采用、产品发展与企业经营，追踪成果从知识走向应用。',tags:['产品创新','技术采用','经营表现']},
  {num:'03',title:'政策与资源配置',icon:'policy',tone:tones.red,question:'资助与政策如何塑造创新格局？',text:'结合资助布局、研究力量与政策实施，比较方向、机构与地区差异。',tags:['资助布局','人才接续','政策作用']},
  {num:'04',title:'社会影响',icon:'people',tone:tones.teal,question:'创新为经济社会带来哪些改变？',text:'结合应用场景与公开资料，研究就业、技能需求与公共服务的变化。',tags:['就业变化','技能需求','公共服务']},
]
</script>

<template>
<div ref="root" class="project-home" :style="{'--home-masthead-height':mastheadHeight+'px'}">
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
      <div class="home-hero-actions"><router-link class="home-cta primary" to="/overview">进入数据总览 <span aria-hidden="true">↗</span></router-link><a class="home-cta outline" href="#approach">了解研究框架 <span aria-hidden="true">↓</span></a></div>
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
      <div class="home-chain-body">
      <div class="home-chain-track" aria-hidden="true"><i></i></div>
      <ol class="home-chain-stages">
        <li v-for="(c,i) in chain" :key="c.label" :style="{'--i':i,'--tone':c.tone}"><span class="home-chain-icon"><svg viewBox="0 0 24 24"><path :d="icons[c.icon]"/></svg></span><em>0{{i+1}}</em><strong>{{c.label}}</strong><small>{{c.sub}}</small></li>
      </ol>
      </div>
      <div class="home-chain-brackets">
        <div class="bracket innovation"><span><i></i>创新链</span></div>
        <div class="bracket industry"><span><i></i>产业链</span></div>
        <div class="bracket policy"><span><i></i>政策链 · 贯穿全过程</span></div>
      </div>
    </div>
  </section>

  <section id="approach" class="home-method-section">
    <div class="home-wrap home-section">
      <div class="home-section-heading reveal"><div><p class="home-eyebrow">研究框架</p><h2>以技术点为单元，<br/>组织全链条数据。</h2></div><p>以共同技术词表为纲，将领域拆解为可研究的技术点；围绕技术点汇聚多源数据、梳理发展脉络，进而开展案例研究与价值评估。</p></div>
      <div class="home-steps">
        <article v-for="(step,i) in steps" :key="step.num" class="reveal" :style="{'--i':i,'--tone':step.tone}">
          <div class="home-step-head"><span class="home-step-icon"><svg viewBox="0 0 24 24"><path :d="icons[step.icon]"/></svg></span><span class="home-step-num">{{step.num}}</span></div>
          <h3>{{step.title}}</h3><p>{{step.text}}</p>
        </article>
      </div>
      <div class="home-subhead reveal"><span>示范领域</span></div>
      <div class="home-domains">
        <router-link v-for="d in domains" :key="d.name" :to="d.to" class="reveal" :style="{'--tone':d.tone}">
          <div><small>{{d.name}}</small><h3>{{d.title}}</h3></div>
          <dl><div v-for="s in d.stats" :key="s[1]"><dt>{{s[0]}}</dt><dd>{{s[1]}}</dd></div></dl>
          <span aria-hidden="true">↗</span>
        </router-link>
      </div>
    </div>
  </section>

  <section id="resources" class="home-wrap home-section">
    <div class="home-section-heading reveal"><div><p class="home-eyebrow">数据基础</p><h2>汇聚多源数据，<br/>构建统一研究底座。</h2></div><router-link class="home-text-link" to="/overview">查看数据总览 <span aria-hidden="true">→</span></router-link></div>
    <div v-if="headline.length" class="home-data-strip reveal"><div v-for="item in headline" :key="item.id"><span>{{item.name}}</span><strong>{{item.value}}<small>{{item.unit}}</small></strong></div></div>
    <div class="home-resources">
      <router-link v-for="group in resourceGroups" :key="group.num" :to="group.to" class="reveal" :style="{'--tone':group.tone}">
        <div class="home-resource-top"><span class="home-resource-icon"><svg viewBox="0 0 24 24"><path :d="icons[group.icon]"/></svg></span><span aria-hidden="true">↗</span></div>
        <h3>{{group.title}}</h3><p>{{group.text}}</p>
        <ul><li v-for="item in group.items" :key="item">{{item}}</li></ul>
      </router-link>
    </div>
  </section>

  <section class="home-case-section"><div class="home-case-glow" aria-hidden="true"></div><svg class="home-case-art" viewBox="0 0 800 400" preserveAspectRatio="xMaxYMid slice" aria-hidden="true"><path v-for="i in 14" :key="i" :d="`M ${-40+i*6} ${420} C ${260+i*10} ${330-i*14}, ${470+i*8} ${40+i*10}, 860 ${-20+i*26}`"/></svg><div class="home-wrap home-case-content">
    <div class="reveal"><p class="home-eyebrow light">案例研究</p><h2>批量抽取优质案例，<br/>呈现基础研究的贡献路径。</h2><p>以技术、企业或产品为线索，按统一结构组织科研支持、关键成果、技术应用与发展表现，实现优质案例的批量抽取、核查与比较。</p><router-link class="home-cta outline" to="/chain?domain=ai">查看证据链 <span aria-hidden="true">↗</span></router-link></div>
    <div class="home-case-panel reveal">
      <p class="home-case-kicker">一个案例的四个层次</p>
      <ol class="home-case-path"><li v-for="(item,i) in casePath" :key="item.title" :style="{'--i':i,'--tone':item.tone}"><span class="home-case-node"><svg viewBox="0 0 24 24"><path :d="icons[item.icon]"/></svg></span><em>0{{i+1}}</em><h3>{{item.title}}</h3><p>{{item.text}}</p></li></ol>
    </div>
  </div></section>

  <section id="evaluation" class="home-wrap home-section home-evaluation">
    <div class="home-section-heading reveal"><div><p class="home-eyebrow">评估维度</p><h2>面向多维评估，<br/>回答基础研究的价值之问。</h2></div><p>以统一的数据底座与证据链为基础，围绕具体问题组织样本、指标与证据。</p></div>
    <div class="home-evaluation-grid"><article v-for="(use,i) in uses" :key="use.num" class="reveal" :style="{'--i':i,'--tone':use.tone}">
      <div class="home-use-head"><span class="home-use-icon"><svg viewBox="0 0 24 24"><path :d="icons[use.icon]"/></svg></span><span class="home-use-num">{{use.num}}</span></div>
      <h3>{{use.title}}</h3><h4>{{use.question}}</h4><p>{{use.text}}</p>
      <ul><li v-for="t in use.tags" :key="t">{{t}}</li></ul>
    </article></div>
  </section>
</div>
</template>
