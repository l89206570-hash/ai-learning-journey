# RAG 知识库 & 检索增强生成

## RAG 核心概念

| 概念 | 要点 |
|------|------|
| RAG | Retrieval Augmented Generation，先检索再回答，给 LLM 限定信息来源避免幻觉 |
| 为什么需要 RAG | LLM 训练数据有截止日期，不知道你的业务知识，容易编造答案（幻觉） |
| RAG vs 直接 LLM | RAG = 开卷考试（有知识库），直接 LLM = 闭卷考试（靠训练数据猜） |

## LlamaIndex 四大核心

| 概念 | 要点 |
|------|------|
| Document | 把原始文本包装成 LlamaIndex 能理解的对象 |
| Node | 把 Document 切成小块的文本片段，每块是一个检索单元 |
| Index | 把 Node 向量化后存到索引里，方便语义检索 |
| QueryEngine | 接收问题 → 检索相关 Node → 把原文+问题发给 LLM → 返回答案 |

## 嵌入模型（Embedding）vs LLM

两者是完全不同的模型，在 RAG 里各司其职：

| | 嵌入模型 (Embedding) | 大模型 (LLM) |
|---|---|---|
| 干什么 | 文字 → 向量（浮点数数组） | 文字 → 文字（生成回答） |
| 不能干什么 | 不会写句子、不会回答问题 | 不会算两段话有多相似 |
| 输入 | "云感T恤 129 元" | "根据以下资料回答：{检索结果}，问题是：{用户问题}" |
| 输出 | [0.12, -0.34, 0.67, ...] | "您好，云感T恤售价 129 元" |
| 项目里用的 | BAAI/bge-small-zh-v1.5（本地 CPU） | deepseek-v4-flash（DeepSeek 服务器） |
| 调用时机 | 建索引 + 每次查询向量化问题 | 检索完成后生成回答 |

常用嵌入模型速查：

| 模型 | 维度 | 语言 | 特点 |
|------|------|------|------|
| BAAI/bge-small-zh-v1.5 | 512 | 中文 | 轻量本地跑 |
| BAAI/bge-large-zh-v1.5 | 1024 | 中文 | 同系列大号，更准但更慢 |
| text-embedding-3-small | 512 | 多语言 | OpenAI，API 调用按 Token 计费 |
| moka-ai/m3e-base | 768 | 中文 | 开源社区常用，ModelScope 可下 |

## 分块策略（Chunking）

| 概念 | 要点 |
|------|------|
| 为什么需要切分 | LLM 上下文窗口有限，小块检索更精准，且向量化是按块进行的 |
| SentenceSplitter | LlamaIndex 默认切分器，按句子边界切，不会把一句话砍成两半 |
| chunk_size | 每块最大字符数，越小→Node 越多→检索更精准但上下文更少 |
| chunk_overlap | 相邻两块重叠的字符数，防止关键信息刚好落在两块的边界上被切断 |

## 索引持久化

| 概念 | 要点 |
|------|------|
| 索引持久化 | StorageContext 管理存/读，persist() 序列化到硬盘，load_index_from_storage() 恢复，实测快 19x |
| build once, load many | 建一次索引（build_index.py），以后每次启动直接加载（query_index.py） |

## 对话式 RAG（chat_engine）

| 概念 | 要点 |
|------|------|
| query_engine | 无状态，每次 .query() 独立，不知道已发生过什么对话 |
| chat_engine | 有状态，内部维护 chat_history，自动记住上文 |

### 三种 chat_mode

| mode | 原理 | 实测结论 |
|------|------|---------|
| default | 历史+检索放 messages 列表 | 新版 LlamaIndex 已废弃 |
| condense_question | 先让 LLM 把追问+历史重写成独立问题，再检索 | 结果不稳定，重写后检索可能跑偏 |
| context | 聊天历史全文塞进 system prompt | 中文多轮最稳定，指代消解能力最强 |

## 多文档索引与元数据过滤

| 概念 | 要点 |
|------|------|
| Document(text, metadata) | metadata 是 dict，可存 category/source/date 等任意标签，Node 切分时继承 |
| MetadataFilter(key, operator, value) | 单条过滤规则：字段名 + 运算符 + 目标值 |
| MetadataFilters(filters, condition) | 组合多条 MetadataFilter，condition 为 "and" / "or"（注意小写） |
| index.as_query_engine(filters=...) | 检索时加过滤筛子，同一份索引可用不同 filter 反复查，不需重建 |

## RAG 全链路

```
文档 → Document → Node → Embedding模型 → 向量 → 索引存储
                                                    ↓
用户问题 → Embedding模型 → 问题向量 → 余弦相似度匹配 → top_k Node
                                                    ↓
                            LLM ← prompt(检索结果 + 问题 + 聊天历史)
                                                    ↓
                                                流式回答
```

## 初级 RAG vs 生产级 RAG

| 维度 | 初级 | 生产级 |
|------|------|--------|
| 文档量 | 几份 | 数千～百万份 |
| 存储 | 本地文件 | 向量数据库（Chroma/Milvus/Pinecone） |
| 检索策略 | 纯向量相似度 | 混合检索（向量 + BM25 关键词） |
| 结果优化 | 无 | 重排序（ReRanker） |
| 分块 | 固定 512 | 按文档结构智能切分 |

## RAG 流式输出实战

流式输出分两层：检索阶段同步完成拿到文档，生成阶段 LLM 逐 token 输出。

### LlamaIndex 方式

```python
# chat_engine 流式输出
response = chat.stream_chat("这件T恤是什么面料")
for chunk in response.response_gen:
    print(chunk, end="")
```

`response.response_gen` 是生成器（yield），每轮循环吐出下一个 token。和普通 chat() 的区别只是调用方式——检索逻辑完全一样，LLM 配置里加 streaming=True 即可。

### 核心认知

- **检索和生成分离：** 检索是同步的（必须等文档查完），流式只在 LLM 生成阶段生效
- **yield 生成器：** 函数可以多次返回值，每次 yield 后暂停，下次从暂停处继续；return 只返回一次
- **踩坑：** 检索文档很长时，第一个 token 返回偏慢（LLM 要先处理完整上下文）。可以先前端显示"正在检索..."占位符，再发起带流式的 LLM 调用

---

# ChromaDB 向量数据库

## 核心概念

| 概念 | 要点 |
|------|------|
| 向量数据库 | 存语义（向量）而非存文字——通过比较向量距离来判断"是不是在说同一件事" |
| ChromaDB | 轻量开源向量数据库，Python 原生，适合小中型项目（1000~百万级文档） |
| Collection | ChromaDB 的组织单元，类似 SQL 表——存 documents + embeddings + metadatas + ids |
| chromadb.PersistentClient() | 持久化模式，数据存硬盘，重启还在。比 LlamaIndex 手动 persist 更自动 |
| distance（距离） | ChromaDB 默认返回余弦距离，越小越相似（0=完全相同）。和 LlamaIndex score（越大越相似）相反 |

## 增删改与过滤

| 概念 | 要点 |
|------|------|
| collection.add() | 添加文档，ChromaDB 自动调嵌入模型向量化后存库 |
| collection.query() | 问题自动向量化→和库里所有向量比距离→返回 top_k |
| collection.update(ids=[...]) | 按 ID 更新文档内容和元数据 |
| collection.delete(ids=[...]) | 按 ID 删除文档 |
| collection.upsert() | 存在就更新，不存在就插入——一条命令覆盖两种场景 |
| where={"$and": [...]} | 组合条件过滤，支持 $or、$in、$gte 等操作符。ChromaDB 先过滤再检索，比"先搜出来再筛"更高效 |

## ChromaDB + LlamaIndex 集成

| 概念 | 要点 |
|------|------|
| ChromaVectorStore(chroma_collection=collection) | 把 ChromaDB Collection 包装成 LlamaIndex 认识的 VectorStore |
| StorageContext.from_defaults(vector_store=...) | 告诉 LlamaIndex"向量存在 ChromaDB 里"——存储层可插拔的关键 |
| VectorStoreIndex.from_documents(docs, storage_context=...) | 建索引时自动把向量写入 ChromaDB |
| load_index_from_storage(storage_context=...) | 恢复索引：向量从 ChromaDB 读 + 元数据从磁盘读，不需要重新 embedding |

## ChromaDB vs SimpleVectorStore

| 维度 | SimpleVectorStore | ChromaDB |
|------|-------------------|----------|
| 存储格式 | JSON + .bin 文件 | SQLite + Parquet（数据库引擎） |
| 加载方式 | 全量加载到内存 | 按需读取，有索引加速 |
| 适合文档量 | < 1000 | 1000 ~ 百万级 |
| 并发查询 | 不支持 | 支持多客户端同时查 |
| 增量写入 | 需要 full rebuild | 直接 add，实时可见 |
| 生产环境 | 不适合 | 适合小中型项目 |

面试金句：SimpleVectorStore 适合原型验证，文档量上千或需增量更新时切换到 ChromaDB。切换成本很低——LlamaIndex 的 VectorStore 抽象层让换存储引擎只需改几行代码。

## SimpleVectorStore → ChromaDB 迁移实战

| 概念 | 要点 |
|------|------|
| 迁移改什么 | 改三处：建索引时加 ChromaDB client/collection/ChromaVectorStore；加载时先连 ChromaDB 再 load_index_from_storage；其余代码（分块/嵌入/LLM/chat_engine/过滤）完全不变 |
| 两次持久化 | ChromaDB 自动存向量（SQLite），LlamaIndex 的 persist() 只存元数据（docstore/index_store）——两者各管各的，加载时两个都要 |
| Collection 名称一致性 | build 的 create_collection(name="xxx") 和 app 的 get_collection("xxx") 必须同名 |

---

# Prompt Engineering 五段法

## 结构化 Prompt 五段

| 段落 | 作用 | 回答的问题 |
|------|------|-----------|
| System | 角色定义 | 你是谁？ |
| Context | 背景信息 | 目标用户/平台/竞品是什么？ |
| Instruction | 具体指令 + 输出格式 | 做什么？步骤？输出什么结构？ |
| Examples | 正例 + 反例 | 什么样算好？什么样算差？ |
| Constraints | 约束条件 | 不能做什么？长度/风格限制？ |

## 实测对比（中文商品描述 → 英文亚马逊 listing）

| 版本 | Token | 耗时 | 标题质量 | 卖点呈现 | 输出格式 |
|------|-------|------|---------|---------|---------|
| A. 裸奔 | 1197 | 12.1s | 中式直译 | 黏在一起 | 自由发挥 |
| B. 一句话 | 537 | 4.8s | 略有优化 | 有分段 | 自由发挥 |
| C. 五段法 | 1460 | 10.3s | SEO 友好 | 逐一拆开 | 严格按模板 |

结论：五段法 Token 最多但买到了可控性——固定输出格式、卖点分离清晰、英文更地道。工程化场景里这点成本换稳定性完全值得。

## 核心认知

- **可控性 > Token 成本：** 多花几百 Token 换来固定结构，后续解析/展示不用再猜格式
- **Constraint 比 Instruction 更有效：** "不要直译"四个字挡掉了前两个版本的主要问题
- **工作流化：** prompt 模板固化后，同品类只需换 Context，不复用重写

## 踩坑

- **prompt 一致性：** 改一段（Context）没改另一段（Examples），模型跟着旧信息跑偏。全部关联段落要同步改
- **user message 权重 ≥ system prompt：** 两边冲突时模型倾向信 user message。改了 prompt 模板还要检查输入里有没有矛盾信息
- **测试关键词要对齐语言：** check_contains 用中文关键词但模型输出英文 → 误报 FAIL。关键词要和 prompt 约束的输出语言一致
- **Context 不要列能力：** Context 是给背景信息（发件人身份、收件人、行业），不是复读 System 角色描述
