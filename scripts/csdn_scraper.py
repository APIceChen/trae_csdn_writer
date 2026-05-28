#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSDN 文章原始内容爬虫
====================
功能：
1. 通过 URL 抓取 CSDN 文章的完整原始内容
2. 保留 Markdown 格式、代码块、表格等所有细节
3. 支持多种抓取策略（Playwright / requests）
4. 自动清洗和格式化输出

使用方式：
    python scripts/csdn_scraper.py <URL> [output_file]

示例：
    python scripts/csdn_scraper.py https://blog.csdn.net/xxx/article/details/12345678
    python scripts/csdn_scraper.py https://blog.csdn.net/xxx/article/details/12345678 output.md

作者：CSDN AI Writer Agent v1.2
版本：v1.0 (2026-05-28)
"""

import sys
import os
import re
import json
import time
import logging
import io
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# 设置 UTF-8 编码输出（解决 Windows GBK 编码问题）
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import requests
    from bs4 import BeautifulSoup
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  警告: 未安装 requests 和 beautifulsoup4，将仅使用 Playwright 模式")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CSDNScraper:
    """CSDN 文章爬虫类"""

    def __init__(self, timeout: int = 30, retry_times: int = 3):
        """
        初始化爬虫

        Args:
            timeout: 请求超时时间（秒）
            retry_times: 失败重试次数
        """
        self.timeout = timeout
        self.retry_times = retry_times
        self.session = None

        # CSDN 相关配置
        self.csdn_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            self.session.headers.update(self.csdn_headers)

    def validate_url(self, url: str) -> bool:
        """
        验证 URL 是否是有效的 CSDN 文章链接

        Args:
            url: 待验证的 URL

        Returns:
            bool: 是否是有效的 CSDN 文章 URL
        """
        # 支持两种格式：
        # 1. 标准格式: https://blog.csdn.net/<author>/article/details/<id>
        # 2. 子域名格式: https://<author>.blog.csdn.net/article/details/<id>
        pattern = r'^https?://(\w+\.)*csdn\.net/.*article/details/\d+'
        return bool(re.match(pattern, url))

    def extract_article_id(self, url: str) -> Optional[str]:
        """
        从 URL 中提取文章 ID

        Args:
            url: CSDN 文章 URL

        Returns:
            str or None: 文章 ID
        """
        match = re.search(r'/article/details/(\d+)', url)
        return match.group(1) if match else None

    def scrape_with_requests(self, url: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        使用 requests + BeautifulSoup 抓取文章（快速模式）

        Args:
            url: CSDN 文章 URL

        Returns:
            tuple: (markdown_content, metadata) 或 None
        """
        if not REQUESTS_AVAILABLE:
            logger.error("❌ requests 库未安装，无法使用此方法")
            return None

        logger.info(f"📡 使用 requests 模式抓取: {url}")

        for attempt in range(self.retry_times):
            try:
                # 发送请求
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                response.encoding = 'utf-8'

                # 解析 HTML
                soup = BeautifulSoup(response.text, 'html.parser')

                # 提取文章标题
                title_tag = soup.find('h1', class_='title-article')
                title = title_tag.get_text(strip=True) if title_tag else "未知标题"

                # 提取作者信息（多策略 fallback）
                author = self.extract_author(soup, url)

                # 提取发布时间
                time_tag = soup.find('span', class_='time')
                publish_time = time_tag.get_text(strip=True) if time_tag else ""

                # 提取文章正文（核心部分）
                article_content = soup.find('div', id='content_views') or \
                                 soup.find('div', class_='article-content')

                if not article_content:
                    logger.warning(f"⚠️  未找到文章正文内容，尝试备用选择器...")
                    article_content = soup.find('article') or soup.find('div', class_='htmledit_views')

                if not article_content:
                    logger.error(f"❌ 无法提取文章正文，页面结构可能已变化")
                    return None

                # 将 HTML 转换为 Markdown
                markdown_content = self.html_to_markdown(article_content)

                # 去重处理（CSDN 页面可能有重复内容）
                markdown_content = self.remove_duplicate_content(markdown_content)

                # 构建元数据
                metadata = {
                    'title': title,
                    'author': author,
                    'publish_time': publish_time,
                    'url': url,
                    'article_id': self.extract_article_id(url),
                    'scrape_method': 'requests+BeautifulSoup',
                    'scrape_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'word_count': len(markdown_content),
                    'has_code_blocks': bool(re.search(r'```', markdown_content)),
                    'has_tables': bool(re.search(r'\|.*\|', markdown_content)),
                    'has_images': bool(re.search(r'!\[.*\]\(.*\)', markdown_content)),
                }

                logger.info(f"✅ requests 模式抓取成功")
                logger.info(f"   标题: {title}")
                logger.info(f"   作者: {author}")
                logger.info(f"   字数: {metadata['word_count']}")

                return markdown_content, metadata

            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️  第 {attempt + 1} 次请求失败: {str(e)}")
                if attempt < self.retry_times - 1:
                    wait_time = (attempt + 1) * 2
                    logger.info(f"⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)

        logger.error(f"❌ requests 模式失败，已达到最大重试次数")
        return None

    def html_to_markdown(self, element) -> str:
        """
        将 HTML 元素转换为 Markdown 格式

        Args:
            element: BeautifulSoup 元素

        Returns:
            str: Markdown 格式的文本
        """
        markdown_lines = []

        for child in element.descendants:
            if child.name is None:
                # 文本节点
                text = child.strip()
                if text:
                    markdown_lines.append(text)
            elif child.name == 'h1':
                text = child.get_text(strip=True)
                if text and not any(text in line for line in markdown_lines):
                    markdown_lines.append(f"\n# {text}\n")
            elif child.name == 'h2':
                text = child.get_text(strip=True)
                if text:
                    markdown_lines.append(f"\n## {text}\n")
            elif child.name == 'h3':
                text = child.get_text(strip=True)
                if text:
                    markdown_lines.append(f"\n### {text}\n")
            elif child.name == 'p':
                # 段落文本会在上面的文本节点处理，这里只添加空行
                pass
            elif child.name == 'pre':
                # 代码块
                code = child.get_text()
                language = ""
                code_class = child.get('class', [])
                if code_class:
                    for cls in code_class:
                        if cls.startswith('language-'):
                            language = cls.replace('language-', '')
                            break
                        elif cls.startswith('lang-'):
                            language = cls.replace('lang-', '')
                            break
                markdown_lines.append(f"\n```{language}\n{code}\n```\n")
            elif child.name == 'code' and child.parent.name != 'pre':
                # 行内代码
                code = child.get_text()
                markdown_lines.append(f"`{code}`")
            elif child.name == 'strong' or child.name == 'b':
                text = child.get_text(strip=True)
                if text:
                    markdown_lines.append(f"**{text}**")
            elif child.name == 'em' or child.name == 'i':
                text = child.get_text(strip=True)
                if text:
                    markdown_lines.append(f"*{text}*")
            elif child.name == 'a':
                href = child.get('href', '')
                text = child.get_text(strip=True)
                if text and href:
                    markdown_lines.append(f"[{text}]({href})")
                elif text:
                    markdown_lines.append(text)
            elif child.name == 'img':
                src = child.get('src', '')
                alt = child.get('alt', '')
                if src:
                    markdown_lines.append(f"![{alt}]({src})")
            elif child.name == 'ul':
                markdown_lines.append("")  # 无序列表开始
            elif child.name == 'li' and child.parent.name == 'ul':
                text = child.get_text(strip=True)
                if text:
                    markdown_lines.append(f"- {text}")
            elif child.name == 'ol':
                markdown_lines.append("")  # 有序列表开始
            elif child.name == 'li' and child.parent.name == 'ol':
                text = child.get_text(strip=True)
                if text:
                    markdown_lines.append(f"1. {text}")
            elif child.name == 'blockquote':
                text = child.get_text(strip=True)
                if text:
                    markdown_lines.append(f"> {text}")
            elif child.name == 'table':
                # 表格处理
                table_md = self.table_to_markdown(child)
                if table_md:
                    markdown_lines.append(f"\n{table_md}\n")
            elif child.name == 'br':
                markdown_lines.append("\n")

        # 合并并清理
        result = '\n'.join(markdown_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)  # 多余空行合并
        result = result.strip()

        return result

    def table_to_markdown(self, table_element) -> str:
        """
        将 HTML 表格转换为 Markdown 表格

        Args:
            table_element: BeautifulSoup table 元素

        Returns:
            str: Markdown 表格
        """
        rows = []
        headers = []

        thead = table_element.find('thead')
        if thead:
            header_cells = thead.find_all(['th', 'td'])
            headers = [cell.get_text(strip=True) for cell in header_cells]

        tbody = table_element.find('tbody')
        if tbody:
            for row in tbody.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                rows.append(row_data)
        else:
            for row in table_element.find_all('tr')[1:]:  # 跳过表头行
                cells = row.find_all(['td', 'th'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                rows.append(row_data)

        if not headers and rows:
            headers = rows.pop(0)  # 第一行作为表头

        if not headers:
            return ""

        # 构建 Markdown 表格
        md_lines = []
        md_lines.append('| ' + ' | '.join(headers) + ' |')
        md_lines.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')

        for row in rows:
            while len(row) < len(headers):
                row.append('')
            md_lines.append('| ' + ' | '.join(row) + ' |')

        return '\n'.join(md_lines)

    def remove_duplicate_content(self, text: str) -> str:
        """
        去除重复的内容（CSDN 页面结构导致的重复）

        Args:
            text: 可能包含重复内容的文本

        Returns:
            str: 去重后的文本
        """
        lines = text.split('\n')
        cleaned_lines = []
        seen_lines = set()
        prev_line = ""

        for line in lines:
            stripped = line.strip()

            # 跳过空行
            if not stripped:
                if prev_line:  # 保留第一个空行
                    cleaned_lines.append(line)
                    prev_line = ""
                continue

            # 检查是否是重复行（忽略空格差异）
            normalized = re.sub(r'\s+', ' ', stripped)

            # 🔥 新增：检测紧邻的完全相同行（最常见的情况）
            # 先标准化：移除常见的列表标记 (-, *, 1. 等)
            prev_normalized_clean = re.sub(r'^[-*•\d.\s]+', '', prev_line.strip()) if prev_line else ""
            current_normalized_clean = re.sub(r'^[-*•\d.\s]+', '', stripped)

            if current_normalized_clean and current_normalized_clean == prev_normalized_clean:
                logger.debug(f"🗑️  移除重复行: {stripped}")
                continue

            # 如果这行内容与上一行非常相似（>80%相同），则跳过
            if prev_line and self.similarity(normalized, prev_line) > 0.8:
                continue

            # 如果这行内容已经出现过（完全相同），且不是代码块，则跳过
            if normalized in seen_lines and not stripped.startswith('```'):
                continue

            seen_lines.add(normalized)
            cleaned_lines.append(line)
            prev_line = normalized

        result = '\n'.join(cleaned_lines)
        result = re.sub(r'\n{3,}', '\n\n', result)  # 多余空行合并
        return result.strip()

    def similarity(self, str1: str, str2: str) -> float:
        """
        计算两个字符串的相似度（简单的字符重叠率）

        Args:
            str1: 字符串1
            str2: 字符串2

        Returns:
            float: 相似度 (0-1)
        """
        if not str1 or not str2:
            return 0.0

        # 简单的字符级别 Jaccard 相似度
        set1 = set(str1.lower())
        set2 = set(str2.lower())

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0

    def extract_author(self, soup, url: str) -> str:
        """
        多策略提取作者信息（增强版）

        Args:
            soup: BeautifulSoup 对象
            url: 文章 URL

        Returns:
            str: 作者名称，如果无法提取则返回 "未知作者"
        """
        from urllib.parse import urlparse

        # 策略 1: 原有方式 - 从 follow-nickName 类名提取（最准确）
        author_tag = soup.find('a', class_='follow-nickName')
        if author_tag:
            author = author_tag.get_text(strip=True)
            if author and author != "未知作者":
                logger.debug(f"✅ 作者信息（策略1-类名）: {author}")
                return author

        # 策略 2: 从 URL 路径提取（CSDN 标准格式）
        try:
            parsed_url = urlparse(url)
            path_parts = [p for p in parsed_url.path.split('/') if p]

            # URL 格式: /author_name/article/details/xxxxx
            if len(path_parts) >= 2 and path_parts[1] == 'article':
                author_from_url = path_parts[0]
                if author_from_url and not author_from_url.startswith('article'):
                    logger.debug(f"✅ 作者信息（策略2-URL）: {author_from_url}")
                    return author_from_url
        except Exception as e:
            logger.debug(f"策略2失败: {e}")

        # 策略 3: 从正文开头提取（格式："整理 | 作者名" 或 "作者 | CSDN"）
        try:
            article_content = soup.find('div', id='content_views') or \
                             soup.find('div', class_='article-content')
            if article_content:
                first_para = article_content.find('p')
                if first_para:
                    text = first_para.get_text()
                    # 匹配 "整理 | 作者名" 或 "作者名 | CSDN"
                    match = re.search(r'整理\s*[｜|]\s*(\S+)', text)
                    if match:
                        author = match.group(1)
                        logger.debug(f"✅ 作者信息（策略3-正文）: {author}")
                        return author

                    # 匹配 "出品 | CSDN（ID：xxx）"
                    match = re.search(r'ID[：:]\s*(\w+)', text)
                    if match:
                        author = match.group(1)
                        logger.debug(f"✅ 作者信息（策略3-正文ID）: {author}")
                        return author
        except Exception as e:
            logger.debug(f"策略3失败: {e}")

        # 策略 4: 从 meta 标签提取
        try:
            meta_author = soup.find('meta', attrs={'name': 'author'})
            if meta_author and meta_author.get('content'):
                author = meta_author['content'].strip()
                if author:
                    logger.debug(f"✅ 作者信息（策略4-meta）: {author}")
                    return author
        except Exception as e:
            logger.debug(f"策略4失败: {e}")

        # 策略 5: 备用选择器
        try:
            # 尝试其他可能的类名
            for class_name in ['nickname', 'username', 'user-name']:
                tag = soup.find('a', class_=class_name)
                if tag:
                    author = tag.get_text(strip=True)
                    if author:
                        logger.debug(f"✅ 作者信息（策略5-{class_name}）: {author}")
                        return author
        except Exception as e:
            logger.debug(f"策略5失败: {e}")

        # 所有策略都失败
        logger.warning("⚠️  无法提取作者信息，所有策略均失败")
        return "未知作者"

    async def scrape_with_playwright(self, url: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        使用 Playwright 抓取文章（完整模式）

        Args:
            url: CSDN 文章 URL

        Returns:
            tuple: (markdown_content, metadata) 或 None
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("❌ playwright 库未安装，请运行: pip install playwright && playwright install")
            return None

        logger.info(f"🌐 使用 Playwright 模式抓取: {url}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()

            try:
                # 访问页面
                await page.goto(url, wait_until='networkidle', timeout=self.timeout * 1000)

                # 等待文章内容加载
                await page.wait_for_selector('#content_views', timeout=10000)

                # 提取文章信息
                title = await page.evaluate('''() => {
                    const el = document.querySelector('h1.title-article');
                    return el ? el.innerText.trim() : '';
                }''')

                author = await page.evaluate('''() => {
                    const el = document.querySelector('a.follow-nickName');
                    return el ? el.innerText.trim() : '';
                }''')

                publish_time = await page.evaluate('''() => {
                    const el = document.querySelector('span.time');
                    return el ? el.innerText.trim() : '';
                }''')

                # 提取文章正文 HTML 并转换
                markdown_content = await page.evaluate('''() => {
                    const content = document.querySelector('#content_views');
                    if (!content) return '';

                    // 简单的 HTML 到 Markdown 转换
                    let md = '';

                    function processNode(node) {
                        if (node.nodeType === Node.TEXT_NODE) {
                            const text = node.textContent.trim();
                            if (text) md += text + ' ';
                        } else if (node.nodeType === Node.ELEMENT_NODE) {
                            const tag = node.tagName.toLowerCase();

                            if (tag === 'h1') {
                                md += '\\n# ' + node.textContent.trim() + '\\n\\n';
                            } else if (tag === 'h2') {
                                md += '\\n## ' + node.textContent.trim() + '\\n\\n';
                            } else if (tag === 'h3') {
                                md += '\\n### ' + node.textContent.trim() + '\\n\\n';
                            } else if (tag === 'pre') {
                                const code = node.textContent;
                                const lang = node.className.match(/language-(\\w+)/);
                                md += '\\n```' + (lang ? lang[1] : '') + '\\n' + code + '\\n```\\n';
                            } else if (tag === 'code' && node.parentNode.tagName.toLowerCase() !== 'pre') {
                                md += '`' + node.textContent + '`';
                            } else if (tag === 'strong' || tag === 'b') {
                                md += '**' + node.textContent.trim() + '**';
                            } else if (tag === 'em' || tag === 'i') {
                                md += '*' + node.textContent.trim() + '*';
                            } else if (tag === 'a') {
                                md += '[' + node.textContent.trim() + '](' + node.href + ')';
                            } else if (tag === 'img') {
                                md += '![' + node.alt + '](' + node.src + ')';
                            } else if (tag === 'br') {
                                md += '\\n';
                            } else if (tag === 'p' || tag === 'div') {
                                // 处理子元素
                                for (const child of node.childNodes) {
                                    processNode(child);
                                }
                                md += '\\n\\n';
                            } else {
                                // 其他标签，递归处理子元素
                                for (const child of node.childNodes) {
                                    processNode(child);
                                }
                            }
                        }
                    }

                    for (const child of content.childNodes) {
                        processNode(child);
                    }

                    return md;
                }''')

                # 清理多余空行
                markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content).strip()

                # 构建元数据
                metadata = {
                    'title': title,
                    'author': author,
                    'publish_time': publish_time,
                    'url': url,
                    'article_id': self.extract_article_id(url),
                    'scrape_method': 'Playwright',
                    'scrape_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'word_count': len(markdown_content),
                    'has_code_blocks': bool(re.search(r'```', markdown_content)),
                    'has_tables': bool(re.search(r'\|.*\|', markdown_content)),
                    'has_images': bool(re.search(r'!\[.*\]\(.*\)', markdown_content)),
                }

                logger.info(f"✅ Playwright 模式抓取成功")
                logger.info(f"   标题: {title}")
                logger.info(f"   作者: {author}")
                logger.info(f"   字数: {metadata['word_count']}")

                await browser.close()
                return markdown_content, metadata

            except Exception as e:
                logger.error(f"❌ Playwright 抓取失败: {str(e)}")
                await browser.close()
                return None

    def scrape(self, url: str, method: str = 'auto') -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        抓取 CSDN 文章（自动选择最佳方式）

        Args:
            url: CSDN 文章 URL
            method: 抓取方法 ('auto', 'requests', 'playwright')

        Returns:
            tuple: (markdown_content, metadata) 或 None
        """
        # 验证 URL
        if not self.validate_url(url):
            logger.error(f"❌ 无效的 CSDN 文章 URL: {url}")
            logger.info("   正确格式: https://blog.csdn.net/<author>/article/details/<article_id>")
            return None

        logger.info(f"🎯 开始抓取 CSDN 文章")
        logger.info(f"   URL: {url}")

        # 选择抓取方法
        if method == 'auto':
            # 优先尝试 requests（快速），失败则用 Playwright（完整）
            result = self.scrape_with_requests(url)
            if result:
                return result
            else:
                logger.info("🔄 requests 模式失败，切换到 Playwright 模式...")
                import asyncio
                return asyncio.run(self.scrape_with_playwright(url))
        elif method == 'requests':
            return self.scrape_with_requests(url)
        elif method == 'playwright':
            import asyncio
            return asyncio.run(self.scrape_with_playwright(url))
        else:
            logger.error(f"❌ 不支持的抓取方法: {method}")
            return None


def save_result(content: str, metadata: Dict[str, Any], output_path: str):
    """
    保存抓取结果到文件

    Args:
        content: Markdown 内容
        metadata: 元数据字典
        output_path: 输出文件路径
    """
    # 构建完整的输出文件
    output = f"""# 原始文章内容

## 📋 文章元数据

| 属性 | 值 |
|------|-----|
| **标题** | {metadata.get('title', '未知')} |
| **作者** | {metadata.get('author', '未知')} |
| **发布时间** | {metadata.get('publish_time', '未知')} |
| **来源 URL** | {metadata.get('url', '')} |
| **文章 ID** | {metadata.get('article_id', '未知')} |
| **抓取时间** | {metadata.get('scrape_time', '')} |
| **抓取方式** | {metadata.get('scrape_method', '未知')} |

## 📊 内容统计

- **字数**: {metadata.get('word_count', 0)} 字符
- **包含代码块**: {'✅ 是' if metadata.get('has_code_blocks') else '❌ 否'}
- **包含表格**: {'✅ 是' if metadata.get('has_tables') else '❌ 否'}
- **包含图片**: {'✅ 是' if metadata.get('has_images') else '❌ 否'}

---

## 📝 正文内容

{content}

---

*本文由 CSDN AI Writer v1.2 自动抓取*
*抓取工具: csdn_scraper.py*
*保留原始格式，未经任何修改*
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)

    logger.info(f"💾 结果已保存到: {output_path}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════╗
║     CSDN 文章原始内容爬虫 v1.0                   ║
╚══════════════════════════════════════════════════╝

使用方式:
    python csdn_scraper.py <URL> [选项]

参数:
    <URL>           CSDN 文章链接（必填）
    -o, --output    输出文件路径（可选，默认自动生成）
    -m, --method    抓取方法: auto|requests|playwright（默认: auto）

示例:
    python csdn_scraper.py https://blog.csdn.net/xxx/article/details/12345678
    python csdn_scraper.py https://blog.csdn.net/xxx/article/details/12345678 -o article.md
    python csdn_scraper.py https://blog.csdn.net/xxx/article/details/12345678 -m playwright

注意:
    - 首次使用 Playwright 模式需要安装: pip install playwright && playwright install
    - requests 模式需要: pip install requests beautifulsoup4
""")
        sys.exit(1)

    url = sys.argv[1]
    output_file = None
    method = 'auto'

    # 解析参数
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] in ['-o', '--output'] and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] in ['-m', '--method'] and i + 1 < len(sys.argv):
            method = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    # 执行抓取
    scraper = CSDNScraper()
    result = scraper.scrape(url, method=method)

    if result:
        content, metadata = result

        # 确定输出路径
        if not output_file:
            article_id = metadata.get('article_id', 'unknown')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"csdn_raw_{article_id}_{timestamp}.md"

        # 保存结果
        save_result(content, metadata, output_file)

        print(f"""
╔══════════════════════════════════════════════════╗
║              ✅ 抓取成功！                        ║
╚══════════════════════════════════════════════════╝

📄 输出文件: {output_file}
📊 统计信息:
   • 标题: {metadata.get('title', '未知')}
   • 作者: {metadata.get('author', '未知')}
   • 字数: {metadata.get('word_count', 0)} 字符
   • 代码块: {'有' if metadata.get('has_code_blocks') else '无'}
   • 表格: {'有' if metadata.get('has_tables') else '无'}
   • 图片: {'有' if metadata.get('has_images') else '无'}

🔧 抓取方式: {metadata.get('scrape_method', '未知')}
⏰ 完成时间: {metadata.get('scrape_time', '')}

现在你可以基于这个原始文件进行改写了！
""")
    else:
        print("""
╔══════════════════════════════════════════════════╗
║              ❌ 抓取失败                          ║
╚══════════════════════════════════════════════════╝

可能的原因:
1. URL 格式不正确或文章不存在
2. 网络连接问题
3. 被 CSDN 反爬机制拦截
4. 页面结构发生变化

建议:
• 检查 URL 是否正确
• 尝试使用 -m playwright 参数
• 稍后重试
• 手动复制文章内容
""")
        sys.exit(1)


if __name__ == '__main__':
    main()
