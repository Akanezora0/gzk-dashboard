# 人工智能技术关键词补充（2024—2026）

整理日期：2026-11-09
用途：补充现有 70 个技术点（`ai_keywords_7class_20260918_v4.json`）在 2024 年下半年至 2026 年的空缺，供撰写技术综述、补充技术演进事件与关键技术里程碑使用。

- 编号沿用各大类现有序号往后顺延，分组（`group_id`）沿用现有二级分组。
- “代表成果”填写首次公开的论文、技术报告或官方发布，日期为首次公开日期。
- 标 ★ 的条目建议进入“关键技术里程碑”，末尾附里程碑卡片与悬停介绍的文案草稿。

## 一、新增技术点

| 编号 | 大类 / 分组 | 技术点 | 英文 / 别名 | 定义（一句话） | 代表成果（首次公开） |
|---|---|---|---|---|---|
| AI1.10 | AI1 / G01 网络架构 | 线性与混合注意力架构 | linear attention, state space model, hybrid attention | 以线性复杂度的序列建模层替代或混合标准注意力，降低长序列计算与显存开销。 | Mamba: Linear-Time Sequence Modeling with Selective State Spaces，2023-12-01，CMU / Princeton，arXiv:2312.00752；后续 MiniMax-01（2025-01）、Qwen3-Next（2025-09）、Kimi Linear（2025-10） |
| AI1.11 ★ | AI1 / G03 多模态与生成模型 | 世界模型 | world model, interactive world generation | 学习环境的动态规律，按动作实时生成可交互、可持续演化的虚拟世界。 | Genie 3，2025-08-05，Google DeepMind，https://deepmind.google/discover/blog/genie-3-a-new-frontier-for-world-models/ ；前序 Genie，2024-02，arXiv:2402.15391 |
| AI1.12 ★ | AI1 / G02 语言建模 | 扩散语言模型 | diffusion language model, masked diffusion LM | 以掩码扩散逐步还原整段文本，替代逐词自回归生成，支持并行解码。 | Large Language Diffusion Models（LLaDA），2025-02-14，中国人民大学高瓴人工智能学院 / 蚂蚁集团，arXiv:2502.09992 |
| AI2.16 | AI2 / G04 推理与上下文 | 上下文工程 | context engineering | 为智能体系统地组织指令、工具、记忆与检索内容，在有限上下文窗口内保留最有效的信息。 | Effective context engineering for AI agents，2025-09-29，Anthropic，https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents |
| AI2.17 | AI2 / G03 反馈学习与对齐 | 智能体强化学习 | agentic RL, RL for agents | 在可交互环境中以任务完成情况为奖励训练模型的多步决策与工具使用能力。 | SWE-RL，2025-02-25，Meta，arXiv:2502.18449 |
| AI2.18 | AI2 / G04 推理与上下文 | 自适应推理与思考预算 | hybrid reasoning, thinking budget | 同一模型按任务难度在快速作答与深度思考之间切换，并可设定推理开销上限。 | Qwen3 Technical Report，2025-05-14，阿里巴巴通义千问，arXiv:2505.09388 |
| AI3.14 | AI3 / G03 计算与推理加速 | 低精度训练（FP8） | FP8 mixed-precision training | 以 8 位浮点完成大模型主体训练计算，显著降低训练成本与显存需求。 | DeepSeek-V3 Technical Report，2024-12-27，DeepSeek，arXiv:2412.19437 |
| AI3.15 | AI3 / G04 并行与调度 | 预填充—解码分离 | prefill-decode disaggregation | 将推理的预填充与解码阶段拆到不同资源池独立调度，提升吞吐并稳定时延。 | DistServe，2024-01-18，北京大学 / UCSD，arXiv:2401.09670；Mooncake，2024-06，月之暗面 / 清华大学，arXiv:2407.00079 |
| AI4.06 ★ | AI4 / G04 应用开发平台 | 智能体运行框架（Harness） | agent harness, harness engineering | 包裹在模型外部、管理长程任务的运行层：工具调用、上下文压缩、文件系统、子智能体、权限与反馈回路。 | Claude Code，2025-02-24，Anthropic；Harness engineering: leveraging Codex in an agent-first world，2026-02，OpenAI（报道见 https://www.infoq.com/news/2026/02/openai-harness-engineering-codex ） |
| AI4.07 ★ | AI4 / G04 应用开发平台 | 智能体互联协议 | Model Context Protocol (MCP), Agent2Agent (A2A) | 以开放协议统一模型与外部工具、数据源及其他智能体之间的连接方式。 | Model Context Protocol，2024-11-25，Anthropic，https://www.anthropic.com/news/model-context-protocol ；A2A，2025-04-09，Google；2025-12 起由 Linux 基金会下属 Agentic AI Foundation 托管 |
| AI4.08 ★ | AI4 / G04 应用开发平台 | 智能体技能 | Agent Skills | 以“说明文档 + 脚本 + 资源”的文件夹封装专门知识与工作流程，智能体按需加载。 | Agent Skills，2025-10-16，Anthropic，https://www.anthropic.com/news/skills ；2025-12 发布为开放标准，2026-10-22 捐赠 Agentic AI Foundation |
| AI5.15 | AI5 / G02 智能体与工具 | 计算机使用智能体 | computer use, GUI agent | 模型通过截图理解界面，以点击、输入等操作直接使用电脑与网页完成任务。 | Computer use（Claude 3.5 Sonnet），2024-10-22，Anthropic，https://www.anthropic.com/news/3-5-models-and-computer-use ；评测基准 OSWorld，2024-04，arXiv:2404.07972 |
| AI5.16 ★ | AI5 / G02 智能体与工具 | 深度研究智能体 | deep research agent | 自主规划检索、阅读数十至上百个来源并综合成带引用的研究报告。 | Deep research，2025-02-02，OpenAI，https://openai.com/index/introducing-deep-research/ ；Gemini Deep Research，2024-12-11，Google |
| AI5.17 ★ | AI5 / G03 语言与软件应用 | 编程智能体 | coding agent, agentic coding | 在真实代码库中自主阅读、修改、运行测试并提交代码，完成完整工程任务。 | SWE-agent，2024-05-06，Princeton，arXiv:2405.15793；Claude Code，2025-02-24，Anthropic；Codex CLI，2025-04-16，OpenAI |
| AI5.18 | AI5 / G06 推荐与自主系统 | 视觉—语言—动作模型 | vision-language-action model (VLA) | 在视觉语言模型上直接输出机器人动作，实现通用的感知—理解—操作。 | π0，2024-10-31，Physical Intelligence，arXiv:2410.24164；Gemini Robotics，2025-03-12，Google DeepMind |
| AI7.08 | AI7 / G03 攻击与防护 | 智能体安全 | agent security, tool-use safety | 防范智能体在调用工具、读取外部内容、加载技能时被注入指令或越权执行。 | AgentDojo，2024-06-19，ETH Zurich，arXiv:2406.13352；Supply-Chain Poisoning Attacks Against LLM Coding Agent Skill Ecosystems，2026-04 |
| AI7.09 | AI7 / G01 能力与偏好评测 | 长程任务评测 | task time horizon | 以模型能可靠完成的人类任务时长衡量智能体能力的增长。 | Measuring AI Ability to Complete Long Tasks，2025-03-18，METR，arXiv:2503.14499 |

### 现有技术点建议补充的近期事件

| 技术点 | 建议补充事件 |
|---|---|
| AI2.09 可验证奖励强化学习 | GRPO（DeepSeekMath，2024-02-05，arXiv:2402.03300）作为 DeepSeek-R1 的方法前序 |
| AI2.14 测试时计算扩展 | OpenAI o1（2024-09-12），推理模型路线的起点 |
| AI3.05 高效注意力 | Native Sparse Attention（2025-02-16，DeepSeek / 北京大学，arXiv:2502.11089，ACL 2025 最佳论文）；DeepSeek Sparse Attention（V3.2-Exp，2025-09-29） |
| AI5.12 视频生成 | Sora（2024-02-15，OpenAI）；Veo 3 音画同步生成（2025-05-20，Google DeepMind） |
| AI5.11 图像生成 | GPT-4o 原生图像生成（2025-03-25，OpenAI） |

## 二、建议新增的关键技术里程碑

| 时间 | 卡片名称 | 卡片副标题 | 对应技术点 |
|---|---|---|---|
| 2024.11 | MCP | 智能体连接标准 | AI4.07 智能体互联协议 |
| 2025.02 | LLaDA | 扩散语言模型 | AI1.12 扩散语言模型 |
| 2025.02 | Deep Research | 自主研究报告 | AI5.16 深度研究智能体 |
| 2025.02 | Claude Code | 编程智能体 | AI5.17 编程智能体 |
| 2025.08 | Genie 3 | 可交互世界模型 | AI1.11 世界模型 |
| 2025.10 | Agent Skills | 可加载的专业技能 | AI4.08 智能体技能 |
| 2026.02 | Harness 工程 | 智能体运行框架 | AI4.06 智能体运行框架 |

备选：DeepSeek-V3（2024.12，FP8 低成本训练，对应 AI3.14）、Computer Use（2024.10，对应 AI5.15）。

### 悬停介绍文案草稿

- **MCP**
  关键创新：用一套开放协议描述工具、数据源与提示模板，任何模型和应用都能以同一方式接入外部能力。
  带来的影响：成为智能体连接外部世界的事实标准，主流模型厂商与开发工具相继支持，并移交 Linux 基金会托管。
- **LLaDA**
  关键创新：以掩码扩散替代逐词生成，从整段被遮盖的文本出发逐步还原，8B 规模性能比肩同级自回归模型。
  带来的影响：证明大语言模型不必依赖自回归范式，打开并行解码与双向推理的新路线。
- **Deep Research**
  关键创新：以强化学习训练的智能体自主规划检索、阅读大量网页与文档，数分钟内写出带引用的研究报告。
  带来的影响：把智能体从“回答问题”推进到“完成研究任务”，各大平台随即推出同类功能。
- **Claude Code**
  关键创新：在终端中直接操作真实代码库，自主阅读、修改、运行测试，完成跨文件的完整工程任务。
  带来的影响：开启智能体编程的普及，软件开发转向“人定目标、智能体执行”的协作方式。
- **Genie 3**
  关键创新：根据文字描述实时生成可交互的三维世界，以每秒 24 帧响应操作并保持数分钟的场景一致。
  带来的影响：世界模型从视频生成走向可交互环境，为智能体与机器人训练提供无限的模拟场景。
- **Agent Skills**
  关键创新：把专门知识、流程与脚本打包成可按需加载的技能文件夹，智能体只在需要时读入相关内容。
  带来的影响：让通用智能体快速获得行业与组织的专门能力，发布为开放标准并捐赠 Agentic AI Foundation。
- **Harness 工程**
  关键创新：工程师设计运行环境、约束与反馈回路，智能体负责编写代码、测试与运维，模型外的运行层成为能力的关键。
  带来的影响：OpenAI 内部以此方式由智能体写出约百万行代码的产品，“模型 + 运行框架”成为评价智能体系统的整体单位。

## 参考来源

- Anthropic, Donating Agent Skills to the Agentic AI Foundation, 2026-10-22: https://www.anthropic.com/news/donating-agent-skills-to-the-agentic-ai-foundation
- Phil Schmid, The importance of Agent Harness in 2026, 2026-01-05: https://www.philschmid.de/agent-harness-2026
- InfoQ, OpenAI Harness Engineering with Codex, 2026-02-21: https://www.infoq.com/news/2026/02/openai-harness-engineering-codex
