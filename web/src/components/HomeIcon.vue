<script setup>
import {homeIcons} from '../helpers/homeIcons'
defineProps({name:{type:String,required:true}})
</script>

<template>
  <svg class="home-icon" viewBox="0 0 24 24" aria-hidden="true">
    <path v-if="homeIcons[name].line" class="home-icon-line" :d="homeIcons[name].line"/>
    <path class="home-icon-fill" :d="homeIcons[name].fill" :mask="homeIcons[name].cut||homeIcons[name].cutFill?`url(#home-icon-cut-${name})`:null"/>
    <path v-if="homeIcons[name].over" class="home-icon-fill" :d="homeIcons[name].over"/>
  </svg>
</template>
