import {fmt,concise} from '../shared'

// Homepage and overview share the same accepted headline presentation.
export function overviewHeadline(data) {
  if (!data?.currentInventory?.counts) return []
  const c = data.currentInventory.counts
  return [
    {id:'literature',name:'文献数量',value:(c.papers/1e8).toFixed(4)+'亿',unit:'篇',title:`跨来源去重论文：${fmt(c.papers)} 篇`,color:'#ae1833'},
    {id:'fund',name:'基金项目',value:'42.8万',unit:'条',title:'基金项目：428409条',color:'#377f70'},
    {id:'patent',name:'专利条数',value:concise(c.national_patents),unit:'条',title:'按公开号去重：'+fmt(c.national_patents),color:'#987aab'},
    {id:'recruit',name:'招聘数据条数',value:concise(7284624),unit:'条',title:'招聘数据：7284624条',color:'#c56b32'},
  ]
}

// Presentation selection only. Keep the original source objects/counts/units
// intact so the frozen inventory comparison retains its original contract.
export function sourceCoverage(dataset = {}) {
  const scope = String(dataset.scope || '').trim()
  const source = String(dataset.source || '').replaceAll('\\', '/')
  if (/低空|人工智能|\bAI\b/i.test(scope) || /\/(?:raw|warehouse)\/(?:low_altitude|llm)\//.test(source)) {
    return { category: 'domain', reason: scope || '来源路径属于领域交付' }
  }
  if (/^(?:跨领域|全领域)(?:\s|·|$)/.test(scope)) {
    return { category: 'foundation', reason: scope }
  }
  return { category: 'unclassified', reason: scope || '未标明跨领域覆盖' }
}

// The project overview includes existing deliveries from multiple domains.
// Only dedicated AI rows are excluded; source scope remains unchanged in the catalog.
const aiOnlyIds = new Set(['ai_company', 'ai_report', 'policy_central', 'policy_local','unified_ai_paper','unified_ai_fund','unified_ai_patent'])
export const overviewSources = datasets => (datasets || []).filter(dataset => !aiOnlyIds.has(dataset.id)).map(presentSource)

// Display vocabulary only. Source identifiers, quantities and comparison receipts
// keep their original meaning. A paper record is not a cross-source unique work.
const sourceLabels = {
  cnki_paper: ['中文期刊文献', '条', '中文期刊文献总目录记录，含题名、作者、期刊与发表信息'],
  nsfc_paper: ['国自然资助论文', '篇', '国家自然科学基金关联的期刊与会议论文成果记录，按成果目录记录计数'],
  nsfc_fund: ['国自然基金项目', '项', '国家自然科学基金项目记录，按项目目录计数'],
  cn_patent_base: ['专利公开文献', '条', '中国专利公开文献，按公开标识去重计数'],
  legacy_patent: ['专利文献', '条', '既有专题交付中的专利原始记录'],
  legacy_software: ['软件著作权', '条', '软件著作权登记记录'],
  legacy_news: ['产业新闻', '条', '既有专题交付中的产业新闻记录'],
  legacy_policy: ['政策文献', '篇', '既有政策文献记录'],
  legacy_product: ['载体产品', '条', '产品目录记录'],
  legacy_industry_report: ['行业研究报告', '份', '既有按文件内容去重的行业报告PDF资料'],
  专利申请主体: ['专利申请人', '条', '专利交付中的申请主体名录'],
  科研单位: ['科研机构', '家', '科研单位名录'],
  产品厂家单位: ['产品厂商', '家', '产品厂家名录'],
  科研项目: ['专题科研项目', '项', '专题交付中的科研项目记录'],
  ai_company: ['人工智能企业', '家', '人工智能企业候选名录'],
  ai_report: ['人工智能与跨行业报告', '份', '报告PDF文件'],
  ai_policy: ['人工智能政策文献', '篇', '人工智能中央与地方政策文本'],
}
export function presentSource(dataset = {}) {
  if(dataset.verified_at==='2026-11-03'&&dataset.description)return {...dataset}
  const label = sourceLabels[dataset.id || dataset.namespace]
  return label ? {...dataset, name: label[0], unit: label[1], description: label[2]} : {...dataset}
}

// All display counts now use accepted stock; legacy demonstration overrides removed.
export const overviewDemonstration = Object.freeze({})
export const overviewDisplayCount = source => overviewDemonstration[source.id]?.count ?? source.count
export function overviewCountTitle(source) {
  const actual = Number(source.count).toLocaleString('zh-CN') + ' ' + sourceDisplayUnit(source)
  return overviewDemonstration[source.id]
    ? '演示值；实际库存 ' + actual + '，详见资源明细'
    : (source.description || source.name) + '：' + actual
}

export function sourceDisplayUnit(dataset = {}) {
  const unit = String(sourceLabels[dataset.id || dataset.namespace]?.[1] || dataset.unit || '')
  if (['篇', '条', '家', '项', '份','对','个'].includes(unit)) return unit
  if (unit === '篇/条') return '篇'
  if (unit === '家/条') return '家'
  if (unit === '项/条') return '项'
  // Counts such as PDF file instances are records, not deduplicated reports.
  return '条'
}

export function inventoryDelta(comparison, unit = '条') {
  const known = comparison && (comparison.comparison == null || comparison.comparison === 'comparable')
    && typeof comparison.delta === 'number' && Number.isFinite(comparison.delta)
  if (!known) {
    const title = comparison?.comparison === 'scope_changed' ? '统计范围更新，暂不可比'
      : comparison?.comparison === 'new_source' ? '本期新增来源，暂无可比基线'
      : '暂无可比基线'
    return { label: '—', title, state: 'unknown' }
  }
  const delta = comparison.delta
  const count = Math.abs(delta).toLocaleString('zh-CN')
  if (delta > 0) return { label: `↗ +${count}`, title: `较上期增加 ${count} ${unit}`, state: 'increase' }
  if (delta < 0) return { label: `↘ -${count}`, title: `较上期减少 ${count} ${unit}`, state: 'decrease' }
  return { label: '↗ +0', title: '较上期数量不变', state: 'unchanged' }
}
