# W4 Day 7 — 综合练习：Agent 自主搜索助手
"""
把 W4 两个核心能力串起来：ChromaDB 知识库 + Agent 自主工具调用

你要做的事（按顺序）：
  TODO ①: 加载 ChromaDB 知识库（参考 build_index.py + app.py）
  TODO ②: 写 search_knowledge_base 工具函数（连 ChromaDB 真实检索）
  TODO ③: 补全 TOOLS 定义 + TOOL_MAP（参考 day6_agent_chat.py）
  TODO ④: 写 Agent Loop（yield 生成器，参考 day6_agent_chat.py）
  TODO ⑤: 写 Streamlit 界面（chat_message + chat_input + status，参考 day6_agent_chat.py）

预期效果：
  用户问"云感T恤多少钱" → Agent 自己调 search_knowledge_base 查 ChromaDB → 回答
  用户问"3*5+2" → Agent 调 calculate → 回答
  用户问"现在几点了" → Agent 调 get_current_time → 回答
"""

import streamlit as st
import json
import os
import chromadb
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from chromadb.utils import embedding_functions

load_dotenv()

# ============================================================
# TODO ①: 加载 ChromaDB 知识库（~10 行）
# ============================================================
# 提示：
#   - 用 chromadb.PersistentClient(path="./chroma_store_ecommerce")
#   - client.get_collection("ecommerce_knowledge")
#   - 创建 embedding_fn（SentenceTransformerEmbeddingFunction，指向 BGE 本地路径）
#   - 参考 build_index.py + app.py 的加载部分
#
# 你的代码：
BGE_MODEL_PATH = os.path.expanduser("~/.cache/modelscope/hub/models/BAAI/bge-small-zh-v1___5")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=BGE_MODEL_PATH)
chroma_client = chromadb.PersistentClient(path="./chroma_store_agent")
collection = chroma_client.get_collection("ecommerce_knowledge", embedding_function=embedding_fn)



# ============================================================
# TODO ②: 写 search_knowledge_base 工具函数（~10 行）
# ============================================================
# 提示：
#   - 函数接收 query: str，返回字符串
#   - 内部调 collection.query(query_texts=[query], n_results=3)
#   - 把返回的 documents 拼成一段字符串（每条结果用换行分隔）
#   - 如果没结果，返回"未找到相关信息"
#   - 参考 day1_chromadb_basics.py Part 3 的 query 写法
#
# 你的代码：
def search_knowledge_base(query:str):
    results = collection.query(query_texts=[query], n_results=3)
    if not results ["documents"][0]:
        return "未找到相关信息"
    
    lines = []
    for i, (doc, distance) in enumerate(zip(
        results["documents"][0],
        results["distances"][0],
    )):
        lines.append(f"[{i+1}] {doc} (距离={distance:.4f})")
    return "\n".join(lines)




# ============================================================
# 复用工具函数（已写好，不用改）
# ============================================================

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def calculate(expression: str):
    allowed = {"__builtins__": {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "pow": pow, "int": int, "float": float,
    }}
    try:
        result = eval(expression, allowed)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算出错：{e}"


# ============================================================
# TODO ③: 补全 TOOLS 定义 + TOOL_MAP（~25 行）
# ============================================================
# 提示：
#   - 至少 3 个工具：get_current_time（无参）、calculate（有参 expression）、
#     search_knowledge_base（有参 query）
#   - JSON Schema 格式：properties 用 {}，required 用 []
#   - TOOL_MAP 把工具名字符串映射到函数对象（不加括号！）
#   - 参考 day6_agent_chat.py 的 TOOLS 和 TOOL_MAP
#
# 你的代码：
TOOLS = [
    {
        "type":"function",
        "function":{
            "name":"get_current_time",
            "description":"获取当前时间",
            "parameters":{
                "type":"object",
                "properties":{},
                "required":[],
            }
        },
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
                        "description":"要计算的数学表达式"
                    }
                },
                "required":["expression"],
            }
        },
    },
    {
        "type":"function",
        "function":{
            "name":"search_knowledge_base",
            "description":"根据用户问题找相关数据",
            "parameters":{
                "type":"object",
                "properties":{
                    "query":{
                        "type":"string",
                        "description":"用户输入的问题",
                    }
                },
                "required":["query"],
            }
        }
    },
]

TOOLS_MAP ={"get_current_time":get_current_time,
            "calculate":calculate, 
            "search_knowledge_base":search_knowledge_base}


# ============================================================
# TODO ④: Agent Loop（yield 生成器，~20 行）
# ============================================================
# 提示：
#   - 函数签名：def agent_loop(messages, model="deepseek-chat", max_turns=5):
#   - for turn in range(max_turns): 调 API → 判断 tool_calls
#   - 有 tool_calls → 查 TOOL_MAP 执行 → yield {"type": "tool_call", ...} → 追加 messages
#   - 无 tool_calls → yield {"type": "answer", ...} → return
#   - 参考 day6_agent_chat.py 的 agent_loop_stream 函数
#
# 你的代码：
def agent_loop_stream(messages: list, model: str = "deepseek-chat", max_turns: int = 5):
    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            temperature=0.1,
        )

        msg = response.choices[0].message

        if msg.tool_calls:
            tool_calls = msg.tool_calls[0]
            tool_name = tool_calls.function.name
            tool_args = json.loads(tool_calls.function.arguments)

            func = TOOLS_MAP[tool_name]
            result = func(**tool_args)

            yield {"type":"tool_call", "name":tool_name, "args": tool_args, "result": result}

            messages.append({
                "role":"assistant",
                "content":None,
                "tool_calls": [tool_calls.model_dump()]
            })
            messages.append({
                "role":"tool",
                "tool_call_id":tool_calls.id,
                "content":result,
            })

        else:
            yield{"type":"answer", "content":msg.content}
            return
    yield {"type":"error", "content":"达到最大工具调用次数，Agent 停止。"}    




# ============================================================
# TODO ⑤: Streamlit 界面（~30 行）
# ============================================================
# 提示：
#   - st.set_page_config + st.title
#   - sidebar: model 选择 + max_turns 滑块 + 清空对话按钮
#   - 初始化 session_state.messages
#   - 遍历 messages 显示历史（st.chat_message + st.write）
#   - st.chat_input 获取输入
#   - 构建 messages 列表（system prompt + 历史 + 当前用户消息）
#   - with st.status(...): 运行 agent_loop，显示工具调用过程
#   - 最终回答写入 st.chat_message("assistant") + session_state.messages
#   - 参考 day6_agent_chat.py 第 3 步的完整 UI
#
# 你的代码：


SYSTEM_PROMPT = """你是一个有用的 AI 助手，可以访问一个电商知识库来回答用户问题。

重要规则：
1. 当用户问商品信息、价格、退换货、物流、售后等电商相关问题 → 调用 search_knowledge_base 搜索知识库
2. 当用户需要计算 → 调用 calculate
3. 当用户问当前时间 → 调用 get_current_time
4. 先检索再回答：如果知识库有相关信息，基于检索结果回答；如果知识库没有，告诉用户"知识库中暂无此信息"
5. 一次只调用一个工具，拿到结果后再决定下一步"""

st.set_page_config(page_title="Agent 自主搜索助手", page_icon="🤖")
st.title("Agent 自主搜索助手")

with st.sidebar:
    st.header("设置")
    model = st.selectbox("模型选择", ["deepseek-chat","deepseek-reasoner"], index=0)
    max_turns = st.slider("最大轮数",1,10,5)

if st.button("清空对话"):
    st.session_state.messages = []
    st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []     

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("输入你的问题，我会用工具来回答..."):
    st.chat_message("user").write(prompt)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for m in st.session_state.messages:
        messages.append(m)

    messages.append({"role": "user", "content": prompt})

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.status("Agent 思考中...", expanded=True) as status:
        final_answer = None
        for step in agent_loop_stream(messages, model=model, max_turns=max_turns):
            if step["type"] == "tool_call":
                st.write(f"🔧 调用工具: **{step['name']}**")
                st.write(f"   参数: {json.dumps(step['args'], ensure_ascii=False)}")
                st.write(f"   结果: {step['result']}")
                st.divider()
            elif step["type"] == "answer":
                final_answer = step["content"]
                status.update(label="回答完成", state="complete")
            elif step["type"] == "error":
                final_answer = step["content"]
                status.update(label="执行错误", state="error")
    if final_answer:
        st.chat_message("assistant").write(final_answer)
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
    else:
        st.chat_message("assistant").write("抱歉，Agent 未能生成回答。")           