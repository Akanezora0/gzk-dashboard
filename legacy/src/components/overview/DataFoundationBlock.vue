<template>
  <div class="data-foundation">
    <!-- 核心四项（与图表同源 Top 4） -->
    <div class="tier-primary">
      <router-link
        v-for="item in primaryCards"
        :key="item.type"
        :to="item.route"
        class="primary-card"
        :class="`accent-${item.accent}`"
      >
        <span class="primary-label">{{ item.label }}</span>
        <span class="primary-count">{{ fmtCount(item.count) }}</span>
        <span class="primary-hint">{{ item.hint }}</span>
      </router-link>
    </div>

    <div class="viz-row">
      <DataCompositionChart :segments="compositionSegments" />
      <DataVolumeBars
        :items="volumeBarItems"
        title="数据源规模"
        subtitle="主要数据源记录规模 · 按规模降序"
        compact
      />
    </div>

    <!-- 数据源全景 -->
    <div class="tier-sources">
      <div class="sources-head">
        <h3 class="sources-title">数据源全景</h3>
        <p class="sources-sub">
          共 <strong>{{ dataSources.length }}</strong> 项数据源，覆盖
          <strong>{{ DATA_ARCHIVE.source_categories }}</strong> 类业务类别
        </p>
      </div>
      <div class="sources-grid">
        <router-link
          v-for="item in dataSources"
          :key="item.type"
          :to="item.route"
          class="source-cell"
        >
          <span class="source-cat" :class="`cat-${item.category}`">{{ item.category }}</span>
          <span class="source-label">{{ item.label }}</span>
          <span class="source-count">{{ fmtCount(item.count) }}</span>
        </router-link>
      </div>
    </div>

    <!-- 数据体量 -->
    <div class="archive-strip">
      <span v-for="a in archiveMeta" :key="a.label" class="archive-item">
        <span class="archive-val">{{ a.val }}</span>
        <span class="archive-label">{{ a.label }}</span>
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { fmtCount } from '../../composables/useApi'
import {
  DATA_ARCHIVE,
  overviewPrimaryCards,
  overviewDataSources,
  overviewVolumeBarItems,
  overviewCompositionSegments,
} from '../../constants/dataCatalog.js'
import DataCompositionChart from './DataCompositionChart.vue'
import DataVolumeBars from './DataVolumeBars.vue'

const props = defineProps({
  catalog: { type: Array, default: () => [] },
})

const archiveMeta = computed(() => [
  { val: DATA_ARCHIVE.source_files, label: '业务数据文件' },
  { val: `约 ${DATA_ARCHIVE.volume_gb} GB`, label: '数据资源体量' },
  { val: DATA_ARCHIVE.structured_files, label: '结构化表文件' },
  { val: `${DATA_ARCHIVE.source_categories} 类`, label: '数据源类别' },
])

const dataSources = computed(() => overviewDataSources(props.catalog))
const primaryCards = computed(() => overviewPrimaryCards(props.catalog))
const volumeBarItems = computed(() => overviewVolumeBarItems(props.catalog))
const compositionSegments = computed(() => overviewCompositionSegments(props.catalog))
</script>

<style scoped>
.data-foundation { width: 100%; }

.tier-primary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-bottom: 20px;
}
.primary-card {
  padding: 22px 20px;
  border-radius: 14px;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 128px;
  background: var(--surface-card);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-shadow), var(--card-highlight);
  transition: transform 0.18s, box-shadow 0.18s, border-color 0.18s;
}
.primary-card:hover {
  transform: translateY(-3px);
  border-color: var(--card-border-strong);
  box-shadow: 0 8px 24px rgba(174, 13, 40, 0.08), var(--card-highlight);
}
.primary-card.accent-red { --num-color: var(--num-blue); }
.primary-card.accent-dark { --num-color: var(--num-violet); }
.primary-card.accent-amber { --num-color: var(--num-amber); }
.primary-card.accent-green { --num-color: var(--num-green); }

.primary-label {
  font-size: 0.86rem;
  color: var(--label-strong);
  font-weight: 600;
}
.primary-count {
  font-size: 2.1rem;
  font-weight: 800;
  color: var(--num-color, var(--text));
  font-variant-numeric: tabular-nums;
  line-height: 1.05;
}
.primary-hint {
  font-size: 0.72rem;
  color: var(--label-muted);
  margin-top: auto;
}

.viz-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 20px;
}

.tier-sources {
  padding: 18px 20px;
  border-radius: 14px;
  background: var(--surface-panel);
  border: 1px solid var(--card-border);
  box-shadow: var(--card-highlight);
  margin-bottom: 16px;
}
.sources-head {
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border);
}
.sources-title {
  margin: 0;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--ruc-red-dark);
  letter-spacing: 0.06em;
}
.sources-sub {
  margin: 6px 0 0;
  font-size: 0.75rem;
  color: var(--label-muted);
}
.sources-sub strong {
  color: var(--ruc-red);
  font-weight: 700;
}

.sources-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}
.source-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  border-radius: 8px;
  background: var(--surface-card);
  border: 1px solid var(--border);
  text-decoration: none;
  color: inherit;
  transition: background 0.12s, border-color 0.12s;
  min-height: 72px;
}
.source-cell:hover {
  background: var(--surface-card-hover);
  border-color: rgba(174, 13, 40, 0.25);
}
.source-cat {
  align-self: flex-start;
  font-size: 0.62rem;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 999px;
  letter-spacing: 0.04em;
}
.cat-基金 { background: rgba(174, 13, 40, 0.1); color: #ae0d28; }
.cat-论文 { background: rgba(26, 77, 122, 0.1); color: #1a4d7a; }
.cat-专利 { background: rgba(180, 83, 9, 0.1); color: #b45309; }
.cat-政策 { background: rgba(120, 113, 108, 0.12); color: #57534e; }
.cat-主体 { background: rgba(45, 106, 79, 0.1); color: #2d6a4f; }
.cat-软著 { background: rgba(45, 106, 79, 0.1); color: #2d6a4f; }
.cat-新闻 { background: rgba(168, 162, 158, 0.15); color: #78716c; }
.cat-产品 { background: rgba(13, 148, 136, 0.1); color: #0d9488; }
.cat-项目 { background: rgba(99, 102, 241, 0.1); color: #6366f1; }
.cat-词典 { background: rgba(124, 58, 237, 0.1); color: #7c3aed; }
.cat-其他 { background: rgba(168, 162, 158, 0.12); color: #78716c; }

.source-label {
  font-size: 0.76rem;
  color: var(--label-muted);
  font-weight: 500;
  line-height: 1.3;
  flex: 1;
}
.source-count {
  font-size: 1rem;
  font-weight: 800;
  color: var(--num-blue);
  font-variant-numeric: tabular-nums;
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
}
.archive-item {
  display: flex;
  align-items: baseline;
  gap: 6px;
  font-size: 0.72rem;
}
.archive-val {
  color: var(--muted);
  font-weight: 600;
}
.archive-label {
  color: #a8a29e;
}

@media (max-width: 1100px) {
  .sources-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 960px) {
  .viz-row { grid-template-columns: 1fr; }
  .tier-primary { grid-template-columns: repeat(2, 1fr); }
  .sources-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 560px) {
  .sources-grid { grid-template-columns: 1fr; }
}
</style>
