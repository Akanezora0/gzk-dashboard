<template>
  <div class="contrib-panel">
    <ScreenPanel title="筛选条件" subtitle="按技术大类与年份切片">
      <div class="filter-row">
        <label>技术大类
          <select v-model="filters.tech_layer" class="select" @change="load">
            <option value="">全部</option>
            <option v-for="l in layers" :key="l" :value="l">{{ l }}</option>
          </select>
        </label>
        <label>起始年 <input v-model.number="filters.year_start" type="number" class="input" @change="load" /></label>
        <label>结束年 <input v-model.number="filters.year_end" type="number" class="input" @change="load" /></label>
        <button type="button" class="btn-reset" @click="resetFilters">重置</button>
      </div>
    </ScreenPanel>

    <div class="layer-sections">
      <ScreenPanel title="支撑范围" subtitle="基金支撑覆盖范围" class="layer-panel">
        <div class="metric-grid">
          <div v-for="m in coverageMetrics" :key="m.label" class="metric-cell">
            <div class="mc-val" :style="{ color: m.color }">{{ m.val }}</div>
            <div class="mc-label">{{ m.label }}</div>
          </div>
        </div>
      </ScreenPanel>
      <ScreenPanel title="影响力度" subtitle="成果影响力" class="layer-panel">
        <div class="metric-grid">
          <div v-for="m in impactMetrics" :key="m.label" class="metric-cell">
            <div class="mc-val" :style="{ color: m.color }">{{ m.val }}</div>
            <div class="mc-label">{{ m.label }}</div>
          </div>
        </div>
      </ScreenPanel>
      <ScreenPanel title="产业渗透" subtitle="进行中" class="layer-panel diffusion">
        <div class="diffusion-placeholder">
          <span class="status-badge">in_progress</span>
          <p>{{ data?.diffusion?.note || '产业渗透指标后续接入证据链复用统计' }}</p>
        </div>
      </ScreenPanel>
    </div>

    <div class="charts-row">
      <ScreenPanel title="贡献维度雷达" subtitle="支撑范围 · 影响力度 · 产业渗透" class="chart-panel">
        <div ref="radarChart" class="chart-box"></div>
      </ScreenPanel>
      <ScreenPanel title="按技术大类分布" subtitle="文献规模与基金支撑占比" class="chart-panel">
        <div ref="barChart" class="chart-box"></div>
      </ScreenPanel>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import ScreenPanel from '../screen/ScreenPanel.vue'
import { apiGet } from '../../composables/useApi'
import {
  CHART, METRIC_CARD_COLORS, RUC_PALETTE, LAYER_COLORS, chartXAxis, chartYAxis,
} from '../../constants/chartTheme.js'

const data = ref(null)
const radarChart = ref(null)
const barChart = ref(null)
let radarInst = null
let barInst = null

const layers = [
  '平台构型与结构', '飞控导航与自主', '感知避障与数据',
  '能源动力与链路', '任务载荷与作业', '安全运维与地面',
]

const LAYER_BAR_COLORS = [
  LAYER_COLORS.layer_airframe,
  LAYER_COLORS.layer_control,
  LAYER_COLORS.layer_sense,
  LAYER_COLORS.layer_power,
  LAYER_COLORS.layer_payload,
  LAYER_COLORS.layer_safety,
]

const filters = reactive({ tech_layer: '', year_start: null, year_end: null })

const coverageMetrics = computed(() => {
  const c = data.value?.coverage || {}
  const cols = METRIC_CARD_COLORS
  return [
    { label: '基金支撑论文', val: c.fund_supported_papers ?? '—', color: cols[0] },
    { label: '基金支撑占比', val: pct(c.fund_supported_ratio), color: cols[1] },
    { label: '覆盖技术点', val: c.covered_tech_points ?? '—', color: cols[2] },
    { label: '覆盖技术大类', val: c.covered_tech_layers ?? '—', color: cols[3] },
  ]
})
const impactMetrics = computed(() => {
  const i = data.value?.impact || {}
  const cols = METRIC_CARD_COLORS
  return [
    { label: '平均被引', val: i.avg_citation ?? '—', color: cols[1] },
    { label: '高被引占比', val: pct(i.high_cite_ratio), color: cols[3] },
    { label: '基金支撑分', val: i.avg_funding_score ?? '—', color: cols[2] },
    { label: '总文献数', val: data.value?.coverage?.total_papers ?? '—', color: cols[0] },
  ]
})

function pct(v) { return v != null ? `${(v * 100).toFixed(1)}%` : '—' }

function resetFilters() {
  filters.tech_layer = ''
  filters.year_start = null
  filters.year_end = null
  load()
}

async function load() {
  const q = new URLSearchParams()
  if (filters.tech_layer) q.set('tech_layer', filters.tech_layer)
  if (filters.year_start) q.set('year_start', filters.year_start)
  if (filters.year_end) q.set('year_end', filters.year_end)
  data.value = await apiGet(`/api/contribution?${q}`)
  await nextTick()
  renderCharts()
}

function renderCharts() {
  renderRadar()
  renderBar()
}

function renderRadar() {
  if (!radarChart.value || !data.value) return
  radarInst?.dispose()
  radarInst = echarts.init(radarChart.value)
  const c = data.value.coverage || {}
  const i = data.value.impact || {}
  radarInst.setOption({
    backgroundColor: 'transparent',
    radar: {
      indicator: [
        { name: '基金占比', max: 100 },
        { name: '高被引', max: 100 },
        { name: '技术点覆盖', max: 100 },
        { name: '技术大类覆盖', max: 100 },
        { name: '基金支撑分', max: 1 },
      ],
      ...CHART.radar,
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          (c.fund_supported_ratio || 0) * 100,
          (i.high_cite_ratio || 0) * 100,
          ((c.covered_tech_points || 0) / 33) * 100,
          ((c.covered_tech_layers || 0) / 6) * 100,
          i.avg_funding_score || 0,
        ],
        name: '基金贡献',
        areaStyle: { color: 'rgba(174, 13, 40, 0.12)' },
        lineStyle: { color: RUC_PALETTE[0], width: 2 },
        itemStyle: { color: RUC_PALETTE[0] },
      }],
    }],
  })
}

function renderBar() {
  if (!barChart.value || !data.value?.by_layer) return
  barInst?.dispose()
  barInst = echarts.init(barChart.value)
  const rows = data.value.by_layer
  const fundLineData = rows.map(x => +(x.fund_ratio * 100).toFixed(1))
  const lineColor = RUC_PALETTE[1]
  barInst.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART.tooltip },
    legend: { data: ['文献数', '基金占比%'], ...CHART.legend, top: 0 },
    grid: { left: 50, right: 20, top: 36, bottom: 60 },
    xAxis: {
      ...chartXAxis(rows.map(x => x.tech_layer.replace('层', ''))),
      axisLabel: { ...CHART.axis, rotate: 25 },
    },
    yAxis: [
      chartYAxis(),
      {
        ...chartYAxis({ splitLine: { show: false } }),
        max: 100,
        axisLabel: { ...CHART.axis, formatter: '{value}%' },
      },
    ],
    series: [
      {
        name: '文献数',
        type: 'bar',
        z: 1,
        data: rows.map((x, i) => ({
          value: x.papers,
          itemStyle: { color: LAYER_BAR_COLORS[i % LAYER_BAR_COLORS.length], borderRadius: [4, 4, 0, 0] },
        })),
      },
      {
        name: '基金占比%',
        type: 'line',
        yAxisIndex: 1,
        z: 10,
        data: fundLineData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 9,
        itemStyle: {
          color: lineColor,
          borderColor: '#ffffff',
          borderWidth: 2.5,
          shadowColor: 'rgba(255, 255, 255, 0.9)',
          shadowBlur: 8,
        },
        lineStyle: {
          color: lineColor,
          width: 3,
          shadowColor: 'rgba(255, 255, 255, 0.88)',
          shadowBlur: 12,
          cap: 'round',
          join: 'round',
        },
      },
    ],
  })
}

function onResize() { radarInst?.resize(); barInst?.resize() }

function resizeCharts() {
  nextTick(() => {
    onResize()
    if (!radarInst && data.value) renderCharts()
  })
}

defineExpose({ resizeCharts })

onMounted(async () => {
  await load()
  window.addEventListener('resize', onResize)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  radarInst?.dispose()
  barInst?.dispose()
})
</script>

<style scoped>
.contrib-panel { display: flex; flex-direction: column; gap: 10px; }
.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  align-items: center;
  font-size: 0.82rem;
  color: var(--muted, #78716c);
}
.select, .input {
  margin-left: 6px;
  padding: 5px 8px;
  background: #ffffff;
  border: 1px solid var(--border, #e8e4df);
  border-radius: 4px;
  color: var(--text, #2a2a2a);
  font-size: 0.82rem;
}
.input { width: 72px; }
.btn-reset {
  padding: 5px 12px;
  background: rgba(174, 13, 40, 0.08);
  border: 1px solid rgba(174, 13, 40, 0.25);
  border-radius: 4px;
  color: var(--ruc-red, #ae0d28);
  cursor: pointer;
  font-size: 0.78rem;
  font-weight: 600;
}
.btn-reset:hover {
  background: rgba(174, 13, 40, 0.14);
  border-color: rgba(174, 13, 40, 0.4);
}
.layer-sections { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.metric-cell {
  text-align: center;
  padding: 10px 6px;
  background: var(--surface-panel, #faf9f7);
  border: 1px solid var(--border, #e8e4df);
  border-radius: 6px;
}
.mc-val { font-size: 1.15rem; font-weight: 700; }
.mc-label { font-size: 0.68rem; color: var(--muted, #78716c); margin-top: 2px; }
.diffusion-placeholder {
  text-align: center;
  padding: 1.5rem 1rem;
  color: var(--muted, #78716c);
  font-size: 0.82rem;
}
.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(180, 83, 9, 0.12);
  color: #b45309;
  font-size: 0.72rem;
  font-weight: 600;
  margin-bottom: 8px;
}
.charts-row { display: grid; grid-template-columns: 1fr 1.2fr; gap: 10px; }
.chart-box { width: 100%; height: 300px; }
@media (max-width: 1000px) {
  .layer-sections, .charts-row { grid-template-columns: 1fr; }
}
</style>
