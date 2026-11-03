<template>
  <div class="chain-flow-visual">
    <svg
      class="flow-svg"
      :viewBox="`0 0 ${G.w} ${G.h}`"
      preserveAspectRatio="xMidYMid meet"
      role="img"
      aria-label="证据链汇流图"
    >
      <defs>
        <marker id="cf-arrow" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" refX="7.5" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill="context-stroke" />
        </marker>
        <marker id="cf-arrow-dash" markerUnits="userSpaceOnUse" markerWidth="8" markerHeight="8" refX="7.5" refY="4" orient="auto">
          <path d="M0,0 L8,4 L0,8 Z" fill="#1a4d7a" opacity="0.7" />
        </marker>
        <marker id="cf-arrow-hub" markerUnits="userSpaceOnUse" markerWidth="9" markerHeight="9" refX="8.5" refY="4.5" orient="auto">
          <path d="M0,0 L9,4.5 L0,9 Z" fill="#6b4c9a" />
        </marker>
        <linearGradient id="cf-hub-grad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#2d6a4f" />
          <stop offset="100%" stop-color="#6b4c9a" />
        </linearGradient>
      </defs>

      <!-- 四等分阶段线 -->
      <line
        v-for="d in dividers"
        :key="d"
        :x1="d" y1="36" :x2="d" :y2="G.h - 16"
        class="stage-line"
      />
      <text
        v-for="s in stages"
        :key="s.label"
        :x="s.x" y="22"
        class="stage-label"
      >{{ s.label }}</text>

      <!-- 连线：底轨 + 流动动画层 -->
      <g v-for="(e, i) in flowEdges" :key="e.id" class="edge-group">
        <path :d="e.d" :class="['edge', 'edge-track', e.track]" />
        <path
          :d="e.d"
          :class="['edge', 'edge-flow', e.flow, { 'edge-dash': e.dashed }]"
          :style="{ animationDelay: `${i * 0.15}s` }"
          :marker-end="e.marker"
        />
      </g>

      <!-- 资源：圆圈（竖排） -->
      <g v-for="n in resourceNodes" :key="n.id" class="node-group">
        <circle
          :cx="n.cx" :cy="n.cy" :r="G.r"
          :fill="n.bg" :stroke="n.color" stroke-width="3"
        />
        <text :x="n.cx" :y="n.cy - 14" class="node-val" :fill="n.color">{{ n.val }}</text>
        <text :x="n.cx" :y="n.cy + 8" class="node-label">{{ n.label }}</text>
        <text :x="n.cx" :y="n.cy + 26" class="node-tag">{{ n.tag }}</text>
      </g>

      <!-- 关联：方框（三行独立，互不重叠） -->
      <g v-for="n in linkNodes" :key="n.id" class="node-group">
        <rect
          :x="n.x" :y="n.y" :width="G.sq.w" :height="G.sq.h" rx="10"
          :fill="n.bg" :stroke="n.color" :stroke-width="n.dashed ? 2 : 3"
          :stroke-dasharray="n.dashed ? '7 5' : undefined"
        />
        <text :x="n.cx" :y="n.cy - 8" class="node-val" :fill="n.color">{{ n.val }}</text>
        <text :x="n.cx" :y="n.cy + 16" class="node-label">{{ n.label }}</text>
      </g>

      <!-- 汇流 / 落地：六边形 -->
      <g v-for="n in hubNodes" :key="n.id" class="node-group">
        <polygon
          :points="hexPoints(n.cx, n.cy, n.size)"
          :fill="n.bg" :stroke="n.color" stroke-width="3"
        />
        <text :x="n.cx" :y="n.cy - 10" class="node-val hub-val" :fill="n.color">{{ n.val }}</text>
        <text :x="n.cx" :y="n.cy + 12" class="node-label hub-label">{{ n.label }}</text>
        <text :x="n.cx" :y="n.cy + 28" class="node-tag">{{ n.tag }}</text>
      </g>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { fmtCount } from '../../composables/useApi'
import { CHAIN_COLORS } from '../../constants/chartTheme.js'
import {
  FUND_PAPER_LINKS, PATENT_TECH_LINKS, SKILLS_B_PAPERS,
  LA_PATENT_COUNT, TECH_TAG_COUNT, DJI_CASE_PRODUCTS, metric,
} from '../../constants/dataCatalog.js'

const props = defineProps({
  contrib: { type: Object, default: () => ({}) },
  progress: { type: Object, default: () => ({}) },
  chainStatus: { type: Array, default: () => [] },
})

/** 画布四等分，元素放大，方框纵向留足间距 */
const G = {
  w: 1200,
  h: 400,
  colW: 300,
  cx: [150, 450, 750, 1050],
  resY: [108, 220, 332],
  hubY: 220,
  r: 44,
  sq: { w: 128, h: 72 },
  hex: { tech: 58, product: 50 },
}

const linkY = {
  fundPaper: 152,
  skills: 248,
  patent: 332,
}

const dividers = [G.colW, G.colW * 2, G.colW * 3]
const stages = G.cx.map((x, i) => ({
  x,
  label: ['资源库', '已建关联', '汇流', '落地'][i],
}))

function chainCount(type, contribKey, fallback) {
  const ch = props.chainStatus.find(s => s.chain_type === type)
  return ch?.count ?? props.contrib[contribKey] ?? fallback ?? 0
}

const counts = computed(() => ({
  fundPaper: chainCount('fund_paper_tech', 'fund_paper_links', FUND_PAPER_LINKS),
  patentTech: chainCount('patent_tech', 'patent_tech_links', PATENT_TECH_LINKS),
  paperTech: chainCount('paper_tech', 'paper_tech_links', SKILLS_B_PAPERS),
}))

const techCount = computed(() => String(props.progress.tech_tags ?? TECH_TAG_COUNT))

const ACCENT = {
  fund: { color: '#ae0d28', bg: CHAIN_COLORS.fund.fill },
  paper: { color: '#1a4d7a', bg: CHAIN_COLORS.paper.fill },
  patent: { color: '#c45c00', bg: CHAIN_COLORS.patent.fill },
  tech: { color: '#2d6a4f', bg: CHAIN_COLORS.tech.fill },
  product: { color: '#6b4c9a', bg: CHAIN_COLORS.product.fill },
  skills: { color: '#1a4d7a', bg: 'rgba(26,77,122,0.08)' },
}

const resX = G.cx[0]
const resOut = resX + G.r

function sqAt(cy) {
  return {
    x: G.cx[1] - G.sq.w / 2,
    y: cy - G.sq.h / 2,
    cx: G.cx[1],
    cy,
    left: G.cx[1] - G.sq.w / 2,
    right: G.cx[1] + G.sq.w / 2,
  }
}

const boxes = {
  fundPaper: sqAt(linkY.fundPaper),
  skills: sqAt(linkY.skills),
  patent: sqAt(linkY.patent),
}

const resourceNodes = computed(() => [
  {
    id: 'fund', cx: resX, cy: G.resY[0],
    val: fmtCount(metric('nsfc_fund_projects')),
    label: '基金项目', tag: '全库',
    ...ACCENT.fund,
  },
  {
    id: 'paper', cx: resX, cy: G.resY[1],
    val: fmtCount(metric('nsfc_papers')),
    label: '论文条目', tag: '全库',
    ...ACCENT.paper,
  },
  {
    id: 'patent', cx: resX, cy: G.resY[2],
    val: fmtCount(LA_PATENT_COUNT),
    label: '专利', tag: '领域',
    ...ACCENT.patent,
  },
])

const linkNodes = computed(() => [
  {
    id: 'fund-paper', ...boxes.fundPaper,
    val: fmtCount(counts.value.fundPaper),
    label: '基金↔论文',
    ...ACCENT.fund,
  },
  {
    id: 'skills', ...boxes.skills,
    val: fmtCount(counts.value.paperTech),
    label: '技术点对应文献池',
    dashed: true,
    ...ACCENT.skills,
  },
  {
    id: 'patent-tech', ...boxes.patent,
    val: fmtCount(counts.value.patentTech),
    label: '专利→技术',
    ...ACCENT.patent,
  },
])

const hubNodes = computed(() => [
  {
    id: 'tech',
    cx: G.cx[2], cy: G.hubY,
    size: G.hex.tech,
    val: techCount.value,
    label: '技术词典', tag: '六大类·技术点',
    ...ACCENT.tech,
  },
  {
    id: 'product',
    cx: G.cx[3], cy: G.hubY,
    size: G.hex.product,
    val: String(DJI_CASE_PRODUCTS),
    label: '大疆产品', tag: '系列·单品',
    ...ACCENT.product,
  },
])

function hexPoints(cx, cy, size) {
  const pts = []
  for (let i = 0; i < 6; i++) {
    const ang = (Math.PI / 3) * i - Math.PI / 6
    pts.push(`${cx + size * Math.cos(ang)},${cy + size * Math.sin(ang)}`)
  }
  return pts.join(' ')
}

function hexEdgeX(cx, size, side = 'left') {
  const offset = size * Math.cos(Math.PI / 6)
  return side === 'left' ? cx - offset : cx + offset
}

function cubic(x0, y0, cx1, cy1, cx2, cy2, x1, y1) {
  return `M ${x0} ${y0} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x1} ${y1}`
}

const paths = computed(() => {
  const b1 = boxes.fundPaper
  const b2 = boxes.skills
  const b3 = boxes.patent
  const [yFund, yPaper, yPatent] = G.resY
  const techIn = hexEdgeX(G.cx[2], G.hex.tech, 'left')
  const techOut = hexEdgeX(G.cx[2], G.hex.tech, 'right')
  const prodIn = hexEdgeX(G.cx[3], G.hex.product, 'left')

  return {
    fundToLink: cubic(
      resOut, yFund,
      resOut + 70, yFund,
      b1.left - 50, linkY.fundPaper - 20,
      b1.left, linkY.fundPaper,
    ),
    paperToLink: cubic(
      resOut, yPaper,
      resOut + 60, yPaper,
      b1.left - 40, linkY.fundPaper + 24,
      b1.left, linkY.fundPaper + 8,
    ),
    paperToSkills: cubic(
      resOut, yPaper + 8,
      resOut + 80, yPaper + 30,
      b2.left - 45, linkY.skills,
      b2.left, linkY.skills,
    ),
    patentToLink: cubic(
      resOut, yPatent,
      resOut + 90, yPatent,
      b3.left - 40, yPatent,
      b3.left, yPatent,
    ),
    link1ToTech: cubic(
      b1.right, linkY.fundPaper,
      b1.right + 80, linkY.fundPaper - 10,
      techIn - 70, G.hubY - 28,
      techIn, G.hubY - 8,
    ),
    link2ToTech: cubic(
      b2.right, linkY.skills,
      b2.right + 90, linkY.skills,
      techIn - 60, G.hubY + 4,
      techIn, G.hubY + 2,
    ),
    link3ToTech: cubic(
      b3.right, linkY.patent,
      b3.right + 80, linkY.patent + 10,
      techIn - 70, G.hubY + 30,
      techIn, G.hubY + 10,
    ),
    techToProduct: cubic(
      techOut, G.hubY,
      techOut + 80, G.hubY - 18,
      prodIn - 80, G.hubY + 18,
      prodIn, G.hubY,
    ),
  }
})

const flowEdges = computed(() => {
  const p = paths.value
  const arrow = 'url(#cf-arrow)'
  const arrowDash = 'url(#cf-arrow-dash)'
  const arrowHub = 'url(#cf-arrow-hub)'
  return [
    { id: 'fundToLink', d: p.fundToLink, track: 'track-fund', flow: 'flow-fund', marker: arrow },
    { id: 'paperToLink', d: p.paperToLink, track: 'track-paper', flow: 'flow-paper', marker: arrow },
    { id: 'paperToSkills', d: p.paperToSkills, track: 'track-skills', flow: 'flow-skills', dashed: true, marker: arrowDash },
    { id: 'patentToLink', d: p.patentToLink, track: 'track-patent', flow: 'flow-patent', marker: arrow },
    { id: 'link1ToTech', d: p.link1ToTech, track: 'track-fund', flow: 'flow-fund', marker: arrow },
    { id: 'link2ToTech', d: p.link2ToTech, track: 'track-skills', flow: 'flow-skills', dashed: true, marker: arrowDash },
    { id: 'link3ToTech', d: p.link3ToTech, track: 'track-patent', flow: 'flow-patent', marker: arrow },
    { id: 'techToProduct', d: p.techToProduct, track: 'track-hub', flow: 'flow-hub', marker: arrowHub },
  ]
})
</script>

<style scoped>
.chain-flow-visual {
  margin-bottom: 8px;
}

.flow-svg {
  display: block;
  width: 100%;
  height: auto;
  aspect-ratio: 1200 / 400;
  max-height: 420px;
  border-radius: 16px;
  background: var(--surface-panel);
  border: 1px solid var(--card-border);
}

.stage-line {
  stroke: rgba(120, 113, 108, 0.12);
  stroke-width: 1;
  stroke-dasharray: 5 7;
}
.stage-label {
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.14em;
  fill: #a8a29e;
  text-anchor: middle;
}

.edge {
  fill: none;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.edge-track {
  stroke-width: 5;
  opacity: 0.14;
}
.track-fund { stroke: #ae0d28; }
.track-paper { stroke: #1a4d7a; }
.track-patent { stroke: #c45c00; }
.track-skills { stroke: #1a4d7a; }
.track-hub { stroke: #6b4c9a; opacity: 0.18; }

.edge-flow {
  stroke-width: 3;
  stroke-dasharray: 10 8;
  animation: cf-flow 1.4s linear infinite;
}
.edge-flow.edge-dash {
  stroke-dasharray: 8 7;
  animation: cf-flow-dash 1.6s linear infinite;
}

.flow-fund { stroke: #ae0d28; opacity: 0.82; }
.flow-paper { stroke: #1a4d7a; opacity: 0.78; }
.flow-patent { stroke: #c45c00; opacity: 0.82; }
.flow-skills { stroke: #1a4d7a; opacity: 0.68; }
.flow-hub {
  stroke: url(#cf-hub-grad);
  opacity: 0.92;
  stroke-width: 3.5;
  stroke-dasharray: 12 8;
  animation: cf-flow-hub 1.2s linear infinite;
}

@keyframes cf-flow {
  to { stroke-dashoffset: -36; }
}
@keyframes cf-flow-dash {
  to { stroke-dashoffset: -30; }
}
@keyframes cf-flow-hub {
  to { stroke-dashoffset: -40; }
}

@media (prefers-reduced-motion: reduce) {
  .edge-flow {
    animation: none;
    stroke-dasharray: none;
  }
}

.node-group circle,
.node-group rect,
.node-group polygon {
  filter: drop-shadow(0 4px 10px rgba(42, 28, 28, 0.09));
}

.node-val {
  font-size: 16px;
  font-weight: 900;
  text-anchor: middle;
  font-variant-numeric: tabular-nums;
}
.hub-val { font-size: 20px; }

.node-label {
  font-size: 12px;
  font-weight: 700;
  fill: #2a2a2a;
  text-anchor: middle;
}
.hub-label { font-size: 13px; }

.node-tag {
  font-size: 10px;
  font-weight: 600;
  fill: #78716c;
  text-anchor: middle;
}

@media (max-width: 640px) {
  .flow-svg { max-height: 360px; }
  .node-val { font-size: 14px; }
  .hub-val { font-size: 17px; }
  .node-label { font-size: 11px; }
}
</style>
