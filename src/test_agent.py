"""测试 Agent"""
from agent import agent

print("✅ Agent 模块导入成功！")

# 测试对话
result = agent.chat("你好，请介绍一下你自己")
print("\n=== AI 回复 ===")
print(result)