<script setup>
/* 长链条案例 · 政策案例：耀元交付的政策案例模块（policy-cases.*），由其自带脚本挂载交互；
   图表与下载文件在 snapshot/public/policy-cases/ */
import {ref,onMounted,onBeforeUnmount} from 'vue'
import markup from './policy-cases.html?raw'
import './policy-cases.css'
import './policy-cases-host.css'
import './policy-cases.js'
import data from './policy-case-data.json'
const host=ref(null),top=ref(0)
let controller
function measure(){top.value=document.querySelector('.site-bar')?.offsetHeight||0}
onMounted(()=>{
 measure();window.addEventListener('resize',measure)
 controller=window.PolicyCases?.mount(host.value.querySelector('.policy-case-app'),{data,assetBase:'/policy-cases/'})
})
onBeforeUnmount(()=>{window.removeEventListener('resize',measure);controller?.destroy()})
</script>
<template>
 <div ref="host" class="policy-case-host" :style="{'--pc-sticky-top':top+'px'}" v-html="markup"></div>
</template>
