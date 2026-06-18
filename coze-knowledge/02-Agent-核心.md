# Agent 核心：从手写循环到框架编排

## Agent Loop 手写实现

不用任何框架，纯 OpenAI API 的 tools 参数实现 Agent 循环。

### 核心概念

| 概念 | 要点 |
|------|------|
| Agent Loop | LLM 反复调工具直到能回答用户的循环：调 API → 判断 → 执行工具/返回答案 |
| ReAct 模式 | Reasoning + Acting，LLM 先思考要不要用工具，再用工具，再看结果 |
| tools= 参数 | chat.completions.create(tools=TOOLS) 告诉 LLM 有哪些工具可用 |
| msg.tool_calls | LLM 返回工具调用请求时用这个字段判断，非 None 表示要调工具 |
| TOOL_MAP | 工具名字符串 → 实际 Python 函数的映射字典，循环里动态调用 |

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

### Agent 不关心工具内部实现

LLM 只知道工具名 + description + 参数，不管数据源是 dict、ChromaDB 还是 API——这就是工具的可替换性。搜索函数内部调 collection.query() 和调 dict.get() 对外接口完全一样。

---

## Agent 三范式对比（ReAct / Plan-Execute / Reflexion）

### ReAct

思考 → 行动 → 观察 → 再思考 → 再行动 → 回答。代码本质：一个 for turn in range(max_turns) 循环 + if/else 分支。LLM 自己决定每一步做什么，代码只负责执行工具和传递结果。

### Plan-then-Execute

上来先不调用工具，只思考并生成路线图后再按路线图执行。和 ReAct 最核心的区别：

| 差异点 | ReAct | Plan-then-Execute |
|--------|-------|-------------------|
| 第一次 API 调用 | 带 tools=TOOLS | 不带 tools，纯文本输出计划 |
| 谁驱动循环 | LLM 的 tool_calls | 你的代码（逐步骤 push）或一句指令 |

### Reflexion

两轮循环：第一轮出初步答案 → messages.append("请检查你的回答是否完整正确") → 第二轮出改进后答案。反思提示放在两个 for 循环之间（和 for 同级缩进，不在循环里面）。

### 三种范式场景选择

| 范式 | 适合场景 | 例子 |
|------|---------|------|
| ReAct | 任务信息不确定，需要灵活探索 | "帮我在三个电商平台对比 iPhone 价格" |
| Plan-then-Execute | 任务步骤明确、可预见 | "写一份周报：查本周代码提交 + 会议纪要 + 项目进度" |
| Reflexion | 对答案质量要求高 | "帮我审核这段代码的安全性"（需要自查是否有遗漏的漏洞） |

---

## Skills vs Tools

Tool 是螺丝刀，Skill 是工具箱（prompt + tools + 流程 + 测试打包在一起）。

| | Tool | Skill |
|------|------|------|
| 组成部分 | 一个函数 + description | prompt + tools + 输入输出 schema + 测试用例 |
| system prompt | 全局通用，"万金油" | 专用 prompt，精准描述本 Skill 的职责 |
| 加新能力 | 改全局 prompt + 往 TOOLS 列表追加 | 新增一个 Skill 对象，不动已有 Skill |
| 工具集大小 | 全部工具混在一起，LLM 从 30 个里选 | 每个 Skill 只有 2-5 个相关工具，选择更准 |
| 可测试性 | 只能端到端测整个 Agent | 每个 Skill 自带 test_cases，独立验证 |
| 切思维模式 | 靠 prompt 里写"如果是代码问题就..." | 切 Skill = 切 prompt + 切工具集，思维模式自动切换 |

### Skill 五要素

1. **name + description** — 告诉调度者"我能做什么"
2. **system_prompt** — 告诉 LLM "在这个 Skill 里你怎么干活"
3. **tools** — 这个 Skill 专属的工具函数（精简，只放相关的）
4. **input_schema** — 触发条件（关键词/embedding 相似度）
5. **test_cases** — 独立于 Agent 的单元测试

### 面试金句

"我们的 Agent 不是直接管 30 个工具，而是按业务域拆成 Skill——每个 Skill 是 prompt + tools + schema 的封装。调度层按意图路由到 Skill，Skill 内部用专用 prompt 执行。加能力不动已有 Skill、每个 Skill 独立可测、切 Skill 切思维模式。"

---

## LangGraph Agent 框架

LangGraph 是状态图执行引擎——提供节点+边+状态的积木，你搭什么图就什么范式。不是"ReAct 框架"，是"搭 Agent 工作流的框架"。ReAct 是设计模式（思考→行动→观察），LangGraph 是执行引擎（搭图跑工作流）。

### Day 1 手写 → Day 2 LangGraph 映射

| Day 1 手写 | LangGraph 替你做 | 省了什么 |
|------|------|------|
| messages = [...] 手动管理列表 | AgentState(TypedDict) + add_messages reducer | 消息追加、去重、合并自动完成 |
| while turn in range(...): 循环控制 | StateGraph.compile() 图执行引擎 | 不用写循环，引擎自动在节点间流转 |
| if msg.tool_calls: ... else: return | tools_condition 条件边 | 不用手写判断分支 |
| json.loads(args) + TOOL_MAP[name](**args) | ToolNode(TOOLS) | 自动解析参数→执行函数→返回 ToolMessage |
| max_turns 手动计数 | recursion_limit 参数（默认 25） | 框架兜底防死循环 |
| 无持久化 | MemorySaver checkpoint | 每步自动保存状态，可暂停/恢复/回溯 |

### LangGraph API 速查

**图结构：**
- StateGraph(AgentState) — 创建状态图，绑定状态类型
- graph.add_node("名字", 函数) — 添加节点
- graph.add_edge("A", "B") — 固定边：A 执行完一定去 B
- graph.add_conditional_edges("A", 判断函数) — 条件边：根据返回值决定去向
- graph.set_entry_point("A") — 指定入口节点
- graph.compile(checkpointer=...) — 编译成可执行图
- tools_condition — 内置判断函数：消息有 tool_calls → "tools"，否则 → END

**工具相关：**
- @tool 装饰器 — 把普通函数包装成 LangChain Tool，自动从类型标注和 docstring 生成参数 schema——替代手写 35 行 JSON
- convert_to_openai_function(tool) — LangChain Tool → OpenAI API 需要的 function 格式
- ToolNode(tool_list) — 自动执行工具调用的节点

### Checksystem 三个核心能力

这三个能力 = LangGraph 和手写 Agent 循环的代差：

| 能力 | API | 作用 |
|------|-----|------|
| 持久化 | SqliteSaver | 跨进程持久化到 SQLite |
| 暂停审批 | interrupt() | 在节点内部暂停图执行，等人给值后继续 |
| 时间旅行 | get_state / update_state | 查看/修改/分叉历史状态 |

面试金句：手写 Agent 循环能做到"调工具→看结果→再调"，但做不到"暂停→恢复"和"时间旅行"。这就是生产环境用 LangGraph 而不是自己写 while True 的原因。

### 三范式图拓扑对比

```
ReAct:       agent ←→ tools              — 一个循环，agent 自己决定何时停
Plan-Exec:   plan → execute ←→ tools     — 先出路线图，再进入执行循环
Reflexion:   agent ←→ tools              — 多一个"质检站"
               ↓
             reflect → agent (重来)
               ↓
              END
```

关键差异在路由逻辑：

| 范式 | agent 之后去哪 | 谁决定结束 |
|------|--------------|-----------|
| ReAct | 有 tool_calls → tools；无 → END | agent 自己（tools_condition） |
| Plan-Exec | 同上 | agent 自己 |
| Reflexion | 有 tool_calls → tools；无 → reflect | reflect 节点（不是 agent） |

---

## Agent Chat 交互界面（Streamlit）

把命令行 Agent Loop 升级成聊天界面。

| 概念 | 要点 |
|------|------|
| yield 生成器 | 函数可以多次返回值，每次 yield 后暂停，下次从暂停处继续；return 只返回一次 |
| st.chat_message() | 聊天气泡组件 |
| st.chat_input() | 底部聊天输入框 |
| st.status() | 可展开的状态框，用 with 创建 |
| 多轮对话记忆 | for m in st.session_state.messages: messages.append(m) 把历史对话传给 LLM |

**TOOL_MAP 的作用：** Agent 收到的是工具名字符串（如 "calculate"），不能直接 "calculate"(args) 调用。TOOL_MAP 是字符串→函数的桥梁。
