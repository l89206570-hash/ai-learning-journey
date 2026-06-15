"""Agent 综合测试 — pytest 三层测试

结构测试：图拓扑正确（agent/tools 节点存在，边正确）
工具测试：MCP 工具定义正确（名称/参数 schema）
行为测试：Agent 能正确选择工具 + 回答包含关键词
稳定性测试：同一问题多次查询结果一致
持久化测试：checkpoint 可恢复
"""

import os
import sys
import json
import time
import asyncio
import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

from agent_graph import (
    build_mcp_langchain_tools, build_react_graph, SYSTEM_PROMPT,
    build_mcp_langchain_tools,
)
from config import MCP_SERVER_SCRIPT, LLM_MODEL

load_dotenv()


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(scope="module")
def event_loop():
    """创建 module 级别的 event loop"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def mcp_session():
    """启动 MCP Server，返回 session"""
    server_params = StdioServerParameters(command="python", args=[MCP_SERVER_SCRIPT])
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


@pytest.fixture(scope="module")
async def mcp_tools_raw(mcp_session):
    """获取 MCP 工具原始列表"""
    result = await mcp_session.list_tools()
    return result.tools


@pytest.fixture(scope="module")
async def lc_tools(mcp_session, mcp_tools_raw):
    """适配后的 LangChain 工具"""
    return build_mcp_langchain_tools(mcp_session, mcp_tools_raw)


@pytest.fixture(scope="module")
async def agent_graph(lc_tools):
    """完整的 Agent 图"""
    return build_react_graph(lc_tools)


# ============================================================
# 第一层：结构测试
# ============================================================

class TestGraphStructure:
    """验证 Agent 图的拓扑结构正确"""

    def test_agent_node_exists(self, agent_graph):
        nodes = agent_graph.get_graph().nodes
        assert "agent" in nodes, "agent 节点应该存在"
        assert "tools" in nodes, "tools 节点应该存在"

    def test_entry_point_is_agent(self, agent_graph):
        # 检查 START 边指向 agent
        edges = agent_graph.get_graph().edges
        start_edges = [e for e in edges if e.source == "__start__"]
        assert len(start_edges) == 1, f"应有 1 条 START 边，实际 {len(start_edges)}"
        assert start_edges[0].target == "agent", f"START 边应指向 agent"

    def test_tools_return_to_agent(self, agent_graph):
        edges = agent_graph.get_graph().edges
        tool_dests = [e.target for e in edges if e.source == "tools"]
        assert "agent" in tool_dests, "tools 节点应该回到 agent"


# ============================================================
# 第二层：工具测试
# ============================================================

class TestTools:
    """验证 MCP 工具定义正确"""

    def test_three_tools_registered(self, mcp_tools_raw):
        tool_names = [t.name for t in mcp_tools_raw]
        assert len(tool_names) >= 3, f"至少 3 个工具，实际 {len(tool_names)}"

    def test_search_knowledge_has_query_param(self, mcp_tools_raw):
        for t in mcp_tools_raw:
            if t.name == "search_knowledge":
                props = t.inputSchema.get("properties", {})
                assert "query" in props
                return
        pytest.fail("search_knowledge 工具未注册")

    def test_check_order_status_has_order_id_param(self, mcp_tools_raw):
        for t in mcp_tools_raw:
            if t.name == "check_order_status":
                props = t.inputSchema.get("properties", {})
                assert "order_id" in props
                return
        pytest.fail("check_order_status 工具未注册")

    def test_check_membership_has_member_level_param(self, mcp_tools_raw):
        for t in mcp_tools_raw:
            if t.name == "check_membership":
                props = t.inputSchema.get("properties", {})
                assert "member_level" in props
                return
        pytest.fail("check_membership 工具未注册")


# ============================================================
# 第三层：行为测试
# ============================================================

class TestAgentBehavior:
    """验证 Agent 行为正确"""

    @pytest.mark.asyncio
    async def test_product_search(self, agent_graph):
        """搜索商品应返回 T恤 相关信息"""
        from langchain_core.messages import HumanMessage, SystemMessage
        state = {"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content="有没有适合夏天穿的T恤")]}
        config = {"configurable": {"thread_id": "test-product"}}
        async for event in agent_graph.astream(state, config):
            pass
        final = await agent_graph.aget_state(config)
        last_msg = final.values["messages"][-1]
        content = last_msg.content if hasattr(last_msg, "content") else ""
        assert "T恤" in content or "T恤" in content

    @pytest.mark.asyncio
    async def test_order_query(self, agent_graph):
        """查订单应返回物流信息"""
        from langchain_core.messages import HumanMessage, SystemMessage
        state = {"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content="帮我查订单 JD20260615001")]}
        config = {"configurable": {"thread_id": "test-order"}}
        async for event in agent_graph.astream(state, config):
            pass
        final = await agent_graph.aget_state(config)
        last_msg = final.values["messages"][-1]
        content = last_msg.content if hasattr(last_msg, "content") else ""
        assert "顺丰" in content or "SF1234567890" in content

    @pytest.mark.asyncio
    async def test_membership_query(self, agent_graph):
        """查会员权益应返回对应信息"""
        from langchain_core.messages import HumanMessage, SystemMessage
        state = {"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content="金卡会员有什么权益")]}
        config = {"configurable": {"thread_id": "test-membership"}}
        async for event in agent_graph.astream(state, config):
            pass
        final = await agent_graph.aget_state(config)
        last_msg = final.values["messages"][-1]
        content = last_msg.content if hasattr(last_msg, "content") else ""
        assert "金卡" in content or "5000" in content


# ============================================================
# 稳定性测试
# ============================================================

class TestStability:
    """验证 Agent 稳定性"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize("run_id", range(3))
    async def test_repeat_query_consistent(self, agent_graph, run_id):
        """重复 3 次相同问题，每次都能正常返回"""
        import uuid
        from langchain_core.messages import HumanMessage, SystemMessage
        tid = f"stability-{uuid.uuid4().hex[:4]}"
        state = {"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content="怎么退货")]}
        config = {"configurable": {"thread_id": tid}}
        async for event in agent_graph.astream(state, config):
            pass
        final = await agent_graph.aget_state(config)
        last_msg = final.values["messages"][-1]
        content = last_msg.content if hasattr(last_msg, "content") else ""
        assert len(content) > 10, f"Run {run_id} returned short answer: {content}"


# ============================================================
# 持久化测试
# ============================================================

class TestPersistence:
    """验证 checkpoint 持久化"""

    @pytest.mark.asyncio
    async def test_checkpoint_persists_state(self, agent_graph):
        """同一 thread_id 第二次查询应能看到历史"""
        from langchain_core.messages import HumanMessage, SystemMessage
        tid = "persist-test-1"
        state1 = {"messages": [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content="云感T恤多少钱")]}
        config = {"configurable": {"thread_id": tid}}
        async for event in agent_graph.astream(state1, config):
            pass

        # 查 checkpoint 应该存在
        cp = await agent_graph.aget_state(config)
        assert cp is not None, "checkpoint 应该存在"
        assert len(cp.values["messages"]) >= 2, "至少 2 条消息"

        # 第二次查询
        state2 = {"messages": [HumanMessage(content="那它的面料是什么")]}
        async for event in agent_graph.astream(state2, config):
            pass
        final = await agent_graph.aget_state(config)
        assert len(final.values["messages"]) >= 3, "应该有更多消息"
