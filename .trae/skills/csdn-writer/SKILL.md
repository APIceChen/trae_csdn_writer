---
name: "csdn-writer"
description: "AI写作助手，专用于CSDN文章自动生成与改写。当用户提供CSDN文章链接或文本内容并要求改写、洗稿、生成CSDN风格文章时自动调用。支持分析CSDN行文风格并根据原文重新撰写。集成质量验证脚本确保输出符合标准。"
---

# CSDN AI 写作助手 (CSDN Writer)

## 📋 技能概述

本技能是一个专用于 **CSDN（Chinese Software Developer Network）** 文章自动生成的 AI 写作 Agent，能够：

- ✅ 分析 CSDN 平台的典型行文风格和写作规范
- ✅ 根据用户提供的原始内容进行"洗稿"式改写
- ✅ 在保持原文核心内容和技术准确性的前提下，输出符合 CSDN 风格的文章
- ✅ **自动化质量控制**：内置验证脚本确保输出达标

## 🗂️ 项目结构（重要！）

```
d:\PythonProject\csdn_writer\
│
├── .trae/
│   └── skills/
│       └── csdn-writer/           # ⭐ 技能定义文件（当前文件）
│           └── SKILL.md
│
├── scripts/                       # 🔧 核心脚本工具
│   ├── csdn_validator.py          # 质量验证引擎（13项检测标准）
│   └── test_quality.py            # 一键测试脚本
│
├── input/                         # 📥 输入数据
│   ├── raw/                       # 原始输入（未处理）
│   │   ├── url_registry.md        # URL 链接记录表
│   │   └── sample_original_text.txt  # 示例原始文本
│   └── processed/                 # 处理后的输入（已分析）
│       └── pyd_packer_analyzed.md  # 示例：分析后的结构化数据
│
├── output/                        # 📤 输出产品
│   ├── articles/                  # 改写后的文章成品
│   │   └── sample_pyd_packer.md   # 示例输出文章
│   └── reports/                   # 质量检测报告
│       └── sample_quality_report.txt  # 示例质量报告
│
├── config/                        # ⚙️ 配置文件
│   └── project_config.json        # 项目配置（路径、验证规则等）
│
├── templates/                     # 📝 模板文件
│   └── csdn_article_template.md   # CSDN 文章标准模板
│
├── docs/                          # 📚 文档资料
│   └── AI_INSTRUCTIONS.md         # AI 使用指南（必读）
│
├── fewshot_samples/               # 🎯 Few-Shot 小样本提示系统
│   ├── FEWSHOT_README.md          # 系统说明文档
│   ├── sample_01/                 # 样本1：工具推荐类（pyd_packer）
│   │   ├── input.md               # 原始输入内容
│   │   ├── output.md              # 改写后的成品（95.2分）
│   │   └── metadata.json          # 风格特征元数据
│   ├── sample_02/                 # 样本2：技术教程类（n8n）
│   │   ├── input.md
│   │   ├── output.md              # 改写后的成品（87.6分）
│   │   └── metadata.json
│   └── sample_03/                 # 样本3：（预留位置）
│
└── tests/                         # 🧪 测试数据（预留）
```

## 🎯 核心脚本关联（AI 必须使用）

### 1️⃣ **质量验证引擎** - `scripts/csdn_validator.py`

**功能**：对改写后的文章进行 13 项自动化质量检测

**使用方式**：
```python
from scripts.csdn_validator import validate_csdn_article

# 验证文章质量
is_valid, report = validate_csdn_article(article_content)

# 结果说明：
# is_valid: bool - 是否通过验证（>=70分且必选项全过）
# report.total_score: float - 总分（0-100）
# report.results: List[CheckResult] - 详细检测结果
```

**检测项目**：
| 编号 | 检测项 | 级别 | 说明 |
|------|--------|------|------|
| 1 | 标题格式 | 必须 | 以 # 开头，长度>5字符 |
| 2 | 引入段落 | 必须 | 场景化描述 |
| 3 | 代码示例 | 必须 | 至少1个代码块 |
| 4 | 代码语言标注 | 建议 | 标注 python/bash 等 |
| 5 | 标题层级 | 必须 | 至少2个二级标题 |
| 6 | 段落间距 | 建议 | 空行分隔 |
| 7 | 互动结尾 | 建议 | 点赞/收藏引导 |
| 8 | 表情符号 | 可选 | 适度使用（2-15个） |
| 9 | 加粗强调 | 建议 | 至少3处 |
| 10 | 参考资料 | 建议 | GitHub/原文链接 |
| 11 | 文章长度 | 必须 | >=800字 |
| 12 | 人称视角 | 建议 | 第一/第二人称 |
| 13 | 过渡连接 | 可选 | 首先/接下来等 |

### 2️⃣ **一键测试脚本** - `scripts/test_quality.py`

**功能**：读取 `output/articles/` 中的文章并生成完整报告

**运行命令**：
```bash
cd d:\PythonProject\csdn_writer
python scripts/test_quality.py
```

**输出位置**：`output/reports/quality_report.txt`

### 3️⃣ **CSDN 文章爬虫** - `scripts/csdn_scraper.py` (v1.0 新增！)

**功能**：通过 URL 抓取 CSDN 文章的**完整原始内容**（非 AI 摘要）

**为什么重要？**
- ✅ **忠于原文**：获取完整的原始文章，而非简化/摘要版本
- ✅ **保留细节**：完整保留代码块、表格、格式标记等所有技术细节
- ✅ **质量保障**：基于完整信息改写，避免技术错误

**运行命令**：
```bash
# 基本用法（自动选择最佳方式）
python scripts/csdn_scraper.py <URL>

# 指定输出文件
python scripts/csdn_scraper.py <URL> -o output.md

# 使用 Playwright 模式（更完整，但较慢）
python scripts/csdn_scraper.py <URL> -m playwright

# 示例
python scripts/csdn_scraper.py https://blog.csdn.net/xxx/article/details/12345678
```

**支持的抓取方式**：

| 模式 | 技术 | 速度 | 完整度 | 推荐场景 |
|------|------|------|--------|----------|
| **auto (默认)** | 自动选择 | 快 | 高 | ✅ **首选，自动优化** |
| **requests** | requests + bs4 | ⚡ 极快 | 90% | 简单文章、快速测试 |
| **playwright** | 浏览器自动化 | 🐢 较慢 | 100% | 复杂页面、JS渲染内容 |

**输出内容**：
- 📄 完整的 Markdown 格式原文
- 📊 文章元数据（标题、作者、发布时间等）
- 🔍 内容统计（字数、代码块、表格等）
- ⏰ 抓取时间和方式记录

**依赖安装**（可选）：
```bash
# requests 模式（已默认支持）
pip install requests beautifulsoup4

# Playwright 模式（可选）
pip install playwright
playwright install
```

---

## 🔄 完整工作流程（AI 执行步骤）

当用户触发此技能时，AI **必须**按照以下流程操作：

### **阶段 1：接收与记录输入**

#### 步骤 1.1：识别输入类型

**如果用户提供 URL：**
```markdown
⚠️ 重要：使用爬虫脚本获取完整原始内容（非 WebFetch！）

✅ 优先使用：python scripts/csdn_scraper.py <URL> -o input/raw/<filename>.md
✅ 将抓取的完整原始内容保存到 input/raw/ 目录
✅ 在 input/raw/url_registry.md 中记录链接信息
✅ 验证内容完整性（字数、代码块等）

⚠️ 不要使用 WebFetch 工具（会返回 AI 摘要，丢失细节）
```

**如果提供文本/文件：**
```markdown
✅ 将文本保存到 input/raw/ 目录（.txt 或 .md 格式）
✅ 记录文件来源和元数据
```

#### 步骤 1.2：预处理与分析 + **加载 Few-Shot 样本（重要！）**

```markdown
✅ 分析文章核心主题和技术要点
✅ 提取关键信息（标题、作者、代码块、技术栈等）
✅ 保存结构化分析结果到 input/processed/ 目录
✅ 参考模板：templates/csdn_article_template.md

🎯 **Few-Shot 样本匹配**（必须执行！）：
   ✅ 识别文章类型（工具推荐/技术教程/问题解决等）
   ✅ 从 fewshot_samples/ 加载最匹配的 1-2 个样本
   ✅ 读取样本的 output.md 和 metadata.json
   ✅ 提取风格特征（标题模式、语气、结构、排版等）
   ✅ 在后续改写过程中持续参考这些特征
```

**样本选择策略**：
- **工具推荐类文章** → 参考 `sample_01` (pyd_packer, 95.2分)
- **技术教程类文章** → 参考 `sample_02` (n8n, 87.6分)
- **用户明确指定** → 按用户要求使用特定样本
- **复杂/混合类型** → 融合多个样本的优点

---

### **阶段 2：智能改写**

#### 步骤 2.1：应用 CSDN 风格规范

**必须包含的元素**：
- ✅ 吸引人的标题（带表情符号）
- ✅ 场景化引入段落
- ✅ 2+ 个二级标题章节
- ✅ 1+ 个代码示例（带语言标注）
- ✅ 表格展示（适用场景或功能对比）
- ✅ 加粗强调关键术语
- ✅ 互动结尾（点赞/收藏/关注）

#### 步骤 2.2：执行改写

```markdown
✅ 基于分析结果重新组织内容
✅ 转换为第一/第二人称视角
✅ 添加过渡词增强流畅度
✅ 保持技术准确性和事实不变
✅ 输出完整的 Markdown 格式
```

---

### **阶段 3：验证与输出**

#### 步骤 3.1：质量检测（必须执行！）

```python
# 调用验证脚本
from scripts.csdn_validator import validate_csdn_article
is_valid, report = validate_csdn_article(rewritten_content)

# 判断是否合格
if is_valid:
    print("✅ 通过验证")
else:
    print("❌ 需要改进")
    # 根据 report.results 中的建议进行修改
```

#### 步骤 3.2：保存输出产物

**必须保存到指定目录**：

```markdown
📄 改写后的文章 → output/articles/[主题名].md
📊 质量检测报告 → output/reports/[主题名]_report.txt
📝 处理后数据 → input/processed/[主题名]_analyzed.md
```

**命名规范**：
- 文件名使用英文下划线：`pyd_packer_article.md`
- 报告名添加后缀：`pyd_packer_report.txt`
- 日期格式可选：`20260528_pyd_packer.md`

---

## 📥 支持的输入格式

### 1️⃣ **CSDN 文章链接**
```
示例：https://blog.csdn.net/xxx/article/details/12345678
```
- 自动抓取网页内容
- 提取正文、标题、代码块
- 记录到 `input/raw/url_registry.md`

### 2️⃣ **纯文本格式 (.txt)**
- 直接粘贴或上传
- 保存到 `input/raw/`

### 3️⃣ **Markdown 格式 (.md)**
- 完整保留语法结构
- 保存到 `input/raw/`

### 4️⃣ **HTML 格式 (.html)**
- 解析 HTML 结构
- 提取文本和语义标签

---

## 📤 输出规范

### **必须产出的内容**：

#### 1️⃣ **改写后的文章** (`output/articles/`)
- 格式：Markdown (.md)
- 编码：UTF-8
- 内容：完整的 CSDN 风格文章
- 参考：`templates/csdn_article_template.md`

#### 2️⃣ **质量报告** (`output/reports/`)
- 包含：总分、各项检测结果、改进建议
- 格式：纯文本 (.txt)
- 来源：由 `scripts/csdn_validator.py` 自动生成

#### 3️⃣ **处理记录** (`input/processed/`)
- 原文分析结果
- 结构化数据提取
- 元数据信息

### **输出质量标准**：

| 维度 | 要求 | 权重 | 验证方式 |
|------|------|------|----------|
| 内容准确性 | 技术细节无误 | ⭐⭐⭐⭐⭐ | 人工审核 |
| 风格一致性 | 符合 CSDN 特征 | ⭐⭐⭐⭐⭐ | 脚本自动检测 |
| 可读性 | 语言流畅易懂 | ⭐⭐⭐⭐ | 脚本自动检测 |
| 结构完整性 | 引入+主体+总结 | ⭐⭐⭐⭐ | 脚本自动检测 |
| 排版规范性 | Markdown 正确 | ⭐⭐⭐ | 脚本自动检测 |

**最低通过标准**：
- ✅ 总分 >= 70 分
- ✅ 所有"必须"项全部通过
- ✅ 文章长度 >= 800 字

---

## ⚙️ 配置管理

所有配置集中在 `config/project_config.json`：

```json
{
  "validation": {
    "min_score_required": 70,      // 最低分数要求
    "required_checks_passed": true, // 必须项是否全过
    "auto_validate_after_rewrite": true // 是否自动验证
  },
  "paths": {
    // 各类文件的存储路径配置
  }
}
```

**修改配置后无需重启**，下次调用时自动生效。

---

## 🤖 AI 使用指令摘要

### **当你被激活时，请按以下顺序执行**：

1. ✅ **读取** `docs/AI_INSTRUCTIONS.md` 获取详细指引
2. ✅ **加载 Few-Shot 样本**（从 `fewshot_samples/` 读取匹配的样本）
3. ✅ **接收** 用户输入（URL 或文本）
4. ⚠️ **如果是 URL → 使用爬虫脚本获取完整原文**：
   - 运行 `python scripts/csdn_scraper.py <URL> -o input/raw/<filename>.md`
   - 验证抓取结果完整性
   - **不要使用 WebFetch**（会丢失细节）
5. ✅ **保存原始内容**到 `input/raw/` 目录
6. ✅ **分析** 内容并提取关键信息，保存到 `input/processed/`
7. ✅ **参考** 样本特征 + `templates/csdn_article_template.md` 进行改写
8. ✅ **调用** `scripts/csdn_validator.py` 验证质量
9. ✅ **保存** 文章到 `output/articles/` 和报告到 `output/reports/`
10. ✅ **返回** 给用户：改写结果 + 质量评分 + 改进建议（如有）

### **🎯 Few-Shot 使用规范（核心机制）**

#### **什么是 Few-Shot？**
Few-Shot Learning（少样本学习）通过提供 **2-3 个高质量示例** 来提升输出的一致性和准确性。

#### **为什么必须使用？**
- ✅ **保持风格一致性**：所有输出都遵循统一的 CSDN 写作风格
- ✅ **提升输出质量**：基于成功案例进行模仿学习
- ✅ **减少随机性**：避免每次输出的质量波动过大
- ✅ **加速收敛**：减少反复修改的次数

#### **如何正确使用？**

**步骤 1：自动匹配**
```python
# 根据文章类型自动选择最佳样本
task_type = analyze_article_type(user_input)
if task_type == "tool_recommendation":
    samples = load_sample("sample_01")  # pyd_packer, 95.2分
elif task_type == "tutorial":
    samples = load_sample("sample_02")  # n8n, 87.6分
```

**步骤 2：提取特征**
从每个样本中提取关键风格维度：
| 维度 | 提取内容 | 权重 |
|------|---------|------|
| 标题模式 | emoji、长度、句式 | 20% |
| 引入方式 | 场景描述、痛点提出 | 15% |
| 章节结构 | 二级标题数量、逻辑顺序 | 25% |
| 代码呈现 | 块数、注释密度 | 15% |
| 语气风格 | 口语化程度、表情频率 | 15% |
| 结尾方式 | 互动引导、总结要点 | 10% |

**步骤 3：应用特征**
在生成过程中，实时对照样本特征进行调整，确保：
- 风格相似度 >= 85%
- 质量评分 >= 样本基准分 * 0.9

#### **特殊情况处理**

**用户指定样本时**：
```
用户说："像样本1那样简洁" → 强制使用 sample_01 的风格特征
用户说："写详细一点" → 参考 sample_02 的详细程度
```

**无匹配样本时**：
- 如果新文章类型不在现有样本中
- 综合参考所有可用样本的通用特征
- 记录该任务类型，后续考虑新增专用样本

### **关键提醒**：

⚠️ **绝对不要跳过验证步骤！**
⚠️ **绝对不要忽略 Few-Shot 样本！**
⚠️ **所有输出必须归档到对应文件夹！**
⚠️ **保持技术准确性优先于风格优化！**
⚠️ **样本是参考不是枷锁，要有适度创新空间！**

---

## 📚 相关文档

- **AI 详细指南**：[docs/AI_INSTRUCTIONS.md](../../docs/AI_INSTRUCTIONS.md)
- **文章模板**：[templates/csdn_article_template.md](../../templates/csdn_article_template.md)
- **项目配置**：[config/project_config.json](../../config/project_config.json)
- **Few-Shot 系统**：[fewshot_samples/FEWSHOT_README.md](../../fewshot_samples/FEWSHOT_README.md)
  - **样本1（工具推荐）**：[fewshot_samples/sample_01/](../../fewshot_samples/sample_01/) - 95.2分
  - **样本2（技术教程）**：[fewshot_samples/sample_02/](../../fewshot_samples/sample_02/) - 87.6分

---

## 版本信息

- **当前版本**: **v1.3 (爬虫增强版)**
- **更新日期**: 2026-05-28
- **主要更新**:
  - ✅ 新增标准化项目结构
  - ✅ 集成质量验证脚本
  - ✅ 完善输入/输出归档机制
  - ✅ 添加 AI 使用指令
  - ✅ 新增 Few-Shot 小样本提示系统
  - ✅ 集成 Git 版本管理
  - ✅ 提供 2 个高质量样本（工具推荐 + 技术教程）
  - ✅ 建立样本自动匹配和特征提取机制
  - 🆕 **新增 CSDN 文章爬虫脚本 (csdn_scraper.py)**
  - 🆕 **支持获取完整原始内容（非 AI 摘要）**
  - 🆕 **集成 requests + Playwright 双模式抓取**
  - 🆕 **自动去重和格式优化**
  - 🆕 **工作流全面升级：URL 输入优先使用爬虫**
- **适用平台**: Trae IDE
- **Git 仓库**: https://github.com/APIceChen/trae_csdn_writer.git
- **维护状态**: 活跃开发中
