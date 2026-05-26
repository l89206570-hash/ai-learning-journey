from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.vector_stores import MetadataFilters, MetadataFilter, FilterOperator
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from modelscope import snapshot_download
from dotenv import load_dotenv
import os

load_dotenv()

model_dir = snapshot_download("BAAI/bge-small-zh-v1.5")
Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)
Settings.llm = OpenAILike(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base="https://api.deepseek.com/beta",
    max_tokens=1024,
    temperature=0.2,
    )

storage_context = StorageContext.from_defaults(persist_dir="./index_storage_day6")
index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine(similarity_top_k=3)

#跨文档查询
response_a = query_engine.query("介绍一下盒模型?")
print(f"\n[CSS] 回答: {response_a}")
print("检索来源:")
for i, node in enumerate(response_a.source_nodes):
    meta = node.metadata
    print(f"  [来源 {i}] score={node.score:.3f} | "
          f"category={meta.get('category')} | source={meta.get('source')}")
                         
print()
response_b = query_engine.query("Django的请求生命周期?")    
print(f"\n[Django] 回答: {response_b}")
print("检索来源:")
for i, node in enumerate(response_b.source_nodes):
    meta = node.metadata
    print(f"  [来源 {i}] score={node.score:.3f} | "
          f"category={meta.get('category')} | source={meta.get('source')}")
    

#按category过滤
print("\n" + "=" * 60)

filter_frontend_framework = MetadataFilters(
    filters=[MetadataFilter(key="category", operator=FilterOperator.EQ, value="前端框架")]
)

query_framework = index.as_query_engine(
    similarity_top_k=3,
    filters=filter_frontend_framework
)

response3 = query_framework.query("React的虚拟DOM原理?")
print(f"\n[React] 回答: {response3}")
print("\n=== 检索来源（应全部来自 category='前端框架')===")
for i, node in enumerate(response3.source_nodes):
    meta = node.metadata
    print(f"  [来源 {i}] score={node.score:.3f} | "
          f"category={meta.get('category')} | source={meta.get('source')}")
    

#组合过滤
print("\n" + "=" * 60)

filter_combined = MetadataFilters(
    filters=[
        MetadataFilter(key="category", operator=FilterOperator.EQ, value="算法"),
        MetadataFilter(key="source", operator=FilterOperator.EQ, value="算法与数据结构.txt")
    ],
    condition="and"
)

query_combined = index.as_query_engine(
    similarity_top_k=3,
    filters=filter_combined
)

response4 = query_combined.query("数组和链表的区别?")
print(f"\n[response4] 回答: {response4}")

print("\n=== 检索来源（应同时满足 category='算法' + source='算法与数据结构.txt')===")
for i, node in enumerate(response4.source_nodes):
    meta = node.metadata
    print(f"  [来源 {i}] score={node.score:.3f} | "
          f"category={meta.get('category')} | "
          f"source={meta.get('source')}")