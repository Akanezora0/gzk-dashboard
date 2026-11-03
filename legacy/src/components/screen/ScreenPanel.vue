<template>
  <div class="screen-panel">
    <div class="screen-panel__inner">
      <div v-if="title" class="screen-panel__head">
        <span class="screen-panel__accent" aria-hidden="true"></span>
        <span class="screen-panel__title">{{ title }}</span>
        <span v-if="subtitle" class="screen-panel__sub">{{ subtitle }}</span>
      </div>
      <div class="screen-panel__body" :style="bodyStyle">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  bodyStyle: { type: Object, default: () => ({}) },
})
</script>

<style scoped>
.screen-panel {
  height: 100%;
  min-height: 0;
  border-radius: 14px;
  background: var(--surface-card);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
  overflow: hidden;
}
.screen-panel__inner {
  height: 100%;
  padding: 14px 16px 12px;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.screen-panel__head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-shrink: 0;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
.screen-panel__accent {
  width: 3px;
  height: 16px;
  border-radius: 2px;
  background: var(--ruc-red);
  flex-shrink: 0;
}
.screen-panel__title {
  font-size: 0.96rem;
  font-weight: 700;
  color: var(--text);
  letter-spacing: 0.03em;
}
.screen-panel__sub {
  margin-left: auto;
  font-size: 0.76rem;
  color: var(--muted);
  font-weight: 500;
}
.screen-panel__body {
  flex: 1;
  min-height: 0;
  overflow: visible;
}
</style>
