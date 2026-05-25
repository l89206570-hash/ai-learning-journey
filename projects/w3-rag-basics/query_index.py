"""加载已有索引，直接查询 —— 不需要重新 embedding"""

# ---------- 导入 ----------
from llama_index.core import Settings, StorageContext, load_index_from_storage
# load_index_from_storage: 从硬盘恢复索引，是 build_index.py 存盘的逆操作

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from modelscope import snapshot_download
from dotenv import load_dotenv
import os

# ---------- 1. 配置模型（跟 build_index.py 一样）----------
# 即使是加载已有索引，也还是要配置 embed_model
# 原因：查询时需要把用户问题转成向量，才能和索引里的向量做相似度计算
load_dotenv()

model_dir = snapshot_download("BAAI/bge-small-zh-v1.5")  # 拿 ModelScope 本地缓存路径
# 这里直接写模型名，因为 build_index.py 已经通过 ModelScope 下载过了
Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)
Settings.llm = OpenAILike(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base="https://api.deepseek.com/beta",
    max_tokens=500,
    temperature=0.2,
)

# ---------- 2. 从硬盘加载索引 ----------
storage_context = StorageContext.from_defaults(persist_dir="./index_storage")
# 告诉系统"数据在 ./index_storage 这个目录里"
index = load_index_from_storage(storage_context)
# 把之前存的向量、文档结构全部恢复，不需要重新 embedding
print("索引已从硬盘加载，无需重新 embedding\n")

# ---------- 3. 创建查询引擎 ----------
query_engine = index.as_query_engine(similarity_top_k=2)
# similarity_top_k=2：每次检索返回最相关的 2 个 Node

# ---------- 4. 交互式问答 ----------
while True:
    q = input("问什么？（输入 q 退出）: ")
    if q.lower() == "q":
        break
    if not q.strip():
        continue
    response = query_engine.query(q)
    print(f"\n{response}\n")
    # 打印检索源：能看到 LLM 是基于哪段原文回答的
    for i, source in enumerate(response.source_nodes):
        text = source.node.text[:120].replace("\n", " ")
        print(f"  [{i+1}] 相似度={source.score:.3f} | {text}...")
    print()
