<template>
  <section class="section-block" :class="[`tone-${tone}`, { flush }]">
    <header v-if="title || $slots.head" class="section-head">
      <div class="section-head-main">
        <span v-if="tag" class="section-tag">{{ tag }}</span>
        <h2 v-if="title" class="section-title">{{ title }}</h2>
        <p v-if="subtitle" class="section-subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.action" class="section-action">
        <slot name="action" />
      </div>
    </header>
    <div class="section-body" :style="bodyStyle">
      <slot />
    </div>
  </section>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  tag: { type: String, default: '' },
  tone: { type: String, default: 'default' },
  flush: { type: Boolean, default: false },
  bodyStyle: { type: Object, default: () => ({}) },
})
</script>

<style scoped>
.section-block {
  position: relative;
  margin-bottom: 36px;
  padding: 28px 32px 32px;
  border-radius: 20px;
  background: var(--surface-module);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow), var(--card-highlight);
  overflow: hidden;
}

.section-block::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.35), rgba(148, 163, 184, 0.08));
  pointer-events: none;
}

.section-block.tone-data {
  border-color: rgba(174, 13, 40, 0.22);
  background:
    radial-gradient(ellipse 90% 70% at 10% 0%, rgba(174, 13, 40, 0.06) 0%, transparent 55%),
    var(--surface-module);
  box-shadow: var(--card-shadow), 0 0 0 1px rgba(174, 13, 40, 0.05) inset;
}
.section-block.tone-data::before {
  background: linear-gradient(90deg, var(--tone-data), rgba(174, 13, 40, 0.12));
}

.section-block.tone-chain {
  border-color: rgba(139, 17, 40, 0.22);
  background:
    radial-gradient(ellipse 90% 70% at 90% 0%, rgba(139, 17, 40, 0.05) 0%, transparent 55%),
    var(--surface-module);
  box-shadow: var(--card-shadow), 0 0 0 1px rgba(139, 17, 40, 0.05) inset;
}
.section-block.tone-chain::before {
  background: linear-gradient(90deg, var(--tone-chain), rgba(139, 17, 40, 0.12));
}

.section-block.tone-case {
  border-color: rgba(196, 30, 58, 0.2);
  background:
    radial-gradient(ellipse 90% 60% at 50% 100%, rgba(196, 30, 58, 0.05) 0%, transparent 60%),
    var(--surface-module);
  box-shadow: var(--card-shadow), 0 0 0 1px rgba(196, 30, 58, 0.05) inset;
}
.section-block.tone-case::before {
  background: linear-gradient(90deg, var(--tone-case), rgba(196, 30, 58, 0.12));
}

.section-block.flush { padding-left: 0; padding-right: 0; }

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}

.section-tag {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--ruc-red);
  margin-bottom: 10px;
  padding: 4px 10px;
  border-radius: 999px;
  background: var(--ruc-red-muted);
  border: 1px solid rgba(174, 13, 40, 0.2);
}

.tone-chain .section-tag {
  color: var(--ruc-red-dark);
  background: rgba(155, 0, 0, 0.08);
  border-color: rgba(155, 0, 0, 0.18);
}

.tone-case .section-tag {
  color: var(--ruc-red-light);
  background: rgba(196, 30, 58, 0.08);
  border-color: rgba(196, 30, 58, 0.18);
}

.section-title {
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.03em;
  line-height: 1.25;
}

.section-subtitle {
  font-size: 0.9rem;
  color: var(--muted);
  margin-top: 10px;
  line-height: 1.65;
  max-width: 720px;
}

.section-action {
  flex-shrink: 0;
}

.section-body {
  min-height: 0;
}

@media (max-width: 768px) {
  .section-block { padding: 24px 20px 28px; margin-bottom: 28px; }
  .section-title { font-size: 1.3rem; }
  .section-head { flex-direction: column; }
}
</style>
