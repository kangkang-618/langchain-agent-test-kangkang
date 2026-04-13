"""
QA 问答链 - 根据检索结果生成回答
"""

import requests
import config


class QAChain:
    """
    问答链

    作用：把用户问题和检索到的文档结合起来，
         让 AI 生成准确、有依据的回答
    """

    def __init__(self, retriever):
        """
        初始化问答链

        参数:
            retriever: Retriever 实例
        """
        self.retriever = retriever
        self.llm_url = f"{config.DEEPSEEK_BASE_URL}/chat/completions"
        self.llm_config = {
            "api_key": config.DEEPSEEK_API_KEY,
            "model": config.DEEPSEEK_MODEL,
        }
        print("✅ QAChain 初始化完成")

    def _call_llm(self, messages, temperature=0.7):
        """
        调用 DeepSeek API

        参数:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            temperature: 温度参数（越低越确定性，越高越有创意）

        返回:
            AI 的回答文本
        """
        # 1. 检查 API Key
        if not self.llm_config["api_key"] or self.llm_config["api_key"] == "sk-your-deepseek-api-key":
            raise ValueError("❌ 请先配置 DEEPSEEK_API_KEY！")

        # 2. 调用 API
        response = requests.post(
            self.llm_url,
            headers={
                "Authorization": f"Bearer {self.llm_config['api_key']}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.llm_config["model"],
                "messages": messages,
                "temperature": temperature,
            },
            timeout=60
        )

        # 3. 检查结果
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]

        elif response.status_code == 401:
            raise ValueError("❌ DeepSeek API Key 无效！")

        else:
            raise Exception(f"❌ LLM 调用失败: {response.status_code} - {response.text}")

    def answer(self, question, history=None):
        """
        回答问题

        参数:
            question: 用户的问题
            history: 对话历史（可选，格式：[("user", "问题"), ("assistant", "回答")]）

        返回:
            (answer, sources): 回答文本 和 参考来源列表
        """
        # 1. 检索相关文档
        docs = self.retriever.retrieve(question, top_k=5)

        # 2. 构建系统提示词（告诉 AI 要怎么回答）
        if docs:
            # 有文档时的提示词
            context = "\n\n".join([
                f"【{doc['source']}】{doc['content']}"
                for doc in docs
            ])

            system_prompt = f"""你是一个专业的智能问答助手，擅长根据提供的参考资料回答问题。

参考材料：
{context}

回答要求：
1. 优先基于参考材料回答，如果材料中有相关信息，引用来源
2. 如果材料不足以完整回答，可以结合你的知识补充
3. 如果材料中确实没有相关信息，明确说明"根据现有资料无法回答"
4. 回答要准确、清晰、有条理
5. 回答使用中文"""
        else:
            # 没有文档时的提示词
            system_prompt = """你是一个专业的智能问答助手。请根据你的知识准确回答问题。回答使用中文。"""

        # 3. 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]

        # 4. 添加对话历史（最多保留最近 6 轮）
        if history:
            for role, content in history[-6:]:
                messages.append({
                    "role": "user" if role == "user" else "assistant",
                    "content": content
                })

        # 5. 添加当前问题
        messages.append({"role": "user", "content": question})

        # 6. 调用 LLM 生成回答
        answer = self._call_llm(messages)

        # 7. 整理来源信息
        sources = [
            {"source": doc["source"], "content": doc["content"]}
            for doc in docs
        ]

        return answer, sources


# ==================== 独立测试 ====================
if __name__ == "__main__":
    print("\n🧪 测试 QAChain\n")

    from retriever import Retriever

    retriever = Retriever()
    qa = QAChain(retriever)

    # 测试问答
    question = "RAG是什么？有什么用？"
    print(f"\n❓ 问题: {question}")
    print("🤔 AI 思考中...")

    try:
        answer, sources = qa.answer(question)
        print(f"\n✅ 回答:\n{answer}")
        print(f"\n📖 参考来源: {len(sources)} 条")
        for i, s in enumerate(sources, 1):
            print(f"  [{i}] {s['source']}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    print("\n✅ QAChain 测试完成！")