"""
REST API - 提供问答接口
支持：提问、上传文档、获取历史
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_loader import DocumentLoader
from embeddings import EmbeddingManager
from retriever import Retriever
from qa_chain import QAChain
from reranker import Reranker
import database

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化组件
doc_loader = DocumentLoader()
embedding_manager = EmbeddingManager()
retriever = Retriever(embedding_manager)
qa_chain = QAChain(retriever)


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    问答接口

    请求：
    {
        "question": "RAG是什么？",
        "session_id": "可选"
    }

    返回：
    {
        "answer": "回答内容",
        "sources": [{"source": "文件名", "content": "..."}]
    }
    """
    data = request.json
    question = data.get("question", "")
    session_id = data.get("session_id", "api_session")

    if not question:
        return jsonify({"error": "问题不能为空"}), 400

    try:
        # 生成回答
        answer, sources = qa_chain.answer(question)

        # 保存到历史
        database.save_message(session_id, "user", question)
        database.save_message(session_id, "assistant", answer)

        return jsonify({
            "answer": answer,
            "sources": sources,
            "session_id": session_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def upload():
    """
    上传文档接口

    请求：
    - file: 文件
    - filename: 文件名
    """
    if "file" not in request.files:
        return jsonify({"error": "没有文件"}), 400

    file = request.files["file"]
    filename = request.form.get("filename", file.filename)

    if not filename:
        filename = file.filename

    try:
        # 保存文件
        from config import KNOWLEDGE_BASE_PATH
        os.makedirs(KNOWLEDGE_BASE_PATH, exist_ok=True)
        save_path = os.path.join(KNOWLEDGE_BASE_PATH, filename)
        file.save(save_path)

        # 处理文档
        docs = doc_loader.load(save_path)

        from langchain_text_splitters import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50
        )
        chunks = text_splitter.split_documents(docs)

        embedding_manager.add_documents(chunks, filename)

        return jsonify({
            "message": "上传成功",
            "filename": filename,
            "chunks": len(chunks)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/history/<session_id>", methods=["GET"])
def get_history(session_id):
    """获取历史记录"""
    try:
        messages = database.get_session_history(session_id, limit=50)

        history = []
        for role, content, sources in messages:
            history.append({
                "role": role,
                "content": content,
                "sources": sources
            })

        return jsonify({"history": history})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    """获取会话列表"""
    try:
        sessions = database.list_sessions()
        return jsonify({"sessions": sessions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({"status": "ok", "message": "API 服务正常运行"})


if __name__ == "__main__":
    print("\n🚀 启动 API 服务...")
    print("   问答接口: http://localhost:5000/api/chat")
    print("   上传接口: http://localhost:5000/api/upload")
    print("   健康检查: http://localhost:5000/api/health\n")

    app.run(host="0.0.0.0", port=5000, debug=True)