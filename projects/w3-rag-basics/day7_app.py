"""Day 7: 电商客服 RAG 综合实战 — 你来实现 """
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from modelscope import snapshot_download
from dotenv import load_dotenv
import os
import streamlit as st

# ============================================================
# A. 全局初始化
# ============================================================
load_dotenv()

# TODO ①: 下载嵌入模型、配置 Settings.embed_model + Settings.llm
# 参考 day6_build_index.py 的写法

model_dir = snapshot_download("BAAI/bge-small-zh-v1.5")
Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)
Settings.llm = OpenAILike(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base="https://api.deepseek.com/beta",
    max_tokens=1024,
    temperature=0.2,
    )

# TODO ②: 加载已持久化的索引
# 提示: StorageContext.from_defaults(persist_dir="./index_storage_day7")
#       load_index_from_storage(...)

storage_context = StorageContext.from_defaults(persist_dir="./index_storage_day7")
index = load_index_from_storage(storage_context)

# ============================================================
# B. Sidebar
# ============================================================
st.set_page_config(page_title="电商客服 RAG", page_icon="🤖")
st.title("🛒 电商智能客服")

with st.sidebar:
    st.subheader("🏷️ 品类筛选")

    # TODO ③: 用 st.radio 创建品类选择器
    # 选项: ["全部", "产品", "FAQ", "售后"]
    # 提示: 把"全部"映射成 None，其他映射成对应的 metadata category 值
    #       metadata 里的 category 字段值是: "产品"、"常见问题"、"政策"
    #       所以需要一张映射表: {"全部": None, "产品": "产品", "FAQ": "常见问题", "售后": "政策"}

    catgory = st.radio("选择品类", ["全部", "产品", "FAQ", "售后"])
    category_mapping = {
        "全部": None,
        "产品": "产品",
        "FAQ": "常见问题",  
        "售后": "政策",
    }
    selected_category = category_mapping[catgory]
    
    st.divider()

    # TODO ④: 重置对话按钮
    # 点击后: chat.reset() + 清空消息列表 + st.rerun()
    # 提示: chat_engine 存在 st.session_state["chat"] 里

    if st.button("🔄 重置对话"):
        if "chat" in st.session_state:
            st.session_state["chat"].reset()
        st.session_state["messages"] = []
        st.rerun()




# ============================================================
# C. Main: 对话区
# ============================================================

# TODO ⑥: 初始化 session_state
# 需要维护两个东西:
#   "chat" — chat_engine 实例（首次创建用 index.as_chat_engine(chat_mode="context")）
#   "messages" — 消息列表 [{"role": "user/assistant", "content": "..."}]
# 提示: if "xxx" not in st.session_state 模式

if "chat" not in st.session_state:
    st.session_state["chat"] = index.as_chat_engine(chat_mode="context")
if "messages" not in st.session_state:
    st.session_state["messages"] = []

    # TODO ⑤: 展示对话历史概览
    # 从 st.session_state["chat"].chat_history 里取历史
    # 用 st.caption 展示每条的前 30 字 + 角色图标

with st.expander("📜 对话历史概览", expanded=False):
    for msg in st.session_state["chat"].chat_history:
        icon = "👤" if msg.role.value == "user" else "🤖"
        st.caption(f"{icon} {msg.content[:30]}")

            
# TODO ⑦: 品类切换检测
# 思路: session_state 里存一个 "current_category"
#       每次渲染时对比 radio 选的值 → 变了就重建 chat_engine + st.rerun()
#       chat_engine 重建时: category=None 不加 filter / category=某值 加 MetadataFilters

current_category = st.session_state.get("current_category")
if selected_category != current_category:
    st.session_state["current_category"] = selected_category
    if selected_category is None:
        st.session_state["chat"] = index.as_chat_engine(chat_mode="context")
    else:
        filters = MetadataFilters(
            filters=[MetadataFilter(key="category", operator=FilterOperator.EQ, value=selected_category)]
        )
        st.session_state["chat"] = index.as_chat_engine(chat_mode="context", filters=filters)
    st.rerun()

# TODO ⑧: 展示历史消息
# 遍历 st.session_state["messages"]，用 st.chat_message(role) + st.write(content)

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# TODO ⑨: 接收用户输入
# user_input = st.chat_input("...")
# 如果 user_input 非空:
#   1. 把用户消息加到 messages 列表 + 渲染
#   2. 调 chat.stream_chat(user_input) 拿 response
#   3. 用 st.write_stream(response.response_gen) 流式输出
#   4. 把 AI 回复加到 messages 列表
#   5. (加分项) 用 st.expander 展示 response.source_nodes 检索来源

usr_input = st.chat_input("请输入您的问题...")
if usr_input:
    st.session_state["messages"].append({"role": "user", "content": usr_input})
    with st.chat_message("user"):
        st.write(usr_input)

    response = st.session_state["chat"].stream_chat(usr_input)
    with st.chat_message("assistant"):
      full_text = st.write_stream(response.response_gen)
    st.session_state["messages"].append({"role": "assistant", "content": full_text})

    with st.expander("🔍 检索来源", expanded=False):
        for i, node in enumerate(response.source_nodes):
            meta = node.node.metadata
            st.caption(f"[来源 {i}] score={node.score:.3f} | "
                       f"category={meta.get('category')} | source={meta.get('source')}")
