"""Day 5: 多文档索引 + 跨文档检索 + 元数据过滤

核心新概念:
- 多份 Document 各有独立 metadata（来源、分类、日期等标签）
- 跨文档检索：一个问题会自动从多个文档中检索相关片段
- 元数据过滤：检索时只看符合条件的那部分文档
"""

# ---------- 导入 ----------
from llama_index.core import Document, VectorStoreIndex, Settings, StorageContext
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
# MetadataFilter: 单个过滤条件（字段名 + 运算符 + 值）
# MetadataFilters: 多个条件组合（AND/OR）
# FilterOperator: 比较运算符（==, >, <, !=, in）

from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from modelscope import snapshot_download
from dotenv import load_dotenv
import os

load_dotenv()

# ---------- 1. 准备多份文档 + 元数据 ----------
# Document 的第二个参数是 metadata dict，可以存任意标签
doc_return = Document(
    text="""## 退货政策
顾客可以在收到商品后 7 天内申请退货。退货商品必须保持原包装完整，吊牌未剪。
食品和生鲜类商品不支持退货。退货邮费由卖家承担，顾客无需支付任何费用。
退款将在仓库签收退货后的 1-3 个工作日内原路退回。""",
    metadata={"category": "policy", "topic": "退货", "source": "help_center"}
)

doc_shipping = Document(
    text="""## 发货说明
订单通常在付款后 24 小时内发货。偏远地区（西藏、新疆、内蒙古）需要额外 2-3 天。
默认使用顺丰快递，满 99 元包邮。不满 99 元需要支付 8 元运费。
跨境电商商品从保税仓发货，需要额外提供身份证信息用于清关。""",
    metadata={"category": "logistics", "topic": "发货", "source": "help_center"}
)

doc_member = Document(
    text="""## 会员权益
普通会员：消费每满 100 元积 1 分，积分可兑换优惠券。
黄金会员：年消费满 5000 元升级，享全场 9.5 折，生日当月双倍积分。
钻石会员：年消费满 20000 元升级，享全场 9 折，专属客服通道，优先发货。""",
    metadata={"category": "membership", "topic": "会员", "source": "help_center"}
)

doc_faq = Document(
    text="""## 常见问题
Q: 收到的商品有质量问题怎么办？
A: 请在签收后 24 小时内拍照联系客服，我们会安排换货或退款，邮费由我们承担。

Q: 可以修改订单地址吗？
A: 未发货的订单可以在 APP 订单详情页自助修改。已发货的订单需要联系客服拦截快递。

Q: 优惠券可以叠加使用吗？
A: 店铺优惠券和平台优惠券可以叠加。同类型优惠券每单只能使用一张。""",
    metadata={"category": "faq", "topic": "常见问题", "source": "help_center"}
)

# 加一份"竞品"文档，后面演示按 source 过滤
doc_competitor = Document(
    text="""## 竞品退货政策（友商对比）
某东：支持 7 天无理由退货，但数码产品拆封后不支持。
某多：仅支持质量问题退货，无理由退货需要买家承担来回运费。
某宝：不同卖家规则不同，平台标准为 7 天无理由，生鲜类不支持。""",
    metadata={"category": "policy", "topic": "退货", "source": "competitor_analysis"}
)

documents = [doc_return, doc_shipping, doc_member, doc_faq, doc_competitor]

# ---------- 2. 切分 + 建索引 ----------
parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = parser.get_nodes_from_documents(documents)
print(f"5 份文档 → 切成了 {len(nodes)} 个 Node")

# 看看每个 Node 携带了什么元数据
print("\n=== Node 元数据一览 ===")
for i, node in enumerate(nodes):
    print(f"[Node {i}] category={node.metadata.get('category')}, "
          f"topic={node.metadata.get('topic')}, "
          f"source={node.metadata.get('source')}, "
          f"text前30字={node.text[:30]}...")

# ---------- 3. 配置嵌入模型和 LLM ----------
model_dir = snapshot_download("BAAI/bge-small-zh-v1.5")
Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)
Settings.llm = OpenAILike(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base="https://api.deepseek.com/beta",
    max_tokens=500,
    temperature=0.2,
)

# ---------- 4. 建索引 + 存盘 ----------
index = VectorStoreIndex(nodes)
index.storage_context.persist(persist_dir="./index_storage_multi")
print(f"\n多文档索引已保存到 ./index_storage_multi")

# ==========================================
# 实验 1: 跨文档检索
# ==========================================
print("\n" + "=" * 60)
print("实验 1: 跨文档检索 —— 一个问题跨多份文档找答案")
print("=" * 60)

# 分两次提问，演示同一个 query_engine 如何跨文档检索不同主题
query_engine = index.as_query_engine(similarity_top_k=3)
# similarity_top_k=3: 返回最相似的 3 个 Node

# 问题 A: 退货 → 应该命中 policy 文档
response_a = query_engine.query("退货政策是什么？")
print(f"\n[退货问题] 回答: {response_a}")
print("检索来源:")
for i, node in enumerate(response_a.source_nodes):
    meta = node.metadata
    print(f"  [来源 {i}] score={node.score:.3f} | "
          f"category={meta.get('category')} | source={meta.get('source')}")

# 问题 B: 会员 → 应该命中 membership 文档（跨文档！）
print()
response_b = query_engine.query("会员有哪些权益？")
print(f"[会员问题] 回答: {response_b}")
print("检索来源:")
for i, node in enumerate(response_b.source_nodes):
    meta = node.metadata
    print(f"  [来源 {i}] score={node.score:.3f} | "
          f"category={meta.get('category')} | source={meta.get('source')}")

# ==========================================
# 实验 2: 元数据过滤 —— 只看客服帮助中心的文档
# ==========================================
print("\n" + "=" * 60)
print("实验 2: 元数据过滤 —— 只看 source='help_center' 的文档")
print("=" * 60)

# 构建过滤器: 只检索 source 字段等于 "help_center" 的 Node
filter_help = MetadataFilters(
    filters=[MetadataFilter(key="source", operator=FilterOperator.EQ, value="help_center")]
)

query_filtered = index.as_query_engine(
    similarity_top_k=3,
    filters=filter_help  # 关键参数：检索时只走符合过滤条件的 Node
)

response2 = query_filtered.query("退货政策是什么？")
print(f"\n回答: {response2}")

print("\n=== 检索来源（应全部来自 help_center）===")
for i, node in enumerate(response2.source_nodes):
    meta = node.metadata
    print(f"[来源 {i}] score={node.score:.3f} | "
          f"source={meta.get('source')} | "
          f"category={meta.get('category')}")

# ==========================================
# 实验 3: 只看竞品分析的文档
# ==========================================
print("\n" + "=" * 60)
print("实验 3: 元数据过滤 —— 只看 source='competitor_analysis'")
print("=" * 60)

filter_competitor = MetadataFilters(
    filters=[MetadataFilter(key="source", operator=FilterOperator.EQ, value="competitor_analysis")]
)

query_competitor = index.as_query_engine(
    similarity_top_k=3,
    filters=filter_competitor
)

response3 = query_competitor.query("退货政策是什么？")
print(f"\n回答: {response3}")

print("\n=== 检索来源（应全部来自 competitor_analysis)===")
for i, node in enumerate(response3.source_nodes):
    meta = node.metadata
    print(f"[来源 {i}] score={node.score:.3f} | "
          f"source={meta.get('source')} | "
          f"text前50字={node.text[:50]}...")

# ==========================================
# 实验 4: 组合过滤 —— category=policy 且 source=help_center
# ==========================================
print("\n" + "=" * 60)
print("实验 4: 组合过滤 —— category='policy' AND source='help_center'")
print("=" * 60)

filter_combo = MetadataFilters(
    filters=[
        MetadataFilter(key="category", operator=FilterOperator.EQ, value="policy"),
        MetadataFilter(key="source", operator=FilterOperator.EQ, value="help_center"),
    ],
    condition="and"  # 默认就是 and，也可以改成 "or"
)

query_combo = index.as_query_engine(
    similarity_top_k=3,
    filters=filter_combo
)

response4 = query_combo.query("退货政策是什么？")
print(f"\n回答: {response4}")

print("\n=== 检索来源（应同时满足 category='policy' + source='help_center'）===")
for i, node in enumerate(response4.source_nodes):
    meta = node.metadata
    print(f"[来源 {i}] score={node.score:.3f} | "
          f"category={meta.get('category')} | "
          f"source={meta.get('source')}")

print("\n" + "=" * 60)
print("Day 5 核心要点:")
print("1. 多份 Document，各自 metadata → 一次建索引，跨文档检索")
print("2. MetadataFilter(field, operator, value) → 按标签筛选检索范围")
print("3. MetadataFilters 组合多个条件 → AND/OR 灵活控制")
print("4. response.source_nodes → 查看每条回答来自哪个文档")
print("=" * 60)
