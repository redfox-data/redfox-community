#!/usr/bin/env python3
"""
公众号爆款封面数据查询脚本
"""

import os
import sys
import argparse
import json

import requests


def fetch_wx_covers(keyword: str, debug: bool = False, max_retries: int = 3, start_date: str = None):
    """
    调用接口获取公众号爆款封面数据

    Args:
        keyword: 搜索关键词（多个关键词用逗号分隔）
        debug: 是否打印调试信息
        max_retries: 最大重试次数
        start_date: 开始日期，格式 yyyy-MM-dd

    Returns:
        dict: 包含3类爆款数据

    Raises:
        Exception: 当API调用失败时抛出异常
    """
    # 从环境变量获取 API Key
    api_key = os.getenv("REDFOX_API_KEY")
    if not api_key:
        raise ValueError("缺少 API Key 配置，请设置环境变量 REDFOX_API_KEY。获取方式：前往 https://redfox.hk/settings/api-keys?source=github 申请，然后执行 export REDFOX_API_KEY=\"ak_xxxx...\"")

    url = "https://redfox.hk/story/api/cozeSkill/getWxCozeSkillData"
    params = {
        "keyword": keyword,
        "source": "公众号爆款封面生成-GitHub"
    }

    # 添加开始日期参数
    if start_date:
        params["startDate"] = start_date

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            if debug:
                print(f"\n=== DEBUG: 第 {attempt + 1} 次尝试 ===", file=sys.stderr)
                print(f"URL: {url}", file=sys.stderr)
                print(f"参数: {params}", file=sys.stderr)

            response = requests.get(url, params=params, headers=headers, timeout=30)

            if debug:
                print(f"状态码: {response.status_code}", file=sys.stderr)
                print(f"响应长度: {len(response.text)} 字节", file=sys.stderr)

            if response.status_code >= 400:
                raise Exception(f"HTTP请求失败: 状态码 {response.status_code}, {response.text[:200]}")

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
                "ten_w_reading": result_data.get("tenWReadingRank", []),
                "original_rank": result_data.get("originalRank", [])
            }

        except requests.exceptions.RequestException as e:
            last_error = f"请求失败: {str(e)}"
            if debug:
                print(f"  错误: {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
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


def get_cover_urls(data, max_per_category=5):
    """提取所有封面图URL"""
    urls = []
    categories = [
        ('low_fan_explosive', '低粉爆文榜'),
        ('ten_w_reading', '10w+阅读榜'),
        ('original_rank', '原创榜')
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
                    'link': f"https://mp.weixin.qq.com/s/{photo_id}"
                })
    return urls


def format_output(data: dict, max_items: int = None, start_date: str = None):
    """
    格式化输出爆款数据（表格形式）

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
        """处理标题：转义特殊字符，空标题使用summary替代"""
        title = item.get('title', '')
        # 如果标题为空，尝试使用 summary 字段
        if not title or title.strip() == '':
            summary = item.get('summary', '')
            if summary:
                # 移除 summary 中的换行符并截取前30个字符
                title = summary.replace('\n', ' ').replace('\r', ' ').strip()[:30]
                if len(summary) > 30:
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

    def get_latest_date(data):
        """获取数据中最新的发布日期"""
        all_items = []
        for key in ['low_fan_explosive', 'ten_w_reading', 'original_rank']:
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

    # 检查是否有任何数据
    low_fan_items = dedup_items(data.get("low_fan_explosive", []))
    ten_w_items = dedup_items(data.get("ten_w_reading", []))
    original_items = dedup_items(data.get("original_rank", []))

    total_count = len(low_fan_items) + len(ten_w_items) + len(original_items)

    # 如果所有类型都没有数据，输出友好提示
    if total_count == 0:
        keyword = data.get("keyword", "")
        output.append(f"# 公众号爆款数据分析报告\n\n**关键词**：{keyword}\n\n")
        output.append("---\n\n")
        output.append("## 暂无相关爆款数据\n\n")
        output.append(f"很抱歉，当前关键词 **「{keyword}」** 尚未有足够的爆款文章数据。\n\n")
        output.append("### 可能原因\n\n")
        output.append("- 该关键词相对小众或新兴，爆款内容积累较少\n")
        output.append("- 近期该赛道热度较低，暂无突出爆款文章\n")
        output.append("- 关键词表述方式可以更加具体或热门\n\n")
        output.append("### 建议操作\n\n")
        output.append("- 更换为更热门的关键词，如：**\"职场成长\"**、**\"美食\"**、**\"情感故事\"** 等\n")
        output.append("- 尝试更细分的长尾关键词\n")
        output.append("- 输入其他感兴趣的领域或赛道进行追踪\n\n")
        output.append("---\n\n")
        output.append("*数据来源：公众号爆款雷达，每日更新最新热门内容*\n")
        return "\n".join(output)

    # 1. 低粉爆文榜
    items = low_fan_items
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **低粉爆文榜**（粉丝量较少的账号中爆款文章）")
    output.append("\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 封面 | 序号 | 发布时间 | 标题 | 作者 | 阅读数 | 点赞数 | 在看数 |")
        output.append("|------|------|----------|------|------|--------|--------|--------|")

        for idx, item in enumerate(items, 1):
            user_name = item.get('userName', '未知')
            fans = item.get('fans', '未知')

            # 封面缩略图
            cover_url = item.get('coverUrl', '')
            if cover_url:
                cover_str = f"![]({cover_url})"
            else:
                cover_str = "--"

            # 作者信息
            author_str = f"{user_name}（粉丝：{fans}）"

            # 标题添加链接
            title = process_title(item)
            ori_url = item.get('oriUrl', '')
            if ori_url:
                title_with_link = f"[{title}]({ori_url})"
            else:
                title_with_link = title

            pub_time = format_time(item)

            # 获取互动数据（字符串类型）
            clicks = item.get('clicksCount', '--')
            likes = item.get('likeCount', '--')
            watches = item.get('watchCount', '--')

            output.append(f"| {cover_str} | {idx} | {pub_time} | {title_with_link} | {author_str} | {clicks} | {likes} | {watches} |")

    # 2. 10w+阅读榜
    items = ten_w_items
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **10w+阅读榜**（阅读量超过10万的爆款文章）")
    output.append("\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 封面 | 序号 | 发布时间 | 标题 | 作者 | 阅读数 | 点赞数 | 在看数 |")
        output.append("|------|------|----------|------|------|--------|--------|--------|")

        for idx, item in enumerate(items, 1):
            user_name = item.get('userName', '未知')
            fans = item.get('fans', '未知')

            # 封面缩略图
            cover_url = item.get('coverUrl', '')
            if cover_url:
                cover_str = f"![]({cover_url})"
            else:
                cover_str = "--"

            # 作者信息
            author_str = f"{user_name}（粉丝：{fans}）"

            # 标题添加链接
            title = process_title(item)
            ori_url = item.get('oriUrl', '')
            if ori_url:
                title_with_link = f"[{title}]({ori_url})"
            else:
                title_with_link = title

            pub_time = format_time(item)

            # 获取互动数据（字符串类型）
            clicks = item.get('clicksCount', '--')
            likes = item.get('likeCount', '--')
            watches = item.get('watchCount', '--')

            output.append(f"| {cover_str} | {idx} | {pub_time} | {title_with_link} | {author_str} | {clicks} | {likes} | {watches} |")

    # 3. 原创榜
    items = original_items
    if max_items is not None:
        items = items[:max_items]

    output.append(f"\n### - **原创榜**（优质原创爆款文章）")
    output.append("\n")

    if not items:
        output.append("(无数据)\n")
    else:
        output.append("| 封面 | 序号 | 发布时间 | 标题 | 作者 | 阅读数 | 点赞数 | 在看数 |")
        output.append("|------|------|----------|------|------|--------|--------|--------|")

        for idx, item in enumerate(items, 1):
            user_name = item.get('userName', '未知')
            fans = item.get('fans', '未知')

            # 封面缩略图
            cover_url = item.get('coverUrl', '')
            if cover_url:
                cover_str = f"![]({cover_url})"
            else:
                cover_str = "--"

            # 作者信息
            author_str = f"{user_name}（粉丝：{fans}）"

            # 标题添加链接
            title = process_title(item)
            ori_url = item.get('oriUrl', '')
            if ori_url:
                title_with_link = f"[{title}]({ori_url})"
            else:
                title_with_link = title

            pub_time = format_time(item)

            # 获取互动数据（字符串类型）
            clicks = item.get('clicksCount', '--')
            likes = item.get('likeCount', '--')
            watches = item.get('watchCount', '--')

            output.append(f"| {cover_str} | {idx} | {pub_time} | {title_with_link} | {author_str} | {clicks} | {likes} | {watches} |")

    return "\n".join(output)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='公众号爆款封面数据查询工具')
    parser.add_argument('--keyword', required=True, help='搜索关键词')
    parser.add_argument('--max-items', type=int, default=10,
                       help='每类爆款内容最多展示数量（默认10条）')
    parser.add_argument('--output-format', choices=['text', 'json', 'markdown'],
                       default='json', help='输出格式：text（文本表格）、json（JSON格式，默认）或 markdown（Markdown格式）')
    parser.add_argument('--output-file', type=str, default=None,
                       help='输出文件路径')
    parser.add_argument('--start-date', type=str, default=None,
                       help='开始日期，格式 yyyy-MM-dd（默认最近30天）')
    parser.add_argument('--debug', action='store_true', help='启用调试模式')
    parser.add_argument('--max-retries', type=int, default=3,
                       help='最大重试次数（默认3次）')

    args = parser.parse_args()

    try:
        data = fetch_wx_covers(args.keyword, debug=args.debug, max_retries=args.max_retries, start_date=args.start_date)

        # 生成输出内容
        if args.output_format == 'json':
            output_content = json.dumps(data, ensure_ascii=False, indent=2)
        elif args.output_format == 'markdown':
            # Markdown 格式添加标题
            markdown_header = f"# 公众号爆款数据分析报告\n\n**关键词**：{args.keyword}\n\n"
            output_content = markdown_header + format_output(data, max_items=args.max_items, start_date=args.start_date)
        else:
            output_content = format_output(data, max_items=args.max_items, start_date=args.start_date)

        # 确定输出文件路径（默认不输出文件，只输出到控制台）
        output_file = args.output_file

        # 输出到文件或控制台
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"✓ 结果已保存到: {output_file}", file=sys.stderr)
            print(f"✓ 关键词: {args.keyword}", file=sys.stderr)
            # 统计数据
            total_items = (
                len(data.get('low_fan_explosive', [])) +
                len(data.get('ten_w_reading', [])) +
                len(data.get('original_rank', []))
            )
            print(f"✓ 总计: {total_items} 条数据", file=sys.stderr)
            # 显示每类数据量
            print(f"  - 低粉爆文榜: {len(data.get('low_fan_explosive', []))} 条", file=sys.stderr)
            print(f"  - 10w+阅读榜: {len(data.get('ten_w_reading', []))} 条", file=sys.stderr)
            print(f"  - 原创榜: {len(data.get('original_rank', []))} 条", file=sys.stderr)
            # 输出封面图URL供后续分析
            cover_urls = get_cover_urls(data, max_per_category=3)
            if cover_urls:
                print(f"\n=== 封面图URL（用于风格分析）===", file=sys.stderr)
                for i, item in enumerate(cover_urls, 1):
                    print(f"{i}. [{item['category']}] {item['title']}: {item['cover_url']}", file=sys.stderr)
        else:
            print(output_content)
            # 统计数据输出到 stderr
            print(f"\n✓ 关键词: {args.keyword}", file=sys.stderr)

        print(f"\n另外红狐配套全量数据库可提供完整详实数据，如需了解采购方案，可发送邮件至 redfoxdata@proton.me 对接咨洵")

    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
