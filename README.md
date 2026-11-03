# 国自科 Dashboard 前端

当前 5184 Dashboard 的独立前端代码，用于 Claude 修改展示并通过 Pull Request 合并。**这份现有设计尚未获用户认可，不是目标模板。请按用户提供的《研究力量接续.pdf》和研究力量版图逐页重新设计。**

## 快速启动

需要 Node.js 20.19+（推荐22）和 npm。

```bash
npm ci
npm run build:lowalt
npm run dev
```

打开 `http://localhost:5184/chain?domain=ai&module=strength`。

默认 `demo` 模式提供合成样例和公开技术节点，用于排版、交互和截图，不包含业务数据库或真实关联明细。示例不是研究结果；部分历史组件仍包含原有展示文案，不能从演示数字推导新结论。数据总览、领域数据与综述在演示模式下仅提供空结构；完整数据通过下面的只读后端接入。

## 接入服务器数据

复制 `.env.example` 为 `.env.local`，设置：

```dotenv
DASHBOARD_MODE=live
DASHBOARD_API_BASE=http://127.0.0.1:5174
DASHBOARD_ARTIFACTS=/absolute/path/to/private/dashboard-assets
```

`DASHBOARD_API_BASE` 指向既有只读 API。远程电脑可先通过自己的 SSH 权限将服务器5174端口转发至本机；勿向公网开放数据库。`DASHBOARD_ARTIFACTS` 下应有 `analysis_public/chain-analysis/v1/`（研究力量JSON和五份动画HTML）及 `reference_serving/authoritative_metrics.json`。真实展示资产保留在服务器，未上传GitHub；服务器内的原路径由维护者配置。改完环境配置重启开发服务。

## 页面与代码

| 页面 | 主要文件 |
|---|---|
| 全站框架、导航、领域切换 | `web/src/App.vue`、`shell.css`、`style.css` |
| AI证据链模块入口 | `web/src/components/AiChainWorkspace.vue` |
| 原始证据链（保留第一标签） | `web/src/components/EvidenceHub.vue` |
| 投入、论文专利、70技术点、曲线 | `web/src/components/InvestmentOutcomes.vue` |
| 机构时间版图 | `web/src/components/ResearchLandscape.vue` |
| 基金负责人接续和案例 | `web/src/components/ResearchContinuity.vue` |
| 技术树与综述 | `web/src/components/EvolutionHub.vue`等 |
| 低空嵌入页 | `lowalt/src/`与`legacy/src/` |

入口参数：`/chain?domain=ai` 原始页；`module=investment` 投入产出；`module=strength` 研究力量（总体格局）；再加 `view=continuity` 查看接续与证据。

`demo/` 是设计样例；`scripts/build_ai_chain.py` 是服务器端展示数据生产器源码，依赖完整项目和本地数据，在本仓库中不用运行。`SOURCE_MAP.json` 记录服务器源文件对应及交接时SHA，便于回合并核对。

## 修改与合并

1. 从 `main` 建功能分支，例如 `claude/research-strength-design`。
2. 按 `CLAUDE.md` 逐页设计，保留原始证据链和其他页面。
3. `npm run build`；在1440/1920宽屏检查布局、文字重叠、年份、筛选、点击详情和窄屏滚动。
4. 提交PR，附改动说明和关键页面截图，注明使用演示还是实际数据。
5. 经用户审阅后合并 `main`。**合并不会自动部署服务器**；维护者按源文件对应表核查差异，在既有备份流程下集成到5184。

工作区源码的相对结构与服务器 `dashboard/cursor_ui/` 一致。移植时保留服务器的环境路径与只读代理配置；不要直接用仓库演示配置覆盖服务器配置。当前站点不会因创建本仓库发生变化。

## 构建

`npm run build` 构建主站和低空页，产物位于忽略的 `.runtime/build/`；`npm run preview` 预览构建版。GitHub Actions只检查构建，不部署。真实数据、`.env.local`、依赖和构建目录均不入Git。
