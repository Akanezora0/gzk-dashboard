<script setup>
/* 论文作者：姓名 + 单位角标；有邮箱时显示信封角标，悬停显示联系邮箱 */
import {computed} from 'vue'
import {parseAuthors} from '../helpers/authors.js'
const props=defineProps({value:[String,Array],max:{type:Number,default:12}})
const list=computed(()=>{const r=parseAuthors(props.value);return r.some(a=>a.name.length>30)?null:r})
const shown=computed(()=>list.value?.slice(0,props.max)||[])
</script>
<template>
 <span v-if="!list" class="au-raw">{{Array.isArray(value)?value.join(' · '):value||'—'}}</span>
 <span v-else-if="!list.length">—</span>
 <span v-else class="au-list"><span v-for="(a,i) in shown" :key="i" class="au">{{a.name}}<sup v-if="a.aff||a.corr">{{a.aff}}{{a.corr?(a.aff?',':'')+'*':''}}</sup><a v-if="a.email" class="au-mail" :href="`mailto:${a.email}`" :data-email="a.email" :aria-label="`${a.name}的联系邮箱 ${a.email}`"><svg viewBox="0 0 16 12" aria-hidden="true"><rect x=".75" y=".75" width="14.5" height="10.5" rx="1.6" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M1.5 1.8 8 6.6l6.5-4.8" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/></svg></a><span v-if="i<shown.length-1" class="au-sep">,</span></span><span v-if="list.length>max" class="au-more">等 {{list.length}} 人</span></span>
</template>
<style scoped>
.au-list{display:inline;line-height:1.75}
.au{white-space:nowrap}
.au sup{font-size:10.5px;color:#8a8286;margin-left:1px;font-variant-numeric:tabular-nums}
.au-sep{margin-right:6px;color:#9a9296}
.au-mail{position:relative;display:inline-flex;vertical-align:super;margin-left:2px;width:12px;height:9px;color:#a21535;text-decoration:none}
.au-mail svg{width:12px;height:9px}
.au-mail::after{content:attr(data-email);position:absolute;left:50%;bottom:calc(100% + 6px);transform:translateX(-50%);padding:4px 8px;border-radius:4px;background:#2a2a2a;color:#fff;font-size:12px;line-height:1.4;white-space:nowrap;opacity:0;pointer-events:none;transition:opacity .15s;z-index:5}
.au-mail:hover::after,.au-mail:focus-visible::after{opacity:1}
.au-more{margin-left:4px;color:#8a8286;font-size:12.5px}
</style>
