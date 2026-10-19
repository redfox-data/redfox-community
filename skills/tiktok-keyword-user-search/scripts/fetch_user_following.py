#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""获取 TikTok 指定用户的关注列表。

用法：
  python scripts/fetch_user_following.py --user-id 6748953635118187521
  python scripts/fetch_user_following.py --sec-user-id MS4wLjABAAAA...
  python scripts/fetch_user_following.py --user-id 6748953635118187521 --sort fans --top 20

翻页（续查更早关注）：
  python scripts/fetch_user_following.py --user-id 6748953635118187521 --min-time 1760525119 --page-token xxx

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
ENDPOINT = "/story/api/tiktok/ability/userFollowing"
SOURCE = "TikTok关键词搜用户-GitHub"
API_KEY_REMINDER = "获取 API Key：前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github)"

SORT_KEYS = {
    "none": None,
    "fans": "fansCount",
    "works": "workCount",
    "likes": "likedTotal",
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


def fmt_num(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def escape_md(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("\n", " ").replace("|", "\\|").strip()


def summarize(text: Any, limit: int = 32) -> str:
    s = escape_md(text)
    return s if len(s) <= limit else s[: limit - 3] + "..."


def verify_badge(item: Dict[str, Any]) -> str:
    custom = escape_md(item.get("customVerify"))
    enterprise = escape_md(item.get("enterpriseVerifyReason"))
    if custom:
        return summarize(custom)
    if enterprise:
        return summarize(f"[企业] {enterprise}")
    return "-"


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "minTime": args.min_time.strip() or "0",
        "pageToken": args.page_token or "",
        "source": SOURCE,
    }
    if args.sec_user_id:
        payload["secUserId"] = args.sec_user_id.strip()
    else:
        payload["userId"] = args.user_id.strip()
    return payload


def render_table(items: List[Dict[str, Any]]) -> str:
    lines = [
        "| # | 昵称 | Handle | 粉丝 | 作品 | 获赞 | 地区 | 认证 |",
        "|---:|---|---|---:|---:|---:|---|---|",
    ]
    for idx, item in enumerate(items, 1):
        name = escape_md(item.get("userName")) or "-"
        if item.get("isSecret") == 1:
            name += "（私密）"
        handle = escape_md(item.get("userHandle"))
        lines.append(
            "| {idx} | {name} | {handle} | {fans} | {works} | {likes} | {region} | {verify} |".format(
                idx=idx,
                name=name,
                handle=handle or "-",
                fans=fmt_num(item.get("fansCount")),
                works=fmt_num(item.get("workCount")),
                likes=fmt_num(item.get("likedTotal")),
                region=escape_md(item.get("region")) or "-",
                verify=verify_badge(item),
            )
        )
    return "\n".join(lines)


def sort_items(items: List[Dict[str, Any]], sort_name: str) -> List[Dict[str, Any]]:
    key = SORT_KEYS.get(sort_name)
    if not key:
        return items

    def sort_value(item: Dict[str, Any]) -> int:
        try:
            return int(float(item.get(key)))
        except (TypeError, ValueError):
            return 0

    return sorted(items, key=sort_value, reverse=True)


def print_next_page_hint(data: Dict[str, Any]) -> None:
    if data.get("hasMore") != 1:
        return
    hint = f"下一页：在原命令后追加 --min-time {data.get('minTime')}"
    page_token = data.get("pageToken")
    if page_token:
        hint += f" --page-token {page_token}"
    print(hint)


def main() -> None:
    parser = argparse.ArgumentParser(description="获取 TikTok 指定用户的关注列表")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--user-id", default=None, help="纯数字用户ID，与 --sec-user-id 二选一")
    group.add_argument("--sec-user-id", default=None, help="字母数字混合ID（MS4wLjAB开头），与 --user-id 二选一")
    parser.add_argument("--min-time", default="0", help="翻页游标，首次传 0，后续传上次返回的 minTime")
    parser.add_argument("--page-token", default="", help="翻页token，首次传空，后续传上次返回的 pageToken")
    parser.add_argument("--sort", choices=sorted(SORT_KEYS), default="none", help="排序方式，默认保持接口原始顺序（关注时间倒序）")
    parser.add_argument("--top", default=0, type=int, help="仅展示前 N 条；0 表示展示接口返回全部")
    parser.add_argument("--api-key", default=None, help="临时 API Key；优先级高于环境变量")
    parser.add_argument("--raw", action="store_true", help="输出原始 JSON")
    args = parser.parse_args()

    if args.user_id is not None and not args.user_id.strip().isdigit():
        raise SystemExit("错误：--user-id 必须为纯数字用户ID；若你持有的是 MS4wLjAB 开头的加密ID，请改用 --sec-user-id")
    if args.sec_user_id is not None and not args.sec_user_id.strip():
        raise SystemExit("错误：--sec-user-id 不能为空")
    if args.top < 0:
        raise SystemExit("错误：--top 不能小于 0")

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
        items = data.get("followingList") or []
        target = f"userId:{args.user_id.strip()}" if args.user_id else f"secUserId:{args.sec_user_id.strip()[:24]}..."
        if args.sort != "none":
            items = sort_items(items, args.sort)
        if args.top:
            items = items[: args.top]

        print(
            f"目标：`{target}` | minTime：{payload['minTime']} | count：{len(data.get('followingList') or [])} | "
            f"hasMore：{data.get('hasMore')} | pageToken：{data.get('pageToken')}"
        )
        print(f"{API_KEY_REMINDER}\n")
        if not items:
            print("暂无数据")
            print_next_page_hint(data)
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
