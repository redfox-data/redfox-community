#!/usr/bin/env python3
"""
小红书作品搜索脚本
调用 Redfox API 搜索小红书作品数据
用法: python3 search_xhs_work.py "<关键词>" [--sort 最多点赞] [--note-time 一个月内] [--note-type 不限] [--page 1]
"""

import sys
import os
import json
import argparse
import time as _time
import urllib.request
import urllib.error

API_URL = "https://redfox.hk/story/api/xhs/ability/searchWork"

# 排序方式枚举
SORT_MAP = {
    "综合":     "综合排序",
    "最新":     "最新发布",
    "最多点赞": "最多点赞",
    "最多评论": "最多评论",
    "最多收藏": "最多收藏",
}

# 时间范围枚举
NOTE_TIME_MAP = {
    "不限":     "不限",
    "一天内":   "一天内",
    "一周内":   "一周内",
    "一个月内": "一个月内",
    "一年内":   "一年内",
}

# 笔记类型枚举
NOTE_TYPE_MAP = {
    "不限":   "不限",
    "视频笔记": "视频笔记",
    "普通笔记": "普通笔记",
}


def get_api_key() -> str:
    val = os.environ.get("REDFOX_API_KEY", "")
    if not val:
        print("[error] 未找到环境变量 REDFOX_API_KEY，请确认已设置 API Key", file=sys.stderr)
        sys.exit(1)
    return val


def format_articles(articles: list) -> list:
    items = []
    for art in articles:
        # releaseTime 是 Unix 时间戳（秒），转换为可读格式
        rt = art.get("releaseTime", 0)
        if rt and rt > 0:
            publish_time = _time.strftime("%Y-%m-%d %H:%M", _time.localtime(rt))
            publish_date = _time.strftime("%Y-%m-%d", _time.localtime(rt))
        else:
            publish_time = ""
            publish_date = ""

        # 标题中可能存在 | 字符，需转义避免破坏 Markdown 表格列分隔
        raw_title = (art.get("noteTitle") or "").strip() or "-"
        # 转义 | 为 \|，防止 Markdown 表格渲染错乱
        safe_title = raw_title.replace("|", "\\|")

        # 构造作者主页链接
        author_uid = (art.get("authorUid") or "").strip()
        author_url = f"https://www.xiaohongshu.com/user/profile/{author_uid}" if author_uid else ""

        items.append({
            "title":          safe_title,
            "author":         (art.get("authorName") or "").strip() or "-",
            "author_url":     author_url,
            "like_count":     art.get("thumbCount", 0) or 0,
            "comment_count":  art.get("replyCount", 0) or 0,
            "share_count":    art.get("forwardCount", 0) or 0,
            "collect_count":  art.get("favoriteCount", 0) or 0,
            "work_url":       art.get("noteUrl") or "",
            "publish_time":   publish_time,
            "publish_date":   publish_date,
            "follower_count": art.get("authorFans", 0) or 0,
            "work_id":        art.get("noteId") or "",
        })
    return items


def search(keyword: str, sort: str, note_time: str, note_type: str, page: int = 1) -> dict:
    api_key = get_api_key()
    payload = json.dumps({
        "keyword":   keyword,
        "sort":      sort,
        "noteTime":  note_time,
        "note_type": note_type,
        "page":      page,
        "source":    "小红书作品搜索-GitHub",
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
        "note_type_label": NOTE_TYPE_MAP.get(note_type, note_type),
        "page":            page,
        "has_next":        has_next,
        "total":           data.get("total", articles_count),
    }


def main():
    parser = argparse.ArgumentParser(description="小红书作品搜索")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument(
        "--sort", dest="sort", default="最多点赞",
        choices=["综合", "最新", "最多点赞", "最多评论", "最多收藏"],
        help="排序方式（默认：最多点赞）",
    )
    parser.add_argument(
        "--note-time", dest="note_time", default="一个月内",
        choices=["不限", "一天内", "一周内", "一个月内", "一年内"],
        help="发布时间筛选（默认：一个月内）",
    )
    parser.add_argument(
        "--note-type", dest="note_type", default="不限",
        choices=["不限", "视频笔记", "普通笔记"],
        help="笔记类型筛选（默认：不限）",
    )
    parser.add_argument(
        "--page", dest="page", type=int, default=1,
        help="页码，从 1 开始（默认：1）",
    )
    args = parser.parse_args()

    keyword = args.keyword.strip()
    if not keyword:
        print("[error] 关键词不能为空", file=sys.stderr)
        sys.exit(1)
    if args.page < 1:
        print("[error] 页码必须为正整数", file=sys.stderr)
        sys.exit(1)

    result = search(keyword, args.sort, args.note_time, args.note_type, args.page)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
