#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取 TikTok 指定话题作品数据。

用法：
  python scripts/fetch_topic_aweme_list.py --ch-id 2525872 --topic charlidamelio --count 10
  python scripts/fetch_topic_aweme_list.py --ch-id 2525872 --cursor 10 --count 10
  python scripts/fetch_topic_aweme_list.py --ch-id 2525872 --cursor 10 --count 10 --sort likes

API Key 优先级：--api-key > REDFOX_API_KEY 环境变量 > shell 配置文件。
"""

import argparse
import json
import os
import re
import socket
import ssl
import sys
from typing import Any, Dict, List, Optional

HOST = "redfox.hk"
ENDPOINT = "/story/api/tiktok/ability/topicAwemeList"
API_URL = f"https://{HOST}{ENDPOINT}"
SOURCE = "tiktok关键词搜话题-GitHub"  # 接口请求携带的来源标识
API_KEY_REMINDER = "获取 API Key：前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github)"

SORT_KEYS = {
    "none": None,
    "views": "viewCount",
    "likes": "likeCount",
    "comments": "commentTotal",
    "shares": "shareTotal",
}


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


def post_redfox_no_sni(payload: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = (
        f"POST {ENDPOINT} HTTP/1.1\r\n"
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
        raise RuntimeError(f"HTTP 请求失败：{status_line}")

    try:
        return json.loads(response_body)
    except json.JSONDecodeError as exc:
        preview = response_body[:300].replace("\n", " ")
        raise RuntimeError(f"响应不是有效 JSON：{preview}") from exc


def fmt_num(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def escape_md(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("\n", " ").replace("|", "\\|").strip()


def summarize(text: Any, limit: int = 72) -> str:
    s = escape_md(text)
    return s if len(s) <= limit else s[: limit - 3] + "..."


def render_table(topic: str, works: List[Dict[str, Any]]) -> str:
    lines = [
        "| # | 作者 | 作品 ID | 播放 | 点赞 | 评论 | 分享 | 作品链接 | 内容摘要 | 话题 |",
        "|---:|---|---|---:|---:|---:|---:|---|---|---|",
    ]
    for idx, work in enumerate(works, 1):
        author = work.get("authorData") or {}
        stats = work.get("statsData") or {}
        work_id = escape_md(work.get("workId"))
        author_name = escape_md(author.get("userName"))
        handle = escape_md(author.get("userHandle"))
        author_cell = f"{author_name} / `{handle}`" if handle else author_name
        share_link = work.get("shareLink") or ""
        link_cell = f"[打开作品]({share_link})" if share_link else "暂无链接"
        lines.append(
            "| {idx} | {author} | `{work_id}` | {views} | {likes} | {comments} | {shares} | {link} | {content} | `{topic}` |".format(
                idx=idx,
                author=author_cell,
                work_id=work_id,
                views=fmt_num(stats.get("viewCount")),
                likes=fmt_num(stats.get("likeCount")),
                comments=fmt_num(stats.get("commentTotal")),
                shares=fmt_num(stats.get("shareTotal")),
                link=link_cell,
                content=summarize(work.get("content")),
                topic=escape_md(topic),
            )
        )
    return "\n".join(lines)


def sort_works(works: List[Dict[str, Any]], sort_name: str) -> List[Dict[str, Any]]:
    key = SORT_KEYS.get(sort_name)
    if not key:
        return works
    return sorted(
        works,
        key=lambda item: ((item.get("statsData") or {}).get(key) or 0),
        reverse=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="获取 TikTok 指定话题作品数据")
    parser.add_argument("--ch-id", required=True, type=int, help="TikTok 话题 ID / challengeId / hashtagId")
    parser.add_argument("--topic", default="", help="话题名称，仅用于表格展示，例如 charlidamelio")
    parser.add_argument("--cursor", default=0, type=int, help="分页游标，首页为 0")
    parser.add_argument("--count", default=10, type=int, help="每页条数")
    parser.add_argument("--sort", choices=sorted(SORT_KEYS), default="views", help="排序方式，默认按播放数降序")
    parser.add_argument("--api-key", default=None, help="临时 API Key；优先级高于环境变量")
    parser.add_argument("--raw", action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    if args.ch_id <= 0:
        raise SystemExit("错误：--ch-id 必须大于 0")
    if args.cursor < 0:
        raise SystemExit("错误：--cursor 不能小于 0")
    if args.count <= 0:
        raise SystemExit("错误：--count 必须大于 0")

    try:
        api_key = resolve_api_key(args.api_key)
        payload = {"ch_id": args.ch_id, "cursor": args.cursor, "count": args.count, "source": SOURCE}
        result = post_redfox_no_sni(payload, api_key)

        if args.raw:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        code = result.get("code")
        msg = result.get("msg", "")
        if code != 2000:
            print(f"接口返回异常：code={code}, msg={msg}")
            if code == 3105:
                print("请更换有效的 REDFOX_API_KEY 后重试。")
                print(API_KEY_REMINDER)
            return

        data = result.get("data") or {}
        works = data.get("workList") or []
        topic = args.topic.strip()
        if topic and not topic.startswith("#"):
            topic = f"#{topic}"
        if not topic:
            topic = f"ch_id:{args.ch_id}"

        print(f"话题：`{topic}` | ch_id：`{args.ch_id}` | cursor：{args.cursor} | count：{len(works)} | hasMore：{data.get('hasMore')} | nextCursor：{data.get('nextCursor')}")
        print(f"{API_KEY_REMINDER}\n")
        if not works:
            print("暂无数据")
            return

        print(render_table(topic, sort_works(works, args.sort)))
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        if "REDFOX_API_KEY" in str(exc) or "API Key" in str(exc):
            print(API_KEY_REMINDER, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
