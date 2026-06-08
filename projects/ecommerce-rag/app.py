"""电商客服 RAG — Streamlit 界面（ChromaDB 后端）"""

import os
import logging
import chromadb
import streamlit as st
from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.vector_stores.chroma import ChromaVectorStore
from modelscope import snapshot_download

from config import (
    CHROMA_PERSIST_DIR, INDEX_META_DIR, CHROMA_COLLECTION_NAME,
    EMBED_MODEL_NAME, LLM_MODEL, LLM_API_KEY, LLM_API_BASE,
    LLM_MAX_TOKENS, LLM_TEMPERATURE, CATEGORY_MAPPING,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ============================================================
# 启动检测：Embedding + LLM + ChromaDB 索引
# ============================================================

@st.cache_resource
def init_embed_model():
    logger.info("下载 Embedding 模型: %s", EMBED_MODEL_NAME)
    try:
        model_dir = snapshot_download(EMBED_MODEL_NAME)
        logger.info("Embedding 模型就绪")
        return HuggingFaceEmbedding(model_name=model_dir)
    except Exception as e:
        logger.error("ModelScope 模型下载失败: %s", e)
        st.error("Embedding 模型下载失败，请检查网络连接后刷新页面。")
        st.stop()


@st.cache_resource
def init_index():
    logger.info("连接 ChromaDB: %s", CHROMA_PERSIST_DIR)

    try:
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        collection = client.get_collection(CHROMA_COLLECTION_NAME)
        logger.info("ChromaDB 连接成功，集合内 %d 条记录", collection.count())
    except Exception as e:
        logger.error("ChromaDB 连接失败: %s", e)
        st.error("ChromaDB 连接失败。请先运行 `python build_index.py` 构建索引。")
        st.stop()

    try:
        vector_store = ChromaVectorStore(chroma_collection=collection)
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, persist_dir=INDEX_META_DIR
        )
        index = load_index_from_storage(storage_context)
        logger.info("索引加载成功")
        return index
    except Exception as e:
        logger.error("索引加载失败: %s", e)
        st.error("索引加载失败，请先运行 `python build_index.py` 后刷新页面。")
        st.stop()


Settings.embed_model = init_embed_model()
Settings.llm = OpenAILike(
    model=LLM_MODEL,
    api_key=LLM_API_KEY,
    api_base=LLM_API_BASE,
    max_tokens=LLM_MAX_TOKENS,
    temperature=LLM_TEMPERATURE,
)
logger.info("Embedding + LLM 配置完成")

index = init_index()


# ============================================================
# Sidebar — 品类筛选 + 重置按钮
# ============================================================
st.set_page_config(page_title="电商客服 RAG", page_icon="🤖")
st.title("🛒 电商智能客服")

with st.sidebar:
    st.subheader("🏷️ 品类筛选")
    catgory = st.radio("选择品类", list(CATEGORY_MAPPING.keys()))
    selected_category = CATEGORY_MAPPING[catgory]

    st.divider()
    if st.button("重置对话"):
        if "chat" in st.session_state:
            st.session_state["chat"].reset()
        st.session_state["messages"] = []
        logger.info("用户点击重置对话")
        st.rerun()


# ============================================================
# Session State 初始化
# ============================================================
if "chat" not in st.session_state:
    try:
        st.session_state["chat"] = index.as_chat_engine(chat_mode="context")
        logger.info("chat_engine 初始化完成")
    except Exception as e:
        logger.error("chat_engine 创建失败: %s", e)
        st.error("会话引擎创建失败，请刷新页面重试。")
        st.stop()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

with st.expander("对话历史概览"):
    for msg in st.session_state["chat"].chat_history:
        st.write(f"{msg.role.value}: {msg.content[:30]}...")


# ============================================================
# 品类切换检测
# ============================================================
current_category = st.session_state.get("current_category", None)
if selected_category != current_category:
    logger.info("品类切换: %s → %s，重建 chat_engine", current_category, selected_category)
    st.session_state["current_category"] = selected_category
    try:
        if selected_category is None:
            st.session_state["chat"] = index.as_chat_engine(chat_mode="context")
        else:
            filters = MetadataFilters(
                filters=[MetadataFilter(key="category", operator=FilterOperator.EQ, value=selected_category)]
            )
            st.session_state["chat"] = index.as_chat_engine(chat_mode="context", filters=filters)
        logger.info("chat_engine 重建完成")
    except Exception as e:
        logger.error("chat_engine 重建失败: %s", e)
        st.error("品类切换失败，请重试。")
        st.stop()
    st.rerun()


# ============================================================
# 渲染历史消息 + 对话交互
# ============================================================
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("请输入您的问题")
if user_input:
    logger.info("收到查询请求，长度 %d 字", len(user_input))
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    try:
        response = st.session_state["chat"].stream_chat(user_input)
        with st.chat_message("assistant"):
            full_text = st.write_stream(response.response_gen)
        st.session_state["messages"].append({"role": "assistant", "content": full_text})
        logger.info("查询完成，回复长度 %d 字", len(full_text))
    except Exception as e:
        logger.error("API 调用失败: %s", e)
        with st.chat_message("assistant"):
            error_msg = "抱歉，AI 服务暂时不可用，请稍后重试。"
            st.error(error_msg)
        st.session_state["messages"].append({"role": "assistant", "content": error_msg})

    with st.expander("🔍 检索来源", expanded=False):
        for i, node in enumerate(response.source_nodes):
            meta = node.node.metadata
            st.caption(f"[来源 {i}] score={node.score:.3f} | "
                       f"category={meta.get('category')} | source={meta.get('source')}")
