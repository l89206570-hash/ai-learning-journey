# W5 Day 6 — MCP Client：连接 Server，发现并调用工具
"""
这个文件扮演"Agent"角色——通过 MCP 协议连接 Server，发现工具、调用工具。

和 Day 2/5 的本质区别：
  Day 2: tools = [search_knowledge, calculate]  ← import 后直接调函数
  Day 5: knowledge_skill.tool_map["search_knowledge"](query)  ← 同进程调用
  Day 6: await client.call_tool("search_knowledge", {"query": "RAG"})  ← JSON-RPC 跨进程

MCP 的价值：
  1. 工具提供者（Server）和工具使用者（Agent）解耦
  2. Server 可以用任何语言写（Python/TS/Go/Rust），Client 只认 JSON-RPC
  3. 一个 Agent 可以同时连多个 MCP Server（比如：知识库 Server + 数据库 Server + API Server）
  4. 工具发现：Client 不需要提前知道有哪些工具，list_tools() 动态发现

架构图：
  ┌──────────────┐    stdio JSON-RPC    ┌──────────────────┐
  │  MCP Client  │ ◄──────────────────► │   MCP Server     │
  │  (Agent)     │    stdin/stdout      │   (工具提供者)    │
  │              │                      │                  │
  │  list_tools()│ ──────────────────► │  3 个 tool 函数  │
  │  call_tool() │ ◄────────────────── │                  │
  └──────────────┘                      └──────────────────┘
"""

import asyncio
import sys
import os
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


async def run_mcp_client():
    """
    MCP Client 的标准使用流程：
      1. 定义 ServerParameters（启动命令）
      2. stdio_client() 启动 Server 子进程，建立 stdio 双向通信
      3. ClientSession 初始化连接
      4. list_tools() 发现 Server 提供了哪些工具
      5. call_tool() 调用工具
    """
    # --- 步骤 1: 定义 Server 启动参数 ---
    # stdio transport：Client 作为父进程启动 Server 子进程
    # 通过 stdin/stdout 进行 JSON-RPC 通信
    server_script = os.path.join(os.path.dirname(__file__), "day6_mcp_server.py")
    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
    )

    print("=" * 60)
    print("MCP Client — 连接知识检索 Server")
    print("=" * 60)

    # --- 步骤 2-3: 建立连接 ---
    # stdio_client 是一个 async context manager
    # 进入 with 块时自动启动 Server 子进程
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # 初始化 MCP 连接（握手：交换协议版本和能力）
            await session.initialize()
            print(f"\n已连接 MCP Server，协议握手完成")

            # --- 步骤 4: 发现工具 ---
            # 这就是 MCP 和直接 import 函数最大的区别：
            # Client 不需要提前知道 Server 有什么工具
            # list_tools() 动态发现 → 返回工具名 + description + 参数 schema
            tools_result = await session.list_tools()
            tools = tools_result.tools

            print(f"\nServer 提供了 {len(tools)} 个工具：")
            for tool in tools:
                print(f"  • {tool.name}: {tool.description}")

            # --- 步骤 5: 调用工具 ---
            # 测试 1：搜索一个概念
            print("\n" + "-" * 40)
            print("[测试 1] 调用 search_knowledge('RAG')")
            result = await session.call_tool("search_knowledge", {"query": "RAG"})
            print(f"结果: {result.content[0].text}")

            # 测试 2：计算
            print("\n" + "-" * 40)
            print("[测试 2] 调用 calculate('13 + 27 * 3')")
            result = await session.call_tool("calculate", {"expression": "13 + 27 * 3"})
            print(f"结果: {result.content[0].text}")

            # 测试 3：列出所有概念
            print("\n" + "-" * 40)
            print("[测试 3] 调用 list_concepts()")
            result = await session.call_tool("list_concepts", {})
            print(f"结果: {result.content[0].text}")

            # 测试 4：搜索不存在的概念
            print("\n" + "-" * 40)
            print("[测试 4] 调用 search_knowledge('Kubernetes')")
            result = await session.call_tool("search_knowledge", {"query": "Kubernetes"})
            print(f"结果: {result.content[0].text}")

            # --- 展示完整的工具 schema ---
            print("\n" + "=" * 60)
            print("工具 Schema（Client 通过 list_tools 拿到的）")
            print("=" * 60)
            for tool in tools:
                print(f"\n{tool.name}:")
                print(f"  description: {tool.description}")
                if hasattr(tool, 'inputSchema') and tool.inputSchema:
                    props = tool.inputSchema.get('properties', {})
                    required = tool.inputSchema.get('required', [])
                    for param_name, param_info in props.items():
                        req_mark = " (必填)" if param_name in required else ""
                        print(f"  参数: {param_name} [{param_info.get('type', '?')}]{req_mark}")
                        print(f"         {param_info.get('description', '')}")


def compare_approaches():
    """对比三种工具集成方式。"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║     三种工具集成方式对比                                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Day 2 — 本地函数 import                                     ║
║    tools = [search_knowledge, calculate]                     ║
║    result = search_knowledge("RAG")  ← 直接 Python 函数调用   ║
║                                                              ║
║    ✅ 最快，零开销                                             ║
║    ❌ 工具和 Agent 强耦合，换语言/换进程都不行                   ║
║    ❌ 工具变更 = Agent 代码变更                                ║
║                                                              ║
║  Day 5 — Skill 封装                                          ║
║    knowledge_skill = Skill(prompt, tools, tests)             ║
║    result = skill.tool_map["search_knowledge"](query)        ║
║                                                              ║
║    ✅ 工具按业务域组织，独立测试                                 ║
║    ✅ prompt 和工具绑定，切 Skill = 切思维模式                   ║
║    ❌ 还是同进程调用，不能跨语言/跨服务                           ║
║                                                              ║
║  Day 6 — MCP 协议                                            ║
║    await client.call_tool("search_knowledge", {"query": "R"})║
║                                                              ║
║    ✅ Agent 和工具完全解耦（不同进程、不同语言、不同机器）        ║
║    ✅ 动态发现：Agent 不需要提前知道有什么工具                   ║
║    ✅ 一个 Agent 可以连多个 MCP Server                         ║
║    ✅ 行业标准协议，所有 LLM/Agent 框架都在适配                  ║
║    ❌ 有序列化开销（JSON-RPC）和进程通信延迟                     ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  面试金句：                                                   ║
║  "我们的 Agent 通过 MCP 协议对接工具——Server 端暴露工具，       ║
║   Agent 端通过标准 JSON-RPC 调用。这样工具提供者和 Agent        ║
║   完全解耦，Server 可以用任何语言实现，一个 Agent 可以同时       ║
║   连接多个 MCP Server。MCP 就像 Agent 的 USB 接口。"           ║
╚══════════════════════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    asyncio.run(run_mcp_client())
    compare_approaches()
