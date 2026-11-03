/** 三产品案例元数据（与 workflow.product_lines 合并展示） */

export const PRODUCT_CASES = [
  {
    id: 'UAV',
    name: '无人机',
    desc: '飞控 · 导航 · 集群协同 · 任务载荷',
    stage: '遥控平台 → 智能作业',
  },
  {
    id: 'eVTOL',
    name: '电动垂直起降',
    desc: '电推进 · 冗余飞控 · 适航合规',
    stage: '概念验证 → 商业化运营',
  },
  {
    id: 'GA',
    name: '通用航空',
    desc: '综合航电 · 安全体系 · 空域协同',
    stage: '活塞航空 → 数字绿色通航',
  },
]

export function productById(id) {
  return PRODUCT_CASES.find(p => p.id === id) || PRODUCT_CASES[0]
}

export function enrichProductLine(id, line = {}) {
  const meta = productById(id)
  return {
    id,
    name: line.name || meta.name,
    desc: meta.desc,
    stage: meta.stage,
    a_papers: line.a_papers,
    b_papers: line.b_papers,
    surveys: line.surveys ?? 4,
    fund_ratio_b: line.fund_ratio_b,
    status: line.status,
  }
}
