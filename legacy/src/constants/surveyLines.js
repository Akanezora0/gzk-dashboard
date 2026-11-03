/** Survey / 文献管线对外展示名称（API 仍用 A/B） */

export const SURVEY_LINE_SKILLS = {
  api: 'B',
  label: 'Skills',
  short: 'Skills 文献',
  pool: 'Skills 文献池',
}

export const SURVEY_LINE_OPENSCHOLAR = {
  api: 'A',
  label: 'OpenScholar',
  short: 'OpenScholar 文献',
  pool: 'OpenScholar 文献池',
}

export const SURVEY_LINES = [SURVEY_LINE_SKILLS, SURVEY_LINE_OPENSCHOLAR]

export function surveyLineLabel(apiValue) {
  const v = String(apiValue || 'B').toUpperCase()
  return v === 'A' ? SURVEY_LINE_OPENSCHOLAR.label : SURVEY_LINE_SKILLS.label
}

export function surveyLineShort(apiValue) {
  const v = String(apiValue || 'B').toUpperCase()
  return v === 'A' ? SURVEY_LINE_OPENSCHOLAR.short : SURVEY_LINE_SKILLS.short
}
