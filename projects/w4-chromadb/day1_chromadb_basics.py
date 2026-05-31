"""
W4 Day 1 — ChromaDB 向量数据库入门

学习目标：
  1. 理解什么是向量数据库，为什么要用它
  2. 掌握 ChromaDB 的核心概念：Client / Collection / Document / Embedding / Metadata
  3. 会做增删查（CRUD）+ 语义搜索 + 元数据过滤
  4. 理解 ChromaDB vs LlamaIndex 本地存储的区别

背景：
  W3 我们用 LlamaIndex 的本地文件存储索引（.json + .bin 文件），这在文档量少时够用。
  但生产环境有成百上千份文档，本地文件会线性变慢，而且不支持分布式、高并发。
  向量数据库（ChromaDB → Milvus）就是解决这些问题的专业方案。

运行方式（国内网络先设镜像）：
  $env:HF_ENDPOINT = "https://hf-mirror.com"   # PowerShell
  然后: python day1_chromadb_basics.py
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("../.env")

# =============================================================================
# Part 1: 什么是向量数据库？
# =============================================================================
# 传统数据库（MySQL/PostgreSQL）存的是结构化数据：数字、字符串、日期。
# 你查 "价格 > 100" 是精确匹配——价格要么大于 100，要么不大于。
#
# 向量数据库存的是「语义」——把文字转成向量（浮点数数组），通过比较向量之间
# 的距离/相似度来判断「这段内容和那段内容是不是在说同一件事」。
#
# 举个例子：
#   "云感T恤 129元" → Embedding 模型 → [0.12, -0.34, 0.67, ..., 0.05]（512 个浮点数）
#   "透气运动衫 149元" → Embedding 模型 → [0.11, -0.36, 0.65, ..., 0.08]
#   两个向量做余弦相似度 ≈ 0.92（很相似！都是衣服+价格）
#
#   而 "退换货政策 7 天" → Embedding → [0.78, 0.21, -0.43, ..., -0.61]
#   和 "云感T恤" 的向量余弦相似度可能只有 0.3（不相关）
#
# 向量数据库就是专门存这些向量 + 做高速相似度搜索的引擎。

print("=" * 60)
print("Part 1: ChromaDB 核心概念")
print("=" * 60)

import chromadb
from chromadb.utils import embedding_functions

# =============================================================================
# 1.1 嵌入函数（Embedding Function）— 把文字转成向量的引擎
# =============================================================================
# ChromaDB 默认用 all-MiniLM-L6-v2（英文模型，80MB，从 AWS S3 下载慢）。
# 我们用 SentenceTransformer 加载 BGE 中文模型，和 W3 用的同一个系列。
# 首次运行时会从 hf-mirror.com 下载约 100MB，之后走本地缓存。

# 使用 W3 时 ModelScope 下载的本地模型，跳过网络下载
BGE_MODEL_PATH = os.path.expanduser(
    "~/.cache/modelscope/hub/models/BAAI/bge-small-zh-v1___5"
)

embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=BGE_MODEL_PATH,  # 指向本地路径，sentence_transformers 会直接加载
)

print(f"嵌入模型: BAAI/bge-small-zh-v1.5 (本地 ModelScope 缓存)")
print(f"模型路径: {BGE_MODEL_PATH}")

# =============================================================================
# 1.2 ChromaDB Client — 连接方式有三种
# =============================================================================
# Ephemeral（内存模式）：不写磁盘，进程结束数据消失。适合测试/快速验证。
# Persistent（持久化模式）：数据存到硬盘，重启还在。适合小项目。
# HTTP Client（远程模式）：连接远端的 ChromaDB 服务器。适合生产环境。

# 今天我们用持久化模式——和 W3 的索引持久化一个道理，但要理解区别：
#   LlamaIndex 本地存储：JSON 存元数据 + .bin 存向量 → 全量加载到内存才能查
#   ChromaDB 持久化：数据库引擎管理文件 → 按需加载，支持增量写入，不会一次全读进内存

PERSIST_DIR = "./chroma_store"
if os.path.exists(PERSIST_DIR):
    shutil.rmtree(PERSIST_DIR)  # 清掉上次测试数据

chroma_client = chromadb.PersistentClient(path=PERSIST_DIR)

print(f"ChromaDB 存储路径: {os.path.abspath(PERSIST_DIR)}")
print(f"ChromaDB 版本: {chromadb.__version__}")

# =============================================================================
# Part 2: Collection — 类似 SQL 的表，但存的是向量
# =============================================================================
# Collection 是 ChromaDB 的核心组织单元。
# 一个 Collection 里存一组相关的文档，每个文档有四个组成部分：
#   - documents: 原始文本
#   - embeddings: 对应的向量（自动生成）
#   - metadatas: 结构化标签（价格、品类、来源等）
#   - ids: 唯一标识符（类比 SQL 主键）

print("\n" + "=" * 60)
print("Part 2: 创建 Collection & 添加数据")
print("=" * 60)

collection = chroma_client.create_collection(
    name="ecommerce_faq",
    metadata={"description": "电商常见问题"},
    embedding_function=embedding_fn,  # ← 指定中文嵌入模型
)

print(f"Collection 名称: {collection.name}")
print(f"Collection 文档数: {collection.count()}")

# ---------------------------------------------------------------------------
# 2.1 添加文档（自动向量化）
# ---------------------------------------------------------------------------
# add() 一次可以加多条——ChromaDB 自动调用 embedding_fn 转成向量
# 底层做的事：
#   1. 把每段文本喂给 BGE 模型
#   2. BGE 模型输出 512 个浮点数（向量）
#   3. 向量 + 文本 + 元数据一起写入数据库

faq_documents = [
    "我们支持7天无理由退换货，只要商品不影响二次销售即可办理。",
    "满199元包邮，不满199元需要支付8元运费。",
    "会员积分可以在下单时抵扣现金，100积分抵1元。",
    "定制类商品不支持退换货，请在购买前确认尺寸和款式。",
    "快递默认发顺丰，部分偏远地区发邮政。",
]

faq_ids = ["faq_1", "faq_2", "faq_3", "faq_4", "faq_5"]

faq_metadatas = [
    {"category": "退换货", "type": "policy"},
    {"category": "物流", "type": "policy"},
    {"category": "会员", "type": "benefit"},
    {"category": "退换货", "type": "policy"},
    {"category": "物流", "type": "shipping"},
]

collection.add(
    documents=faq_documents,
    ids=faq_ids,
    metadatas=faq_metadatas,
)

print(f"添加后文档数: {collection.count()}")  # 5
print(f"存储的 ID 列表: {collection.get()['ids']}")

# =============================================================================
# Part 3: 语义搜索 — 向量数据库的核心能力
# =============================================================================
# query() 做的事：问题自动向量化 → 和库里所有向量算距离 → 按距离排序返回 top_k
# 这就是 RAG 的「检索」环节！

print("\n" + "=" * 60)
print("Part 3: 语义搜索（语义相似度匹配）")
print("=" * 60)

# ---------------------------------------------------------------------------
# 3.1 基础查询
# ---------------------------------------------------------------------------
question = "退货需要什么条件？"

results = collection.query(
    query_texts=[question],  # 问题，ChromaDB 自动向量化
    n_results=3,  # 返回最相似的 3 条（类似 LlamaIndex 的 similarity_top_k）
)

# 返回值是一个字典，包含四个 key：
#   ids:       匹配到的文档 ID 列表
#   documents: 匹配到的文档原文
#   distances: 距离值（余弦距离，越小越相似，范围 0~2）
#   metadatas: 匹配到的元数据

print(f"问题: {question}")
print(f"返回了 {len(results['documents'][0])} 条结果:\n")

for i, (doc_id, doc, distance, meta) in enumerate(
    zip(
        results["ids"][0],
        results["documents"][0],
        results["distances"][0],
        results["metadatas"][0],
    )
):
    print(f"  #{i+1} [{doc_id}] 距离={distance:.4f} | {meta['category']}")
    print(f"      {doc}")

# 你会发现#1 是"7天无理由退换货"——虽然两段话没有共享「条件」这个词，
# 但语义上最匹配。这就是向量检索的核心价值：搜的是意思，不是关键词。

# ---------------------------------------------------------------------------
# 3.2 距离 vs 相似度
# ---------------------------------------------------------------------------
# ChromaDB 默认返回余弦距离（cosine distance），范围 0~2：
#   0.0  = 向量方向完全相同（语义最相似）
#   1.0  = 正交（不相关）
#   2.0  = 完全相反
# 越小越相似！
#
# 这和 LlamaIndex 的 score 是反的：
#   ChromaDB distance: 越小越好
#   LlamaIndex score:  越大越好（0~1 相似度）
#
# 面试时被问"向量相似度怎么算"：
#   常用的有三种——余弦相似度、欧氏距离、内积（点积）。

# ---------------------------------------------------------------------------
# 3.3 查一个无关问题——观察距离变化
# ---------------------------------------------------------------------------
question2 = "今天天气怎么样？"
results2 = collection.query(query_texts=[question2], n_results=3)

print(f"\n问题（不相关）: {question2}")
for i, (doc_id, distance) in enumerate(
    zip(results2["ids"][0], results2["distances"][0])
):
    print(f"  #{i+1} [{doc_id}] 距离={distance:.4f}")

print("\n注意: 不相关问题的距离普遍更大，这就是判断检索质量的信号")

# =============================================================================
# Part 4: 元数据过滤 — 精确筛选 + 语义搜索
# =============================================================================
# 语义搜索很强大，但有时你需要精确限制范围：
#   "我只想搜「退换货」相关的问题"
#   "只看 type='policy' 的文档"
# 这就是 metadata filter——和 W3 的 MetadataFilter 完全一样的概念，
# 但 ChromaDB 在数据库层面直接过滤。

print("\n" + "=" * 60)
print("Part 4: 元数据过滤（语义 + 精确双筛选）")
print("=" * 60)

# 4.1 按字段精确过滤
question3 = "有什么限制条件？"
results3 = collection.query(
    query_texts=[question3],
    n_results=3,
    where={"category": "退换货"},  # ← 只搜退换货类别
)

print(f"问题: {question3}")
print(f"过滤条件: category='退换货'")
for i, (doc_id, doc) in enumerate(
    zip(results3["ids"][0], results3["documents"][0])
):
    print(f"  #{i+1} [{doc_id}] {doc}")

# 4.2 复杂过滤条件（$and / $or）
print("\n--- 复杂条件 ---")
results4 = collection.query(
    query_texts=["退货政策"],
    n_results=3,
    where={
        "$and": [
            {"category": "退换货"},
            {"type": "policy"},
        ]
    },
)

print(f"条件: category='退换货' AND type='policy'")
for i, (doc_id, doc) in enumerate(
    zip(results4["ids"][0], results4["documents"][0])
):
    print(f"  #{i+1} [{doc_id}] {doc}")

# ChromaDB vs LlamaIndex 的过滤语法对比：
#   LlamaIndex: MetadataFilter(key="category", value="退换货", operator=FilterOperator.EQ)
#   ChromaDB:   where={"category": "退换货"}
# 面试金句："元数据过滤在向量数据库层面做，避免了先检索后过滤的性能浪费"

# =============================================================================
# Part 5: 更新和删除
# =============================================================================

print("\n" + "=" * 60)
print("Part 5: 更新 & 删除文档")
print("=" * 60)

# 5.1 更新文档（按 ID）
collection.update(
    ids=["faq_2"],
    documents=["满299元包邮，不满299元需要支付10元运费。"],  # 运费涨了
    metadatas=[{"category": "物流", "type": "policy"}],
)
print("更新后 faq_2:", collection.get(ids=["faq_2"])["documents"][0])

# 5.2 删除文档（按 ID）
collection.delete(ids=["faq_5"])
print(f"删除 faq_5 后: {collection.count()} 条")

# 5.3 upsert——存在就更新，不存在就插入
collection.upsert(
    documents=["新增大客户批发通道，请联系客服获取报价。"],
    ids=["faq_6"],
    metadatas=[{"category": "销售", "type": "channel"}],
)
print(f"upsert 后: {collection.count()} 条")

# =============================================================================
# Part 6: 数据持久化验证
# =============================================================================

print("\n" + "=" * 60)
print("Part 6: 持久化验证")
print("=" * 60)

# 已经用 PersistentClient，数据在 chroma_store/ 目录里
# 模拟"重启"：创建新 client 连同一个目录

client2 = chromadb.PersistentClient(path=PERSIST_DIR)
collection2 = client2.get_collection(
    "ecommerce_faq",
    embedding_function=embedding_fn,  # 查询时也要传相同的 embedding function
)
print(f"重新连接后 Collection 文档数: {collection2.count()}")
print(f"ID 列表: {collection2.get()['ids']}")

# 对比 W3 的索引持久化：
#   W3 LlamaIndex: index.storage_context.persist() → 手动调用 + JSON 文件
#   ChromaDB:       PersistentClient 自动持久化 → 数据库引擎管理
#
# ChromaDB 的优势：
#   1. 增量写入——不需要每次全量重建
#   2. 并发读——多人同时查询不冲突
#   3. 自动管理——不用手动调用 persist()

print("\n[OK] Day 1 ChromaDB 基础完成！")
print("下一步: python day1_chromadb_llamaindex.py（ChromaDB + LlamaIndex 集成）")
