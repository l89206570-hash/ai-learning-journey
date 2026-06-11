---
tags:
  - resources
  - ai-learning
  - reference
created: 2026-05-22
updated: 2026-06-11
---

# AI 学习资源库
> 自动维护，每周更新 | 最后更新: 2026-06-11

## 当前推荐学习（按优先级排序）
1. [Agent Learning Hub](https://github.com/datawhalechina/Agent-Learning-Hub) — Datawhale 系统性 AI Agent 路线图 + 11 级项目阶梯，适合 W4-W10
2. [AIcall](https://github.com/lin-ggyy/AIcall) — 轻量级 LLM 调用服务，学习 API 调用的工程写法，适合 W1-W2
3. [RAG_DeepDive_HandsOn](https://github.com/SumitCodesAI/RAG_DeepDive_HandsOn) — 从简单 RAG 到 Agentic RAG 的实操代码，适合 W4
4. [awesome-ai-agents-2026](https://github.com/Zijian-Ni/awesome-ai-agents-2026) — 2026 Agent 生态全景图，适合 W6
5. [RAGFlow](https://github.com/infiniflow/ragflow) — 生产级 RAG 引擎，学习架构设计，适合 W7
6. [Dify](https://github.com/langgenius/dify) — 开源 LLM 应用平台，学习产品化思路，适合 W8
7. [CrewAI](https://github.com/crewAIInc/crewAI) — 最快上手 Multi-Agent，适合 W10
8. [Superpowers](https://github.com/obra/superpowers) — Agent 行为层，强制设计门+计划+微任务 TDD，防 Agent 跳过设计直接写代码，适合 W5+

## 最近动态（2026-06-11 中周扫描）

**AI 行业重大新闻：** Anthropic 以 $9650 亿估值申请 IPO，年化收入超 $470 亿，Claude 编写自身 80%+ 代码。同时呼吁全球暂停高级 AI 开发（递归自我改进失控风险）。SpaceX 签约 Google（$92 亿/月）和 Anthropic（$125 亿/月）GPU 计算租赁，总合同超 $7000 亿。OpenAI 将 ChatGPT 转型为"超级应用"（集成编码工具+AI Agent）。Nvidia RTX Spark "PC Superchip" Computex 发布，将 AI 处理带入笔记本。特朗普签署行政令要求 AI 模型接受联邦安全测试（发布前最长 30 天审查）。《大美国 AI 法案》（269 页）引入全面联邦 AI 框架，冻结州级 AI 法律 3 年。

**CrewAI v1.14.7a2（6月5日）：** 新增 Conversational Flow Tracing、Chat API、更丰富的 LLM 事件（finish_reason/sampling/response.id）、Flow DSL 重构、可覆盖 Locking Backend。Stars → 51.6K（+3.8K）。项目处于高速迭代期（领先上次稳定版 152 commits）。

**LlamaIndex v0.14.22（5月14日）：** 新增多模态合成、GPT-5.5 支持、Claude Opus 4.7 支持。重新定位为"领先的文档 Agent 和 OCR 平台"，2026 重点方向是"长周期文档 Agent"。Stars → 49.5K（+3.5K）。

**LangChain：** langchain-core 1.4.1、langchain 1.3.6，常规迭代，修复 Bedrock 预验证、stream assembly v3 改进、安全依赖升级（pygments CVE 修复）。无架构级变化。

### 2026-06-09 扫描（本周一）

**GitHub 2026 趋势确认：** Dify 143K stars 领跑全平台，Hermes Agent 150K（自学习个人 AI）、OpenHands 60.5K（自主编程 Agent）、MetaGPT 59.6K（多 Agent 模拟软件公司）、OpenCode 55K（模型无关编程 Agent）、Cline 49K（VS Code 原生 Agent）。Rust 开始进入 Agent 框架（推理速度 3.8x Python），上下文压缩层（Headroom）成为新基建。

**杭州招聘验证：** 海康/钉钉/字节/淘天/招商银行全线招聘 AI Agent 开发。核心技能要求：Python（必会）、LangChain/LangGraph、RAG、Agent 框架、Prompt Engineering。加分项：Java/Go、Docker/K8s、模型微调（SFT/RLHF）、MCP 协议。实习岗 12K-18K/月。钉钉要求持有《AI应用工程师》证书——关注是否需要考。

**React + AI Stack 固化：** Next.js 15 + Vercel AI SDK + Zustand 成为前端标配。"Vibe Coding"（自然语言生成完整实现）成为新默认开发范式。

### 2026-06-08 扫描（上周）

**LangGraph 2.0 生产化：** 2月发布，Guardrail Nodes（ContentFilter/RateLimiter/AuditLogger）提升为一等原语，原生 MCP/A2A 多智能体协议支持，v1 起承诺 2.0 前不引入破坏性变更。v1.2.x 系列持续迭代到 6 月。

**MCP 协议成熟：** 已捐赠给 Agentic AI Foundation（Linux Foundation），月下载量 ~9700 万（16 个月增长 4750%）。MCP 负责 Agent↔Tool 连接，A2A 负责 Agent↔Agent 通信。2026-07-28 spec 大版本锁定，转向无状态协议。安全成 CISO 级关注点。

**Claude Agent SDK 订阅化：** 2026-06-15 起，Claude Pro/Max/Team 订阅包含每月 Agent SDK 额度（$20-$200），无需单独 API Key。Claude Code 新增 Dynamic Workflows（研究预览）——多 Agent 并行协调。

**Agent 工程最佳实践收敛：** 设计门→计划→微任务 TDD→双审（规格+质量）成为共识工作流。Agent 异步运行+消息通道审批替代实时盯着看。推理引擎层开始为 Agent 工作负载做 KV Cache 生命周期管理。

## GitHub 项目
| 项目 | Stars | 为什么值得学 | 适合阶段 | 收录日期 |
|------|-------|-------------|---------|---------|
| AICall | 200+ | 轻量级 LLM 服务架构，适合学 API 工程写法 | W1-W2 | 2026-05-20 |
| RAG_DeepDive_HandsOn | — | RAG 从入门到 Agentic 的完整实操 | W4 | 2026-05-20 |
| RAGFlow | 40K+ | 生产级 RAG 架构参考，企业级设计 | W4-W7 | 2026-05-20 |
| awesome-ai-agents-2026 | — | 2026 Agent 生态全景，选型必看 | W6 | 2026-05-20 |
| Dify | 143K+ | LLM 应用产品化最佳参考，2026 年增长迅猛 | W8 | 2026-05-20 |
| CrewAI | 51.6K+ | 最快上手多 Agent 协作 | W10 | 2026-05-20 |
| Agent Learning Hub | — | Datawhale 系统性 AI Agent 学习路线图 + 11 级项目阶梯 | W4-W10 | 2026-05-22 |
| LangGraph | 10K+ | 复杂状态ful Agent 工作流 | W6-W10 | 2026-05-20 |
| LlamaIndex | 49.5K+ | 文档 Agent + OCR 平台，长周期文档 Agent 方向 | W4-W7 | 2026-05-20 |
| OpenClaw | 302K+ | 多平台 AI Agent 网关，177+ 生产配置模板，架构设计参考 | W6-W10 | 2026-05-26 |
| Gemini CLI | 97K+ | Google 官方开源终端 Agent，原生 MCP 支持，1M Token 上下文 | W6 | 2026-05-26 |
| DeerFlow | 25K+ | 字节跳动开源，Planning+Tools+Memory+Execution 深度研究 Agent | W6-W10 | 2026-05-26 |
| n8n | 179K+ | 可视化工作流自动化，原生 AI Agent 节点，400+ 集成 | W8 | 2026-05-26 |
| Headroom | — | 上下文压缩层，AST 感知代码压缩，可逆压缩架构，MCP Server 集成 | W6-W8 | 2026-06-09 |
| CC Switch | — | 多 AI 工具配置统一管理，50+ provider 预设，用量统计 | W6 | 2026-06-09 |
| Hermes Agent | 150K+ | NousResearch 自学习个人 AI，持久记忆，本地运行 | W8-W10 | 2026-06-09 |
| MetaGPT | 59.6K+ | 多 Agent 模拟整个软件公司，需求→架构→代码全流程 | W10 | 2026-06-09 |
| OpenCode | 55K+ | 模型无关编程 Agent，支持任意 provider 切换 | W6 | 2026-06-09 |
| Cline | 49K+ | VS Code 原生 AI Agent，视觉共享，人在回路审批 | W6 | 2026-06-09 |
| Mastra | 10K+ | TypeScript 全栈 AI 框架，Zod 类型安全，端到端 | W8 | 2026-06-09 |
| Superpowers | 150K+ | Agent 行为层框架，强制 Brainstorm→Plan→Execute+TDD 工作流，防 Agent 直接瞎写代码 | W5-W10 | 2026-06-08 |
| MCP Workbench | — | MCP 协议可视调试器，查看 JSON-RPC 原始负载、握手、工具 schema | W6 | 2026-06-08 |
| MCP-Universe | — | MCP Agent 构建+评测框架，含 MCP+ 输出压缩（省 75% Token）和 MCPMark 基准 | W6-W8 | 2026-06-08 |

## 教程 & 文章
| 标题 | 链接 | 主题 | 适合阶段 | 收录日期 |
|------|------|------|---------|---------|
| LangChain 官方文档 | https://python.langchain.com/ | LLM 应用编排 | W5 | 2026-05-20 |
| LlamaIndex 官方文档 | https://docs.llamaindex.ai/ | RAG 框架 | W4 | 2026-05-20 |
| MCP 协议规范 | https://modelcontextprotocol.io/ | Agent 工具协议标准 | W6 | 2026-05-20 |
| Anthropic Agent 构建指南 | https://docs.anthropic.com/en/docs/agents-and-tools | 官方 Agent 设计模式，Skills/Tools/Subagent 体系 | W6 | 2026-05-22 |
| Streamlit 文档 | https://docs.streamlit.io/ | 快速 UI 搭建 | W3 | 2026-05-20 |
| DSPy 文档 | https://dspy.ai/ | 程序化 Prompt 优化 | W9 | 2026-05-20 |

## 官方文档源（一手信息）

> 这些是各家的官方文档入口。遇到具体问题优先查官方文档，而不是搜二手教程。
> 建议每周花 30 分钟快速扫一遍 Changelog/Blog，了解各家新出了什么能力。

| 厂商 | 文档入口 | 重点关注 | 适合阶段 |
|------|---------|---------|---------|
| Anthropic | https://docs.anthropic.com | Agent 设计模式、Claude Code、Skills、MCP、Prompt 最佳实践 | W4+ |
| OpenAI | https://platform.openai.com/docs | Function Calling、Assistants API、GPT 能力更新 | W2+ |
| Google | https://google.github.io/adk-docs/ | Agent Development Kit、Gemini API、多模态 | W6+ |
| DeepSeek | https://platform.deepseek.com/api-docs | Chat/Reasoner 模型差异、Prompt 工程、Token 计费 | W1-W2 |
| 阿里百炼 | https://help.aliyun.com/zh/model-studio | Qwen 接入、DashScope SDK、电商场景案例 | W2-W3 |
| LangChain | https://docs.langchain.com | Deep Agents、LCEL、Prompt Caching | W5+ |
| LlamaIndex | https://docs.llamaindex.ai | Agentic RAG、Workflow、Data Connectors | W4+ |

## 圈内信息源（持续追踪）

> 每周至少看 1 篇/1 期，保持对行业动向的感知。面试时"你关注什么信息源"是高频问题。

### 博客 / 专栏
| 来源 | 链接 | 为什么值得看 | 更新频率 |
|------|------|-------------|---------|
| Anthropic Engineering Blog | https://www.anthropic.com/engineering | 一线 Agent 工程实践，Claude Code/Harness 设计思路 | 月更 |
| OpenAI Blog | https://openai.com/blog/ | 模型能力更新、API 新功能、产品方向 | 月更 |
| Lilian Weng's Blog | https://lilianweng.github.io/ | 原 OpenAI 安全负责人，Agent/RAG 综述经典 | 不定期 |
| LangChain Blog | https://blog.langchain.dev/ | Agent 架构演进、生产踩坑、最佳实践 | 周更 |

### 视频 / 访谈
| 频道 | 平台 | 为什么值得看 | 备注 |
|------|------|-------------|------|
| Datawhale 社区分享 | 视频号/B站 | 学习路线 + 项目实战 + 求职经验 | 与 Agent Learning Hub 配套 |
| 跟李沐学AI | B站/YouTube | 论文精读、技术原理、职业建议 | 打基础阶段看论文精读 |
| 阿里技术/达摩院 | B站/视频号 | 阿里 AI 技术方向、Qwen 生态 | 杭州求职加分项 |
| Anthropic 官方频道 | YouTube | Claude Code 教程、Agent 设计、开发者大会 | 英文，按需观看 |

### 播客（通勤/做饭时听）
| 节目 | 平台 | 特点 |
|------|------|------|
| Latent Space | Spotify/Apple | AI 工程师访谈，Agent/RAG/推理最前沿 |
| Practical AI | Spotify/Apple | 开发者视角，偏实用性 |
| 硅谷101 | 小宇宙 | 中文，AI 行业趋势 + 人物故事 |

## 信息获取效率工具

> 信息源多了之后，一个个手动翻很耗时。用下面这些工具把"主动搜索"变成"被动接收"。

### RSS 聚合（首选）

用 **Feedly**（免费版，https://feedly.com）或 **Inoreader**（免费版）集中订阅以下 RSS 源。每天打开一个页面扫完所有更新，5-10 分钟。

| RSS 源 | 链接 | 内容 |
|--------|------|------|
| Anthropic Engineering | https://www.anthropic.com/engineering/rss | Claude/Agent/MCP 工程实践 |
| OpenAI Blog | https://openai.com/blog/rss | 模型更新、API 新功能 |
| LangChain Blog | https://blog.langchain.dev/rss | Agent 架构演进、生产踩坑 |
| Lilian Weng's Blog | https://lilianweng.github.io/index.xml | Agent/RAG 综述 |
| Google AI Blog | https://blog.google/technology/ai/rss/ | Gemini、Google AI 进展 |
| DeepSeek Blog | 暂无 RSS，手动关注官网/公众号 | 模型发布、技术报告 |

### 优质 Newsletter（被动投喂）

| 名称 | 订阅方式 | 频率 | 特点 |
|------|---------|------|------|
| TLDR AI | https://tldr.tech/ai | 每日 | 5 分钟速览当天 AI 新闻，信息密度高 |
| The Batch (Andrew Ng) | https://www.deeplearning.ai/the-batch/ | 每周 | 行业趋势 + 技术解读 |
| Anthropic Newsletter | https://www.anthropic.com/ | 不定期 | 产品更新、Claude Code 新功能 |

### 微信/中文圈

| 公众号 | 为什么值得看 |
|--------|-------------|
| Datawhale | 学习路线、项目实战、社区分享 |
| 机器之心 | AI 新闻 + 论文解读 |
| 量子位 | AI 行业动态 + 人物报道 |
| 阿里技术 | 阿里 AI 实践、Qwen 生态、杭州方向 |
| 夕小瑶科技说 | Agent/RAG 前沿 + 论文精读 |

### GitHub Watch（只在有大更新时通知）

给以下仓库点 Watch → Custom → Releases only，有新版本自动邮件通知：

- `datawhalechina/Agent-Learning-Hub`
- `langchain-ai/langgraph`
- `crewAIInc/crewAI`
- `langgenius/dify`
- `infiniflow/ragflow`

> 不要 Watch "All Activity"，消息会爆炸。只订阅 Releases。

## 游戏开发（兴趣线，业余）

> 入职后启动，当前只收集资源不下场学。

### 引擎
| 资源 | 链接 | 说明 |
|------|------|------|
| Godot Engine | https://godotengine.org/ | 免费开源，GDScript 类似 Python |
| GDQuest | https://www.gdquest.com/ | 最佳 Godot 入门教程 |
| Brackeys Godot | YouTube 搜 "Brackeys Godot" | 2025 年新出，质量高 |

### AI + 游戏交叉
| 框架/工具 | 链接 | 用途 |
|----------|------|------|
| Godot LLM | GitHub 搜 "godot-llm" | Godot 内调用 LLM API |
| LLM Unity | GitHub 搜 "LLMUnity" | Unity 内调用 LLM，参考架构 |
| Yarn Spinner | https://yarnspinner.dev/ | 对话系统（用来看架构设计） |

### 游戏设计参考
| 资源 | 说明 |
|------|------|
| GMTK (Game Maker's Toolkit) | 游戏设计分析 YouTube 频道 |
| GDC Vault | 游戏开发者大会免费演讲 |
| 《体验引擎》 | 游戏手感设计原理 |
| 《游戏设计艺术》 | 经典入门书 |

### 独立游戏标杆（研究案例）
| 游戏 | 开发人数 | 学习点 |
|------|---------|--------|
| 《星露谷物语》| 1 人 | 一人全栈能做到什么程度 |
| 《Celeste》| 2 人 | 2D 手感标杆 |
| 《吸血鬼幸存者》| 1 人 | 玩法驱动，最小美术投入 |
- PageIndex（VectifyAI）— 无向量 RAG 范式，等更多生产案例
- rtk — Rust Agent 框架，Token 成本控制，观察生态发展
- InsForge — Agent 后端一体化平台，观察成熟度
- Agentic RAG（CRAG/自适应检索）— RAG + Agent 推理循环融合，2026 年主流方向，W7 后深入
- Aluminium OS（Google）— Android + Chrome OS 统一平台，影响 SaaS/工具类产品形态
- GPT-5.5 Action Layer — Computer Use 原语操作第三方 UI，Agent 自动化边界扩展

## 已过时/不推荐
- （空）— 保留此区防止重复评估已淘汰技术
