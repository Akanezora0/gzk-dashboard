<script setup>
import {chartPresentation} from '../../../shared/chartPresentation.js'
import {ref,onMounted,onBeforeUnmount,watch,nextTick,inject} from 'vue'
import * as echarts from 'echarts/core'
import {BarChart,LineChart,PieChart,GraphChart} from 'echarts/charts'
import {GridComponent,TooltipComponent,LegendComponent,GraphicComponent,DataZoomComponent,ToolboxComponent} from 'echarts/components'
import {LabelLayout} from 'echarts/features'
import {CanvasRenderer} from 'echarts/renderers'

echarts.use([BarChart,LineChart,PieChart,GraphChart,GridComponent,TooltipComponent,LegendComponent,GraphicComponent,DataZoomComponent,ToolboxComponent,CanvasRenderer,LabelLayout])
const props=defineProps({
  option:Object,
  height:{type:[String,Number],default:320},
  label:{type:String,default:'可交互数据图表'},
})
const emit=defineEmits(['select'])
const el=ref(null)
const viewSettled=inject('viewSettled', ref(true))
let instance,observer,motion,resizeFrame,played=false

function draw(update=played, force=false){
  if(!instance||!props.option)return
  if(!force&&!viewSettled.value&&!motion?.matches)return
  const option=chartPresentation(props.option,update,motion?.matches)
  instance.setOption(option,{notMerge:true,lazyUpdate:false})
  played=true
}
function resize(){
  cancelAnimationFrame(resizeFrame)
  resizeFrame=requestAnimationFrame(()=>instance?.resize())
}
onMounted(()=>{
  motion=window.matchMedia('(prefers-reduced-motion: reduce)')
  motion.addEventListener('change',draw)
  instance=echarts.init(el.value)
  instance.on('click',p=>emit('select',p))
  const begin=()=>{if(!played)draw(false)}
  if(motion.matches||viewSettled.value)begin()
  else{
    const stop=watch(viewSettled,value=>{if(!value)return;stop();nextTick(begin)})
    setTimeout(()=>draw(false,true),560)
  }
  observer=new ResizeObserver(resize)
  observer.observe(el.value)
})
onBeforeUnmount(()=>{
  motion?.removeEventListener('change',draw)
  observer?.disconnect()
  cancelAnimationFrame(resizeFrame)
  instance?.dispose()
  instance=null
})
watch(()=>props.option,()=>nextTick(()=>draw(played)),{deep:true})
defineExpose({reset:()=>draw(),resize})
</script>
<template><div ref="el" class="echart" :style="{height:typeof height==='number'?height+'px':height}" role="img" :aria-label="label"></div></template>
