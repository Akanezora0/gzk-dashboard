<template>
  <div class="chain-page">
    <div class="chain-toolbar">
      <div class="toolbar-group">
        <span class="toolbar-label">链路</span>
        <button v-for="t in chainTypes" :key="t.id" type="button" class="tab"
          :class="{ active: chainType === t.id }" @click="switchChain(t.id)">{{ t.label }}</button>
      </div>
      <div class="toolbar-group">
        <span class="toolbar-label">布局</span>
        <button v-for="l in layouts" :key="l.id" type="button" class="tab sm"
          :class="{ active: layout === l.id }" @click="switchLayout(l.id)">{{ l.label }}</button>
      </div>
      <div class="toolbar-group filters">
        <label v-for="nt in nodeTypes" :key="nt.id" class="filter-chip">
          <input v-model="nt.show" type="checkbox" @change="applyFilter" />
          <span class="dot" :style="{ background: nt.color }"></span>{{ nt.label }}
        </label>
      </div>
      <div class="toolbar-meta">{{ metaSummary }}</div>
    </div>

    <div class="chain-body">
      <ScreenPanel title="证据链图谱" :subtitle="chainSubtitle" class="graph-wrap">
        <div class="legend">
          <span><i class="leg verified"></i>已验证</span>
          <span><i class="leg candidate"></i>候选/部分</span>
        </div>
        <div ref="graphEl" class="graph-canvas"></div>
      </ScreenPanel>

      <ScreenPanel title="证据详情" subtitle="点击节点或边查看" class="detail-wrap">
        <div v-if="!selectedNode && !selectedEdge" class="empty-detail">
          <p>点击图中节点查看基本信息与关联统计</p>
          <p>点击边查看匹配置信度与匹配方式</p>
          <div class="type-legend">
            <div v-for="nt in nodeTypes" :key="nt.id" class="tl-row">
              <span class="dot" :style="{ background: nt.color }"></span>{{ nt.label }}
            </div>
          </div>
        </div>
        <div v-else-if="selectedNode" class="detail-content">
          <div class="detail-type">{{ typeLabel(selectedNode.type) }}</div>
          <h3>{{ selectedNode.label }}</h3>
          <dl>
            <template v-if="selectedNode.year"><dt>年份</dt><dd>{{ selectedNode.year }}</dd></template>
            <template v-if="selectedNode.patent_count"><dt>专利命中</dt><dd>{{ selectedNode.patent_count }}</dd></template>
            <template v-if="selectedNode.status"><dt>状态</dt><dd><span class="tag" :class="tagClass(selectedNode.status)">{{ selectedNode.status }}</span></dd></template>
          </dl>
          <div v-if="neighborCount > 0" class="neighbor-hint">关联 {{ neighborCount }} 个节点（已高亮）</div>
        </div>
        <div v-else class="detail-content">
          <div class="detail-type">关系边</div>
          <h3>{{ edgeTypeLabel(selectedEdge.type) }}</h3>
          <dl>
            <dt>置信度</dt>
            <dd>
              <div class="conf-bar"><div class="conf-fill" :style="{ width: `${(selectedEdge.confidence || 0) * 100}%` }"></div></div>
              {{ ((selectedEdge.confidence || 0) * 100).toFixed(0) }}%
            </dd>
            <dt>匹配方式</dt><dd>{{ matchLabel(selectedEdge.match_method) }}</dd>
          </dl>
        </div>
      </ScreenPanel>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { Graph } from '@antv/g6'
import ScreenPanel from '../components/screen/ScreenPanel.vue'
import { CANVAS_LABEL } from '../constants/chartTheme.js'

const route = useRoute()
const graphEl = ref(null)
const chainType = ref(route.query.chain_type || 'fund_paper_tech')
const layout = ref('force')
const selectedNode = ref(null)
const selectedEdge = ref(null)
const neighborCount = ref(0)
const rawData = ref({ nodes: [], edges: [], meta: {} })
let graph = null

const chainTypes = [
  { id: 'fund_paper_tech', label: '基金—论文—技术' },
  { id: 'patent_tech', label: '专利—技术' },
]
const layouts = [
  { id: 'force', label: '力导向' },
  { id: 'dagre', label: '层级' },
  { id: 'radial', label: '辐射' },
]
const nodeTypes = reactive([
  { id: 'fund', label: '基金', color: '#6366f1', show: true },
  { id: 'paper', label: '论文', color: '#3d8bfd', show: true },
  { id: 'patent', label: '专利', color: '#f59e0b', show: true },
  { id: 'tech_point', label: '技术点', color: '#22c55e', show: true },
])

const NODE_COLORS = Object.fromEntries(nodeTypes.map(n => [n.id, n.color]))

const chainSubtitle = computed(() =>
  chainType.value === 'fund_paper_tech' ? '基金资助 → 论文成果 → 技术点' : '专利成果 → 技术归类'
)
const metaSummary = computed(() => {
  const m = rawData.value.meta || {}
  if (chainType.value === 'patent_tech') return `专利—技术链 ${fmtCount(m.patent_tech_links || rawData.value.edges?.length)} 条`
  return `基金—论文对 ${m.fund_paper_pairs ?? '—'} 组`
})

function typeLabel(t) {
  return { fund: '基金项目', paper: '论文', patent: '专利', tech_point: '技术点' }[t] || t
}
function edgeTypeLabel(t) {
  return { fund_supports: '基金资助', paper_hits_tech: '论文命中技术', patent_hits_tech: '专利命中技术' }[t] || t
}
function matchLabel(m) {
  return { direct_mapping: '直接映射', semantic_match: '语义匹配', rule_match: '规则匹配' }[m] || m
}
function tagClass(s) {
  if (s === 'verified') return 'green'
  if (s === 'candidate' || s === 'partial') return 'yellow'
  return 'red'
}

function filteredGraphData() {
  const showTypes = new Set(nodeTypes.filter(n => n.show).map(n => n.id))
  const nodes = (rawData.value.nodes || []).filter(n => showTypes.has(n.type))
  const nodeIds = new Set(nodes.map(n => n.id))
  const edges = (rawData.value.edges || []).filter(e => nodeIds.has(e.source) && nodeIds.has(e.target))
  return {
    nodes: nodes.map(n => ({ id: n.id, data: { ...n, label: (n.label || n.id).slice(0, 18) } })),
    edges: edges.map((e, i) => ({ id: `e${i}`, source: e.source, target: e.target, data: e })),
  }
}

function layoutConfig() {
  if (layout.value === 'dagre') return { type: 'dagre', rankdir: 'LR', nodeSep: 40, rankSep: 80 }
  if (layout.value === 'radial') return { type: 'radial', unitRadius: 120, preventOverlap: true }
  return { type: 'force', preventOverlap: true, linkDistance: 100, nodeStrength: -80 }
}

function highlightNeighbors(nodeId) {
  if (!graph || !nodeId) return
  const related = new Set([nodeId])
  for (const e of rawData.value.edges || []) {
    if (e.source === nodeId) related.add(e.target)
    if (e.target === nodeId) related.add(e.source)
  }
  neighborCount.value = related.size - 1
  graph.updateNodeData(
    (rawData.value.nodes || []).map(n => ({
      id: n.id,
      style: {
        opacity: related.has(n.id) ? 1 : 0.2,
        lineWidth: related.has(n.id) ? 2 : 0,
        stroke: related.has(n.id) ? '#ffffff' : 'transparent',
      },
    }))
  )
  graph.draw?.()
}

async function renderGraph() {
  if (!graphEl.value) return
  if (graph) graph.destroy()

  const { nodes, edges } = filteredGraphData()
  graph = new Graph({
    container: graphEl.value,
    width: graphEl.value.clientWidth,
    height: 560,
    data: { nodes, edges },
    layout: layoutConfig(),
    node: {
      style: {
        fill: d => NODE_COLORS[d.data.type] || '#64748b',
        labelText: d => d.data.label,
        labelFill: CANVAS_LABEL.secondary,
        labelPlacement: 'right',
        labelFontSize: 10,
        size: d => d.data.type === 'tech_point' ? 32 : 24,
      },
    },
    edge: {
      style: {
        stroke: d => (d.data.confidence >= 0.9 ? '#22c55e' : '#f59e0b'),
        lineWidth: 1.5,
        endArrow: true,
        opacity: 0.7,
      },
    },
    behaviors: ['drag-canvas', 'zoom-canvas', 'drag-element'],
  })

  graph.on('node:click', evt => {
    const d = evt.target?.data
    selectedNode.value = d || null
    selectedEdge.value = null
    if (d?.id) highlightNeighbors(d.id)
  })
  graph.on('edge:click', evt => {
    selectedEdge.value = evt.target?.data || null
    selectedNode.value = null
    neighborCount.value = 0
  })
  graph.on('canvas:click', () => {
    selectedNode.value = null
    selectedEdge.value = null
    neighborCount.value = 0
    applyFilter()
  })

  await graph.render()
}

async function loadGraph() {
  rawData.value = await apiGet(`/api/chain?chain_type=${chainType.value}&limit=100`)
  selectedNode.value = null
  selectedEdge.value = null
  neighborCount.value = 0
  await nextTick()
  await renderGraph()
}

function applyFilter() { renderGraph() }
function switchChain(t) { chainType.value = t; loadGraph() }
function switchLayout(l) { layout.value = l; renderGraph() }

function onResize() { graph?.resize?.() }

onMounted(async () => {
  await loadGraph()
  window.addEventListener('resize', onResize)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  graph?.destroy()
})
</script>

<style scoped>
.chain-page { display: flex; flex-direction: column; gap: 10px; }
.chain-toolbar {
  display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
  padding: 10px 14px;
  background: rgba(15, 30, 55, 0.6);
  border: 1px solid rgba(61, 139, 253, 0.15);
  border-radius: 8px;
}
.toolbar-group { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.toolbar-label { font-size: 0.72rem; color: #64748b; margin-right: 4px; }
.tab {
  background: rgba(36, 48, 68, 0.8); border: 1px solid var(--border);
  color: #94a3b8; padding: 5px 12px; border-radius: 6px; cursor: pointer; font-size: 0.78rem;
}
.tab.sm { padding: 4px 10px; font-size: 0.72rem; }
.tab.active { background: rgba(61,139,253,0.25); border-color: #3d8bfd; color: #fff; }
.filter-chip {
  display: flex; align-items: center; gap: 4px;
  font-size: 0.72rem; color: #94a3b8; cursor: pointer;
  padding: 4px 8px; border-radius: 4px; background: rgba(10,20,40,0.5);
}
.filter-chip input { accent-color: #3d8bfd; }
.dot { width: 8px; height: 8px; border-radius: 50%; }
.toolbar-meta { margin-left: auto; font-size: 0.72rem; color: #64748b; }

.chain-body { display: grid; grid-template-columns: 1fr 280px; gap: 10px; min-height: 600px; }
.graph-wrap { min-height: 600px; }
.graph-canvas {
  width: 100%;
  height: 560px;
  background:
    radial-gradient(ellipse at 40% 50%, rgba(174, 13, 40, 0.04) 0%, transparent 55%),
    #faf9f7;
  border-radius: 6px;
}
.legend { display: flex; gap: 14px; font-size: 0.72rem; color: #64748b; margin-bottom: 6px; }
.leg { display: inline-block; width: 12px; height: 3px; margin-right: 4px; vertical-align: middle; }
.leg.verified { background: #22c55e; }
.leg.candidate { background: #f59e0b; }

.detail-wrap { min-height: 600px; }
.empty-detail { color: #64748b; font-size: 0.82rem; line-height: 1.6; padding: 1rem 0; }
.empty-detail p { margin-bottom: 8px; }
.type-legend { margin-top: 1rem; }
.tl-row { display: flex; align-items: center; gap: 8px; padding: 4px 0; font-size: 0.78rem; }
.detail-content h3 { font-size: 0.9rem; color: #e2e8f0; margin: 6px 0 10px; line-height: 1.4; }
.detail-type { font-size: 0.72rem; color: #3d8bfd; font-weight: 600; }
.detail-content dl { font-size: 0.8rem; }
.detail-content dt { color: #64748b; margin-top: 8px; }
.detail-content dd { color: #e2e8f0; margin-top: 2px; }
.conf-bar { height: 6px; background: #1e293b; border-radius: 3px; margin: 4px 0; overflow: hidden; }
.conf-fill { height: 100%; background: linear-gradient(90deg, #3d8bfd, #22c55e); border-radius: 3px; }
.neighbor-hint { margin-top: 12px; font-size: 0.72rem; color: #22c55e; }

@media (max-width: 900px) { .chain-body { grid-template-columns: 1fr; } }
</style>
