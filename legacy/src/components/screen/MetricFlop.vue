<template>
  <div class="metric-flop" @click="$emit('click')">
    <div class="metric-flop__chart">
      <dv-digital-flop :config="flopConfig" style="width:100%;height:42px" />
    </div>
    <div class="metric-flop__label">{{ label }}</div>
    <div v-if="en" class="metric-flop__en">{{ en }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: { type: [Number, String], required: true },
  label: { type: String, required: true },
  en: { type: String, default: '' },
  color: { type: String, default: '#ae0d28' },
  suffix: { type: String, default: '' },
})

defineEmits(['click'])

const flopConfig = computed(() => {
  const num = typeof props.value === 'number' ? props.value : parseFloat(String(props.value).replace(/[^0-9.]/g, '')) || 0
  return {
    number: [num],
    content: props.suffix ? `{nt}${props.suffix}` : '{nt}',
    toFixed: num >= 10000 ? 1 : 0,
    style: { fontSize: 28, fill: props.color, fontWeight: 700 },
    textAlign: 'center',
  }
})
</script>

<style scoped>
.metric-flop {
  text-align: center;
  padding: 10px 6px;
  cursor: pointer;
  border-radius: 10px;
  transition: background 0.2s, transform 0.15s, border-color 0.15s;
  background: var(--surface-card);
  border: 1px solid var(--border);
}
.metric-flop:hover {
  background: var(--ruc-red-muted);
  border-color: rgba(174, 13, 40, 0.25);
  transform: translateY(-2px);
}
.metric-flop__label {
  font-size: 0.8rem;
  color: var(--muted);
  font-weight: 600;
  margin-top: 4px;
}
.metric-flop__en {
  font-size: 0.68rem;
  color: #a8a29e;
  text-transform: uppercase;
  margin-top: 2px;
}
</style>
