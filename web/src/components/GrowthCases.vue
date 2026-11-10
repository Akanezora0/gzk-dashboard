<script setup>
/* 06 全部案例 · 成长案例：参与他人项目后担任负责人的全部记录 */
import {computed,ref,watch} from 'vue'
import {fmt,TYPE_SHORT,TYPE_COLOR} from '../helpers/strengthTip.js'
import {useMemberGrowth} from '../helpers/memberGrowth.js'
const {data,error}=useMemberGrowth()
const query=ref(''),later=ref('全部'),page=ref(0),open=ref('')
const PAGE=15,GROUPS=['全部','青年','地区','面上','重点等']
const rows=computed(()=>{const q=query.value.trim();return (data.value?.cases||[]).filter(c=>(later.value==='全部'||c.later_group===later.value)&&(!q||[c.person_name,c.later_inst,c.early_inst,c.later_title,c.early_title].some(v=>String(v||'').includes(q))))})
const pages=computed(()=>Math.max(1,Math.ceil(rows.value.length/PAGE)))
const visible=computed(()=>rows.value.slice(page.value*PAGE,(page.value+1)*PAGE))
watch([query,later],()=>{page.value=0;open.value=''})
const count=g=>g==='全部'?(data.value?.cases||[]).length:(data.value?.cases||[]).filter(c=>c.later_group===g).length
const label=g=>g==='全部'?'全部':g==='重点等'?'联合·重大等':TYPE_SHORT[g]+'项目'
const fg=g=>g==='青年'?'#7a0a1c':'#fff'
</script>
<template><div class="gc">
 <div v-if="error" class="rs-empty">{{error}}</div>
 <div v-else-if="!data" class="rs-empty">正在读取成长案例…</div>
 <template v-else>
  <div class="gc-bar">
   <div class="gc-chips"><span>首次负责</span><button v-for="g in GROUPS" :key="g" class="rs-chip" :class="{on:later===g}" @click="later=g">{{label(g)}} {{fmt(count(g))}}</button></div>
   <input v-model="query" class="rs-ev-search" type="search" placeholder="搜索姓名、单位或项目" aria-label="搜索成长案例">
  </div>
  <div class="gc-head"><span>负责人</span><span>参与的项目</span><span></span><span>首次负责的项目</span><span>间隔</span></div>
  <div v-for="c in visible" :key="c.person_id" class="gc-row" :class="{on:open===c.person_id}">
   <button type="button" class="gc-line" :aria-expanded="open===c.person_id" @click="open=open===c.person_id?'':c.person_id">
    <span class="who"><b>{{c.person_name||'—'}}</b><small>{{c.later_inst}}</small></span>
    <span class="proj"><em class="part">{{c.early_year}} · 参与</em><span>{{c.early_title}}</span></span>
    <i aria-hidden="true">→</i>
    <span class="proj"><em :style="{background:TYPE_COLOR[c.later_group],color:fg(c.later_group)}">{{c.later_year}} · {{TYPE_SHORT[c.later_group]}}</em><span>{{c.later_title}}</span></span>
    <span class="gap">{{c.gap}} 年</span>
   </button>
   <div v-if="open===c.person_id" class="gc-detail">
    <div><small>参与项目</small><b>{{c.early_title}}</b><p>{{c.early_type}} · 批准号 {{c.early_grant}} · {{c.early_year}} 年批准<br>负责人 {{c.early_pi}} · {{c.early_inst}}</p></div>
    <div><small>首次负责项目</small><b>{{c.later_title}}</b><p>{{c.later_type}} · 批准号 {{c.later_grant}} · {{c.later_year}} 年批准{{c.later_amount?` · ${c.later_amount}${c.later_unit||''}`:''}}<br>{{c.later_inst}}{{c.early_inst===c.later_inst?' · 同一单位':''}}</p></div>
   </div>
  </div>
  <p v-if="!rows.length" class="rs-empty">没有符合条件的案例。</p>
  <nav v-if="pages>1" class="gc-pager" aria-label="翻页"><button class="rs-btn" :disabled="page===0" @click="page--">上一页</button><span>{{page+1}} / {{pages}} · 共 {{fmt(rows.length)}} 人</span><button class="rs-btn" :disabled="page>=pages-1" @click="page++">下一页</button></nav>
 </template>
</div></template>
<style scoped>
.gc-bar{display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:14px}
.gc-chips{display:flex;align-items:center;gap:8px;flex-wrap:wrap}.gc-chips>span{font-size:14px;color:var(--rs-muted);margin-right:4px}
.gc-head,.gc-line{display:grid;grid-template-columns:130px minmax(0,1fr) 20px minmax(0,1fr) 56px;gap:14px;align-items:center}
.gc-head{padding:8px 12px;font-size:13px;color:var(--rs-muted);border-bottom:1px solid var(--rs-line)}
.gc-row{border-bottom:1px solid #f1ede9}
.gc-line{width:100%;padding:10px 12px;background:none;border:0;text-align:left;font-family:inherit;cursor:pointer;border-radius:8px}
.gc-line:hover,.gc-row.on .gc-line{background:#f7f5f2}
.gc-line i{font-style:normal;color:#d9737f;text-align:center}
.who b{display:block;font-size:15.5px;color:var(--rs-ink)}.who small{display:block;font-size:12px;color:var(--rs-muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.proj{display:flex;align-items:center;gap:8px;min-width:0;font-size:14px;color:var(--rs-ink-2)}.proj>span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;min-width:0}
.proj em{flex:none;font-style:normal;font-size:12px;font-weight:700;border-radius:12px;padding:2px 9px}
em.part{background:#fff;color:#57534e;border:1px dashed #bfb6ae}
.gap{font-size:14px;font-weight:650;color:var(--rs-ink);text-align:right;font-variant-numeric:tabular-nums}
.gc-detail{display:grid;grid-template-columns:1fr 1fr;gap:18px;padding:6px 12px 16px 156px}
.gc-detail small{font-size:12px;color:var(--rs-muted)}.gc-detail b{display:block;margin:3px 0;font-size:15px;line-height:1.5;color:var(--rs-ink)}.gc-detail p{margin:0;font-size:13px;line-height:1.7;color:var(--rs-ink-2)}
.gc-pager{display:flex;justify-content:center;align-items:center;gap:16px;margin-top:16px;font-size:14px;color:var(--rs-muted)}
.gc-pager button:disabled{opacity:.4;cursor:default}
@media(max-width:900px){.gc-head{display:none}.gc-line{grid-template-columns:1fr;gap:6px}.gc-line i{display:none}.gap{text-align:left}.gc-detail{grid-template-columns:1fr;padding-left:12px}}
</style>
