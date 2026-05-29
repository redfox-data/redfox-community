#!/usr/bin/env python3
"""
抖音爆款作品搜索脚本
调用 Redfox API 搜索抖音热门作品数据
用法: python3 search_douyin.py "<关键词>"
"""

import sys
import os
import json
import urllib.request
import urllib.error

API_URL = "https://redfox.hk/story/api/dy/search/search"


def get_api_key() -> str:
    """从环境变量获取 API Key，"""
    for key_name in ["REDFOX_API_KEY"]:
        val = os.environ.get(key_name)
        if val:
            return val
    print("[error] 未找到环境变量 REDFOX_API_KEY，请确认已设置 API Key", file=sys.stderr)
    sys.exit(1)


def search(keyword: str) -> list:
    """调用搜索接口，返回作品列表"""
    api_key = get_api_key()
    payload = json.dumps({"keyword": keyword, "source": "抖音作品查询-GitHub"}).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
            "User-Agent": "QoderWork/1.0",
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
    articles = data.get("articles") or []

    # 提取需要的字段并统一格式
    items = []
    for art in articles:
        items.append({
            "title": art.get("title", "").strip(),
            "author": art.get("accountName", "").strip(),
            "like_count": art.get("likeCount", 0) or 0,
            "comment_count": art.get("commentCount", 0) or 0,
            "share_count": art.get("shareCount", 0) or 0,
            "collect_count": art.get("collectCount", 0) or 0,
            "work_url": art.get("workUrl", ""),
            "publish_time": art.get("publishTime", ""),
            "follower_count": art.get("followerCount", 0) or 0,
        })

    # 按点赞数降序排列
    items.sort(key=lambda x: x["like_count"], reverse=True)
    return items


def main():
    if len(sys.argv) < 2:
        print("用法: python3 search_douyin.py \"<关键词>\"", file=sys.stderr)
        sys.exit(1)

    keyword = sys.argv[1].strip()
    if not keyword:
        print("[error] 关键词不能为空", file=sys.stderr)
        sys.exit(1)

    items = search(keyword)
    print(json.dumps(items, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
