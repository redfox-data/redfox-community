#!/usr/bin/env python3
"""
小红书热门数据查询脚本（标准 HTTPS 安全版）
"""

import sys
import argparse
import json
from urllib.parse import urlparse

import requests


ALLOWED_API_HOSTS = {
    "onetotenvip.com",
}


def fetch_secure_https(base_url: str, params: dict, headers: dict, timeout: int = 60):
    """使用 requests 发起标准 HTTPS 请求（启用证书与主机名校验）"""
    parsed = urlparse(base_url)
    if parsed.scheme != "https":
        raise ValueError("仅允许 HTTPS 接口")

    host = parsed.hostname or ""
    if host not in ALLOWED_API_HOSTS:
        raise ValueError(f"不允许的接口域名: {host}")

    response = requests.get(base_url, params=params, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.status_code, response.text


def fetch_xhs_trends(keyword: str, debug: bool = False, max_retries: int = 3, start_date: str = None):
    """
    调用新接口获取小红书热门数据

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
    base_url = "https://onetotenvip.com/skill/cozeSkill/getXhsCozeSkillData"
    params = {
        "keyword": keyword,
        "source": "小红书爆款标题创作-GitHub"
    }

    # 添加开始日期参数
    if start_date:
        params["startDate"] = start_date
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "close",
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            if debug:
                print(f"\n=== DEBUG: 第 {attempt + 1} 次尝试 ===", file=sys.stderr)

            status_code, body = fetch_secure_https(base_url, params, headers)

            if debug:
                print(f"状态码: {status_code}", file=sys.stderr)
                print(f"响应长度: {len(body)} 字节", file=sys.stderr)

            if status_code >= 400:
                raise Exception(f"HTTP请求失败: 状态码 {status_code}")

            data = json.loads(body)

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

        except Exception as e:
            last_error = str(e)
            if debug:
                print(f"  错误: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
            import time
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            continue

    raise Exception(f"{last_error}（已尝试 {max_retries} 次）")


def get_cover_urls(data, max_per_category=5):
    """提取所有封面图URL"""
    urls = []
    categories = [
        ('low_fan_explosive', '低粉高赞'),
        ('daily_like_top500', '点赞最多'),
        ('daily_increment', '单日互动爆发'),
        ('weekly_increment', '7日持续增长')
    ]
    for key, name in categories:
        items = data.get(key, [])[:max_per_category]
        for item in items:
            cover_url = item.get('coverUrl', '')
            photo_id = item.get('photoId', '')
            title = item.get('title', '')[:20]
            if cover_url and photo_id:
                urls.append({
                    'category': name,
                    'title': title,
                    'photo_id': photo_id,
                    'cover_url': cover_url,
                    'link': f"https://www.xiaohongshu.com/explore/{photo_id}"
                })
    return urls


def format_output(data: dict, max_items: int = None, start_date: str = None):
    """
    格式化输出热门数据（表格形式）

    Args:
        data: 原始数据
        max_items: 每类爆款数据最多展示数量，None 表示展示所有数据
        start_date: 开始日期，格式 yyyy-MM-dd，用于计算统计时间范围
    """
    from datetime import datetime, timedelta

    # 计算统计时间范围
    def get_time_range(start_date):
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                end = datetime.now()
                days = (end - start).days
                if days <= 1:
                    return "近1天"
                elif days <= 7:
                    return f"近{days}天"
                else:
                    return f"近{days}天"
            except:
                return "近30天"
        return "近30天"

    time_range = get_time_range(start_date)

    def process_title(item):
        """处理标题：转义特殊字符，空标题使用desc替代"""
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

        return title

    def format_time(item):
        """格式化发布时间为 X月X日"""
        pub_time = item.get('publicTime', '')
        if pub_time:
            # publicTime 格式: "2026-03-06 13:03:56"
            try:
                month = int(pub_time[5:7])
                day = int(pub_time[8:10])
                return f"{month}月{day}日"
            except:
                pass
        return '--'

    def format_note_link(item):
        """生成作品链接"""
        photo_id = item.get('photoId', '')
        if photo_id:
            return f"[查看详情](https://www.xiaohongshu.com/explore/{photo_id})"
        return '--'

    def get_latest_date(data):
        """获取数据中最新的发布日期"""
        all_items = []
        for key in ['low_fan_explosive', 'daily_like_top500', 'daily_increment', 'weekly_increment']:
            all_items.extend(data.get(key, []))

        latest_date = None
        for item in all_items:
            pub_time = item.get('publicTime', '')
            if pub_time:
                try:
                    date_str = pub_time[:10]  # 取 "YYYY-MM-DD" 部分
                    if latest_date is None or date_str > latest_date:
                        latest_date = date_str
                except:
                    pass
        return latest_date

    output = []

    # 检查数据日期
    latest_date = get_latest_date(data)

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

    # 按时间倒序排序
    def sort_by_time_desc(items):
        """按发布时间倒序排列"""
        def get_time_key(item):
            pub_time = item.get('publicTime', '')
            if pub_time:
                return pub_time
            return '0'
        return sorted(items, key=get_time_key, reverse=True)

    # 检查是否有任何数据
    low_fan_items = dedup_items(data.get("low_fan_explosive", []))
    daily_like_items = dedup_items(data.get("daily_like_top500", []))
    daily_increment_items = dedup_items(data.get("daily_increment", []))
    weekly_increment_items = dedup_items(data.get("weekly_increment", []))

    total_count = len(low_fan_items) + len(daily_like_items) + len(daily_increment_items) + len(weekly_increment_items)

    # 如果所有类型都没有数据，输出友好提示
    if total_count == 0:
        keyword = data.get("keyword", "")
        output.append(f"# 小红书爆款数据分析报告\n\n**关键词**：{keyword}\n\n")
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

    # 1. 低粉高赞
    items = sort_by_time_desc(low_fan_items)
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **低粉高赞**（粉丝<5000的博主中点赞最多的内容）")
    output.append("\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 发布时间 | 标题 | 作者 | 收藏 | 分享 | 评论 | 点赞 | **互动总数** |")
        output.append("|------|----------|------|------|------|------|------|------|-------------|")

        for idx, item in enumerate(items, 1):
            user_id = item.get('userId', '')
            user_id = item.get('userId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', 0)

            # 作者信息添加主页链接
            if user_id:
                author_str = f"[{user_name}](https://www.xiaohongshu.com/user/profile/{user_id})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)
            pub_time = format_time(item)

            # 标题添加作品链接
            photo_id = item.get('photoId', '')
            if photo_id:
                note_link = f"https://www.xiaohongshu.com/explore/{photo_id}"
                title_with_link = f"[{title}]({note_link})"
            else:
                title_with_link = title

            output.append(f"| {idx} | {pub_time} | {title_with_link} | {author_str} | {item.get('collectedCount', 0)} | {item.get('useShareCount', 0)} | {item.get('useCommentCount', 0)} | {item.get('useLikeCount', 0)} | **{item.get('interactiveCount', 0)}** |")

    # 2. 点赞最多
    items = sort_by_time_desc(data.get("daily_like_top500", []))
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **点赞最多**（统计时间内点赞数最多的内容）")
    output.append("\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 发布时间 | 标题 | 作者 | **点赞** | 收藏 | 分享 | 评论 | 互动总数 |")
        output.append("|------|----------|------|------|--------|------|------|------|------------|")

        for idx, item in enumerate(items, 1):
            user_id = item.get('userId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', 0)

            # 作者信息添加主页链接
            if user_id:
                author_str = f"[{user_name}](https://www.xiaohongshu.com/user/profile/{user_id})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)
            pub_time = format_time(item)

            # 封面图
            cover_url = item.get('coverUrl', '')
            if cover_url:
                cover_str = f"[查看封面]({cover_url})"
            else:
                cover_str = "--"

            # 标题添加作品链接
            photo_id = item.get('photoId', '')
            if photo_id:
                note_link = f"https://www.xiaohongshu.com/explore/{photo_id}"
                title_with_link = f"[{title}]({note_link})"
            else:
                title_with_link = title

            output.append(f"| {idx} | {pub_time} | {title_with_link} | {author_str} | **{item.get('useLikeCount', 0)}** | {item.get('collectedCount', 0)} | {item.get('useShareCount', 0)} | {item.get('useCommentCount', 0)} | {item.get('interactiveCount', 0)} |")

    # 3. 单日互动爆发
    items = sort_by_time_desc(data.get("daily_increment", []))
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **单日互动爆发**（当天互动量增长最多的内容）")
    output.append("\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 发布时间 | 标题 | 作者 | 收藏 | 分享 | 评论 | 点赞 | 互动总数 |")
        output.append("|------|----------|------|------|------|------|------|------|------------|")

        for idx, item in enumerate(items, 1):
            user_id = item.get('userId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', 0)

            # 作者信息添加主页链接
            if user_id:
                author_str = f"[{user_name}](https://www.xiaohongshu.com/user/profile/{user_id})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)
            pub_time = format_time(item)

            # 标题添加作品链接
            photo_id = item.get('photoId', '')
            if photo_id:
                note_link = f"https://www.xiaohongshu.com/explore/{photo_id}"
                title_with_link = f"[{title}]({note_link})"
            else:
                title_with_link = title

            # 从 anaAdd 对象获取新增互动数据
            ana_add = item.get('anaAdd', {})
            if ana_add:
                total = ana_add.get('addInteractiveount', 0)
                collected = ana_add.get('addCollectedCunt', 0)
                share = ana_add.get('addShareCount', 0)
                comment = ana_add.get('addCommentCount', 0)
                like = ana_add.get('addLikeCount', 0)
            else:
                total = 0
                collected = 0
                share = 0
                comment = 0
                like = 0

            output.append(f"| {idx} | {pub_time} | {title_with_link} | {author_str} | {collected} | {share} | {comment} | {like} | **{total}** |")

    # 4. 7日持续增长
    items = sort_by_time_desc(data.get("weekly_increment", []))
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **7日持续增长**（近7天互动量持续增长最多的内容）")
    output.append("\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 序号 | 发布时间 | 标题 | 作者 | 收藏 | 分享 | 评论 | 点赞 | 互动总数 |")
        output.append("|------|----------|------|------|------|------|------|------|------------|")

        for idx, item in enumerate(items, 1):
            user_id = item.get('userId', '')
            user_name = item.get('userName', '未知')
            fans = item.get('fans', 0)

            # 作者信息添加主页链接
            if user_id:
                author_str = f"[{user_name}](https://www.xiaohongshu.com/user/profile/{user_id})（粉丝：{fans}）"
            else:
                author_str = f"{user_name}（粉丝：{fans}）"

            title = process_title(item)
            pub_time = format_time(item)

            # 标题添加作品链接
            photo_id = item.get('photoId', '')
            if photo_id:
                note_link = f"https://www.xiaohongshu.com/explore/{photo_id}"
                title_with_link = f"[{title}]({note_link})"
            else:
                title_with_link = title

            # 从 anaAdd 对象获取新增互动数据
            ana_add = item.get('anaAdd', {})
            if ana_add:
                total = ana_add.get('addInteractiveount', 0)
                collected = ana_add.get('addCollectedCunt', 0)
                share = ana_add.get('addShareCount', 0)
                comment = ana_add.get('addCommentCount', 0)
                like = ana_add.get('addLikeCount', 0)
            else:
                total = 0
                collected = 0
                share = 0
                comment = 0
                like = 0

            output.append(f"| {idx} | {pub_time} | {title_with_link} | {author_str} | {collected} | {share} | {comment} | {like} | **{total}** |")

    return "\n".join(output)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='小红书热门数据查询工具')
    parser.add_argument('--keyword', required=True, help='搜索关键词')
    parser.add_argument('--max-items', type=int, default=10,
                       help='每类爆款内容最多展示数量（默认10条）')
    parser.add_argument('--output-format', choices=['text', 'json', 'markdown'],
                       default='markdown', help='输出格式：text（文本表格）、json（JSON格式）或 markdown（Markdown格式，默认）')
    parser.add_argument('--output-file', type=str, default=None,
                       help='输出文件路径（默认：关键词_爆款数据.md）')
    parser.add_argument('--start-date', type=str, default=None,
                       help='开始日期，格式 yyyy-MM-dd（默认最近30天）')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--max-retries', type=int, default=3,
                       help='最大重试次数（默认3次）')

    args = parser.parse_args()

    try:
        data = fetch_xhs_trends(args.keyword, debug=args.debug, max_retries=args.max_retries, start_date=args.start_date)

        # 生成输出内容
        if args.output_format == 'json':
            output_content = json.dumps(data, ensure_ascii=False, indent=2)
        elif args.output_format == 'markdown':
            # Markdown 格式添加标题
            markdown_header = f"# 小红书爆款数据分析报告\n\n**关键词**：{args.keyword}\n\n"
            output_content = markdown_header + format_output(data, max_items=args.max_items, start_date=args.start_date)
        else:
            output_content = format_output(data, max_items=args.max_items, start_date=args.start_date)

        # 确定输出文件路径（markdown 格式默认输出到文件）
        output_file = args.output_file
        if output_file is None and args.output_format == 'markdown':
            # 默认文件名：关键词_爆款数据.md
            output_file = f"{args.keyword}_爆款数据.md"

        # 输出到文件或控制台
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"✓ 结果已保存到: {output_file}", file=sys.stderr)
            print(f"✓ 关键词: {args.keyword}", file=sys.stderr)
            # 统计数据
            total_items = (
                len(data.get('low_fan_explosive', [])) +
                len(data.get('daily_like_top500', [])) +
                len(data.get('daily_increment', [])) +
                len(data.get('weekly_increment', []))
            )
            print(f"✓ 总计: {total_items} 条数据", file=sys.stderr)
            # 显示每类数据量
            print(f"  - 低粉高赞: {len(data.get('low_fan_explosive', []))} 条", file=sys.stderr)
            print(f"  - 点赞最多: {len(data.get('daily_like_top500', []))} 条", file=sys.stderr)
            print(f"  - 单日互动爆发: {len(data.get('daily_increment', []))} 条", file=sys.stderr)
            print(f"  - 7日持续增长: {len(data.get('weekly_increment', []))} 条", file=sys.stderr)
            # 输出封面图URL供后续分析
            cover_urls = get_cover_urls(data, max_per_category=3)
            if cover_urls:
                print(f"\n=== 封面图URL（用于风格分析）===", file=sys.stderr)
                for i, item in enumerate(cover_urls, 1):
                    print(f"{i}. [{item['category']}] {item['title']}: {item['cover_url']}", file=sys.stderr)
        else:
            print(output_content)

    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
