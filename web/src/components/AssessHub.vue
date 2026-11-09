<script setup>
/* 评估：基础研究投入与布局的合理性评估（筹建中，占位页） */
import PageHero from './PageHero.vue'
const dims=[
 {n:'01',t:'投入规模',d:'资助总量与增长节奏，与研究产出、学科发展阶段的匹配程度。',k:['经费增速','产出弹性']},
 {n:'02',t:'方向布局',d:'经费在技术方向与技术点上的分布，与前沿热点、产业需求的契合程度。',k:['方向份额','前沿覆盖']},
 {n:'03',t:'主体结构',d:'承担机构、负责人与地区分布的集中度、新进入与持续性。',k:['集中度','持续产出率']},
 {n:'04',t:'成果转化',d:'论文、专利向企业研发、产品与行业应用的承接效率。',k:['承接时滞','应用覆盖']}]
</script>
<template><div class="assess">
 <PageHero eyebrow="评估" title="基础研究投入与布局评估" lead="综合数据底座、创新链分析与案例研究，评估基础研究的投入规模、方向布局与成果转化是否合理。"/>
 <section class="as-panel">
  <header><h3>评估维度</h3><span>评估框架与指标体系建设中</span></header>
  <div class="as-grid"><article v-for="d in dims" :key="d.n"><b>{{d.n}}</b><h4>{{d.t}}</h4><p>{{d.d}}</p><div class="as-k"><span v-for="k in d.k" :key="k">{{k}}</span></div></article></div>
  <div class="as-foot"><span>相关数据可在创新链分析中查看</span><router-link :to="{path:'/chain',query:{domain:'ai',module:'investment'}}">投入与产出 →</router-link><router-link :to="{path:'/chain',query:{domain:'ai',module:'strength'}}">研究团队 →</router-link></div>
 </section>
</div></template>
<style scoped>
.assess{padding-top:26px}
.as-panel{padding:28px 30px 30px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.as-panel header{display:flex;justify-content:space-between;align-items:baseline;gap:16px;margin-bottom:20px}
.as-panel h3{margin:0;font-size:21px;font-weight:750;color:#232930;padding-left:14px;border-left:4px solid #a21535;line-height:1.2}
.as-panel header span{font-size:13.5px;color:#9a9296}
.as-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px}
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
