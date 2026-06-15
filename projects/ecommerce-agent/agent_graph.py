"""LangGraph Agent — 通过 MCP 协议调用电商业务工具

架构：
  LangGraph ReAct Agent → MCP Adapter → MCP Server (stdio JSON-RPC)
  - agent 节点：LLM 决策 → 回复 或 调用工具
  - tools 节点：执行 MCP 工具（search_knowledge / check_order_status / check_membership）
  - checkpoint：SqliteSaver 持久化，支持暂停恢复
"""

import os
import sys
import json
import asyncio
import logging

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.messages import convert_to_openai_messages
from langchain_core.tools import StructuredTool
from langchain_core.utils.function_calling import convert_to_openai_function

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from openai import OpenAI
from pydantic import create_model

from config import (
    LLM_MODEL, LLM_API_KEY, LLM_API_BASE, LLM_MAX_TOKENS, LLM_TEMPERATURE,
    MCP_SERVER_SCRIPT,
)

load_dotenv()
logger = logging.getLogger(__name__)

llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_API_BASE)


# ============================================================
# MCP 适配层：MCP 工具 → LangChain async StructuredTool
# ============================================================

def build_mcp_langchain_tools(session: ClientSession, mcp_tools_raw) -> list:
    """把 MCP 工具转成 LangChain async StructuredTool"""
    lc_tools = []

    for mcp_tool in mcp_tools_raw:
        tool_name = mcp_tool.name
        tool_desc = mcp_tool.description or ""
        input_schema = getattr(mcp_tool, 'inputSchema', {}) or {}
        properties = input_schema.get('properties', {})
        param_names = list(properties.keys())

        if param_names:
            field_defs = {name: (str, None) for name in param_names}
            DynamicInput = create_model(f"{tool_name}_input", **field_defs)
        else:
            DynamicInput = create_model(f"{tool_name}_input")

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
        logger.info("  [适配] MCP 工具 '%s' → LangChain async StructuredTool", tool_name)

    return lc_tools


# ============================================================
# Agent State
# ============================================================

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# ============================================================
# 构建 ReAct 图
# ============================================================

SYSTEM_PROMPT = """你是一个电商客服 AI 助手，可以帮助用户：
1. 查询商品信息、FAQ、售后政策 → 用 search_knowledge 工具
2. 查询订单状态和物流 → 用 check_order_status 工具
3. 查询会员权益 → 用 check_membership 工具

规则：
- 分析用户问题，判断需要哪个工具或需要搜索知识库
- 一次只调用一个工具，拿到结果再决定下一步
- 信息足够时直接给出最终答案（不要再调工具）
- 回答要简洁友好，用中文"""


def build_react_graph(lc_tools: list):
    """构建 ReAct Agent 图。和 W5 Day 7 相同拓扑，工具来自 MCP"""

    def call_model(state: AgentState):
        openai_tools = [
            {"type": "function", "function": convert_to_openai_function(t)}
            for t in lc_tools
        ]
        openai_messages = convert_to_openai_messages(state["messages"])

        response = llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=openai_messages,
            tools=openai_tools,
            max_tokens=LLM_MAX_TOKENS,
            temperature=LLM_TEMPERATURE,
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
# 运行 Agent（供 CLI / Streamlit 调用）
# ============================================================

async def run_agent_async(graph, user_query: str, thread_id: str) -> str:
    """用 astream 运行 Agent，返回最终答案"""
    initial_state = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_query),
        ]
    }
    config = {"configurable": {"thread_id": thread_id}}

    async for event in graph.astream(initial_state, config):
        pass  # 流式推进到结束

    final_state = await graph.aget_state(config)
    last_msg = final_state.values["messages"][-1]
    return last_msg.content if hasattr(last_msg, "content") else str(last_msg)


# ============================================================
# CLI 测试入口
# ============================================================

async def main():
    """命令行测试 Agent"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    server_params = StdioServerParameters(command="python", args=[MCP_SERVER_SCRIPT])

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            print("[MCP] 已连接电商 MCP Server\n")

            result = await session.list_tools()
            mcp_tools_raw = result.tools
            print(f"MCP Server 提供 {len(mcp_tools_raw)} 个工具：")
            for t in mcp_tools_raw:
                print(f"  • {t.name}: {t.description}")

            lc_tools = build_mcp_langchain_tools(session, mcp_tools_raw)
            graph = build_react_graph(lc_tools)

            print("\n" + "=" * 60)
            print("跨境电商 Agent — LangGraph + MCP（async）")
            print("=" * 60 + "\n")

            # 测试 1: 商品搜索
            answer = await run_agent_async(graph, "我想买一件适合夏天穿的T恤，有什么推荐？", "test-1")
            print(f"Q: 我想买一件适合夏天穿的T恤\nA: {answer}\n")

            # 测试 2: 订单查询
            answer = await run_agent_async(graph, "帮我查一下订单 JD20260615001 到哪了", "test-2")
            print(f"Q: 查订单 JD20260615001\nA: {answer}\n")

            # 测试 3: 退换货 + 会员
            answer = await run_agent_async(graph, "我是金卡会员，买的衣服不合身想退货，运费谁出？", "test-3")
            print(f"Q: 金卡会员退货\nA: {answer}\n")


if __name__ == "__main__":
    asyncio.run(main())
