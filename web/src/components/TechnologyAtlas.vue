<script setup>
import {computed,ref} from 'vue'
const props=defineProps({tree:Object,selected:String,compact:Boolean})
const emit=defineEmits(['select'])
const active=ref('all')
const categories=computed(()=>props.tree.nodes.filter(n=>n.node_type==='category'))
const groups=computed(()=>props.tree.nodes.filter(n=>n.node_type==='technical_group'))
const topics=computed(()=>props.tree.nodes.filter(n=>n.node_type==='technology'))
const tones=['#a91638','#397ba2','#448d7a','#9574a9','#bc893b','#557b97','#b26880']
const showCategories=computed(()=>categories.value.filter(c=>active.value==='all'||c.id===active.value))
</script>
<template><div class="tech-atlas" :class="{compact}"><div class="atlas-toolbar"><div class="atlas-count"><strong>{{categories.length}}</strong> 大类 <i>／</i> <strong>{{groups.length}}</strong> 技术组 <i>／</i> <strong>{{topics.length}}</strong> 关键词</div><label>技术大类 <select v-model="active" aria-label="技术全景分类"><option value="all">全部</option><option v-for="c in categories" :key="c.id" :value="c.id">{{c.label}}</option></select></label></div><div class="atlas-lanes"><section v-for="c in showCategories" :key="c.id" class="atlas-lane" :style="{'--atlas-tone':tones[categories.indexOf(c)]}"><h4><span>{{String(categories.indexOf(c)+1).padStart(2,'0')}}</span>{{c.label}}</h4><div class="atlas-groups"><div v-for="(g,gi) in groups.filter(g=>g.parent_id===c.id)" :key="g.id" class="atlas-group" :style="{'--group-tint':(5+gi*4)+'%','--group-border':(16+gi*6)+'%'}"><span class="atlas-group-title" :title="g.label">{{g.label}}</span><div class="atlas-terms"><button v-for="t in topics.filter(t=>t.parent_id===g.id)" :key="t.id" :class="{active:selected===t.id}" :title="[t.label,...(t.aliases||[])].join(' · ')" @click="emit('select',t)">{{t.label}}</button></div></div></div></section></div></div></template>
