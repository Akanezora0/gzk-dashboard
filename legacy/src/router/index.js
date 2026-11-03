import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/overview' },
  { path: '/overview', name: 'overview', component: () => import('../views/OverviewScreen.vue') },

  { path: '/data', name: 'data', component: () => import('../views/DataHub.vue') },
  { path: '/data/:type', redirect: to => ({ path: '/data', query: { tab: to.params.type } }) },

  { path: '/chain', name: 'chain', component: () => import('../views/ChainHub.vue') },
  { path: '/contribution', redirect: to => ({ path: '/chain', query: { tab: 'contribution', ...to.query } }) },

  { path: '/case', name: 'case', component: () => import('../views/CasePlaceholder.vue'),
    beforeEnter(to) {
      const q = to.query
      if (q.layer || q.tech || q.view) {
        return { path: '/chain', query: { tab: 'tech_tree', ...q } }
      }
    },
  },
  { path: '/case/low-altitude', redirect: to => ({ path: '/chain', query: { tab: 'tech_tree', ...to.query } }) },

  { path: '/quality', name: 'quality', component: () => import('../views/QualityMonitor.vue') },
]

export default createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    // 同一路径仅 query 变化（如 /data?tab=）时保持滚动位置
    if (to.path === from.path && to.fullPath !== from.fullPath) {
      return false
    }
    return { top: 0 }
  },
})
