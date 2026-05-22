 # 知识点存档

> 每天学到的概念、语法、踩坑记录。配合 `progress.md` 使用。

---

## Python 基础

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

## API 调用

| 概念 | 要点 | 来源 |
|------|------|------|
| OpenAI 客户端 | `OpenAI(api_key=..., base_url=...)` 可对接兼容接口 | W1D1 |
| `chat.completions.create()` | 发送对话请求，model + messages 是必填项 | W1D1 |
| system prompt | 设定 AI 的角色和行为 | W1D1 |
| `.env` 管理密钥 | `load_dotenv()` + `os.getenv()` 读取 API Key，不写死在代码里 | W1D1 |

---

## Streamlit

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
## Python 进阶

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

## 踩坑记录

| 问题 | 原因 | 解决 | 日期 |
|------|------|------|------|
| `IndentationError` | Python 用缩进划分代码块，冒号 `:` 后必须缩进 | 检查缩进级别，统一用 4 空格 | W1D1 |
| try/except 对齐 | `try` 和 `except` 必须在同一缩进级别 | 确保对齐 | W1D1 |
| `NameError: not defined` | 函数还没定义就调用了 | 定义写在调用之前 | W1D2 |
| 函数调用自己 | 函数体内调用同名函数导致死循环 | 调用代码写在 `def` 外面 | W1D2 |
| `with` 后面无内容 | `with ... :` 后下一行必须缩进且有代码 | 冒号后写逻辑，缩进 4 格 | W1D2 |
| `readlines()` 带 `\n` | 每行末尾自带换行符 | 用 `.rstrip("\n")` 去掉 | W1D2 |
| `StreamlitDuplicateElementId` | 同页面多个相同组件没有唯一 key | 给每个组件加唯一的 `key` 参数 | W1D3 |
| `columns` 内容跑出布局 | `with col2:` 内的代码缩进错误，变成在并排区域外面 | 检查缩进确保在 `with col:` 块内 | W1D3 |
| f-string 嵌套双引号 | `f"等待{config["name"]}"` 中双引号套双引号导致 SyntaxError | 内层用单引号：`f"等待{config['name']}"` | W2D1 |
| 变量先于定义使用 | `choice = response.choices[0]` 写在 `response = ...create()` 前面 | 先创建 response 再从中取值，顺序不能反 | W2D1 |
| 展示区缩进在按钮内 | 结果展示写在 `if st.button()` 里面，`st.rerun()` 后永远不执行 | 展示区顶到左边和按钮 `if` 平级 | W2D1 |
| Chat 模型耗时异常 | deepseek-chat 有时 36 秒，正常应该是 3-5 秒 | 服务端排队/网络波动，不代表模型本身速度 | W2D1 |
| Reasoner 引入不必要的库 | V3 为矩阵运算引入了 numpy，斐波那契完全不需要 | 代码评审关注：是否引入了不必要的依赖 | W2D1 |
| `st.rerun()` 放在按钮外导致无限刷新 | sidebar 历史展示区里放了 st.rerun()，每次渲染都触发重跑 | st.rerun() 必须放在按钮的 else 分支里，不在展示区 | W2D1 |
