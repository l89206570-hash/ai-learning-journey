"""
W4 Day 1 — ChromaDB + LlamaIndex 集成

学习目标：
  1. 用 ChromaDB 替代 LlamaIndex 默认的本地文件存储
  2. 理解集成的关键组件：VectorStore → StorageContext → Index
  3. 对比 ChromaDB 模式和本地文件模式的差异
  4. 掌握在实际项目中如何选型

核心认知：
  LlamaIndex 的架构是分层的：
    Document → Node → Embedding → VectorStore（存向量）→ Index（组织检索）
                                      ↑
                              这里是可替换的！
  默认用 SimpleVectorStore（内存/JSON文件），换成 ChromaDB 就是换这个环节。
  其他部分（分块、嵌入模型、LLM、检索逻辑）完全不变。

和 W3 的代码对比：
  W3: 索引存为 JSON/.bin 文件 → load_index_from_storage() 恢复
  W4: 索引向量存在 ChromaDB → 直接连 ChromaDB Collection 取数据
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("../.env")

# =============================================================================
# Part 1: 理解架构差异 — ChromaDB 在 LlamaIndex 里的位置
# =============================================================================
# W3 的存储链路：
#   Document → Node → [嵌入模型] → 向量 → SimpleVectorStore → JSON/.bin 文件
#                                               ↑ 默认用内存字典存向量
#
# W4 的存储链路：
#   Document → Node → [嵌入模型] → 向量 → ChromaVectorStore → ChromaDB 数据库
#                                               ↑ 换成 ChromaDB 引擎
#
# 关键区别：
#   - SimpleVectorStore: 全量加载到内存，存盘就是 pickle 序列化 → 文档量大时内存爆炸
#   - ChromaDB: 数据库引擎管理，按需从磁盘读 → 支持百万级文档
#   - 查询性能: 小数据量差不多，大数据量 ChromaDB 快 N 倍（有索引优化）

print("=" * 60)
print("Part 1: 准备嵌入模型 & LLM")
print("=" * 60)

from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike

# --- 嵌入模型：用 W3 ModelScope 缓存的本地 BGE 中文模型 ---
BGE_MODEL_PATH = os.path.expanduser(
    "~/.cache/modelscope/hub/models/BAAI/bge-small-zh-v1___5"
)

embed_model = HuggingFaceEmbedding(
    model_name=BGE_MODEL_PATH,  # 从本地路径加载，不需要网络
)
Settings.embed_model = embed_model

# --- LLM：复用 DeepSeek V4 ---
# OpenAILike 不校验模型名白名单，适合 DeepSeek/千问等兼容接口
Settings.llm = OpenAILike(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base="https://api.deepseek.com/beta",
    context_window=128000,  # DeepSeek V4 的上下文窗口
    max_tokens=4096,
    is_chat_model=True,
)

print(f"嵌入模型: {embed_model.model_name}")
print(f"LLM: DeepSeek V4 Flash")

# =============================================================================
# Part 2: 用 ChromaDB 作为 LlamaIndex 的向量存储
# =============================================================================

print("\n" + "=" * 60)
print("Part 2: 构建 ChromaDB-backed 索引")
print("=" * 60)

import chromadb
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    Document,
    Settings,
)
from llama_index.vector_stores.chroma import ChromaVectorStore

# ---------------------------------------------------------------------------
# 2.1 创建 ChromaDB Collection → 包装成 LlamaIndex 的 VectorStore
# ---------------------------------------------------------------------------
# 这一步是把两个世界的对象桥接起来：
#   ChromaDB 世界: Client → Collection
#   LlamaIndex 世界: ChromaVectorStore(collection) → StorageContext → VectorStoreIndex

CHROMA_PATH = "./chroma_store_llamaindex"
if os.path.exists(CHROMA_PATH):
    shutil.rmtree(CHROMA_PATH)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# 如果 Collection 已存在可以先删再建（相当于 W3 的重新 build_index）
collection = chroma_client.create_collection(
    name="ecommerce_knowledge",
    metadata={"description": "电商知识库 — W4 Day 1"},
)

# 包装成 LlamaIndex 认识的 VectorStore
vector_store = ChromaVectorStore(chroma_collection=collection)

# 把 VectorStore 放入 StorageContext
# StorageContext 是 LlamaIndex 的"存储配置中心"——告诉它向量存在哪、文档存在哪
storage_context = StorageContext.from_defaults(vector_store=vector_store)

print(f"ChromaDB Collection: {collection.name}")
print(f"VectorStore 类型: {type(vector_store).__name__}")

# ---------------------------------------------------------------------------
# 2.2 加载文档 → 建索引 → 向量自动写入 ChromaDB
# ---------------------------------------------------------------------------
# 和 W3 完全一样的流程，唯一区别是 storage_context 指向了 ChromaDB
# 建索引时 LlamaIndex 会自动把向量写到 ChromaDB 里

documents = [
    Document(
        text="我们支持7天无理由退换货，只要商品不影响二次销售即可办理。定制类商品除外。",
        metadata={"category": "退换货", "type": "policy", "priority": "high"},
    ),
    Document(
        text="普通快递满199元包邮，不满199元支付8元运费。顺丰快递满299元包邮。",
        metadata={"category": "物流", "type": "shipping", "priority": "high"},
    ),
    Document(
        text="会员积分规则：每消费1元获得1积分，100积分可抵扣1元。生日当月双倍积分。",
        metadata={"category": "会员", "type": "benefit", "priority": "medium"},
    ),
    Document(
        text="大客户批发价格请咨询客服热线 400-888-1234，量大从优。",
        metadata={"category": "销售", "type": "channel", "priority": "medium"},
    ),
    Document(
        text="所有商品均支持花呗分期，满500元可享3期免息，满1000元可享6期免息。",
        metadata={"category": "支付", "type": "payment", "priority": "low"},
    ),
]

# 建索引——LlamaIndex 自动：分块 → 向量化 → 存入 ChromaDB
index = VectorStoreIndex.from_documents(
    documents,
    storage_context=storage_context,
    show_progress=True,
)

print(f"\n索引进完。ChromaDB 里存了多少条? {collection.count()} 条")
# 注意：数量可能 > 5，因为 LlamaIndex 会把 Document 切分成 Node

# =============================================================================
# Part 3: 查询 —— 和 W3 完全一样的调用方式
# =============================================================================

print("\n" + "=" * 60)
print("Part 3: 语义搜索查询")
print("=" * 60)

# 和 W3 一样用 as_query_engine() —— 底层自动从 ChromaDB 检索
query_engine = index.as_query_engine(similarity_top_k=3)

# ---------------------------------------------------------------------------
# 3.1 基础查询
# ---------------------------------------------------------------------------
question = "如何获得包邮？"
response = query_engine.query(question)

print(f"问题: {question}")
print(f"回答: {response}")

# 查看检索来源
print(f"\n检索到的来源片段:")
for i, node in enumerate(response.source_nodes):
    print(f"  #{i+1} (score={node.score:.4f}) | {node.node.metadata.get('category', 'N/A')}")
    print(f"      {node.node.text[:80]}...")

# ---------------------------------------------------------------------------
# 3.2 带元数据过滤的查询
# ---------------------------------------------------------------------------
print("\n--- 带元数据过滤 ---")
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
)

# 只搜会员相关的
filters = MetadataFilters(
    filters=[
        MetadataFilter(key="category", value="会员", operator=FilterOperator.EQ),
    ]
)

filtered_engine = index.as_query_engine(
    similarity_top_k=3,
    filters=filters,
)

question2 = "积分有什么用？"
response2 = filtered_engine.query(question2)

print(f"问题: {question2}")
print(f"过滤条件: category='会员'")
print(f"回答: {response2}")
print(f"检索到 {len(response2.source_nodes)} 条相关片段")

# =============================================================================
# Part 4: 重新加载 —— ChromaDB 的 build once, load many
# =============================================================================

print("\n" + "=" * 60)
print("Part 4: 从 ChromaDB 恢复索引（不重新向量化）")
print("=" * 60)

# Step 1: 先持久化索引元数据（docstore + index_store 等）
#         这一步只存"索引有哪些 Node"的结构信息，不重新算向量。
#         向量已经通过 ChromaDB 自动持久化了。
PERSIST_DIR_INDEX = "./chroma_store_llamaindex/index_meta"
index.storage_context.persist(persist_dir=PERSIST_DIR_INDEX)
print(f"索引元数据已持久化到: {PERSIST_DIR_INDEX}")

# Step 2: 模拟"重启"——重新连接 ChromaDB + 从磁盘恢复索引结构
from llama_index.core import load_index_from_storage

client2 = chromadb.PersistentClient(path=CHROMA_PATH)
collection2 = client2.get_collection("ecommerce_knowledge")
vector_store2 = ChromaVectorStore(chroma_collection=collection2)

# 恢复时同时指定向量存储（ChromaDB）和元数据路径
storage_context2 = StorageContext.from_defaults(
    vector_store=vector_store2,
    persist_dir=PERSIST_DIR_INDEX,
)
index2 = load_index_from_storage(storage_context=storage_context2)

engine2 = index2.as_query_engine(similarity_top_k=3)
response3 = engine2.query("快递怎么收费？")

print(f"问题: 快递怎么收费？")
print(f"回答: {response3}")
print(f"\n注意：加载时没有重新 embedding，向量直接从 ChromaDB 读取")
print(f"对比 W3：W3 也要手动 persist + load，但 ChromaDB 的恢复是数据库级别的")

# =============================================================================
# Part 5: 对比总结
# =============================================================================

print("\n" + "=" * 60)
print("Part 5: ChromaDB vs SimpleVectorStore 对比")
print("=" * 60)

print("""
┌────────────────────┬─────────────────────────┬─────────────────────────┐
│ 维度               │ SimpleVectorStore (W3)  │ ChromaDB (W4)           │
├────────────────────┼─────────────────────────┼─────────────────────────┤
│ 存储格式           │ JSON + .bin 文件        │ SQLite + Parquet 文件   │
│ 加载方式           │ 全量加载到内存          │ 按需读取，索引加速       │
│ 适合文档量         │ < 1000                  │ 1000 ~ 百万级           │
│ 并发查询           │ 不支持                  │ 支持多客户端同时查       │
│ 元数据过滤         │ LlamaIndex 层面过滤     │ 数据库层面过滤（更快）   │
│ 增量写入           │ 需要 full rebuild       │ 直接 add，实时可见       │
│ 生产环境           │ 不适合                  │ 适合小中型项目           │
│ LlamaIndex 集成    │ 默认，零配置            │ 需要 ChromaVectorStore   │
│ 学习成本           │ 低                      │ 中                       │
└────────────────────┴─────────────────────────┴─────────────────────────┘

面试金句:
  "SimpleVectorStore 适合原型验证，文档量上千或需要增量更新时切换到 ChromaDB。
   切换成本很低——LlamaIndex 的 VectorStore 抽象层让换存储引擎只需改几行代码。
   如果再到百万级文档或需要分布式，就上 Milvus 或 Pinecone。"
""")

print("[OK] Day 1 ChromaDB + LlamaIndex 集成完成！")
