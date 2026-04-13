"""
多租户 RAG 检索器
"""
import os
from typing import List, Dict, Any
from web_app.database import DatabaseManager


class TenantRetriever:
    def __init__(self, tenant_id: str, db_manager: DatabaseManager):
        self.tenant_id = tenant_id
        self.db_manager = db_manager

        # 每个 tenant 有独立的 Chroma collection
        self.persist_directory = f"data/chroma_db/{tenant_id}"
        self.collection_name = f"tenant_{tenant_id}"

        # 初始化 embeddings
        from langchain_openai import OpenAIEmbeddings
        self.embeddings = OpenAIEmbeddings(
            base_url="https://api.siliconflow.cn/v1",
            api_key=os.getenv("EMBEDDING_API_KEY", "your-siliconflow-api-key")
        )

        # 初始化 Chroma
        try:
            from langchain_chroma import Chroma
            self.vectorstore = Chroma(
                client=None,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
        except ImportError:
            from langchain_community.vectorstores import Chroma
            self.vectorstore = Chroma(
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
                persist_directory=self.persist_directory
            )
        except Exception as e:
            print(f"初始化 Chroma 失败: {e}")
            self.vectorstore = None

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """在当前租户的文档中搜索"""
        if self.vectorstore is None:
            return []

        try:
            results = self.vectorstore.similarity_search(
                query=query,
                k=top_k
            )
        except Exception as e:
            print(f"搜索失败: {e}")
            results = []

        # 增加命中次数
        for doc in results:
            try:
                self.db_manager.increment_doc_hit(self.tenant_id, doc.metadata.get('doc_id'))
            except:
                pass

        return results