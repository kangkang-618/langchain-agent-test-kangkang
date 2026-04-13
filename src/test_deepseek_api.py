"""
测试 DeepSeek API 连通性
"""
import requests

# 你的 DeepSeek API Key
API_KEY = "sk-49a64f6aac9f4b508cfb147009565274"  # 替换成你的！
BASE_URL = "https://api.deepseek.com"

# 测试 Chat API（确保 Key 有效）
print("=" * 50)
print("测试1: Chat API")
print("=" * 50)

response = requests.post(
    f"{BASE_URL}/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": "你好"}],
        "stream": False
    }
)

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    print("✅ Chat API 正常！")
else:
    print(f"❌ 错误: {response.text}")

# 测试 Embeddings API
print("\n" + "=" * 50)
print("测试2: Embeddings API")
print("=" * 50)

response = requests.post(
    f"{BASE_URL}/embeddings",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek-embed",
        "input": "你好"
    }
)

print(f"状态码: {response.status_code}")
print(f"响应: {response.text[:500]}")