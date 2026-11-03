const BASE = ''

export async function apiGet(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) throw new Error(`API ${path}: ${res.status}`)
  return res.json()
}

export function fmtCount(n) {
  if (n == null) return '—'
  if (n >= 100000000) return `${(n / 100000000).toFixed(1)}亿+`
  if (n >= 10000) return `${(n / 10000).toFixed(1)}万+`
  return String(n)
}

export function statusColor(status) {
  if (status === 'verified' || status === 'completed' || status === 'available') return '#22c55e'
  if (status === 'candidate' || status === 'partial' || status === 'in_progress') return '#f59e0b'
  return '#ef4444'
}
