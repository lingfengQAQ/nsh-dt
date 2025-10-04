# 逆水寒殿试答题器

逆水寒游戏殿试答题助手，截图识别题目，AI+本地诗词库秒速给出答案。

## ✨ 功能特色

- 📚 **40万首诗词库**：100%简体中文，搜索速度<1ms
- 🤖 **多AI支持**：OpenAI、豆包、DeepSeek等
- 🖼️ **智能截图**：悬浮窗框选题目区域
- ⚡ **极速搜索**：倒排索引优化，8000倍性能提升

## 🚀 快速开始

### 1. 安装
```bash
git clone https://github.com/lingfengQAQ/nsh-dt.git
cd nsh-dt
pip install -r requirements.txt
```

### 2. 下载数据库
**重要**: 数据库文件193MB，需单独下载

从 [Releases](https://github.com/lingfengQAQ/nsh-dt/releases) 下载 `poetry.db`，放到项目根目录

### 3. 配置
首次运行后点击"设置"：
- **OCR**: 配置Tesseract路径 或 百度云API
- **AI**: 添加至少一个AI服务的API密钥

### 4. 启动
```bash
python main.py
```

## 🎮 使用方法

1. 点击"打开截图区域"
2. 拖动调整悬浮窗覆盖题目
3. 点击"截图并识别"或按回车
4. 查看答案（诗词题优先看本地库结果）

## 📊 诗词数据库

- **数据量**: 401,294首
- **大小**: 193MB
- **编码**: 100%简体中文
- **来源**: [古诗文网](https://github.com/caoxingyu/gushiwen) + [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)
- **搜索**: <1ms（倒排索引）

### 支持的题型
识别包含以下关键词的诗词组字题：
- "从以下字中选出一句诗词"
- "用这些字组成一句诗"

**示例**:
- ✅ "请从以下字中选出一句诗词：应怜屐齿印苍苔"
- ❌ "李白写过什么诗？"（由AI回答）

## 🔨 自行构建数据库（可选）

```bash
# 下载数据源
git clone https://github.com/caoxingyu/gushiwen.git
git clone https://github.com/chinese-poetry/chinese-poetry.git

# 合并并去重（自动繁简转换）
python archive/merge_databases.py
```

## ❓ 常见问题

**Q: 为什么Git仓库没有poetry.db？**
A: 文件太大(193MB)，从Releases下载或自行构建

**Q: 本地知识库找不到答案？**
A:
- 确保题目包含"请从以下字中选出一句诗词"等触发短语
- 题目格式示例：`40分请从以下字中选出一句诗词应怜屐齿印苍苔确定`
- 程序会自动提取"诗词"后的字符，去除前后干扰词

**Q: OCR识别不准？**
A: 调整截图区域确保清晰，或切换OCR引擎

**Q: AI回答不完整？**
A: 设置中增加"最大令牌数"到4000+

**Q: 如何查看日志？**
A: 查看项目根目录下的 `app.log` 文件，包含所有识别和搜索记录

## 📂 项目结构

```
nsh-dt/
├── main.py                    # 主程序
├── knowledge_base_manager.py  # 诗词搜索（倒排索引）
├── ai_manager.py              # AI服务
├── ocr_manager.py             # OCR识别
├── screenshot_tool.py         # 截图工具
├── settings_window.py         # 设置界面
├── poetry.db                  # 诗词库（需下载）
└── archive/                   # 数据库构建脚本
```

## 🔧 更新日志

**v3.1** (2025-01)
- 🔧 优化本地知识库字符提取逻辑
  - 智能提取"诗词"后的字符
  - 自动去除题号、分数前缀（如"40分"）
  - 自动去除尾部干扰词（确定、取消等）
- 📝 增强日志记录功能
  - 记录OCR识别结果、本地库搜索、AI回答
  - 日志同时输出到文件(app.log)和控制台
  - UTF-8编码，追加模式
- 📦 优化打包支持
  - poetry.db从exe同目录加载（不打包到exe内）
  - 减小打包后体积

**v3.0** (2025-01)
- 诗词库扩充至40万首（合并去重）
- 搜索性能提升8000倍（8s→1ms）
- 100%繁简转换
- 项目文件整理

**v2.1**
- UI统一优化
- 答案高亮显示

## 📄 协议

MIT License

## 🙏 致谢

- [古诗文网](https://github.com/caoxingyu/gushiwen) - 高质量诗词数据
- [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) - 海量古诗词
- [OpenCC](https://github.com/BYVoid/OpenCC) - 繁简转换

---
**祝您在逆水寒殿试中取得好成绩！** 🏆
