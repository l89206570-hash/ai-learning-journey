"""对比：重新建索引 vs 从硬盘加载，速度差多少"""
from llama_index.core import Document, VectorStoreIndex, Settings, StorageContext
from llama_index.core import load_index_from_storage
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from modelscope import snapshot_download
from dotenv import load_dotenv
import time

load_dotenv()

model_dir = snapshot_download("BAAI/bge-small-zh-v1.5")
Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)

with open("knowledge.txt", "r", encoding="utf-8") as f:
    knowledge = f.read()

# 方式 1：重新建索引
t1 = time.time()
documents = [Document(text=knowledge)]
index_new = VectorStoreIndex.from_documents(documents)
t2 = time.time()
print(f"重新建索引: {t2 - t1:.2f}s")

# 方式 2：从硬盘加载
t3 = time.time()
storage_context = StorageContext.from_defaults(persist_dir="./index_storage")
index_loaded = load_index_from_storage(storage_context)
t4 = time.time()
print(f"从硬盘加载: {t4 - t3:.2f}s")
print(f"快了 {(t2 - t1) / max(t4 - t3, 0.001):.0f}x")
