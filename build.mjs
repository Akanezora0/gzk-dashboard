import {spawnSync} from 'node:child_process'
import {createRequire} from 'node:module'
import path from 'node:path'
import {workspace} from './ui.config.mjs'
for (const folder of process.argv.includes('--lowalt') ? ['lowalt'] : ['web','lowalt']) {
 const require=createRequire(path.join(workspace,folder,'package.json'))
 const vite=path.join(path.dirname(require.resolve('vite/package.json')),'bin/vite.js')
 const result=spawnSync(process.execPath,[vite,'build'],{cwd:path.join(workspace,folder),stdio:'inherit'})
 if(result.status!==0)process.exit(result.status||1)
}
