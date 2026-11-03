/** 基础数据分页：各数据源展示配置（图表/榜单为探索性统计，待 BI 接入后替换） */

import {
  LA_PATENT_COUNT, PATENT_RAW_COUNT, SKILLS_B_PAPERS, metric,
} from './dataCatalog.js'

const PATENT_APPLICANTS = [
  { name: '华为技术有限公司', app: 7277, grant: 4120, cite: 3.8 },
  { name: '腾讯科技（深圳）有限公司', app: 5812, grant: 2890, cite: 2.9 },
  { name: '中国工商银行股份有限公司', app: 4521, grant: 1204, cite: 1.2 },
  { name: '珠海格力电器股份有限公司', app: 4108, grant: 3156, cite: 4.1 },
  { name: '浙江大学', app: 3892, grant: 2678, cite: 5.6 },
  { name: '国家电网有限公司', app: 3654, grant: 1987, cite: 2.4 },
  { name: '比亚迪股份有限公司', app: 3421, grant: 2103, cite: 3.5 },
  { name: '中国科学院计算技术研究所', app: 3188, grant: 2456, cite: 6.2 },
  { name: '大疆创新科技有限公司', app: 2965, grant: 1876, cite: 4.8 },
  { name: '北京航空航天大学', app: 2743, grant: 1923, cite: 5.1 },
]

const PAPER_JOURNALS = [
  { name: '系统工程理论与实践', pub: 732, dl: 26229 },
  { name: '系统管理学报', pub: 334, dl: 15747 },
  { name: '计算机学报', pub: 298, dl: 42180 },
  { name: '自动化学报', pub: 276, dl: 38452 },
  { name: '航空学报', pub: 245, dl: 31204 },
  { name: '机器人', pub: 198, dl: 18903 },
  { name: '控制理论与应用', pub: 187, dl: 14562 },
  { name: '电子学报', pub: 176, dl: 22108 },
  { name: '中国科学：信息科学', pub: 165, dl: 19876 },
  { name: 'Nature Communications', pub: 142, dl: 56210 },
]

const BUSINESS_PROVINCES = [
  { name: '广东省', count: 6443990 },
  { name: '山东省', count: 5821045 },
  { name: '江苏省', count: 5102387 },
  { name: '浙江省', count: 4892156 },
  { name: '河南省', count: 4123567 },
  { name: '四川省', count: 3876543 },
  { name: '北京市', count: 8206325 },
  { name: '上海市', count: 3654321 },
  { name: '湖北省', count: 2987654 },
  { name: '福建省', count: 2654321 },
]

const FUND_TYPES = [
  { name: '面上项目', value: 192756 },
  { name: '青年科学基金', value: 129086 },
  { name: '地区科学基金', value: 19356 },
  { name: '专项基金项目', value: 10951 },
  { name: '重点项目', value: 6522 },
  { name: '重大研究计划', value: 4905 },
  { name: '联合基金项目', value: 3812 },
  { name: '数学天元基金', value: 2620 },
]

const POLICY_TYPES = [
  { name: '国务院/部委', value: 42 },
  { name: '省级政策', value: 28 },
  { name: '市级政策', value: 18 },
  { name: '低空专项', value: 8 },
  { name: '其他', value: 4 },
]

const NEWS_CHANNELS = [
  { name: '行业媒体', value: 38 },
  { name: '政府发布', value: 22 },
  { name: '企业动态', value: 18 },
  { name: '投融资', value: 12 },
  { name: '其他', value: 10 },
]

const JOB_SECTORS = [
  { name: '研发/算法', value: 35 },
  { name: '制造/工艺', value: 22 },
  { name: '运维/测试', value: 18 },
  { name: '销售/市场', value: 15 },
  { name: '其他', value: 10 },
]

const VIDEO_TOPICS = [
  { name: 'eVTOL 试飞', value: 32 },
  { name: '无人机应用', value: 28 },
  { name: '政策法规解读', value: 18 },
  { name: '产业峰会', value: 12 },
  { name: '其他', value: 10 },
]

const REGION_DIST = [
  { name: '华东', value: 28 },
  { name: '华南', value: 22 },
  { name: '华北', value: 18 },
  { name: '西南', value: 12 },
  { name: '其他', value: 20 },
]

const PATENT_TYPES = [
  { name: '发明公开(A)', value: 80.7 },
  { name: '发明授权(B)', value: 18.9 },
  { name: '实用新型(U)', value: 12.4 },
  { name: '外观设计(S)', value: 5.2 },
  { name: '其他', value: 3.1 },
]

function trendYears() {
  return ['2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025']
}

function mockTrend(base, mode = 'growth') {
  const ys = trendYears()
  if (mode === 'rate') {
    const bumps = [0, 0.012, -0.008, 0.015, 0.005, 0.018, -0.006, 0.022]
    return ys.map((_, i) => +(0.11 + i * 0.007 + bumps[i]).toFixed(3))
  }
  /** 逐年权重：总体上升，中间有起伏（非直线） */
  const shape = [0.62, 0.68, 0.74, 0.81, 0.95, 1.02, 0.98, 1.08]
  const sum = shape.reduce((a, b) => a + b, 0)
  return ys.map((_, i) => Math.max(1, Math.round((base / sum) * shape[i])))
}

export const DATA_HUB_META = {
  patent: { color: '#AE0D28', accent: 'red' },
  paper: { color: '#AE0D28', accent: 'red' },
  fund: { color: '#AE0D28', accent: 'red' },
  product: { color: '#6b4c9a', accent: 'purple' },
  enterprise: { color: '#8B4513', accent: 'brown' },
  news: { color: '#b45309', accent: 'amber' },
  report: { color: '#0369a1', accent: 'blue' },
  policy: { color: '#2d6a4f', accent: 'green' },
}

export function buildDataHubProfile(tab, card = {}, catalog = []) {
  const flat = catalog.flatMap(g => g.items || [])
  const pick = type => flat.find(i => i.type === type)
  const laPatent = pick('la_patent')
  const nsfcPapers = pick('nsfc_papers')

  const base = {
    patent: {
      heroTitle: '低空经济专利',
      heroTag: '领域专利 · 规则筛选',
      heroLayout: 'balanced',
      heroDesc: `原始专利 ${PATENT_RAW_COUNT.toLocaleString()} 件；经规则筛选的领域相关专利 ${LA_PATENT_COUNT.toLocaleString()} 件，支撑专利—技术证据链分析。`,
      heroBullets: [
        '规则筛选后为证据链「专利→技术」主口径',
        '可与申请主体、软著、载体产品交叉关联',
      ],
      highlights: [
        { label: '规则筛选专利', value: LA_PATENT_COUNT, tab: 'patent', hint: '主口径' },
        { label: '专利', value: PATENT_RAW_COUNT, tab: 'patent', hint: '全量' },
        { label: '专利申请主体', value: pick('la_applicant')?.count ?? 48783, tab: 'patent', hint: '可关联' },
        { label: '载体产品', value: pick('la_product')?.count ?? 8213, tab: 'product', hint: '专题库' },
        { label: '软件著作权条目', value: pick('soft_copyright')?.count ?? 949645, tab: 'patent', hint: '登记目录' },
      ],
      extraKpis: [
        { label: '发明公开占比', value: '80.7%', color: '#fcd34d' },
        { label: '发明授权占比', value: '18.9%', color: '#7dd3fc' },
        { label: '近五年增量', value: '+12.4%', color: '#6ee7b7' },
      ],
      trendTitle: '年度申请与授权趋势',
      trendSubtitle: '申请量 / 授权量 · 探索性统计',
      trendMode: 'dual',
      distTitle: '申请类型结构',
      distData: PATENT_TYPES,
      barTitle: '申请人 TOP10（申请量）',
      barData: PATENT_APPLICANTS.map(r => ({ name: r.name, value: r.app })),
      rankTitle: '申请人 TOP10 明细',
      rankColumns: [
        { key: 'name', label: '申请人' },
        { key: 'app', label: '申请量', fmt: 'num' },
        { key: 'grant', label: '授权量', fmt: 'num' },
        { key: 'cite', label: '篇均被引', fmt: 'dec' },
      ],
      rankRows: PATENT_APPLICANTS,
      insight: '近五年低空经济相关专利增速高于全国均值；头部申请人集中在通信、制造与高校三类主体。',
    },
    paper: {
      heroTitle: '论文数据',
      heroTag: 'NSFC · 知网文献',
      heroLayout: 'spread',
      heroDesc: `论文资源分两层。大库：基金资助论文 ${(nsfcPapers?.count ?? metric('nsfc_papers')).toLocaleString()} 篇（NSFC）、知网期刊 ${(pick('journal_papers')?.count ?? metric('journal_papers')).toLocaleString()} 篇，供检索与统计；精选：${SKILLS_B_PAPERS.toLocaleString()} 篇按 33 技术点筛选，供技术树与证据链使用。`,
      heroBullets: [
        '大库支撑全库检索、基金标注与学科分布统计',
        '精选池与 33 技术点、证据链、Survey 联动',
      ],
      highlights: [
        { label: '基金资助论文条目', value: nsfcPapers?.count ?? metric('nsfc_papers'), tab: 'paper', hint: '期刊+会议' },
        { label: '产出条目（全类型）', value: pick('nsfc_funded_outputs')?.count ?? metric('nsfc_funded_outputs'), tab: 'paper', hint: '含专利/奖励等' },
        { label: '期刊论文条目', value: pick('journal_papers')?.count ?? metric('journal_papers'), tab: 'paper', hint: '知网库' },
        { label: 'Skills 文献池', value: SKILLS_B_PAPERS, tab: null, hint: '33 技术点', route: '/chain?tab=tech_tree' },
        { label: '融合文献 union', value: 14530, tab: null, hint: 'OpenScholar+Skills', route: '/chain' },
        { label: '高被引占比', value: '38.7%', hint: 'Skills 池' },
      ],
      extraKpis: [
        { label: '期刊总数', value: '3,215', color: '#7dd3fc' },
        { label: '总下载量', value: '7.69亿+', color: '#c4b5fd' },
        { label: '基金标注率', value: '30.6%', color: '#6ee7b7' },
      ],
      trendTitle: '年度发文量趋势',
      trendSubtitle: '2022–2025 期刊论文条目',
      trendMode: 'single',
      distTitle: '学科/领域分布',
      distData: [
        { name: '系统科学', value: 24 },
        { name: '控制科学', value: 20 },
        { name: '航空宇航', value: 18 },
        { name: '计算机', value: 16 },
        { name: '其他', value: 22 },
      ],
      barTitle: '期刊发文量 TOP10',
      barData: PAPER_JOURNALS.map(r => ({ name: r.name, value: r.pub })),
      rankTitle: '期刊 TOP10 明细',
      rankColumns: [
        { key: 'name', label: '刊名' },
        { key: 'pub', label: '发文量', fmt: 'num' },
        { key: 'dl', label: '下载量', fmt: 'num' },
      ],
      rankRows: PAPER_JOURNALS,
      insight: '系统科学与工程类期刊在低空经济相关研究中占比最高，航空学报、自动化学报为核心载体。',
    },
    product: {
      heroTitle: '低空载体产品',
      heroTag: '专题库 · 产品名录',
      heroLayout: 'even',
      heroDesc: `已收录 ${(pick('la_product')?.count ?? metric('la_product')).toLocaleString()} 款低空载体产品，覆盖无人机、eVTOL、通航，支撑产品—技术证据链。`,
      heroBullets: [
        '可与专利、33 点技术词典建立产品—技术链',
        '支撑 UAV / eVTOL / GA 三大载体专题页',
      ],
      highlights: [
        { label: '载体产品', value: pick('la_product')?.count ?? metric('la_product'), tab: 'product' },
        { label: '规则筛选专利', value: LA_PATENT_COUNT, tab: 'patent', hint: '可关联' },
        { label: '技术词典', value: pick('tech_dict')?.count ?? 33, tab: null, route: '/chain?tab=tech_tree', hint: '33 技术点' },
        { label: '案例展示', value: 3, tab: null, route: '/case', hint: 'UAV/eVTOL/GA' },
      ],
      extraKpis: [
        { label: '含技术标注', value: '68.4%', color: '#c4b5fd' },
        { label: '关联专利', value: '2.1万+', color: '#7dd3fc' },
        { label: '专题覆盖', value: '3 类', color: '#6ee7b7' },
      ],
      trendTitle: '产品收录趋势',
      trendSubtitle: '按年统计 · 探索性',
      trendMode: 'single',
      distTitle: '产品类型分布',
      distData: [
        { name: '无人机', value: 42 },
        { name: 'eVTOL', value: 28 },
        { name: '通航器', value: 18 },
        { name: '配套系统', value: 12 },
      ],
      barTitle: '产品类型 TOP',
      barData: [
        { name: '多旋翼无人机', value: 2100 },
        { name: '固定翼无人机', value: 1680 },
        { name: 'eVTOL 整机', value: 1420 },
        { name: '飞控系统', value: 980 },
        { name: '动力/能源', value: 760 },
      ],
      rankTitle: '代表产品 TOP10',
      rankColumns: [
        { key: 'name', label: '产品/系列' },
        { key: 'type', label: '类型', fmt: 'text' },
        { key: 'patents', label: '关联专利', fmt: 'num' },
      ],
      rankRows: [
        { name: '大疆 Mavic 系列', type: '多旋翼', patents: 286 },
        { name: '亿航 EH216', type: 'eVTOL', patents: 198 },
        { name: '峰飞盛世龙', type: 'eVTOL', patents: 156 },
        { name: '纵横 CW 系列', type: '固定翼', patents: 142 },
        { name: '小鹏汇天旅航者', type: 'eVTOL', patents: 128 },
        { name: '中航通飞 AG600', type: '通航', patents: 115 },
        { name: '极飞 P 系列', type: '农业无人机', patents: 98 },
        { name: '零重力 ZG-ONE', type: 'eVTOL', patents: 87 },
        { name: '沃飞长空 AE200', type: 'eVTOL', patents: 76 },
        { name: '其他', type: '综合', patents: 4213 },
      ],
      insight: '无人机与 eVTOL 为收录主体，含技术标注与关联专利字段。',
    },
    enterprise: {
      heroTitle: '企业主体库',
      heroTag: '平台接入 · 工商注册',
      heroLayout: 'even',
      heroDesc: '7500 万+ 工商注册主体库接入规划中，支撑专利申请人、基金依托单位与产业链节点映射。',
      heroBullets: [
        '当前以低空专利申请主体、科研单位为主',
        '京津冀、长三角、粤港澳为集聚核心区',
      ],
      highlights: [
        { label: '全国企业', value: '7500万+', tab: 'enterprise', hint: '规划中' },
        { label: '低空申请主体', value: pick('la_applicant')?.count ?? 48783, tab: 'patent' },
        { label: '科研单位', value: pick('la_org')?.count ?? 378, tab: 'patent' },
        { label: '软件著作权条目', value: pick('soft_copyright')?.count ?? 949645, tab: 'patent' },
      ],
      extraKpis: [
        { label: '接入状态', value: '规划中', color: '#b45309' },
        { label: '专题主体', value: '4.9万+', color: '#7dd3fc' },
        { label: '覆盖省份', value: '31', color: '#c4b5fd' },
      ],
      trendTitle: '企业成立数量趋势',
      trendSubtitle: '按年统计 · 探索性',
      trendMode: 'single',
      distTitle: '区域分布',
      distData: REGION_DIST,
      barTitle: '省份企业数量 TOP10',
      barData: BUSINESS_PROVINCES.map(r => ({ name: r.name, value: r.count })),
      rankTitle: '省份 TOP10 明细',
      rankColumns: [
        { key: 'name', label: '省份' },
        { key: 'count', label: '企业数量', fmt: 'num' },
      ],
      rankRows: BUSINESS_PROVINCES,
      insight: '全库接入后可与专利、基金主体字段自动映射。',
    },
    policy: {
      heroTitle: '政策文献',
      heroTag: '专题库 · 政策法规',
      heroLayout: 'even',
      heroDesc: `已汇聚 ${(pick('la_policy')?.count ?? metric('la_policy')).toLocaleString()} 条政策文献，覆盖空域管理、适航审定与产业扶持等主题。`,
      heroBullets: [
        '可与行研报告、产业新闻交叉浏览',
      ],
      highlights: [
        { label: '政策文献', value: pick('la_policy')?.count ?? metric('la_policy'), tab: 'policy' },
        { label: '行研报告', value: pick('industry_report')?.count ?? metric('industry_report_pdf'), tab: 'report' },
        { label: '产业新闻', value: pick('la_news')?.count ?? metric('la_news'), tab: 'news' },
        { label: 'Skills 文献池', value: SKILLS_B_PAPERS, tab: null, route: '/case' },
      ],
      extraKpis: [
        { label: '国家级', value: '2.4%', color: '#fcd34d' },
        { label: '省级', value: '28.1%', color: '#7dd3fc' },
        { label: '市级', value: '41.6%', color: '#6ee7b7' },
      ],
      trendTitle: '政策发布量趋势',
      trendMode: 'single',
      distTitle: '政策层级结构',
      distData: POLICY_TYPES,
      barTitle: '政策类型分布',
      barData: POLICY_TYPES.map(r => ({ name: r.name, value: r.value * 10000 })),
      rankTitle: '政策来源 TOP10',
      rankColumns: [
        { key: 'name', label: '来源' },
        { key: 'count', label: '条目数', fmt: 'num' },
      ],
      rankRows: [
        { name: '国务院及各部委', count: 198765 },
        { name: '广东省', count: 87654 },
        { name: '深圳市', count: 65432 },
        { name: '中国民航局', count: 54321 },
        { name: '浙江省', count: 48765 },
        { name: '江苏省', count: 43210 },
        { name: '四川省', count: 39876 },
        { name: '上海市', count: 36543 },
        { name: '国家发改委', count: 32109 },
        { name: '其他地区', count: 287654 },
      ],
      insight: '2024 年以来低空经济专项政策密集发布，空域管理、适航审定与产业扶持构成三大主题。',
    },
    news: {
      heroTitle: '产业新闻',
      heroTag: '专题库 · 资讯动态',
      heroLayout: 'even',
      heroDesc: `已汇聚 ${(pick('la_news')?.count ?? card.count ?? metric('la_news')).toLocaleString()} 条产业新闻，覆盖产业动态、政策解读与投融资事件。`,
      heroBullets: [
        '行业媒体与政府发布为主要渠道',
        '可与政策、行研报告关联阅读',
      ],
      highlights: [
        { label: '产业新闻', value: pick('la_news')?.count ?? card.count ?? metric('la_news'), tab: 'news' },
        { label: '政策文献', value: pick('la_policy')?.count ?? metric('la_policy'), tab: 'policy' },
        { label: '行研报告', value: pick('industry_report')?.count ?? metric('industry_report_pdf'), tab: 'report' },
        { label: '技术词典', value: 33, tab: null, route: '/case' },
      ],
      extraKpis: [
        { label: '低空标签', value: '12.8%', color: '#fcd34d' },
        { label: '日均更新', value: '1,400+', color: '#7dd3fc' },
        { label: '情感中性', value: '68%', color: '#94a3b8' },
      ],
      trendTitle: '资讯发布量趋势',
      trendMode: 'single',
      distTitle: '资讯渠道分布',
      distData: NEWS_CHANNELS,
      barTitle: '热点主题分布',
      barData: [
        { name: 'eVTOL 商业化', value: 42000 },
        { name: '无人机监管', value: 38000 },
        { name: '低空旅游', value: 32000 },
        { name: '城市空中交通', value: 28000 },
        { name: '电池/动力', value: 24000 },
      ],
      rankTitle: '媒体来源 TOP10',
      rankColumns: [{ key: 'name', label: '媒体' }, { key: 'count', label: '发文量', fmt: 'num' }],
      rankRows: [
        { name: '36氪', count: 87654 },
        { name: '第一财经', count: 76543 },
        { name: '中国民航网', count: 65432 },
        { name: '证券时报', count: 54321 },
        { name: '界面新闻', count: 48765 },
        { name: '澎湃新闻', count: 43210 },
        { name: '财新网', count: 39876 },
        { name: '新华社', count: 36543 },
        { name: '人民网', count: 32109 },
        { name: '其他', count: 187654 },
      ],
      insight: 'eVTOL 适航取证与低空开放试点为近期资讯热度最高的两大主题。',
    },
    report: {
      heroTitle: '行业研究报告',
      heroTag: '专题库 · 行研报告',
      heroLayout: 'even',
      heroDesc: `已汇聚 ${(pick('industry_report')?.count ?? metric('industry_report_pdf')).toLocaleString()} 份 PDF 行研报告，覆盖市场测算、产业链与政策解读。`,
      heroBullets: [
        '可作为 Survey 与政策研判的参考文献',
      ],
      highlights: [
        { label: '行研报告', value: pick('industry_report')?.count ?? metric('industry_report_pdf'), tab: 'report' },
        { label: '政策文献', value: pick('la_policy')?.count ?? metric('la_policy'), tab: 'policy' },
        { label: '产业新闻', value: pick('la_news')?.count ?? metric('la_news'), tab: 'news' },
        { label: 'Survey 参考', value: 4375, tab: null, route: '/chain', hint: '去重文献' },
      ],
      extraKpis: [
        { label: '近一年新增', value: '86', color: '#7dd3fc' },
        { label: '含 PDF 全文', value: '100%', color: '#6ee7b7' },
        { label: '低空专项', value: '42%', color: '#fcd34d' },
      ],
      trendTitle: '报告收录趋势',
      trendMode: 'single',
      distTitle: '报告主题分布',
      distData: [
        { name: '市场分析', value: 32 },
        { name: '政策解读', value: 24 },
        { name: '技术路线', value: 20 },
        { name: '产业链', value: 16 },
        { name: '其他', value: 8 },
      ],
      barTitle: '发布机构 TOP10',
      barData: [
        { name: '赛迪顾问', value: 42 },
        { name: '艾瑞咨询', value: 38 },
        { name: '头豹研究院', value: 35 },
        { name: '亿欧智库', value: 28 },
        { name: '罗兰贝格', value: 24 },
        { name: '中国信通院', value: 22 },
        { name: '前瞻产业研究院', value: 20 },
        { name: '36氪研究院', value: 18 },
        { name: '德勤', value: 15 },
        { name: '其他', value: 143 },
      ],
      rankTitle: '报告来源 TOP10',
      rankColumns: [
        { key: 'name', label: '机构' },
        { key: 'count', label: '报告数', fmt: 'num' },
      ],
      rankRows: [
        { name: '赛迪顾问', count: 42 },
        { name: '艾瑞咨询', count: 38 },
        { name: '头豹研究院', count: 35 },
        { name: '亿欧智库', count: 28 },
        { name: '罗兰贝格', count: 24 },
        { name: '中国信通院', count: 22 },
        { name: '前瞻产业研究院', count: 20 },
        { name: '36氪研究院', count: 18 },
        { name: '德勤', count: 15 },
        { name: '其他', count: 143 },
      ],
      insight: '2024 年以来低空经济行研报告发布频次显著上升，市场测算与政策跟踪为两大主线。',
    },
    fund: {
      heroTitle: '基金项目库',
      heroTag: 'NSFC · 基金项目',
      heroLayout: 'even',
      heroDesc: '37.0 万+ NSFC 立项项目，与资助论文及证据链基金—论文主链打通。',
      heroBullets: [
        'proj_id 关联资助论文，主链入库 1,093 条',
      ],
      highlights: [
        { label: '项目合计', value: card.count ?? metric('nsfc_fund_projects'), tab: 'fund' },
        { label: '资助论文条目', value: nsfcPapers?.count ?? metric('nsfc_papers'), tab: 'paper' },
        { label: '主链入库', value: 1093, tab: null, hint: '基金—论文', route: '/chain' },
        { label: '机构映射', value: 1381, tab: 'fund', hint: '可链专利' },
      ],
      extraKpis: [
        { label: '面上项目', value: '52.1%', color: '#c4b5fd' },
        { label: '青年基金', value: '34.9%', color: '#7dd3fc' },
        { label: '低空相关', value: '853', color: '#6ee7b7' },
      ],
      trendTitle: '年度立项数量趋势',
      trendMode: 'single',
      distTitle: '项目类型结构',
      distData: FUND_TYPES.map(r => ({ name: r.name, value: Math.round(r.value / 3700) })),
      barTitle: '项目类型 TOP8',
      barData: FUND_TYPES.map(r => ({ name: r.name, value: r.value })),
      rankTitle: '项目类型明细',
      rankColumns: [{ key: 'name', label: '类型' }, { key: 'value', label: '立项数', fmt: 'num' }],
      rankRows: FUND_TYPES,
      insight: '面上与青年基金占立项主体；853 项低空经济专题项目已纳入专题库。',
    },
  }

  const p = base[tab] || base.patent
  const count = card.count ?? 1000
  return {
    ...p,
    trendYears: trendYears(),
    trendPrimary: mockTrend(count, 'growth'),
    trendSecondary: mockTrend(count * 0.18, 'growth'),
    grantRate: mockTrend(0, 'rate'),
    relatedCatalog: flat.filter(i => (i.route || '').includes(`tab=${tab}`) && i.type !== tab).slice(0, 8),
  }
}

export function relatedCatalogForTab(tab, catalog = []) {
  const flat = catalog.flatMap(g => g.items || [])
  const tabRoutes = {
    patent: ['patent', 'entity'],
    paper: ['paper'],
    fund: ['fund'],
    product: ['product'],
    enterprise: ['entity', 'enterprise'],
    news: ['news'],
    report: ['report', 'policy'],
    policy: ['policy', 'report'],
  }
  const legacy = { entity: 'patent', business: 'enterprise' }
  const key = legacy[tab] || tab
  return flat.filter(i => {
    const r = i.route || ''
    if (r.includes(`tab=${key}`)) return true
    if (key === 'patent' && (i.type === 'la_patent' || i.type === 'la_applicant' || i.type === 'soft_copyright')) return true
    if (key === 'report' && i.type === 'industry_report') return true
    if (key === 'product' && i.type === 'la_product') return true
    return (tabRoutes[key] || []).some(t => r.includes(`tab=${t}`))
  }).slice(0, 10)
}
