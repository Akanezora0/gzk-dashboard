/** 与规范库 serving/authoritative_metrics.json 同步 — 前端 fallback 与溯源键名 */
import raw from '@serving/authoritative_metrics.json'

export const AUTHORITATIVE_METRICS = raw

export function metric(key, fallback = 0) {
  const m = raw.metrics?.[key] ?? raw.fund_type_breakdown?.[key]
  return m?.value ?? fallback
}

export function metricMeta(key) {
  return raw.metrics?.[key] ?? raw.fund_type_breakdown?.[key] ?? null
}

/** 页面展示用：低空专利主口径（同事规则筛选） */
export const LA_PATENT_COUNT = metric('patent_rule_filtered')
export const PATENT_RAW_COUNT = metric('patent_raw')
export const TECH_TAG_COUNT = metric('tech_tags')
export const SKILLS_B_PAPERS = metric('skills_b_line_papers')
export const FUND_PAPER_LINKS = metric('sqlite_fact_fund_paper_link')
export const PATENT_TECH_LINKS = metric('sqlite_fact_patent_tech_link')
export const FUND_PROJECTS_SQLITE = metric('sqlite_dim_fund_project')

/** 案例侧大疆产品名录（case/data/fact_product_series_generation_product.csv） */
export const DJI_CASE_PRODUCTS = 91

/** 总览页不展示；保留常量供内部文档引用 */
export const DATA_FOOTNOTE = ''

/** 总览页不展示口径脚注 */
export const OVERVIEW_DATA_NOTE = ''

/**
 * 总览统一数据源：一项对应一类独立数据资源（不含子类拆分、关联表）
 */
export const OVERVIEW_DATA_SOURCE_DEFS = [
  // 目录型：文档称「资助论文目录」，摘要多为空，展示保留「条目」
  { type: 'nsfc_papers', label: '基金资助论文条目', hint: '期刊与会议', category: '论文', accent: 'red', route: '/data?tab=paper' },
  // 以下为完整业务数据（论文/项目/专利/政策等），不加「条目」
  { type: 'journal_papers', label: '期刊论文条目', hint: '知网文献库', category: '论文', accent: 'dark', route: '/data?tab=paper' },
  { type: 'soft_copyright', label: '软件著作权条目', hint: '登记信息', category: '软著', accent: 'green', route: '/data?tab=patent' },
  { type: 'fund_total', label: '基金项目', hint: '立项项目', category: '基金', accent: 'amber', route: '/data?tab=fund', metricKey: 'nsfc_fund_projects' },
  { type: 'patent_raw', label: '专利', hint: '全量专利库', category: '专利', route: '/data?tab=patent' },
  { type: 'la_news', label: '产业新闻', hint: '产业动态', category: '新闻', route: '/data?tab=news' },
  { type: 'la_patent', label: '规则筛选专利', hint: '领域相关', category: '专利', route: '/data?tab=patent', metricKey: 'patent_rule_filtered' },
  { type: 'la_applicant', label: '专利申请主体', hint: '企业/机构', category: '主体', route: '/data?tab=patent' },
  { type: 'la_policy', label: '政策文献', hint: '含政策全文', category: '政策', route: '/data?tab=policy' },
  { type: 'la_product', label: '载体产品', hint: '低空载体产品', category: '产品', route: '/data?tab=product' },
  { type: 'la_research', label: '专题科研项目', hint: '专题项目', category: '项目', route: '/data?tab=fund' },
  { type: 'industry_report', label: '行业报告', hint: '报告文献', category: '政策', route: '/data?tab=report', metricKey: 'industry_report_pdf' },
  { type: 'la_org', label: '科研单位', hint: '机构名录', category: '主体', route: '/data?tab=patent' },
  { type: 'tech_dict', label: '技术词典', hint: '技术点词表', category: '词典', route: '/chain?tab=tech_tree', metricKey: 'tech_tags' },
]

/** @deprecated 使用 OVERVIEW_DATA_SOURCE_DEFS */
export const OVERVIEW_CSV_SOURCE_DEFS = OVERVIEW_DATA_SOURCE_DEFS

/** 柱状图 / 饼图配色（按规模序循环） */
export const OVERVIEW_BAR_COLORS = [
  '#ae0d28', '#c41e3a', '#9b0000', '#2d6a4f', '#b45309',
  '#78716c', '#a8a29e', '#6366f1', '#0d9488', '#7c3aed',
  '#ca8a04', '#0369a1', '#be123c', '#4d7c0f', '#9333ea',
]

function countForOverviewType(type, catalog, metricKey) {
  const flat = (catalog || []).flatMap(g => g.items || [])
  const item = flat.find(i => i.type === type)
  if (item?.count != null) return item.count
  const key = metricKey || type
  return metric(key)
}

/** 总览统一数据源列表（按规模降序，含图表配色） */
export function overviewDataSources(catalog) {
  return sortByCountDesc(
    OVERVIEW_DATA_SOURCE_DEFS.map(def => ({
      type: def.type,
      label: def.label,
      hint: def.hint,
      category: def.category,
      accent: def.accent,
      route: def.route,
      count: countForOverviewType(def.type, catalog, def.metricKey),
    })).filter(i => i.count > 0)
  ).map((item, i) => ({
    ...item,
    color: OVERVIEW_BAR_COLORS[i % OVERVIEW_BAR_COLORS.length],
  }))
}

/** 总览 Hero 四卡：规模 Top 4，与图表同源 */
export function overviewPrimaryCards(catalog) {
  return overviewDataSources(catalog).slice(0, 4)
}

/** @deprecated 使用 overviewDataSources */
export function overviewCsvSources(catalog) {
  return overviewDataSources(catalog)
}

/** @deprecated 使用 overviewDataSources */
export function overviewAllSources(catalog) {
  return overviewDataSources(catalog)
}

export function overviewVolumeBarItems(catalog) {
  return overviewDataSources(catalog).map(({ label, count, color }) => ({ label, count, color }))
}

/** 饼图分段：与柱图同源，取规模 Top 8 */
export function overviewCompositionSegments(catalog) {
  return overviewDataSources(catalog).slice(0, 8).map(({ label, count, color }) => ({
    label, count, color,
  }))
}

/** 图表分段：按 count 降序 */
export function sortByCountDesc(items) {
  return [...(items || [])].sort((a, b) => (b.count || 0) - (a.count || 0))
}

/** 非独立数据源：关联表、同文件拆分子类等（/data 详情页可展示，总览不重复计） */
export const CATALOG_LINK_TYPES = new Set([
  'product_tech_links',
  'nsfc_paper_links',
  'nsfc_funded_outputs',
  'skills_union_papers',
  'skills_b_line_papers',
  'skills_a_line_papers',
  'fund_general', 'fund_youth', 'fund_region', 'fund_special',
  'fund_key', 'fund_major', 'fund_joint', 'fund_math',
])

export const DATA_ARCHIVE = {
  source_files: metric('archive_business_files'),
  volume_gb: metric('archive_volume_gb'),
  volume_mb: 13981,
  structured_files: 286,
  unstructured_files: 529,
  source_categories: 26,
}

/** /data 页 Tab 元数据（展示顺序见 dataHubTabs） */
const DATA_HUB_TAB_DEFS = [
  { type: 'paper', label: '论文', available: true, countKey: 'nsfc_papers' },
  { type: 'patent', label: '专利', available: true, countKey: 'patent_rule_filtered' },
  { type: 'fund', label: '基金', available: true, countKey: 'nsfc_fund_projects' },
  { type: 'product', label: '产品', available: true, countKey: 'la_product' },
  { type: 'enterprise', label: '企业', available: false, planned: true },
  { type: 'news', label: '新闻', available: true, countKey: 'la_news' },
  { type: 'report', label: '行研报告', available: true, countKey: 'industry_report_pdf' },
  { type: 'policy', label: '政策', available: true, countKey: 'la_policy' },
]

function tabFromOverviewRoute(route) {
  const m = (route || '').match(/tab=(\w+)/)
  return m?.[1] || null
}

/** /data Tab 顺序：按总览数据源规模序首次出现，规划中置末 */
export function dataHubTabs(catalog) {
  const defMap = Object.fromEntries(DATA_HUB_TAB_DEFS.map(d => [d.type, d]))
  const ordered = []
  const seen = new Set()
  for (const src of overviewDataSources(catalog)) {
    const tab = tabFromOverviewRoute(src.route)
    if (tab && defMap[tab] && !seen.has(tab)) {
      seen.add(tab)
      ordered.push(tab)
    }
  }
  for (const def of DATA_HUB_TAB_DEFS) {
    if (def.planned && !seen.has(def.type)) ordered.push(def.type)
  }
  return ordered.map(type => {
    const def = defMap[type]
    return {
      type: def.type,
      label: def.label,
      available: def.available,
      ...(def.planned ? { planned: true } : {}),
      ...(def.countKey ? { count: metric(def.countKey) } : {}),
    }
  })
}

export const DATA_TAB_TYPES = dataHubTabs()

function fundItems() {
  const fb = raw.fund_type_breakdown || {}
  return [
    { type: 'fund_total', label: '基金项目', count: metric('nsfc_fund_projects'), route: '/data?tab=fund' },
    { type: 'fund_general', label: '面上项目', count: fb.fund_general?.value, route: '/data?tab=fund' },
    { type: 'fund_youth', label: '青年科学基金', count: fb.fund_youth?.value, route: '/data?tab=fund' },
    { type: 'fund_region', label: '地区科学基金', count: fb.fund_region?.value, route: '/data?tab=fund' },
    { type: 'fund_special', label: '专项基金项目', count: fb.fund_special?.value, route: '/data?tab=fund' },
    { type: 'fund_key', label: '重点项目', count: fb.fund_key?.value, route: '/data?tab=fund' },
    { type: 'fund_major', label: '重大研究计划', count: fb.fund_major?.value, route: '/data?tab=fund' },
    { type: 'fund_joint', label: '联合基金项目', count: fb.fund_joint?.value, route: '/data?tab=fund' },
    { type: 'fund_math', label: '数学天元基金', count: fb.fund_math?.value, route: '/data?tab=fund' },
    { type: 'nsfc_papers', label: '基金资助论文条目（期刊+会议）', count: metric('nsfc_papers'), route: '/data?tab=paper' },
    { type: 'nsfc_funded_outputs', label: '基金资助产出条目（全类型）', count: metric('nsfc_funded_outputs'), route: '/data?tab=paper' },
    { type: 'journal_papers', label: '期刊论文条目（知网文献库）', count: metric('journal_papers'), route: '/data?tab=paper' },
  ]
}

export const DEFAULT_DATA_CATALOG = [
  {
    group: '国家自然科学基金',
    group_id: 'nsfc',
    items: fundItems(),
  },
  {
    group: '低空经济专题库',
    group_id: 'lowalt',
    items: [
      { type: 'patent_raw', label: '专利（全量）', count: PATENT_RAW_COUNT, route: '/data?tab=patent' },
      { type: 'la_patent', label: '低空专利（规则筛选）', count: LA_PATENT_COUNT, route: '/data?tab=patent' },
      { type: 'la_applicant', label: '专利申请主体', count: metric('la_applicant'), route: '/data?tab=patent' },
      { type: 'la_product', label: '低空载体产品', count: metric('la_product'), route: '/data?tab=product' },
      { type: 'product_tech_links', label: '产品—技术点关联', count: metric('product_tech_links'), route: '/case' },
      { type: 'la_research', label: '专题科研项目', count: metric('la_research'), route: '/data?tab=fund' },
      { type: 'la_org', label: '科研单位', count: metric('la_org'), route: '/data?tab=patent' },
      { type: 'soft_copyright', label: '软件著作权条目', count: metric('soft_copyright'), route: '/data?tab=patent' },
      { type: 'la_policy', label: '政策文献', count: metric('la_policy'), route: '/data?tab=policy' },
      { type: 'industry_report', label: '行业报告 PDF', count: metric('industry_report_pdf'), route: '/data?tab=report' },
      { type: 'la_news', label: '产业新闻', count: metric('la_news'), route: '/data?tab=news' },
      { type: 'tech_dict', label: '技术词典', count: TECH_TAG_COUNT, route: '/chain?tab=tech_tree' },
    ],
  },
]

export function totalCatalogItems(catalog) {
  return (catalog || []).reduce((s, g) => s + (g.items?.length || 0), 0)
}

export function heroMetrics(catalog) {
  return overviewPrimaryCards(catalog).map(i => ({
    label: i.label,
    count: i.count,
    route: i.route || '/data',
  }))
}

export function tabCountFor(type, catalog, dataCards) {
  const tab = DATA_TAB_TYPES.find(t => t.type === type)
  if (tab?.count) return tab.count
  const card = dataCards?.find(c => c.type === type)
  if (card?.count) return card.count
  const flat = (catalog || []).flatMap(g => g.items || [])
  const map = {
    patent: 'la_patent',
    paper: 'nsfc_papers',
    fund: 'fund_total',
    product: 'la_product',
    enterprise: 'la_applicant',
    news: 'la_news',
    report: 'industry_report',
    policy: 'la_policy',
  }
  const item = flat.find(i => i.type === map[type])
  return item?.count
}

/** @deprecated 使用 DATA_ARCHIVE */
export const DATA_ASSET_SUMMARY = { ...DATA_ARCHIVE, catalog_groups: 3 }

export const DEFAULT_PERCEPTION = []
