/** ECharts / 可视化 · 人大红浅色主题 */

/** 六大类技术树 — 色相拉开，避免多个红色相近 */
export const LAYER_COLORS = {
  layer_airframe: '#ae0d28',
  layer_control: '#1a4d7a',
  layer_sense: '#2d6a4f',
  layer_power: '#c45c00',
  layer_payload: '#6b4c9a',
  layer_safety: '#57534e',
}

export const LAYER_BRANCHES_PALETTE = [
  { id: 'layer_airframe', name: '平台构型与结构', short: '构型结构', color: LAYER_COLORS.layer_airframe, angle: -90 },
  { id: 'layer_control', name: '飞控导航与自主', short: '飞控导航', color: LAYER_COLORS.layer_control, angle: -30 },
  { id: 'layer_sense', name: '感知避障与数据', short: '感知数据', color: LAYER_COLORS.layer_sense, angle: 30 },
  { id: 'layer_power', name: '能源动力与链路', short: '能源链路', color: LAYER_COLORS.layer_power, angle: 90 },
  { id: 'layer_payload', name: '任务载荷与作业', short: '任务载荷', color: LAYER_COLORS.layer_payload, angle: 150 },
  { id: 'layer_safety', name: '安全运维与地面', short: '安全运维', color: LAYER_COLORS.layer_safety, angle: 210 },
]

/** 证据链节点 — 与 LAYER 同系，六色可辨 */
export const EVIDENCE_NODE_COLORS = {
  fund: '#ae0d28',
  paper: '#1a4d7a',
  patent: '#c45c00',
  tech_point: '#2d6a4f',
  product: '#6b4c9a',
  industry: '#57534e',
}

export const EVIDENCE_EDGE_COLORS = {
  fund_supports: '#ae0d28',
  paper_hits_tech: '#1a4d7a',
  patent_hits_tech: '#c45c00',
  tech_to_product: '#2d6a4f',
  product_to_industry: '#6b4c9a',
}

/** 指标卡片四色（支撑范围/影响力度） */
export const METRIC_CARD_COLORS = ['#ae0d28', '#1a4d7a', '#2d6a4f', '#c45c00']

export const RUC_PALETTE = [
  '#ae0d28',
  '#1a4d7a',
  '#2d6a4f',
  '#c45c00',
  '#6b4c9a',
  '#57534e',
  '#9b0000',
  '#78716c',
]

export const CHART = {
  axis: { color: '#78716c', fontSize: 10 },
  label: { color: '#4a4540' },
  splitLine: { lineStyle: { color: '#e8e4df' } },
  tooltip: {
    confine: true,
    backgroundColor: '#fffffffa',
    borderColor: '#e2d5d9',
    padding: [11, 14],
    extraCssText: 'box-shadow:0 6px 22px #49212c16;border-radius:8px;',
    textStyle: { color: '#344054', fontSize: 14, lineHeight: 22 },
  },
  legend: { textStyle: { color: '#78716c', fontSize: 11 } },
  radar: {
    axisName: { color: '#78716c', fontSize: 11 },
    splitLine: { lineStyle: { color: '#e8e4df' } },
    splitArea: { areaStyle: { color: ['rgba(174,13,40,0.04)', 'rgba(174,13,40,0.02)'] } },
  },
}

/** 浅色画布上的 SVG / ECharts 标签 */
export const CANVAS_LABEL = {
  primary: '#2a2a2a',
  secondary: '#4a4540',
  muted: '#78716c',
  dimmed: '#a8a29e',
  onNode: '#ffffff',
}

export function chartXAxis(data = []) {
  return {
    type: 'category',
    data,
    axisLabel: CHART.axis,
    axisLine: { lineStyle: { color: '#e8e4df' } },
  }
}

export function chartYAxis(extra = {}) {
  return {
    type: 'value',
    axisLabel: CHART.axis,
    splitLine: CHART.splitLine,
    ...extra,
  }
}

export function paletteColor(i) {
  return RUC_PALETTE[i % RUC_PALETTE.length]
}

export function rucAlpha(hex, alpha = 0.12) {
  return `${hex}${Math.round(alpha * 255).toString(16).padStart(2, '0')}`
}

/** 证据链流程图节点 */
export const CHAIN_COLORS = {
  fund: { fill: 'rgba(174,13,40,0.14)', ring: '#ae0d28', line: '#ae0d28' },
  paper: { fill: 'rgba(26,77,122,0.12)', ring: '#1a4d7a', line: '#1a4d7a' },
  patent: { fill: 'rgba(196,92,0,0.12)', ring: '#c45c00', line: '#c45c00' },
  tech: { fill: 'rgba(45,106,79,0.12)', ring: '#2d6a4f', line: '#2d6a4f' },
  product: { fill: 'rgba(107,76,154,0.12)', ring: '#6b4c9a', line: '#6b4c9a' },
  link: ['#ae0d28', '#c45c00', '#1a4d7a', '#57534e'],
  impact: ['#ae0d28', '#1a4d7a', '#2d6a4f'],
}
