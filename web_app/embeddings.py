"""
Embedding 管理器 - 文本向量化
把文字转换成数字向量，存入向量数据库
"""

import os
import requests
import chromadb
from chromadb.config import Settings
import config


class EmbeddingManager:
    """
    Embedding 管理器

    作用：
    1. 把文本转换成向量
    2. 存入 Chroma 向量数据库
    3. 根据问题检索相似文本
    """

    def __init__(self):
        """初始化"""
        self.embedding_url = config.EMBEDDING_BASE_URL
        self.embedding_key = config.EMBEDDING_API_KEY
        self.embedding_model = config.EMBEDDING_MODEL

        # 确保目录存在
        os.makedirs(config.CHROMA_PATH, exist_ok=True)

        # 创建 Chroma 客户端
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_PATH,
            settings=Settings(anonymized_telemetry=False)  # 关闭匿名遥测
        )

        # 获取或创建集合（collection）
        self.collection = self.client.get_or_create_collection(
            "knowledge_base",
            metadata={"description": "企业知识库向量存储"}
        )

        print(f"✅ EmbeddingManager 初始化完成")
        print(f"   向量库路径: {config.CHROMA_PATH}")

    def _call_embedding_api(self, texts):
        """
        调用硅基流动 API，把文本转成向量

        参数:
            texts: 文本列表（单个字符串 或 字符串列表）

        返回:
            向量列表
        """
        # 1. 检查 API Key
        if not self.embedding_key or self.embedding_key == "your-siliconflow-api-key":
            raise ValueError("❌ 请先配置 EMBEDDING_API_KEY！")

        # 2. 确保是列表
        if isinstance(texts, str):
            texts = [texts]

        # 3. 调用 API
        response = requests.post(
            config.EMBEDDING_BASE_URL + "/v1/embeddings",
            headers={
                "Authorization": f"Bearer {self.embedding_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.embedding_model,
                "input": texts  # 传入列表，API 会批量处理
            },
            timeout=30
        )

        # 4. 检查结果
        if response.status_code == 200:
            data = response.json()
            return [item["embedding"] for item in data["data"]]

        elif response.status_code == 401:
            raise ValueError("❌ Embedding API Key 无效！")

        else:
            raise Exception(f"❌ Embedding API 错误: {response.status_code} - {response.text}")

    def add_documents(self, chunks, source):
        """
        添加文档到向量库

        参数:
            chunks: Document 对象列表（LangChain 格式）
            source: 文档来源/文件名
        """
        # 1. 先删除旧数据（同一个文件重新上传时）
        self._delete_by_source(source)

        # 2. 提取所有文本
        texts = [chunk.page_content for chunk in chunks]

        # 3. 批量转成向量（比一个个转快很多）
        embeddings = self._call_embedding_api(texts)

        # 4. 存入向量库
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            doc_id = f"{source}_{i}"
            self.collection.add(
                ids=[doc_id],
                documents=[text],
                embeddings=[embedding],
                metadatas=[{"source": source, "chunk_index": i}]
            )

        print(f"✅ 已添加 {len(texts)} 个文档块: {source}")

    def _delete_by_source(self, source):
        """删除指定来源的所有文档"""
        existing = self.collection.get()
        if existing and existing["ids"]:
            ids_to_delete = [
                existing["ids"][i]
                for i, m in enumerate(existing["metadatas"])
                if m.get("source") == source
            ]
            if ids_to_delete:
                self.collection.delete(ids_to_delete)
                print(f"🗑️  删除旧数据: {len(ids_to_delete)} 条")

    def search(self, query, top_k=None):
        """
        搜索最相关的文档

        参数:
            query: 查询文本
            top_k: 返回多少条（默认从 config 读取）

        返回:
            列表，每个元素是 dict: {content, source, score}
        """
        if top_k is None:
            top_k = config.TOP_K

        # 1. 把查询文本转成向量
        query_embedding = self._call_embedding_api(query)[0]

        # 2. 在向量库中搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        # 3. 整理结果
        if not results or not results["documents"]:
            return []

        docs = []
        for i, doc in enumerate(results["documents"][0]):
            distance = results["distances"][0][i] if "distances" in results else 0
            source = results["metadatas"][0][i].get("source", "unknown") if results["metadatas"] else "unknown"

            docs.append({
                "content": doc,
                "source": source,
                "score": distance
            })

        return docs

    def list_documents(self):
        """列出所有已存储的文档"""
        existing = self.collection.get()
        if not existing or not existing["metadatas"]:
            return []

        sources = set()
        for m in existing["metadatas"]:
            if "source" in m:
                sources.add(m["source"])

        return sorted(list(sources))

    def delete_all(self):
        """清空向量库"""
        try:
            self.client.delete_collection("knowledge_base")
            # 重新创建集合
            self.collection = self.client.get_or_create_collection(
                "knowledge_base",
                metadata={"description": "企业知识库向量存储"}
            )
            print("🗑️ 向量库已清空")
        except Exception as e:
            print(f"清空向量库失败: {e}")


# ==================== 独立测试 ====================
if __name__ == "__main__":
    print("\n🧪 测试 EmbeddingManager\n")

    try:
        manager = EmbeddingManager()

        # 测试：列出已有文档
        docs = manager.list_documents()
        print(f"\n📚 知识库已有文档: {docs}")

        print("\n✅ EmbeddingManager 测试完成！")

    except Exception as e:
        print(f"❌ 错误: {e}")