<script setup>
/* 评估：沿首页三个评估维度组织（占位页） */
import PageHero from './PageHero.vue'
// 与首页“评估维度”一致
const dims=[
 {n:'01',t:'经济效应',q:'科研成果如何转化为产业动能？',d:'连接技术采用、产品发展与企业经营，追踪成果从知识走向应用。',k:['产品创新','技术采用','经营表现']},
 {n:'02',t:'政策与资源配置',q:'资助与政策如何塑造创新格局？',d:'结合资助布局、研究团队与政策实施，比较方向、机构与地区差异。',k:['资助布局','人才培育','政策作用']},
 {n:'03',t:'社会影响',q:'创新为经济社会带来哪些改变？',d:'结合应用场景与公开资料，研究就业、技能需求与公共服务的变化。',k:['就业变化','技能需求','公共服务']}]
</script>
<template><div class="assess">
 <PageHero title="基础研究多维评估" lead="以多源全域数据底座为基础，结合短链条分析与长链条案例，从经济效应、政策与资源配置、社会影响三个维度回答基础研究的价值之问。"/>
 <section class="as-panel">
  <header><h3>评估维度</h3></header>
  <div class="as-grid"><article v-for="d in dims" :key="d.n"><b>{{d.n}}</b><h4>{{d.t}}</h4><p class="q">{{d.q}}</p><p>{{d.d}}</p><div class="as-k"><span v-for="k in d.k" :key="k">{{k}}</span></div></article></div>
  <div class="as-foot"><span>相关分析</span><router-link :to="{path:'/evolution',query:{domain:'ai'}}">技术演进 · 投入与产出 →</router-link><router-link :to="{path:'/chain',query:{domain:'ai'}}">短链条分析 →</router-link><router-link :to="{path:'/cases',query:{domain:'ai'}}">长链条案例 →</router-link></div>
 </section>
</div></template>
<style scoped>
.assess{padding-top:26px}
.as-panel{padding:28px 30px 30px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.as-panel header{display:flex;justify-content:space-between;align-items:baseline;gap:16px;margin-bottom:20px}
.as-panel h3{margin:0;font-size:21px;font-weight:750;color:#232930;padding-left:14px;border-left:4px solid #a21535;line-height:1.2}
.as-panel header span{font-size:13.5px;color:#9a9296}
.as-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.as-grid p.q{flex:none;margin:0 0 6px;font-size:14.5px;font-weight:650;color:#a21535}
.as-grid article{display:flex;flex-direction:column;padding:22px;border:1px dashed #ddd3cf;border-radius:4px;background:repeating-linear-gradient(135deg,#fff 0 10px,#fcf9f8 10px 20px)}
.as-grid b{font-size:14px;font-weight:800;color:#a21535}
.as-grid h4{margin:8px 0;font-size:18px;font-weight:750;color:#232930}
.as-grid p{flex:1;margin:0 0 14px;font-size:13.5px;line-height:1.75;color:#6a6468}
.as-k{display:flex;flex-wrap:wrap;gap:6px}.as-k span{padding:3px 9px;border-radius:2px;background:#f4efed;font-size:12px;color:#7a7378}
.as-foot{display:flex;align-items:center;gap:18px;margin-top:18px;padding:14px 18px;border-radius:4px;background:#fbf5f6;font-size:13.5px;color:#5d575b}
.as-foot a{font-weight:650;color:#a21535;text-decoration:none}
@media(max-width:1000px){.as-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:600px){.as-grid{grid-template-columns:1fr}.as-panel{padding:20px 16px}.as-foot{flex-wrap:wrap}}
</style>
