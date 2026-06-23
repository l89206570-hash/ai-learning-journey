"""
服装工厂知识库 — 文档入库脚本
将 data/ 目录下的 Markdown 文档向量化存入 ChromaDB

使用方式：
    python ingest.py              # 首次入库（需先建向量库）
    python ingest.py --reset      # 清空后重新入库
"""

import os
import sys
import glob
import argparse
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions


# --- 配置 ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = str(BASE_DIR / "data")
COLLECTION_NAME = "garment_factory_kb"
DB_PATH = str(BASE_DIR / "chroma_db")

# 使用多语言 sentence-transformers 模型，中文检索效果远好于 all-MiniLM-L6-v2
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
MIN_CHUNK_LENGTH = 50  # 过滤过短片段（纯标题等），防止无意义向量污染检索


def load_documents(data_dir: str) -> list[dict]:
    """读取 data/ 下所有 .md 文件，返回 [{"path": ..., "content": ...}, ...]"""
    docs = []
    md_files = glob.glob(os.path.join(data_dir, "*.md"))
    if not md_files:
        print(f"[警告] {data_dir} 下没有找到 .md 文件")
        return docs

    for filepath in sorted(md_files):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        filename = os.path.basename(filepath)
        doc_type = filename.replace(".md", "")
        docs.append({
            "path": filepath,
            "filename": filename,
            "doc_type": doc_type,
            "content": content,
        })
        print(f"  已加载: {filename} ({len(content)} 字符)")

    return docs


def split_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """
    将长文本按段落切分成 chunk。
    策略：先按 ## 标题切大段，大段过长再按自然段切。
    """
    # 按 ## 二级标题切分
    sections = text.split("\n## ")

    chunks = []
    for section in sections:
        # 按自然段切
        paragraphs = section.split("\n\n")

        current = ""
        for p in paragraphs:
            p = p.strip()
            # 跳过空行
            if not p:
                continue

            if len(current) + len(p) > chunk_size and current:
                chunks.append(current.strip())
                current = p
            else:
                if current:
                    current += "\n\n" + p
                else:
                    current = p

        if current.strip() and len(current.strip()) >= MIN_CHUNK_LENGTH:
            chunks.append(current.strip())

    return chunks


def build_metadatas(chunks: list[str], doc_type: str) -> list[dict]:
    """为每个 chunk 构建元数据"""
    metadatas = []
    for i, chunk in enumerate(chunks):
        metadatas.append({
            "doc_type": doc_type,
            "chunk_index": i,
            "char_count": len(chunk),
        })
    return metadatas


def main():
    parser = argparse.ArgumentParser(description="服装工厂知识库入库工具")
    parser.add_argument("--reset", action="store_true", help="清空已有数据后重新入库")
    args = parser.parse_args()

    # 初始化 ChromaDB
    client = chromadb.PersistentClient(path=DB_PATH)
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    # 如果 reset，先删后建
    if args.reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"[重置] 已删除旧集合 '{COLLECTION_NAME}'")
        except Exception:
            pass

    # 获取或创建集合
    try:
        collection = client.get_collection(COLLECTION_NAME)
        print(f"[OK] 已连接到现有集合 '{COLLECTION_NAME}'，当前 {collection.count()} 条")
    except Exception:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_fn,
        )
        print(f"[OK] 已创建新集合 '{COLLECTION_NAME}'")

    # 加载文档
    print("\n--- 加载文档 ---")
    docs = load_documents(DATA_DIR)
    if not docs:
        print("没有文档可入库，退出。")
        return

    # 切分 + 入库
    print("\n--- 切分并入库 ---")
    total_chunks = 0

    for doc in docs:
        chunks = split_text(doc["content"])
        if not chunks:
            print(f"  跳过 {doc['filename']}：无有效内容")
            continue

        metadatas = build_metadatas(chunks, doc["doc_type"])

        # 为每个 chunk 生成全局唯一 ID：文档类型_序号
        ids = [f"{doc['doc_type']}_{i}" for i in range(len(chunks))]

        collection.add(
            documents=chunks,
            metadatas=metadatas,
            ids=ids,
        )

        total_chunks += len(chunks)
        print(f"  入库 {doc['filename']}: {len(chunks)} chunks")

    print(f"\n[完成] 共入库 {total_chunks} 条记录 → 集合 '{COLLECTION_NAME}'")
    print(f"数据库路径: {DB_PATH}")


if __name__ == "__main__":
    main()
