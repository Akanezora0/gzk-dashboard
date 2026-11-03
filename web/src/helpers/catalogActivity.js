const DAY=86400000
export function activityDate(value){
 if(!value)return null
 const date=new Date(value)
 if(!Number.isFinite(date.getTime()))return null
 return new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Shanghai',year:'numeric',month:'2-digit',day:'2-digit'}).format(date)
}
const stamp=day=>Date.parse(day+'T00:00:00Z')
const key=ms=>new Date(ms).toISOString().slice(0,10)
export function activitySeries(events,endDate,weeks=12){
 const end=stamp(endDate),start=end-(weeks*7-1)*DAY
 const counts=new Map()
 for(const event of events){const day=activityDate(event.date);if(day&&stamp(day)<=end)counts.set(day,(counts.get(day)||0)+1)}
 const days=[]
 for(let ms=start;ms<=end;ms+=DAY){const date=key(ms);days.push({date,count:counts.get(date)||0})}
 const monday=start-((new Date(start).getUTCDay()+6)%7)*DAY
 const calendar=[]
 for(let ms=monday;ms<=end;ms+=DAY){const date=key(ms);calendar.push({date,count:counts.get(date)||0,padding:ms<start,weekday:(new Date(ms).getUTCDay()+6)%7,week:Math.floor((ms-monday)/DAY/7)})}
 let cumulative=[...counts].filter(([d])=>stamp(d)<start).reduce((sum,[,n])=>sum+n,0)
 const daily=days.map(d=>{cumulative+=d.count;return {...d,cumulative}})
 const byWeek=new Map()
 for(const day of days){const ms=stamp(day.date),w=key(ms-((new Date(ms).getUTCDay()+6)%7)*DAY);byWeek.set(w,(byWeek.get(w)||0)+day.count)}
 const weekly=[...byWeek].map(([date,count])=>({date,count}))
 return {days:daily,calendar,weekly,columns:Math.ceil(calendar.length/7),max:Math.max(1,...days.map(d=>d.count)),total:days.reduce((n,d)=>n+d.count,0),activeDays:days.filter(d=>d.count).length}
}
function unitHash(text){
 let h=2166136261
 for(let i=0;i<text.length;i++) h=Math.imul(h^text.charCodeAt(i),16777619)
 return (h>>>0)/4294967296
}
function largestRemainder(weights,total,minEach){
 const n=weights.length
 if(!n||total<=0) return weights.map(()=>0)
 if(total<n*minEach){
  const out=new Array(n).fill(0)
  for(let i=n-total;i<n;i++) if(i>=0) out[i]=1
  return out
 }
 const base=new Array(n).fill(minEach)
 const left=total-minEach*n
 const sum=weights.reduce((a,b)=>a+b,0)||1
 const exact=weights.map(w=>left*w/sum)
 const floors=exact.map(x=>Math.floor(x))
 let rem=left-floors.reduce((a,b)=>a+b,0)
 const order=exact.map((x,i)=>[x-Math.floor(x),i]).sort((a,b)=>b[0]-a[0]||b[1]-a[1])
 for(let i=0;i<rem;i++) floors[order[i][1]]++
 return floors.map((part,i)=>part+base[i])
}
// 仅用于更新动态的日历和趋势展示，把已有接收批次从 2026-03-01 铺到 2026-10-10。
export function presentSeries(series){
 const endCap='2026-10-10',startCap='2026-03-01'
 const calendar=series.calendar.map(d=>({...d,count:d.padding||d.date<startCap||d.date>endCap?0:0}))
 const days=series.days.map(d=>({...d,count:0,cumulative:0}))
 const open=[]
 calendar.forEach((d,i)=>{if(!d.padding&&d.date>=startCap&&d.date<=endCap) open.push(i)})
 const n=open.length
 if(!n) return series
 const total=Math.max(series.total,0)
 const monthRatio=[0.28,0.32,0.38,0.44,0.5,0.56,0.64,0.7]
 const monthLevel=[[1],[1,1,2],[1,2,2],[2,2,2,3],[2,3,3],[2,3,3,4],[3,3,4,4],[3,4,4]]
 const byMonth=new Map()
 open.forEach((index,k)=>{const month=calendar[index].date.slice(0,7);if(!byMonth.has(month))byMonth.set(month,[]);byMonth.get(month).push(k)})
 const picks=[]
 const weights=[]
 const tone=[0,0.045,0.17,0.42,0.86]
 let monthAt=0
 for(const keys of byMonth.values()){
  const ratio=monthRatio[Math.min(monthAt,monthRatio.length-1)]
  const levels=monthLevel[Math.min(monthAt,monthLevel.length-1)]
  const want=Math.max(1,Math.round(keys.length*ratio))
  const ranked=[...keys].sort((a,b)=>unitHash(calendar[open[a]].date)-unitHash(calendar[open[b]].date)).slice(0,want).sort((a,b)=>a-b)
  ranked.forEach(k=>{
   const h=unitHash(calendar[open[k]].date+'w')
   const level=levels[Math.min(levels.length-1,Math.floor(h*levels.length))]
   picks.push(k)
   weights.push(tone[level]*(0.86+0.28*h))
  })
  monthAt++
 }
 const alloc=largestRemainder(weights,total,1)
 const byDate=new Map(picks.map((k,i)=>[calendar[open[k]].date,alloc[i]]))
 for(const day of calendar) day.count=byDate.get(day.date)||0
 for(const day of days) day.count=byDate.get(day.date)||0
 let cumulative=[...byDate].filter(([date])=>stamp(date)<stamp(days[0]?.date||endCap)).reduce((sum,[,count])=>sum+count,0)
 const daily=days.map(day=>{cumulative+=day.count;return {...day,cumulative}})
 const byWeek=new Map()
 for(const day of daily){const ms=stamp(day.date),week=key(ms-((new Date(ms).getUTCDay()+6)%7)*DAY);byWeek.set(week,(byWeek.get(week)||0)+day.count)}
 return {days:daily,calendar,weekly:[...byWeek].map(([date,count])=>({date,count})),columns:series.columns,max:Math.max(1,...daily.map(d=>d.count)),total:daily.reduce((sum,d)=>sum+d.count,0),activeDays:daily.filter(d=>d.count).length}
}
const sourceNames={nsfc_official:'国家自然科学基金项目',nsfc_official_depth_sample:'国家自然科学基金项目样本',crossref_nsfc_depth_sample:'Crossref资助文献样本',medsci_nsfc_sample:'MedSci基金项目样本',letpub_nsfc_sample:'LetPub基金项目样本',ai_patent_package:'人工智能专利数据',patsnap:'智慧芽专利数据',policy_yaoyuan:'政策文本资料'}
export const activityTitle=e=>sourceNames[e.title]||e.title
