/** Compute the current low-altitude contribution response from its minimal projection. */
export function pythonRound(value, digits = 0) {
  // Round the exact binary64 value to a decimal grid, ties to even (Python round).
  if (!Number.isFinite(value) || value === 0) return value
  const negative = value < 0
  const buf = new ArrayBuffer(8)
  const view = new DataView(buf)
  view.setFloat64(0, Math.abs(value), false)
  const bits = view.getBigUint64(0, false)
  const exponent = Number((bits >> 52n) & 0x7ffn)
  let numerator = bits & ((1n << 52n) - 1n)
  if (exponent) numerator += 1n << 52n
  const power = exponent ? exponent - 1023 - 52 : -1074
  let denominator = 1n
  if (power >= 0) numerator <<= BigInt(power)
  else denominator <<= BigInt(-power)
  const scale = 10n ** BigInt(digits)
  numerator *= scale
  let quotient = numerator / denominator
  const twiceRemainder = 2n * (numerator % denominator)
  if (twiceRemainder > denominator || (twiceRemainder === denominator && quotient % 2n)) quotient += 1n
  const rounded = Number(quotient) / Number(scale)
  return negative ? -rounded : rounded
}

export function contribution(rows, metadata, query = {}) {
  const get = key => query instanceof URLSearchParams ? query.get(key) : query[key] ?? null
  const year = key => {
    const value = get(key)
    if (value === null) return null
    if (value === '' || !Number.isInteger(Number(value))) throw new TypeError(`${key} must be an integer`)
    return Number(value)
  }
  const filters = {tech_layer:get('tech_layer'), tech_tag_id:get('tech_tag_id'), year_start:year('year_start'), year_end:year('year_end')}
  const selected = rows.filter(row => {
    if (filters.tech_tag_id ? row.tech_tag_id !== filters.tech_tag_id : filters.tech_layer && row.tech_layer !== filters.tech_layer) return false
    if (filters.year_start && (row.year || 0) < filters.year_start) return false
    if (filters.year_end && (row.year || 9999) > filters.year_end) return false
    return true
  })
  const n = selected.length
  let funded = 0, highCite = 0, citations = 0, scores = 0
  const points = new Set(), layers = new Set(), byLayer = new Map()
  for (const row of selected) {
    funded += Number(row.has_funding_metadata)
    highCite += Number(row.citation_count >= 20)
    citations += row.citation_count
    scores += row.funding_score
    points.add(row.tech_tag_id)
    layers.add(row.tech_layer)
    const layer = row.tech_layer === undefined ? '未知' : row.tech_layer
    const bucket = byLayer.get(layer) || {papers:0, funded:0}
    bucket.papers += 1
    bucket.funded += Number(row.has_funding_metadata)
    byLayer.set(layer, bucket)
  }
  return {
    filters,
    coverage: {
      fund_supported_papers:funded,
      fund_supported_ratio:n ? pythonRound(funded / n, 4) : 0,
      total_papers:n,
      covered_tech_points:points.size,
      covered_tech_layers:layers.size,
      fund_patent_candidates:metadata.fund_patent_candidates,
    },
    impact: {
      avg_citation:n ? pythonRound(citations / n, 2) : 0,
      high_cite_ratio:n ? pythonRound(highCite / n, 4) : 0,
      avg_funding_score:n ? pythonRound(scores / n, 4) : 0,
    },
    diffusion:{...metadata.diffusion},
    by_layer:[...byLayer.keys()].sort().map(layer => ({tech_layer:layer, papers:byLayer.get(layer).papers, fund_ratio:pythonRound(byLayer.get(layer).funded / byLayer.get(layer).papers, 4)})),
  }
}
