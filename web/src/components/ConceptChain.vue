<script setup>
import {computed} from 'vue'
import {fmt,concise} from '../shared'
const props=defineProps({data:Object})
const metrics=computed(()=>props.data.study.contribution.source_metrics)
const sources=computed(()=>[
 {label:'基金项目',count:metrics.value.fund_projects,unit:'关联项目',tone:'#ab1839'},
 {label:'论文成果',count:null,unit:'中文题录 '+concise(props.data.domain.metrics.find(x=>x.namespace==='cnki_paper')?.ai_candidates)+' · 基金成果 '+concise(metrics.value.fund_papers),tone:'#367fa4'},
 {label:'专利成果',count:props.data.domain.metrics.find(x=>x.namespace==='legacy_patent')?.ai_candidates,unit:'领域候选记录',tone:'#328674'}])
const relations=computed(()=>[
 {label:'基金 → 论文',count:metrics.value.fund_paper_edges,note:'项目编号连接资助成果',unit:'资助关联',tone:'#ab1839'},
 {label:'论文 → 技术',count:metrics.value.paper_tech_edges,note:'题名与摘要识别研究方法',unit:'候选关联',tone:'#367fa4'},
 {label:'专利 → 技术',count:metrics.value.patent_tech_edges,note:'公开文本提取技术内容',unit:'候选关联',tone:'#328674'}])
</script>
<template><div class="concept-scroll"><div class="concept-chain" role="img" aria-label="基金论文专利成果，经资助和技术关联汇入70关键词，支撑技术演进与基金贡献研究，并衔接企业政策案例">
<div class="concept-headings"><span>多源成果</span><span>关系构建</span><span>共同技术词典</span><span>研究与应用</span></div>
<svg class="concept-connections" viewBox="0 0 1000 320" preserveAspectRatio="none" aria-hidden="true"><defs><marker id="concept-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10" fill="#a697ae"/></marker></defs><g fill="none" stroke-width="2" marker-end="url(#concept-arrow)"><path d="M175 53C220 53 225 53 272 53" stroke="#ba6578"/><path d="M175 160C215 160 225 53 272 53" stroke="#5a93b2"/><path d="M175 160L272 160" stroke="#5a93b2"/><path d="M175 267L272 267" stroke="#599f91"/><path d="M470 53C530 53 495 160 568 160" stroke="#ba6578"/><path d="M470 160L568 160" stroke="#5a93b2"/><path d="M470 267C530 267 495 160 568 160" stroke="#599f91"/><path d="M726 160C770 160 752 90 800 90" stroke="#a084b2"/><path d="M726 160C770 160 752 238 800 238" stroke="#b2a5ba" stroke-dasharray="5 5"/></g></svg>
<div class="concept-columns"><div class="concept-source-stack"><article v-for="s in sources" :key="s.label" :style="{'--concept-tone':s.tone}"><b>{{s.label}}</b><strong>{{s.count===null?'两类题录':concise(s.count)}}</strong><small>{{s.unit}}</small></article></div>
<div class="concept-relation-stack"><article v-for="r in relations" :key="r.label" :style="{'--concept-tone':r.tone}"><b>{{r.label}}</b><div><strong>{{fmt(r.count)}}</strong><small>{{r.unit}}</small></div><p>{{r.note}}</p></article></div>
<div class="concept-dictionary"><div><small>基础模型 · 算力 · 服务 · 应用</small><strong>{{data.tree.counts.topics}}<span>关键词</span></strong><b>{{data.tree.counts.categories}} 大类 · {{data.tree.counts.groups}} 技术组</b><p>在共同主题中汇聚成果</p></div></div>
<div class="concept-outcomes"><article><span>研究分析</span><h4>技术演进与基金贡献</h4><p>发展脉络 · 支撑范围<br/>学术影响 · 关系追溯</p></article><article class="planned"><span>案例衔接 · 筹备中</span><h4>企业、产品与政策</h4><p>代表应用 · 主体联系<br/>政策支持 · 产业研究</p></article></div></div></div></div></template>
