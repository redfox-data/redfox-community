#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号10w+热门文章榜单获取脚本

功能：
1. 调用API获取10w+阅读热门文章数据
2. 按互动数排序
3. 输出TOP30榜单列表（纯文本格式）
4. 提供四维度内容分析（内容概述、热点利用、传播作用、达成效果）

使用方法：
python fetch_hot_articles.py --keyword "战争" --source "公众号10w+热门文章推荐-GitHub" --start_date "2024-01-01"
python fetch_hot_articles.py --keyword "" --source "公众号10w+热门文章推荐-GitHub" --start_date "yesterday"
python fetch_hot_articles.py --keyword "AI" --source "公众号10w+热门文章推荐-GitHub" --start_date ""
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from coze_workload_identity import requests


def parse_date(date_str: str) -> str:
    """
    解析日期参数

    Args:
        date_str: 日期字符串，支持：
                 - "yesterday": 昨天（今日数据用）
                 - "today": 今天
                 - "": 不限时间
                 - "YYYY-MM-DD": 具体日期

    Returns:
        格式化的日期字符串（YYYY-MM-DD），如果为空则返回空字符串
    """
    if not date_str or date_str == "":
        return ""

    date_str = date_str.strip().lower()

    # 昨天（今日数据用）
    if date_str == "daybeforeyesterday":
        # 前天（用于最新推荐）
        daybeforeyesterday = datetime.now() - timedelta(days=2)
        return daybeforeyesterday.strftime("%Y-%m-%d")

    if date_str == "yesterday":
        # 昨天
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")

    # 今天
    if date_str == "today":
        return datetime.now().strftime("%Y-%m-%d")

    # 验证日期格式是否正确
    try:
        # 尝试解析日期
        dt = datetime.strptime(date_str, "%Y-%m-%d")

        # 检查日期是否在前30天内
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)

        if dt < thirty_days_ago:
            raise Exception(f"日期不能早于30天前（最早支持：{thirty_days_ago.strftime('%Y-%m-%d')}）")

        if dt > today:
            raise Exception("日期不能晚于今天")

        return date_str
    except ValueError:
        raise Exception(f"日期格式错误，请使用 YYYY-MM-DD 格式，如 2024-01-01")


def fetch_explosive_articles(keyword: str, source: str, start_date: str = "") -> dict:
    """
    调用API获取爆款内容数据

    Args:
        keyword: 关键词（从用户输入中提取，如"战争"）
        source: 数据源（固定值："公众号10w+热门文章推荐-GitHub"）
        start_date: 开始日期（YYYY-MM-DD，空字符串表示不限时间）

    Returns:
        API返回的数据
    """
    base_url = "https://onetotenvip.com/skill/cozeSkill/getWxCozeSkillData"

    # GET请求参数
    params = {
        "keyword": keyword,
        "source": source
    }

    # 如果有开始日期，添加到参数中
    if start_date:
        params["startDate"] = start_date

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(base_url, params=params, headers=headers, timeout=30)

        # 检查HTTP状态码
        if response.status_code >= 400:
            raise Exception(f"HTTP请求失败: 状态码 {response.status_code}, 响应内容: {response.text}")

        data = response.json()

        # 检查API返回的错误信息（成功码为2000）
        if "code" in data and data["code"] != 2000:
            error_msg = data.get("message", data.get("msg", "未知错误"))
            raise Exception(f"API错误: {error_msg}")

        return data

    except requests.exceptions.RequestException as e:
        raise Exception(f"网络请求失败: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"JSON解析失败: {str(e)}")


def process_ranking_data(data: dict, top_n: int = 10) -> list:
    """
    处理榜单数据，按互动数排序

    Args:
        data: API返回的原始数据
        top_n: 返回前N条数据（默认10条）

    Returns:
        排序后的榜单列表
    """
    # 提取文章列表 - 从data.tenWReadingRank字段获取
    articles = []

    if isinstance(data, dict):
        # 从data.tenWReadingRank字段获取文章列表
        articles = data.get("data", {}).get("tenWReadingRank", [])
        if not articles:
            # 兼容：如果data.tenWReadingRank不存在，尝试从根目录获取
            articles = data.get("tenWReadingRank", [])
    elif isinstance(data, list):
        articles = data

    if not articles:
        return []

    # 按互动数排序
    def get_interaction_score(article):
        interactive_count = article.get("interactiveCount", 0)
        if not interactive_count or parse_count_to_int(interactive_count) == 0:
            # 使用 parse_count_to_int 正确处理 "10w+" 等格式
            clicks_count = parse_count_to_int(article.get("clicksCount", "0"))
            like_count = parse_count_to_int(article.get("likeCount", "0"))
            return int(clicks_count or 0) + int(like_count or 0) * 10
        return parse_count_to_int(interactive_count)

    sorted_articles = sorted(articles, key=get_interaction_score, reverse=True)

    return sorted_articles[:top_n]


def format_summary_table(articles: list) -> str:
    """
    生成文章摘要表格（序号 标题 作者 阅读数）

    Args:
        articles: 文章列表

    Returns:
        Markdown格式的表格字符串
    """
    if not articles:
        return "暂无数据"

    # 表格头部
    table_lines = ["| 序号 | 标题 | 作者 | 阅读数 |", "|------|------|------|--------|"]

    # 表格内容
    for idx, article in enumerate(articles, 1):
        title = article.get("title", "未知标题")
        account_name = article.get("userName", article.get("accountId", "未知账号"))
        clicks_count = article.get("clicksCount", "0")

        # 处理阅读数显示
        read_count_display = clicks_count if isinstance(clicks_count, str) else format_number(clicks_count)

        # 添加表格行
        table_lines.append(f"| {idx} | {title} | {account_name} | {read_count_display} |")

    return "\n".join(table_lines)


def format_ranking_list(articles: list) -> str:
    """
    将榜单数据格式化为纯文本列表样式（不使用任何表格格式）

    格式示例：
    **1、[标题](链接)**  🔥🔥🔥
    📄 作者：[作者名称](公众号名片链接)  |  分类
    👀 阅读数：5w+
    ⏰ 发布时间：2026-03-24 08:08:57
    ...

    Args:
        articles: 排序后的文章列表

    Returns:
        纯文本列表格式的字符串
    """
    if not articles:
        return "未获取到符合条件的爆款内容数据"

    output_lines = []

    for idx, article in enumerate(articles, 1):
        title = article.get("title", "未知标题")
        account_name = article.get("userName", article.get("accountId", "未知账号"))
        account_id = article.get("accountId", "")
        publish_time = article.get("publicTime", "未知")
        article_link = article.get("oriUrl", "#")
        clicks_count = article.get("clicksCount", "0")

        # 处理阅读数显示
        read_count_display = clicks_count if isinstance(clicks_count, str) else format_number(clicks_count)

        # 构建输出内容
        # 第1行：序号 + 标题（可点击）
        if article_link and article_link != "#":
            output_lines.append(f"**{idx}、[{title}]({article_link})**")
        else:
            output_lines.append(f"**{idx}、{title}**")

        # 第2行：作者（可跳转）
        if account_id:
            account_url = f"https://open.weixin.qq.com/qr/code?username={account_id}"
            output_lines.append(f"📄 作者：[{account_name}]({account_url})")
        else:
            output_lines.append(f"📄 作者：{account_name}")

        # 第3行：阅读数
        output_lines.append(f"👀 阅读数：{read_count_display}")

        # 第4行：发布时间
        output_lines.append(f"⏰ 发布时间：{publish_time}")

        # 第5行：内容分析
        content_analysis = analyze_content(article)
        output_lines.append(f"🔍 内容分析：{content_analysis}")

        # 添加分隔线（除了最后一项）
        if idx < len(articles):
            output_lines.append("---")
            output_lines.append("")

    return "\n".join(output_lines)


def format_number(num) -> str:
    """
    格式化数字显示（万、亿）
    """
    try:
        num = int(num)
        if num >= 100000000:
            return f"{num/100000000:.1f}亿"
        elif num >= 10000:
            return f"{num/10000:.1f}万"
        else:
            return str(num)
    except:
        return str(num)


def parse_count_to_int(count_str) -> int:
    """
    将字符串类型的计数转换为整数
    支持 "1w+", "100w+", "5000", "10w+" 等格式
    """
    if isinstance(count_str, (int, float)):
        return int(count_str)

    if not count_str:
        return 0

    count_str = str(count_str).strip().lower()

    # 处理 "1w+", "100w+", "10w+" 等格式
    if 'w+' in count_str:
        # 提取数字部分，去掉 w+ 后缀
        num_str = count_str.replace('w+', '')
        try:
            num = float(num_str)
            return int(num * 10000)
        except ValueError:
            return 0
    elif 'w' in count_str:
        # 提取数字部分，去掉 w 后缀
        num_str = count_str.replace('w', '')
        try:
            num = float(num_str)
            return int(num * 10000)
        except ValueError:
            return 0
    elif '+' in count_str:
        # 处理纯数字带+的情况，如 "10000+"
        num_str = count_str.replace('+', '')
        try:
            return int(num_str)
        except ValueError:
            return 0

    # 处理纯数字
    try:
        return int(count_str)
    except:
        return 0


def analyze_content(article: dict) -> str:
    """
    基于文章的具体文本内容，生成专业且通俗的内容分析

    分析规则：
    1. 内容概述：简明扼要地概括文章核心内容
    2. 热点利用：分析文章借用了哪些热点话题或趋势
    3. 传播作用：阐述内容起到的作用
    4. 达成效果：说明内容达到的效果

    Args:
        article: 文章数据

    Returns:
        内容分析字符串（专业通俗风格）
    """
    # 提取文本内容
    title = article.get("title", "")
    summary = article.get("summary", "")
    content = article.get("content", "")
    article_type = article.get("type", "")

    # 合并所有文本用于分析
    all_text = f"{title} {summary} {content}"

    # 智能判断内容特征
    content_summary = ""
    hotspot_usage = ""
    spread_effect = ""
    achieve_result = ""

    # 判断内容概述
    if any(word in all_text for word in ["新规", "政策", "实施", "调整"]):
        content_summary = f"本文聚焦{title[:10]}...等政策变动"
    elif any(word in all_text for word in ["推荐", "排名", "榜单", "TOP"]):
        content_summary = f"本文发布{title[:10]}...等相关榜单"
    elif any(word in all_text for word in ["揭秘", "曝光", "真相", "内幕"]):
        content_summary = f"本文揭露{title[:10]}...等内幕信息"
    elif any(word in all_text for word in ["攻略", "教程", "方法", "技巧"]):
        content_summary = f"本文提供{title[:10]}...等实用指南"
    elif any(word in all_text for word in ["对比", "区别", "VS", "PK"]):
        content_summary = f"本文对比{title[:10]}...等不同选项"
    else:
        content_summary = f"本文围绕{title[:15]}...展开论述"

    # 判断热点利用
    if any(word in all_text for word in ["新规", "政策", "法规"]):
        hotspot_usage = "文章借助政策实施这一时效性热点"
    elif any(word in all_text for word in ["AI", "人工智能", "大模型", "智能"]):
        hotspot_usage = "文章借力AI技术这一科技热点"
    elif any(word in all_text for word in ["国产", "自主", "替代", "中国"]):
        hotspot_usage = "文章借助国产替代这一产业热点"
    elif any(word in all_text for word in ["涨价", "降价", "利率", "房价"]):
        hotspot_usage = "文章抓住财富管理这一持续热点"
    elif any(word in all_text for word in ["节日", "假期", "春节", "国庆"]):
        hotspot_usage = "文章结合节日消费这一周期性热点"
    elif any(word in all_text for word in ["疫情", "健康", "养生", "医疗"]):
        hotspot_usage = "文章切入健康养生这一民生热点"
    else:
        hotspot_usage = "文章聚焦相关领域热点话题"

    # 判断传播作用
    if any(word in all_text for word in ["提醒", "警告", "注意", "避免", "防"]):
        spread_effect = "精准切中目标用户的信息盲区，起到风险预警和知识普及的作用"
    elif any(word in all_text for word in ["推荐", "建议", "参考", "选择"]):
        spread_effect = "满足用户对决策参考的信息需求，起到专业指导的作用"
    elif any(word in all_text for word in ["科普", "知识", "介绍", "了解"]):
        spread_effect = "满足用户对知识获取的需求，起到信息传播的作用"
    elif any(word in all_text for word in ["激励", "鼓励", "加油", "努力"]):
        spread_effect = "激发用户情绪共鸣，起到情感激励的作用"
    elif any(word in all_text for word in ["争议", "讨论", "质疑", "反驳"]):
        spread_effect = "引发公众关注和讨论，起到话题引导的作用"
    else:
        spread_effect = "满足用户对相关信息的需求，起到内容传播的作用"

    # 判断达成效果
    if any(word in all_text for word in ["推广", "营销", "介绍", "推荐产品"]):
        achieve_result = "成功唤起用户的关注度并引发转发传播"
    elif any(word in all_text for word in ["提醒", "警示", "警告"]):
        achieve_result = "有效提升用户对相关风险的防范意识"
    elif any(word in all_text for word in ["科普", "知识", "讲解"]):
        achieve_result = "有效增强了用户对相关话题的认知和理解"
    elif any(word in all_text for word in ["激励", "鼓励"]):
        achieve_result = "成功激发用户的积极情绪和行动意愿"
    elif any(word in all_text for word in ["争议", "讨论"]):
        achieve_result = "成功引发公众讨论并扩大话题影响力"
    else:
        achieve_result = "有效提升内容的传播度和影响力"

    # 组合分析内容
    analysis_parts = []

    if content_summary:
        analysis_parts.append(content_summary)
    if hotspot_usage:
        analysis_parts.append(f"{hotspot_usage}")
    if spread_effect:
        analysis_parts.append(f"{spread_effect}")
    if achieve_result:
        analysis_parts.append(f"{achieve_result}")

    analysis = "，".join(analysis_parts) + "。"

    return analysis


def main():
    parser = argparse.ArgumentParser(description="获取公众号10w+热门文章榜单")
    parser.add_argument("--keyword", required=True, help="关键词（从用户输入中提取）")
    parser.add_argument("--source", required=False, default="公众号10w+阅读文章推荐", help="数据源（固定值）")
    parser.add_argument("--start_date", required=False, default="", help="开始日期（YYYY-MM-DD格式，或'yesterday'表示昨天，空字符串表示不限时间）")
    parser.add_argument("--top_n", type=int, default=50, help="返回前N条数据（默认50）")
    parser.add_argument("--limit", type=int, default=10, help="首次展示条数（默认10），用于分页")
    parser.add_argument("--mode", default="preview", help="输出模式：preview（首次预览）| full（完整输出）")
    parser.add_argument("--temp_file", default="temp_articles.json", help="临时JSON文件路径（用于保存数据）")

    args = parser.parse_args()

    try:
        # 解析日期参数
        start_date = ""
        if args.start_date:
            start_date = parse_date(args.start_date)

        print(f"正在获取10w+热门文章数据...")
        print(f"关键词: {args.keyword}")
        print(f"数据源: {args.source}")
        print(f"开始日期: {start_date if start_date else '不限'}")
        print("-" * 60)

        # 获取数据
        data = fetch_explosive_articles(args.keyword, args.source, start_date)

        # 处理并排序，获取所有数据
        all_articles = process_ranking_data(data, args.top_n)

        total_count = len(all_articles)

        # 保存数据到临时JSON文件
        temp_file = args.temp_file if args.temp_file else "temp_articles.json"
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "keyword": args.keyword,
                    "articles": all_articles,
                    "total_count": total_count
                }, f, ensure_ascii=False, indent=2)
            print(f"✅ 数据已保存到临时文件: {temp_file}")
        except Exception as e:
            print(f"⚠️  警告：保存临时文件失败 - {str(e)}")

        # 根据模式决定输出内容
        if args.mode == "preview":
            # 预览模式：只显示前10条
            preview_articles = all_articles[:args.limit]
            
            # 输出数据说明
            print("\n💡 数据说明")
            print("最新10w+阅读爆文推荐将在每日19点30分准时更新，以下数据为获取时间时的快照，和实时数据有所差别。")
            print("-" * 60)
            
            # 生成摘要表格（输出在最前面）
            summary_table = format_summary_table(preview_articles)
            print("\n📊 文章概览\n")
            print(summary_table)
            print("\n")
            
            # 输出文章详情
            print("📝 文章详情\n")
            print(format_ranking_list(preview_articles))

            # 输出统计和提示信息
            print("\n" + "=" * 60)
            if total_count > 0:
                print(f"共获取到 {total_count} 条10w+热门文章数据，当前展示前 {len(preview_articles)} 条")
                if total_count > len(preview_articles):
                    print(f"💡 提示：还有 {total_count - len(preview_articles)} 条数据未展示，是否需要全部展示？")
                else:
                    print("已展示全部数据")
            else:
                print("未获取到符合条件的10w+热门文章数据")
                print("建议：尝试调整关键词")

        elif args.mode == "full":
            # 完整模式：显示所有数据
            # 输出数据说明
            print("\n💡 数据说明")
            print("最新10w+阅读爆文推荐将在每日19点30分准时更新，以下数据为获取时间时的快照，和实时数据有所差别。")
            print("-" * 60)
            
            # 生成摘要表格
            summary_table = format_summary_table(all_articles)
            print("\n📊 文章概览\n")
            print(summary_table)
            print("\n")
            
            # 输出文章详情
            print("📝 文章详情\n")
            full_list = format_ranking_list(all_articles)
            print(full_list)

            # 输出统计信息
            print("\n" + "=" * 60)
            if total_count > 0:
                print(f"共获取到 {total_count} 条10w+热门文章数据（已全部展示）")
            else:
                print("未获取到符合条件的10w+热门文章数据")

        return 0

    except json.JSONDecodeError as e:
        print(f"错误: JSON参数解析失败 - {str(e)}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"错误: {str(e)}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
