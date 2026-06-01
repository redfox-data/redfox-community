#!/usr/bin/env python3
"""
抖音每日最热作品榜查询工具

日度收录全平台抖音作品，输出单日点赞TOP50榜单，
支持按赛道分类查询、历史日期回溯。

用法:
    python douyin_daily_hot.py                          # 默认：昨日全品类 TOP20
    python douyin_daily_hot.py --type 美食               # 指定赛道
    python douyin_daily_hot.py --start 2026-05-28        # 指定日期
    python douyin_daily_hot.py --type 美食 --start 2026-05-20 --end 2026-05-28  # 日期范围
    python douyin_daily_hot.py --full                    # 输出全部 50 条

环境变量:
    REDFOX_API_KEY   API 密钥（必填）
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# ────────────────────────────────────────────────────
# 常量
# ────────────────────────────────────────────────────

API_BASE = "https://redfox.hk/story/api/dy/search/likesRank"
DEFAULT_LIMIT = 20
FULL_LIMIT = 50

CATEGORIES = [
    "全部", "个人才艺", "生活vlog", "财富理财", "二次元", "居家装修",
    "学习教育", "小剧场", "数码科技", "旅行", "美食", "化妆美容",
    "动物", "亲子", "汽车", "情感", "三农", "健康医学", "潮流风尚",
    "舞蹈才艺", "颜值造型", "人文", "音乐", "影视", "身体锻炼",
    "体育", "明星娱乐", "游戏",
]

# ────────────────────────────────────────────────────
# 工具函数
# ────────────────────────────────────────────────────

def format_number(n):
    """将数字格式化为可读字符串，如 10w+、1.2w、5000"""
    if n is None:
        return "-"
    n = int(n)
    if n >= 100000:
        return f"{n // 10000}w+"
    elif n >= 10000:
        return f"{n / 10000:.1f}w"
    else:
        return str(n)


def format_fans(fans_str):
    """格式化粉丝数，若已是字符串则直接返回"""
    if fans_str is None:
        return "-"
    if isinstance(fans_str, str):
        return fans_str
    return format_number(fans_str)


def format_time(ts):
    """将时间字符串 YYYY-MM-DD HH:MM 转为 MM-DD HH:00 格式"""
    if not ts:
        return "-"
    try:
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%m-%d %H:00")
    except ValueError:
        return ts


def yesterday():
    """返回昨日日期字符串 YYYY-MM-DD"""
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


# ────────────────────────────────────────────────────
# API 调用
# ────────────────────────────────────────────────────

def call_api(category="全部", start_time=None, end_time=None):
    """调用抖音点赞排行榜接口，返回解析后的数据列表"""

    api_key = os.environ.get("REDFOX_API_KEY", "")
    if not api_key:
        print("❌ 错误：未配置环境变量 REDFOX_API_KEY，请先设置 API 密钥。")
        sys.exit(1)

    if start_time is None:
        start_time = yesterday()
    if end_time is None:
        end_time = yesterday()

    body = {
        "source": "抖音每日热门作品榜-GitHub",
    }
    if category and category != "全部":
        body["type"] = category
    if start_time:
        body["startTime"] = start_time
    if end_time:
        body["endTime"] = end_time

    json_body = json.dumps(body).encode("utf-8")

    req = Request(API_BASE, data=json_body, method="POST")
    req.add_header("X-API-KEY", api_key)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")

    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_handlers = {
            401: "API Key 无效或未配置，请检查 REDFOX_API_KEY 环境变量。",
            404: "该日期暂无数据。",
            429: "请求频率超限，请稍后重试。",
        }
        msg = error_handlers.get(e.code, f"服务端错误 (HTTP {e.code})，请稍后重试。")
        print(f"❌ 错误：{msg}")
        sys.exit(1)
    except URLError as e:
        print(f"❌ 网络错误：无法连接到 API 服务。{e.reason}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ 错误：无法解析 API 响应。")
        sys.exit(1)

    # 解析响应
    code = data.get("code", -1)
    if code != 2000:
        print(f"❌ API 返回错误码：{code}，消息：{data.get('msg', '未知错误')}")
        sys.exit(1)

    items = data.get("data", [])

    if not items:
        print("📭 未查询到数据，该条件下暂无榜单记录。")
        sys.exit(0)

    return items


# ────────────────────────────────────────────────────
# Markdown 输出
# ────────────────────────────────────────────────────

def print_table(items, category, start_time, end_time, limit=20):
    """按 SKILL.md 标准输出 Markdown 格式榜单，作品标题为 [标题](workUrl) 超链接"""

    display_limit = min(limit, len(items))
    date_label = start_time if start_time == end_time else f"{start_time} ~ {end_time}"
    is_all = (category == "全部" or category is None)

    print()
    print("💡 榜单说明：每日 06:00 更新昨日数据。互动数据为入库时间，与实时数据存在差异。")
    print()

    if is_all:
        print(f"📊 抖音每日点赞TOP{display_limit}（{date_label}）")
    else:
        print(f"📊 抖音{category}赛道点赞TOP{display_limit}（{date_label}）")
    print()

    # Markdown 表头
    if is_all:
        print("| 排名 | 作品标题 | 作者（粉丝数） | 赛道 | 收藏 | 评论 | 分享 | **点赞** | 发布时间 |")
        print("|------|---------|--------------|------|------|------|------|------|---------|")
    else:
        print("| 排名 | 作品标题 | 作者（粉丝数） | 收藏 | 评论 | 分享 | **点赞** | 发布时间 |")
        print("|------|---------|--------------|------|------|------|------|---------|")

    # 数据行
    for idx, item in enumerate(items[:limit], start=1):
        raw_title = (item.get("title") or "-").replace("|", "｜")
        work_url = item.get("workUrl", "")
        if work_url:
            title = f"[{raw_title}]({work_url})"
        else:
            title = raw_title
        author = item.get("accountName", "-")
        fans = format_fans(item.get("followerCount"))
        author_display = f"{author}（{fans}）"
        cat = item.get("category") or "-"
        collect = format_number(item.get("collectCount"))
        comment = format_number(item.get("commentCount"))
        share = format_number(item.get("shareCount"))
        like = f"**{format_number(item.get('likeCount'))}**"
        pub_time = format_time(item.get("publishTime"))

        if is_all:
            print(f"| {idx} | {title} | {author_display} | {cat} | {collect} | {comment} | {share} | {like} | {pub_time} |")
        else:
            print(f"| {idx} | {title} | {author_display} | {collect} | {comment} | {share} | {like} | {pub_time} |")

    print()

    if len(items) > limit:
        remaining = len(items) - limit
        print("⚡ 更多操作")
        print(f"• 本次榜单完整共 {len(items)} 条数据，是否需要查看剩余 {remaining} 条？")
        print("• 使用 --full 参数查看完整榜单")
    print()


# ────────────────────────────────────────────────────
# 主函数
# ────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="抖音每日最热作品榜查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
示例:
  %(prog)s                                          # 昨日全品类 TOP20
  %(prog)s --type 美食                               # 美食赛道 TOP20
  %(prog)s --start 2026-05-28                        # 指定日期 TOP20
  %(prog)s --type 美食 --start 2026-05-28            # 指定日期 + 赛道
  %(prog)s --type 美食 --start 2026-05-20 --end 2026-05-28  # 日期范围
  %(prog)s --full                                    # 输出完整 50 条

支持赛道:
  {', '.join(CATEGORIES)}
        """,
    )

    parser.add_argument(
        "--type", "-t",
        default="全部",
        choices=CATEGORIES,
        help="赛道分类（默认：全部）",
    )
    parser.add_argument(
        "--start", "-s",
        default=None,
        help="起始日期，格式 YYYY-MM-DD（默认：昨日）",
    )
    parser.add_argument(
        "--end", "-e",
        default=None,
        help="结束日期，格式 YYYY-MM-DD（默认：同 start）",
    )
    parser.add_argument(
        "--full", "-f",
        action="store_true",
        help="输出全部 50 条数据",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=None,
        help="自定义输出条数（默认 20，最大 50）",
    )

    args = parser.parse_args()

    start_time = args.start or yesterday()
    end_time = args.end or start_time

    # 获取数据
    items = call_api(
        category=args.type,
        start_time=start_time,
        end_time=end_time,
    )

    # 确定输出条数
    if args.full:
        limit = FULL_LIMIT
    elif args.limit is not None:
        limit = min(args.limit, FULL_LIMIT)
    else:
        limit = DEFAULT_LIMIT

    # 输出
    print_table(items, args.type, start_time, end_time, limit=limit)


if __name__ == "__main__":
    main()
