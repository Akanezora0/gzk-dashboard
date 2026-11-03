<template>
  <div class="chain-evidence">
    <ChainFlowVisual
      :contrib="contrib"
      :progress="progress"
      :chain-status="chainStatus"
    />
  </div>
</template>

<script setup>
import ChainFlowVisual from './ChainFlowVisual.vue'

defineProps({
  contrib: { type: Object, default: () => ({}) },
  progress: { type: Object, default: () => ({}) },
  chainStatus: { type: Array, default: () => [] },
})
</script>
