from rag import kb

# 测试检索
results = kb.search("LangChain是什么")
print("检索结果:")
for r in results:
    print(f"- {r['source']}: {r['content'][:100]}...")