<script setup>
/* 投入与产出：方向与技术点布局 → 投入产出对照 → 基金贡献度 */
import {computed} from 'vue'
import {useRoute,useRouter} from 'vue-router'
import FundContribution from './FundContribution.vue'
import InvestLayout from './invest/InvestLayout.vue'
import InvestCompare from './invest/InvestCompare.vue'
import {useInvestData} from '../helpers/investData'
defineProps({data:Object})
const emit=defineEmits(['explore'])
const route=useRoute(),router=useRouter()
const tabs=[{id:'layout',label:'方向与技术点布局'},{id:'compare',label:'投入产出对照'},{id:'contribution',label:'基金贡献度'}]
// 兼容旧链接：funding / outputs / terms → 布局；curves → 对照
const legacy={funding:'layout',outputs:'layout',terms:'layout',curves:'compare'}
const active=computed(()=>{const q=String(route.query.analysis||'');return tabs.find(t=>t.id===(legacy[q]||q))||tabs[0]})
function choose(id){router.replace({query:{...route.query,analysis:id,measure:undefined}})}
const {curves,terms,error,load}=useInvestData()
</script>
<template><div class="investment-module">
 <div class="view-tools view-tabs"><nav aria-label="投入与产出分析"><button v-for="t in tabs" :key="t.id" :class="{active:active.id===t.id}" @click="choose(t.id)">{{t.label}}</button></nav></div>
 <div :key="active.id" class="pane-swap">
  <FundContribution v-if="active.id==='contribution'" :data="data" @explore="id=>emit('explore',id)"/>
  <div v-else-if="error" class="analysis-loading">投入与产出数据暂时无法读取 <button @click="load">重新读取</button></div>
  <div v-else-if="!curves" class="analysis-loading">正在读取投入与产出数据…</div>
  <div v-else class="investment-pane"><InvestLayout v-if="active.id==='layout'" :curves="curves" :terms="terms"/><InvestCompare v-else :curves="curves"/></div>
 </div>
</div></template>
<style scoped>
.investment-pane{background:#fff;border:1px solid #e6dfdb;border-radius:4px;padding:28px 30px 30px}
.analysis-loading{padding:80px;text-align:center;background:#fff;border-radius:4px;color:#6b6560}
@media(max-width:700px){.investment-pane{padding:20px 16px}}
</style>
