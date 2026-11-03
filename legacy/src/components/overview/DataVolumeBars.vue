<template>
  <div class="volume-bars" :class="{ compact }">
    <div class="chart-head">
      <h4>{{ title }}</h4>
      <p>{{ subtitle }}</p>
    </div>
    <div class="bars-list">
      <div v-for="(item, i) in normalized" :key="`${item.label}-${i}`" class="bar-row">
        <div class="bar-meta">
          <span class="bar-label">{{ item.label }}</span>
          <span class="bar-val" :style="{ color: item.color }">{{ item.display }}</span>
        </div>
        <div class="bar-track">
          <div
            class="bar-fill"
            :style="{
              width: `${item.pct}%`,
              background: item.gradient,
              animationDelay: `${i * 0.06}s`,
            }"
          >
            <span class="bar-glow" :style="{ background: item.color }"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { fmtCount } from '../../composables/useApi'

const props = defineProps({
  items: { type: Array, default: () => [] },
  title: { type: String, default: '核心数据量级' },
  subtitle: { type: String, default: '主要数据源记录规模对比' },
  compact: { type: Boolean, default: false },
})

const normalized = computed(() => {
  const list = [...props.items.filter(i => i.count > 0)].sort((a, b) => b.count - a.count)
  const max = Math.max(...list.map(i => i.count), 1)
  return list.map(i => ({
    ...i,
    display: fmtCount(i.count),
    pct: Math.max(4, (i.count / max) * 100),
    gradient: `linear-gradient(90deg, ${i.color}88, ${i.color})`,
  }))
})
</script>

<style scoped>
.volume-bars {
  padding: 16px 18px;
  border-radius: 14px;
  background: var(--surface-card);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
  height: 100%;
  min-height: 280px;
  display: flex;
  flex-direction: column;
}
.volume-bars.compact {
  min-height: 320px;
}
.chart-head h4 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--label-strong);
}
.chart-head p {
  margin: 4px 0 0;
  font-size: 0.72rem;
  color: var(--label-muted);
}
.bars-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 14px;
  flex: 1;
  overflow-y: auto;
  padding-right: 4px;
}
.compact .bars-list {
  gap: 8px;
  max-height: 340px;
}
.compact .bar-meta {
  margin-bottom: 3px;
}
.compact .bar-label {
  font-size: 0.72rem;
}
.compact .bar-val {
  font-size: 0.82rem;
}
.compact .bar-track {
  height: 7px;
}
.bar-meta {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 6px;
  gap: 8px;
}
.bar-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--label-strong);
  flex: 1;
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bar-val {
  font-size: 0.95rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
  flex-shrink: 0;
}
.bar-track {
  height: 10px;
  border-radius: 999px;
  background: #ece8e3;
  overflow: hidden;
}
.bar-fill {
  position: relative;
  height: 100%;
  border-radius: 999px;
  animation: barGrow 0.9s ease-out both;
  min-width: 4px;
}
.bar-glow {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  box-shadow: 0 0 10px currentColor;
  opacity: 0.9;
}
@keyframes barGrow {
  from { width: 0 !important; opacity: 0.3; }
}
</style>
