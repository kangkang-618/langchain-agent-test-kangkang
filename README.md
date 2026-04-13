# 🏢 智能知识库问答系统

> 基于 LangChain + RAG + Streamlit 的企业级知识库问答系统

## 🎯 功能特点

- 🌐 **Web 界面** - Streamlit 美观界面
- 📄 **多格式支持** - PDF、Word、TXT、Markdown
- 🔍 **混合检索** - 向量检索 + 关键词匹配 + 重排序
- 🤖 **AI 问答** - DeepSeek 大模型
- 💬 **多轮对话** - 支持对话上下文记忆
- 📖 **来源标注** - 答案可查看参考来源
- 💾 **历史持久化** - SQLite 数据库存储
- 🐳 **Docker 部署** - 一键部署到服务器

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Streamlit |
| RAG | LangChain + ChromaDB |
| Embedding | BAAI/bge-m3 |
| LLM | DeepSeek |
| 存储 | SQLite |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt