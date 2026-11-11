<script setup>
/* 领域数据 · 企业／经济共用筛选：关键词、行业、地区、产业角色 */
import {computed} from 'vue'
import {countBy,roleName,ROLES} from '../../helpers/industryData'
const props=defineProps({companies:Array,modelValue:Object,caption:String})
const emit=defineEmits(['update:modelValue'])
const industries=computed(()=>countBy(props.companies||[],c=>c.industry))
const provinces=computed(()=>countBy(props.companies||[],c=>c.province))
const set=(k,v)=>emit('update:modelValue',{...props.modelValue,[k]:v})
const dirty=computed(()=>Object.values(props.modelValue).some(v=>v&&v!=='all'))
function reset(){emit('update:modelValue',{q:'',industry:'all',province:'all',role:'all'})}
</script>
<template>
 <section class="panel ind-filter" aria-label="筛选">
  <label class="ind-field grow"><span>关键词</span><input :value="modelValue.q" placeholder="输入企业名称" aria-label="按企业名称筛选" @input="set('q',$event.target.value)"/></label>
  <label class="ind-field"><span>行业门类</span><select :value="modelValue.industry" @change="set('industry',$event.target.value)"><option value="all">全部行业</option><option v-for="i in industries" :key="i.name" :value="i.name">{{i.name}}（{{i.count}}）</option></select></label>
  <label class="ind-field"><span>注册地区</span><select :value="modelValue.province" @change="set('province',$event.target.value)"><option value="all">全部地区</option><option v-for="i in provinces" :key="i.name" :value="i.name">{{i.name}}（{{i.count}}）</option></select></label>
  <label class="ind-field"><span>产业角色</span><select :value="modelValue.role" @change="set('role',$event.target.value)"><option value="all">全部角色</option><option v-for="r in ROLES" :key="r" :value="r">{{roleName(r)}}</option></select></label>
  <button class="text-button ind-reset" :disabled="!dirty" @click="reset">重置筛选</button>
  <p v-if="caption" class="ind-caption">{{caption}}</p>
 </section>
</template>
