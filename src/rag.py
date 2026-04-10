"""
RAG 模块 - 文档处理和向量检索
"""

import os
import chromadb
from langchain_community.document_loaders import TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import KNOWLEDGE_BASE_PATH, CHROMA_PATH, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K


class KnowledgeBase:
    """知识库管理器"""
    
    def __init__(self):
        self.embedding_url = "https://api.siliconflow.cn/v1/embeddings"
        self.embedding_key = "your-siliconflow-api-key"
        self.embedding_model = "BAAI/bge-m3"
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        self._ensure_dirs()
    
    def _ensure_dirs(self):
        os.makedirs(KNOWLEDGE_BASE_PATH, exist_ok=True)
        os.makedirs(CHROMA_PATH, exist_ok=True)
    
    def _get_loader(self, file_path):
        if file_path.endswith('.md'):
            return UnstructuredMarkdownLoader(file_path)
        return TextLoader(file_path, encoding='utf-8')
    
    def _embed_text(self, text):
        import requests
        response = requests.post(
            self.embedding_url,
            headers={"Authorization": f"Bearer {self.embedding_key}", "Content-Type": "application/json"},
            json={"model": self.embedding_model, "input": text}
        )
        if response.status_code == 200:
            return response.json()["data"][0]["embedding"]
        raise Exception(f"Embedding API 错误: {response.status_code}")
    
    def add_document(self, filename):
        file_path = os.path.join(KNOWLEDGE_BASE_PATH, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {filename}")
        
        loader = self._get_loader(file_path)
        documents = loader.load()
        texts = self.text_splitter.split_documents(documents)
        
        if not texts:
            raise ValueError("文档内容为空")
        
        self._save_to_chroma(texts, filename)
        return f"成功添加文档 {filename}，共 {len(texts)} 个片段"
    
    def _save_to_chroma(self, texts, source):
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        try:
            collection = client.get_collection("knowledge_base")
        except:
            collection = client.create_collection("knowledge_base")
        
        existing = collection.get()
        if existing and existing['metadatas']:
            ids_to_delete = [existing['ids'][i] for i, m in enumerate(existing['metadatas']) if m.get('source') == source]
            if ids_to_delete:
                collection.delete(ids_to_delete)
        
        embeddings = [self._embed_text(t.page_content) for t in texts]
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            collection.add(ids=[f"{source}_{i}"], documents=[text.page_content], embeddings=[embedding], metadatas=[{"source": source}])
    
    def search(self, query, top_k=None):
        if top_k is None:
            top_k = TOP_K
        if not os.path.exists(CHROMA_PATH):
            return []
        
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        try:
            collection = client.get_collection("knowledge_base")
        except:
            return []
        
        query_embedding = self._embed_text(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
        
        if not results or not results['documents']:
            return []
        
        docs = []
        for i, doc in enumerate(results['documents'][0]):
            source = results['metadatas'][0][i].get('source', 'unknown')
            docs.append({'content': doc, 'source': source, 'score': results['distances'][0][i] if 'distances' in results else 0})
        return docs
    
    def list_documents(self):
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
        return list(set(m['source'] for m in existing['metadatas'] if 'source' in m))
    
    def delete_document(self, filename):
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
        
        ids_to_delete = [existing['ids'][i] for i, m in enumerate(existing['metadatas']) if m.get('source') == filename]
        if not ids_to_delete:
            return f"未找到文件: {filename}"
        
        collection.delete(ids_to_delete)
        file_path = os.path.join(KNOWLEDGE_BASE_PATH, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        return f"已删除文档: {filename}"


kb = KnowledgeBase()
