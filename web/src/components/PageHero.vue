<script setup>
/* 各页面统一首屏：浅色卡片、引题、标题、说明、右侧关键数字与入口 */
defineProps({eyebrow:String,title:String,lead:String,stats:{type:Array,default:()=>[]},action:Object})
const emit=defineEmits(['action'])
</script>
<template>
<section class="page-hero" :class="{'has-tabs':$slots.tabs}">
  <div class="page-hero-art" aria-hidden="true"><svg viewBox="0 0 800 300" preserveAspectRatio="xMaxYMid slice"><path v-for="i in 16" :key="i" :d="`M ${-60+i*4} 330 C ${250+i*12} ${250-i*10}, ${470+i*9} ${30+i*9}, 860 ${-30+i*20}`"/></svg></div>
  <div class="page-hero-head">
    <div><p v-if="eyebrow" class="page-hero-eyebrow">{{eyebrow}}</p><h2 v-html="title"></h2><p v-if="lead" class="page-hero-lead">{{lead}}</p></div>
    <div class="page-hero-meta"><div v-for="s in stats" :key="s.label"><strong>{{s.value}}</strong><span>{{s.label}}</span></div><button v-if="action" type="button" class="page-hero-link" @click="emit('action')">{{action.label}} <span aria-hidden="true">→</span></button></div>
  </div>
  <slot name="tabs"/>
</section>
</template>
