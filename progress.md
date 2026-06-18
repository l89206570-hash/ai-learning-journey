---
tags:
  - progress
  - ai-learning
created: 2026-05-21
updated: 2026-06-18
---

# AI 学习日志

> 2026-06-16 下午更新：从漫游模式明确为一主一辅方向。主轴知识库/工作流变现，辅轴AI视频传播引流。

## 当前状态
- **今日日期：** 2026-06-18
- **模式：** 一主一辅，周末 2-6h，不赶进度但保持惯性
- **主轴：** 知识库/工作流搭建（Coze 起步 → Dify 进阶）→ 接单变现
- **辅轴：** AI 短片/视频制作（记录搭建过程 → 发小红书/B站 → 引流）
- **已完成基础：** W1-W6（Python / API / RAG / Agent / LangGraph / MCP 基础）
- **路线文件：** `E:\.claude\plans\ai-ai-noble-raccoon.md`
- **已搁置：** resource-pipeline 项目、游戏开发兴趣线

## 已完成的学习（W1-W6 速成期）

### W1 — Python 速成
API 调用、函数定义、try/except、文件读写、argparse、Streamlit 入门、邮件润色工具

### W2 — 多模型与 API 进阶
多模型对比器、MiMo Token Plan 接入、4 模型对决、DS vs Qwen 深度对比

### W3 — RAG 基础
对话式 RAG、多文档索引+元数据过滤、面试题库 RAG、电商客服 RAG 综合实战

### W4 — RAG 进阶 + Agent 入门
ChromaDB + LlamaIndex 集成、Prompt Engineering 五段法、Agent Loop 手写、Agent Chat Streamlit 界面、Agent + ChromaDB 自主搜索

### 产品化冲刺
电商客服 RAG 完整产品级项目（config/logging/Docker/测试），`projects/ecommerce-rag/`

### W5 — Agent 工程化
Agent 三范式对比（ReAct/Plan-Execute/Reflexion）、LangGraph 重构、Checkpoint 深入、Skills vs Tools、MCP 协议入门、MCP + LangGraph 集成

### W6 — 综合项目
Claude Code 架构拆解、Agent 测试框架 + 评测体系、跨境电商 Agent 综合项目

## 新方向项目（一主一辅，启动于 2026-06-18）

### 主轴：知识库/工作流变现

**2026-06-18：第一个 Dify 知识库 Bot 完成**
- 平台选型：Coze → Dify Cloud（Coze 知识库上传需付费 39.9/月）
- 素材准备：从 knowledge.md 提取 3 份结构化文件（RAG+ChromaDB / Agent核心 / 工程化实践）
- Dify 配置：DeepSeek 模型接入（OpenAI-API-compatible 适配），知识库绑定 + Prompt
- 测试结果：3/3 正确（RAG流式输出 / ReAct vs Plan-Execute / MCP协议），跨度内检索 + 跨文件概念融合
- 补坑：RAG 文件补充流式输出代码示例（yield 生成器 + stream_chat）

**市场调研（同日）：**
- 知识库变现全流程：搭 Bot → 做案例 → 发内容 → 接咨询 → 谈需求 → 交付 → 维护
- 市场价格：基础 Bot 500-2000 / 知识库+工作流 2000-5000 / 企业定制 5000-20000 + 月费
- 客户画像：电商卖家（客服压力）、小团队（SOP问答）、知识付费博主（粉丝答疑）
- 核心壁垒：懂业务场景 > 会用工具；能沟通需求 > 能写代码

### 辅轴：AI 短剧/视频创作

**2026-06-18：即梦文生图第一轮探索**
- 工具：即梦图片 4.5 模型（写实风格）
- 固定角色 prompt → 基准图 → 视角微调
- 发现的一致性坑：
  - 侧面视角眉毛变长（模型不真正理解 3D 空间）
  - 逐轮增加参数导致下巴渐尖（独立采样漂移）
- 学到的解决方案：锁 seed 值 / 垫图（图生图）+ 参考强度 70-80
- 下一步：垫图锁脸 → 可灵图生视频

### 待启动
- 服装工厂数据收集 → 第二个知识库案例
- AI 短剧：垫图一致性验证 → 可灵图生视频

## 学习笔记
- 踩坑记录和心得见各项目目录下的代码和 README
