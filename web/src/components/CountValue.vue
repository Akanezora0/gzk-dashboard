<script setup>
import {ref,watch,onMounted,onBeforeUnmount} from 'vue'
import {fmt} from '../shared'
const props=defineProps({value:{type:Number,default:0},formatter:{type:Function,default:fmt}})
const shown=ref(props.value)
let frame,media
function update(value){
  cancelAnimationFrame(frame)
  if(media?.matches){shown.value=value;return}
  const from=shown.value,start=performance.now()
  function tick(now){
    const t=Math.min(1,(now-start)/650)
    shown.value=Math.round(from+(value-from)*(1-(1-t)**3))
    if(t<1)frame=requestAnimationFrame(tick)
  }
  frame=requestAnimationFrame(tick)
}
function reduce(){if(media.matches){cancelAnimationFrame(frame);shown.value=props.value}}
onMounted(()=>{media=matchMedia('(prefers-reduced-motion: reduce)');media.addEventListener('change',reduce);shown.value=0;update(props.value)})
watch(()=>props.value,update)
onBeforeUnmount(()=>{cancelAnimationFrame(frame);media?.removeEventListener('change',reduce)})
</script>
<template><span class="count-value" :aria-label="formatter(value)"><span aria-hidden="true">{{formatter(shown)}}</span></span></template>
