# CSDN AI Writer 项目使用指南

> **版本**: v1.1
> **更新日期**: 2026-05-28
> **适用平台**: Trae IDE

---

## 📌 项目简介

**CSDN AI Writer** 是一个专用于 CSDN 技术文章自动生成与改写的 AI Agent 技能系统，具备：

- ✅ 智能文章改写（保持技术准确性 + 转换为 CSDN 风格）
- ✅ 自动化质量检测（13 项标准，100 分制评分）
- ✅ 标准化文件管理（输入/输出/配置分类归档）
- ✅ 完整的工作流程控制（从输入到输出的全链路）

---

## 🗂️ 项目结构一览

```
csdn_writer/
│
├── .trae/skills/csdn-writer/     # ⭐ Agent 技能定义
│   └── SKILL.md                  #    （AI 触发规则和工作流）
│
├── scripts/                      # 🔧 核心工具脚本
│   ├── csdn_validator.py         #    质量验证引擎
│   └── test_quality.py           #    一键测试工具
│
├── input/                        # 📥 输入数据区
│   ├── raw/                      #    原始内容（URL、文本）
│   │   ├── url_registry.md       #    URL 链接记录表
│   │   └── *.txt / *.md          #    原始文本文件
│   └── processed/                #    分析后的结构化数据
│       └── *_analyzed.md         #    内容分析结果
│
├── output/                       # 📤 输出产品区
│   ├── articles/                 #    改写后的文章成品
│   │   └── *.md                  #    Markdown 格式文章
│   └── reports/                  #    质量检测报告
│       └── *_report.txt          #    验证结果报告
│
├── config/                       # ⚙️ 配置文件
│   └── project_config.json       #    项目参数设置
│
├── templates/                    # 📝 模板库
│   └── csdn_article_template.md  #    CSDN 文章标准模板
│
├── docs/                         # 📚 文档资料
│   └── AI_INSTRUCTIONS.md        #    AI 使用指南（详细版）
│
└── tests/                        # 🧪 测试数据（预留）
```

---

## 🚀 快速开始

### 方式一：在 Trae IDE 中使用（推荐）

直接在对话中触发技能：

```markdown
# 示例 1：通过 URL 改写
帮我把这篇CSDN文章改写一下：
https://blog.csdn.net/xxx/article/details/12345

# 示例 2：通过文本改写
我有一段关于Docker的技术文档，帮我改成CSDN风格：

[粘贴文本内容]
```

**AI 会自动执行完整流程并返回结果！**

---

### 方式二：命令行手动测试

#### 1️⃣ 验证已有文章质量

```bash
# 进入项目目录
cd d:\PythonProject\csdn_writer

# 运行质量检测（自动检测 output/articles/ 下的文件）
python scripts/test_quality.py

# 或指定特定文件
python scripts/test_quality.py output/articles/your_article.md
```

#### 2️⃣ 在 Python 中调用验证器

```python
import sys
sys.path.insert(0, 'scripts')
from csdn_validator import validate_csdn_article

# 读取文章
with open('output/articles/sample.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 执行验证
is_valid, report = validate_csdn_article(content)

# 查看结果
print(f"是否通过: {is_valid}")
print(f"总分: {report.total_score}/100")
print("\n详细报告:")
print(report.summary)
```

---

## 📋 使用流程详解

### 当你提供输入后，AI 会执行以下步骤：

#### **阶段 1：接收与记录**
1. 识别输入类型（URL 或文本）
2. 保存原始内容到 `input/raw/`
3. 记录元数据信息

#### **阶段 2：深度分析**
4. 提取核心主题和技术要点
5. 识别关键信息和代码块
6. 保存分析结果到 `input/processed/`

#### **阶段 3：智能改写**
7. 参考 `templates/csdn_article_template.md`
8. 应用 CSDN 行文风格规范
9. 保持技术准确性的同时优化表达

#### **阶段 4：质量验证**
10. 调用 `scripts/csdn_validator.py` 检测
11. 检查 13 项质量标准
12. 如未达标则自动改进

#### **阶段 5：归档与汇报**
13. 保存文章到 `output/articles/`
14. 生成报告到 `output/reports/`
15. 向用户返回完整结果

---

## 📊 质量标准说明

### 13 项自动化检测项目：

| # | 项目 | 级别 | 要求 |
|---|------|------|------|
| 1 | 标题格式 | 🔴 必须 | # 开头, >5字符 |
| 2 | 引入段落 | 🔴 必须 | 场景化描述 |
| 3 | 代码示例 | 🔴 必须 | >=1 个代码块 |
| 4 | 语言标注 | 🟡 建议 | python/bash 等 |
| 5 | 标题层级 | 🔴 必须 | >=2 个 ## |
| 6 | 段落间距 | 🟡 建议 | 空行分隔 |
| 7 | 互动结尾 | 🟡 建议 | 点赞/收藏引导 |
| 8 | 表情符号 | ⚪ 可选 | 2-15 个 |
| 9 | 加粗强调 | 🟡 建议 | >=3 处 |
| 10 | 参考资料 | 🟡 建议 | GitHub/原文链接 |
| 11 | 文章长度 | 🔴 必须 | >=800 字 |
| 12 | 人称视角 | 🟡 建议 | 第一/第二人称 |
| 13 | 过渡连接 | ⚪ 可选 | 首先/接下来等 |

### 通过标准：
- ✅ 总分 >= 70 分
- ✅ 所有"必须"项全部通过
- ✅ 文章长度 >= 800 字

### 分数等级：
- **90-100分** ✨ 优秀 - 可直接发布
- **75-89分** 👍 良好 - 小幅调整即可
- **60-74分** ✅ 合格 - 有明显改进空间
- **<60分** ❌ 需改进 - 必须修改

---

## 📁 文件命名规范

### 输入文件 (`input/`):

```bash
# 原始文本
input/raw/pyd_packer_original.txt      # 原始文本
input/raw/docker_tutorial_original.md  # 原始 Markdown

# URL 记录（统一写入此文件）
input/raw/url_registry.md              # 所有链接的登记表

# 分析结果
input/processed/pyd_packer_analyzed.md # 结构化分析数据
```

### 输出文件 (`output/`):

```bash
# 改写后的文章
output/articles/python_data_processing.md   # 文章成品
output/articles/docker_quick_start.md       # 文章成品

# 质量报告（自动生成）
output/reports/python_data_processing_report.txt  # 对应报告
output/reports/docker_quick_start_report.txt      # 对应报告
```

**命名规则**：
- 使用英文小写 + 下划线
- 简洁反映主题内容
- 报告名添加 `_report` 后缀

---

## ⚙️ 配置自定义

编辑 `config/project_config.json` 可调整：

```json
{
  "validation": {
    "min_score_required": 70,        // 最低分数要求（可调高/低）
    "required_checks_passed": true,  // 是否要求必选项全过
    "auto_validate_after_rewrite": true  // 改写后是否自动验证
  },
  "paths": {
    // 各类文件存储路径（一般不需修改）
  }
}
```

---

## 🎨 模板定制

编辑 `templates/csdn_article_template.md` 可修改默认的文章结构模板。

**常用调整**：
- 修改标题公式
- 调整章节顺序
- 自定义互动结尾语
- 添加特殊格式要求

---

## 📚 相关文档

| 文档 | 路径 | 说明 |
|------|------|------|
| **Agent 技能定义** | `.trae/skills/csdn-writer/SKILL.md` | 触发条件、工作流程、脚本关联 |
| **AI 使用指南** | `docs/AI_INSTRUCTIONS.md` | 详细操作指引、最佳实践、异常处理 |
| **文章模板** | `templates/csdn_article_template.md` | CSDN 文章标准格式参考 |
| **项目配置** | `config/project_config.json` | 参数设置和路径配置 |

---

## 💡 最佳实践建议

### 对于使用者（你）：

1. **明确需求**
   - 提供具体的改写方向或偏好
   - 说明目标受众（初学者/进阶者）
   - 标注需要保留或修改的部分

2. **提供高质量输入**
   - 内容越完整，改写效果越好
   - 包含代码示例会提升最终质量
   - 提供背景信息有助于理解上下文

3. **利用反馈循环**
   - 查看质量报告中的改进建议
   - 可以要求 AI 进行多轮优化
   - 保存满意的版本作为参考

### 对于开发者（扩展功能）：

1. **添加新的检测项**
   - 编辑 `scripts/csdn_validator.py`
   - 在 `CSDNStyleValidator` 类中添加新方法
   - 在 `_generate_summary()` 中注册

2. **支持更多输入格式**
   - 在 SKILL.md 的"支持的输入格式"部分扩展
   - 编写对应的解析器
   - 更新 `input/processed/` 的处理逻辑

3. **集成外部服务**
   - 接入 CSDN API 实现自动发布
   - 连接翻译服务支持多语言
   - 整成图片处理服务自动配图

---

## ❓ 常见问题

### Q1: 改写后的文章可以直接发布吗？
**A**: 如果质量检测 >= 90 分且所有必选项通过，可以直接发布。建议人工审核一遍技术准确性。

### Q2: 如何批量处理多篇文章？
**A**: 目前需逐篇处理。可在 `input/raw/url_registry.md` 中列出多个链接，然后依次调用技能。

### Q3: 可以自定义 CSDN 风格吗？
**A**: 可以！编辑 `templates/csdn_article_template.md` 和 `docs/AI_INSTRUCTIONS.md` 中的风格特征库。

### Q4: 验证不通过怎么办？
**A**: AI 会根据检测报告自动改进。你也可以查看 `output/reports/` 中的具体建议手动调整。

### Q5: 如何保护我的原始内容安全？
**A**: 所有输入都保存在本地 `input/` 目录，不会上传到外部服务器。

---

## 🔄 版本更新日志

### v1.1 (2026-05-28) - 结构优化版
- ✅ 新增标准化目录结构
- ✅ 实现输入/输出分类归档
- ✅ 集成质量验证脚本
- ✅ 创建完整的 AI 使用指南
- ✅ 添加项目配置管理
- ✅ 提供标准文章模板

### v1.0 (2026-05-28) - 初始版本
- ✅ 基础改写能力
- ✅ CSDN 风格识别
- ✅ 简单的质量检查

---

## 📞 技术支持

如遇到问题：

1. 查看 `docs/AI_INSTRUCTIONS.md` 详细指南
2. 检查 `output/reports/` 中的错误日志
3. 确认 `config/project_config.json` 配置正确
4. 验证 Python 环境（需要 Python 3.7+）

---

## 📄 许可证

本项目仅供学习和研究使用。使用时请遵守相关平台的版权规定。

---

**🎉 开始使用 CSDN AI Writer，让你的技术文章更专业、更有吸引力！**
