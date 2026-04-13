"""
测试配置导入
"""
from config import *

print("✅ 配置导入成功！")
print(f"项目路径: {PROJECT_ROOT}")
print(f"知识库路径: {KNOWLEDGE_BASE_PATH}")
print(f"向量库路径: {CHROMA_PATH}")
print(f"使用模型: {DEEPSEEK_MODEL}")