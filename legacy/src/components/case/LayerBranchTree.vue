<template>
  <div class="layer-branch-tree">
    <div v-if="loading" class="loading">加载中…</div>
    <svg
      v-else
      class="branch-svg"
      :viewBox="`0 0 ${W} ${H}`"
      preserveAspectRatio="xMidYMid meet"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient :id="trunkGradId" x1="0%" y1="100%" x2="0%" y2="0%">
          <stop offset="0%" :stop-color="meta.color" stop-opacity="0.45" />
          <stop offset="55%" :stop-color="meta.color" stop-opacity="0.82" />
          <stop offset="100%" :stop-color="meta.color" stop-opacity="1" />
        </linearGradient>
        <linearGradient :id="trunkHiId" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#ffffff" stop-opacity="0" />
          <stop offset="45%" stop-color="#ffffff" stop-opacity="0.35" />
          <stop offset="100%" stop-color="#ffffff" stop-opacity="0" />
        </linearGradient>
        <radialGradient :id="groundId" cx="50%" cy="50%" r="50%">
          <stop offset="0%" :stop-color="meta.color" stop-opacity="0.14" />
          <stop offset="100%" :stop-color="meta.color" stop-opacity="0" />
        </radialGradient>
        <filter :id="glowId" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="3" result="b" />
          <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <filter :id="leafShadowId" x="-40%" y="-40%" width="180%" height="180%">
          <feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#2a2a2a" flood-opacity="0.14" />
        </filter>
        <clipPath :id="trunkClipId">
          <path :d="trunkShape" />
        </clipPath>
      </defs>

      <!-- 地面 -->
      <ellipse :cx="ROOT_X" :cy="H - 22" rx="88" ry="14" :fill="`url(#${groundId})`" />
      <text :x="ROOT_X" :y="H - 4" class="root-label" text-anchor="middle">低空经济 · {{ meta.short }}</text>

      <!-- 树干（填充 + 高光 + 树皮纹理） -->
      <path :d="trunkShape" :fill="`url(#${trunkGradId})`" class="trunk-body" />
      <path :d="trunkShape" :fill="`url(#${trunkHiId})`" class="trunk-highlight" />
      <path :d="trunkShadePath" class="trunk-shade" :stroke="meta.color" />
      <g :clip-path="`url(#${trunkClipId})`" class="bark-layer">
        <path
          v-for="(cr, ci) in barkTexture.vertical"
          :key="`bv-${ci}`"
          :d="cr.d"
          class="bark-crack"
          :stroke="meta.color"
          :stroke-opacity="cr.opacity"
        />
        <path
          v-for="(hr, hi) in barkTexture.horizontal"
          :key="`bh-${hi}`"
          :d="hr.d"
          class="bark-ring"
          :stroke="meta.color"
          :stroke-opacity="hr.opacity"
        />
        <ellipse
          v-for="(kn, ki) in barkTexture.knots"
          :key="`bk-${ki}`"
          :cx="kn.cx"
          :cy="kn.cy"
          :rx="kn.r"
          :ry="kn.r * 0.72"
          class="bark-knot"
          :fill="meta.color"
          :fill-opacity="kn.opacity"
        />
      </g>

      <!-- 叶枝 -->
      <g
        v-for="leaf in leafLayout"
        :key="leaf.id"
        class="leaf-group"
        :class="{ selected: leaf.selected }"
        @click="onLeafClick(leaf.id)"
      >
        <path :d="leaf.petiole" class="petiole" :stroke="meta.color" />
        <path :d="leaf.twigs" class="twig" :stroke="meta.color" />
        <circle :cx="leaf.ax" :cy="leaf.ay" r="3.5" class="bud" :fill="meta.color" />
        <path
          :d="leaf.leafPath"
          class="leaf-shape"
          :fill="leaf.fill"
          :stroke="leaf.stroke"
          :filter="leaf.selected ? `url(#${glowId})` : `url(#${leafShadowId})`"
        />
        <path
          v-for="(vn, vi) in leaf.veins"
          :key="`vein-${leaf.id}-${vi}`"
          :d="vn"
          class="leaf-vein"
          :stroke="leaf.veinStroke"
        />
        <text
          :x="leaf.lx"
          :y="leaf.ly"
          class="leaf-text"
          :text-anchor="leaf.side < 0 ? 'end' : 'start'"
        >{{ leaf.label }}</text>
      </g>

      <!-- 层顶冠 -->
      <g class="crown" :filter="`url(#${glowId})`">
        <path
          :d="roundHexPath(TIP.x, TIP.y, 20, 5)"
          :fill="meta.color"
          fill-opacity="0.18"
          :stroke="meta.color"
          stroke-width="2.5"
        />
        <path
          :d="roundHexPath(TIP.x, TIP.y, 14, 3.5)"
          :fill="meta.color"
          fill-opacity="0.42"
        />
        <text :x="TIP.x" :y="TIP.y + 5" class="tip-count" text-anchor="middle">{{ points.length }}</text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { branchById, sortTechPoints, layerFromTree } from '../../constants/techTree.js'
import { roundHexPath } from '../../utils/roundHex.js'
import { buildLeafShape, pickLeafVariant, buildBarkTexture } from '../../utils/organicLeaf.js'
import { apiGet } from '../../composables/useApi'

const props = defineProps({
  layerId: { type: String, required: true },
  selectedTech: { type: String, default: '' },
})

const emit = defineEmits(['leaf-click'])

const PAD_X = 92
const INNER_W = 560
const W = INNER_W + PAD_X * 2
const H = 520
const ROOT_X = PAD_X + INNER_W / 2
const TIP = { x: ROOT_X - 6, y: 48 }

const loading = ref(true)
const tree = ref({ layers: [] })
const uid = Math.random().toString(36).slice(2, 8)
const trunkGradId = `trunkGrad-${uid}`
const trunkHiId = `trunkHi-${uid}`
const trunkClipId = `trunkClip-${uid}`
const groundId = `ground-${uid}`
const glowId = `trunkGlow-${uid}`
const leafShadowId = `leafShadow-${uid}`

const meta = computed(() => branchById(props.layerId) || { color: '#3d8bfd', short: '技术大类' })

const layerData = computed(() => layerFromTree(tree.value, props.layerId))

const points = computed(() => sortTechPoints(layerData.value?.tech_points || []))

const trunkCurve = computed(() => {
  const x0 = ROOT_X
  const y0 = H - 58
  const x1 = TIP.x
  const y1 = TIP.y + 16
  const cx = ROOT_X + 48
  const cy = H * 0.42
  return { x0, y0, x1, y1, cx, cy }
})

function trunkAt(t) {
  const { x0, y0, x1, y1, cx, cy } = trunkCurve.value
  const u = 1 - t
  return {
    x: u * u * x0 + 2 * u * t * cx + t * t * x1,
    y: u * u * y0 + 2 * u * t * cy + t * t * y1,
  }
}

function trunkTangent(t) {
  const { x0, y0, x1, y1, cx, cy } = trunkCurve.value
  const u = 1 - t
  return {
    x: 2 * u * (cx - x0) + 2 * t * (x1 - cx),
    y: 2 * u * (cy - y0) + 2 * t * (y1 - cy),
  }
}

/** 树干填充轮廓（上窄下宽） */
const trunkShape = computed(() => {
  const samples = 24
  const left = []
  const right = []
  for (let i = 0; i <= samples; i++) {
    const t = i / samples
    const p = trunkAt(t)
    const tan = trunkTangent(t)
    const len = Math.hypot(tan.x, tan.y) || 1
    const nx = -tan.y / len
    const ny = tan.x / len
    const half = 9 + (1 - t) * 14
    left.push({ x: p.x + nx * half, y: p.y + ny * half })
    right.unshift({ x: p.x - nx * half, y: p.y - ny * half })
  }
  const pts = [...left, ...right]
  return `${pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')} Z`
})

/** 树干左侧暗面，增强立体感 */
const trunkShadePath = computed(() => {
  const samples = 14
  const pts = []
  for (let i = 0; i <= samples; i++) {
    const t = i / samples
    const p = trunkAt(t)
    const tan = trunkTangent(t)
    const len = Math.hypot(tan.x, tan.y) || 1
    const nx = -tan.y / len
    const ny = tan.x / len
    const half = 9 + (1 - t) * 14
    pts.push({ x: p.x + nx * half * 0.72, y: p.y + ny * half * 0.72 })
  }
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
})

const barkTexture = computed(() => buildBarkTexture(trunkAt, trunkTangent))

function petiolePath(ax, ay, bx, by, side) {
  const mx = ax + (bx - ax) * 0.45 + side * 8
  const my = ay + (by - ay) * 0.45 - 10
  return `M ${ax} ${ay} Q ${mx} ${my} ${bx} ${by}`
}

function twigPath(ax, ay, bx, by, side) {
  const tx = ax + (bx - ax) * 0.25 + side * 14
  const ty = ay + (by - ay) * 0.25 - 6
  return `M ${ax} ${ay} Q ${tx} ${ty} ${bx} ${by}`
}

const leafLayout = computed(() => {
  const pts = points.value
  const n = pts.length
  return pts.map((pt, i) => {
    const t = n <= 1 ? 0.5 : 0.1 + (0.78 * i) / (n - 1)
    const anchor = trunkAt(t)
    const tan = trunkTangent(t)
    const tLen = Math.hypot(tan.x, tan.y) || 1
    const nx = -tan.y / tLen
    const ny = tan.x / tLen
    const side = i % 2 === 0 ? -1 : 1
    const spread = 92 + Math.floor(i / 2) * 14
    const lift = ((i % 3) - 1) * 6
    const selected = props.selectedTech === pt.tech_tag_id
    const leafW = selected ? 26 : 23

    const bx = anchor.x + nx * side * 24
    const by = anchor.y + ny * side * 24 + lift
    const tipX = bx + nx * side * spread * 0.74
    const tipY = by + ny * side * spread * 0.74
    const lx = tipX + nx * side * 44
    const ly = tipY + ny * side * 44 + 5

    const palette = leafPalette(pt, selected)
    const variant = pickLeafVariant(i, pt.tech_tag_id)
    const shape = buildLeafShape(variant, bx, by, tipX, tipY, leafW)

    return {
      id: pt.tech_tag_id,
      label: pt.tech_label,
      ax: anchor.x,
      ay: anchor.y,
      side,
      selected,
      petiole: petiolePath(anchor.x, anchor.y, bx, by, side),
      twigs: twigPath(anchor.x, anchor.y, bx, by, side),
      leafPath: shape.path,
      veins: shape.veins,
      lx,
      ly,
      ...palette,
    }
  })
})

function leafPalette(pt, selected) {
  if (selected) {
    return {
      fill: 'rgba(254,242,242,0.95)',
      stroke: '#ae0d28',
      veinStroke: 'rgba(174,13,40,0.45)',
    }
  }
  if (pt.survey_b_ready && (pt.paper_count_b || 0) > 50) {
    return {
      fill: 'rgba(34,197,94,0.88)',
      stroke: 'rgba(21,128,61,0.85)',
      veinStroke: 'rgba(21,128,61,0.5)',
    }
  }
  if (pt.survey_b_ready) {
    return {
      fill: 'rgba(245,158,11,0.9)',
      stroke: 'rgba(180,83,9,0.85)',
      veinStroke: 'rgba(146,64,14,0.45)',
    }
  }
  return {
    fill: 'rgba(120,113,108,0.82)',
    stroke: 'rgba(87,83,78,0.9)',
    veinStroke: 'rgba(68,64,60,0.45)',
  }
}

function onLeafClick(id) {
  emit('leaf-click', id)
}

onMounted(async () => {
  try {
    tree.value = await apiGet('/api/tech/tree')
  } catch { /* ignore */ }
  loading.value = false
})
</script>

<style scoped>
.layer-branch-tree {
  width: 100%;
  height: 100%;
  min-height: 460px;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(ellipse 80% 45% at 50% 88%, rgba(174, 13, 40, 0.06) 0%, transparent 70%),
    linear-gradient(180deg, #fdfcfb 0%, var(--surface-panel, #faf9f7) 100%);
  border-radius: 16px;
  border: 1px solid var(--border, #e8e4df);
}
.loading {
  text-align: center;
  padding: 120px 0;
  color: var(--muted, #78716c);
}
.branch-svg {
  width: 100%;
  height: 100%;
  min-height: 440px;
  max-height: 560px;
  display: block;
  overflow: visible;
}
.trunk-body { opacity: 0.96; }
.trunk-highlight { opacity: 0.55; pointer-events: none; }
.trunk-shade {
  fill: none;
  stroke-width: 2.5;
  stroke-opacity: 0.16;
  stroke-linecap: round;
  pointer-events: none;
}
.bark-layer { pointer-events: none; }
.bark-crack {
  fill: none;
  stroke-width: 1.4;
  stroke-linecap: round;
}
.bark-ring {
  fill: none;
  stroke-width: 1.1;
  stroke-linecap: round;
}
.bark-knot { pointer-events: none; }
.root-label {
  font-size: 14px;
  font-weight: 600;
  fill: #57534e;
}
.tip-count {
  font-size: 16px;
  font-weight: 800;
  fill: #2a2a2a;
  pointer-events: none;
}
.petiole {
  fill: none;
  stroke-width: 2.5;
  stroke-opacity: 0.55;
  stroke-linecap: round;
}
.twig {
  fill: none;
  stroke-width: 1.5;
  stroke-opacity: 0.35;
  stroke-linecap: round;
}
.bud {
  opacity: 0.75;
}
.leaf-group {
  cursor: pointer;
  transition: opacity 0.15s;
}
.leaf-group:not(.selected):hover { opacity: 0.92; }
.leaf-shape {
  stroke-width: 1.8;
  transition: transform 0.18s ease, stroke-width 0.15s;
  transform-box: fill-box;
  transform-origin: center;
}
.leaf-vein {
  fill: none;
  stroke-width: 1;
  pointer-events: none;
}
.leaf-group:hover .leaf-shape { transform: scale(1.08); stroke-width: 2.2; }
.leaf-group.selected .leaf-shape {
  stroke-width: 2.6;
  transform: scale(1.1);
}
.leaf-text {
  font-size: 15px;
  font-weight: 600;
  fill: #44403c;
  pointer-events: none;
  transition: fill 0.15s;
}
.leaf-group.selected .leaf-text {
  fill: #1c1917;
  font-weight: 700;
  font-size: 16px;
}
.leaf-group:hover .leaf-text { fill: #1c1917; }
</style>
