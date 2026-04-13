"""
数据库模型 - 多租户企业知识库 SaaS
"""
import sqlite3
from datetime import datetime
import hashlib
import json
from typing import Optional


class DatabaseManager:
    def __init__(self, db_path: str = "data/knowledge_multi_tenant.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 创建租户表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS tenants
                       (
                           tenant_id
                           TEXT
                           PRIMARY
                           KEY,
                           tenant_name
                           TEXT
                           NOT
                           NULL,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           status
                           INTEGER
                           DEFAULT
                           1
                       )
                       ''')

        # 创建用户表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           user_id
                           TEXT
                           PRIMARY
                           KEY,
                           tenant_id
                           TEXT
                           NOT
                           NULL,
                           username
                           TEXT
                           UNIQUE,
                           email
                           TEXT,
                           password_hash
                           TEXT,
                           role
                           TEXT
                           DEFAULT
                           'user',
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           tenant_id
                       ) REFERENCES tenants
                       (
                           tenant_id
                       )
                           )
                       ''')

        # 创建文档表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS documents
                       (
                           doc_id
                           TEXT
                           PRIMARY
                           KEY,
                           tenant_id
                           TEXT
                           NOT
                           NULL,
                           filename
                           TEXT
                           NOT
                           NULL,
                           file_path
                           TEXT,
                           upload_time
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           hit_count
                           INTEGER
                           DEFAULT
                           0,
                           created_by
                           TEXT,
                           FOREIGN
                           KEY
                       (
                           tenant_id
                       ) REFERENCES tenants
                       (
                           tenant_id
                       ),
                           FOREIGN KEY
                       (
                           created_by
                       ) REFERENCES users
                       (
                           user_id
                       )
                           )
                       ''')

        # 创建问答历史表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS ask_history
                       (
                           history_id
                           TEXT
                           PRIMARY
                           KEY,
                           tenant_id
                           TEXT
                           NOT
                           NULL,
                           user_id
                           TEXT,
                           question
                           TEXT
                           NOT
                           NULL,
                           answer
                           TEXT,
                           doc_ids
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           FOREIGN
                           KEY
                       (
                           tenant_id
                       ) REFERENCES tenants
                       (
                           tenant_id
                       ),
                           FOREIGN KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           user_id
                       )
                           )
                       ''')

        # 创建审计日志表
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS audit_logs
                       (
                           log_id
                           TEXT
                           PRIMARY
                           KEY,
                           tenant_id
                           TEXT
                           NOT
                           NULL,
                           user_id
                           TEXT,
                           action
                           TEXT
                           NOT
                           NULL,
                           target_id
                           TEXT,
                           timestamp
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           details
                           TEXT
                       )
                       ''')

        conn.commit()
        conn.close()

    def create_tenant(self, tenant_name: str) -> str:
        """创建租户"""
        tenant_id = f"tenant_{hashlib.md5(tenant_name.encode()).hexdigest()[:8]}"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       INSERT INTO tenants (tenant_id, tenant_name)
                       VALUES (?, ?)
                       ''', (tenant_id, tenant_name))

        conn.commit()
        conn.close()
        return tenant_id

    def create_user(self, tenant_id: str, username: str, email: str, password: str, role: str = 'user') -> str:
        """创建用户"""
        user_id = f"user_{hashlib.md5(f"{tenant_id}_{username}".encode()).hexdigest()[:8]}"
        password_hash = hashlib.md5(password.encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       INSERT INTO users (user_id, tenant_id, username, email, password_hash, role)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', (user_id, tenant_id, username, email, password_hash, role))

        conn.commit()
        conn.close()
        return user_id

    def verify_user(self, username: str, password: str) -> Optional[dict]:
        """验证用户登录"""
        password_hash = hashlib.md5(password.encode()).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT user_id, tenant_id, username, role
                       FROM users
                       WHERE username = ?
                         AND password_hash = ?
                       ''', (username, password_hash))

        user = cursor.fetchone()
        conn.close()

        if user:
            return {
                "user_id": user[0],
                "tenant_id": user[1],
                "username": user[2],
                "role": user[3]
            }
        return None

    def log_action(self, tenant_id: str, user_id: str, action: str, target_id: str, details: dict = None):
        """记录审计日志"""
        import uuid
        log_id = str(uuid.uuid4())
        details_json = json.dumps(details) if details else "{}"

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       INSERT INTO audit_logs (log_id, tenant_id, user_id, action, target_id, timestamp, details)
                       VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                       ''', (log_id, tenant_id, user_id, action, target_id, details_json))

        conn.commit()
        conn.close()

    def increment_doc_hit(self, tenant_id: str, doc_id: str):
        """增加文档命中次数"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       UPDATE documents
                       SET hit_count = hit_count + 1
                       WHERE tenant_id = ?
                         AND doc_id = ?
                       ''', (tenant_id, doc_id))

        conn.commit()
        conn.close()

    def get_tenant_stats(self, tenant_id: str) -> dict:
        """获取租户统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 文档数
        cursor.execute('SELECT COUNT(*) FROM documents WHERE tenant_id = ?', (tenant_id,))
        doc_count = cursor.fetchone()[0]

        # 用户数
        cursor.execute('SELECT COUNT(*) FROM users WHERE tenant_id = ?', (tenant_id,))
        user_count = cursor.fetchone()[0]

        # 问答数
        cursor.execute('SELECT COUNT(*) FROM ask_history WHERE tenant_id = ?', (tenant_id,))
        ask_count = cursor.fetchone()[0]

        conn.close()

        return {
            "doc_count": doc_count,
            "user_count": user_count,
            "ask_count": ask_count
        }

    def get_top_docs(self, tenant_id: str, limit: int = 10) -> list:
        """获取热门文档"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
                       SELECT doc_id, filename, hit_count
                       FROM documents
                       WHERE tenant_id = ?
                       ORDER BY hit_count DESC LIMIT ?
                       ''', (tenant_id, limit))

        docs = [{"doc_id": row[0], "filename": row[1], "hit_count": row[2]} for row in cursor.fetchall()]
        conn.close()

        return docs