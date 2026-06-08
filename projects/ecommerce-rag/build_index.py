"""建索引脚本 — 从 ecommerce_docs/ 读取文档 → 切分 → 存入 ChromaDB"""

import os
import sys
import logging
import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext, VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.vector_stores.chroma import ChromaVectorStore
from modelscope import snapshot_download

from config import (
    DOCS_DIR, DOC_FILES, CHROMA_PERSIST_DIR, INDEX_META_DIR,
    EMBED_MODEL_NAME, LLM_MODEL, LLM_API_KEY, LLM_API_BASE,
    LLM_MAX_TOKENS, LLM_TEMPERATURE, CHROMA_COLLECTION_NAME,
    CHUNK_SIZE, CHUNK_OVERLAP,
)

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ============================================================
# Step 1: 加载文档
# ============================================================
logger.info("开始加载文档...")
documents = []

for doc_cfg in DOC_FILES:
    filepath = os.path.join(DOCS_DIR, doc_cfg["filename"])
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        logger.error("文档文件不存在: %s，请检查 ecommerce_docs/ 目录", filepath)
        sys.exit(1)
    documents.append(
        Document(text=text, metadata={"category": doc_cfg["category"], "source": doc_cfg["source"]})
    )
    logger.info("  已加载: %s（%d 字）", doc_cfg["filename"], len(text))


# ============================================================
# Step 2: 切分 Node
# ============================================================
parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
nodes = parser.get_nodes_from_documents(documents)
logger.info("3 份文档 → 切成了 %d 个 Node", len(nodes))
for i, node in enumerate(nodes):
    logger.debug("[Node %d] category=%s, source=%s, text前30字=%s...",
                 i, node.metadata.get("category"), node.metadata.get("source"), node.text[:30])


# ============================================================
# Step 3: 配置 Embedding + LLM
# ============================================================
logger.info("下载 Embedding 模型: %s", EMBED_MODEL_NAME)
try:
    model_dir = snapshot_download(EMBED_MODEL_NAME)
except Exception as e:
    logger.error("ModelScope 模型下载失败: %s", e)
    logger.error("请检查网络连接或手动下载模型到本地")
    sys.exit(1)

Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)
Settings.llm = OpenAILike(
    model=LLM_MODEL,
    api_key=LLM_API_KEY,
    api_base=LLM_API_BASE,
    max_tokens=LLM_MAX_TOKENS,
    temperature=LLM_TEMPERATURE,
)
logger.info("Embedding + LLM 配置完成")


# ============================================================
# Step 4: 创建 ChromaDB 后端
# ============================================================
logger.info("连接 ChromaDB: %s", CHROMA_PERSIST_DIR)
chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

try:
    collection = chroma_client.get_collection(CHROMA_COLLECTION_NAME)
    logger.warning("  集合已存在，删除旧数据后重建")
    chroma_client.delete_collection(CHROMA_COLLECTION_NAME)
except Exception:
    pass  # 集合不存在，直接创建

collection = chroma_client.create_collection(name=CHROMA_COLLECTION_NAME)
logger.info("  集合就绪: %s", CHROMA_COLLECTION_NAME)

vectorstore = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vectorstore)


# ============================================================
# Step 5: 建索引 + 持久化
# ============================================================
logger.info("开始建索引（%d 个 Node）...", len(nodes))
try:
    index = VectorStoreIndex(nodes, storage_context=storage_context)
    index.storage_context.persist(persist_dir=INDEX_META_DIR)
except Exception as e:
    logger.error("建索引失败: %s", e)
    sys.exit(1)

logger.info("索引构建完成，ChromaDB 向量条数: %d", collection.count())
