import path from 'node:path'
import fs from 'node:fs'
import {fileURLToPath} from 'node:url'
import {createSnapshotApi} from './snapshot/server/api.mjs'
export const workspace=fileURLToPath(new URL('.',import.meta.url))
const local={}
for (const filename of ['.env','.env.local']) {
 const file=path.join(workspace,filename)
 if(fs.existsSync(file)) for(const line of fs.readFileSync(file,'utf8').split(/\r?\n/)) {
  const match=line.match(/^\s*(DASHBOARD_[A-Z_]+)\s*=\s*(.*?)\s*$/)
  if(match)local[match[1]]=match[2].replace(/^['"]|['"]$/g,'')
 }
}
const setting=(key,fallback)=>process.env[key]??local[key]??fallback
export const mode=setting('DASHBOARD_MODE','snapshot')
if(!['snapshot','live'].includes(mode))throw new Error('DASHBOARD_MODE must be snapshot or live')
export const port=Number(setting('DASHBOARD_PORT','5184'))
export const host=setting('DASHBOARD_HOST','127.0.0.1')
export const artifacts=path.resolve(workspace,setting('DASHBOARD_RUNTIME','.runtime'))
const liveAssets=setting('DASHBOARD_LIVE_ASSETS','')
// A live API can be used with bundled visual assets; set LIVE_ASSETS for server-generated versions.
export const publicAssets=mode==='live'&&liveAssets?path.join(path.resolve(liveAssets),'analysis_public'):path.join(workspace,'snapshot/public')
export const servingAssets=mode==='live'&&liveAssets?path.join(path.resolve(liveAssets),'reference_serving'):path.join(workspace,'snapshot/reference_serving')
export const proxy=mode==='live'?{'/api':{target:setting('DASHBOARD_API_BASE','http://127.0.0.1:5174'),changeOrigin:false}}:{}
export function previewBoundary() {
 const api=mode==='snapshot'?createSnapshotApi(path.join(workspace,'snapshot')):null
 const install=server=>{server.middlewares.use(async(req,res,next)=>{
  let url
  try {url=new URL(req.url,'http://localhost')}catch{return next()}
  if(url.pathname.startsWith('/api/')) {
   if(!['GET','HEAD'].includes(req.method)){res.statusCode=405;res.end('Read-only API');return}
   if(api) {
    try {
     const result=await api(url)
     res.statusCode=result.status
     res.setHeader('Content-Type','application/json; charset=utf-8')
     res.setHeader('Cache-Control','no-store')
     res.end(req.method==='HEAD'?'':JSON.stringify(result.body))
    }catch(error){console.error('Snapshot API failed:',error.message);res.statusCode=500;res.end(JSON.stringify({error:'Snapshot read failed'}))}
    return
   }
  }
  if(!url.pathname.startsWith('/low-altitude/'))return next()
  const base=path.join(artifacts,'build/low-altitude-web')
  let file
  try {file=path.resolve(base,decodeURIComponent(url.pathname.slice('/low-altitude/'.length)||'index.html'))}catch{res.statusCode=400;res.end('Invalid path');return}
  if(!file.startsWith(base+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.statusCode=404;res.end('Build the embedded view with npm run build:lowalt');return}
  const type={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.json':'application/json','.png':'image/png','.woff2':'font/woff2'}
  res.setHeader('Content-Type',type[path.extname(file)]||'application/octet-stream')
  if(req.method==='HEAD')res.end();else fs.createReadStream(file).pipe(res)
 })}
 return {name:'portable-dashboard',configureServer:install,configurePreviewServer:install}
}
