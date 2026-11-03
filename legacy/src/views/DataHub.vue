<template>
  <PageShell
    emphasis
    :title="PAGE_META.data.title"
    :intro="PAGE_META.data.intro"
    :breadcrumb="PAGE_META.data.breadcrumb"
  >
    <!-- Tab 切换（固定位置，切换时不滚回顶部） -->
    <div class="tab-bar">
      <button
        v-for="t in DATA_TYPES"
        :key="t.type"
        type="button"
        class="tab-btn"
        :class="{ active: activeTab === t.type, planned: t.planned }"
        :disabled="t.planned"
        @click="switchTab(t.type)"
      >
        <span class="tab-label">{{ t.label }}</span>
        <span v-if="!t.planned" class="tab-count">{{ tabCount(t.type) }}</span>
        <span v-else class="tab-planned-tag">补充中</span>
      </button>
    </div>

    <Transition
      name="tab-pane"
      mode="out-in"
      @before-leave="disposeCharts"
      @after-enter="onTabPaneReady"
    >
      <div v-if="profile" :key="activeTab" class="tab-pane">
        <!-- 数据源 Hero -->
        <section class="data-hero" :class="profile.heroLayout && `hero-${profile.heroLayout}`" :style="{ '--hero-color': meta.color }">
          <div class="hero-main">
            <div class="hero-head">
              <span class="hero-tag">{{ profile.heroTag }}</span>
              <h1 class="hero-title">{{ profile.heroTitle }}</h1>
              <p v-if="profile.heroSubtitle" class="hero-subtitle">{{ profile.heroSubtitle }}</p>
            </div>
            <p class="hero-desc">{{ profile.heroDesc }}</p>
            <ul v-if="profile.heroBullets?.length" class="hero-bullets">
              <li v-for="(item, bi) in profile.heroBullets" :key="bi">{{ item }}</li>
            </ul>
            <p v-if="profile.insight" class="hero-insight">{{ profile.insight }}</p>
          </div>
          <div class="hero-highlights">
            <button
              v-for="(h, i) in profile.highlights"
              :key="i"
              type="button"
              class="highlight-chip"
              :class="{ clickable: h.tab || h.route }"
              @click="onHighlightClick(h)"
            >
              <span class="hc-val">{{ fmtHighlight(h.value) }}</span>
              <span class="hc-label">{{ h.label }}</span>
              <span v-if="h.hint" class="hc-hint">{{ h.hint }}</span>
            </button>
          </div>
        </section>

        <!-- KPI 条 -->
        <div v-if="card" class="kpi-strip">
          <MetricFlop
            :value="card.count"
            label="数据总量"
            :en="card.name_en || activeTab.toUpperCase()"
            color="#AE0D28"
          />
          <div class="kpi-static">
            <div class="ks-val">{{ card.year_range || '—' }}</div>
            <div class="ks-label">时间范围</div>
          </div>
          <div class="kpi-static">
            <div class="ks-val" :class="card.status">{{ statusLabel(card.status) }}</div>
            <div class="ks-label">数据状态</div>
          </div>
          <div
            v-for="ek in profile.extraKpis || []"
            :key="ek.label"
            class="kpi-static kpi-extra"
          >
            <div class="ks-val" :style="{ color: ek.color }">{{ ek.value }}</div>
            <div class="ks-label">{{ ek.label }}</div>
          </div>
        </div>

        <!-- 主可视化区 -->
        <div v-if="embedUrl" class="embed-wrap">
          <iframe :src="embedUrl" frameborder="0" allowfullscreen title="DataEase BI" />
        </div>

        <template v-else>
          <div class="viz-grid">
            <ScreenPanel
              class="panel-trend"
              :title="profile.trendTitle"
              :subtitle="profile.trendSubtitle || '探索性统计 · 待 DataEase 接入'"
            >
              <div ref="trendChart" class="chart-box chart-tall"></div>
            </ScreenPanel>

            <ScreenPanel
              class="panel-dist"
              :title="profile.distTitle"
              subtitle="点击图例可筛选"
            >
              <div ref="distChart" class="chart-box chart-tall"></div>
            </ScreenPanel>

            <ScreenPanel
              class="panel-bar"
              :title="profile.barTitle"
              subtitle="点击条目高亮对应行"
            >
              <div ref="barChart" class="chart-box"></div>
            </ScreenPanel>

            <ScreenPanel
              class="panel-rank"
              :title="profile.rankTitle"
              subtitle="点击行查看详情"
            >
              <div class="rank-table-wrap">
                <table class="rank-table">
                  <thead>
                    <tr>
                      <th class="col-rn">#</th>
                      <th
                        v-for="col in profile.rankColumns"
                        :key="col.key"
                        :class="col.align === 'right' ? 'col-num' : ''"
                      >{{ col.label }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="(row, ri) in profile.rankRows"
                      :key="ri"
                      class="rank-row"
                      :class="{ active: selectedRank === ri }"
                      @click="selectRank(ri)"
                    >
                      <td class="col-rn">{{ ri + 1 }}</td>
                      <td
                        v-for="col in profile.rankColumns"
                        :key="col.key"
                        :class="col.align === 'right' || col.fmt !== 'text' ? 'col-num' : 'col-name'"
                        :title="row[col.key]"
                      >{{ formatCell(row[col.key], col.fmt) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </ScreenPanel>
          </div>

          <!-- 关联目录 -->
          <section v-if="relatedItems.length" class="related-section">
            <h3 class="section-title">关联数据目录</h3>
            <p class="section-sub">点击切换至相关数据源或跳转专题</p>
            <div class="related-grid">
              <button
                v-for="item in relatedItems"
                :key="item.type"
                type="button"
                class="related-card"
                @click="onRelatedClick(item)"
              >
                <span class="rel-count">{{ fmtCount(item.count) }}</span>
                <span class="rel-label">{{ item.label }}</span>
              </button>
            </div>
          </section>

          <!-- 数据体量 -->
          <div class="archive-strip">
            <span v-for="a in archiveMeta" :key="a.label" class="archive-item">
              <span class="archive-val">{{ a.val }}</span>
              <span class="archive-label">{{ a.label }}</span>
            </span>
          </div>
        </template>
      </div>
    </Transition>
  </PageShell>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as echarts from 'echarts'
import PageShell from '../components/layout/PageShell.vue'
import ScreenPanel from '../components/screen/ScreenPanel.vue'
import MetricFlop from '../components/screen/MetricFlop.vue'
import { PAGE_META, DATA_TYPES } from '../constants/site.js'
import { DATA_ARCHIVE, DEFAULT_DATA_CATALOG, tabCountFor } from '../constants/dataCatalog.js'
import { buildDataHubProfile, DATA_HUB_META, relatedCatalogForTab } from '../constants/dataHubProfiles.js'
import { CHART, chartXAxis, chartYAxis, paletteColor } from '../constants/chartTheme.js'
import { apiGet, fmtCount } from '../composables/useApi'

const route = useRoute()
const router = useRouter()
const overview = ref(null)
const trendChart = ref(null)
const distChart = ref(null)
const barChart = ref(null)
const selectedRank = ref(0)
let trendInst = null
let distInst = null
let barInst = null

const LEGACY_TAB_MAP = {
  entity: 'patent',
  business: 'enterprise',
  job: 'patent',
  video: 'patent',
}

function resolveTab(raw) {
  if (!raw) return null
  const mapped = LEGACY_TAB_MAP[raw] || raw
  const t = DATA_TYPES.find(x => x.type === mapped)
  if (t?.available) return mapped
  if (t?.planned) return null
  return DATA_TYPES.find(x => x.available)?.type || 'paper'
}

const activeTab = ref(resolveTab(route.query.tab) || DATA_TYPES.find(t => t.available)?.type || 'paper')

if (route.query.tab && resolveTab(route.query.tab) !== route.query.tab) {
  const resolved = resolveTab(route.query.tab)
  if (resolved) router.replace({ path: '/data', query: { tab: resolved } })
}

const meta = computed(() => DATA_HUB_META[activeTab.value] || DATA_HUB_META.patent)
const card = computed(() => overview.value?.data_cards?.find(c => c.type === activeTab.value))
const catalog = computed(() => overview.value?.data_catalog?.length ? overview.value.data_catalog : DEFAULT_DATA_CATALOG)
const profile = computed(() => buildDataHubProfile(activeTab.value, card.value || {}, catalog.value))
const relatedItems = computed(() => relatedCatalogForTab(activeTab.value, catalog.value))
const embedUrl = computed(() => '')

const archiveMeta = [
  { val: DATA_ARCHIVE.source_files, label: '业务数据文件' },
  { val: `约 ${DATA_ARCHIVE.volume_gb} GB`, label: '数据资源体量' },
  { val: DATA_ARCHIVE.structured_files, label: '结构化表文件' },
  { val: `${DATA_ARCHIVE.source_categories} 类`, label: '数据源类别' },
]

function tabCount(type) {
  const n = tabCountFor(type, catalog.value, overview.value?.data_cards)
  return n != null ? fmtCount(n) : '—'
}

function statusLabel(s) {
  if (s === 'available') return '已接入'
  if (s === 'partial') return '部分可用'
  return s || '—'
}

function fmtHighlight(v) {
  if (typeof v === 'number') return fmtCount(v)
  return String(v)
}

function formatCell(val, fmt) {
  if (val == null) return '—'
  if (fmt === 'num') return typeof val === 'number' ? val.toLocaleString('zh-CN') : val
  if (fmt === 'dec') return typeof val === 'number' ? val.toFixed(1) : val
  return val
}

function switchTab(type) {
  const t = DATA_TYPES.find(x => x.type === type)
  if (!t?.available) return
  if (type === activeTab.value) return
  activeTab.value = type
  selectedRank.value = 0
  router.replace({ path: '/data', query: { tab: type } })
}

function onHighlightClick(h) {
  if (h.route) {
    router.push(h.route)
    return
  }
  if (h.tab) switchTab(h.tab)
}

function onRelatedClick(item) {
  const m = (item.route || '').match(/tab=(\w+)/)
  if (m) switchTab(m[1])
  else if (item.route) router.push(item.route)
}

function selectRank(i) {
  selectedRank.value = i
  renderBarChart()
}

function renderTrendChart() {
  const p = profile.value
  const color = meta.value.color
  if (!trendChart.value || !p) return
  trendInst?.dispose()
  trendInst = echarts.init(trendChart.value)

  if (p.trendMode === 'dual') {
    trendInst.setOption({
      backgroundColor: 'transparent',
      grid: { left: 52, right: 20, top: 36, bottom: 32 },
      legend: { data: ['申请量', '授权量'], top: 0, ...CHART.legend },
      tooltip: { trigger: 'axis', ...CHART.tooltip },
      xAxis: chartXAxis(p.trendYears),
      yAxis: chartYAxis(),
      series: [
        {
          name: '申请量', type: 'bar', data: p.trendPrimary, barMaxWidth: 18,
          itemStyle: { color: 'rgba(174,13,40,0.75)', borderRadius: [3, 3, 0, 0] },
        },
        {
          name: '授权量', type: 'line', data: p.trendSecondary, smooth: true,
          lineStyle: { color: '#b45309', width: 2 },
          itemStyle: { color: '#b45309' },
        },
      ],
    })
    return
  }

  trendInst.setOption({
    backgroundColor: 'transparent',
    grid: { left: 52, right: 20, top: 28, bottom: 32 },
    tooltip: { trigger: 'axis', ...CHART.tooltip },
    xAxis: chartXAxis(p.trendYears),
    yAxis: chartYAxis(),
    series: [{
      type: 'line', data: p.trendPrimary, smooth: true,
      areaStyle: { color: 'rgba(174,13,40,0.08)' },
      lineStyle: { color, width: 2.5 },
      itemStyle: { color },
    }],
  })
}

function renderDistChart() {
  const p = profile.value
  const color = meta.value.color
  if (!distChart.value || !p) return
  distInst?.dispose()
  distInst = echarts.init(distChart.value)
  distInst.setOption({
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)', ...CHART.tooltip },
    legend: { orient: 'vertical', right: 4, top: 'middle', ...CHART.legend },
    series: [{
      type: 'pie',
      radius: ['42%', '68%'],
      center: ['38%', '50%'],
      data: p.distData.map((d, i) => ({
        ...d,
        itemStyle: { color: paletteColor(i) },
      })),
      label: { color: '#4a4540', fontSize: 10 },
      emphasis: { scale: true, scaleSize: 8 },
    }],
  })
  distInst.on('click', params => {
    const idx = p.distData.findIndex(d => d.name === params.name)
    if (idx >= 0) selectRank(Math.min(idx, p.rankRows.length - 1))
  })
}

function renderBarChart() {
  const p = profile.value
  const color = meta.value.color
  if (!barChart.value || !p) return
  barInst?.dispose()
  barInst = echarts.init(barChart.value)

  const nameKey = p.rankColumns?.[0]?.key || 'name'
  const valueKey = p.rankColumns?.find(c => c.fmt === 'num')?.key || 'value'
  const rows = (p.rankRows || []).slice(0, 10)
  const data = rows.length
    ? rows.map(row => ({
        name: row[nameKey] ?? row.name,
        value: row[valueKey] ?? row.value ?? 0,
      }))
    : [...p.barData].sort((a, b) => b.value - a.value).slice(0, 10)

  barInst.setOption({
    backgroundColor: 'transparent',
    grid: { left: 8, right: 48, top: 8, bottom: 8, containLabel: true },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: { type: 'value', show: false },
    yAxis: {
      type: 'category',
      inverse: true,
      data: data.map(d => d.name),
      axisLabel: {
        color: '#4a4540',
        fontSize: 10,
        width: 120,
        overflow: 'truncate',
      },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [{
      type: 'bar',
      data: data.map((d, i) => ({
        value: d.value,
        itemStyle: {
          color: i === selectedRank.value ? color : 'rgba(174,13,40,0.35)',
          borderRadius: [0, 4, 4, 0],
        },
      })),
      barMaxWidth: 14,
      label: {
        show: true,
        position: 'right',
        color: '#78716c',
        fontSize: 9,
        formatter: p => (p.value >= 10000 ? `${(p.value / 10000).toFixed(1)}万` : p.value),
      },
    }],
  })
  barInst.off('click')
  barInst.on('click', params => {
    if (params.dataIndex >= 0) selectRank(params.dataIndex)
  })
}

function disposeCharts() {
  trendInst?.dispose()
  distInst?.dispose()
  barInst?.dispose()
  trendInst = null
  distInst = null
  barInst = null
}

function onTabPaneReady() {
  // 等待 Transition 完成挂载 + ScreenPanel 布局后再 init ECharts
  nextTick(() => {
    requestAnimationFrame(() => {
      renderCharts()
    })
  })
}

function renderCharts() {
  renderTrendChart()
  renderDistChart()
  renderBarChart()
}

function onResize() {
  trendInst?.resize()
  distInst?.resize()
  barInst?.resize()
}

watch(() => route.query.tab, v => {
  const resolved = resolveTab(v)
  if (!resolved) return
  if (resolved !== activeTab.value) {
    activeTab.value = resolved
    selectedRank.value = 0
  }
})

onMounted(async () => {
  try { overview.value = await apiGet('/api/overview') } catch { /* ignore */ }
  onTabPaneReady()
  window.addEventListener('resize', onResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  disposeCharts()
})
</script>

<style scoped>
/* Tab 切换动画 */
.tab-pane-enter-active,
.tab-pane-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}
.tab-pane-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.tab-pane-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* Hero */
.data-hero {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 20px;
  padding: 22px 24px;
  margin-bottom: 18px;
  border-radius: 16px;
  background: var(--surface-card);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow), var(--card-highlight);
  border-top: 3px solid var(--hero-color, var(--ruc-red));
  align-items: stretch;
}
.hero-main {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}
.hero-head {
  flex-shrink: 0;
}
.hero-tag {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--hero-color, var(--ruc-red));
  background: color-mix(in srgb, var(--hero-color, var(--ruc-red)) 12%, transparent);
  padding: 5px 12px;
  border-radius: 999px;
  margin-bottom: 10px;
}
.hero-title {
  font-size: 1.55rem;
  font-weight: 800;
  color: var(--text);
  letter-spacing: 0.02em;
  line-height: 1.25;
  margin: 0 0 0;
}
.hero-subtitle {
  margin: 8px 0 0;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text);
  line-height: 1.5;
  max-width: 520px;
}
.hero-desc {
  font-size: 0.92rem;
  color: var(--muted);
  line-height: 1.65;
  max-width: 520px;
  font-weight: 500;
  margin: 0;
}
.hero-bullets {
  margin: 0;
  padding: 0;
  list-style: none;
  max-width: 520px;
}
.hero-bullets li {
  position: relative;
  padding-left: 14px;
  font-size: 0.84rem;
  color: var(--muted);
  line-height: 1.55;
  margin-bottom: 7px;
  font-weight: 500;
}
.hero-bullets li:last-child { margin-bottom: 0; }
.hero-bullets li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.58em;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--hero-color, var(--ruc-red));
  opacity: 0.55;
}
.hero-insight {
  margin: 0;
  font-size: 0.85rem;
  color: var(--muted);
  line-height: 1.6;
  padding-left: 12px;
  border-left: 2px solid rgba(174, 13, 40, 0.35);
  font-weight: 500;
  max-width: 520px;
}

/* 6 卡（论文）：纵向均匀分布，避免 insight 单独沉底 */
.data-hero.hero-spread .hero-main {
  justify-content: space-between;
  gap: 0;
}

/* 5 卡（专利）：适度拉开 */
.data-hero.hero-balanced .hero-main {
  justify-content: space-between;
  gap: 4px;
}

/* 4 卡（基金等）：收紧间距 + 控制文案量 */
.data-hero.hero-compact .hero-main {
  justify-content: flex-start;
  gap: 7px;
}
.data-hero.hero-compact .hero-tag { margin-bottom: 6px; }
.data-hero.hero-compact .hero-title { font-size: 1.45rem; }
.data-hero.hero-compact .hero-subtitle { margin-top: 4px; }
.data-hero.hero-compact .hero-desc {
  font-size: 0.88rem;
  line-height: 1.55;
}
.data-hero.hero-compact .hero-bullets li {
  font-size: 0.82rem;
  line-height: 1.45;
  margin-bottom: 4px;
}
.data-hero.hero-compact .hero-insight {
  font-size: 0.82rem;
  line-height: 1.5;
}

/* 4 卡但内容偏少：均匀分布填满 */
.data-hero.hero-even .hero-main {
  justify-content: space-between;
  gap: 0;
}
.data-hero.hero-even .hero-desc,
.data-hero.hero-even .hero-bullets li {
  font-size: 0.86rem;
  line-height: 1.5;
}
.hero-highlights {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  align-content: start;
}
.highlight-chip {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--surface-panel);
  border: 1px solid var(--border);
  text-align: left;
  transition: transform 0.15s, border-color 0.15s, background 0.15s;
}
.highlight-chip.clickable {
  cursor: pointer;
}
.highlight-chip.clickable:hover {
  transform: translateY(-2px);
  border-color: rgba(174, 13, 40, 0.3);
  background: var(--surface-card-hover);
}
.hc-val {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--ruc-red-dark);
  font-variant-numeric: tabular-nums;
}
.hc-label {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--text);
}
.hc-hint {
  font-size: 0.72rem;
  color: var(--muted);
  font-weight: 500;
}

/* Tabs */
.tab-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
  position: sticky;
  top: 0;
  z-index: 20;
  padding: 10px 0;
  background: linear-gradient(to bottom, rgba(245, 243, 240, 0.97) 70%, transparent);
}
.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #ffffff;
  border: 1px solid var(--border);
  color: var(--text);
  padding: 9px 16px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.88rem;
  font-weight: 600;
  transition: background 0.15s, border-color 0.15s, color 0.15s, transform 0.12s;
}
.tab-btn:hover {
  border-color: rgba(174, 13, 40, 0.35);
  color: var(--ruc-red-dark);
  transform: translateY(-1px);
}
.tab-btn.active {
  background: var(--ruc-red-muted);
  border-color: var(--ruc-red);
  color: var(--ruc-red-dark);
  box-shadow: 0 2px 12px rgba(174, 13, 40, 0.12);
}
.tab-btn.planned {
  border-style: dashed;
  border-color: #c4c0ba;
  color: #a8a29e;
  background: transparent;
  cursor: not-allowed;
  opacity: 0.72;
}
.tab-btn.planned:hover {
  transform: none;
  border-color: #c4c0ba;
  color: #a8a29e;
}
.tab-count {
  font-size: 0.76rem;
  font-weight: 700;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}
.tab-btn.active .tab-count { color: var(--ruc-red); }
.tab-planned-tag {
  font-size: 0.68rem;
  font-weight: 600;
  color: #a8a29e;
  padding: 1px 6px;
  border-radius: 999px;
  border: 1px dashed #c4c0ba;
}

/* KPI */
.kpi-strip {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  margin-bottom: 16px;
}
.kpi-static {
  text-align: center;
  padding: 14px 10px;
  background: var(--surface-card);
  border-radius: 12px;
  border: 1px solid var(--border);
  transition: border-color 0.15s;
}
.kpi-static:hover { border-color: rgba(174, 13, 40, 0.2); }
.ks-val { font-size: 1.08rem; font-weight: 800; color: var(--text); font-variant-numeric: tabular-nums; }
.ks-val.available { color: var(--green); }
.ks-label { font-size: 0.76rem; color: var(--muted); margin-top: 4px; font-weight: 600; }

/* Charts grid */
.viz-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  grid-template-rows: auto auto;
  gap: 12px;
  margin-bottom: 18px;
}
.panel-trend { grid-column: 1; grid-row: 1; }
.panel-dist { grid-column: 2; grid-row: 1; }
.panel-bar { grid-column: 1; grid-row: 2; }
.panel-rank { grid-column: 2; grid-row: 2; }
.chart-box { width: 100%; height: 260px; }
.chart-tall { height: 280px; }

/* Rank table */
.rank-table-wrap {
  max-height: 260px;
  overflow-y: auto;
  scrollbar-width: thin;
}
.rank-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
}
.rank-table thead {
  position: sticky;
  top: 0;
  z-index: 1;
  background: var(--surface-panel);
}
.rank-table th {
  padding: 8px 10px;
  text-align: left;
  font-weight: 700;
  color: var(--ruc-red-dark);
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}
.rank-table td {
  padding: 9px 10px;
  border-bottom: 1px solid var(--border);
  color: var(--text);
}
.col-rn { width: 28px; color: var(--muted); font-weight: 700; }
.col-name {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.col-num { text-align: right; font-variant-numeric: tabular-nums; font-weight: 600; color: var(--text); }
.rank-row { cursor: pointer; transition: background 0.12s; }
.rank-row:hover { background: var(--ruc-red-muted); }
.rank-row.active {
  background: rgba(174, 13, 40, 0.12);
  box-shadow: inset 3px 0 0 var(--ruc-red);
}

.related-section {
  padding: 18px 20px;
  margin-bottom: 16px;
  border-radius: 14px;
  background: var(--surface-panel);
  border: 1px solid var(--border);
}
.section-title {
  font-size: 1rem;
  font-weight: 800;
  color: var(--text);
  letter-spacing: 0.04em;
  margin-bottom: 4px;
}
.section-sub {
  font-size: 0.82rem;
  color: var(--muted);
  margin-bottom: 14px;
  font-weight: 500;
}
.related-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
}
.related-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 10px;
  border-radius: 10px;
  background: var(--surface-card);
  border: 1px solid var(--border);
  cursor: pointer;
  text-align: center;
  transition: transform 0.12s, border-color 0.12s, background 0.12s;
}
.related-card:hover {
  transform: translateY(-2px);
  border-color: rgba(174, 13, 40, 0.3);
  background: var(--surface-card-hover);
}
.rel-count {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--ruc-red);
  font-variant-numeric: tabular-nums;
}
.rel-label {
  font-size: 0.74rem;
  color: var(--muted);
  font-weight: 600;
  line-height: 1.35;
}

.archive-strip {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  padding: 12px 16px;
  border-radius: 10px;
  background: var(--surface-panel);
  border: 1px dashed var(--border);
  margin-bottom: 10px;
}
.archive-val { color: var(--muted); font-weight: 600; }
.archive-label { color: #a8a29e; }
.catalog-foot {
  font-size: 0.74rem;
  color: var(--muted);
  text-align: center;
  line-height: 1.55;
  margin-bottom: 8px;
}

.embed-wrap iframe { width: 100%; height: 75vh; border-radius: 8px; background: var(--surface-panel); }

@media (max-width: 1100px) {
  .data-hero { grid-template-columns: 1fr; }
  .kpi-strip { grid-template-columns: repeat(3, 1fr); }
  .viz-grid { grid-template-columns: 1fr; }
  .panel-trend, .panel-dist, .panel-bar, .panel-rank { grid-column: 1; grid-row: auto; }
  .related-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 640px) {
  .hero-highlights { grid-template-columns: 1fr; }
  .kpi-strip { grid-template-columns: repeat(2, 1fr); }
  .related-grid { grid-template-columns: repeat(2, 1fr); }
}
</style>
