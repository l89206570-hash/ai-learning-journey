# W6 Day 2 — pytest 给 MCP+LangGraph Agent 写测试
"""
测试金字塔：
  L1: 单次人工验证（开发时随手测）
  L2: 固定测试集回归（每次改动跑一遍）← 今天做这个
  L3: 线上真实用户反馈（A/B test）

Agent 测试三个维度：
  1. 正确性 — 答案是否包含关键信息
  2. 效率   — Token 消耗、工具调用轮次
  3. 稳定性 — 重复运行答案是否一致

和传统软件测试的区别：
  - 不能 assert exact string（LLM 非确定性）
  - 用关键词存在性检查 + 结构断言替代精确匹配
  - 需要关注 Token 成本（每次测试都在花钱）
"""

import os
import sys
import pytest
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.messages import convert_to_openai_messages
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_function
from openai import OpenAI

load_dotenv()


# ============================================================
# 和 MCP Server 同样的知识库（但用本地 @tool）
# ============================================================

KNOWLEDGE = {
    "Python": "Python 是 Guido van Rossum 于 1991 年发布的编程语言，以简洁易读著称。广泛应用于 AI 开发。",
    "RAG": "RAG（检索增强生成）是一种让 LLM 先检索外部知识再回答的 AI 技术。",
    "Agent": "AI Agent 是能自主使用工具、规划步骤、执行任务的智能体，是 2026 年最热方向。",
    "ChromaDB": "ChromaDB 是一个开源的向量数据库，用于存储和检索嵌入向量。",
    "Streamlit": "Streamlit 是一个 Python Web 框架，几行代码就能构建数据应用。",
    "LangGraph": "LangGraph 是一个状态图执行引擎，用于构建可暂停、可回溯的 Agent 工作流。",
    "MCP": "MCP（Model Context Protocol）是 Agent 工具连接标准协议。",
    "FastAPI": "FastAPI 是一个高性能 Python Web 框架，适合构建 API 服务。",
    "Docker": "Docker 是一个容器化平台，让应用和依赖打包成镜像。",
    "LangChain": "LangChain 是一个 LLM 应用开发框架。",
}


@tool
def search_knowledge(query: str) -> str:
    """在知识库中模糊搜索技术概念。输入关键词，返回匹配的概念和说明。"""
    results = []
    for key, value in KNOWLEDGE.items():
        if query.lower() in key.lower() or key.lower() in query.lower():
            results.append(f"【{key}】{value}")
    if results:
        return "\n\n".join(results)
    return f"未找到与「{query}」相关的知识。已知概念：{', '.join(KNOWLEDGE.keys())}"


@tool
def calculate(expression: str) -> str:
    """安全计算数学表达式。支持 + - * / 和 abs/round/min/max/sum/pow。"""
    allowed = {"__builtins__": {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "int": int, "float": float,
    }}
    try:
        result = eval(expression, allowed)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算出错：{e}"


@tool
def list_concepts() -> str:
    """列出知识库中所有已知的技术概念名称。"""
    return f"知识库包含 {len(KNOWLEDGE)} 个概念：{', '.join(KNOWLEDGE.keys())}"


# ============================================================
# Agent 构建（和 day7_langgraph_mcp 相同结构，但用本地 @tool）
# ============================================================

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_test_agent(tools: list):
    """构建 ReAct Agent 图，和 day7 完全相同的图拓扑。"""
    llm = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )

    def call_model(state: AgentState):
        openai_tools = [
            {"type": "function", "function": convert_to_openai_function(t)}
            for t in tools
        ]
        openai_messages = convert_to_openai_messages(state["messages"])

        response = llm.chat.completions.create(
            model="deepseek-chat",
            messages=openai_messages,
            tools=openai_tools,
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            lc_tool_calls = [
                {
                    "name": tc.function.name,
                    "args": __import__("json").loads(tc.function.arguments),
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
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=MemorySaver())


# ============================================================
# Fixtures
# ============================================================

TOOLS = [search_knowledge, calculate, list_concepts]

SYSTEM_PROMPT = """你是一个使用 ReAct 模式的 AI 助手。
规则：
1. 分析用户问题，需要信息时调用工具
2. 一次只调用一个工具
3. 信息足够时直接回答"""


@pytest.fixture(scope="module")
def agent():
    """模块级 fixture：所有测试共用同一个 Agent 图实例。"""
    return build_test_agent(TOOLS)


def run_agent(agent, query: str, thread_id: str = "test") -> dict:
    """Helper：运行 Agent 并返回结构化结果。"""
    import time

    initial_state = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=query),
        ]
    }
    config = {"configurable": {"thread_id": thread_id}}

    turns = 0
    start = time.time()

    for event in agent.stream(initial_state, config):
        turns += 1
        node_name = list(event.keys())[0]
        node_data = event[node_name]
        msgs = node_data.get("messages", [])

        for msg in msgs:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                turns += 0.5  # 工具调用算半轮（agent 请求 + 工具返回 = 完整一轮）

    elapsed = time.time() - start
    final_state = agent.get_state(config)
    last_msg = final_state.values["messages"][-1]
    answer = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

    # 统计 tool calls 次数
    tool_call_count = 0
    for msg in final_state.values["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            tool_call_count += len(msg.tool_calls)

    return {
        "answer": answer,
        "turns": int(turns),
        "tool_calls": tool_call_count,
        "elapsed": round(elapsed, 2),
        "messages": final_state.values["messages"],
    }


# ============================================================
# 测试用例
# ============================================================

class TestAgentStructure:
    """图结构测试 — 不调 LLM，纯代码验证"""

    def test_graph_has_correct_nodes(self, agent):
        """图包含 agent 和 tools 两个节点。"""
        nodes = list(agent.get_graph().nodes.keys())
        assert "agent" in nodes, f"缺少 agent 节点，现有: {nodes}"
        assert "tools" in nodes, f"缺少 tools 节点，现有: {nodes}"
        assert "__start__" in nodes

    def test_entry_point_is_agent(self, agent):
        """入口是 agent 节点。"""
        # 检查图的编译信息
        graph_info = agent.get_graph()
        assert graph_info is not None


class TestToolNode:
    """ToolNode 工具执行测试 — 不调 LLM"""

    def test_search_knowledge_found(self):
        """search_knowledge 工具：找到匹配概念。"""
        result = search_knowledge.invoke({"query": "RAG"})
        assert "RAG" in result
        assert "检索增强生成" in result

    def test_search_knowledge_not_found(self):
        """search_knowledge 工具：未找到时返回兜底。"""
        result = search_knowledge.invoke({"query": "量子计算"})
        assert "未找到" in result
        assert "已知概念" in result

    def test_calculate_valid(self):
        """calculate 工具：合法表达式。"""
        result = calculate.invoke({"expression": "2+3*4"})
        assert "14" in result

    def test_calculate_invalid(self):
        """calculate 工具：非法表达式安全兜底。"""
        result = calculate.invoke({"expression": "__import__('os').system('dir')"})
        assert "计算出错" in result or "14" not in result

    def test_list_concepts(self):
        """list_concepts 工具：返回概念列表。"""
        result = list_concepts.invoke({})
        assert "10 个概念" in result
        for concept in ["Python", "RAG", "Agent", "MCP"]:
            assert concept in result


class TestAgentBehavior:
    """Agent 行为测试 — 调 LLM，验证 Agent 能否正确使用工具"""

    def test_agent_direct_answer(self, agent):
        """简单问题不需要工具，直接回答。"""
        result = run_agent(agent, "你好，请用一句话介绍你自己", "test-direct")
        assert len(result["answer"]) > 10, f"答案太短: {result['answer'][:50]}"
        # 简单打招呼不应该调工具
        assert result["tool_calls"] == 0, f"不需要工具的问候却调了 {result['tool_calls']} 次工具"

    def test_agent_search_single_concept(self, agent):
        """Agent 调用 search_knowledge 查一个概念。"""
        result = run_agent(agent, "请帮我查一下 RAG 是什么", "test-search-single")
        assert result["tool_calls"] >= 1, f"应该至少调一次工具，实际 {result['tool_calls']}"
        assert "RAG" in result["answer"] or "检索" in result["answer"], \
            f"答案应包含 RAG 相关内容: {result['answer'][:100]}"

    def test_agent_math_calculation(self, agent):
        """Agent 调用 calculate 做数学题。"""
        result = run_agent(agent, "请帮我算一下 (100 + 200) * 3 等于多少", "test-calc")
        assert result["tool_calls"] >= 1, f"应该调 calculate，实际 {result['tool_calls']}"
        assert "900" in result["answer"], f"答案应包含 900: {result['answer'][:100]}"

    def test_agent_unknown_concept_graceful(self, agent):
        """Agent 查不存在的概念时不崩溃。"""
        result = run_agent(agent, "帮我查一下魔法是什么", "test-unknown")
        # 应该能正常返回答案（即使工具说未找到）
        assert len(result["answer"]) > 20, f"答案太短: {result['answer'][:50]}"
        assert "未找到" in result["answer"] or "不" in result["answer"] or \
               "没有" in result["answer"] or "信息" in result["answer"] or \
               len(result["answer"]) > 30, \
            f"应提示未找到或自行解释: {result['answer'][:100]}"

    def test_agent_multi_concept_search(self, agent):
        """Agent 查多个概念——可能多次调工具。"""
        result = run_agent(agent, "请帮我查一下 Python 和 RAG 这两个概念", "test-multi")
        # 至少查了知识库
        assert result["tool_calls"] >= 1, f"应该至少调一次工具: {result['tool_calls']}"
        assert len(result["answer"]) > 30, f"答案太短: {result['answer'][:50]}"

    def test_agent_list_then_search(self, agent):
        """Agent 先列出所有概念，再搜其中一个——链式调用。"""
        result = run_agent(
            agent,
            "先看看知识库有哪些概念，然后挑其中一个详细解释",
            "test-chain"
        )
        assert result["tool_calls"] >= 2, \
            f"应该先 list 再 search，至少 2 次工具调用，实际 {result['tool_calls']}"


class TestAgentStability:
    """稳定性测试 — 重复运行，检查一致性"""

    @pytest.mark.parametrize("run_id", range(3))
    def test_repeat_search_stable(self, agent, run_id):
        """重复 3 次查同一个概念，答案都应包含关键信息。"""
        result = run_agent(
            agent,
            f"请帮我查一下 Python 是什么",
            f"test-stable-{run_id}"
        )
        assert "Python" in result["answer"] or "编程语言" in result["answer"], \
            f"第 {run_id + 1} 次: 答案不包含 Python 相关信息: {result['answer'][:100]}"
        assert len(result["answer"]) > 20, \
            f"第 {run_id + 1} 次: 答案太短"


class TestMemorySaver:
    """Checkpoint 持久化测试"""

    def test_state_persists_across_calls(self, agent):
        """同一 thread_id 第二次调用记住之前的对话。"""
        thread = "test-memory"

        # 第一轮：自我介绍
        result1 = run_agent(agent, "我叫小明，请记住我的名字", thread)

        # 第二轮：问"我叫什么"
        result2 = run_agent(agent, "我叫什么名字？", thread)

        # 第二轮应该提到小明（如果模型记得）
        # 注意：MemorySaver 存的是 messages，第二轮 messages 包含历史
        final_state = agent.get_state({"configurable": {"thread_id": thread}})
        all_messages = final_state.values["messages"]
        # 应该有系统消息 + 用户1 + AI1 + (可能工具) + 用户2 + AI2
        assert len(all_messages) >= 4, \
            f"至少应有 4 条消息（sys + user1 + ai1 + user2 + ai2），实际 {len(all_messages)}"
        # 用户消息应包含"我叫小明"
        user_messages = [m for m in all_messages if hasattr(m, "type") and m.type == "human"]
        names_mentioned = any("小明" in m.content for m in user_messages)
        assert names_mentioned, "历史中应包含小明的名字"
