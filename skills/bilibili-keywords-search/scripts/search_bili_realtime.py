#!/usr/bin/env python3
"""
B站关键词实时搜索脚本
调用 Redfox API 实时搜索B站视频数据
用法: python3 search_bili_realtime.py "<关键词>" [--sort 排序] [--time 时间] [--page 页码]

接口返回字段说明（opusInfoList 中每条）：
  bvId / avId   视频 BV号 / AV号
  url           完整视频链接（有效，直接使用）
  title         标题（含<em class="keyword">高亮标签，需清洗）
  nickname      UP主昵称
  likeNum       点赞数
  commentNum    评论数
  collectNum    收藏数
  viewNum       播放量
  danmakuCount  弹幕数
  cover         封面（相对协议 //i0.hdslb.com/...，需补 https:）
  publishTime   发布时间戳（秒级）
  tags          标签（逗号分隔字符串）
  categoryName  分区名称
  duration      视频时长（秒）
"""

import sys
import os
import re
import json
import argparse
import urllib.request
import urllib.error
from datetime import datetime

API_URL = "https://redfox.hk/story/api/bili/search"

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


def clean_title(title: str) -> str:
    """清洗 B站搜索结果标题，采用五层清洗链：
    1. 清除 HTML 标签（如 <em class="keyword"> 高亮标签）
    2. 清除所有 Unicode 空白字符（含普通空格、制表符、换行等）
    3. 清除全角空格、不间断空格、零宽空格
    4. 清除零宽字符、格式字符、控制字符
    5. 将半角方括号 [] 替换为中文方括号 【】，避免与 Markdown 链接语法冲突
    """
    text = re.sub(r"<[^>]+>", "", title)           # 1. 清除HTML标签
    text = re.sub(r"\s+", "", text)                 # 2. 清除所有Unicode空白
    text = re.sub(r"[  \u00a0\u200b]", "", text)  # 3. 清除全角/不间断/零宽空格
    text = re.sub(r"[\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\u0000-\u001f\u007f-\u009f]", "", text)  # 4. 清除零宽/格式/控制字符
    text = text.replace("[", "【").replace("]", "】")  # 5. [] → 【】
    return text.strip()


def normalize_cover(cover: str) -> str:
    """补全相对协议封面链接"""
    if cover and cover.startswith("//"):
        return "https:" + cover
    return cover or ""


def build_video_url(item: dict) -> str:
    """优先使用 url 字段；若为空则用 bvId 拼接标准 B站链接"""
    url = item.get("url", "")
    if url:
        return url
    bv_id = item.get("bvId", "")
    if bv_id:
        return f"https://www.bilibili.com/video/{bv_id}"
    return ""


def fmt_publish_time(ts) -> str:
    """秒级时间戳转可读日期"""
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)


def format_articles(articles: list) -> list:
    items = []
    for art in articles:
        items.append({
            "title":          clean_title(art.get("title", "")),
            "author":         art.get("nickname", "").strip(),
            "like_count":     art.get("likeNum", 0) or 0,
            "comment_count":  art.get("commentNum", 0) or 0,
            "collect_count":  art.get("collectNum", 0) or 0,
            "play_count":     art.get("viewNum", 0) or 0,
            "danmaku_count":  art.get("danmakuCount", 0) or 0,
            "work_url":       build_video_url(art),
            "publish_time":   fmt_publish_time(art.get("publishTime", 0)),
            "cover_url":      normalize_cover(art.get("cover", "")),
            "tags":           art.get("tags", ""),
            "category":       art.get("categoryName", ""),
        })
    items.sort(key=lambda x: x["like_count"], reverse=True)
    return items


def search(keyword: str, sort_type: str, publish_time: str, page: int = 1) -> dict:
    api_key = get_api_key()
    payload = json.dumps({
        "keyword":     keyword,
        "sortType":    sort_type,
        "publishTime": publish_time,
        "page":        page,
        "source":      "B站关键词搜作品-GitHub",
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
    articles_list = data.get("opusInfoList") or []
    total_pages = data.get("pages", 1) or 1
    has_next = page < total_pages

    return {
        "articles":           format_articles(articles_list),
        "sort_type_label":    SORT_TYPE_MAP.get(sort_type, sort_type),
        "publish_time_label": PUBLISH_TIME_MAP.get(publish_time, publish_time),
        "page":               page,
        "total_pages":        total_pages,
        "has_next":           has_next,
    }


def main():
    parser = argparse.ArgumentParser(description="B站关键词搜作品")
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
