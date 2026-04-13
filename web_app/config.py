"""
配置文件 - 存放所有配置
支持从环境变量读取（Docker 部署时使用）
"""

import os

# ==================== API 配置 ====================
# DeepSeek API Key
# 优先从环境变量读取，没有则用默认值（本地开发时）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-49a64f6aac9f4b508cfb147009565274")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# Embedding API Key
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "sk-afmphtocipluraxgokpkswcpwiogxhftoacetqqipsfaxbiq")
EMBEDDING_BASE_URL = "https://api.siliconflow.cn"
EMBEDDING_MODEL = "BAAI/bge-m3"

# ==================== 路径配置 ====================
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

CHROMA_PATH = os.path.join(PROJECT_ROOT, "data", "chroma_db")
KNOWLEDGE_BASE_PATH = os.path.join(PROJECT_ROOT, "knowledge_base")

# ==================== RAG 配置 ====================
TOP_K = 5
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
SIMILARITY_THRESHOLD = 1.5