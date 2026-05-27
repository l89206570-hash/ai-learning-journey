---
tags:
  - progress
  - ai-learning
  - weekly-log
created: 2026-05-21
updated: 2026-05-26
---

# AI 应用开发学习进度

## 当前状态
- **当前周：** W3（W1-W3 已完成）
- **开始日期：** 2026-05-21
- **今日日期：** 2026-05-27
- **今日工作时长：** 4h
- **累计工作时长：** 28h
- **状态：** 🟢 W3 完成，明日进入 W4
- **特殊：** MiMo-V2.5-Pro Token Plan 激活（5/23 → 6/23），已接入 Codex Desktop
- **兴趣线：** 游戏开发（业余，入职前不主动投入时间）→ 计划见 `[[game-dev-track]]`

## 本周进度（W1 — Python 速成）
- ✅ Day 1 完成：API 调用、函数定义、try/except、for 循环、enumerate、空值过滤
- ✅ Day 2 完成：文件读写（with open, .readlines(), 编码, 文件写入, 统计计数, .startswith()）
- ✅ Day 3 完成：Streamlit 入门 — 侧边栏、多标签页、文件上传、翻译历史、多语言翻译
- ✅ Day 4 完成：独立练习 — 用 API 从零写 Streamlit 工具（邮件润色 + 润色历史）

## W2 进度（W2 — 多模型与 API 进阶）
- ✅ Day 1 完成：多模型对比器 — 字典配置管理、time.time() 计时、response.usage Token 追踪、getattr 安全取值、st.checkbox、st.rerun() + session_state 分离模式、sidebar 对比历史（reversed/[::-1] 倒序）、模型差异分析（Chat vs Reasoner 设计目标）
- ✅ Day 2 完成：MiMo-V2.5-Pro 接入 — Token Plan 激活（6/23 到期）、mimo2codex 代理部署、Codex Desktop 接入、config.toml 配置
- ✅ Day 3 完成：4 模型对决 — 多客户端架构（provider 路由）、直连 MiMo Token Plan 端点（免代理）、千问 DashScope 接入、三组任务实测对比（数学推理/代码/翻译）
- ✅ Day 4 完成：DS vs Qwen 深度对比分析 — 6 条系统化 prompt 覆盖 4 维度、量化差异数据（Token 3.3x / 延迟 6.7x / 正确率相同）、产出面试对比文档 model-comparison.md

## W3 进度（W3 — RAG 基础）
- ✅ Day 1 完成：RAG 认知 + 第一个问答系统 — Document/Node/Index/QueryEngine 四大核心、BGE 中文嵌入模型、ModelScope 国内下载、OpenAILike 通用接口、DeepSeek V4 beta 端点、RAG vs 直接 LLM 对比
- ✅ Day 2 完成：RAG 四大核心概念 — 分块策略（chunk_size/chunk_overlap 对比）、检索可视化（source_nodes + similarity score）、索引持久化（build once load many，19x 加速）、Prompt 模板（{context_str}/{query_str} 占位符 + 自定义模板）
- ✅ Day 3 完成：对话式 RAG — chat_engine 有状态 vs query_engine 无状态对比、chat_mode="context" 指代消解（"它"→退货）、chat.chat_history 内部状态检查、三种 chat_mode 行为差异（default 反问 vs condense_question 重写 vs context 全文记忆）
- ✅ Day 4 完成：对话式 RAG 进阶 — reset() 记忆管理 + response.source_nodes + chat_mode 实测 + stream_chat() 流式输出
- ✅ Day 5 完成：多文档索引 — Document metadata 打标签 + 跨文档检索 + MetadataFilter 过滤 + MetadataFilters 组合 AND
- ✅ Day 6 完成：面试题库 RAG 实操 — 从零写多文档索引 + 三种查询模式 + import 差异理解 + condition 大小写踩坑
- ✅ Day 7 完成：RAG 综合实战 — 电商客服 RAG 从零搭建：多文档索引 + 品类过滤 + chat_engine context 模式 + stream_chat 流式输出 + chat_history 记忆 + Streamlit chat 组件 + 动态过滤切换

## 遇到的困难
- f-string 嵌套双引号导致 SyntaxError（已解决：内层改用单引号）
- 变量使用在赋值之前（已理解：代码执行顺序）
- 展示区错误嵌套在按钮内（已理解：st.rerun() 后展示区必须在按钮外部）
- deepseek-chat 偶尔响应 36 秒（已理解：服务端排队，非模型本身问题）
- Day 7: st.rerun() 放 if 外导致无限循环（已理解：破坏性操作必须放条件分支内）
- Day 7: chat_history 返回对象不是字典，用 .role.value 和 .content 属性访问
- Day 7: source_nodes 层级 — response.source_nodes[i].node.metadata 不是 .metadata

## 明日计划
- W4 Day 1：向量数据库 ChromaDB 入门

## 已完成的产出
| 周 | 产出 | 链接 |
|----|------|------|
| W1 | translator.py（API 调用 + 批量翻译） | projects/w1-translator/translator.py |
| W1 | app.py（Streamlit Web 界面 — 单条/批量翻译、多语言、历史记录） | projects/w1-translator/app.py |
| W1 | polish_app.py（邮件润色工具 — 独立练习） | projects/w1-translator/polish_app.py |
| W2 | battle.py（多模型对比器 — 独立从零编写） | projects/w2-model-battle/battle.py |
| W2 | mimo-30day-plan.md（MiMo 30 天利用计划） | mimo-30day-plan.md |
| W2 | `[[model-comparison]]`（DS vs Qwen 深度对比分析 + 面试素材） | projects/w2-model-battle/model-comparison.md |
| W3 | chat_engine.py（对话式 RAG — 有状态 vs 无状态对比） | projects/w3-rag-basics/chat_engine.py |
| W3 | day4_chat_advanced.py（记忆管理 + response 结构 + mode 对比） | projects/w3-rag-basics/day4_chat_advanced.py |
| W3 | day5_multi_doc.py（多文档索引 + 元数据过滤） | projects/w3-rag-basics/day5_multi_doc.py |
| W3 | day6_build_index.py + day6_query.py（面试题库 RAG — 从零实操） | projects/w3-rag-basics/day6_query.py |
| W3 | day7_app.py（电商客服 RAG 综合实战 — 流式对话 + 品类过滤 + 记忆管理） | projects/w3-rag-basics/day7_app.py |

## 收入记录
| 日期 | 来源 | 金额 |
|------|------|------|

## 面试记录
| 日期 | 公司 | 岗位 | 结果 | 复盘要点 |
|------|------|------|------|----------|
