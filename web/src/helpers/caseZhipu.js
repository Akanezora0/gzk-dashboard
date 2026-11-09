/*
 * 产业链案例：智谱（北京智谱华章科技股份有限公司）
 * 资料来源：同事整理的智谱案例页（2026-11-06），原始依据见 sources。
 * 财务为上市集团口径：2025 全年经审计，2026 上半年未经审计。
 */
export const sources={
 glm:{title:'GLM · ACL 2022',url:'https://aclanthology.org/2022.acl-long.26.pdf',location:'方法：正文印刷页 321–322；基金致谢：印刷页 328（PDF 第 9 页）'},
 ptuning:{title:'P-Tuning v2 · ACL 2022',url:'https://aclanthology.org/2022.acl-short.8.pdf',location:'致谢：印刷页 65（PDF 第 5 页）'},
 glm130b:{title:'GLM-130B · ICLR 2023',url:'https://arxiv.org/pdf/2210.02414v2',location:'v2 版本；基金致谢位于 PDF 第 10 页，含 61825602、62276148，并列示 Zhipu.AI 支持'},
 summary:{title:'CN115455175A · 基于多语言模型的跨语言摘要生成方法和装置',url:'https://patents.google.com/patent/CN115455175A/zh',location:'说明书 [0066]–[0071]，实施例采用 GLM；申请号 CN202210966889.3'},
 qa:{title:'CN115795009A · 基于生成式多语言模型的跨语言问答系统构建方法和装置',url:'https://patentimages.storage.googleapis.com/2e/9a/51/3192beb8538199/CN115795009A.pdf',location:'说明书 [0074]–[0079]，点名 GLM；申请号 CN202211480992.3'},
 retrieval:{title:'CN116644196A · 基于参数高效的通用检索方法和装置',url:'https://patents.google.com/patent/CN116644196A/en',location:'说明书 [0032]–[0033]，采用 P-Tuning v2；申请号 CN202310920950.5；2024-07-12 视为撤回'},
 ptcode:{title:'ChatGLM-6B · 官方 P-Tuning 实现',url:'https://github.com/zai-org/ChatGLM-6B/blob/main/ptuning/README.md',location:'ADGEN 商品描述生成示例；约训练 0.1% 参数，特定配置约需 7GB 显存'},
 chatglm:{title:'ChatGLM 技术报告',url:'https://arxiv.org/html/2406.12793v1',location:'第 1–2 节：GLM 系列的模型演进、对齐与工具使用能力'},
 code:{title:'CodeGeeX2 官方仓库',url:'https://github.com/zai-org/CodeGeeX2',location:'以 ChatGLM2-6B 为底座进行代码语料继续预训练，通过 IDE 插件提供能力'},
 prospectus:{title:'智谱招股章程 · 2025-12-30',url:'https://www.hkexnews.hk/listedco/listconews/sehk/2025/1230/2025123000018_c.pdf',location:'应用案例：PDF 第 181、183、185–186 页；平台专利：PDF 第 203 页'},
 annual:{title:'2025 年度业绩公告 · 2026-03-31',url:'https://www.hkexnews.hk/listedco/listconews/sehk/2026/0331/2026033101550_c.pdf',location:'收入分项：PDF 第 7–8 页；损益：PDF 第 18–19 页'},
 annualreport:{title:'2025 年度报告 · 2026-04-19',url:'https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0419/2026041900086_c.pdf',location:'收入结构：PDF 第 19–20 页'},
 interim:{title:'2026 年中期业绩公告 · 2026-08-31',url:'https://www.hkexnews.hk/listedco/listconews/sehk/2026/0831/2026083101540_c.pdf',location:'收入：PDF 第 1–2、23 页；业务毛利：第 25–26 页；损益：第 35 页'},
}

export const evidence={
 case:{kind:'案例口径',title:'案例范围与统计口径',claim:'案例企业为北京智谱华章科技股份有限公司（曾用名：北京智谱华章科技有限公司）。本案例选取两条研究路线、三件方法承接专利与四类应用场景，财务数据采用上市集团口径。',refs:['glm','ptuning','prospectus','interim']},
 fundglm:{kind:'基金 → 论文',title:'GLM 的基金支持',claim:'GLM（ACL 2022）论文致谢列示国家自然科学基金项目 61825602，是从研究成果回溯基金支持的直接入口。',refs:['glm']},
 fundpt:{kind:'基金 → 论文',title:'P-Tuning v2 的基金支持',claim:'P-Tuning v2（ACL 2022）论文致谢列示国家自然科学基金项目 61825602 与 61836013。',refs:['ptuning']},
 glmpaper:{kind:'论文方法',title:'GLM：通用预训练方法',claim:'GLM 以自回归空白填充为核心：把被遮蔽的文本片段作为生成目标，同时利用上下文表示。该方法在企业跨语言摘要与问答专利中有明确的实施例，GLM / ChatGLM 的模型演进另见技术报告。',refs:['glm','summary','qa','chatglm']},
 ptpaper:{kind:'论文方法',title:'P-Tuning v2：小参数任务适配',claim:'P-Tuning v2 通过训练连续提示参数，使预训练模型适配具体任务。该方法出现在企业通用检索专利方案中，也有 ChatGLM-6B 官方任务适配实现。',refs:['ptuning','retrieval','ptcode']},
 glmpatents:{kind:'论文 → 企业专利',title:'两件专利采用 GLM',claim:'跨语言摘要生成与跨语言问答系统两件专利，说明书实施例明确采用 GLM，申请人为智谱，是论文方法进入企业研发的实例。',refs:['summary','qa']},
 ptpatent:{kind:'论文 → 企业专利',title:'通用检索专利采用 P-Tuning v2',claim:'CN116644196A《基于参数高效的通用检索方法和装置》方案明确使用 P-Tuning v2，申请人为智谱曾用名。该申请于 2024-07-12 视为撤回，作为方法承接实例收录。',refs:['retrieval','ptuning']},
 glmimplementation:{kind:'论文 → 模型与产品',title:'从 GLM 到模型与编程工具',claim:'GLM、GLM-130B 与 ChatGLM 的技术资料呈现模型方法的演进。CodeGeeX2 以 ChatGLM2-6B 为底座，经代码语料继续预训练，再以 IDE 插件进入开发流程。',refs:['glm130b','chatglm','code']},
 ptimplementation:{kind:'论文 → 官方实现',title:'官方任务适配：生成商品介绍',claim:'ChatGLM-6B 官方 P-Tuning 实现以 ADGEN 为例：输入服装材质、颜色、款式等属性，生成商品介绍。示例约训练 0.1% 的参数，结合量化与梯度检查点的配置约需 7GB 显存。',refs:['ptcode','ptuning']},
 qingyan:{kind:'产品应用',title:'智谱清言',claim:'GLM / ChatGLM 的对话、检索与工具使用能力，对应清言的问答、检索与 Python 分析功能。技术报告记录模型演进与工具使用能力，招股章程提供产品业务背景。',refs:['chatglm','prospectus']},
 codegeex:{kind:'产品应用',title:'CodeGeeX',claim:'CodeGeeX2 以 ChatGLM2-6B 为底座，经代码语料继续预训练，通过 IDE 插件交付。招股章程披露：截至 2025-06-30，CodeGeeX 日均生成代码超过 1 亿行。',refs:['code','prospectus']},
 wps:{kind:'产品应用',title:'WPS AI',claim:'招股章程披露 GLM 与金山办公 WPS AI 的产品集成，覆盖大纲、演示文稿与讲稿生成，模型能力经应用软件进入办公任务。',refs:['prospectus']},
 bank:{kind:'行业应用',title:'银行业务资料查询',claim:'招股章程披露某综合性企业商业银行业务部门的案例：模型处理金融新规咨询等任务，相关问答流程 AI 自动化率超过 50%。',refs:['prospectus']},
 finance:{kind:'经营数据',title:'集团经营数据',claim:'2025 年全年收入 7.243 亿元，其中 API 收入 1.904 亿元、占 26.3%；研发开支 31.804 亿元；净亏损 47.182 亿元。2026 年上半年收入 9.539 亿元，API 收入约 8.252 亿元、占 86.5%；研发开支 21.312 亿元；净亏损 20.720 亿元。2025 全年经审计，2026 上半年未经审计。',refs:['annual','annualreport','interim','prospectus']},
}

export const routes=[
 {id:'glm',label:'GLM',sub:'通用预训练方法',title:'GLM：从通用方法到跨语言任务',lead:'以自回归空白填充为基础，让模型学习理解上下文并生成文本。',tag:'预训练 · 生成式语言建模',
  fund:['61825602'],fundEv:'fundglm',paper:'GLM',paperSub:'ACL 2022 · 自回归空白填充',paperEv:'glmpaper',
  branches:[{label:'企业专利',title:'跨语言摘要 · 跨语言问答',sub:'CN115455175A / CN115795009A · 说明书实施例采用 GLM',ev:'glmpatents'},{label:'技术报告与官方代码',title:'GLM / ChatGLM → 编程工具',sub:'CodeGeeX2 以 ChatGLM2-6B 为底座进行代码继续预训练',ev:'glmimplementation'}]},
 {id:'ptuning',label:'P-Tuning v2',sub:'小参数任务适配',title:'P-Tuning v2：用少量参数适配任务',lead:'训练连续提示参数，连接通用预训练模型与具体检索、生成任务。',tag:'参数高效微调 · 连续提示',
  fund:['61825602','61836013'],fundEv:'fundpt',paper:'P-Tuning v2',paperSub:'ACL 2022 · 连续提示参数训练',paperEv:'ptpaper',
  branches:[{label:'企业专利',title:'参数高效的通用检索',sub:'CN116644196A · 方案采用 P-Tuning v2',ev:'ptpatent'},{label:'官方任务适配实现',title:'ChatGLM-6B · 商品描述生成',sub:'ADGEN 示例：约训练 0.1% 参数，约需 7GB 显存',ev:'ptimplementation'}]},
]

export const products=[
 {id:'qingyan',icon:'chat',tag:'对话与工具调用',name:'智谱清言',sub:'从模型交互到信息检索与任务处理',flow:['用户提问','问答 / 检索','Python 分析'],big:'',text:'GLM / ChatGLM 的能力演进，为对话、检索与工具使用提供模型基础。',note:'技术报告 · 产品功能资料'},
 {id:'codegeex',icon:'code',tag:'开发者工具',name:'CodeGeeX',sub:'模型能力通过 IDE 插件进入软件开发',flow:['项目上下文','补全 / 注释 / 翻译','开发流程'],big:'>1 亿行',text:'日均生成代码',note:'企业披露，截至 2025-06-30'},
 {id:'wps',icon:'doc',tag:'办公软件集成',name:'WPS AI',sub:'模型服务嵌入办公软件与文档流程',flow:['用户需求','大纲 / 演示文稿','讲稿生成'],big:'',text:'GLM 进入办公内容生成场景，连接模型供给方与应用软件企业。',note:'招股章程披露的产品集成'},
 {id:'bank',icon:'bank',tag:'金融行业问答',name:'银行业务资料查询',sub:'某综合性企业的商业银行业务部门',flow:['法规与业务资料','金融新规咨询','问答处理'],big:'>50%',text:'相关问答流程 AI 自动化率',note:'招股章程披露，限定于该部门相关流程'},
]

/* 收入分项顺序：API 模型调用、企业通用模型部署、企业智能体交付、技术服务及其他（人民币亿元） */
export const finance={
 annual:{label:'2025 全年',note:'2025 年全年 · 经审计；趋势为 2023—2025 年',revenue:7.243,api:1.904,share:26.3,rd:31.804,loss:47.182,gross:2.97,
  mix:[1.904,3.657,1.657,.025],trend:{labels:['2023','2024','2025'],revenue:[1.245,3.124,7.243],rd:[5.289,21.954,31.804]},
  lead:'2025 年收入增至 <b>7.24 亿元</b>，以企业通用模型部署为主，API 占 <b>26.3%</b>；同期研发开支 <b>31.80 亿元</b>，为收入的 4.4 倍。'},
 half:{label:'2026 上半年',note:'2026 年 1—6 月 · 未经审计；与 2025 年同期比较',revenue:9.539,api:8.252,share:86.5,rd:21.312,loss:20.720,gross:2.52,
  mix:[8.252,.670,.556,.061],trend:{labels:['2025 上半年','2026 上半年'],revenue:[1.909,9.539],rd:[15.947,21.312]},
  lead:'2026 年上半年收入 <b>9.54 亿元</b>，是上年同期的 <b>5 倍</b>；API 模型调用占 <b>86.5%</b>，收入结构转向以付费调用为主。'},
}
export const mixLabels=['API 模型调用','企业通用模型部署','企业智能体交付','技术服务及其他']

export const sourceIndex=[
 {id:'S01',title:'GLM / P-Tuning v2 论文',desc:'方法定义、基金致谢与项目编号',refs:['glm','ptuning']},
 {id:'S02',title:'三件企业专利公开文本',desc:'跨语言摘要、跨语言问答、参数高效检索',refs:['summary','qa','retrieval']},
 {id:'S03',title:'模型报告与官方代码',desc:'ChatGLM 技术路线、P-Tuning 实现、CodeGeeX2',refs:['chatglm','glm130b','ptcode','code']},
 {id:'S04',title:'智谱招股章程',desc:'产品集成、应用场景与产品使用指标',refs:['prospectus']},
 {id:'S05',title:'年度与中期财务披露',desc:'收入结构、研发开支、毛利与集团盈亏',refs:['annual','annualreport','interim']},
]
