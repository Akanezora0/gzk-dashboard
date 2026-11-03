<template>
  <div class="evidence-explorer">
    <div class="explorer-toolbar">
      <div class="tb-left">
        <span class="tb-title">{{ modeLabel }}</span>
        <span v-if="metaText" class="tb-meta">{{ metaText }}</span>
        <span v-if="usingFallback" class="tb-fallback">演示拓扑</span>
      </div>
      <div class="tb-controls">
        <button
          v-for="s in stageSteps"
          :key="s.id"
          type="button"
          class="stage-btn"
          :class="{ active: activeStage === s.id }"
          @click="setStage(s.id)"
        >
          {{ s.label }}
        </button>
        <label v-if="!aggregate" class="limit-ctrl">
          样本量
          <select v-model.number="sampleLimit" class="select-sm" @change="reload">
            <option :value="40">40</option>
            <option :value="60">60</option>
            <option :value="80">80</option>
          </select>
        </label>
        <button type="button" class="btn-icon" title="重置视图" @click="resetView">↺</button>
      </div>
    </div>

    <div class="explorer-body">
      <div class="graph-zone">
        <div ref="chartEl" class="chart-canvas"></div>
        <div v-if="loading" class="graph-loading">加载证据图…</div>
        <div v-else-if="!hasData" class="graph-loading">
          <span>暂无图数据</span>
          <button type="button" class="btn-retry" @click="reload">重新加载</button>
        </div>
        <div class="graph-hint">拖拽平移 · 滚轮缩放 · 点击节点/边查看证据详情</div>
      </div>

      <aside class="inspector" :class="{ open: !!inspectTarget }">
        <template v-if="inspectTarget">
          <div class="insp-head">
            <span class="insp-type" :style="{ color: inspectColor }">{{ inspectTypeLabel }}</span>
            <button type="button" class="insp-close" @click="clearInspect">×</button>
          </div>
          <h3 class="insp-title">{{ inspectTitle }}</h3>

          <template v-if="inspectTarget.kind === 'node'">
            <dl class="insp-dl">
              <template v-for="(val, key) in nodeFields" :key="key">
                <dt>{{ fieldLabel(key) }}</dt>
                <dd>{{ val }}</dd>
              </template>
            </dl>
            <div v-if="adjacentEdges.length" class="insp-links">
              <div class="insp-sub">关联证据 ({{ adjacentEdges.length }})</div>
              <button
                v-for="(e, i) in adjacentEdges.slice(0, 6)"
                :key="i"
                type="button"
                class="edge-chip"
                @click="selectEdge(e)"
              >
                <span class="ec-type">{{ edgeMeta(e.type)?.label }}</span>
                <span class="ec-conf" :class="confClass(e.confidence)">{{ (e.confidence * 100).toFixed(0) }}%</span>
              </button>
            </div>
          </template>

          <template v-else>
            <dl class="insp-dl">
              <dt>关系类型</dt>
              <dd>{{ edgeMeta(inspectTarget.data.type)?.label }}</dd>
              <dt>置信度</dt>
              <dd><span class="conf-badge" :class="confClass(inspectTarget.data.confidence)">{{ confidenceLabel(inspectTarget.data.confidence) }} · {{ (inspectTarget.data.confidence * 100).toFixed(0) }}%</span></dd>
              <dt>匹配方法</dt>
              <dd>{{ methodLabel(inspectTarget.data.match_method) }}</dd>
              <dt>源节点</dt>
              <dd class="link-text" @click="selectNodeById(inspectTarget.data.source)">{{ nodeLabel(inspectTarget.data.source) }}</dd>
              <dt>目标节点</dt>
              <dd class="link-text" @click="selectNodeById(inspectTarget.data.target)">{{ nodeLabel(inspectTarget.data.target) }}</dd>
            </dl>
            <p class="insp-desc">{{ edgeMeta(inspectTarget.data.type)?.desc }}</p>
          </template>
        </template>

        <div v-else class="insp-empty">
          <div class="insp-empty-icon">◎</div>
          <p>在左侧图中点击<strong>节点</strong>或<strong>连线</strong>，查看可追溯的证据字段与匹配置信度。</p>
          <div class="legend-block">
            <div v-for="(m, t) in visibleNodeMeta" :key="t" class="legend-row">
              <span class="leg-dot" :style="{ background: m.color }"></span>
              <span>{{ m.label }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { apiGet, fmtCount } from '../../composables/useApi'
import {
  CHAIN_EDGE_META, CHAIN_NODE_META, confidenceLabel, FALLBACK_AGGREGATE_GRAPH,
} from '../../constants/chainHubContent.js'
import { CHART, CANVAS_LABEL } from '../../constants/chartTheme.js'

const props = defineProps({
  chainType: { type: String, default: 'aggregate_overview' },
  aggregate: { type: Boolean, default: true },
  height: { type: Number, default: 420 },
})

const emit = defineEmits(['loaded', 'node-select'])

const chartEl = ref(null)
const raw = ref({ nodes: [], edges: [], meta: {} })
const loading = ref(false)
const usingFallback = ref(false)
const DEFAULT_SAMPLE_LIMIT = 40
const sampleLimit = ref(DEFAULT_SAMPLE_LIMIT)
const activeStage = ref('')
const inspectTarget = ref(null)
let inst = null
let nodeIndex = {}
let forceStable = false
let layoutTimer = null
let resizeObs = null

/** 相对坐标 0~1，渲染时按画布像素换算（ECharts graph 不支持百分比字符串） */
const AGG_LAYOUT_FRAC = {
  fund: { x: 0.08, y: 0.5 },
  paper: { x: 0.28, y: 0.22 },
  patent: { x: 0.28, y: 0.78 },
  tech_point: { x: 0.52, y: 0.5 },
  product: { x: 0.74, y: 0.5 },
  industry: { x: 0.9, y: 0.5 },
}

function getChartSize() {
  const el = chartEl.value
  const w = el?.clientWidth || 0
  const h = el?.clientHeight || 0
  return {
    w: w > 48 ? w : 720,
    h: h > 48 ? h : props.height,
  }
}

function layoutPoint(type, index) {
  const { w, h } = getChartSize()
  const frac = AGG_LAYOUT_FRAC[type]
  if (frac) return { x: Math.round(frac.x * w), y: Math.round(frac.y * h) }
  return {
    x: Math.round((0.1 + (index % 6) * 0.14) * w),
    y: Math.round((0.2 + Math.floor(index / 6) * 0.18) * h),
  }
}

const hasData = computed(() => (raw.value.nodes || []).length > 0)

const stageSteps = computed(() => {
  if (props.chainType === 'patent_tech') {
    return [
      { id: 'patent', label: '① 专利' },
      { id: 'tech_point', label: '② 技术点' },
    ]
  }
  if (!props.aggregate && props.chainType === 'fund_paper_tech') {
    return [
      { id: 'fund', label: '① 基金' },
      { id: 'paper', label: '② 论文' },
      { id: 'tech_point', label: '③ 技术点' },
    ]
  }
  return [
    { id: 'fund', label: '① 基金' },
    { id: 'paper', label: '② 成果' },
    { id: 'tech_point', label: '③ 技术' },
    { id: 'product', label: '④ 产品' },
    { id: 'industry', label: '⑤ 产业' },
  ]
})

const modeLabel = computed(() => {
  if (props.aggregate || props.chainType === 'aggregate_overview') return '聚合证据拓扑'
  if (props.chainType === 'fund_paper_tech') return ''
  return '专利—技术 样本图'
})

const metaText = computed(() => {
  const m = raw.value.meta || {}
  if (props.chainType === 'patent_tech') {
    const terms = m.tech_terms ?? '—'
    return `已排除「无人机系统」· ${terms} 个技术点 · 专利—技术 ${fmtCount(m.patent_tech_links || raw.value.edges?.length)} 条`
  }
  if (props.aggregate) {
    return `基金—论文 ${fmtCount(m.fund_paper_pairs)} 组 · 专利—技术 ${fmtCount(m.patent_tech_links)} 条`
  }
  return ``
})

const visibleNodeMeta = computed(() => {
  const types = new Set((raw.value.nodes || []).map(n => n.type))
  return Object.fromEntries(
    Object.entries(CHAIN_NODE_META).filter(([k]) => types.has(k) || props.aggregate),
  )
})

function isAggregateGraph(data) {
  return data?.chain_type === 'aggregate_overview'
    || data?.nodes?.some(n => String(n.id).startsWith('agg:'))
}

function edgeMeta(t) { return CHAIN_EDGE_META[t] }
function confClass(c) {
  if (c >= 0.9) return 'high'
  if (c >= 0.7) return 'mid'
  return 'low'
}
function methodLabel(m) {
  return {
    direct_mapping: 'SQLite 直接映射',
    semantic_match: '标题/摘要语义匹配',
    skills_claim: 'Skills 文献池认领',
    metadata_tag: '基金标注（Crossref/OpenAlex）',
    rule_match: '规则 + LLM 归类',
    candidate: '候选关联（待验证）',
  }[m] || m || '—'
}
function fieldLabel(k) {
  return {
    type: '节点类型', year: '年份', status: '验证状态',
    tech_layer: '技术大类', patent_count: '关联专利数', count: '聚合规模',
  }[k] || k
}

function nodeLabel(id) {
  const n = nodeIndex[id]
  return n?.label || id
}

function nodeFieldsComputed(n) {
  const out = {}
  if (n.type) out.type = CHAIN_NODE_META[n.type]?.label || n.type
  if (n.year != null) out.year = n.year
  if (n.status) out.status = n.status === 'verified' ? '已验证' : n.status
  if (n.tech_layer) out.tech_layer = n.tech_layer
  if (n.patent_count != null) out.patent_count = fmtCount(n.patent_count)
  if (n.count != null) out.count = fmtCount(n.count)
  return out
}

const inspectTypeLabel = computed(() => {
  if (!inspectTarget.value) return ''
  if (inspectTarget.value.kind === 'edge') return '证据边'
  const t = inspectTarget.value.data?.type
  return CHAIN_NODE_META[t]?.label || t
})

const inspectTitle = computed(() => {
  if (!inspectTarget.value) return ''
  if (inspectTarget.value.kind === 'edge') {
    const e = inspectTarget.value.data
    return `${nodeLabel(e.source)} → ${nodeLabel(e.target)}`
  }
  return inspectTarget.value.data?.label || inspectTarget.value.data?.id
})

const inspectColor = computed(() => {
  if (!inspectTarget.value) return '#78716c'
  if (inspectTarget.value.kind === 'edge') {
    return edgeMeta(inspectTarget.value.data.type)?.color || '#78716c'
  }
  return CHAIN_NODE_META[inspectTarget.value.data?.type]?.color || '#78716c'
})

const nodeFields = computed(() => {
  if (inspectTarget.value?.kind !== 'node') return {}
  return nodeFieldsComputed(inspectTarget.value.data)
})

const adjacentEdges = computed(() => {
  if (inspectTarget.value?.kind !== 'node') return []
  const id = inspectTarget.value.data.id
  return (raw.value.edges || []).filter(e => e.source === id || e.target === id)
})

function useFixedLayout() {
  return props.aggregate || props.chainType === 'aggregate_overview'
}

function setStage(id) {
  activeStage.value = activeStage.value === id ? '' : id
  if (!inst) {
    renderFull(false)
    return
  }
  updateVisualOnly()
}

function clearInspect() {
  inspectTarget.value = null
  inst?.dispatchAction({ type: 'downplay', seriesIndex: 0 })
  applyGraphVisualState()
}

function selectNodeById(id) {
  const n = nodeIndex[id]
  if (n) selectNode(n)
}

function selectNode(n) {
  inspectTarget.value = { kind: 'node', data: n }
  emit('node-select', n)
  if (useFixedLayout()) {
    applyGraphVisualState()
    nextTick(() => applySelectionHighlight(n.id))
  } else {
    nextTick(() => {
      applySelectionHighlight(n.id)
      centerViewOnNode(n.id)
    })
  }
}

function selectEdge(e) {
  inspectTarget.value = { kind: 'edge', data: e }
  applyGraphVisualState()
  inst?.dispatchAction({ type: 'downplay', seriesIndex: 0 })
}

function applySelectionHighlight(nodeId) {
  if (!inst) return
  const idx = (raw.value.nodes || []).findIndex(n => n.id === nodeId)
  if (idx < 0) return
  inst.dispatchAction({ type: 'downplay', seriesIndex: 0 })
  inst.dispatchAction({
    type: 'focusNodeAdjacency',
    seriesIndex: 0,
    dataIndex: idx,
  })
}

function centerViewOnNode(nodeId) {
  if (!inst || useFixedLayout()) return
  try {
    const idx = (raw.value.nodes || []).findIndex(n => n.id === nodeId)
    if (idx < 0) return
    const series = inst.getModel().getSeriesByIndex(0)
    const data = series.getData()
    const layout = data.getItemLayout(idx)
    if (layout && layout.length >= 2) {
      inst.setOption({
        series: [{
          center: [layout[0], layout[1]],
          zoom: 1.08,
        }],
      }, false)
    }
  } catch {
    /* 部分版本 graph 布局坐标不可用，仅保留邻接高亮 */
  }
}

function applyGraphVisualState() {
  if (!inst) {
    renderFull(false)
    return
  }
  updateVisualOnly()
}

function resetView() {
  activeStage.value = ''
  inspectTarget.value = null
  inst?.dispatchAction({ type: 'downplay', seriesIndex: 0 })
  inst?.dispatchAction({ type: 'restore' })
  if (props.aggregate) setDefaultSelection()
  else applyGraphVisualState()
}

async function ensureChartReady() {
  await nextTick()
  for (let i = 0; i < 8; i++) {
    if (!chartEl.value) {
      await nextTick()
      continue
    }
    const w = chartEl.value.clientWidth
    const h = chartEl.value.clientHeight
    if (w >= 48 || h >= 48 || i >= 4) {
      if (!inst) {
        inst = echarts.init(chartEl.value)
        inst.on('click', onChartClick)
        inst.on('finished', scheduleStabilize)
      }
      return true
    }
    await new Promise(r => setTimeout(r, 60))
  }
  return false
}

function paintAggregateGraph() {
  raw.value = { ...FALLBACK_AGGREGATE_GRAPH }
  usingFallback.value = true
  emit('loaded', raw.value)
}

async function mountAndRender() {
  if (props.aggregate && !(raw.value.nodes || []).length) {
    paintAggregateGraph()
  }
  const ok = await ensureChartReady()
  if (!ok) return
  if (!(raw.value.nodes || []).length) return
  setupResizeObserver()
  renderFull(true)
  await nextTick()
  setDefaultSelection()
  layoutRefresh()
}

function resizeChart() {
  nextTick(() => {
    requestAnimationFrame(() => {
      if (!inst && chartEl.value && (raw.value.nodes || []).length) {
        renderFull(false)
      }
      inst?.resize()
    })
  })
}

function nodeDisplayLabel(n) {
  const base = (n.label || n.id).slice(0, props.aggregate ? 8 : 14)
  const cnt = n.count ?? n.patent_count
  return cnt != null ? `${base}\n(${fmtCount(cnt)})` : base
}

function isStageDimmed(nodeType) {
  if (!activeStage.value) return false
  if (activeStage.value === 'paper' && nodeType === 'patent') return false
  if (activeStage.value === 'paper' && (nodeType === 'paper' || nodeType === 'patent')) return false
  return nodeType !== activeStage.value
}

function isHighlightedNode(id) {
  if (!inspectTarget.value) return false
  if (inspectTarget.value.kind === 'node') return inspectTarget.value.data.id === id
  const e = inspectTarget.value.data
  return e.source === id || e.target === id
}

function buildNodeLabel(n, dimmed, useFixed) {
  if (useFixed) {
    return {
      show: true,
      position: 'inside',
      color: dimmed ? CANVAS_LABEL.dimmed : CANVAS_LABEL.onNode,
      fontSize: props.aggregate ? 11 : 10,
      lineHeight: 13,
      fontWeight: 600,
    }
  }
  return {
    show: true,
    position: 'right',
    color: dimmed ? CANVAS_LABEL.dimmed : CANVAS_LABEL.secondary,
    fontSize: props.chainType === 'patent_tech' ? 8 : 9,
    lineHeight: 11,
    fontWeight: 500,
    distance: 5,
    width: props.chainType === 'patent_tech' ? 64 : 80,
    overflow: 'truncate',
  }
}

function buildSeriesNodes() {
  const nodes = raw.value.nodes || []
  const categories = [...new Set(nodes.map(n => n.type))]
  const useFixed = useFixedLayout()

  return nodes.map((n, i) => {
    const st = layoutPoint(n.type, i)
    const dimmed = isStageDimmed(n.type)
    const hl = isHighlightedNode(n.id)
    return {
      id: n.id,
      name: nodeDisplayLabel(n),
      x: useFixed ? st.x : undefined,
      y: useFixed ? st.y : undefined,
      symbolSize: n.type === 'tech_point' ? (props.aggregate ? 62 : 44) : (props.aggregate ? 52 : 38),
      category: categories.indexOf(n.type),
      itemStyle: {
        color: CHAIN_NODE_META[n.type]?.color || '#78716c',
        borderColor: hl ? '#ffffff' : 'rgba(255,255,255,0.85)',
        borderWidth: hl ? 2.5 : 1.5,
        opacity: dimmed ? 0.28 : 1,
        shadowBlur: hl ? 14 : 4,
        shadowColor: hl ? (CHAIN_NODE_META[n.type]?.color || '#78716c') : 'rgba(42,42,42,0.08)',
      },
      label: buildNodeLabel(n, dimmed, useFixed),
    }
  })
}

function buildSeriesLinks() {
  const edges = raw.value.edges || []
  return edges.map((e, idx) => {
    const em = edgeMeta(e.type)
    const dimmed = activeStage.value && !(
      (activeStage.value === 'paper' && (e.type === 'fund_supports' || e.type === 'patent_hits_tech')) ||
      (nodeIndex[e.source]?.type === activeStage.value || nodeIndex[e.target]?.type === activeStage.value)
    )
    const hl = inspectTarget.value?.kind === 'edge' && inspectTarget.value.data === e
      || (inspectTarget.value?.kind === 'node' && (e.source === inspectTarget.value.data.id || e.target === inspectTarget.value.data.id))
    const baseColor = em?.color || '#78716c'
    const conf = e.confidence ?? 0.7
    return {
      source: e.source,
      target: e.target,
      lineStyle: {
        color: baseColor,
        width: hl ? 3 : 1.5 + conf * 0.8,
        opacity: dimmed ? 0.1 : (hl ? 0.95 : 0.35 + conf * 0.45),
        curveness: props.chainType === 'patent_tech' ? 0.12 : 0.18,
      },
      _raw: e,
      _idx: idx,
    }
  })
}

function buildOption(isInitial = false) {
  const nodes = raw.value.nodes || []
  const edges = raw.value.edges || []
  nodeIndex = Object.fromEntries(nodes.map(n => [n.id, n]))
  const categories = [...new Set(nodes.map(n => n.type))].map(t => ({
    name: t,
    itemStyle: { color: CHAIN_NODE_META[t]?.color || '#64748b' },
  }))
  const useFixed = useFixedLayout()

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      ...CHART.tooltip,
      formatter(p) {
        if (p.dataType === 'edge') {
          const e = p.data._raw
          if (!e) return ''
          return `${edgeMeta(e.type)?.label}<br/>置信 ${(e.confidence * 100).toFixed(0)}% · ${methodLabel(e.match_method)}`
        }
        const n = nodeIndex[p.data.id]
        if (!n) return p.name
        return `<b>${n.label || n.id}</b><br/>${CHAIN_NODE_META[n.type]?.label || n.type}`
      },
    },
    series: [{
      type: 'graph',
      layout: useFixed ? 'none' : 'force',
      roam: true,
      draggable: false,
      force: useFixed ? undefined : {
        repulsion: props.chainType === 'patent_tech' ? 100 : 130,
        edgeLength: [90, 115],
        gravity: 0.1,
        friction: 0.98,
        layoutAnimation: isInitial && !forceStable,
      },
      data: buildSeriesNodes(),
      links: buildSeriesLinks(),
      categories,
      edgeSymbol: ['none', 'arrow'],
      edgeSymbolSize: 7,
      emphasis: {
        focus: 'adjacency',
        blurScope: 'global',
        scale: true,
        lineStyle: { width: 3 },
      },
      blur: {
        itemStyle: { opacity: 0.12 },
        lineStyle: { opacity: 0.08 },
      },
    }],
  }
}

function renderFull(isInitial = false) {
  if (!chartEl.value) return
  if (!inst) {
    inst = echarts.init(chartEl.value)
    inst.on('click', onChartClick)
    inst.on('finished', scheduleStabilize)
  }
  inst.setOption(buildOption(isInitial), isInitial)
  nextTick(() => {
    inst?.resize()
    if (useFixedLayout() && !isInitial) updateVisualOnly()
  })
}

function layoutRefresh() {
  if (!inst || !chartEl.value) return
  if (useFixedLayout()) {
    updateVisualOnly()
  }
  inst.resize()
}

function updateVisualOnly() {
  if (!inst) return
  inst.setOption({
    series: [{
      data: buildSeriesNodes(),
      links: buildSeriesLinks(),
    }],
  }, false)
}

function stabilizeForceLayout() {
  if (useFixedLayout() || forceStable) return
  forceStable = true
  inst?.setOption({ series: [{ force: { layoutAnimation: false } }] }, false)
}

function scheduleStabilize() {
  clearTimeout(layoutTimer)
  layoutTimer = setTimeout(stabilizeForceLayout, 2200)
}

function setDefaultSelection() {
  const nodes = raw.value.nodes || []
  const edges = raw.value.edges || []
  if (!nodes.length || !props.aggregate) return
  const tech = nodes.find(n => n.type === 'tech_point')
  const edge = edges.find(e => e.type === 'paper_hits_tech') || edges[0]
  if (tech) {
    inspectTarget.value = { kind: 'node', data: tech }
  } else if (edge) {
    inspectTarget.value = { kind: 'edge', data: edge }
  }
  if (inst) {
    updateVisualOnly()
    if (tech) applySelectionHighlight(tech.id)
  }
}

async function reload() {
  loading.value = true
  usingFallback.value = false
  forceStable = false
  clearTimeout(layoutTimer)
  try {
    if (props.aggregate) {
      paintAggregateGraph()
      await ensureChartReady()
      setupResizeObserver()
      renderFull(true)
      setDefaultSelection()
      layoutRefresh()
      tryFetchAggregate()
      return
    }

    const q = new URLSearchParams({
      chain_type: props.chainType,
      limit: String(sampleLimit.value),
      aggregate: 'false',
    })
    let data = await apiGet(`/api/chain?${q}`)

    if (data.error || !data.nodes?.length) {
      data = { nodes: [], edges: [], meta: { note: data.error || '无数据' } }
    }

    raw.value = data
    emit('loaded', data)
    await ensureChartReady()
    renderFull(true)
    scheduleStabilize()
  } finally {
    loading.value = false
  }
}

async function tryFetchAggregate() {
  try {
    const q = new URLSearchParams({
      chain_type: 'aggregate_overview',
      limit: '30',
      aggregate: 'true',
    })
    let data = await apiGet(`/api/chain?${q}`)
    if (data.error || !data.nodes?.length || !isAggregateGraph(data)) {
      const q2 = new URLSearchParams({
        chain_type: 'fund_paper_tech',
        limit: '30',
        aggregate: 'true',
      })
      data = await apiGet(`/api/chain?${q2}`)
    }
    if (!data.error && data.nodes?.length && isAggregateGraph(data)) {
      raw.value = data
      usingFallback.value = false
      emit('loaded', data)
      renderFull(true)
      setDefaultSelection()
      layoutRefresh()
    }
  } catch {
    /* 保留本地演示拓扑 */
  }
}

function onChartClick(params) {
  if (params.dataType === 'node') {
    const n = nodeIndex[params.data.id]
    if (n) selectNode(n)
  } else if (params.dataType === 'edge' && params.data._raw) {
    selectEdge(params.data._raw)
  }
}

function onResize() { layoutRefresh() }

function setupResizeObserver() {
  if (!chartEl.value || typeof ResizeObserver === 'undefined') return
  resizeObs?.disconnect()
  resizeObs = new ResizeObserver(() => {
    if ((raw.value.nodes || []).length) layoutRefresh()
  })
  resizeObs.observe(chartEl.value)
}

watch(() => [props.chainType, props.aggregate], () => {
  activeStage.value = ''
  inspectTarget.value = null
  forceStable = false
  reload()
})

onMounted(async () => {
  window.addEventListener('resize', onResize)
  await mountAndRender()
  if (!props.aggregate) await reload()
})

onBeforeUnmount(() => {
  clearTimeout(layoutTimer)
  resizeObs?.disconnect()
  window.removeEventListener('resize', onResize)
  inst?.off('click', onChartClick)
  inst?.off('finished', scheduleStabilize)
  inst?.dispose()
})

defineExpose({ reload, mountAndRender, resizeChart, highlightNode: selectNodeById, getData: () => raw.value })
</script>

<style scoped>
.evidence-explorer {
  border-radius: 14px;
  background: var(--surface-panel, #faf9f7);
  border: 1px solid var(--border, #e8e4df);
  overflow: hidden;
  box-shadow: var(--card-shadow, 0 2px 16px rgba(42, 28, 28, 0.06));
}
.explorer-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border, #e8e4df);
  background: #ffffff;
}
.tb-title {
  font-size: 0.88rem;
  font-weight: 700;
  color: var(--text, #2a2a2a);
  margin-right: 10px;
}
.tb-meta {
  font-size: 0.76rem;
  color: var(--muted, #78716c);
  font-weight: 500;
}
.tb-fallback {
  margin-left: 8px;
  font-size: 0.68rem;
  font-weight: 600;
  color: #b45309;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(180, 83, 9, 0.1);
}
.tb-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px;
}
.stage-btn {
  padding: 5px 11px;
  border-radius: 999px;
  border: 1px solid var(--border, #e8e4df);
  background: #ffffff;
  color: var(--muted, #78716c);
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.12s;
}
.stage-btn:hover {
  border-color: rgba(174, 13, 40, 0.35);
  color: var(--ruc-red, #ae0d28);
}
.stage-btn.active {
  background: rgba(174, 13, 40, 0.1);
  border-color: var(--ruc-red, #ae0d28);
  color: var(--ruc-red-dark, #9b0000);
}
.limit-ctrl {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  color: var(--muted, #78716c);
  margin-left: 4px;
}
.select-sm {
  background: #ffffff;
  border: 1px solid var(--border, #e8e4df);
  color: var(--text, #2a2a2a);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 0.72rem;
}
.btn-icon {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid var(--border, #e8e4df);
  background: #ffffff;
  color: var(--muted, #78716c);
  cursor: pointer;
  font-size: 1rem;
}
.btn-icon:hover {
  color: var(--ruc-red, #ae0d28);
  border-color: rgba(174, 13, 40, 0.35);
}

.explorer-body {
  display: grid;
  grid-template-columns: 1fr 300px;
  min-height: v-bind('height + "px"');
}
.graph-zone {
  position: relative;
  min-width: 0;
  height: v-bind('height + "px"');
}
.chart-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  background:
    radial-gradient(ellipse at 40% 50%, rgba(174, 13, 40, 0.04) 0%, transparent 55%),
    #faf9f7;
}
.graph-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: rgba(250, 249, 247, 0.85);
  color: var(--muted, #78716c);
  font-size: 0.85rem;
}
.btn-retry {
  padding: 6px 14px;
  border-radius: 8px;
  border: 1px solid rgba(174, 13, 40, 0.35);
  background: rgba(174, 13, 40, 0.08);
  color: var(--ruc-red, #ae0d28);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}
.graph-hint {
  position: absolute;
  bottom: 8px;
  left: 12px;
  font-size: 0.68rem;
  color: #a8a29e;
  pointer-events: none;
}

.inspector {
  border-left: 1px solid var(--border, #e8e4df);
  padding: 16px 14px;
  background: #ffffff;
  overflow-y: auto;
  max-height: v-bind('height + "px"');
}
.insp-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}
.insp-type {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.insp-close {
  background: none;
  border: none;
  color: #a8a29e;
  font-size: 1.2rem;
  cursor: pointer;
  line-height: 1;
}
.insp-close:hover { color: var(--text, #2a2a2a); }
.insp-title {
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--text, #2a2a2a);
  line-height: 1.45;
  margin: 0 0 14px;
  word-break: break-word;
}
.insp-dl {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 6px 12px;
  font-size: 0.78rem;
  margin-bottom: 14px;
}
.insp-dl dt { color: var(--muted, #78716c); font-weight: 600; }
.insp-dl dd { color: var(--text, #2a2a2a); margin: 0; }
.link-text {
  color: var(--ruc-red, #ae0d28) !important;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.insp-desc {
  font-size: 0.76rem;
  color: var(--muted, #78716c);
  line-height: 1.5;
  margin: 0;
}
.insp-sub {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--muted, #78716c);
  margin-bottom: 8px;
}
.edge-chip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  padding: 7px 10px;
  margin-bottom: 6px;
  border-radius: 8px;
  border: 1px solid var(--border, #e8e4df);
  background: var(--surface-panel, #faf9f7);
  cursor: pointer;
  transition: border-color 0.12s;
}
.edge-chip:hover { border-color: rgba(174, 13, 40, 0.35); }
.ec-type { font-size: 0.72rem; color: var(--text, #2a2a2a); font-weight: 600; }
.ec-conf {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
}
.ec-conf.high { background: rgba(45, 106, 79, 0.12); color: #2d6a4f; }
.ec-conf.mid { background: rgba(180, 83, 9, 0.12); color: #b45309; }
.ec-conf.low { background: rgba(120, 113, 108, 0.12); color: #78716c; }
.conf-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 700;
  font-size: 0.76rem;
}
.conf-badge.high { background: rgba(45, 106, 79, 0.12); color: #2d6a4f; }
.conf-badge.mid { background: rgba(180, 83, 9, 0.12); color: #b45309; }
.conf-badge.low { background: rgba(120, 113, 108, 0.12); color: #78716c; }

.insp-empty {
  text-align: center;
  padding: 24px 8px;
  color: var(--muted, #78716c);
  font-size: 0.8rem;
  line-height: 1.55;
}
.insp-empty-icon {
  font-size: 2rem;
  color: #d6d3d1;
  margin-bottom: 12px;
}
.insp-empty strong { color: var(--text, #2a2a2a); }
.legend-block { margin-top: 20px; text-align: left; }
.legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.74rem;
  color: var(--muted, #78716c);
  margin-bottom: 6px;
}
.leg-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

@media (max-width: 900px) {
  .explorer-body { grid-template-columns: 1fr; }
  .inspector {
    border-left: none;
    border-top: 1px solid var(--border, #e8e4df);
    max-height: 280px;
  }
}
</style>
