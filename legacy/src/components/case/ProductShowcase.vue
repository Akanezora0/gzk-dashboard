<template>
  <div class="product-showcase">
    <div class="showcase-stats">
      <div v-for="s in stats" :key="s.label" class="stat-chip">
        <span class="stat-val">{{ s.val }}</span>
        <span class="stat-label">{{ s.label }}</span>
      </div>
    </div>

    <div class="product-section-head">
      <h3 class="product-section-title">载体产品方向</h3>
      <p class="product-section-sub">UAV · eVTOL · 通航等典型载体，可进入对应专题</p>
    </div>

    <div class="product-grid">
      <article
        v-for="p in enrichedProducts"
        :key="p.id"
        class="product-card"
        :class="{ active: model === p.id, expanded: expanded === p.id }"
        @mouseenter="hover = p.id"
        @mouseleave="hover = ''"
        @click="select(p.id)"
      >
        <header class="pc-head">
          <span class="pc-id">{{ p.id }}</span>
          <span class="pc-name">{{ p.name }}</span>
        </header>
        <p class="pc-desc">{{ p.desc }}</p>
        <p class="pc-stage">{{ p.stage }}</p>

        <div v-if="expanded === p.id || hover === p.id" class="pc-detail">
          <div class="pc-metrics">
          <span>OpenScholar {{ p.a_papers }} 篇</span>
          <span>Skills {{ p.b_papers }} 篇</span>
            <span>Survey {{ p.surveys }} 篇</span>
            <span>基金 {{ pct(p.fund_ratio_b) }}</span>
          </div>
          <p class="pc-status">{{ p.status }}</p>
          <router-link
            :to="`/case?product=${p.id}`"
            class="pc-link"
            @click.stop
          >进入 {{ p.id }} 专题 →</router-link>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { SKILLS_B_PAPERS } from '../../constants/dataCatalog.js'

const props = defineProps({
  modelValue: { type: String, default: 'UAV' },
  workflow: { type: Object, default: () => ({}) },
  progress: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['update:modelValue'])

const hover = ref('')
const expanded = ref('')

const PRODUCT_META = {
  UAV: { desc: '飞控 · 导航 · 集群协同 · 任务载荷', stage: '遥控平台 → 智能作业' },
  eVTOL: { desc: '电推进 · 冗余飞控 · 适航合规', stage: '概念验证 → 商业化运营' },
  GA: { desc: '综合航电 · 安全体系 · 空域协同', stage: '活塞航空 → 数字绿色通航' },
}

const stats = computed(() => {
  const p = props.progress
  const w = props.workflow.tech_point_work || {}
  return [
    { label: '技术大类', val: p.tech_layers ?? 6 },
    { label: '技术点', val: p.tech_tags ?? 33 },
    { label: '产品 Survey', val: props.workflow.deliverables?.product_surveys ?? 12 },
    { label: '技术点 Survey', val: props.workflow.deliverables?.tech_surveys ?? 66 },
    { label: 'Skills 文献', val: w.b_line_papers ?? SKILLS_B_PAPERS },
  ]
})

const enrichedProducts = computed(() => {
  const lines = props.workflow.product_lines || []
  return ['UAV', 'eVTOL', 'GA'].map(id => {
    const line = lines.find(x => x.id === id) || {}
    const meta = PRODUCT_META[id] || {}
    return {
      id,
      name: line.name || id,
      desc: meta.desc,
      stage: meta.stage,
      a_papers: line.a_papers,
      b_papers: line.b_papers,
      surveys: line.surveys,
      fund_ratio_b: line.fund_ratio_b,
      status: line.status,
    }
  })
})

function pct(v) {
  return v != null ? `${(v * 100).toFixed(1)}%` : '—'
}

function select(id) {
  emit('update:modelValue', id)
  expanded.value = expanded.value === id ? '' : id
}
</script>

<style scoped>
.product-showcase {
  margin-top: 4px;
}
.showcase-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 22px;
  margin-bottom: 28px;
}
.stat-chip {
  padding: 10px 16px;
  border-radius: 999px;
  background: var(--surface-panel);
  border: 1px solid var(--border);
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.stat-val {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--ruc-red);
  font-variant-numeric: tabular-nums;
}
.stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--label-strong);
}
.product-section-head {
  margin-bottom: 14px;
}
.product-section-title {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--text);
}
.product-section-sub {
  margin: 6px 0 0;
  font-size: 0.78rem;
  color: var(--muted);
}
.product-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.pc-head { display: flex; align-items: baseline; gap: 8px; }
.pc-name { font-size: 0.88rem; color: var(--label-strong); font-weight: 600; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
.product-card {
  padding: 18px 20px;
  border-radius: 14px;
  background: var(--surface-card);
  border: 1px solid var(--border);
  box-shadow: var(--card-shadow);
  cursor: pointer;
  transition: background 0.2s, transform 0.2s, border-color 0.2s;
}
.product-card:hover, .product-card.active {
  background: var(--surface-card-hover);
  border-color: rgba(174, 13, 40, 0.3);
}
.product-card.expanded {
  transform: scale(1.01);
  border-color: var(--ruc-red);
  box-shadow: 0 8px 24px rgba(174, 13, 40, 0.1);
}
.pc-id {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--ruc-red);
}
.pc-desc { font-size: 0.78rem; color: var(--muted); margin-top: 8px; line-height: 1.45; }
.pc-stage { font-size: 0.72rem; color: #a8a29e; margin-top: 6px; }
.pc-detail { margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border); animation: fadeIn 0.2s ease; }
.pc-metrics { display: flex; flex-wrap: wrap; gap: 8px; font-size: 0.72rem; color: var(--muted); }
.pc-status { font-size: 0.72rem; color: #a8a29e; margin-top: 8px; }
.pc-link { display: inline-block; margin-top: 10px; font-size: 0.78rem; color: var(--ruc-red); text-decoration: none; }
.pc-link:hover { color: var(--ruc-red-dark); }

@media (max-width: 900px) {
  .product-grid { grid-template-columns: 1fr; }
}
</style>
