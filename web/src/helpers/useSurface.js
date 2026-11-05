import {watch,nextTick,onBeforeUnmount} from 'vue'
const stack=[]
let locks=0,previousOverflow=''
const focusables='button:not(:disabled),a[href],input:not(:disabled),select:not(:disabled),textarea:not(:disabled),[tabindex]:not([tabindex="-1"])'
// Shared focus, Escape, outside-click and scroll handling for detail surfaces.
export function useSurface(open,{element,close,modal=false}){
 const token={};let active=false,returnTo=null
 const el=()=>typeof element==='function'?element():element.value
 function key(e){if(stack.at(-1)!==token)return;if(e.key==='Escape'){e.preventDefault();e.stopPropagation();close();return}if(modal&&e.key==='Tab'){const nodes=[...(el()?.querySelectorAll(focusables)||[])].filter(n=>n.getClientRects().length);if(!nodes.length){e.preventDefault();return}const first=nodes[0],last=nodes.at(-1);if(e.shiftKey&&(document.activeElement===first||!el()?.contains(document.activeElement))){e.preventDefault();last.focus()}else if(!e.shiftKey&&(document.activeElement===last||!el()?.contains(document.activeElement))){e.preventDefault();first.focus()}}}
 function outside(e){if(active&&!modal&&stack.at(-1)===token&&!el()?.contains(e.target))close()}
 function cleanup(restore=true){if(!active)return;active=false;const i=stack.indexOf(token);if(i>=0)stack.splice(i,1);document.removeEventListener('keydown',key,true);document.removeEventListener('pointerdown',outside,true);if(modal&&--locks===0)document.body.style.overflow=previousOverflow;if(restore&&returnTo?.isConnected)returnTo.focus({preventScroll:true})}
 watch(open,async value=>{if(!value){cleanup();return}if(active)return;active=true;returnTo=document.activeElement;stack.push(token);if(modal&&locks++===0){previousOverflow=document.body.style.overflow;document.body.style.overflow='hidden'}document.addEventListener('keydown',key,true);document.addEventListener('pointerdown',outside,true);await nextTick();if(active)el()?.querySelector(focusables)?.focus({preventScroll:true})},{immediate:true,flush:'post'})
 onBeforeUnmount(()=>cleanup(false))
}
