from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike 
from modelscope import snapshot_download 
from dotenv import load_dotenv  
import os

load_dotenv()

with open("knowledge.txt", "r", encoding = "utf-8") as f:
    knowledge = f.read()
documents = [Document(text=knowledge)]
model_dir = snapshot_download("BAAI/bge-small-zh-v1.5")
Settings.embed_model = HuggingFaceEmbedding(model_name=model_dir)
Settings.llm = OpenAILike(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base="https://api.deepseek.com/beta",
    max_tokens=1000,
    temperature=0.2,
)
index = VectorStoreIndex.from_documents(documents)

query_engine = index.as_query_engine()
response = query_engine.query("钻石会员有什么权益？")
print(response)
direct_response = Settings.llm.complete("钻石会员有什么权益？")
print("--- 不加RAG ---")  
print(direct_response)