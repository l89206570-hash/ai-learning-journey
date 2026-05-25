"""建一次索引，存到 ./index_storage 目录 —— 以后查的时候直接加载，不用重新 embedding"""

# ---------- 导入 ----------
from llama_index.core import Document, VectorStoreIndex, Settings, StorageContext
# Document: 把你自己的文本包装成 LlamaIndex 认识的对象
# VectorStoreIndex: 把 Node 向量化并建索引（最常用的索引类型）
# Settings: 全局配置，设置 embed_model 和 llm 后全库自动复用
# StorageContext: 管理"存哪里"和"从哪读"的上下文

from llama_index.core.node_parser import SentenceSplitter
# SentenceSplitter: 按句子边界切分文档，不会把一句话砍成两半

from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# HuggingFaceEmbedding: 加载本地 HuggingFace 格式的嵌入模型

from llama_index.llms.openai_like import OpenAILike
# OpenAILike: 通用 OpenAI 兼容接口，不校验模型名白名单

from modelscope import snapshot_download
from dotenv import load_dotenv
import os

# ---------- 1. 加载文档 ----------
load_dotenv()

with open("knowledge.txt", "r", encoding="utf-8") as f:
    knowledge = f.read()

documents = [Document(text=knowledge)]  # 原始文本 → Document 对象

# ---------- 2. 切分文档 ----------
parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = parser.get_nodes_from_documents(documents)
# 每个 Node 是一小块文本，Node 是检索的最小单元
print(f"切成了 {len(nodes)} 个 Node")

# ---------- 3. 配置嵌入模型和 LLM ----------
model_dir = snapshot_download("BAAI/bge-small-zh-v1.5")  # ModelScope 国内直连
Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)
# 中文轻量嵌入模型，0.3 亿参数，本地 CPU 跑

Settings.llm = OpenAILike(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base="https://api.deepseek.com/beta",  # V4 需要 beta 端点
)

# ---------- 4. 建索引 + 存盘 ----------
index = VectorStoreIndex(nodes)
# 内部：每个 Node → 算向量 → 存入向量存储

index.storage_context.persist(persist_dir="./index_storage")
# 把向量数据和文档数据序列化到 ./index_storage 目录
print("索引已保存到 ./index_storage")
print(f"文件列表: {os.listdir('./index_storage')}")
