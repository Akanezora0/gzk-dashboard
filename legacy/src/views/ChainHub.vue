<template>
  <PageShell
    emphasis
    :title="PAGE_META.chain.title"
    :intro="PAGE_META.chain.intro"
    :breadcrumb="PAGE_META.chain.breadcrumb"
  >
    <div class="tab-bar">
      <button
        v-for="t in CHAIN_TABS"
        :key="t.id"
        type="button"
        class="tab-btn"
        :class="{ active: activeTab === t.id }"
        @click="switchTab(t.id)"
      >
        <span class="tab-label">{{ t.label }}</span>
        <span v-if="tabBadge(t.id)" class="tab-badge">{{ tabBadge(t.id) }}</span>
      </button>
    </div>

    <Transition
      name="tab-pane"
      mode="out-in"
      @before-leave="onTabLeave"
      @after-enter="onTabReady"
    >
      <div v-if="profile" :key="activeTab" class="tab-pane">
        <section class="chain-hero">
          <div class="hero-main">
            <span class="hero-tag">{{ profile.heroTag }}</span>
            <h1 class="hero-title">{{ profile.heroTitle }}</h1>
            <p class="hero-desc">{{ profile.heroDesc }}</p>
            <ul v-if="profile.heroBullets?.length" class="hero-bullets">
              <li v-for="(item, i) in profile.heroBullets" :key="i">{{ item }}</li>
            </ul>
            <p v-if="profile.insight" class="hero-insight">{{ profile.insight }}</p>
          </div>
          <div class="hero-highlights">
            <div
              v-for="(h, i) in profile.highlights"
              :key="i"
              class="highlight-chip"
            >
              <span class="hc-val" :style="{ color: h.color || 'var(--ruc-red)' }">{{ h.value }}</span>
              <span class="hc-label">{{ h.label }}</span>
              <span v-if="h.hint" class="hc-hint">{{ h.hint }}</span>
            </div>
          </div>
        </section>

        <!-- 证据链总览 -->
        <template v-if="activeTab === 'overview'">
          <section class="flow-section">
            <ChainFlowVisual
              :chain-status="chainStatus"
              :contrib="contrib"
              :progress="progress"
            />
          </section>

          <section class="cards-section">
            <div class="section-head">
              <h2 class="section-title">四条可验证链路</h2>
              <p class="section-sub">点击卡片进入对应细分探索</p>
            </div>
            <ChainLinkCards
              :chains="chainStatus"
              :active="selectedChainType"
              @select="onChainCardSelect"
            />
          </section>

          <section class="pipeline-section">
            <div class="section-head">
              <h2 class="section-title">证据构建过程</h2>
              <p class="section-sub">从多源采集到贡献评估的五步流程</p>
            </div>
            <ChainPipeline :steps="CHAIN_PIPELINE" />
          </section>

          <div class="nav-hints">
            <button type="button" class="nav-hint" @click="switchTab('tech_tree')">
              <span class="nh-label">下一步</span>
              <span class="nh-title">技术树 · 33 技术点 →</span>
            </button>
            <button type="button" class="nav-hint" @click="switchTab('contribution')">
              <span class="nh-label">深入分析</span>
              <span class="nh-title">基金贡献度 →</span>
            </button>
          </div>
        </template>

        <!-- 技术树（原案例展示技术内容） -->
        <template v-else-if="activeTab === 'tech_tree'">
          <TechTreePanel />
        </template>

        <!-- 基金→论文→技术 -->
        <template v-else-if="activeTab === 'fund_paper'">
          <ScreenPanel
            title="基金—论文—技术 证据图"
            subtitle="Skills 低空文献池 · NSFC 直连完整链 · 力导向布局"
            :body-style="{ minHeight: '560px' }"
          >
            <ChainEvidenceExplorer
              ref="fundExplorer"
              chain-type="fund_paper_tech"
              :aggregate="false"
              :height="560"
            />
          </ScreenPanel>
        </template>

        <!-- 专利→技术 -->
        <template v-else-if="activeTab === 'patent'">
          <ScreenPanel
            title="专利—技术 证据图"
            subtitle="排除过宽词条 · 各技术点均匀抽样 · 力导向布局"
            :body-style="{ minHeight: '560px' }"
          >
            <ChainEvidenceExplorer
              ref="patentExplorer"
              chain-type="patent_tech"
              :aggregate="false"
              :height="560"
            />
          </ScreenPanel>
        </template>

        <!-- 基金贡献度 -->
        <template v-else>
          <ContributionPanel ref="contribPanel" />
        </template>

        <div v-if="DATA_SOURCE_FOOTNOTE.length" class="archive-strip">
          <div v-for="a in DATA_SOURCE_FOOTNOTE" :key="a.label" class="archive-item">
            <span class="archive-val">{{ a.value }}</span>
            <span class="archive-label">{{ a.label }}</span>
          </div>
        </div>
      </div>
    </Transition>
  </PageShell>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PageShell from '../components/layout/PageShell.vue'
import ScreenPanel from '../components/screen/ScreenPanel.vue'
import ChainFlowVisual from '../components/overview/ChainFlowVisual.vue'
import ChainLinkCards from '../components/chain/ChainLinkCards.vue'
import ChainEvidenceExplorer from '../components/chain/ChainEvidenceExplorer.vue'
import ChainPipeline from '../components/chain/ChainPipeline.vue'
import ContributionPanel from '../components/chain/ContributionPanel.vue'
import TechTreePanel from '../components/case/TechTreePanel.vue'
import { PAGE_META, CHAIN_TABS } from '../constants/site.js'
import { CHAIN_TAB_PROFILES, CHAIN_PIPELINE, DATA_SOURCE_FOOTNOTE } from '../constants/chainHubProfiles.js'
import { apiGet, fmtCount } from '../composables/useApi'

const route = useRoute()
const router = useRouter()
const activeTab = ref(normalizeTab(route.query.tab))
const chainStatus = ref([])
const contrib = ref({})
const progress = ref({})
const selectedChainType = ref('')

const fundExplorer = ref(null)
const patentExplorer = ref(null)
const contribPanel = ref(null)

const profile = computed(() => CHAIN_TAB_PROFILES[activeTab.value] || CHAIN_TAB_PROFILES.overview)

function normalizeTab(raw) {
  const id = raw || 'overview'
  if (CHAIN_TABS.some(t => t.id === id)) return id
  const legacy = { fund_paper: 'fund_paper', patent: 'patent', contribution: 'contribution' }
  return legacy[id] || 'overview'
}

function tabBadge(id) {
  if (id === 'overview' || id === 'tech_tree') return null
  const tab = CHAIN_TABS.find(t => t.id === id)
  if (!tab?.chainType) return null
  const ch = chainStatus.value.find(s => s.chain_type === tab.chainType)
  return ch ? fmtCount(ch.count) : null
}

function switchTab(id) {
  activeTab.value = id
  selectedChainType.value = ''
  const q = { tab: id }
  if (id === 'tech_tree') {
    if (route.query.layer) q.layer = route.query.layer
    if (route.query.tech) q.tech = route.query.tech
    if (route.query.product) q.product = route.query.product
  }
  router.replace({ path: '/chain', query: q })
}

function onChainCardSelect(ch) {
  selectedChainType.value = ch.chain_type
  const map = {
    fund_paper_tech: 'fund_paper',
    patent_tech: 'patent',
    paper_tech: 'fund_paper',
    fund_patent_tech: 'patent',
  }
  switchTab(map[ch.chain_type] || 'overview')
}

function onTabLeave() { /* charts dispose internally */ }

function onTabReady() {
  nextTick(() => {
    requestAnimationFrame(() => {
      ;[fundExplorer, patentExplorer].forEach(r => {
        const exp = r?.value
        if (exp?.mountAndRender) exp.mountAndRender()
        else if (exp?.resizeChart) exp.resizeChart()
      })
      if (activeTab.value === 'contribution' && contribPanel.value?.resizeCharts) {
        contribPanel.value.resizeCharts()
      }
    })
  })
}

watch(() => route.query.tab, v => {
  activeTab.value = normalizeTab(v)
})

onMounted(async () => {
  try {
    const d = await apiGet('/api/overview')
    chainStatus.value = d.chain_status || []
    contrib.value = d.contribution_summary || {}
    progress.value = d.progress || {}
  } catch { /* ignore */ }
})
</script>

<style scoped>
.tab-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
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
  border-radius: 999px;
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
.tab-badge { font-size: 0.72rem; font-weight: 700; color: var(--muted); font-variant-numeric: tabular-nums; }
.tab-btn.active .tab-badge { color: var(--ruc-red); }

.tab-pane-enter-active, .tab-pane-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.tab-pane-enter-from { opacity: 0; transform: translateY(8px); }
.tab-pane-leave-to { opacity: 0; transform: translateY(-6px); }

.chain-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(0, 1fr);
  gap: 24px 28px;
  padding: 26px 28px;
  margin-bottom: 18px;
  border-radius: 16px;
  background: var(--surface-card);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow);
  align-items: stretch;
}
.hero-main {
  display: flex;
  flex-direction: column;
  gap: 0;
  min-height: 100%;
}
.hero-tag {
  display: inline-block;
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--ruc-red);
  margin-bottom: 10px;
}
.hero-title {
  font-size: clamp(1.65rem, 2.8vw, 2.05rem);
  font-weight: 800;
  color: var(--text);
  line-height: 1.28;
  margin: 0 0 14px;
  letter-spacing: -0.02em;
}
.hero-desc {
  font-size: 0.95rem;
  color: var(--muted);
  line-height: 1.65;
  margin: 0;
}
.hero-bullets {
  list-style: none;
  margin: 18px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.hero-bullets li {
  position: relative;
  padding-left: 14px;
  font-size: 0.86rem;
  line-height: 1.55;
  color: #4a4540;
}
.hero-bullets li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.55em;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--ruc-red);
  opacity: 0.75;
}
.hero-insight { font-size: 0.78rem; color: #a8a29e; line-height: 1.5; margin: 12px 0 0; font-style: italic; }
.hero-highlights {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  align-content: center;
}
.highlight-chip {
  padding: 16px 14px;
  border-radius: 12px;
  background: var(--surface-panel);
  border: 1px solid var(--border);
  text-align: center;
}
.hc-val {
  display: block;
  font-size: 1.9rem;
  font-weight: 900;
  font-variant-numeric: tabular-nums;
  line-height: 1.15;
  letter-spacing: -0.02em;
}
.hc-label { display: block; font-size: 0.76rem; font-weight: 600; color: var(--text); margin-top: 6px; }
.hc-hint { display: block; font-size: 0.66rem; color: var(--muted); margin-top: 2px; }

.section-title { font-size: 1rem; font-weight: 800; color: var(--text); margin: 0 0 4px; }
.section-sub { font-size: 0.82rem; color: var(--muted); margin: 0; font-weight: 500; }
.flow-section, .cards-section { margin-bottom: 18px; }
.pipeline-section { margin: 4px 0 16px; }
.section-head { margin-bottom: 12px; }

.nav-hints {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 18px;
}
.nav-hint {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 16px 18px;
  border-radius: 12px;
  background: var(--surface-card);
  border: 1px solid var(--border);
  cursor: pointer;
  text-align: left;
  transition: border-color 0.15s, transform 0.12s;
}
.nav-hint:hover {
  border-color: rgba(174, 13, 40, 0.3);
  transform: translateY(-2px);
}
.nh-label { font-size: 0.68rem; font-weight: 600; color: var(--muted); }
.nh-title { font-size: 0.92rem; font-weight: 700; color: var(--ruc-red-dark); }

.archive-strip {
  display: flex; flex-wrap: wrap; justify-content: center; gap: 20px;
  padding: 12px 16px; border-radius: 10px;
  background: var(--surface-panel); border: 1px dashed var(--border); margin-top: 8px;
}
.archive-val { color: var(--muted); font-weight: 600; }
.archive-label { color: #a8a29e; }

@media (max-width: 960px) {
  .chain-hero { grid-template-columns: 1fr; }
  .nav-hints { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .hero-highlights { grid-template-columns: 1fr; }
}
</style>
