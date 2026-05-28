import os
import re
import sys
import io

# 设置 UTF-8 编码输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

files = {
    'requests v1.1': 'input/raw/test_code_article_requests.md',
    'Playwright': 'input/raw/test_code_article_playwright.md'
}

print("=" * 60)
print("📊 CSDN 文章抓取对比分析报告")
print("测试文章: Python爬取6000篇文章分析CSDN (含代码)")
print("=" * 60)

for name, path in files.items():
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            chars = len(content)
            line_count = len(lines)
            
            # 统计代码块
            code_blocks = content.count('```') // 2
            
            # 统计图片
            images = len(re.findall(r'!\[.*?\]\(.*?\)', content))
            
            # 统计链接
            links = len(re.findall(r'\[.*?\]\(.*?\)', content))
            
            # 检测重复行
            seen = set()
            duplicates = 0
            for line in lines:
                stripped = line.strip()
                if stripped and stripped in seen:
                    duplicates += 1
                seen.add(stripped)
            
            print(f"\n{'='*60}")
            print(f"📌 {name}")
            print(f"{'='*60}")
            print(f"✅ 总字符数: {chars:,} 字符")
            print(f"📏 总行数: {line_count} 行")
            print(f"💻 代码块: {code_blocks} 个")
            print(f"🖼️  图片: {images} 张")
            print(f"🔗 链接: {links} 个")
            print(f"⚠️  重复行: {duplicates} 行")

print("\n" + "=" * 60)
