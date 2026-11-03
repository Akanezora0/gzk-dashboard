<template>
  <div class="tech-tree-panel">
    <SectionBlock
      tone="case"
      :title="sectionTitle"
      :subtitle="sectionSubtitle"
    >
      <Transition name="case-pane" mode="out-in">
        <div v-if="!activeLayer" key="overview" class="overview-layout">
          <div class="tree-overview-wrap" :class="{ 'is-expanded': !!expandedLayer }">
            <EvolutionTree
              size="page"
              :interactive="true"
              :show-leaves="true"
              :active-layer="expandedLayer"
              :navigate-on-click="false"
              :product="product"
              @branch-click="onCanvasBranchClick"
              @leaf-click="onCanvasLeafClick"
            />
          </div>

          <div class="layer-grid">
            <button
              v-for="card in layerCards"
              :key="card.id"
              type="button"
              class="layer-card"
              :class="{ active: expandedLayer === card.id }"
              @click="onLayerCardClick(card.id)"
            >
              <span class="lc-count" :style="{ color: card.color }">{{ card.pointCount }}</span>
              <span class="lc-name">{{ card.name }}</span>
              <span class="lc-meta">{{ card.paperCount }} 篇文献 · {{ card.surveyReady }} survey</span>
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
              <div class="metric"><span class="mv">{{ detail.paper_count }}</span><span class="ml">文献</span></div>
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
import SectionBlock from '../layout/SectionBlock.vue'
import EvolutionTree from './EvolutionTree.vue'
import LayerBranchTree from './LayerBranchTree.vue'
import SurveyReaderPanel from './SurveyReaderPanel.vue'
import { branchById, LAYER_BRANCHES, layerFromTree } from '../../constants/techTree.js'
import { apiGet } from '../../composables/useApi'

const route = useRoute()
const router = useRouter()
const tree = ref({ layers: [] })
const selected = ref('')
const detail = ref(null)
const surveyHtml = ref('')
const surveyTitle = ref('')
const surveyLoading = ref(false)
const lineType = ref('B')
const product = ref(route.query.product || 'UAV')
const activeLayer = ref(route.query.layer || '')
const expandedLayer = ref('')
const surveyRefs = ref([])
const citeChart = ref(null)
let chartInst = null

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

const sectionTitle = computed(() =>
  activeLayer.value ? layerTitle.value : '六大类技术树总览')

const sectionSubtitle = computed(() =>
  activeLayer.value
    ? '技术点沿枝干两侧展开 · 右侧查看该技术点 survey'
    : '点击大类节点展开技术点；点击技术点进入 survey · 点击下方卡片进入该大类详情')

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

function chainQuery(extra = {}) {
  return { tab: 'tech_tree', product: product.value, ...extra }
}

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

/** 画布内联：点击层节点展开/收起技术点 */
function onCanvasBranchClick(layerId) {
  expandedLayer.value = expandedLayer.value === layerId ? '' : layerId
}

/** 画布：点击技术点进入 survey 详情 */
async function onCanvasLeafClick(techId, layerId) {
  const layer = layerId || expandedLayer.value
  if (!layer) return
  activeLayer.value = layer
  expandedLayer.value = ''
  router.replace({ path: '/chain', query: chainQuery({ layer, tech: techId }) })
  await selectPoint(techId, { skipRouter: true })
}

/** 底部卡片：进入该层详情页 */
function onLayerCardClick(layerId) {
  activeLayer.value = layerId
  selected.value = ''
  detail.value = null
  surveyHtml.value = ''
  surveyTitle.value = ''
  surveyRefs.value = []
  expandedLayer.value = ''
  router.replace({ path: '/chain', query: chainQuery({ layer: layerId }) })
}

function clearLayer() {
  activeLayer.value = ''
  selected.value = ''
  detail.value = null
  surveyHtml.value = ''
  surveyTitle.value = ''
  surveyRefs.value = []
  expandedLayer.value = ''
  router.replace({ path: '/chain', query: chainQuery() })
}

async function selectPoint(tid, { skipRouter = false } = {}) {
  if (!skipRouter) {
    router.replace({
      path: '/chain',
      query: chainQuery({ layer: activeLayer.value, tech: tid }),
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
    surveyTitle.value = s.title || 'survey 摘要'
    surveyHtml.value = marked.parse(s.excerpt_md || s.content_md || '')
    surveyRefs.value = s.references || []
  } catch {
    surveyTitle.value = 'survey 摘要'
    surveyHtml.value = '<p>暂无 survey 文稿</p>'
  }
  surveyLoading.value = false
}

onMounted(async () => {
  tree.value = await apiGet('/api/tech/tree')
  if (route.query.layer) activeLayer.value = String(route.query.layer)
  const tid = route.query.tech
  if (tid) await selectPoint(String(tid), { skipRouter: true })
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
.back-btn {
  background: none;
  border: none;
  padding: 0;
  margin-bottom: 12px;
  color: var(--ruc-red);
  font-size: 0.82rem;
  cursor: pointer;
}
.back-btn:hover { color: var(--ruc-red-dark); }
.tree-overview-wrap {
  border-radius: 14px;
  background: var(--surface-panel);
  border: 1px solid var(--border);
  transition: box-shadow 0.35s ease, border-color 0.35s ease;
  overflow: hidden;
}
.tree-overview-wrap.is-expanded {
  border-color: rgba(174, 13, 40, 0.22);
  box-shadow: 0 8px 32px rgba(174, 13, 40, 0.08);
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
.layer-card.active {
  border-color: rgba(174, 13, 40, 0.35);
  background: var(--ruc-red-muted);
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
.lc-count { font-size: 1.25rem; font-weight: 800; font-variant-numeric: tabular-nums; }
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
.layer-workspace { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: stretch; min-height: 500px; }
.tree-pane { min-width: 0; min-height: 460px; display: flex; align-items: stretch; }
.survey-pane { min-width: 0; overflow: hidden; }
.overview-layout { display: flex; flex-direction: column; gap: 16px; }
.layer-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
.mini-chart { width: 100%; height: 100px; min-height: 100px; }
.case-pane-enter-active, .case-pane-leave-active, .case-fade-enter-active, .case-fade-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}
.case-pane-enter-from { opacity: 0; transform: translateY(10px); }
.case-pane-leave-to { opacity: 0; transform: translateY(-8px); }
.case-fade-enter-from, .case-fade-leave-to { opacity: 0; }
@media (max-width: 960px) {
  .layer-workspace { grid-template-columns: 1fr; }
  .layer-grid { grid-template-columns: repeat(2, 1fr); }
  .metrics-bar { grid-template-columns: repeat(2, 1fr); }
  .mini-chart { grid-column: 1 / -1; }
}
@media (max-width: 640px) {
  .layer-grid { grid-template-columns: 1fr; }
}
</style>
