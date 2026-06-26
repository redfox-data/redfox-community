#!/usr/bin/env python3
"""
B站关键词搜账号脚本
调用 Redfox API 根据关键词搜索B站账号
用法: python3 search_bili_user.py "<关键词>" [--order 排序] [--page 页码]

接口: https://redfox.hk/story/api/bili/userSearch (POST)

请求字段:
  keyword   搜索关键词（必填）
  order     排序方式: totalrank(综合排序) / fans(按粉丝数)
  page      页码，从1开始
  source    来源标识

接口返回字段说明（data.userList 中每条）:
  uid         B站用户UID
  nickname    昵称
  avatar      头像链接（http协议，需转https）
  description 个人简介
  fansNum     粉丝数
  gender      性别 (1=男 2=女 3=未知)
  level       B站等级 (0-6)
  isLiving    是否在直播 (0/1)
  isUploader  是否UP主 (0/1)
  liveRoomId  直播间ID（0表示无直播间）
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.error

API_URL = "https://redfox.hk/story/api/bili/userSearch"

ORDER_MAP = {
    "totalrank": "综合排序",
    "fans":      "按粉丝数",
}


def get_api_key() -> str:
    val = os.environ.get("REDFOX_API_KEY", "")
    if not val:
        print("[error] 未找到环境变量 REDFOX_API_KEY，请确认已设置 API Key", file=sys.stderr)
        sys.exit(1)
    return val


def normalize_avatar(url: str) -> str:
    """将 http:// 头像链接转为 https://"""
    if url and url.startswith("http://"):
        return "https://" + url[len("http://"):]
    return url or ""


def build_space_url(uid: int) -> str:
    """根据UID拼接B站个人主页链接"""
    return f"https://space.bilibili.com/{uid}" if uid else ""


def format_users(users: list) -> list:
    items = []
    for u in users:
        items.append({
            "uid":          u.get("uid", 0),
            "nickname":     u.get("nickname", "").strip(),
            "avatar":       normalize_avatar(u.get("avatar", "")),
            "description":  (u.get("description", "") or "").strip(),
            "fans_num":     u.get("fansNum", 0) or 0,
            "gender":       u.get("gender", 3),
            "level":        u.get("level", 0),
            "is_living":    u.get("isLiving", 0) == 1,
            "is_uploader":  u.get("isUploader", 0) == 1,
            "live_room_id": u.get("liveRoomId", 0),
            "space_url":    build_space_url(u.get("uid", 0)),
        })
    return items


def search(keyword: str, order: str, page: int = 1) -> dict:
    api_key = get_api_key()
    payload = json.dumps({
        "keyword": keyword,
        "order":   order,
        "page":    page,
        "source":  "B站关键词搜账号-GitHub",
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
    user_list = data.get("userList") or []

    # 当前页返回数 >= 20 条则认为有更多数据
    has_next = len(user_list) >= 20

    return {
        "users":          format_users(user_list),
        "order_label":    ORDER_MAP.get(order, order),
        "page":           page,
        "has_next":       has_next,
        "total_count":    len(user_list),
    }


def main():
    parser = argparse.ArgumentParser(description="B站关键词搜账号")
    parser.add_argument("keyword", help="搜索关键词")
    parser.add_argument(
        "--order", dest="order", default="fans",
        choices=["totalrank", "fans"],
        help="排序方式：totalrank-综合排序 fans-按粉丝数（默认fans）",
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

    result = search(keyword, args.order, args.page)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
