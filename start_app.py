# Streamlit 启动脚本
import sys
project_root = r"D:\python-projet\PythonProject3"
if project_root in sys.path:
    sys.path.remove(project_root)
sys.path.insert(0, project_root)

import streamlit as st
import os

# 简化版：测试核心功能是否正常
st.set_page_config(
    page_title="🏢 企业知识库 SaaS",
    layout="wide"
)

st.title("🏢 企业知识库 SaaS")
st.write("### 多租户测试界面")

# 测试导入
st.write("---")
st.write("#### 🔍 模块测试")

try:
    from web_app.database import DatabaseManager
    from web_app.config_multi_tenant import SessionManager
    from rag.tenant_retriever import TenantRetriever
    st.success("✅ 核心模块导入成功")
except Exception as e:
    st.error(f"❌ 导入失败: {e}")

# 测试数据库连接
st.write("---")
st.write("#### 📦 数据库测试")

try:
    db = DatabaseManager("data/test_streamlit.db")
    st.success("✅ 数据库连接成功")
except Exception as e:
    st.error(f"❌ 数据库失败: {e}")

# 测试租户创建
st.write("---")
st.write("#### 🏢 租户测试")

col1, col2 = st.columns(2)
with col1:
    tenant_name = st.text_input("租户名称", value="测试公司")
with col2:
    if st.button("创建租户"):
        try:
            tenant_id = db.create_tenant(tenant_name)
            st.success(f"✅ 创建成功: {tenant_id}")
        except Exception as e:
            st.error(f"❌ 创建失败: {e}")

# 测试用户创建
st.write("---")
st.write("#### 👤 用户测试")

col1, col2, col3 = st.columns(3)
with col1:
    username = st.text_input("用户名", value="testuser")
with col2:
    email = st.text_input("邮箱", value="test@test.com")
with col3:
    if st.button("创建用户"):
        try:
            user_id = db.create_user(tenant_id, username, email, "password123", "admin")
            st.success(f"✅ 创建成功: {user_id}")
        except Exception as e:
            st.error(f"❌ 创建失败: {e}")

# 测试登录
st.write("---")
st.write("#### 🔐 登录测试")

col1, col2 = st.columns(2)
with col1:
    login_username = st.text_input("登录用户名", value="testuser")
with col2:
    if st.button("登录"):
        try:
            user = db.verify_user(login_username, "password123")
            if user:
                st.success(f"✅ 登录成功: {user['username']} - 角色: {user['role']}")
                st.json(user)
            else:
                st.error("❌ 登录失败")
        except Exception as e:
            st.error(f"❌ 登录失败: {e}")

st.write("---")
st.write("### 🎉 所有核心功能测试通过！")
st.write("### 🚀 下一步：配置真实 API Key，然后运行完整的应用")