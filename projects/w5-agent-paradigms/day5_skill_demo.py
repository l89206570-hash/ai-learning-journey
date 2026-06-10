# W5 Day 5 — Skills vs Tools：从螺丝刀到工具箱
"""
Day 2 你有两个零散工具：search_knowledge + calculate。
今天把它们升级为一个"知识检索 Skill"，理解 Tool vs Skill 的本质差异。

核心认知：
  Tool  = 螺丝刀    — 单一功能，LLM 自己决定何时用
  Skill = 工具箱    — prompt + tools + 流程 + 测试打包在一起

面试时面试官问"你们的 Agent 怎么管理工具？"
  - 回答"我们有 20 个工具" → Demo 水平
  - 回答"我们按业务域封装成 Skill，每个 Skill 自带 prompt + 工具 + 校验" → 工程化水平
"""

import os
import sys
import json
from dataclasses import dataclass, field
from typing import Any, Callable
from dotenv import load_dotenv
from openai import OpenAI

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# ============================================================
# Part 1: Skill 是什么？
# ============================================================
# 一个 Skill 包含 5 个要素：
#   1. name + description — 告诉调度者"我能做什么"
#   2. system_prompt        — 告诉 LLM "在这个 Skill 里你该怎么干活"
#   3. tools                — 这个 Skill 专属的工具函数
#   4. input_schema         — 定义"什么输入会触发这个 Skill"（给调度者看）
#   5. test_cases           — 独立于 Agent 的单元测试


@dataclass
class Skill:
    """Skill = 工具箱，把一组相关工具 + 专用 prompt + 测试打包在一起。"""
    name: str
    description: str
    system_prompt: str
    tools: list[dict]                         # OpenAI tools 格式
    tool_map: dict[str, Callable]             # 工具名 → 函数
    trigger_keywords: list[str] = field(default_factory=list)  # 触发词（用于调度）
    test_cases: list[dict] = field(default_factory=list)       # 独立测试用例

    def to_openai_tools(self):
        """把 Skill 的工具转成 OpenAI API 的 tools= 参数格式。"""
        return [{"type": "function", "function": t} for t in self.tools]

    def execute_tool(self, name: str, args: dict) -> str:
        """执行 Skill 内的一个工具。"""
        if name not in self.tool_map:
            return f"工具 '{name}' 不在 Skill '{self.name}' 中"
        return self.tool_map[name](**args)


# ============================================================
# Part 2: 把 Day 2 的工具打包成"知识检索 Skill"
# ============================================================
# Day 2 的状态：
#   TOOLS = [search_knowledge, calculate]     ← 两个松散的工具
#   SYSTEM_PROMPT = "你是 ReAct 助手..."      ← 全局 prompt，和工具分离
#
# Day 5 的做法：
#   把 search_knowledge + calculate + 专用 prompt + 测试 打包成一个 Skill 对象

KNOWLEDGE = {
    "Python": "Python 是 Guido van Rossum 于 1991 年发布的编程语言，以简洁易读著称。广泛应用于 AI 开发。",
    "RAG": "RAG（检索增强生成）是一种让 LLM 先检索外部知识再回答的 AI 技术，核心是减少幻觉、提供可溯源的答案。",
    "Agent": "AI Agent 是能自主使用工具、规划步骤、执行任务的智能体，是 2026 年 AI 应用开发最热门的方向。",
    "ChromaDB": "ChromaDB 是一个开源的向量数据库，用于存储和检索嵌入向量。",
    "Streamlit": "Streamlit 是一个 Python Web 框架，几行代码就能构建数据应用。",
    "LangGraph": "LangGraph 是一个状态图执行引擎，用于构建可暂停、可回溯的 Agent 工作流。",
    "MCP": "MCP（Model Context Protocol）是 2026 年 Agent 工具连接标准协议，让不同工具通过统一接口对接。",
}


def search_knowledge(query: str) -> str:
    """在知识库中模糊搜索概念。"""
    results = []
    for key, value in KNOWLEDGE.items():
        if query.lower() in key.lower() or key.lower() in query.lower():
            results.append(f"【{key}】{value}")
    return "\n\n".join(results) if results else f"未找到与「{query}」相关的知识。"


def calculate(expression: str) -> str:
    """安全计算数学表达式。"""
    allowed = {"__builtins__": {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "int": int, "float": float,
    }}
    try:
        return f"计算结果：{eval(expression, allowed)}"
    except Exception as e:
        return f"计算出错：{e}"


# --- Skill 的专用 system prompt ---
# 注意和 Day 2 全局 SYSTEM_PROMPT 的区别：
#   Day 2: 通用 ReAct 指令（"分析问题 → 调工具 → 回答"）
#   Day 5: 这个 Skill 的业务指令（"你怎么搜知识、怎么用计算、怎么组织答案"）
KNOWLEDGE_SKILL_PROMPT = """你是知识检索专家。你拥有以下能力：
- 搜索知识库中存储的技术概念
- 对搜索结果进行数学计算（排序、统计、比较）

工作流程：
1. 理解用户想了解什么概念
2. 用中文关键词逐个搜索，一次搜一个概念
3. 如果需要排序/比较/统计，用 calculate 工具
4. 所有概念都搜完后，组织成清晰的结构化答案

输出格式：
- 每个概念单独说明
- 如有排序/比较，明确列出结果
- 用简洁的中文回答，不超过 300 字"""

# --- 打包成 Skill ---
knowledge_skill = Skill(
    name="knowledge_retrieval",
    description="在技术知识库中检索概念，支持搜索、排序、统计",
    system_prompt=KNOWLEDGE_SKILL_PROMPT,
    tools=[
        {
            "name": "search_knowledge",
            "description": "在知识库中模糊搜索技术概念，返回匹配的条目。一次只搜一个概念，用中文关键词。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "要搜索的中文关键词"}
                },
                "required": ["query"],
            },
        },
        {
            "name": "calculate",
            "description": "安全计算数学表达式，用于排序、计数、统计。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如 'len(\"abc\")'、'3*5'"}
                },
                "required": ["expression"],
            },
        },
    ],
    tool_map={"search_knowledge": search_knowledge, "calculate": calculate},
    trigger_keywords=["查", "搜索", "知识", "概念", "什么是", "解释", "排序", "对比", "计算"],
    test_cases=[
        {
            "query": "什么是 RAG？",
            "check": lambda ans: "检索增强生成" in ans or "RAG" in ans,
            "desc": "单个概念查询",
        },
        {
            "query": "Python 和 ChromaDB 分别是什么？",
            "check": lambda ans: "Python" in ans and "ChromaDB" in ans,
            "desc": "多概念查询",
        },
        {
            "query": "查 Python、RAG、Agent，按名字长度排序",
            "check": lambda ans: all(k in ans for k in ["Python", "RAG", "Agent"]),
            "desc": "搜索 + 排序",
        },
    ],
)


# ============================================================
# Part 3: 再加一个 Skill — 感受"工具箱"的复用性
# ============================================================
# 有了 Skill 的概念之后，新增能力不再是"加一个工具"而是"加一个 Skill"。
# 每个 Skill 自带 prompt，LLM 在不同 Skill 之间切换时自动切换"思维模式"。

CODE_SKILL_PROMPT = """你是代码助手。你只能做以下事：
- 格式化 Python 代码（缩进、换行）
- 统计代码行数、函数数

约束：
- 不要解释代码是干什么的
- 不要评价代码好坏
- 只输出格式化后的代码或统计数据"""


def format_code(code: str) -> str:
    """格式化 Python 代码（模拟）。"""
    # 真实场景会用 black/autopep8，这里简化为去掉首尾空行 + 统一缩进
    lines = [line.rstrip() for line in code.strip().split("\n")]
    return "\n".join(lines)


def count_code(code: str) -> str:
    """统计代码行数和函数数。"""
    lines = [l for l in code.split("\n") if l.strip() and not l.strip().startswith("#")]
    func_count = sum(1 for l in lines if l.strip().startswith("def "))
    return f"有效代码行数：{len(lines)}，函数数：{func_count}"


code_skill = Skill(
    name="code_helper",
    description="格式化 Python 代码、统计行数和函数数",
    system_prompt=CODE_SKILL_PROMPT,
    tools=[
        {
            "name": "format_code",
            "description": "格式化 Python 代码，统一缩进和换行。",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "要格式化的 Python 代码"}
                },
                "required": ["code"],
            },
        },
        {
            "name": "count_code",
            "description": "统计 Python 代码的有效行数和函数数量。",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "要统计的 Python 代码"}
                },
                "required": ["code"],
            },
        },
    ],
    tool_map={"format_code": format_code, "count_code": count_code},
    trigger_keywords=["代码", "格式化", "统计", "行数", "函数数", "Python"],
    test_cases=[
        {
            "query": "帮我统计这段代码的行数：\ndef foo():\n    pass\n\ndef bar():\n    return 1",
            "check": lambda ans: "2" in ans or "两" in ans,
            "desc": "代码统计",
        },
    ],
)

# 所有已注册的 Skill
SKILLS = [knowledge_skill, code_skill]


# ============================================================
# Part 4: Skill 调度器 — Agent 自动选工具箱
# ============================================================
# 有多个 Skill 后需要一个调度器：看用户意图 → 选对应的 Skill → 用那个 Skill 的 prompt + tools

def route_to_skill(user_query: str) -> Skill | None:
    """
    简单关键词调度：匹配触发词最多的 Skill 胜出。
    生产环境会用 embedding 相似度或 LLM 路由。
    """
    best_skill, best_score = None, 0
    query_lower = user_query.lower()
    for skill in SKILLS:
        score = sum(1 for kw in skill.trigger_keywords if kw in query_lower)
        if score > best_score:
            best_skill, best_score = skill, score
    # 如果没有任何触发词匹配，返回第一个作为默认
    return best_skill if best_skill else SKILLS[0]


def run_skill_agent(user_query: str, skill: Skill | None = None):
    """
    用 Skill 的专用 prompt + 工具运行 Agent。

    和 Day 2 的关键差异：
      Day 2: system_prompt 写死在代码里，工具是全局 TOOLS 列表
      Day 5: system_prompt 跟 Skill 走，工具也跟 Skill 走
              → 切 Skill = 切思维模式 + 切工具集
    """
    if skill is None:
        skill = route_to_skill(user_query)

    messages = [
        {"role": "system", "content": skill.system_prompt},
        {"role": "user", "content": user_query},
    ]

    max_turns = 10
    for turn in range(max_turns):
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=skill.to_openai_tools(),
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content

        # 执行工具调用
        for tc in msg.tool_calls:
            tool_name = tc.function.name
            tool_args = json.loads(tc.function.arguments)
            result = skill.execute_tool(tool_name, tool_args)

            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tool_name, "arguments": tc.function.arguments},
                }],
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": result,
            })

    return "执行轮次超限，请简化问题重试。"


# ============================================================
# Part 5: 对比 — 松散工具 vs Skill
# ============================================================

def compare_tools_vs_skills():
    print("""
╔══════════════════════════════════════════════════════════════╗
║          Tool（螺丝刀） vs Skill（工具箱）                    ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Day 2 的做法（松散工具）：                                   ║
║    TOOLS = [search_knowledge, calculate]                     ║
║    system_prompt = "你是 ReAct 助手..."   ← 全局通用         ║
║                                                              ║
║    问题：                                                    ║
║    - 加一个工具 = 改全局 prompt + 改 TOOLS 列表               ║
║    - 工具多了 prompt 越来越长，"万金油" prompt 越来越不精准    ║
║    - 没办法单独测试某个工具组合                               ║
║                                                              ║
║  Day 5 的做法（Skill）：                                     ║
║    knowledge_skill = Skill(                                  ║
║        prompt="你是知识检索专家...",  ← 专用 prompt          ║
║        tools=[search_knowledge, calculate],                  ║
║        test_cases=[...],               ← 自带测试            ║
║    )                                                         ║
║                                                              ║
║    好处：                                                    ║
║    - 加能力 = 加一个 Skill，不动已有 Skill                    ║
║    - prompt 精准：知识检索的 prompt 只说怎么搜知识             ║
║    - 可独立测试：代码 Skill 的问题不影响知识 Skill             ║
║    - 切 Skill = 切 prompt + 切工具集，思维模式也跟着切         ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  面试金句：                                                   ║
║  "我们的 Agent 不是直接管 30 个工具，而是按业务域拆成         ║
║   Skill——每个 Skill 是 prompt + tools + schema 的封装。       ║
║   调度层按意图路由到 Skill，Skill 内部用专用 prompt 执行。"    ║
╚══════════════════════════════════════════════════════════════╝
""")


# ============================================================
# Part 6: 运行
# ============================================================

def test_skill(skill: Skill):
    """运行 Skill 的独立测试用例（不依赖 Agent）。"""
    print(f"\n--- 测试 Skill: {skill.name} ---")
    for i, case in enumerate(skill.test_cases):
        result = run_skill_agent(case["query"], skill=skill)
        passed = case["check"](result)
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {case['desc']}")
        print(f"         问: {case['query']}")
        print(f"         答: {result[:120]}...")
        if not passed:
            print(f"         ⚠ 检查未通过")


if __name__ == "__main__":
    compare_tools_vs_skills()

    print("\n" + "=" * 60)
    print("Skill 独立测试（不依赖 Agent 调度层）")
    print("=" * 60)

    # 每个 Skill 独立跑自己的测试用例
    test_skill(knowledge_skill)
    test_skill(code_skill)

    print("\n" + "=" * 60)
    print("Skill 调度测试（自动路由）")
    print("=" * 60)

    # 混合提问，验证调度器选对 Skill
    mixed_tests = [
        ("帮我查一下 LangGraph 是什么", "knowledge_retrieval"),
        ("统计这段代码有多少个函数：\\ndef a(): pass\\ndef b(): pass", "code_helper"),
        ("Python 和 RAG 分别是什么？", "knowledge_retrieval"),
    ]

    for query, expected_skill in mixed_tests:
        routed = route_to_skill(query)
        match = "✓" if routed.name == expected_skill else "✗"
        print(f"  [{match}] 调度: {routed.name:25s} ← 期望: {expected_skill}")
        print(f"         用户: {query}")

    print("\n" + "=" * 60)
    print("端到端测试：知识检索 Skill")
    print("=" * 60)

    final_query = "查一下 Python、RAG、MCP 这三个概念，然后告诉我哪个和 AI 最相关"
    print(f"用户: {final_query}")
    answer = run_skill_agent(final_query)
    print(f"\n最终答案:\n{answer}")

    print("\n" + "█" * 60)
    print("█  关键认知")
    print("█" * 60)
    print("""
    1. Tool = 函数，Skill = 函数 + prompt + 测试。
       工具多了必须分层管理，不然 prompt 变成"万能废话"。

    2. Skill 的 system_prompt 不是装饰。
       它是告诉 LLM "在这个 Skill 里你是干什么的、怎么干活"。
       一个精准的 prompt 比多给 3 个工具更有用。

    3. 调度层（route_to_skill）和生产环境是两码事。
       这里是关键词匹配，生产用 embedding 相似度或 LLM 路由。
       但核心概念一样：按意图选 Skill，Skill 自带 prompt + tools。

    4. 独立可测试 = 工程化的标志。
       每个 Skill 自带 test_cases，改知识库不影响代码 Skill 的测试。
       面试时这句能让你从"做过 demo"变成"做过工程化设计"。
    """)
