"""
RAG 模块 - 文档处理和向量检索
"""

import os
import chromadb
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    KNOWLEDGE_BASE_PATH,
    CHROMA_PATH,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K
)


class KnowledgeBase:
    """知识库管理器"""

    def __init__(self):
        # 硅基流动 Embedding API（国内可用，免费）
        self.embedding_url = "https://api.siliconflow.cn/v1/embeddings"
        self.embedding_key = "sk-afmphtocipluraxgokpkswcpwiogxhftoacetqqipsfaxbiq"  # 替换成你的！
        self.embedding_model = "BAAI/bge-m3"

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保目录存在"""
        os.makedirs(KNOWLEDGE_BASE_PATH, exist_ok=True)
        os.makedirs(CHROMA_PATH, exist_ok=True)

    def _get_loader(self, file_path):
        """根据文件类型选择加载器"""
        if file_path.endswith('.md'):
            return UnstructuredMarkdownLoader(file_path)
        else:
            return TextLoader(file_path, encoding='utf-8')

    def _embed_text(self, text):
        """使用硅基流动获取文本向量"""
        import requests

        response = requests.post(
            self.embedding_url,
            headers={
                "Authorization": f"Bearer {self.embedding_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.embedding_model,
                "input": text
            }
        )

        if response.status_code == 200:
            return response.json()["data"][0]["embedding"]
        else:
            raise Exception(f"Embedding API 错误: {response.status_code} - {response.text}")

    def add_document(self, filename):
        """添加文档到知识库"""
        file_path = os.path.join(KNOWLEDGE_BASE_PATH, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {filename}")

        # 加载文档
        loader = self._get_loader(file_path)
        documents = loader.load()

        # 切分文本
        texts = self.text_splitter.split_documents(documents)

        if not texts:
            raise ValueError("文档内容为空")

        # 存入向量数据库
        self._save_to_chroma(texts, filename)

        return f"成功添加文档 {filename}，共 {len(texts)} 个片段"

    def _save_to_chroma(self, texts, source):
        """保存到 Chroma 向量库"""
        # 连接/创建向量库
        client = chromadb.PersistentClient(path=CHROMA_PATH)

        # 获取或创建 collection
        try:
            collection = client.get_collection("knowledge_base")
        except:
            collection = client.create_collection("knowledge_base")

        # 清空该文件的历史数据
        existing = collection.get()
        if existing and existing['metadatas']:
            ids_to_delete = [
                existing['ids'][i] for i, m in enumerate(existing['metadatas'])
                if m.get('source') == source
            ]
            if ids_to_delete:
                collection.delete(ids_to_delete)

        # 获取所有文本的向量
        embeddings = []
        for text in texts:
            emb = self._embed_text(text.page_content)
            embeddings.append(emb)

        # 添加新数据
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            doc_id = f"{source}_{i}"
            collection.add(
                ids=[doc_id],
                documents=[text.page_content],
                embeddings=[embedding],
                metadatas=[{"source": source}]
            )

    def search(self, query, top_k=None):
        """检索知识库"""
        if top_k is None:
            top_k = TOP_K

        # 检查向量库是否存在
        if not os.path.exists(CHROMA_PATH):
            return []

        client = chromadb.PersistentClient(path=CHROMA_PATH)

        try:
            collection = client.get_collection("knowledge_base")
        except:
            return []

        # 获取查询向量
        query_embedding = self._embed_text(query)

        # 检索
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        if not results or not results['documents']:
            return []

        # 整理结果
        docs = []
        for i, doc in enumerate(results['documents'][0]):
            source = results['metadatas'][0][i].get('source', 'unknown') if results['metadatas'] else 'unknown'
            docs.append({
                'content': doc,
                'source': source,
                'score': results['distances'][0][i] if 'distances' in results else 0
            })

        return docs

    def list_documents(self):
        """列出知识库中的文档"""
        if not os.path.exists(CHROMA_PATH):
            return []

        client = chromadb.PersistentClient(path=CHROMA_PATH)

        try:
            collection = client.get_collection("knowledge_base")
        except:
            return []

        existing = collection.get()
        if not existing or not existing['metadatas']:
            return []

        # 去重获取文件列表
        sources = set()
        for m in existing['metadatas']:
            if 'source' in m:
                sources.add(m['source'])

        return list(sources)

    def delete_document(self, filename):
        """删除知识库中的文档"""
        if not os.path.exists(CHROMA_PATH):
            return "向量库不存在"

        client = chromadb.PersistentClient(path=CHROMA_PATH)

        try:
            collection = client.get_collection("knowledge_base")
        except:
            return "向量库不存在"

        existing = collection.get()
        if not existing or not existing['metadatas']:
            return "知识库为空"

        # 找出要删除的 ID
        ids_to_delete = [
            existing['ids'][i] for i, m in enumerate(existing['metadatas'])
            if m.get('source') == filename
        ]

        if not ids_to_delete:
            return f"未找到文件: {filename}"

        collection.delete(ids_to_delete)

        # 同时删除原文件
        file_path = os.path.join(KNOWLEDGE_BASE_PATH, filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        return f"已删除文档: {filename}"


# 全局实例
kb = KnowledgeBase()