"""W3D2: 检索过程可视化 —— 看到底检索到了哪些文本块"""
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from modelscope import snapshot_download
from dotenv import load_dotenv
import os

load_dotenv()

with open("knowledge.txt", "r", encoding="utf-8") as f:
    knowledge = f.read()

# 强制切成小块，让检索效果更明显
documents = [Document(text=knowledge)]
parser = SentenceSplitter(chunk_size=256, chunk_overlap=30)
nodes = parser.get_nodes_from_documents(documents)
print(f"使用 chunk_size=256，切成 {len(nodes)} 个 Node\n")

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

# ----- 核心：查看检索到的源节点 -----
query_engine = index.as_query_engine(similarity_top_k=2)

questions = [
    "钻石会员有什么权益？",
    "退货需要什么条件？",
    "快递用什么物流？",
]

for q in questions:
    print("=" * 60)
    print(f"用户问: {q}")
    response = query_engine.query(q)
    print(f"\nAI 回答: {response}\n")

    for i, source in enumerate(response.source_nodes):
        score = source.score
        text = source.node.text[:150].replace("\n", " ")
        print(f"  检索源 {i+1} (相似度={score:.4f}): {text}...")
    print()
