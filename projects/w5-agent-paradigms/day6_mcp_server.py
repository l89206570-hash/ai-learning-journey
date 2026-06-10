# W5 Day 6 — MCP Server：暴露知识库 + 计算工具
"""
MCP（Model Context Protocol）= Agent 的 USB 接口。

这个文件定义了一个 MCP Server，暴露 3 个工具：
  1. search_knowledge — 搜索技术概念
  2. calculate       — 数学计算
  3. list_concepts   — 列出所有已知概念

MCP Server 的核心职责：
  - 注册工具（tool name + description + parameters schema）
  - 接收 JSON-RPC 请求
  - 执行工具并返回结果

运行方式（stdio transport）：
  python day6_mcp_server.py

和 Day 2 @tool 的本质区别：
  Day 2: @tool 装饰器 → LangChain 内部使用，同一个 Python 进程
  Day 5: Skill 封装   → 工具组织方式改进，但还是同进程
  Day 6: MCP Server   → 工具在独立进程运行，通过 stdio JSON-RPC 通信
                          客户端不需要 import 服务端代码
                          服务端可以用任何语言实现
"""

import sys
from mcp.server.fastmcp import FastMCP

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ============================================================
# 创建 MCP Server
# ============================================================
# FastMCP 是 MCP 1.x 的高层 API，自动处理：
#   - JSON-RPC 消息解析/序列化
#   - stdio transport（通过标准输入输出通信）
#   - 工具注册和发现（client 调用 list_tools() 时自动返回 schema）

mcp = FastMCP("知识检索 MCP Server")

# ============================================================
# 知识库（和 Day 2/5 一样的数据）
# ============================================================

KNOWLEDGE = {
    "Python": "Python 是 Guido van Rossum 于 1991 年发布的编程语言，以简洁易读著称。广泛应用于 AI 开发。",
    "RAG": "RAG（检索增强生成）是一种让 LLM 先检索外部知识再回答的 AI 技术，核心是减少幻觉、提供可溯源的答案。",
    "Agent": "AI Agent 是能自主使用工具、规划步骤、执行任务的智能体，是 2026 年 AI 应用开发最热门的方向。",
    "ChromaDB": "ChromaDB 是一个开源的向量数据库，用于存储和检索嵌入向量。",
    "Streamlit": "Streamlit 是一个 Python Web 框架，几行代码就能构建数据应用。",
    "LangGraph": "LangGraph 是一个状态图执行引擎，用于构建可暂停、可回溯的 Agent 工作流。",
    "MCP": "MCP（Model Context Protocol）是 Agent 工具连接标准协议，让不同工具通过统一接口对接。",
    "FastAPI": "FastAPI 是一个高性能 Python Web 框架，适合构建 API 服务。",
    "Docker": "Docker 是一个容器化平台，让应用和依赖打包成镜像，一键部署到任何环境。",
    "LangChain": "LangChain 是一个 LLM 应用开发框架，提供消息管理、工具封装、链式调用等能力。",
}

# ============================================================
# 注册工具
# ============================================================
# FastMCP 的 @mcp.tool() 装饰器 = 注册工具 + 自动生成 JSON Schema
# 和 Day 2 的 @tool 装饰器写法几乎一样，但背后是 JSON-RPC 协议而非直接函数调用


@mcp.tool()
def search_knowledge(query: str) -> str:
    """在知识库中模糊搜索技术概念。输入中文关键词，返回匹配的概念和说明。"""
    results = []
    for key, value in KNOWLEDGE.items():
        if query.lower() in key.lower() or key.lower() in query.lower():
            results.append(f"【{key}】{value}")
    if results:
        return "\n\n".join(results)
    return f"未找到与「{query}」相关的知识。已知概念：{', '.join(KNOWLEDGE.keys())}"


@mcp.tool()
def calculate(expression: str) -> str:
    """安全计算数学表达式。支持 + - * / 和 abs/round/min/max/sum/pow 函数。"""
    allowed = {"__builtins__": {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "int": int, "float": float, "len": len,
    }}
    try:
        result = eval(expression, allowed)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算出错：{e}"


@mcp.tool()
def list_concepts() -> str:
    """列出知识库中所有已知的技术概念名称。不返回详细说明，只返回概念列表。"""
    concepts = list(KNOWLEDGE.keys())
    return f"知识库包含 {len(concepts)} 个概念：{', '.join(concepts)}"


# ============================================================
# 启动 Server
# ============================================================
# mcp.run() 会自动：
#   1. 监听 stdin（标准输入）
#   2. 解析 JSON-RPC 请求
#   3. 路由到对应的工具函数
#   4. 把结果序列化为 JSON-RPC 响应写到 stdout

if __name__ == "__main__":
    print("MCP Server 启动中...", file=sys.stderr)  # stderr 不会干扰 stdio transport
    mcp.run()
