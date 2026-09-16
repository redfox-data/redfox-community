#!/usr/bin/env python3
"""
3平台适配器 — 豆包 / Kimi / DeepSeek 统一接口

统一接口:
  submit(platform, query) -> task_id
  poll(platform, task_id) -> result_dict | None  (None = still pending)
  extract_result(platform, raw_data) -> (content, sources)
  extract_result_full(platform, raw_data) -> dict  (含信源可用性诊断)
  is_valid_answer(content) -> (valid, reason)
"""

import os
import json
import re
import time
from urllib.parse import urlparse

import requests

API_BASE = "https://redfox.hk"
API_KEY = os.environ.get("REDFOX_API_KEY")

PLATFORMS = {
    "doubao": {
        "submit_path": "/story/api/doubaoSearch/submit",
        "result_path": "/story/api/doubaoSearch/result",
        "label": "豆包",
    },
    "kimi": {
        "submit_path": "/story/api/kimi/submit",
        "result_path": "/story/api/kimi/result",
        "label": "Kimi",
    },
    "deepseek": {
        "submit_path": "/story/api/deepSearch/dsSubmit",
        "result_path": "/story/api/deepSearch/dsResult",
        "label": "DeepSeek",
    },
}

SOURCE_TAG = "品牌GEO分析-GitHub"


def _get_headers():
    """返回统一请求头，若 API_KEY 缺失则抛异常"""
    if not API_KEY:
        raise ValueError(
            "未配置 REDFOX_API_KEY 环境变量，"
            "请前往 https://redfox.hk/settings/api-keys?source=github 获取 API Key"
        )
    return {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }


def submit(platform, query, source=None, max_retries=3):
    """提交搜索请求，返回 task_id

    Args:
        platform: 平台 key (doubao / kimi / deepseek)
        query: 搜索关键词
        source: 来源标识，默认 SOURCE_TAG
        max_retries: 限流重试次数

    Returns:
        task_id 字符串

    Raises:
        ValueError: 平台未知或响应中无 taskId
        requests.RequestException: 网络错误
    """
    if platform not in PLATFORMS:
        raise ValueError(f"未知平台: {platform}，可选: {list(PLATFORMS.keys())}")

    config = PLATFORMS[platform]
    url = f"{API_BASE}{config['submit_path']}"

    for attempt in range(max_retries + 1):
        resp = requests.post(
            url,
            json={"inquiry_text": query, "source": source or SOURCE_TAG},
            headers=_get_headers(),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        task_id = (data.get("data") or {}).get("taskId")
        if task_id:
            return task_id

        # 限流错误，等待后重试
        code = data.get("code", 0)
        if code == 3108 and attempt < max_retries:
            wait = (attempt + 1) * 2  # 2s, 4s, 6s
            time.sleep(wait)
            continue

        raise ValueError(f"提交失败，未获取到 taskId: {json.dumps(data, ensure_ascii=False)}")

    raise ValueError(f"提交失败，重试 {max_retries} 次后仍未获取到 taskId")


def poll(platform, task_id):
    """轮询单个任务状态

    Returns:
        - dict: 任务完成时返回完整响应 JSON
        - None: 任务仍在处理中
        - raises ValueError: 任务失败
    """
    if platform not in PLATFORMS:
        raise ValueError(f"未知平台: {platform}")

    config = PLATFORMS[platform]
    url = f"{API_BASE}{config['result_path']}"

    resp = requests.post(
        url,
        json={"taskId": task_id},
        headers=_get_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()

    # 状态字段可能在 data.data.status 或 data.status
    inner = data.get("data") or {}
    status = inner.get("status", "") if isinstance(inner, dict) else ""
    if not status:
        status = data.get("status", "")

    if status in ("completed", "success", "done"):
        return data
    if status in ("failed", "error"):
        raise ValueError(f"搜索任务失败: {json.dumps(data, ensure_ascii=False)}")
    return None  # still pending


# ── 回答有效性校验 ────────────────────────────────────────────
# 平台在限流/故障时会返回一段「话术」而非真实回答（实测豆包：
# 「当前高峰期算力紧张，优先通道暂时繁忙。我们正在优先为你调度资源，请稍后再试。」）。
# 这类文本若被记为 completed，会让该平台凭空少一次品牌提及，
# 直接压低提及率与 GEO 得分 —— 必须识别出来并从统计中剔除。

# 强错误标记：命中即判无效（与长度无关）
HARD_ERROR_MARKERS = (
    "算力紧张", "算力不足", "算力资源", "优先通道",
    "服务繁忙", "系统繁忙", "服务器繁忙", "当前繁忙",
    "请求过于频繁", "操作过于频繁", "访问过于频繁", "提问过于频繁",
    "当前高峰期", "调度资源", "服务暂时不可用", "系统开小差",
    "内容审核未通过", "涉嫌违规", "不符合相关规范", "无法回答该问题",
    "抱歉，我无法", "内容由AI生成，仅供参考",
)

# 软错误标记：仅在文本明显偏短时才判无效（避免误伤正常回答里的同词）
SOFT_ERROR_MARKERS = (
    "请稍后再试", "请稍后重试", "请稍候再试", "稍后再试",
    "网络异常", "网络错误", "服务异常", "系统异常", "服务不可用",
    "请刷新页面", "请重新提问", "请换个问题",
)

MAX_SOFT_LEN = 200       # 软标记判定的长度上限
MIN_VALID_LEN = 40       # 低于此长度一律视为异常响应


def is_valid_answer(content):
    """判断平台返回的是否为真实回答（而非限流/故障话术）

    Args:
        content: 平台返回的正文

    Returns:
        (valid: bool, reason: str)  reason 仅在不通过时有值
    """
    text = strip_inline_citations(content or "").strip()
    if not text:
        return False, "空回答"

    n = len(text)

    for marker in HARD_ERROR_MARKERS:
        if marker in text:
            return False, f"平台错误话术（命中「{marker}」）"

    if n < MIN_VALID_LEN:
        return False, f"内容过短（{n} 字），疑似异常响应"

    if n < MAX_SOFT_LEN:
        for marker in SOFT_ERROR_MARKERS:
            if marker in text:
                return False, f"平台错误话术（命中「{marker}」）"

    return True, ""


# ── 内联引用标记清洗 ──────────────────────────────────────────
# 各平台的引用标记都指向引擎内部片段，不含真实 URL，必须从正文剥离，
# 否则会原样出现在报告与原始存档里：
#   Kimi    : <REF>cite✦tools://web_search:1#1:~:text=Mini 5 Pro...249g</REF>
#   DeepSeek: ⋯1999 元起[citation:1]（成对出现，标记本身无跳转意义）

_CITATION_RES = (
    re.compile(r"<REF>.*?(?:</REF>|\Z)", re.S | re.I),
    re.compile(r"<ref>.*?(?:</ref>|\Z)", re.S | re.I),
    re.compile(r"cite\u2726tools://[^\s<\u3000]*"),
    re.compile(r"[\[\u3010]\s*citation\s*:\s*\d+\s*[\]\u3011]", re.I),
    re.compile(r"[\u2726\u2727]"),
)


def strip_inline_citations(text):
    """剥离正文中的内联引用标记（Kimi <REF>…</REF> / DeepSeek [citation:N]）"""
    if not text:
        return ""
    out = text
    for pattern in _CITATION_RES:
        out = pattern.sub("", out)
    # 清理残留的孤立标签与多余空格
    out = re.sub(r"</?REF>", "", out, flags=re.I)
    out = re.sub(r"[ \t]{2,}", " ", out)
    # 标记被移除后留下的空行/行尾空格
    out = re.sub(r"[ \t]+(\n)", r"\1", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip()


_URL_RE = re.compile(r"https?://[^\s<>\"'\uff0c\u3002\uff09\uff08\)\]\u3001]+")


def extract_urls_from_text(text, limit=50):
    """从正文中提取裸 URL，用于平台未提供结构化信源时的兜底"""
    if not text:
        return []
    seen, urls = set(), []
    for m in _URL_RE.finditer(text):
        u = m.group(0).rstrip(".,;:")
        if u not in seen:
            seen.add(u)
            urls.append(u)
        if len(urls) >= limit:
            break
    return urls


def extract_result(platform, raw_data):
    """从 API 原始响应中提取统一格式的内容和引用来源

    三平台实际响应格式:
      豆包: data.result.content + data.result.searchGuid[].text_card{title,url,sitename}
      Kimi: data.result.content（webPages 实测恒为空数组，引用只以正文内联
            <REF>cite✦tools://…标记存在，不含真实 URL，故多数情况无信源）
      DeepSeek: data.result.content + data.result（待确认）

    信源提取顺序: 结构化字段 → 通用字段 → 正文裸 URL 兜底
    返回前会调用 strip_inline_citations() 清理正文中的内联引用标记。

    Args:
        platform: 平台 key
        raw_data: poll() 返回的完整 JSON dict

    Returns:
        (content: str, sources: list[dict])
        sources 每项: {"title": str, "url": str, "domain": str}
    """
    data = raw_data.get("data") or raw_data

    # result 字段可能是 dict（豆包/Kimi/DeepSeek）或 list
    result_obj = data.get("result")

    # ── 提取 content ──────────────────────────────────────
    content = ""
    if isinstance(result_obj, dict):
        # 豆包/Kimi/DeepSeek: content 在 result.content
        content = (
            result_obj.get("content")
            or result_obj.get("answer")
            or result_obj.get("text")
            or result_obj.get("response")
            or ""
        )
    elif isinstance(result_obj, str):
        content = result_obj

    # 兜底: 直接在 data 层找 content
    if not content:
        content = (
            data.get("content")
            or data.get("answer")
            or data.get("text")
            or data.get("response")
            or ""
        )

    # ── 提取 sources ──────────────────────────────────────
    sources = []

    if isinstance(result_obj, dict):
        # 豆包: searchGuid[].text_card{title, url, sitename}
        search_guid = result_obj.get("searchGuid") or []
        for item in search_guid:
            if not isinstance(item, dict):
                continue
            card = item.get("text_card") or item
            url = card.get("url") or card.get("link") or ""
            title = card.get("title") or card.get("name") or card.get("sitename") or ""
            if url or title:
                sources.append({
                    "title": title,
                    "url": url,
                    "domain": extract_domain(url),
                })

        # Kimi: webPages[]
        web_pages = result_obj.get("webPages") or []
        for item in web_pages:
            if not isinstance(item, dict):
                continue
            url = item.get("url") or item.get("link") or item.get("href") or ""
            title = item.get("title") or item.get("name") or ""
            if url or title:
                sources.append({
                    "title": title,
                    "url": url,
                    "domain": extract_domain(url),
                })

        # 通用: result.sources / result.references / result.citations
        if not sources:
            for key in ("sources", "references", "citations"):
                raw_sources = result_obj.get(key)
                if isinstance(raw_sources, list) and raw_sources:
                    for s in raw_sources:
                        if not isinstance(s, dict):
                            continue
                        url = s.get("url") or s.get("link") or s.get("href") or ""
                        title = s.get("title") or s.get("name") or s.get("text") or ""
                        sources.append({
                            "title": title,
                            "url": url,
                            "domain": extract_domain(url),
                        })
                    break

    # 兜底: data 层的 sources
    if not sources:
        for key in ("sources", "references", "citations"):
            raw_sources = data.get(key)
            if isinstance(raw_sources, list) and raw_sources:
                for s in raw_sources:
                    if not isinstance(s, dict):
                        continue
                    url = s.get("url") or s.get("link") or s.get("href") or ""
                    title = s.get("title") or s.get("name") or s.get("text") or ""
                    sources.append({
                        "title": title,
                        "url": url,
                        "domain": extract_domain(url),
                    })
                break

    # 最后兜底: 正文中的裸 URL（Kimi 的 webPages 恒为空，只能这样兜）
    # 注意必须从「剥离引用标记之前」的原文里取
    if not sources:
        for url in extract_urls_from_text(content):
            domain = extract_domain(url)
            sources.append({"title": domain, "url": url, "domain": domain})

    # 剥离内联引用标记（Kimi <REF>…</REF>），避免污染报告与存档
    content = strip_inline_citations(content)

    return content, sources


def extract_result_full(platform, raw_data):
    """在 extract_result 基础上附带信源可用性诊断

    Returns:
        {
            "content": str,
            "sources": list[dict],
            "sources_available": bool,   # 是否拿到了可解析的外链信源
            "sources_note": str,         # 不可用时的原因说明（可直接进报告）
        }
    """
    content, sources = extract_result(platform, raw_data)
    available = bool(sources)
    note = ""
    if not available:
        if platform == "kimi":
            note = "Kimi 仅返回正文内联引用标记（cite✦tools://…），不含可解析外链，故无信源数据"
        else:
            note = f"{PLATFORMS.get(platform, {}).get('label', platform)} 本次响应未返回可解析的信源"
    return {
        "content": content,
        "sources": sources,
        "sources_available": available,
        "sources_note": note,
    }


def extract_domain(url):
    """从 URL 中提取域名（去除 www. 前缀）"""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc or parsed.path.split("/")[0]
        return domain.replace("www.", "").lower()
    except Exception:
        return url.lower()
