<script setup>
import {computed, onMounted, onBeforeUnmount, ref} from 'vue'

const dataset = ref(null), loadError = ref(false), mode = ref('index')
const root = ref(null), width = ref(1100)
const controller = new AbortController()
let observer
const themes = ['#b2607d', '#557b9a', '#3582a8', '#a51d42', '#318b79', '#9071ad', '#b58635']
const series = [
  {key: 'funding', name: '在研资助规模', color: '#a52245', dash: ''},
  {key: 'papers', name: '当年论文', color: '#347ea7', dash: '7 4'},
  {key: 'patents', name: '当年专利申请', color: '#b58a31', dash: '2 4'},
]
const format = value => new Intl.NumberFormat('zh-CN', {maximumFractionDigits: 1}).format(value)
function nice(value) {
  if (value <= 0) return 1
  const power = 10 ** Math.floor(Math.log10(value)), factor = value / power
  return (factor <= 1 ? 1 : factor <= 2 ? 2 : factor <= 5 ? 5 : 10) * power
}
const explanation = computed(() => mode.value === 'index'
  ? '各条曲线以自身九年峰值为100，比较变化节奏与峰值位置。'
  : '经费使用左侧纵轴，论文与专利数量使用右侧纵轴；各方向均采用年度值。')
const geometry = computed(() => {
  const w = width.value, h = w < 600 ? 300 : 350
  const left = mode.value === 'raw' ? 72 : 50, right = mode.value === 'raw' ? 84 : 24
  const top = mode.value === 'raw' && w < 520 ? 50 : 34
  return {w, h, left, right, top, bottom: h - 38, plotWidth: w - left - right, plotHeight: h - 38 - top}
})
const charts = computed(() => (dataset.value?.layers || []).map((layer, i) => {
  const g = geometry.value
  const leftMax = mode.value === 'index' ? 100 : nice(Math.max(...layer.funding))
  const rightMax = mode.value === 'index' ? 100 : nice(Math.max(...layer.papers, ...layer.patents))
  return {
    ...layer, theme: themes[i],
    ticks: Array.from({length: 5}, (_, j) => ({y: g.bottom - j * g.plotHeight / 4, left: format(leftMax * j / 4), right: format(rightMax * j / 4)})),
    lines: series.map(s => {
      const peak = Math.max(...layer[s.key]), scale = s.key === 'funding' ? leftMax : rightMax
      const points = layer[s.key].map((value, j) => {
        const v = mode.value === 'index' ? (peak ? value / peak * 100 : 0) : value
        return {x: g.left + g.plotWidth * j / (dataset.value.years.length - 1), y: g.bottom - v / scale * g.plotHeight}
      })
      return {...s, points, path: points.map((p, j) => `${j ? 'L' : 'M'}${p.x.toFixed(2)},${p.y.toFixed(2)}`).join(' ')}
    }),
  }
}))
async function load() {
  loadError.value = false
  try {
    // Read the accepted snapshot only; the standalone PPT controls/scripts are never mounted.
    const response = await fetch('/chain-analysis/v1/curves.html', {signal: controller.signal})
    if (!response.ok) throw new Error('Curve snapshot unavailable')
    const document = new DOMParser().parseFromString(await response.text(), 'text/html')
    const data = JSON.parse(document.querySelector('script#data')?.textContent || 'null')
    if (data?.years?.length !== 9 || data?.layers?.length !== 7 || !data.layers.every(layer =>
      typeof layer.name === 'string' && series.every(s => Array.isArray(layer[s.key]) && layer[s.key].length === data.years.length && layer[s.key].every(v => Number.isFinite(v) && v >= 0)))) {
      throw new Error('Invalid curve snapshot')
    }
    dataset.value = data
  } catch (error) {
    if (error.name !== 'AbortError') loadError.value = true
  }
}
onMounted(() => {
  observer = new ResizeObserver(([entry]) => {width.value = Math.max(280, entry.contentRect.width - 48)})
  observer.observe(root.value)
  load()
})
onBeforeUnmount(() => {controller.abort(); observer?.disconnect()})
</script>

<template>
  <section ref="root" class="investment-curves" aria-label="七大技术方向投入与产出曲线">
    <div v-if="loadError" class="curve-status">曲线数据暂时无法读取。<button @click="load">重新读取</button></div>
    <div v-else-if="!dataset" class="curve-status">正在读取曲线数据…</div>
    <template v-else>
      <div class="curves-toolbar">
        <div class="curves-intro"><p>2017—2025年 · 2017—2022年立项项目队列</p><p>{{explanation}}</p></div>
        <label class="curve-mode">显示方式<select v-model="mode" aria-label="曲线显示方式"><option value="index">相对趋势 · 峰值=100</option><option value="raw">原始数值 · 双轴</option></select></label>
      </div>
      <div class="curve-list">
        <article v-for="chart in charts" :key="chart.id" class="curve-card" :style="{'--curve-theme': chart.theme}">
          <h3>{{chart.name}}</h3>
          <div class="curve-legend" aria-label="图例">
            <span v-for="s in series" :key="s.key"><svg width="25" height="12" aria-hidden="true"><line x1="0" x2="25" y1="6" y2="6" :stroke="s.color" stroke-width="2.5" :stroke-dasharray="s.dash"/></svg>{{s.name}}</span>
          </div>
          <svg class="curve-plot" :viewBox="`0 0 ${geometry.w} ${geometry.h}`" role="img" :aria-label="`${chart.name}，2017至2025年度投入与产出`">
            <text class="axis-caption" :x="geometry.left" y="16">{{mode==='index' ? '相对规模（峰值=100）' : '批准经费（万元）'}}</text>
            <text v-if="mode==='raw'" class="axis-caption" :x="geometry.w-geometry.right" :y="geometry.w<520 ? 28 : 16" text-anchor="end">论文（篇）／专利（件）</text>
            <g v-for="(tick,i) in chart.ticks" :key="i">
              <line :x1="geometry.left" :x2="geometry.w-geometry.right" :y1="tick.y" :y2="tick.y" :stroke="i===0 ? '#cdd6df' : '#eaf0f4'"/>
              <text class="axis-tick" :x="geometry.left-12" :y="tick.y+4" text-anchor="end">{{tick.left}}</text>
              <text v-if="mode==='raw'" class="axis-tick" :x="geometry.w-geometry.right+10" :y="tick.y+4">{{tick.right}}</text>
            </g>
            <template v-for="(year,i) in dataset.years" :key="year">
              <text v-if="geometry.w>=520 || i%2===0" class="axis-year" :x="geometry.left+geometry.plotWidth*i/(dataset.years.length-1)" :y="geometry.bottom+26" text-anchor="middle">{{year}}</text>
            </template>
            <g v-for="s in chart.lines" :key="s.key">
              <path class="curve-series" :data-series="s.key" :d="s.path" fill="none" :stroke="s.color" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round" :stroke-dasharray="s.dash"/>
              <template v-for="(point,i) in s.points" :key="i">
                <rect v-if="s.key==='funding'" :x="point.x-3" :y="point.y-3" width="6" height="6" rx="1" :fill="s.color"/>
                <circle v-else-if="s.key==='papers'" :cx="point.x" :cy="point.y" r="3.4" fill="#fff" :stroke="s.color" stroke-width="2"/>
                <path v-else :d="`M${point.x},${point.y-4}l4,4 -4,4 -4,-4Z`" :fill="s.color"/>
              </template>
            </g>
          </svg>
        </article>
      </div>
    </template>
  </section>
</template>

<style scoped>
.investment-curves{width:100%;min-width:0;margin:0 auto}
.curves-toolbar{display:flex;justify-content:space-between;align-items:center;gap:24px;margin:0 0 24px}
.curves-intro p{margin:0;color:#817a74;font-size:14px;line-height:1.8}.curves-intro p+p{margin-top:3px}
.curve-mode{display:flex;align-items:center;gap:10px;flex-shrink:0;color:#68635f;font-size:14px}
.curve-mode select{font:inherit;color:#403b37;background:white;border:1px solid #ded9d4;border-radius:8px;padding:9px 12px;cursor:pointer}
.curve-list{display:flex;flex-direction:column;align-items:center;gap:28px}
.curve-card{box-sizing:border-box;width:100%;min-width:0;margin:0 auto;padding:22px 24px 16px;background:#fff;border:1px solid #e6e1dc;border-top:5px solid var(--curve-theme);border-radius:14px}
.curve-card h3{margin:0 0 15px;font-size:22px;font-weight:700;line-height:1.5;color:var(--curve-theme)}
.curve-legend{display:flex;flex-wrap:wrap;align-items:center;gap:12px 30px;margin:0 0 10px;color:#576774;font-size:13px}
.curve-legend span{display:inline-flex;align-items:center;gap:9px}.curve-legend svg{flex:none}
.curve-plot{display:block;width:100%;height:auto;margin:0 auto}
.curve-plot text{font-family:inherit}.axis-caption{fill:#82909d;font-size:11px}.axis-tick{fill:#8897a4;font-size:12px}.axis-year{fill:#7f909d;font-size:12px}
.curve-status{padding:65px 24px;background:#fff;border:1px solid #e6e1dc;border-radius:14px;color:#817a74;text-align:center}.curve-status button{margin-left:12px}
@media(max-width:800px){.curves-toolbar{align-items:flex-start;flex-direction:column;gap:14px}.curve-card h3{font-size:20px}.curve-legend{gap:8px 18px;font-size:12px}}
@media(max-width:480px){.curve-card{padding-left:16px;padding-right:16px}.curve-legend{gap:8px 12px}.curve-legend span{gap:5px}}
</style>
