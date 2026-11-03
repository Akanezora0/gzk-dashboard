<template>
  <div class="chain-link-cards">
    <button
      v-for="ch in chains"
      :key="ch.chain_type"
      type="button"
      class="link-card"
      :class="{ active: active === ch.chain_type, [ch.status]: true }"
      @click="$emit('select', ch)"
    >
      <div class="lc-head">
        <span class="lc-dot" :class="ch.status"></span>
        <span class="lc-name">{{ ch.label }}</span>
      </div>
      <div class="lc-count">{{ fmtCount(ch.count) }}</div>
      <div class="lc-note">{{ ch.note }}</div>
      <div class="lc-foot">
        <span class="lc-status">{{ statusLabel(ch.status) }}</span>
        <span class="lc-action">探索证据 →</span>
      </div>
    </button>
  </div>
</template>

<script setup>
import { fmtCount } from '../../composables/useApi'
import { statusLabel } from '../../constants/chainHubContent.js'

defineProps({
  chains: { type: Array, default: () => [] },
  active: { type: String, default: '' },
})

defineEmits(['select'])
</script>

<style scoped>
.chain-link-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.link-card {
  text-align: left;
  padding: 16px 18px;
  border-radius: 14px;
  background: var(--surface-card);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: transform 0.15s, border-color 0.15s, box-shadow 0.15s;
}
.link-card:hover {
  transform: translateY(-3px);
  border-color: rgba(174, 13, 40, 0.3);
  box-shadow: 0 6px 20px rgba(174, 13, 40, 0.08);
}
.link-card.active {
  border-color: var(--ruc-red);
  box-shadow: 0 0 0 1px rgba(174, 13, 40, 0.15);
}
.lc-head { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; }
.lc-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.lc-dot.verified { background: #2d6a4f; }
.lc-dot.partial, .lc-dot.candidate { background: #b45309; }
.lc-name { font-size: 0.82rem; font-weight: 700; color: var(--text); line-height: 1.35; }
.lc-count { font-size: 1.65rem; font-weight: 800; color: var(--ruc-red-dark); font-variant-numeric: tabular-nums; margin-bottom: 6px; }
.lc-note { font-size: 0.76rem; color: var(--muted); line-height: 1.45; min-height: 2.4em; }
.lc-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
}
.lc-status { font-size: 0.72rem; font-weight: 600; color: var(--ruc-red); }
.lc-action { font-size: 0.72rem; font-weight: 600; color: #a8a29e; }
.link-card:hover .lc-action { color: var(--ruc-red-dark); }

@media (max-width: 960px) {
  .chain-link-cards { grid-template-columns: repeat(2, 1fr); }
}
</style>
