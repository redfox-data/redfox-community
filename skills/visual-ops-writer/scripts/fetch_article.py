"""文章抓取脚本（统一版）

输入：sourceUrl（任意文章链接）
输出：JSON {title, sections, images, raw_html}
- title: 文章标题
- sections: [{heading, level, text}]  章节切分（按 H2/H3 拆分）
- images: [url, ...]  文章中所有图片 URL（按出现顺序）
- raw_html: 原始 HTML（可选，用于 fallback）

使用方式：
  python fetch_article.py --url "https://xxx.com/post/123" --output article.json

注意：
  - 仅依赖 Python 标准库
  - 抓取失败时，输出 error 字段，调用方需判断降级
  - 图片 URL 同时保留绝对路径（直接用）和相对路径补全
"""

import argparse
import json
import os
import re
import ssl
import sys
import urllib.request
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse


class ArticleExtractor(HTMLParser):
    """从 HTML 中提取标题、章节文本、图片 URL。"""

    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.title = ""
        self.in_title = False
        self.images = []
        # 章节切分：记录当前 H2/H3 节点与其下文本
        self.sections = []
        self._current_section = None
        self._current_text_parts = []
        self._in_heading = False
        self._heading_level = 0
        self._skip_tags = {"script", "style", "noscript", "nav", "footer", "header"}
        self._skip_depth = 0
        self._depth = 0

    # ---- 标签处理 ----
    def handle_starttag(self, tag, attrs):
        self._depth += 1
        attrs_dict = dict(attrs)

        if tag == "title":
            self.in_title = True
            return

        if tag in ("h1", "h2", "h3"):
            self._in_heading = True
            self._heading_level = int(tag[1])
            self._flush_section()
            self._current_section = {
                "heading": "",
                "level": self._heading_level,
                "text": "",
            }
            return

        if tag == "img":
            src = attrs_dict.get("src") or attrs_dict.get("data-src") or attrs_dict.get("data-original")
            if src:
                full_url = urljoin(self.base_url, src)
                if full_url not in self.images:
                    self.images.append(full_url)
            return

        if tag in self._skip_tags:
            self._skip_depth += 1
            return

        if tag in ("p", "br", "li", "div"):
            self._current_text_parts.append("\n")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
            return

        if tag in ("h1", "h2", "h3"):
            self._in_heading = False
            if self._current_section:
                self._current_section["text"] = "".join(self._current_text_parts).strip()
                self.sections.append(self._current_section)
                self._current_section = None
                self._current_text_parts = []
            return

        if tag in self._skip_tags and self._skip_depth > 0:
            self._skip_depth -= 1
            return

        self._depth -= 1

    def handle_data(self, data):
        if self.in_title:
            self.title += data
            return
        if self._skip_depth > 0:
            return
        if self._in_heading and self._current_section is not None:
            self._current_section["heading"] += data
            return
        if self._current_section is not None:
            self._current_text_parts.append(data)

    # ---- 辅助 ----
    def _flush_section(self):
        if self._current_section is not None:
            self._current_section["text"] = "".join(self._current_text_parts).strip()
            if self._current_section["heading"] or self._current_section["text"]:
                self.sections.append(self._current_section)
        self._current_section = None
        self._current_text_parts = []

    def close(self):
        super().close()
        # 处理文档末尾没有 H2/H3 闭合的情况
        self._flush_section()
        # 清理文本（合并多余空白行）
        cleaned = []
        for sec in self.sections:
            sec["text"] = re.sub(r"\n{3,}", "\n\n", sec["text"]).strip()
            cleaned.append(sec)
        self.sections = cleaned


def fetch_html(url, timeout=30):
    """抓取 URL 对应的 HTML 文本。"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        raw = resp.read()
        try:
            return raw.decode(charset, errors="replace")
        except (LookupError, TypeError):
            return raw.decode("utf-8", errors="replace")


def extract_article(html, base_url):
    """从 HTML 中提取文章结构。"""
    parser = ArticleExtractor(base_url)
    parser.feed(html)
    parser.close()

    return {
        "title": parser.title.strip(),
        "sections": parser.sections,
        "images": parser.images,
    }


def filter_meaningful_images(images, min_path_depth=2):
    """过滤装饰性图片（icon/avatar/logo/loading 等）。"""
    skip_patterns = [
        r"/icon", r"/logo", r"/avatar", r"/loading", r"/spinner",
        r"1x1\.", r"pixel\.", r"\.gif$", r"data:image",
        r"/sprite", r"/static/img/.*\?\d+",  # 静态资源
    ]
    regex = re.compile("|".join(skip_patterns), re.IGNORECASE)
    return [u for u in images if not regex.search(u)]


def main():
    parser = argparse.ArgumentParser(
        description="抓取任意文章 URL，输出结构化 JSON（标题+章节+图片）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--url", type=str, required=True, help="文章 URL")
    parser.add_argument("--output", type=str, default="article.json", help="输出 JSON 路径")
    parser.add_argument("--keep-html", action="store_true", help="在输出中保留原始 HTML")
    parser.add_argument("--no-filter", action="store_true", help="不过滤装饰性图片")
    args = parser.parse_args()

    # 校验 URL
    parsed = urlparse(args.url)
    if parsed.scheme not in ("http", "https"):
        print(f"[ERR] Invalid URL scheme: {args.url}")
        sys.exit(1)

    print(f"[FETCH] {args.url}")
    try:
        html = fetch_html(args.url)
    except Exception as e:
        print(f"[ERR] Fetch failed: {e}")
        result = {"error": f"fetch_failed: {e}", "url": args.url}
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        sys.exit(1)

    print(f"[OK] HTML fetched: {len(html)} bytes")
    result = extract_article(html, args.url)
    result["url"] = args.url

    if not args.no_filter:
        before = len(result["images"])
        result["images"] = filter_meaningful_images(result["images"])
        print(f"[OK] Filtered images: {before} -> {len(result['images'])}")

    if args.keep_html:
        result["raw_html"] = html

    # 统计
    print(f"[OK] Title: {result['title']}")
    print(f"[OK] Sections: {len(result['sections'])}")
    print(f"[OK] Images: {len(result['images'])}")

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n[Done] Saved to {args.output}")


if __name__ == "__main__":
    main()
