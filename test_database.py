# 第1步验证：测试 database 模块
print("🔍 第1步验证：测试 database 模块...")

# 直接导入，不经过 __init__.py
import sys
sys.path.insert(0, 'D:/python-projet/PythonProject3')

# 直接导入 database 模块
from app.database import DatabaseManager

# 测试数据库初始化
db = DatabaseManager("data/test_step1.db")
print("✅ 数据库初始化成功")

# 测试创建租户
tenant_id = db.create_tenant("测试公司")
print(f"✅ 创建租户成功: {tenant_id}")

# 测试创建用户
user_id = db.create_user(tenant_id, "testuser", "test@test.com", "password123", "admin")
print(f"✅ 创建用户成功: {user_id}")

# 测试登录
user = db.verify_user("testuser", "password123")
if user:
    print(f"✅ 登录成功: {user['username']} - 角色: {user['role']}")
else:
    print("❌ 登录失败")

print("\n✅ 第1步验证完成！")