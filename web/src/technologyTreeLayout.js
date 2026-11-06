export const treeColors={AI1:'#ad2344',AI2:'#397da3',AI3:'#348873',AI4:'#9871aa',AI5:'#be8831',AI6:'#5a809f',AI7:'#b46780'}
export const branchOrder=['AI7','AI6','AI2','AI1','AI3','AI4','AI5']
export function labelLines(value,limit=10.5){
 const text=String(value).replace(/（含[^）]+）/g,'').replace('模型即服务（MaaS，含模型托管与推理API）','模型即服务（MaaS）')
 const lines=[];let line='',units=0
 for(const c of text){const n=/[\x00-\xff]/.test(c)?.7:1;if(units+n>limit){lines.push(line);line='';units=0}line+=c;units+=n}
 if(line)lines.push(line);return lines
}
export function topicLabelLines(value){
 const text=String(value).replace(/（含[^）]+）/g,'')
 const parts=text.match(/^(.*)（(.*)）$/)
 if(parts&&labelLines(text).length>1&&labelLines(parts[1]).length===1&&labelLines(parts[2]).length===1)return [parts[1],parts[2]]
 if(text.startsWith('模型运维'))return ['模型运维','MLOps / LLMOps']
 return labelLines(text)
}
export function shortWorkLabel(value){const lines=labelLines(value,9);return lines[0]+(lines.length>1?'…':'')}
export function treeLayout(tree,chronology){
 const cats=tree.nodes.filter(n=>n.node_type==='category'),events=chronology?.events||[]
 const years=[...new Set(events.map(e=>Math.max(2016,Number(e.year))))].sort((a,b)=>b-a)
 const width=1420,nodeWidth=164,nodeHeight=66,left=91,laneWidth=185
 let y=105;const bands=[],points=[]
 for(const year of years){
  const rows=branchOrder.map(id=>events.filter(e=>e.category_id===id&&Math.max(2016,e.year)===year).sort((a,b)=>b.year-a.year||a.topic_id.localeCompare(b.topic_id)))
  const h=Math.max(110,Math.max(...rows.map(a=>a.length),1)*78+24)
  bands.push({year,y,height:h})
  rows.forEach((es,col)=>es.forEach((e,row)=>points.push({...e,x:left+col*laneWidth+laneWidth/2,y:y+24+row*78,w:nodeWidth,h:nodeHeight,tone:treeColors[e.category_id],lines:topicLabelLines(e.topic_label)})))
  y+=h
 }
 const height=y+130,byId=new Map(points.map(p=>[p.id,p]))
 const categories=branchOrder.map((id,col)=>({...cats.find(c=>c.id===id),x:left+col*laneWidth+laneWidth/2,tone:treeColors[id],trunk:['AI1','AI3'].includes(id)}))
 const edges=(chronology?.edges||[]).map(e=>({...e,from:byId.get(e.source),to:byId.get(e.target)})).filter(e=>e.from&&e.to)
 return {width,height,points,bands,categories,edges,nodeHeight}
}
export const featuredEventIds=['transformer_2017','gpt_2018','rag_2020','lora_2021','instructgpt_2022','llava_2023','deepseekmoe_2024','deepseekr1_2025']
export function relationCurve(e){
 const a=e.from,b=e.to,up=b.y<=a.y,dy=up?-1:1
 const sy=a.y+dy*a.h/2,ty=b.y-dy*b.h/2,dist=Math.max(32,Math.abs(ty-sy)*.45)
 return `M ${a.x} ${sy} C ${a.x} ${sy+dy*dist}, ${b.x} ${ty-dy*dist}, ${b.x} ${ty}`
}

/* ===== 横向技术演进树：横轴为年份，七条泳道为技术大类 ===== */
export const laneOrder=['AI1','AI2','AI3','AI4','AI5','AI6','AI7']
export function horizontalLayout(tree,chronology){
 const cats=tree.nodes.filter(n=>n.node_type==='category'),events=chronology?.events||[]
 const yk=y=>Math.max(2016,Number(y))
 const years=[...new Set(events.map(e=>yk(e.year)))].sort((a,b)=>a-b)
 const colW=232,left=180,nodeW=184,nodeH=44,gap=8,minLane=92,axisH=46
 const cell={};events.forEach(e=>{const k=e.category_id+'|'+yk(e.year);(cell[k]=cell[k]||[]).push(e)})
 const lanes=[];let y=0
 laneOrder.forEach(id=>{const most=Math.max(1,...years.map(yr=>(cell[id+'|'+yr]||[]).length));const h=Math.max(minLane,most*(nodeH+gap)+28);lanes.push({...cats.find(c=>c.id===id),id,y,h,tone:treeColors[id]});y+=h})
 const height=y+axisH,width=left+years.length*colW+36
 const points=[]
 lanes.forEach(l=>years.forEach((yr,i)=>{const list=(cell[l.id+'|'+yr]||[]).sort((a,b)=>a.year-b.year||a.topic_id.localeCompare(b.topic_id));const block=list.length*(nodeH+gap)-gap;list.forEach((e,j)=>points.push({...e,col:i,x:left+i*colW+(colW-nodeW)/2,y:l.y+(l.h-block)/2+j*(nodeH+gap),w:nodeW,h:nodeH,tone:l.tone,yearKey:yr}))}))
 const byId=new Map(points.map(p=>[p.id,p]))
 const edges=(chronology?.edges||[]).map(e=>({...e,from:byId.get(e.source),to:byId.get(e.target)})).filter(e=>e.from&&e.to)
 return {width,height,left,colW,axisH,years,lanes,points,edges}
}
export function horizontalCurve(e){
 const a=e.from,b=e.to
 if(a.col===b.col){const x=a.x+a.w,y1=a.y+a.h/2,y2=b.y+b.h/2;return `M ${x} ${y1} C ${x+26} ${y1}, ${x+26} ${y2}, ${x} ${y2}`}
 const fwd=b.x>=a.x,x1=fwd?a.x+a.w:a.x,x2=fwd?b.x:b.x+b.w,y1=a.y+a.h/2,y2=b.y+b.h/2,dx=Math.max(36,Math.abs(x2-x1)*.45)*(fwd?1:-1)
 return `M ${x1} ${y1} C ${x1+dx} ${y1}, ${x2-dx} ${y2}, ${x2} ${y2}`
}
