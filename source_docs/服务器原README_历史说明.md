> 历史来源说明，已由根 README 和 docs/00–08 替代。只用于追溯旧设计/部署背景；其中旧演示值、执行限制与路径不适用于当前协作版。

# Cursor 前端美化工作区

在 Cursor Remote SSH 中直接打开 **`/root/gzk_jc/dashboard/cursor_ui`**。这是2026-09-24已上线版本的独立源码副本；本次只改视觉与体验，现有内容逻辑由项目总协调维护。先读本页，再看对应组件即可开始，不必重新研究全部数据或历史聊天。

## 项目背景与当前进展

国自科项目研究“基础研究支撑经济发展全链条数据系统构建与集成”，贯通**创新链、产业链、政策链**。总协调负责技术词典、survey、技术演进、证据链、指标与Dashboard；数据负责人负责采集、验收与入库；刘洁研究产业链，耀元研究政策链。标题不能把整个项目缩成仅创新链，也不能把尚在筹备的产业/政策专题写成已完成。

当前页面已实现：

| 页面 | 要保留的内容与交互 |
|---|---|
| 数据总览 `/overview` | 数据规模／更新动态／资源明细三个标签；九类数据圆环、右侧均衡横条、四大数字；真实登记活动日历、趋势与分页 |
| 领域数据 `/data` | 低空经济／人工智能切换；按论文、基金、专利等类型设计不同统计；AI年份中2016年前合并，2016单独显示 |
| 技术演进 `/evolution` | AI：七类70词纵向技术树，基础模型、算力两条主干；节点详情、综述阅读、重点技术时间轴、综述库；低空：原六类33点技术树 |
| 证据链 `/chain` | 多链关系、构建过程、可交互证据图、基金贡献度；保持样本与总体、关联与因果的区别 |
| 案例专题 `/cases` | 产业链与政策链专题，当前保留“筹备中” |

基线：数据/API为`llm_dashboard_20260922_v9`，前端为`names_20260924`。共同关键词是2026-09-18确认的7类、29组、70词；AI领域数量仍引用旧54词筛选快照，不能因美化改成“新70词完整领域统计”。survey实时可读状态由接口返回；美化不启动/停止/重跑生成任务。

全项目权威材料（按需读取，不复制维护）：
- `/root/gzk_jc/docs/00_阅读指南.md`：用户固定入口。
- `/root/gzk_jc/docs/01_项目总览.md`：研究目标与三链分工。
- `/root/gzk_jc/docs/02_工作方法.md`：观察单位、共同词表、证据解释。
- `/root/gzk_jc/docs/03_当前进展与计划.md`：“双领域Dashboard科研展示版（2026-09-24）”；survey状态看该文对应章节及批次实时README，旧速览不是实时状态。
- `/root/gzk_jc/docs/04_数据现状与入库.md`：数据事实；最新资产查`data/catalog/已有数据一览.md`和`sources/REGISTRY.md`。
- `/root/gzk_jc/docs/05_使用与维护.md`：“LLM独立Dashboard”、数据名称与演示数值、9月23日前端内容与后续美化约定、正式修改锁和恢复约定。

## 改哪里

| 本目录路径 | 作用 |
|---|---|
| `web/src/App.vue`、`shell.css`、`style.css` | 主站框架、全局排版与导航 |
| `web/src/components/OverviewHub.vue`、`CatalogPulse.vue`、`DatasetCatalog.vue` | 数据总览三标签 |
| `web/src/components/DomainHub.vue` | AI领域数据 |
| `web/src/components/EvolutionHub.vue`、`TechnologyEvolutionTree.vue`、`FeaturedTechnologyTimeline.vue` | AI技术演进与综述 |
| `web/src/components/EvidenceHub.vue`、`FundContribution.vue` | AI证据链及基金贡献 |
| `web/src/components/LowAltitudeEmbed.vue` | 低空嵌入容器 |
| `lowalt/src/` | 低空嵌入的布局、接口与显示适配 |
| `legacy/src/` | **独立复制的**低空组件，可在这里美化；不会改原低空站 |
| `web/src/helpers/foundationSources.js` | 已确认名称、单位及临时演示配置，优先保持 |
| `ui.config.mjs`、两侧`vite.config.js` | 已隔离的缓存、构建输出与只读API代理，勿改回生产路径 |

Vue 3 + Vite + ECharts / G6。组件已有基础动效，延续人大红、科研展示气质；文字清晰、有分量，标题层级醒目，两侧留白，适合大屏汇报，同时兼顾普通电脑。用户希望丰富、互动、精致，避免产品营销式文案、堆砌目录和开发日志；不要用删除图表、缩减类别来换取简洁。

## 启动与构建

已经复制源码并验证构建；`node_modules`复用服务器现有依赖，不是源码链接。**无需安装依赖，不要对这些链接执行npm install/ci/update**；需要新增依赖时先改成独立安装目录，再与总协调协调。

```bash
cd /root/gzk_jc/dashboard/cursor_ui
npm run dev
```

预览仅监听服务器本机：在Cursor的Ports面板转发5184端口，然后打开`http://localhost:5184/overview`。预览服务本次验证后已停止，由你运行上面的命令启动；若端口被占用，先确认是否自己已经启动，不杀其他任务。

- 改`web/src`自动热更新。
- 改`legacy/src`或`lowalt/src`后运行`npm run build:lowalt`，刷新页面。低空iframe由**副本构建**供给，非线上低空页面。
- 完整验证：`npm run build`；查看构建版：停止自己的dev后`npm run preview`（同为5184）。
- 两侧构建与缓存只写`/root/gzk_jc/data/outputs/shared/ui_handoff/cursor_20260924/`，不覆盖5174。低空指标引用此目录的`reference_serving/authoritative_metrics.json`冻结副本。
- API只读代理现有5174，因此本工作区需同一服务器的既有后端可用；不是离线整站。报错时检查接口，不伪造数据，也不重启生产服务。

## 内容与操作边界

1. 可以调整配色、字体、留白、布局、图表样式、动效、响应式和交互易用性。保留五页结构、两领域、已确认文案与统计、可点击溯源、深链、综述阅读、详情外部点击/Esc关闭。技术树坐标可优化，关键词、年代、关系含义和证据不能凭美观重写。
2. 四大数是中文期刊文献、国自然资助论文、国自然基金项目、专利公开文献。前两者按来源记录计数，不能相加为唯一论文总数。九类／14来源应保留；AI专项数据不塞回全领域总览。增量取真实比较回执，不能编造增长或把刷新当新增。
3. **专利690.4万是用户要求的临时演示值，必须保留紧邻的“演示值”及真实库存入口**；真实库存56,903,568仍在资源明细。演示数不得写回API/数据库，不参与真实增量计算。详细说明在05。
4. 图表、样本、综述引用数保持语义；不要把引文等同技术采用/经济贡献，不把筹备模块写成已完成。工程边界解释放文档，前端保留必要的真实状态与演示识别。
5. **唯一改动工作区是本目录**；产物只写上述独立输出目录。原`dashboard/llm`、`dashboard/web`、5174/5173/8080、数据库、原件、survey和数据负责人的目录不修改；不用Git提交/推送，不启动模型调用。
6. 正式修改仍按主项目AGENTS/05执行共用`.maintenance/formal_writer.lock`、verified检查点、seal及恢复预检。主项目根为`/root/gzk_jc`，不要在此副本另起恢复管理体系。全局检查点可能因既有RAR权限失败，可按05对本工作区及独立产物建逐SHA核验的限定备份，不改原件权限、不暂停后台任务。
7. 当前用户授权是副本美化与预览。完成后提供预览、改动文件、验证结果及遗留问题；总协调审阅差异后集成发布，不整包覆盖生产或使用旧备份恢复全项目。

## 备份与交付

美化前备份：`/root/gzk_jc/data/outputs/shared/ui_handoff/cursor_20260924/frontend_before_cursor_20260924.tar.gz`。
同目录`backup_manifest.json`记录170个文件SHA；已独立解包逐文件核验，包含两侧源码、低空依赖源码、包锁、当前线上构建及相关配置/文档。没有硬链接，不含node_modules、业务数据库或密钥；这是一份前端备份，不是整库备份。`source_copy_baseline.json`记录工作副本与原文件对应，便于后续提取美化差异。

本说明是本次UI交接入口，不作为新的项目进度台账。数值/口径冲突集中交总协调；颜色、间距、动效等常规视觉选择自行完成并验证。

## 研究力量页面（PR #1）

入口参数：`/chain?domain=ai` 原始页；`module=investment` 投入产出；`module=strength` 研究力量（总体格局）；再加 `view=continuity` 查看接续与证据。

本地页面已集成已审定的 `claude/research-strength-v2`；服务器启动、API代理及资产路径继续使用本目录原有配置。


## 人工维护更新动态（2026-11-05）

唯一内容入口：`web/content/catalog-activity.json`。这是独立的展示台账，页面不再调用`/api/llm/catalog-activity`、扫描接收目录或自动同步后台库存。可在任意工作端编辑该文件，并随前端代码一起交接；不要另改日历或趋势里的数字。

在`events`数组中复制一条记录，填写唯一`id`、`date`（YYYY-MM-DD）、`title`、`detail`及`status`（received/loaded/published）。`receivedBatches`、`loadedBatches`、`publishedBatches`分别表示本条对接收、入库、展示批次的贡献，均为非负整数；只写说明的记录填0。接收10批且其中2批入库可填10、2、0；之后补写入库事件时接收填0，避免重复累计。`records`与`files`是可选的记录数、文件数，不作为批次数。`origin`为维护备注，不在页面展示。

例：
```json
{"id":"manual-20261105-01","date":"2026-11-05","status":"received","title":"专题资料补充","detail":"本次补充内容说明","receivedBatches":3,"loadedBatches":0,"publishedBatches":0}
```

顶部“最新规范库交付”同样维护在本文件的`latestRelease`内。修改后更新`updatedAt`。日历与每日／每周／累计趋势、筛选明细从同一份记录计算。沿用历史展示的日期和深浅，无重新分配逻辑；历史来源注记保留在文件内。

开发服务读取文本文件，点击“刷新”重新读取；正式静态部署需运行`npm run build`发布更新后的文件。文件有JSON语法、唯一编号、日期及批次数校验；读取错误会保留已加载内容并提示重试。该台账为人工展示内容配置，不写入后台接收台账或研究数据库。


## 共用交互规则（2026-11-05）

同一层级的页面使用以下公共实现，后续增加页面时直接复用：

- `shared/interactions.css`：内容标签的字体、间距和下划线；内容短淡入；次级工具按钮、提示框、详情浮层、遮罩与键盘焦点。顶层导航、领域切换、模块导航仍保留各自层级样式。选中标签不持续闪动。
- `web/src/components/CountValue.vue`：数据页数字使用650ms计数；领域页的卡片入场沿用软著页规则。指标条固定六列，较窄屏幕切换三列／两列，卡片数量变化不再改变每张卡片宽度。低空页面复用同一数字组件。
- `shared/chartPresentation.js`：两侧数据页图表的入场、更新及悬浮提示默认样式；不修改图表系列、统计值及交互语义。投入产出曲线继续保持无悬浮提示。
- `web/src/helpers/useYearPlayback.js`：研究力量年度播放；默认显示最后一年，手动播放每秒一年，暂停保持当前年份，完成后停止，拖动年份先暂停。
- `shared/annual-player.js`／`.css`：四份投入产出HTML采用相同播放规则；年份和数字短淡入、金额不滚动。切换论文／专利后默认显示该组最后一年。`python manage.py run dashboard/cursor_ui/scripts/build_ai_chain.py --animations-only`仅生成这五份展示资源及来源摘要，不重算研究数据。原始HTML保留，展示适配在生产脚本内追加。
- `web/src/helpers/useSurface.js`：详情浮层支持外部点击与Esc关闭；模态框统一滚动锁定、键盘焦点限制及关闭后焦点返回。技术树原有节点关闭逻辑保留，外观使用公共样式。

系统开启“减少动态效果”时，数字直接显示最终值，入场／过渡关闭；年度播放仍由用户主动触发。关系线的流动保留其数据关系表达用途，正常模式下继续播放。

验收证据：`data/outputs/shared/ui_handoff/cursor_20260924/verification/unify_dashboard_interactions_20261105/`。本轮未修改业务数据库、研究力量JSON及四份动画内嵌数据。
