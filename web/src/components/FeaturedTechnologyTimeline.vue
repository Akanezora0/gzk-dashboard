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
 ['lora_2021','LoRA','低成本高效适配'],['switch_2021','Switch Transformer','稀疏专家模型'],
 ['instructgpt_2022','InstructGPT','人类反馈强化学习'],['cot_2022','思维链 CoT','逐步推理提示'],['flashattention_2022','FlashAttention','高效注意力'],['react_2022','ReAct','推理与行动智能体'],
 ['llava_2023','LLaVA','视觉语言模型'],['dpo_2023','DPO','直接偏好优化'],['chronology_AI3.06','vLLM','分页注意力推理服务'],['chronology_AI5.04','Toolformer','工具调用'],
 ['deepseekmoe_2024','DeepSeekMoE','精细化专家架构'],
 ['deepseekr1_2025','DeepSeek-R1','强化学习驱动推理'],
]
const byId=computed(()=>new Map((props.chronology?.events||[]).map(e=>[e.id,e])))
const items=computed(()=>picks.map(([id,name,note])=>({ev:byId.value.get(id),name,note})).filter(i=>i.ev).sort((a,b)=>String(a.ev.first_public_date||a.ev.year).localeCompare(String(b.ev.first_public_date||b.ev.year))))
const entry=ev=>props.entries?.find(e=>e.topic_id===ev.topic_id&&e.route==='B')

/* 配色：约每两年一种主色（红 → 金 → 青 → 蓝 → 紫），相邻主色之间平滑过渡 */
const palette=[[2017,[162,21,53]],[2019,[178,119,42]],[2021,[35,128,110]],[2023,[44,100,160]],[2025,[111,74,148]]]
function tone(fy){
 if(fy<=palette[0][0]+.5)return 'rgb('+palette[0][1]+')'
 if(fy>=palette.at(-1)[0]+.5)return 'rgb('+palette.at(-1)[1]+')'
 let k=0;while(fy>palette[k+1][0]+.5)k++
 const a=palette[k],b=palette[k+1],u=(fy-a[0]-.5)/(b[0]-a[0])
 return 'rgb('+a[1].map((v,i)=>Math.round(v+(b[1][i]-v)*u)).join(',')+')'
}

/* 布局：主线为等距连续年份轴，技术点按发布日期落在所属年份区间；
   卡片尽量贴近时间点、上下与远近交替，直角引线分层避免交叉 */
const wrap=ref(null),stageW=ref(1180)
const W=computed(()=>Math.max(1080,stageW.value))
const AY=270,NEAR=62,FAR=172,CARD=128
const layout=computed(()=>{
 const list=items.value,w=W.value;if(!list.length)return {years:[],pts:[],ax0:0,ax1:0,stops:[]}
 const years=[...new Set(list.map(i=>i.ev.year))].sort((a,b)=>a-b)
 const first=years[0],last=years.at(-1),span=last-first+1
 const ax0=34,ax1=w-50,yw=(ax1-ax0)/span
 const yearX=y=>ax0+(y-first)*yw,fyOf=x=>first+(x-ax0)/yw
 const pts=list.map((it,i)=>{const same=list.filter(o=>o.ev.year===it.ev.year),j=same.indexOf(it);return {...it,i,tx:yearX(it.ev.year)+36+(j+.5)/same.length*(yw-68),dir:i%2?1:-1,far:Math.floor(i/2)%2===1}})
 const lx=pts.map(p=>p.tx),lo=CARD/2+8,hi=w-CARD/2-14,cons=[]
 pts.forEach((p,i)=>{if(i>=2)cons.push([i-2,i,CARD/2+10]);if(i>=4)cons.push([i-4,i,CARD+14])})
 for(let it=0;it<300;it++){for(const [a,b,g] of cons){const d=lx[b]-lx[a];if(d<g){const m=(g-d)/2;lx[a]-=m;lx[b]+=m}}for(let i=0;i<lx.length;i++)lx[i]=Math.min(hi,Math.max(lo,lx[i]))}
 pts.forEach((p,i)=>{p.lx=lx[i]})
 pts.forEach(p=>{
  const side=pts.filter(q=>q.dir===p.dir&&q!==p)
  const rank=p.lx>=p.tx?side.filter(q=>q.i>p.i&&q.tx<p.lx).length:side.filter(q=>q.i<p.i&&q.tx>p.lx).length
  p.end=AY+p.dir*(p.far?FAR:NEAR);p.c=tone(fyOf(p.tx))
  p.path=`M ${p.tx} ${AY} V ${AY+p.dir*(14+rank*8)} H ${p.lx} V ${p.end}`
 })
 const marks=years.length?Array.from({length:span},(_,k)=>({year:first+k,x:yearX(first+k),c:tone(first+k)})):[]
 const stops=Array.from({length:21},(_,t)=>({o:t/20,c:tone(fyOf(ax0+(ax1-ax0)*t/20))}))
 return {years:marks,pts,ax0,ax1,stops,end:tone(last+1)}
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
  <div class="ms-stage" :style="{width:W+'px',height:AY*2+28+'px'}">
   <svg :width="W" :height="AY*2" aria-hidden="true">
    <defs><linearGradient id="ms-grad" gradientUnits="userSpaceOnUse" :x1="layout.ax0" :x2="layout.ax1"><stop v-for="s in layout.stops" :key="s.o" :offset="s.o" :stop-color="s.c"/></linearGradient></defs>
    <rect :x="layout.ax0-14" :y="AY-4" :width="W-layout.ax0-14" height="8" rx="4" fill="url(#ms-grad)"/>
    <path :d="`M${W-30},${AY-11} L${W-13},${AY} L${W-30},${AY+11}Z`" :fill="layout.end"/>
    <g v-for="p in layout.pts" :key="'s'+p.ev.id" :class="{dim:selected&&selected.ev.id!==p.ev.id}" class="ms-stem">
     <path :d="p.path" fill="none" :stroke="p.c" stroke-width="1.6"/>
     <circle :cx="p.tx" :cy="AY" r="4.5" fill="#fff" :stroke="p.c" stroke-width="2.4"/>
    </g>
   </svg>
   <span v-for="y in layout.years" :key="'y'+y.year" class="ms-year" :style="{left:y.x+'px',top:AY+'px','--c':y.c}">{{y.year}}</span>
   <article v-for="p in layout.pts" :key="p.ev.id" class="ms-item" :class="[p.dir<0?'up':'down',{on:selected?.ev.id===p.ev.id,dim:selected&&selected.ev.id!==p.ev.id}]" :style="{left:p.lx+'px',top:p.end+'px','--c':p.c}">
    <button :id="'ms-'+p.ev.id" class="ms-name" :aria-expanded="selected?.ev.id===p.ev.id" @click="choose(p)"><b>{{p.name}}</b><small>{{p.note}}</small></button>
    <button v-if="entry(p.ev)?.ready_for_dashboard" class="ms-survey" @click="emit('survey',p.ev.topic_id)">阅读综述 ↗</button>
   </article>
  </div>
 </div>
 <TechNodeDetail v-if="selected" :point="selected.ev" :tone="selected.c" :tree="tree" :chronology="chronology" :entries="entries" @close="close" @survey="id=>emit('survey',id)"/>
</div></template>
