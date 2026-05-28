#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证改写后的 CSDN 文章质量
使用方法：python scripts/test_quality.py
或：python scripts/test_quality.py output/articles/xxx.md
"""

import sys
import os
import io
from pathlib import Path

# 添加 scripts 目录到路径（用于导入 csdn_validator）
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from csdn_validator import validate_csdn_article

# 设置 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 项目根目录
PROJECT_ROOT = script_dir.parent

def main():
    print("=" * 70)
    print("🔍 CSDN 文章改写质量检测工具")
    print("=" * 70)
    print()

    # 确定要检测的文件
    if len(sys.argv) > 1:
        # 使用命令行参数指定的文件
        article_path = sys.argv[1]
    else:
        # 默认读取 output/articles/ 目录下的第一个 .md 文件
        articles_dir = PROJECT_ROOT / 'output' / 'articles'
        md_files = list(articles_dir.glob('*.md'))

        if not md_files:
            print(f"❌ 在 {articles_dir} 目录下未找到 Markdown 文件")
            print("   请将要检测的文件放入该目录，或通过命令行指定文件路径")
            print(f"\n   用法: python {sys.argv[0]} <文章文件路径>")
            return

        article_path = str(md_files[0])

    # 读取改写后的文章
    try:
        with open(article_path, 'r', encoding='utf-8') as f:
            article_content = f.read()
        print(f"✅ 成功读取文章: {os.path.basename(article_path)}")
        print(f"   文件大小: {len(article_content)} 字符")
        print()
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return

    # 执行验证
    print("📊 开始执行质量检测...\n")
    is_valid, report = validate_csdn_article(article_content)

    # 输出详细报告
    print("\n" + "=" * 70)
    print("📋 详细检测结果")
    print("=" * 70 + "\n")

    for i, result in enumerate(report.results, 1):
        status_icon = "✅" if result.passed else "❌"
        level_text = {
            "required": "【必须】",
            "recommended": "【建议】",
            "optional": "【可选】"
        }
        level = level_text.get(result.level.value, "")

        print(f"{i:2d}. {status_icon} {level} {result.name}")
        print(f"    {result.message}")

        if not result.passed and result.suggestion:
            print(f"    💡 {result.suggestion}")

        print()

    # 最终结论
    print("=" * 70)
    print("🎯 最终评估")
    print("=" * 70)

    required_passed = sum(1 for r in report.results
                         if r.level.value == "required" and r.passed)
    required_total = sum(1 for r in report.results
                        if r.level.value == "required")

    recommended_passed = sum(1 for r in report.results
                           if r.level.value == "recommended" and r.passed)
    recommended_total = sum(1 for r in report.results
                          if r.level.value == "recommended")

    print(f"\n📈 总体评分：{report.total_score:.1f}/100")
    print(f"✅ 必选项通过率：{required_passed}/{required_total} ({required_passed/required_total*100:.0f}%)" if required_total > 0 else "")
    print(f"💡 建议项通过率：{recommended_passed}/{recommended_total} ({recommended_passed/recommended_total*100:.0f}%)" if recommended_total > 0 else "")

    if is_valid:
        print("\n🎉 恭喜！文章符合 CSDN 发布标准！✨")
        print("   可以直接发布到 CSDN 平台！")
    else:
        print("\n⚠️  文章需要进一步优化")
        print("   请根据上述建议进行修改后重新检测")

    # 保存报告到文件
    report_dir = PROJECT_ROOT / 'output' / 'reports'
    report_path = report_dir / f"{Path(article_path).stem}_report.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report.summary)
        f.write(f"\n\n最终结果: {'通过 ✅' if is_valid else '未通过 ❌'}\n")

    print(f"\n📄 完整报告已保存至: {report_path}")
    print()

if __name__ == "__main__":
    main()
