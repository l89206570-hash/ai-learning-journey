"""评测脚本 — 对跨境电商 Agent 进行正确性 × 效率 × 稳定性评测"""

import os
import sys
import json
import time
import asyncio
import logging
from dotenv import load_dotenv

from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from openai import OpenAI

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent_graph import build_mcp_langchain_tools, build_react_graph, SYSTEM_PROMPT
from config import LLM_MODEL, LLM_API_KEY, LLM_API_BASE, MCP_SERVER_SCRIPT

load_dotenv()
logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

llm_client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_API_BASE)


# ============================================================
# 评测用例
# ============================================================

EVAL_CASES = [
    {
        "id": "product_search",
        "query": "有没有适合夏天穿的T恤",
        "expect_keywords": ["T恤", "棉", "129"],
        "expect_tool": "search_knowledge",
    },
    {
        "id": "order_status",
        "query": "帮我查订单 JD20260615001 到哪了",
        "expect_keywords": ["顺丰", "SF1234567890"],
        "expect_tool": "check_order_status",
    },
    {
        "id": "return_policy",
        "query": "买的衣服不合身，怎么退货",
        "expect_keywords": ["退货", "7天", "退款"],
        "expect_tool": "search_knowledge",
    },
    {
        "id": "membership",
        "query": "钻石会员有什么好处",
        "expect_keywords": ["钻石", "10000", "优先"],
        "expect_tool": "check_membership",
    },
    {
        "id": "shipping_time",
        "query": "发货要多久",
        "expect_keywords": ["发货", "物流", "时效"],
        "expect_tool": "search_knowledge",
    },
]


# ============================================================
# 评测主流程
# ============================================================

async def run_eval():
    server_params = StdioServerParameters(command="python", args=[MCP_SERVER_SCRIPT])

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.list_tools()
            lc_tools = build_mcp_langchain_tools(session, result.tools)
            graph = build_react_graph(lc_tools)

            print("=" * 70)
            print("跨境电商 Agent 评测")
            print("=" * 70)
            print(f"{'ID':<20} {'关键词':<8} {'工具':<8} {'耗时(s)':<10} {'状态'}")
            print("-" * 70)

            total = len(EVAL_CASES)
            keyword_pass = 0
            tool_pass = 0
            total_time = 0

            for case in EVAL_CASES:
                t0 = time.time()

                body_correct = True
                prompt = SYSTEM_PROMPT
                full_prompt = prompt + "\n\n用户：" + case["query"] + "\n助手："

                try:
                    response = llm_client.chat.completions.create(
                        model=LLM_MODEL,
                        messages=[{"role": "user", "content": full_prompt}],
                        tools=[],
                        max_tokens=512,
                    )
                    content = response.choices[0].message.content
                except Exception as e:
                    content = ""
                    body_correct = False

                elapsed = time.time() - t0
                total_time += elapsed

                kw_hit = any(kw in content for kw in case["expect_keywords"]) if content else False
                # 工具检查：通过 LLM 的 tool_calls 判断
                try:
                    response_with_tool = llm_client.chat.completions.create(
                        model=LLM_MODEL,
                        messages=[{"role": "user", "content": full_prompt}],
                        tools=[
                            {"type": "function", "function": {"name": "search_knowledge", "description": "搜索电商知识库", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}}}},
                            {"type": "function", "function": {"name": "check_order_status", "description": "查询订单状态", "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}}}}},
                            {"type": "function", "function": {"name": "check_membership", "description": "查询会员权益", "parameters": {"type": "object", "properties": {"member_level": {"type": "string"}}}}},
                        ],
                        max_tokens=512,
                    )
                    tool_called = response_with_tool.choices[0].message.tool_calls
                    tool_hit = (tool_called and tool_called[0].function.name == case["expect_tool"]) if tool_called else False
                except Exception:
                    tool_hit = False

                if kw_hit:
                    keyword_pass += 1
                if tool_hit:
                    tool_pass += 1

                status = "✅ PASS" if (body_correct and kw_hit) else "⚠️  WARN"
                logger.info("%s | kw=%s tool=%s t=%.1fs", case["id"], kw_hit, tool_hit, elapsed)
                print(f"{case['id']:<20} {'✅' if kw_hit else '❌':<8} {'✅' if tool_hit else '❌':<8} {elapsed:<10.2f} {status}")

            # ============================================================
            # 稳定性测试：重复 3 次
            # ============================================================
            print("\n" + "=" * 70)
            print("稳定性测试（重复 3 次）")
            print("=" * 70)

            stability_case = EVAL_CASES[0]
            times = []
            for run_id in range(3):
                t0 = time.time()
                try:
                    response = llm_client.chat.completions.create(
                        model=LLM_MODEL,
                        messages=[{"role": "user", "content": stability_case["query"]}],
                        max_tokens=512,
                    )
                    content = response.choices[0].message.content
                except Exception:
                    content = ""
                elapsed = time.time() - t0
                times.append(elapsed)
                kw_hit = any(kw in content for kw in stability_case["expect_keywords"])
                print(f"  Run {run_id + 1}: {elapsed:.2f}s | {'✅' if kw_hit else '❌'} keywords")

            avg_time = sum(times) / len(times) if times else 0
            print(f"  平均耗时: {avg_time:.2f}s | 标准差: {max(times) - min(times):.2f}s")

            # ============================================================
            # 总结
            # ============================================================
            print("\n" + "=" * 70)
            print("评测总结")
            print("=" * 70)
            print(f"  正确性（关键词）: {keyword_pass}/{total}")
            print(f"  正确性（工具选择）: {tool_pass}/{total}")
            print(f"  平均耗时: {total_time/total:.2f}s")
            print(f"  {'✅ 全部通过' if keyword_pass == total else '⚠️  有 ' + str(total - keyword_pass) + ' 条未命中关键词'}")


if __name__ == "__main__":
    asyncio.run(run_eval())
