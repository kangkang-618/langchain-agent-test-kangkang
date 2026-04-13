"""测试 RAG"""
from rag import kb

print("✅ RAG 模块导入成功！")

# 列出文档
docs = kb.list_documents()
print(f"知识库文档: {docs}")