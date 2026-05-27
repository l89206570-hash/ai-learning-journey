from llama_index.core import Document, VectorStoreIndex, Settings, StorageContext
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from modelscope import snapshot_download
from dotenv import load_dotenv
import os

load_dotenv()

doc_faq = Document(text=open(os.path.join("ecommerce_docs", "faq.txt"), "r", encoding="utf-8").read(),
    metadata={"category": "常见问题", "source": "faq.txt"})

doc_policy = Document(text=open(os.path.join("ecommerce_docs", "policy.txt"), "r", encoding="utf-8").read(),
    metadata={"category": "政策", "source": "policy.txt"})

doc_products = Document(text=open(os.path.join("ecommerce_docs", "products.txt"), "r", encoding="utf-8").read(),
    metadata={"category": "产品", "source": "products.txt"})

document = [doc_faq, doc_policy, doc_products]

parser = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = parser.get_nodes_from_documents(document)
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

index = VectorStoreIndex(nodes)
index.storage_context.persist(persist_dir="./index_storage_day7")
