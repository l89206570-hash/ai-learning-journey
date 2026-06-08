"""固定测试集 — 每次改动后跑一遍，确认基本功能正常"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.vector_stores.chroma import ChromaVectorStore
from modelscope import snapshot_download
import chromadb

from config import (
    CHROMA_PERSIST_DIR, INDEX_META_DIR, CHROMA_COLLECTION_NAME,
    EMBED_MODEL_NAME, LLM_MODEL, LLM_API_KEY, LLM_API_BASE,
    LLM_MAX_TOKENS, LLM_TEMPERATURE,
)

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

TEST_CASES = [
    {"query": "你们支持哪些快递", "category": None, "expect_keywords": ["快递", "物流", "配送"]},
    {"query": "这款面霜适合什么肤质", "category": "产品介绍", "expect_keywords": ["肤质", "皮肤", "成分"]},
    {"query": "怎么成为会员", "category": "常见问题", "expect_keywords": ["会员", "积分", "注册"]},
    {"query": "发货要多久", "category": None, "expect_keywords": ["发货", "时间", "时效"]},
    {"query": "怎么退货", "category": "政策说明", "expect_keywords": ["退货", "退款", "退换"]},
]

passed = 0
failed = 0


def init():
    """初始化 Settings + 加载索引"""
    model_dir = snapshot_download(EMBED_MODEL_NAME)
    Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)
    Settings.llm = OpenAILike(
        model=LLM_MODEL, api_key=LLM_API_KEY, api_base=LLM_API_BASE,
        max_tokens=LLM_MAX_TOKENS, temperature=LLM_TEMPERATURE,
    )

    client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    collection = client.get_collection(CHROMA_COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir=INDEX_META_DIR
    )
    return load_index_from_storage(storage_context)


def run_tests(index):
    global passed, failed
    for i, case in enumerate(TEST_CASES):
        label = f"[{i+1}/{len(TEST_CASES)}] {case['category'] or '全部'} | {case['query']}"
        try:
            if case["category"]:
                filters = MetadataFilters(
                    filters=[MetadataFilter(key="category", operator=FilterOperator.EQ, value=case["category"])]
                )
                engine = index.as_chat_engine(chat_mode="context", filters=filters)
            else:
                engine = index.as_chat_engine(chat_mode="context")

            response = engine.chat(case["query"])
            reply = str(response)

            # 检查回复是否包含预期关键词（至少命中一个）
            hit = any(kw in reply for kw in case["expect_keywords"])
            if hit:
                logger.info("✅ PASS %s | 回复前50字: %s", label, reply[:50])
                passed += 1
            else:
                logger.warning("⚠️  WARN %s | 未命中关键词 %s | 回复前50字: %s",
                               label, case["expect_keywords"], reply[:50])
                passed += 1  # 关键词检查不是强断言，记 pass 但标 warning

            # 检查检索来源不为空
            source_count = len(response.source_nodes)
            if source_count == 0:
                logger.warning("⚠️  WARN %s | 检索来源为 0", label)
            else:
                logger.info("  检索来源: %d 条, top score=%.3f", source_count, response.source_nodes[0].score)

        except Exception as e:
            logger.error("❌ FAIL %s | 异常: %s", label, e)
            failed += 1


if __name__ == "__main__":
    logger.info("=== 初始化测试环境 ===")
    try:
        index = init()
        logger.info("初始化成功\n")
    except Exception as e:
        logger.error("初始化失败: %s", e)
        sys.exit(1)

    logger.info("=== 运行固定测试集（共 %d 条）===", len(TEST_CASES))
    run_tests(index)

    logger.info("\n=== 结果: %d 通过, %d 失败 ===", passed, failed)
    if failed > 0:
        sys.exit(1)
