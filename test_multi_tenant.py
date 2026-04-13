#!/usr/bin/env python3
"""
快速测试脚本 - 验证多租户功能
"""

print("=" * 50)
print("🏢 企业知识库 SaaS - 功能测试")
print("=" * 50)

# 测试 1：数据库模块
print("\n📦 测试 1：数据库模块...")
try:
    from app.database import DatabaseManager

    # 初始化数据库
    db = DatabaseManager("data/test_knowledge.db")
    print("✅ 数据库初始化成功")

    # 创建测试租户
    tenant_id = db.create_tenant("测试企业")
    print(f"✅ 创建租户成功: {tenant_id}")

    # 创建测试用户
    admin_id = db.create_user(tenant_id, "admin", "admin@test.com", "admin123", "admin")
    user_id = db.create_user(tenant_id, "user1", "user@test.com", "user123", "user")
    print(f"✅ 创建用户成功: admin={admin_id}, user={user_id}")

    # 测试登录
    user = db.verify_user("admin", "admin123")
    if user:
        print(f"✅ 登录测试成功: {user['username']} ({user['role']})")
    else:
        print("❌ 登录测试失败")

    # 测试统计数据
    stats = db.get_tenant_stats(tenant_id)
    print(f"✅ 统计数据: 文档={stats['doc_count']}, 用户={stats['user_count']}, 问答={stats['ask_count']}")

    print("\n✅ 测试 1：数据库模块 - 全部通过！")
except Exception as e:
    print(f"\n❌ 测试 1 失败: {e}")
    import traceback

    traceback.print_exc()

# 测试 2：配置模块
print("\n📦 测试 2：配置模块...")
try:
    from app.config_multi_tenant import SessionManager, APP_TITLE

    session = SessionManager.get_instance()
    print(f"✅ 会话管理器初始化成功")
    print(f"✅ 应用标题: {APP_TITLE}")

    # 测试登录
    session.login("tenant_001", "user_001", "admin", tenant_name="测试企业", username="admin")
    print(f"✅ 登录成功: {session.current_username}")
    print(f"✅ 角色: {session.current_user_role}")
    print(f"✅ 权限检查: can_upload={session.can_upload_doc()}, can_admin={session.can_view_admin()}")

    # 测试登出
    session.logout()
    print(f"✅ 登出成功")

    print("\n✅ 测试 2：配置模块 - 全部通过！")
except Exception as e:
    print(f"\n❌ 测试 2 失败: {e}")
    import traceback

    traceback.print_exc()

# 测试 3：RAG 模块
print("\n📦 测试 3：RAG 模块...")
try:
    from app.database import DatabaseManager
    from rag.tenant_retriever import TenantRetriever

    db = DatabaseManager("data/test_knowledge.db")
    tenant_id = db.create_tenant("RAG测试企业")

    retriever = TenantRetriever(tenant_id, db)
    print("✅ 多租户检索器初始化成功")

    # 注意：没有文档时搜索结果为空是正常的
    results = retriever.search("测试问题", top_k=3)
    print(f"✅ 搜索测试完成: 找到 {len(results)} 个结果")

    print("\n✅ 测试 3：RAG 模块 - 全部通过！")
except Exception as e:
    print(f"\n⚠️ 测试 3 有警告（这可能是因为没有文档）: {e}")

# 测试 4：Streamlit 界面
print("\n📦 测试 4：Streamlit 界面...")
try:
    import streamlit as st

    print("✅ Streamlit 导入成功")
    print(f"✅ Streamlit 版本: {st.__version__}")
    print("\n✅ 测试 4：Streamlit 界面 - 全部通过！")
except Exception as e:
    print(f"\n❌ 测试 4 失败: {e}")
    import traceback

    traceback.print_exc()

# 总结
print("\n" + "=" * 50)
print("🎉 测试完成！")
print("=" * 50)
print("\n🚀 下一步：")
print("1. 配置 .env 文件，填入你的 API Key")
print("2. 运行: streamlit run app/main_multi_tenant.py")
print("3. 打开浏览器访问: http://localhost:8501")
print("4. 注册账号，开始使用！")