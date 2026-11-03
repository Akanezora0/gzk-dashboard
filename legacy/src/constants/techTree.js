/** 六大类技术树：枝干布局与配色（主页树 & 案例页共用） */

import { LAYER_BRANCHES_PALETTE } from './chartTheme.js'

export const LAYER_BRANCHES = LAYER_BRANCHES_PALETTE

export function branchById(id) {
  return LAYER_BRANCHES.find(b => b.id === id)
}

/** 技术点沿枝干的排序：Survey 定稿前按文献规模代理成熟度 */
export function sortTechPoints(points = []) {
  return [...points].sort((a, b) => {
    const pa = a.paper_count_b ?? 0
    const pb = b.paper_count_b ?? 0
    if (pb !== pa) return pb - pa
    return (a.tech_label || '').localeCompare(b.tech_label || '', 'zh')
  })
}

export function layerFromTree(tree, layerId) {
  return (tree?.layers || []).find(l => l.tech_layer_id === layerId)
}

/**
 * 各层技术点「放射状开花」参数（按层单独调）
 * arcSpan: 弧宽（度）；angleBias: 弧心微调
 * baseDist / ringStep: 圈半径（已含防重叠下限）
 * minStem: 花梗可见最短长度（px）
 */
export const LAYER_BLOOM_PROFILES = {
  /** 8 点 · 顶部 · 双圈 — 已确认 OK */
  layer_airframe: { arcSpan: 156, angleBias: 0, baseDist: 96, ringStep: 62, perRing: 4, layerEdge: 50, minStem: 42, labelMax: 8 },
  /** 5 点 · 右上 · 单圈宽弧 */
  layer_control: { arcSpan: 152, angleBias: -4, baseDist: 108, ringStep: 64, perRing: 5, layerEdge: 48, minStem: 40, labelMax: 8 },
  /** 4 点 · 左上 — 已确认 OK */
  layer_sense: { arcSpan: 112, angleBias: -6, baseDist: 94, ringStep: 56, perRing: 4, layerEdge: 48, minStem: 38, labelMax: 8 },
  /** 5 点 · 底部 · 单圈宽弧（略偏上，避开底部提示卡） */
  layer_power: { arcSpan: 148, angleBias: -14, baseDist: 106, ringStep: 64, perRing: 5, layerEdge: 48, minStem: 40, labelMax: 8 },
  /** 7 点 · 左下 · 紧凑双圈 4+3 */
  layer_payload: {
    arcSpan: 132,
    angleBias: 2,
    baseDist: 86,
    ringStep: 44,
    perRing: 4,
    layerEdge: 50,
    minStem: 36,
    tripleArcScale: 0.82,
    ringStaggerScale: 0.72,
    maxDistExtra: 68,
    ringDistCaps: [136, 192],
    minRingGap: 50,
    leafGap: 11,
    focusScaleBoost: 1.2,
    resolveCollisions: true,
    collisionNudge: 16,
    labelMax: 8,
  },
  /** 4 点 · 左下 — 已确认 OK */
  layer_safety: { arcSpan: 108, angleBias: -6, baseDist: 94, ringStep: 56, perRing: 4, layerEdge: 48, minStem: 38, labelMax: 8 },
}

export const DEFAULT_BLOOM_PROFILE = {
  arcSpan: 128, angleBias: 0, baseDist: 92, ringStep: 58, perRing: 4, layerEdge: 48, minStem: 38, labelMax: 8,
}
