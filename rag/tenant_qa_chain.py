"""
多租户问答链
"""
import sqlite3
import os
from typing import Dict, Any
from web_app.database import DatabaseManager


class TenantQAChain:
    def __init__(self, tenant_id: str, user_id: str, db_manager: DatabaseManager):
        self.tenant_id = tenant_id
        self.user_id = user_id
        self.db_manager = db_manager

        # 初始化检索器
        from rag.tenant_retriever import TenantRetriever
        self.retriever = TenantRetriever(tenant_id, db_manager)

        # 初始化 LLM
        from langchain_openai import ChatOpenAI
        self.llm = ChatOpenAI(
            temperature=0.7,
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key=os.getenv("DEEPSEEK_API_KEY", "sk-your-deepseek-api-key")
        )

        # 创建对话链
        from langchain.chains.retrieval_qa.base import ConversationalRetrievalChain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            self.llm,
            retriever=self.retriever,
            return_source_documents=True
        )

    def ask(self, question: str) -> Dict[str, Any]:
        """提问"""
        # 记录审计日志
        self.db_manager.log_action(
            tenant_id=self.tenant_id,
            user_id=self.user_id,
            action="ask_question",
            target_id="n/a",
            details={"question": question}
        )

        # 生成答案
        result = self.qa_chain.invoke({"question": question, "chat_history": []})

        # 提取文档 ID
        doc_ids = []
        if "source_documents" in result:
            doc_ids = [doc.metadata.get('doc_id', '') for doc in result["source_documents"]]

        # 保存问答历史
        import uuid
        history_id = str(uuid.uuid4())
        conn = sqlite3.connect('data/test_04.db')
        cursor = conn.cursor()

        cursor.execute('''
                       INSERT INTO ask_history (history_id, tenant_id, user_id, question, answer, doc_ids)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', (history_id, self.tenant_id, self.user_id, question, result.get('answer', ''),
                             ','.join(doc_ids)))

        conn.commit()
        conn.close()

        # 返回结果
        return {
            "answer": result.get('answer', ''),
            "source_documents": result.get('source_documents', []),
            "history_id": history_id
        }