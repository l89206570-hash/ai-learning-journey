"""W4 Day 2: 电商客服 Streamlit 界面（ChromaDB 后端）— 你来实现

和 W3 day7_app.py 的区别：
  W3: load_index_from_storage(persist_dir) — 向量从 JSON 文件全量加载
  W4: 先连 ChromaDB Collection，再 load_index_from_storage — 向量从数据库按需读取

参考：
  - W3 day7_app.py（完整的 Streamlit 对话界面逻辑）
  - W4 day1_chromadb_llamaindex.py Part 4（从 ChromaDB 恢复索引）
"""
import os
import chromadb
import streamlit as st
from dotenv import load_dotenv
from llama_index.core import (
    Settings,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.vector_stores import (
    MetadataFilters,
    MetadataFilter,
    FilterOperator,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.vector_stores.chroma import ChromaVectorStore
from modelscope import snapshot_download

load_dotenv()

# ============================================================
# TODO ①: 配置 Settings + 从 ChromaDB 加载索引
# ============================================================
# Settings 部分和 W3 一样：
#   - snapshot_download("BAAI/bge-small-zh-v1.5") → HuggingFaceEmbedding
#   - OpenAILike(model="deepseek-v4-flash", api_base="https://api.deepseek.com/beta", ...)
#
# 加载索引部分（和 W3 不同！）：
#   - chromadb.PersistentClient(path="./chroma_store_ecommerce")
#   - client.get_collection("ecommerce_knowledge")
#   - ChromaVectorStore(chroma_collection=collection)
#   - StorageContext.from_defaults(vector_store=..., persist_dir="./chroma_store_ecommerce/index_meta")
#   - load_index_from_storage(storage_context)
#
# 提示：参考 day1_chromadb_llamaindex.py Part 4

model_dir = snapshot_download("BAAI/bge-small-zh-v1.5")
Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)
Settings.llm = OpenAILike(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base="https://api.deepseek.com/beta",
    max_tokens=1024,
    temperature=0.2,
    ) 

client = chromadb.PersistentClient(path="./chroma_store_ecommerce")
collection = client.get_collection("ecommerce_knowledge")
vector_store = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store, persist_dir="./chroma_store_ecommerce/index_meta")
index = load_index_from_storage(storage_context)

# ============================================================
# TODO ②: Sidebar — 品类筛选 + 重置按钮
# ============================================================
# 和 W3 day7_app.py 完全一样：
#   - st.set_page_config + st.title
#   - category_mapping = {"全部": None, "产品": "产品", "FAQ": "常见问题", "售后": "政策"}
#   - st.radio 选择品类
#   - 重置按钮：chat.reset() + 清空 messages + st.rerun()

st.set_page_config(page_title="电商客服 RAG", page_icon="🤖")
st.title("🛒 电商智能客服")
with st.sidebar:
    st.subheader("🏷️ 品类筛选")
    category_mapping = {
        "全部": None,
        "产品": "产品介绍",
        "FAQ": "常见问题",
        "售后": "政策说明",
    }
    catgory = st.radio("选择品类", list(category_mapping.keys()))
    selected_category = category_mapping[catgory]
    
    st.divider()
    if st.button("重置对话"):
        if "chat" in st.session_state:
            st.session_state["chat"].reset()
        st.session_state["messages"] = []
        st.rerun()



# ============================================================
# TODO ③: Session State 初始化 + 对话历史概览
# ============================================================
# - if "chat" not in st.session_state → index.as_chat_engine(chat_mode="context")
# - if "messages" not in st.session_state → []
# - expander 展示 chat.chat_history（msg.role.value / msg.content[:30]）

if "chat" not in st.session_state:
    st.session_state["chat"] = index.as_chat_engine(chat_mode="context")
if "messages" not in st.session_state:
        st.session_state["messages"] = []
with st.expander("对话历史概览"):
    for msg in st.session_state["chat"].chat_history:
        st.write(f"{msg.role.value}: {msg.content[:30]}...")

# ============================================================
# TODO ④: 品类切换检测
# ============================================================
# 和 W3 完全一样：
#   - session_state["current_category"] 存上次品类
#   - 和 selected_category 对比 → 变了就重建 chat_engine
#   - None → 不加 filter；某值 → MetadataFilters(...)

current_category = st.session_state.get("current_category", None)
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
# ============================================================
# TODO ⑤: 渲染历史消息 + 对话交互
# ============================================================
# - 遍历 messages，st.chat_message + st.write
# - st.chat_input 接收输入
# - chat.stream_chat(user_input) → st.write_stream(response.response_gen)
# - expander 展示 source_nodes（score + category + source）

for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("请输入您的问题")
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    response = st.session_state["chat"].stream_chat(user_input)
    with st.chat_message("assistant"):
         full_text =st.write_stream(response.response_gen)
    st.session_state["messages"].append({"role": "assistant", "content": full_text})
    
    with st.expander("🔍 检索来源", expanded=False):
        for i, node in enumerate(response.source_nodes):
            meta = node.node.metadata
            st.caption(f"[来源 {i}] score={node.score:.3f} | "
                       f"category={meta.get('category')} | source={meta.get('source')}")
