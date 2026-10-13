#!/usr/bin/env python3
"""
懂车帝用户搜索和作品订阅脚本
调用 Redfox API 按关键词搜索懂车帝用户
用法: python3 search_user.py "<关键词>" [--page 1]
"""

import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://redfox.hk/story/api/dongchedi/searchUser"
SOURCE = "懂车帝用户搜索和作品订阅-GitHub"

PAGE_SIZE = 10  # 接口每页约 10 条

CONFIG_FILE = Path.home() / ".qoder" / "apis" / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"

ERROR_HINTS = {
    3106: "缺少 API Key，请配置环境变量 REDFOX_API_KEY 后重试",
    3107: "API Key 无效，请前往 https://redfox.hk/settings/api-keys 检查密钥",
    3108: "请求频率超限，请稍后重试",
}

PROFILE_URL_TPL = "https://www.dongchedi.com/user/{user_id}"


def get_api_key():
    """按 环境变量 -> 配置文件 的顺序读取 API Key"""
    env_key = os.environ.get(ENV_KEY)
    if env_key:
        return env_key
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            key = data.get("api_key")
            if key:
                return key
        except (json.JSONDecodeError, OSError):
            pass
    return None


def _ssl_context():
    """创建兼容多环境的 SSL 上下文"""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    except Exception:
        ctx = None
    return ctx


def _escape_markdown(text: str) -> str:
    """清理换行并转义 Markdown 特殊字符，避免破坏表格与链接渲染"""
    text = (text or "").replace("\r", "").replace("\n", " ")
    for ch in ["|", "[", "]", "*", "`", "_"]:
        text = text.replace(ch, "\\" + ch)
    return text.strip()


def format_users(user_list: list) -> list:
    """
    格式化用户列表。
    API 返回字段：avatar, bio, displayName, followers, userId
    """
    items = []
    for user in user_list:
        if not isinstance(user, dict):
            continue
        user_id = str(user.get("userId") or "").strip()
        items.append({
            "nickname": _escape_markdown(user.get("displayName") or ""),
            "user_id": user_id,
            "followers": int(user.get("followers") or 0),
            "bio": _escape_markdown(user.get("bio") or ""),
            "avatar": (user.get("avatar") or "").strip(),
            "profile_url": PROFILE_URL_TPL.format(user_id=user_id) if user_id else "",
        })
    return items


def search(keyword: str, page: int) -> dict:
    api_key = get_api_key()
    if not api_key:
        print("[error] 未检测到 RedFox API Key，请任选一种方式配置：", file=sys.stderr)
        print(f"  1. 环境变量（推荐）：export {ENV_KEY}=ak_你的密钥", file=sys.stderr)
        print("  2. 配置文件：echo '{\"api_key\":\"ak_你的密钥\"}' > ~/.qoder/apis/redfox.json", file=sys.stderr)
        print("  注册地址：https://redfox.hk/settings/api-keys?source=github", file=sys.stderr)
        sys.exit(1)

    offset = (page - 1) * PAGE_SIZE
    payload = json.dumps({
        "keyword": keyword,
        "offset": offset,
        "source": SOURCE,
    }).encode("utf-8")

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

    ctx = _ssl_context()
    try:
        kwargs = {"timeout": 30}
        if ctx:
            kwargs["context"] = ctx
        with urllib.request.urlopen(req, **kwargs) as resp:
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
        hint = ERROR_HINTS.get(code, "")
        print(
            f"[error] 接口返回错误: code={code}, msg={result.get('msg', '未知')}"
            + (f"，{hint}" if hint else ""),
            file=sys.stderr,
        )
        sys.exit(1)

    data = result.get("data") or {}
    user_list = data.get("userList") or []

    # 翻页判断：接口返回 hasMore（1 有 / 0 无），缺失时按本页条数估算
    has_more = data.get("hasMore")
    if has_more is not None:
        try:
            has_next = int(has_more) > 0
        except (TypeError, ValueError):
            has_next = str(has_more).strip().lower() in ("true", "1")
    else:
        has_next = len(user_list) >= PAGE_SIZE

    return {
        "keyword": keyword,
        "page": page,
        "has_next": has_next,
        "next_offset": data.get("offset"),
        "total": len(user_list),
        "users": format_users(user_list),
    }


def main():
    parser = argparse.ArgumentParser(description="懂车帝用户搜索和作品订阅")
    parser.add_argument("keyword", help="搜索关键词")
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

    result = search(keyword, args.page)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
