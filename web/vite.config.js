import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'node:path'
import {workspace,artifacts,proxy,previewBoundary,publicAssets,port,host} from '../ui.config.mjs'
export default defineConfig({
 plugins:[previewBoundary(),vue()],
 publicDir:publicAssets,
 cacheDir:path.join(artifacts,'cache/web'),
 build:{outDir:path.join(artifacts,'build/web'),emptyOutDir:true},
 server:{host,port,strictPort:true,proxy,fs:{allow:[workspace,path.resolve(workspace,'node_modules')]}},
 preview:{host,port,strictPort:true,proxy},
})
