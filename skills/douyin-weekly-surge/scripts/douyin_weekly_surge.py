#!/usr/bin/env python3
"""
抖音七日点赞飙升榜查询工具

周度收录全平台抖音作品，输出七日新增点赞TOP50榜单，
支持按赛道分类查询、历史日期回溯。

用法:
    python douyin_weekly_surge.py                          # 默认：截至昨日七日全品类 TOP20
    python douyin_weekly_surge.py --type 美食               # 指定赛道
    python douyin_weekly_surge.py --start 2026-05-28        # 指定日期
    python douyin_weekly_surge.py --type 美食 --start 2026-05-28  # 指定日期 + 赛道
    python douyin_weekly_surge.py --full                    # 输出全部 50 条

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

API_BASE = "https://redfox.hk/story/api/dy/search/hotContentRank"
DEFAULT_LIMIT = 20
FULL_LIMIT = 50

CATEGORIES = [
    "全部", "小剧场", "财富理财", "二次元", "身体锻炼", "居家装修",
    "数码科技", "科学普及", "旅行", "美食", "动物", "明星娱乐",
    "汽车", "亲子", "人文", "三农", "潮流风尚", "游戏",
    "生活记录", "体育", "舞蹈才艺", "学习教育", "休闲玩乐", "影视",
    "音乐", "颜值造型", "健康医学", "综艺", "个人成长",
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


def format_time(ts):
    """将时间字符串转为 MM-DD HH:00 格式"""
    if not ts:
        return "-"
    try:
        if isinstance(ts, (int, float)):
            dt = datetime.fromtimestamp(ts / 1000)
        else:
            dt = datetime.strptime(str(ts)[:19], "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%m-%d %H:00")
    except (ValueError, OSError):
        return str(ts)[:16]


def yesterday():
    """返回昨日日期字符串 YYYY-MM-DD"""
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")


# ────────────────────────────────────────────────────
# API 调用
# ────────────────────────────────────────────────────

def call_api(category="全部", start_time=None):
    """调用抖音七日点赞飙升榜接口，返回解析后的数据列表"""

    api_key = os.environ.get("REDFOX_API_KEY", "")
    if not api_key:
        print("❌ 错误：未配置环境变量 REDFOX_API_KEY，请先设置 API 密钥。")
        sys.exit(1)

    if start_time is None:
        start_time = yesterday()

    body = {
        "source": "抖音七日点赞飙升榜-GitHub",
    }
    if category and category != "全部":
        body["type"] = category
    if start_time:
        body["startTime"] = start_time

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

    # 解析响应：数据位于 data.weeklyRank
    code = data.get("code", -1)
    if code != 2000:
        print(f"❌ API 返回错误码：{code}，消息：{data.get('msg', '未知错误')}")
        sys.exit(1)

    items = data.get("data", {}).get("weeklyRank", [])

    if not items:
        print("📭 未查询到数据，该条件下暂无榜单记录。")
        sys.exit(0)

    return items


# ────────────────────────────────────────────────────
# Markdown 输出
# ────────────────────────────────────────────────────

def print_table(items, category, start_time, limit=20):
    """按 SKILL.md 标准输出 Markdown 格式七日飙升榜单，作品标题为 [标题](workUrl) 超链接"""

    display_limit = min(limit, len(items))
    date_label = start_time
    is_all = (category == "全部" or category is None)

    print()
    print("💡 榜单说明：每日 17:00 更新过去七日数据。飙升数据为七日新增统计，与累计总量存在差异。")
    print()

    if is_all:
        print(f"📊 抖音七日点赞飙升TOP{display_limit}（截至 {date_label}）")
    else:
        print(f"📊 抖音{category}赛道七日点赞飙升TOP{display_limit}（截至 {date_label}）")
    print()

    # Markdown 表头
    if is_all:
        print("| 排名 | 作品标题 | 作者 | 赛道 | 七日新增收藏 | 七日新增评论 | 七日新增分享 | **七日新增点赞** | 发布时间 |")
        print("|------|---------|------|------|---------|---------|---------|------------|---------|")
    else:
        print("| 排名 | 作品标题 | 作者 | 七日新增收藏 | 七日新增评论 | 七日新增分享 | **七日新增点赞** | 发布时间 |")
        print("|------|---------|------|---------|---------|---------|------------|---------|")

    # 数据行
    for idx, item in enumerate(items[:limit], start=1):
        raw_title = (item.get("aweme_desc") or "-").replace("|", "｜").replace("[", "【").replace("]", "】").replace("\n", " ").replace("\r", " ")
        work_url = item.get("share_url", "")
        if work_url:
            title = f"[{raw_title}]({work_url})"
        else:
            title = raw_title
        author = item.get("user_nickname", "-")
        cat = item.get("category") or "-"
        collect = format_number(item.get("add_collect_count"))
        comment = format_number(item.get("add_comment_count"))
        share = format_number(item.get("add_share_count"))
        like = f"**{format_number(item.get('add_digg_count'))}**"
        pub_time = format_time(item.get("create_time_str"))

        if is_all:
            print(f"| {idx} | {title} | {author} | {cat} | {collect} | {comment} | {share} | {like} | {pub_time} |")
        else:
            print(f"| {idx} | {title} | {author} | {collect} | {comment} | {share} | {like} | {pub_time} |")

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
        description="抖音七日点赞飙升榜查询工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
示例:
  %(prog)s                                          # 截至昨日七日全品类 TOP20
  %(prog)s --type 美食                               # 美食赛道 TOP20
  %(prog)s --start 2026-05-28                        # 指定日期 TOP20
  %(prog)s --type 美食 --start 2026-05-28            # 指定日期 + 赛道
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
        help="查询日期，格式 YYYY-MM-DD（默认：昨日）",
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

    # 获取数据
    items = call_api(
        category=args.type,
        start_time=start_time,
    )

    # 确定输出条数
    if args.full:
        limit = FULL_LIMIT
    elif args.limit is not None:
        limit = min(args.limit, FULL_LIMIT)
    else:
        limit = DEFAULT_LIMIT

    # 输出
    print_table(items, args.type, start_time, limit=limit)


if __name__ == "__main__":
    main()
