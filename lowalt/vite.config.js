import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'node:path'
import {embeddedDisplayCopy} from './src/displayCopy.js'
import {workspace,artifacts,servingAssets} from '../ui.config.mjs'
export default defineConfig({
 base:'/low-altitude/',plugins:[embeddedDisplayCopy(),vue()],cacheDir:path.join(artifacts,'cache/lowalt'),
 resolve:{alias:[
  {find:/^(?:\.\.\/)+composables\/useApi(?:\.js)?$/,replacement:path.join(workspace,'lowalt/src/api.js')},
  {find:'@legacy',replacement:path.join(workspace,'legacy/src')},
  {find:'@serving',replacement:servingAssets},
 ]},
 build:{outDir:path.join(artifacts,'build/low-altitude-web'),emptyOutDir:true},
})
