<template>
  <div class="page-shell" :class="{ 'page-shell--emphasis': emphasis }">
    <Breadcrumb :items="breadcrumb" />
    <header class="page-head">
      <div>
        <div v-if="question" class="q-badge">{{ question }}</div>
        <h2 class="page-title">{{ title }}</h2>
        <p v-if="intro" class="page-intro">{{ intro }}</p>
      </div>
      <slot name="actions" />
    </header>
    <div class="page-body">
      <slot />
    </div>
  </div>
</template>

<script setup>
import Breadcrumb from './Breadcrumb.vue'

defineProps({
  title: { type: String, required: true },
  intro: { type: String, default: '' },
  question: { type: String, default: '' },
  breadcrumb: { type: Array, default: () => [] },
  emphasis: { type: Boolean, default: false },
})
</script>

<style scoped>
.page-shell { width: 100%; }
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}
.q-badge {
  display: inline-block;
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--ruc-red);
  background: var(--ruc-red-muted);
  padding: 2px 8px;
  border-radius: 4px;
  margin-bottom: 4px;
}
.page-title {
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text);
  letter-spacing: 0.03em;
}
.page-intro {
  font-size: 0.78rem;
  color: var(--muted);
  margin-top: 4px;
  line-height: 1.5;
  max-width: 640px;
}
.page-shell--emphasis .page-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--text);
}
.page-shell--emphasis .page-intro {
  font-size: 0.9rem;
  color: var(--muted);
  line-height: 1.6;
}
.page-body { min-height: 200px; }
</style>
