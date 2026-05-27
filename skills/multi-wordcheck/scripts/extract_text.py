#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import re
import sys
from urllib.parse import urlparse

from coze_workload_identity import requests

# 支持的文本文件扩展名
SUPPORTED_TEXT_EXTENSIONS = {'.txt', '.csv', '.md', '.log', '.json', '.xml', '.html', '.htm', '.ini', '.cfg', '.conf', '.yaml', '.yml', '.toml'}

# SSR框架水合数据的script标签匹配模式
SSR_SCRIPT_PATTERNS = [
    (r'<script\s+id="__NEXT_DATA__"[^>]*type="application/json"[^>]*>(.*?)</script>', 'next_data'),
    (r'<script\s+type="application/json"[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', 'next_data'),
    (r'window\.__NUXT__\s*=\s*(?:"\s*)?(\{.*?\})(?:\s*"?\s*)?;', 'nuxt'),
    (r'window\.__INITIAL_STATE__\s*=\s*(\{.*?\})\s*;', 'initial_state'),
]

# 文章内容可能使用的字段名（优先级从高到低）
CONTENT_FIELD_NAMES = [
    'content', 'articleBody', 'body', 'html', 'article_content',
    'articleContent', 'text', 'description', 'detail', 'markdown',
    'richContent', 'fullText', 'mainContent', 'postContent',
]


def _decode_unicode_escapes(text):
    """安全解码JSON字符串中的unicode转义（如\u003c → <），不影响原始UTF-8中文"""
    def replace_unicode(m):
        code = m.group(1)
        try:
            return chr(int(code, 16))
        except (ValueError, OverflowError):
            return m.group(0)
    return re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, text)


def _clean_html_tags(text):
    """移除HTML标签并解码HTML实体和unicode转义"""
    text = _decode_unicode_escapes(text)
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n[ \t]*\n', '\n', text)
    text = re.sub(r'\n{2,}', '\n', text)
    return text.strip()


def _has_enough_chinese(text, min_chars=10):
    """检查文本是否包含足够的中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]{' + str(min_chars) + r',}', text))


def _safe_json_loads(raw_text):
    """容错性JSON解析：清理控制字符后解析"""
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', ' ', raw_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    cleaned = re.sub(r'[\x00-\x1f\x7f]', ' ', raw_text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    try:
        decoder = json.JSONDecoder()
        obj, _ = decoder.raw_decode(cleaned)
        return obj
    except (json.JSONDecodeError, ValueError):
        pass

    return None


def _recursive_find_content(obj, depth=0, max_depth=12):
    """递归查找对象中最长的文章内容字段"""
    if depth > max_depth or obj is None:
        return ""

    best_content = ""

    if isinstance(obj, dict):
        for key in CONTENT_FIELD_NAMES:
            if key in obj:
                val = obj[key]
                if isinstance(val, str) and len(val) > 200:
                    clean = _clean_html_tags(val)
                    if len(clean) > 100 and _has_enough_chinese(clean, 5):
                        if len(clean) > len(best_content):
                            best_content = clean

        for v in obj.values():
            result = _recursive_find_content(v, depth + 1, max_depth)
            if result and len(result) > len(best_content):
                best_content = result

    elif isinstance(obj, list):
        for item in obj[:20]:
            result = _recursive_find_content(item, depth + 1, max_depth)
            if result and len(result) > len(best_content):
                best_content = result

    return best_content


def _extract_from_jsonld(body):
    """从JSON-LD结构化数据中提取文章内容"""
    jsonld_matches = re.findall(
        r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        body, re.DOTALL
    )
    best_text = ""
    for match in jsonld_matches:
        try:
            jdata = json.loads(match)
            if isinstance(jdata, list):
                jdata = jdata[0]
            article_body = jdata.get("articleBody", "")
            if article_body and len(article_body) > 50:
                clean = _clean_html_tags(article_body)
                if len(clean) > len(best_text):
                    best_text = clean
        except (json.JSONDecodeError, AttributeError):
            continue
    return best_text


def _extract_from_ssr_data(body):
    """从SSR框架水合数据中提取文章内容（Next.js/Nuxt.js等）"""
    best_content = ""

    for pattern, framework in SSR_SCRIPT_PATTERNS:
        matches = re.findall(pattern, body, re.DOTALL)
        for raw_text in matches:
            if not raw_text or len(raw_text) < 200:
                continue

            # 方法1：JSON解析
            data = _safe_json_loads(raw_text)
            if data is not None:
                if framework == 'next_data':
                    props = data.get('props', {}).get('pageProps', {})
                    content = _recursive_find_content(props)
                else:
                    content = _recursive_find_content(data)

                if content and len(content) > len(best_content):
                    best_content = content

            # 方法2：正则提取所有content字段，取最长
            content_fields = re.findall(r'"((?:content|articleBody|body|html|article_content|articleContent))"\s*:\s*"((?:[^"\\]|\\.)*)"', raw_text)
            for field_name, field_value in content_fields:
                if len(field_value) > 200:
                    decoded = _decode_unicode_escapes(field_value)
                    clean = _clean_html_tags(decoded)
                    if len(clean) > 100 and _has_enough_chinese(clean, 5):
                        if len(clean) > len(best_content):
                            best_content = clean

    return best_content


def _extract_from_inline_scripts(body):
    """从内联script标签中提取可能的文章数据"""
    best_content = ""

    scripts = re.findall(r'<script[^>]*>(.*?)</script>', body, re.DOTALL)
    for script_content in scripts:
        if len(script_content) < 500:
            continue
        if '__NEXT_DATA__' in script_content or 'application/ld+json' in script_content:
            continue

        string_values = re.findall(r'"(?:content|articleBody|body|html|text|description|detail|markdown)"\s*:\s*"((?:[^"\\]|\\.)*)"', script_content)
        for val in string_values:
            if len(val) > 200:
                decoded = _decode_unicode_escapes(val)
                clean = _clean_html_tags(decoded)
                if len(clean) > 100 and _has_enough_chinese(clean, 5):
                    if len(clean) > len(best_content):
                        best_content = clean

    return best_content


def _extract_from_meta(body):
    """从meta标签和title中提取基本内容"""
    parts = []
    title_match = re.search(r'<title>(.*?)</title>', body, re.DOTALL)
    if title_match:
        title = _clean_html_tags(title_match.group(1)).strip()
        if title:
            parts.append(title)

    meta_desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']', body)
    if not meta_desc:
        meta_desc = re.search(r'<meta\s+content=["\']([^"\']*)["\']\s+name=["\']description["\']', body)
    if meta_desc:
        desc = _clean_html_tags(meta_desc.group(1)).strip()
        if desc and desc not in parts:
            parts.append(desc)

    return "\n".join(parts)


def _extract_chinese_blocks(body):
    """从HTML中提取连续中文文本块（兜底策略，适用于SPA页面）"""
    clean_body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL)
    clean_body = re.sub(r'<style[^>]*>.*?</style>', '', clean_body, flags=re.DOTALL)
    clean_body = re.sub(r'<noscript[^>]*>.*?</noscript>', '', clean_body, flags=re.DOTALL)

    blocks = re.findall(
        r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\u2018\u2019\u201c\u201d\u2026\u2014\u2013'
        r'0-9a-zA-Z\s\uff0c\u3002\uff01\uff1f\u3001\uff1b\uff1a\u201c\u201d\u2018\u2019\uff08\uff09\u3010\u3011\u300a\u300b\u00b7\u2026\u2014\u2013./~.+]+',
        clean_body
    )

    seen = set()
    result = []
    for block in blocks:
        stripped = block.strip()
        chinese_count = len(re.findall(r'[\u4e00-\u9fff]', stripped))
        if chinese_count >= 5 and stripped not in seen:
            seen.add(stripped)
            result.append(stripped)

    return "\n".join(result)


def extract_from_text_file(file_path):
    """从文本文件中提取内容"""
    try:
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
                return text.strip()
            except (UnicodeDecodeError, UnicodeError):
                continue
        raise Exception("无法识别文件编码")
    except Exception as e:
        raise Exception(f"文本文件提取失败: {str(e)}")


def extract_from_web(url):
    """从网页中提取文本，使用 coze_workload_identity.requests"""
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code >= 400:
            raise Exception(f"网页请求失败: HTTP {response.status_code}")

        body = response.text

        # 策略1：从JSON-LD结构化数据提取
        jsonld_text = _extract_from_jsonld(body)
        if jsonld_text and len(jsonld_text) > 100:
            return jsonld_text

        # 策略2：从SSR框架水合数据提取（Next.js/Nuxt.js/React SSR等）
        ssr_text = _extract_from_ssr_data(body)
        if ssr_text and len(ssr_text) > 100:
            return ssr_text

        # 策略3：从内联script标签提取文章数据
        inline_text = _extract_from_inline_scripts(body)
        if inline_text and len(inline_text) > 100:
            return inline_text

        # 策略4：从meta标签+title提取基本描述
        meta_text = _extract_from_meta(body)

        # 策略5：从HTML中提取中文文本块（适合纯SPA页面）
        chinese_text = _extract_chinese_blocks(body)

        # 智能合并
        combined_parts = []
        if meta_text:
            combined_parts.append(meta_text)
        if chinese_text:
            meta_first_line = meta_text.split('\n')[0][:30] if meta_text else ""
            if meta_first_line and meta_first_line in chinese_text:
                combined_parts = [chinese_text]
            else:
                combined_parts.append(chinese_text)

        combined = "\n".join(combined_parts)

        if combined.strip():
            return combined.strip()

        # 策略6：BeautifulSoup兜底
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(body, 'html.parser')
            for tag in soup(["script", "style", "noscript"]):
                tag.decompose()
            text = soup.get_text(separator='\n', strip=True)
            if text.strip():
                return text.strip()
        except ImportError:
            pass

        raise Exception("未能从网页中提取到文本内容")

    except Exception as e:
        raise Exception(f"网页提取失败: {str(e)}")


def extract_text(source_type, source_value):
    """提取文本内容的统一入口"""
    try:
        text = ""

        if source_type == "file":
            if not os.path.exists(source_value):
                return {
                    "status": "error",
                    "type": "file",
                    "source": source_value,
                    "error": "文件不存在"
                }

            file_ext = os.path.splitext(source_value)[1].lower()

            if file_ext in SUPPORTED_TEXT_EXTENSIONS:
                text = extract_from_text_file(source_value)
            else:
                return {
                    "status": "error",
                    "type": "file",
                    "source": source_value,
                    "error": f"不支持的文件类型: {file_ext}，仅支持以下文本文件类型: {', '.join(sorted(SUPPORTED_TEXT_EXTENSIONS))}"
                }

        elif source_type == "web":
            text = extract_from_web(source_value)

        else:
            return {
                "status": "error",
                "error": f"不支持的源类型: {source_type}，仅支持 file 或 web"
            }

        if not text:
            return {
                "status": "warning",
                "type": source_type,
                "source": source_value,
                "text": "",
                "text_length": 0,
                "message": "未提取到文本内容"
            }

        text_length = len(text)

        # 字数限制检查
        if text_length > 10000:
            return {
                "status": "exceeded_limit",
                "type": source_type,
                "source": source_value,
                "text": text,
                "text_length": text_length,
                "message": "⚠ 当前内容字数超过10000字，查询将会消耗过多的时间和积分，强烈建议手动分批查询。"
            }
        if text_length > 3000:
            return {
                "status": "batch_required",
                "type": source_type,
                "source": source_value,
                "text": text,
                "text_length": text_length,
                "message": "⚠ 单次查询内容字数建议不超过3000字，现在已超过单次执行字数是否进行分批查询？"
            }

        return {
            "status": "success",
            "type": source_type,
            "source": source_value,
            "text": text,
            "text_length": text_length
        }

    except Exception as e:
        return {
            "status": "error",
            "type": source_type,
            "source": source_value,
            "error": str(e)
        }


def main():
    parser = argparse.ArgumentParser(description="文本提取工具")
    parser.add_argument("--type", required=True, choices=["file", "web"], help="提取类型：file（文件）或web（网页）")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", help="文件路径（type=file时使用）")
    group.add_argument("--url", help="网页地址（type=web时使用）")

    args = parser.parse_args()

    source_value = args.path if args.type == "file" else args.url

    result = extract_text(args.type, source_value)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
