export const EARLY_YEAR_BUCKET = '2016年之前'

// Used only by the AI domain page's statistical charts. Original records,
// date ranges, source totals, and the low-altitude application stay intact.
export function groupAiYears(years = []) {
  const totals = new Map()
  for (const row of years) {
    const count = Number(row.count)
    if (row.count == null || row.count === '' || !Number.isFinite(count)) {
      throw new TypeError('年份统计缺少有效计数')
    }
    const raw = row.year == null ? '' : String(row.year).trim()
    const numeric = /^\d{4}$/.test(raw) ? Number(raw) : null
    const year = raw === EARLY_YEAR_BUCKET || (numeric != null && numeric < 2016)
      ? EARLY_YEAR_BUCKET : numeric ?? (raw || '年份未知')
    totals.set(year, (totals.get(year) || 0) + count)
  }
  const entries = [...totals].map(([year, count]) => ({ year, count }))
  const order = year => year === EARLY_YEAR_BUCKET ? -Infinity : typeof year === 'number' ? year : Infinity
  return entries.sort((a, b) => order(a.year) - order(b.year))
}

export function aiYearLabel(year) {
  return /^\d{4}$/.test(String(year)) ? `${year}年` : String(year ?? '')
}
