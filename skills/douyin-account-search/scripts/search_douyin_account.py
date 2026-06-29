#!/usr/bin/env python3
"""
抖音账号搜索脚本
调用 Redfox API 搜索抖音账号数据
用法: python3 search_douyin_account.py "<关键词>" [--page 1]
"""

import sys
import os
import json
import argparse
import ssl
import urllib.request
import urllib.error

API_URL = "https://redfox.hk/story/api/dy/user/search"

PAGE_SIZE = 20  # 每页 10 条


def get_api_key() -> str:
    val = os.environ.get("REDFOX_API_KEY", "")
    if not val:
        print("[error] 未找到环境变量 REDFOX_API_KEY，请确认已设置 API Key", file=sys.stderr)
        sys.exit(1)
    return val


def _ssl_context():
    """创建兼容多环境的 SSL 上下文"""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    except Exception:
        ctx = None
    return ctx


def format_accounts(user_list: list) -> list:
    """
    格式化账号列表。
    API 返回字段：displayName, fansCount, totalLikes, secureId, bio, isVerified, avatarUrl
    """
    items = []
    for acc in user_list:
        if not isinstance(acc, dict):
            continue

        nickname = (acc.get("displayName") or acc.get("nickname") or "").strip()
        # Markdown 转义：防止 _、`、*、| 等字符破坏表格渲染
        for ch in ["_", "`", "*", "|", "[", "]"]:
            nickname = nickname.replace(ch, "\\" + ch)
        account_id = (acc.get("uniqueName") or acc.get("accountId") or acc.get("shortId") or "").strip()
        follower_count = acc.get("fansCount") or acc.get("followerCount") or acc.get("follower_count") or 0
        like_count = acc.get("totalLikes") or acc.get("heartCount") or acc.get("likeCount") or 0
        follow_count = acc.get("followCount") or acc.get("follow_count") or 0
        video_count = acc.get("videoCount") or acc.get("video_count") or 0
        signature = (acc.get("bio") or acc.get("signature") or acc.get("desc") or "").strip()

        # avatar
        avatar = (acc.get("avatarUrl") or acc.get("avatar") or acc.get("avatarLarger") or "").strip()

        verified = acc.get("isVerified") or acc.get("verified") or False
        sec_uid = (acc.get("secureId") or acc.get("secUid") or "").strip()
        uid = (acc.get("userId") or acc.get("uid") or "").strip()

        # 构建主页链接: https://www.douyin.com/user/{secureId}
        profile_url = acc.get("profileUrl") or acc.get("profile_url") or ""
        if not profile_url and sec_uid:
            profile_url = f"https://www.douyin.com/user/{sec_uid}"

        # 清理签名中的换行
        signature = signature.replace("\n", " ").replace("\r", "")
        if len(signature) > 60:
            signature = signature[:60] + "..."

        items.append({
            "nickname":       nickname,
            "account_id":     account_id,
            "follower_count": int(follower_count) if follower_count else 0,
            "like_count":     int(like_count) if like_count else 0,
            "follow_count":   int(follow_count) if follow_count else 0,
            "video_count":    int(video_count) if video_count else 0,
            "signature":      signature,
            "avatar":         avatar,
            "verified":       bool(verified),
            "sec_uid":        sec_uid,
            "uid":            uid,
            "profile_url":    profile_url,
        })
    return items


def search(keyword: str, page: int = 1) -> dict:
    api_key = get_api_key()
    offset = (page - 1) * PAGE_SIZE

    payload_dict = {
        "queryWord": keyword,
        "offset":    offset,
        "source":    "抖音账号搜索-GitHub",
    }

    payload = json.dumps(payload_dict).encode("utf-8")

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
        print(f"[error] 接口返回错误: code={code}, msg={result.get('msg', '未知')}", file=sys.stderr)
        sys.exit(1)

    data = result.get("data") or {}

    # API 返回 accountList
    user_list = data.get("accountList") or data.get("userList") or data.get("list") or data.get("users") or []
    accounts_count = len(user_list)

    # 翻页判断：API 返回 hasMore 或按数量判断
    has_more_flag = data.get("hasMore")
    if has_more_flag is not None:
        has_next = bool(has_more_flag) or (isinstance(has_more_flag, int) and has_more_flag > 0)
    else:
        has_next = accounts_count >= PAGE_SIZE

    return {
        "accounts": format_accounts(user_list),
        "page":     page,
        "has_next": has_next,
        "total":    accounts_count,
    }


def main():
    parser = argparse.ArgumentParser(description="抖音账号搜索")
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
