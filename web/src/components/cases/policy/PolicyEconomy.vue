<script setup>
/* 政策案例二 · 政策实施与经济效益（研究中） */
</script>
<template><div class="pe">
 <header class="pe-top"><span class="pe-logo" aria-hidden="true">政</span><div><h3>政策实施与经济效益</h3><p>政策文本 × 企业运营数据 · 研究中</p></div></header>
 <section class="pe-sec">
  <p class="pe-lead">匹配政策文本与企业运营数据，研究政策实施对企业经营表现的影响，把政策效应评估从技术创新延伸到经济效益。</p>
  <div class="pe-path"><template v-for="(s,i) in [['政策文本','采集与量化评分'],['企业匹配','政策与企业运营数据'],['经营表现','收入、利润与投入'],['因果评估','经济效益与稳健性']]" :key="s[0]"><i v-if="i" aria-hidden="true">→</i><div><b>{{s[0]}}</b><small>{{s[1]}}</small></div></template></div>
  <div class="pe-plan">
   <article><b>01</b><h5>数据与样本</h5><p>政策与企业数据的匹配范围及指标口径</p></article>
   <article><b>02</b><h5>核心结果</h5><p>经济效益估计及置信区间</p></article>
   <article><b>03</b><h5>机制与检验</h5><p>政策传导机制及稳健性分析</p></article>
  </div>
 </section>
</div></template>
<style scoped>
.pe{display:flex;flex-direction:column;gap:18px}
.pe-top{display:flex;align-items:center;gap:14px;padding:16px 22px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.pe-logo{display:grid;place-items:center;width:44px;height:44px;border-radius:4px;background:#a21535;color:#fff;font-size:20px;font-weight:800}
.pe-top h3{margin:2px 0;font-size:21px;font-weight:750;color:#232930}
.pe-top p{margin:0;font-size:12px;color:#9a9296}
.pe-sec{padding:26px 28px 28px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.pe-lead{margin:0 0 20px;font-size:17px;font-weight:600;line-height:1.8;color:#2f2b2d}
.pe-path{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding:22px 24px;border-radius:4px;background:linear-gradient(140deg,#8c1c32,#5f1326);color:#fff}
.pe-path i{font-style:normal;color:#e6a9b7}
.pe-path div{padding:10px 16px;border:1px solid #ffffff3d;border-radius:3px;background:#ffffff12}
.pe-path b{display:block;font-size:14.5px}.pe-path small{display:block;font-size:11.5px;opacity:.75}
.pe-plan{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:18px}
.pe-plan article{padding:20px 22px;border:1px dashed #e3d4d7;border-radius:4px;background:#fcfaf9}
.pe-plan b{font-size:14px;font-weight:800;color:#a21535}
.pe-plan h5{margin:6px 0;font-size:16.5px;font-weight:750;color:#232930}
.pe-plan p{margin:0;font-size:13.5px;color:#6a6468}
@media(max-width:760px){.pe-sec{padding:20px 16px}.pe-plan{grid-template-columns:1fr}.pe-path{flex-direction:column;align-items:stretch}.pe-path i{transform:rotate(90deg);text-align:center}}
</style>
