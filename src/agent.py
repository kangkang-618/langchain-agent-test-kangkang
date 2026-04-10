"""
Agent 控制器 - ReAct 推理引擎
"""

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent, AgentState

from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL
from tools import TOOLS


class Agent:
    """Agent 控制器"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=DEEPSEEK_MODEL,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
            temperature=0.7,
        )
        self.agent = create_agent(self.llm, TOOLS, state_schema=AgentState)
    
    def chat(self, user_input, history=None):
        if history is None:
            history = []
        messages = history + [("user", user_input)]
        result = self.agent.invoke({"messages": messages})
        return result
    
    def chat_with_rag(self, user_input, kb, history=None):
        if history is None:
            history = []
        
        relevant_docs = kb.search(user_input)
        
        if relevant_docs:
            context = "\n\n".join([f"【{doc['source']}】: {doc['content']}" for doc in relevant_docs])
            systemPrompt = f"""你是一个智能助手，可以回答用户问题。
当用户问题时，优先使用以下知识库内容回答：

=== 知识库内容 ===
{context}
=== 知识库结束 ===

如果知识库内容不足以回答问题，可以结合你的知识回答。回答时请注明来源。"""
        else:
            systemPrompt = "你是一个智能助手，可以回答用户问题。"
        
        messages = [("system", systemPrompt)] + history + [("user", user_input)]
        result = self.agent.invoke({"messages": messages})
        return result, relevant_docs


agent = Agent()
