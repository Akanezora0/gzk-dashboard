// The API owns batch coverage classification. A shared directory or a broad
// looking title alone is not evidence that a batch covers all research fields.
export function catalogCoverage(event = {}) {
  return ['foundation', 'domain', 'unknown'].includes(event.coverage_scope)
    ? event.coverage_scope : 'unknown'
}

export function catalogScopeCounts(events = []) {
  return {
    foundation: events.filter(event => catalogCoverage(event) === 'foundation').length,
    unknown: events.filter(event => catalogCoverage(event) === 'unknown').length,
  }
}
