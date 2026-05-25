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

 # 实验1：记忆管理
chat = index.as_chat_engine(chat_mode="context")

chat.chat("你们的退货政策是什么？")
print(f"第一轮后历史: {len(chat.chat_history)} 条")

chat.chat("运费谁出？")
print(f"第二轮后历史: {len(chat.chat_history)} 条")

chat.reset()
print(f"reset() 后历史: {len(chat.chat_history)} 条")

r = chat.chat("我刚问了什么？")
print(f"reset 后提问: {r}")

# 实验2: 看 response 对象的内部结构
chat3 = index.as_chat_engine(chat_mode="context")
resp = chat3.chat("钻石会员有什么权益？")
print(f"回答文本: {resp}")
print(f"类型: {type(resp)}")
print(f"来源节点: {len(resp.source_nodes)} 个")
for i, s in enumerate(resp.source_nodes):
    print(f"  [{i}] 相似度={s.score:.3f} | {s.node.text[:60]}...")

# 实验3：三种 chat_mode 对比
print("\n=== 实验3: 三种 chat_mode 对比 ===")
questions = [
    ("第一问", "钻石会员有什么权益？"),
    ("追问", "年费多少？"),
]

for mode in ["default", "condense_question", "context"]:
    print(f"\n--- chat_mode={mode} ---")
    try:
        c = index.as_chat_engine(chat_mode=mode)
        for label, q in questions:
            r = c.chat(q)
            print(f"{label}: {q}")
            print(f"回答: {r}\n")
    except Exception as e:
        print(f"Error: {e}")

# 实验4：流式输出 — 逐 token 实时打印
print("\n=== 实验4: 流式输出 ===")
chat4 = index.as_chat_engine(chat_mode="context")
print("正在流式输出（逐字出现）:")
response = chat4.stream_chat("钻石会员有什么权益？")
for chunk in response.response_gen:
    print(chunk, end="", flush=True)
print("\n\n[流式输出结束]")
print(f"流式响应来源节点: {len(response.source_nodes)} 个")