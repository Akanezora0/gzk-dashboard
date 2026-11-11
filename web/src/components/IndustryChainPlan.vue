<script setup>
/* 产业链分析：技术发展 → 产业应用 → 经济社会价值（框架，页面内容待同事提供后替换） */
const plan=[
 {n:'01',t:'技术成果承接',d:'按共同技术词表把专利、软著与企业对应起来，观察技术成果由哪些企业承接。'},
 {n:'02',t:'产品与产业应用',d:'梳理企业产品与服务覆盖的技术方向与行业，形成技术到产品、产业的对应。'},
 {n:'03',t:'经济社会价值',d:'结合企业经营、劳动力需求与社会效益指标，衡量技术进入产业后形成的价值。'}]
</script>
<template>
 <section class="policy-plan">
  <header><h3>产业链分析</h3><p>以人工智能领域为示范，沿技术发展、产业应用与经济社会价值三个环节组织分析。</p></header>
  <div class="pp-grid"><article v-for="p in plan" :key="p.n"><b>{{p.n}}</b><h4>{{p.t}}</h4><p>{{p.d}}</p></article></div>
  <div class="pp-foot"><span>企业名录、专利、软著与招聘数据已纳入数据底座，可在领域数据中检索。</span><router-link to="/data?domain=ai&type=company">查看企业数据 →</router-link></div>
 </section>
</template>
<style scoped>
.policy-plan{padding:28px 30px 30px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.policy-plan h3{margin:0;font-size:21px;font-weight:750;color:#232930;padding-left:14px;border-left:4px solid #a21535;line-height:1.2}
.policy-plan header p{margin:10px 0 20px;font-size:15px;color:#5d575b}
.pp-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.pp-grid article{padding:20px 22px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.pp-grid b{font-size:14px;font-weight:800;color:#a21535}
.pp-grid h4{margin:8px 0;font-size:17px;font-weight:750}
.pp-grid p{margin:0;font-size:13.5px;line-height:1.75;color:#6a6468}
.pp-foot{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-top:18px;padding:14px 18px;border-radius:4px;background:#fbf5f6;font-size:13.5px;color:#5d575b}
.pp-foot a{font-weight:650;color:#a21535;text-decoration:none;white-space:nowrap}
@media(max-width:760px){.pp-grid{grid-template-columns:1fr}.pp-foot{flex-direction:column;align-items:flex-start}.policy-plan{padding:20px 16px}}
</style>
