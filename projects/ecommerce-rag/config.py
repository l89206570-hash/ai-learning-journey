"""环境变量配置管理 — 所有配置项集中在这里，禁止在其他文件中硬编码"""

import os

# -------- 目录路径 --------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(PROJECT_ROOT, "ecommerce_docs")
CHROMA_PERSIST_DIR = os.path.join(PROJECT_ROOT, "chroma_store_ecommerce")
INDEX_META_DIR = os.path.join(CHROMA_PERSIST_DIR, "index_meta")

# -------- Embedding 模型 --------
EMBED_MODEL_NAME = os.getenv("EMBED_MODEL_NAME", "BAAI/bge-small-zh-v1.5")

# -------- LLM --------
LLM_MODEL = os.getenv("LLM_MODEL", "deepseek-v4-flash")
LLM_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
LLM_API_BASE = os.getenv("LLM_API_BASE", "https://api.deepseek.com/beta")
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "1024"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))

# -------- ChromaDB --------
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "ecommerce_knowledge")

# -------- 文档切分 --------
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))

# -------- 知识库文件列表 --------
DOC_FILES = [
    {"filename": "faq.txt", "category": "常见问题", "source": "faq.txt"},
    {"filename": "products.txt", "category": "产品介绍", "source": "products.txt"},
    {"filename": "policy.txt", "category": "政策说明", "source": "policy.txt"},
]

# -------- 品类映射（业务配置）--------
CATEGORY_MAPPING = {
    "全部": None,
    "产品": "产品介绍",
    "FAQ": "常见问题",
    "售后": "政策说明",
}
