import {ref,onBeforeUnmount} from 'vue'
// Final frame on entry; pause preserves the current frame; completion never loops.
export function useYearPlayback(first,last){
 const year=ref(last),playing=ref(false)
 let timer
 function pause(){clearInterval(timer);timer=undefined;playing.value=false}
 function play(){if(playing.value){pause();return}if(year.value>=last)year.value=first;playing.value=true;timer=setInterval(()=>{if(year.value<last)year.value++;if(year.value>=last)pause()},1000)}
 function seek(value){pause();year.value=Math.max(first,Math.min(last,Number(value)))}
 onBeforeUnmount(pause)
 return {year,playing,play,pause,seek}
}
