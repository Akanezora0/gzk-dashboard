<script setup>
import {computed} from 'vue'
import {projectTimeline} from '../helpers/projectTimeline.js'
import {typeGroup,TYPE_NAME,TYPE_COLOR} from '../helpers/strengthTip.js'
const props=defineProps({projects:{type:Array,default:()=>[]},papers:{type:Array,default:()=>[]}})
const timeline=computed(()=>projectTimeline(props.projects,props.papers))
</script>
<template>
 <div class="project-timeline" v-if="timeline.years.length">
  <svg :viewBox="`0 0 960 ${timeline.height}`" role="img" aria-label="项目批准、执行期与关联论文年度时间轴">
   <g v-for="(p,i) in timeline.rows" :key="p.project_id||p.grant_no">
    <text x="40" :y="18+i*54" font-size="14" fill="#57534e">{{TYPE_NAME[typeGroup(p.project_type)]}} · {{p.grant_no}}<tspan v-if="p.bar">　执行期 {{p.start}}—{{p.end}}</tspan><tspan v-else-if="p.approval">　{{p.approval}} 年批准</tspan></text>
    <line x1="40" x2="920" :y1="35+i*54" :y2="35+i*54" stroke="#f0ece8" stroke-width="2"/>
    <rect v-if="p.bar" :x="p.bar.x" :y="27+i*54" :width="p.bar.width" height="16" rx="8" :fill="TYPE_COLOR[typeGroup(p.project_type)]"/>
    <path v-if="p.approvalX!==null" :d="`M${p.approvalX},${26+i*54} l9,9 l-9,9 l-9,-9 Z`" fill="#ae0d28" stroke="#fff" stroke-width="2"/>
   </g>
   <rect x="40" :y="timeline.axisY" width="880" height="7" rx="3.5" fill="#57534e"/>
   <g v-for="p in timeline.paperCounts" :key="p.year"><circle :cx="p.x" :cy="timeline.axisY+3.5" r="9" fill="#2f5f7a" stroke="#fff" stroke-width="3"/><title>{{p.year}} 年：{{p.count}} 篇关联论文</title></g>
   <text v-for="y in timeline.years" :key="y.year" :x="y.x" :y="timeline.axisY+34" text-anchor="middle" font-size="13" fill="#78716c">{{y.year}}</text>
  </svg>
  <div class="timeline-legend"><span><i class="diamond"></i>批准年份</span><span><i class="period"></i>项目执行期</span><span v-if="timeline.paperCounts.length"><i class="paper"></i>关联论文发表年份</span></div>
 </div>
</template>
<style scoped>
.project-timeline{margin:18px 0 22px;min-width:0}.project-timeline svg{display:block;width:100%;height:auto}.timeline-legend{display:flex;flex-wrap:wrap;gap:16px;color:#78716c;font-size:12px;padding:0 4.2%}.timeline-legend span{display:inline-flex;align-items:center;gap:6px}.timeline-legend i{display:inline-block}.diamond{width:8px;height:8px;background:#ae0d28;transform:rotate(45deg)}.period{width:20px;height:7px;border-radius:4px;background:#f0b7bf}.paper{width:8px;height:8px;border-radius:50%;background:#2f5f7a}
@media(max-width:600px){.project-timeline{overflow-x:auto}.project-timeline svg{min-width:650px}}
</style>
