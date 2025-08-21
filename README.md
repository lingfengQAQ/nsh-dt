# 智能问题回答助手

一个功能强大的桌面应用程序，能够通过截图快速识别题目，并并行调用多个在线AI服务和本地知识库，为您提供最快、最全面的答案。

## ✨ 功能亮点

-   ✅ **多源并行搜索**: AI服务与本地知识库同时搜索，结果实时呈现，速度极快。
-   ✅ **强大的本地诗词库**: 内置超过33万首古典诗词，支持离线、快速的诗词查找。
-   ✅ **多线程本地搜索**: 对本地数据库的搜索进行多线程优化，充分利用CPU性能。
-   ✅ **灵活的截图工具**: 可自由调整大小和位置的悬浮窗，始终置顶，操作便捷。
-   ✅ **高精度OCR识别**: 支持Tesseract（本地）和百度云（在线）两种OCR引擎。
-   ✅ **广泛的AI兼容性**: 支持所有兼容OpenAI API的AI服务，并可轻松添加自定义服务。
-   ✅ **完善的设置中心**: 提供图形化界面，轻松管理AI、OCR及知识库设置。

## 🚀 安装与配置

### 1. 安装Python依赖

首先，请确保您已安装所有必需的Python库：

```bash
pip install -r requirements.txt
```

### 2. 准备本地知识库

本程序的核心功能之一是强大的本地诗词搜索。首次使用时，您需要生成知识库。

1.  **下载诗词数据**:
    *   从 [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) 项目下载完整的诗词数据库 (点击 `Code` -> `Download ZIP`)。
    *   解压后，将名为 `chinese-poetry-master` 的文件夹放入本程序根目录。

2.  **整合数据库**:
    *   运行 `consolidate_poetry.py` 脚本，它会自动扫描诗词数据并生成一个庞大的 `poetry_knowledge_base.json` 文件。
    ```bash
    python consolidate_poetry.py
    ```

3.  **拆分数据库以优化性能**:
    *   运行 `split_database.py` 脚本，它会将上一步生成的大文件拆分成多个小文件，为多线程搜索做准备。
    ```bash
    python split_database.py
    ```

### 3. 配置OCR服务

程序支持两种OCR引擎，请至少配置一种：

-   **Tesseract-OCR (本地, 推荐)**:
    1.  从 [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) 下载并安装。
    2.  在程序“设置” -> “OCR设置”中，选择“Tesseract”并指定 `tesseract.exe` 的路径。

-   **百度云OCR (在线)**:
    1.  在百度智能云创建文字识别应用，获取 `API Key` 和 `Secret Key`。
    2.  在程序设置中选择“百度”，并填入您的密钥。

### 4. 配置AI服务

在“设置” -> “AI设置”中，您可以添加和管理多个AI服务。

-   **名称**: 自定义，方便识别。
-   **类型**: 选择 `openai`, `doubao` 或其他，对于不确定的兼容API，选 `custom`。
-   **API密钥**: 您的服务密钥。
-   **模型**: 填入您要使用的具体模型名称 (如 `gpt-4o`)。
-   **API地址**: 服务的API基础URL (如 `https://api.openai.com/v1`)。
-   **最大令牌数**: 建议设置为 `4000` 或更高，以防回答被截断。

## 💡 使用流程

1.  **启动程序**:
    ```bash
    python main.py
    ```
2.  **打开截图区域**: 点击主界面的“打开截图区域”按钮。
3.  **调整区域**: 拖动并调整悬浮窗，使其覆盖您想识别的题目。
4.  **截图并识别**: 点击“截图并识别”按钮。
5.  **查看结果**: 程序将立即开始并行搜索。本地知识库和所有AI的回答会实时显示在各自的卡片中，谁先完成谁先显示。

## 📁 文件结构

```
.
├── main.py                  # 主程序入口
├── ai_manager.py            # AI服务管理模块
├── knowledge_base_manager.py# 本地知识库管理（多线程）
├── ocr_manager.py           # OCR引擎管理
├── settings_window.py       # 设置窗口界面
├── screenshot_tool.py       # 截图工具
|
├── consolidate_poetry.py    # 脚本：整合原始诗词数据
├── split_database.py        # 脚本：拆分数据库以优化性能
|
├── poetry_knowledge_base.json # （生成的）完整知识库
├── poetry_db_parts/         # （生成的）拆分后的数据库目录
|
├── requirements.txt         # Python依赖
├── settings.json            # 配置文件（自动生成）
└── README.md                # 本说明文档
```

## ❓ 常见问题

-   **Q: 本地诗词搜索很慢怎么办？**
    A: 请确保您已经运行了 `split_database.py` 脚本。这个脚本会将数据库拆分成小块，是实现多线程加速的关键。

-   **Q: AI返回“回答内容为空”或类似错误？**
    A: 这通常是因为 `最大令牌数` 设置得太小。请在AI设置中，将该值调高（如 `4000`），以确保AI有足够的空间生成完整回答。

-   **Q: 如何添加新的诗词？**
    A: 将新的诗词数据（JSON格式）放入 `chinese-poetry-master` 相应的子目录中，然后重新运行 `consolidate_poetry.py` 和 `split_database.py` 即可。

## 📜 许可证

本项目采用 [MIT License](LICENSE)。
