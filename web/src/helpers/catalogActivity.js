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
 for(const event of events){const day=activityDate(event.date);if(day&&stamp(day)<=end)counts.set(day,(counts.get(day)||0)+(event.receivedBatches??1))}
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
const sourceNames={nsfc_official:'国家自然科学基金项目',nsfc_official_depth_sample:'国家自然科学基金项目样本',crossref_nsfc_depth_sample:'Crossref资助文献样本',medsci_nsfc_sample:'MedSci基金项目样本',letpub_nsfc_sample:'LetPub基金项目样本',ai_patent_package:'人工智能专利数据',patsnap:'智慧芽专利数据',policy_yaoyuan:'政策文本资料',cfrr:'CFRR论文与专利关联资料'}
export const activityTitle=e=>sourceNames[e.title]||e.title

// This ledger is maintained independently from backend asset receipts.
export function parseActivityLedger(data){
 if(data?.schemaVersion!==1||!Array.isArray(data.events))throw new Error('更新台账格式不正确')
 const ids=new Set()
 const events=data.events.map(row=>{
  if(!row.id||ids.has(row.id))throw new Error('更新台账记录编号缺失或重复')
  ids.add(row.id)
  if(!/^\d{4}-\d{2}-\d{2}$/.test(row.date)||activityDate(row.date)!==row.date)throw new Error('更新日期格式不正确')
  if(!['received','loaded','published'].includes(row.status)||!row.title)throw new Error('更新类型或标题不正确')
  for(const field of ['receivedBatches','loadedBatches','publishedBatches']){
   if(!Number.isSafeInteger(row[field]??0)||(row[field]??0)<0)throw new Error('批次数必须为非负整数')
  }
  const detail=typeof row.detail==='string'?row.detail.replace(/\s*版本\s*[A-Za-z0-9_.\-]+。?/g,'').trim():row.detail
  return {...row,detail,receivedBatches:row.receivedBatches??0,loadedBatches:row.loadedBatches??0,publishedBatches:row.publishedBatches??0,loaded:row.status==='loaded'||row.status==='published',presentBatches:row.receivedBatches??0}
 }).sort((a,b)=>b.date.localeCompare(a.date)||a.id.localeCompare(b.id))
 return {...data,events}
}
