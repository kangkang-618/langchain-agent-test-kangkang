"""
Streamlit Web 应用 - 企业级智能知识库问答系统
运行方式：streamlit run web_app/main.py
"""

import streamlit as st
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_loader import DocumentLoader
from embeddings import EmbeddingManager
from retriever import Retriever
from qa_chain import QAChain
import config
import database

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="🏢 智能知识库问答",
    page_icon="🤖",
    layout="wide"
)


# ==================== 初始化 ====================
@st.cache_resource
def init_components():
    doc_loader = DocumentLoader()
    embedding_manager = EmbeddingManager()
    retriever = Retriever(embedding_manager)
    qa_chain = QAChain(retriever)
    return doc_loader, qa_chain, retriever


def init_session_state():
    """初始化会话状态"""
    if "session_id" not in st.session_state:
        # 生成新的会话 ID
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.chat_history = []

        # 从数据库加载历史
        sessions = database.list_sessions()
        if sessions:
            st.session_state.all_sessions = sessions
        else:
            st.session_state.all_sessions = []


# ==================== 侧边栏 ====================
def render_sidebar(doc_loader, qa_chain, retriever):
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("## 📚 知识库管理")

        # -------- 文件上传 --------
        st.markdown("### 📤 上传文档")
        uploaded_file = st.file_uploader(
            "支持 PDF、Word、TXT、MD",
            type=["pdf", "docx", "doc", "txt", "md"]
        )

        if uploaded_file is not None:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 上传", use_container_width=True):
                    with st.spinner("处理中..."):
                        try:
                            save_dir = config.KNOWLEDGE_BASE_PATH
                            os.makedirs(save_dir, exist_ok=True)
                            save_path = os.path.join(save_dir, uploaded_file.name)

                            with open(save_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())

                            docs = doc_loader.load(save_path)

                            from langchain_text_splitters import RecursiveCharacterTextSplitter
                            text_splitter = RecursiveCharacterTextSplitter(
                                chunk_size=config.CHUNK_SIZE,
                                chunk_overlap=config.CHUNK_OVERLAP,
                                length_function=len,
                            )
                            chunks = text_splitter.split_documents(docs)

                            embedding_manager = EmbeddingManager()
                            embedding_manager.add_documents(chunks, uploaded_file.name)

                            st.success(f"✅ {uploaded_file.name} 上传成功！")
                            st.rerun()

                        except Exception as e:
                            st.error(f"❌ 上传失败: {e}")

        # -------- 文档列表 --------
        st.markdown("### 📋 知识库文档")
        docs = retriever.list_documents()
        if docs:
            for doc in docs:
                st.markdown(f"- 📄 {doc}")
        else:
            st.info("知识库为空")

        # -------- 清空知识库 --------
        st.markdown("---")
        if st.button("🗑️ 清空知识库", use_container_width=True):
            try:
                retriever.clear()
                st.success("✅ 知识库已清空")
                st.rerun()
            except Exception as e:
                st.error(f"❌ 清空失败: {e}")

        # -------- 历史会话 --------
        st.markdown("---")
        st.markdown("## 💬 对话历史")

        sessions = database.list_sessions()
        if sessions:
            for s in sessions[:10]:  # 只显示最近10个
                title = s.get("title") or "新对话"
                updated = s.get("updated_at", "")[:16] if s.get("updated_at") else ""
                if st.button(f"📝 {title}\n   {updated}", key=f"session_{s['session_id']}"):
                    # 切换到历史会话
                    st.session_state.session_id = s["session_id"]
                    st.session_state.messages = []
                    st.session_state.chat_history = []

                    # 从数据库加载消息
                    db_messages = database.get_session_history(s["session_id"])
                    import json
                    for role, content, sources in db_messages:
                        # sources 是 JSON 字符串，需要解析
                        if sources:
                            sources_list = json.loads(sources)
                        else:
                            sources_list = None

                        st.session_state.messages.append({
                            "role": role,
                            "content": content,
                            "sources": sources_list
                        })
                        st.session_state.chat_history.append((role, content))

                    st.rerun()
        else:
            st.info("暂无历史对话")

        # -------- 新建对话 --------
        st.markdown("---")
        if st.button("➕ 新建对话", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()


# ==================== 主界面 ====================
def render_chat(qa_chain):
    """渲染聊天界面"""
    st.markdown("# 🤖 智能知识库问答系统")

    # 显示欢迎信息
    if not st.session_state.messages:
        st.markdown("""
        欢迎使用智能知识库问答系统！

        **使用方式：**
        1. 在左侧上传文档
        2. 输入问题开始提问
        3. 点击"参考来源"查看答案依据
        """)
        st.markdown("---")

    # 显示历史消息
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                st.markdown(message["content"])

                sources = message.get("sources")
                if sources and len(sources) > 0:
                    with st.expander(f"📖 参考来源 ({len(sources)}条)", expanded=False):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**来源 {i}: {source['source']}**")
                            st.markdown(f"_{source['content'][:200]}..._")
                else:
                    with st.expander("📖 参考来源", expanded=False):
                        st.info("无参考来源（基于 AI 自身知识回答）")
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(f"**来源 {i}: {source['source']}**")
                            st.markdown(f"_{source['content'][:200]}..._")

    # 聊天输入框
    if prompt := st.chat_input("输入问题，按 Enter 发送..."):
        # -------- 用户消息 --------
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        # -------- 保存到数据库 --------
        database.save_message(
            st.session_state.session_id,
            "user",
            prompt,
            None
        )

        # -------- AI 回复 --------
        with st.chat_message("assistant"):
            with st.spinner("🤔 思考中..."):
                try:
                    answer, sources = qa_chain.answer(
                        prompt,
                        st.session_state.chat_history
                    )

                    st.markdown(answer)

                    # 保存到历史
                    st.session_state.chat_history.append(("user", prompt))
                    st.session_state.chat_history.append(("assistant", answer))

                    # 序列化来源（JSON 字符串）
                    import json
                    sources_json = json.dumps(sources, ensure_ascii=False)

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })

                    # 保存到数据库
                    database.save_message(
                        st.session_state.session_id,
                        "assistant",
                        answer,
                        sources_json
                    )

                    # 如果是第一条消息，更新标题
                    if len(st.session_state.messages) == 2:
                        title = prompt[:20] + "..." if len(prompt) > 20 else prompt
                        database.update_session_title(st.session_state.session_id, title)

                    if sources and len(sources) > 0:
                        with st.expander(f"📖 参考来源 ({len(sources)}条)", expanded=False):
                            for i, source in enumerate(sources, 1):
                                st.markdown(f"**来源 {i}: {source['source']}**")
                                st.markdown(f"_{source['content'][:200]}..._")
                    else:
                        with st.expander("📖 参考来源", expanded=False):
                            st.info("无参考来源（基于 AI 自身知识回答）")

                except Exception as e:
                    error_msg = f"❌ 发生错误: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "sources": []
                    })


# ==================== 主函数 ====================
def main():
    init_session_state()
    doc_loader, qa_chain, retriever = init_components()

    col_sidebar, col_main = st.columns([1, 3])

    with col_sidebar:
        render_sidebar(doc_loader, qa_chain, retriever)

    with col_main:
        render_chat(qa_chain)


if __name__ == "__main__":
    main()