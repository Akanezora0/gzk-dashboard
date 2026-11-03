<template>
  <div class="data-page">
    <div class="data-header">
      <div>
        <h2>{{ pageTitle }}</h2>
        <p>{{ pageDesc }}</p>
      </div>
      <router-link to="/overview" class="back-link">← 返回总览</router-link>
    </div>

    <div v-if="card" class="kpi-strip">
      <MetricFlop :value="card.count" :label="'数据总量'" :en="card.name_en" color="#3d8bfd" />
      <div class="kpi-static">
        <div class="ks-val">{{ card.year_range }}</div>
        <div class="ks-label">时间范围</div>
      </div>
      <div class="kpi-static">
        <div class="ks-val" :class="card.status">{{ card.status }}</div>
        <div class="ks-label">数据状态</div>
      </div>
    </div>

    <div v-if="embedUrl" class="embed-wrap">
      <iframe :src="embedUrl" frameborder="0" allowfullscreen title="DataEase BI" />
    </div>

    <div v-else class="bi-grid">
      <ScreenPanel title="趋势概览" subtitle="快照数据 · 待 DataEase 接入">
        <div ref="trendChart" class="chart-box"></div>
      </ScreenPanel>
      <ScreenPanel title="分布结构" subtitle="探索性统计">
        <div ref="distChart" class="chart-box"></div>
      </ScreenPanel>
      <ScreenPanel title="DataEase 配置指引" class="guide-panel">
        <ol class="guide-list">
          <li>启动：<code>cd dashboard/dataease && docker compose up -d</code></li>
          <li>访问 http://localhost:8100 创建看板</li>
          <li>连接 SQLite：<code>tech_offer_supply.db</code> 或 CSV 数据源</li>
          <li>将分享链接写入 <code>dashboard/api/config.yaml</code></li>
        </ol>
        <p class="guide-note">配置完成后本页将自动嵌入 DataEase iframe，替代下方占位图表。</p>
      </ScreenPanel>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import ScreenPanel from '../components/screen/ScreenPanel.vue'
import MetricFlop from '../components/screen/MetricFlop.vue'
import { apiGet } from '../composables/useApi'

const route = useRoute()
const overview = ref(null)
const trendChart = ref(null)
const distChart = ref(null)
let trendInst = null
let distInst = null

const dataType = computed(() => route.params.type)

const meta = {
  patent: { title: '专利申请授权数据', desc: '年度申请/授权趋势 · 授权率 · 地域分布 · IPC 分类', color: '#3d8bfd' },
  paper: { title: '学术研究论文库', desc: '年度发文 · 期刊 Top10 · 被引分档 · 基金支持占比', color: '#60a5fa' },
  business: { title: '工商企业注册信息', desc: '省份分布 · 成立年份 · 产业链节点企业', color: '#a78bfa' },
  policy: { title: '政策法规文库', desc: '政策时间线 · 工具类型 · 支持阶段', color: '#22c55e' },
  news: { title: '近期新闻资讯', desc: '产业动态 · 事件感知', color: '#f59e0b' },
  job: { title: '招聘岗位信息', desc: '人才需求 · 技能分布', color: '#ec4899' },
  video: { title: '短视频平台数据', desc: '传播热度 · 话题分布', color: '#14b8a6' },
  fund: { title: '基金项目库', desc: '立项年份 · 学科分布 · 支撑论文数', color: '#6366f1' },
}

const pageTitle = computed(() => meta[dataType.value]?.title || dataType.value)
const pageDesc = computed(() => meta[dataType.value]?.desc || '数据分析看板')
const card = computed(() => overview.value?.data_cards?.find(c => c.type === dataType.value))
const embedUrl = computed(() => '')

function mockTrendYears() {
  return ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
}

function renderCharts() {
  const base = card.value?.count || 1000
  const scale = Math.log10(Math.max(base, 100))
  const trend = mockTrendYears().map((_, i) => Math.round(base * (0.3 + i * 0.1) / 8))

  if (trendChart.value) {
    trendInst?.dispose()
    trendInst = echarts.init(trendChart.value)
    trendInst.setOption({
      backgroundColor: 'transparent',
      grid: { left: 50, right: 20, top: 20, bottom: 30 },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: mockTrendYears(), axisLabel: { color: '#94a3b8' } },
      yAxis: { type: 'value', axisLabel: { color: '#94a3b8' }, splitLine: { lineStyle: { color: '#1e293b' } } },
      series: [{
        type: 'line', data: trend, smooth: true,
        areaStyle: { color: 'rgba(61,139,253,0.15)' },
        lineStyle: { color: meta[dataType.value]?.color || '#3d8bfd', width: 2 },
        itemStyle: { color: meta[dataType.value]?.color || '#3d8bfd' },
      }],
    })
  }

  if (distChart.value) {
    distInst?.dispose()
    distInst = echarts.init(distChart.value)
    const pieData = [
      { name: '华东', value: Math.round(scale * 25) },
      { name: '华南', value: Math.round(scale * 18) },
      { name: '华北', value: Math.round(scale * 15) },
      { name: '西南', value: Math.round(scale * 12) },
      { name: '其他', value: Math.round(scale * 30) },
    ]
    distInst.setOption({
      backgroundColor: 'transparent',
      tooltip: { trigger: 'item' },
      legend: { orient: 'vertical', right: 10, top: 'center', textStyle: { color: '#94a3b8', fontSize: 11 } },
      series: [{
        type: 'pie', radius: ['40%', '65%'], center: ['40%', '50%'],
        data: pieData,
        label: { color: '#94a3b8', fontSize: 10 },
        itemStyle: { borderRadius: 4, borderColor: '#0a1020', borderWidth: 2 },
      }],
    })
  }
}

onMounted(async () => {
  try { overview.value = await apiGet('/api/overview') } catch { /* ignore */ }
  await nextTick()
  renderCharts()
  window.addEventListener('resize', () => { trendInst?.resize(); distInst?.resize() })
})
onBeforeUnmount(() => { trendInst?.dispose(); distInst?.dispose() })
</script>

<style scoped>
.data-page { display: flex; flex-direction: column; gap: 10px; }
.data-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  padding: 10px 14px;
  background: rgba(15, 30, 55, 0.6);
  border: 1px solid rgba(61, 139, 253, 0.15);
  border-radius: 8px;
}
.data-header h2 { font-size: 1rem; color: #e2e8f0; }
.data-header p { font-size: 0.75rem; color: #64748b; margin-top: 4px; }
.back-link { font-size: 0.78rem; color: #3d8bfd; text-decoration: none; }
.back-link:hover { text-decoration: underline; }

.kpi-strip {
  display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;
}
.kpi-static {
  text-align: center; padding: 14px;
  background: rgba(15,30,55,0.6); border-radius: 8px;
  border: 1px solid var(--border);
}
.ks-val { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; }
.ks-val.available { color: #22c55e; }
.ks-label { font-size: 0.68rem; color: #64748b; margin-top: 4px; }

.bi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 10px;
}
.guide-panel { grid-column: 1 / -1; }
.chart-box { width: 100%; height: 280px; }
.embed-wrap iframe { width: 100%; height: 75vh; border-radius: 8px; background: #111; }

.guide-list { padding-left: 1.2rem; font-size: 0.82rem; color: #94a3b8; line-height: 1.8; }
.guide-list code {
  background: rgba(36,48,68,0.8); padding: 2px 6px; border-radius: 4px;
  font-size: 0.75rem; color: #3d8bfd;
}
.guide-note { font-size: 0.72rem; color: #64748b; margin-top: 10px; }

@media (max-width: 900px) {
  .kpi-strip, .bi-grid { grid-template-columns: 1fr; }
  .guide-panel { grid-column: auto; }
}
</style>
