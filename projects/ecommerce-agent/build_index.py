"""建索引脚本 — 从 ecommerce_docs/ 读取文档 → 切分 → 存入 ChromaDB

使用方式：
  python build_index.py
"""

import os
import sys
import logging
import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext, VectorStoreIndex, Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from modelscope import snapshot_download

from config import (
    DOCS_DIR, DOC_FILES, CHROMA_PERSIST_DIR, INDEX_META_DIR,
    EMBED_MODEL_NAME, CHROMA_COLLECTION_NAME,
    CHUNK_SIZE, CHUNK_OVERLAP,
)

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    # Step 1: 加载文档
    logger.info("Loading documents...")
    documents = []
    for doc_cfg in DOC_FILES:
        filepath = os.path.join(DOCS_DIR, doc_cfg["filename"])
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            logger.error("Document not found: %s", filepath)
            sys.exit(1)
        documents.append(
            Document(text=text, metadata={"category": doc_cfg["category"], "source": doc_cfg["source"]})
        )
        logger.info("  Loaded: %s (%d chars)", doc_cfg["filename"], len(text))

    # Step 2: 切分
    parser = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    nodes = parser.get_nodes_from_documents(documents)
    logger.info("Split into %d nodes", len(nodes))

    # Step 3: Embedding
    logger.info("Downloading embedding model: %s", EMBED_MODEL_NAME)
    try:
        model_dir = snapshot_download(EMBED_MODEL_NAME)
    except Exception as e:
        logger.error("Model download failed: %s", e)
        sys.exit(1)
    Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)
    logger.info("Embedding model ready")

    # Step 4: ChromaDB
    logger.info("Connecting ChromaDB: %s", CHROMA_PERSIST_DIR)
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

    try:
        existing = chroma_client.get_collection(CHROMA_COLLECTION_NAME)
        logger.warning("Collection exists, deleting old data")
        chroma_client.delete_collection(CHROMA_COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.create_collection(name=CHROMA_COLLECTION_NAME)
    logger.info("Collection ready: %s", CHROMA_COLLECTION_NAME)

    vectorstore = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vectorstore)

    # Step 5: 建索引
    logger.info("Building index (%d nodes)...", len(nodes))
    try:
        index = VectorStoreIndex(nodes, storage_context=storage_context)
        index.storage_context.persist(persist_dir=INDEX_META_DIR)
    except Exception as e:
        logger.error("Build index failed: %s", e)
        sys.exit(1)

    logger.info("Index built, %d vectors in ChromaDB", collection.count())


if __name__ == "__main__":
    main()
