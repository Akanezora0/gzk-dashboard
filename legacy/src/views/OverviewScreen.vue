<template>
  <div class="overview">
    <div v-if="loading" class="state-msg">加载中…</div>
    <div v-else-if="error" class="state-msg error">{{ error }}</div>

    <template v-else>
      <SectionBlock
        tag="数据底座"
        title="多源基础数据"
        subtitle="已汇聚基金、论文、专利、政策、软著、新闻等多类广泛数据，形成可扩展的多源异构数据底座，可支撑技术词典构建、证据链关联与基金贡献评估等分析应用。"
        tone="data"
      >
        <template #action>
          <router-link to="/data" class="section-link">进入低空经济领域数据</router-link>
        </template>
        <DataFoundationBlock :catalog="dataCatalog" />
      </SectionBlock>

      <SectionBlock
        tag="证据链"
        title="证据链"
        subtitle="从基金投入到论文专利，再到技术词典与示范产品，构建可验证的多源证据链。"
        tone="chain"
      >
        <template #action>
          <router-link to="/chain" class="section-link">进入证据链分析</router-link>
        </template>
        <ChainEvidenceBlock
          :contrib="contrib"
          :progress="progress"
          :chain-status="chainStatus"
        />
      </SectionBlock>

      <SectionBlock
        tag="技术树"
        title="低空经济技术演进"
        subtitle="以六大类技术树组织 33 个技术点；点击进入该大类演进脉络与技术点详情。"
        tone="case"
      >
        <template #action>
          <router-link to="/chain?tab=tech_tree" class="section-link">进入技术树</router-link>
        </template>

        <EvolutionTree :compact="true" :interactive="true" :product="activeProduct" class="overview-tree" />

        <ProductShowcase
          v-model="activeProduct"
          :workflow="workflow"
          :progress="progress"
        />
      </SectionBlock>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import SectionBlock from '../components/layout/SectionBlock.vue'
import DataFoundationBlock from '../components/overview/DataFoundationBlock.vue'
import ChainEvidenceBlock from '../components/overview/ChainEvidenceBlock.vue'
import EvolutionTree from '../components/case/EvolutionTree.vue'
import ProductShowcase from '../components/case/ProductShowcase.vue'
import { DEFAULT_DATA_CATALOG } from '../constants/dataCatalog.js'
import { apiGet } from '../composables/useApi'

const loading = ref(true)
const error = ref('')
const data = ref(null)
const activeProduct = ref('UAV')

const chainStatus = computed(() => data.value?.chain_status ?? [])
const dataCatalog = computed(() => {
  const c = data.value?.data_catalog
  return c?.length ? c : DEFAULT_DATA_CATALOG
})
const workflow = computed(() => data.value?.workflow_highlights ?? {})
const contrib = computed(() => data.value?.contribution_summary ?? {})
const progress = computed(() => data.value?.progress ?? {})

onMounted(async () => {
  try {
    data.value = await apiGet('/api/overview')
    loading.value = false
  } catch (e) {
    error.value = String(e.message || e)
    loading.value = false
  }
})
</script>

<style scoped>
.overview {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.state-msg {
  text-align: center;
  padding: 80px 0;
  color: #64748b;
  font-size: 1rem;
}
.state-msg.error { color: #f87171; }

.overview-tree {
  display: block;
}

.section-link {
  display: inline-flex;
  align-items: center;
  padding: 10px 18px;
  border-radius: 999px;
  background: var(--ruc-red-muted);
  border: 1px solid rgba(174, 13, 40, 0.25);
  color: var(--ruc-red-dark);
  font-size: 0.85rem;
  text-decoration: none;
  transition: background 0.15s, border-color 0.15s;
}
.section-link:hover {
  background: rgba(174, 13, 40, 0.18);
  border-color: var(--ruc-red);
  color: var(--ruc-red-dark);
}
</style>
