# 🏢 智能知识库问答系统

> 基于 LangChain + RAG 的企业级智能问答系统

## 🎯 项目简介

这是一个完整的 AI Agent 系统，可以：

- 📚 **RAG 知识检索** - 上传文档，自动向量化
- 🤖 **AI Agent** - 基于 ReAct 框架的多步推理
- 🔧 **工具调用** - 计算器、文件读取等多种工具

## 🛠️ 技术栈

- **大模型**: DeepSeek
- **Embedding**: BAAI/bge-m3
- **向量数据库**: Chroma
- **开发框架**: LangChain 1.2.x

## 🚀 快速开始

```bash
pip install -r requirements.txt
cd src
python main.py
