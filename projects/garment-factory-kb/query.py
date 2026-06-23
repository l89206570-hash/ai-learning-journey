"""
服装工厂知识库 — RAG 查询脚本
基于 ChromaDB 检索 + 本地 LLM（DeepSeek API）生成回答

使用方式：
    python query.py "缝制环节有哪些常见疵点？"
    python query.py "如何应对客户色差投诉？" --top-k 5
    python query.py "平缝机断线怎么排查？" --filter order_specs
"""

import os
import sys
import argparse
import json
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from openai import OpenAI


# --- 配置 ---
BASE_DIR = Path(__file__).resolve().parent
COLLECTION_NAME = "garment_factory_kb"
DB_PATH = str(BASE_DIR / "chroma_db")

# DeepSeek API（兼容 OpenAI SDK）
DS_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-api-key-here")
DS_BASE_URL = "https://api.deepseek.com"
DS_MODEL = "deepseek-chat"

# 系统提示词
SYSTEM_PROMPT = """你是鑫盛服装厂的知识库助手。根据提供的文档片段回答用户问题。
- 优先使用文档中的信息，文档没有提到则诚实说"文档中未涉及"
- 回答简洁实用，面向工厂一线员工和管理人员
- 涉及操作规范时，强调安全要点"""


def retrieve(collection, query: str, top_k: int = 3, doc_filter: str = None):
    """从 ChromaDB 检索相关文档片段"""
    where_filter = None

    # BUG #3 已修：字段名从 "source" 改为 "doc_type"，匹配 ingest.py 里的元数据结构
    if doc_filter:
        where_filter = {"doc_type": doc_filter}

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where_filter,
    )

    return results


def build_prompt(query: str, documents: list[str], metadatas: list[dict]) -> str:
    """构造发给 LLM 的 prompt"""
    context_parts = []
    for i, (doc, meta) in enumerate(zip(documents, metadatas), 1):
        source = meta.get("doc_type", "未知来源")
        context_parts.append(f"[片段 {i}] 来源：{source}\n{doc}")

    context = "\n\n".join(context_parts)

    return f"""参考以下文档片段回答问题：

{context}

---
用户问题：{query}

请根据以上文档内容回答。"""


def query_llm(system: str, user: str) -> str:
    """调用 DeepSeek API"""
    client = OpenAI(api_key=DS_API_KEY, base_url=DS_BASE_URL)

    response = client.chat.completions.create(
        model=DS_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
        max_tokens=800,
    )

    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="服装工厂知识库查询工具")
    parser.add_argument("query", nargs="?", help="查询问题")
    parser.add_argument("--top-k", type=int, default=3, help="检索片段数 (默认 3)")
    parser.add_argument("--filter", type=str, default=None,
                        help="限定文档类型 (如 production_process, quality_standards)")
    parser.add_argument("--no-llm", action="store_true", help="只检索不调用 LLM")
    args = parser.parse_args()

    # 交互模式 / 命令行模式
    if args.query:
        query = args.query
    else:
        query = input("请输入问题: ").strip()
        if not query:
            print("问题不能为空")
            return

    # 连接 ChromaDB
    client = chromadb.PersistentClient(path=DB_PATH)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )
    collection = client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_fn,
    )

    print(f"\n[检索] 查询: {query}")
    print(f"[检索] top_k={args.top_k}", end="")
    if args.filter:
        print(f", filter={args.filter}", end="")
    print()

    # 检索
    results = retrieve(collection, query, top_k=args.top_k, doc_filter=args.filter)

    documents = results["documents"][0]  # query() 返回双层嵌套 [[...]]
    metadatas = results["metadatas"][0]
    distances = results.get("distances", [[]])[0]

    if not documents:
        print("\n[!] 未检索到匹配的文档片段。")
        if args.filter:
            print(f"    可能原因：filter '{args.filter}' 不匹配任何文档（检查字段名是否正确）")
        return

    print(f"\n--- 检索到 {len(documents)} 个相关片段 ---")
    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
        doc_type = meta.get("doc_type", "?")
        print(f"\n  [{i}] 来源: {doc_type} | 距离: {dist:.4f}")
        print(f"  {doc[:200]}...")

    # 调用 LLM 生成回答
    if not args.no_llm:
        print("\n--- LLM 回答 ---")
        prompt = build_prompt(query, documents, metadatas)
        try:
            answer = query_llm(SYSTEM_PROMPT, prompt)
            print(answer)
        except Exception as e:
            print(f"[错误] LLM 调用失败: {e}")
            print("（可以加 --no-llm 只看检索结果）")


if __name__ == "__main__":
    main()
