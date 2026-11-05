import fs from 'node:fs'
import path from 'node:path'
import {createHash} from 'node:crypto'
import {gunzipSync} from 'node:zlib'
import {fileURLToPath} from 'node:url'
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..')
const sha=b=>createHash('sha256').update(b).digest('hex')
const index=JSON.parse(fs.readFileSync(path.join(root,'snapshot/api/index.json'),'utf8')).responses
let responses=0,records=0,parts=0
for(const [url,spec] of Object.entries(index)){
 const raw=fs.readFileSync(path.join(root,'snapshot/api',spec.file))
 if(raw.length!==spec.bytes||sha(raw)!==spec.sha256)throw Error('API snapshot mismatch: '+url)
 JSON.parse(raw);responses++
}
const manifest=JSON.parse(fs.readFileSync(path.join(root,'snapshot/records/manifest.json'),'utf8'))
for(const ns of manifest.namespaces){
 let count=0
 for(const spec of ns.parts){
  const raw=fs.readFileSync(path.join(root,'snapshot/records',spec.file))
  if(sha(raw)!==spec.sha256)throw Error('Record shard mismatch: '+spec.file)
  const unzipped=gunzipSync(raw)
  if(sha(unzipped)!==spec.uncompressed_sha256)throw Error('Record content mismatch: '+spec.file)
  const n=unzipped.toString('utf8').split('\n').filter(Boolean).length
  if(n!==spec.count)throw Error('Record count mismatch: '+spec.file)
  count+=n;parts++
 }
 if(count!==ns.total)throw Error('Namespace count mismatch: '+ns.namespace)
 records+=count
}
const assets=JSON.parse(fs.readFileSync(path.join(root,'snapshot/manifest.json'),'utf8')).assets
for(const spec of assets){if(sha(fs.readFileSync(path.join(root,spec.file)))!==spec.sha256)throw Error('Visual asset mismatch: '+spec.file)}
console.log(JSON.stringify({passed:true,responses,records,parts,visualAssets:assets.length}))
