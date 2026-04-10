"""
主程序 - 企业级智能知识库问答系统
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import agent
from rag import kb
from config import KNOWLEDGE_BASE_PATH


def print_welcome():
    print("=" * 50)
    print("🏢 企业级智能知识库问答系统")
    print("=" * 50)
    print("命令：")
    print("  :upload <文件名>  - 上传文档")
    print("  :list           - 查看知识库")
    print("  :delete <文件名> - 删除文档")
    print("  :quit           - 退出")
    print()


def upload_document(filename):
    file_path = os.path.join(KNOWLEDGE_BASE_PATH, filename)
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {filename}")
        return
    try:
        result = kb.add_document(filename)
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ 上传失败: {e}")


def main():
    print_welcome()
    history = []
    
    while True:
        try:
            user_input = input("你: ").strip()
            if not user_input:
                continue
            
            if user_input.startswith(':upload '):
                upload_document(user_input[8:].strip())
                continue
            elif user_input == ':list':
                docs = kb.list_documents()
                if docs:
                    print("📚 知识库文档:", docs)
                else:
                    print("📭 知识库为空")
                continue
            elif user_input.startswith(':delete '):
                print(kb.delete_document(user_input[8:].strip()))
                continue
            elif user_input in [':quit', ':exit']:
                print("👋 再见！")
                break
            
            print("\n🤖 AI 思考中...")
            result, docs = agent.chat_with_rag(user_input, kb, history)
            messages = result['messages']
            ai_message = messages[-1].content
            
            if docs:
                print("\n📖 参考来源:", [d['source'] for d in docs])
            print(f"\nAI: {ai_message}\n")
            
            history.append(("user", user_input))
            history.append(("assistant", ai_message))
            if len(history) > 20:
                history = history[-20:]
        
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}\n")


if __name__ == "__main__":
    main()
