/** 站点信息架构与页面元数据 */

import { dataHubTabs } from './dataCatalog.js'

// export const SITE_TITLE = '低空经济技术供给全景监测'
export const SITE_TITLE = '基础研究促进经济发展全景监测'
export const SITE_SUBTITLE = '一屏总览 · 基金—成果—技术—产业证据链 · 示范领域：低空经济'

export const NAV_ITEMS = [
  { path: '/overview', label: '总览', short: '总览' },
  { path: '/data', label: '低空经济领域数据', short: '领域数据' },
  { path: '/chain', label: '证据链', short: '证据链' },
  { path: '/case', label: '案例展示', short: '案例展示' },
]

export const QUESTIONS = {
  Q1: {
    id: 'Q1',
    title: '产业关键技术如何演进？',
    summary: '以技术词典为主线，关联论文、专利、机构、基金，展示分阶段演进时间线与可验证证据链。',
    path: '/chain',
    tab: 'tech_tree',
    outputs: ['技术演进时间线', '代表论文/专利/基金', 'Survey 与自动化报告'],
  },
  Q2: {
    id: 'Q2',
    title: '代表性成果如何推动技术演进？',
    summary: '以产业关键产品为锚点，追踪论文/专利经技术点进入产业节点的证据链，评估成果推动力。',
    path: '/chain',
    tab: 'fund_paper',
    outputs: ['成果—技术—产业证据链', '代表性成果清单', '案例化展示'],
  },
  Q3: {
    id: 'Q3',
    title: '基金投入对技术发展的贡献有多大？',
    summary: '基金→论文/专利→技术为核心，从支撑范围、影响力度、产业渗透衡量基金支撑与影响力。',
    path: '/chain',
    tab: 'contribution',
    outputs: ['基金贡献度指标', '分层评估框架', '定量+案例报告'],
  },
}

export const PAGE_META = {
  overview: {
    title: '总览',
    breadcrumb: [{ label: '总览', path: '/overview' }],
    intro: '多源数据底座、证据链与示范领域技术演进一屏总览。',
  },
  data: {
    title: '低空经济领域数据展示',
    breadcrumb: [
      { label: '总览', path: '/overview' },
      { label: '低空经济领域数据', path: '/data' },
    ],
    intro: '聚焦低空经济示范领域，展示论文、专利、基金、新闻、政策、产品、行研报告等数据规模分布。',
  },
  chain: {
    title: '证据链',
    breadcrumb: [
      { label: '总览', path: '/overview' },
      { label: '证据链', path: '/chain' },
    ],
    // intro: '基金—论文/专利—技术点可验证关联链路，六大类技术树与基金贡献分析。',
  },
  case: {
    title: '案例展示',
    breadcrumb: [
      { label: '总览', path: '/overview' },
      { label: '案例展示', path: '/case' },
    ],
    intro: '产品案例专题筹备中；技术树与 Survey 已并入证据链模块。',
  },
  quality: {
    title: '数据质量与进展',
    breadcrumb: [
      { label: '总览', path: '/overview' },
      { label: '数据质量', path: '/quality' },
    ],
    intro: '链路完成度、字段覆盖与迭代进展。',
  },
}

/** /data 页 Tab：已有彩色可点，规划中灰色虚线置末；顺序与总览数据源规模序一致 */
export const DATA_TYPES = dataHubTabs()

export const CHAIN_TABS = [
  { id: 'overview', label: '证据链总览' },
  { id: 'tech_tree', label: '技术树' },
  { id: 'fund_paper', label: '基金→论文→技术', chainType: 'fund_paper_tech' },
  { id: 'patent', label: '专利→技术', chainType: 'patent_tech' },
  { id: 'contribution', label: '基金贡献度' },
]
