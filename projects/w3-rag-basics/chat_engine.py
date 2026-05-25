from llama_index.core import Settings, StorageContext, load_index_from_storage
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
    max_tokens=500,
    temperature=0.2,
)

storage_context = StorageContext.from_defaults(persist_dir="./index_storage")
index = load_index_from_storage(storage_context)

# 实验1: query_engine 无状态，记不住上文
print("=== query_engine（无状态）===")
query_engine = index.as_query_engine()
print(query_engine.query("退货政策是什么"))
print(query_engine.query("它需要什么条件？"))

# 实验2: chat_engine 有状态，记住历史
print("\n=== chat_engine（有状态）===")
chat = index.as_chat_engine(chat_mode="context")
print(chat.chat("你们的退货政策是什么？"))
print(chat.chat("它需要什么条件？"))

# 实验3: 看聊天历史
print("\n=== 聊天历史 ===")
for i, msg in enumerate(chat.chat_history):
    print(f"[{i}] {msg.role}: {msg.content}")
