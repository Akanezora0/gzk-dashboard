// Current accepted stock is separate from historical analytical cohorts.
export function applyCurrentInventory(data,current){
 const replacements=new Map(current.datasets.map(row=>[row.id,row]))
 const datasets=data.overview.datasets.map(row=>replacements.has(row.id)?{...row,...replacements.get(row.id)}:row)
 const ids=new Set(datasets.map(row=>row.id))
 datasets.push(...current.datasets.filter(row=>!ids.has(row.id)))
 const changed=new Set(current.datasets.map(row=>row.id))
 return {...data,currentInventory:current,overview:{...data.overview,datasets,source_date:current.as_of,dataset_count:datasets.length},inventory:{...data.inventory,datasets:(data.inventory?.datasets||[]).filter(row=>!changed.has(row.id))}}
}
