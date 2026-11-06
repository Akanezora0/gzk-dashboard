import '../../shared/interactions.css'
import {createApp} from 'vue'
import {createRouter,createWebHistory} from 'vue-router'
import App from './App.vue'
import './style.css'
import './shell.css'
import './refinement.css'
import './presentation.css'
import '../../shared/surfaces.css'
const Empty={template:'<div />'}
const domainPages=['data','evolution','chain','cases']
const router=createRouter({history:createWebHistory(),routes:[{path:'/',redirect:'/home'},{path:'/case',redirect:to=>({path:'/cases',query:to.query})},{path:'/foundation',redirect:to=>({path:'/overview',query:to.query,hash:'#sources'})},...['home','overview',...domainPages].map(name=>({path:`/${name}`,name,component:Empty})),{path:'/:pathMatch(.*)*',redirect:'/home'}],scrollBehavior:(to,from)=>to.hash?{el:to.hash,top:100}:to.path===from.path&&to.query.domain===from.query.domain?false:{top:0}})
router.beforeEach((to,from)=>{
 if(to.path==='/data'&&to.query.view==='catalog')return {path:'/overview',query:{kind:to.query.kind,source:to.query.source},hash:'#sources'}
 if(to.path==='/chain'&&['tech_tree','evolution'].includes(to.query.tab))return {path:'/evolution',query:{...to.query,tab:undefined}}
 if(domainPages.includes(String(to.name))){
   const current=to.query.domain
   if(!['ai','lowalt'].includes(current))return {...to,query:{...to.query,domain:['ai','lowalt'].includes(from.query.domain)?from.query.domain:sessionStorage.getItem('gzk-research-domain')==='lowalt'?'lowalt':'ai'},replace:true}
   sessionStorage.setItem('gzk-research-domain',current)
 }
})
router.afterEach(to=>{const labels={home:'首页',overview:'数据总览',data:'领域数据',evolution:'技术演进',chain:'证据链',cases:'案例专题'};document.title=`${labels[to.name]||'首页'} · 基础研究数据与评估系统`})
createApp(App).use(router).mount('#app')
