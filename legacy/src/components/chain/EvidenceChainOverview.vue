<template>
  <div class="evidence-overview">
    <div class="q-block">
      <div class="q-head">
        <span class="q-text">成果推动力 · 多源证据链</span>
      </div>
      <div class="flow-pipeline">
        <div class="flow-stage">
          <div class="stage-label">成果入口</div>
          <div class="stage-card paper">
            <div class="sc-num">{{ fmtCount(papers) }}</div>
            <div class="sc-name">Skills 论文</div>
          </div>
          <div class="stage-card patent">
            <div class="sc-num">{{ fmtCount(patentLinks) }}</div>
            <div class="sc-name">专利—技术关联</div>
          </div>
        </div>
        <div class="flow-arrow">
          <span class="arrow-line"></span>
          <span class="arrow-label">命中<br>技术点</span>
        </div>
        <div class="flow-stage center">
          <div class="stage-label">技术词典</div>
          <div class="stage-card tech">
            <div class="sc-num">{{ techCount }}</div>
            <div class="sc-name">技术点</div>
            <div class="sc-sub">6 层 · 低空经济</div>
          </div>
        </div>
        <div class="flow-arrow">
          <span class="arrow-line"></span>
          <span class="arrow-label">支撑<br>产品</span>
        </div>
        <div class="flow-stage">
          <div class="stage-label">产业落地</div>
          <div class="stage-card product">
            <div class="sc-name">UAV · eVTOL · GA</div>
            <div class="sc-sub">战略性产品缩影</div>
          </div>
        </div>
      </div>

      <table class="chain-table">
        <thead>
          <tr>
            <th>证据链类型</th>
            <th>关联规模</th>
            <th>状态</th>
            <th>说明</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ch in chains" :key="ch.chain_type">
            <td>{{ ch.label }}</td>
            <td class="num">{{ fmtCount(ch.count) }}</td>
            <td><span class="status-tag" :class="ch.status">{{ statusLabel(ch.status) }}</span></td>
            <td class="note">{{ ch.note }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="q-block q3">
      <div class="q-head">
        <span class="q-text">基金贡献 · 三维评估</span>
      </div>
      <div class="contrib-layers">
        <div class="layer-group">
          <div class="lg-title">支撑范围</div>
          <div class="metric-row">
            <div class="metric-item">
              <div class="mi-val">{{ pct(contrib.funding_metadata_ratio) }}</div>
              <div class="mi-label">基金支撑论文占比</div>
            </div>
            <div class="metric-item">
              <div class="mi-val">{{ fmtCount(contrib.fund_paper_links) }}</div>
              <div class="mi-label">基金—论文关联</div>
            </div>
            <div class="metric-item">
              <div class="mi-val">{{ fmtCount(contrib.fund_projects) }}</div>
              <div class="mi-label">相关基金项目</div>
            </div>
          </div>
        </div>
        <div class="layer-group">
          <div class="lg-title">影响力度</div>
          <div class="metric-row">
            <div class="metric-item">
              <div class="mi-val">{{ pct(contrib.high_citation_ratio) }}</div>
              <div class="mi-label">高被引论文占比</div>
            </div>
            <div class="metric-item">
              <div class="mi-val">{{ fmtCount(contrib.patent_tech_links) }}</div>
              <div class="mi-label">专利—技术关联</div>
            </div>
          </div>
        </div>
        <div class="layer-group diffusion">
          <div class="lg-title">产业渗透</div>
          <div class="diffusion-note">跨节点复用、进入关键产品链等指标持续接入</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { fmtCount } from '../../composables/useApi'

defineProps({
  chains: { type: Array, default: () => [] },
  contrib: { type: Object, default: () => ({}) },
  papers: { type: Number, default: 0 },
  patentLinks: { type: Number, default: 0 },
  techCount: { type: Number, default: 33 },
})

function pct(v) { return v != null ? `${(v * 100).toFixed(1)}%` : '—' }

function statusLabel(s) {
  return { verified: '已验证', partial: '部分', candidate: '候选' }[s] || s
}
</script>

<style scoped>
.evidence-overview { display: flex; flex-direction: column; gap: 16px; }

.q-block {
  padding: 12px;
  background: rgba(10, 20, 40, 0.4);
  border-radius: 8px;
  border: 1px solid rgba(61, 139, 253, 0.12);
}

.q-head {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}
.q-id {
  font-size: 0.68rem;
  font-weight: 700;
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.15);
  padding: 2px 7px;
  border-radius: 4px;
}
.q-id.q3 { color: #22c55e; background: rgba(34, 197, 94, 0.15); }
.q-text { font-size: 0.82rem; font-weight: 600; color: #e2e8f0; }

.flow-pipeline {
  display: flex;
  align-items: stretch;
  gap: 4px;
  margin-bottom: 14px;
  padding: 8px 0;
}

.flow-stage {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.flow-stage.center { flex: 0.8; }

.stage-label {
  font-size: 0.65rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stage-card {
  width: 100%;
  padding: 10px 8px;
  border-radius: 6px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.stage-card.paper { background: rgba(61, 139, 253, 0.12); border-color: rgba(61, 139, 253, 0.3); }
.stage-card.patent { background: rgba(245, 158, 11, 0.1); border-color: rgba(245, 158, 11, 0.25); margin-top: 4px; }
.stage-card.tech { background: rgba(34, 197, 94, 0.12); border-color: rgba(34, 197, 94, 0.3); padding: 14px 8px; }
.stage-card.product { background: rgba(236, 72, 153, 0.1); border-color: rgba(236, 72, 153, 0.25); }

.sc-num { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; }
.sc-name { font-size: 0.72rem; color: #cbd5e1; margin-top: 2px; }
.sc-sub { font-size: 0.62rem; color: #64748b; margin-top: 2px; }

.flow-arrow {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 36px;
  flex-shrink: 0;
  padding-top: 18px;
}
.arrow-line {
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, rgba(61, 139, 253, 0.3), #3d8bfd);
  position: relative;
}
.arrow-line::after {
  content: '';
  position: absolute;
  right: -1px;
  top: -4px;
  border: 5px solid transparent;
  border-left-color: #3d8bfd;
}
.arrow-label {
  font-size: 0.58rem;
  color: #64748b;
  text-align: center;
  line-height: 1.3;
  margin-top: 4px;
}

.chain-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.72rem;
}
.chain-table th {
  text-align: left;
  color: #64748b;
  font-weight: 500;
  padding: 6px 8px;
  border-bottom: 1px solid rgba(42, 53, 72, 0.8);
}
.chain-table td {
  padding: 6px 8px;
  border-bottom: 1px solid rgba(42, 53, 72, 0.4);
  color: #94a3b8;
}
.chain-table td.num { color: #e2e8f0; font-weight: 600; }
.chain-table td.note { color: #64748b; font-size: 0.68rem; }

.status-tag {
  display: inline-block;
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 0.65rem;
}
.status-tag.verified { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.status-tag.partial { background: rgba(245, 158, 11, 0.15); color: #f59e0b; }
.status-tag.candidate { background: rgba(100, 116, 139, 0.2); color: #94a3b8; }

.contrib-layers {
  display: grid;
  grid-template-columns: 1fr 1fr 0.7fr;
  gap: 10px;
}
.layer-group {
  padding: 10px;
  background: rgba(15, 30, 55, 0.5);
  border-radius: 6px;
}
.lg-title {
  font-size: 0.72rem;
  font-weight: 600;
  color: #3d8bfd;
  margin-bottom: 8px;
}
.metric-row { display: flex; flex-direction: column; gap: 8px; }
.metric-item { text-align: center; }
.mi-val { font-size: 1rem; font-weight: 700; color: #e2e8f0; }
.mi-label { font-size: 0.65rem; color: #64748b; margin-top: 2px; }
.diffusion-note { font-size: 0.68rem; color: #64748b; line-height: 1.5; padding-top: 4px; }

@media (max-width: 900px) {
  .flow-pipeline { flex-direction: column; }
  .flow-arrow { width: 100%; padding: 0; flex-direction: row; }
  .arrow-line { width: 60%; }
  .contrib-layers { grid-template-columns: 1fr; }
}
</style>
