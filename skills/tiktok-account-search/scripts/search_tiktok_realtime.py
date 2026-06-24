#!/usr/bin/env python3
"""
TikTok 账号搜索脚本
调用 Redfox API 搜索 TikTok 账号数据
用法: python3 search_tiktok_realtime.py "<关键词>" [--page 1]
"""

import sys
import os
import json
import argparse
import ssl
import urllib.request
import urllib.error

API_URL = "https://redfox.hk/story/api/deepSearch/tk/searchUser"

PAGE_SIZE = 10  # 每页 10 条


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
        # 部分系统证书链不完整，放宽验证以保证可用性
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    except Exception:
        ctx = None
    return ctx


def format_accounts(user_list: list) -> list:
    """
    格式化账号列表。
    API 返回结构：userList[].data 包含用户信息
    已知字段：account, avatar(array), followerCount, nickname, secUid, signature, uid
    """
    items = []
    for entry in user_list:
        # 数据可能在 entry["data"] 或直接在 entry 中
        acc = entry.get("data") if isinstance(entry, dict) and "data" in entry else entry
        if not isinstance(acc, dict):
            continue

        nickname = (acc.get("nickname") or "").strip()
        account_id = (acc.get("account") or acc.get("uniqueId") or "").strip()
        follower_count = acc.get("followerCount") or acc.get("follower_count") or 0
        following_count = acc.get("followingCount") or acc.get("following_count") or 0
        like_count = acc.get("heartCount") or acc.get("heart_count") or acc.get("likeCount") or 0
        video_count = acc.get("videoCount") or acc.get("video_count") or acc.get("awemeCount") or 0
        signature = (acc.get("signature") or acc.get("desc") or acc.get("bio") or "").strip()
        sec_uid = (acc.get("secUid") or "").strip()
        uid = (acc.get("uid") or "").strip()

        # avatar 可能是数组或字符串
        avatar_raw = acc.get("avatar") or acc.get("avatarLarger") or ""
        if isinstance(avatar_raw, list):
            avatar = avatar_raw[0] if avatar_raw else ""
        else:
            avatar = str(avatar_raw)

        verified = acc.get("verified") or acc.get("isVerified") or False
        region = (acc.get("region") or acc.get("country") or "").strip()

        # 构建主页链接
        profile_url = acc.get("profileUrl") or acc.get("profile_url") or ""
        if not profile_url and account_id:
            profile_url = f"https://www.tiktok.com/@{account_id}"

        # 清理签名中的换行
        signature = signature.replace("\n", " ").replace("\r", "")
        if len(signature) > 60:
            signature = signature[:60] + "..."

        items.append({
            "nickname":        nickname,
            "account_id":      account_id,
            "follower_count":  int(follower_count) if follower_count else 0,
            "following_count": int(following_count) if following_count else 0,
            "like_count":      int(like_count) if like_count else 0,
            "video_count":     int(video_count) if video_count else 0,
            "signature":       signature,
            "avatar":          avatar,
            "verified":        bool(verified),
            "region":          region,
            "sec_uid":         sec_uid,
            "uid":             uid,
            "profile_url":     profile_url,
        })
    # 按粉丝数降序排列
    items.sort(key=lambda x: x["follower_count"], reverse=True)
    return items


def search(keyword: str, page: int = 1, rid: str = "") -> dict:
    api_key = get_api_key()
    cursor = (page - 1) * PAGE_SIZE

    payload_dict = {
        "keyword": keyword,
        "cursor":  cursor,
        "source":  "TikTok账号搜索-GitHub",
    }
    # 第一页不传 rid，翻页时传入上一页返回的 rid
    if rid:
        payload_dict["rid"] = rid

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

    # API 返回 userList
    user_list = data.get("userList") or data.get("list") or data.get("users") or []
    accounts_count = len(user_list)

    # 翻页判断：API 返回 hasMore 或按数量判断
    has_more_flag = data.get("hasMore")
    if has_more_flag is not None:
        has_next = bool(has_more_flag) or (isinstance(has_more_flag, int) and has_more_flag > 0)
    else:
        has_next = accounts_count >= PAGE_SIZE

    # 提取 rid 供翻页时使用
    next_rid = data.get("rid") or ""

    return {
        "accounts": format_accounts(user_list),
        "page":     page,
        "has_next": has_next,
        "total":    accounts_count,
        "rid":      next_rid,
    }


def main():
    parser = argparse.ArgumentParser(description="TikTok 账号实时搜索")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument(
        "--page", dest="page", type=int, default=1,
        help="页码，从1开始（默认1）",
    )
    parser.add_argument(
        "--rid", dest="rid", type=str, default="",
        help="翻页游标，从上一页响应中获取（第1页不传）",
    )
    args = parser.parse_args()

    keyword = args.keyword.strip()
    if not keyword:
        print("[error] 关键词不能为空", file=sys.stderr)
        sys.exit(1)
    if args.page < 1:
        print("[error] 页码必须为正整数", file=sys.stderr)
        sys.exit(1)

    result = search(keyword, args.page, args.rid)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
