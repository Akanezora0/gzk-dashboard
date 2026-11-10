<script setup>
import {computed,ref} from 'vue'
import {safeUrl} from '../shared'
const props=defineProps({point:Object,tree:Object,chronology:Object,entries:Array,tone:String,story:Object})
const emit=defineEmits(['close','survey'])
const root=ref(null)
defineExpose({root})
const events=computed(()=>new Map((props.chronology?.events||[]).map(e=>[e.id,e])))
const relations=computed(()=>(props.chronology?.edges||[]).filter(e=>e.source===props.point?.id||e.target===props.point?.id).map(e=>({...e,from:events.value.get(e.source),to:events.value.get(e.target)})).filter(e=>e.from&&e.to))
const entry=computed(()=>props.entries?.find(e=>e.topic_id===props.point?.topic_id&&e.route==='B'))
const topic=computed(()=>props.tree?.nodes.find(n=>n.id===props.point?.topic_id))
const categoryLabel=computed(()=>props.tree?.nodes.find(n=>n.id===props.point?.category_id)?.label||props.point?.category_id)
</script>
<template><aside ref="root" class="tree-node-detail" :style="{'--branch-color':tone}" aria-label="技术节点详情"><div class="tree-detail-top"><span>{{categoryLabel}}</span><button aria-label="收起节点详情" @click="emit('close',true)">×</button></div><p class="tree-detail-year">{{point.year}}<small>{{topic?.level2}}</small></p><h3>{{point.topic_label}}</h3><dl v-if="story" class="tree-story"><dt>关键创新</dt><dd>{{story.innovation}}</dd><dt>带来的影响</dt><dd>{{story.impact}}</dd></dl><p v-else class="tree-definition">{{topic?.source?.cells?.C||topic?.definition}}</p><button class="tree-survey-open" :disabled="!entry?.ready_for_dashboard" @click="emit('survey',point.topic_id)"><span>{{entry?.ready_for_dashboard?'阅读技术综述':'综述整理中'}}</span><small v-if="entry?.ready_for_dashboard">{{entry.actual_references}} 篇引用文献 ↗</small></button><a class="tree-source-paper" :href="safeUrl(point.url)" target="_blank" rel="noopener"><span>代表成果 ↗</span><b>{{point.title}}</b></a><p v-if="point.authors?.length" class="tree-people">{{point.authors.join(' · ')}}</p><p v-if="point.institutions?.length" class="tree-people">{{point.institutions.join(' · ')}}</p><div v-if="relations.length" class="tree-relation-list"><h4>相关技术联系</h4><a v-for="e in relations" :key="e.id" :href="safeUrl(e.source_url)" target="_blank" rel="noopener"><b>{{e.from.topic_label}} · {{e.to.topic_label}}</b><span>{{e.label}} ↗</span></a></div></aside></template>
