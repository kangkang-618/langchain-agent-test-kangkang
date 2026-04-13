"""
重排序模块 - 提高检索准确性
当检索结果较多时，用重排序模型选出最相关的几个
"""

import requests
import config


class Reranker:
    """
    重排序器

    作用：初步检索得到多个结果，再用重排序模型排序，
         选出最符合用户问题的几个
    """

    def __init__(self):
        self.api_key = config.EMBEDDING_API_KEY
        self.model = "BAAI/bge-reranker-base"  # 轻量级重排序模型

        # 如果用免费的向量模型做重排序，不需要额外 API
        # 这里用 Embedding 模型模拟重排序
        self.embedding_url = f"{config.EMBEDDING_BASE_URL}/v1/embeddings"

    def rerank(self, query, documents, top_k=3):
        """
        对文档进行重排序

        参数:
            query: 用户的问题
            documents: 文档列表 [{content, source, score}]
            top_k: 返回多少个

        返回:
            重排序后的文档列表
        """
        if not documents:
            return []

        if len(documents) <= top_k:
            return documents

        # 方法：用 Embedding 计算 query 和每个 doc 的相似度
        # 相似度越高的越相关

        scored_docs = []
        for doc in documents:
            # 计算 query 和 doc 的语义相似度
            similarity = self._calculate_similarity(query, doc["content"])
            scored_docs.append({
                "content": doc["content"],
                "source": doc["source"],
                "score": doc["score"],
                "rerank_score": similarity
            })

        # 按重排序分数降序排列
        reranked = sorted(scored_docs, key=lambda x: x["rerank_score"], reverse=True)

        return reranked[:top_k]

    def _calculate_similarity(self, text1, text2):
        """
        计算两个文本的语义相似度
        使用向量点积作为相似度指标
        """
        try:
            import numpy as np

            # 获取两个文本的向量
            emb1 = self._get_embedding(text1)
            emb2 = self._get_embedding(text2)

            # 计算点积（相似度）
            dot_product = sum(a * b for a, b in zip(emb1, emb2))

            return dot_product

        except Exception as e:
            # 如果出错，返回原始分数
            return 1.0

    def _get_embedding(self, text):
        """获取文本向量"""
        response = requests.post(
            self.embedding_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "input": text
            },
            timeout=30
        )

        if response.status_code == 200:
            return response.json()["data"][0]["embedding"]
        else:
            raise Exception(f"Embedding 错误: {response.status_code}")


# ==================== 独立测试 ====================
if __name__ == "__main__":
    print("\n🧪 测试 Reranker\n")

    reranker = Reranker()

    # 模拟一些检索结果
    docs = [
        {"content": "Python 是一种编程语言", "source": "doc1.txt", "score": 0.5},
        {"content": "人工智能 AI 很重要", "source": "doc2.txt", "score": 0.6},
        {"content": "RAG 是检索增强生成技术", "source": "doc3.txt", "score": 0.4},
        {"content": "机器学习是 AI 的子领域", "source": "doc4.txt", "score": 0.3},
        {"content": "Java 是一种编程语言", "source": "doc5.txt", "score": 0.7},
    ]

    query = "什么是 RAG？"
    print(f"问题: {query}")
    print(f"原始结果: {len(docs)} 个文档")

    # 重排序
    reranked = reranker.rerank(query, docs, top_k=3)

    print(f"\n重排序后: {len(reranked)} 个最相关文档")
    for i, doc in enumerate(reranked, 1):
        print(f"  [{i}] {doc['source']}")
        print(f"      原始分数: {doc['score']:.4f}, 重排分数: {doc['rerank_score']:.4f}")
        print(f"      内容: {doc['content']}")

    print("\n✅ Reranker 测试完成！")