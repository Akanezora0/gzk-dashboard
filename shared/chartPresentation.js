// Shared animation and hover-card defaults; callers retain series and data semantics.
export function chartPresentation(source, update=false, reduced=false){
 const option={animationDuration:update?520:920,animationDurationUpdate:480,animationEasing:'cubicOut',animationEasingUpdate:'cubicOut',...source}
 if(Array.isArray(source.series))option.series=source.series.map((item,index)=>({...item,animationDelay:item.animationDelay??(i=>i*26+index*70),animationDuration:item.animationDuration??(update?480:920),animationEasing:item.animationEasing??'cubicOut'}))
 if(source.tooltip&&typeof source.tooltip==='object'&&!Array.isArray(source.tooltip))option.tooltip={confine:true,backgroundColor:'#fffffffa',borderColor:'#e2d5d9',padding:[11,14],extraCssText:'box-shadow:0 6px 22px #49212c16;border-radius:8px;',...source.tooltip,textStyle:{color:'#344054',fontSize:14,lineHeight:22,...source.tooltip.textStyle}}
 if(reduced)option.animation=false
 return option
}
