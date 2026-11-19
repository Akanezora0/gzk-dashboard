<script setup>
/* 政策案例图表卡：标题 + 图（点击放大）+ 简短图注 */
defineProps({src:String,title:String,caption:String})
defineEmits(['zoom'])
</script>
<template><figure class="pf">
 <header><b>{{title}}</b><button type="button" class="pf-zoom" :aria-label="`放大${title}`" @click="$emit('zoom',{src,title})">放大</button></header>
 <button type="button" class="pf-img" :aria-label="`放大${title}`" @click="$emit('zoom',{src,title})"><img :src="src" :alt="title" loading="lazy"></button>
 <figcaption v-if="caption">{{caption}}</figcaption>
</figure></template>
<style scoped>
.pf{margin:0;display:flex;flex-direction:column;padding:16px 18px;border:1px solid #ece5e1;border-radius:4px;background:#fff;transition:border-color .2s,box-shadow .3s}
.pf:hover{border-color:#e2c3ca;box-shadow:0 14px 30px -26px rgba(80,20,35,.55)}
.pf header{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-bottom:10px}
.pf header b{font-size:15px;font-weight:700;color:#232930}
.pf-zoom{flex:none;padding:4px 12px;border:1px solid #e6dfdb;border-radius:4px;background:#fff;font:inherit;font-size:12.5px;color:#6a6468;cursor:pointer;transition:color .18s,border-color .18s}
.pf-zoom:hover{color:#a21535;border-color:#a21535}
.pf-img{flex:1;display:flex;align-items:center;padding:0;border:0;background:none;cursor:zoom-in}
.pf-img img{display:block;width:100%;height:auto}
.pf figcaption{margin-top:10px;padding-top:10px;border-top:1px solid #f2ecea;font-size:12.5px;line-height:1.7;color:#8a8286}
</style>
