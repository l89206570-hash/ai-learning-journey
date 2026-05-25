"""W3D2: 探索分块策略 —— 看看文档到底被切成了什么样"""
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

documents = [Document(text=knowledge)]
print(f"原始文档: {len(knowledge)} 字符, {len(knowledge.splitlines())} 行\n")

# 默认切分器: chunk_size=1024, chunk_overlap=200
parser = SentenceSplitter(chunk_size=1024, chunk_overlap=200)
nodes = parser.get_nodes_from_documents(documents)

print(f"切成了 {len(nodes)} 个 Node:\n")
for i, node in enumerate(nodes):
    print(f"--- Node {i+1} ({len(node.text)} 字符) ---")
    print(node.text[:300])
    print()

# 对比不同 chunk_size
print("=" * 50)
print("不同 chunk_size 对比:")
for cs in [256, 512, 2048]:
    p = SentenceSplitter(chunk_size=cs, chunk_overlap=50)
    ns = p.get_nodes_from_documents(documents)
    avg = sum(len(n.text) for n in ns) // len(ns)
    print(f"  chunk_size={cs:>4}: {len(ns)} 个Node, 平均{avg}字符/Node")
