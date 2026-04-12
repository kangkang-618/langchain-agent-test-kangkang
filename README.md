# 🏢 智能知识库问答系统

> 基于 LangChain + RAG + Streamlit 的企业级知识库问答系统，支持多种文档格式、Web 界面、聊天历史。

## 🎯 功能特点

- 🌐 **Web 界面** - Streamlit 美观界面
- 📄 **多格式支持** - PDF、Word、TXT、Markdown
- 🔍 **混合检索** - 向量检索 + 关键词匹配 + 重排序
- 🤖 **AI 问答** - DeepSeek 大模型
- 💬 **多轮对话** - 支持对话上下文记忆
- 📖 **来源标注** - 答案可查看参考来源
- 💾 **历史持久化** - SQLite 数据库存储
- 🌐 **REST API** - Flask API 接口
- 🐳 **Docker 部署** - 一键部署到服务器

## 🏗️ 系统架构
用户提问
↓
┌─────────────────┐
│ Web 界面 │
│ (Streamlit) │
└────────┬────────┘
│
┌────────▼────────┐
│ 问答链 │
│ (QA Chain) │
└────────┬────────┘
│
┌────┴────┐
↓ ↓
┌───────┐ ┌───────┐
│ 检索器 │ │ 重排序 │
│ 混合检索│ │ │
└───┬───┘ └───────┘
↓
┌────▼────┐
│向量数据库│
└─────────┘

CopyCopied!

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Streamlit | Web 界面框架 |
| Agent | ReAct | 多步推理 |
| RAG | LangChain | 检索增强生成 |
| 向量检索 | ChromaDB | 本地向量数据库 |
| Embedding | BAAI/bge-m3 | 国产免费模型 |
| LLM | DeepSeek | 高性价比大模型 |
| 存储 | SQLite | 聊天历史持久化 |
| API | Flask | REST 接口 |
| 部署 | Docker | 容器化部署 |

## 📂 项目结构
langchain-agent-test-kangkang/
├── web_app/ # Web 应用
│ ├── main.py # Streamlit 主程序
│ ├── config.py # 配置文件
│ ├── document_loader.py # 文档加载器
│ ├── embeddings.py # 向量化
│ ├── retriever.py # 检索器
│ ├── reranker.py # 重排序
│ ├── qa_chain.py # 问答链
│ ├── database.py # 数据库
│ └── api.py # REST API
├── data/ # 数据目录
├── knowledge_base/ # 文档存储
├── Dockerfile # Docker 配置
├── docker-compose.yml # Docker Compose
├── requirements.txt # Python 依赖
└── README.md # 项目文档

CopyCopied!

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
2. 配置 API Key
编辑 web_app/config.py：

pythonCopyCopied!
DEEPSEEK_API_KEY = "your-deepseek-api-key"
EMBEDDING_API_KEY = "your-siliconflow-api-key"
3. 启动 Web 界面
bashCopyCopied!
streamlit run web_app/main.py
4. 启动 API 服务
bashCopyCopied!
python web_app/api.py
📖 核心功能演示
Web 界面
![功能演示]

上传文档（PDF、Word、TXT、MD）
输入问题，AI 基于文档回答
点击「参考来源」查看答案依据
历史对话自动保存
API 接口
bashCopyCopied!
# 问答
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "RAG是什么？"}'

# 上传文档
curl -X POST http://localhost:5000/api/upload \
  -F "file=@文档.pdf"
🤝 贡献
欢迎提交 Issue 和 Pull Request！

📄 License
MIT License

👨‍💻 作者
康康

🙏 致谢
LangChain
DeepSeek
Chroma
硅基流动
CopyCopied!
