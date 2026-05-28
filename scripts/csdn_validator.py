#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSDN 文章质量检测与约束工具
用于验证改写后的文章是否符合 CSDN 行文风格规范
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Tuple
from enum import Enum


class CheckLevel(Enum):
    """检查级别"""
    REQUIRED = "required"      # 必须满足
    RECOMMENDED = "recommended"  # 建议满足
    OPTIONAL = "optional"      # 可选


@dataclass
class CheckResult:
    """单项检查结果"""
    name: str
    passed: bool
    level: CheckLevel
    message: str
    suggestion: str = ""


@dataclass
class QualityReport:
    """质量报告"""
    total_score: float
    max_score: float
    results: List[CheckResult]
    summary: str


class CSDNStyleValidator:
    """CSDN 风格验证器"""

    def __init__(self):
        self.checks = [
            self._check_title_format,
            self._check_has_introduction,
            self._check_has_code_blocks,
            self._check_code_block_language,
            self._check_heading_hierarchy,
            self._check_paragraph_spacing,
            self._check_interactive_ending,
            self._check_emoji_usage,
            self._check_bold_emphasis,
            self._check_reference_section,
            self._check_length_requirement,
            self._check_personal_pronoun,
            self._check_transition_words,
        ]

    def validate(self, content: str) -> QualityReport:
        """
        执行完整验证

        Args:
            content: 待验证的 Markdown 内容

        Returns:
            QualityReport: 包含详细检查结果的质量报告
        """
        results = []
        total_score = 0
        max_score = 0

        for check_func in self.checks:
            result = check_func(content)
            results.append(result)

            # 计分逻辑
            if result.level == CheckLevel.REQUIRED:
                weight = 10
            elif result.level == CheckLevel.RECOMMENDED:
                weight = 5
            else:
                weight = 2

            max_score += weight
            if result.passed:
                total_score += weight

        final_score = (total_score / max_score * 100) if max_score > 0 else 0
        summary = self._generate_summary(results, final_score)

        return QualityReport(
            total_score=final_score,
            max_score=100.0,
            results=results,
            summary=summary
        )

    def _check_title_format(self, content: str) -> CheckResult:
        """检查标题格式（必须以 # 开头）"""
        lines = content.split('\n')
        has_title = False
        title_line = ""

        for line in lines[:10]:  # 只检查前10行
            if line.startswith('# '):
                has_title = True
                title_line = line
                break

        if has_title and len(title_line.strip()) > 5:
            return CheckResult(
                name="标题格式",
                passed=True,
                level=CheckLevel.REQUIRED,
                message="✅ 标题格式正确",
                suggestion=""
            )
        else:
            return CheckResult(
                name="标题格式",
                passed=False,
                level=CheckLevel.REQUIRED,
                message="❌ 缺少或标题过短",
                suggestion="文章应以 '# 标题' 开头，且长度建议大于5个字符"
            )

    def _check_has_introduction(self, content: str) -> CheckResult:
        """检查是否有引入段落"""
        intro_patterns = [
            r'大家好',
            r'在日常',
            r'今天.*分享',
            r'本文将',
            r'我们经常'
        ]

        # 检查前500字符
        intro_section = content[:500]
        found = any(re.search(pattern, intro_section) for pattern in intro_patterns)

        return CheckResult(
            name="引入段落",
            passed=found,
            level=CheckLevel.REQUIRED,
            message="✅ 包含场景化引入" if found else "❌ 缺少引入段落",
            suggestion="建议在开头添加场景化描述，如'大家好！在日常开发中...'"
        )

    def _check_has_code_blocks(self, content: str) -> CheckResult:
        """检查是否包含代码块"""
        code_blocks = re.findall(r'```[\s\S]*?```', content)

        if len(code_blocks) >= 1:
            return CheckResult(
                name="代码示例",
                passed=True,
                level=CheckLevel.REQUIRED,
                message=f"✅ 包含 {len(code_blocks)} 个代码块",
                suggestion=""
            )
        else:
            return CheckResult(
                name="代码示例",
                passed=False,
                level=CheckLevel.REQUIRED,
                message="❌ 未发现代码块",
                suggestion="技术文章应包含至少一个代码示例（使用 ``` 包裹）"
            )

    def _check_code_block_language(self, content: str) -> CheckResult:
        """检查代码块是否标注语言类型"""
        code_blocks = re.findall(r'```(\w*)', content)
        labeled_blocks = [lang for lang in code_blocks if lang and lang.lower() not in ['', 'text']]

        if len(labeled_blocks) > 0 or len(code_blocks) == 0:
            return CheckResult(
                name="代码语言标注",
                passed=True,
                level=CheckLevel.RECOMMENDED,
                message="✅ 代码块已标注语言" if len(labeled_blocks) > 0 else "ℹ️ 无代码块",
                suggestion=""
            )
        else:
            return CheckResult(
                name="代码语言标注",
                passed=False,
                level=CheckLevel.RECOMMENDED,
                message="⚠️ 代码块未标注语言",
                suggestion="建议使用 ```python、```bash 等标注语言类型"
            )

    def _check_heading_hierarchy(self, content: str) -> CheckResult:
        """检查标题层级结构"""
        h2_count = len(re.findall(r'^## ', content, re.MULTILINE))
        h3_count = len(re.findall(r'^### ', content, re.MULTILINE))

        if h2_count >= 2:
            return CheckResult(
                name="标题层级",
                passed=True,
                level=CheckLevel.REQUIRED,
                message=f"✅ 包含 {h2_count} 个二级标题，{h3_count} 个三级标题",
                suggestion=""
            )
        else:
            return CheckResult(
                name="标题层级",
                passed=False,
                level=CheckLevel.REQUIRED,
                message="❌ 标题层级不足",
                suggestion="建议使用 ## 和 ### 组织内容，至少包含2个二级标题"
            )

    def _check_paragraph_spacing(self, content: str) -> CheckResult:
        """检查段落间距"""
        # 检查是否有空行分隔段落
        paragraphs = re.split(r'\n\s*\n', content)
        well_spaced = len(paragraphs) >= 3

        return CheckResult(
            name="段落间距",
            passed=well_spaced,
            level=CheckLevel.RECOMMENDED,
            message="✅ 段落间距合理" if well_spaced else "⚠️ 段落过于密集",
            suggestion="使用空行分隔不同段落，提高可读性"
        )

    def _check_interactive_ending(self, content: str) -> CheckResult:
        """检查是否有互动结尾"""
        ending_patterns = [
            r'点赞',
            r'收藏',
            r'关注',
            r'评论',
            r'留言',
            r'交流',
            r'欢迎.*提问',
            r'有问题.*评论'
        ]

        last_section = content[-500:]  # 检查最后500字符
        found = any(re.search(pattern, last_section) for pattern in ending_patterns)

        return CheckResult(
            name="互动结尾",
            passed=found,
            level=CheckLevel.RECOMMENDED,
            message="✅ 包含互动引导" if found else "⚠️ 缺少互动结尾",
            suggestion="建议在结尾添加'点赞、收藏、关注'等互动引导语"
        )

    def _check_emoji_usage(self, content: str) -> CheckResult:
        """检查表情符号使用（适度使用）"""
        emoji_pattern = re.compile(r'[^\x00-\x7F]+')
        emojis = emoji_pattern.findall(content)
        emoji_count = sum(1 for e in emojis if any(ord(c) > 127 for c in e))

        if 2 <= emoji_count <= 15:
            return CheckResult(
                name="表情符号",
                passed=True,
                level=CheckLevel.OPTIONAL,
                message=f"✅ 表情符号使用适度（{emoji_count}个）",
                suggestion=""
            )
        elif emoji_count < 2:
            return CheckResult(
                name="表情符号",
                passed=False,
                level=CheckLevel.OPTIONAL,
                message="ℹ️ 表情符号较少",
                suggestion="CSDN风格文章常使用适量表情符号增强亲和力"
            )
        else:
            return CheckResult(
                name="表情符号",
                passed=False,
                level=CheckLevel.OPTIONAL,
                message="⚠️ 表情符号过多",
                suggestion="避免过度使用表情符号，保持专业性"
            )

    def _check_bold_emphasis(self, content: str) -> CheckResult:
        """检查加粗强调"""
        bold_count = len(re.findall(r'\*\*[^*]+\*\*', content))

        if bold_count >= 3:
            return CheckResult(
                name="加粗强调",
                passed=True,
                level=CheckLevel.RECOMMENDED,
                message=f"✅ 使用了 {bold_count} 处加粗强调",
                suggestion=""
            )
        else:
            return CheckResult(
                name="加粗强调",
                passed=False,
                level=CheckLevel.RECOMMENDED,
                message="⚠️ 加粗强调不足",
                suggestion="重要术语和关键信息建议使用 **加粗** 强调"
            )

    def _check_reference_section(self, content: str) -> CheckResult:
        """检查参考资料部分"""
        ref_patterns = [
            r'参考[资料资源]',
            r'相关链接',
            r'延伸阅读',
            r'GitHub',
            r'原文链接'
        ]

        last_part = content[-800:]
        found = any(re.search(pattern, last_part, re.IGNORECASE) for pattern in ref_patterns)

        return CheckResult(
            name="参考资料",
            passed=found,
            level=CheckLevel.RECOMMENDED,
            message="✅ 包含参考资源" if found else "⚠️ 缺少参考资料",
            suggestion="建议在文末添加 GitHub 链接、原文出处等参考信息"
        )

    def _check_length_requirement(self, content: str) -> CheckResult:
        """检查文章长度"""
        word_count = len(content.replace(' ', '').replace('\n', ''))

        if word_count >= 1500:
            return CheckResult(
                name="文章长度",
                passed=True,
                level=CheckLevel.REQUIRED,
                message=f"✅ 文章长度适宜（约{word_count}字）",
                suggestion=""
            )
        elif word_count >= 800:
            return CheckResult(
                name="文章长度",
                passed=True,
                level=CheckLevel.REQUIRED,
                message=f"✅ 文章长度达标（约{word_count}字）",
                suggestion="可以适当扩充内容使其更丰富"
            )
        else:
            return CheckResult(
                name="文章长度",
                passed=False,
                level=CheckLevel.REQUIRED,
                message="❌ 文章过短",
                suggestion="CSDN技术文章建议至少800字，当前仅{word_count}字"
            )

    def _check_personal_pronoun(self, content: str) -> CheckResult:
        """检查人称代词使用"""
        pronouns = ['我们', '你', '大家', '我']
        found = sum(1 for p in pronouns if p in content)

        if found >= 2:
            return CheckResult(
                name="人称视角",
                passed=True,
                level=CheckLevel.RECOMMENDED,
                message=f"✅ 使用了亲切的人称表达",
                suggestion=""
            )
        else:
            return CheckResult(
                name="人称视角",
                passed=False,
                level=CheckLevel.RECOMMENDED,
                message="⚠️ 缺少人称化表达",
                suggestion="建议使用第一/第二人称（如'我们'、'你'）增强亲和力"
            )

    def _check_transition_words(self, content: str) -> CheckResult:
        """检查过渡词使用"""
        transitions = ['首先', '然后', '接下来', '最后', '此外', '总之', '总的来说']
        found = sum(1 for t in transitions if t in content)

        if found >= 2:
            return CheckResult(
                name="过渡连接",
                passed=True,
                level=CheckLevel.OPTIONAL,
                message=f"✅ 过渡词使用自然",
                suggestion=""
            )
        else:
            return CheckResult(
                name="过渡连接",
                passed=False,
                level=CheckLevel.OPTIONAL,
                message="ℹ️ 可增加过渡词",
                suggestion="使用'首先'、'接下来'、'最后'等增强流畅度"
            )

    def _generate_summary(self, results: List[CheckResult], score: float) -> str:
        """生成总结报告"""
        required_passed = sum(1 for r in results if r.level == CheckLevel.REQUIRED and r.passed)
        required_total = sum(1 for r in results if r.level == CheckLevel.REQUIRED)

        if score >= 90:
            quality = "优秀 ✨"
        elif score >= 75:
            quality = "良好 👍"
        elif score >= 60:
            quality = "合格 ✅"
        else:
            quality = "需改进 ⚠️"

        summary = f"""
{'='*60}
📊 CSDN 文章质量检测报告
{'='*60}

总体评分：{score:.1f}/100 ({quality})
必选项通过：{required_passed}/{required_total}

详细检测结果：
{'-'*60}
"""

        for i, result in enumerate(results, 1):
            level_icon = {
                CheckLevel.REQUIRED: "🔴",
                CheckLevel.RECOMMENDED: "🟡",
                CheckLevel.OPTIONAL: "⚪"
            }
            icon = level_icon[result.level]
            summary += f"{i}. [{icon}] {result.name}: {result.message}\n"
            if not result.passed and result.suggestion:
                summary += f"   💡 建议：{result.suggestion}\n"

        summary += f"\n{'='*60}\n"

        return summary


def validate_csdn_article(content: str, verbose: bool = True) -> Tuple[bool, QualityReport]:
    """
    主函数：验证 CSDN 文章质量

    Args:
        content: Markdown 格式的文章内容
        verbose: 是否输出详细信息

    Returns:
        Tuple[bool, QualityReport]: (是否通过, 详细报告)
    """
    validator = CSDNStyleValidator()
    report = validator.validate(content)

    if verbose:
        print(report.summary)

    # 判断是否通过：必选项全部通过且总分>=70
    required_all_pass = all(
        r.passed for r in report.results if r.level == CheckLevel.REQUIRED
    )
    is_valid = required_all_pass and report.total_score >= 70

    return is_valid, report


# 示例用法
if __name__ == "__main__":
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # 测试用例
    test_content = """
# 测试文章标题

大家好！今天我们来学习 Python 编程。

## 第一步：安装环境

首先，我们需要安装 Python：

```python
print("Hello, World!")
```

是不是很简单？

## 第二步：编写代码

接下来，让我们写第一个程序...

## 总结

总的来说，Python 是一门很好的语言。

---
觉得有用的话，记得点赞关注哦！
"""

    print("开始验证文章质量...\n")
    is_valid, report = validate_csdn_article(test_content)

    if is_valid:
        print("\n✅ 文章符合 CSDN 发布标准！")
    else:
        print("\n⚠️ 文章需要改进后才能发布")
