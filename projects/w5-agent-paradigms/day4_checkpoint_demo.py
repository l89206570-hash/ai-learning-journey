# W5 Day 4 — Checkpoint 深入
"""
LangGraph Checkpoint 系统的三个关键能力：

1. SqliteSaver 持久化 — 脚本重启状态还在     （MemorySaver 重启就没了）
2. interrupt() 暂停审批 — 关键步骤等人点"确认" （手写 while 循环做不到暂停→恢复）
3. get_state() + update_state() 时间旅行  — 回到任意历史状态重新跑 （手写做不到）

核心认知：这就是 LangGraph 和手写 Agent 循环的"代差"。

运行方式：
  python day4_checkpoint_demo.py          # 跑全部 3 个 Section
  python day4_checkpoint_demo.py 1        # 只看 SqliteSaver
  python day4_checkpoint_demo.py 2        # 只看 interrupt
  python day4_checkpoint_demo.py 3        # 只看时间旅行
"""

import os, json, sys, sqlite3
from typing import Annotated, Literal
from typing_extensions import TypedDict
from dotenv import load_dotenv
from openai import OpenAI

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages, RemoveMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import interrupt, Command
from langchain_core.messages import (
    HumanMessage, AIMessage, SystemMessage, ToolMessage, convert_to_openai_messages
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
# 共享工具 & 基础设施
# ============================================================

KNOWLEDGE = {
    "Python": "Python 是 Guido van Rossum 于 1991 年发布的编程语言，以简洁易读著称。广泛应用于 AI 开发。",
    "RAG": "RAG（检索增强生成）让 LLM 先检索外部知识再回答，减少幻觉、提供可溯源答案。",
    "Agent": "AI Agent 是能自主使用工具、规划步骤、执行任务的智能体，2026 最热方向。",
    "ChromaDB": "ChromaDB 是开源向量数据库，用于存储和检索嵌入向量。",
    "LangGraph": "LangGraph 是 LangChain 的 Agent 编排框架，用有向图定义 Agent 工作流。",
}


@tool
def search_knowledge(query: str):
    """在知识库中模糊搜索概念"""
    results = []
    for key, value in KNOWLEDGE.items():
        if key.lower() in query.lower() or query.lower() in key.lower():
            results.append(f"【{key}】{value}")
    return "\n\n".join(results) if results else f"未找到「{query}」相关知识。"


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


@tool
def dangerous_operation(action: str):
    """执行危险操作（删除数据、发送群邮件等），需要人工审批"""
    return f"[已执行] {action}"


TOOLS = [search_knowledge, calculate, dangerous_operation]
OPENAI_TOOLS = [
    {"type": "function", "function": convert_to_openai_function(t)}
    for t in TOOLS
]


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    approval: str  # Section 2 interrupt demo 用


def _call_llm(messages, with_tools=True):
    """通用 LLM 调用"""
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


def agent_node(state: AgentState):
    """ReAct agent 节点"""
    result = _call_llm(state["messages"], with_tools=True)
    return {"messages": [result]}


def build_react_graph(checkpointer=None):
    """构建最简 ReAct 图"""
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    return graph.compile(checkpointer=checkpointer)


# ============================================================
# Section 1: SqliteSaver — 持久化，重启不丢
# ============================================================

def demo_1_sqlite():
    """演示 SqliteSaver 持久化：脚本重启后状态还在"""
    DB_PATH = os.path.join(os.path.dirname(__file__), "checkpoint.db")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    print("=" * 60)
    print("Section 1: SqliteSaver — 持久化")
    print("=" * 60)
    print("核心问题：MemorySaver 数据在内存里，脚本退出就没了。")
    print("         SqliteSaver 把 checkpoint 写进 SQLite，重启还在。\n")

    # ---- 第一次运行 ----
    print("--- 第一次运行（创建连接，跑一轮对话）---")
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    app = build_react_graph(SqliteSaver(conn))
    config = {"configurable": {"thread_id": "w5d4-demo1"}}

    result = app.invoke(
        {"messages": [HumanMessage(content="请帮我查一下 Python 这个概念")]},
        config,
    )
    last_msg = result["messages"][-1].content
    print(f"  AI: {last_msg[:120]}...")
    conn.close()
    print("  (conn.close() — 模拟脚本退出)\n")

    # ---- 模拟重启：新连接，同一个 DB ----
    print("--- '重启'后（新连接连同一个 DB，同一 thread_id）---")
    conn2 = sqlite3.connect(DB_PATH, check_same_thread=False)
    app2 = build_react_graph(SqliteSaver(conn2))
    config2 = {"configurable": {"thread_id": "w5d4-demo1"}}

    # 看看之前的状态还在不在
    state = app2.get_state(config2)
    msg_count = len(state.values.get("messages", [])) if state.values else 0
    print(f"  get_state → 历史消息数: {msg_count}  ✅ 重启后状态还在")

    # 继续对话（LLM 能看到之前的上下文）
    result2 = app2.invoke(
        {"messages": [HumanMessage(content="那 RAG 呢？")]},
        config2,
    )
    last_msg2 = result2["messages"][-1].content
    print(f"  AI: {last_msg2[:120]}...")
    conn2.close()

    # ---- 对比 MemorySaver ----
    print("\n--- 对比：MemorySaver（new 一个新实例 = 数据全丢）---")
    mem_app1 = build_react_graph(MemorySaver())
    mem_config = {"configurable": {"thread_id": "w5d4-demo1"}}
    mem_app1.invoke(
        {"messages": [HumanMessage(content="查一下 Python")]},
        mem_config,
    )
    # 新建一个 MemorySaver 实例 — 旧数据没了
    mem_app2 = build_react_graph(MemorySaver())
    state2 = mem_app2.get_state(mem_config)
    print(f"  new MemorySaver() 后 get_state → {state2.values}  ❌ 数据没了")

    print(f"\n  SqliteSaver: checkpoint 持久化在 {DB_PATH}")
    print(f"  MemorySaver: 数据在实例内存里，换实例就丢")

    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


# ============================================================
# Section 2: interrupt() — 关键步骤暂停，等人审批
# ============================================================

def build_interrupt_graph():
    """
    在 agent → tools 之间插入 approval 节点 + 路由。

    图结构：
      START → agent ──(有 tool_calls)──→ approval ──(批准)→ tools → agent
           │                                       ──(拒绝)→ rejected → agent
           └──(无 tool_calls)──→ END

    关键拆解：
      approval_node  = 节点函数，调用 interrupt() 暂停图，结果存 state.approval
      route_after_approval = 路由函数，读 state.approval 决定下一站
      → 节点负责"做事"，路由负责"选路"，不能混在一个函数里
    """
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(TOOLS))

    def approval_node(state: AgentState):
        """审批节点：调用 interrupt() 暂停，结果存到 state"""
        last_msg = state["messages"][-1]
        if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
            tc = last_msg.tool_calls[0]
            # interrupt() 暂停图执行，返回 Command(resume=...) 传进来的值
            answer = interrupt(
                f"[审批] Agent 要调用 {tc['name']}({tc['args']})\n"
                f"        输入 y 批准 / n 拒绝: "
            )
            result = str(answer).strip().lower()
            if result == "y":
                return {"approval": "y"}
            else:
                # 拒绝时：删掉带 tool_calls 的 AIMessage，换成纯文本消息
                # 否则 DeepSeek 会报错：tool_calls 后面必须有匹配的 tool messages
                return {
                    "approval": "n",
                    "messages": [
                        RemoveMessage(id=last_msg.id),
                        AIMessage(content=f"调 {tc['name']} 被用户拒绝，请换其他方法完成任务。"),
                    ],
                }
        return {"approval": "no_tool"}

    def route_after_approval(state: AgentState):
        """审批后路由：根据 state.approval 决定下一站"""
        result = state.get("approval", "")
        if result == "y":
            print(f"  ✅ 已批准 → 执行工具")
            return "tools"
        elif result == "no_tool":
            return END
        else:
            print(f"  ❌ 已拒绝 → Agent 重新决策")
            return "agent"  # 直接回 agent，approval_node 已经替换了消息

    graph.set_entry_point("agent")
    graph.add_node("approval", approval_node)

    graph.add_conditional_edges("agent", tools_condition, {
        "tools": "approval",  # agent 有 tool_calls → 先进审批
        END: END,
    })
    graph.add_conditional_edges("approval", route_after_approval, {
        "tools": "tools",
        "agent": "agent",
        END: END,
    })
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=MemorySaver())


def demo_2_interrupt():
    """演示 interrupt() 暂停审批"""
    print("\n" + "=" * 60)
    print("Section 2: interrupt() — 人机协作审批")
    print("=" * 60)
    print("核心问题：Agent 自己决定调危险操作 → 你敢让它直接调吗？")
    print("         interrupt() 在工具执行前暂停，等人点了'确认'再继续。\n")

    app = build_interrupt_graph()
    config = {"configurable": {"thread_id": "w5d4-demo2"}}

    TASK = "请先调用 dangerous_operation 发送一封主题为'测试'的群邮件，然后帮我查一下 Python。"

    print(f"任务: {TASK}\n")
    print("--- 开始执行（遇到工具调用会暂停等你审批）---")

    # 用循环处理多次 interrupt：Agent 每调一个工具，approval 节点就暂停一次
    # 第一次传初始消息，之后传 Command(resume=...) 恢复
    turn = 0
    current_input = {
        "messages": [
            SystemMessage(content="你是一个 AI 助手。当用户要求执行操作时，你必须先调用对应的工具函数。不要跳过工具直接回答。"),
            HumanMessage(content=TASK),
        ]
    }

    while True:
        turn += 1
        result = app.invoke(current_input, config)

        if "__interrupt__" in result:
            # interrupt() 被调用 → 图暂停，result 里有中断信息
            interrupt_info = result["__interrupt__"][0]
            print(f"\n  ⏸️  [第{turn}次暂停]")
            print(f"  提示: {interrupt_info.value}")
            user_decision = input("  👤 批准吗？(y/n): ").strip().lower()
            # Command(resume=...) 恢复，next loop 传给 app.invoke
            current_input = Command(resume=user_decision)
        else:
            # 图正常跑完
            last_msg = result["messages"][-1].content if result.get("messages") else "(无消息)"
            print(f"\n  ✅ 图执行完成（共 {turn} 次 invoke）")
            print(f"  最终回答: {last_msg[:400]}")
            break


# ============================================================
# Section 3: get_state() + update_state() — 时间旅行
# ============================================================

def demo_3_time_travel():
    """演示时间旅行：查看历史、从历史分叉"""
    print("\n" + "=" * 60)
    print("Section 3: get_state() + update_state() — 时间旅行")
    print("=" * 60)
    print("核心问题：Agent 跑完了，能回到第 2 步看看当时的状态吗？")
    print("         能从第 2 步分叉，选另一条路重新跑吗？")
    print("         → get_state() 查看，get_state_history() 浏览时间线")
    print("         → update_state() 修改历史 + fork 新分支\n")

    DB_PATH = os.path.join(os.path.dirname(__file__), "checkpoint.db")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    app = build_react_graph(SqliteSaver(conn))
    config = {"configurable": {"thread_id": "w5d4-demo3"}}

    # ---- 先跑一轮完整对话 ----
    print("--- 第一轮对话（正常跑）---")
    app.invoke(
        {"messages": [HumanMessage(content="帮我查 Python，然后计算 3+5")]},
        config,
    )

    # ---- 查看历史 checkpoint ----
    print("\n--- 查看所有 checkpoints（时间线）---")
    print("  (最新在前，最早在后)")
    checkpoints = []
    for cp in app.get_state_history(config):
        checkpoints.append(cp)
        step = cp.metadata.get("step", "?")
        source = cp.metadata.get("source", "?")
        msgs = cp.values.get("messages", [])
        last_content = ""
        for m in reversed(msgs):
            if hasattr(m, "content") and m.content:
                last_content = m.content[:80].replace("\n", " ")
                break
            elif hasattr(m, "type") and m.type == "tool":
                last_content = f"[工具] {m.content[:60]}"
                break
        print(f"  Step {step:>3} | source={source:>6} | {last_content}")
    print(f"  共 {len(checkpoints)} 个 checkpoint\n")

    # ---- 查看某个 checkpoint 的详细状态 ----
    print("--- get_state 查看 Step 2 的详细状态 ---")
    # checkpoint 是倒序的，step=2 是倒数第 3 个
    target_cp = None
    for cp in reversed(checkpoints):
        if cp.metadata.get("step") == 2:
            target_cp = cp
            break

    if target_cp and target_cp.values:
        msgs = target_cp.values["messages"]
        print(f"  Step 2 的消息（共 {len(msgs)} 条）：")
        for i, m in enumerate(msgs):
            if hasattr(m, "content") and m.content:
                print(f"    [{i}] {type(m).__name__}: {m.content[:80]}")
            elif hasattr(m, "type") and m.type == "tool":
                print(f"    [{i}] ToolMessage: {m.content[:80]}")
            elif hasattr(m, "tool_calls") and m.tool_calls:
                tc_names = [t["name"] for t in m.tool_calls]
                print(f"    [{i}] AIMessage: tool_calls={tc_names}")

    # ---- 时间旅行分叉 ----
    # 从 step 2 的 checkpoint fork 一个新分支（新 thread_id），
    # 假装"如果当时搜 Python 得到的是 1992 年"，看 Agent 怎么回答
    print("\n--- 时间旅行：从 Step 2 分叉（fork）新时间线 ---")
    print("  修改历史：把 Python 搜索结果改成 '1992 年发布'")
    print("  新 thread_id = w5d4-demo3-fork")

    fork_config = {"configurable": {"thread_id": "w5d4-demo3-fork"}}

    # 把 Step 2 的消息拷贝到新 thread，并修改第一个工具结果
    fork_msgs = list(msgs)
    first_tool = fork_msgs[2]  # 第一个工具结果
    fork_msgs[2] = ToolMessage(
        content="Python 是 Guido van Rossum 于 1992 年发布的编程语言。(被篡改的历史)",
        tool_call_id=first_tool.tool_call_id,
    )
    print(f"  原始: {first_tool.content[:60]}")
    print(f"  修改: {fork_msgs[2].content}")

    # 用 update_state 在新 thread 上写入被篡改的历史
    app.update_state(fork_config, values={"messages": fork_msgs})
    print("  ✅ update_state 完成 — 新分支已写入")

    # 从新分支继续跑
    print("\n--- 从新分支继续：问 Agent Python 是哪年发布的 ---")
    result = app.invoke(
        {"messages": [HumanMessage(content="根据你查到的信息，告诉我 Python 是哪年发布的")]},
        fork_config,
    )
    final = result["messages"][-1].content
    print(f"  AI 回答: {final[:300]}")

    if "1992" in final:
        print("\n  ✅ 时间旅行成功！Agent 用了被篡改的历史（1992 年）")
    else:
        print("\n  ⚠️ Agent 可能没用被篡改的历史")

    conn.close()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)


# ============================================================
# 核心认知总结
# ============================================================

def print_summary():
    print("\n" + "█" * 60)
    print("█  W5 Day 4 核心认知")
    print("█" * 60)
    print("""
    ┌──────────────────┬────────────────────┬──────────────────────┐
    │ 能力             │ 手写 Agent 循环     │ LangGraph Checkpoint │
    ├──────────────────┼────────────────────┼──────────────────────┤
    │ 状态持久化       │ ❌ 需手动序列化     │ ✅ SqliteSaver 自动   │
    │ 暂停等人审批     │ ❌ 做不到           │ ✅ interrupt() 原生   │
    │ 回到任意历史状态 │ ❌ 只能保存最终结果 │ ✅ get_state 任意回溯  │
    │ 修改历史后重跑   │ ❌ 需手动构造输入   │ ✅ update_state 分叉  │
    └──────────────────┴────────────────────┴──────────────────────┘

    这三个能力 = LangGraph 和手写的"代差"。
    手写 Agent 能做"调工具→看结果→再调"，但做不到"暂停→恢复"和"时间旅行"。
    这就是为什么生产环境用 LangGraph 而不是自己写 while True。
    """)

    print("""
    今天三个 API 的用途总结：

    SqliteSaver: 把 checkpoint 存到 SQLite 文件
      → 脚本重启 / 服务器重启 / 进程挂了 → 状态还在
      → 用法: SqliteSaver(sqlite3.connect("xxx.db"))

    interrupt("提示信息"): 在节点内暂停图执行
      → 等人调用 Command(resume=值) 后继续
      → 场景: 危险操作审批 / 关键决策点等人确认

    get_state(config) + update_state(config, values):
      → get_state: 查任意时刻的对话状态
      → get_state_history: 列出所有历史 checkpoint
      → update_state: 修改某个 checkpoint 的内容，创建分叉
      → 场景: 调试 / A/B 测试 / "如果当时选了另一个工具会怎样"
    """)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    section = sys.argv[1] if len(sys.argv) > 1 else "all"

    if section in ("all", "1"):
        demo_1_sqlite()
    if section in ("all", "2"):
        demo_2_interrupt()
    if section in ("all", "3"):
        demo_3_time_travel()
    if section in ("all", "1", "2", "3"):
        print_summary()
