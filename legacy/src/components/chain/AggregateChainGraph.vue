<template>
  <div class="aggregate-graph">
    <div ref="chartEl" class="chart-canvas"></div>
    <div v-if="metaText" class="graph-meta">{{ metaText }}</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { apiGet, fmtCount } from '../../composables/useApi'
import { CHAIN_NODE_META } from '../../constants/chainHubContent.js'
import { CHART, CANVAS_LABEL, EVIDENCE_EDGE_COLORS } from '../../constants/chartTheme.js'

const props = defineProps({
  chainType: { type: String, default: 'aggregate_overview' },
  aggregate: { type: Boolean, default: true },
})

const chartEl = ref(null)
const raw = ref({ nodes: [], edges: [], meta: {} })
let inst = null

const TYPE_LAYOUT = {
  fund: { x: 80, y: 180 },
  paper: { x: 280, y: 100 },
  patent: { x: 280, y: 260 },
  tech_point: { x: 480, y: 180 },
  product: { x: 680, y: 180 },
  industry: { x: 880, y: 180 },
}

const metaText = computed(() => {
  const m = raw.value.meta || {}
  if (props.chainType === 'patent_tech') {
    return `专利—技术关联 ${fmtCount(m.patent_tech_links || raw.value.edges?.length)} 条`
  }
  if (props.aggregate) {
    return `基金—论文 ${fmtCount(m.fund_paper_pairs)} 组 · 专利—技术 ${fmtCount(m.patent_tech_links)} 条 · 聚合视图`
  }
  return `基金—论文对 ${fmtCount(m.fund_paper_pairs)} 组`
})

function nodeLabel(n) {
  const cnt = n.count ?? n.patent_count
  const base = (n.label || n.id).slice(0, 12)
  return cnt != null ? `${base}\n(${fmtCount(cnt)})` : base
}

function buildGraphOption() {
  const nodes = raw.value.nodes || []
  const edges = raw.value.edges || []
  const categories = [...new Set(nodes.map(n => n.type))].map(t => ({ name: t }))

  const eNodes = nodes.map((n, i) => {
    const layout = TYPE_LAYOUT[n.type] || { x: 100 + i * 120, y: 180 }
    const color = CHAIN_NODE_META[n.type]?.color || '#78716c'
    return {
      id: n.id,
      name: nodeLabel(n),
      x: layout.x,
      y: layout.y,
      symbolSize: n.type === 'tech_point' ? 58 : 48,
      category: categories.findIndex(c => c.name === n.type),
      itemStyle: { color, borderColor: '#ffffff', borderWidth: 1.5 },
      label: {
        show: true,
        position: 'inside',
        color: CANVAS_LABEL.onNode,
        fontSize: 11,
        lineHeight: 14,
        fontWeight: 600,
      },
    }
  })

  const eLinks = edges.map(e => ({
    source: e.source,
    target: e.target,
    lineStyle: {
      color: EVIDENCE_EDGE_COLORS[e.type] || '#78716c',
      width: 2,
      curveness: props.chainType === 'patent_tech' ? 0.15 : 0.2,
    },
  }))

  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', ...CHART.tooltip },
    series: [{
      type: 'graph',
      layout: 'none',
      roam: true,
      draggable: false,
      data: eNodes,
      links: eLinks,
      categories,
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: 8,
      emphasis: { focus: 'adjacency', lineStyle: { width: 4 } },
    }],
  }
}

async function load() {
  const q = new URLSearchParams({
    chain_type: props.chainType,
    limit: '30',
    aggregate: props.aggregate ? 'true' : 'false',
  })
  raw.value = await apiGet(`/api/chain?${q}`)
  await nextTick()
  render()
}

function render() {
  if (!chartEl.value) return
  inst?.dispose()
  inst = echarts.init(chartEl.value)
  inst.setOption(buildGraphOption())
}

function onResize() { inst?.resize() }

watch(() => [props.chainType, props.aggregate], load)

onMounted(async () => {
  await load()
  window.addEventListener('resize', onResize)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  inst?.dispose()
})
</script>

<style scoped>
.aggregate-graph { width: 100%; }
.chart-canvas {
  width: 100%;
  height: 360px;
  background:
    radial-gradient(ellipse at 40% 50%, rgba(174, 13, 40, 0.04) 0%, transparent 55%),
    #faf9f7;
  border-radius: 6px;
}
.graph-meta {
  text-align: center;
  font-size: 0.72rem;
  color: var(--muted, #78716c);
  margin-top: 6px;
}
</style>
