/** 证据链分页面 Tab 配置 */

import { EVIDENCE_NODE_COLORS, RUC_PALETTE } from './chartTheme.js'
import {
  LA_PATENT_COUNT, PATENT_TECH_LINKS, FUND_PAPER_LINKS,
  TECH_TAG_COUNT, SKILLS_B_PAPERS, metric,
} from './dataCatalog.js'

export const CHAIN_TAB_PROFILES = {
  overview: {
    heroTag: '证据链总览',
    heroTitle: '多源成果如何汇入技术词典？',
    heroDesc: '以技术供需逻辑出发，探索低空经济产业。',
    heroBullets: [
      '资源库汇聚基金项目、资助论文与领域专利等多源成果，形成可扩展数据底座',
      '关联层记录基金—论文、专利—技术等已入库关系，支撑证据追溯与复核',
      '以六大类 33 点技术词典为汇流锚点，贯通成果贡献评估与示范产品映射',
    ],
    insight: '',
    highlights: [
      { value: fmtWan(metric('nsfc_fund_projects')), label: '基金项目', hint: 'NSFC 全库立项', color: EVIDENCE_NODE_COLORS.fund },
      { value: fmtWan(metric('nsfc_papers')), label: '基金资助论文条目', hint: 'NSFC 全库目录', color: EVIDENCE_NODE_COLORS.paper },
      { value: fmtWan(LA_PATENT_COUNT), label: '规则筛选专利', hint: '领域专利', color: EVIDENCE_NODE_COLORS.patent },
      { value: String(TECH_TAG_COUNT), label: '技术词典节点', hint: '六大类', color: EVIDENCE_NODE_COLORS.tech_point },
    ],
  },
  tech_tree: {
    heroTag: '技术树',
    heroTitle: '低空经济六大类技术树',
    heroDesc: '面向低空经济全产业链，按构型结构、飞控导航、感知数据、能源链路、任务载荷、安全运维六大类组织技术体系，是证据链汇流与成果评估的统一锚点。',
    heroBullets: [
      '六大类结构覆盖平台构型、飞控感知、能源载荷与安全运维等关键环节，共 33 个技术点',
      '各技术点挂载 Survey 摘要与文献统计，支持按大类展开、逐点查阅',
      '与基金—论文、专利—技术等证据链在节点层汇合，可联动追溯关联成果',
    ],
    insight: '',
    highlights: [
      { value: '6', label: '技术大类', color: EVIDENCE_NODE_COLORS.tech_point },
      { value: '33', label: '技术点', color: RUC_PALETTE[2] },
      { value: String(SKILLS_B_PAPERS), label: '文献池', color: EVIDENCE_NODE_COLORS.paper },
      { value: '66', label: 'survey', color: RUC_PALETTE[3] },
    ],
  },
  fund_paper: {
    heroTag: '基金 → 论文 → 技术',
    heroTitle: '基金资助如何转化为技术证据？',
    heroDesc: '从基金项目与资助论文的直接映射出发，经文献语义匹配命中技术词典中的具体技术点。',
    insight: '点击图中节点或连线查看匹配置信度与匹配方法，证据可追溯。',
    highlights: [
      { value: fmtWan(metric('nsfc_fund_projects')), label: '基金项目', color: EVIDENCE_NODE_COLORS.fund },
      { value: String(FUND_PAPER_LINKS), label: '基金→论文关系', color: EVIDENCE_NODE_COLORS.paper },
      { value: String(FUND_PAPER_LINKS), label: '基金→论文→技术', hint: '主链', color: RUC_PALETTE[2] },
      { value: String(SKILLS_B_PAPERS), label: '论文→技术认领', hint: 'Skills', color: RUC_PALETTE[3] },
    ],
  },
  patent: {
    heroTag: '专利 → 技术',
    heroTitle: '专利成果如何支撑技术演进？',
    heroDesc: '领域专利与技术术语关联，规则与语义混合归类，按置信度排序展示样本边。',
    insight: '专利链与基金—论文链并行，在技术词典节点汇合。',
    highlights: [
      { value: fmtWan(LA_PATENT_COUNT), label: '规则筛选专利', color: EVIDENCE_NODE_COLORS.patent },
      { value: fmtWan(PATENT_TECH_LINKS), label: '专利→技术关系', color: RUC_PALETTE[3] },
      { value: '33', label: '技术点覆盖', color: EVIDENCE_NODE_COLORS.tech_point },
      { value: '规则+语义', label: '匹配策略', color: RUC_PALETTE[5] },
    ],
  },
  contribution: {
    heroTag: '基金贡献度',
    heroTitle: '基金投入产生了多大技术影响？',
    heroDesc: '支撑范围衡量基金支撑覆盖面，影响力度衡量文献质量与被引，产业渗透追踪技术复用与产业链进入。',
    insight: '筛选器可按技术大类与年份切片；产业渗透指标后续接入证据链复用统计。',
    highlights: [
      { value: '30.6%', label: '基金支撑文献占比', color: EVIDENCE_NODE_COLORS.fund },
      { value: '38.7%', label: '高被引文献占比', color: EVIDENCE_NODE_COLORS.paper },
      { value: '6', label: '技术大类覆盖', color: EVIDENCE_NODE_COLORS.tech_point },
      { value: String(TECH_TAG_COUNT), label: '技术点覆盖', color: EVIDENCE_NODE_COLORS.product },
    ],
  },
}

function fmtWan(n) {
  if (n == null || n === 0) return '—'
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`
  return String(n)
}

export const CHAIN_PIPELINE = [
  { step: 1, title: '多源采集', desc: '基金项目、资助论文、领域专利等成果入库', source: '专题库 + 平台数据' },
  { step: 2, title: '直接映射', desc: '基金→论文、专利→技术等高置信关系构建', source: '主链' },
  { step: 3, title: '语义认领', desc: '33 技术点文献池标题匹配', source: 'Skills' },
  { step: 4, title: '技术汇合', desc: '多源关系边汇入六大类技术词典', source: '33 技术点' },
  { step: 5, title: '贡献评估', desc: '支撑范围、影响力度、产业渗透定量分析', source: '贡献度 Tab' },
]

export const DATA_SOURCE_FOOTNOTE = []
