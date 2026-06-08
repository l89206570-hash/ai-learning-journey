# 电商智能客服 RAG

基于 LlamaIndex + ChromaDB + DeepSeek 的跨境电商智能客服系统，支持语义检索、品类过滤、流式对话和多轮记忆。

## 技术栈

| 组件 | 技术 |
|------|------|
| LLM | DeepSeek V4 Flash |
| Embedding | BAAI/bge-small-zh-v1.5 |
| RAG 框架 | LlamaIndex |
| 向量库 | ChromaDB（持久化） |
| 前端 | Streamlit |
| 部署 | Docker + docker-compose |

## 快速开始

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env，填入你的 DEEPSEEK_API_KEY
```

### 2. 构建索引

```bash
docker compose run --rm build_index
```

### 3. 启动应用

```bash
docker compose up app
```

浏览器打开 `http://localhost:8501`

## 项目结构

```
.
├── app.py              # Streamlit 界面
├── build_index.py      # 知识库索引构建
├── config.py           # 环境变量配置
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── tests/
│   └── test_queries.py # 固定测试集
└── ecommerce_docs/     # 知识库源文件
    ├── faq.txt
    ├── products.txt
    └── policy.txt
```

## 测试

```bash
# 先确保 ChromaDB 索引已构建
docker compose run --rm build_index

# 运行测试
python tests/test_queries.py
```

### 测试结果（2026-06-05）

| # | 品类 | 查询 | 结果 |
|---|------|------|------|
| 1 | 全部 | "你们支持哪些快递" | 命中 policy.txt, score=0.86 |
| 2 | 产品 | "这款面霜适合什么肤质" | 命中 products.txt, score=0.91 |
| 3 | FAQ | "怎么成为会员" | 命中 faq.txt, score=0.78 |
| 4 | 全部 | "发货要多久" | 命中 policy.txt, score=0.83 |
| 5 | 售后 | "怎么退货" | 命中 policy.txt, score=0.88 |

## 部署到生产

本地开发用 Docker Compose。如需对外服务，建议：

1. 前端：Streamlit → FastAPI + Nginx 反向代理
2. 认证：至少加一层 Basic Auth
3. 日志：接入 LangFuse 追踪每次 LLM 调用
4. 监控：接入 Prometheus + Grafana
