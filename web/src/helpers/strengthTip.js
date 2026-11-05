import {reactive,nextTick} from 'vue'

/** Shared hover card for the research-strength charts. */
export function useTip(){
  const tip=reactive({show:false,html:'',x:0,y:0})
  const show=(e,html)=>{tip.html=html;tip.show=true;move(e)}
  const move=e=>{const x=e.clientX,y=e.clientY;tip.x=Math.max(12,Math.min(x+14,window.innerWidth-332));tip.y=Math.max(12,Math.min(y+14,window.innerHeight-172));nextTick(()=>{if(!tip.show)return;const box=document.querySelector('.rs-tip')?.getBoundingClientRect();if(!box)return;tip.x=Math.max(12,Math.min(x+14,window.innerWidth-box.width-12));tip.y=Math.max(12,Math.min(y+14,window.innerHeight-box.height-12))})}
  const hide=()=>{tip.show=false}
  return {tip,show,move,hide}
}

export const fmt=n=>Number(n||0).toLocaleString('en-US')
/** Approximate rendered width of a label (CJK full width, Latin ~0.58em). */
export const textWidth=(t,size)=>[...String(t)].reduce((a,ch)=>a+(/[　-鿿＀-￯·“”（）]/.test(ch)?size:size*0.58),0)

export async function toggleFullscreen(el){
  try{if(document.fullscreenElement)await document.exitFullscreen();else await el?.requestFullscreen?.()}catch{/* optional */}
}

/** Group the NSFC project-type names used by the continuity records. */
export const typeGroup=t=>{t=String(t||'');if(t.startsWith('青年'))return '青年';if(t.startsWith('地区'))return '地区';if(t.startsWith('面上'))return '面上';return '重点等'}
export const TYPE_NAME={'青年':'青年科学基金','地区':'地区科学基金','面上':'面上项目','重点等':'联合·重大·重点等'}
export const TYPE_SHORT={'青年':'青年','地区':'地区','面上':'面上','重点等':'联合等'}
export const TYPE_COLOR={'青年':'#f0b7bf','地区':'#bdb5ad','面上':'#ae0d28','重点等':'#7a0a1c'}
export const BASIS={explicit_nsfc_award:'论文明确标注基金批准号',fund_registered_outcome:'基金项目成果登记',nsfc_recent_registered:'NSFC 近期成果登记'}

/** Emphasise figures inside a conclusion sentence. Text is our own copy, so v-html is safe. */
export const emph=t=>String(t).replace(/(\d[\d,.]*\s*%|\d[\d,.]*\s*(?:家|项|条|人))/g,'<b>$1</b>')
