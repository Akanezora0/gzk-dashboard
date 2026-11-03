import path from 'node:path'
import fs from 'node:fs'
import {fileURLToPath} from 'node:url'
export const workspace=fileURLToPath(new URL('.',import.meta.url))
const local={}
for(const filename of ['.env','.env.local']){
 const p=path.join(workspace,filename)
 if(fs.existsSync(p))for(const line of fs.readFileSync(p,'utf8').split(/\r?\n/)){
  const m=line.match(/^\s*(DASHBOARD_[A-Z_]+)\s*=\s*(.*?)\s*$/)
  if(m)local[m[1]]=m[2].replace(/^['"]|['"]$/g,'')
 }
}
const setting=(key,fallback)=>process.env[key]??local[key]??fallback
export const demo=setting('DASHBOARD_MODE','demo')==='demo'
export const port=Number(setting('DASHBOARD_PORT','5184'))
export const artifacts=path.resolve(workspace,setting('DASHBOARD_ARTIFACTS','.runtime'))
export const publicAssets=demo?path.join(workspace,'demo/public'):path.join(artifacts,'analysis_public')
export const servingAssets=demo?path.join(workspace,'demo/reference_serving'):path.join(artifacts,'reference_serving')
export const proxy=demo?{}:{'/api':{target:setting('DASHBOARD_API_BASE','http://127.0.0.1:5174'),changeOrigin:false}}
export function previewBoundary(){
 const install=server=>{server.middlewares.use((req,res,next)=>{
  const url=new URL(req.url,'http://localhost')
  if(url.pathname.startsWith('/api/')&&!['GET','HEAD'].includes(req.method)){res.statusCode=405;res.end('Read-only preview');return}
  if(demo&&url.pathname.startsWith('/api/')){
   const key=url.pathname.split('/').filter(Boolean).at(-1)
   const file=path.join(workspace,'demo/api',key+'.json')
   res.setHeader('Content-Type','application/json; charset=utf-8')
   res.end(fs.existsSync(file)?fs.readFileSync(file):JSON.stringify({items:[],records:[],nodes:[],edges:[],total:0,rows:[],demo:true}));return
  }
  if(!url.pathname.startsWith('/low-altitude/'))return next()
  const base=path.join(artifacts,'build/low-altitude-web')
  const file=path.resolve(base,decodeURIComponent(url.pathname.slice('/low-altitude/'.length)||'index.html'))
  if(!file.startsWith(base+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.statusCode=404;res.end('Run npm run build:lowalt first');return}
  const type={'.html':'text/html; charset=utf-8','.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.json':'application/json','.png':'image/png'}
  res.setHeader('Content-Type',type[path.extname(file)]||'application/octet-stream');fs.createReadStream(file).pipe(res)
 })}
 return {name:'portable-preview',configureServer:install,configurePreviewServer:install,transformIndexHtml(html){
  return html
 }}
}
