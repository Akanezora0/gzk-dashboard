<template><main ref="root" class="lowalt-embed"><router-view v-slot="{Component,route}"><component :is="Component" :key="route.path" class="lowalt-page"/></router-view></main></template>
<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
const root = ref(null)
let observer, frame, lastHeight = 0
function updateHeight() {
  cancelAnimationFrame(frame)
  frame = requestAnimationFrame(() => {
    const height = Math.ceil(root.value?.getBoundingClientRect().height || 0) + 2
    if (height === lastHeight) return
    lastHeight = height
    if (window.parent !== window) window.parent.postMessage({ channel: 'gzk-low-altitude', type: 'resize', height }, window.location.origin)
  })
}
onMounted(() => {
  observer = new ResizeObserver(updateHeight)
  observer.observe(root.value)
  window.addEventListener('resize', updateHeight)
  updateHeight()
})
onBeforeUnmount(() => {
  observer?.disconnect()
  cancelAnimationFrame(frame)
  window.removeEventListener('resize', updateHeight)
})
</script>
<style>
.lowalt-page{animation:lowalt-in .42s cubic-bezier(.22,.68,0,1) both}
@keyframes lowalt-in{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@media(prefers-reduced-motion:reduce){.lowalt-page{animation:none}}
</style>
