# W5 Day 7 — MCP + LangGraph 集成：Agent 通过 MCP 协议调工具
"""
Day 2 的 LangGraph Agent：ToolNode([search_knowledge, calculate]) ← 本地 @tool 函数
Day 7 的 LangGraph Agent：ToolNode(mcp_tools)                   ← 通过 MCP 协议远程调用

架构对比：
  Day 2:  Agent → ToolNode → search_knowledge("RAG")  ← 直接 Python 函数调用
  Day 7:  Agent → ToolNode → MCPAdapter → MCP Client → MCP Server → search_knowledge("RAG")
           └── LangGraph 图 ──┘  └── 适配层 ──┘  └── JSON-RPC over stdio ──┘

核心差异：Day 7 的 ToolNode 用 async coroutine 的 StructuredTool，
         图用 ainvoke/astream 执行，全程在同一个 asyncio event loop 里，
         不需要 asyncio.run() 嵌套。
"""

import os
import sys
import json
import asyncio
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.messages import convert_to_openai_messages
from langchain_core.tools import StructuredTool
from langchain_core.utils.function_calling import convert_to_openai_function

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from openai import OpenAI

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

llm_client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


# ============================================================
# Part 1: MCP 工具 → LangChain async StructuredTool
# ============================================================

from pydantic import BaseModel, create_model


def build_mcp_langchain_tools(session: ClientSession, mcp_tools_raw) -> list:
    """
    把 MCP 工具转成 LangChain async StructuredTool。

    关键：用 coroutine 而非 func——工具函数是 async 的，
    全程在同一个 asyncio event loop 里执行，不需要 asyncio.run() 嵌套。
    用 create_model 动态生成 args_schema，给每个工具适配正确的参数签名。
    """
    lc_tools = []

    for mcp_tool in mcp_tools_raw:
        tool_name = mcp_tool.name
        tool_desc = mcp_tool.description or ""
        input_schema = getattr(mcp_tool, 'inputSchema', {}) or {}
        properties = input_schema.get('properties', {})
        param_names = list(properties.keys())

        # 动态创建 Pydantic model 作为 args_schema
        # 例如 search_knowledge → Input(query: str)
        if param_names:
            field_defs = {
                name: (str, None) for name in param_names
            }
            DynamicInput = create_model(f"{tool_name}_input", **field_defs)
        else:
            # 无参数工具（如 list_concepts）
            DynamicInput = create_model(f"{tool_name}_input")

        # 闭包捕获 session + tool_name + param_names
        async def _tool_fn(_name=tool_name, _params=param_names, **kwargs):
            call_args = {k: v for k, v in kwargs.items() if k in _params}
            result = await session.call_tool(_name, call_args)
            if result.content and len(result.content) > 0:
                return result.content[0].text
            return str(result)

        tool = StructuredTool.from_function(
            coroutine=_tool_fn,
            name=tool_name,
            description=tool_desc,
            args_schema=DynamicInput,
        )

        lc_tools.append(tool)
        print(f"  [适配] MCP 工具 '{tool_name}' → LangChain async StructuredTool")

    return lc_tools


# ============================================================
# Part 2: 构建 LangGraph ReAct Agent（和 Day 2 完全相同）
# ============================================================

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_react_graph(lc_tools: list):
    """
    构建 ReAct Agent 图。
    和 Day 2 唯一区别：
      - tools 来自 MCP 适配层（async StructuredTool）
      - 图用 ainvoke/astream（async），因为工具是 async 的
    """

    def call_model(state: AgentState):
        openai_tools = [
            {"type": "function", "function": convert_to_openai_function(t)}
            for t in lc_tools
        ]
        openai_messages = convert_to_openai_messages(state["messages"])

        response = llm_client.chat.completions.create(
            model="deepseek-chat",
            messages=openai_messages,
            tools=openai_tools,
        )
        msg = response.choices[0].message

        if msg.tool_calls:
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

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(lc_tools))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=MemorySaver())


# ============================================================
# Part 3: 运行（全程 async，用 astream）
# ============================================================

SYSTEM_PROMPT = """你是一个使用 ReAct 模式的 AI 助手。

规则：
1. 分析用户的问题，想清楚需要什么信息
2. 一次只调用一个工具，拿到结果再决定下一步
3. 当信息足够时，直接给出最终答案（不要再调工具）
4. 搜索知识库用中文关键词"""


async def run_agent_async(graph, user_query: str, thread_id: str):
    """用 astream 运行 LangGraph Agent（async 版本）。"""
    initial_state = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_query),
        ]
    }
    config = {"configurable": {"thread_id": thread_id}}

    print(f"用户: {user_query}\n")

    step = 0
    async for event in graph.astream(initial_state, config):
        step += 1
        node_name = list(event.keys())[0]
        node_data = event[node_name]
        msgs = node_data.get("messages", [])

        for msg in msgs:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tc = msg.tool_calls[0]
                print(f"  [Step {step}] Agent 请求工具: {tc['name']}({tc['args']})")
            elif hasattr(msg, "content") and msg.content:
                if hasattr(msg, "type") and msg.type == "tool":
                    short = msg.content[:80].replace("\n", " ")
                    print(f"  [Step {step}] 工具返回: {short}...")
                elif hasattr(msg, "type") and msg.type == "ai":
                    print(f"  [Step {step}] Agent 回答")

    final_state = await graph.aget_state(config)
    last_msg = final_state.values["messages"][-1]
    answer = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
    print(f"\n最终答案:\n{answer}\n")
    return answer


async def main():
    server_script = os.path.join(os.path.dirname(__file__), "day6_mcp_server.py")
    server_params = StdioServerParameters(command="python", args=[server_script])

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print(f"[MCP] 已连接 Server\n")

            # 发现 MCP 工具
            result = await session.list_tools()
            mcp_tools_raw = result.tools
            print(f"MCP Server 提供 {len(mcp_tools_raw)} 个工具：")
            for t in mcp_tools_raw:
                print(f"  • {t.name}")

            # 适配为 LangChain async 工具
            print("\n适配为 LangChain async 工具：")
            lc_tools = build_mcp_langchain_tools(session, mcp_tools_raw)

            # 建图
            graph = build_react_graph(lc_tools)

            # 测试 1: 多概念搜索 + 排序
            print("\n" + "=" * 60)
            print("Day 7: LangGraph + MCP — Agent 通过 MCP 协议调工具（async）")
            print("=" * 60 + "\n")

            task = "请帮我查一下 Python、RAG、MCP 这三个概念，然后按名称长度从短到长排序"
            await run_agent_async(graph, task, "w5d7-test-1")

            # 测试 2: 查不存在的概念，验证兜底
            task2 = "帮我查一下 Kubernetes 是什么"
            await run_agent_async(graph, task2, "w5d7-test-2")

    # 图中工具全部调完，对比
    print("=" * 60)
    print("Day 2 vs Day 7 — Agent 代码对比")
    print("=" * 60)
    print("""
    ┌────────────────────────────┬──────────────────────────────────┐
    │ Day 2（本地 @tool）          │ Day 7（MCP 远程工具）            │
    ├────────────────────────────┼──────────────────────────────────┤
    │ @tool                       │ MCP Server 进程（独立运行）      │
    │ def search_knowledge(...):  │   → MCP Client (stdio JSON-RPC) │
    │   直接查 KNOWLEDGE dict     │   → call_tool("search_...", {}) │
    ├────────────────────────────┼──────────────────────────────────┤
    │ TOOLS = [                   │ mcp_raw = await list_tools()     │
    │   search_knowledge,         │ lc = build_mcp_tools(...)        │
    │   calculate                 │                                  │
    │ ]                           │                                  │
    ├────────────────────────────┼──────────────────────────────────┤
    │ ToolNode(TOOLS)             │ ToolNode(lc_tools)               │
    │   → 同步函数调用            │   → async coroutine              │
    │   → graph.stream()          │   → graph.astream()              │
    ├────────────────────────────┼──────────────────────────────────┤
    │ 图拓扑: agent ↔ tools       │ 图拓扑: agent ↔ tools            │
    │  完全相同                   │  完全相同                        │
    └────────────────────────────┴──────────────────────────────────┘

    核心认知：
    1. LangGraph 图结构（agent ↔ tools）完全不变
    2. 变的只是：
       - 工具来源：本地 import → MCP 远程进程
       - 执行方式：stream() → astream()（因为工具是 async coroutine）
    3. 适配层只做一件事：MCP async call_tool → async StructuredTool.coroutine
    4. 一个 Agent 可同时连多个 MCP Server，都是 list_tools + adapt
    """)


if __name__ == "__main__":
    asyncio.run(main())
