# AI 应用开发入职路线图

> 本文件是学习路线图的主文档，由每周定时任务自动更新。
> 如需查看最新版本，请在 Claude Code 中说"当前 AI 行业有什么新变化？"

**目标岗位：** AI 应用开发工程师
**目标地点：** 杭州（电商/AI 生态）
**起点：** 零经验转行，会写小工具，会用但不懂原理
**时间窗口：** 2026年5月20日 → 2026年9月初（金九银十），约 14-16 周
**学习强度：** 全职，每周 40-50 小时
**赚钱目标：** 学习过程中通过接单/卖模板产生收入

## 技术栈（2026年5月基线）

| 类别 | 主力工具 | 原因 |
|------|---------|------|
| LLM 对接 | DeepSeek V4, Qwen, Claude/OpenAI API | DeepSeek 开源榜首，Qwen 阿里系必备 |
| 编排框架 | LangChain + LlamaIndex 双修 | 两框架法则 |
| Agent 框架 | LangGraph（主力）, CrewAI（快速原型） | Agent 是 2026 最热方向 |
| 向量数据库 | ChromaDB（入门）→ Milvus（进阶） | RAG 必备 |
| Web 框架 | Streamlit → FastAPI | Demo 到产品 |
| 协议标准 | MCP | 2026 Agent-Tool 连接标准 |
| 可观测性 | LangSmith / LangFuse | 开发期就有 Trace 意识，面试区分 demo 与上线 |
| Agent 标杆 | Claude Code 架构拆解 | 学习工具组织、权限、状态、子任务的设计模式 |
| AI 编程 | Cursor + Claude Code 深度使用 | 大厂硬性要求 |

## 四个月路线图速览

| 月 | 主题 | 关键产出 |
|----|------|---------|
| 1 | Python + LLM 基础 | 2 个部署上线的项目 |
| 2 | AI 框架 + Agent 实战 | 跨境电商客服系统 + Agent Harness 拆解 + 第一笔收入 |
| 3 | Agent 工程化 + 差异化 | 评测/可观测性 + 垂直领域项目 + 开始投简历 |
| 4 | 面试 + 复盘 | 至少 1 个 offer |

详细计划见 Claude Code plan 文件或查看 `progress.md`。
### 基础线 F4 — Docker 部署

| 步骤 | 内容 | 产出 |
|------|------|------|
| F4-1 | 镜像与容器 — Dockerfile、build/run/logs/exec、层缓存、.dockerignore | ✅ 已完成 |
| F4-2 | 多容器编排 — docker-compose、网络、volume、环境变量 | ✅ 已完成 |
| F4-3 | 部署实战 — 云服务器、镜像仓库推送拉取、端口/安全组/HTTPS | 🔲 待安排 |

进阶内容分为两条线，见 `advanced-plan.md`：
- **通用进阶**（任何 AI 工程师都该掌握）—— Agent 原理、工程化、生产化
- **定制进阶**（针对你的目标）—— 阿里/电商生态、接单产品化、求职靶向、现有项目升级

## 信息摄入习惯

每周至少保持以下最低信息摄入，避免闷头写代码脱离行业动态：

| 类型 | 频率 | 做什么 |
|------|------|--------|
| 官方 Changelog | 每周 30min | 快速扫 Anthropic/OpenAI/DeepSeek/Qwen 的更新日志 |
| 圈内内容 | 每周 1 篇/期 | 博客、视频或播客任选，保持对趋势的感知 |
| 资源库维护 | 发现新东西时 | 更新 `resources.md`，淘汰过时内容 |

面试时"你关注什么信息源"是高频问题，养成习惯本身就是面试素材。具体源清单见 `resources.md`。

## 最新扫描（2026-06-09）

**技术栈确认：** 当前选型无需调整。Agent + RAG + MCP 方向正确，杭州招聘 JD 完全匹配。

**杭州招聘动态：**
- 海康/钉钉/字节/淘天/招商银行全线招聘 AI Agent 开发
- 核心技能：Python、LangChain/LangGraph、RAG、Agent 框架、Prompt Engineering
- 加分项：Java/Go、Docker/K8s、MCP 协议、模型微调
- 实习岗 12K-18K/月，社招更高
- ⚠️ 钉钉部分岗位要求《AI应用工程师》证书——关注是否需要考

**新增推荐仓库：** Headroom（上下文压缩）、MetaGPT、Cline、Mastra、Hermes Agent — 详情见 resources.md

**进度：** 🟢 W5 Day 3 完成（6/8）。三 Agent 范式对比 + LangGraph 三图拓扑验证完成。下一步 W5 Day 4（Checkpoint 深入）。产品化冲刺已完成（Docker/docker-compose/日志/测试 全部通过）。

**战略调整（2026-06-05）：** 目标公司类型收窄为「AI + 业务场景」型（跨境电商/出海/外贸），不投 AI 基础设施/平台型公司。核心竞争力 = 懂 AI + 能落地业务场景，不和纯程序员比工程底子。
