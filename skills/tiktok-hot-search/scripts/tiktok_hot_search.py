#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TikTok 热门搜索（视频 / 用户 / 话题）。

一次输入关键词，按需获取热门视频、相关用户与相关话题列表。

用法：
  python scripts/tiktok_hot_search.py --keyword "NVIDIA" --type all --count 10
  python scripts/tiktok_hot_search.py --keyword "camping gear" --type video --sort likes --publish 7
  python scripts/tiktok_hot_search.py --keyword "手冲咖啡" --type user --fans 3 --verified
  python scripts/tiktok_hot_search.py --keyword "cat" --type topic
  python scripts/tiktok_hot_search.py --keyword "NVIDIA" --type video --offset 10 --count 10

API Key 优先级：--api-key > REDFOX_API_KEY 环境变量 > shell 配置文件。
"""

import argparse
import json
import os
import re
import socket
import ssl
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

HOST = "redfox.hk"
ENDPOINTS = {
    "video": "/story/api/tiktok/ability/searchVideo",
    "user": "/story/api/tiktok/ability/searchUser",
    "topic": "/story/api/tiktok/ability/searchTopic",
}
LABELS = {"video": "视频", "user": "相关用户", "topic": "相关话题"}
SOURCE = "TikTok热门搜索-GitHub"  # 接口请求携带的来源标识
API_KEY_REMINDER = "获取 API Key：前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github)"

VIDEO_SORT_KEYS = {
    "none": None,
    "views": "viewCount",
    "likes": "likeCount",
    "comments": "commentTotal",
    "shares": "shareTotal",
}
VIDEO_SORT_LABELS = {
    "views": "按播放数降序",
    "likes": "按点赞数降序",
    "comments": "按评论数降序",
    "shares": "按分享数降序",
    "none": "按原始相关度顺序",
}
BEIJING = timezone(timedelta(hours=8))


class ApiError(RuntimeError):
    """业务状态码异常（code 非 2000）。"""

    def __init__(self, code: Any, msg: Any) -> None:
        self.code = code
        self.msg = msg
        super().__init__(f"接口返回异常：code={code}, msg={msg}")


def _extract_api_key_from_config(filepath: str) -> Optional[str]:
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                if "REDFOX_API_KEY" not in line:
                    continue
                match = re.search(r"REDFOX_API_KEY\s*[=:]\s*[\"']?([^\s\"'#]+)[\"']?", line.strip())
                if match:
                    return match.group(1)
    except (OSError, UnicodeDecodeError):
        return None
    return None


def resolve_api_key(cli_key: Optional[str]) -> str:
    if cli_key:
        return cli_key
    env_key = os.getenv("REDFOX_API_KEY")
    if env_key:
        return env_key

    home = os.path.expanduser("~")
    for path in [
        os.path.join(home, ".zshrc"),
        os.path.join(home, ".bashrc"),
        os.path.join(home, ".bash_profile"),
        os.path.join(home, ".profile"),
    ]:
        key = _extract_api_key_from_config(path)
        if key:
            return key

    raise ValueError(
        "缺少 REDFOX_API_KEY。请设置环境变量：export REDFOX_API_KEY=<你的apikey>，"
        "或使用 --api-key ak_xxxxxxxx 临时传入。"
    )


def post_redfox_no_sni(endpoint: str, payload: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = (
        f"POST {endpoint} HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        f"X-API-KEY: {api_key}\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n"
        "\r\n"
    ).encode("utf-8") + body

    context = ssl.create_default_context()
    # redfox.hk 当前链路实测需要无 SNI；保留证书链校验，仅关闭 hostname 检查以兼容无 SNI。
    context.check_hostname = False

    with socket.create_connection((HOST, 443), timeout=30) as sock:
        with context.wrap_socket(sock, server_hostname=None) as ssock:
            ssock.sendall(request)
            chunks = []
            while True:
                chunk = ssock.recv(65536)
                if not chunk:
                    break
                chunks.append(chunk)

    raw = b"".join(chunks).decode("utf-8", "replace")
    header, _, response_body = raw.partition("\r\n\r\n")
    status_line = header.split("\r\n", 1)[0] if header else ""
    if " 200 " not in status_line:
        if " 502 " in status_line:
            raise RuntimeError("服务返回 502 错误，可能存在网络不稳定问题，请稍后重试")
        raise RuntimeError(f"HTTP 请求失败：{status_line}")

    try:
        return json.loads(response_body)
    except json.JSONDecodeError as exc:
        preview = response_body[:300].replace("\n", " ")
        raise RuntimeError(f"响应不是有效 JSON：{preview}") from exc


def call_api(kind: str, payload: Dict[str, Any], api_key: str) -> Any:
    result = post_redfox_no_sni(ENDPOINTS[kind], payload, api_key)
    code = result.get("code")
    if code != 2000:
        raise ApiError(code, result.get("msg", ""))
    return result.get("data")


def build_payload(kind: str, args: argparse.Namespace) -> Dict[str, Any]:
    if kind == "video":
        return {
            "keyword": args.keyword,
            "offset": str(args.offset),
            "count": str(args.count),
            "sortType": "1" if args.sort == "likes" else "0",
            "publishTime": args.publish,
            "region": args.region,
            "source": SOURCE,
        }
    if kind == "user":
        payload: Dict[str, Any] = {
            "keyword": args.keyword,
            "offset": str(args.offset),
            "count": str(args.count),
            "source": SOURCE,
        }
        if args.fans:
            payload["followerCountFilter"] = args.fans
        if args.verified:
            payload["profileTypeFilter"] = 1
        return payload
    return {"keyword": args.keyword, "offset": args.offset, "source": SOURCE}


def fmt_num(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def fmt_time(value: Any) -> str:
    try:
        ts = int(value)
    except (TypeError, ValueError):
        return "-"
    if ts <= 0:
        return "-"
    if ts > 10 ** 12:  # 兼容毫秒时间戳
        ts //= 1000
    return datetime.fromtimestamp(ts, tz=BEIJING).strftime("%Y-%m-%d")


def escape_md(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("\n", " ").replace("|", "\\|").strip()


def summarize(text: Any, limit: int = 60) -> str:
    s = escape_md(text)
    return s if len(s) <= limit else s[: limit - 3] + "..."


def extract_video_items(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("workList", "list", "videoList", "items"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    return []


def sort_videos(items: List[Dict[str, Any]], sort_name: str) -> List[Dict[str, Any]]:
    key = VIDEO_SORT_KEYS.get(sort_name)
    if not key:
        return items
    return sorted(
        items,
        key=lambda item: ((item.get("statsData") or {}).get(key) or 0),
        reverse=True,
    )


def render_video(data: Any, args: argparse.Namespace) -> str:
    items = sort_videos(extract_video_items(data), args.sort)
    lines = [f"### 视频（{VIDEO_SORT_LABELS[args.sort]}）"]
    info = f"视频：offset：{args.offset} | count：{args.count} | 本页：{len(items)} 条"
    if items:
        info += f" | 下一页 offset：{args.offset + args.count}"
    lines.append(info)
    lines.append("")
    if not items:
        lines.append("暂无数据")
        return "\n".join(lines)

    lines.append("| # | 作者 | 作品 ID | 播放 | 点赞 | 评论 | 分享 | 发布时间 | 作品链接 | 内容摘要 |")
    lines.append("|---:|---|---|---:|---:|---:|---:|---|---|---|")
    for idx, item in enumerate(items, 1):
        author = item.get("authorData") or {}
        stats = item.get("statsData") or {}
        handle = escape_md(author.get("userHandle"))
        name = escape_md(author.get("userName"))
        author_cell = f"{name} / `{handle}`" if handle else name
        share_link = item.get("shareLink") or ""
        link_cell = f"[打开作品]({share_link})" if share_link else "暂无链接"
        lines.append(
            "| {idx} | {author} | `{work_id}` | {views} | {likes} | {comments} | {shares} | {date} | {link} | {content} |".format(
                idx=idx,
                author=author_cell,
                work_id=escape_md(item.get("workId")),
                views=fmt_num(stats.get("viewCount")),
                likes=fmt_num(stats.get("likeCount")),
                comments=fmt_num(stats.get("commentTotal")),
                shares=fmt_num(stats.get("shareTotal")),
                date=fmt_time(item.get("publishTime")),
                link=link_cell,
                content=summarize(item.get("content")),
            )
        )
    return "\n".join(lines)


def render_user(data: Any, args: argparse.Namespace) -> str:
    data = data if isinstance(data, dict) else {}
    items = data.get("userList") or []
    items = sorted(items, key=lambda item: (item.get("fansCount") or 0), reverse=True)
    cursor = data.get("cursor")
    has_more = data.get("hasMore")

    lines = ["### 相关用户（按粉丝数降序）"]
    info = f"相关用户：offset：{args.offset} | count：{args.count} | 本页：{len(items)} 条"
    if items:
        info += f" | hasMore：{has_more} | 下一页 offset：{cursor}"
    lines.append(info)
    lines.append("")
    if not items:
        lines.append("暂无数据")
        return "\n".join(lines)

    lines.append("| # | 昵称 | TikTok号 | 粉丝数 | 获赞总数 | 作品数 | 主页链接 |")
    lines.append("|---:|---|---|---:|---:|---:|---|")
    for idx, user in enumerate(items, 1):
        handle = escape_md(user.get("userHandle"))
        link_cell = f"[打开主页](https://www.tiktok.com/@{handle})" if handle else "暂无链接"
        lines.append(
            "| {idx} | {name} | {handle} | {fans} | {liked} | {works} | {link} |".format(
                idx=idx,
                name=escape_md(user.get("userName")),
                handle=handle,
                fans=fmt_num(user.get("fansCount")),
                liked=fmt_num(user.get("likedTotal")),
                works=fmt_num(user.get("workCount")),
                link=link_cell,
            )
        )
    return "\n".join(lines)


def render_topic(data: Any, args: argparse.Namespace) -> str:
    data = data if isinstance(data, dict) else {}
    items = data.get("topicList") or []
    items = sorted(items, key=lambda item: (item.get("viewCount") or 0), reverse=True)
    next_cursor = data.get("nextCursor")
    has_more = data.get("hasMore")

    lines = ["### 相关话题（按浏览量降序）"]
    info = f"相关话题：offset：{args.offset} | 本页：{len(items)} 条"
    if items:
        info += f" | hasMore：{has_more} | 下一页 offset：{next_cursor}"
    lines.append(info)
    lines.append("")
    if not items:
        lines.append("暂无数据")
        return "\n".join(lines)

    lines.append("| # | 话题 | 话题 ID | 浏览量 | 使用次数 | 话题链接 |")
    lines.append("|---:|---|---|---:|---:|---|")
    for idx, topic in enumerate(items, 1):
        name = escape_md(topic.get("topicName"))
        name_cell = f"#{name}" if name else "-"
        share_link = topic.get("shareLink") or ""
        link_cell = f"[打开话题]({share_link})" if share_link else "暂无链接"
        lines.append(
            "| {idx} | {name} | `{topic_id}` | {views} | {usage} | {link} |".format(
                idx=idx,
                name=name_cell,
                topic_id=escape_md(topic.get("topicId")),
                views=fmt_num(topic.get("viewCount")),
                usage=fmt_num(topic.get("usageCount")),
                link=link_cell,
            )
        )
    return "\n".join(lines)


RENDERERS = {"video": render_video, "user": render_user, "topic": render_topic}


def describe_api_error(exc: ApiError) -> str:
    if exc.code in (3103, 3105):
        return "API Key 无效或已禁用，请更换有效的 REDFOX_API_KEY 后重试。"
    if exc.code == 3201:
        return "积分不足，请前往红狐控制台充值后重试。"
    if exc.code in (1001, 1002, 1003):
        return f"参数问题：{exc.msg}。请按提示修正参数后重试。"
    if exc.code == 4004:
        return "操作过于频繁，请稍后重试。"
    return f"接口返回异常：code={exc.code}, msg={exc.msg}"


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok 热门搜索（视频 / 用户 / 话题）")
    parser.add_argument("--keyword", required=True, help="搜索关键词")
    parser.add_argument("--type", choices=("video", "user", "topic", "all"), default="all",
                        help="查询类型，默认 all（视频+用户+话题）")
    parser.add_argument("--count", default=10, type=int, help="每类条数（1~50，默认 10；话题查询忽略该参数）")
    parser.add_argument("--offset", default=0, type=int, help="偏移量，首页为 0；翻页填上一次输出提示的 offset")
    parser.add_argument("--sort", choices=sorted(VIDEO_SORT_KEYS), default="views",
                        help="视频排序方式，默认按播放数降序")
    parser.add_argument("--publish", choices=("0", "1", "7", "30", "90", "180"), default="0",
                        help="视频发布时间筛选：0-不限制（默认）/1-一天/7-一周/30-一月/90-三月/180-半年")
    parser.add_argument("--region", default="US", help="视频搜索地区，默认 US")
    parser.add_argument("--fans", default=None, type=int, choices=(1, 2, 3, 4),
                        help="用户粉丝数筛选：1-0~1K/2-1K~10K/3-10K~100K/4-100K以上")
    parser.add_argument("--verified", action="store_true", help="仅看认证用户")
    parser.add_argument("--api-key", default=None, help="临时 API Key；优先级高于环境变量")
    parser.add_argument("--raw", action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    args.keyword = (args.keyword or "").strip()
    if not args.keyword:
        raise SystemExit("错误：--keyword 不能为空")
    if not 1 <= args.count <= 50:
        raise SystemExit("错误：--count 必须在 1~50 之间")
    if args.offset < 0:
        raise SystemExit("错误：--offset 不能小于 0")
    args.region = (args.region or "US").strip().upper() or "US"

    kinds = ["video", "user", "topic"] if args.type == "all" else [args.type]

    try:
        api_key = resolve_api_key(args.api_key)
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        print(API_KEY_REMINDER, file=sys.stderr)
        sys.exit(1)

    print(f"关键词：`{args.keyword}`")
    print(f"{API_KEY_REMINDER}\n")

    failures = 0
    for kind in kinds:
        try:
            payload = build_payload(kind, args)
            data = call_api(kind, payload, api_key)
            if args.raw:
                print(f"### {LABELS[kind]} 原始返回")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                print()
            else:
                print(RENDERERS[kind](data, args))
                print()
        except ApiError as exc:
            failures += 1
            print(f"{LABELS[kind]}查询失败：{describe_api_error(exc)}")
            if exc.code in (3103, 3105):
                print(API_KEY_REMINDER)
            print()
        except Exception as exc:  # 网络或解析异常
            failures += 1
            print(f"{LABELS[kind]}查询失败：{exc}")

    if failures and failures == len(kinds):
        sys.exit(1)


if __name__ == "__main__":
    main()
