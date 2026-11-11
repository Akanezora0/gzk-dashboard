<template>
  <iframe ref="frame" class="low-altitude-frame" :class="{ready}" :src="initialSrc" :title="'低空经济 · ' + (labels[page] || '专题')" :style="{height: height + 'px'}" @load="ready=true" />
</template>
<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
const props = defineProps({ page: { type: String, required: true } })
const route = useRoute(), router = useRouter(), frame = ref(null), height = ref(720), ready = ref(false)
const labels = { data: '领域数据', evolution: '技术演进', chain: '短链条分析', cases: '长链条分析' }
function cleanQuery() {
  const { domain, ...query } = route.query
  return Object.fromEntries(Object.entries(query).filter(([, value]) => value != null))
}
// Keep src stable; query and page changes flow through the memory router.
const initialSrc = '/low-altitude/index.html?' + new URLSearchParams({ page: props.page, ...cleanQuery() }).toString()
function sendRoute() {
  frame.value?.contentWindow?.postMessage({ channel: 'gzk-low-altitude', type: 'set-route', page: props.page, query: cleanQuery() }, window.location.origin)
}
function receive(event) {
  if (event.origin !== window.location.origin || event.source !== frame.value?.contentWindow) return
  const message = event.data
  if (message?.channel !== 'gzk-low-altitude') return
  if (message.type === 'ready') sendRoute()
  if (message.type === 'resize' && Number.isFinite(message.height)) height.value = Math.max(320, Math.min(18000, message.height))
  if (message.type === 'navigate' && ['overview', ...Object.keys(labels)].includes(message.page)) {
    const target = { path: '/' + message.page, query: { ...message.query, ...(message.page === 'overview' ? {} : { domain: 'lowalt' }) } }
    if (router.resolve(target).fullPath === route.fullPath) return
    if (route.path === target.path) router.replace(target)
    else router.push(target)
  }
}
watch(() => [props.page, route.fullPath], sendRoute)
onMounted(() => window.addEventListener('message', receive))
onBeforeUnmount(() => window.removeEventListener('message', receive))
</script>
<style scoped>
.low-altitude-frame { display: block; width: 100%; border: 0; background: transparent; min-height: 320px; opacity: 0; transition: opacity .45s ease; }
.low-altitude-frame.ready { opacity: 1; }
@media (prefers-reduced-motion: reduce) { .low-altitude-frame { transition: none; opacity: 1; } }
</style>
