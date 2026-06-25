#!/usr/bin/env python
"""
B站账号作品列表实时查询脚本
调用 Redfox API 查询指定B站UP主的作品列表
用法: python fetch_bili_user_works.py "<uid>" [--cursor 翻页游标]

接口：POST https://redfox.hk/story/api/bili/userWorkList
请求参数：
  uid     string  必填  B站账号UID
  cursor  string  非必填  翻页参数，第一页不传，传下次请求的cursor值获取下一页
鉴权：Header REDFOX_API_KEY

接口返回字段说明：
  data 层级：
    totalWorkCount  总作品数
    cursor          翻页游标
    opusInfoList    作品列表

  opusInfoList 中每条：
  bvId / avId           视频 BV号 / AV号
  url                   完整视频链接
  title                 标题
  nickname              UP主昵称
  totalDanmakuCount     弹幕数
  commentNum            评论数
  collectNum            收藏数
  viewNum               播放量
  cover                 封面（相对协议 //i0.hdslb.com/...，需补 https:）
  publishTime           发布时间戳（秒级）
  tags                  标签（逗号分隔字符串）
  categoryName          分区名称
  duration              视频时长（秒）
"""

import sys
import os
import io
import json
import time
import argparse
import urllib.request
import urllib.error
from datetime import datetime

# ── 强制 stdout 使用 UTF-8，解决 Windows 终端乱码 ──
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

API_URL = "https://redfox.hk/story/api/bili/userWorkList"
MAX_RETRIES = 3          # 最大重试次数
RETRY_DELAY_BASE = 2     # 重试基础等待秒数（指数退避）


def get_api_key() -> str:
    val = os.environ.get("REDFOX_API_KEY", "")
    if not val:
        print("[error] 未找到环境变量 REDFOX_API_KEY，请确认已设置 API Key", file=sys.stderr)
        sys.exit(1)
    return val


def normalize_cover(cover) -> str:
    """补全相对协议封面链接，并将 http 转为 https"""
    if not cover:
        return ""
    cover = str(cover)
    if cover.startswith("//"):
        return "https:" + cover
    if cover.startswith("http://"):
        return "https://" + cover[7:]
    return cover


def build_video_url(item: dict) -> str:
    """优先使用 url 字段；若为空则用 bvId 拼接标准 B站链接"""
    url = item.get("url") or ""
    if url:
        return url
    bv_id = item.get("bvId") or ""
    if bv_id:
        return f"https://www.bilibili.com/video/{bv_id}"
    return ""


def fmt_publish_time(ts) -> str:
    """秒级时间戳转可读日期"""
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts) if ts else ""


def fmt_duration(seconds) -> str:
    """秒数转 mm:ss 或 hh:mm:ss 格式"""
    try:
        secs = int(seconds)
        if secs < 0:
            return str(seconds)
        h, remainder = divmod(secs, 3600)
        m, s = divmod(remainder, 60)
        if h > 0:
            return f"{h}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
    except Exception:
        return str(seconds) if seconds else "00:00"


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


def format_works(works: list) -> list:
    items = []
    for art in works:
        items.append({
            "title":         safe_str(art.get("title")),
            "author":        safe_str(art.get("nickname")),
            "danmaku_count": safe_int(art.get("totalDanmakuCount")),
            "comment_count": safe_int(art.get("commentNum")),
            "collect_count": safe_int(art.get("collectNum")),
            "play_count":    safe_int(art.get("viewNum")),
            "work_url":      build_video_url(art),
            "publish_time":  fmt_publish_time(art.get("publishTime")),
            "cover_url":     normalize_cover(art.get("cover")),
            "bv_id":         safe_str(art.get("bvId")),
            "tags":          safe_str(art.get("tags")),
            "category":      safe_str(art.get("categoryName")),
            "duration":      fmt_duration(art.get("duration")),
        })
    items.sort(key=lambda x: x["play_count"], reverse=True)
    return items


def fetch_user_works(uid: str, cursor: str = "") -> dict:
    api_key = get_api_key()

    body = {"uid": uid, "source": "B站搜账号下作品集-GitHub"}
    if cursor:
        body["cursor"] = cursor

    payload = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={
            "Content-Type":  "application/json",
            "X-API-Key":     api_key,
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

    code = result.get("code")
    if code != 2000:
        print(f"[error] 接口返回错误: code={code}, msg={result.get('msg', '未知')}", file=sys.stderr)
        sys.exit(1)

    data = result.get("data") or {}
    works_list = data.get("opusInfoList") or []
    next_cursor = data.get("cursor") or data.get("nextCursor") or ""
    # 排除"no_more"等非游标标识值
    _no_more_markers = {"no_more", "none", "null", "0", "-1"}
    has_next = bool(next_cursor) and next_cursor.lower() not in _no_more_markers
    total_work_count = data.get("totalWorkCount") or 0

    # 提取UP主基础信息
    user_info = {}
    if works_list:
        first = works_list[0]
        user_info = {
            "nickname": safe_str(first.get("nickname")),
            "mid": uid,
        }
    # 如果接口单独返回了用户信息字段
    if "userInfo" in data:
        ui = data["userInfo"]
        user_info = {
            "nickname": safe_str(ui.get("nickname") or ui.get("name") or user_info.get("nickname")),
            "mid": safe_str(ui.get("mid") or ui.get("uid") or uid),
            "fan_count": safe_int(ui.get("fanCount") or ui.get("fans")),
            "sign": safe_str(ui.get("sign")),
            "level": safe_str(ui.get("level")),
            "avatar": safe_str(ui.get("avatar") or ui.get("face")),
        }

    return {
        "user_info":         user_info,
        "works":             format_works(works_list),
        "cursor":            next_cursor,
        "has_next":          has_next,
        "total_count":       len(works_list),
        "total_work_count":  safe_int(total_work_count),
    }


def main():
    parser = argparse.ArgumentParser(description="B站账号作品列表实时查询")
    parser.add_argument("uid", help="B站账号UID（纯数字）")
    parser.add_argument(
        "--cursor", dest="cursor", default="",
        help="翻页游标，第一页不传，传上次返回的cursor值获取下一页",
    )
    args = parser.parse_args()

    uid = args.uid.strip()
    if not uid:
        print("[error] UID不能为空", file=sys.stderr)
        sys.exit(1)

    result = fetch_user_works(uid, args.cursor)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
