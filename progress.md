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
- **当前周：** W4（Day 4 完成）
- **开始日期：** 2026-05-21
- **今日日期：** 2026-05-29
- **今日工作时长：** 4h
- **累计工作时长：** 38h
- **状态：** 🟢 W4 Day 4 完成
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

- ✅ Day 4 完成：Prompt 标准化实战 — battle.py 接入五段法模板系统 + 3 条固定测试
- ✅ Day 3 完成：Prompt Engineering 进阶 — 结构化五段法（System/Context/Instruction/Examples/Constraints）+ 裸奔 vs 一句话 vs 五段法实测对比

## W4 进度（W4 — RAG 进阶：向量数据库）
- ✅ Day 1 完成：ChromaDB 入门 — 核心概念（Client/Collection/Embedding Function）、语义搜索 + 元数据过滤、CRUD、持久化、ChromaDB + LlamaIndex 集成（ChromaVectorStore/StorageContext）
- ✅ Day 2 完成：ChromaDB 应用实战 — 将 W3 Day 7 电商客服从 SimpleVectorStore 迁移到 ChromaDB，拆分 build_index.py + app.py，验证语义检索、品类过滤、流式对话、上下文记忆

## 遇到的困难
- ChromaDB 默认英文嵌入模型 all-MiniLM-L6-v2 从 AWS S3 下载极慢（80MB，国内网络） → 改用 ModelScope 缓存的 BGE 中文模型本地路径
- HF 镜像 hf-mirror.com 在国内也连不上 → 直接用 ModelScope 本地缓存路径
- LlamaIndex 0.14+ 移除内置 openai_like，新版 OpenAI 类校验模型名白名单 → 需单独 pip install llama-index-llms-openai-like
- load_index_from_storage() 只传 vector_store 不够 → 需先 persist 索引元数据，加载时同时传 persist_dir
- Windows 终端 GBK 编码无法打印 emoji → 避免在 print 中用 emoji

## 遇到的困难
- f-string 嵌套双引号导致 SyntaxError（已解决：内层改用单引号）
- 变量使用在赋值之前（已理解：代码执行顺序）
- 展示区错误嵌套在按钮内（已理解：st.rerun() 后展示区必须在按钮外部）
- deepseek-chat 偶尔响应 36 秒（已理解：服务端排队，非模型本身问题）
- Day 7: st.rerun() 放 if 外导致无限循环（已理解：破坏性操作必须放条件分支内）
- Day 7: chat_history 返回对象不是字典，用 .role.value 和 .content 属性访问
- Day 7: source_nodes 层级 — response.source_nodes[i].node.metadata 不是 .metadata
- Day 2: `VectorStoreIndex()` 没赋值给变量直接调 persist → NameError（已理解：必须先赋值 `index = ...`）
- Day 2: `client` 拼成 `cilent` → NameError（已理解：变量名写错不会报语法错，运行时才炸）
- Day 2: `as_chat_mode` vs `as_chat_engine`（已理解：方法名写错同理运行时才报错）
- Day 2: `MetadataFilter` 写成 `MetadataFilters`（已理解：单数是过滤条，复数是装多条规则的容器）
- Day 2: metadata category 不一致（build_index 写"产品介绍"但 app 过滤"产品"）→ 品类筛选无结果（已理解：两端值必须完全一致）
- Day 2: 品类切换重建 chat_engine → 上下文丢失（已理解：切换品类 = 新会话，是当前设计的 trade-off）
- Day 2: W4 venv 缺 streamlit → ModuleNotFoundError（已解决：`pip install streamlit`）

## 明日计划
- W4 Day 5：Agent Loop 手写 — 不用任何框架，用纯 `OpenAI().chat.completions.create()` 写 Agent 循环（≤100 行）

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
| W4 | day1_chromadb_basics.py（ChromaDB 核心概念 — Collection/语义搜索/元数据过滤/CRUD/持久化） | projects/w4-chromadb/day1_chromadb_basics.py |
| W4 | day1_chromadb_llamaindex.py（ChromaDB + LlamaIndex 集成 — ChromaVectorStore/StorageContext/build once load many） | projects/w4-chromadb/day1_chromadb_llamaindex.py |
| W4 | build_index.py（ChromaDB 电商知识库建索引 — PersistentClient + create_collection + persist） | projects/w4-chromadb/build_index.py |
| W4 | app.py（电商客服 Streamlit 界面 — ChromaDB 后端 + 品类过滤 + 流式对话 + 检索来源） | projects/w4-chromadb/app.py |
| W4 | day3_prompt_engineering.py（Prompt Engineering 五段法 — 裸奔 vs 一句话 vs 结构化实测对比） | projects/w4-chromadb/day3_prompt_engineering.py |
| W4 | battle.py（升级版 — 接入五段法模板系统 + selectbox 切换 + text_area 可编辑） | projects/w2-model-battle/battle.py |
| W4 | day4_test_cases.py（固定测试集 — 3 条场景测试 + check_contains 关键词检查） | projects/w4-chromadb/day4_test_cases.py |

## 收入记录
| 日期 | 来源 | 金额 |
|------|------|------|

## 面试记录
| 日期 | 公司 | 岗位 | 结果 | 复盘要点 |
|------|------|------|------|----------|
