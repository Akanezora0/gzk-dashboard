<script setup>
import {computed,ref,onMounted,onBeforeUnmount,nextTick} from 'vue'
import TechNodeDetail from './TechNodeDetail.vue'
const props=defineProps({tree:Object,chronology:Object,entries:Array})
const emit=defineEmits(['survey'])

/* 里程碑条目：[事件 id, 显示名, 一句话说明] */
const picks=[
 ['transformer_2017','Transformer','注意力成为通用架构'],
 ['gpt_2018','GPT','生成式预训练'],['bert_2018','BERT','双向预训练'],
 ['chronology_AI2.15','Transformer-XL','突破固定上下文长度'],['chronology_AI3.07','DistilBERT','模型蒸馏压缩'],
 ['scaling_2020','规模规律','规模与性能的规律'],['chronology_AI2.12','GPT-3','上下文学习'],['rag_2020','RAG','检索增强生成'],['chronology_AI1.09','DDPM','扩散模型'],
 ['lora_2021','LoRA','低成本高效适配'],['chronology_AI2.03','FLAN','指令微调'],['switch_2021','Switch Transformer','稀疏专家模型'],['chronology_AI5.08','Codex','代码生成'],
 ['instructgpt_2022','InstructGPT','人类反馈强化学习'],['cot_2022','思维链 CoT','逐步推理提示'],['flashattention_2022','FlashAttention','高效注意力'],['react_2022','ReAct','推理与行动智能体'],
 ['llava_2023','LLaVA','视觉语言模型'],['dpo_2023','DPO','直接偏好优化'],['chronology_AI3.06','vLLM','分页注意力推理服务'],['chronology_AI5.04','Toolformer','工具调用'],
 ['deepseekmoe_2024','DeepSeekMoE','精细化专家架构'],['chronology_AI2.14','测试时计算扩展','推理阶段扩展计算'],
 ['deepseekr1_2025','DeepSeek-R1','强化学习驱动推理'],
]
const byId=computed(()=>new Map((props.chronology?.events||[]).map(e=>[e.id,e])))
const items=computed(()=>picks.map(([id,name,note])=>({ev:byId.value.get(id),name,note})).filter(i=>i.ev).sort((a,b)=>String(a.ev.first_public_date||a.ev.year).localeCompare(String(b.ev.first_public_date||b.ev.year))))
const entry=ev=>props.entries?.find(e=>e.topic_id===ev.topic_id&&e.route==='B')

/* 渐变：人大红 → 紫 → 蓝 */
const stops=[[0,[162,21,53]],[.5,[111,74,148]],[1,[44,100,160]]]
function tone(t){t=Math.max(0,Math.min(1,t));const [a,b]=t>.5?[stops[1],stops[2]]:[stops[0],stops[1]];const u=(t-a[0])/(b[0]-a[0]);return 'rgb('+a[1].map((v,i)=>Math.round(v+(b[1][i]-v)*u)).join(',')+')'}

/* 布局：主线为连续年份轴（等距），技术点按发布日期落在所属年份区间内；
   标签等距分槽、上下与远近交替，引线从时间点折向标签，避免文字重叠 */
const wrap=ref(null),stageW=ref(1180)
const W=computed(()=>Math.max(1080,stageW.value))
const AY=272,NEAR=66,FAR=172
const layout=computed(()=>{
 const list=items.value,w=W.value;if(!list.length)return {years:[],pts:[],ax0:0,ax1:0}
 const years=[...new Set(list.map(i=>i.ev.year))].sort((a,b)=>a-b)
 const first=years[0],last=years.at(-1),span=last-first+1
 const ax0=34,ax1=w-44,yw=(ax1-ax0)/span
 const yearX=y=>ax0+(y-first)*yw
 const lx0=70,lx1=w-74,slot=list.length>1?(lx1-lx0)/(list.length-1):0
 const pts=list.map((it,i)=>{
  const same=list.filter(o=>o.ev.year===it.ev.year),j=same.indexOf(it)
  const tx=yearX(it.ev.year)+32+(j+.5)/same.length*(yw-60)
  const dir=i%2?1:-1,far=Math.floor(i/2)%2===1,len=far?FAR:NEAR
  const lx=lx0+i*slot,end=AY+dir*len,c=tone((tx-ax0)/(ax1-ax0))
  const path=`M ${tx} ${AY} V ${AY+dir*12} C ${tx} ${AY+dir*30}, ${lx} ${AY+dir*22}, ${lx} ${AY+dir*42} V ${end}`
  return {...it,i,tx,lx,end,dir,c,path}
 })
 const marks=[];for(let y=first;y<=last;y++)marks.push({year:y,x:yearX(y),c:tone((yearX(y)-ax0)/(ax1-ax0))})
 return {years:marks,pts,ax0,ax1,yw}
})

/* 详情卡片 */
const selected=ref(null)
function choose(p){selected.value=selected.value?.ev.id===p.ev.id?null:p}
function close(restore=false){const id=selected.value?.ev.id;selected.value=null;if(restore&&id)nextTick(()=>document.getElementById('ms-'+id)?.focus({preventScroll:true}))}
function onOutside(e){if(!selected.value||document.querySelector('.survey-overlay'))return;const t=e.target instanceof Element?e.target:null;if(t?.closest('.tree-node-detail')||t?.closest('.ms-name'))return;close()}
function onKey(e){if(e.key==='Escape'&&selected.value&&!document.querySelector('.survey-overlay'))close(true)}
let ro
onMounted(()=>{document.addEventListener('pointerdown',onOutside,true);document.addEventListener('keydown',onKey);ro=new ResizeObserver(()=>{if(wrap.value)stageW.value=wrap.value.clientWidth});wrap.value&&ro.observe(wrap.value);stageW.value=wrap.value?.clientWidth||1180})
onBeforeUnmount(()=>{document.removeEventListener('pointerdown',onOutside,true);document.removeEventListener('keydown',onKey);ro?.disconnect()})
</script>

<template><div class="ms">
 <div ref="wrap" class="ms-scroll">
  <div class="ms-stage" :style="{width:W+'px',height:AY*2+'px'}">
   <svg :width="W" :height="AY*2" aria-hidden="true">
    <defs><linearGradient id="ms-grad" x1="0" x2="1"><stop offset="0" stop-color="rgb(162,21,53)"/><stop offset=".5" stop-color="rgb(111,74,148)"/><stop offset="1" stop-color="rgb(44,100,160)"/></linearGradient></defs>
    <line :x1="layout.ax0-14" :x2="W-18" :y1="AY" :y2="AY" stroke="url(#ms-grad)" stroke-width="3" stroke-linecap="round"/>
    <path :d="`M${W-30},${AY-6} L${W-17},${AY} L${W-30},${AY+6}`" fill="none" stroke="rgb(44,100,160)" stroke-width="3" stroke-linejoin="round"/>
    <g v-for="y in layout.years" :key="'t'+y.year"><line :x1="y.x" :x2="y.x" :y1="AY-5" :y2="AY+5" :stroke="y.c" stroke-width="2"/></g>
    <g v-for="p in layout.pts" :key="'s'+p.ev.id" :class="{dim:selected&&selected.ev.id!==p.ev.id}" class="ms-stem">
     <path :d="p.path" fill="none" :stroke="p.c" stroke-width="1.6" opacity=".7"/>
     <circle :cx="p.tx" :cy="AY" r="4.5" fill="#fff" :stroke="p.c" stroke-width="2.4"/>
     <circle :cx="p.lx" :cy="p.end" r="3.5" :fill="p.c"/>
    </g>
   </svg>
   <span v-for="y in layout.years" :key="'y'+y.year" class="ms-year" :style="{left:y.x+'px',top:AY+'px',background:y.c}">{{y.year}}</span>
   <article v-for="p in layout.pts" :key="p.ev.id" class="ms-item" :class="[p.dir<0?'up':'down',{on:selected?.ev.id===p.ev.id,dim:selected&&selected.ev.id!==p.ev.id}]" :style="{left:p.lx+'px',top:(p.dir<0?p.end-8:p.end+8)+'px','--c':p.c}">
    <button :id="'ms-'+p.ev.id" class="ms-name" :aria-expanded="selected?.ev.id===p.ev.id" @click="choose(p)"><b>{{p.name}}</b><small>{{p.note}}</small></button>
    <button v-if="entry(p.ev)?.ready_for_dashboard" class="ms-survey" @click="emit('survey',p.ev.topic_id)">阅读综述 ↗</button>
   </article>
  </div>
 </div>
 <TechNodeDetail v-if="selected" :point="selected.ev" :tone="selected.c" :tree="tree" :chronology="chronology" :entries="entries" @close="close" @survey="id=>emit('survey',id)"/>
</div></template>
