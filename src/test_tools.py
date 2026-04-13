"""
测试工具
"""
from tools import TOOLS, TOOL_DICT, search_web, calculator

print("✅ 工具导入成功！")
print(f"可用工具数量: {len(TOOLS)}")
print(f"工具列表: {[t.name for t in TOOLS]}")

# 测试计算器
result = calculator("100 + 200")
print(f"\n计算器测试: {result}")

# 测试搜索
result = search_web("今天北京天气")
print(f"\n搜索测试: {result[:200]}...")