#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TikTok 关键词搜索用户。

用法：
  python scripts/search_user.py --keyword 南浔
  python scripts/search_user.py --keyword 南浔 --count 20 --sort none
  python scripts/search_user.py --keyword 手冲咖啡 --fans 3 --verified

翻页（续查下一页）：
  python scripts/search_user.py --keyword 南浔 --offset 20

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
ENDPOINT = "/story/api/tiktok/ability/searchUser"
SOURCE = "TikTok关键词搜用户-GitHub"
API_KEY_REMINDER = "获取 API Key：前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github)"

FANS_FILTER_LABELS = {
    1: "0~1K",
    2: "1K~10K",
    3: "10K~100K",
    4: "100K以上",
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


def post_redfox(payload: Dict[str, Any], api_key: str) -> Dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = (
        f"POST {ENDPOINT} HTTP/1.1\r\n"
        f"Host: {HOST}\r\n"
        f"REDFOX_API_KEY: {api_key}\r\n"
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


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "keyword": args.keyword.strip(),
        "offset": str(args.offset),
        "count": str(args.count),
        "source": SOURCE,
    }
    if args.fans:
        payload["followerCountFilter"] = args.fans
    if args.verified:
        payload["profileTypeFilter"] = 1
    if args.name_relevance:
        payload["otherPrefFilter"] = 1
    return payload


def fmt_num(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def escape_md(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("\n", " ").replace("|", "\\|").strip()


def render_table(items: List[Dict[str, Any]]) -> str:
    lines = [
        "| # | 昵称 | Handle | userId | 粉丝 | 关注 | 获赞 | 作品 |",
        "|---:|---|---|---|---:|---:|---:|---:|",
    ]
    for idx, item in enumerate(items, 1):
        name = escape_md(item.get("userName")) or "-"
        handle = escape_md(item.get("userHandle"))
        user_id = escape_md(item.get("userId"))
        lines.append(
            "| {idx} | {name} | {handle} | `{user_id}` | {fans} | {follows} | {likes} | {works} |".format(
                idx=idx,
                name=name,
                handle=handle or "-",
                user_id=user_id or "-",
                fans=fmt_num(item.get("fansCount")),
                follows=fmt_num(item.get("followCount")),
                likes=fmt_num(item.get("likedTotal")),
                works=fmt_num(item.get("workCount")),
            )
        )
    return "\n".join(lines)


def sort_items(items: List[Dict[str, Any]], sort_name: str) -> List[Dict[str, Any]]:
    if sort_name != "fans":
        return items

    def sort_value(item: Dict[str, Any]) -> int:
        try:
            return int(float(item.get("fansCount")))
        except (TypeError, ValueError):
            return 0

    return sorted(items, key=sort_value, reverse=True)


def print_next_page_hint(data: Dict[str, Any]) -> None:
    if data.get("hasMore") != 1:
        return
    cursor = data.get("cursor")
    print(f"下一页：在原命令后追加 --offset {cursor if cursor is not None else '（见上方 cursor）'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok 关键词搜索用户")
    parser.add_argument("--keyword", required=True, help="搜索关键词，如昵称或 handle")
    parser.add_argument("--offset", default="0", help="偏移量，首页传 0，翻页传上次返回的 cursor")
    parser.add_argument("--count", default=10, type=int, help="单页条数")
    parser.add_argument("--fans", type=int, choices=(1, 2, 3, 4), default=None,
                        help="粉丝数筛选：1-0~1K/2-1K~10K/3-10K~100K/4-100K以上")
    parser.add_argument("--verified", action="store_true", help="仅看认证用户")
    parser.add_argument("--name-relevance", action="store_true", help="按用户名相关性排序（接口偏好参数）")
    parser.add_argument("--sort", choices=["fans", "none"], default="fans",
                        help="排序方式：fans=粉丝数降序（默认），none=接口原始相关度顺序")
    parser.add_argument("--top", default=0, type=int, help="仅展示前 N 条；0 表示展示接口返回全部")
    parser.add_argument("--api-key", default=None, help="临时 API Key；优先级高于环境变量")
    parser.add_argument("--raw", action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    keyword = args.keyword.strip()
    if not keyword:
        raise SystemExit("错误：--keyword 不能为空")
    if int(args.offset) < 0:
        raise SystemExit("错误：--offset 不能小于 0")
    if args.count <= 0 or args.count > 50:
        raise SystemExit("错误：--count 必须在 1~50 之间")

    try:
        api_key = resolve_api_key(args.api_key)
        payload = build_payload(args)
        result = post_redfox(payload, api_key)

        if args.raw:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return

        code = result.get("code")
        msg = result.get("msg") or result.get("message", "")
        if code not in (200, 2000):
            print(f"接口返回异常：code={code}, msg={msg}")
            if code == 3105:
                print("请更换有效的 REDFOX_API_KEY 后重试。")
                print(API_KEY_REMINDER)
            return

        data = result.get("data") or {}
        items = data.get("userList") or []
        items = sort_items(items, args.sort)
        if args.top:
            items = items[: args.top]

        filters = []
        if args.fans:
            filters.append(f"粉丝{FANS_FILTER_LABELS[args.fans]}")
        if args.verified:
            filters.append("仅认证")
        filter_text = (" | " + "、".join(filters)) if filters else ""

        print(
            f"关键词：`{escape_md(keyword)}` | offset：{args.offset} | count：{len(data.get('userList') or [])} | "
            f"hasMore：{data.get('hasMore')} | cursor：{data.get('cursor')}{filter_text}"
        )
        print(f"{API_KEY_REMINDER}\n")
        if not items:
            print("暂无数据")
            return

        print(render_table(items))
        print_next_page_hint(data)
    except Exception as exc:
        print(f"错误：{exc}", file=sys.stderr)
        if "REDFOX_API_KEY" in str(exc) or "API Key" in str(exc):
            print(API_KEY_REMINDER, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
