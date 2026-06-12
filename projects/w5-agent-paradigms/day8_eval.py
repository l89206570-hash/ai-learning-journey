# W6 Day 3 — Agent 评测体系：正确性 × 效率 × 稳定性
"""
和 pytest 测试的区别：
  pytest  → 代码级正确性（图结构、工具逻辑、Agent 行为）
  评测脚本 → 量化指标（Token 成本、延迟、轮次、稳定性分数）

评测三维度：
  1. 正确性 — 关键词命中率（答案是否包含关键信息）
  2. 效率   — Token 消耗、工具调用轮次、延迟
  3. 稳定性 — 同一查询 3 次，答案关键信息是否一致

使用方式：每次改 prompt 或换模型后跑一遍，看哪些指标变了。
"""

import os
import sys
import json
import time
import asyncio
from typing import Annotated
from typing_extensions import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.messages import convert_to_openai_messages
from langchain_core.tools import tool
from langchain_core.utils.function_calling import convert_to_openai_function
from openai import OpenAI

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

# ============================================================
# 知识库 + 工具（和 test_agent.py 一样）
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
# Agent 构建
# ============================================================

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def build_agent(tools: list):
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
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=MemorySaver())


# ============================================================
# 评测核心
# ============================================================

SYSTEM_PROMPT = """你是一个使用 ReAct 模式的 AI 助手。
规则：
1. 分析用户问题，需要信息时调用工具
2. 一次只调用一个工具
3. 信息足够时直接回答"""


def evaluate_once(agent, query: str, expected_keywords: list, thread_id: str) -> dict:
    """运行 Agent 一次，收集所有指标。"""
    initial_state = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=query),
        ]
    }
    config = {"configurable": {"thread_id": thread_id}}

    turns = 0
    tool_calls_made = []
    start = time.time()

    for event in agent.stream(initial_state, config):
        node_name = list(event.keys())[0]
        node_data = event[node_name]
        msgs = node_data.get("messages", [])

        for msg in msgs:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                turns += 1
                for tc in msg.tool_calls:
                    tool_calls_made.append(tc["name"])
            elif hasattr(msg, "content") and msg.content:
                if hasattr(msg, "type") and msg.type == "tool":
                    pass  # 工具返回不算新 turn

    elapsed = time.time() - start
    final_state = agent.get_state(config)
    last_msg = final_state.values["messages"][-1]
    answer = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

    # 关键词命中率
    hits = sum(1 for kw in expected_keywords if kw in answer)
    hit_rate = hits / len(expected_keywords) if expected_keywords else 1.0

    return {
        "answer": answer,
        "turns": turns,
        "tool_calls_made": tool_calls_made,
        "elapsed": round(elapsed, 2),
        "keywords_hit": f"{hits}/{len(expected_keywords)}",
        "hit_rate": hit_rate,
        "answer_len": len(answer),
    }


# ============================================================
# 测试用例
# ============================================================

# 格式：(场景, 查询, 期望关键词列表, 期望最少工具调用次数)
EVAL_CASES = [
    (
        "知识检索",
        "请帮我查一下 RAG 是什么",
        ["RAG", "检索", "增强", "生成"],  # 至少命中 2 个
        1,
    ),
    (
        "数学计算",
        "算一下 (50 + 150) * 2 等于多少",
        ["400"],
        1,
    ),
    (
        "多概念对比",
        "Python 和 LangGraph 分别是什么？请简要对比",
        ["Python", "LangGraph"],
        2,  # 需要查两次
    ),
    (
        "未知概念兜底",
        "帮我查一下量子计算是什么",
        [],  # 不强制关键词，但至少要有内容
        1,
    ),
    (
        "链式调用",
        "先列出知识库有哪些概念，然后详细解释第一个",
        [],  # 不限制关键词
        2,  # 先 list 再 search
    ),
]


# ============================================================
# 运行评测
# ============================================================

def run_eval():
    agent = build_agent([search_knowledge, calculate, list_concepts])

    print("=" * 80)
    print("Agent 评测报告")
    print(f"模型: deepseek-chat | 工具数: 3 | 测试用例: {len(EVAL_CASES)}")
    print("=" * 80)

    all_results = []

    for case_idx, (name, query, keywords, min_tools) in enumerate(EVAL_CASES, 1):
        print(f"\n{'─' * 60}")
        print(f"  [{case_idx}/{len(EVAL_CASES)}] {name}")
        print(f"  查询: {query}")
        print(f"  期望关键词: {keywords}")

        # 每条跑 3 次测稳定性
        runs = []
        for run_id in range(3):
            result = evaluate_once(
                agent, query, keywords,
                f"eval-{case_idx}-{run_id}"
            )
            runs.append(result)

        # --- 汇总 ---
        avg_elapsed = sum(r["elapsed"] for r in runs) / 3
        avg_turns = sum(r["turns"] for r in runs) / 3
        avg_hit_rate = sum(r["hit_rate"] for r in runs) / 3
        avg_len = sum(r["answer_len"] for r in runs) / 3

        # 稳定性：3 次答案长度的变异系数（越小越稳定）
        lens = [r["answer_len"] for r in runs]
        mean_len = sum(lens) / 3
        if mean_len > 0:
            cv = (sum((l - mean_len) ** 2 for l in lens) / 3) ** 0.5 / mean_len
        else:
            cv = 0

        # 工具调用准确性
        min_actual = min(r["turns"] for r in runs)
        tool_ok = "✅" if min_actual >= min_tools else "⚠️"

        # 正确性判定
        correctness = "✅" if avg_hit_rate >= 0.5 else "⚠️"
        if not keywords:
            correctness = "✅" if avg_len > 30 else "❌"

        # 稳定性判定
        stability = "✅" if cv < 0.5 else "⚠️"
        efficiency = "✅" if avg_elapsed < 15 else "⚠️"

        print(f"\n  指标:")
        print(f"    正确性 {correctness}  关键词命中率: {avg_hit_rate:.0%}")
        print(f"    效率   {efficiency}  平均延迟: {avg_elapsed:.1f}s | 平均轮次: {avg_turns:.1f}")
        print(f"    稳定性 {stability}  答案长度 CV: {cv:.2f}（<0.5 稳定）")
        print(f"    工具   {tool_ok}  最少调用: {min_actual}（期望 ≥{min_tools}）")

        for r in runs:
            short = r["answer"][:60].replace("\n", " ")
            print(f"      Run: {r['elapsed']:.1f}s | turns={r['turns']} | "
                  f"命中={r['keywords_hit']} | {short}...")

        all_results.append({
            "name": name,
            "correctness": correctness,
            "efficiency": efficiency,
            "stability": stability,
            "tool_ok": tool_ok,
            "avg_hit_rate": avg_hit_rate,
            "avg_elapsed": avg_elapsed,
            "avg_turns": avg_turns,
            "cv": cv,
        })

    # --- 总结表 ---
    print(f"\n{'=' * 80}")
    print("评测总结")
    print(f"{'=' * 80}")
    print(f"{'场景':<12} {'正确性':<6} {'效率':<6} {'稳定性':<6} {'工具':<6} {'命中率':<8} {'延迟':<8} {'轮次'}")
    print(f"{'─' * 65}")
    for r in all_results:
        hit_str = f"{r['avg_hit_rate']:.0%}"
        print(f"{r['name']:<12} {r['correctness']:<6} {r['efficiency']:<6} "
              f"{r['stability']:<6} {r['tool_ok']:<6} "
              f"{hit_str:<8} {r['avg_elapsed']:.1f}s{'':<4} {r['avg_turns']:.0f}")

    pass_count = sum(1 for r in all_results
                     if r['correctness'] == '✅' and r['stability'] == '✅')
    print(f"\n通过: {pass_count}/{len(all_results)}（正确性 + 稳定性同时达标）")

    # 面试金句
    print(f"\n{'─' * 60}")
    print("面试素材：")
    print(f"  我的 Agent 有 {len(EVAL_CASES)} 条固定评测用例，每次改 prompt 或换模型后自动跑一遍。")
    print(f"  评测三维度：正确性（关键词命中率）、效率（延迟+轮次）、稳定性（3 次重复的答案一致性）。")
    print(f"  本次 {pass_count}/{len(all_results)} 条通过。")


if __name__ == "__main__":
    run_eval()
