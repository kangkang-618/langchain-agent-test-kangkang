"""
配置文件 - 多租户企业知识库 SaaS
"""
import os
from web_app.database import DatabaseManager
import os

# ==================== API 配置 ====================
# DeepSeek API
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-49a64f6aac9f4b508cfb147009565274")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 硅基流动 Embedding API（国内可用，免费）
EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", "sk-afmphtocipluraxgokpkswcpwiogxhftoacetqqipsfaxbiq")
EMBEDDING_BASE_URL = "https://api.siliconflow.cn/v1"
EMBEDDING_MODEL = "BAAI/bge-m3"

# ==================== 多租户配置 ====================
# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据库路径
DB_PATH = os.path.join(PROJECT_ROOT, "data", "knowledge_multi_tenant.db")

# 向量数据库路径（每个租户独立）
CHROMA_BASE_PATH = os.path.join(PROJECT_ROOT, "data", "chroma_multi_tenant")

# 知识库文档路径
KNOWLEDGE_BASE_PATH = os.path.join(PROJECT_ROOT, "knowledge_base")

# ==================== RAG 配置 ====================
# 每次检索的文档数量
TOP_K = 5

# 文档分块大小（中文建议 300-500）
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50

# 检索相似度阈值（低于此值的结果会被过滤）
SIMILARITY_THRESHOLD = 1.5


# ==================== 会话管理 ====================
class SessionManager:
    """会话管理器"""
    _instance = None

    def __init__(self):
        self.current_tenant_id = None
        self.current_user_id = None
        self.current_user_role = None
        self.current_tenant_name = None
        self.current_username = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = SessionManager()
        return cls._instance

    def login(self, tenant_id: str, user_id: str, role: str, tenant_name: str = "", username: str = ""):
        """登录"""
        self.current_tenant_id = tenant_id
        self.current_user_id = user_id
        self.current_user_role = role
        self.current_tenant_name = tenant_name
        self.current_username = username

    def logout(self):
        """登出"""
        self.current_tenant_id = None
        self.current_user_id = None
        self.current_user_role = None
        self.current_tenant_name = None
        self.current_username = None

    def is_logged_in(self) -> bool:
        """是否已登录"""
        return self.current_user_id is not None

    def can_upload_doc(self) -> bool:
        """是否可以上传文档"""
        return self.is_logged_in() and self.current_user_role in ['admin', 'user']

    def can_delete_doc(self) -> bool:
        """是否可以删除文档"""
        return self.is_logged_in() and self.current_user_role in ['admin', 'user']

    def can_view_admin(self) -> bool:
        """是否可以查看管理后台"""
        return self.is_logged_in() and self.current_user_role in ['admin']
# ==================== 数据库管理器 ====================
# 在文件底部初始化数据库管理器
db_manager = DatabaseManager(DB_PATH)

# ==================== 会话管理器实例 ====================
session = SessionManager.get_instance()


# ==================== 应用配置 ====================
APP_TITLE = "🏢 企业知识库 SaaS"

WELCOME_MESSAGE = """
欢迎使用企业知识库 SaaS！

**功能特点：**
- 🏢 多租户隔离（每个企业数据完全隔离）
- 🔐 权限管理（管理员、普通用户、只读用户）
- 📊 数据统计（文档数、问答数、用户数）
- 📖 来源标注
- 💬 多轮对话
"""