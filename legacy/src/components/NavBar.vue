<template>
  <nav class="nav-bar">
    <router-link
      v-for="item in NAV_ITEMS"
      :key="item.path"
      :to="item.path"
      class="nav-item"
      :class="[
        `nav-item--${item.path.replace(/^\//, '') || 'overview'}`,
        { active: isActive(item.path) },
      ]"
    >{{ item.short || item.label }}</router-link>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { NAV_ITEMS } from '../constants/site.js'

const route = useRoute()

function isActive(path) {
  if (path === '/overview') return route.path === '/overview' || route.path === '/'
  return route.path === path || route.path.startsWith(`${path}/`)
}
</script>
