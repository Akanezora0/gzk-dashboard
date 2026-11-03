<template>
  <div class="chain-flow">
    <p v-if="conclusion" class="flow-conclusion">{{ conclusion }}</p>

    <div class="flow-track">
      <div
        v-for="(step, i) in steps"
        :key="step.id"
        class="flow-step"
        :class="{ highlight: step.highlight }"
      >
        <div class="step-icon" :style="{ background: step.color }">
          <span class="step-abbr">{{ step.abbr }}</span>
        </div>
        <div class="step-body">
          <div class="step-label">{{ step.label }}</div>
          <div class="step-value">{{ step.value }}</div>
          <div v-if="step.note" class="step-note">{{ step.note }}</div>
        </div>
        <div v-if="i < steps.length - 1" class="step-arrow" aria-hidden="true">
          <svg viewBox="0 0 24 24" width="20" height="20"><path fill="currentColor" d="M8 5l8 7-8 7V5z"/></svg>
        </div>
      </div>
    </div>

    <div class="flow-branches">
      <div class="branch-card patent">
        <span class="branch-tag">并行链路</span>
        <span class="branch-text">专利成果</span>
        <span class="branch-val">{{ fmtCount(patentTechLinks) }} 条</span>
        <span class="branch-desc">专利—技术点关联</span>
      </div>
      <div class="branch-card fund">
        <span class="branch-tag">主链</span>
        <span class="branch-text">基金资助论文</span>
        <span class="branch-val">{{ fmtCount(fundPaperLinks) }} 组</span>
        <span class="branch-desc">基金—论文—技术点</span>
      </div>
    </div>

    <div class="flow-legend">
      <span><i class="leg verified"></i>已验证</span>
      <span><i class="leg partial"></i>部分覆盖</span>
      <span><i class="leg candidate"></i>候选</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { fmtCount } from '../../composables/useApi'
import {
  FUND_PAPER_LINKS, PATENT_TECH_LINKS, FUND_PROJECTS_SQLITE, TECH_TAG_COUNT,
} from '../../constants/dataCatalog.js'

const props = defineProps({
  contrib: { type: Object, default: () => ({}) },
  progress: { type: Object, default: () => ({}) },
  chainStatus: { type: Array, default: () => [] },
})

const fundPaperLinks = computed(() => props.contrib.fund_paper_links ?? FUND_PAPER_LINKS)
const patentTechLinks = computed(() => props.contrib.patent_tech_links ?? PATENT_TECH_LINKS)
const fundProjects = computed(() => props.contrib.fund_projects ?? FUND_PROJECTS_SQLITE)
const techTags = computed(() => props.progress.tech_tags ?? TECH_TAG_COUNT)

const conclusion = computed(() => {
  const fundRatio = props.contrib.funding_metadata_ratio
  const highCite = props.contrib.high_citation_ratio
  const fr = fundRatio != null ? `${(fundRatio * 100).toFixed(1)}%` : '—'
  const hc = highCite != null ? `${(highCite * 100).toFixed(1)}%` : '—'
  return `基金—论文—技术主链 ${fmtCount(fundPaperLinks.value)} 组、专利—技术 ${fmtCount(patentTechLinks.value)} 条，成果进入技术演进可溯源；基金支撑文献占 ${fr}，高被引占 ${hc}。`
})

const steps = computed(() => [
  {
    id: 'fund',
    abbr: '基',
    label: '基金投入',
    value: fmtCount(fundProjects.value) + ' 项',
    note: '立项项目',
    color: '#ae0d28',
    highlight: false,
  },
  {
    id: 'output',
    abbr: '果',
    label: '论文·专利',
    value: fmtCount(fundPaperLinks.value) + ' / ' + fmtCount(patentTechLinks.value),
    note: '资助关联 / 技术关联',
    color: '#9b0000',
    highlight: false,
  },
  {
    id: 'tech',
    abbr: '技',
    label: '技术词典',
    value: techTags.value + ' 点',
    note: '6 层结构',
    color: '#2d6a4f',
    highlight: true,
  },
  {
    id: 'product',
    abbr: '产',
    label: '示范产品',
    value: 'UAV · eVTOL · GA',
    note: '三类载体',
    color: '#c41e3a',
    highlight: false,
  },
])
</script>

<style scoped>
.chain-flow { width: 100%; }

.flow-conclusion {
  font-size: 0.78rem;
  line-height: 1.6;
  color: var(--muted);
  padding: 8px 12px;
  margin-bottom: 12px;
  background: var(--ruc-red-muted);
  border-left: 3px solid var(--ruc-red);
  border-radius: 0 6px 6px 0;
}
.flow-track {
  display: flex;
  align-items: stretch;
  gap: 4px;
  padding: 12px 8px;
  background: var(--surface-panel);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow-x: auto;
}
.flow-step {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 140px;
}
.flow-step.highlight .step-body {
  border-color: rgba(45, 106, 79, 0.35);
  background: rgba(45, 106, 79, 0.06);
}
.step-body {
  flex: 1;
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--surface-card);
  min-width: 0;
}
.step-label { font-size: 0.68rem; color: var(--muted); }
.step-value { font-size: 0.82rem; font-weight: 700; color: var(--text); margin-top: 2px; }
.step-note { font-size: 0.62rem; color: #a8a29e; margin-top: 1px; }
.step-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(42, 28, 28, 0.08);
}
.step-abbr { font-size: 0.85rem; font-weight: 700; color: #fff; }
.step-arrow { color: #a8a29e; flex-shrink: 0; opacity: 0.7; }
.flow-branches {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-top: 10px;
}
.branch-card {
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.72rem;
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto auto;
  gap: 2px 8px;
  align-items: center;
}
.flow-legend {
  display: flex;
  gap: 14px;
  margin-top: 8px;
  font-size: 0.68rem;
  color: var(--muted);
}
.leg {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 4px;
  vertical-align: middle;
}
.branch-card.patent {
  background: rgba(180, 83, 9, 0.08);
  border: 1px solid rgba(180, 83, 9, 0.25);
}
.branch-card.fund {
  background: rgba(174, 13, 40, 0.06);
  border: 1px solid rgba(174, 13, 40, 0.2);
}
.branch-tag {
  grid-row: span 2;
  font-size: 0.62rem;
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--surface-panel);
  color: var(--muted);
}
.branch-text { color: var(--muted); }
.branch-val { font-weight: 700; color: var(--ruc-red-dark); justify-self: end; }
.branch-desc { color: #a8a29e; font-size: 0.65rem; grid-column: 2; }
.leg.verified { background: #2d6a4f; }
.leg.partial { background: #b45309; }
.leg.candidate { background: #78716c; }

@media (max-width: 768px) {
  .flow-track { flex-direction: column; }
  .step-arrow { transform: rotate(90deg); align-self: center; }
  .flow-branches { grid-template-columns: 1fr; }
}
</style>
