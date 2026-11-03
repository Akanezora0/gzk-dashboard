<template>
  <PageShell
    emphasis
    :title="PAGE_META.case.title"
    :intro="PAGE_META.case.intro"
    :breadcrumb="PAGE_META.case.breadcrumb"
  >
    <section class="case-placeholder">
      <div class="placeholder-inner">
        <span class="placeholder-tag">案例展示</span>
        <h2 class="placeholder-title">产品案例专题 · 筹备中</h2>
        <p class="placeholder-desc">
          本模块将结合产品专题工作，展示 UAV / eVTOL / 通航等载体产品的技术演进与产业证据。
          技术树与 Survey 内容已并入
          <router-link to="/chain?tab=tech_tree" class="inline-link">证据链 · 技术树</router-link>
          子页。
        </p>
      </div>
    </section>
  </PageShell>
</template>

<script setup>
import PageShell from '../components/layout/PageShell.vue'
import { PAGE_META } from '../constants/site.js'
</script>

<style scoped>
.case-placeholder {
  min-height: 360px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
}
.placeholder-inner {
  max-width: 520px;
  text-align: center;
  padding: 36px 32px;
  border-radius: 16px;
  background: var(--surface-card);
  border: 1px dashed var(--border);
}
.placeholder-tag {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--ruc-red);
  margin-bottom: 12px;
}
.placeholder-title {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text);
  margin: 0 0 14px;
}
.placeholder-desc {
  font-size: 0.9rem;
  color: var(--muted);
  line-height: 1.65;
  margin: 0;
}
.inline-link {
  color: var(--ruc-red);
  font-weight: 600;
  text-decoration: none;
}
.inline-link:hover { text-decoration: underline; }
</style>
