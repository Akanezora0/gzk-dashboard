// Scoped build-time copy adaptation for the embedded legacy pages only.
// Original low-altitude source, API values and the standalone site are unchanged.
const names = [
  ['基金资助论文条目', '国自然资助论文'],
  ['基金资助论文', '国自然资助论文'],
  ['期刊论文条目', '中文期刊文献'],
  ['软件著作权条目', '软件著作权'],
  ['产出条目（全类型）', '国自然项目成果'],
  ['NSFC 全库立项', '已收录基金项目'],
  ['NSFC 全库目录', '期刊与会议成果记录'],
  ['全量专利库', '既有专题专利资料'],
  ['专利（全量）', '原交付专利文献'],
  ['专利申请主体', '专利申请人'],
]
export function embeddedDisplayCopy() {
  return {
    name: 'gzk-embedded-display-copy',
    enforce: 'pre',
    transform(code, id) {
      const file = id.split('?')[0].replaceAll('\\', '/')
      if (!/\/(?:dashboard\/web|legacy)\/src\/constants\/(dataCatalog|dataHubProfiles|chainHubProfiles)\.js$/.test(file)) return null
      let copy = code
      for (const [from, to] of names) copy = copy.replaceAll(from, to)
      copy = copy.replaceAll("hint: '全量'", "hint: '原交付范围'")
      copy = copy.replaceAll('近五年低空经济相关专利增速高于全国均值；头部申请人集中在通信、制造与高校三类主体。', '按既有低空经济专利资料，观察申请主体和技术分布。')
      copy = copy.replaceAll('原始专利 ${PATENT_RAW_COUNT.toLocaleString()} 件', '原交付专利文献 ${PATENT_RAW_COUNT.toLocaleString()} 条')
      copy = copy.replaceAll('领域相关专利 ${LA_PATENT_COUNT.toLocaleString()} 件', '领域相关专利文献 ${LA_PATENT_COUNT.toLocaleString()} 条')
      copy = copy.replaceAll('论文资源分两层。大库：', '论文资源分为共享底座与专题文献池。共享底座：')
      copy = copy.replaceAll('篇（NSFC）、知网期刊', '篇（期刊与会议成果记录）、中文期刊文献')
      copy = copy.replaceAll("metric('journal_papers')).toLocaleString()} 篇", "metric('journal_papers')).toLocaleString()} 条")
      copy = copy.replaceAll('论文条目', '论文记录')
      return copy === code ? null : { code: copy, map: null }
    },
  }
}
