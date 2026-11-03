// Keeps the original low-altitude API contract on the LLM server's origin.
const inFlight = new Map()
export function apiGet(path) {
  if (!path.startsWith('/api/')) return Promise.reject(new Error('未知低空数据路径'))
  if (inFlight.has(path)) return inFlight.get(path)
  // The old tree's click handler and route watcher can ask for the same detail
  // together. Share only pending requests; completed results are never cached.
  const request = (async () => {
    const res = await fetch('/api/low-altitude/' + path.slice('/api/'.length))
    if (!res.ok) throw new Error(`低空数据读取失败：${res.status}`)
    const payload = await res.json()
    // Normalize catalog labels only; never rewrite titles, counts or source evidence.
    if (path === '/api/overview' && Array.isArray(payload.data_catalog)) {
      const labels = {nsfc_papers:'国自然资助论文', journal_papers:'中文期刊文献', nsfc_funded_outputs:'国自然项目成果', soft_copyright:'软件著作权', fund_total:'国自然基金项目', patent_raw:'原交付专利文献', la_applicant:'专利申请人'}
      payload.data_catalog = payload.data_catalog.map(group => ({...group, items:(group.items || []).map(item => ({...item, label:labels[item.type] || item.label}))}))
    }
    return payload
  })().finally(() => inFlight.delete(path))
  inFlight.set(path, request)
  return request
}

export function fmtCount(n) {
  if (n == null) return '—'
  if (n >= 100000000) return `${(n / 100000000).toFixed(1)}亿`
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万`
  return String(n)
}

export function statusColor(status) {
  if (status === 'verified' || status === 'completed' || status === 'available') return '#22c55e'
  if (status === 'candidate' || status === 'partial' || status === 'in_progress') return '#f59e0b'
  return '#ef4444'
}
