/* Presentation-only adapter: source frames and category values remain unchanged. */
(()=>{
 const isTerms=typeof switchMode==='function',sourceRender=render
 const currentFrames=()=>isTerms?DATA.views[mode].frames:frames
 const elements=()=>[...document.querySelectorAll('.year-current,#total,.tile .amount strong,.tile .share-label b,.yearbox .year,.yearpanel .year')]
 const motion=matchMedia('(prefers-reduced-motion: reduce)')
 pause()
 render=function(animate=true){
  const targets=elements();document.querySelectorAll('.number-ghost,.ui-number-ghost').forEach(e=>e.remove())
  const old=targets.map(e=>e.textContent);targets.forEach(e=>e.getAnimations().forEach(a=>a.cancel()))
  sourceRender(false)
  if(!animate||motion.matches)return
  targets.forEach((e,i)=>{if(old[i]===e.textContent)return;const text=e.textContent;e.textContent='';e.style.position='relative';const next=document.createElement('span');next.className='ui-number-current';next.textContent=text;const ghost=document.createElement('span');ghost.className='ui-number-ghost';ghost.textContent=old[i];ghost.setAttribute('aria-hidden','true');Object.assign(ghost.style,{position:'absolute',left:'0',top:'0',whiteSpace:'nowrap',pointerEvents:'none'});e.append(next,ghost);ghost.animate([{opacity:1},{opacity:0}],{duration:220,easing:'ease-out'}).onfinish=()=>ghost.remove();next.animate([{opacity:0},{opacity:1}],{duration:480,delay:90,easing:'ease-out',fill:'backwards'})})
 }
 const sync=()=>isTerms?button():updateButton()
 play=function(){if(timer||currentFrames().length<2)return;if(index>=currentFrames().length-1){index=0;render()}timer=setInterval(()=>{if(index<currentFrames().length-1){index++;render()}if(index>=currentFrames().length-1)pause()},1000);sync()}
 if(isTerms){
  const change=switchMode;switchMode=function(m){change(m);index=currentFrames().length-1;render(false)}
  document.querySelectorAll('.modes button').forEach((b,i)=>b.onclick=()=>switchMode(i))
 }else{
  const change=switchView;switchView=function(v){change(v);index=currentFrames().length-1;render(false)}
  document.querySelectorAll('.modes button').forEach((b,i)=>b.onclick=()=>switchView(i))
 }
 index=currentFrames().length-1;render(false)
 motion.addEventListener('change',()=>{if(motion.matches){pause();document.getAnimations().forEach(a=>a.cancel());document.querySelectorAll('.ui-number-ghost,.number-ghost').forEach(e=>e.remove())}})
 window.addEventListener('pagehide',pause)
})()
