<template>
  <div class="evo-tree" :class="{ interactive, compact, [`size-${size || (compact ? 'compact' : 'full')}`]: true, 'has-focus': !!activeLayer }">
    <div v-if="loading" class="tree-loading">加载技术树…</div>
    <svg
      v-else
      ref="svgEl"
      class="tree-svg"
      :viewBox="`0 0 ${W} ${H}`"
      preserveAspectRatio="xMidYMid meet"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <radialGradient id="trunkGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="#ae0d28" stop-opacity="0.35" />
          <stop offset="100%" stop-color="#ae0d28" stop-opacity="0" />
        </radialGradient>
        <filter id="branchGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <filter id="bloomSoft" x="-30%" y="-30%" width="160%" height="160%">
          <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#2a2a2a" flood-opacity="0.12" />
        </filter>
      </defs>

      <g class="tree-scene" :transform="sceneTransform || undefined">
      <!-- 地面 -->
      <ellipse :cx="CX" :cy="H - 18" :rx="size === 'case' ? 150 : 210" ry="12" fill="rgba(174,13,40,0.06)" />

      <!-- 枝干 -->
      <g
        v-for="(b, bi) in branches"
        :key="b.id"
        class="branch-group"
        :class="{ dimmed: isDimmed(b.id), focused: isFocused(b.id) }"
      >
        <path
          :d="branchPath(b)"
          class="branch-stroke branch-base"
          :stroke="branchStroke(b)"
          fill="none"
          stroke-linecap="round"
        />
        <path
          :d="branchPath(b)"
          class="branch-stroke branch-flow"
          :class="{ active: isFocused(b.id), hover: hoverBranch === b.id && !activeLayer }"
          :stroke="branchStroke(b)"
          fill="none"
          stroke-linecap="round"
          :style="{ animationDelay: `${bi * 0.35}s`, animationPlayState: isDimmed(b.id) ? 'paused' : 'running' }"
          @mouseenter="onBranchHover(b.id)"
          @mouseleave="hoverBranch = ''"
          @click="onBranchClick(b.id)"
        />

        <!-- 展开：放射状开花（先画线，再画节点；层六边形置于最上） -->
        <g v-if="showLeaves && isFocused(b.id)" class="leaf-cluster">
          <path
            v-for="(leaf, pi) in leafEntries(b)"
            :key="`${leaf.tech_tag_id}-stem`"
            :d="leaf.stemPath"
            class="bloom-stem"
            :stroke="b.color"
            :style="{ animationDelay: `${pi * 0.05}s` }"
          />
          <g
            v-for="(leaf, pi) in leafEntries(b)"
            :key="leaf.tech_tag_id"
            class="bloom-node"
            :transform="`translate(${leaf.x}, ${leaf.y})`"
            :style="{ animationDelay: `${0.08 + pi * 0.06}s` }"
            @click.stop="onLeafClick(leaf.tech_tag_id)"
          >
            <rect
              :x="-leaf.pillW / 2 - 3"
              y="-17"
              :width="leaf.pillW + 6"
              height="34"
              rx="17"
              class="bloom-pill-mask"
            />
            <rect
              :x="-leaf.pillW / 2"
              y="-14"
              :width="leaf.pillW"
              height="28"
              rx="14"
              class="bloom-pill"
              :stroke="b.color"
            />
            <text class="bloom-label" y="5">{{ leaf.shortLabel }}</text>
          </g>
        </g>

        <!-- 层节点（展开时叠在技术点之上） -->
        <g
          class="layer-node"
          :class="{ 'layer-on-top': isFocused(b.id) }"
          :transform="`translate(${b.x}, ${b.y})`"
          @mouseenter="onBranchHover(b.id)"
          @mouseleave="hoverBranch = ''"
          @click="onBranchClick(b.id)"
        >
          <path
            :d="roundHexPath(0, 0, layerRadius(b), layerCorner(b))"
            class="layer-shell"
            :class="{ active: isFocused(b.id), hover: hoverBranch === b.id && !activeLayer }"
            :fill="isFocused(b.id) ? '#ffffff' : branchStroke(b)"
            :fill-opacity="isFocused(b.id) ? 1 : (isDimmed(b.id) ? 0.06 : 0.14)"
            :stroke="branchStroke(b)"
            stroke-width="2"
            :style="{ animationDelay: `${bi * 0.4}s`, animationPlayState: isDimmed(b.id) ? 'paused' : 'running' }"
          />
          <path
            :d="roundHexPath(0, 0, layerRadius(b) - 12, layerCorner(b) - 2)"
            :fill="branchStroke(b)"
            :fill-opacity="isFocused(b.id) ? 0.12 : (isDimmed(b.id) ? 0.12 : 0.32)"
          />
          <text class="layer-count" y="-4" :fill="isDimmed(b.id) ? '#a8a29e' : '#2a2a2a'">{{ b.pointCount }}</text>
          <text class="layer-label" y="14" :fill="isDimmed(b.id) ? '#c4bfba' : '#4a4540'">{{ b.short }}</text>
        </g>
      </g>

      <!-- 树干：圆角六边形 -->
      <g class="trunk" :class="{ dimmed: !!activeLayer }" :transform="`translate(${CX}, ${CY})`">
        <path :d="roundHexPath(0, 0, trunkGlowR, trunkGlowR * 0.18)" fill="url(#trunkGlow)" class="trunk-glow" />
        <path
          :d="roundHexPath(0, 0, trunkMid, trunkMid * 0.19)"
          class="trunk-body"
          fill="#ffffff"
          stroke="#ae0d28"
          stroke-width="2.5"
        />
        <path
          :d="roundHexPath(0, 0, trunkInner, trunkInner * 0.19)"
          fill="rgba(174,13,40,0.08)"
          class="trunk-inner"
        />
        <text class="trunk-title" y="-6">低空经济</text>
        <text class="trunk-sub" y="14">{{ totalPoints }} 技术点</text>
      </g>
      </g>
    </svg>

    <div v-if="hoverLayer && interactive && !activeLayer" class="tree-float">
      <div class="float-title">{{ hoverLayer.name }}</div>
      <div class="float-row">{{ hoverLayer.pointCount }} 个技术点 · {{ hoverLayer.paperCount }} 篇文献</div>
      <div class="float-hint">点击展开该技术点</div>
    </div>
    <div v-else-if="activeLayer && interactive" class="tree-float">
      <div class="float-title">{{ activeLayerMeta?.name }}</div>
      <div class="float-row">{{ activeLayerMeta?.pointCount }} 个技术点已展开</div>
      <div class="float-hint">点击技术点进入 survey · 再次点击该大类收起</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiGet } from '../../composables/useApi'
import { LAYER_BRANCHES, sortTechPoints, layerFromTree, LAYER_BLOOM_PROFILES, DEFAULT_BLOOM_PROFILE } from '../../constants/techTree.js'
import { roundHexPath } from '../../utils/roundHex.js'

const props = defineProps({
  compact: { type: Boolean, default: true },
  /** compact | case | full — case 用于案例页总览，一屏内展示 */
  size: { type: String, default: '' },
  interactive: { type: Boolean, default: true },
  showLeaves: { type: Boolean, default: false },
  activeLayer: { type: String, default: '' },
  selectedTech: { type: String, default: '' },
  product: { type: String, default: 'UAV' },
  navigateOnClick: { type: Boolean, default: true },
})

const emit = defineEmits(['branch-click', 'leaf-click'])

const router = useRouter()
const loading = ref(true)
const tree = ref({ layers: [] })
const hoverBranch = ref('')
const svgEl = ref(null)

const SIZE_PROFILES = {
  case: { w: 620, h: 288, r: 98, trunkInner: 38, trunkMid: 46, trunkGlow: 62, layerR: 34, layerRActive: 38 },
  /** 案例页总览：比 full 略小，保留可读字号 */
  page: { w: 820, h: 560, r: 178, trunkInner: 44, trunkMid: 54, trunkGlow: 82, layerR: 44, layerRActive: 52 },
  compact: { w: 760, h: 390, r: 132, trunkInner: 42, trunkMid: 52, trunkGlow: 78, layerR: 42, layerRActive: 46 },
  full: { w: 760, h: 520, r: 175, trunkInner: 42, trunkMid: 52, trunkGlow: 78, layerR: 42, layerRActive: 46 },
}

const layout = computed(() => {
  if (props.size && SIZE_PROFILES[props.size]) return SIZE_PROFILES[props.size]
  return props.compact ? SIZE_PROFILES.compact : SIZE_PROFILES.full
})

const W = computed(() => layout.value.w)
const H = computed(() => layout.value.h)
const CX = computed(() => W.value / 2)
const CY = computed(() => {
  if (props.size === 'case') return H.value * 0.54
  if (props.compact && !props.size) return 198
  return H.value * 0.48
})
const R = computed(() => layout.value.r)
const trunkInner = computed(() => layout.value.trunkInner)
const trunkMid = computed(() => layout.value.trunkMid)
const trunkGlowR = computed(() => layout.value.trunkGlow)

function layerRadius(b) {
  return isFocused(b.id) ? layout.value.layerRActive : layout.value.layerR
}

function layerCorner(b) {
  const base = props.size === 'case' ? 7 : 9
  return isFocused(b.id) ? base + 1 : base
}

const totalPoints = computed(() =>
  (tree.value.layers || []).reduce((s, l) => s + l.tech_points.length, 0)
)

const branches = computed(() =>
  LAYER_BRANCHES.map(meta => {
    const layer = layerFromTree(tree.value, meta.id)
    const points = layer?.tech_points || []
    const pos = polar(CX.value, CY.value, R.value, meta.angle)
    return {
      ...meta,
      x: pos.x,
      y: pos.y,
      pointCount: points.length,
      paperCount: layer?.paper_count ?? points.reduce((s, p) => s + (p.paper_count_b || 0), 0),
      sortedPoints: sortTechPoints(points),
    }
  })
)

const hoverLayer = computed(() =>
  branches.value.find(b => b.id === hoverBranch.value) || null
)

const activeLayerMeta = computed(() =>
  branches.value.find(b => b.id === props.activeLayer) || null
)

/** 各层技术点开花布局（预计算，供渲染与 viewBox 共用） */
const bloomByLayer = computed(() => {
  const map = {}
  for (const b of branches.value) {
    map[b.id] = buildBloomLayout(b)
  }
  return map
})

/** 聚焦：SVG 坐标系 transform，层节点居中且内容不越界 */
const sceneTransform = computed(() => {
  if (!props.activeLayer || props.size !== 'page') return ''
  const b = branches.value.find(x => x.id === props.activeLayer)
  if (!b) return ''

  const leaves = bloomByLayer.value[b.id] || []
  const layerR = layout.value.layerRActive + 10
  let minX = b.x - layerR
  let maxX = b.x + layerR
  let minY = b.y - layerR
  let maxY = b.y + layerR

  for (const leaf of leaves) {
    minX = Math.min(minX, leaf.x - leaf.pillW / 2 - 12)
    maxX = Math.max(maxX, leaf.x + leaf.pillW / 2 + 12)
    minY = Math.min(minY, leaf.y - 20)
    maxY = Math.max(maxY, leaf.y + 20)
  }

  const pad = 36
  const floatReserve = 72
  const viewH = H.value - floatReserve
  const bw = maxX - minX + pad * 2
  const bh = maxY - minY + pad * 2
  const bloomProf = LAYER_BLOOM_PROFILES[b.id] || DEFAULT_BLOOM_PROFILE
  const scaleBoost = bloomProf.focusScaleBoost ?? 1
  const baseScale = Math.min((W.value * 0.86) / bw, (viewH * 0.72) / bh, 1.75)
  const scale = Math.min(1.75, baseScale * scaleBoost)
  const cx = CX.value
  const cy = viewH * 0.5

  return `translate(${cx}, ${cy}) scale(${scale}) translate(${-b.x}, ${-b.y})`
})

const DIM_COLOR = '#b8b3ac'

function isFocused(id) {
  return props.activeLayer === id
}

function isDimmed(id) {
  return !!props.activeLayer && props.activeLayer !== id
}

function branchStroke(b) {
  return isDimmed(b.id) ? DIM_COLOR : b.color
}

function onBranchHover(id) {
  if (!props.activeLayer) hoverBranch.value = id
}

function polar(cx, cy, r, deg) {
  const rad = (deg * Math.PI) / 180
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) }
}

function branchPath(b) {
  const innerR = trunkMid.value * 0.92
  const inner = polar(CX.value, CY.value, innerR, b.angle)
  const outer = { x: b.x, y: b.y }
  const ctrl = polar(CX.value, CY.value, R.value * 0.48, b.angle + (b.angle > 90 || b.angle < -90 ? 6 : -6))
  return `M ${inner.x} ${inner.y} Q ${ctrl.x} ${ctrl.y} ${outer.x} ${outer.y}`
}

function shortLabel(text, max = 8) {
  const s = String(text || '')
  return s.length > max ? `${s.slice(0, max)}…` : s
}

function pillWidth(label) {
  return Math.min(112, Math.max(52, label.length * 13 + 20))
}

function bloomStemPath(bx, by, px, py, layerEdge, pillW) {
  const dx = px - bx
  const dy = py - by
  const len = Math.hypot(dx, dy) || 1
  const ux = dx / len
  const uy = dy / len
  const sx = bx + ux * layerEdge
  const sy = by + uy * layerEdge
  const back = pillW * 0.28 + 4
  const ex = px - ux * back
  const ey = py - uy * back
  const bow = Math.min(18, len * 0.12)
  const mx = (sx + ex) / 2 - uy * bow
  const my = (sy + ey) / 2 + ux * bow
  return `M ${sx} ${sy} Q ${mx} ${my} ${ex} ${ey}`
}

const LEAF_GAP = 14
const MAX_ARC = 168

/** 根据标签宽度与半径，估算相邻点所需最小角距（度） */
function minAngleStep(pillW, dist, gap = LEAF_GAP) {
  return (2 * Math.atan((pillW / 2 + gap) / dist) * 180) / Math.PI
}

function resolveRingArc(countInRing, maxPillW, dist, arcSpan, maxDistExtra = 200, gap = LEAF_GAP) {
  if (countInRing <= 1) return { dist, arcSpan: 0 }

  let d = dist
  let span = arcSpan
  let step = minAngleStep(maxPillW, d, gap)
  let need = step * (countInRing - 1)
  const maxD = dist + maxDistExtra

  while (need > MAX_ARC && d < maxD) {
    d += 14
    step = minAngleStep(maxPillW, d, gap)
    need = step * (countInRing - 1)
  }

  span = Math.max(span, Math.min(MAX_ARC, need + 8))
  while (span / (countInRing - 1) < minAngleStep(maxPillW, d, gap) - 0.01 && d < maxD) {
    d += 12
    span = Math.max(span, minAngleStep(maxPillW, d, gap) * (countInRing - 1) + 6)
    span = Math.min(MAX_ARC, span)
  }

  return { dist: d, arcSpan: span }
}

function fitArcAtDist(countInRing, maxPillW, dist, arcSpan, gap = LEAF_GAP) {
  if (countInRing <= 1) return arcSpan
  const need = minAngleStep(maxPillW, dist, gap) * (countInRing - 1)
  return Math.max(arcSpan, Math.min(MAX_ARC, need + 4))
}

const PILL_H = 28

function pillsOverlap(a, b, gap = LEAF_GAP) {
  return (
    Math.abs(a.x - b.x) < (a.pillW + b.pillW) / 2 + gap &&
    Math.abs(a.y - b.y) < PILL_H + gap
  )
}

/** 仅微调位置，避免两圈标签 bbox 相交 */
function resolveLeafCollisions(leaves, bx, by, layerEdge, prof) {
  if (!prof.resolveCollisions || leaves.length < 2) return leaves

  const gap = prof.leafGap ?? LEAF_GAP
  const maxNudge = prof.collisionNudge ?? 18
  const items = leaves.map(l => ({ ...l }))

  for (let iter = 0; iter < 14; iter++) {
    let hit = false
    for (let i = 0; i < items.length; i++) {
      for (let j = i + 1; j < items.length; j++) {
        if (!pillsOverlap(items[i], items[j], gap)) continue
        hit = true
        const dx = items[j].x - items[i].x || 1
        const dy = items[j].y - items[i].y || 0.01
        const len = Math.hypot(dx, dy) || 1
        const push = Math.min(maxNudge, maxNudge * 0.35 + 2)
        const ux = dx / len
        const uy = dy / len
        items[i].x -= ux * push * 0.5
        items[i].y -= uy * push * 0.5
        items[j].x += ux * push * 0.5
        items[j].y += uy * push * 0.5
      }
    }
    if (!hit) break
  }

  return items.map(l => ({
    ...l,
    stemPath: bloomStemPath(bx, by, l.x, l.y, layerEdge, l.pillW),
  }))
}

/** 放射状开花：弧向排布 + 圈间错角 + 防重叠扩距 */
function buildBloomLayout(b) {
  const prof = LAYER_BLOOM_PROFILES[b.id] || DEFAULT_BLOOM_PROFILE
  const pts = b.sortedPoints
  const n = pts.length
  if (!n) return []

  const perRing = prof.perRing || 4
  const centerAngle = b.angle + (prof.angleBias || 0)
  const layerEdge = prof.layerEdge || 50
  const minStem = prof.minStem ?? 36
  const leafGap = prof.leafGap ?? LEAF_GAP

  const items = pts.map(pt => {
    const label = shortLabel(pt.tech_label, prof.labelMax || 8)
    return { pt, label, pillW: pillWidth(label) }
  })

  const rings = []
  for (let i = 0; i < n; i += perRing) rings.push(items.slice(i, i + perRing))

  const out = []
  let prevDist = 0
  let prevStep = 0

  rings.forEach((ringItems, ringIdx) => {
    const countInRing = ringItems.length
    const maxPillW = Math.max(...ringItems.map(it => it.pillW))

    let dist = prof.baseDist + ringIdx * prof.ringStep
    let arcSpan = prof.arcSpan
    if (countInRing === 2) arcSpan *= prof.twinArcScale ?? 0.88
    else if (countInRing === 3) arcSpan *= prof.tripleArcScale ?? 0.9

    const resolved = resolveRingArc(
      countInRing,
      maxPillW,
      dist,
      arcSpan,
      prof.maxDistExtra ?? 200,
      leafGap,
    )
    dist = resolved.dist
    arcSpan = resolved.arcSpan

    const minDist = layerEdge + minStem + maxPillW * 0.32
    if (dist < minDist) dist = minDist

    if (ringIdx > 0) {
      const radialGap = Math.max(prof.ringStep, 34 + maxPillW * 0.38)
      dist = Math.max(dist, prevDist + radialGap)
    }

    const ringCap = prof.ringDistCaps?.[ringIdx]
    if (ringCap != null) dist = Math.min(dist, ringCap)

    if (ringIdx > 0) {
      const minOuter = prevDist + (prof.minRingGap ?? 48)
      dist = Math.max(dist, minOuter)
      const outerCap = prof.ringDistCaps?.[ringIdx]
      if (outerCap != null) dist = Math.min(dist, outerCap)
    }

    if (countInRing > 1) {
      arcSpan = fitArcAtDist(countInRing, maxPillW, dist, arcSpan, leafGap)
    }

    const step = countInRing > 1 ? arcSpan / (countInRing - 1) : 0
    const staggerScale = prof.ringStaggerScale ?? 0.55
    const ringStagger = ringIdx > 0 && countInRing > 1 ? prevStep * staggerScale : 0
    const start = centerAngle - arcSpan / 2 + ringStagger

    ringItems.forEach((it, idxInRing) => {
      const leafDeg = start + step * idxInRing
      const leafRad = (leafDeg * Math.PI) / 180
      const x = b.x + dist * Math.cos(leafRad)
      const y = b.y + dist * Math.sin(leafRad)

      out.push({
        ...it.pt,
        x,
        y,
        shortLabel: it.label,
        pillW: it.pillW,
        stemPath: bloomStemPath(b.x, b.y, x, y, layerEdge, it.pillW),
      })
    })

    prevDist = dist
    prevStep = step
  })

  return resolveLeafCollisions(out, b.x, b.y, layerEdge, prof)
}

function leafEntries(b) {
  return bloomByLayer.value[b.id] || []
}

function onBranchClick(layerId) {
  if (!props.interactive) return
  emit('branch-click', layerId)
  if (!props.navigateOnClick) return
  router.push({ path: '/chain', query: { tab: 'tech_tree', product: props.product, layer: layerId } })
}

function onLeafClick(techId) {
  emit('leaf-click', techId, props.activeLayer)
  if (!props.navigateOnClick) return
  router.push({ path: '/chain', query: { tab: 'tech_tree', product: props.product, layer: props.activeLayer, tech: techId } })
}

onMounted(async () => {
  try {
    tree.value = await apiGet('/api/tech/tree')
  } catch { /* ignore */ }
  loading.value = false
})
</script>

<style scoped>
.evo-tree {
  position: relative;
  width: 100%;
  min-height: 320px;
  padding: 8px 12px 4px;
  border-radius: 14px;
  background: var(--surface-panel);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-highlight);
}

.evo-tree.size-case {
  min-height: 0;
  padding: 4px 8px 0;
}
.evo-tree.size-case .tree-svg {
  max-height: 300px;
}
.evo-tree.size-case .layer-count { font-size: 13px; }
.evo-tree.size-case .layer-label { font-size: 10px; }
.evo-tree.size-case .trunk-title { font-size: 12px; }
.evo-tree.size-case .trunk-sub { font-size: 10px; }

.tree-loading {
  text-align: center;
  padding: 120px 0;
  color: #64748b;
  font-size: 0.95rem;
}

.tree-svg {
  width: 100%;
  height: auto;
  display: block;
  user-select: none;
  overflow: hidden;
}

.branch-group.dimmed {
  opacity: 0.38;
  transition: opacity 0.35s ease;
}
.branch-group.focused {
  opacity: 1;
}
.branch-group.focused .layer-shell.active {
  animation: layerFocus 0.55s ease;
}
@keyframes layerFocus {
  0% { transform: scale(1); filter: none; }
  40% { transform: scale(1.1); filter: url(#branchGlow); }
  100% { transform: scale(1); }
}

.trunk.dimmed {
  opacity: 0.45;
  transition: opacity 0.35s ease;
}

.leaf-cluster { pointer-events: none; }
.leaf-cluster .bloom-node { pointer-events: all; cursor: pointer; }

.tree-scene {
  transition: transform 0.55s cubic-bezier(0.22, 1, 0.36, 1);
}

.evo-tree.has-focus {
  box-shadow: 0 10px 36px rgba(174, 13, 40, 0.1);
  overflow: hidden;
}
.evo-tree.size-page.has-focus {
  padding-bottom: 84px;
}
.evo-tree.size-page.has-focus .tree-float {
  bottom: 8px;
}

.bloom-stem {
  fill: none;
  stroke-width: 2;
  stroke-linecap: round;
  opacity: 0;
  stroke-dasharray: 6 5;
  animation: stemBloom 0.55s ease forwards, stemFlow 2s linear 0.55s infinite;
}
@keyframes stemBloom {
  from { opacity: 0; stroke-dashoffset: 24; }
  to { opacity: 0.5; stroke-dashoffset: 0; }
}

.bloom-node {
  opacity: 0;
  animation: bloomIn 0.45s cubic-bezier(0.22, 1, 0.36, 1) forwards;
}
@keyframes bloomIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.bloom-pill-mask {
  fill: #ffffff;
  stroke: none;
}
.bloom-pill {
  fill: #ffffff;
  stroke-width: 2;
  filter: url(#bloomSoft);
  transition: stroke-width 0.15s;
}
.bloom-label {
  font-size: 11px;
  font-weight: 700;
  fill: #2a2a2a;
  pointer-events: none;
  text-anchor: middle;
}
.bloom-node:hover .bloom-pill {
  stroke-width: 2.8;
}
.bloom-node:hover .bloom-label { fill: var(--ruc-red-dark, #9b0000); }

.layer-on-top .layer-shell.active {
  filter: url(#branchGlow);
}

@keyframes stemFlow {
  to { stroke-dashoffset: -18; }
}

.branch-base {
  stroke-width: 6;
  opacity: 0.18;
  pointer-events: none;
}

.branch-flow {
  stroke-width: 3;
  opacity: 0.45;
  stroke-dasharray: 8 10;
  cursor: pointer;
  animation: branchFlow 2.4s linear infinite;
  transition: stroke-width 0.2s, opacity 0.2s;
}
.branch-flow.hover,
.branch-flow.active {
  stroke-width: 5;
  opacity: 0.9;
  filter: url(#branchGlow);
}

@keyframes branchFlow {
  to { stroke-dashoffset: -36; }
}

.layer-node { cursor: pointer; }

.layer-shell {
  transform-box: fill-box;
  transform-origin: center;
  animation: layerBreathe 3.2s ease-in-out infinite;
  transition: fill-opacity 0.2s, stroke-width 0.2s;
}
.layer-shell.hover,
.layer-shell.active {
  fill-opacity: 0.24;
  stroke-width: 2.5;
  filter: url(#branchGlow);
}

@keyframes layerBreathe {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.04); opacity: 0.92; }
}

.layer-count {
  text-anchor: middle;
  font-size: 15px;
  font-weight: 800;
  fill: #2a2a2a;
}
.layer-label {
  text-anchor: middle;
  font-size: 11px;
  font-weight: 600;
  fill: #4a4540;
}

.trunk-glow {
  transform-box: fill-box;
  transform-origin: center;
  animation: trunkGlow 3s ease-in-out infinite;
}
.trunk-inner {
  transform-box: fill-box;
  transform-origin: center;
  animation: trunkInner 3s ease-in-out infinite;
  animation-delay: -0.6s;
}

@keyframes trunkGlow {
  0%, 100% { transform: scale(1); opacity: 0.85; }
  50% { transform: scale(1.08); opacity: 1; }
}
@keyframes trunkInner {
  0%, 100% { transform: scale(1); opacity: 0.85; }
  50% { transform: scale(0.94); opacity: 1; }
}

.trunk-title {
  text-anchor: middle;
  font-size: 14px;
  font-weight: 700;
  fill: #2a2a2a;
}
.trunk-sub {
  text-anchor: middle;
  font-size: 11px;
  fill: #78716c;
}

.tree-float {
  position: absolute;
  bottom: 12px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 20px;
  border-radius: 12px;
  text-align: center;
  pointer-events: none;
  background: #ffffff;
  border: 1px solid var(--border);
  box-shadow: var(--card-shadow);
}
.float-title { font-size: 0.95rem; font-weight: 600; color: var(--text); }
.float-row { font-size: 0.82rem; color: var(--muted); margin-top: 4px; }
.float-hint { font-size: 0.72rem; color: var(--ruc-red); margin-top: 6px; }
</style>
