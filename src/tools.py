"""
工具定义 - 企业级知识库问答系统
"""

import os
import re
from langchain_core.tools import Tool

from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    KNOWLEDGE_BASE_PATH,
    CHROMA_PATH,
    TOP_K,
)

# ========== 计算器工具 ==========
def calculator(expression, *args):
    """安全计算数学表达式"""
    try:
        if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', expression):
            result = eval(expression)
            return f"计算结果: {expression} = {result}"
        else:
            return "计算错误: 只允许数字和运算符"
    except Exception as e:
        return f"计算错误: {str(e)}"


# ========== 文件操作工具 ==========
def read_file(filename, *args):
    """读取知识库中的文件"""
    file_path = os.path.join(KNOWLEDGE_BASE_PATH, filename)
    if not os.path.exists(file_path):
        return f"文件不存在: {filename}"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if len(content) > 5000:
            content = content[:5000] + "\n\n... (文件过长，已截断)"
        return f"=== {filename} ===\n{content}"
    except Exception as e:
        return f"读取文件失败: {str(e)}"


def list_files(*args):
    """列出知识库中的所有文件"""
    try:
        if not os.path.exists(KNOWLEDGE_BASE_PATH):
            return "知识库文件夹不存在"
        files = [f for f in os.listdir(KNOWLEDGE_BASE_PATH)
                 if f.endswith(('.txt', '.md'))]
        if not files:
            return "知识库为空"
        return "知识库文件:\n" + "\n".join(f"- {f}" for f in files)
    except Exception as e:
        return f"获取文件列表失败: {str(e)}"


# ========== RAG 检索工具 ==========
def rag_retrieve(query, *args):
    """从向量知识库检索相关内容"""
    try:
        import chromadb
        if not os.path.exists(CHROMA_PATH):
            return "知识库为空，请先上传文档！"
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        try:
            collection = client.get_collection("knowledge_base")
        except:
            return "知识库为空，请先上传文档！"
        
        query_embedding = _embed_text(query)
        results = collection.query(query_embeddings=[query_embedding], n_results=TOP_K)
        
        if not results or not results['documents']:
            return "未找到相关内容"
        
        output = []
        for i, doc in enumerate(results['documents'][0]):
            source = results['metadatas'][0][i].get('source', 'unknown')
            output.append(f"【{i+1}】{source}: {doc[:300]}...")
        return "\n\n".join(output)
    except Exception as e:
        return f"RAG检索失败: {str(e)}"


def _embed_text(text):
    """使用硅基流动获取文本向量"""
    import requests
    from config import EMBEDDING_API_KEY
    response = requests.post(
        "https://api.siliconflow.cn/v1/embeddings",
        headers={"Authorization": f"Bearer {EMBEDDING_API_KEY}", "Content-Type": "application/json"},
        json={"model": "BAAI/bge-m3", "input": text}
    )
    if response.status_code == 200:
        return response.json()["data"][0]["embedding"]
    else:
        raise Exception(f"Embedding API 错误")


# ========== 工具注册表 ==========
TOOLS = [
    Tool(name="calculator", func=calculator, description="计算数学表达式"),
    Tool(name="read_file", func=read_file, description="读取知识库文件"),
    Tool(name="list_files", func=list_files, description="列出知识库文件"),
    Tool(name="rag_retrieve", func=rag_retrieve, description="从知识库检索"),
]

TOOL_DICT = {tool.name: tool for tool in TOOLS}
