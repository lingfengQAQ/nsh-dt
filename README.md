# 逆水寒殿试答题器

专为逆水寒游戏殿试答题设计的智能助手，通过截图快速识别题目，调用AI服务和本地诗词库，为您提供准确答案。

## ✨ 功能特色

- 🎯 **专为殿试设计**: 针对逆水寒殿试题目优化，特别适合诗词类题目
- 📚 **海量诗词库**: 内置超过40万首古典诗词，100%简体中文，覆盖历代经典
- ⚡ **极速搜索**: 倒排索引优化，诗词搜索仅需1毫秒（8000倍性能提升）
- 🖼️ **智能截图识别**: 可调节悬浮窗，精准识别题目文字
- 🤖 **多AI支持**: 兼容OpenAI、豆包、硅基流动等多个AI服务
- 🔍 **高精度OCR**: 支持Tesseract和百度云两种OCR引擎
- 📝 **优化答案显示**: 突出显示答案，减少冗余信息

## 📊 诗词数据库

### 数据库信息
- **数据量**: 401,294首诗词
- **数据库大小**: 193MB
- **字符编码**: 100%简体中文（使用OpenCC转换）
- **数据来源**:
  - [古诗文网](https://github.com/caoxingyu/gushiwen) (108k首，高质量)
  - [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) (293k首，全唐诗、全宋词等)
- **搜索性能**: <1ms (倒排索引优化)

### 🎯 支持的问题格式
本地知识库专门响应以下类型的诗词组字问题：
- "请从以下字中选出一句诗词"
- "请从下列字中选出一句诗词"
- "从以下字中选出一句诗词"
- "用这些字组成一句诗"
- "用下面的字组成诗句"
- "这些字能组成什么诗句"

### 💡 使用示例
- ✅ **会触发**: "请从以下字中选出一句诗词：应怜屐齿印苍苔"
- ❌ **不会触发**: "李白写过什么诗？"
- ✅ **会触发**: "用这些字组成一句诗：春眠不觉晓处处闻啼鸟"

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/lingfengQAQ/nsh-dt.git
cd nsh-dt
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 下载诗词数据库
**重要**: 由于数据库文件较大(193MB)，未包含在Git仓库中，需要单独下载：

```bash
# 下载地址（请从Release页面下载）
# https://github.com/lingfengQAQ/nsh-dt/releases

# 下载后将 poetry.db 放置到项目根目录
```

或者自行构建数据库（参见下方"数据库构建"章节）

### 4. 配置服务
启动程序后点击"设置"：

**OCR配置**：
- **Tesseract**（推荐本地使用）：
  - 下载地址: https://github.com/UB-Mannheim/tesseract/wiki
  - 安装后配置tesseract.exe路径
  - 默认路径: `C:\Program Files\Tesseract-OCR\tesseract.exe`

- **百度云OCR**（在线服务）：
  - 注册地址: https://cloud.baidu.com/
  - 获取API Key和Secret Key
  - 每月有免费额度

**AI配置**：
- 添加AI服务（OpenAI、豆包、DeepSeek等）
- 配置API密钥和模型
- 至少启用一个AI服务

## 🎮 使用方法

1. **启动程序**：
   ```bash
   python main.py
   ```

2. **答题流程**：
   - 点击"打开截图区域"
   - 调整悬浮窗覆盖题目区域
   - 点击"截图并识别"或按回车键
   - 查看本地库和AI答案

3. **殿试技巧**：
   - 诗词组字题目优先查看本地知识库答案
   - 本地库匹配结果会显示完整诗句、作者和诗名
   - 多个AI答案可供参考对比
   - 按Esc键快速关闭截图区域

## 📂 项目结构

```
nsh-dt/
├── main.py                    # 主程序入口
├── ai_manager.py              # AI服务管理
├── knowledge_base_manager.py  # 诗词库管理与搜索
├── ocr_manager.py             # OCR文字识别
├── settings_window.py         # 设置界面
├── screenshot_tool.py         # 截图工具
├── ui.py                      # UI组件库
├── requirements.txt           # Python依赖
├── settings.json.example      # 配置文件模板
├── poetry.db                  # 诗词数据库（需下载）
└── archive/                   # 归档目录
    ├── README.md              # 归档文件说明
    ├── import_gushiwen.py     # 古诗文网数据导入
    ├── merge_databases.py     # 数据库合并脚本
    └── rebuild_db.py           # 数据库重建脚本
```

## 🔨 数据库构建（可选）

如果需要自行构建诗词数据库：

### 方式一：使用已合并数据库
```bash
# 1. 下载古诗文网数据
git clone https://github.com/caoxingyu/gushiwen.git

# 2. 下载中国古诗词数据
git clone https://github.com/chinese-poetry/chinese-poetry.git

# 3. 运行合并脚本
python archive/merge_databases.py
```

### 方式二：单独数据源
```bash
# 仅使用古诗文网数据（推荐质量优先）
python archive/import_gushiwen.py

# 或使用chinese-poetry数据（推荐数量优先）
python archive/rebuild_db.py
```

合并后的数据库会自动进行：
- 去重处理（基于标题+作者）
- 繁简转换（使用OpenCC库）
- 索引优化（倒排索引）

## ❓ 常见问题

**Q: 为什么Git仓库中没有poetry.db？**
A: 数据库文件193MB较大，超过GitHub推荐大小。请从Release页面下载或自行构建。

**Q: 诗词搜索很慢？**
A: 确保使用最新版本数据库，已内置倒排索引优化（搜索时间<1ms）。

**Q: AI回答不完整？**
A: 在AI设置中增加"最大令牌数"到4000以上。

**Q: OCR识别不准确？**
A: 调整截图区域确保题目清晰，或切换OCR引擎（Tesseract ↔ 百度云）。

**Q: 适用于哪些题目？**
A: 特别适合诗词文学类题目。其他类型题目（历史、地理等）通过AI服务回答。

**Q: 如何更新数据库？**
A: 重新运行merge_databases.py脚本，会自动获取最新数据并去重。

## 🔧 更新日志

### v3.0 (2025-01)
- 🎉 重大升级：诗词数据库扩充至40万首（108k + 293k合并）
- ⚡ 性能优化：搜索速度提升8000倍（8秒 → 1毫秒）
- 🔄 数据质量：100%繁简转换，修复历史数据错误
- 📁 项目整理：归档旧文件，优化项目结构
- 🔐 安全改进：敏感配置排除Git提交

### v2.1
- 全面统一主界面与设置面板的视觉风格
- 新增答案高亮区，首个AI回答可一眼看到
- 设置面板支持更友好的导航与卡片化布局
- 改善知识库查询性能并在退出时主动释放内存

### v2.0
- 重命名为"逆水寒殿试答题器"
- 优化诗词答案显示，突出关键信息
- 改进错误处理和稳定性
- 固定依赖版本，提升兼容性

## 🤝 贡献

欢迎提交Issue和Pull Request！

如果发现诗词数据错误，请提供：
- 错误的诗句内容
- 正确的诗句内容
- 诗词来源（诗名、作者）

## 📄 开源协议

本项目采用 MIT License 开源协议。

## 🙏 致谢

- [古诗文网](https://github.com/caoxingyu/gushiwen) - 提供高质量诗词数据
- [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) - 提供海量古诗词数据
- [OpenCC](https://github.com/BYVoid/OpenCC) - 繁简转换工具

---

**祝您在逆水寒殿试中取得好成绩！** 🏆
