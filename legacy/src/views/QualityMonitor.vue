<template>
  <PageShell
    :title="PAGE_META.quality.title"
    :intro="PAGE_META.quality.intro"
    :breadcrumb="PAGE_META.quality.breadcrumb"
  >
    <div v-if="loading" class="loading">加载中…</div>
    <div v-else class="quality-page">
    <!-- 状态概览 -->
    <div class="status-grid">
      <div v-for="s in statusCards" :key="s.label" class="status-card" :style="{ '--accent': s.color }">
        <div class="sc-val">{{ s.val }}</div>
        <div class="sc-label">{{ s.label }}</div>
        <div class="sc-bar"><div class="sc-fill" :style="{ width: s.pct + '%' }"></div></div>
      </div>
    </div>

    <!-- 链路状态 -->
    <ScreenPanel title="链路状态矩阵" subtitle="已完成 / 候选 / 待补齐">
      <div class="chain-grid">
        <div v-for="ch in data.chain_status" :key="ch.chain_type" class="chain-card" :class="ch.status">
          <div class="cc-head">
            <span class="status-light" :class="ch.status"></span>
            <span class="cc-name">{{ ch.label }}</span>
          </div>
          <div class="cc-count">{{ fmtCount(ch.count) }}</div>
          <div class="cc-meta">
            <span class="tag" :class="tagClass(ch.status)">{{ ch.status }}</span>
            <span class="conf">{{ ch.confidence }}</span>
          </div>
          <div class="cc-note">{{ ch.note }}</div>
        </div>
      </div>
    </ScreenPanel>

    <div class="dual-row">
      <!-- 缺失率 -->
      <ScreenPanel title="字段缺失率" subtitle="抽样数据源">
        <div ref="missingChart" class="chart-box"></div>
      </ScreenPanel>
      <!-- 进展 -->
      <ScreenPanel title="项目进展" subtitle="迭代状态">
        <div v-for="(items, key) in data.quality_tasks" :key="key" class="progress-section">
          <div class="ps-title" :class="key">{{ labels[key] }}</div>
          <ul>
            <li v-for="(item, i) in items" :key="i">{{ item }}</li>
          </ul>
        </div>
      </ScreenPanel>
    </div>
    </div>
  </PageShell>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import PageShell from '../components/layout/PageShell.vue'
import ScreenPanel from '../components/screen/ScreenPanel.vue'
import { PAGE_META } from '../constants/site.js'
import { apiGet, fmtCount } from '../composables/useApi'

const loading = ref(true)
const data = ref({})
const missingChart = ref(null)
let chartInst = null
const labels = { completed: '已完成', in_progress: '进行中', pending: '待补齐' }

const statusCards = computed(() => {
  const s = data.value.sqlite_counts || {}
  const maxPatent = s.dim_patent || 1
  return [
    { label: '回补队列', val: (data.value.reject_queue_size || 0).toLocaleString(), color: '#ef4444', pct: Math.min(100, (data.value.reject_queue_size || 0) / 1000) },
    { label: '基金项目', val: (s.dim_fund_project || 0).toLocaleString(), color: '#6366f1', pct: 100 },
    { label: '论文入库', val: (s.dim_paper || 0).toLocaleString(), color: '#3d8bfd', pct: Math.min(100, (s.dim_paper || 0) / 50) },
    { label: '专利入库', val: fmtCount(s.dim_patent), color: '#f59e0b', pct: Math.min(100, (s.dim_patent || 0) / maxPatent * 100) },
    { label: '基金—论文链', val: (s.fact_fund_paper_link || 0).toLocaleString(), color: '#22c55e', pct: Math.min(100, (s.fact_fund_paper_link || 0) / 12) },
    { label: '专利—技术链', val: fmtCount(s.fact_patent_tech_link), color: '#14b8a6', pct: Math.min(100, (s.fact_patent_tech_link || 0) / 300) },
  ]
})

function tagClass(s) {
  if (s === 'verified') return 'green'
  if (s === 'candidate' || s === 'partial') return 'yellow'
  return 'red'
}

function renderMissingChart() {
  if (!missingChart.value) return
  chartInst?.dispose()
  chartInst = echarts.init(missingChart.value)
  const rows = []
  for (const r of data.value.missing_rate_report || []) {
    for (const f of (r.field_stats || [])) {
      if (f.missing_ratio_pct > 0) rows.push({ name: `${r.name}.${f.field}`, pct: f.missing_ratio_pct })
    }
  }
  const top = rows.sort((a, b) => b.pct - a.pct).slice(0, 8)
  chartInst.setOption({
    backgroundColor: 'transparent',
    grid: { left: 120, right: 30, top: 10, bottom: 20 },
    xAxis: { type: 'value', max: 100, axisLabel: { color: '#94a3b8', formatter: '{value}%' }, splitLine: { lineStyle: { color: '#1e293b' } } },
    yAxis: { type: 'category', data: top.map(r => r.name.slice(0, 20)), axisLabel: { color: '#94a3b8', fontSize: 10 } },
    series: [{
      type: 'bar',
      data: top.map(r => r.pct),
      itemStyle: {
        color: (p) => p.value > 10 ? '#ef4444' : p.value > 1 ? '#f59e0b' : '#22c55e',
        borderRadius: [0, 4, 4, 0],
      },
    }],
  })
}

onMounted(async () => {
  data.value = await apiGet('/api/quality')
  loading.value = false
  await nextTick()
  renderMissingChart()
  window.addEventListener('resize', () => chartInst?.resize())
})
onBeforeUnmount(() => chartInst?.dispose())
</script>

<style scoped>
.loading { text-align: center; padding: 3rem; color: #64748b; }
.quality-page { display: flex; flex-direction: column; gap: 10px; }

.status-grid {
  display: grid; grid-template-columns: repeat(6, 1fr); gap: 8px;
}
.status-card {
  padding: 12px 10px; border-radius: 8px;
  background: rgba(15, 30, 55, 0.7);
  border: 1px solid rgba(255,255,255,0.06);
  border-top: 3px solid var(--accent);
}
.sc-val { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; }
.sc-label { font-size: 0.68rem; color: #64748b; margin-top: 2px; }
.sc-bar { height: 3px; background: #1e293b; border-radius: 2px; margin-top: 8px; overflow: hidden; }
.sc-fill { height: 100%; background: var(--accent); border-radius: 2px; transition: width 0.5s; }

.chain-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
.chain-card {
  padding: 12px; border-radius: 8px;
  background: rgba(10, 20, 40, 0.6);
  border: 1px solid var(--border);
}
.chain-card.verified { border-left: 3px solid #22c55e; }
.chain-card.candidate, .chain-card.partial { border-left: 3px solid #f59e0b; }
.cc-head { display: flex; align-items: center; gap: 8px; }
.status-light { width: 8px; height: 8px; border-radius: 50%; }
.status-light.verified { background: #22c55e; box-shadow: 0 0 6px #22c55e; }
.status-light.candidate, .status-light.partial { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
.cc-name { font-size: 0.82rem; color: #e2e8f0; font-weight: 600; }
.cc-count { font-size: 1.4rem; font-weight: 700; color: #3d8bfd; margin: 6px 0; }
.cc-meta { display: flex; gap: 8px; align-items: center; font-size: 0.72rem; }
.conf { color: #64748b; }
.cc-note { font-size: 0.68rem; color: #64748b; margin-top: 6px; }

.dual-row { display: grid; grid-template-columns: 1.2fr 1fr; gap: 10px; }
.chart-box { width: 100%; height: 260px; }
.progress-section { margin-bottom: 12px; }
.ps-title { font-size: 0.78rem; font-weight: 600; margin-bottom: 4px; }
.ps-title.completed { color: #22c55e; }
.ps-title.in_progress { color: #f59e0b; }
.ps-title.pending { color: #64748b; }
.progress-section ul { padding-left: 1rem; font-size: 0.72rem; color: #94a3b8; line-height: 1.6; }

@media (max-width: 1100px) {
  .status-grid { grid-template-columns: repeat(3, 1fr); }
  .chain-grid, .dual-row { grid-template-columns: 1fr; }
}
</style>
