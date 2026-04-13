"""
检索器 - 根据问题找最相关的文档
"""

import re
from embeddings import EmbeddingManager
import config


class Retriever:
    """
    检索器

    作用：接收用户问题，返回最相关的文档
    """

    def __init__(self, embedding_manager=None):
        """
        初始化检索器

        参数:
            embedding_manager: EmbeddingManager 实例（可选，不传会自动创建）
        """
        if embedding_manager is None:
            self.embedding_manager = EmbeddingManager()
        else:
            self.embedding_manager = embedding_manager

    def retrieve(self, query, top_k=None, min_score=None):
        """
        检索相关文档

        参数:
            query: 用户的问题
            top_k: 返回多少条（默认从 config 读取）
            min_score: 相似度阈值（分数高于这个才认为是相关的）

        返回:
            list[dict]: 文档列表，每个元素包含 content, source, score
        """
        if top_k is None:
            top_k = config.TOP_K

        if min_score is None:
            min_score = config.SIMILARITY_THRESHOLD

        # 1. 向量检索
        results = self.embedding_manager.search(query, top_k)

        # 2. 过滤低分结果
        filtered = [r for r in results if r["score"] <= min_score]

        # 3. 如果过滤后为空，返回原始结果（上限3条）
        if not filtered and results:
            filtered = results[:3]

        # 4. 重排序（提高准确性）
        # 先检索更多结果，再精选最相关的
        if len(filtered) > 2:
            from reranker import Reranker
            reranker = Reranker()
            filtered = reranker.rerank(query, filtered, top_k=top_k or config.TOP_K)

        return filtered

    def hybrid_retrieve(self, query, top_k=None):
        """
        混合检索：向量检索 + 关键词匹配
        两种方法结合，结果更准确
        """
        if top_k is None:
            top_k = config.TOP_K

        # 1. 向量检索
        vector_results = self.retrieve(query, top_k)

        # 2. 关键词匹配
        keyword_results = self._keyword_match(query, vector_results)

        # 3. 合并去重
        seen = set()
        merged = []

        # 优先添加关键词匹配（更精确）
        for r in keyword_results:
            content_hash = hash(r["content"][:100])
            if content_hash not in seen:
                seen.add(content_hash)
                merged.append(r)

        # 再添加向量匹配
        for r in vector_results:
            content_hash = hash(r["content"][:100])
            if content_hash not in seen:
                seen.add(content_hash)
                merged.append(r)

        return merged[:top_k]

    def _keyword_match(self, query, candidates):
        """
        简单的关键词匹配
        在已有结果中按关键词匹配程度排序
        """
        # 提取查询中的关键词（2个字以上）
        keywords = re.findall(r'[\w]{2,}', query)

        if not keywords:
            return []

        scored = []
        for doc in candidates:
            text = doc["content"]
            # 统计关键词出现次数
            count = sum(1 for kw in keywords if kw in text)
            if count > 0:
                scored.append((count, doc))

        # 按匹配次数降序
        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored]

    def list_documents(self):
        """列出知识库中的所有文档"""
        return self.embedding_manager.list_documents()

    def clear(self):
        """清空知识库"""
        self.embedding_manager.delete_all()


# ==================== 独立测试 ====================
if __name__ == "__main__":
    print("\n🧪 测试 Retriever\n")

    retriever = Retriever()

    # 列出文档
    docs = retriever.list_documents()
    print(f"📚 知识库文档: {docs}")

    # 搜索
    if docs:
        results = retriever.retrieve("RAG技术", top_k=3)
        print(f"\n🔍 搜索结果: {len(results)} 条")
        for r in results:
            print(f"  - {r['source']}: {r['content'][:50]}...")

    print("\n✅ Retriever 测试完成！")