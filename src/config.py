"""
配置文件 - 企业级知识库问答系统
"""

import os

# ========== API 配置 ==========
# DeepSeek API（国内可用）
DEEPSEEK_API_KEY = "sk-49a64f6aac9f4b508cfb147009565274" # 替换成你的！
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# Embedding 模型（用 DeepSeek 的 embedding）
EMBEDDING_MODEL = "deepseek-embed"
EMBEDDING_API_KEY = DEEPSEEK_API_KEY
EMBEDDING_BASE_URL = DEEPSEEK_BASE_URL

# ========== 路径配置 ==========
# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 向量数据库路径
CHROMA_PATH = os.path.join(PROJECT_ROOT, "data", "chroma_db")

# 知识库文档路径
KNOWLEDGE_BASE_PATH = os.path.join(PROJECT_ROOT, "knowledge_base")

# ========== RAG 配置 ==========
# 每次检索的文档数量
TOP_K = 3

# 文档分块大小
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# ========== Agent 配置 ==========
# 最大推理步数
MAX_REACT_STEPS = 5

# 是否启用搜索
SEARCH_ENABLED = True

# 搜索结果数量
MAX_SEARCH_RESULTS = 3