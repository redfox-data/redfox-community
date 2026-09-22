#!/usr/bin/env python3
"""
公众号头条增长榜脚本
调用 Redfox API 获取公众号周度头条阅读增长榜（本周头条阅读 vs 上周头条阅读）。
榜单更新：每周一下午 16:30 更新新一期；未到更新时间时最新一期可能暂无数据，脚本自动回退展示上一期。

用法:
  python3 heima_rank.py                                  # 最新一期综合全部分类总榜（排序固定：头条增长率降序）
  python3 heima_rank.py --type 人文资讯                  # 按作者类别筛选（23 个固定类别）
  python3 heima_rank.py --date 2026-09-07                # 指定期数（周一）
  python3 heima_rank.py --page 2                         # 翻页（1-5）
  python3 heima_rank.py --list-types                     # 列出全部作者类别

接口返回字段说明（data 数组中每条）：
  account_id    公众号账号ID
  nickname      公众号昵称
  author_type   作者类别
  cur_read      本周头条阅读数
  prev_read     上周头条阅读数
  growth_val    阅读增长量
  growth_pct    阅读增长百分比（如 431.97 表示 431.97%）
  rank_date     榜单时间（统计周周一）
"""

import argparse
import difflib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta

API_URL = "https://redfox.hk/story/api/gzh/heima/rankList"
SOURCE = "公众号头条增长榜-GitHub"  # 接口请求携带的来源标识
MAX_PAGE = 5
PAGE_SIZE = 20
DEFAULT_FETCH_ATTEMPTS = 3  # 用户未指定日期时，最多尝试 3 个期数（当周及往前回退最多 2 周）找最近有数据的一期

AUTHOR_TYPES = [
    "人文资讯", "知识百科", "健康养生", "时尚潮流", "美食餐饮", "乐活生活",
    "旅游出行", "搞笑幽默", "情感心理", "体育娱乐", "美容美体", "文摘精选",
    "民生资讯", "财富理财", "科技数码", "创投商业", "汽车交通", "房产楼市",
    "职场发展", "教育考试", "学术研究", "企业品牌", "时事新闻",
]

SORT_MAP = {
    "growth_pct": "头条增长率",
}

UPDATE_NOTE = "周榜更新时间为每周一下午 16:30"  # 榜单更新周期提示，随每次查询输出


def get_api_key() -> str:
    key = os.environ.get("REDFOX_API_KEY", "").strip()
    if key:
        return key
    home = os.path.expanduser("~")
    for cfg in (".zshrc", ".bashrc", ".bash_profile", ".profile"):
        path = os.path.join(home, cfg)
        try:
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    m = re.search(r'export\s+REDFOX_API_KEY\s*=\s*["\']?([^"\'\n]+)["\']?', f.read())
                if m:
                    return m.group(1).strip()
        except (OSError, PermissionError):
            continue
    print("[error] 未找到 REDFOX_API_KEY，请先配置环境变量：export REDFOX_API_KEY=<你的apikey>", file=sys.stderr)
    sys.exit(1)


def parse_rank_date(raw: str) -> str:
    """把用户输入的日期归一化为统计周周一，格式 yyyy-MM-dd HH:mm:ss"""
    m = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", raw)
    if not m:
        raise ValueError(f"无法解析日期: {raw}，期望格式 yyyy-MM-dd")
    d = datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    monday = d - timedelta(days=d.weekday())
    return monday.strftime("%Y-%m-%d 00:00:00")


def latest_monday() -> str:
    now = datetime.now()
    return (now - timedelta(days=now.weekday())).strftime("%Y-%m-%d 00:00:00")


def shift_weeks(rank_date: str, weeks: int) -> str:
    d = datetime.strptime(rank_date, "%Y-%m-%d %H:%M:%S")
    return (d - timedelta(weeks=weeks)).strftime("%Y-%m-%d 00:00:00")


def week_span(rank_date: str) -> str:
    start = datetime.strptime(rank_date, "%Y-%m-%d %H:%M:%S")
    end = start + timedelta(days=6)
    return f"{start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')}"


def fetch_rank_list(api_key: str, rank_date: str, author_type: str, sort: str, page: int):
    body = {"page": page, "rank_date": rank_date, "sort": sort, "source": SOURCE}
    if author_type:
        body["author_type"] = author_type
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-API-KEY": api_key,
            "User-Agent": "QoderWork/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        print(f"[error] HTTP {e.code}: {detail}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"[error] 网络请求失败: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"[error] 数据解析异常: {e}", file=sys.stderr)
        sys.exit(1)

    if result.get("code") != 2000:
        print(f"[error] 接口返回错误: code={result.get('code')}, msg={result.get('msg', '未知')}", file=sys.stderr)
        sys.exit(1)
    return result


def build_output(rank_date: str, author_type: str, sort: str, page: int,
                 items: list, dates_tried: list):
    start = (page - 1) * PAGE_SIZE
    rows = []
    for i, it in enumerate(items):
        rows.append({
            "rank": start + i + 1,
            "account_id": it.get("account_id"),
            "nickname": it.get("nickname", ""),
            "author_type": it.get("author_type", ""),
            "cur_read": it.get("cur_read", 0) or 0,
            "prev_read": it.get("prev_read", 0) or 0,
            "growth_val": it.get("growth_val", 0) or 0,
            "growth_pct": it.get("growth_pct", 0) or 0,
        })
    return {
        "rank_date": rank_date,
        "week_span": week_span(rank_date),
        "update_note": UPDATE_NOTE,
        "author_type": author_type or "综合",
        "sort": sort,
        "sort_label": SORT_MAP.get(sort, sort),
        "page": page,
        "total_pages": MAX_PAGE,
        "has_next": page < MAX_PAGE,
        "count": len(rows),
        "dates_tried": dates_tried,
        "items": rows,
    }


def main():
    parser = argparse.ArgumentParser(description="公众号头条增长榜")
    parser.add_argument("--date", dest="rank_date", default=None,
                        help="榜单日期（统计周任意一天，自动归一到周一），如 2026-09-07，默认最新一期")
    parser.add_argument("--type", dest="author_type", default="",
                        help="作者类别（不传则默认为综合全部分类总榜），如 人文资讯")
    parser.add_argument("--page", type=int, default=1, help="页码 1-5（默认1）")
    parser.add_argument("--list-types", action="store_true", help="列出全部作者类别")
    args = parser.parse_args()

    if args.list_types:
        print(json.dumps(AUTHOR_TYPES, ensure_ascii=False, indent=2))
        return

    if not 1 <= args.page <= MAX_PAGE:
        print(f"[error] 页码超出范围：{args.page}（有效范围 1-{MAX_PAGE}）", file=sys.stderr)
        sys.exit(1)

    author_type = args.author_type.strip()
    if author_type and author_type not in AUTHOR_TYPES:
        close = difflib.get_close_matches(author_type, AUTHOR_TYPES, n=3, cutoff=0.4)
        hint = f"，你是否想查：{' / '.join(close)}" if close else ""
        print(f"[error] 无效的作者类别「{author_type}」{hint}。用 --list-types 查看全部 23 个类别", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key()
    sort = "growth_pct"  # 固定规则：一律按头条增长率降序

    dates_tried = []
    if args.rank_date:
        # 用户明确指定日期：只查这一期，为空就如实报空，不自动改查其他日期
        try:
            rank_date = parse_rank_date(args.rank_date)
        except ValueError as e:
            print(f"[error] {e}", file=sys.stderr)
            sys.exit(1)
        dates_tried.append(rank_date)
        result = fetch_rank_list(api_key, rank_date, author_type, sort, args.page)
        items = result.get("data") or []
    else:
        # 未指定日期：从最近一个周一往前找最近有数据的期数
        items = []
        rank_date = latest_monday()
        for attempt in range(DEFAULT_FETCH_ATTEMPTS):
            candidate = shift_weeks(rank_date, attempt)
            dates_tried.append(candidate)
            result = fetch_rank_list(api_key, candidate, author_type, sort, args.page)
            items = result.get("data") or []
            rank_date = candidate
            if items:
                break

    print(json.dumps(build_output(rank_date, author_type, sort, args.page, items,
                                  dates_tried),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
