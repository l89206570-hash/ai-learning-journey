---
tags:
  - knowledge
  - ai-learning
  - python
  - llm
  - rag
  - streamlit
created: 2026-05-21
updated: 2026-06-01
---

# 知识点存档

> 每天学到的概念、语法、踩坑记录。配合 [[progress]] 使用。

---

## [[Python 基础]]

### 函数

| 概念 | 要点 | 来源 |
|------|------|------|
| `def` 定义函数 | `def` 是注册名字，不是执行；定义在前，调用在后 | W1D1 |
| 参数 vs 实参 | 括号里声明的叫形参（parameter），调用时传的叫实参（argument） | W1D1 |
| 参数类型标注 | `def func(name: str) -> str:` 标注入参和返回值类型 | W1D1 |
| 返回值 | `return` 把数据传回给调用者；`print()` 只输出到屏幕，返回 `None` | W1D1 |
| 无参函数 | `def f():` 不需要输入，括号留空 | W4D5 |
| 有参函数 | `def f(word: str):` 需要输入，函数体内用到的变量必须在括号里声明 | W4D5 |
| `**dict` 字典展开 | `func(**{"key": val})` 等价于 `func(key=val)`，动态传参用 | W4D5 |
| 函数签名规则 | 函数体内出现的每个变量，要么来自参数，要么在函数内部创建 | W4D5 |

### JSON

| 概念 | 要点 | 来源 |
|------|------|------|
| JSON 本质 | 跨语言传数据的通用格式，本质是"长得像 Python 字典的字符串" | W4D5 |
| `json.loads()` | JSON 字符串 → Python 字典 | W4D5 |
| `json.dumps()` | Python 字典 → JSON 字符串 | W4D5 |
| 为什么需要 JSON | Python 和 API 服务器用不同语言，JSON 是中间格式 | W4D5 |

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
| `for ... range(n)` | 固定次数循环，自动兜底防死循环，适合批处理 | W4D5 |
| `while` 循环 | 条件循环，`while True` 靠内部 `return`/`break` 退出，适合不确定次数的情况 | W4D5 |

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
| `st.rerun()` | **停止当前脚本，从头重新执行。** 之后的代码不会运行。必须放在条件分支里，裸奔在外面会无限循环。先改数据再 rerun，下次进来值相等跳过 if | W2D1, W3D7 |
| `st.rerun()` 防无限循环 | 开关模式：`if 值变了 → 改值 → 重建 → rerun（重启）→ 值相等 → 跳过 if → 正常渲染` | W3D7 |
| session_state vs chat_mode | session_state 是**保活容器**（让对象跨重跑存活），chat_mode="context" 是**记忆机制**（把历史塞进 system prompt）。两者解决不同问题 | W3D7 |
| session_state 分离 | 展示用完整数据（last_battle），历史存截断版（battle_history），各司其职省内存 | W2D1 |

### 新增组件

| 概念 | 要点 | 来源 |
|------|------|------|
| `st.checkbox()` | 勾选框，返回 `True/False`，`value=True` 设置默认勾选，`help=` 鼠标悬停提示 | W2D1 |

### Chat 组件（W3D7）

| 概念 | 要点 | 来源 |
|------|------|------|
| `st.chat_input()` | 对话式输入框，自动带输入提示，用户回车后返回字符串 | W3D7 |
| `st.chat_message(role)` | 聊天气泡容器，`role="user"` 或 `"assistant"`，`with` 块内写内容 | W3D7 |
| `st.write_stream(generator)` | 接收 generator，逐个 yield 渲染，返回完整字符串——替代手动 `for chunk in gen` 拼接 | W3D7 |

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

#### 嵌入模型 vs LLM（W3D7 核心认知）

> 两者是完全不同的模型，在 RAG 里各司其职：

| | 嵌入模型 (Embedding) | 大模型 (LLM) |
|---|---|---|
| 干什么 | 文字 → 向量（浮点数数组） | 文字 → 文字（生成回答） |
| 不能干什么 | 不会写句子、不会回答问题 | 不会算两段话有多相似 |
| 输入 | `"云感T恤 129 元"` | `"根据以下资料回答：{检索结果}，问题是：{用户问题}"` |
| 输出 | `[0.12, -0.34, 0.67, ...]` | `"您好，云感T恤售价 129 元"` |
| 项目里用的 | `BAAI/bge-small-zh-v1.5`（本地 CPU） | `deepseek-v4-flash`（DeepSeek 服务器） |
| 调用时机 | 建索引 + 每次查询向量化问题 | 检索完成后生成回答 |

#### 常用嵌入模型速查

| 模型 | 维度 | 语言 | 特点 |
|------|------|------|------|
| `BAAI/bge-small-zh-v1.5` | 512 | 中文 | 轻量本地跑，你正在用 |
| `BAAI/bge-large-zh-v1.5` | 1024 | 中文 | 同系列大号，更准但更慢 |
| `text-embedding-3-small` | 512 | 多语言 | OpenAI，API 调用按 Token 计费 |
| `moka-ai/m3e-base` | 768 | 中文 | 开源社区常用，ModelScope 可下 |

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

### 多文档索引（W3D5）

| 概念 | 要点 | 来源 |
|------|------|------|
| `Document(text, metadata)` | metadata 是 dict，可存 category/source/date 等任意标签，Node 切分时继承 | W3D5 |
| 跨文档检索 | 所有 Document 的 Node 进同一个向量库，检索自动跨越文档边界，不需切换代码 | W3D5 |
| `MetadataFilter(key, operator, value)` | 单条过滤规则：字段名 + 运算符 + 目标值 | W3D5 |
| `MetadataFilters(filters, condition)` | 组合多条 MetadataFilter，condition 为 `"and"` / `"or"`（注意小写） | W3D5 |
| `FilterOperator.EQ` | 等值比较，还有 NE/GT/LT/GTE/LTE/IN | W3D5 |
| `index.as_query_engine(filters=...)` | 检索时加过滤筛子，同一份索引可用不同 filter 反复查，不需重建 | W3D5 |
| `condition="and"` vs `"AND"` | 必须小写，大写会触发 Pydantic 校验错误 | W3D5 |

### 建索引 vs 查询的导入差异（W3D6）

| 导入 | 建索引 | 查询 | 原因 |
|------|:--:|:--:|------|
| `Document` | ✅ | ❌ | 建索引需包装文本，查询时已在索引里 |
| `VectorStoreIndex` | ✅ | ❌ | 查询用 `load_index_from_storage` 替代 |
| `SentenceSplitter` | ✅ | ❌ | 切分一次性，查询时 Node 已切好 |
| `MetadataFilters/MetadataFilter/FilterOperator` | ❌ | ✅ | 过滤是查询时加的筛子 |
| `load_index_from_storage` | ❌ | ✅ | 建索引写磁盘，查询读磁盘 |

共同依赖：`Settings`、`StorageContext`、嵌入模型、LLM — 不管建还是查都要配。

### 初级 RAG vs 生产级 RAG

| 维度 | 你现在 | 生产级 |
|------|--------|--------|
| 文档量 | 4 份 | 数千～百万份 |
| 存储 | 本地文件 | 向量数据库（Chroma/Milvus/Pinecone） |
| 检索策略 | 纯向量相似度 | 混合检索（向量 + BM25 关键词） |
| 结果优化 | 无 | 重排序（ReRanker） |
| 分块 | 固定 512 | 按文档结构智能切分 |

### 动态过滤切换（W3D7）

| 概念 | 要点 | 来源 |
|------|------|------|
| 重建 chat_engine | 切换品类时不能只改 filter 参数，必须重建整个 chat_engine（因为 filter 是创建时固化的） | W3D7 |
| 切换检测模式 | session_state 存 `current_category`，每次渲染对比 radio 值 → 变了就删旧 engine → 重建 → `st.rerun()` | W3D7 |
| chat_engine 生命周期 | 存在 `st.session_state["chat"]` 里跨重跑存活；品类切换或重置时删除/重建 | W3D7 |
| 先改值再 rerun | `current_category = 新值 → 重建 engine → st.rerun()`。如果先 rerun 再改值，下次进来值没变又会触发 | W3D7 |

### RAG 数据结构类型（W3D7）

| 类型 | 来源 | 访问方式 | 易错点 |
|------|------|---------|--------|
| `ChatMessage` | `chat.chat_history[i]` | `msg.role.value` / `msg.content` | 不是 dict，不能用 `msg["role"]` |
| `NodeWithScore` | `response.source_nodes[i]` | `node.score` / `node.node.metadata` / `node.node.text` | metadata 在 `.node` 里，不是顶层 |
| `ChatMessage.role` | 枚举 `MessageRole.USER` / `MessageRole.ASSISTANT` | `.value` 拿到 `"user"` / `"assistant"` 字符串 | 不调 `.value` 拿的是枚举对象不是字符串 |

### 对话双重存储（W3D7）

| 存储位置 | 格式 | 谁在用 | 怎么维护 | 删了会怎样 |
|----------|------|--------|---------|-----------|
| `st.session_state["messages"]` | `[{"role": "user", "content": "..."}]` | 你（渲染页面） | 手动 append | 页面上看不到历史，LLM 记忆不受影响 |
| `chat.chat_history` | `[ChatMessage, ChatMessage, ...]` | LlamaIndex（context mode） | chat_engine 自动维护 | AI 失去上下文记忆，变回无状态问答 |
| 为什么两个都要 | messages 让你自由控制页面显示，chat_history 让 LlamaIndex 把历史塞进 prompt。各管各的 | W3D7 |

### RAG 全链路（W3D7 总结）

```
文档 → Document → Node → Embedding模型 → 向量 → 索引存储
                                                    ↓
用户问题 → Embedding模型 → 问题向量 → 余弦相似度匹配 → top_k Node
                                                    ↓
                            LLM ← prompt(检索结果 + 问题 + 聊天历史)
                                                    ↓
                                                流式回答
```
| 来源 | W3D7 |

### 项目环境搭建

| 概念 | 要点 | 来源 |
|------|------|------|
| 虚拟环境 | `python -m venv .venv`，每个项目独立一套环境，互不干扰 | W3D1 |
| 环境三要素 | `.venv/`（包）+ `.env`（密钥）+ 代码文件 | W3D1 |

---

## [[Prompt Engineering 进阶]]（W4D3）

### 结构化 Prompt 五段法

| 段落 | 作用 | 回答的问题 |
|------|------|-----------|
| **System** | 角色定义 | 你是谁？ |
| **Context** | 背景信息 | 目标用户/平台/竞品是什么？ |
| **Instruction** | 具体指令 + 输出格式 | 做什么？步骤？输出什么结构？ |
| **Examples** | 正例 + 反例 | 什么样算好？什么样算差？ |
| **Constraints** | 约束条件 | 不能做什么？长度/风格限制？ |

### 实测对比（中文商品描述 → 英文亚马逊 listing）

| 版本 | Token | 耗时 | 标题质量 | 卖点呈现 | 输出格式 |
|------|-------|------|---------|---------|---------|
| A. 裸奔 | 1197 | 12.1s | 中式直译 | 黏在一起 | 自由发挥 |
| B. 一句话 | 537 | 4.8s | 略有优化 | 有分段 | 自由发挥 |
| C. 五段法 | 1460 | 10.3s | SEO 友好 | 逐一拆开 | 严格按模板 |

**结论：** 五段法 Token 最多但买到了可控性——固定输出格式、卖点分离清晰、英文更地道。工程化场景里这点成本换稳定性完全值得。

### 核心认知

- **可控性 > Token 成本：** 多花几百 Token 换来固定结构，后续解析/展示不用再猜格式
- **Constraint 比 Instruction 更有效：** "不要直译"四个字挡掉了前两个版本的主要问题
- **工作流化：** prompt 模板固化后，同品类（裤子/鞋子/配件）只需换 Context，不复用重写

| 来源 | W4D3 |

### Prompt 工程化实战（W4D4）

> 将 battle.py 从"无 system prompt"升级为可切换、可编辑的模板系统。

**改造内容：**
- `PROMPT_TEMPLATES` 字典管理 4 个场景（无模板/翻译/代码/推理），每个用五段法
- sidebar 加 `selectbox` 选场景 + `expander` 内 `text_area` 可编辑 prompt
- `day4_test_cases.py`：3 条固定测试，每次改 prompt 后跑一遍验证

**踩坑：**
- **prompt 一致性：** 改一段（Context）没改另一段（Examples），模型跟着旧信息跑偏。全部关联段落要同步改
- **user message 权重 ≥ system prompt：** 两边冲突时模型倾向信 user message。改了 prompt 模板还要检查输入里有没有矛盾信息
- **测试关键词要对齐语言：** `check_contains` 用中文关键词但模型输出英文 → 误报 FAIL。关键词要和 prompt 约束的输出语言一致

### 独立练习：邮件润色场景（W4D4）

> 不看代码模板，从零写一个邮件润色的五段法 prompt。

**学到的：**
- **Context 不要列能力：** 第一次写了四条"你能够..."在凑数。Context 是给背景信息（发件人身份、收件人、行业），不是复读 System
- **输出格式要提前定：** 没指定格式时模型跑出流水文。加了 `【润色后邮件】` + `【修改建议】` 后输出可解析、用户知道改了哪里
- **约束要贴近业务：** 邮件场景最关键的约束是"不改变原意（时间/地点/金额/需求）"，不是泛泛的"回答清晰"

**模板 vs 无模板实测对比（中文商务邮件 → 英文）：**

| | 无模板 | 邮件模板 |
|------|--------|---------|
| 邮件正文 | 英文，格式基本正确 | 英文，结构更完整（含 Subject） |
| 修改说明 | 无 | 逐条指出改了什么、为什么改 |
| 公司名纠错 | 自动改了 SUMSUNG→Samsung | 改了并说明原因 |
| 缺失信息 | 不提示 | 提示"网址缺失，建议补充" |
| 整体价值 | 翻译完就没了 | 翻译 + 教学，知道怎么改进 |

**结论：** 无模板也能翻对，但邮件模板多了"告诉用户为什么改"——这才是业务场景里的增值部分。

| 来源 | W4D4 |

---

## [[ChromaDB]] 向量数据库（W4D1）

### 核心概念

| 概念 | 要点 | 来源 |
|------|------|------|
| 向量数据库 | 存语义（向量）而非存文字——通过比较向量距离来判断"是不是在说同一件事" | W4D1 |
| ChromaDB | 轻量开源向量数据库，Python 原生，适合小中型项目（1000~百万级文档） | W4D1 |
| Collection | ChromaDB 的组织单元，类似 SQL 表——存 documents + embeddings + metadatas + ids | W4D1 |
| `chromadb.PersistentClient()` | 持久化模式，数据存硬盘，重启还在。比 LlamaIndex 手动 persist 更自动 | W4D1 |
| `collection.add()` | 添加文档，ChromaDB 自动调嵌入模型向量化后存库 | W4D1 |
| `collection.query()` | 问题自动向量化→和库里所有向量比距离→返回 top_k。传 `query_texts` + `n_results` | W4D1 |
| distance（距离） | ChromaDB 默认返回余弦距离，**越小越相似**（0=完全相同）。和 LlamaIndex score（越大越相似）相反 | W4D1 |

### 嵌入函数

| 概念 | 要点 | 来源 |
|------|------|------|
| `embedding_function` | 创建 Collection 时指定，负责把文字转成向量。ChromaDB 自带英文模型，中文场景必须换 | W4D1 |
| `SentenceTransformerEmbeddingFunction` | ChromaDB 方式加载模型：`model_name=` 可接 HuggingFace 模型名或本地路径 | W4D1 |
| 本地模型路径 | 用 ModelScope 缓存的绝对路径（`~/.cache/modelscope/hub/models/...`），跳过网络下载 | W4D1 |

### 元数据过滤

| 概念 | 要点 | 来源 |
|------|------|------|
| `where={"key": "value"}` | 精确过滤，等于 LlamaIndex 的 `MetadataFilter`，但在数据库层面执行 | W4D1 |
| `where={"$and": [...]}` | 组合条件，也支持 `$or`、`$in`、`$gte` 等操作符 | W4D1 |
| 过滤 vs 检索顺序 | ChromaDB 先过滤再检索，比"先搜出来再筛"更高效 | W4D1 |

### 增删改

| 概念 | 要点 | 来源 |
|------|------|------|
| `collection.update(ids=[...])` | 按 ID 更新文档内容和元数据 | W4D1 |
| `collection.delete(ids=[...])` | 按 ID 删除文档 | W4D1 |
| `collection.upsert()` | 存在就更新，不存在就插入——一条命令覆盖两种场景 | W4D1 |

### ChromaDB + LlamaIndex 集成

| 概念 | 要点 | 来源 |
|------|------|------|
| `ChromaVectorStore(chroma_collection=collection)` | 把 ChromaDB Collection 包装成 LlamaIndex 认识的 VectorStore | W4D1 |
| `StorageContext.from_defaults(vector_store=...)` | 告诉 LlamaIndex"向量存在 ChromaDB 里"——存储层可插拔的关键 | W4D1 |
| `VectorStoreIndex.from_documents(docs, storage_context=...)` | 建索引时自动把向量写入 ChromaDB，和本地存储建索引写法完全一样 | W4D1 |
| `index.storage_context.persist()` | 只存索引元数据（Node 结构等），向量由 ChromaDB 自己管理 | W4D1 |
| `load_index_from_storage(storage_context=...)` | 恢复索引：向量从 ChromaDB 读 + 元数据从磁盘读，不需要重新 embedding | W4D1 |

### ChromaDB vs SimpleVectorStore 对比

| 维度 | SimpleVectorStore (W3) | ChromaDB (W4) |
|------|------------------------|---------------|
| 存储格式 | JSON + .bin 文件 | SQLite + Parquet（数据库引擎） |
| 加载方式 | 全量加载到内存 | 按需读取，有索引加速 |
| 适合文档量 | < 1000 | 1000 ~ 百万级 |
| 并发查询 | 不支持 | 支持多客户端同时查 |
| 增量写入 | 需要 full rebuild | 直接 add，实时可见 |
| 生产环境 | 不适合 | 适合小中型项目 |

- 面试金句：SimpleVectorStore 适合原型验证，文档量上千或需增量更新时切换到 ChromaDB。切换成本很低——LlamaIndex 的 VectorStore 抽象层让换存储引擎只需改几行代码。

### 踩坑

| 问题 | 原因 | 解决 | 日期 |
|------|------|------|------|
| `UnicodeEncodeError: 'gbk' codec` | Windows 终端默认 GBK 编码，无法打印 emoji | 避免在 print 中用 emoji（如 `✅`） | W4D1 |
| ChromaDB 默认嵌入模型下载极慢 | `all-MiniLM-L6-v2` 从 AWS S3 下载 80MB，国内很慢 | 用 `SentenceTransformerEmbeddingFunction` 指向 ModelScope 缓存的中文模型 | W4D1 |
| `OpenAI` (新) 校验模型名白名单 | LlamaIndex 0.14+ 的 `llama_index.llms.openai.OpenAI` 只认 OpenAI 官方模型名 | 用 `llama_index.llms.openai_like.OpenAILike`（需单独 `pip install llama-index-llms-openai-like`），不校验模型名 | W4D1 |
| `load_index_from_storage()` 报找不到索引 | 只传 vector_store 不够，还需 persist_dir 指定元数据位置 | 先 `index.storage_context.persist(persist_dir=...)`，再加载时传 `StorageContext.from_defaults(vector_store=..., persist_dir=...)` | W4D1 |

### SimpleVectorStore → ChromaDB 迁移实战（W4D2）

| 概念 | 要点 | 来源 |
|------|------|------|
| 迁移改什么 | 改三处：建索引时加 ChromaDB client/collection/ChromaVectorStore；加载时先连 ChromaDB 再 load_index_from_storage；其余代码（分块/嵌入/LLM/chat_engine/过滤）完全不变 | W4D2 |
| build once, load many | build_index.py 建库（一次性，`create_collection` + `VectorStoreIndex` + `persist`），app.py 每次启动只加载（`get_collection` + `load_index_from_storage` | W4D2 |
| 两次持久化 | ChromaDB 自动存向量（SQLite），LlamaIndex 的 `persist()` 只存元数据（docstore/index_store）——两者各管各的，加载时两个都要 | W4D2 |
| Collection 名称一致性 | build 的 `create_collection(name="xxx")` 和 app 的 `get_collection("xxx")` 必须同名 | W4D2 |
| metadata 值一致性 | build_index 写入的 metadata category 值和 app 过滤用的值必须完全一致，否则品类筛选无结果 | W4D2 |
| 品类切换 = 新会话 | 切换品类时重建 chat_engine 会清空 chat_history，上下文丢失。这是当前设计的 trade-off | W4D2 |

| 问题 | 原因 | 解决 | 日期 |
|------|------|------|------|
| `VectorStoreIndex()` 无赋值 | 创建了 index 但没赋给变量，下一行调 `index.xxx` 报 NameError | `index = VectorStoreIndex(...)` | W4D2 |
| 变量名 typo（cilent/client） | 拼写错误不报语法错，运行时才炸 NameError | 仔细检查变量名 | W4D2 |
| `MetadataFilter` vs `MetadataFilters` | 单数是过滤条，复数是装多条规则的容器 | 单条用 `MetadataFilter`，多条用 `MetadataFilters(filters=[...])` | W4D2 |
| W4 venv 缺 streamlit | Day 1 只用 ChromaDB 不需要 streamlit，Day 2 新增依赖 | `pip install streamlit` | W4D2 |

---

## [[Agent Loop]]（W4D5）

> 不用任何框架，纯 OpenAI API 的 `tools` 参数实现 Agent 循环。

### 核心概念

| 概念 | 要点 | 来源 |
|------|------|------|
| Agent Loop | LLM 反复调工具直到能回答用户的循环：调 API → 判断 → 执行工具/返回答案 | W4D5 |
| ReAct 模式 | Reasoning + Acting，LLM 先思考要不要用工具，再用工具，再看结果 | W4D5 |
| `tools=` 参数 | `chat.completions.create(tools=TOOLS)` 告诉 LLM 有哪些工具可用 | W4D5 |
| `msg.tool_calls` | LLM 返回工具调用请求时用这个字段判断，非 `None` 表示要调工具 | W4D5 |
| TOOLS 结构 | `{"type": "function", "function": {"name": "...", "parameters": {...}}}` | W4D5 |
| TOOL_MAP | 工具名字符串 → 实际 Python 函数的映射字典，循环里动态调用 | W4D5 |

### 循环流程

```
用户提问 → messages = [system, user]
  ↓
for turn in range(max_turns):
  ├─ 调 API（带 tools=TOOLS）
  ├─ 如果 msg.tool_calls：
  │    ├─ 取 tool_name + tool_args
  │    ├─ TOOL_MAP[tool_name](**tool_args) 执行
  │    ├─ messages 追加 assistant(tool_calls) + tool(result)
  │    └─ 继续循环
  └─ 如果没有 tool_calls：
       └─ 返回 msg.content（最终答案）
```

### 踩坑

| 问题 | 原因 | 解决 |
|------|------|------|
| 函数体用 `word` 但声明里没写参数 | 函数体内用到的变量必须在括号里声明 | `def f(word: str):` |
| `return print(...)` | `print()` 返回 `None`，只有输出没有传值 | 要传值用 `return`，要显示用 `print` |
| TOOLS 里函数名抄错 | 复制粘贴没改干净 | 复制完逐项检查关键字段 |
| `properties` 拼成 `properyies` | 手滑 | 跑一下就能发现 SyntaxError |
| `len(str)` 不是 `len(word)` | `str` 是内置类型名，不是你的变量 | 变量名是你起的，别和内置名冲突 |

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
| `MetadataFilters` condition 大小写 | `condition="AND"` 触发 Pydantic ValidationError，报 enum 错误         | 必须用小写 `condition="and"`                                         | W3D6 |
| deepseek-v4-flash Empty Response | 检索正常但 LLM 返回空，Django 问题正常但 CSS 问题为空——非代码 bug，模型行为不稳定          | 单次只问一件事，或换 deepseek-chat                                        | W3D5 |
| query.py 缺少 Settings 配置       | 加载索引后直接用 as_query_engine 但没配 embed_model 和 llm，导致查询时无模型可用   | 在 load_index_from_storage 之前配好 Settings.embed_model + Settings.llm | W3D6 |
| `st.rerun()` 放 if 外导致无限刷新     | `st.session_state["messages"] = []` 和 `st.rerun()` 没缩进在 `if st.button()` 内，每次渲染都触发 | st.rerun() 必须在按钮的 if 分支里面 | W3D7 |
| `for msg,` 多余逗号               | `for msg, in list` 被 Python 解析为元组解包，ChatMessage 对象不可迭代 | 去掉末尾逗号：`for msg in list` | W3D7 |
| ChatMessage 当成 dict 用          | `msg["role"]` 访问 ChatMessage 对象，但它是对象不是字典 | 用 `msg.role.value` 和 `msg.content` 属性访问 | W3D7 |
| source_nodes 层级混淆             | `node.metadata` 直接取——`source_nodes` 返回的是 `NodeWithScore` 列表，metadata 在 `node.node.metadata` 里 | 用 `node.node.metadata` 取元数据 | W3D7 |
