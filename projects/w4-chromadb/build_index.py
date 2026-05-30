"""W4 Day 2: 电商客服 ChromaDB 建索引 — 你来实现

和 W3 day7_build_index.py 的区别：
  W3: 向量存 JSON 文件（SimpleVectorStore，LlamaIndex 默认）
  W4: 向量存 ChromaDB（数据库引擎），需要 ChromaVectorStore 桥接

参考：
  - W3 day7_build_index.py（文档加载 + 切分 + Settings 配置）
  - W4 day1_chromadb_llamaindex.py Part 2（ChromaDB 建索引流程）
"""
import os
import chromadb
from dotenv import load_dotenv
from llama_index.core import (
    Settings,
    StorageContext,
    VectorStoreIndex,
    Document,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from llama_index.vector_stores.chroma import ChromaVectorStore
from modelscope import snapshot_download

load_dotenv()

# ============================================================
# TODO ①: 加载文档 + 切分 + 配置 Settings
# ============================================================
# 和 W3 day7_build_index.py 完全一样：
#   - 读 ecommerce_docs/ 下 3 个 txt → Document(text=..., metadata={...})
#   - SentenceSplitter(chunk_size=512, chunk_overlap=50) 切分
#   - snapshot_download("BAAI/bge-small-zh-v1.5") → HuggingFaceEmbedding
#   - OpenAILike(model="deepseek-v4-flash", api_base="https://api.deepseek.com/beta", ...)
#   - 打印切分结果

doc_faq = Document(text=open(os.path.join("ecommerce_docs", "faq.txt"), "r", encoding="utf-8").read(),
    metadata={"category": "常见问题", "source": "faq.txt"})

doc_product = Document(text=open(os.path.join("ecommerce_docs", "products.txt"), "r", encoding="utf-8").read(),
    metadata={"category": "产品介绍", "source": "products.txt"})

doc_policy = Document(text=open(os.path.join("ecommerce_docs", "policy.txt"), "r", encoding="utf-8").read(),
    metadata={"category": "政策说明", "source": "policy.txt"})

documents = [doc_faq, doc_product, doc_policy]

parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = parser.get_nodes_from_documents(documents)
print(f"3 份文档 → 切成了 {len(nodes)} 个 Node")
print("\n=== Node 元数据一览 ===")
for i, node in enumerate(nodes):
    print(f"[Node {i}] category={node.metadata.get('category')}, "
          f"source={node.metadata.get('source')}, "
          f"text前30字={node.text[:30]}...")

model_dir = snapshot_download("BAAI/bge-small-zh-v1.5")
Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)
Settings.llm = OpenAILike(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base="https://api.deepseek.com/beta", 
    max_tokens=1024,
    temperature=0.2,
)




# ============================================================
# TODO ②: 创建 ChromaDB 后端（和 W3 的关键区别！）
# ============================================================
# Step 1: chromadb.PersistentClient(path="./chroma_store_ecommerce")
# Step 2: client.create_collection(name="ecommerce_knowledge")
# Step 3: ChromaVectorStore(chroma_collection=collection) 包装
# Step 4: StorageContext.from_defaults(vector_store=vector_store)
#
# 提示：参考 day1_chromadb_llamaindex.py 的 Part 2

chroma_client = chromadb.PersistentClient(path="./chroma_store_ecommerce")
collection = chroma_client.create_collection(name="ecommerce_knowledge")
vectorstore = ChromaVectorStore(chroma_collection=collection)
storage_context = StorageContext.from_defaults(vector_store=vectorstore)


# ============================================================
# TODO ③: 建索引 + 持久化
# ============================================================
# - VectorStoreIndex(nodes, storage_context=storage_context)
# - index.storage_context.persist(persist_dir="./chroma_store_ecommerce/index_meta")
# - 打印 collection.count() 确认入库条数
#
# 注意：ChromaDB 自动存向量（SQLite），persist() 只存索引元数据（docstore/index_store）
#       两者各管各的，加载时两个都要

index = VectorStoreIndex(nodes, storage_context=storage_context)
index.storage_context.persist(persist_dir="./chroma_store_ecommerce/index_meta")
print(f"ChromaDB 中的向量条数: {collection.count()}")
