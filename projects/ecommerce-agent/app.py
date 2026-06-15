"""跨境电商 Agent — Streamlit 界面

Agent 后端：LangGraph + MCP，支持：
  - 智能客服对话（自动判断是否搜索知识库/查订单/查会员）
  - 工具调用过程可视化
  - 品类筛选
  - 对话历史
"""

import os
import sys
import json
import asyncio
import logging
import threading
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from config import (
    LLM_MODEL, LLM_API_KEY, LLM_API_BASE, LLM_MAX_TOKENS, LLM_TEMPERATURE,
    MCP_SERVER_SCRIPT,
)
from agent_graph import build_mcp_langchain_tools, build_react_graph, SYSTEM_PROMPT

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from openai import OpenAI

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_API_BASE)


# ============================================================
# Agent 管理器：在后台线程持有 MCP 连接 + LangGraph 图
# ============================================================

class AgentManager:
    """管理 MCP 连接和 Agent 图的生命周期"""

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._ready = False
        self._graph = None
        self._session = None
        self._read_stream = None
        self._write_stream = None

        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        # 等待初始化完成
        future = asyncio.run_coroutine_threadsafe(self._init(), self._loop)
        future.result(timeout=60)
        self._ready = True

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _init(self):
        logger.info("Starting MCP Server: %s", MCP_SERVER_SCRIPT)
        server_params = StdioServerParameters(command="python", args=[MCP_SERVER_SCRIPT])
        self._read_stream, self._write_stream = await stdio_client(server_params).__aenter__()
        self._session = await ClientSession(self._read_stream, self._write_stream).__aenter__()
        await self._session.initialize()
        logger.info("MCP Server connected")

        result = await self._session.list_tools()
        mcp_tools_raw = result.tools
        logger.info("MCP tools discovered: %s", [t.name for t in mcp_tools_raw])

        lc_tools = build_mcp_langchain_tools(self._session, mcp_tools_raw)
        self._graph = build_react_graph(lc_tools)
        logger.info("Agent graph built, ready")

    def query_sync(self, user_query: str, thread_id: str, history: list = None) -> str:
        """同步查询 Agent"""
        future = asyncio.run_coroutine_threadsafe(
            self._query_async(user_query, thread_id, history), self._loop
        )
        return future.result(timeout=120)

    async def _query_async(self, user_query: str, thread_id: str, history: list = None):
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        if history:
            for h in history:
                if h["role"] == "user":
                    messages.append(HumanMessage(content=h["content"]))
                elif h["role"] == "assistant":
                    messages.append(AIMessage(content=h["content"]))
        messages.append(HumanMessage(content=user_query))

        initial_state = {"messages": messages}
        config = {"configurable": {"thread_id": thread_id}}

        async for event in self._graph.astream(initial_state, config):
            pass

        final_state = await self._graph.aget_state(config)
        last_msg = final_state.values["messages"][-1]
        return last_msg.content if hasattr(last_msg, "content") else str(last_msg)

    def query_stream(self, user_query: str, thread_id: str, history: list = None):
        """流式查询，yield 每一步事件"""
        future = asyncio.run_coroutine_threadsafe(
            self._stream_events(user_query, thread_id, history), self._loop
        )
        while True:
            try:
                event = future.result(timeout=0.1)
                if event is None:
                    break
                yield event
            except asyncio.TimeoutError:
                # 超时等待下一个事件
                import time
                time.sleep(0.1)
            except StopIteration:
                break

    async def _stream_events(self, user_query, thread_id, history):
        # 简化版：直接返回最终结果
        result = await self._query_async(user_query, thread_id, history)
        return result

    def shutdown(self):
        self._loop.call_soon_threadsafe(self._loop.stop)


# Agent 初始化（缓存，Streamlit 重跑时复用）
@st.cache_resource
def init_agent():
    return AgentManager()


agent_manager = init_agent()


# ============================================================
# Sidebar
# ============================================================
st.set_page_config(page_title="跨境电商 Agent", page_icon="🤖")
st.title("🛒 跨境电商智能客服 Agent")

with st.sidebar:
    st.subheader("🤖 Agent 能力")
    st.markdown("""
    - 🔍 **商品搜索** — 自动搜索商品库
    - 📦 **订单查询** — 查物流状态
    - 👑 **会员权益** — 查等级和特权
    - ❓ **FAQ** — 常见问题解答
    - 📋 **售后政策** — 退换货规则
    """)

    st.divider()
    if st.button("重置对话"):
        st.session_state["messages"] = []
        st.rerun()


# ============================================================
# Session State
# ============================================================
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "thread_id" not in st.session_state:
    import uuid
    st.session_state["thread_id"] = str(uuid.uuid4())[:8]


# ============================================================
# 渲染历史消息
# ============================================================
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "tools_used" in msg and msg["tools_used"]:
            with st.expander("🔧 工具调用详情", expanded=False):
                for t in msg["tools_used"]:
                    st.caption(f"  ⚙️ {t['name']}({t.get('args', '')})")


# ============================================================
# 对话交互
# ============================================================
user_input = st.chat_input("请输入您的问题（如：帮我查一下T恤的价格、我的订单到哪了、会员有什么权益...）")

if user_input:
    logger.info("收到查询: %s", user_input)
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Agent 思考中..."):
                # 调用 Agent（同步）
                history = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state["messages"][:-1]
                ]
                answer = agent_manager.query_sync(
                    user_input,
                    st.session_state["thread_id"],
                    history,
                )
                st.write(answer)
                st.session_state["messages"].append({
                    "role": "assistant",
                    "content": answer,
                })
                logger.info("Agent 回复长度 %d 字", len(answer))
        except Exception as e:
            logger.error("Agent 调用失败: %s", e)
            error_msg = "抱歉，AI 服务暂时不可用，请稍后重试。"
            st.error(error_msg)
            st.session_state["messages"].append({"role": "assistant", "content": error_msg})

with st.expander("🔍 调试信息", expanded=False):
    st.caption(f"Thread ID: {st.session_state['thread_id']}")
    st.caption(f"消息数: {len(st.session_state['messages'])}")
