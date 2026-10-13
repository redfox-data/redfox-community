#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TikTok 监控订阅推送（关键词 / 账号 / 话题）。

按订阅项拉取昨日新内容，三类订阅项共用一套时间窗过滤逻辑：
- 关键词订阅 → searchVideo：关键词新增爆款视频（最近一天，按点赞排序）
- 账号订阅 → userAwemeList：账号最新作品
- 话题订阅 → topicAwemeList：话题最新作品

用法：
  python scripts/subscribe.py fetch --keywords "nvidia,iphone" --accounts "MS4wLjAB..." --topics "2525872"
  python scripts/subscribe.py fetch --keywords "nvidia" --first --html
  python scripts/subscribe.py fetch --keywords "nvidia" --date 2026-10-12 --markdown
  python scripts/subscribe.py fetch --keywords "nvidia" --save-json

API Key 优先级：--api-key > REDFOX_API_KEY 环境变量 > shell 配置文件。
"""

import argparse
import json
import os
import re
import socket
import ssl
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import unquote

_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SAVE_PATH = os.path.join(_SKILL_DIR, "output", "tiktok_subscribe_latest.json")
AI_SUMMARY_PATH = os.path.join(_SKILL_DIR, "output", "tiktok_subscribe_ai_summary.json")

HOST = "redfox.hk"
ENDPOINTS = {
    "keyword": "/story/api/tiktok/ability/searchVideo",
    "account": "/story/api/tiktok/ability/userAwemeList",
    "topic": "/story/api/tiktok/ability/topicAwemeList",
}
SOURCE = "TikTok监控订阅推送-GitHub"  # 接口请求携带的来源标识
API_KEY_REMINDER = "获取 API Key：前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github)"
BEIJING = timezone(timedelta(hours=8))

KIND_LABELS = {"keyword": "关键词", "account": "账号", "topic": "话题"}


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


# ---------------------------------------------------------------- 参数解析


def parse_keywords(raw: Optional[str]) -> List[str]:
    out: List[str] = []
    for token in (raw or "").split(","):
        token = token.strip()
        if token and token not in out:
            out.append(token)
    return out


def extract_sec_uid(token: str) -> Optional[str]:
    """从 secUserId 或带 sec_uid 参数的分享链接中提取 secUserId。"""
    token = token.strip()
    if token.startswith("https://") or token.startswith("http://"):
        match = re.search(r"[?&]sec_uid=([^&#]+)", token)
        if match:
            return unquote(match.group(1)).strip()
        return None
    return token


def parse_accounts(raw: Optional[str]) -> Tuple[List[str], List[str]]:
    """返回 (有效 secUserId 列表, 无效 token 列表)。"""
    valid: List[str] = []
    invalid: List[str] = []
    for token in (raw or "").split(","):
        token = token.strip()
        if not token:
            continue
        sec_uid = extract_sec_uid(token)
        if not sec_uid:
            invalid.append(token)
            continue
        if not sec_uid.startswith("MS4w") or len(sec_uid) < 40:
            invalid.append(token)
            continue
        if sec_uid not in valid:
            valid.append(sec_uid)
    return valid, invalid


def parse_topics(raw: Optional[str]) -> Tuple[List[int], List[str]]:
    """返回 (有效话题 ID 列表, 无效 token 列表)。"""
    valid: List[int] = []
    invalid: List[str] = []
    for token in (raw or "").split(","):
        token = token.strip()
        if not token:
            continue
        if token.isdigit() and int(token) > 0:
            ch_id = int(token)
            if ch_id not in valid:
                valid.append(ch_id)
        else:
            invalid.append(token)
    return valid, invalid


def compute_window(date_str: Optional[str]) -> Tuple[int, int, str, str]:
    """每日更新模式时间窗：[结束日 9:00 - 1 天, 结束日 9:00)，本地时区。

    返回 (start_ts, end_ts, start_label, end_label)。
    """
    if date_str:
        end_local = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=9, minute=0, second=0, microsecond=0)
    else:
        now = datetime.now()
        end_local = datetime(now.year, now.month, now.day, 9, 0, 0)
    start_local = end_local - timedelta(days=1)
    start_ts = int(start_local.timestamp())
    end_ts = int(end_local.timestamp())
    label_fmt = "%m-%d %H:%M"
    return start_ts, end_ts, start_local.strftime(label_fmt), end_local.strftime(label_fmt)


# ---------------------------------------------------------------- 作品归一化


def fmt_num(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def to_ts(value: Any) -> int:
    try:
        ts = int(value)
    except (TypeError, ValueError):
        return 0
    if ts <= 0:
        return 0
    if ts > 10 ** 12:  # 兼容毫秒时间戳
        ts //= 1000
    return ts


def fmt_time(value: Any) -> str:
    ts = to_ts(value)
    if not ts:
        return "-"
    return datetime.fromtimestamp(ts, tz=BEIJING).strftime("%m-%d %H:%M")


def escape_md(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("\n", " ").replace("|", "\\|").strip()


def plain_summarize(text: Any, limit: int = 60) -> str:
    s = str(text if text is not None else "").replace("\n", " ").strip()
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


def normalize_work(item: Dict[str, Any]) -> Dict[str, Any]:
    author = item.get("authorData") or {}
    stats = item.get("statsData") or {}
    ts = to_ts(item.get("publishTime"))
    content = str(item.get("content") or "").replace("\n", " ").strip()
    return {
        "name": str(author.get("userName") or ""),
        "handle": str(author.get("userHandle") or ""),
        "fans": author.get("fansCount") or 0,
        "workId": str(item.get("workId") or ""),
        "views": stats.get("viewCount") or 0,
        "likes": stats.get("likeCount") or 0,
        "comments": stats.get("commentTotal") or 0,
        "shares": stats.get("shareTotal") or 0,
        "publishTs": ts,
        "time": fmt_time(ts),
        "shareLink": str(item.get("shareLink") or ""),
        "content": content,
        "contentSummary": plain_summarize(content),
    }


def sort_works(works: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(works, key=lambda w: w["views"], reverse=True)


# ---------------------------------------------------------------- 三类拉取


def fetch_keyword_works(keyword: str, api_key: str, args: argparse.Namespace,
                        window: Optional[Tuple[int, int, str, str]]) -> List[Dict[str, Any]]:
    """关键词订阅：searchVideo，sortType=1（最多点赞），每日模式带 publishTime=1。"""
    first = args.first
    offset = 0
    works: List[Dict[str, Any]] = []
    pages = 1 if first else args.max_pages
    for _ in range(pages):
        payload: Dict[str, Any] = {
            "keyword": keyword,
            "offset": str(offset),
            "count": str(args.count),
            "sortType": "1",
            "publishTime": "0" if first else "1",
            "region": args.region,
            "source": SOURCE,
        }
        data = call_api("keyword", payload, api_key)
        page = [normalize_work(it) for it in extract_video_items(data)]
        if not page:
            break
        works.extend(page)
        if first:
            break
        # 命中窗口判定：本页出现早于窗口起点的作品即结束翻页；本页不足 count 也结束
        if window and any(w["publishTs"] and w["publishTs"] < window[0] for w in page):
            break
        if len(page) < args.count:
            break
        offset += args.count
    return works


def fetch_account_works(sec_uid: str, api_key: str, args: argparse.Namespace,
                        window: Optional[Tuple[int, int, str, str]]) -> List[Dict[str, Any]]:
    """账号订阅：userAwemeList，一次返回近期全部作品（无翻页）。"""
    payload: Dict[str, Any] = {"secUserId": sec_uid, "source": SOURCE}
    data = call_api("account", payload, api_key)
    items = data if isinstance(data, list) else extract_video_items(data)
    return [normalize_work(it) for it in items]


def fetch_topic_works(ch_id: int, api_key: str, args: argparse.Namespace,
                      window: Optional[Tuple[int, int, str, str]]) -> Tuple[List[Dict[str, Any]], Optional[int]]:
    """话题订阅：topicAwemeList，cursor 游标翻页。返回 (作品列表, hasMore)。"""
    first = args.first
    cursor = 0
    has_more: Optional[int] = None
    works: List[Dict[str, Any]] = []
    pages = 1 if first else args.max_pages
    for _ in range(pages):
        payload: Dict[str, Any] = {"ch_id": ch_id, "cursor": cursor, "count": args.count, "source": SOURCE}
        data = call_api("topic", payload, api_key)
        data = data if isinstance(data, dict) else {}
        page = [normalize_work(it) for it in (data.get("workList") or [])]
        has_more = data.get("hasMore")
        next_cursor = data.get("nextCursor")
        if not page:
            break
        works.extend(page)
        if first:
            break
        if has_more != 1:
            break
        if window and any(w["publishTs"] and w["publishTs"] < window[0] for w in page):
            break
        if len(page) < args.count:
            break
        cursor = int(next_cursor) if next_cursor is not None else cursor + args.count
    return works, has_more


# ---------------------------------------------------------------- 状态判定


def filter_window(works: List[Dict[str, Any]], window: Optional[Tuple[int, int, str, str]]) -> List[Dict[str, Any]]:
    if not window:
        return works
    return [w for w in works if w["publishTs"] and window[0] <= w["publishTs"] < window[1]]


def timed_status(works_all: List[Dict[str, Any]], in_window: List[Dict[str, Any]],
                 window_start: int, has_7d_check: bool) -> str:
    if in_window:
        return "updated"
    if has_7d_check:
        ts_list = [w["publishTs"] for w in works_all if w["publishTs"]]
        if ts_list and max(ts_list) >= window_start - 6 * 86400:
            return "no_update_yesterday"
        return "no_update_7d"
    return "no_update_yesterday"


def build_account_label(works: List[Dict[str, Any]]) -> str:
    if works:
        name = works[0].get("name")
        handle = works[0].get("handle")
        if name and handle:
            return f"{name}（@{handle}）"
        if name:
            return name
        if handle:
            return f"@{handle}"
    return ""


# ---------------------------------------------------------------- Markdown 渲染


def render_item(item: Dict[str, Any], window: Optional[Tuple[int, int, str, str]],
                first: bool) -> str:
    kind = item["kind"]
    label = item["label"]
    status = item["status"]
    works = item["works"]

    if status == "error":
        return f"### ▸ {label}\n\n拉取失败：{item['error']}\n"

    if status != "updated":
        if status == "no_update_7d":
            return f"### ▸ {label}\n\n近 7 天无更新（该订阅项最近 7 天没有新内容）\n"
        return f"### ▸ {label}\n\n昨日无更新（该订阅项昨日时间窗内无新内容）\n"

    title_suffix = "昨日新内容" if not first else "最新动态"
    lines = [f"### ▸ {label} {title_suffix}（{len(works)} 条）"]
    info = f"本页：{len(works)} 条 ｜ 按播放数降序"
    if not first and window:
        info += f" ｜ 时间窗：{window[2]} ~ {window[3]}"
    lines.append(info)
    lines.append("")

    if kind == "account":
        lines.append("| # | 作品摘要 | 播放 | 点赞 | 评论 | 分享 | 发布时间 |")
        lines.append("|---:|---|---:|---:|---:|---:|---|")
        for idx, w in enumerate(works, 1):
            link = f"[{w['contentSummary']}]({w['shareLink']})" if w["shareLink"] else w["contentSummary"]
            lines.append(
                "| {idx} | {content} | {views} | {likes} | {comments} | {shares} | {time} |".format(
                    idx=idx, content=link, views=fmt_num(w["views"]), likes=fmt_num(w["likes"]),
                    comments=fmt_num(w["comments"]), shares=fmt_num(w["shares"]), time=w["time"],
                )
            )
    else:
        lines.append("| # | 作者 | 作品摘要 | 播放 | 点赞 | 评论 | 分享 | 发布时间 |")
        lines.append("|---:|---|---|---:|---:|---:|---:|---|")
        for idx, w in enumerate(works, 1):
            handle = escape_md(w["handle"])
            author_cell = f"{escape_md(w['name'])} / `{handle}`" if handle else escape_md(w["name"])
            link = f"[{w['contentSummary']}]({w['shareLink']})" if w["shareLink"] else w["contentSummary"]
            lines.append(
                "| {idx} | {author} | {content} | {views} | {likes} | {comments} | {shares} | {time} |".format(
                    idx=idx, author=author_cell, content=link, views=fmt_num(w["views"]),
                    likes=fmt_num(w["likes"]), comments=fmt_num(w["comments"]),
                    shares=fmt_num(w["shares"]), time=w["time"],
                )
            )
    return "\n".join(lines)


# ---------------------------------------------------------------- 主流程


def build_payload_check(args: argparse.Namespace) -> None:
    if args.count < 1 or args.count > 50:
        raise SystemExit("错误：--count 必须在 1~50 之间")
    if args.max_pages < 1 or args.max_pages > 10:
        raise SystemExit("错误：--max-pages 必须在 1~10 之间")
    if args.date:
        try:
            datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            raise SystemExit("错误：--date 必须为 YYYY-MM-DD 格式")
    args.region = (args.region or "US").strip().upper() or "US"


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok 监控订阅推送（关键词 / 账号 / 话题）")
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch", help="拉取订阅项昨日新内容（三类订阅项可混合传入）")
    fetch.add_argument("--keywords", default=None, help="订阅关键词列表，逗号分隔")
    fetch.add_argument("--accounts", default=None,
                       help="订阅账号列表，逗号分隔（secUserId 或带 sec_uid= 参数的分享链接）")
    fetch.add_argument("--topics", default=None, help="订阅话题 ID 列表，逗号分隔（ch_id 数字）")
    fetch.add_argument("--date", default=None, help="时间窗结束日 YYYY-MM-DD（默认：今日 9:00 边界）")
    fetch.add_argument("--first", action="store_true", help="首次订阅模式：拉第一页最新内容，不按时间窗过滤")
    fetch.add_argument("--count", default=20, type=int, help="每订阅项条数（1~50，默认 20）")
    fetch.add_argument("--max-pages", default=3, type=int, help="每日模式每订阅项最多翻页数（1~10，默认 3）")
    fetch.add_argument("--region", default="US", help="关键词视频搜索地区，默认 US")
    fetch.add_argument("--api-key", default=None, help="临时 API Key；优先级高于环境变量")
    fetch.add_argument("--raw", action="store_true", help="输出原始 JSON")
    fetch.add_argument("--markdown", action="store_true", help="输出 Markdown 格式表格")
    fetch.add_argument("--html", action="store_true", help="生成 HTML 日报并自动打开浏览器")
    fetch.add_argument("--save-json", nargs="?", const=DEFAULT_SAVE_PATH, default=None,
                       metavar="PATH", help="结果保存为 JSON（供 HTML 报告使用）；"
                                            f"不带路径时默认保存到 {DEFAULT_SAVE_PATH}")
    args = parser.parse_args()

    build_payload_check(args)

    keywords = parse_keywords(args.keywords)
    accounts, invalid_accounts = parse_accounts(args.accounts)
    topics, invalid_topics = parse_topics(args.topics)

    if not keywords and not accounts and not topics:
        raise SystemExit("错误：请至少提供 --keywords / --accounts / --topics 之一")
    if invalid_topics:
        raise SystemExit(
            "错误：--topics 中包含无效话题 ID：" + "、".join(invalid_topics) +
            "。话题订阅需要话题 ID（ch_id，大于 0 的数字），可从 TikTok 话题链接或话题搜索中获取。"
        )
    if invalid_accounts:
        raise SystemExit(
            "错误：--accounts 中包含无法解析的账号：" + "、".join(invalid_accounts) +
            "。账号订阅需要 secUserId（MS4w 开头的长串）或带 sec_uid= 参数的分享链接，获取方式见 SKILL.md。"
        )

    try:
        api_key = resolve_api_key(args.api_key)
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        print(API_KEY_REMINDER, file=sys.stderr)
        sys.exit(1)

    window: Optional[Tuple[int, int, str, str]] = None
    if not args.first:
        window = compute_window(args.date)

    mode_label = "首次订阅（拉取最新动态，不按时间窗过滤）" if args.first else "每日更新"
    print(f"订阅项：关键词 {len(keywords)} 个 ｜ 账号 {len(accounts)} 个 ｜ 话题 {len(topics)} 个")
    if window:
        print(f"模式：{mode_label} ｜ 时间窗：{window[2]} ~ {window[3]} ｜ 按播放数降序")
    else:
        print(f"模式：{mode_label} ｜ 按播放数降序")
    print(API_KEY_REMINDER)
    print()

    items: List[Dict[str, Any]] = []
    failures = 0

    for kw in keywords:
        item: Dict[str, Any] = {"kind": "keyword", "key": kw, "label": f"关键词「{kw}」"}
        try:
            if args.raw:
                payload = {"keyword": kw, "offset": "0", "count": str(args.count), "sortType": "1",
                           "publishTime": "0" if args.first else "1", "region": args.region, "source": SOURCE}
                data = call_api("keyword", payload, api_key)
                print(f"### {item['label']} 原始返回")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                print()
                item["status"] = "raw"
                items.append(item)
                continue
            works = fetch_keyword_works(kw, api_key, args, window)
            if not args.first and window:
                in_window = filter_window(works, window)
                status = timed_status(works, in_window, window[0], has_7d_check=False)
                works = in_window
            else:
                status = "updated" if works else "no_update_yesterday"
            item["status"] = status
            item["works"] = sort_works(works)[: args.count]
        except ApiError as exc:
            failures += 1
            item["status"] = "error"
            item["error"] = describe_api_error(exc)
        except Exception as exc:  # 网络或解析异常
            failures += 1
            item["status"] = "error"
            item["error"] = str(exc)
        items.append(item)
        if item["status"] != "raw":
            print(render_item(item, window, args.first))
            print()

    for sec_uid in accounts:
        item = {"kind": "account", "key": sec_uid, "label": ""}
        try:
            works = fetch_account_works(sec_uid, api_key, args, window)
            label_name = build_account_label(works)
            item["label"] = f"账号 {label_name}" if label_name else "账号（未获取到账号信息）"
            if not args.first and window:
                in_window = filter_window(works, window)
                status = timed_status(works, in_window, window[0], has_7d_check=True)
                works = in_window
            else:
                status = "updated" if works else "no_update_7d"
            item["status"] = status
            item["works"] = sort_works(works)[: args.count]
        except ApiError as exc:
            failures += 1
            item["status"] = "error"
            item["error"] = describe_api_error(exc)
            if exc.code in (3103, 3105):
                print(API_KEY_REMINDER)
        except Exception as exc:
            failures += 1
            item["status"] = "error"
            item["error"] = str(exc)
        items.append(item)
        print(render_item(item, window, args.first))
        print()

    for ch_id in topics:
        item = {"kind": "topic", "key": str(ch_id), "label": f"话题 ID {ch_id}"}
        try:
            works, _has_more = fetch_topic_works(ch_id, api_key, args, window)
            if not args.first and window:
                in_window = filter_window(works, window)
                status = timed_status(works, in_window, window[0], has_7d_check=True)
                works = in_window
            else:
                status = "updated" if works else "no_update_7d"
            item["status"] = status
            item["works"] = sort_works(works)[: args.count]
        except ApiError as exc:
            failures += 1
            item["status"] = "error"
            item["error"] = describe_api_error(exc)
        except Exception as exc:
            failures += 1
            item["status"] = "error"
            item["error"] = str(exc)
        items.append(item)
        print(render_item(item, window, args.first))
        print()

    updated = sum(1 for it in items if it["status"] == "updated")
    no_yesterday = sum(1 for it in items if it["status"] == "no_update_yesterday")
    no_7d = sum(1 for it in items if it["status"] == "no_update_7d")
    err_count = sum(1 for it in items if it["status"] == "error")
    total_works = sum(len(it.get("works") or []) for it in items if it["status"] == "updated")
    print(f"汇总：更新 {updated} 项 ｜ 昨日无更新 {no_yesterday} 项 ｜ 近 7 天无更新 {no_7d} 项 ｜ "
          f"失败 {err_count} 项 ｜ 共拉取作品 {total_works} 条")

    save_path = args.save_json
    if args.html and not save_path:
        save_path = DEFAULT_SAVE_PATH

    if save_path:
        saved = {
            "meta": {
                "mode": "first" if args.first else "daily",
                "date": args.date or datetime.now().strftime("%Y-%m-%d"),
                "windowStart": window[2] if window else None,
                "windowEnd": window[3] if window else None,
                "count": args.count,
                "maxPages": args.max_pages,
                "region": args.region,
                "generatedAt": datetime.now(tz=BEIJING).strftime("%Y-%m-%d %H:%M:%S"),
            },
            "items": items,
        }
        try:
            path = save_path
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(saved, f, ensure_ascii=False, indent=2)
            print(f"查询结果已保存：{path}")
        except OSError as exc:
            print(f"结果保存失败：{exc}", file=sys.stderr)

    if args.html:
        report_script = os.path.join(_SKILL_DIR, "scripts", "generate_report.py")
        cmd = [sys.executable, report_script, "--data", save_path]
        if os.path.exists(AI_SUMMARY_PATH):
            cmd += ["--analysis", AI_SUMMARY_PATH]
        try:
            subprocess.run(cmd, check=True)
        except Exception as exc:
            print(f"HTML 日报生成失败：{exc}", file=sys.stderr)

    if failures and failures == len(items):
        sys.exit(1)


if __name__ == "__main__":
    main()
