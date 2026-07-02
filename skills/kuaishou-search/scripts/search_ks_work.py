#!/usr/bin/env python3
"""
快手作品搜索脚本
调用 Redfox API 搜索快手作品数据
用法: python3 search_ks_work.py "<关键词>" [--sort 最多点赞] [--note-time 一个月内] [--page 1] [--start-time YYYY-M-D] [--end-time YYYY-M-D]
"""

import sys
import os
import json
import argparse
import time as _time
import urllib.request
import urllib.error
from datetime import datetime, timedelta

API_URL = "https://redfox.hk/story/api/ks/search/keywordSearchWork"

# 排序方式枚举
SORT_MAP = {
    "综合":     "综合排序",
    "最新":     "最新发布",
    "最多点赞": "最多点赞",
    "最多评论": "最多评论",
    "最多收藏": "最多收藏",
    "最多播放": "最多播放",
}

# 时间范围枚举
NOTE_TIME_MAP = {
    "不限":     "不限",
    "一天内":   "一天内",
    "一周内":   "一周内",
    "一个月内": "一个月内",
    "一年内":   "一年内",
}


def compute_date_range(note_time: str):
    """根据 noteTime 语义计算精确的 startTime 和 endTime。
    规则：取满开始时间（含当天），不取满结束时间（取次日）。
    例如：今天 → 2026-7-1 ~ 2026-7-2
    """
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    def fmt(d):
        return f"{d.year}-{d.month}-{d.day}"

    if note_time == "不限":
        return "", ""
    elif note_time == "一天内":
        return fmt(today), fmt(tomorrow)
    elif note_time == "一周内":
        return fmt(today - timedelta(days=7)), fmt(tomorrow)
    elif note_time == "一个月内":
        return fmt(today - timedelta(days=30)), fmt(tomorrow)
    elif note_time == "一年内":
        return fmt(today - timedelta(days=365)), fmt(tomorrow)
    else:
        return "", ""


def get_api_key() -> str:
    val = os.environ.get("REDFOX_API_KEY", "")
    if not val:
        print("[error] 未找到环境变量 REDFOX_API_KEY，请确认已设置 API Key", file=sys.stderr)
        sys.exit(1)
    return val


def format_articles(articles: list) -> list:
    items = []
    for art in articles:
        # releaseTime 可能是日期字符串（如 "2026-06-24 18:00:00"）或 Unix 时间戳
        rt_raw = art.get("releaseTime") or art.get("publishTime") or ""
        publish_time = ""
        publish_date = ""
        if rt_raw:
            rt_str = str(rt_raw).strip()
            # 尝试按日期字符串解析
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(rt_str, fmt)
                    publish_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    publish_date = dt.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
            # 若日期字符串解析失败，尝试按 Unix 时间戳解析
            if not publish_time:
                try:
                    ts = int(rt_raw)
                    if ts > 0:
                        publish_time = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime(ts))
                        publish_date = _time.strftime("%Y-%m-%d", _time.localtime(ts))
                except (ValueError, TypeError):
                    pass

        # 标题中可能存在 | 字符，需转义避免破坏 Markdown 表格列分隔
        raw_title = (art.get("caption") or art.get("workTitle") or art.get("title") or "").strip() or "-"
        safe_title = raw_title.replace("|", "\\|")

        items.append({
            "title":          safe_title,
            "author":         (art.get("authorName") or "").strip() or "-",
            "author_url":     "",
            "play_count":     art.get("playCount") or art.get("viewCount") or 0,
            "like_count":     art.get("likeCount") or art.get("thumbCount") or 0,
            "comment_count":  art.get("commentCount") or art.get("replyCount") or 0,
            "collect_count":  art.get("collectCount") or art.get("favoriteCount") or 0,
            "work_url":       art.get("workUrl") or "",
            "publish_time":   publish_time,
            "publish_date":   publish_date,
            "work_id":        art.get("workId") or art.get("noteId") or "",
        })
    return items


def search(keyword: str, sort: str, note_time: str, page: int = 1,
           start_time: str = "", end_time: str = "") -> dict:
    api_key = get_api_key()

    # 若未显式传入起止时间，则根据 noteTime 自动计算
    if not start_time and not end_time:
        start_time, end_time = compute_date_range(note_time)

    payload = json.dumps({
        "keyword":   keyword,
        "sort":      sort,
        "noteTime":  note_time,
        "page":      page,
        "startTime": start_time,
        "endTime":   end_time,
        "source":    "快手作品搜索-GitHub",
    }).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key":    api_key,
            "User-Agent":   "QoderWork/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[error] HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[error] 网络请求失败: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"[error] 数据解析异常: {e}", file=sys.stderr)
        sys.exit(1)

    code = result.get("code")
    if code != 2000:
        print(f"[error] 接口返回错误: code={code}, msg={result.get('msg', '未知')}", file=sys.stderr)
        sys.exit(1)

    data = result.get("data") or {}
    articles_list = data.get("workList") or []
    articles_count = len(articles_list)

    # 翻页逻辑：当前页不足 20 条 → 已是最后一页；达到 20 条 → 有下一页
    has_next = articles_count >= 20

    return {
        "articles":        format_articles(articles_list),
        "sort_label":      SORT_MAP.get(sort, sort),
        "note_time_label": NOTE_TIME_MAP.get(note_time, note_time),
        "page":            page,
        "has_next":        has_next,
        "total":           data.get("total", articles_count),
        "start_time":      start_time,
        "end_time":        end_time,
    }


def main():
    parser = argparse.ArgumentParser(description="快手作品搜索")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument(
        "--sort", dest="sort", default="最多点赞",
        choices=["综合", "最新", "最多点赞", "最多评论", "最多收藏", "最多播放"],
        help="排序方式（默认：最多点赞）",
    )
    parser.add_argument(
        "--note-time", dest="note_time", default="一个月内",
        choices=["不限", "一天内", "一周内", "一个月内", "一年内"],
        help="发布时间筛选（默认：一个月内）",
    )
    parser.add_argument(
        "--page", dest="page", type=int, default=1,
        help="页码，从 1 开始（默认：1）",
    )
    parser.add_argument(
        "--start-time", dest="start_time", default="",
        help="开始时间，格式 YYYY-M-D（默认根据 note-time 自动计算）",
    )
    parser.add_argument(
        "--end-time", dest="end_time", default="",
        help="结束时间，格式 YYYY-M-D（默认根据 note-time 自动计算）",
    )
    args = parser.parse_args()

    keyword = args.keyword.strip()
    if not keyword:
        print("[error] 关键词不能为空", file=sys.stderr)
        sys.exit(1)
    if args.page < 1:
        print("[error] 页码必须为正整数", file=sys.stderr)
        sys.exit(1)

    result = search(keyword, args.sort, args.note_time, args.page,
                    args.start_time, args.end_time)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
