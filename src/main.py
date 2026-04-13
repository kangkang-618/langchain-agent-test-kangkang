"""
主程序 - 企业级知识库问答系统
"""

import os
import sys

# 添加 src 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import agent
from rag import kb
from config import KNOWLEDGE_BASE_PATH


def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("🏢 企业级智能知识库问答系统")
    print("=" * 60)
    print("功能：")
    print("  1. 知识库问答（基于 RAG）")
    print("  2. 工具调用（计算器等）")
    print("  3. 文档管理")
    print()
    print("命令：")
    print("  :upload <文件路径> - 上传文档到知识库")
    print("  :list            - 查看知识库文档")
    print("  :delete <文件名> - 删除知识库文档")
    print("  :quit            - 退出程序")
    print("=" * 60)
    print()


def upload_document(filename):
    """上传文档（从 knowledge_base 文件夹）"""
    # 直接用文件名，在 knowledge_base 目录下查找
    file_path = os.path.join(KNOWLEDGE_BASE_PATH, filename)

    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {filename}")
        print(f"   请确认文件在 knowledge_base 文件夹中")
        return

    try:
        result = kb.add_document(filename)
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ 上传失败: {e}")


def main():
    """主函数"""
    print_welcome()

    # 对话历史
    history = []

    print("💬 开始对话吧！\n")

    while True:
        try:
            user_input = input("你: ").strip()

            if not user_input:
                continue

            # 处理命令
            elif user_input.startswith(':upload '):
                filename = user_input[8:].strip()
                upload_document(filename)
                continue

            elif user_input == ':list':
                docs = kb.list_documents()
                if docs:
                    print("📚 知识库文档:")
                    for doc in docs:
                        print(f"  - {doc}")
                else:
                    print("📭 知识库为空")
                continue

            elif user_input == ':delete':
                print("用法: :delete <文件名>")
                continue

            elif user_input.startswith(':delete '):
                filename = user_input[8:].strip()
                result = kb.delete_document(filename)
                print(result)
                continue

            elif user_input in [':quit', ':exit', 'quit', 'exit']:
                print("👋 再见！")
                break

            # 对话
            print("\n🤖 AI 思考中...")

            result, docs = agent.chat_with_rag(user_input, kb, history)

            # 提取 AI 回复
            messages = result['messages']
            ai_message = messages[-1].content

            # 显示引用
            if docs:
                print("\n📖 参考来源:")
                for i, doc in enumerate(docs, 1):
                    print(f"  [{i}] {doc['source']}")
            print()

            # 显示回复
            print(f"AI: {ai_message}\n")

            # 更新历史
            history.append(("user", user_input))
            history.append(("assistant", ai_message))

            # 限制历史长度
            if len(history) > 20:
                history = history[-20:]

        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}\n")


if __name__ == "__main__":
    main()