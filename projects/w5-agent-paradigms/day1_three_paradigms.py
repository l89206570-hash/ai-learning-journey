# W5 Day 1 — Agent 三范式对比
"""
用同一个任务分别实现三种 Agent 范式，感受各自的设计思路差异。

三种范式：
  ReAct（思考-行动-观察循环）
    → 每步思考 → 选一个工具 → 看到结果 → 再思考 → 直到能回答
  Plan-then-Execute（先规划后执行）
    → 先列完整步骤清单 → 逐步执行 → 汇总结果
  Reflexion（自我反思修正）
    → 执行 → 自我评价质量 → 不满意就分析原因 → 重新执行 → 直到满意

统一任务（三种范式都做同一个）：
  "请帮我查一下 Python、RAG、Agent 这三个概念，
   然后按名称长度从短到长排序，并告诉我哪个概念和 AI 最相关"
"""

import os
import json
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Windows 终端 GBK 编码修复（DeepSeek 回复含 emoji 会炸）
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# ============================================================
# 共享工具（三种范式用同一套工具）
# ============================================================

KNOWLEDGE = {
    "Python": "Python 是 Guido van Rossum 于 1991 年发布的编程语言，以简洁易读著称。广泛应用于 AI 开发。",
    "RAG": "RAG（检索增强生成）是一种让 LLM 先检索外部知识再回答的 AI 技术，核心是减少幻觉、提供可溯源的答案。",
    "Agent": "AI Agent 是能自主使用工具、规划步骤、执行任务的智能体，是 2026 年 AI 应用开发最热门的方向。",
    "ChromaDB": "ChromaDB 是一个开源的向量数据库，用于存储和检索嵌入向量。",
    "Streamlit": "Streamlit 是一个 Python Web 框架，几行代码就能构建数据应用。",
}


def search_knowledge(query: str):
    """在知识库中模糊搜索概念"""
    query_lower = query.lower()
    results = []
    for key, value in KNOWLEDGE.items():
        if key.lower() in query_lower or query_lower in key.lower():
            results.append(f"【{key}】{value}")
    if results:
        return "\n\n".join(results)
    return f"未找到与「{query}」相关的知识。"


def calculate(expression: str):
    """安全计算数学表达式"""
    allowed = {"__builtins__": {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "int": int, "float": float,
    }}
    try:
        return f"计算结果：{eval(expression, allowed)}"
    except Exception as e:
        return f"计算出错：{e}"


# ============================================================
# 工具描述（JSON Schema 格式，跟 W4D5 一样）
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "在知识库中搜索技术概念。输入关键词，返回相关解释。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词，例如 'Python'"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "安全计算数学表达式。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如 '3+5*2'"}
                },
                "required": ["expression"]
            }
        }
    },
]

TOOL_MAP = {
    "search_knowledge": search_knowledge,
    "calculate": calculate,
}

# ============================================================
# 范式一：ReAct（你 W4D5 写过，这里稍作整理）
# ============================================================
#
# 循环结构：
#   while 还没到最终答案:
#       LLM 思考 → 返回 tool_call 或 text
#       如果有 tool_call → 执行工具 → 结果塞回 messages → 继续循环
#       如果是 text → 这就是最终答案，结束
#
# ============================================================

REACT_SYSTEM = """你是一个使用 ReAct 模式的 AI 助手。

规则：
1. 分析用户的问题，想清楚需要什么信息
2. 一次只调用一个工具，拿到结果再决定下一步
3. 当信息足够时，直接给出最终答案（不要再调工具）
4. 搜索知识库用中文关键词"""


def react_agent(user_query: str, max_turns: int = 5):
    """ReAct 范式：思考 → 行动 → 观察 → 循环"""
    messages = [
        {"role": "system", "content": REACT_SYSTEM},
        {"role": "user", "content": user_query},
    ]

    print("=" * 50)
    print(f"[ReAct] 用户: {user_query}")
    print("=" * 50)

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model="deepseek-chat", messages=messages, tools=TOOLS
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            func = TOOL_MAP[tool_name]
            result = func(**tool_args)
            print(f"  [调用工具] {tool_name}({tool_args}) → {result}")
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call.model_dump()]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
        else:
            print(f"  [最终回答] {msg.content}")
            return msg.content

    return "达到最大轮次"


# ============================================================
# 范式二：Plan-then-Execute（先规划后执行）
# ============================================================
#
# 流程分两个阶段：
#   阶段1 PLAN：LLM 不调工具，先输出一个步骤列表（纯文本）
#   阶段2 EXECUTE：按步骤逐个执行，每步可以调工具
#
# ============================================================

PLAN_SYSTEM = """你是一个使用 Plan-then-Execute 模式的 AI 助手。

当用户提出问题时，你需要先制定计划再执行。

计划阶段：
- 分析任务，输出一个编号的步骤列表
- 每个步骤要具体可执行
- 格式：步骤1: xxx\n步骤2: xxx\n...

执行阶段：
- 严格按顺序执行每一步
- 需要信息时调用工具
- 全部步骤完成后给出最终答案"""


# --- 方式 B：逐步骤执行 ---
# 你（代码）控制节奏，每轮告诉 LLM "现在执行第N步"
def plan_execute_agent_b(user_query: str, max_turns: int = 8):
    """Plan-then-Execute B：逐步骤执行"""
    messages = [
        {"role": "system", "content": PLAN_SYSTEM},
        {"role": "user", "content": user_query},
    ]

    print("=" * 50)
    print(f"[Plan-Execute-B] 用户: {user_query}")
    print("=" * 50)

    # ===== 阶段1：制定计划（不加 tools） =====
    response = client.chat.completions.create(
        model="deepseek-chat", messages=messages
    )
    plan_text = response.choices[0].message.content
    print(f"[计划]\n{plan_text}\n")
    messages.append({"role": "assistant", "content": plan_text})

    # ===== 阶段2：逐步骤执行（加 tools） =====
    # 解析计划里有几个步骤（数 "步骤" 关键词出现次数）
    step_count = plan_text.count("步骤")
    if step_count == 0:
        step_count = 3  # 兜底

    for step_number in range(1, step_count + 1):
        if step_number > max_turns:
            break
        print(f"--- 执行第 {step_number}/{step_count} 步 ---")

        # 你驱动 LLM：明确告诉它现在该做什么
        messages.append({
            "role": "user",
            "content": f"现在执行计划的第{step_number}步。完成后简要告诉我结果。"
        })

        # 单轮 API 调用（带 tools），不循环——因为你只让它做一件事
        response = client.chat.completions.create(
            model="deepseek-chat", messages=messages, tools=TOOLS
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            func = TOOL_MAP[tool_name]
            result = func(**tool_args)
            print(f"  [调用工具] {tool_name}({tool_args}) → {result}")
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call.model_dump()]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
            # 工具结果追加后，让 LLM 基于结果说一句话（步级别完成）
            response = client.chat.completions.create(
                model="deepseek-chat", messages=messages, tools=TOOLS
            )
            step_msg = response.choices[0].message
            print(f"  [步骤{step_number}完成] {step_msg.content}")
            messages.append({"role": "assistant", "content": step_msg.content})
        else:
            print(f"  [步骤{step_number}完成] {msg.content}")
            messages.append({"role": "assistant", "content": msg.content})

    # ===== 阶段3：汇总 =====
    print("--- 汇总 ---")
    messages.append({
        "role": "user",
        "content": "所有步骤已完成，请汇总给出最终答案。"
    })
    response = client.chat.completions.create(
        model="deepseek-chat", messages=messages
    )
    final = response.choices[0].message.content
    print(f"[最终答案] {final}")
    return final


# --- 方式 C：一句话指令 ---
# 计划拿到后，一句"执行"让 LLM 自己把控
def plan_execute_agent_c(user_query: str, max_turns: int = 6):
    """Plan-then-Execute C：一句话指令"""
    messages = [
        {"role": "system", "content": PLAN_SYSTEM},
        {"role": "user", "content": user_query},
    ]

    print("=" * 50)
    print(f"[Plan-Execute-C] 用户: {user_query}")
    print("=" * 50)

    # ===== 阶段1：制定计划（不加 tools） =====
    response = client.chat.completions.create(
        model="deepseek-chat", messages=messages
    )
    plan_text = response.choices[0].message.content
    print(f"[计划]\n{plan_text}\n")
    messages.append({"role": "assistant", "content": plan_text})

    # ===== 阶段2：一句指令，后面就是 ReAct 风格循环 =====
    messages.append({
        "role": "user",
        "content": "请严格按照上述计划逐步执行，完成后给出最终答案。"
    })

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model="deepseek-chat", messages=messages, tools=TOOLS
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            func = TOOL_MAP[tool_name]
            result = func(**tool_args)
            print(f"  [调用工具] {tool_name}({tool_args}) → {result}")
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call.model_dump()]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
        else:
            print(f"  [最终答案] {msg.content}")
            return msg.content

    return "达到最大轮次"


# ============================================================
# 范式三：Reflexion（自我反思修正）
# ============================================================
#
# 流程：
#   第一次执行 → 给出答案
#   LLM 自我评价：这个答案够好吗？
#     不够好 → 分析哪里不足 → 补充搜索/修正 → 重新回答
#     够好了 → 输出最终答案
#
# ============================================================

REFLEXION_SYSTEM = """你是一个使用 Reflexion 模式的 AI 助手。

你的工作方式：
1. 先尝试回答用户问题（可以调用工具获取信息）
2. 审视自己的回答，问自己：
   - 信息是否完整？
   - 结论是否正确？
   - 有没有遗漏用户的要求？
3. 如果不够好，说明哪里不足，然后重新回答
4. 如果已经满意，标记 FINAL 并给出最终答案

重要：你必须至少做一轮自我检查，不能跳过反思步骤。"""


def reflexion_agent(user_query: str, max_turns: int = 6):
    """Reflexion 范式：执行 → 自我评价 → 修正 → 重试"""
    messages = [
        {"role": "system", "content": REFLEXION_SYSTEM},
        {"role": "user", "content": user_query},
    ]

    print("=" * 50)
    print(f"[Reflexion] 用户: {user_query}")
    print("=" * 50)

    # TODO: 实现 Reflexion
    #
    # 思路（分两轮）：
    # 第一轮 — 正常执行（带 tools），得到初步答案
    # 第二轮 — 追加一条 user 消息："请检查你的回答是否完整正确，如果不够好请改进"
    #          然后再次执行（带 tools），拿到改进后的答案
    for turn in range(max_turns):
        response = client.chat.completions.create(
        model="deepseek-chat", messages=messages, tools=TOOLS
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            func = TOOL_MAP[tool_name]
            result = func(**tool_args)
            print(f"  [调用工具] {tool_name}({tool_args}) → {result}")
            messages.append({"role": "assistant", "content": None, "tool_calls": [tool_call.model_dump()]})
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})
        else:
            first_answer = msg.content
            print(f"  [初步答案] {first_answer}")
            break    
    messages.append({
        "role": "user",
        "content": "请检查你的回答是否完整正确，如果不够好请改进"
    })
    for turn in range(max_turns):
        response = client.chat.completions.create(
            model="deepseek-chat", messages=messages, tools=TOOLS
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            func = TOOL_MAP[tool_name]
            result = func(**tool_args)
            print(f"  [调用工具] {tool_name}({tool_args}) → {result}")
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call.model_dump()]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
        else:
            print(f"  [最终答案] {msg.content}")
            return msg.content

    return "达到最大轮次"

# ============================================================
# 测试：三种范式跑同一个任务
# ============================================================

if __name__ == "__main__":
    TASK = "请帮我查一下 Python、RAG、Agent 这三个概念，然后按名称长度从短到长排序，并告诉我哪个概念和 AI 最相关"

    print("\n" + "█" * 60)
    print("█  范式一：ReAct")
    print("█" * 60 + "\n")
    result1 = react_agent(TASK)
    print(f"\n[ReAct 最终结果] {result1}\n")

    print("\n" + "█" * 60)
    print("█  范式二：Plan-then-Execute（方式 B：逐步骤执行）")
    print("█" * 60 + "\n")
    result2b = plan_execute_agent_b(TASK)
    print(f"\n[Plan-Execute-B 最终结果] {result2b}\n")

    print("\n" + "█" * 60)
    print("█  范式二：Plan-then-Execute（方式 C：一句话指令）")
    print("█" * 60 + "\n")
    result2c = plan_execute_agent_c(TASK)
    print(f"\n[Plan-Execute-C 最终结果] {result2c}\n")

    print("\n" + "█" * 60)
    print("█  范式三：Reflexion")
    print("█" * 60 + "\n")
    result3 = reflexion_agent(TASK)
    print(f"\n[Reflexion 最终结果] {result3}\n")
