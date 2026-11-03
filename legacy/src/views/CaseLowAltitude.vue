<template>
  <div class="case-page">
    <header class="case-header">
      <div>
        <span class="case-tag">案例展示</span>
        <h1 class="case-title">低空经济技术演进</h1>
        <p class="case-intro">{{ caseIntro }}</p>
      </div>
      <div class="header-actions">
        <div v-if="!activeLayer" class="view-switch">
          <button
            type="button"
            class="view-btn"
            :class="{ active: caseView === 'tech' }"
            @click="setCaseView('tech')"
          >技术点</button>
          <button
            type="button"
            class="view-btn"
            :class="{ active: caseView === 'product' }"
            @click="setCaseView('product')"
          >产品</button>
        </div>
        <div v-if="caseView === 'product' && !activeLayer" class="product-tabs">
          <button
            v-for="p in products" :key="p.id" type="button" class="tab"
            :class="{ active: product === p.id }" @click="setProduct(p.id)"
          >{{ p.id }}</button>
        </div>
      </div>
    </header>

    <SectionBlock
      tone="case"
      :title="sectionTitle"
      :subtitle="sectionSubtitle"
    >
      <Transition name="case-pane" mode="out-in">
        <div v-if="!activeLayer && caseView === 'product'" key="product" class="product-layout">
          <div class="product-hero">
            <div>
              <span class="hero-id">{{ productLine.id }}</span>
              <span class="hero-name">{{ productLine.name }}</span>
              <p class="hero-desc">{{ productLine.desc }}</p>
              <p class="hero-stage">{{ productLine.stage }}</p>
            </div>
            <div class="hero-metrics">
              <div class="hm"><span class="hmv">{{ productLine.a_papers ?? '—' }}</span><span class="hml">OpenScholar</span></div>
              <div class="hm"><span class="hmv">{{ productLine.b_papers ?? '—' }}</span><span class="hml">Skills</span></div>
              <div class="hm"><span class="hmv">{{ productLine.surveys ?? 4 }}</span><span class="hml">Survey</span></div>
              <div class="hm"><span class="hmv">{{ pct(productLine.fund_ratio_b) }}</span><span class="hml">基金占比</span></div>
            </div>
          </div>
          <SurveyReaderPanel
            class="product-survey-pane"
            :tech-id="product"
            :tech-label="`${productLine.name} · 产品综述`"
            :title="productSurveyTitle"
            :html="productSurveyHtml"
            :loading="productSurveyLoading"
            :line-type="productLineType"
            :references="productSurveyRefs"
            @switch-line="loadProductSurvey"
          />
          <p class="product-hint">
            产品 Survey 从宏观维度梳理 {{ productLine.id }} 技术演进；下方可切换至
            <button type="button" class="inline-link" @click="setCaseView('tech')">33 技术点 · 六大类词典</button>
            查看各技术点细粒度 Survey。
          </p>
        </div>

        <div v-else-if="!activeLayer" key="overview" class="overview-layout">
          <div class="overview-stats">
            <div v-for="s in overviewStats" :key="s.label" class="stat-chip">
              <span class="stat-val" :style="{ color: s.color }">{{ s.value }}</span>
              <span class="stat-label">{{ s.label }}</span>
            </div>
          </div>

          <div class="tree-overview-wrap">
            <EvolutionTree
              size="page"
              :interactive="true"
              :show-leaves="false"
              :navigate-on-click="false"
              :product="product"
              @branch-click="onBranchClick"
            />
          </div>

          <div class="layer-grid">
            <button
              v-for="card in layerCards"
              :key="card.id"
              type="button"
              class="layer-card"
              @click="onBranchClick(card.id)"
            >
              <span class="lc-count" :style="{ color: card.color }">{{ card.pointCount }}</span>
              <span class="lc-name">{{ card.name }}</span>
              <span class="lc-meta">{{ card.paperCount }} 篇文献 · {{ card.surveyReady }} Survey</span>
              <span class="lc-action">进入该大类 →</span>
            </button>
          </div>
        </div>

        <div v-else :key="'layer-' + activeLayer" class="layer-detail">
          <button type="button" class="back-btn" @click="clearLayer">← 返回六大类总览</button>
          <div class="layer-workspace">
            <div class="tree-pane">
              <LayerBranchTree
                :layer-id="activeLayer"
                :selected-tech="selected"
                @leaf-click="selectPoint"
              />
            </div>
            <SurveyReaderPanel
              class="survey-pane"
              :tech-id="selected"
              :tech-label="detail?.tech_label || ''"
              :title="surveyTitle"
              :html="surveyHtml"
              :loading="surveyLoading"
              :line-type="lineType"
              :references="references"
              @switch-line="loadSurvey"
            />
          </div>

          <Transition name="case-fade" mode="out-in">
            <div v-if="detail" :key="selected" class="metrics-bar">
              <div class="metric"><span class="mv">{{ detail.paper_count }}</span><span class="ml">Skills 文献</span></div>
              <div class="metric"><span class="mv">{{ pct(detail.funding_ratio) }}</span><span class="ml">基金占比</span></div>
              <div class="metric"><span class="mv">{{ detail.avg_citation }}</span><span class="ml">平均被引</span></div>
              <div class="metric"><span class="mv">{{ detail.avg_funding_score }}</span><span class="ml">基金支撑分</span></div>
              <div ref="citeChart" class="mini-chart"></div>
            </div>
          </Transition>
        </div>
      </Transition>
    </SectionBlock>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import * as echarts from 'echarts'
import SectionBlock from '../components/layout/SectionBlock.vue'
import EvolutionTree from '../components/case/EvolutionTree.vue'
import LayerBranchTree from '../components/case/LayerBranchTree.vue'
import SurveyReaderPanel from '../components/case/SurveyReaderPanel.vue'
import { branchById, LAYER_BRANCHES, layerFromTree } from '../constants/techTree.js'
import { PRODUCT_CASES, enrichProductLine } from '../constants/productCases.js'
import { apiGet } from '../composables/useApi'

const route = useRoute()
const router = useRouter()
const tree = ref({ layers: [] })
const selected = ref('')
const detail = ref(null)
const surveyHtml = ref('')
const surveyTitle = ref('')
const surveyLoading = ref(false)
const lineType = ref('B')
const productLineType = ref('B')
const product = ref(route.query.product || 'UAV')
const caseView = ref(route.query.view === 'product' ? 'product' : 'tech')
const activeLayer = ref(route.query.layer || '')
const workflow = ref({})
const productSurveyHtml = ref('')
const productSurveyTitle = ref('')
const productSurveyLoading = ref(false)
const productSurveyRefs = ref([])
const citeChart = ref(null)
let chartInst = null

const products = PRODUCT_CASES

const surveyRefs = ref([])

const references = computed(() => {
  const papers = detail.value?.top_papers || []
  if (papers.length) return papers
  return surveyRefs.value
})

const layerTitle = computed(() => {
  const b = branchById(activeLayer.value)
  if (b) return b.name
  const l = tree.value.layers?.find(x => x.tech_layer_id === activeLayer.value)
  return l?.tech_layer_name || '技术大类'
})

const productLine = computed(() => {
  const line = (workflow.value.product_lines || []).find(x => x.id === product.value)
  return enrichProductLine(product.value, line || {})
})

const caseIntro = computed(() => {
  if (activeLayer.value) return `当前大类：${layerTitle.value} · 载体 ${product.value}`
  if (caseView.value === 'product') {
    return `${productLine.value.name}（${product.value}）产品 Survey · 宏观技术演进综述`
  }
  return `${product.value} 示范载体 · 六大类技术词典 33 点 · 点击枝干进入该大类`
})

const sectionTitle = computed(() => {
  if (activeLayer.value) return layerTitle.value
  if (caseView.value === 'product') return `${product.value} 产品 Survey`
  return '六大类技术树总览'
})

const sectionSubtitle = computed(() => {
  if (activeLayer.value) return '技术点沿枝干两侧展开 · 右侧查看该技术点 Survey'
  if (caseView.value === 'product') return 'OpenScholar / Skills 双管线成稿 · 支撑汇报与产业解读'
  return '点击枝干或下方技术大类卡片，进入该大类演进脉络'
})

const overviewStats = computed(() => {
  const layers = tree.value.layers || []
  const points = layers.reduce((s, l) => s + (l.tech_points?.length || 0), 0)
  const papers = layers.reduce((s, l) => s + (l.paper_count || 0), 0)
  const survey = layers.reduce((s, l) => {
    return s + (l.tech_points || []).filter(p => p.survey_b_ready).length
  }, 0)
  return [
    { label: '技术大类', value: layers.length || 6, color: '#ae0d28' },
    { label: '技术点', value: points || 33, color: '#1a4d7a' },
    { label: 'Skills 文献', value: papers > 999 ? `${(papers / 1000).toFixed(1)}k` : papers, color: '#2d6a4f' },
    { label: 'Survey 就绪', value: survey, color: '#b45309' },
  ]
})

const layerCards = computed(() =>
  LAYER_BRANCHES.map(meta => {
    const layer = layerFromTree(tree.value, meta.id)
    const points = layer?.tech_points || []
    const surveyReady = points.filter(p => p.survey_b_ready).length
    return {
      id: meta.id,
      name: meta.name,
      color: meta.color,
      pointCount: points.length,
      paperCount: layer?.paper_count ?? points.reduce((s, p) => s + (p.paper_count_b || 0), 0),
      surveyReady,
    }
  }),
)

function pct(v) { return v != null ? `${(v * 100).toFixed(1)}%` : '—' }

function renderCiteChart() {
  if (!citeChart.value || !detail.value?.citation_histogram) return
  chartInst?.dispose()
  chartInst = echarts.init(citeChart.value)
  const h = detail.value.citation_histogram
  chartInst.setOption({
    backgroundColor: 'transparent',
    grid: { left: 40, right: 10, top: 10, bottom: 24 },
    xAxis: { type: 'category', data: Object.keys(h), axisLabel: { color: '#78716c', fontSize: 10 } },
    yAxis: { type: 'value', axisLabel: { color: '#78716c', fontSize: 10 }, splitLine: { lineStyle: { color: '#e8e4df' } } },
    series: [{ type: 'bar', data: Object.values(h), itemStyle: { color: '#ae0d28', borderRadius: [3, 3, 0, 0] } }],
  })
}

function setCaseView(view) {
  caseView.value = view
  const q = { product: product.value, view }
  if (activeLayer.value) q.layer = activeLayer.value
  if (selected.value) q.tech = selected.value
  router.replace({ path: '/case', query: q })
  if (view === 'product') loadProductSurvey(productLineType.value)
}

function setProduct(id) {
  product.value = id
  const q = { product: id, view: caseView.value }
  if (activeLayer.value) {
    q.layer = activeLayer.value
    if (selected.value) q.tech = selected.value
  }
  router.replace({ path: '/case', query: q })
  if (!activeLayer.value && caseView.value === 'product') loadProductSurvey(productLineType.value)
}

async function loadProductSurvey(lt) {
  productLineType.value = lt
  productSurveyLoading.value = true
  try {
    const s = await apiGet(`/api/survey/product?product_id=${product.value}&line_type=${lt}`)
    productSurveyTitle.value = s.title || `${product.value} Survey`
    productSurveyHtml.value = marked.parse(s.excerpt_md || s.content_md || '')
    productSurveyRefs.value = s.references || []
  } catch {
    productSurveyTitle.value = `${product.value} Survey`
    productSurveyHtml.value = '<p>暂无产品 Survey 文稿</p>'
    productSurveyRefs.value = []
  }
  productSurveyLoading.value = false
}

function onBranchClick(layerId) {
  activeLayer.value = layerId
  selected.value = ''
  detail.value = null
  surveyHtml.value = ''
  surveyTitle.value = ''
  surveyRefs.value = []
  router.replace({ path: '/case', query: { product: product.value, layer: layerId } })
}

function clearLayer() {
  activeLayer.value = ''
  selected.value = ''
  detail.value = null
  surveyHtml.value = ''
  surveyTitle.value = ''
  surveyRefs.value = []
  router.replace({ path: '/case', query: { product: product.value, view: caseView.value } })
}

async function selectPoint(tid, { skipRouter = false } = {}) {
  if (!skipRouter) {
    router.replace({
      path: '/case',
      query: { product: product.value, layer: activeLayer.value, tech: tid },
    })
  }
  if (tid === selected.value && detail.value?.tech_tag_id === tid) return

  selected.value = tid
  detail.value = await apiGet(`/api/tech/${tid}`)
  await nextTick()
  renderCiteChart()
  await loadSurvey(lineType.value)
}

async function loadSurvey(lt) {
  lineType.value = lt
  if (!selected.value) return
  surveyLoading.value = true
  try {
    const s = await apiGet(`/api/survey?tech_tag_id=${selected.value}&line_type=${lt}`)
    surveyTitle.value = s.title || 'Survey 摘要'
    surveyHtml.value = marked.parse(s.excerpt_md || s.content_md || '')
    surveyRefs.value = s.references || []
  } catch {
    surveyTitle.value = 'Survey 摘要'
    surveyHtml.value = '<p>暂无 Survey 文稿</p>'
  }
  surveyLoading.value = false
}

onMounted(async () => {
  const [treeData, overview] = await Promise.all([
    apiGet('/api/tech/tree'),
    apiGet('/api/overview').catch(() => ({})),
  ])
  tree.value = treeData
  workflow.value = overview.workflow_highlights || {}
  if (route.query.layer) activeLayer.value = String(route.query.layer)
  if (!activeLayer.value && caseView.value === 'product') {
    await loadProductSurvey(productLineType.value)
  }
  const tid = route.query.tech
  if (tid) await selectPoint(String(tid), { skipRouter: true })
})

watch(() => route.query.product, v => {
  if (!v) return
  product.value = v
  if (!activeLayer.value && caseView.value === 'product') loadProductSurvey(productLineType.value)
})
watch(() => route.query.view, v => {
  if (activeLayer.value) return
  caseView.value = v === 'product' ? 'product' : 'tech'
  if (caseView.value === 'product') loadProductSurvey(productLineType.value)
})
watch(() => route.query.layer, v => {
  activeLayer.value = v ? String(v) : ''
  if (!v) {
    selected.value = ''
    detail.value = null
    surveyHtml.value = ''
    surveyTitle.value = ''
    surveyRefs.value = []
  }
})
watch(() => route.query.tech, async v => {
  if (!v) return
  const tid = String(v)
  if (tid === selected.value && detail.value) return
  await selectPoint(tid, { skipRouter: true })
})
onBeforeUnmount(() => chartInst?.dispose())
</script>

<style scoped>
.case-page { width: 100%; }

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
}
.case-tag {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--ruc-red);
}
.case-title {
  font-size: 1.45rem;
  font-weight: 600;
  color: var(--text);
  margin-top: 8px;
}
.case-intro {
  font-size: 0.85rem;
  color: var(--muted);
  margin-top: 8px;
}

.view-switch {
  display: flex;
  gap: 6px;
  padding: 3px;
  border-radius: 999px;
  background: var(--surface-panel);
  border: 1px solid var(--border);
}
.view-btn {
  padding: 6px 14px;
  border: none;
  border-radius: 999px;
  background: transparent;
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.view-btn.active {
  background: var(--ruc-red-muted);
  color: var(--ruc-red-dark);
}
.tab {
  background: var(--surface-panel);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 8px 16px;
  border-radius: 999px;
  cursor: pointer;
  font-size: 0.82rem;
}
.tab.active {
  background: var(--ruc-red-muted);
  border-color: rgba(174, 13, 40, 0.3);
  color: var(--ruc-red-dark);
}

.product-hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding: 18px 20px;
  border-radius: 14px;
  background: var(--surface-card);
  border: 1px solid var(--card-border);
}
.hero-id {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--ruc-red);
  margin-right: 10px;
}
.hero-name { font-size: 1rem; font-weight: 600; color: var(--text); }
.hero-desc { font-size: 0.82rem; color: var(--muted); margin-top: 10px; line-height: 1.5; }
.hero-stage { font-size: 0.74rem; color: #a8a29e; margin-top: 6px; }
.hm {
  text-align: center;
  padding: 10px 12px;
  border-radius: 10px;
  background: var(--surface-panel);
  border: 1px solid var(--border);
  min-width: 72px;
}
.hmv { display: block; font-size: 1.1rem; font-weight: 800; color: var(--ruc-red-dark); }
.hml { display: block; font-size: 0.68rem; color: var(--muted); margin-top: 2px; }
.inline-link, .back-btn {
  background: none;
  border: none;
  padding: 0;
  color: var(--ruc-red);
  font-size: inherit;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}
.inline-link:hover, .back-btn:hover { color: var(--ruc-red-dark); }

.stat-chip {
  text-align: center;
  padding: 14px 10px;
  border-radius: 12px;
  background: var(--surface-card);
  border: 1px solid var(--border);
}
.stat-label { display: block; font-size: 0.76rem; font-weight: 600; color: var(--muted); margin-top: 4px; }
.tree-overview-wrap {
  border-radius: 14px;
  background: var(--surface-panel);
  border: 1px solid var(--border);
}
.layer-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: left;
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--surface-card);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: border-color 0.15s, transform 0.12s, background 0.15s;
}
.layer-card:hover {
  border-color: rgba(174, 13, 40, 0.3);
  background: var(--surface-card-hover);
  transform: translateY(-2px);
}
.lc-name { font-size: 0.88rem; font-weight: 700; color: var(--text); line-height: 1.35; }
.lc-meta { font-size: 0.74rem; color: var(--muted); font-weight: 500; }
.lc-action { font-size: 0.72rem; font-weight: 600; color: #a8a29e; margin-top: 4px; }
.layer-card:hover .lc-action { color: var(--ruc-red); }

.metrics-bar {
  display: grid;
  grid-template-columns: repeat(4, 1fr) 1.2fr;
  gap: 12px;
  margin-top: 20px;
  padding-top: 18px;
  border-top: 1px solid var(--border);
}
.metric {
  text-align: center;
  padding: 14px 10px;
  border-radius: 12px;
  background: var(--surface-card);
  border: 1px solid var(--border);
}
.mv { display: block; font-size: 1.2rem; font-weight: 700; color: var(--ruc-red-dark); }
.ml { font-size: 0.72rem; color: var(--muted); margin-top: 4px; }

/* keep layout helpers */
.product-tabs { display: flex; gap: 8px; }
.header-actions { display: flex; flex-direction: column; align-items: flex-end; gap: 10px; }
.product-layout { display: flex; flex-direction: column; gap: 16px; }
.hero-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; flex-shrink: 0; }
.product-survey-pane { min-height: 480px; }
.product-survey-pane :deep(.reader-body) { max-height: 360px; }
.product-hint { font-size: 0.78rem; color: var(--muted); line-height: 1.55; padding: 0 4px; }
.back-btn { margin-bottom: 12px; font-size: 0.82rem; text-decoration: none; }
.layer-workspace { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: stretch; min-height: 500px; }
.tree-pane { min-width: 0; min-height: 460px; display: flex; align-items: stretch; }
.survey-pane { min-width: 0; overflow: hidden; }
.overview-layout { display: flex; flex-direction: column; gap: 16px; }
.overview-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.stat-val { display: block; font-size: 1.35rem; font-weight: 800; font-variant-numeric: tabular-nums; }
.layer-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.lc-count { font-size: 1.25rem; font-weight: 800; font-variant-numeric: tabular-nums; }
.mini-chart { width: 100%; height: 100px; min-height: 100px; }

.case-pane-enter-active, .case-pane-leave-active, .case-fade-enter-active, .case-fade-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}
.case-pane-enter-from { opacity: 0; transform: translateY(10px); }
.case-pane-leave-to { opacity: 0; transform: translateY(-8px); }
.case-fade-enter-from, .case-fade-leave-to { opacity: 0; }

@media (max-width: 960px) {
  .case-header { flex-direction: column; }
  .header-actions { align-items: flex-start; width: 100%; }
  .product-hero { flex-direction: column; }
  .hero-metrics { width: 100%; grid-template-columns: repeat(2, 1fr); }
  .layer-workspace { grid-template-columns: 1fr; }
  .overview-stats { grid-template-columns: repeat(2, 1fr); }
  .layer-grid { grid-template-columns: repeat(2, 1fr); }
  .metrics-bar { grid-template-columns: repeat(2, 1fr); }
  .mini-chart { grid-column: 1 / -1; }
}
@media (max-width: 640px) {
  .layer-grid { grid-template-columns: 1fr; }
}
</style>
