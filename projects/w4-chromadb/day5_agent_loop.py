# W4 Day 5 — Agent Loop 手写
"""
不用任何框架，纯 OpenAI API 实现 Agent 循环（≤100 行）

核心概念：
  用户提问 → LLM 判断是否需要工具 → 需要就调用工具 → 结果喂回 LLM → 循环 → 最终回答

三个你没见过的东西：
  1. json 模块：字符串和字典互相转换（json.loads / json.dumps）
  2. datetime 模块：获取当前时间
  3. API 的 tools 参数：告诉 LLM "你有这些工具可以用"
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# ============================================================
# 第 1 步：创建 API 客户端（跟之前 battle.py 一样）
# ============================================================
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

# ============================================================
# 第 2 步：定义工具函数（LLM 会调用它们）
# ============================================================

def get_current_time():
    """返回当前时间字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_word_length(word: str):
    """返回输入字符串的长度"""
    return f"单词「{word}」的长度是{len(word)}"


def calculate(expression: str):
    """
    安全地计算数学表达式。
    用 eval() 但不传 globals，只传内置数学函数，防止注入攻击。
    """
    # eval 只允许 __builtins__ 里的数学运算，不能执行任意代码
    allowed = {"__builtins__": {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "int": int, "float": float,
    }}
    try:
        result = eval(expression, allowed)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算出错：{e}"


# 用于知识搜索的假数据（模拟一个知识库）
KNOWLEDGE = {
    "python": "Python 是 Guido van Rossum 于 1991 年发布的编程语言，以简洁易读著称。",
    "rag": "RAG（检索增强生成）是一种让 LLM 先检索外部知识再回答的技术，减少幻觉。",
    "agent": "AI Agent 是能自主使用工具、规划步骤、执行任务的智能体。",
    "chromadb": "ChromaDB 是一个开源的向量数据库，用于存储和检索嵌入向量。",
    "streamlit": "Streamlit 是一个 Python Web 框架，几行代码就能构建数据应用。",
}


def search_knowledge(query: str):
    """
    模拟知识库搜索：在 KNOWLEDGE 字典里模糊匹配。
    如果 query 包含字典 key 的部分文字，就返回对应内容。
    """
    query_lower = query.lower()
    results = []
    for key, value in KNOWLEDGE.items():
        if key in query_lower or query_lower in key:
            results.append(f"【{key}】{value}")
    if results:
        return "\n".join(results)
    return f"未找到与「{query}」相关的知识。"


# ============================================================
# 第 3 步：定义工具描述（告诉 API 每个工具的名字、用途、参数）
# ============================================================
# 这个列表会被传给 chat.completions.create(tools=TOOLS)
# 格式是 OpenAI 的 function calling 规范

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "获取当前的日期和时间。不需要参数。",
            "parameters": {
                "type": "object",
                "properties": {},  # 无参数
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "安全地计算数学表达式。支持加减乘除、括号、abs/round/min/max/pow。",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "要计算的数学表达式，例如 '3 + 5 * 2'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": "在知识库中搜索技术概念。输入关键词，返回相关解释。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，例如 'python'、'chromadb'"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_word_length",
            "description": "返回用户输入字符串长度",
            "parameters": {
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": "要计算长度的单词",
                    }
                },
                "required": ["word"],                                
                }
            }
    },
]

# 工具名 → 实际函数的映射（Agent 循环里用来执行）
TOOL_MAP = {
    "get_current_time": get_current_time,
    "calculate": calculate,
    "search_knowledge": search_knowledge,
    "get_word_length": get_word_length,
}

# ============================================================
# 第 4 步：Agent 循环（核心！）
# ============================================================

SYSTEM_PROMPT = """你是一个有用的 AI 助手。你可以使用工具来获取信息。

重要规则：
1. 当用户问当前时间 → 调用 get_current_time
2. 当用户需要计算 → 调用 calculate
3. 当用户问技术概念（如 Python、RAG、ChromaDB）→ 调用 search_knowledge
4. 一次只调用一个工具，等拿到结果后再决定下一步
5. 当你有足够信息回答用户时，直接给出最终答案"""


def agent_loop(user_query: str, model: str = "deepseek-chat", max_turns: int = 5):
    """
    Agent 主循环：反复调 LLM，直到它给出最终答案或达到最大轮次。

    参数:
        user_query: 用户的问题
        model: 使用的模型
        max_turns: 最多允许 LLM 调用几轮工具（防止死循环）
    """
    # 初始化对话历史
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query},
    ]

    print(f"{'='*60}")
    print(f"用户: {user_query}")
    print(f"{'='*60}")

    for turn in range(max_turns):
        # --- 调 API ---
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,           # ← 关键！告诉 LLM 有哪些工具
            temperature=0.1,       # 低温度，让输出更稳定
        )

        msg = response.choices[0].message

        # --- 情况 A：LLM 要调用工具 ---
        if msg.tool_calls:
            tool_call = msg.tool_calls[0]           # 取第一个工具调用
            tool_name = tool_call.function.name      # 工具名
            tool_args = json.loads(tool_call.function.arguments)  # 参数（JSON 字符串 → 字典）

            # 执行工具
            func = TOOL_MAP[tool_name]
            result = func(**tool_args)  # **tool_args 把字典展开成关键字参数

            print(f"🔧 调用工具: {tool_name}({tool_args})")
            print(f"   → 结果: {result}")

            # 把 LLM 的工具调用请求和工具执行结果都追加到对话历史
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call.model_dump()]  # 把 tool_call 转成字典
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
            # 继续下一轮循环，LLM 会看到工具结果并决定下一步

        # --- 情况 B：LLM 直接给出了文本回答（没有调用工具）---
        else:
            print(f"🤖 回答: {msg.content}")
            return msg.content

    # 达到最大轮次还没结束
    return "⚠️ 达到最大工具调用次数，Agent 停止。"


# ============================================================
# 第 5 步：测试
# ============================================================

if __name__ == "__main__":
    # 单轮对话：只需要回答问题
    agent_loop("你好，现在几点了？")

    print()

    # 需要用工具：计算
    agent_loop("帮我算一下 (3 + 5) * 12 - 8 / 2")

    print()

    # 需要用工具：搜索知识
    agent_loop("什么是 RAG？它和 Agent 有什么关系？")

    agent_loop("hello 这个单词有几个字母？")