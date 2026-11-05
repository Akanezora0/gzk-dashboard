import test from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import {fileURLToPath} from 'node:url'
import {createSnapshotApi,canonical} from '../snapshot/server/api.mjs'
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../snapshot')
const api=createSnapshotApi(root)
test('API queries are order-independent and unknown queries are explicit',async()=>{
 assert.equal(canonical('/x?b=2&a=1'),'/x?a=1&b=2')
 assert.equal((await api('/api/unknown')).status,404)
 assert.equal((await api('/api/llm/records?scope=llm')).status,422)
})
test('Every captured page payload and published survey is readable',async()=>{
 const index=JSON.parse(fs.readFileSync(path.join(root,'api/index.json'))).responses
 let ai=0,lowalt=0
 for(const [url,entry] of Object.entries(index)){
  const response=await api(url);assert.equal(response.status,entry.status,url)
  if(url.startsWith('/api/llm/survey/')&&response.status===200)ai++
  if(url.startsWith('/api/low-altitude/survey?')&&response.status===200)lowalt++
 }
 assert.equal(ai,102);assert.equal(lowalt,66)
})
test('Record collections preserve full pagination and literal search',async()=>{
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'records/manifest.json')))
 for(const ns of manifest.namespaces){
  const base='/api/llm/records?scope=ai&namespace='+ns.namespace
  const first=(await api(base+'&limit=10')).body
  assert.equal(first.total,ns.total);assert.equal(first.rows.length,Math.min(ns.total,10))
  if(ns.total>10){const last=(await api(base+'&offset='+(ns.total-1)+'&limit=10')).body;assert.equal(last.rows.length,1);assert.notEqual(first.rows[0].id,last.rows[0].id)}
  const term=first.rows[0]?.title?.slice(0,8)
  if(term){const result=(await api(base+'&q='+encodeURIComponent(term))).body;assert.ok(result.rows.length);assert.ok(result.rows.every(x=>x.title.toLowerCase().includes(term.toLowerCase())))}
  const none=(await api(base+'&q=不存在的标题_zxyz0123456789')).body;assert.equal(none.total,0)
 }
 const percent=(await api('/api/llm/records?scope=ai&namespace=cnki_paper&q=%25')).body
 assert.ok(percent.rows.every(r=>r.title.includes('%')))
 assert.equal((await api('/api/llm/records?scope=ai&offset=-1')).status,400)
})
test('Contribution filtering uses the actual records and original rounding',async()=>{
 const full=(await api('/api/low-altitude/contribution')).body
 assert.equal(full.coverage.total_papers,3727)
 const selected=(await api('/api/low-altitude/contribution?tech_tag_id=airframe_fixed_wing&year_start=2018&year_end=2024')).body
 assert.equal(selected.coverage.total_papers,59)
 const layer=(await api('/api/low-altitude/contribution?tech_layer='+encodeURIComponent('平台构型与结构层')+'&year_start=2010&year_end=2020')).body
 assert.equal(layer.coverage.total_papers,367)
})

test('Concurrent contribution cold requests initialize a complete dataset',async()=>{
 const cold=createSnapshotApi(root)
 const responses=await Promise.all(Array.from({length:8},()=>cold('/api/low-altitude/contribution')))
 responses.forEach(r=>{assert.equal(r.status,200);assert.equal(r.body.coverage.total_papers,3727)})
})
