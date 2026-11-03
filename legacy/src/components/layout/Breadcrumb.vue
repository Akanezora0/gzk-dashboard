<template>
  <nav v-if="items.length" class="breadcrumb" aria-label="面包屑">
    <template v-for="(item, i) in items" :key="item.path || item.label">
      <router-link v-if="item.path && i < items.length - 1" :to="item.path">{{ item.label }}</router-link>
      <span v-else class="current">{{ item.label }}</span>
      <span v-if="i < items.length - 1" class="sep">/</span>
    </template>
  </nav>
</template>

<script setup>
defineProps({
  items: { type: Array, default: () => [] },
})
</script>

<style scoped>
.breadcrumb {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 0.75rem;
  margin-bottom: 8px;
}
.breadcrumb a {
  color: var(--muted);
  text-decoration: none;
}
.breadcrumb a:hover { color: var(--ruc-red); }
.breadcrumb .current { color: var(--text); }
.breadcrumb .sep { color: #c4c0ba; margin: 0 2px; }
</style>
