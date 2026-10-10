#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TikTok 账号深度分析（账号基础信息 / 主页作品 / 喜欢作品）。

输入 TikTok 主页链接、@handle、secUserId 或昵称，自动定位账号并输出：
账号基础信息、主页作品榜与喜欢作品透视。

用法：
  python scripts/tiktok_account_analyzer.py --account "@tomcurtainofficial" --types all
  python scripts/tiktok_account_analyzer.py --account "Tom Curtain" --resolve
  python scripts/tiktok_account_analyzer.py --account "Tom Curtain" --pick 2 --types all
  python scripts/tiktok_account_analyzer.py --account "MS4wLjAB..." --types all
  python scripts/tiktok_account_analyzer.py --account "@tomcurtainofficial" --types favorites --cursor 1791462081000000
  python scripts/tiktok_account_analyzer.py --account "@tomcurtainofficial" --types all --save-json

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

_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SAVE_PATH = os.path.join(_SKILL_DIR, "output", "tiktok_account_latest.json")

HOST = "redfox.hk"
ENDPOINTS = {
    "search": "/story/api/tiktok/ability/searchUser",
    "works": "/story/api/tiktok/ability/userAwemeList",
    "favorites": "/story/api/tiktok/ability/userFavoriteAwemeList",
}
SOURCE = "TikTok账号深度分析-GitHub"  # 接口请求携带的来源标识
API_KEY_REMINDER = "获取 API Key：前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github)"
BEIJING = timezone(timedelta(hours=8))

SEC_USER_ID_GUIDE = (
    "secUserId 获取方式（secUserId 为 MS4w 开头的完整长串）：\n"
    "1. 手机 TikTok App 进入目标账号主页 → 点右上角「分享」→「复制链接」，"
    "分享链接中带有 sec_uid=MS4w... 参数，把完整分享链接提供给本技能即可；\n"
    "2. 或按 F12 打开浏览器开发者工具 → Console 粘贴执行：\n"
    "   JSON.parse(document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__').textContent)"
    ".__DEFAULT_SCOPE__['webapp.user-detail'].userInfo.user.secUid\n"
    "3. 复制时请确认以 MS4w 开头且整串完整，中途截断会查询失败。"
)


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


# ─── 账号输入解析 ──────────────────────────────────────────────────────────────────

def parse_account(text: str) -> Dict[str, Optional[str]]:
    """解析账号输入，返回 {sec_user_id, handle, keyword} 之一为主。

    优先级：secUserId > 带 sec_uid 的分享链接 > @handle / 主页链接 > 昵称 / 关键词。
    """
    text = (text or "").strip()
    result: Dict[str, Optional[str]] = {"sec_user_id": None, "handle": None, "keyword": None}

    # 1) 直接 secUserId
    if re.fullmatch(r"MS4w[A-Za-z0-9_\-]{10,}", text):
        result["sec_user_id"] = text
        return result
    # 2) 分享链接 / 主页链接中的 sec_uid 参数
    match = re.search(r"[?&]sec_uid=(MS4w[A-Za-z0-9_\-]+)", text)
    if match:
        result["sec_user_id"] = match.group(1)
        return result
    # 3) 主页链接 / @handle / 裸 handle
    match = re.search(r"tiktok\.com/@([A-Za-z0-9._]{1,24})", text)
    if match:
        result["handle"] = match.group(1)
        return result
    match = re.fullmatch(r"@?([A-Za-z0-9._]{1,24})", text)
    if match:
        result["handle"] = match.group(1)
        return result
    # 4) 其余视为昵称 / 关键词
    result["keyword"] = text
    return result


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


def plain_summarize(text: Any, limit: int = 60) -> str:
    s = str(text if text is not None else "").replace("\n", " ").strip()
    return s if len(s) <= limit else s[: limit - 3] + "..."


# ─── 数据提取与规范化 ────────────────────────────────────────────────────────────────

def extract_work_items(data: Any) -> List[Dict[str, Any]]:
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("workList", "list", "records"):
            value = data.get(key)
            if isinstance(value, list):
                return value
    return []


def sort_works_by_time(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(items, key=lambda item: (item.get("publishTime") or 0), reverse=True)


def normalize_work(item: Dict[str, Any], idx: int) -> Dict[str, Any]:
    stats = item.get("statsData") or {}
    return {
        "rank": idx,
        "workId": str(item.get("workId") or ""),
        "content": str(item.get("content") or "").replace("\n", " ").strip(),
        "contentSummary": plain_summarize(item.get("content")),
        "date": fmt_time(item.get("publishTime")),
        "publishTime": item.get("publishTime") or 0,
        "views": stats.get("viewCount") or 0,
        "likes": stats.get("likeCount") or 0,
        "comments": stats.get("commentTotal") or 0,
        "favorites": stats.get("favoriteCount") or 0,
        "shares": stats.get("shareTotal") or 0,
        "shareLink": str(item.get("shareLink") or ""),
    }


def normalize_favorite(item: Dict[str, Any], idx: int) -> Dict[str, Any]:
    data = normalize_work(item, idx)
    author = item.get("authorData") or {}
    data["author"] = str(author.get("userName") or "")
    data["authorHandle"] = str(author.get("userHandle") or "")
    return data


def normalize_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    """兼容 searchUser 用户条目与作品 authorData 两种来源。"""
    data = data or {}
    handle = str(data.get("userHandle") or "")
    name = str(data.get("userName") or "")
    signature = str(data.get("userSignature") or "").replace("\n", " ").strip()
    verify = str(data.get("verifyInfo") or data.get("enterpriseVerify") or "")
    return {
        "name": name,
        "handle": handle,
        "secUserId": str(data.get("secUserId") or ""),
        "userId": str(data.get("userId") or ""),
        "fans": data.get("fansCount") or 0,
        "follow": data.get("followCount") or 0,
        "liked": data.get("likedTotal") or 0,
        "works": data.get("workCount") or 0,
        "area": str(data.get("userArea") or ""),
        "signature": signature,
        "verify": verify,
        "avatar": str(data.get("avatarImage") or ""),
        "profileUrl": f"https://www.tiktok.com/@{handle}" if handle else "",
    }


# ─── 渲染输出 ────────────────────────────────────────────────────────────────────────

def render_candidates(items: List[Dict[str, Any]]) -> str:
    lines = ["| # | 昵称 | TikTok号 | 粉丝数 | 获赞总数 | 作品数 | 主页链接 |",
             "|---:|---|---|---:|---:|---:|---|"]
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


def render_profile(profile: Dict[str, Any]) -> str:
    rows = [
        ("昵称", escape_md(profile.get("name")) or "—"),
        ("TikTok号", escape_md(profile.get("handle")) or "—"),
        ("粉丝数", fmt_num(profile.get("fans"))),
        ("关注数", fmt_num(profile.get("follow"))),
        ("获赞总数", fmt_num(profile.get("liked"))),
        ("作品数", fmt_num(profile.get("works"))),
        ("地区", escape_md(profile.get("area")) or "—"),
        ("认证", escape_md(profile.get("verify")) or "—"),
        ("签名", escape_md(profile.get("signature")) or "—"),
    ]
    link = profile.get("profileUrl") or ""
    rows.append(("主页链接", f"[打开主页]({link})" if link else "暂无链接"))
    lines = ["| 项目 | 数据 |", "|---|---|"]
    for key, value in rows:
        lines.append(f"| {key} | {value} |")
    return "\n".join(lines)


def render_works(items: List[Dict[str, Any]], offset: int) -> str:
    page = items[offset: offset + 100]  # 由调用方统一切片，这里防御
    lines = ["| # | 发布时间 | 作品 | 播放 | 点赞 | 评论 | 收藏 | 分享 | 作品链接 |",
             "|---:|---|---|---:|---:|---:|---:|---:|---|"]
    for item in page:
        share_link = item.get("shareLink") or ""
        link_cell = f"[打开作品]({share_link})" if share_link else "暂无链接"
        lines.append(
            "| {rank} | {date} | {content} | {views} | {likes} | {comments} | {favorites} | {shares} | {link} |".format(
                rank=item.get("rank"),
                date=item.get("date"),
                content=escape_md(item.get("contentSummary")) or "—",
                views=fmt_num(item.get("views")),
                likes=fmt_num(item.get("likes")),
                comments=fmt_num(item.get("comments")),
                favorites=fmt_num(item.get("favorites")),
                shares=fmt_num(item.get("shares")),
                link=link_cell,
            )
        )
    return "\n".join(lines)


def render_favorites(items: List[Dict[str, Any]]) -> str:
    lines = ["| # | 发布时间 | 作品 | 作者 | 播放 | 点赞 | 作品链接 |",
             "|---:|---|---|---|---:|---:|---|"]
    for item in items:
        share_link = item.get("shareLink") or ""
        link_cell = f"[打开作品]({share_link})" if share_link else "暂无链接"
        author = item.get("author") or "—"
        handle = item.get("authorHandle") or ""
        if handle and handle not in author:
            author = f"{author} (@{handle})"
        lines.append(
            "| {rank} | {date} | {content} | {author} | {views} | {likes} | {link} |".format(
                rank=item.get("rank"),
                date=item.get("date"),
                content=escape_md(item.get("contentSummary")) or "—",
                author=escape_md(author),
                views=fmt_num(item.get("views")),
                likes=fmt_num(item.get("likes")),
                link=link_cell,
            )
        )
    return "\n".join(lines)


# ─── 主流程 ──────────────────────────────────────────────────────────────────────────

def resolve_account(parsed: Dict[str, Optional[str]], args: argparse.Namespace,
                    api_key: str) -> Dict[str, Any]:
    """定位账号：返回 {secUserId, profile, candidates, exactMatch}。"""
    if parsed["sec_user_id"]:
        return {
            "secUserId": parsed["sec_user_id"],
            "profile": None,
            "candidates": [],
            "exactMatch": True,
            "via": "secUserId",
        }
    keyword = parsed["handle"] or parsed["keyword"]
    payload: Dict[str, Any] = {
        "keyword": keyword,
        "offset": "0",
        "count": "20",
        "source": SOURCE,
    }
    data = call_api("search", payload, api_key)
    data = data if isinstance(data, dict) else {}
    candidates = data.get("userList") or []

    if parsed["handle"]:
        wanted = parsed["handle"].lower()
        for user in candidates:
            if str(user.get("userHandle") or "").lower() == wanted:
                return {
                    "secUserId": str(user.get("secUserId") or ""),
                    "profile": normalize_profile(user),
                    "candidates": candidates,
                    "exactMatch": True,
                    "via": "searchUser",
                }
        # 未精确命中：按 --pick 选择（默认第 1 个），并提示候选列表
        pick = max(1, min(args.pick, len(candidates))) if candidates else 0
        chosen = candidates[pick - 1] if pick else None
        print(f"搜索「{keyword}」未精确匹配到 @{parsed['handle']}，找到 {len(candidates)} 个候选账号：")
        if candidates:
            print(render_candidates(candidates))
        print()
        if not chosen:
            raise SystemExit(
                "未找到匹配账号。请提供准确的 TikTok 主页链接，"
                "或带 sec_uid 参数的分享链接以便精准查询。\n" + SEC_USER_ID_GUIDE
            )
        print(f"已选定第 {pick} 个候选：{escape_md(chosen.get('userName'))} (@{escape_md(chosen.get('userHandle'))})")
        print("如非目标账号，请带 --pick N 重新指定，或提供主页链接 / 带 sec_uid 参数的分享链接精确定位。\n")
        return {
            "secUserId": str(chosen.get("secUserId") or ""),
            "profile": normalize_profile(chosen),
            "candidates": candidates,
            "exactMatch": False,
            "via": "searchUser",
        }

    # 昵称 / 关键词：--resolve 时仅展示候选；否则按 --pick 选择（默认第 1 个）
    if candidates:
        print(f"搜索「{keyword}」找到 {len(candidates)} 个候选账号：")
        print(render_candidates(candidates))
        print()
    if args.resolve:
        if candidates:
            print("确认目标账号后，回复「选第 N 个」或直接提供主页链接 / 带 sec_uid 参数的分享链接继续分析。")
        else:
            print("未找到匹配账号。请提供准确的 TikTok 主页链接或带 sec_uid 参数的分享链接。\n" + SEC_USER_ID_GUIDE)
        raise SystemExit(0)
    pick = max(1, min(args.pick, len(candidates))) if candidates else 0
    chosen = candidates[pick - 1] if pick else None
    if not chosen:
        raise SystemExit(
            "未找到匹配账号。请提供准确的 TikTok 主页链接，"
            "或带 sec_uid 参数的分享链接以便精准查询。\n" + SEC_USER_ID_GUIDE
        )
    print(f"已选定第 {pick} 个候选：{escape_md(chosen.get('userName'))} (@{escape_md(chosen.get('userHandle'))})")
    print("如非目标账号，请带 --pick N 重新指定，或提供主页链接 / 带 sec_uid 参数的分享链接精确定位。\n")
    return {
        "secUserId": str(chosen.get("secUserId") or ""),
        "profile": normalize_profile(chosen),
        "candidates": candidates,
        "exactMatch": False,
        "via": "searchUser",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok 账号深度分析（基础信息 / 主页作品 / 喜欢作品）")
    parser.add_argument("--account", required=True,
                        help="TikTok 账号标识：主页链接 / @handle / secUserId / 带 sec_uid 参数的分享链接 / 昵称或关键词")
    parser.add_argument("--resolve", action="store_true",
                        help="只定位账号（仅 1 次搜索调用），不拉取作品与喜欢列表")
    parser.add_argument("--pick", default=1, type=int, help="从候选账号中选择第 N 个（默认 1）")
    parser.add_argument("--types", choices=("profile", "works", "favorites", "all"), default="all",
                        help="查询类型，默认 all（基础信息+主页作品+喜欢作品）")
    parser.add_argument("--count", default=10, type=int, help="作品与喜欢列表每页条数（1~50，默认 10）")
    parser.add_argument("--works-offset", default=0, type=int, help="主页作品显示偏移（本地切片，默认 0）")
    parser.add_argument("--cursor", default=None, help="喜欢列表翻页游标；首页不传，翻页传上一次输出提示的 cursor")
    parser.add_argument("--api-key", default=None, help="临时 API Key；优先级高于环境变量")
    parser.add_argument("--raw", action="store_true", help="输出原始 JSON")
    parser.add_argument("--save-json", nargs="?", const=DEFAULT_SAVE_PATH, default=None,
                        metavar="PATH", help="查询结果保存为 JSON（供 HTML 报告使用）；"
                                            f"不带路径时默认保存到 {DEFAULT_SAVE_PATH}")
    args = parser.parse_args()

    args.account = (args.account or "").strip()
    if not args.account:
        raise SystemExit("错误：--account 不能为空")
    if not 1 <= args.count <= 50:
        raise SystemExit("错误：--count 必须在 1~50 之间")
    if args.works_offset < 0:
        raise SystemExit("错误：--works-offset 不能小于 0")
    if args.pick < 1:
        raise SystemExit("错误：--pick 不能小于 1")

    parsed = parse_account(args.account)
    if not parsed["sec_user_id"] and not parsed["handle"] and not parsed["keyword"]:
        raise SystemExit(
            "「{input}」无法识别，请提供 TikTok 主页链接、@handle、secUserId 或昵称 / 关键词。".format(
                input=args.account))

    kinds = ["profile", "works", "favorites"] if args.types == "all" else [args.types]

    try:
        api_key = resolve_api_key(args.api_key)
    except ValueError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        print(API_KEY_REMINDER, file=sys.stderr)
        sys.exit(1)

    print(f"账号定位：{args.account}")
    print(f"{API_KEY_REMINDER}\n")

    saved: Dict[str, Any] = {
        "meta": {
            "accountInput": args.account,
            "types": kinds,
            "count": args.count,
            "generatedAt": datetime.now(tz=BEIJING).strftime("%Y-%m-%d %H:%M:%S"),
        },
        "profile": None,
        "works": None,
        "favorites": None,
    }

    failures = 0
    try:
        account = resolve_account(parsed, args, api_key)
    except ApiError as exc:
        failures += 1
        print(f"账号定位失败：{describe_api_error(exc)}")
        if exc.code in (3103, 3105):
            print(API_KEY_REMINDER)
        print()
        sys.exit(1)
    except Exception as exc:
        failures += 1
        print(f"账号定位失败：{exc}")
        sys.exit(1)

    sec_user_id = account["secUserId"]
    saved["meta"]["resolvedVia"] = account["via"]
    saved["meta"]["pick"] = args.pick
    profile = account["profile"]

    works_all: List[Dict[str, Any]] = []
    works_page: List[Dict[str, Any]] = []
    favorites_page: List[Dict[str, Any]] = []
    fav_has_more: Any = None
    fav_next_cursor: Any = None

    # 主页作品（profile 来自 searchUser 时仍需拉取作品列表）
    if "works" in kinds:
        try:
            data = call_api("works", {"secUserId": sec_user_id, "source": SOURCE}, api_key)
            if args.raw:
                print("### 主页作品原始返回")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                print()
            else:
                works_all = sort_works_by_time(extract_work_items(data))
                works_page = [
                    normalize_work(item, idx)
                    for idx, item in enumerate(works_all, 1)
                ][args.works_offset: args.works_offset + args.count]
                print(f"### 📊 主页作品（按发布时间倒序）")
                print(f"主页作品：本页 {len(works_page)} 条 | 已拉取共 {len(works_all)} 条 | 显示偏移：{args.works_offset}")
                print()
                if works_page:
                    print(render_works(works_page, 0))
                else:
                    print("暂无数据")
                print()
                # secUserId 直接定位时，从作品 authorData 补全账号信息
                if profile is None and works_all:
                    profile = normalize_profile(works_all[0].get("authorData") or {})
                # searchUser 解析的账号缺少地区 / 签名 / 认证等字段，从作品 authorData 补齐
                elif profile is not None and works_all:
                    extra = normalize_profile(works_all[0].get("authorData") or {})
                    for key in ("area", "signature", "verify", "avatar", "userId"):
                        if not profile.get(key) and extra.get(key):
                            profile[key] = extra[key]
        except ApiError as exc:
            failures += 1
            print(f"主页作品查询失败：{describe_api_error(exc)}")
            if exc.code in (3103, 3105):
                print(API_KEY_REMINDER)
            print()
        except Exception as exc:
            failures += 1
            print(f"主页作品查询失败：{exc}")
            print()

    # 喜欢作品
    if "favorites" in kinds:
        try:
            payload: Dict[str, Any] = {"sec_user_id": sec_user_id, "source": SOURCE}
            if args.cursor:
                try:
                    payload["max_cursor"] = int(args.cursor)
                except ValueError:
                    raise SystemExit("错误：--cursor 必须为整数游标")
            else:
                payload["max_cursor"] = 0
            data = call_api("favorites", payload, api_key)
            if args.raw:
                print("### 喜欢作品原始返回")
                print(json.dumps(data, ensure_ascii=False, indent=2))
                print()
            else:
                data = data if isinstance(data, dict) else {}
                fav_items = sort_works_by_time(extract_work_items(data))
                fav_has_more = data.get("hasMore")
                fav_next_cursor = data.get("nextCursor")
                favorites_page = [
                    normalize_favorite(item, idx)
                    for idx, item in enumerate(fav_items[: args.count], 1)
                ]
                print("### 🧡 喜欢作品（按发布时间倒序）")
                info = f"喜欢作品：本页 {len(favorites_page)} 条 | hasMore：{fav_has_more}"
                if fav_has_more == 1 and fav_next_cursor:
                    info += f" | 下一页 cursor：{fav_next_cursor}"
                print(info)
                print()
                if favorites_page:
                    print(render_favorites(favorites_page))
                else:
                    print("暂无数据（该账号的喜欢列表可能已设为私密）")
                print()
        except ApiError as exc:
            failures += 1
            print(f"喜欢作品查询失败：{describe_api_error(exc)}")
            if exc.code in (3103, 3105):
                print(API_KEY_REMINDER)
            print()
        except SystemExit:
            raise
        except Exception as exc:
            failures += 1
            print(f"喜欢作品查询失败：{exc}")
            print()

    # 账号基础信息
    if "profile" in kinds:
        if args.raw:
            pass
        elif profile:
            name = escape_md(profile.get("name")) or "—"
            handle = escape_md(profile.get("handle")) or "—"
            print(f"### 👤 账号基础信息 — {name} (@{handle})")
            print(render_profile(profile))
            print()
        else:
            print("### 👤 账号基础信息")
            print("该账号暂无主页作品数据，仅能确认 secUserId：`" + escape_md(sec_user_id) + "`")
            print()

    if args.save_json:
        try:
            path = args.save_json
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            saved["profile"] = profile
            saved["works"] = {
                "items": works_page,
                "paging": {"apiTotal": len(works_all), "offset": args.works_offset, "count": args.count},
            }
            saved["favorites"] = {
                "items": favorites_page,
                "paging": {"hasMore": fav_has_more, "nextCursor": fav_next_cursor},
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(saved, f, ensure_ascii=False, indent=2)
            print(f"查询结果已保存：{path}")
        except OSError as exc:
            print(f"结果保存失败：{exc}", file=sys.stderr)

    if failures and failures == len(kinds):
        sys.exit(1)


if __name__ == "__main__":
    main()
