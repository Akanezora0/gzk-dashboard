<script setup>
import CountValue from '../../../../web/src/components/CountValue.vue'
defineProps({value:{type:[Number,String],default:0},label:String,en:String,color:{type:String,default:'#ae0d28'},suffix:{type:String,default:''}})
</script>
<template><div class="metric-flop"><strong class="metric-value" :style="{color}"><CountValue :value="Number(String(value).replace(/,/g,''))||0"/><small v-if="suffix">{{suffix}}</small></strong><div class="metric-flop__label">{{label}}</div><div v-if="en" class="metric-flop__en">{{en}}</div></div></template>
<style scoped>
.metric-flop{text-align:center;padding:16px 8px;border:1px solid #e6eaef;border-radius:12px;background:#fff}.metric-value{font-size:26px;line-height:1.25;font-weight:700;font-variant-numeric:tabular-nums}.metric-value small{font-size:12px;margin-left:3px}.metric-flop__label{font-size:13px;color:#7b8796;margin-top:4px}.metric-flop__en{font-size:11px;color:#a8a29e;margin-top:2px}
</style>
