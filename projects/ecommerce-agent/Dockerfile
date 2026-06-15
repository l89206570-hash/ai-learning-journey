FROM python:3.11-slim

WORKDIR /app

# 系统依赖（ChromaDB 需要 sqlite3）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 先装依赖（利用 Docker 层缓存）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 拷代码
COPY . .

# Streamlit 端口
EXPOSE 8501

# 默认启动 Streamlit
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
