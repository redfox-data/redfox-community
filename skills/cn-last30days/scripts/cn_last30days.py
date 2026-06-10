#!/usr/bin/env python3
"""
cn-last30days: 中国社媒平台话题研究工具
==========================================
从小红书、抖音、公众号三大平台搜索过去30天内人们关于某话题的真实讨论。

Usage:
    python cn_last30days.py "AI视频工具"
    python cn_last30days.py "大模型" --output-format html
    python cn_last30days.py "小红书运营" --platforms xhs,gzh
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

# Windows stdout UTF-8
if os.name == "nt":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

# ─── 常量 ──────────────────────────────────────────────────────────────────────────
API_BASE = "https://redfox.hk/story/api"
PLATFORMS = {
    "xhs": {
        "endpoint": "/xhs/crawl/work",
        "label": "小红书",
        "source": "多平台话题研究-xhs-GitHub",
        "list_key": "articles",
        "requires_dates": True,
    },
    "dy": {
        "endpoint": "/dy/search/search",
        "label": "抖音",
        "source": "多平台话题研究-dy-GitHub",
        "list_key": "articles",
        "requires_dates": False,
    },
    "gzh": {
        "endpoint": "/gzh/search/hotArticle",
        "label": "公众号",
        "source": "多平台话题研究-gzh-GitHub",
        "list_key": "articles",
        "requires_dates": True,
    },
}
DEFAULT_COUNT = 50
SOURCE_LABEL = "多平台话题研究-GitHub"

# ─── API Key ────────────────────────────────────────────────────────────────────────
PUBLIC_API_KEY = "ak_db0e200c049b44288d46da0e758d53dd"


class InsufficientCreditsError(Exception):
    """API 积分不足错误"""
    pass


def get_api_key(cli_key: str | None = None) -> str:
    """按优先级获取 API Key: 命令行 > 环境变量 > 配置文件 > 公共Key"""
    if cli_key:
        return cli_key
    for env_name in ("REDFOX_API_KEY", "X_API_KEY"):
        val = os.environ.get(env_name, "").strip()
        if val:
            return val
    config_path = Path.home() / ".qoder" / "apis" / "redfox.json"
    if config_path.exists():
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
            key = data.get("api_key", "").strip()
            if key:
                return key
        except (json.JSONDecodeError, OSError):
            pass
    return PUBLIC_API_KEY


# ─── 数量解析 ───────────────────────────────────────────────────────────────────────
def parse_count(value: Any) -> int:
    """解析数量字段，支持 '1.2w'、'5000+' 等中文格式"""
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).replace("+", "").replace(",", "").strip()
    if not text:
        return 0
    try:
        if "w" in text.lower():
            return int(float(text.lower().replace("w", "")) * 10000)
        if text.endswith("万"):
            return int(float(text[:-1]) * 10000)
        if text.endswith("亿"):
            return int(float(text[:-1]) * 100000000)
        return int(float(text))
    except (TypeError, ValueError):
        return 0


def fuzzy_count(value: Any) -> str:
    """模糊化互动数，5000以下保留原始值"""
    num = parse_count(value)
    if num <= 0:
        return "--"
    if num < 5000:
        return str(num)
    if num < 10000:
        return "5000+"
    wan = num // 10000
    return f"{wan}w+"


# ─── HTTP 请求 ──────────────────────────────────────────────────────────────────────
def _http_post(url: str, payload: dict, api_key: str, max_retries: int = 3) -> dict:
    """带重试的 HTTP POST 请求"""
    import urllib.request
    import urllib.error

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
        "User-Agent": "cn-last30days/1.0",
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_error = None

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
            result = json.loads(raw)
            code = result.get("code")
            if code == 3108:
                # 限频，等待重试
                time.sleep(5 * (attempt + 1))
                continue
            if code == 3201:
                # 积分不足，不可重试
                raise InsufficientCreditsError(result.get("msg", "积分不足"))
            if code not in (200, 2000):
                raise Exception(f"API 错误 code={code}: {result.get('msg', '未知')}")
            return result
        except urllib.error.HTTPError as e:
            last_error = f"HTTP {e.code}"
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        except urllib.error.URLError as e:
            last_error = f"网络错误: {e.reason}"
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
        except Exception as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)

    raise Exception(f"请求失败: {last_error}（已尝试 {max_retries} 次）")


# ─── 平台数据获取 ────────────────────────────────────────────────────────────────────
def _fetch_platform(platform_key: str, keyword: str, count: int, api_key: str, days: int = 30) -> dict:
    """获取单个平台的数据"""
    plat = PLATFORMS[platform_key]
    url = f"{API_BASE}{plat['endpoint']}"
    label = plat["label"]

    sys.stderr.write(f"[{label}] 搜索中...\n")
    sys.stderr.flush()

    # 构建请求参数
    today = datetime.now()
    start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")

    payload = {
        "keyword": keyword,
        "source": SOURCE_LABEL,
    }
    # 需要日期的平台始终传 startDate/endDate
    if plat.get("requires_dates"):
        payload["startDate"] = start_date
        payload["endDate"] = end_date
    # 抖音可选传日期，传上更好过滤
    else:
        payload["startDate"] = start_date
        payload["endDate"] = end_date
    # 小红书额外支持 sortType
    if platform_key == "xhs":
        payload["sortType"] = "_0"  # 相关性排序

    credit_error = False
    all_articles = []
    seen_ids = set()

    try:
        result = _http_post(url, payload, api_key)
        data = result.get("data") or {}
        # 使用 list_key 提取列表数据
        list_key = plat.get("list_key", "articles")
        articles = data.get(list_key, []) if isinstance(data, dict) else (data if isinstance(data, list) else [])

        # 去重并归一化
        for art in articles:
            uid = (
                art.get("workUuid") or art.get("uuid")
                or art.get("id") or art.get("noteId")
                or ""
            )
            if uid and uid in seen_ids:
                continue
            if uid:
                seen_ids.add(uid)

            item = _normalize_article(art, platform_key, len(all_articles) + 1)
            all_articles.append(item)

            if len(all_articles) >= count:
                break

    except InsufficientCreditsError as e:
        sys.stderr.write(f"[{label}] ⚠️ {e}\n")
        sys.stderr.write(f"[{label}] 请配置个人 API Key: export REDFOX_API_KEY=你的密钥\n")
        sys.stderr.write(f"[{label}] 注册地址: https://www.redfox.hk/login\n")
        sys.stderr.flush()
        credit_error = True
    except Exception as e:
        sys.stderr.write(f"[{label}] 请求失败: {e}\n")
        sys.stderr.flush()

    sys.stderr.write(f"[{label}] 获取 {len(all_articles)} 条\n")
    sys.stderr.flush()
    result = {
        "platform": platform_key,
        "label": label,
        "items": all_articles[:count],
        "total": len(all_articles[:count]),
    }
    if credit_error:
        result["error"] = "积分不足，请配置个人 API Key"
    return result


def _first_of(art: dict, *keys: str, default: Any = None) -> Any:
    """从文章字典中按优先级取第一个非空值"""
    for k in keys:
        v = art.get(k)
        if v is not None and v != "" and v != 0:
            return v
    return default


def _normalize_article(art: dict, platform: str, idx: int) -> dict:
    """将不同平台的数据归一化为统一格式"""
    if platform == "xhs":
        return _normalize_xhs(art, idx)
    elif platform == "dy":
        return _normalize_dy(art, idx)
    elif platform == "gzh":
        return _normalize_gzh(art, idx)
    return art


def _normalize_xhs(art: dict, idx: int) -> dict:
    """归一化小红书数据 - 兼容 xhsUser/searchArticle (work*前缀) 和 xhs/search/search 两种格式"""
    note_id = str(_first_of(art, "workId", "id", "noteId", "workUuid", "uuid", default=""))
    author_id = str(_first_of(art, "accountUserid", "authorId", "accountId", default=""))
    title_raw = _first_of(art, "workTitle", "title", "displayTitle", default="")
    desc_raw = _first_of(art, "workDesc", "desc", "displayDesc", "summary", default="")
    title = (title_raw or desc_raw or "无标题")[:200]
    desc = (desc_raw or "")[:500]
    # 链接
    note_link = _first_of(art, "workUrl", "shareInfoLink", "url", default="")
    if not note_link and note_id:
        xsec_token = art.get("xsecToken", "")
        if xsec_token:
            note_link = f"https://www.xiaohongshu.com/explore/{note_id}?xsec_token={xsec_token}"
        else:
            note_link = f"https://www.xiaohongshu.com/explore/{note_id}"
    author_link = f"https://www.xiaohongshu.com/user/profile/{author_id}" if author_id else ""
    # 作者
    author_name = _first_of(art, "accountNickname", "authorNickname", "author", "accountName", "nickname", default="未知")
    # 时间
    pub_time = _first_of(art, "workPublishTime", "createTime", "publishTime", "time", default="")
    if isinstance(pub_time, (int, float)) and pub_time > 1000000000000:
        from datetime import datetime as _dt
        try:
            pub_time = _dt.fromtimestamp(pub_time / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
        except (OSError, ValueError):
            pub_time = str(pub_time)
    # 封面
    cover = _first_of(art, "coverUrl", "cover", default="")
    # 账号类型
    account_type = _first_of(art, "accountType", default="")
    # 笔记类型
    work_type = _first_of(art, "workType", "noteType", default="")
    return {
        "id": f"XHS{idx}",
        "platform": "小红书",
        "platform_key": "xhs",
        "title": title,
        "desc": desc,
        "url": note_link,
        "author": author_name,
        "author_id": author_id,
        "author_link": author_link,
        "author_fans": fuzzy_count(_first_of(art, "authorFans", "followerCount", default=0)),
        "published_at": str(pub_time),
        "engagement": {
            "likes": parse_count(_first_of(art, "workLikedCount", "likedCount", "likeCount", default=0)),
            "comments": parse_count(_first_of(art, "workCommentsCount", "commentsCount", "commentCount", default=0)),
            "collects": parse_count(_first_of(art, "workCollectedCount", "collectedCount", "collectCount", default=0)),
            "shares": parse_count(_first_of(art, "workSharedCount", "sharedCount", "shareCount", default=0)),
            "interactions": parse_count(_first_of(art, "interactiveCount", default=0)),
        },
        "engagement_display": _engagement_display(art, "xhs"),
        "cover": cover,
        "scores": _extract_scores(art),
        "account_type": account_type,
        "work_type": work_type,
    }


def _normalize_dy(art: dict, idx: int) -> dict:
    """归一化抖音数据 - 兼容 dyData/searchArticle 和 dy/search/search 两种格式"""
    work_url = _first_of(art, "workUrl", "url", default="")
    title_raw = _first_of(art, "title", "desc", default="")
    desc_raw = _first_of(art, "desc", "summary", default="")
    title = (title_raw or "无标题")[:200]
    desc = (desc_raw or "")[:500]
    author_name = _first_of(art, "accountName", "author", "authorNickname", default="未知")
    author_id = str(_first_of(art, "accountId", "authorId", default=""))
    pub_time = _first_of(art, "publishTime", "createTime", default="")
    cover = _first_of(art, "cover", "coverUrl", default="")
    return {
        "id": f"DY{idx}",
        "platform": "抖音",
        "platform_key": "dy",
        "title": title,
        "desc": desc,
        "url": work_url,
        "author": author_name,
        "author_id": author_id,
        "author_link": f"https://www.douyin.com/user/{author_id}" if author_id else "",
        "author_fans": fuzzy_count(_first_of(art, "followerCount", "authorFans", default=0)),
        "published_at": str(pub_time),
        "engagement": {
            "likes": parse_count(_first_of(art, "likeCount", "likedCount", default=0)),
            "comments": parse_count(_first_of(art, "commentCount", "commentsCount", default=0)),
            "collects": parse_count(_first_of(art, "collectCount", "collectedCount", default=0)),
            "shares": parse_count(_first_of(art, "shareCount", "sharedCount", default=0)),
        },
        "engagement_display": _engagement_display(art, "dy"),
        "cover": cover,
        "scores": _extract_scores(art),
    }


def _normalize_gzh(art: dict, idx: int) -> dict:
    """归一化公众号数据 - 适配 gzh/search/hotArticle 格式"""
    url = _first_of(art, "url", "workUrl", default="")
    title = (art.get("title") or "无标题")[:200]
    summary = _first_of(art, "summary", "desc", default="")
    author_name = _first_of(art, "author", "accountName", default="-")
    author_id = str(_first_of(art, "accountId", "authorId", default=""))
    pub_time = _first_of(art, "publicTime", "publishTime", "createTime", default="")
    cover = _first_of(art, "imageUrl", "coverUrl", "cover", default="")
    return {
        "id": f"GZH{idx}",
        "platform": "公众号",
        "platform_key": "gzh",
        "title": title,
        "desc": (summary or "")[:500],
        "url": url,
        "author": author_name,
        "author_id": author_id,
        "author_link": "",
        "author_fans": fuzzy_count(_first_of(art, "followerCount", "authorFans", default=0)),
        "published_at": str(pub_time),
        "engagement": {
            "reads": parse_count(_first_of(art, "clicksCount", "readCount", default=0)),
            "likes": parse_count(_first_of(art, "likeCount", "likedCount", default=0)),
            "watches": parse_count(_first_of(art, "watchCount", default=0)),
            "collects": parse_count(_first_of(art, "collectCount", "collectedCount", default=0)),
            "shares": parse_count(_first_of(art, "shareCount", "sharedCount", default=0)),
            "comments": parse_count(_first_of(art, "commentsCount", "commentCount", default=0)),
        },
        "engagement_display": _engagement_display(art, "gzh"),
        "cover": cover,
        "scores": _extract_scores(art),
    }


def _engagement_display(art: dict, platform: str) -> str:
    """生成可读的互动数据字符串"""
    if platform == "xhs":
        likes = fuzzy_count(_first_of(art, "workLikedCount", "likedCount", "likeCount", default=0))
        comments = fuzzy_count(_first_of(art, "workCommentsCount", "commentsCount", "commentCount", default=0))
        collects = fuzzy_count(_first_of(art, "workCollectedCount", "collectedCount", "collectCount", default=0))
        interactions = fuzzy_count(_first_of(art, "interactiveCount", default=0))
        return f"🔥{interactions}互动 👍{likes} ⭐{collects} 💬{comments}"
    elif platform == "dy":
        likes = fuzzy_count(_first_of(art, "workLikedCount", "likeCount", "likedCount", default=0))
        comments = fuzzy_count(_first_of(art, "workCommentsCount", "commentCount", "commentsCount", default=0))
        shares = fuzzy_count(_first_of(art, "workSharedCount", "shareCount", "sharedCount", default=0))
        collects = fuzzy_count(_first_of(art, "workCollectedCount", "collectCount", "collectedCount", default=0))
        return f"👍{likes} 💬{comments} ⭐{collects} 🔄{shares}"
    elif platform == "gzh":
        reads = fuzzy_count(_first_of(art, "clicksCount", "readCount", default=0))
        likes = fuzzy_count(_first_of(art, "likeCount", "likedCount", default=0))
        watches = fuzzy_count(_first_of(art, "watchCount", default=0))
        comments = fuzzy_count(_first_of(art, "commentsCount", "commentCount", default=0))
        shares = fuzzy_count(_first_of(art, "shareCount", "sharedCount", default=0))
        return f"📖{reads} 👍{likes} 👁{watches} 💬{comments} 🔄{shares}"
    return ""


def _extract_scores(art: dict) -> dict:
    """提取评分字段（如有关键词搜索评分）"""
    return {
        "total": art.get("totalScore", 0),
        "relevance": art.get("relevanceScore", 0),
        "popularity": art.get("popularityScore", 0),
        "recency": art.get("recencyScore", 0),
    }


# ─── 主搜索函数 ─────────────────────────────────────────────────────────────────────
def search(
    keyword: str,
    platforms: list[str] | None = None,
    count: int = DEFAULT_COUNT,
    api_key: str | None = None,
    days: int = 30,
) -> dict:
    """在多个平台上搜索话题数据"""
    if not platforms:
        platforms = list(PLATFORMS.keys())

    key = get_api_key(api_key)
    results = {}

    # 并行获取各平台数据
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_fetch_platform, p, keyword, count, key, days): p
            for p in platforms
        }
        for future in as_completed(futures):
            p = futures[future]
            try:
                results[p] = future.result()
            except Exception as e:
                results[p] = {
                    "platform": p,
                    "label": PLATFORMS[p]["label"],
                    "items": [],
                    "total": 0,
                    "error": str(e),
                }

    # 汇总统计
    total_items = sum(r["total"] for r in results.values())
    today = datetime.now(timezone.utc)
    return {
        "keyword": keyword,
        "searched_at": today.isoformat(),
        "date_range": {
            "from": (today - timedelta(days=days)).strftime("%Y-%m-%d"),
            "to": today.strftime("%Y-%m-%d"),
        },
        "platforms": results,
        "total_items": total_items,
    }


# ─── JSON 输出 ──────────────────────────────────────────────────────────────────────
def format_as_json(data: dict, max_items: int = 50) -> dict:
    """精简 JSON 格式（供 AI 智能体分析使用）"""
    output = {
        "keyword": data["keyword"],
        "searched_at": data["searched_at"],
        "date_range": data["date_range"],
        "total_items": data["total_items"],
        "platforms": {},
    }

    for pkey, pdata in data["platforms"].items():
        items = []
        for item in pdata.get("items", [])[:max_items]:
            items.append({
                "id": item["id"],
                "platform": item["platform"],
                "title": item["title"],
                "author": item["author"],
                "author_fans": item["author_fans"],
                "published_at": item["published_at"],
                "engagement_display": item["engagement_display"],
                "engagement": item["engagement"],
                "url": item["url"],
                "desc": item["desc"][:200],
                "scores": item.get("scores", {}),
            })
        output["platforms"][pkey] = {
            "label": pdata["label"],
            "total": pdata["total"],
            "items": items,
        }
        if pdata.get("error"):
            output["platforms"][pkey]["error"] = pdata["error"]

    return output


# ─── HTML 报告 ──────────────────────────────────────────────────────────────────────

def _md_to_html(text: str) -> str:
    """简易 Markdown → HTML 转换（无第三方依赖）"""
    import re
    lines = text.split("\n")
    out = []
    in_list = False
    for line in lines:
        stripped = line.strip()
        # 标题
        if stripped.startswith("### "):
            if in_list:
                out.append("</ul>"); in_list = False
            out.append(f'<h4>{stripped[4:]}</h4>')
        elif stripped.startswith("## "):
            if in_list:
                out.append("</ul>"); in_list = False
            out.append(f'<h3>{stripped[2:]}</h3>')
        elif stripped.startswith("# "):
            if in_list:
                out.append("</ul>"); in_list = False
            out.append(f'<h2>{stripped[2:]}</h2>')
        # 分隔线
        elif stripped == "---":
            if in_list:
                out.append("</ul>"); in_list = False
            out.append('<hr>')
        # 无序列表
        elif stripped.startswith("- "):
            if not in_list:
                out.append('<ul>'); in_list = True
            content = _md_inline(stripped[2:])
            out.append(f'<li>{content}</li>')
        # 有序列表
        elif re.match(r'^\d+\.\s', stripped):
            if not in_list:
                out.append('<ol>'); in_list = True
            content = _md_inline(re.sub(r'^\d+\.\s', '', stripped))
            out.append(f'<li>{content}</li>')
        # 空行
        elif not stripped:
            if in_list:
                out.append("</ul>"); in_list = False
            out.append('')
        # 普通段落
        else:
            if in_list:
                out.append("</ul>"); in_list = False
            out.append(f'<p>{_md_inline(stripped)}</p>')
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def _md_inline(text: str) -> str:
    """行内 Markdown 转换：粗体、链接"""
    import re
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" target="_blank">\1</a>', text)
    # **bold**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    return text


def format_as_html(data: dict, max_items: int = 50, report_html: str = "") -> str:
    """生成网站风格 HTML 报告"""
    keyword = data["keyword"]
    total = data["total_items"]
    date_range = data["date_range"]

    # 平台配色和图标
    platform_meta = {
        "xhs": {"primary": "#ff2442", "bg": "#fff1f0", "icon": "📕", "name": "小红书"},
        "dy": {"primary": "#161823", "bg": "#f5f5f5", "icon": "🎵", "name": "抖音"},
        "gzh": {"primary": "#07c160", "bg": "#f0fff4", "icon": "📖", "name": "公众号"},
    }

    # 统计卡片
    stats_html = ""
    for pkey, pdata in data["platforms"].items():
        meta = platform_meta.get(pkey, platform_meta["xhs"])
        ptotal = pdata["total"]
        # 统计总互动
        total_likes = sum(it.get("engagement", {}).get("likes", 0) for it in pdata.get("items", [])[:max_items])
        total_reads = sum(
            it.get("engagement", {}).get("reads", 0) + it.get("engagement", {}).get("likes", 0) + it.get("engagement", {}).get("collects", 0) + it.get("engagement", {}).get("shares", 0) + it.get("engagement", {}).get("comments", 0)
            for it in pdata.get("items", [])[:max_items]
        )
        stats_html += f'''
            <div class="stat-card" style="--p-color: {meta['primary']}; --p-bg: {meta['bg']}">
                <div class="stat-icon">{meta['icon']}</div>
                <div class="stat-body">
                    <div class="stat-label">{meta['name']}</div>
                    <div class="stat-num">{ptotal} <small>条</small></div>
                </div>
            </div>'''

    # 构建 Tab 和内容
    tabs_html = ""
    panels_html = ""
    for pkey, pdata in data["platforms"].items():
        meta = platform_meta.get(pkey, platform_meta["xhs"])
        label = pdata["label"]
        ptotal = pdata["total"]
        is_first = pkey == list(data["platforms"].keys())[0]

        active = " active" if is_first else ""
        tabs_html += f'<button class="tab-btn{active}" data-platform="{pkey}" style="--tab-color: {meta['primary']}">{meta["icon"]} {label} <span class="tab-count">{ptotal}</span></button>\n'

        display = "block" if is_first else "none"
        items = pdata.get("items", [])[:max_items]
        error_html = ""
        if pdata.get("error"):
            error_html = f'<div class="error-banner">⚠️ {pdata["error"]}</div>'

        cards = ""
        for idx, item in enumerate(items):
            title_escaped = item["title"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
            desc_escaped = item["desc"][:200].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") if item["desc"] else ""
            author_escaped = item["author"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

            url_attr = f'href="{item["url"]}"' if item["url"] else 'href="#"'
            author_link = item.get("author_link", "")
            author_html = f'<a href="{author_link}" class="author-link" target="_blank">{author_escaped}</a>' if author_link else f'<span class="author-name">{author_escaped}</span>'

            # 互动数据标签
            eng = item.get("engagement", {})
            eng_tags = ""
            if pkey == "gzh":
                reads = eng.get("reads", 0)
                eng_tags = f'<span class="eng-tag reads">📖 {reads:,}</span>' if reads else ""
            for tag_key, tag_icon in [("likes", "👍"), ("collects", "⭐"), ("comments", "💬"), ("shares", "🔄")]:
                val = eng.get(tag_key, 0)
                if val:
                    eng_tags += f'<span class="eng-tag">{tag_icon} {val:,}</span>'

            cards += f'''
            <div class="card" style="--card-accent: {meta['primary']}">
                <div class="card-rank">{idx + 1}</div>
                <div class="card-body">
                    <a {url_attr} class="card-title" target="_blank">{title_escaped}</a>
                    <div class="card-meta">
                        {author_html}
                        <span class="dot">·</span>
                        <span class="fans">{item["author_fans"]}粉</span>
                        <span class="dot">·</span>
                        <span class="time">{item["published_at"][:10] if item["published_at"] else "--"}</span>
                    </div>
                    {'<p class="card-desc">' + desc_escaped + '</p>' if desc_escaped else ''}
                    <div class="card-footer">
                        <div class="engagement">{eng_tags}</div>
                        <a {url_attr} class="view-btn" target="_blank">查看原文 ↗</a>
                    </div>
                </div>
            </div>'''

        panels_html += f'''
        <div class="tab-panel" id="panel-{pkey}" style="display: {display}">
            {error_html}
            <div class="card-list">
                {cards}
            </div>
            {"<div class='no-data-hint'><p>未查询到相关内容，建议更换关键词重试。</p></div>" if not items else ""}
        </div>'''

    # ── 研究报告区域 ──
    report_section = ""
    if report_html:
        report_section = f'''
    <div class="report-section">
        <h2 class="section-title">📝 研究报告</h2>
        <div class="report-content">{report_html}</div>
    </div>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>cn-last30days · {keyword}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{
            --primary: #4f46e5;
            --primary-light: #e0e7ff;
            --text: #1f2937;
            --text-secondary: #6b7280;
            --border: #e5e7eb;
            --bg: #f9fafb;
            --card-bg: #ffffff;
            --radius: 12px;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Noto Sans SC', Roboto, sans-serif;
            background: var(--bg); color: var(--text); line-height: 1.6;
        }}
        /* ── 导航栏 ── */
        .navbar {{
            background: white; border-bottom: 1px solid var(--border);
            padding: 12px 24px; position: sticky; top: 0; z-index: 100;
            display: flex; align-items: center; gap: 12px;
        }}
        .navbar .logo {{ font-size: 18px; font-weight: 800; color: var(--primary); letter-spacing: -0.5px; }}
        .navbar .logo span {{ color: #ef4444; }}
        .navbar .badge {{
            background: var(--primary-light); color: var(--primary);
            font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 20px;
        }}
        /* ── Hero ── */
        .hero {{
            background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
            color: white; padding: 48px 24px; text-align: center;
        }}
        .hero h1 {{ font-size: 28px; font-weight: 800; margin-bottom: 8px; }}
        .hero .keyword {{
            display: inline-block; background: rgba(255,255,255,0.15); border-radius: 8px;
            padding: 4px 16px; font-size: 16px; margin: 8px 0;
        }}
        .hero .date-range {{ font-size: 14px; opacity: 0.8; }}
        /* ── 统计卡片 ── */
        .stats-row {{
            display: flex; gap: 16px; padding: 24px; max-width: 960px; margin: -28px auto 0;
            position: relative; z-index: 10; flex-wrap: wrap; justify-content: center;
        }}
        .stat-card {{
            background: white; border-radius: var(--radius); padding: 20px 24px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08); flex: 1; min-width: 180px;
            display: flex; align-items: center; gap: 16px; border-left: 4px solid var(--p-color);
        }}
        .stat-icon {{ font-size: 32px; }}
        .stat-label {{ font-size: 13px; color: var(--text-secondary); }}
        .stat-num {{ font-size: 24px; font-weight: 800; color: var(--text); }}
        .stat-num small {{ font-size: 13px; font-weight: 400; color: var(--text-secondary); }}
        /* ── 主内容区 ── */
        .main {{ max-width: 960px; margin: 24px auto; padding: 0 24px; }}
        /* ── Tab ── */
        .tab-bar {{
            display: flex; gap: 4px; background: white; border-radius: var(--radius) var(--radius) 0 0;
            padding: 8px 8px 0; border: 1px solid var(--border); border-bottom: none;
        }}
        .tab-btn {{
            padding: 12px 24px; border: none; background: transparent;
            font-size: 15px; font-weight: 600; cursor: pointer; color: var(--text-secondary);
            border-radius: 8px 8px 0 0; transition: all 0.2s; position: relative;
        }}
        .tab-btn:hover {{ background: var(--bg); color: var(--tab-color); }}
        .tab-btn.active {{
            background: var(--bg); color: var(--tab-color);
        }}
        .tab-btn.active::after {{
            content: ''; position: absolute; bottom: 0; left: 20%; right: 20%;
            height: 3px; background: var(--tab-color); border-radius: 3px 3px 0 0;
        }}
        .tab-count {{
            font-size: 12px; background: var(--bg); padding: 2px 8px;
            border-radius: 10px; font-weight: 500; margin-left: 4px;
        }}
        .tab-btn.active .tab-count {{ background: var(--primary-light); color: var(--tab-color); }}
        /* ── 卡片列表 ── */
        .card-list {{ background: white; border: 1px solid var(--border); border-radius: 0 0 var(--radius) var(--radius); }}
        .card {{
            display: flex; gap: 16px; padding: 20px 24px;
            border-bottom: 1px solid #f3f4f6; transition: background 0.15s;
        }}
        .card:last-child {{ border-bottom: none; }}
        .card:hover {{ background: #fafbfc; }}
        .card-rank {{
            font-size: 20px; font-weight: 800; color: var(--card-accent);
            min-width: 32px; text-align: center; padding-top: 2px; opacity: 0.8;
        }}
        .card-body {{ flex: 1; min-width: 0; }}
        .card-title {{
            font-size: 16px; font-weight: 600; color: var(--text); text-decoration: none;
            line-height: 1.5; display: block; transition: color 0.15s;
        }}
        .card-title:hover {{ color: var(--card-accent); }}
        .card-meta {{ font-size: 13px; color: var(--text-secondary); margin-top: 6px; display: flex; align-items: center; gap: 0; flex-wrap: wrap; }}
        .author-link {{ color: var(--primary); text-decoration: none; font-weight: 500; transition: color 0.15s; }}
        .author-link:hover {{ color: var(--card-accent); text-decoration: underline; }}
        .author-name {{ color: var(--primary); font-weight: 500; }}
        .dot {{ margin: 0 6px; }}
        .card-desc {{ font-size: 14px; color: var(--text-secondary); line-height: 1.6; margin-top: 8px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
        .card-footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 10px; }}
        .engagement {{ display: flex; gap: 8px; flex-wrap: wrap; }}
        .eng-tag {{ font-size: 12px; color: var(--text-secondary); background: #f3f4f6; padding: 2px 8px; border-radius: 4px; }}
        .eng-tag.reads {{ background: #ecfdf5; color: #065f46; }}
        .view-btn {{
            font-size: 13px; color: var(--card-accent); text-decoration: none;
            font-weight: 500; white-space: nowrap; transition: opacity 0.15s;
        }}
        .view-btn:hover {{ opacity: 0.7; }}
        /* ── 其他 ── */
        .error-banner {{
            background: #fef3c7; color: #92400e; padding: 12px 16px;
            border-radius: 8px; margin: 16px 24px; font-size: 14px;
        }}
        .no-data-hint {{ text-align: center; color: var(--text-secondary); padding: 48px; }}
        /* ── 研究报告 ── */
        .report-section {{
            max-width: 960px; margin: 0 auto; padding: 0 24px;
        }}
        .section-title {{
            font-size: 20px; font-weight: 800; color: var(--text); margin-bottom: 16px;
            padding-bottom: 8px; border-bottom: 2px solid var(--primary);
        }}
        .report-content {{
            background: white; border: 1px solid var(--border); border-radius: var(--radius);
            padding: 32px; line-height: 1.8; color: var(--text); font-size: 15px;
        }}
        .report-content h2 {{ font-size: 20px; font-weight: 800; color: var(--primary); margin: 24px 0 12px; }}
        .report-content h3 {{ font-size: 18px; font-weight: 700; color: var(--text); margin: 20px 0 10px; }}
        .report-content h4 {{ font-size: 16px; font-weight: 700; color: var(--text); margin: 16px 0 8px; }}
        .report-content p {{ margin-bottom: 12px; }}
        .report-content strong {{ color: #1e1b4b; }}
        .report-content a {{ color: var(--primary); text-decoration: none; }}
        .report-content a:hover {{ text-decoration: underline; }}
        .report-content ul, .report-content ol {{ margin: 8px 0 12px 20px; }}
        .report-content li {{ margin-bottom: 4px; }}
        .report-content hr {{ border: none; border-top: 1px solid var(--border); margin: 20px 0; }}
        .footer {{
            text-align: center; color: var(--text-secondary); font-size: 12px;
            padding: 32px 24px; margin-top: 16px;
        }}
        .footer a {{ color: var(--primary); text-decoration: none; }}
        /* ── 响应式 ── */
        @media (max-width: 640px) {{
            .hero {{ padding: 32px 16px; }}
            .hero h1 {{ font-size: 20px; }}
            .stats-row {{ padding: 16px; margin-top: -20px; }}
            .stat-card {{ min-width: 140px; padding: 14px 16px; }}
            .stat-num {{ font-size: 20px; }}
            .main {{ padding: 0 12px; }}
            .card {{ padding: 14px 16px; gap: 10px; }}
            .card-rank {{ font-size: 16px; min-width: 24px; }}
            .card-title {{ font-size: 15px; }}
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="logo">🇨🇳 cn<span>-last30days</span></div>
        <div class="badge">v2.0</div>
    </nav>
    <div class="hero">
        <h1>中国社媒话题研究</h1>
        <div class="keyword">{keyword}</div>
        <div class="date-range">{date_range["from"]} ~ {date_range["to"]}</div>
    </div>
    <div class="stats-row">
        {stats_html}
        <div class="stat-card" style="--p-color: var(--primary); --p-bg: var(--primary-light)">
            <div class="stat-icon">📊</div>
            <div class="stat-body">
                <div class="stat-label">合计</div>
                <div class="stat-num">{total} <small>条</small></div>
            </div>
        </div>
    </div>
    {report_section}
    <div class="main">
        <div class="tab-bar">
            {tabs_html}
        </div>
        {panels_html}
    </div>
    <div class="footer">
        数据来源：<a href="https://redfox.hk" target="_blank">redfox.hk</a> API · 小红书 / 抖音 / 公众号 · 近30天热门内容<br>
        互动数据为入库快照，实时数据可能持续增长
    </div>
    <script>
        document.querySelectorAll('.tab-btn').forEach(btn => {{
            btn.addEventListener('click', () => {{
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-panel').forEach(p => p.style.display = 'none');
                btn.classList.add('active');
                document.getElementById('panel-' + btn.dataset.platform).style.display = 'block';
            }});
        }});
    </script>
</body>
</html>'''

    return html


# ─── CLI ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="cn-last30days: 中国社媒平台话题研究工具"
    )
    parser.add_argument("keyword", nargs="?", default="dummy", help="搜索关键词（--from-json 模式下可省略）")
    parser.add_argument(
        "--platforms", "-p",
        default="xhs,dy,gzh",
        help="平台列表，逗号分隔（默认: xhs,dy,gzh）"
    )
    parser.add_argument(
        "--count", "-n",
        type=int,
        default=DEFAULT_COUNT,
        help=f"每个平台获取条数（默认: {DEFAULT_COUNT}）"
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=30,
        help="搜索时间范围，最近多少天（默认: 30，最大: 30）"
    )
    parser.add_argument(
        "--output-format", "-f",
        choices=["json", "html", "both"],
        default="json",
        help="输出格式（默认: json，综合报告后再按需生成HTML）"
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path.home() / "Downloads" / "CnLast30Days"),
        help="HTML 输出目录"
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API Key（覆盖环境变量和配置文件）"
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=50,
        help="输出中最多展示条数（默认: 50）"
    )
    parser.add_argument(
        "--from-json",
        default=None,
        help="从已有 JSON 文件生成 HTML，不调用 API（值: JSON 文件路径）"
    )
    parser.add_argument(
        "--report-file",
        default=None,
        help="研究报告 Markdown 文件路径（嵌入到 HTML 报告顶部）"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="调试模式，打印原始 API 响应"
    )

    args = parser.parse_args()

    # ── 从 JSON 生成 HTML 模式 ──
    if args.from_json:
        json_path = Path(args.from_json)
        if not json_path.exists():
            sys.stderr.write(f"错误: JSON 文件不存在: {json_path}\n")
            sys.exit(1)
        raw = json.loads(json_path.read_text(encoding="utf-8"))
        # 从精简 JSON 反向构造 data 结构
        data = {
            "keyword": raw.get("keyword", ""),
            "total_items": raw.get("total_items", 0),
            "date_range": raw.get("date_range", {}),
            "platforms": {},
        }
        for pkey, pdata in raw.get("platforms", {}).items():
            items = []
            for it in pdata.get("items", []):
                item = dict(it)
                item["source"] = pkey
                items.append(item)
            data["platforms"][pkey] = {
                "label": pdata.get("label", pkey),
                "total": pdata.get("total", len(items)),
                "items": items,
            }
        # 读取研究报告
        report_html = ""
        if args.report_file:
            report_path = Path(args.report_file)
            if report_path.exists():
                report_md = report_path.read_text(encoding="utf-8")
                report_html = _md_to_html(report_md)
            else:
                sys.stderr.write(f"⚠️ 报告文件不存在: {report_path}，跳过\n")
        html_content = format_as_html(data, max_items=args.max_items, report_html=report_html)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        base_name = json_path.stem  # 用原 JSON 文件名
        html_file = output_dir / f"{base_name}.html"
        html_file.write_text(html_content, encoding="utf-8")
        sys.stderr.write(f"✅ HTML 已保存: {html_file}\n")
        print(json.dumps({"files": {"html": str(html_file)}}, ensure_ascii=False))
        return

    # ── 正常搜索模式 ──
    # 解析平台列表
    platforms = []
    for p in args.platforms.split(","):
        p = p.strip().lower()
        if p in PLATFORMS:
            platforms.append(p)
        else:
            sys.stderr.write(f"未知平台: {p}，可用: {', '.join(PLATFORMS.keys())}\n")
    if not platforms:
        sys.stderr.write("错误: 未指定有效平台\n")
        sys.exit(1)

    # 执行搜索
    keyword = args.keyword.strip()
    if not keyword:
        sys.stderr.write("错误: 关键词不能为空\n")
        sys.exit(1)

    sys.stderr.write(f"\n{'='*60}\n")
    sys.stderr.write(f"cn-last30days · 搜索: {keyword}\n")
    sys.stderr.write(f"平台: {', '.join(PLATFORMS[p]['label'] for p in platforms)}\n")
    sys.stderr.write(f"每平台: {args.count} 条 | 时间: 近{args.days}天\n")
    sys.stderr.write(f"{'='*60}\n\n")
    sys.stderr.flush()

    try:
        data = search(
            keyword=keyword,
            platforms=platforms,
            count=args.count,
            api_key=args.api_key,
            days=args.days,
        )
    except Exception as e:
        sys.stderr.write(f"\n❌ 搜索失败: {e}\n")
        sys.exit(1)

    # 准备输出目录和文件名
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    keyword_safe = keyword.replace('"', '').replace(' ', '_')[:30]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"cn30days_{keyword_safe}_{timestamp}"

    # 保存 JSON
    json_file = None
    if args.output_format in ("json", "both"):
        json_data = format_as_json(data, max_items=args.max_items)
        json_file = output_dir / f"{base_name}.json"
        json_file.write_text(
            json.dumps(json_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        sys.stderr.write(f"\n✅ JSON 已保存: {json_file}\n")

    # 保存 HTML
    html_file = None
    if args.output_format in ("html", "both"):
        html_content = format_as_html(data, max_items=args.max_items)
        html_file = output_dir / f"{base_name}.html"
        html_file.write_text(html_content, encoding="utf-8")
        sys.stderr.write(f"✅ HTML 已保存: {html_file}\n")

    # 统计（stderr，不影响 stdout）
    sys.stderr.write(f"\n{'='*60}\n")
    sys.stderr.write(f"搜索完成！共 {data['total_items']} 条结果\n")
    for pkey, pdata in data["platforms"].items():
        status = f"✅ {pdata['total']} 条" if not pdata.get("error") else f"❌ {pdata['error']}"
        sys.stderr.write(f"  {pdata['label']}: {status}\n")
    sys.stderr.write(f"{'='*60}\n")
    sys.stderr.flush()

    # stdout 输出简洁摘要（供 AI 智能体解析，单行 JSON）
    summary = {
        "keyword": keyword,
        "date_range": data["date_range"],
        "total_items": data["total_items"],
        "platforms": {p: v["total"] for p, v in data["platforms"].items()},
        "files": {},
    }
    if json_file:
        summary["files"]["json"] = str(json_file)
    if html_file:
        summary["files"]["html"] = str(html_file)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
