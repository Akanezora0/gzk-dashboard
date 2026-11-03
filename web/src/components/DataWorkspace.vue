<script setup>
import DomainHub from './DomainHub.vue'
import '../domain.css'
defineProps({data:Object})
</script>
<template><div class="data-workspace"><DomainHub :data="data"/></div></template>
