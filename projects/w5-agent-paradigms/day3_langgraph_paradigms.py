# W5 Day 3 — LangGraph 实现 Plan-Execute + Reflexion
"""
Day 2 你搭了 ReAct 图（agent ↔ tools 循环）。
今天搭 Plan-Execute 和 Reflexion 图，验证"同一个框架，图拓扑不同 = 范式不同"。

三张图的拓扑对比：
  ReAct:       agent ↔ tools（循环直到 agent 决定结束）
  Plan-Exec:   plan → execute → tools → execute → ... → END
  Reflexion:   agent → tools → ... → reflect → (满意→END / 不满意→agent重来)
"""

import os
import json
import sys
from typing import Annotated, Literal
from typing_extensions import TypedDict
from dotenv import load_dotenv
from openai import OpenAI

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage, convert_to_openai_messages
)
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_function

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# ============================================================
# 共享工具 — 跟 Day 1/Day 2 一样
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


TOOLS = [search_knowledge, calculate]
OPENAI_TOOLS = [
    {"type": "function", "function": convert_to_openai_function(t)}
    for t in TOOLS
]

# ============================================================
# 共享状态
# ============================================================

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    # Plan-Execute 专用：存计划文本，跨节点传递
    plan: str
    # Reflexion 专用：反思轮次计数
    reflection_count: int


def _call_llm(messages, with_tools=True):
    """通用 LLM 调用 — 三种范式共用"""
    tools = OPENAI_TOOLS if with_tools else None
    openai_msgs = convert_to_openai_messages(messages)
    response = client.chat.completions.create(
        model="deepseek-chat", messages=openai_msgs, tools=tools,
    )
    msg = response.choices[0].message
    if msg.tool_calls:
        lc_tool_calls = [
            {"name": tc.function.name, "args": json.loads(tc.function.arguments), "id": tc.id}
            for tc in msg.tool_calls
        ]
        return AIMessage(content="", tool_calls=lc_tool_calls)
    return AIMessage(content=msg.content)


# ============================================================
# 范式二：Plan-then-Execute（LangGraph 版）
# ============================================================
#
# 图结构：
#   START → plan(纯文本，不用工具) → execute(带工具，按计划执行)
#            execute ──┬── tools_condition ──→ tools ──→ execute
#                      └── tools_condition ──→ END
#
# 和 Day 1 方式 C 对应：先拿到计划 → 一句"按计划执行" → ReAct 循环

PLAN_SYSTEM = """你是一个使用 Plan-then-Execute 模式的 AI 助手。

当用户提出问题时，先制定计划再执行。
计划格式：一个编号的步骤列表，每步具体可执行。
完成后给出最终答案。"""


def plan_node(state: AgentState):
    """
    计划节点：不加 tools，让 LLM 输出纯文本计划。
    和 Day 1 "阶段1：制定计划" 对应——那次调用没传 tools。
    """
    plan_msg = _call_llm(state["messages"], with_tools=False)
    plan_text = plan_msg.content
    print(f"  [计划]\n{plan_text}\n")
    return {
        "messages": [plan_msg],
        "plan": plan_text,
    }


def execute_node(state: AgentState):
    """
    执行节点：带 tools，让 LLM 按计划逐步执行。
    这一步会触达 tools_condition → tools 节点 → 回到这里。
    """
    # 第一次进 execute_node 时追加"按计划执行"指令
    last_msg = state["messages"][-1]
    need_instruction = hasattr(last_msg, "content") and "按计划执行" not in str(last_msg.content)

    if need_instruction and state.get("plan"):
        messages = list(state["messages"]) + [
            HumanMessage(content="请严格按照上述计划逐步执行，完成后给出最终答案。")
        ]
    else:
        messages = state["messages"]

    result = _call_llm(messages, with_tools=True)
    return {"messages": [result]}


def build_plan_execute_graph():
    """构建 Plan-Execute 图"""
    graph = StateGraph(AgentState)

    graph.add_node("plan", plan_node)
    graph.add_node("execute", execute_node)
    graph.add_node("tools", ToolNode(TOOLS))

    graph.set_entry_point("plan")
    graph.add_edge("plan", "execute")
    graph.add_conditional_edges("execute", tools_condition)
    graph.add_edge("tools", "execute")

    return graph.compile(checkpointer=MemorySaver())


# ============================================================
# 范式三：Reflexion（LangGraph 版）
# ============================================================
#
# 图结构：
#   START → agent(带工具) ──┬── tools_condition ──→ tools ──→ agent
#                           └── tools_condition ──→ reflect(自我评价)
#   reflect ──┬── "retry" ──→ agent（带着改进建议重新来）
#             └── "done"  ──→ END
#
# 关键：agent 的 tools_condition 不再直接到 END，
# 而是无 tool_calls 时去 reflect——让 reflect 决定是否真的结束。
# 只有 reflect 满意了，图才到 END。

REFLEXION_SYSTEM = """你是一个使用 Reflexion 模式的 AI 助手。

工作方式：
1. 先尝试回答用户问题（可以调用工具获取信息）
2. 审视自己的回答：信息完整吗？结论正确吗？有没有遗漏用户要求？
3. 如果不够好，说明哪里不足然后重新回答
4. 如果满意，给出最终答案"""


def agent_node(state: AgentState):
    """Agent 节点：带工具，尝试回答问题"""
    result = _call_llm(state["messages"], with_tools=True)
    return {"messages": [result]}


def reflect_node(state: AgentState):
    """
    反思节点：不带工具，让 LLM 检查自己的答案。
    返回 {"retry"} → 回到 agent 重做，或 {"done"} → 结束。

    和 Day 1 的"请检查你的回答是否完整正确"是同一个思路，
    但这里用 return 值控制图流转，不是写第二个 for 循环。
    """
    messages = list(state["messages"])
    messages.append(HumanMessage(
        content="请检查你上面的回答是否完整正确。"
                "如果不够好，先说哪里不足，然后重新搜索并回答。"
                "如果已经满意，请说 FINAL 并给出最终答案。"
    ))
    result = _call_llm(messages, with_tools=False)
    response_text = result.content

    # 判断 LLM 是否满意
    if "FINAL" in response_text.upper():
        print(f"  [反思] 满意 → 结束")
        print(f"  [最终答案] {response_text}")
        return {
            "messages": [result],
            "reflection_count": state.get("reflection_count", 0) + 1,
        }
    else:
        count = state.get("reflection_count", 0) + 1
        if count >= 3:  # 最多反思 3 次
            print(f"  [反思] 已达最大反思次数 → 结束")
            return {
                "messages": [result],
                "reflection_count": count,
            }
        print(f"  [反思 #{count}] 不满意 → 重新回答")
        print(f"  [反思意见] {response_text[:200]}...")
        return {
            "messages": [result],
            "reflection_count": count,
        }


def agent_router(state: AgentState) -> Literal["tools", "reflect"]:
    """
    agent 之后去哪：
      — 有 tool_calls → tools（执行工具，再回 agent）
      — 无 tool_calls → reflect（进入反思检查）
    注意：和 Day 2 的 tools_condition 区别——这里不去 END，去 reflect
    """
    last_msg = state["messages"][-1]
    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
        return "tools"
    return "reflect"


def reflect_router(state: AgentState) -> Literal["retry", "done"]:
    """
    反思路由：检查最后一条消息是否含 FINAL。
    含 FINAL → done（结束）
    不含     → retry（回到 agent 重做）
    次数超限 → done
    """
    last_msg = state["messages"][-1]
    content = last_msg.content if hasattr(last_msg, "content") else ""
    if "FINAL" in content.upper():
        return "done"
    if state.get("reflection_count", 0) >= 3:
        return "done"
    return "retry"


def build_reflexion_graph():
    """构建 Reflexion 图"""
    graph = StateGraph(AgentState)

    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.add_node("reflect", reflect_node)

    graph.set_entry_point("agent")
    # 用自定义 agent_router 替代 tools_condition：
    # 有 tool_calls → tools → 回到 agent
    # 无 tool_calls → reflect（而不是直接 END）
    graph.add_conditional_edges("agent", agent_router, {
        "tools": "tools",
        "reflect": "reflect",
    })
    graph.add_edge("tools", "agent")

    # 关键边：reflect 后根据结果决定回 agent 还是结束
    graph.add_conditional_edges("reflect", reflect_router, {
        "retry": "agent",
        "done": END,
    })

    return graph.compile(checkpointer=MemorySaver())


# ============================================================
# 运行测试
# ============================================================

def run_graph(app, name: str, initial_messages, config):
    """通用图运行 + 逐步打印"""
    print(f"\n{'='*60}")
    print(f"[{name}]")
    print(f"{'='*60}")
    print("--- 逐步执行 ---")

    step = 0
    for event in app.stream({"messages": initial_messages, "plan": "", "reflection_count": 0}, config):
        step += 1
        node_name = list(event.keys())[0]
        node_data = event[node_name]
        msgs = node_data.get("messages", [])
        for msg in msgs:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tc = msg.tool_calls[0]
                print(f"  [Step {step} — {node_name}] 调工具: {tc['name']}({tc['args']})")
            elif hasattr(msg, "type") and msg.type == "tool":
                print(f"  [Step {step} — {node_name}] 工具结果: {msg.content[:80]}...")

    final_state = app.get_state(config)
    answer = final_state.values["messages"][-1].content
    print(f"\n[最终答案] {answer[:500]}...")
    return answer


if __name__ == "__main__":
    TASK = "请帮我查一下 Python、RAG、Agent 这三个概念，然后按名称长度从短到长排序，并告诉我哪个概念和 AI 最相关"

    # ============================
    # 测试 Plan-Execute
    # ============================
    pe_app = build_plan_execute_graph()
    pe_config = {"configurable": {"thread_id": "w5d3-plan-exec"}}
    pe_messages = [
        SystemMessage(content=PLAN_SYSTEM),
        HumanMessage(content=TASK),
    ]
    run_graph(pe_app, "Plan-then-Execute (LangGraph)", pe_messages, pe_config)

    # ============================
    # 测试 Reflexion
    # ============================
    refl_app = build_reflexion_graph()
    refl_config = {"configurable": {"thread_id": "w5d3-reflexion"}}
    refl_messages = [
        SystemMessage(content=REFLEXION_SYSTEM),
        HumanMessage(content=TASK),
    ]
    run_graph(refl_app, "Reflexion (LangGraph)", refl_messages, refl_config)

    # ============================
    # 三范式图拓扑对比
    # ============================
    print("\n" + "█" * 60)
    print("█  三张图的拓扑对比")
    print("█" * 60)
    print("""
    ReAct (Day 2):     agent ←→ tools          — 一个循环，agent 决定何时停

    Plan-Execute:      plan → execute ←→ tools  — 先出路线图，再走循环

    Reflexion:         agent ←→ tools
                         ↓
                       reflect → agent (重来)   — 循环外多一个"质量检查站"
                         ↓
                        END

    同一个 LangGraph，三张不同的图拓扑 = 三种不同的 Agent 范式。
    LangGraph 不是"ReAct 框架"，是"搭 Agent 图的工作台"。
    """)
