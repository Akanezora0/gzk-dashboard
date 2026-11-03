export const colors=['#AE0D28','#2877B0','#278771','#8B63AA','#D18A23','#538EAF','#B65370','#6E7F43']
export const fmt=n=>n==null?'—':Number(n).toLocaleString('zh-CN')
export const concise=n=>n==null?'—':Number(n)>=10000?(Number(n)/10000).toFixed(1)+'万':fmt(n)
export const safeUrl=s=>{try{const u=new URL(s,window.location.origin);return ['https:','http:'].includes(u.protocol)?u.href:'#'}catch{return '#'}}
export const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))
export const kindLabel={paper:'论文',fund:'基金',patent:'专利',software:'软著',copyright:'软著',policy:'政策',news:'新闻',report:'报告',company:'企业',product:'产品',institution:'机构',tech_point:'技术',technology:'技术',tech:'技术'}
export const chartBase={color:colors,textStyle:{fontFamily:'system-ui, PingFang SC, Microsoft YaHei, sans-serif',fontSize:14,color:'#394354'},tooltip:{trigger:'axis',confine:true,textStyle:{fontSize:14}},grid:{top:28,right:28,bottom:48,left:72,containLabel:true}}
export async function api(path){const r=await fetch(path);if(!r.ok)throw new Error(`数据读取失败（${r.status}）`);return r.json()}

// Presentation summaries: quantitative definitions and QA notes remain with the source snapshot.
export const sourceContent=id=>({legacy_industry_report:'行业研究、产业背景与案例资料',cn_patent_base:'公开号码、申请人、发明人、时间与技术文本',nsfc_paper:'期刊与会议成果、资助项目关联',cnki_paper:'文献题录、作者、机构与发表信息',legacy_software:'软件名称、登记及著作权人信息',nsfc_fund:'项目编号、名称、批准时间与承担单位',legacy_patent:'专利名称、号码、时间及申请主体',legacy_news:'新闻标题、正文与来源信息',ai_company:'企业名称与分类线索',legacy_policy:'政策标题、原文与发布信息',legacy_product:'载体产品名称、类型及厂商',ai_report:'人工智能与跨行业报告PDF文件',policy_central:'中央政策原文与发文信息',policy_local:'地方政策原文、地区与发文信息',专利申请主体:'专利申请人及主体信息',科研单位:'科研机构名称与单位信息',产品厂家单位:'产品厂商名称与单位信息',科研项目:'专题项目与承担主体信息'})[id]||'名称、来源与相关记录'
