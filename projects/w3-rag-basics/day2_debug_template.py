"""W3D2: 调试 —— 看到底发给 LLM 的完整 prompt 长什么样"""
from llama_index.core import Settings, StorageContext, load_index_from_storage
from llama_index.core.prompts import PromptTemplate
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

# 步骤 1：拿到检索结果
retriever = index.as_retriever(similarity_top_k=2)
nodes = retriever.retrieve("钻石会员有什么权益？")
print("=== 检索到的 Node ===")
for i, n in enumerate(nodes):
    print(f"[{i+1}] score={n.score:.3f}: {n.node.text[:200]}")
print()

# 步骤 2：看完整的合成 prompt
query_engine = index.as_query_engine(similarity_top_k=2)
prompts = query_engine.get_prompts()
qa_key = None
for k in prompts:
    if "qa_template" in k:
        qa_key = k
        break

if qa_key:
    default_prompt = prompts[qa_key].get_template()
    # 用实际数据填充模板
    context = "\n".join([n.node.text for n in nodes])
    filled = default_prompt.format(context_str=context, query_str="钻石会员有什么权益？")
    print("=== 发给 LLM 的完整 prompt ===")
    print(filled)
    print()

# 步骤 3：直接测自定义模板
my_template = PromptTemplate(
    "只根据以下资料回答问题，资料没有就说不知道，三句话内。\n"
    "{context_str}\n"
    "问题: {query_str}"
)
# 填上实际数据看看
filled2 = my_template.format(context_str=context, query_str="钻石会员有什么权益？")
print("=== 自定义模板填好后 ===")
print(filled2)
