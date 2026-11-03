<template>
  <div class="workflow-panel">
    <div class="deliverables">
      <div v-for="d in deliverableItems" :key="d.label" class="deliver-item" :class="d.tier">
        <div class="deliver-val">{{ d.val }}</div>
        <div class="deliver-label">{{ d.label }}</div>
      </div>
    </div>

    <div class="product-matrix">
      <div v-for="p in highlights.product_lines || []" :key="p.id" class="product-row">
        <div class="pr-head">
          <span class="pr-id">{{ p.id }}</span>
          <span class="pr-name">{{ p.name }}</span>
          <span class="pr-status">{{ p.status }}</span>
        </div>
        <div class="pr-metrics">
          <span>OpenScholar {{ p.a_papers }} 篇</span>
          <span>Skills {{ p.b_papers }} 篇</span>
          <span>DOI交集 {{ p.doi_overlap }}</span>
          <span>基金占比 {{ pct(p.fund_ratio_b) }}</span>
          <span>Survey {{ p.surveys }} 篇</span>
        </div>
      </div>
    </div>

    <div class="pipeline-list">
      <div v-for="stage in highlights.pipeline_stages || []" :key="stage.name" class="pipe-item">
        <span class="pipe-dot" :class="stage.status"></span>
        <div>
          <div class="pipe-name">{{ stage.name }}</div>
          <div class="pipe-desc">{{ stage.desc }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { LA_PATENT_COUNT, SKILLS_B_PAPERS, metric } from '../../constants/dataCatalog.js'

const props = defineProps({
  highlights: { type: Object, default: () => ({}) },
})

const deliverableItems = computed(() => {
  const d = props.highlights.deliverables || {}
  const t = props.highlights.tech_point_work || {}
  return [
    { label: '三产品 Survey', val: d.product_surveys ?? 12, tier: 'primary' },
    { label: '技术点 Survey', val: d.tech_surveys ?? 66, tier: 'primary' },
    { label: 'Skills 文献池', val: t.b_line_papers ?? SKILLS_B_PAPERS, tier: 'primary' },
    { label: '融合文献', val: t.union_papers ?? metric('skills_union_papers'), tier: 'secondary' },
    { label: '期刊论文库', val: d.journal_papers ? `${(d.journal_papers / 10000).toFixed(0)}万+` : '283万+', tier: 'secondary' },
    { label: '低空专利', val: d.la_patents ? `${(d.la_patents / 10000).toFixed(1)}万+` : `${(LA_PATENT_COUNT / 10000).toFixed(1)}万+`, tier: 'secondary' },
  ]
})

function pct(v) {
  return v != null ? `${(v * 100).toFixed(1)}%` : '—'
}
</script>

<style scoped>
.deliverables {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  margin-bottom: 22px;
}
.deliver-item {
  padding: 16px 12px;
  border-radius: 12px;
  background: var(--surface-card);
  border: 1px solid var(--border);
  box-shadow: var(--card-shadow);
  text-align: center;
}
.deliver-item.primary {
  background: var(--surface-panel);
  border-color: rgba(174, 13, 40, 0.15);
  padding: 18px 12px;
}
.deliver-val {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--ruc-red-dark);
  font-variant-numeric: tabular-nums;
}
.deliver-item.primary .deliver-val {
  font-size: 1.65rem;
  color: var(--ruc-red);
}
.deliver-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--label-strong);
  margin-top: 6px;
}

.product-matrix {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}
.product-row {
  padding: 14px 18px;
  border-radius: 12px;
  background: var(--surface-card);
  border: 1px solid var(--card-border);
}
.pr-head {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 8px;
}
.pr-id {
  font-weight: 700;
  color: var(--ruc-red);
  font-size: 0.95rem;
}
.pr-name {
  font-size: 0.88rem;
  color: var(--text);
  font-weight: 500;
}
.pr-status {
  margin-left: auto;
  font-size: 0.72rem;
  color: var(--muted);
}
.pr-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 0.78rem;
  color: var(--muted);
}

.pipeline-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.pipe-item {
  display: flex;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 10px;
  background: var(--surface-card);
  border: 1px solid rgba(148, 163, 184, 0.14);
}
.pipe-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 5px;
  flex-shrink: 0;
}
.pipe-dot.verified { background: #2d6a4f; }
.pipe-dot.in_progress { background: #b45309; }
.pipe-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text);
}
.pipe-desc {
  font-size: 0.72rem;
  color: var(--muted);
  margin-top: 2px;
  line-height: 1.45;
}

@media (max-width: 960px) {
  .deliverables { grid-template-columns: repeat(3, 1fr); }
  .pipeline-list { grid-template-columns: 1fr; }
}
</style>
