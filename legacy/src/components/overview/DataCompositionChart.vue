<template>
  <div class="composition-chart">
    <div class="chart-head">
      <h4>数据源构成</h4>
      <p>多源异构数据相对规模（对数刻度）</p>
    </div>
    <div ref="chartEl" class="chart-canvas"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { CHART } from '../../constants/chartTheme.js'

const props = defineProps({
  segments: { type: Array, default: () => [] },
})

const chartEl = ref(null)
let chart = null

function buildOption(segments) {
  const data = segments.map(s => ({
    name: s.label,
    value: Math.max(1, Math.log10(s.count + 1)),
    raw: s.count,
    itemStyle: { color: s.color },
  }))

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      ...CHART.tooltip,
      formatter: p => `${p.name}<br/>${formatRaw(p.data.raw)}`,
    },
    series: [{
      type: 'pie',
      radius: ['42%', '72%'],
      center: ['50%', '52%'],
      roseType: 'area',
      itemStyle: {
        borderRadius: 6,
        borderColor: '#ffffff',
        borderWidth: 2,
      },
      label: {
        color: '#4a4540',
        fontSize: 11,
        formatter: '{b}',
      },
      labelLine: {
        lineStyle: { color: '#c4c0ba' },
      },
      emphasis: {
        scaleSize: 8,
        itemStyle: { shadowBlur: 12, shadowColor: 'rgba(174,13,40,0.25)' },
      },
      data,
    }],
  }
}

function formatRaw(n) {
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万+ 条`
  return `${n.toLocaleString()} 条`
}

function render() {
  if (!chartEl.value) return
  if (!chart) chart = echarts.init(chartEl.value)
  chart.setOption(buildOption(props.segments), true)
}

watch(() => props.segments, render, { deep: true })
onMounted(() => {
  render()
  window.addEventListener('resize', () => chart?.resize())
})
onBeforeUnmount(() => {
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.composition-chart {
  padding: 16px 18px;
  border-radius: 14px;
  background: var(--surface-card);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
  height: 100%;
  min-height: 280px;
  display: flex;
  flex-direction: column;
}
.chart-head h4 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--label-strong);
}
.chart-head p {
  margin: 4px 0 0;
  font-size: 0.72rem;
  color: var(--label-muted);
}
.chart-canvas {
  flex: 1;
  min-height: 220px;
}
</style>
