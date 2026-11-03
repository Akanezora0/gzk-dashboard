/** 证据链分页面文案与边类型说明 */

import { EVIDENCE_NODE_COLORS, EVIDENCE_EDGE_COLORS } from './chartTheme.js'
import {
  LA_PATENT_COUNT, PATENT_TECH_LINKS, FUND_PAPER_LINKS, TECH_TAG_COUNT, SKILLS_B_PAPERS,
  metric,
} from './dataCatalog.js'

export const CHAIN_EDGE_META = {
  fund_supports: { label: '基金资助', color: EVIDENCE_EDGE_COLORS.fund_supports, desc: '基金项目与论文直接映射入库' },
  paper_hits_tech: { label: '论文命中技术点', color: EVIDENCE_EDGE_COLORS.paper_hits_tech, desc: 'Skills/OpenScholar 文献认领至技术词典' },
  patent_hits_tech: { label: '专利归类技术', color: EVIDENCE_EDGE_COLORS.patent_hits_tech, desc: '规则 + LLM 专利—技术术语匹配' },
  tech_to_product: { label: '技术落地产品', color: EVIDENCE_EDGE_COLORS.tech_to_product, desc: '技术点映射示范产品' },
  product_to_industry: { label: '产品进入产业链', color: EVIDENCE_EDGE_COLORS.product_to_industry, desc: '产品节点对接发改委产业链体系' },
}

export const CHAIN_NODE_META = {
  fund: { label: '基金项目', color: EVIDENCE_NODE_COLORS.fund, icon: 'fund' },
  paper: { label: '论文', color: EVIDENCE_NODE_COLORS.paper, icon: 'paper' },
  patent: { label: '专利', color: EVIDENCE_NODE_COLORS.patent, icon: 'patent' },
  tech_point: { label: '技术点', color: EVIDENCE_NODE_COLORS.tech_point, icon: 'tech' },
  product: { label: '示范产品', color: EVIDENCE_NODE_COLORS.product, icon: 'product' },
  industry: { label: '产业链', color: EVIDENCE_NODE_COLORS.industry, icon: 'industry' },
}

export const CHAIN_HERO = {
  tag: '可验证证据链',
  title: '成果如何进入技术演进？',
  desc: '从基金投入、论文与专利成果，到 33 个技术点与示范产品，每条关联可追溯至 SQLite 证据仓或 Skills 文献认领，支撑后续结论产出。',
  pillars: [
    { key: 'trace', title: '可追溯', text: '节点携带来源 ID、匹配置信度与匹配方法' },
    { key: 'multi', title: '多源并行', text: '基金—论文主链与专利—技术链在技术词典汇合' },
    { key: 'layer', title: '三维评估', text: '支撑范围 · 影响力度 · 产业渗透衡量基金贡献' },
  ],
}

export function statusLabel(s) {
  return { verified: '已验证', partial: '部分可用', candidate: '候选扩量', in_progress: '建设中' }[s] || s
}

export function confidenceLabel(c) {
  if (c >= 0.9) return '高置信'
  if (c >= 0.7) return '中置信'
  return '待复核'
}

/** 聚合 DAG 默认展示（API 不可用或 aggregate 参数未生效时的兜底） */
export const FALLBACK_AGGREGATE_GRAPH = {
  chain_type: 'aggregate_overview',
  nodes: [
    { id: 'agg:fund', type: 'fund', label: '基金项目', count: FUND_PAPER_LINKS, status: 'verified' },
    { id: 'agg:paper', type: 'paper', label: '论文成果', count: FUND_PAPER_LINKS, status: 'verified' },
    { id: 'agg:patent', type: 'patent', label: '专利成果', count: LA_PATENT_COUNT, status: 'verified' },
    { id: 'agg:tech', type: 'tech_point', label: '技术点', count: TECH_TAG_COUNT, status: 'verified' },
    { id: 'agg:product', type: 'product', label: '示范产品', count: metric('demo_products'), status: 'verified' },
    { id: 'agg:industry', type: 'industry', label: '产业链节点', count: metric('industry_chain_nodes'), status: 'partial' },
  ],
  edges: [
    { source: 'agg:fund', target: 'agg:paper', type: 'fund_supports', confidence: 0.95, match_method: 'direct_mapping' },
    { source: 'agg:paper', target: 'agg:tech', type: 'paper_hits_tech', confidence: 0.8, match_method: 'semantic_match' },
    { source: 'agg:patent', target: 'agg:tech', type: 'patent_hits_tech', confidence: 0.85, match_method: 'rule_match' },
    { source: 'agg:tech', target: 'agg:product', type: 'tech_to_product', confidence: 0.9, match_method: 'direct_mapping' },
    { source: 'agg:product', target: 'agg:industry', type: 'product_to_industry', confidence: 0.75, match_method: 'candidate' },
  ],
  meta: { fund_paper_pairs: FUND_PAPER_LINKS, patent_tech_links: PATENT_TECH_LINKS, aggregated: true, fallback: true },
}
