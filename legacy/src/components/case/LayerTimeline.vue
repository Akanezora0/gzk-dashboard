<template>
  <div class="layer-timeline">
    <div class="timeline-head">
      <h3>{{ layerName }}</h3>
      <p>沿该枝干排列的技术点（当前按文献规模排序，Survey 定稿后将按演进时序重排）</p>
    </div>
    <div class="timeline-track">
      <div class="track-line"></div>
      <button
        v-for="(pt, i) in points"
        :key="pt.tech_tag_id"
        type="button"
        class="timeline-node"
        :class="{ active: selected === pt.tech_tag_id }"
        :style="{ '--delay': i * 50 + 'ms' }"
        @click="$emit('select', pt.tech_tag_id)"
      >
        <div class="node-dot" :class="statusClass(pt)"></div>
        <div class="node-body">
          <div class="node-rank">{{ i + 1 }}</div>
          <div class="node-label">{{ pt.tech_label }}</div>
          <div class="node-meta">
            <span>{{ pt.paper_count_b ?? 0 }} 篇文献</span>
            <span v-if="pt.survey_b_ready" class="survey-ok">Survey</span>
          </div>
        </div>
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  layerName: { type: String, default: '' },
  points: { type: Array, default: () => [] },
  selected: { type: String, default: '' },
})

defineEmits(['select'])

function statusClass(pt) {
  if (pt.survey_b_ready && (pt.paper_count_b || 0) > 50) return 'ok'
  if (pt.survey_b_ready) return 'partial'
  return 'pending'
}
</script>

<style scoped>
.layer-timeline { width: 100%; }

.timeline-head h3 {
  font-size: 1.15rem;
  font-weight: 600;
  color: #f1f5f9;
}
.timeline-head p {
  font-size: 0.82rem;
  color: #64748b;
  margin-top: 6px;
  line-height: 1.5;
}

.timeline-track {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
  padding-left: 28px;
}

.track-line {
  position: absolute;
  left: 11px;
  top: 8px;
  bottom: 8px;
  width: 3px;
  background: linear-gradient(180deg, #3d8bfd, rgba(61,139,253,0.15));
  border-radius: 2px;
}

.timeline-node {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 18px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: none;
  text-align: left;
  cursor: pointer;
  color: inherit;
  transition: background 0.15s, transform 0.15s;
  animation: nodeIn 0.35s ease backwards;
  animation-delay: var(--delay, 0ms);
}
.timeline-node:hover, .timeline-node.active {
  background: rgba(61, 139, 253, 0.1);
  transform: translateX(4px);
}

@keyframes nodeIn {
  from { opacity: 0; transform: translateX(-8px); }
  to { opacity: 1; transform: translateX(0); }
}

.node-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-top: 4px;
  flex-shrink: 0;
  margin-left: -34px;
  position: relative;
  z-index: 1;
  box-shadow: 0 0 0 3px rgba(12, 18, 32, 0.9);
}
.node-dot.ok { background: #22c55e; }
.node-dot.partial { background: #f59e0b; }
.node-dot.pending { background: #64748b; }

.node-body { flex: 1; min-width: 0; }
.node-rank {
  font-size: 0.68rem;
  color: #64748b;
  font-weight: 700;
}
.node-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: #e2e8f0;
  margin-top: 2px;
}
.node-meta {
  display: flex;
  gap: 10px;
  font-size: 0.78rem;
  color: #94a3b8;
  margin-top: 4px;
}
.survey-ok { color: #22c55e; }
</style>
