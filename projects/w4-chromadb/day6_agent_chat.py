# W4 Day 6 — Agent Chat 交互界面
"""
把 Day 5 的命令行 Agent Loop 升级成 Streamlit 聊天界面。

新概念：
  1. st.chat_message() — 聊天气泡组件
  2. st.chat_input() — 聊天输入框（回车发送）
  3. st.status() — 可展开的执行状态框（展示工具调用过程）
  4. 多轮对话 — session_state 保存完整消息历史

复用 Day 5 的内容：
  - TOOLS 列表（工具定义）
  - TOOL_MAP 字典（工具名 → 函数）
  - agent loop 核心逻辑
"""

import streamlit as st
import json
from datetime import datetime
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 第 1 步：复用 Day 5 的工具定义和客户端
# ============================================================

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def get_current_time():
    """返回当前时间字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_word_length(word: str):
    """返回输入字符串的长度"""
    return f"单词「{word}」的长度是 {len(word)}"


def calculate(expression: str):
    """安全地计算数学表达式"""
    allowed = {"__builtins__": {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "int": int, "float": float,
    }}
    try:
        result = eval(expression, allowed)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算出错：{e}"


KNOWLEDGE = {
    "python": "Python 是 Guido van Rossum 于 1991 年发布的编程语言，以简洁易读著称。",
    "rag": "RAG（检索增强生成）是一种让 LLM 先检索外部知识再回答的技术，减少幻觉。",
    "agent": "AI Agent 是能自主使用工具、规划步骤、执行任务的智能体。",
    "chromadb": "ChromaDB 是一个开源的向量数据库，用于存储和检索嵌入向量。",
    "streamlit": "Streamlit 是一个 Python Web 框架，几行代码就能构建数据应用。",
}


def search_knowledge(query: str):
    """模拟知识库搜索"""
    query_lower = query.lower()
    results = []
    for key, value in KNOWLEDGE.items():
        if key in query_lower or query_lower in key:
            results.append(f"【{key}】{value}")
    if results:
        return "\n".join(results)
    return f"未找到与「{query}」相关的知识。"


# ---------- 工具定义（跟 Day 5 一样）----------


# TODO 1: 把 Day 5 的 TOOLS 列表复制过来
# 提示：包含 get_current_time、calculate、search_knowledge、get_word_length
# 如果忘了格式，翻 knowledge.md 看 JSON Schema 的写法，或者看 day5_agent_loop.py

TOOLS = [
{
    "type":"function",
    "function":{
        "name":"get_current_time",
        "description":"这是一个返回当前时间的函数",
        "parameters":{
            "type":"object",
            "properties":{},
            "required":[],
        }
    }
},
{
    "type":"function",
    "function":{
        "name":"calculate",
        "description":"安全的计算数学表达式",
        "parameters":{
            "type":"object",
            "properties":{
                "expression":{
                    "type":"string",
                    "description":"要计算的数学表达式",
                }
            },
            "required":["expression"],
        }
    }
},
{
    "type":"function",
    "function":{
        "name":"search_knowledge",
        "description":"模拟知识库搜索",
        "parameters":{
            "type":"object",
            "properties":{
                "query":{
                    "type":"string",
                    "description":"要回答的用户的问题",
                }
            },
            "required":["query"],
        }
    }
},    # 在这里补充 4 个工具定义
{
    "type":"function",
    "function":{
        "name":"get_word_length",
        "description":"返回输入字符串长度",
        "parameters":{
            "type":"object",
            "properties":{
                "word":{
                    "type":"string",
                    "description":"要返回的字符串",
                }
            },
            "required":["word"]
        }
    }
},
]


# TODO 2: 把 Day 5 的 TOOL_MAP 字典复制过来
# 提示：key 是工具名（字符串），value 是函数名（不加引号不加括号）

TOOL_MAP = {
    "get_current_time": get_current_time,
    "calculate": calculate,
    "search_knowledge": search_knowledge,
    "get_word_length": get_word_length,
    # 在这里补充 4 个映射
}


# ============================================================
# 第 2 步：Agent Loop（跟 Day 5 几乎一样，改了一行）
# ============================================================
# 和 Day 5 的区别：
#   Day 5 用 print 输出 → Day 6 改成 yield（生成器）
#   yield 让你可以"一步一步"把进度传回 Streamlit，而不是等全部结束

SYSTEM_PROMPT = """你是一个有用的 AI 助手。你可以使用工具来获取信息。

重要规则：
1. 当用户问当前时间 → 调用 get_current_time
2. 当用户需要计算 → 调用 calculate
3. 当用户问技术概念（如 Python、RAG、ChromaDB）→ 调用 search_knowledge
4. 一次只调用一个工具，等拿到结果后再决定下一步
5. 当你有足够信息回答用户时，直接给出最终答案"""


def agent_loop_stream(messages: list, model: str = "deepseek-chat", max_turns: int = 5):
    """
    跟 Day 5 的 agent_loop 一样，但用 yield 代替 print。

    yield 是什么？
      普通函数 return 一次就结束了。
      生成器函数 yield 可以"返回"多次，每次返回后暂停，下次从暂停处继续。
      这里每次 yield 返回一步进展，Streamlit 收到后立即显示。

    每次 yield 返回一个字典：
      {"type": "tool_call", "name": "工具名", "args": {...}, "result": "结果"}
      {"type": "answer", "content": "最终回答"}
      {"type": "error", "content": "错误信息"}
    """
    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            temperature=0.1,
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            tool_call = msg.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            func = TOOL_MAP[tool_name]
            result = func(**tool_args)

            # yield 代替 Day 5 的 print
            yield {"type": "tool_call", "name": tool_name, "args": tool_args, "result": result}

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
            yield {"type": "answer", "content": msg.content}
            return

    yield {"type": "error", "content": "达到最大工具调用次数，Agent 停止。"}


# ============================================================
# 第 3 步：Streamlit UI（你来写！）
# ============================================================

st.set_page_config(page_title="AI Agent Chat", page_icon="🤖")
st.title("AI Agent Chat")

# ---------- 侧边栏 ----------
with st.sidebar:
    st.header("⚙️ 设置")
    model = st.selectbox("模型", ["deepseek-chat", "deepseek-reasoner"], index=0)
    max_turns = st.slider("最大工具调用轮数", 1, 10, 5)

    st.divider()
    st.caption("可用工具：get_current_time / calculate / search_knowledge / get_word_length")

    # TODO 3: 添加"清空对话"按钮
    # 提示：用 st.button("清空对话")，点击后清空 session_state.messages 并 st.rerun()
if st.button("清空对话"):
    st.session_state.messages = []
    st.rerun()


# ---------- 主界面：显示对话历史 ----------

# TODO 4: 初始化 session_state.messages
# 提示：if "messages" not in st.session_state: st.session_state.messages = []
if "messages" not in st.session_state:
    st.session_state.messages = []


# TODO 5: 遍历显示历史消息
# 提示：用 for msg in st.session_state.messages:
#           with st.chat_message(msg["role"]):   ← 这是聊天气泡组件
#               st.write(msg["content"])
# 消息格式：{"role": "user"|"assistant"|"tool", "content": "..."}
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ---------- 聊天输入 ----------

# TODO 6: 获取用户输入
# 提示：prompt = st.chat_input("输入你的问题，我会用工具来回答...")
# 如果 prompt 不为空：
#   1. 把用户消息加入 session_state.messages
#   2. 用 st.chat_message("user") 显示用户消息
#   3. 构建 messages 列表（system prompt + 历史消息）
#   4. 调用 agent_loop_stream()
#   5. 用 st.status() 显示工具调用过程
#   6. 把最终回答加入 session_state.messages
#   7. 用 st.chat_message("assistant") 显示回答

if prompt := st.chat_input("输入你的问题，我会用工具来回答..."):
    # 步骤 1: 显示用户消息
    st.chat_message("user").write(prompt)

    # 步骤 2: 构建完整的 messages（system + 历史 + 当前用户消息）
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # 把历史消息也加进去（支持多轮对话上下文）
    for m in st.session_state.messages:
        messages.append(m)

    # 把当前用户消息加入
    messages.append({"role": "user", "content": prompt})

    # 把用户消息存入 session_state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 步骤 3: 运行 Agent Loop，用 st.status 显示过程
    with st.status("Agent 思考中...", expanded=True) as status:
        final_answer = None
        for step in agent_loop_stream(messages, model=model, max_turns=max_turns):
            if step["type"] == "tool_call":
                # TODO 8: 在 status 里显示工具调用信息
                # 提示：st.write(f"🔧 调用 {step['name']}") 然后 st.write(f"结果: {step['result']}")
                # 这一步我已经帮你写了，你只需要理解
                st.write(f"🔧 调用工具: **{step['name']}**")
                st.write(f"   参数: {json.dumps(step['args'], ensure_ascii=False)}")
                st.write(f"   结果: {step['result']}")
                st.divider()
            elif step["type"] == "answer":
                final_answer = step["content"]
                status.update(label="回答完成", state="complete")
            elif step["type"] == "error":
                final_answer = step["content"]
                status.update(label="执行异常", state="error")

    # 步骤 4: 显示最终回答并存入历史
    if final_answer:
        st.chat_message("assistant").write(final_answer)
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
    else:
        st.chat_message("assistant").write("抱歉，Agent 未能生成回答。")


# ============================================================
# 测试问题（复制到聊天框试用）：
#   1. 现在几点了？
#   2. 帮我算一下 (15 + 7) * 3 - 4
#   3. 什么是 RAG？
#   4. hello 这个单词有几个字母？
#   5. Python 和 Streamlit 有什么关系？
# ============================================================
