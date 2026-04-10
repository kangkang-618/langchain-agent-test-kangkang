"""
配置文件 - 企业级知识库问答系统
"""

import os

# ========== API 配置 ==========
# DeepSeek API（国内可用）- 请替换成你的 API Key
DEEPSEEK_API_KEY = "sk-your-deepseek-api-key"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# Embedding 模型（用硅基流动）
EMBEDDING_API_KEY = "your-siliconflow-api-key"  # 请替换成你的硅基流动 API Key

# ========== 路径配置 ==========
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_PATH = os.path.join(PROJECT_ROOT, "data", "chroma_db")
KNOWLEDGE_BASE_PATH = os.path.join(PROJECT_ROOT, "knowledge_base")

# ========== RAG 配置 ==========
TOP_K = 3
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ========== Agent 配置 ==========
MAX_REACT_STEPS = 5
SEARCH_ENABLED = False
MAX_SEARCH_RESULTS = 3
