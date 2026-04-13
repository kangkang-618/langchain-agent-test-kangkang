# 第1步验证：完全独立的测试
import sys
import os

# ====== 关键：把项目根目录放在最前面 ======
# 这样 Python 会优先从项目目录加载，而不是虚拟环境
project_root = r"D:\python-projet\PythonProject3"
if project_root in sys.path:
    sys.path.remove(project_root)
sys.path.insert(0, project_root)

# ====== 验证路径 ======
print(f"项目路径: {sys.path[0]}")
print(f"第一个 app 模块位置: {__import__('app', fromlist=['']).__file__ if 'app' in sys.modules else '未加载'}")

# ====== 测试 ======
print("\n🔍 第1步验证：测试 database 模块...")

try:
    from web_app.database import DatabaseManager

    print("✅ 导入成功")

    db = DatabaseManager("data/test_01.db")
    print("✅ 数据库初始化成功")

    tenant_id = db.create_tenant("测试公司")
    print(f"✅ 创建租户成功: {tenant_id}")

    user_id = db.create_user(tenant_id, "testuser", "test@test.com", "pass123", "admin")
    print(f"✅ 创建用户成功: {user_id}")

    user = db.verify_user("testuser", "pass123")
    if user:
        print(f"✅ 登录成功: {user['username']} - 角色: {user['role']}")

    print("\n🎉 第1步验证通过！")

except Exception as e:
    print(f"\n❌ 失败: {e}")
    import traceback

    traceback.print_exc()