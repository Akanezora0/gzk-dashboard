<script setup>
import {computed} from 'vue'
import {featuredEventIds,treeColors} from '../technologyTreeLayout'
const props=defineProps({chronology:Object,entries:Array})
const emit=defineEmits(['select','survey'])
const labels={transformer_2017:'Transformer',gpt_2018:'GPT 生成式预训练',rag_2020:'RAG 检索增强',lora_2021:'LoRA 高效适配',instructgpt_2022:'RLHF 人类反馈',llava_2023:'多模态理解',deepseekmoe_2024:'DeepSeekMoE',deepseekr1_2025:'DeepSeek-R1'}
const notes={transformer_2017:'注意力成为通用架构',gpt_2018:'从预训练走向生成',rag_2020:'让生成连接外部知识',lora_2021:'降低模型适配成本',instructgpt_2022:'将人类偏好引入训练',llava_2023:'连接视觉与语言',deepseekmoe_2024:'探索稀疏专家架构',deepseekr1_2025:'强化学习与复杂推理'}
const events=computed(()=>featuredEventIds.map(id=>props.chronology?.events.find(e=>e.id===id)).filter(Boolean))
const entry=p=>props.entries?.find(e=>e.topic_id===p.topic_id&&e.route==='B')
</script>
<template><div class="featured-tech-track"><article v-for="p in events" :key="p.id" :style="{'--branch-color':treeColors[p.category_id]}" class="featured-tech-stop"><button class="featured-event" @click="emit('select',p)" :aria-label="'在技术树中定位 '+labels[p.id]"><strong>{{p.year}}</strong><i></i><h4>{{labels[p.id]}}</h4><p>{{notes[p.id]}}</p></button><button class="featured-survey" v-if="entry(p)?.ready_for_dashboard" @click="emit('survey',p.topic_id)">阅读综述 ↗</button><button v-else class="featured-survey" @click="emit('select',p)">查看技术节点 ↑</button></article></div></template>
