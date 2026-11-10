<script setup>
/* 产业链案例详情：核心链条 → 主体与数据 → 应用与经营 → 案例资料 */
import {computed,ref} from 'vue'
import {marked} from 'marked'
import {safeUrl} from '../../shared'
const props=defineProps({caseId:String,detail:Object,source:String})
const sections=[['chain','核心链条'],['data','主体与数据'],['application','应用与经营'],['evidence','案例资料']]
function go(id){document.getElementById(`icd-${props.caseId}-${id}`)?.scrollIntoView({behavior:'smooth',block:'start'})}
const name=computed(()=>props.detail.title.split('·')[0].trim())
const showSource=ref(false)
const sourceHtml=computed(()=>{if(!showSource.value||!props.source)return '';const doc=new DOMParser().parseFromString(marked.parse(props.source.replace(/</g,'&lt;'),{gfm:true}),'text/html');doc.querySelectorAll('a').forEach(a=>{a.href=safeUrl(a.getAttribute('href'));a.target='_blank';a.rel='noopener noreferrer'});return doc.body.innerHTML})
const fileName=computed(()=>props.detail.source||`${props.caseId}.md`)
function download(){const url=URL.createObjectURL(new Blob([props.source||''],{type:'text/markdown;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=fileName.value;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
</script>

<template><div class="icd">
 <header class="icd-top">
  <div class="icd-id"><span class="icd-logo" aria-hidden="true">{{name.slice(0,1)}}</span><div><p class="icd-kicker">{{detail.caseNo}} · {{detail.eyebrow}}</p><h3>{{detail.title}}</h3><p class="icd-entity">{{detail.entity.join(' · ')}}</p></div></div>
  <nav class="icd-nav" aria-label="案例章节"><button v-for="([id,l],i) in sections" :key="id" type="button" @click="go(id)"><i>{{String(i+1).padStart(2,'0')}}</i>{{l}}</button></nav>
 </header>
 <p class="icd-lead">{{detail.lead}}</p>

 <section :id="`icd-${caseId}-chain`" class="icd-sec">
  <header class="icd-sh"><span>01</span><h4>核心链条</h4><small>{{detail.chainTitle}}</small></header>
  <ol class="icd-route"><li v-for="r in detail.route" :key="r.k"><em>{{r.k}}</em><b>{{r.h}}</b><p>{{r.p}}</p></li></ol>
 </section>

 <section :id="`icd-${caseId}-data`" class="icd-sec">
  <header class="icd-sh"><span>02</span><h4>主体与数据</h4><small>统计范围</small></header>
  <div class="icd-stats"><div v-for="s in detail.stats" :key="s.l"><strong>{{s.v}}</strong><span>{{s.l}}</span></div></div>
  <dl class="icd-profile"><div v-for="f in detail.profile" :key="f.k"><dt>{{f.k}}</dt><dd>{{f.v}}</dd></div></dl>
 </section>

 <section :id="`icd-${caseId}-application`" class="icd-sec">
  <header class="icd-sh"><span>03</span><h4>应用与经营</h4><small>已有观察</small></header>
  <div class="icd-obs"><article v-for="o in detail.observations" :key="o.h"><h5>{{o.h}}</h5><p>{{o.p}}</p></article></div>
  <div v-if="detail.table" class="icd-table"><table><thead><tr><th v-for="h in detail.table.head" :key="h">{{h}}</th></tr></thead><tbody><tr v-for="r in detail.table.rows" :key="r[0]"><td v-for="(c,i) in r" :key="i">{{c}}</td></tr></tbody></table></div>
 </section>

 <section :id="`icd-${caseId}-evidence`" class="icd-sec">
  <header class="icd-sh"><span>04</span><h4>案例资料</h4><small>来源材料与原文链接</small></header>
  <div v-if="detail.evidence.length" class="icd-obs"><article v-for="e in detail.evidence" :key="e.h"><h5>{{e.h}}</h5><p>{{e.p}}</p><p class="icd-links"><a v-for="l in e.links" :key="l.u" :href="safeUrl(l.u)" target="_blank" rel="noopener noreferrer">{{l.t}} ↗</a></p></article></div>
  <div class="icd-source">
   <button type="button" class="icd-toggle" :aria-expanded="showSource" @click="showSource=!showSource">{{showSource?'收起案例材料':'展开案例材料'}}</button>
   <button type="button" class="icd-toggle ghost" @click="download">下载来源 Markdown</button>
  </div>
  <article v-if="showSource" class="icd-md" v-html="sourceHtml"></article>
 </section>
</div></template>

<style scoped>
.icd{display:flex;flex-direction:column;gap:18px}
.icd-top{display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;padding:18px 22px;background:#fff;border:1px solid #e6dfdb;border-radius:4px}
.icd-id{display:flex;align-items:center;gap:14px;min-width:0}
.icd-logo{display:grid;place-items:center;flex:none;width:46px;height:46px;border-radius:4px;background:#a21535;color:#fff;font-size:20px;font-weight:800}
.icd-kicker{margin:0;font-size:12px;letter-spacing:.5px;color:#a21535;font-weight:650}
.icd-id h3{margin:2px 0;font-size:22px;font-weight:750;color:#232930}
.icd-entity{margin:0;font-size:12.5px;color:#8a8286}
.icd-nav{display:flex;gap:4px;padding:4px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9;flex-wrap:wrap}
.icd-nav button{display:inline-flex;align-items:baseline;gap:6px;padding:7px 12px;border:0;border-radius:3px;background:none;font:inherit;font-size:13.5px;font-weight:600;color:#6a6468;cursor:pointer;white-space:nowrap}
.icd-nav button:hover{background:#a21535;color:#fff}.icd-nav button:hover i{color:#f2c4cc}
.icd-nav i{font-style:normal;font-size:11px;color:#b0a6a9}
.icd-lead{margin:0;padding:0 4px;font-size:16px;color:#4d474b}
.icd-sec{padding:24px 26px 26px;background:#fff;border:1px solid #e6dfdb;border-radius:4px;scroll-margin-top:96px}
.icd-sh{display:flex;align-items:baseline;gap:12px;margin-bottom:18px;flex-wrap:wrap}
.icd-sh span{font-size:24px;font-weight:300;color:#a21535;font-variant-numeric:tabular-nums}
.icd-sh h4{margin:0;font-size:20px;font-weight:750;color:#232930}
.icd-sh small{font-size:13.5px;color:#8a8286}
.icd-route{display:grid;grid-template-columns:repeat(4,1fr);gap:28px;margin:0;padding:0;list-style:none;counter-reset:r}
.icd-route li{position:relative;padding:16px 18px;border:1px solid #ece5e1;border-top:3px solid #a21535;border-radius:4px;background:#fcfaf9}
.icd-route li:not(:last-child)::after{content:"→";position:absolute;right:-22px;top:50%;transform:translateY(-50%);color:#c9a0ab;font-size:16px}
.icd-route em{display:block;font-style:normal;font-size:12px;font-weight:650;color:#a21535}
.icd-route b{display:block;margin:6px 0;font-size:16px;font-weight:750;color:#232930;line-height:1.45}
.icd-route p{margin:0;font-size:13.5px;line-height:1.75;color:#6a6468}
.icd-stats{display:grid;grid-template-columns:repeat(3,1fr);border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.icd-stats>div{padding:16px 22px;border-left:1px solid #ece5e1}.icd-stats>div:first-child{border-left:0}
.icd-stats strong{display:block;font-size:28px;font-weight:800;color:#a21535;font-variant-numeric:tabular-nums;line-height:1.3}
.icd-stats span{font-size:13px;color:#8a8286}
.icd-profile{display:grid;grid-template-columns:repeat(3,1fr);gap:0 28px;margin:16px 0 0}
.icd-profile>div{padding:12px 0;border-bottom:1px solid #f0eae7}
.icd-profile dt{font-size:12.5px;color:#8a8286}
.icd-profile dd{margin:3px 0 0;font-size:14.5px;font-weight:650;color:#3d3a3c}
.icd-obs{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.icd-obs article{padding:18px 20px;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9}
.icd-obs h5{margin:0 0 8px;font-size:16px;font-weight:750;color:#232930}
.icd-obs p{margin:0;font-size:13.5px;line-height:1.8;color:#5d575b}
.icd-links{margin-top:10px!important;display:flex;gap:6px 14px;flex-wrap:wrap}
.icd-links a{font-weight:650;color:#a21535;text-decoration:none}.icd-links a:hover{text-decoration:underline}
.icd-table{margin-top:18px;overflow-x:auto}
.icd-table table{width:100%;border-collapse:collapse;font-size:14px}
.icd-table th{padding:10px 14px;text-align:left;font-size:12.5px;font-weight:650;color:#8a8286;border-bottom:2px solid #e6dfdb}
.icd-table td{padding:11px 14px;border-bottom:1px solid #f0eae7;color:#3d3a3c;font-variant-numeric:tabular-nums}
.icd-table td:not(:first-child),.icd-table th:not(:first-child){text-align:right}
.icd-source{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}
.icd-toggle{padding:8px 16px;border:1px solid #a21535;border-radius:4px;background:#a21535;font:inherit;font-size:13.5px;font-weight:650;color:#fff;cursor:pointer}
.icd-toggle.ghost{background:#fff;color:#a21535}
.icd-md{margin-top:16px;padding:22px 26px;max-height:640px;overflow:auto;border:1px solid #ece5e1;border-radius:4px;background:#fcfaf9;font-size:14px;line-height:1.85;color:#3d3a3c}
.icd-md :deep(h1){font-size:19px;margin:0 0 12px}.icd-md :deep(h2){font-size:16.5px;margin:20px 0 8px;color:#a21535}.icd-md :deep(h3){font-size:15px;margin:16px 0 6px}
.icd-md :deep(table){border-collapse:collapse;margin:10px 0;font-size:13px;display:block;overflow-x:auto}
.icd-md :deep(th),.icd-md :deep(td){padding:6px 10px;border:1px solid #e6dfdb;text-align:left}
.icd-md :deep(blockquote){margin:10px 0;padding:6px 14px;border-left:3px solid #d9b3bd;color:#6a6468;background:#fff}
.icd-md :deep(code){font-size:12.5px;background:#f3eeec;padding:1px 4px;border-radius:3px}
@media(max-width:1100px){.icd-route{grid-template-columns:repeat(2,1fr)}.icd-route li:nth-child(2)::after{display:none}.icd-obs{grid-template-columns:1fr 1fr}}
@media(max-width:760px){.icd-top{padding:14px 16px}.icd-sec{padding:18px 16px}.icd-route,.icd-obs,.icd-profile{grid-template-columns:1fr}.icd-route li::after{display:none}.icd-stats{grid-template-columns:1fr}.icd-stats>div{border-left:0;border-top:1px solid #ece5e1}.icd-stats>div:first-child{border-top:0}.icd-md{padding:16px}}
</style>
