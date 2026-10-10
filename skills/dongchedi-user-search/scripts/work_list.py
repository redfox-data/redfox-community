#!/usr/bin/env python3
"""
懂车帝用户作品列表脚本
调用 Redfox API 获取指定用户（作者）的作品列表
用法: python3 work_list.py "<userId>" [--date yesterday]
"""

import argparse
import datetime
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://redfox.hk/story/api/dongchedi/workList"
SOURCE = "懂车帝用户作品列表-GitHub"

# 作品类型映射：1-文章，2-视频，7-图文动态，9-文章（长图文）
WORK_TYPE_LABELS = {1: "文章", 2: "视频", 7: "图文动态", 9: "文章"}

CONFIG_FILE = Path.home() / ".qoder" / "apis" / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"

ERROR_HINTS = {
    3106: "缺少 API Key，请配置环境变量 REDFOX_API_KEY 后重试",
    3107: "API Key 无效，请前往 https://redfox.hk/settings/api-keys 检查密钥",
    3108: "请求频率超限，请稍后重试",
}


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


def _format_time(ts) -> str:
    """Unix 时间戳（秒）转 YYYY-MM-DD HH:MM"""
    try:
        ts = int(ts)
    except (TypeError, ValueError):
        return ""
    if ts <= 0:
        return ""
    try:
        return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except (OverflowError, OSError, ValueError):
        return ""


def _resolve_date(value: str) -> str:
    """解析 --date 参数：支持 YYYY-MM-DD、yesterday/昨天、today/今天"""
    value = (value or "").strip()
    if not value:
        return ""
    key = value.lower()
    if key in ("yesterday", "昨天"):
        return (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    if key in ("today", "今天"):
        return datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        datetime.datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        print(
            f"[error] --date 需要 YYYY-MM-DD 格式或 yesterday/today，收到: {value}",
            file=sys.stderr,
        )
        sys.exit(1)
    return value


def format_works(works: list) -> list:
    """
    格式化作品列表。
    API 返回字段：authorId, authorName, collectCount, commentCount, coverUrl,
    description, durationSeconds, imageUrlList, likeCount, publishTime,
    readCount, title, videoId, workId, workType, workUrl
    """
    items = []
    for work in works:
        if not isinstance(work, dict):
            continue

        try:
            work_type = int(work.get("workType"))
        except (TypeError, ValueError):
            work_type = 0

        items.append({
            "work_id": str(work.get("workId") or ""),
            "title": _escape_markdown(work.get("title") or work.get("description") or ""),
            "work_type": work_type,
            "work_type_label": WORK_TYPE_LABELS.get(work_type, "其他"),
            "publish_time": int(work.get("publishTime") or 0),
            "publish_time_str": _format_time(work.get("publishTime")),
            "read_count": int(work.get("readCount") or 0),
            "like_count": int(work.get("likeCount") or 0),
            "comment_count": int(work.get("commentCount") or 0),
            "collect_count": int(work.get("collectCount") or 0),
            "duration_seconds": int(work.get("durationSeconds") or 0),
            "cover_url": (work.get("coverUrl") or "").strip(),
            "image_urls": [u for u in (work.get("imageUrlList") or []) if isinstance(u, str)],
            "video_id": (work.get("videoId") or "").strip(),
            "work_url": (work.get("workUrl") or "").strip(),
            "author_name": _escape_markdown(work.get("authorName") or ""),
            "author_id": str(work.get("authorId") or ""),
        })
    return items


def fetch_works(user_id: str, date_filter: str = "") -> dict:
    api_key = get_api_key()
    if not api_key:
        print("[error] 未检测到 RedFox API Key，请任选一种方式配置：", file=sys.stderr)
        print(f"  1. 环境变量（推荐）：export {ENV_KEY}=ak_你的密钥", file=sys.stderr)
        print("  2. 配置文件：echo '{\"api_key\":\"ak_你的密钥\"}' > ~/.qoder/apis/redfox.json", file=sys.stderr)
        print("  注册地址：https://redfox.hk/settings/api-keys?source=github", file=sys.stderr)
        sys.exit(1)

    payload = json.dumps({
        "userId": user_id,
        "cursor": 0,  # 接口不支持分页，cursor 固定传 0
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
        kwargs = {"timeout": 60}
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

    data = result.get("data") or []
    # 兼容 data 被包裹为对象的情况
    if isinstance(data, dict):
        data = data.get("workList") or data.get("list") or []

    works = format_works(data)
    total_count = len(works)
    # 内部按发布时间（本地时区）筛选指定日期的作品
    if date_filter:
        works = [
            w for w in works
            if (w.get("publish_time_str") or "")[:10] == date_filter
        ]
    return {
        "user_id": user_id,
        "date": date_filter,
        "total_count": total_count,
        "count": len(works),
        "works": works,
    }


def main():
    parser = argparse.ArgumentParser(description="懂车帝用户作品列表")
    parser.add_argument("user_id", help="用户ID（来自 search_user.py 返回的 user_id）")
    parser.add_argument(
        "--date", dest="date", default="",
        help="按发布时间筛选指定日期（YYYY-MM-DD / yesterday / today），默认不过滤",
    )
    args = parser.parse_args()

    user_id = args.user_id.strip()
    if not user_id:
        print("[error] 用户ID不能为空", file=sys.stderr)
        sys.exit(1)

    date_filter = _resolve_date(args.date)

    result = fetch_works(user_id, date_filter)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
