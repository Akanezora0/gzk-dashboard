<template>
  <div class="screen-root">
    <header class="screen-header">
      <div class="header-glow" aria-hidden="true"></div>
      <div class="header-frame">
        <div class="header-line header-line--top"></div>
        <div class="header-content">
          <h1>
            <span class="title-deco title-deco--l" aria-hidden="true"></span>
            <span class="title-text">{{ SITE_TITLE }}</span>
            <span class="title-deco title-deco--r" aria-hidden="true"></span>
          </h1>
          <p class="sub">
            {{ SITE_SUBTITLE }}
            · 更新：<time>{{ updateTime }}</time>
          </p>
        </div>
        <div class="header-line header-line--bottom"></div>
      </div>
    </header>
    <NavBar />
    <main class="screen-main">
      <router-view />
    </main>
    <footer class="screen-footer">
      <router-link to="/quality" class="footer-link">数据质量与进展</router-link>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import NavBar from './components/NavBar.vue'
import { apiGet } from './composables/useApi'
import { SITE_TITLE, SITE_SUBTITLE } from './constants/site.js'

const updateTime = ref('—')

onMounted(async () => {
  try {
    const d = await apiGet('/api/overview')
    updateTime.value = d.update_time || '—'
  } catch { /* ignore */ }
})
</script>

<style scoped>
.screen-header {
  position: relative;
  text-align: center;
  margin-bottom: 1.25rem;
  padding: 0.5rem 1rem 0;
}

.header-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -55%);
  width: min(720px, 90vw);
  height: 120px;
  background: radial-gradient(ellipse, rgba(174, 13, 40, 0.1) 0%, transparent 70%);
  pointer-events: none;
  animation: headerPulse 4s ease-in-out infinite;
}

@keyframes headerPulse {
  0%, 100% { opacity: 0.55; transform: translate(-50%, -55%) scale(1); }
  50% { opacity: 1; transform: translate(-50%, -55%) scale(1.06); }
}

.header-frame {
  position: relative;
  max-width: 1360px;
  margin: 0 auto;
  padding: 1.5rem 0 1.25rem;
}

.header-line {
  height: 2px;
  margin: 0 auto;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(174, 13, 40, 0.15) 15%,
    rgba(174, 13, 40, 0.75) 50%,
    rgba(174, 13, 40, 0.15) 85%,
    transparent 100%
  );
  box-shadow: 0 0 12px rgba(174, 13, 40, 0.15);
}
.header-line--top { margin-bottom: 1.35rem; }
.header-line--bottom {
  margin-top: 1.15rem;
  width: 45%;
  opacity: 0.75;
  animation: lineShimmer 3s ease-in-out infinite;
}

@keyframes lineShimmer {
  0%, 100% { opacity: 0.5; width: 42%; }
  50% { opacity: 0.9; width: 48%; }
}

.header-content {
  padding: 0 1.5rem;
}

.screen-header h1 {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin: 0;
  line-height: 1.2;
}

.title-text {
  font-size: clamp(2rem, 4.2vw, 2.85rem);
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--ruc-red-dark);
}

@keyframes titleGradient {
  0% { background-position: 0% center; }
  100% { background-position: 200% center; }
}

.title-deco {
  display: block;
  width: 28px;
  height: 28px;
  border: 2px solid rgba(174, 13, 40, 0.45);
  flex-shrink: 0;
  opacity: 0.85;
}
.title-deco--l {
  border-right: none;
  border-bottom: none;
  transform: rotate(-8deg);
}
.title-deco--r {
  border-left: none;
  border-top: none;
  transform: rotate(-8deg);
}

.screen-header .sub {
  color: var(--muted);
  font-size: 0.88rem;
  margin-top: 0.85rem;
  line-height: 1.65;
  letter-spacing: 0.02em;
}
.screen-header .sub time {
  color: var(--ruc-red);
  font-weight: 500;
}

.screen-main {
  max-width: 1360px;
  margin: 0 auto;
  padding: 0 2rem 2.5rem;
}
.screen-footer {
  max-width: 1360px;
  margin: 0 auto;
  padding: 12px 1rem 20px;
  text-align: center;
  font-size: 0.72rem;
  color: var(--muted);
  border-top: 1px dashed var(--border);
}
.footer-link {
  color: var(--muted);
  text-decoration: none;
}
.footer-link:hover { color: var(--ruc-red); }

@media (max-width: 640px) {
  .title-deco { display: none; }
  .title-text { letter-spacing: 0.04em; }
}
</style>
