<script setup>
import { computed, nextTick, ref, watch } from 'vue'

const props = defineProps({ dataset: { type: Object, default: () => ({}) } })
const graph = computed(() => props.dataset?.graph || {})
const records = computed(() => Array.isArray(props.dataset?.continuity) ? props.dataset.continuity : [])
const focus = computed(() => props.dataset?.focus || {})
const detail = computed(() => props.dataset?.caseDetail || {})
const number = value => Number(value || 0).toLocaleString('zh-CN')
const yearOf = value => Number(String(value || '').slice(0, 4)) || null
const projectId = p => p.project_id || `NSFC:${p.grant_no}`
const yearList = Array.from({ length: 9 }, (_, i) => 2017 + i)
const org = ref('兰州理工大学')
const personId = ref('')
const search = ref('')
const picked = ref(null)
const selectedPaper = ref(null)
const evidenceElement = ref(null)
const trajectoryElement = ref(null)
const openCasePaper = ref('')
const allProjects = computed(() => graph.value.project_nodes || [])
const papersById = computed(() => new Map((graph.value.paper_nodes || []).map(p => [p.paper_id, p])))
const allPaperLinks = computed(() => graph.value.project_paper_edges || [])
const linksByProject = computed(() => {
  const map = new Map()
  for (const edge of allPaperLinks.value) {
    if (!map.has(edge.project_id)) map.set(edge.project_id, [])
    map.get(edge.project_id).push(edge)
  }
  return map
})
const projectIdentity = computed(() => {
  const map = new Map()
  for (const r of records.value) {
    // Only join projects using the supplied verified person identity, never a name match.
    if (!r.person_id) continue
    for (const key of ['earlier_project_id', 'later_project_id']) map.set(r[key], r.person_id)
  }
  return map
})
const institutions = computed(() => {
  const preferred = ['清华大学', '北京邮电大学', '南京工业大学', '兰州理工大学']
  return [...new Set(allProjects.value.map(p => p.institution).filter(Boolean))]
    .sort((a, b) => preferred.indexOf(a) - preferred.indexOf(b))
    .map(name => ({ name, count: allProjects.value.filter(p => p.institution === name).length }))
})
const institutionProjects = computed(() => allProjects.value.filter(p => p.institution === org.value))
const people = computed(() => {
  const groups = new Map()
  for (const p of institutionProjects.value) {
    const verified = projectIdentity.value.get(projectId(p))
    const id = verified || projectId(p)
    if (!groups.has(id)) groups.set(id, { id, name: p.principal_investigator || '负责人待补充', verified: Boolean(verified), projects: [] })
    groups.get(id).projects.push(p)
  }
  return [...groups.values()].map(p => ({ ...p, projects: p.projects.sort((a, b) => Number(a.approval_year) - Number(b.approval_year)) }))
    .sort((a, b) => b.projects.length - a.projects.length || a.name.localeCompare(b.name, 'zh-CN'))
})
const filteredPeople = computed(() => {
  const query = search.value.trim().toLowerCase()
  return people.value.filter(p => !query || `${p.name} ${p.projects.map(x => x.title).join(' ')}`.toLowerCase().includes(query))
})
const person = computed(() => people.value.find(p => p.id === personId.value) || null)
const selectedProjects = computed(() => person.value?.projects || [])
const selectedContinuities = computed(() => {
  const ids = new Set(selectedProjects.value.map(projectId))
  return records.value.filter(r => ids.has(r.earlier_project_id) && ids.has(r.later_project_id))
})
const personPaperCount = computed(() => new Set(selectedProjects.value.flatMap(p => (linksByProject.value.get(projectId(p)) || []).map(e => e.paper_id))).size)
const institutionCoverage = computed(() => (graph.value.coverage_by_institution || []).find(r => r.canonical_name === org.value))
watch(institutions, value => { if (!value.some(i => i.name === org.value)) org.value = value[0]?.name || '' }, { immediate: true })
watch(people, value => {
  if (!value.some(p => p.id === personId.value)) personId.value = value.find(p => ['李晓旭', '鄂海红', '缪小冬', '黄民烈'].includes(p.name))?.id || value[0]?.id || ''
}, { immediate: true })
watch([personId, () => props.dataset], () => { picked.value = null; selectedPaper.value = null })
function changeInstitution(name) { org.value = name; search.value = ''; picked.value = null; selectedPaper.value = null }
function choosePerson(id) { personId.value = id; picked.value = null; selectedPaper.value = null }

const annual = computed(() => {
  const supplied = focus.value.year_summary || []
  if (supplied.length) return supplied.filter(x => x.year >= 2017 && x.year <= 2021).sort((a, b) => a.year - b.year)
  const groups = new Map()
  for (const r of focus.value.org_years || []) {
    if (!groups.has(r.approval_year)) groups.set(r.approval_year, new Set())
    groups.get(r.approval_year).add(r.organization_id)
  }
  return [...groups].map(([year, set]) => ({ year: Number(year), total: set.size })).sort((a, b) => a.year - b.year)
})
const firstAnnual = computed(() => annual.value[0])
const lastAnnual = computed(() => annual.value.at(-1))
const growth = computed(() => firstAnnual.value?.total ? ((lastAnnual.value.total / firstAnnual.value.total - 1) * 100).toFixed(1) : null)
const totalScopeProjects = computed(() => (focus.value.org_years || []).reduce((sum, r) => sum + Number(r.projects || 0), 0))
const cohorts = computed(() => Object.values(focus.value.cohort_institutions || {}))
const youthContinuities = computed(() => records.value.filter(r => r.earlier_project_type?.includes('青年')))
const youthToGeneral = computed(() => youthContinuities.value.filter(r => r.later_project_type === '面上项目').length)
const baselineInstitution = computed(() => props.dataset.institutionSummary?.find(r => r.present_2017))
const baselineFundingShare = computed(() => {
  const rows=props.dataset.institutionSummary || []
  const sum=rows.reduce((s,r)=>s+Number(r.amount_yi),0)
  return sum ? (100*Number(baselineInstitution.value?.amount_yi||0)/sum).toFixed(1) : ''
})
const cohortCounts = computed(() => {
  const years = cohorts.value.map(o => Object.entries(o.years || {}).filter(([y, count]) => Number(y) >= 2022 && Number(y) <= 2025 && Number(count) > 0).length)
  return [1, 2, 4].map(threshold => ({ threshold, count: years.filter(n => n >= threshold).length, label: threshold === 4 ? '四年均有论文' : `至少${threshold === 1 ? '一' : '两'}年有论文` }))
})
const annualX = index => 48 + index * (520 / Math.max(1, annual.value.length - 1))
const annualY = value => 135 - (Number(value) / Math.max(...annual.value.map(x => Number(x.total)), 1)) * 70
const annualPath = computed(() => annual.value.map((r, i) => `${i ? 'L' : 'M'} ${annualX(i)} ${annualY(r.total)}`).join(' '))
const shortType = t => String(t || '基金项目').replace('青年科学基金项目（C类）', '青年项目').replace('青年科学基金项目', '青年项目').replace('面上项目', '面上项目')
const titleLines = title => {
  const chars = [...String(title || '')]
  return [chars.slice(0, 12).join(''), chars.slice(12, 24).join('') + (chars.length > 24 ? '…' : '')].filter(Boolean)
}
const sx = year => 236 + (Number(year) - 2017) * 84
const rowY = index => 94 + index * 150
const timelineHeight = computed(() => 80 + selectedProjects.value.length * 150)
function startX(p) { return sx(Math.max(2017, Math.min(2025.9, yearOf(p.start_date) || Number(p.approval_year)))) }
function endX(p) { return sx(Math.max(2017, Math.min(2026, (yearOf(p.end_date) || Number(p.approval_year)) + 1))) - 12 }
function paperGroups(p) {
  const groups = new Map()
  for (const edge of linksByProject.value.get(projectId(p)) || []) {
    const paper = papersById.value.get(edge.paper_id)
    const year = Number(paper?.publication_year || edge.paper_publication_year)
    if (!paper || year < 2017 || year > 2025) continue
    if (!groups.has(year)) groups.set(year, new Map())
    groups.get(year).set(edge.paper_id, { ...paper, bases: edge.bases || [], evidence_count: edge.evidence_count })
  }
  return [...groups].sort((a, b) => a[0] - b[0]).map(([year, entries]) => ({ year, papers: [...entries.values()] }))
}
const activeProject = computed(() => picked.value?.project || selectedProjects.value[0] || null)
const pickedPapers = computed(() => picked.value?.papers || [])
const activePaper = computed(() => selectedPaper.value || pickedPapers.value[0] || null)
const evidenceBasis = values => [...new Set(values || [])].map(v => ({ explicit_nsfc_award: '论文明确标注基金批准号', fund_registered_outcome: '基金项目成果登记', nsfc_history_registered: '基金历史成果登记', nsfc_recent_registered: '基金近期成果登记' })[v] || '项目与论文的来源关联')
function safeLink(value) { try { const u = new URL(value); return ['http:', 'https:'].includes(u.protocol) ? u.href : '' } catch { return '' } }
function paperLink(p) { return safeLink(p?.primary_url || p?.doi_url || (p?.doi ? `https://doi.org/${p.doi}` : '')) }
function pickProject(p) { picked.value = { kind: 'project', project: p }; selectedPaper.value = null }
function pickYear(project, group) { picked.value = { kind: 'papers', project, ...group }; selectedPaper.value = null }
async function viewEvidence() { await nextTick(); evidenceElement.value?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }) }
const caseProjects = computed(() => (detail.value.projects || []).slice().sort((a, b) => Number(a.approval_year) - Number(b.approval_year)))
const casePapers = p => (detail.value.papers || []).filter(paper => paper.project_id === projectId(p)).sort((a, b) => Number(a.publication_year) - Number(b.publication_year))
async function viewCaseTimeline() {
  changeInstitution('兰州理工大学')
  await nextTick()
  personId.value = people.value.find(p => p.name === '李晓旭')?.id || personId.value
  await nextTick()
  trajectoryElement.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}
</script>

<template>
  <div class="rc">
    <header class="rc-intro">
      <div><span class="rc-eyebrow">基金研究接续</span><h2>支持覆盖更多机构，研究沿项目持续展开</h2><p>从机构参与到负责人接续，把资助时间与成果时间放在同一条研究轨迹上。</p></div>
      <div v-if="records.length" class="rc-proof-count"><strong>{{ number(records.length) }}</strong><span>条双端官方身份<br>核验的项目接续</span></div>
    </header>

    <div class="rc-overview">
      <section class="rc-surface rc-expansion">
        <div class="rc-section-top"><div><span class="rc-kicker">01 / 机构扩面</span><h3>年度承担机构增加 <em v-if="growth !== null">{{ growth }}%</em></h3></div><span class="rc-period">2017—2021 年批准项目</span></div>
        <div v-if="annual.length" class="rc-overflow">
          <svg class="rc-growth-svg" viewBox="0 0 620 182" role="img" :aria-label="`年度承担机构从${firstAnnual.total}家增加到${lastAnnual.total}家`">
            <path d="M 48 142 H 568" stroke="#e7e3df" fill="none"/>
            <path :d="annualPath" stroke="#ae0d28" stroke-width="3" stroke-linejoin="round" fill="none"/>
            <g v-for="(a, i) in annual" :key="a.year">
              <line :x1="annualX(i)" :x2="annualX(i)" :y1="annualY(a.total)" y2="142" stroke="#e8e4e0"/>
              <circle :cx="annualX(i)" :cy="annualY(a.total)" r="5" fill="#ae0d28" stroke="white" stroke-width="2"/>
              <text :x="annualX(i)" :y="annualY(a.total) - 19" class="rc-svg-value" text-anchor="middle">{{ number(a.total) }}<tspan font-size="11" dx="3">家</tspan></text>
              <text :x="annualX(i)" y="166" class="rc-svg-year" text-anchor="middle">{{ a.year }}</text>
            </g>
          </svg>
        </div>
        <p v-else class="rc-empty">机构年度数据正在准备。</p>
        <p class="rc-caption">同一 AI 项目样本 · 五年共 {{ number(totalScopeProjects) }} 个批准项目；按年度去重统计承担机构。</p>
      </section>
      <section class="rc-surface rc-persistence">
        <div class="rc-section-top"><div><span class="rc-kicker">02 / 成果延续</span><h3>首次观察后，成果持续出现</h3></div></div>
        <p class="rc-small-lead">2018—2021 年首次观察到的 <b>{{ number(cohorts.length) }} 家</b>机构，追踪其项目在 2022—2025 年的论文。</p>
        <div v-for="item in cohortCounts" :key="item.threshold" class="rc-cohort-line">
          <span>{{ item.label }}</span><div class="rc-cohort-track"><i :style="{width: `${cohorts.length ? item.count / cohorts.length * 100 : 0}%`}"/></div><strong>{{ number(item.count) }}<small> 家</small></strong>
        </div>
        <p class="rc-caption">论文观察窗口：2022—2025。按机构去重；三个持续性条件逐级包含。</p>
      </section>
    </div>

    <div class="rc-key-findings">
      <article v-if="baselineInstitution"><span>机构参与扩展，既有力量仍是主力</span><strong>{{baselineFundingShare}}<small>%</small></strong><p>2017 年已有项目的机构，承接了 2021 年八成以上的批准经费，覆盖 {{number(baselineInstitution.projects)}} 个项目。</p></article>
      <article><span>青年项目接续以面上项目为主</span><strong>{{(100*youthToGeneral/Math.max(1,youthContinuities.length)).toFixed(1)}}<small>%</small></strong><p>在 {{youthContinuities.length}} 条青年项目起点的已核验接续中，{{youthToGeneral}} 条连接到面上项目，呈现从早期探索到持续研究的路径。</p></article>
      <article><span>扩面之后，关注研究能否延续</span><strong>{{cohortCounts[1]?.count||0}}<small>家</small></strong><p>{{cohorts.length}} 家首次观察机构中，有 {{cohortCounts[1]?.count||0}} 家在后续共同观察期内至少两年形成关联论文。</p></article>
    </div>

    <section ref="trajectoryElement" class="rc-surface rc-trajectories">
      <div class="rc-section-top"><div><span class="rc-kicker">03 / 沿负责人展开</span><h3>同一条研究主干，接上项目与成果</h3></div><span class="rc-period">立项 2017—2021 · 论文 2017—2025</span></div>
      <div class="rc-institution-tabs" aria-label="选择机构">
        <button v-for="i in institutions" :key="i.name" type="button" :class="{active:org===i.name}" :aria-pressed="org===i.name" @click="changeInstitution(i.name)">{{ i.name }}<span>{{ number(i.count) }} 项</span></button>
      </div>
      <div v-if="institutions.length" class="rc-explorer">
        <aside class="rc-people">
          <label class="rc-search"><span>选择负责人</span><input v-model="search" type="search" placeholder="搜索姓名或项目" aria-label="搜索负责人或项目"/></label>
          <div class="rc-people-list">
            <button v-for="p in filteredPeople" :key="p.id" type="button" :class="{active:p.id===personId}" :aria-pressed="p.id===personId" @click="choosePerson(p.id)"><span>{{ p.name }}</span><small>{{ p.projects.length }} 个项目<template v-if="p.projects.length>1 && p.verified"> · 核验接续</template><template v-else> · {{ p.projects[0].approval_year }} 年</template></small><b aria-hidden="true">›</b></button>
            <p v-if="!filteredPeople.length" class="rc-empty">没有匹配的负责人记录。</p>
          </div>
          <p class="rc-caption">{{ org }}<br>{{ number(institutionCoverage?.paper_nodes_2017_2025 || 0) }} 篇关联论文 · 按论文身份去重</p>
        </aside>
        <div class="rc-timeline-column">
          <div class="rc-person-heading"><div><h4>{{ person?.name || '请选择负责人' }}</h4><p>{{ selectedProjects.length }} 个展示项目 · {{ number(personPaperCount) }} 篇关联论文（2017—2025 年）</p></div><span v-if="selectedContinuities.length" class="rc-verified">官方负责人身份支持接续</span></div>
          <div class="rc-overflow rc-timeline-scroll" tabindex="0" aria-label="项目与论文时间轴，可横向滚动">
            <svg v-if="selectedProjects.length" class="rc-timeline" :viewBox="`0 0 1040 ${timelineHeight}`" :style="{height: `${timelineHeight}px`}" role="group" aria-label="点击项目批准节点或年度论文节点查看证据">
              <g v-for="year in yearList" :key="year"><line :x1="sx(year)" :x2="sx(year)" y1="48" :y2="timelineHeight-18" stroke="#efedeb"/><text :x="sx(year)" y="30" text-anchor="middle" class="rc-svg-year">{{ year }}</text></g>
              <g v-for="(p,index) in selectedProjects" :key="projectId(p)">
                <line x1="218" x2="1004" :y1="rowY(index)" :y2="rowY(index)" stroke="#e7e3df" stroke-width="2"/>
                <g class="rc-svg-button" role="button" tabindex="0" :aria-label="`查看项目：${p.title}`" @click="pickProject(p)" @keydown.enter="pickProject(p)" @keydown.space.prevent="pickProject(p)">
                  <rect x="4" :y="rowY(index)-43" width="206" height="84" rx="8" :fill="activeProject && projectId(activeProject)===projectId(p) ? '#f5f2ef' : 'transparent'"/>
                  <text x="15" :y="rowY(index)-21" class="rc-svg-project-type">{{ shortType(p.project_type) }}</text>
                  <text v-for="(line,li) in titleLines(p.title)" :key="li" x="15" :y="rowY(index)+li*19+1" class="rc-svg-project-title">{{ line }}</text>
                  <title>{{ p.title }} · {{ p.approval_year }} 年批准</title>
                  <line :x1="sx(p.approval_year)" :x2="startX(p)" :y1="rowY(index)" :y2="rowY(index)" stroke="#ae0d28" stroke-dasharray="3 4"/>
                  <rect v-if="p.start_date && p.end_date" :x="startX(p)" :y="rowY(index)-5" :width="Math.max(8,endX(p)-startX(p))" height="10" rx="5" :fill="activeProject && projectId(activeProject)===projectId(p) ? '#b74b5d' : '#d5b4ba'"/>
                  <path :d="`M ${sx(p.approval_year)} ${rowY(index)-8} l 8 8 l -8 8 l -8 -8 Z`" fill="#ae0d28"/>
                </g>
                <g v-for="group in paperGroups(p)" :key="group.year" class="rc-svg-button" role="button" tabindex="0" :aria-label="`${p.title}，${group.year} 年 ${group.papers.length} 篇关联论文，查看列表`" @click="pickYear(p,group)" @keydown.enter="pickYear(p,group)" @keydown.space.prevent="pickYear(p,group)">
                  <path :d="`M ${sx(group.year)} ${rowY(index)+7} v 18 q 0 9 10 9`" stroke="#9bb1b8" fill="none"/>
                  <rect :x="sx(group.year)-21" :y="rowY(index)+20" width="58" height="52" rx="9" fill="transparent"/>
                  <circle :cx="sx(group.year)+10" :cy="rowY(index)+34" r="6" fill="#396f80" :stroke="picked?.project && projectId(picked.project)===projectId(p) && picked?.year===group.year ? '#396f80' : 'white'" stroke-width="4"/>
                  <text :x="sx(group.year)+10" :y="rowY(index)+59" text-anchor="middle" class="rc-svg-paper-count">{{ group.papers.length }} 篇</text>
                  <title>{{ group.year }} 年发表 · 点击查看 {{ group.papers.length }} 篇论文</title>
                </g>
              </g>
            </svg>
          </div>
          <div class="rc-legend"><span><i class="rc-diamond"/>项目批准</span><span><i class="rc-line"/>计划执行期</span><span><i class="rc-paper-dot"/>当年关联论文，点击展开</span><button v-if="picked" type="button" class="rc-text-button" @click="viewEvidence">查看所选证据 ↓</button></div>
          <div v-if="selectedContinuities.length" class="rc-continuity-note"><strong>接续依据</strong><span v-for="r in selectedContinuities" :key="r.continuity_id">{{ r.earlier_approval_year }} {{ shortType(r.earlier_project_type) }} <b>→</b> {{ r.later_approval_year }} {{ shortType(r.later_project_type) }}<small>前后项目的官方负责人身份一致<template v-if="r.execution_windows_overlap">；执行期有重叠</template>。</small></span></div>
        </div>
      </div>
      <p v-else class="rc-empty">尚未传入机构与项目明细。</p>

      <div v-if="activeProject" ref="evidenceElement" class="rc-evidence" aria-live="polite">
        <div class="rc-project-evidence"><span class="rc-kicker">{{ picked?.kind==='papers' ? `${picked.year} 年成果所属项目` : '所选项目' }}</span><h4>{{ activeProject.title }}</h4><dl><div><dt>批准号</dt><dd>{{ activeProject.grant_no }}</dd></div><div><dt>负责人</dt><dd>{{ activeProject.principal_investigator }}</dd></div><div><dt>批准年份</dt><dd>{{ activeProject.approval_year }}</dd></div><div v-if="activeProject.start_date && activeProject.end_date"><dt>执行期</dt><dd>{{ activeProject.start_date }} 至 {{ activeProject.end_date }}</dd></div><div v-if="activeProject.amount_raw"><dt>批准经费</dt><dd>{{ number(activeProject.amount_raw) }} {{ activeProject.amount_unit || '万元' }}</dd></div></dl><details v-if="activeProject.abstract_zh"><summary>研究目标与项目摘要</summary><p>{{ activeProject.abstract_zh }}</p></details></div>
        <div v-if="picked?.kind==='papers'" class="rc-paper-evidence"><span class="rc-kicker">{{ picked.year }} 年 · {{ pickedPapers.length }} 篇论文</span><div class="rc-paper-picker"><button v-for="p in pickedPapers" :key="p.paper_id" type="button" :class="{active:activePaper?.paper_id===p.paper_id}" @click="selectedPaper=p">{{ p.title }}</button></div><div v-if="activePaper" class="rc-paper-source"><strong>{{ activePaper.title }}</strong><p>{{ activePaper.venue || '关联论文' }} · {{ activePaper.publication_year }} 年</p><p class="rc-basis">{{ evidenceBasis(activePaper.bases).join('；') || '项目与论文的来源关联' }}</p><small v-if="activePaper.doi">DOI · {{ activePaper.doi }}</small><a v-if="paperLink(activePaper)" :href="paperLink(activePaper)" target="_blank" rel="noopener noreferrer">阅读原文 ↗</a></div></div>
        <div v-else class="rc-evidence-hint"><span class="rc-kicker">读图方式</span><h4>从项目，追到一年的具体成果</h4><p>点击蓝色论文节点，查看论文题名、发表年份及与该项目的关联依据。</p><p class="rc-caption">成果依据：项目成果登记、论文明确资助标注。</p></div>
      </div>
      <details class="rc-caption rc-bottom-note"><summary>查看样本与关系口径</summary><p>四所机构在 2017—2021 年获批项目的 2017—2025 年论文；同一论文可关联多个项目。负责人按官方身份关联，未接通的同名记录按项目分列。接续比例以已观察到的前后项目关系为分母。</p></details>
    </section>

    <section v-if="caseProjects.length" class="rc-surface rc-case">
      <div class="rc-section-top"><div><span class="rc-kicker">04 / 深入一个研究问题</span><h3>小样本图像分类：从判别特征到迁移与可靠度量</h3><p>李晓旭 · 兰州理工大学</p></div><button type="button" class="rc-outline-button" @click="viewCaseTimeline">在时间轴中查看 ↑</button></div>
      <div class="rc-case-question"><span>共同问题</span><strong>{{ detail.project_continuity?.shared_question }}</strong></div>
      <div class="rc-case-stages">
        <article v-for="p in caseProjects" :key="p.grant_no" class="rc-case-stage">
          <header><span class="rc-stage-dot"/><span class="rc-kicker">{{ p.approval_year }} 年批准 · {{ shortType(p.project_type) }}</span><h4>{{ p.short_title || p.title }}</h4><p>执行 {{ yearOf(p.start_date) }}—{{ yearOf(p.end_date) }} · {{ number(p.amount_raw) }} {{ p.amount_unit || '万元' }}</p></header>
          <div class="rc-project-goals"><span class="rc-mini-label">项目研究目标</span><p>{{ p.research_question }}</p><ul><li v-for="method in p.planned_methods || []" :key="method">{{ method }}</li></ul><details><summary>查看项目全称与批准号</summary><p>{{ p.title }}<br>批准号 {{ p.grant_no }}</p><p>{{ p.abstract_zh }}</p></details></div>
          <div class="rc-case-outcomes">
            <article v-for="paper in casePapers(p)" :key="paper.paper_id" class="rc-outcome">
              <div class="rc-outcome-meta"><span>{{ paper.publication_year }}</span><span>{{ paper.contribution_type==='review' ? '综述 · 方法梳理' : '方法研究' }}</span></div>
              <h5>{{ paper.short_title }}</h5><p>{{ paper.summary_sentence }}</p>
              <div class="rc-outcome-actions"><button type="button" :aria-expanded="openCasePaper===paper.paper_id" @click="openCasePaper=openCasePaper===paper.paper_id ? '' : paper.paper_id">{{ openCasePaper===paper.paper_id ? '收起' : '研究内容与证据' }} {{ openCasePaper===paper.paper_id ? '−' : '+' }}</button><a v-if="paperLink(paper)" :href="paperLink(paper)" target="_blank" rel="noopener noreferrer">阅读原文 ↗</a></div>
              <div v-if="openCasePaper===paper.paper_id" class="rc-outcome-detail"><strong>{{ paper.title }}</strong><dl><dt>研究问题</dt><dd>{{ paper.problem }}</dd><dt>方法与内容</dt><dd>{{ paper.method }}</dd><dt>项目关联依据</dt><dd>{{ evidenceBasis(paper.bases || paper.relationship_evidence?.bases).join('；') }} · 批准号 {{ p.grant_no }}</dd><dt v-if="paper.evidence_location">内容核验</dt><dd v-if="paper.evidence_location">{{ paper.evidence_location }}</dd><dt v-if="paper.authorship?.verified">作者核验</dt><dd v-if="paper.authorship?.verified">原文署名已核验：{{ paper.authorship.pi_name_in_paper || '李晓旭' }}</dd><dt v-if="paper.doi">DOI</dt><dd v-if="paper.doi">{{ paper.doi }}</dd></dl></div>
            </article>
          </div>
        </article>
      </div>
      <footer class="rc-case-footer"><strong>同一研究问题持续推进，方法研究与知识梳理共同积累。</strong><p>两期项目执行期在 2022 年交叠，研究围绕少样本识别继续深化。研究内容可查论文原文；项目联系依据成果登记或明确资助标注。</p></footer>
    </section>
  </div>
</template>

<style scoped>
.rc-key-findings{display:grid;grid-template-columns:repeat(3,1fr);gap:26px;margin:8px 0 30px}.rc-key-findings article{border-top:2px solid #b77b87;padding:20px 0 4px}.rc-key-findings span{font-size:16px;font-weight:650;color:#463832;display:block;line-height:1.65}.rc-key-findings strong{display:block;font-size:36px;color:#ae0d28;font-weight:650;margin:9px 0}.rc-key-findings small{font-size:16px;font-weight:400;margin-left:4px}.rc-key-findings p{font-size:14px;line-height:1.9;color:#80746b}.rc-timeline{width:100%!important;min-width:850px!important;height:auto!important}.rc-timeline-scroll{max-height:none}
@media(max-width:720px){.rc-key-findings{grid-template-columns:1fr;gap:12px}.rc-key-findings strong{font-size:29px}}

.rc{--red:#ae0d28;--ink:#292b2d;--muted:#777570;--line:#e6e2dd;--warm:#f7f6f3;--blue:#396f80;color:var(--ink);font-size:14px;line-height:1.65;max-width:1600px;margin:0 auto}.rc *{box-sizing:border-box}.rc h2,.rc h3,.rc h4,.rc h5,.rc p{margin:0}.rc button,.rc input{font:inherit}.rc button{cursor:pointer}.rc button:focus-visible,.rc a:focus-visible,.rc input:focus-visible,.rc [tabindex]:focus-visible,.rc summary:focus-visible{outline:3px solid #b84c61;outline-offset:3px}.rc a{color:var(--red);text-decoration:none}.rc a:hover{text-decoration:underline}.rc-intro{display:flex;justify-content:space-between;gap:28px;align-items:center;margin:24px 0 28px}.rc-eyebrow,.rc-kicker{font-size:12px;font-weight:600;letter-spacing:.06em;color:var(--muted)}.rc-eyebrow{color:var(--red)}.rc h2{font-size:clamp(23px,2.2vw,31px);letter-spacing:-.035em;margin:7px 0 9px;line-height:1.4}.rc-intro p{color:var(--muted);font-size:15px}.rc-proof-count{display:flex;align-items:center;gap:15px;white-space:nowrap;border-left:1px solid var(--line);padding-left:28px}.rc-proof-count strong{font-size:43px;line-height:1.1;letter-spacing:-.05em;color:var(--red);font-variant-numeric:tabular-nums}.rc-proof-count span{font-size:12px;color:var(--muted)}.rc-surface{background:#fff;border:1px solid var(--line);border-radius:17px;padding:25px 28px}.rc-overview{display:grid;grid-template-columns:1.2fr 1fr;gap:18px;margin-bottom:24px}.rc-section-top{display:flex;justify-content:space-between;gap:18px;align-items:flex-start}.rc h3{font-size:20px;line-height:1.5;letter-spacing:-.025em;margin-top:6px}.rc h3 em{font-style:normal;color:var(--red);margin-left:5px}.rc-period{font-size:12px;color:var(--muted);white-space:nowrap;margin-top:6px}.rc-overflow{overflow-x:auto;overscroll-behavior-inline:contain}.rc-growth-svg{display:block;width:100%;min-width:420px;max-height:190px;margin:4px 0 0}.rc-svg-value{fill:var(--ink);font-size:23px;font-weight:650;font-variant-numeric:tabular-nums}.rc-svg-year{fill:var(--muted);font-size:13px}.rc-small-lead{font-size:13px;color:var(--muted);margin:15px 0 16px!important}.rc-small-lead b{color:var(--ink);font-weight:600}.rc-cohort-line{display:grid;grid-template-columns:112px 1fr 52px;gap:13px;align-items:center;margin:13px 0;font-size:13px}.rc-cohort-track{height:5px;border-radius:6px;background:#eeece8;overflow:hidden}.rc-cohort-track i{display:block;background:#ae0d28;height:100%;border-radius:6px}.rc-cohort-line strong{text-align:right;font-size:19px;line-height:1.3;font-variant-numeric:tabular-nums}.rc-cohort-line small{font-size:11px;color:var(--muted);font-weight:400}.rc-caption{font-size:11px!important;color:var(--muted);line-height:1.75!important}.rc-persistence>.rc-caption{margin-top:19px}.rc-trajectories{scroll-margin-top:24px;padding-bottom:20px}.rc-institution-tabs{display:flex;flex-wrap:wrap;gap:9px;margin:23px 0 22px}.rc-institution-tabs button{padding:8px 16px;border:1px solid var(--line);border-radius:24px;background:#fff;color:var(--ink);font-size:13px;transition:background .15s}.rc-institution-tabs button span{color:var(--muted);font-size:11px;margin-left:8px}.rc-institution-tabs button.active{background:#292b2d;border-color:#292b2d;color:#fff}.rc-institution-tabs button.active span{color:#ddd9d4}.rc-explorer{display:grid;grid-template-columns:205px minmax(0,1fr);border:1px solid var(--line);border-radius:12px;overflow:hidden}.rc-people{padding:18px 14px;background:var(--warm);border-right:1px solid var(--line)}.rc-search>span{font-size:12px;color:var(--muted);display:block;margin-bottom:10px}.rc-search input{width:100%;border:1px solid var(--line);border-radius:7px;background:#fff;padding:8px 10px;font-size:12px;color:var(--ink)}.rc-people-list{max-height:475px;overflow-y:auto;margin:15px -2px}.rc-people-list button{position:relative;display:block;width:100%;text-align:left;background:transparent;border:1px solid transparent;padding:11px 25px 11px 11px;border-radius:8px;margin-bottom:3px;color:var(--ink)}.rc-people-list button>span{font-weight:600;display:block}.rc-people-list button small{display:block;color:var(--muted);font-size:10px;margin-top:3px}.rc-people-list button b{position:absolute;right:10px;top:15px;color:#b2aaa4;font-size:21px;font-weight:400}.rc-people-list button.active{background:white;border-color:var(--line);box-shadow:0 1px 3px #00000004}.rc-people-list button.active>span{color:var(--red)}.rc-timeline-column{min-width:0;padding:18px 22px 13px}.rc-person-heading{display:flex;gap:15px;justify-content:space-between;align-items:center;margin-bottom:14px}.rc-person-heading h4{font-size:21px;font-weight:650;letter-spacing:-.025em}.rc-person-heading p{color:var(--muted);font-size:12px;margin-top:3px}.rc-verified{font-size:10px;color:var(--red);background:#faf3f3;border-radius:20px;padding:4px 9px;white-space:nowrap}.rc-timeline{display:block;width:1040px;min-width:1040px;font-family:inherit}.rc-timeline-scroll{max-height:650px;overflow-y:auto}.rc-svg-button{cursor:pointer;outline-offset:-2px!important}.rc-svg-button:hover .rc-svg-project-title{fill:var(--red)}.rc-svg-project-type{fill:var(--red);font-size:11px;font-weight:600}.rc-svg-project-title{fill:var(--ink);font-size:13px;font-weight:500}.rc-svg-paper-count{fill:var(--blue);font-size:11px;font-weight:600}.rc-legend{display:flex;flex-wrap:wrap;gap:17px;align-items:center;padding:12px 0 3px;font-size:11px;color:var(--muted)}.rc-legend span{display:flex;align-items:center;gap:6px}.rc-diamond{width:7px;height:7px;transform:rotate(45deg);background:var(--red);display:inline-block}.rc-line{display:inline-block;width:23px;height:6px;border-radius:8px;background:#d5b4ba}.rc-paper-dot{width:7px;height:7px;border-radius:50%;background:var(--blue);display:inline-block}.rc-text-button{border:0;background:transparent;color:var(--red);font-size:11px}.rc-continuity-note{padding:13px 0 0;margin-top:12px;border-top:1px solid var(--line);display:flex;align-items:flex-start;gap:18px;flex-wrap:wrap;font-size:12px}.rc-continuity-note>strong{color:var(--red);font-size:11px}.rc-continuity-note b{margin:0 9px;font-weight:400;color:var(--red)}.rc-continuity-note small{display:block;color:var(--muted);margin-top:3px;font-size:10px}.rc-evidence{display:grid;grid-template-columns:1fr 1.25fr;gap:28px;background:var(--warm);border-radius:10px;margin-top:18px;padding:20px 24px;scroll-margin-top:24px}.rc-evidence h4{font-size:15px;font-weight:600;margin:7px 0 12px}.rc-evidence dl{margin:0;display:grid;grid-template-columns:1fr 1fr;gap:6px 18px;font-size:12px}.rc-evidence dl>div{display:flex;gap:10px}.rc dt{color:var(--muted);font-weight:400;flex-shrink:0}.rc dd{margin:0;overflow-wrap:anywhere}.rc-evidence details{font-size:12px;margin-top:12px}.rc details summary{cursor:pointer;color:var(--red);font-size:12px}.rc details p{color:var(--muted);font-size:12px;line-height:1.9;margin-top:10px}.rc-evidence-hint{border-left:1px solid var(--line);padding-left:26px}.rc-evidence-hint p{color:var(--muted);font-size:13px;margin-top:10px}.rc-paper-picker{max-height:150px;overflow:auto;display:grid;gap:4px;margin-top:9px}.rc-paper-picker button{background:white;border:1px solid var(--line);border-radius:6px;text-align:left;font-size:11px;padding:7px 9px;color:var(--ink);overflow-wrap:anywhere;line-height:1.5}.rc-paper-picker button.active{color:var(--red);border-color:#b94e61}.rc-paper-source{margin-top:14px;font-size:12px;line-height:1.7;overflow-wrap:anywhere}.rc-paper-source>strong{font-weight:600}.rc-paper-source p{color:var(--muted);font-size:11px;margin-top:5px}.rc-paper-source small{display:block;font-size:10px;color:var(--muted)}.rc-paper-source a{display:inline-block;margin-top:7px;font-size:11px}.rc-basis{color:var(--blue)!important}.rc-bottom-note{margin-top:15px!important}.rc-empty{padding:30px 12px;text-align:center;color:var(--muted);font-size:13px}.rc-case{margin-top:24px}.rc-case .rc-section-top p{margin-top:7px;color:var(--muted);font-size:14px}.rc-outline-button{background:white;border:1px solid var(--line);border-radius:7px;padding:8px 13px;white-space:nowrap;font-size:12px;color:var(--ink)}.rc-case-question{display:flex;gap:20px;align-items:center;margin:24px 0 26px;padding:17px 20px;background:var(--warm);border-radius:10px}.rc-case-question>span{font-size:11px;color:var(--muted);white-space:nowrap}.rc-case-question>strong{font-size:16px;font-weight:600}.rc-case-stages{display:grid;grid-template-columns:1fr 1fr;gap:36px}.rc-case-stage{min-width:0}.rc-case-stage>header{border-top:3px solid var(--red);position:relative;padding-top:22px}.rc-stage-dot{position:absolute;top:-7px;left:0;width:11px;height:11px;border-radius:50%;background:var(--red);box-shadow:0 0 0 4px white}.rc-case-stage>header .rc-kicker{color:var(--red)}.rc-case-stage h4{font-size:21px;line-height:1.4;margin:7px 0 8px;letter-spacing:-.025em}.rc-case-stage>header p{font-size:12px;color:var(--muted)}.rc-project-goals{font-size:13px;padding:18px 0 21px;min-height:240px}.rc-mini-label{font-size:11px;color:var(--muted);display:block;margin-bottom:6px}.rc-project-goals>p{font-weight:500}.rc-project-goals ul{padding-left:17px;margin:9px 0 13px;color:#686661;font-size:12px;line-height:1.9}.rc-case-outcomes{border-left:1px solid #c2d0d3;margin-left:4px;padding-left:22px;display:grid;gap:17px;align-content:start}.rc-outcome{position:relative;background:#f7f9f9;border:1px solid #e4ebec;border-radius:10px;padding:16px 18px}.rc-outcome:before{content:'';position:absolute;left:-23px;top:28px;width:22px;height:1px;background:#aabfc5}.rc-outcome-meta{display:flex;justify-content:space-between;gap:10px;color:var(--blue);font-size:11px}.rc-outcome-meta>span:first-child{font-size:16px;font-weight:650}.rc-outcome h5{font-size:17px;margin:7px 0 7px;font-weight:600;line-height:1.5}.rc-outcome>p{color:#676e70;font-size:12px;line-height:1.85}.rc-outcome-actions{display:flex;justify-content:space-between;gap:15px;margin-top:14px;padding-top:12px;border-top:1px solid #e0e8ea;font-size:11px}.rc-outcome-actions button{padding:0;border:0;background:transparent;color:var(--blue);font-size:11px}.rc-outcome-actions a{color:var(--blue)}.rc-outcome-detail{padding-top:16px;margin-top:12px;border-top:1px solid #dce5e7;font-size:12px;line-height:1.8;overflow-wrap:anywhere}.rc-outcome-detail>strong{font-weight:600}.rc-outcome-detail dl{margin:14px 0 0;display:grid;grid-template-columns:80px 1fr;gap:8px 12px;font-size:11px}.rc-case-footer{margin-top:27px;padding-top:18px;border-top:1px solid var(--line)}.rc-case-footer strong{font-size:14px;font-weight:600}.rc-case-footer p{color:var(--muted);font-size:11px;line-height:1.9;margin-top:7px}
@media(min-width:1450px){.rc-timeline{width:100%;min-width:1040px}}
@media(max-width:1100px){.rc-overview{grid-template-columns:1fr}.rc-growth-svg{max-height:190px}.rc-expansion .rc-section-top{align-items:center}.rc-cohort-line{grid-template-columns:125px 1fr 70px}.rc-explorer{grid-template-columns:175px minmax(0,1fr)}.rc-evidence{grid-template-columns:1fr 1fr}.rc-evidence dl{grid-template-columns:1fr}.rc-section-top{flex-wrap:wrap}.rc-project-goals{min-height:290px}.rc-case-stages{gap:24px}}
@media(max-width:720px){.rc-intro{display:block;margin:18px 0}.rc-proof-count{margin-top:18px;padding-left:0;border-left:0;gap:12px}.rc-proof-count strong{font-size:32px}.rc-proof-count span{font-size:11px}.rc-proof-count br{display:none}.rc-surface{padding:19px 16px;border-radius:12px}.rc-period{white-space:normal}.rc h3{font-size:18px}.rc-expansion .rc-section-top{display:block}.rc-explorer{display:block}.rc-people{border-right:0;border-bottom:1px solid var(--line);padding:12px}.rc-search{display:flex;gap:15px;align-items:center}.rc-search>span{margin:0;white-space:nowrap}.rc-search input{max-width:260px}.rc-people-list{display:flex;gap:6px;max-height:none;overflow-x:auto;margin:12px 0 0}.rc-people-list button{width:auto;min-width:130px;flex-shrink:0;padding:8px 12px}.rc-people-list button b{display:none}.rc-people>.rc-caption{display:none}.rc-timeline-column{padding:16px 12px}.rc-person-heading{flex-wrap:wrap}.rc-evidence{grid-template-columns:1fr;padding:16px;gap:20px}.rc-evidence-hint{padding:18px 0 0;border-left:0;border-top:1px solid var(--line)}.rc-case-stages{grid-template-columns:1fr;gap:36px}.rc-project-goals{min-height:0}.rc-case-question{display:block;padding:14px 16px}.rc-case-question>span{display:block;margin-bottom:6px}.rc-case-question>strong{font-size:15px}.rc-case-outcomes{padding-left:17px}.rc-outcome:before{left:-18px;width:17px}.rc-outcome{padding:14px}.rc-case-stage h4{font-size:20px}.rc-outcome-detail dl{grid-template-columns:1fr;gap:4px}.rc-outcome-detail dd{margin-bottom:9px}.rc-institution-tabs{gap:7px}.rc-institution-tabs button{padding:7px 11px;font-size:12px}.rc-cohort-line{grid-template-columns:107px 1fr 53px;gap:9px}.rc-intro p{font-size:13px}}
@media(prefers-reduced-motion:reduce){.rc *{scroll-behavior:auto!important;transition:none!important}}
</style>
