"""跨境电商 MCP Server — 暴露业务工具给 LangGraph Agent

工具清单：
  1. search_knowledge — 搜索商品/FAQ/政策知识库（ChromaDB）
  2. check_order_status — 模拟查询订单物流状态
  3. check_membership — 查询会员等级和权益

运行方式（stdio transport，由 Agent 自动启动）：
  python mcp_server.py
"""

import sys
import os
import logging
import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from modelscope import snapshot_download
from mcp.server.fastmcp import FastMCP

from config import (
    CHROMA_PERSIST_DIR, INDEX_META_DIR, CHROMA_COLLECTION_NAME,
    EMBED_MODEL_NAME, CATEGORY_MAPPING,
)

load_dotenv()

# 抑制 modelscope 日志输出到 stdout，避免干扰 MCP JSON-RPC 协议
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logging.getLogger("modelscope").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

mcp = FastMCP("电商客服 MCP Server")

# ============================================================
# 初始化 ChromaDB + Embedding（Server 启动时加载）
# ============================================================

def _init_chroma():
    """连接 ChromaDB，返回 LlamaIndex 可查询的 index 对象"""
    logger.info("Connecting ChromaDB: %s", CHROMA_PERSIST_DIR)
    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_collection(CHROMA_COLLECTION_NAME)
    logger.info("ChromaDB connected, %d records", collection.count())

    # 重定向 stdout 避免 modelscope/HF 日志干扰 MCP JSON-RPC 协议
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        model_dir = snapshot_download(EMBED_MODEL_NAME)
        Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)
    finally:
        sys.stdout = old_stdout

    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir=INDEX_META_DIR
    )
    index = load_index_from_storage(storage_context)
    logger.info("Index loaded, ready for queries")
    return index


# 全局初始化（MCP Server 启动时执行一次）
_index = _init_chroma()


# ============================================================
# Tool 1: 知识库搜索
# ============================================================

@mcp.tool()
def search_knowledge(query: str, category: str = "全部") -> str:
    """搜索电商知识库（商品/FAQ/售后政策）。query 用中文关键词，category 可选：全部/产品/FAQ/售后"""
    category_value = CATEGORY_MAPPING.get(category, None)

    if category_value:
        filters = MetadataFilters(
            filters=[MetadataFilter(key="category", operator=FilterOperator.EQ, value=category_value)]
        )
        retriever = _index.as_retriever(similarity_top_k=3, filters=filters)
    else:
        retriever = _index.as_retriever(similarity_top_k=3)

    nodes = retriever.retrieve(query)

    if not nodes:
        return "未找到相关知识。请尝试更换关键词或选择不同品类。"

    results = []
    for i, node in enumerate(nodes):
        score = node.score if hasattr(node, 'score') else 0
        meta = node.metadata
        results.append(
            f"[{i+1}] score={score:.3f} | {meta.get('category', '')} | {meta.get('source', '')}\n"
            f"{node.text[:200]}..."
        )
    return "\n\n".join(results)


# ============================================================
# Tool 2: 订单查询
# ============================================================

# 模拟订单数据
_ORDERS = {
    "JD20260615001": {"status": "已发货", "carrier": "顺丰", "tracking": "SF1234567890", "eta": "2026-06-17"},
    "JD20260614002": {"status": "已签收", "carrier": "中通", "tracking": "ZT9876543210", "eta": "已送达"},
    "JD20260613003": {"status": "待发货", "carrier": "—", "tracking": "—", "eta": "预计 48h 内发货"},
    "JD20260612004": {"status": "退货中", "carrier": "圆通", "tracking": "YT5555555555", "eta": "等待商家签收"},
}

@mcp.tool()
def check_order_status(order_id: str) -> str:
    """查询订单状态和物流信息。输入订单号（如 JD20260615001），返回订单状态、快递公司、运单号、预计到达时间。"""
    order = _ORDERS.get(order_id)
    if not order:
        return f"未找到订单 {order_id}。已知订单号：{', '.join(_ORDERS.keys())}"
    return (
        f"订单 {order_id}：\n"
        f"  状态：{order['status']}\n"
        f"  快递：{order['carrier']}\n"
        f"  运单号：{order['tracking']}\n"
        f"  预计到达：{order['eta']}"
    )


# ============================================================
# Tool 3: 会员权益查询
# ============================================================

_MEMBERSHIP = {
    "银卡会员": "年消费 ≥ 2000 元。权益：退货免运费。",
    "金卡会员": "年消费 ≥ 5000 元。权益：退货免运费 + 15 天无理由退货。",
    "钻石会员": "年消费 ≥ 10000 元。权益：退货免运费 + 30 天无理由退货 + 优先质检。",
}

@mcp.tool()
def check_membership(member_level: str) -> str:
    """查询会员等级对应的权益。输入会员等级（银卡会员/金卡会员/钻石会员），返回权益详情。"""
    level = member_level.strip()
    result = _MEMBERSHIP.get(level)
    if result:
        return f"【{level}】{result}"
    return f"未找到「{level}」等级信息。已知等级：{', '.join(_MEMBERSHIP.keys())}"


# ============================================================
# 启动 Server
# ============================================================

if __name__ == "__main__":
    print("电商 MCP Server 启动中...", file=sys.stderr)
    mcp.run()
