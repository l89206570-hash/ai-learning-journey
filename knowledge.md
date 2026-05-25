---
tags:
  - knowledge
  - ai-learning
  - python
  - llm
  - rag
  - streamlit
created: 2026-05-21
updated: 2026-05-25
---

# 知识点存档

> 每天学到的概念、语法、踩坑记录。配合 [[progress]] 使用。

---

## [[Python 基础]]

### 函数

| 概念 | 要点 | 来源 |
|------|------|------|
| `def` 定义函数 | `def` 是注册名字，不是执行；定义在前，调用在后 | W1D1 |
| 参数类型标注 | `def func(name: str) -> str:` 标注入参和返回值类型 | W1D1 |
| 返回值 | `return` 把数据传回给调用者 | W1D1 |

### 异常处理

| 概念 | 要点 | 来源 |
|------|------|------|
| `try/except` | `try` 包裹可能出错的代码，`except` 捕获异常并处理 | W1D1 |
| 兜底策略 | API 调用失败时返回错误信息，不让程序崩溃 | W1D1 |

### 文件读写

| 概念 | 要点 | 来源 |
|------|------|------|
| `with open()` | 上下文管理器，自动关闭文件，不用手动 `f.close()` | W1D2 |
| 文件模式 | `"r"` 读、`"w"` 写（覆盖）、`"a"` 追加 | W1D2 |
| `encoding="utf-8"` | 处理中文文件必须指定，否则乱码 | W1D2 |
| `.readlines()` | 返回列表，每个元素是一行（含末尾 `\n`） | W1D2 |
| `.write()` | 写入字符串到文件，不会自动加换行 | W1D2 |

### 字符串

| 概念 | 要点 | 来源 |
|------|------|------|
| `.strip()` | 去掉首尾空白字符（空格、换行、制表符） | W1D1 |
| `.rstrip()` | 只去掉右侧空白；`.rstrip("\n")` 精确去掉换行符 | W1D2 |
| `.startswith()` | 检查字符串是否以指定内容开头，比 `in` 更精确 | W1D2 |
| `f-string` | `f"{变量} 文字"` 格式化字符串 | W1D1 |

### 循环与条件

| 概念 | 要点 | 来源 |
|------|------|------|
| `for ... in` | 遍历列表每个元素 | W1D1 |
| `enumerate(seq, start)` | 同时拿到索引和值，`start` 设置起始序号 | W1D1 |
| `reversed(seq)` | 倒序遍历列表，返回迭代器，不额外占内存 | W2D1 |
| `list[::-1]` | 列表切片倒序，返回新拷贝的列表，会多占一份内存 | W2D1 |
| `continue` | 跳过本轮循环，进入下一轮 | W1D2 |
| `if/elif/else` | 多条件分支判断 | W1D1 |

### 数据结构

| 概念 | 要点 | 来源 |
|------|------|------|
| 列表 `[]` | 有序集合，`list[i]` 按下标访问 | W1D1 |
| 字典 `{}` | 键值对集合，`dict["key"]` 访问 | W1D2 |

### 模块与入口

| 概念 | 要点 | 来源 |
|------|------|------|
| `import` | 导入外部模块或库 | W1D1 |
| `sys.argv` | 命令行参数列表，`sys.argv[1]` 是第一个参数 | W1D2 |
| `if __name__ == "__main__"` | 判断是否直接运行此文件（vs 被 import） | W1D2 |

---

## [[API 调用]]

| 概念 | 要点 | 来源 |
|------|------|------|
| OpenAI 客户端 | `OpenAI(api_key=..., base_url=...)` 可对接兼容接口 | W1D1 |
| `chat.completions.create()` | 发送对话请求，model + messages 是必填项 | W1D1 |
| system prompt | 设定 AI 的角色和行为 | W1D1 |
| `.env` 管理密钥 | `load_dotenv()` + `os.getenv()` 读取 API Key，不写死在代码里 | W1D1 |

### 多端点多客户端

| 概念 | 要点 | 来源 |
|------|------|------|
| 多客户端架构 | 不同模型走不同 API 端点，一个端点一个 `OpenAI()` 客户端实例 | W2D3 |
| provider 路由模式 | MODELS 字典每项加 `"provider"` 字段，`_clients[config["provider"]]` 查对应 client | W2D3 |
| 客户端缓存 | 用一个 `_clients = {}` 字典存所有 client，按 provider 名索引复用 | W2D3 |
| DashScope 兼容端点 | 千问走 `https://dashscope.aliyuncs.com/compatible-mode/v1`，模型名 `qwen-plus` | W2D3 |
| MiMo Token Plan 端点 | `tp-` 开头 Key 走 `https://token-plan-cn.xiaomimimo.com/v1`，无需本地代理 | W2D3 |

---

## [[模型选型与性能]]

> 基于 W2D3 4 模型实测数据（数学推理 / 代码 / 翻译三组对比）

| 模型 | 速度 | Token 效率 | 适用场景 |
|------|------|-----------|---------|
| DeepSeek Chat (V3) | ⭐⭐⭐ 最快 | ⭐⭐⭐ 最省 | 日常对话、翻译、代码、性价比首选 |
| DeepSeek Reasoner | ⭐⭐⭐ 快 | ⭐⭐ 中 | 数学推理、复杂逻辑，比 Chat 更简洁 |
| Qwen (千问) | ⭐ 慢 | ⭐ 费 | 输出丰富详细，适合需要多版本答案的场景 |
| MiMo-V2.5-Pro | ⭐⭐ 中 | ⭐⭐ 中 | Token Plan 免费期首选，输出结构清晰（表格/分节） |

**核心原则：** 简单任务不要用大炮打蚊子 — 翻译/代码用 Chat 模型又快又省，推理/数学才上 Reasoner。

### DS vs Qwen 行为差异（W2D4 深度对比）

> 基于 6 条系统化 prompt（翻译/推理/代码/指令遵循），详见 `projects/w2-model-battle/model-comparison.md`

| 维度 | DS Chat | Qwen | 面试金句 |
|------|---------|------|---------|
| 输出控制 | 问多少答多少 | 永远多给 3-5 倍内容 | "DS Chat 够用就好，Qwen 知无不言" |
| 中文表达 | 偏书面体 | 更自然口语化 | "Qwen 中文更像真人说话" |
| 推理风格 | 清单式，简洁 | 学术论文式，列公式 | "Qwen 把开放题当论文写" |
| Token 效率 | 6 题 1384 tok | 6 题 4628 tok（3.3x） | "正确率相同，成本差 3 倍" |
| 延迟 | 6 题 12.6s | 6 题 84.5s（6.7x） | "DS Chat 快一个数量级" |
| 正确率 | 6/6 | 6/6 | "结果都对，但过程完全不同" |

**选型结论：** 中文对话/创作首选 Qwen（母语级），逻辑推理和成本敏感场景选 DS Flash，代码场景两者无差异。

### DeepSeek 模型名陷阱（W2D4 发现）

| 发现 | 要点 | 来源 |
|------|------|------|
| `[[DeepSeek]]` 模型名陷阱 | `deepseek-chat` 已自动映射到 V4，2026.04.24 起生效 | W2D4 |
| V4 两个版本 | V4-Flash（轻量快）vs V4-Pro（旗舰强推理），Flash 性价比高，Pro 不总是更好 | W2D4 |
| 定期看 Changelog | 不看更新日志连自己调的什么模型都不知道——面试高频问题"你怎么跟踪模型变化" | W2D4 |

### V4-Flash vs V4-Pro vs Qwen 补充对比（W2D4 第二轮）

| 发现 | 要点 |
|------|------|
| Pro 在翻译上退步 | V4-Pro 用"backup nodes"而非"standby nodes"，耗时 5x 但术语反而不如 Flash |
| Pro 中文创作有进步 | "西湖像在轻轻地呼气"比 Flash 的"温吞吞的橘色"更有文学感 |
| Qwen 中文护城河 | 即使 V4-Pro 也追不上 Qwen 的母语级语感，"所以啊"、语气词、新意象碾压 |

---

## [[Streamlit]]

### 基础组件

| 概念 | 要点 | 来源 |
|------|------|------|
| `st.title()` | 页面标题，渲染为 `<h1>` | W1D3 |
| `st.text_area()` | 多行文本输入框，`height` 控制高度，`key` 标识状态 | W1D3 |
| `st.button()` | 按钮，点击返回 `True`，`type="primary"` 高亮 | W1D3 |
| `st.write()` | 万能输出，字符串、变量、Markdown 都能渲染 | W1D3 |
| `st.subheader()` | 小标题 | W1D3 |
| `st.divider()` | 分割线 `---` | W1D3 |
| `st.metric()` | 指标卡片，带 +/- 变化箭头 | W1D3 |

### 提示框

| 概念 | 要点 | 来源 |
|------|------|------|
| `st.warning()` | 黄色警告 | W1D3 |
| `st.error()` | 红色错误 | W1D3 |
| `st.success()` | 绿色成功 | W1D3 |
| `st.info()` | 蓝色提示 | W1D3 |
| `st.toast()` | 右下角轻提示，不遮挡主内容 | W1D3 |

### 布局

| 概念 | 要点 | 来源 |
|------|------|------|
| `st.columns(n)` | 等宽分列，返回 n 个对象，`with col:` 往里写内容 | W1D3 |
| `st.tabs(["A", "B"])` | 标签页，返回值解包到多个变量，`with tab:` 使用 | W1D3 |
| `st.sidebar.xxx()` | 所有 `st.xxx` 组件都可以前置 `sidebar.` 放到侧边栏 | W1D3 |
| `st.expander("标题")` | 折叠面板，`with expander:` 包裹可展开/收回的内容 | W1D3 |

### 输入组件

| 概念 | 要点 | 来源 |
|------|------|------|
| `st.selectbox()` | 下拉单选 | W1D3 |
| `st.radio()` | 单选按钮 | W1D3 |
| `st.multiselect()` | 多选下拉，返回列表，`default` 设置默认值 | W1D3 |
| `st.file_uploader()` | 文件上传，`type` 限制后缀，`.getvalue()` 拿字节 | W1D3 |

### 数据展示

| 概念 | 要点 | 来源 |
|------|------|------|
| `st.dataframe()` | 可交互表格（排序、列宽拖动、搜索） | W1D3 |
| `st.table()` | 静态表格，不能交互 | W1D3 |
| `pd.DataFrame(dict)` | pandas 字典转表格，`{"列名": [值列表]}` | W1D3 |

### 状态与反馈

| 概念 | 要点 | 来源 |
|------|------|------|
| `with st.spinner("文字")` | 加载动画，代码块执行完自动消失 | W1D3 |
| `st.progress(0~1)` | 进度条，`.progress(百分比, text="")` 更新 | W1D3 |
| `st.session_state` | 跨页面重刷保留数据的"保险箱"，`if "key" not in` 初始化 | W1D3 |
| `st.download_button()` | 下载按钮，`data` 给内容，`file_name` 给文件名 | W1D3 |

### Streamlit 核心机制

| 概念 | 要点 | 来源 |
|------|------|------|
| 脚本重跑 | 每次用户交互，整个脚本从头到尾重新执行一次 | W1D3 |
| 组件 key | 相同组件需要唯一 `key` 参数区分，否则报 `DuplicateElementId` | W1D3 |
| 变量不持久 | 普通变量每次重跑重置，要持久化用 `st.session_state` | W1D3 |
| `st.rerun()` | 手动触发页面重跑，配合 session_state 使用：按钮里存数据 → rerun → 展示区读数据渲染 | W2D1 |
| session_state 分离 | 展示用完整数据（last_battle），历史存截断版（battle_history），各司其职省内存 | W2D1 |

### 新增组件

| 概念 | 要点 | 来源 |
|------|------|------|
| `st.checkbox()` | 勾选框，返回 `True/False`，`value=True` 设置默认勾选，`help=` 鼠标悬停提示 | W2D1 |

---
## [[Python 进阶]]

### 时间与性能

| 概念 | 要点 | 来源 |
|------|------|------|
| `time.time()` | 返回当前 Unix 时间戳（秒浮点数），调用前后各取一次相减 = 耗时 | W2D1 |
| API 性能关注 | response.usage 可拿到 `prompt_tokens`、`completion_tokens`、`total_tokens` | W2D1 |

### 字典技巧

| 概念 | 要点 | 来源 |
|------|------|------|
| `.get(key, default)` | 安全从字典取值，key 不存在返回 default 而不是报 KeyError | W2D1 |
| `getattr(obj, attr, default)` | 安全从对象取属性，属性不存在返回 default 而不是报 AttributeError | W2D1 |
| 字典做配置 | `MODELS = {"key": {...}}` 管理模式，新增模型只加配置不改逻辑代码 | W2D1 |
| 字典推导式 | `{k: 处理(v) for k, v in dict.items()}` 一行完成过滤/转换 | W2D1 |

---

---
## [[RAG]]（检索增强生成）

### 核心概念

| 概念 | 要点 | 来源 |
|------|------|------|
| `[[RAG]]` | Retrieval Augmented Generation，先检索再回答，给 LLM 限定信息来源避免幻觉 | W3D1 |
| 为什么需要 RAG | LLM 训练数据有截止日期，不知道你的业务知识，容易编造答案（幻觉） | W3D1 |
| RAG vs 直接 LLM | RAG = 开卷考试（有知识库），直接 LLM = 闭卷考试（靠训练数据猜） | W3D1 |

### [[LlamaIndex]] 四大核心

| 概念 | 要点 | 来源 |
|------|------|------|
| `[[Document]]` | 把原始文本包装成 LlamaIndex 能理解的对象 | W3D1 |
| `[[Node]]` | 把 Document 切成小块的文本片段，每块是一个检索单元 | W3D1 |
| `[[Index]]` | 把 Node 向量化后存到索引里，方便语义检索 | W3D1 |
| `[[QueryEngine]]` | 接收问题 → 检索相关 Node → 把原文+问题发给 LLM → 返回答案 | W3D1 |

### [[embedding|嵌入模型]]（Embedding）

| 概念 | 要点 | 来源 |
|------|------|------|
| `[[embedding|嵌入模型]]` 的作用 | 把文字转成向量，用于计算"哪段文本和问题最相关" | W3D1 |
| BAAI/bge-small-zh-v1.5 | 中文优化的轻量嵌入模型，本地运行不调 API | W3D1 |
| ModelScope 下载 | `snapshot_download("模型名")` 从阿里云国内直连下载，替代 HuggingFace | W3D1 |
| HF 镜像 | `os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"` 但不如 ModelScope 稳定 | W3D1 |

### [[LlamaIndex]] 配置

| 概念 | 要点 | 来源 |
|------|------|------|
| `Settings.embed_model` | 全局设置嵌入模型，建索引时自动使用 | W3D1 |
| `Settings.llm` | 全局设置 LLM，查询时自动使用 | W3D1 |
| `OpenAILike` | LlamaIndex 通用 OpenAI 兼容接口，不校验模型名白名单 | W3D1 |
| `api_base` vs `base_url` | OpenAILike 用 `api_base`，原版 OpenAI 用 `base_url` | W3D1 |
| DeepSeek V4 beta 端点 | V4 需要 `api_base="https://api.deepseek.com/beta"`，V3 不需要 | W3D1 |

### 分块策略（Chunking）

| 概念 | 要点 | 来源 |
|------|------|------|
| 为什么需要切分 | LLM 上下文窗口有限，小块检索更精准，且向量化是按块进行的 | W3D2 |
| `SentenceSplitter` | LlamaIndex 默认切分器，按句子边界切，不会把一句话砍成两半 | W3D2 |
| `chunk_size` | 每块最大字符数，越小→Node 越多→检索更精准但上下文更少 | W3D2 |
| `chunk_overlap` | 相邻两块重叠的字符数，防止关键信息刚好落在两块的边界上被切断 | W3D2 |
| 实际测试 | 533 字符文档：chunk_size=256→3 块，512→2 块，1024→1 块（不够切） | W3D2 |

### 检索过程

| 概念 | 要点 | 来源 |
|------|------|------|
| `similarity_top_k` | 控制检索返回几个最相关的 Node，值越大信息越全但噪音越多 | W3D2 |
| `source_nodes` | response 的属性，包含了本次检索到的 Node 列表 | W3D2 |
| `source.score` | 相似度分数（0~1），越高越相关，但高分不一定等于精确匹配 | W3D2 |
| 检索流程 | 用户问题→向量化→和索引中每个 Node 的向量比余弦相似度→取 top_k | W3D2 |

### 索引持久化

| 概念 | 要点 | 来源 |
|------|------|------|
| 索引持久化 | `StorageContext` 管理存/读，`persist()` 序列化到硬盘，`load_index_from_storage()` 恢复，实测快 19x | W3D2 |
| `index.storage_context.persist()` | 把建好的索引序列化存到硬盘，只需执行一次 | W3D2 |
| `load_index_from_storage()` | 从硬盘恢复索引，不需要重新 embedding，实测快 19x | W3D2 |
| build once, load many | 建一次索引（build_index.py），以后每次启动直接加载（query_index.py） | W3D2 |

### Prompt 模板

| 概念 | 要点 | 来源 |
|------|------|------|
| prompt 在 RAG 里的角色 | 不是手写完整 messages，而是设计"填空题"——`{context_str}` 和 `{query_str}` 是占位符 | W3D2 |
| `{context_str}` | 占位符，LlamaIndex 在查询时自动替换为检索到的文档片段 | W3D2 |
| `{query_str}` | 占位符，自动替换为用户的问题 | W3D2 |
| `PromptTemplate` | LlamaIndex 的自定义模板类，传一个字符串即可定制 prompt 格式 | W3D2 |
| `get_prompts()` | 查看当前 query engine 使用的默认模板，调试用 | W3D2 |
| 自定义模板的意义 | 控制 LLM 行为边界——"资料没有就说不知道"防止幻觉，"不超过 3 句话"控制输出长度 | W3D2 |

### chat_engine 对话式 RAG（W3D3）

| 概念 | 要点 | 来源 |
|------|------|------|
| `query_engine` | 无状态，每次 `.query()` 独立，不知道已发生过什么对话 | W3D3 |
| `chat_engine` | 有状态，内部维护 `chat_history`，自动记住上文 | W3D3 |
| `chat.chat("消息")` | 发送消息并得到回复，历史自动累积 | W3D3 |
| `chat.chat_history` | 内部记忆列表，`[{user}, {assistant}, {user}, {assistant}, ...]`，每轮 +2 条 | W3D3 |

### 三种 chat_mode（W3D3-W3D4）

| mode | 原理 | 实测结论 |
|------|------|---------|
| `default` | 历史+检索放 messages 列表 | ❌ 新版 LlamaIndex 已废弃 |
| `condense_question` | 先让 LLM 把追问+历史重写成独立问题，再检索 | ⚠️ 结果不稳定，重写后检索可能跑偏 |
| `context` | 聊天历史全文塞进 system prompt | ✅ 中文多轮最稳定，指代消解能力最强 |

### chat_engine 进阶（W3D4）

| 概念 | 要点 | 来源 |
|------|------|------|
| `chat.reset()` | 清空全部聊天历史，适合话题彻底切换 | W3D4 |
| `stream_chat()` | 流式输出，逐 token 实时返回，提升用户体验 | W3D4 |
| `response.response_gen` | 流式输出的生成器，`for chunk in ...: print(chunk, end="")` | W3D4 |
| `response.source_nodes` | 查看 LLM 回答的检索依据（原文片段 + 相似度分数） | W3D4 |
| `source.score` | 相似度 0~1，但高分≠精确——实验发现检索到退货政策但 LLM 仍能答对会员权益 | W3D4 |
| `AgentChatResponse` | chat_engine 返回的类型（不是普通字符串），含多个属性 | W3D4 |
| 检索≠回答依据 | LLM 可能在检索不相关时用自己的知识回答——知识库更新时是风险 | W3D4 |

### 项目环境搭建

| 概念 | 要点 | 来源 |
|------|------|------|
| 虚拟环境 | `python -m venv .venv`，每个项目独立一套环境，互不干扰 | W3D1 |
| 环境三要素 | `.venv/`（包）+ `.env`（密钥）+ 代码文件 | W3D1 |

---

## [[踩坑记录]]

| 问题                            | 原因                                                            | 解决                                                               | 日期   |
| ----------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------- | ---- |
| `IndentationError`            | Python 用缩进划分代码块，冒号 `:` 后必须缩进                                  | 检查缩进级别，统一用 4 空格                                                  | W1D1 |
| try/except 对齐                 | `try` 和 `except` 必须在同一缩进级别                                    | 确保对齐                                                             | W1D1 |
| `NameError: not defined`      | 函数还没定义就调用了                                                    | 定义写在调用之前                                                         | W1D2 |
| 函数调用自己                        | 函数体内调用同名函数导致死循环                                               | 调用代码写在 `def` 外面                                                  | W1D2 |
| `with` 后面无内容                  | `with ... :` 后下一行必须缩进且有代码                                     | 冒号后写逻辑，缩进 4 格                                                    | W1D2 |
| `readlines()` 带 `\n`          | 每行末尾自带换行符                                                     | 用 `.rstrip("\n")` 去掉                                             | W1D2 |
| `StreamlitDuplicateElementId` | 同页面多个相同组件没有唯一 key                                             | 给每个组件加唯一的 `key` 参数                                               | W1D3 |
| `columns` 内容跑出布局              | `with col2:` 内的代码缩进错误，变成在并排区域外面                               | 检查缩进确保在 `with col:` 块内                                           | W1D3 |
| f-string 嵌套双引号                | `f"等待{config["name"]}"` 中双引号套双引号导致 SyntaxError                | 内层用单引号：`f"等待{config['name']}"`                                   | W2D1 |
| 变量先于定义使用                      | `choice = response.choices[0]` 写在 `response = ...create()` 前面 | 先创建 response 再从中取值，顺序不能反                                         | W2D1 |
| 展示区缩进在按钮内                     | 结果展示写在 `if st.button()` 里面，`st.rerun()` 后永远不执行                | 展示区顶到左边和按钮 `if` 平级                                               | W2D1 |
| Chat 模型耗时异常                   | deepseek-chat 有时 36 秒，正常应该是 3-5 秒                             | 服务端排队/网络波动，不代表模型本身速度                                             | W2D1 |
| Reasoner 引入不必要的库              | V3 为矩阵运算引入了 numpy，斐波那契完全不需要                                   | 代码评审关注：是否引入了不必要的依赖                                               | W2D1 |
| `st.rerun()` 放在按钮外导致无限刷新      | sidebar 历史展示区里放了 st.rerun()，每次渲染都触发重跑                         | st.rerun() 必须放在按钮的 else 分支里，不在展示区                                | W2D1 |
| Python 函数同名参数覆盖               | `OpenAI(api_key=A, api_key=B)` 后一个 api_key 覆盖前一个，不报错          | 不同端点的 client 各自创建实例，用字典索引                                        | W2D3 |
| 变量赋值是替换不是追加                   | `client = A; client = B; client = C` 只剩 C 一个值                 | 用字典 `{"a": A, "b": B, "c": C}` 存多个实例                             | W2D3 |
| 千问模型名填错导致巨慢                   | `qwen3.6-plus` 不是标准名，导致 33 秒才返回                               | 用 `qwen-plus`（DashScope 标准模型名）                                   | W2D3 |
| Qwen 过度输出                     | 简单问题给出 2000+ Token 论文式回答，Token 是 DS Chat 的 3.3 倍              | 需要精确控制输出长度时加 system prompt 约束，如"用不超过 3 句话回答"                     | W2D4 |
| f.read() 末尾逗号变元组              | `knowledge = f.read(),` 末尾逗号让变量变成 `(内容,)` 元组而非字符串             | 去掉末尾逗号                                                           | W3D1 |
| encoding 写在 open() 外面         | `f.read(), encoding="utf-8"` 被 Python 解析为元组                   | `encoding` 是 `open()` 的参数：`open("f.txt", "r", encoding="utf-8")` | W3D1 |
| HF 下载卡住                       | HuggingFace 在国内被墙，model.safetensors 无进度                       | 用 ModelScope `snapshot_download()` 国内直连                          | W3D1 |
| OpenAI/OpenAILike 参数名不同       | `OpenAI` 用 `base_url`，`OpenAILike` 用 `api_base`               | 查 `inspect.signature(Class.__init__)` 确认参数名                      | W3D1 |
| DeepSeek V4 400 错误            | `deepseek-v4-flash` 走 beta 通道，标准接口返回 400                      | `api_base="https://api.deepseek.com/beta"`                       | W3D1 |
