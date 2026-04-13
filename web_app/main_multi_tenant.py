import sys
from pathlib import Path
import streamlit as st
import sqlite3
import os
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 导入配置
from web_app.config_multi_tenant import (
    db_manager, SessionManager, APP_TITLE, WELCOME_MESSAGE,
    TOP_K, CHROMA_BASE_PATH, KNOWLEDGE_BASE_PATH
)

# 初始化会话管理器
session = SessionManager.get_instance()

# 初始化会话状态
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.tenant_id = None
    st.session_state.user_id = None
    st.session_state.role = None
    st.session_state.username = None


# ==================== 登录页面 ====================
def login_page():
    st.title("🏢 企业知识库 SaaS")
    st.write("### 登录 / 注册")

    col1, col2 = st.columns(2)

    with col1:
        tab1, tab2 = st.tabs(["登录", "注册"])

        with tab1:
            username = st.text_input("用户名", key="login_username")
            password = st.text_input("密码", type="password", key="login_password")

            if st.button("登录", key="login_btn"):
                user = db_manager.verify_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.tenant_id = user['tenant_id']
                    st.session_state.user_id = user['user_id']
                    st.session_state.role = user['role']
                    st.session_state.username = user['username']

                    session.login(
                        user['tenant_id'],
                        user['user_id'],
                        user['role'],
                        username=user['username']
                    )
                    st.success(f"欢迎回来, {user['username']}!")
                    st.rerun()
                else:
                    st.error("用户名或密码错误")

        with tab2:
            st.write("创建新账户")
            tenant_name = st.text_input("企业/团队名称（可选，用于创建新租户）", key="register_tenant")
            username = st.text_input("用户名", key="reg_username")
            email = st.text_input("邮箱", key="reg_email")
            password = st.text_input("密码", type="password", key="reg_password")
            role = st.selectbox("角色", ["admin", "user", "viewer"], key="reg_role")

            if st.button("注册", key="register_btn"):
                if not username or not password:
                    st.error("用户名和密码必填")
                    return

                # 如果有租户名，先创建租户
                if tenant_name:
                    tenant_id = db_manager.create_tenant(tenant_name)
                else:
                    # 默认租户
                    tenant_id = "default_tenant"
                    # 确保默认租户存在
                    conn = sqlite3.connect(db_manager.db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT tenant_id FROM tenants WHERE tenant_id = ?", (tenant_id,))
                    if not cursor.fetchone():
                        cursor.execute("INSERT INTO tenants (tenant_id, tenant_name) VALUES (?, ?)",
                                       (tenant_id, "默认租户"))
                        conn.commit()
                    conn.close()

                # 创建用户
                user_id = db_manager.create_user(tenant_id, username, email, password, role)
                st.success(f"注册成功！你的用户名: {username}，现在可以登录了")

    with col2:
        st.write("### 📊 系统介绍")
        st.markdown("""
        **企业知识库 SaaS** 是一个支持多租户的智能问答系统：

        - 🏢 **多租户隔离** - 每个企业数据完全隔离，安全可靠
        - 🔐 **权限管理** - 支持管理员、普通用户、只读用户三种角色
        - 📊 **数据统计** - 实时展示文档数、问答数、用户数
        - 📖 **来源标注** - 答案可追溯到具体文档
        - 💬 **多轮对话** - 支持上下文记忆

        **适用场景：**
        - 企业内部知识库问答
        - 团队技术文档检索
        - 产品手册和 FAQ
        - 培训资料和考试题库
        """)


# ==================== 主应用页面 ====================
def main_app():
    st.title(f"🏢 企业知识库")

    # 显示当前用户信息
    with st.sidebar:
        st.write(f"### 👤 {st.session_state.username}")
        st.write(f"**角色**: {st.session_state.role}")

        st.divider()

        # 根据角色显示不同的操作
        if st.session_state.role in ['admin', 'user']:
            st.write("### 📤 上传文档")
            uploaded_files = st.file_uploader(
                "上传文档",
                type=["pdf", "docx", "txt", "md"],
                accept_multiple_files=True,
                key="doc_uploader"
            )

            if uploaded_files:
                import hashlib
                try:
                    for file in uploaded_files:
                        # 生成文档ID
                        doc_id = f"doc_{hashlib.md5(file.name.encode()).hexdigest()[:8]}"
                        file_path = f"{KNOWLEDGE_BASE_PATH}/{st.session_state.tenant_id}/{file.name}"

                        # 保存文件
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        with open(file_path, "wb") as f:
                            f.write(file.getbuffer())

                        # 记录到数据库
                        conn = sqlite3.connect(db_manager.db_path)
                        cursor = conn.cursor()
                        cursor.execute('''
                                       INSERT INTO documents (doc_id, tenant_id, filename, file_path, created_by)
                                       VALUES (?, ?, ?, ?, ?)
                                       ''', (doc_id, st.session_state.tenant_id, file.name, file_path,
                                             st.session_state.user_id))
                        conn.commit()
                        conn.close()

                        st.success(f"✅ {file.name} 上传成功")
                except Exception as e:
                    st.error(f"❌ 上传失败: {e}")
                    import traceback
                    st.error(f"详细错误: {traceback.format_exc()}")

                    # 记录到数据库
                    conn = sqlite3.connect(db_manager.db_path)
                    cursor = conn.cursor()
                    cursor.execute('''
                                   INSERT INTO documents (doc_id, tenant_id, filename, file_path, created_by)
                                   VALUES (?, ?, ?, ?, ?)
                                   ''',
                                   (doc_id, st.session_state.tenant_id, file.name, file_path, st.session_state.user_id))
                    conn.commit()
                    conn.close()

                    st.success(f"✅ {file.name} 上传成功")

        # 文档列表
        st.write("### 📋 文档列表")
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT doc_id, filename, upload_time, hit_count
                       FROM documents
                       WHERE tenant_id = ?
                       ORDER BY upload_time DESC LIMIT 20
                       ''', (st.session_state.tenant_id,))

        docs = cursor.fetchall()
        conn.close()

        if docs:
            for doc in docs:
                st.text(f"📄 {doc[1]} (👁 {doc[3]})")
        else:
            st.info("暂无文档，请上传")

        st.divider()

        # 统计数据（仅管理员可见）
        if st.session_state.role == 'admin':
            st.write("### 📊 数据统计")
            stats = db_manager.get_tenant_stats(st.session_state.tenant_id)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📄 文档数", stats['doc_count'])
            with col2:
                st.metric("👥 用户数", stats['user_count'])
            with col3:
                st.metric("💬 问答数", stats['ask_count'])

            st.divider()

            # 热门文档
            st.write("### 🔥 热门文档 TOP 10")
            top_docs = db_manager.get_top_docs(st.session_state.tenant_id, 10)

            for doc in top_docs:
                st.write(f"📄 {doc['filename']} - 👁 {doc['hit_count']} 次")

            st.divider()

        # 退出登录
        if st.button("退出登录"):
            session.logout()
            st.session_state.logged_in = False
            st.rerun()

    # 问答区域
    st.divider()

    st.write("### 💬 提问")
    question = st.text_input("输入您的问题...", key="question_input", placeholder="例如：公司的年假政策是什么？")

    if st.button("发送", key="ask_btn") and question:
        from rag.tenant_qa_chain import TenantQAChain

        # 创建问答链
        qa_chain = TenantQAChain(
            tenant_id=st.session_state.tenant_id,
            user_id=st.session_state.user_id,
            db_manager=db_manager
        )

        with st.spinner("正在思考..."):
            result = qa_chain.ask(question)

        st.success("回答完成！")

        st.write("📖 **答案：**")
        st.markdown(result['answer'])

        if result.get('source_documents'):
            st.write("📚 **参考来源：**")
            for i, doc in enumerate(result['source_documents'][:3]):
                st.write(f"{i + 1}. {doc.metadata.get('filename', '未知文档')}")


# ==================== 主程序 ====================
def main():
    if not st.session_state.get("logged_in", False):
        login_page()
    else:
        main_app()


if __name__ == "__main__":
    main()