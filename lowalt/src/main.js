import { createApp, nextTick } from 'vue'
import { createPinia } from 'pinia'
import DataVVue3 from '@kjgl77/datav-vue3'
import { createRouter, createMemoryHistory } from 'vue-router'
import App from './App.vue'
import '@kjgl77/datav-vue3/dist/style.css'
import '@legacy/styles/screen-theme.scss'
import './embed.css'

const pages = new Set(['data', 'evolution', 'chain', 'cases'])
const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/data', component: () => import('@legacy/views/DataHub.vue') },
    { path: '/evolution', component: () => import('@legacy/components/case/TechTreePanel.vue') },
    { path: '/chain', component: () => import('@legacy/views/ChainHub.vue') },
    { path: '/cases', component: () => import('@legacy/views/CasePlaceholder.vue') },
    { path: '/case', redirect: to => ({ path: to.query.layer || to.query.tech || to.query.view ? '/evolution' : '/cases', query: to.query }) },
    { path: '/case/low-altitude', redirect: to => ({ path: '/evolution', query: to.query }) },
    { path: '/contribution', redirect: to => ({ path: '/chain', query: { ...to.query, tab: 'contribution' } }) },
    { path: '/data/:type', redirect: to => ({ path: '/data', query: { ...to.query, tab: to.params.type } }) },
    { path: '/overview', component: { template: '<div />' } },
    { path: '/:pathMatch(.*)*', redirect: '/data' },
  ],
})

function parentRoute(to) {
  const page = to.path.slice(1)
  if (pages.has(page)) return { page, query: { ...to.query } }
  return null
}

function send(message) {
  if (window.parent !== window) window.parent.postMessage({ channel: 'gzk-low-altitude', ...message }, window.location.origin)
}

router.beforeEach(to => {
  if (to.path === '/chain' && to.query.tab === 'tech_tree') {
    return { path: '/evolution', query: { ...to.query, tab: undefined } }
  }
  if (to.path === '/case' || to.path === '/case/low-altitude') {
    const tech = to.query.layer || to.query.tech || to.query.view || to.path.endsWith('/low-altitude')
    return { path: tech ? '/evolution' : '/cases', query: { ...to.query, tab: undefined } }
  }
  if (to.path === '/contribution') return { path: '/chain', query: { ...to.query, tab: 'contribution' } }
  if (to.path.startsWith('/data/')) return { path: '/data', query: { ...to.query, tab: to.path.split('/')[2] } }
  if (to.path === '/overview') {
    send({ type: 'navigate', page: 'overview', query: {} })
    return false
  }
})

let applyingParent = 0
let ready = false
router.afterEach(async to => {
  await nextTick()
  const value = parentRoute(to)
  if (ready && !applyingParent && value) send({ type: 'navigate', ...value })
})

window.addEventListener('message', async event => {
  if (event.source !== window.parent || event.origin !== window.location.origin) return
  const message = event.data
  if (message?.channel !== 'gzk-low-altitude' || message.type !== 'set-route' || !pages.has(message.page)) return
  const target = { path: '/' + message.page, query: message.query || {} }
  if (router.resolve(target).fullPath === router.currentRoute.value.fullPath) return
  applyingParent += 1
  try { await router.replace(target) }
  finally { applyingParent -= 1 }
})

const initial = new URLSearchParams(window.location.search)
const page = pages.has(initial.get('page')) ? initial.get('page') : 'data'
initial.delete('page')
async function start() {
  await router.replace({ path: '/' + page, query: Object.fromEntries(initial) })
  await router.isReady()
  const app = createApp(App)
  app.use(createPinia()).use(router).use(DataVVue3).mount('#app')
  ready = true
  send({ type: 'ready' })
}
start()
