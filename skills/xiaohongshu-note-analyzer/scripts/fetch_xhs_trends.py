#!/usr/bin/env python3
"""
小红书热门数据查询脚本
从环境变量 REDFOX_API_KEY 获取凭证，请求头新增 X-API-KEY
"""

import os
import sys
import argparse
import json
import requests


def fetch_xhs_trends(keyword: str, debug: bool = False, max_retries: int = 3, start_date: str = None):
    """
    调用接口获取小红书热门数据

    Args:
        keyword: 搜索关键词（多个关键词用逗号分隔，最多5个，总长度不超过200）
        debug: 是否打印调试信息
        max_retries: 最大重试次数
        start_date: 开始日期，格式 yyyy-MM-dd，最长为最近30天

    Returns:
        dict: 包含4类爆款数据

    Raises:
        Exception: 当API调用失败时抛出异常
    """
    # 获取凭证
    api_key = os.getenv("REDFOX_API_KEY")
    if not api_key:
        raise ValueError("缺少凭证配置，请配置环境变量 REDFOX_API_KEY")

    # 接口地址
    url = "https://redfox.hk/story/api/cozeSkill/getXhsCozeSkillData"

    # 构建请求参数
    params = {
        "keyword": keyword,
        "source": "小红书笔记创作-GitHub"
    }
    if start_date:
        params["startDate"] = start_date

    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            if debug:
                print(f"\n=== DEBUG: 第 {attempt + 1} 次尝试 ===", file=sys.stderr)

            response = requests.get(url, params=params, headers=headers, timeout=30)

            if debug:
                print(f"状态码: {response.status_code}", file=sys.stderr)
                print(f"响应长度: {len(response.text)} 字节", file=sys.stderr)

            if response.status_code >= 400:
                raise Exception(f"HTTP请求失败: 状态码 {response.status_code}, {response.text}")

            data = response.json()

            if "data" not in data:
                error_msg = data.get("msg", "未知错误")
                raise Exception(f"API 错误: {error_msg}")

            result_data = data.get("data", {})

            if debug:
                print("=== DEBUG: API 返回的 data 字段键 ===", file=sys.stderr)
                print(json.dumps(list(result_data.keys()), ensure_ascii=False, indent=2), file=sys.stderr)

            return {
                "keyword": keyword,
                "low_fan_explosive": result_data.get("lowPowderExplosiveArticle", []),
                "daily_like_top500": result_data.get("likeTheTop500", []),
                "daily_increment": result_data.get("singleDayIncrements", []),
                "weekly_increment": result_data.get("sevenDaysOfIncrements", [])
            }

        except requests.exceptions.RequestException as e:
            last_error = f"请求失败: {str(e)}"
            if debug:
                print(f"  错误: {str(e)[:100]}", file=sys.stderr)
            import time
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue
        except Exception as e:
            last_error = str(e)
            if debug:
                print(f"  错误: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
            import time
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue

    raise Exception(f"{last_error}（已尝试 {max_retries} 次）")


def format_output(data: dict, max_items: int = None):
    """
    格式化输出热门数据（表格形式）

    Args:
        data: 原始数据
        max_items: 每类爆款数据最多展示数量，None 表示展示所有数据
    """

    def process_title(item):
        """处理标题：转义特殊字符，空标题使用desc替代，并添加作品链接"""
        title = item.get('title', '')
        # 如果标题为空，尝试使用 desc 字段
        if not title or title.strip() == '':
            desc = item.get('desc', '')
            if desc:
                # 移除 desc 中的换行符并截取前30个字符
                title = desc.replace('\n', ' ').replace('\r', ' ').strip()[:30]
                if len(desc) > 30:
                    title = title + '...'

        if not title or title.strip() == '':
            title = '无标题'

        # 转义 Markdown 表格特殊字符（|）
        title = title.replace('|', '\\|')
        # 移除换行符
        title = title.replace('\n', ' ').replace('\r', ' ')
        # 移除多余空格
        title = ' '.join(title.split())

        # 截断过长标题
        if len(title) > 30:
            title = title[:30] + "..."

        # 添加作品链接
        photo_id = item.get('photoId', '')
        if photo_id:
            work_link = f"https://www.xiaohongshu.com/explore/{photo_id}"
            title = f"[{title}]({work_link})"

        return title

    output = []

    # 按 photoId 去重（API 返回数据可能有重复）
    def dedup_items(items):
        seen = set()
        result = []
        for item in items:
            photo_id = item.get('photoId', '')
            if photo_id and photo_id not in seen:
                seen.add(photo_id)
                result.append(item)
        return result

    # 检查是否有任何数据
    low_fan_items = dedup_items(data.get("low_fan_explosive", []))
    daily_like_items = dedup_items(data.get("daily_like_top500", []))
    daily_increment_items = dedup_items(data.get("daily_increment", []))
    weekly_increment_items = dedup_items(data.get("weekly_increment", []))

    total_count = len(low_fan_items) + len(daily_like_items) + len(daily_increment_items) + len(weekly_increment_items)

    # 如果所有类型都没有数据，输出友好提示
    if total_count == 0:
        keyword = data.get("keyword", "")
        output.append(f"# 小红书爆款数据分析报告\n\n**关键词**：{keyword}\n\n**爆款总数**：{total_count} 条\n\n")
        output.append("---\n\n")
        output.append("## 暂无相关爆款数据\n\n")
        output.append(f"很抱歉，当前关键词 **「{keyword}」** 尚未有足够的爆款笔记数据。\n\n")
        output.append("### 可能原因\n\n")
        output.append("- 该关键词相对小众或新兴，爆款内容积累较少\n")
        output.append("- 近期该赛道热度较低，暂无突出爆款笔记\n")
        output.append("- 关键词表述方式可以更加具体或热门\n\n")
        output.append("### 建议操作\n\n")
        output.append("- 更换为更热门的关键词，如：**\"早八穿搭\"**、**\"减脂餐\"**、**\"职场干货\"** 等\n")
        output.append("- 尝试更细分的长尾关键词，如：**\"小个子穿搭\"**、**\"学生党便当\"** 等\n")
        output.append("- 输入其他感兴趣的领域或赛道进行追踪\n\n")
        output.append("---\n\n")
        output.append("*数据来源：小红书爆款雷达，每日更新最新热门内容*\n")
        return "\n".join(output)

    # 1. 新手友好爆款
    items = low_fan_items
    if max_items is not None:
        items = items[:max_items]

    # 计算实际展示的总数
    display_low_fan = items
    display_daily_like = daily_like_items[:max_items] if max_items is not None else daily_like_items
    display_daily_increment = daily_increment_items[:max_items] if max_items is not None else daily_increment_items
    display_weekly_increment = weekly_increment_items[:max_items] if max_items is not None else weekly_increment_items
    display_total = len(display_low_fan) + len(display_daily_like) + len(display_daily_increment) + len(display_weekly_increment)

    # 输出标题和总数量
    keyword = data.get("keyword", "")
    output.append(f"# 小红书爆款数据分析报告\n\n**关键词**：{keyword}\n\n**爆款总数**：{display_total} 条\n\n---\n")

    output.append(f"\n## 爆款笔记（共 {len(items)} 条）")
    output.append(f"### - **新手友好爆款**（共 {len(items)} 条）")
    output.append(f"统计时间：近30天\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 标题 | 作者 | **互动总数** | 收藏 | 分享 | 评论 | 点赞 |")
        output.append("|------|------|------|------------|------|------|------|------|")

        for idx, item in enumerate(items, 1):
            user_id = item.get('userId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', 0)

            if user_id:
                author_link = f"https://www.xiaohongshu.com/user/profile/{user_id}"
                author_str = f"[{user_name}]({author_link})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)

            output.append(f"| {idx} | {title} | {author_str} | **{item.get('interactiveCount', 0)}** | {item.get('collectedCount', 0)} | {item.get('useShareCount', 0)} | {item.get('useCommentCount', 0)} | {item.get('useLikeCount', 0)} |")

    # 2. 当日点赞爆款
    items = daily_like_items[:max_items] if max_items is not None else daily_like_items

    output.append(f"\n### - **当日点赞爆款**（共 {len(items)} 条）")
    output.append(f"统计时间：近30天\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 标题 | 作者 | **点赞** | 收藏 | 分享 | 评论 |")
        output.append("|------|------|------|-------|------|------|------|")

        for idx, item in enumerate(items, 1):
            user_id = item.get('userId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', 0)

            if user_id:
                author_link = f"https://www.xiaohongshu.com/user/profile/{user_id}"
                author_str = f"[{user_name}]({author_link})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)

            output.append(f"| {idx} | {title} | {author_str} | **{item.get('useLikeCount', 0)}** | {item.get('collectedCount', 0)} | {item.get('useShareCount', 0)} | {item.get('useCommentCount', 0)} |")

    # 3. 当日增长爆款
    items = daily_increment_items[:max_items] if max_items is not None else daily_increment_items

    output.append(f"\n### - **当日增长爆款**（共 {len(items)} 条）")
    output.append(f"统计时间：近30天\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 标题 | 作者 | 收藏 | 分享 | 评论 | 点赞 | **新增互动总量** |")
        output.append("|------|------|------|------|------|------|------|---------------|")

        for idx, item in enumerate(items, 1):
            user_id = item.get('userId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', 0)

            if user_id:
                author_link = f"https://www.xiaohongshu.com/user/profile/{user_id}"
                author_str = f"[{user_name}]({author_link})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)

            ana_add = item.get('anaAdd', {})
            add_interactive = ana_add.get('addInteractiveount', 0)

            output.append(f"| {idx} | {title} | {author_str} | {ana_add.get('collectedCount', 0)} | {ana_add.get('addShareCount', 0)} | {ana_add.get('addCommentCount', 0)} | {ana_add.get('addLikeCount', 0)} | **{add_interactive}** |")

    # 4. 持续增长爆款
    items = weekly_increment_items[:max_items] if max_items is not None else weekly_increment_items

    output.append(f"\n### - **持续增长爆款**（共 {len(items)} 条）")
    output.append(f"统计时间：近30天\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 标题 | 作者 | 收藏 | 分享 | 评论 | 点赞 | **新增互动总量** |")
        output.append("|------|------|------|------|------|------|------|---------------|")

        for idx, item in enumerate(items, 1):
            user_id = item.get('userId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', 0)

            if user_id:
                author_link = f"https://www.xiaohongshu.com/user/profile/{user_id}"
                author_str = f"[{user_name}]({author_link})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)

            ana_add = item.get('anaAdd', {})
            add_interactive = ana_add.get('addInteractiveount', 0)

            output.append(f"| {idx} | {title} | {author_str} | {ana_add.get('collectedCount', 0)} | {ana_add.get('addShareCount', 0)} | {ana_add.get('addCommentCount', 0)} | {ana_add.get('addLikeCount', 0)} | **{add_interactive}** |")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="获取小红书热门数据")
    parser.add_argument("--keyword", required=True, help="搜索关键词")
    parser.add_argument("--start-date", help="开始日期，格式 yyyy-MM-dd")
    parser.add_argument("--max-items", type=int, default=50, help="每类内容最多展示数量")
    parser.add_argument("--output-format", choices=["text", "json", "markdown"], default="markdown", help="输出格式")
    parser.add_argument("--debug", action="store_true", help="调试模式")

    args = parser.parse_args()

    try:
        data = fetch_xhs_trends(
            keyword=args.keyword,
            debug=args.debug,
            start_date=args.start_date
        )

        if args.output_format == "json":
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            output = format_output(data, max_items=args.max_items)
            print(output)

    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
