"""
文档加载器 - 把各种格式的文档转成文本
支持：PDF、Word、TXT、Markdown
"""

import os
from langchain_community.document_loaders import (
    PyPDFLoader,  # PDF 加载器
    Docx2txtLoader,  # Word 加载器
    TextLoader,  # 纯文本加载器
    UnstructuredMarkdownLoader,  # Markdown 加载器
)


class DocumentLoader:
    """
    文档加载器类

    作用：统一处理不同格式的文档
    """

    # 映射：文件后缀 → 对应的加载器
    LOADER_MAP = {
        ".pdf": PyPDFLoader,  # PDF 文件
        ".docx": Docx2txtLoader,  # Word 文件（新版）
        ".doc": Docx2txtLoader,  # Word 文件（旧版）
        ".txt": TextLoader,  # 纯文本
        ".md": UnstructuredMarkdownLoader,  # Markdown
    }

    def __init__(self):
        """初始化时获取支持的文件类型"""
        self.supported_types = list(self.LOADER_MAP.keys())
        print(f"📚 支持的文件类型: {self.supported_types}")

    def get_loader(self, file_path: str):
        """
        根据文件后缀选择合适的加载器

        参数:
            file_path: 文件的完整路径

        返回:
            对应的加载器实例
        """
        # 1. 获取文件后缀（小写）
        ext = os.path.splitext(file_path)[1].lower()

        # 2. 查找对应的加载器
        if ext not in self.LOADER_MAP:
            raise ValueError(
                f"不支持的文件类型: {ext}\n"
                f"支持的类型: {self.supported_types}"
            )

        # 3. 获取加载器类
        loader_class = self.LOADER_MAP[ext]

        # 4. TextLoader 需要指定编码，否则中文会乱码
        if ext == ".txt":
            return loader_class(file_path, encoding="utf-8")

        return loader_class(file_path)

    def load(self, file_path: str):
        """
        加载文件，返回文本内容

        参数:
            file_path: 文件的完整路径

        返回:
            list[Document]: 文档对象列表
        """
        # 1. 获取合适的加载器
        loader = self.get_loader(file_path)

        # 2. 加载文档
        documents = loader.load()

        # 3. 清理文本（去除多余空行）
        for doc in documents:
            content = doc.page_content
            # 把多个连续空行合并成一个
            content = "\n".join(
                line.strip() for line in content.split("\n") if line.strip()
            )
            doc.page_content = content

        return documents


# ==================== 独立测试 ====================
if __name__ == "__main__":
    # 测试代码
    loader = DocumentLoader()
    print(f"✅ DocumentLoader 创建成功！")