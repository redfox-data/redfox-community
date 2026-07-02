#!/usr/bin/env python
"""
小红书账号作品列表实时查询脚本
调用 Redfox API 查询指定小红书用户的作品列表
用法: python fetch_xhs_user_works.py "<userId>" [--offset 翻页偏移量]

接口：POST https://redfox.hk/story/api/xhs/ability/userWorkList
请求参数：
  userId  string  必填  小红书账号userId
  offset  string  必填  偏移量，取作品列表中的offset值（第一页传空字符串）
鉴权：Header REDFOX_API_KEY

接口返回字段说明（数组，每条作品）：
  noteId            作品ID
  noteTitle         标题
  noteUrl           作品链接
  noteType          类型（normal=图文, video=视频）
  authorId          用户ID
  authorName        昵称
  authorAvatar      头像
  bio               简介
  thumbCount        点赞数
  replyCount        评论数
  favoriteCount     收藏数
  forwardCount      分享数
  releaseTime       发布时间
  syncTime          更新时间
  lastEditTime      编辑时间戳
  thumbnail         封面图
  pinned            是否置顶
  offset            翻页游标
  hasNextPage       是否还有更多
  picList           图片列表
"""

import sys
import os
import io
import json
import time
import argparse
import urllib.request
import urllib.error

# ── 强制 stdout 使用 UTF-8，解决 Windows 终端乱码 ──
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

API_URL = "https://redfox.hk/story/api/xhs/ability/userWorkList"
MAX_RETRIES = 3          # 最大重试次数
RETRY_DELAY_BASE = 2     # 重试基础等待秒数（指数退避）


def get_api_key() -> str:
    val = os.environ.get("REDFOX_API_KEY", "")
    if not val:
        print("[error] 未找到环境变量 REDFOX_API_KEY，请确认已设置 API Key", file=sys.stderr)
        sys.exit(1)
    return val


def safe_str(val) -> str:
    """安全转字符串，None 返回空串"""
    if val is None:
        return ""
    return str(val).strip()


def safe_int(val, default=0) -> int:
    """安全转整数，None / 异常返回默认值"""
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default


def safe_bool(val, default=False) -> bool:
    """安全转布尔值"""
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "1", "yes")


def normalize_note_type(note_type: str) -> str:
    """将 noteType 转为中文描述"""
    t = safe_str(note_type).lower()
    if t == "video":
        return "视频"
    return "图文"


def format_works(works: list) -> list:
    items = []
    for art in works:
        items.append({
            "title":          safe_str(art.get("noteTitle")),
            "author":         safe_str(art.get("authorName")),
            "thumb_count":    safe_int(art.get("thumbCount")),
            "reply_count":    safe_int(art.get("replyCount")),
            "favorite_count": safe_int(art.get("favoriteCount")),
            "forward_count":  safe_int(art.get("forwardCount")),
            "work_url":       safe_str(art.get("noteUrl")),
            "release_time":   safe_str(art.get("releaseTime")),
            "note_type":      normalize_note_type(art.get("noteType")),
            "thumbnail":      safe_str(art.get("thumbnail")),
            "note_id":        safe_str(art.get("noteId")),
            "pinned":         safe_bool(art.get("pinned")),
        })
    return items


def fetch_user_works(user_id: str, offset: str = "") -> dict:
    api_key = get_api_key()

    body = {
        "userId": user_id,
        "offset": offset,
        "source": "小红书账号作品追踪-GitHub",
    }

    payload = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type":  "application/json",
            "REDFOX_API_KEY": api_key,
            "User-Agent":    "QoderWork/1.0",
        },
        method="POST",
    )

    # ── 带指数退避的重试机制 ──
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            break  # 成功，跳出重试循环
        except urllib.error.HTTPError as e:
            # HTTP 状态码错误（4xx/5xx）不重试，直接退出
            body_text = e.read().decode("utf-8", errors="replace")
            print(f"[error] HTTP {e.code}: {body_text}", file=sys.stderr)
            sys.exit(1)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            # 网络层错误（DNS失败、超时、连接重置等）可重试
            last_error = e
            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY_BASE * (2 ** (attempt - 1))
                print(
                    f"[warn] 第{attempt}次请求失败: {e}，{delay}秒后重试...",
                    file=sys.stderr,
                )
                time.sleep(delay)
            else:
                print(
                    f"[error] 网络请求失败（已重试{MAX_RETRIES}次）: {last_error}",
                    file=sys.stderr,
                )
                sys.exit(1)
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"[error] 数据解析异常: {e}", file=sys.stderr)
            sys.exit(1)

    # ── 解析响应 ──
    # 兼容两种格式：直接数组 或 {code, data: [...]}
    works_list = []
    if isinstance(result, list):
        works_list = result
    elif isinstance(result, dict):
        code = result.get("code")
        if code and code != 2000:
            print(f"[error] 接口返回错误: code={code}, msg={result.get('msg', '未知')}", file=sys.stderr)
            sys.exit(1)
        data = result.get("data")
        if isinstance(data, list):
            works_list = data
        elif isinstance(data, dict):
            works_list = data.get("list") or data.get("works") or []
        else:
            works_list = []
    else:
        works_list = []

    # 提取作品列表
    works = format_works(works_list)

    # 提取翻页信息：从最后一条作品的 offset 和 hasNextPage 字段获取
    next_offset = ""
    has_next = False
    if works_list:
        last_item = works_list[-1]
        next_offset = safe_str(last_item.get("offset"))
        has_next = safe_bool(last_item.get("hasNextPage"))

    # 排除无效 offset 标识
    _no_more_markers = {"no_more", "none", "null", "0", "-1", ""}
    if next_offset.lower() in _no_more_markers:
        has_next = False
        next_offset = ""

    # 提取博主基础信息（从第一条作品中获取）
    user_info = {}
    if works_list:
        first = works_list[0]
        user_info = {
            "nickname": safe_str(first.get("authorName")),
            "user_id":  user_id,
            "avatar":   safe_str(first.get("authorAvatar")),
            "bio":      safe_str(first.get("bio")),
        }

    return {
        "user_info":   user_info,
        "works":       works,
        "offset":      next_offset,
        "has_next":    has_next,
        "total_count": len(works_list),
    }


def main():
    parser = argparse.ArgumentParser(description="小红书账号作品列表实时查询")
    parser.add_argument("user_id", help="小红书账号 userId")
    parser.add_argument(
        "--offset", dest="offset", default="",
        help="翻页偏移量，第一页不传，传上次返回的 offset 值获取下一页",
    )
    args = parser.parse_args()

    user_id = args.user_id.strip()
    if not user_id:
        print("[error] userId不能为空", file=sys.stderr)
        sys.exit(1)

    result = fetch_user_works(user_id, args.offset)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
