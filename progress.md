---
tags:
  - progress
  - ai-learning
  - weekly-log
created: 2026-05-21
updated: 2026-06-09
---

# AI 应用开发学习进度

## 当前状态
- **当前周：** 🟢 W6（Day 4-6 完成）
- **开始日期：** 2026-05-21
- **今日日期：** 2026-06-15
- **状态：** W6 Day 4-6 完成 → 下次继续 W6 Day 7（可观测性基础）
- **学习方案：** W5-W7 修订方案见 `E:\.claude\plans\mutable-doodling-wolf.md`
- **战略调整：** 目标收窄为「AI + 业务场景」型公司（跨境电商/出海/外贸），核心卖点 = 懂 AI + 能落地业务，不和纯程序员比工程底子。详情见 memory/career-strategy-shift.md。
- **特殊：** MiMo-V2.5-Pro Token Plan 激活（5/23 → 6/23），已接入 Codex Desktop
- **兴趣线：** 游戏开发（业余，入职前不主动投入时间）→ 计划见 `[[game-dev-track]]`
- **基础线：** F1-F3 全部完成（函数基础 / 数据结构操作 / JSON & 序列化）

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

## W4 进度（W4 — RAG 进阶：向量数据库）
- ✅ Day 1 完成：ChromaDB 入门 — 核心概念（Client/Collection/Embedding Function）、语义搜索 + 元数据过滤、CRUD、持久化、ChromaDB + LlamaIndex 集成（ChromaVectorStore/StorageContext）
- ✅ Day 2 完成：ChromaDB 应用实战 — 将 W3 Day 7 电商客服从 SimpleVectorStore 迁移到 ChromaDB，拆分 build_index.py + app.py，验证语义检索、品类过滤、流式对话、上下文记忆
- ✅ Day 3 完成：Prompt Engineering 进阶 — 结构化五段法 + 裸奔 vs 一句话 vs 五段法实测对比
- ✅ Day 4 完成：固定测试集 — 3 条场景测试 + check_contains 关键词检查
- ✅ Day 5 完成：Agent Loop 手写 — 纯 API tools 参数实现 Agent 循环 + 练习添加新工具（get_word_length）
- ✅ Day 6 完成：Agent Chat 交互界面 — 命令行升级 Streamlit + yield 生成器 + st.chat_message/chat_input/status + 多轮对话记忆
- ✅ Day 7 完成：综合练习 — Agent + ChromaDB 自主搜索助手，Agent 自己判断是否检索知识库、调工具、组织回答

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
- Day 5: 函数基础不牢 — 不熟悉参数声明、返回值 vs print、类型标注的写法（已理解：函数体内用到的变量必须在括号里声明；return 传值，print 输出）
- Day 5: JSON 概念模糊 — 不理解 loads/dumps 的用途（已理解：JSON 是跨语言传数据的中间格式，本质是"像字典的字符串"）
- Day 5: `**dict` 字典展开不理解 — 不知道参数怎么动态传入函数（已理解：`func(**{k: v})` = `func(k=v)`）
- Day 6: `properties` 拼成 `parmaters` / `parmters` → API 不识别工具定义（已理解：JSON Schema 字段名必须精确）
- Day 6: `{}` vs `[]` 混淆 — properties 用 `{}`（对象/键值对），required 用 `[]`（数组/列表）
- Day 6: TOOL_MAP 字典里用 `=` 代替 `:` → SyntaxError（已理解：字典用 `:` 分隔键值对）
- Day 6: 删掉 `pass` 后 for 循环体为空 → IndentationError（已理解：`pass` 是占位符，替换不是删除）

## W5 进度（W5 — Agent 工程化）
- ✅ Day 1 完成：Agent 三范式对比 — ReAct / Plan-then-Execute（方式 B+C）/ Reflexion 纯 API 实现，同一任务对比三种范式差异
- ✅ Day 2 完成：LangGraph 重构 ReAct — StateGraph + ToolNode + tools_condition + checkpoint，对比手写 vs 框架的代码量差异
- ✅ Day 3 完成：LangGraph 实现 Plan-Execute + Reflexion — 三张图拓扑对比，自定义 router 替代 tools_condition，验证"图拓扑不同=范式不同"
- ✅ Day 4 完成：Checkpoint 深入 — SqliteSaver 持久化、interrupt() 暂停审批、get_state/update_state 时间旅行，理解 LangGraph 和手写的代差
- ✅ Day 5 完成：Skills vs Tools + Mermaid — 将 Day 2 零散工具封装为 Skill（prompt + tools + 测试），多 Skill 调度路由，Mermaid 架构图（ReAct 图/三范式对比/技术栈全景/Agent Loop 时序）
- ✅ Day 6 完成：MCP 协议入门 — FastMCP Server（3 个工具）+ Client（stdio transport + list_tools 动态发现 + call_tool），对比三种集成方式（import/Skill/MCP）
- ✅ Day 7 完成：MCP + LangGraph 集成 — 适配层（list_tools → create_model → coroutine 包装），async StructuredTool + graph.astream()，Agent 通过 MCP 协议调用远程工具，图拓扑不变

## W6 进度（W6 — Agent 工程化 + 综合项目）
- ✅ Day 1 完成：Claude Code 架构拆解 — 四大模块（工具注册/权限中间件/双层状态管理/子任务系统），Mermaid 架构图，与 W5 实践对接表，面试讲述词
- ✅ Day 2-3 完成：Agent 测试框架 + 评测体系 — pytest 三层测试（结构/工具/行为/稳定性/持久化）+ 评测脚本（正确性×效率×稳定性）
- 🔲 Day 4-6 完成：跨境电商 Agent 综合项目 — LangGraph + MCP Server + ChromaDB，Agent 自主决定工具调用（搜索/查订单/查会员），pytest 7/7 通过，评测 5/5 工具选择

## 遇到的困难（W5）
- Day 1: `plan_text.count("步骤")` 多数了步数 → 计划文本说明文字也含"步骤"，导致多跑空轮次
- Day 1: Reflexion 反思提示缩进错（放在 for 循环里面而不是两个 for 之间）→ 每轮 tool_call 后都触发反思
- Day 1: 伪代码 `[...]` 和 `...` 当真实代码 → Python 不认，要用实际变量
- Day 1: `response.choices[0].message` 拿了整个对象而不是 `.content` → 格式不对
- Day 4: `langgraph.checkpoint.sqlite` 模块不存在 → LangGraph 1.x 把 checkpoint 拆成独立包，需 `pip install langgraph-checkpoint-sqlite`
- Day 4: `interrupt()` 不抛异常，`invoke()` 正常返回带 `__interrupt__` → 不能 try/except，要检查 `"__interrupt__" in result`
- Day 4: 拒绝 tool_calls 后 `add_messages` append 导致 tool_calls 消息孤立 → DeepSeek 要求 tool_calls 后必须有匹配 tool message，需 `RemoveMessage` 删除原消息

## 产品化冲刺 ✅ 完成（2026-06-05，1 天）

| 步骤 | 内容 | 结果 |
|------|------|------|
| D1 配置管理 | 零硬编码，全部走 config.py + 环境变量 | ✅ |
| D2 日志 | logging 模块替代 print，含时间戳 + 级别 | ✅ |
| D3 错误处理 | 5 个关键点 try/except，中文提示不红屏 | ✅ |
| D3 启动检测 | Embedding/LLM/ChromaDB 启动时校验，有问题提前暴露 | ✅ |
| D4 Dockerfile | CPU-only torch（省 1.5GB） | ✅ |
| D4 docker-compose | 一键启动 build_index + app | ✅ |
| D4 README | 项目说明、部署步骤、测试结果 | ✅ |
| D5 测试 | 5 条固定测试，5/5 通过 | ✅ |
| Docker 验证 | 构建 → 建索引 → 启动 → HTTP 200 | ✅ |

**项目位置：** `projects/ecommerce-rag/`

### 产品化中学到的
- Docker Hub 国内需配镜像加速器
- PyTorch 默认拉 CUDA 500MB+，CPU 版只需 ~100MB
- ChromaDB 已存在集合需先删再建
- Docker Compose `${VAR}` 从 `.env` 文件或 shell 环境读取
- docker-compose.yml 的 `version` 字段已废弃

### AI 协作规则（本次总结）
- 改动超 3 文件先写方案，一次改一个文件
- 改完就跑验证，通过就 commit
- 需求单里没写的不要加
- 信任层级：生成式 > 编辑式 > 删除式
- 一个对话只干一件事

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
| W4 | day5_agent_loop.py（Agent Loop 手写 — 纯 API tools 参数 + 3 工具 + 手动添加 get_word_length 练习） | projects/w4-chromadb/day5_agent_loop.py |
| W4 | warmup_4.py（W4D6 暖身 — 函数/JSON/**dict 综合练习） | projects/exercises/warmup_4.py |
| W4 | day6_agent_chat.py（Agent Chat Streamlit 界面 — yield 生成器 + st.chat_message/chat_input/status + 多轮记忆） | projects/w4-chromadb/day6_agent_chat.py |
| W4 | day7_agent_search.py（综合练习 — Agent + ChromaDB 自主搜索，3 工具 + 语义检索 + Streamlit 界面） | projects/w4-chromadb/day7_agent_search.py |
| F1 | fund_functions.py（函数基础 — def/参数/return/嵌套函数） | projects/exercise/fund_functions.py |
| F2 | fund_data_structures.py（数据结构操作 — dict/list/嵌套取值/排序） | projects/exercise/fund_data_structures.py |
| F3 | fund_json.py（JSON & 序列化 — dumps/loads/dump/load/API 模拟） | projects/exercise/fund_json.py |
| F4-1 | Docker 镜像与容器 — Dockerfile、build/run/logs/exec、层缓存、.dockerignore（产品化冲刺完成） | projects/ecommerce-rag/ |
| F4-2 | Docker 多容器编排 — docker-compose、网络、volume、环境变量、depends_on（产品化冲刺完成） | projects/ecommerce-rag/ |
| W6 | ecommerce-agent（跨境电商 Agent — LangGraph + MCP Server + ChromaDB + pytest） | projects/ecommerce-agent/ |
| W5 | day1_three_paradigms.py（Agent 三范式对比 — ReAct + Plan-Execute B/C + Reflexion） | projects/w5-agent-paradigms/day1_three_paradigms.py |
| W5 | paradigm-comparison.md（三范式实测对比分析） | projects/w5-agent-paradigms/paradigm-comparison.md |
| W5 | day2_langgraph_react.py（LangGraph 重构 ReAct — StateGraph + ToolNode + checkpoint） | projects/w5-agent-paradigms/day2_langgraph_react.py |
| W5 | day3_langgraph_paradigms.py（LangGraph Plan-Execute + Reflexion — 三图拓扑对比） | projects/w5-agent-paradigms/day3_langgraph_paradigms.py |
| W5 | day4_checkpoint_demo.py（Checkpoint 深入 — SqliteSaver + interrupt + 时间旅行） | projects/w5-agent-paradigms/day4_checkpoint_demo.py |
| PRD | 电商客服 RAG 产品化 — 完整产品级项目（config/logging/Docker/测试） | projects/ecommerce-rag/app.py |

## 收入记录
| 日期 | 来源 | 金额 |
|------|------|------|

## 面试记录
| 日期 | 公司 | 岗位 | 结果 | 复盘要点 |
|------|------|------|------|----------|
