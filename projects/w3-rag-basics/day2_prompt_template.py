"""W3D2: Prompt 模板 —— 看到底 LLM 收到了什么"""
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.prompts import PromptTemplate
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai_like import OpenAILike
from modelscope import snapshot_download
from dotenv import load_dotenv
import os

load_dotenv()
model_dir = snapshot_download("BAAI/bge-small-zh-v1.5")  # 拿 ModelScope 本地缓存路径，不走 HF
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

# ---------- 1. 获得 LlamaIndex 正在使用的默认 prompt ----------
default_template = index.as_query_engine().get_prompts()
print("=== LlamaIndex 默认 Prompt 模板 ===")
print(default_template["response_synthesizer:text_qa_template"].default_template.template)
print()

# ---------- 2. 自定义模板 ----------
# {context_str} = 检索到的文本
# {query_str}   = 用户的问题
my_template = PromptTemplate(
    "【系统指令】你是电商客服。只根据下方资料回答，资料没有的就回复'我不确定'。\n"
    "【回答要求】简洁，不超过 3 句话，直接给答案不要重复问题。\n"
    "\n"
    "【资料】\n"
    "{context_str}\n"
    "\n"
    "【用户消息】\n"
    "{query_str}"
)

query_engine = index.as_query_engine(text_qa_template=my_template, similarity_top_k=2)

# ---------- 3. 测试对比 ----------
questions = [
    "钻石会员有什么权益？",
    "可以送到月球吗？",  # 知识库里没有的
    "退货要几天？",
]

for q in questions:
    print("=" * 60)
    print(f"用户问: {q}")
    response = query_engine.query(q)
    print(f"AI 回答: {response}\n")
