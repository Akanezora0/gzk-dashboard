<script setup>
import {computed} from 'vue'
import {homeIcons} from '../helpers/homeIcons'
const props=defineProps({name:{type:String,required:true}})
let seq=0
const uid=`hi-${Math.random().toString(36).slice(2,8)}-${seq++}`
const g=computed(()=>homeIcons[props.name]||{})
const hasCut=computed(()=>!!(g.value.cut||g.value.cutFill))
</script>

<template>
  <svg class="home-icon" viewBox="0 0 24 24" aria-hidden="true">
    <defs v-if="hasCut">
      <mask :id="uid" maskUnits="userSpaceOnUse" x="0" y="0" width="24" height="24">
        <rect width="24" height="24" fill="#fff"/>
        <path v-if="g.cut" :d="g.cut" fill="none" stroke="#000" stroke-width="1.7" stroke-linecap="square"/>
        <path v-if="g.cutFill" :d="g.cutFill" fill="#000"/>
      </mask>
    </defs>
    <path v-if="g.line" class="home-icon-line" :d="g.line"/>
    <path class="home-icon-fill" :d="g.fill" :mask="hasCut?`url(#${uid})`:null"/>
    <path v-if="g.over" class="home-icon-fill" :d="g.over"/>
  </svg>
</template>
