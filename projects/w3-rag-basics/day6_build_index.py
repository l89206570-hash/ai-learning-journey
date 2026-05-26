from llama_index.core import Document, VectorStoreIndex, Settings, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from modelscope import snapshot_download
from dotenv import load_dotenv
import os

load_dotenv()


doc_backend = Document(
    text=open(os.path.join("interview_docs", "后端开发.txt"), "r", encoding="utf-8").read(),
    metadata={"category": "后端", "source": "后端开发.txt"}
)

doc_frontend_basic = Document(
    text=open(os.path.join("interview_docs", "frontend基础.txt"), "r", encoding="utf-8").read(),
    metadata={"category": "前端基础", "source": "frontend基础.txt"}
)

doc_frontend_framework = Document(
    text=open(os.path.join("interview_docs", "frontend框架.txt"), "r", encoding="utf-8").read(),
    metadata={"category": "前端框架", "source": "frontend框架.txt"}
)

doc_algorithm = Document(
    text=open(os.path.join("interview_docs", "算法与数据结构.txt"), "r", encoding="utf-8").read(),
    metadata={"category": "算法", "source": "算法与数据结构.txt"}
)

documents = [doc_backend, doc_frontend_basic, doc_frontend_framework, doc_algorithm]

parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = parser.get_nodes_from_documents(documents)

print(f"4 份文档 → 切成了 {len(nodes)} 个 Node")

# 看看每个 Node 携带了什么元数据
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
    max_tokens=500,
    temperature=0.2,
)

index = VectorStoreIndex(nodes)
index.storage_context.persist(persist_dir="./index_storage_day6")



