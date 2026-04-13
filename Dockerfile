# 基于 Python 3.11 镜像
import WORKDIR
import data

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖（chromadb 需要）
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 创建数据目录
RUN mkdir -p data/knowledge_base data/chroma_db

# 暴露端口
EXPOSE 8501

# 启动命令
CMD ["streamlit", "run", "web_app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]