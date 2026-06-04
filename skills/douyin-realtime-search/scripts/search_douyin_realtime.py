#!/usr/bin/env python3
"""
抖音作品实时搜索脚本
调用 Redfox API 实时搜索抖音作品数据
用法: python3 search_douyin_realtime.py "<关键词>" [--sort 3] [--time 7] [--page 1]
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error

API_URL = "https://redfox.hk/story/api/dy/search/openSearch"

# sortType 枚举
SORT_TYPE_MAP = {
    "1": "综合排序",
    "2": "最新发布",
    "3": "最多点赞",
}

# publishTime 枚举
PUBLISH_TIME_MAP = {
    "7":  "最近7天",
    "30": "最近30天",
    "90": "最近90天",
    "0":  "不限",
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
        items.append({
            "title":          art.get("description", "").strip(),
            "author":         art.get("nickname", "").strip(),
            "like_count":     art.get("likeNum", 0) or 0,
            "comment_count":  art.get("commentNum", 0) or 0,
            "share_count":    art.get("shareNum", 0) or 0,
            "collect_count":  art.get("collectNum", 0) or 0,
            "work_url":       art.get("url", ""),
            "publish_time":   art.get("publishTime", ""),
            "follower_count": art.get("fansNum", 0) or 0,
        })
    items.sort(key=lambda x: x["like_count"], reverse=True)
    return items


def search(keyword: str, sort_type: str, publish_time: str, page: int = 1) -> dict:
    api_key = get_api_key()
    payload = json.dumps({
        "keyword":     keyword,
        "sortType":    sort_type,
        "publishTime": publish_time,
        "offset":      page - 1,
        "source":      "抖音作品实时搜索-GitHub",
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
        with urllib.request.urlopen(req, timeout=15) as resp:
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
    articles_list = data.get("list") or []
    articles_count = len(articles_list)

    # 翻页逻辑：当前页正好 9 条 → 有下一页；不足 9 条或为空 → 已是最后一页
    has_next = articles_count == 9

    return {
        "articles":           format_articles(articles_list),
        "latestHotArticles":  format_articles(data.get("latestHotArticles") or []),
        "hotTopics":          data.get("hotTopics") or [],
        "sort_type_label":    SORT_TYPE_MAP.get(sort_type, sort_type),
        "publish_time_label": PUBLISH_TIME_MAP.get(publish_time, publish_time),
        "page":               page,
        "has_next":           has_next,
    }


def main():
    parser = argparse.ArgumentParser(description="抖音作品实时搜索")
    parser.add_argument("keyword", help="搜索关键词，多个词用英文逗号连接")
    parser.add_argument(
        "--sort", dest="sort_type", default="1",
        choices=["1", "2", "3"],
        help="排序方式：1-综合排序 2-最新发布 3-最多点赞（默认1）",
    )
    parser.add_argument(
        "--time", dest="publish_time", default="7",
        choices=["7", "30", "90", "0"],
        help="发布时间筛选：7-最近7天 30-最近30天 90-最近90天 0-不限（默认7）",
    )
    parser.add_argument(
        "--page", dest="page", type=int, default=1,
        help="页码，从1开始（默认1）",
    )
    args = parser.parse_args()

    keyword = args.keyword.strip()
    if not keyword:
        print("[error] 关键词不能为空", file=sys.stderr)
        sys.exit(1)
    if args.page < 1:
        print("[error] 页码必须为正整数", file=sys.stderr)
        sys.exit(1)

    result = search(keyword, args.sort_type, args.publish_time, args.page)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
