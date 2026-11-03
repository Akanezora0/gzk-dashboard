<script setup>
import {computed,ref,watch} from 'vue'
import {useRoute} from 'vue-router'
import {fmt,sourceContent} from '../shared'
import {overviewSources,sourceDisplayUnit} from '../helpers/foundationSources'
import '../catalog.css'
const props=defineProps({data:Object,integrated:Boolean}),route=useRoute(),query=ref('')
const kind=ref(route.query.kind||'全部')
const rows=computed(()=>overviewSources(props.data.overview.datasets))
const types=computed(()=>[...new Set(rows.value.map(d=>d.kind))])
const filtered=computed(()=>rows.value.filter(d=>(kind.value==='全部'||d.kind===kind.value)&&[d.name,d.kind,d.scope,d.status].join(' ').toLowerCase().includes(query.value.toLowerCase())))
watch(()=>route.query.kind,value=>kind.value=types.value.includes(value)?value:'全部')
function domainLink(d){const m=props.data.domain.metrics.find(m=>m.namespace===d.id);return m?{path:'/data',query:{namespace:m.namespace,type:m.kind==='copyright'?'software':m.kind,domain:'ai'}}:null}
</script>
<template><div class="source-catalog" :class="{integrated}"><section id="sources" class="panel catalog-table-panel"><div class="panel-heading"><h3>数据资源明细 <span class="title-badge">{{rows.length}} 项</span></h3><router-link to="/data">查看领域数据 →</router-link></div><div class="catalog-filters"><div class="compact-tabs"><button v-for="t in ['全部',...types]" :key="t" :class="{active:kind===t}" @click="kind=t">{{t}}</button></div><input class="catalog-search" v-model="query" placeholder="检索数据资源、范围" aria-label="检索基座目录"/></div><div class="table-scroll"><table class="data-table"><thead><tr><th>数据资源</th><th>类别</th><th>库存数量</th><th>范围与状态</th><th>主要内容</th><th>领域分析</th></tr></thead><tbody><tr v-for="d in filtered" :key="d.id" :id="'source-'+d.id" class="catalog-source-row" :class="{selected:d.id===route.query.source}"><td class="catalog-source"><b :title="d.description">{{d.name}}</b></td><td>{{d.kind}}</td><td class="number-cell">{{fmt(d.count)}} <small>{{sourceDisplayUnit(d)}}</small></td><td>{{d.scope}}<small class="table-sub">{{d.status}}</small></td><td>{{d.description||sourceContent(d.id)}}</td><td><router-link v-if="domainLink(d)" :to="domainLink(d)" class="catalog-row-link">查看筛选 →</router-link><span v-else>—</span></td></tr></tbody></table></div><p v-if="!filtered.length" class="empty-state">没有符合条件的数据资源。</p></section></div></template>
