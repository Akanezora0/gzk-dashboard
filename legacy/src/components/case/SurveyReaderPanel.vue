<template>
  <div class="survey-reader">
    <div class="reader-head">
      <div class="head-main">
        <h4>{{ title || 'Survey 摘要' }}</h4>
        <p v-if="techLabel" class="reader-sub">{{ techLabel }}</p>
      </div>
      <div class="line-tabs">
        <button
          v-for="line in SURVEY_LINES"
          :key="line.api"
          type="button"
          class="ltab"
          :class="{ active: lineType === line.api }"
          @click="$emit('switch-line', line.api)"
        >{{ line.label }}</button>
      </div>
    </div>

    <div v-if="!techId" class="reader-empty">
      点击树上的技术点，在此查看 Survey 摘要
    </div>
    <Transition v-else name="survey-fade" mode="out-in">
      <div v-if="loading" key="loading" class="reader-empty">加载中…</div>
      <div v-else :key="techId + '-' + lineType" class="reader-content">
        <div class="reader-body markdown-body" v-html="html"></div>
        <div v-if="references.length" class="refs-panel">
          <div class="refs-head">代表文献 · {{ references.length }} 篇</div>
          <ul class="refs-list">
            <li v-for="(r, i) in references" :key="i">
              <span class="ref-idx">{{ i + 1 }}</span>
              <div class="ref-body">
                <div class="ref-title">{{ r.title || '—' }}</div>
                <div class="ref-meta">
                  <span v-if="r.year">{{ r.year }}</span>
                  <span v-if="r.citation_count != null">被引 {{ r.citation_count }}</span>
                  <span v-if="r.has_funding_metadata" class="fund">基金</span>
                </div>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { SURVEY_LINES } from '../../constants/surveyLines.js'

defineProps({
  techId: { type: String, default: '' },
  techLabel: { type: String, default: '' },
  title: { type: String, default: '' },
  html: { type: String, default: '' },
  loading: { type: Boolean, default: false },
  lineType: { type: String, default: 'B' },
  references: { type: Array, default: () => [] },
})

defineEmits(['switch-line'])
</script>

<style scoped>
.survey-reader {
  height: 100%;
  min-height: 420px;
  display: flex;
  flex-direction: column;
  border-radius: 14px;
  background: var(--surface-card, #ffffff);
  border: 1px solid var(--border, #e8e4df);
  box-shadow: var(--card-highlight, 0 1px 0 rgba(255, 255, 255, 0.8) inset);
  overflow: hidden;
}

.reader-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border, #e8e4df);
  background: var(--surface-panel, #faf9f7);
  flex-shrink: 0;
}
.head-main { min-width: 0; flex: 1; }
.reader-head h4 {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text, #2a2a2a);
  line-height: 1.45;
}
.reader-sub {
  margin: 6px 0 0;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--muted, #57534e);
}

.line-tabs { display: flex; gap: 6px; flex-shrink: 0; }
.ltab {
  padding: 5px 12px;
  border-radius: 999px;
  border: 1px solid var(--border, #e8e4df);
  background: var(--surface-card, #fff);
  color: var(--muted, #57534e);
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.ltab:hover {
  border-color: rgba(174, 13, 40, 0.25);
  color: var(--text, #2a2a2a);
}
.ltab.active {
  background: var(--ruc-red-muted, rgba(174, 13, 40, 0.08));
  border-color: rgba(174, 13, 40, 0.35);
  color: var(--ruc-red-dark, #9b0000);
}

.reader-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  font-size: 0.85rem;
  color: var(--muted, #57534e);
  text-align: center;
}

.reader-body {
  flex: 1;
  min-height: 0;
  max-height: 240px;
  overflow-y: auto;
  padding: 16px 18px;
  font-size: 0.82rem;
  line-height: 1.7;
  color: var(--text, #2a2a2a);
}

.reader-content {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.reader-body :deep(p) {
  margin: 0 0 0.75em;
  color: #3d3a36;
}
.reader-body :deep(h1),
.reader-body :deep(h2),
.reader-body :deep(h3) {
  color: var(--text, #2a2a2a);
  font-weight: 700;
  margin: 0.85em 0 0.4em;
}
.reader-body :deep(strong) {
  color: #1c1917;
  font-weight: 700;
}
.reader-body :deep(a) {
  color: var(--ruc-red, #ae0d28);
}

.survey-fade-enter-active,
.survey-fade-leave-active {
  transition: opacity 0.2s ease;
}
.survey-fade-enter-from,
.survey-fade-leave-to {
  opacity: 0;
}

.refs-panel {
  flex-shrink: 0;
  border-top: 1px solid var(--border, #e8e4df);
  max-height: 180px;
  display: flex;
  flex-direction: column;
  background: var(--surface-panel, #faf9f7);
}
.refs-head {
  padding: 9px 16px;
  font-size: 0.74rem;
  font-weight: 700;
  color: var(--text, #2a2a2a);
  background: rgba(174, 13, 40, 0.06);
  border-bottom: 1px solid var(--border, #e8e4df);
  flex-shrink: 0;
}
.refs-list {
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  flex: 1;
}
.refs-list li {
  display: flex;
  gap: 10px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--border, #e8e4df);
  font-size: 0.76rem;
}
.refs-list li:last-child { border-bottom: none; }
.ref-idx {
  color: var(--ruc-red-dark, #9b0000);
  font-weight: 800;
  flex-shrink: 0;
  width: 18px;
  font-variant-numeric: tabular-nums;
}
.ref-title {
  color: var(--text, #2a2a2a);
  font-weight: 600;
  line-height: 1.45;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ref-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 4px;
  color: #57534e;
  font-size: 0.7rem;
  font-weight: 500;
}
.ref-meta .fund {
  color: #15803d;
  font-weight: 700;
}
</style>
