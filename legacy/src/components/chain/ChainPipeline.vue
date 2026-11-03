<template>
  <section class="chain-pipeline">
    <div class="pipeline-flow">
      <div
        v-for="(p, i) in steps"
        :key="p.step"
        class="pipe-card"
        :class="{ active: activeStep === p.step }"
        @mouseenter="activeStep = p.step"
        @mouseleave="activeStep = 0"
      >
        <div class="pipe-card-inner">
          <div class="pipe-index">
            <span class="pipe-num">{{ p.step }}</span>
          </div>
          <div class="pipe-content">
            <h4 class="pipe-title">{{ p.title }}</h4>
            <p class="pipe-desc">{{ p.desc }}</p>
            <div class="pipe-source">
              <span class="src-tag">数据来源</span>
              <span class="src-val">{{ p.source }}</span>
            </div>
          </div>
        </div>
        <div v-if="i < steps.length - 1" class="pipe-connector" aria-hidden="true">
          <span class="conn-line"></span>
          <span class="conn-arrow">›</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  steps: { type: Array, required: true },
})

const activeStep = ref(0)
</script>

<style scoped>
.chain-pipeline {
  margin: 20px 0 16px;
}

.pipeline-flow {
  display: flex;
  align-items: stretch;
  gap: 0;
  overflow-x: auto;
  padding: 4px 0 8px;
  scrollbar-width: thin;
}

.pipe-card {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
  position: relative;
}

.pipe-card-inner {
  flex: 1;
  min-width: 160px;
  padding: 18px 16px 16px;
  border-radius: 14px;
  background: var(--surface-card);
  border: 1px solid var(--border);
  box-shadow: var(--card-shadow);
  transition: border-color 0.18s, box-shadow 0.18s, transform 0.15s;
}
.pipe-card.active .pipe-card-inner,
.pipe-card:hover .pipe-card-inner {
  border-color: rgba(174, 13, 40, 0.35);
  box-shadow: 0 6px 20px rgba(174, 13, 40, 0.08);
  transform: translateY(-2px);
}
.pipe-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--ruc-red-muted);
  border: 1px solid rgba(174, 13, 40, 0.35);
  color: var(--ruc-red);
  font-size: 0.85rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}
.pipe-title {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text);
  margin: 0 0 8px;
  letter-spacing: 0.02em;
}
.pipe-desc {
  font-size: 0.82rem;
  color: var(--muted);
  line-height: 1.55;
  margin: 0 0 12px;
  font-weight: 500;
}
.pipe-source {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
}
.src-tag {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #a8a29e;
}
.src-val {
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--ruc-red);
}
.pipe-connector { display: flex; align-items: center; padding: 0 6px; flex-shrink: 0; color: #a8a29e; }
.conn-line {
  width: 20px;
  height: 2px;
  background: linear-gradient(90deg, var(--border), rgba(174, 13, 40, 0.35));
  border-radius: 1px;
}
.conn-arrow { font-size: 1.1rem; font-weight: 700; color: #a8a29e; margin-left: 2px; }

@media (max-width: 960px) {
  .pipeline-flow {
    flex-direction: column;
    align-items: stretch;
  }
  .pipe-connector { display: none; }
  .pipe-card { margin-bottom: 8px; }
}
</style>
