
"""
工具定义 - 企业级知识库问答系统
"""

import os
import json
import re
from duckduckgo_search import DDGS
from langchain_core.tools import Tool

# ========== 配置 ==========
from config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_BASE_URL,
    KNOWLEDGE_BASE_PATH,
    CHROMA_PATH,
    TOP_K,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    MAX_SEARCH_RESULTS,
    PROJECT_ROOT,
    EMBEDDING_MODEL,
)

# ========== 搜索工具 ==========
def search_web(query):
    """搜索互联网获取最新信息"""
    try:
        results = []
        with DDGS() as ddgs:
            for i, r in enumerate(ddgs.text(query, max_results=MAX_SEARCH_RESULTS)):
                if i >= MAX_SEARCH_RESULTS:
                    break
                results.append(f"标题: {r['title']}\n链接: {r['href']}\n摘要: {r['body']}")

        if results:
            return "\n\n".join(results)
        else:
            return "未找到相关搜索结果"
    except Exception as e:
        return f"搜索失败: {str(e)}"


# ========== 计算器工具 ==========
def calculator(expression):
    """安全计算数学表达式"""
    try:
        if re.match(r'^[\d\s\+\-\*\/\(\)\.]+$', expression):
            result = eval(expression)
            return f"计算结果: {expression} = {result}"
        else:
            return "计算错误: 只允许数字和 + - * / ( ) 运算符"
    except Exception as e:
        return f"计算错误: {str(e)}"


# ========== 文件操作工具 ==========
def read_file(filename, *args):
    """读取知识库中的文件"""
    file_path = os.path.join(KNOWLEDGE_BASE_PATH, filename)

    if not os.path.exists(file_path):
        return f"文件不存在: {filename}"

    if not (filename.endswith('.txt') or filename.endswith('.md')):
        return "不支持的文件类型，只支持 .txt 和 .md 文件"

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
            return "知识库为空，没有文档文件"

        return "知识库中的文件:\n" + "\n".join(f"- {f}" for f in files)
    except Exception as e:
        return f"获取文件列表失败: {str(e)}"


# ========== RAG 检索工具 ==========
def rag_retrieve(query, *args):
    """从向量知识库检索相关内容"""
    try:
        import chromadb
        from langchain_openai import OpenAIEmbeddings

        if not os.path.exists(CHROMA_PATH):
            return "知识库为空，请先上传文档！"

        client = chromadb.PersistentClient(path=CHROMA_PATH)

        try:
            collection = client.get_collection("knowledge_base")
        except:
            return "知识库为空，请先上传文档！"

        embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=DEEPSEEK_API_KEY,
            openai_api_base=DEEPSEEK_BASE_URL
        )

        query_embedding = embeddings.embed_query(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=TOP_K
        )

        if not results or not results['documents']:
            return "在知识库中未找到相关内容"

        output = []
        for i, (doc, metadatas) in enumerate(zip(results['documents'], results['metadatas'])):
            source = metadatas[0].get('source', 'unknown') if metadatas else 'unknown'
            output.append(f"【来源 {i+1}】文件: {source}\n内容: {doc[:500]}...")

        return "\n\n".join(output)

    except ImportError:
        return "RAG功能未安装，请运行: pip install chromadb langchain-openai"
    except Exception as e:
        return f"RAG检索失败: {str(e)}"


# ========== 工具注册表 ==========
TOOLS = [
    # 搜索工具暂时禁用（国内访问不稳定）
    # Tool(
    #     name="search_web",
    #     func=search_web,
    #     description="搜索互联网获取最新信息..."
    # ),
    Tool(
        name="calculator",
        func=calculator,
        description="安全计算数学表达式。用于：计算统计数字、百分比等。输入：数学表达式"
    ),
    Tool(
        name="read_file",
        func=read_file,
        description="读取知识库中的文档内容。输入：文件名"
    ),
    Tool(
        name="list_files",
        func=list_files,
        description="列出知识库中所有已上传的文档。输入：无"
    ),
    Tool(
        name="rag_retrieve",
        func=rag_retrieve,
        description="从向量知识库检索相关内容。输入：搜索 query"
    ),
]

TOOL_DICT = {tool.name: tool for tool in TOOLS}