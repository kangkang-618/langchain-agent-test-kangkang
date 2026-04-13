# 第2步验证：测试配置模块
import sys

project_root = r"D:\python-projet\PythonProject3"
if project_root in sys.path:
    sys.path.remove(project_root)
sys.path.insert(0, project_root)

print("🔍 第2步验证：测试配置模块...")

try:
    from web_app.config_multi_tenant import (
        SessionManager,
        db_manager,
        APP_TITLE,
        DB_PATH,
        CHROMA_BASE_PATH
    )

    print("✅ 导入成功")

    # 测试会话管理器
    session = SessionManager.get_instance()
    print(f"✅ 会话管理器创建成功")

    # 测试登录状态
    session.login("tenant_001", "user_001", "admin", "测试公司", "admin")
    print(f"✅ 登录成功: {session.current_username}")
    print(f"✅ 角色: {session.current_user_role}")
    print(f"✅ 权限: can_upload={session.can_upload_doc()}, can_admin={session.can_view_admin()}")

    # 测试配置
    print(f"✅ APP标题: {APP_TITLE}")
    print(f"✅ 数据库路径: {DB_PATH}")

    # 登出
    session.logout()
    print(f"✅ 登出成功")

    print("\n🎉 第2步验证通过！")

except Exception as e:
    print(f"\n❌ 失败: {e}")
    import traceback

    traceback.print_exc()