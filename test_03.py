# 第3步验证：测试多租户检索器
import sys

project_root = r"D:\python-projet\PythonProject3"
if project_root in sys.path:
    sys.path.remove(project_root)
sys.path.insert(0, project_root)

print("🔍 第3步验证：测试多租户检索器...")

try:
    from web_app.database import DatabaseManager
    from rag.tenant_retriever import TenantRetriever

    print("✅ 导入成功")

    # 用不同的数据库文件，避免数据冲突
    db = DatabaseManager("data/test_03_new.db")  # 新数据库！
    print("✅ 数据库初始化成功")

    # 用一个新的租户名字
    tenant_id = db.create_tenant("检索测试公司2026")
    print(f"✅ 创建租户: {tenant_id}")

    retriever = TenantRetriever(tenant_id, db)
    print("✅ 多租户检索器创建成功")
    print(f"✅ Collection名称: {retriever.collection_name}")
    print(f"✅ 存储路径: {retriever.persist_directory}")

    results = retriever.search("测试问题", top_k=3)
    print(f"✅ 搜索完成: 找到 {len(results)} 个结果")

    print("\n🎉 第3步验证通过！")

except Exception as e:
    print(f"\n❌ 失败: {e}")
    import traceback

    traceback.print_exc()