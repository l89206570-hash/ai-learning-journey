# W5 Day 2 — LangGraph 重构 ReAct Agent
"""
用 LangGraph 重建 Day 1 的 ReAct Agent，对比框架 vs 手写差异。

Day 1 你做的事（纯 API 手写）：
  1. 手动管理 messages 列表（追加 assistant + tool 消息）
  2. 手动解析 tool_calls JSON → 查 TOOL_MAP → 调用函数
  3. 手动写 while 循环控制"调用工具还是回答"
  4. 手动跟踪 turn 数防止死循环

LangGraph 帮你做什么（今天学）：
  1. StateGraph = 声明式状态管理，消息自动追加
  2. ToolNode = 自动解析 tool_calls → 执行 → 返回 ToolMessage
  3. tools_condition = 自动判断"走工具还是结束"
  4. Checkpoint = 每步自动保存状态，可回溯

概念映射（手写 → LangGraph）：
  手写 while 循环                   → StateGraph 的节点 + 边
  手写 if msg.tool_calls 判断       → tools_condition 条件边
  手写 json.loads + TOOL_MAP[func] → ToolNode
  手写 messages.append(...)        → add_messages reducer
"""

import os
import json
import sys
from typing import Annotated, Literal
from typing_extensions import TypedDict
from dotenv import load_dotenv
from openai import OpenAI

# LangGraph 核心
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, convert_to_openai_messages
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_function

# Windows 终端 GBK 编码修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# ============================================================
# 共享工具 — 跟 Day 1 一模一样
# ============================================================

KNOWLEDGE = {
    "Python": "Python 是 Guido van Rossum 于 1991 年发布的编程语言，以简洁易读著称。广泛应用于 AI 开发。",
    "RAG": "RAG（检索增强生成）是一种让 LLM 先检索外部知识再回答的 AI 技术，核心是减少幻觉、提供可溯源的答案。",
    "Agent": "AI Agent 是能自主使用工具、规划步骤、执行任务的智能体，是 2026 年 AI 应用开发最热门的方向。",
    "ChromaDB": "ChromaDB 是一个开源的向量数据库，用于存储和检索嵌入向量。",
    "Streamlit": "Streamlit 是一个 Python Web 框架，几行代码就能构建数据应用。",
}


@tool
def search_knowledge(query: str):
    """在知识库中模糊搜索概念"""
    query_lower = query.lower()
    results = []
    for key, value in KNOWLEDGE.items():
        if key.lower() in query_lower or query_lower in key.lower():
            results.append(f"【{key}】{value}")
    if results:
        return "\n\n".join(results)
    return f"未找到与「{query}」相关的知识。"


@tool
def calculate(expression: str):
    """安全计算数学表达式"""
    allowed = {"__builtins__": {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "int": int, "float": float,
    }}
    try:
        return f"计算结果：{eval(expression, allowed)}"
    except Exception as e:
        return f"计算出错：{e}"


# @tool 装饰器自动生成 schema，不需要手写 Day1 那种 JSON TOOLS 列表
TOOLS = [search_knowledge, calculate]

# ============================================================
# LangGraph 实现
# ============================================================

# --- 步骤 1: 定义 State（替代你手写的 messages 列表）---
# State 是图的"共享内存"，每个节点能读也能写
# add_messages 是 reducer：新消息自动 append 到 messages 列表末尾
#      → Day 1 你手写: messages.append({...})  ← 现在 LangGraph 自动做
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# --- 步骤 2: 定义 Agent 节点（替代你手写的 LLM 调用那一段）---
# 节点 = 一个纯函数，接收 State 返回 State 的更新部分
# LangGraph 调用这个函数 → 拿到返回 → 用 add_messages 合并到 State

def call_model(state: AgentState):
    """
    Agent 节点：调用 LLM，返回消息。
    LangGraph 会自动用 add_messages 把返回值追加到 state["messages"]。
    """
    # 转换工具 schema
    openai_tools = [
        {"type": "function", "function": convert_to_openai_function(t)}
        for t in TOOLS
    ]
    # LangChain 消息 → OpenAI dict 格式
    openai_messages = convert_to_openai_messages(state["messages"])

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=openai_messages,
        tools=openai_tools,
    )
    msg = response.choices[0].message

    # OpenAI message → LangChain AIMessage（add_messages 只认 LangChain 格式）
    if msg.tool_calls:
        # 有 tool_calls → 转成带 tool_calls 的 AIMessage
        lc_tool_calls = [
            {
                "name": tc.function.name,
                "args": json.loads(tc.function.arguments),
                "id": tc.id,
            }
            for tc in msg.tool_calls
        ]
        ai_msg = AIMessage(content="", tool_calls=lc_tool_calls)
    else:
        ai_msg = AIMessage(content=msg.content)

    return {"messages": [ai_msg]}


# --- 步骤 3: 构建图 ---
# 节点 + 边 + 条件边 = 可执行的 Agent 工作流

def build_graph():
    """
    构建 LangGraph ReAct 图。

    结构：
        START → agent_node ──┬── tools_condition ──→ tool_node ──┐
                              │                                    │
                              └── tools_condition ──→ END          │
                                                                   │
                                      ←────────────────────────────┘
    """
    # 创建图，绑定 State 类型
    graph = StateGraph(AgentState)

    # 添加节点
    # "agent" = 你 Day 1 的 LLM 调用部分
    # "tools" = 你 Day 1 的 tool_calls 解析 + 执行部分
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(TOOLS))

    # 入口：从 START 开始就是 agent 节点
    graph.set_entry_point("agent")

    # 条件边：agent 之后去哪？
    #   → 如果 LLM 返回了 tool_calls → 去 tools 节点
    #   → 如果 LLM 返回了纯文本      → 去 END（结束）
    # 这就是你 Day 1 手写的 if msg.tool_calls: else:
    graph.add_conditional_edges(
        "agent",
        tools_condition,  # LangGraph 内置的条件判断函数
    )

    # 普通边：tools 执行完 → 回到 agent（形成循环）
    # 这就是你 Day 1 的 while 循环里的"回到顶部"
    graph.add_edge("tools", "agent")

    # 编译，加 checkpointer（内存版，记录每步状态）
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# ============================================================
# 运行测试
# ============================================================

SYSTEM_PROMPT = """你是一个使用 ReAct 模式的 AI 助手。

规则：
1. 分析用户的问题，想清楚需要什么信息
2. 一次只调用一个工具，拿到结果再决定下一步
3. 当信息足够时，直接给出最终答案（不要再调工具）
4. 搜索知识库用中文关键词"""


def run_langgraph_agent(user_query: str):
    """
    用 LangGraph 运行 ReAct Agent。

    对比 Day 1 的 react_agent()：
      — 没有 while 循环了
      — 没有 if msg.tool_calls / else 分支了
      — 没有 json.loads(tool_call.function.arguments) 了
      — 没有 messages.append(...) 了
      — 没有 turn 计数器了

    所有这些被 LangGraph 的图执行引擎接管了。
    """
    app = build_graph()

    # 初始 State — SystemMessage(角色设定) + HumanMessage(用户问题)
    initial_state = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_query),
        ]
    }

    # 配置（checkpointer 需要 thread_id 来区分不同对话）
    config = {"configurable": {"thread_id": "w5d2-demo"}}

    print("=" * 60)
    print(f"[LangGraph ReAct] 用户: {user_query}")
    print("=" * 60)

    # --- 方式 A: stream() 逐步打印（展示框架在做什么）---
    print("\n--- 逐步执行（展示每步发生了什么）---")
    step = 0
    for event in app.stream(initial_state, config):
        step += 1
        node_name = list(event.keys())[0]  # "agent" 或 "tools"
        node_data = event[node_name]
        msgs = node_data.get("messages", [])

        for msg in msgs:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tool_call = msg.tool_calls[0]
                print(f"  [Step {step} — agent] 调工具: {tool_call['name']}({tool_call['args']})")
            elif hasattr(msg, "content") and msg.content and not hasattr(msg, "tool_calls"):
                # ToolMessage — 工具返回结果
                if hasattr(msg, "type") and msg.type == "tool":
                    print(f"  [Step {step} — tools] 结果: {msg.content[:100]}...")
                # AIMessage — 最终答案
                elif hasattr(msg, "type") and msg.type == "ai":
                    print(f"  [Step {step} — agent] 最终答案")

    # 拿到最终 State
    final_state = app.get_state(config)
    final_messages = final_state.values["messages"]

    # 最后一条消息就是最终答案
    last_msg = final_messages[-1]
    answer = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
    print(f"\n[最终答案] {answer}")
    return answer


def compare_day1_vs_day2():
    """
    打印 Day 1 手写 vs Day 2 LangGraph 的代码对比。
    """
    print("\n" + "=" * 60)
    print("Day 1 手写 vs Day 2 LangGraph — 代码量对比")
    print("=" * 60)

    comparison = """
    ┌──────────────────────────┬───────────────────────────────────┐
    │ Day 1 你手写了什么        │ Day 2 LangGraph 替你做            │
    ├──────────────────────────┼───────────────────────────────────┤
    │ messages = [...]          │ AgentState(TypedDict)             │
    │                           │ + add_messages reducer             │
    ├──────────────────────────┼───────────────────────────────────┤
    │ while turn in range(...): │ StateGraph.compile()              │
    │   循环控制                 │ 图执行引擎自动循环                  │
    ├──────────────────────────┼───────────────────────────────────┤
    │ if msg.tool_calls: ...    │ tools_condition                   │
    │ else: return              │ 条件边自动路由                      │
    ├──────────────────────────┼───────────────────────────────────┤
    │ json.loads(args)          │ ToolNode(TOOL_MAP)                │
    │ TOOL_MAP[name](**args)   │ 自动解析+执行+返回 ToolMessage     │
    ├──────────────────────────┼───────────────────────────────────┤
    │ 手动 messages.append(...) │ add_messages reducer              │
    │ 两条（assistant + tool）  │ 节点返回 + reducer 自动合并         │
    ├──────────────────────────┼───────────────────────────────────┤
    │ max_turns 手动计数        │ recursion_limit 参数               │
    │                           │ (compile 时设, 默认 25)           │
    ├──────────────────────────┼───────────────────────────────────┤
    │ 无持久化                  │ MemorySaver checkpoint             │
    │                           │ 每步自动保存, 可回溯/恢复           │
    └──────────────────────────┴───────────────────────────────────┘
    """
    print(comparison)


if __name__ == "__main__":
    TASK = "请帮我查一下 Python、RAG、Agent 这三个概念，然后按名称长度从短到长排序，并告诉我哪个概念和 AI 最相关"

    # 用 LangGraph 跑同一个任务
    result = run_langgraph_agent(TASK)

    # 打印对比
    compare_day1_vs_day2()

    print("\n" + "█" * 60)
    print("█  关键认知")
    print("█" * 60)
    print("""
    1. LangGraph 不是"封装了 ReAct 循环"。
       它是更底层的——提供了一个"状态图执行引擎"。
       ReAct 只是你用它搭出来的一种图结构（agent ↔ tools）。

    2. 你可以搭出 Plan-Execute 图（计划节点 → 执行节点 → 汇总节点）。
       也可以搭 Reflexion 图（执行 → 反思节点 → 重试或结束）。
       同一个框架，你搭什么图就什么范式——不是"ReAct 框架"。

    3. Day 1 的手写代码是你理解框架的基础。
       不会手写就不知道框架帮你省了什么，面试就被一句"ReAct 原理"问倒。
    """)
