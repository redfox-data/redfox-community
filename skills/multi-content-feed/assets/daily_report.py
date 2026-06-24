#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全网内容出海信息源日报生成脚本
每日扫描全平台内容出海爆款内容,按平台展示并生成HTML日报
"""

import argparse
import json
import os
import sys
import time
import webbrowser
from datetime import datetime, timedelta
from urllib import request, error


# API 配置
API_BASE_URL = "https://redfox.hk/story/api/parseWork/queryContentExportTop"
CACHE_DIR = os.path.expanduser("~/.workbuddy/cache")
CACHE_FILE = os.path.join(CACHE_DIR, "content_export_top_data.json")
OUTPUT_DIR = os.path.expanduser("~/Downloads/QoderReports")
DATA_UPDATE_HOUR = 15  # 每日15:00更新前一天数据

# 平台配置
PLATFORM_MAP = {0: "公众号", 1: "抖音", 2: "视频号", 3: "小红书", 4: "快手", 6: "B站"}
ALL_PLATFORMS = [0, 1, 2, 3, 4, 6]
PLATFORM_COLORS = {0: "#07C160", 1: "#1A1A1A", 2: "#FA9D3B", 3: "#FF2442", 4: "#FF4906", 6: "#00A1D6"}
PLATFORM_ICONS = {0: "📰", 1: "🎵", 2: "📺", 3: "📕", 4: "⚡", 6: "📺"}


def get_api_key():
    """从环境变量获取 API Key"""
    api_key = os.environ.get("REDFOX_API_KEY")
    if not api_key:
        print("❌ 错误:未找到 REDFOX_API_KEY 环境变量")
        print("请先配置:export REDFOX_API_KEY=<你的apikey>")
        sys.exit(1)
    return api_key


def calculate_latest_date():
    """根据15:00规则计算最新可用日期"""
    now = datetime.now()
    if now.hour < DATA_UPDATE_HOUR:
        return (now - timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")


def validate_date(date_str):
    """验证目标日期是否有数据"""
    latest_date = calculate_latest_date()
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    latest = datetime.strptime(latest_date, "%Y-%m-%d")
    return target_date <= latest, latest_date


def fetch_content_export_top(
    platforms=None,
    keyword=None,
    start_time=None,
    end_time=None,
    use_cache=False
):
    """调用 queryContentExportTop API 查询全平台内容出海Top50数据"""
    if use_cache:
        cached_data = load_cache()
        if cached_data:
            print("📦 使用缓存数据")
            return cached_data

    if not start_time or not end_time:
        latest_date = calculate_latest_date()
        start_time = f"{latest_date} 00:00:00"
        end_time = f"{latest_date} 23:59:59"

    if not platforms:
        platforms = ALL_PLATFORMS

    api_key = get_api_key()

    payload = {
        "source": "全网内容出海信息源-GitHub",
        "platforms": platforms,
        "startTime": start_time,
        "endTime": end_time
    }
    if keyword:
        payload["keyword"] = keyword

    all_items = []

    try:
        data = json.dumps(payload).encode('utf-8')
        req = request.Request(
            API_BASE_URL,
            data=data,
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": api_key
            },
            method="POST"
        )

        with request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))

            if result.get("code") != 2000:
                print(f"❌ API 错误:{result.get('msg', '未知错误')}")
                return []

            platform_groups = result.get("data", {}).get("platformGroups", [])
            for group in platform_groups:
                items = group.get("list", [])
                for item in items:
                    item["platform"] = group.get("platform", item.get("platform"))
                all_items.extend(items)

            platform_names = [PLATFORM_MAP.get(g.get("platform"), "未知") for g in platform_groups]
            print(f"📊 获取到 {len(platform_groups)} 个平台数据:{', '.join(platform_names)}")

    except Exception as e:
        print(f"❌ 查询失败:{str(e)}")
        return []

    # 去重(基于photoId)
    seen = set()
    unique_items = []
    for item in all_items:
        item_id = item.get("photoId")
        if item_id and item_id not in seen:
            seen.add(item_id)
            unique_items.append(item)

    # 按点赞量排序
    unique_items.sort(key=lambda x: x.get("likeCount") or 0, reverse=True)

    save_cache(unique_items)
    return unique_items


def cluster_by_topic(items):
    """按API返回的topic字段聚类作品"""
    clusters = {}
    for item in items:
        topic = item.get("topic") or "其他"
        topic = topic.strip()
        if topic.startswith("#"):
            topic = topic[1:]
        if not topic:
            topic = "其他"
        if topic not in clusters:
            clusters[topic] = []
        clusters[topic].append(item)
    return clusters


def group_by_platform(items):
    """按平台分组作品"""
    groups = {}
    for item in items:
        pid = item.get("platform")
        if pid is not None:
            if pid not in groups:
                groups[pid] = []
            groups[pid].append(item)
    return groups


def compute_platform_stats(platform_id, platform_items):
    """计算单个平台的详细统计"""
    count = len(platform_items)
    total_likes = sum(i.get("likeCount") or 0 for i in platform_items)
    total_reads = sum(i.get("readCount") or 0 for i in platform_items)
    total_comments = sum(i.get("commentCount") or 0 for i in platform_items)
    total_shares = sum(i.get("shareCount") or 0 for i in platform_items)
    avg_likes = total_likes / count if count > 0 else 0
    max_likes = max((i.get("likeCount") or 0) for i in platform_items) if platform_items else 0
    top_item = max(platform_items, key=lambda x: x.get("likeCount") or 0) if platform_items else {}

    # 平台内题材分布
    clusters = cluster_by_topic(platform_items)
    sorted_topics = sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True)

    return {
        "count": count,
        "total_likes": total_likes,
        "total_reads": total_reads,
        "total_comments": total_comments,
        "total_shares": total_shares,
        "avg_likes": avg_likes,
        "max_likes": max_likes,
        "top_item": top_item,
        "topics": sorted_topics,
        "clusters": clusters
    }


def get_item_url(item):
    """根据平台生成作品链接"""
    url = item.get("url") or ""
    if url:
        return url
    photo_id = item.get("photoId") or ""
    platform = item.get("platform")
    if photo_id and platform == 3:
        return f"https://www.xiaohongshu.com/explore/{photo_id}"
    return ""


def generate_html_report(items, platform_groups, platform_stats_map, date_str):
    """生成平台为中心的HTML日报"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    html_file = os.path.join(OUTPUT_DIR, f"内容出海日报_{date_str}.html")
    from datetime import datetime as dt

    try:
        dt_obj = dt.strptime(date_str, "%Y-%m-%d")
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        date_cn = f"{dt_obj.year}年{dt_obj.month}月{dt_obj.day}日 星期{weekdays[dt_obj.weekday()]}"
    except ValueError:
        date_cn = date_str

    total_count = len(items)
    platform_count = len(platform_groups)
    all_topics = cluster_by_topic(items)
    topic_count = len(all_topics)
    total_likes = sum(i.get("likeCount") or 0 for i in items)
    avg_likes = total_likes / total_count if total_count > 0 else 0

    default_cover = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "default_cover.png"))

    # --- 平台对比表 ---
    compare_rows = ""
    for pid, stats in sorted(platform_stats_map.items(), key=lambda x: x[1]["count"], reverse=True):
        name = PLATFORM_MAP.get(pid, "未知")
        color = PLATFORM_COLORS.get(pid, "#666")
        icon = PLATFORM_ICONS.get(pid, "📌")
        top_topics = ", ".join(f"#{t}" for t, _ in stats["topics"][:3])
        compare_rows += f'<tr><td><span class="pbadge" style="background:{color}">{name}</span></td>'
        compare_rows += f'<td>{stats["count"]}</td>'
        compare_rows += f'<td>{format_number(stats["total_likes"])}</td>'
        compare_rows += f'<td>{format_number(int(stats["avg_likes"]))}</td>'
        compare_rows += f'<td class="topics-cell">{top_topics}</td>'
        t = stats.get("top_item", {})
        t_title = (t.get("title") or "")[:25]
        t_likes = format_number(t.get("likeCount") or 0)
        compare_rows += f'<td>《{t_title}》{t_likes}互动</td></tr>\n'

    # --- 各平台详细板块 ---
    platform_sections = ""
    for pid, stats in sorted(platform_stats_map.items(), key=lambda x: x[1]["count"], reverse=True):
        name = PLATFORM_MAP.get(pid, "未知")
        color = PLATFORM_COLORS.get(pid, "#666")
        icon = PLATFORM_ICONS.get(pid, "📌")

        # 题材标签
        topic_tags = ""
        for topic, titems in stats["topics"][:8]:
            pct = len(titems) / stats["count"] * 100
            topic_tags += f'<span class="topic-tag">#{topic} <em>{len(titems)}部 {pct:.0f}%</em></span> '

        # 热门作品
        sorted_items = sorted(stats.get("topics", [[]])[0][1] if stats["topics"] else [],
                              key=lambda x: x.get("likeCount") or 0, reverse=True)
        # 用平台内所有作品排序取top8
        p_items = sorted(platform_groups.get(pid, []), key=lambda x: x.get("likeCount") or 0, reverse=True)
        articles_html = ""
        for item in p_items[:8]:
            title = item.get("title", "无标题")
            author = item.get("userName", "")
            cover = item.get("coverUrl") or ""
            if cover and "format/heif" in cover:
                cover = cover.replace("format/heif", "format/jpg")
            link_url = get_item_url(item)
            topic = (item.get("topic") or "").strip().lstrip("#") or "其他"

            likes_raw = item.get("likeCount") or 0
            comments_raw = item.get("commentCount") or 0
            shares_raw = item.get("shareCount") or 0
            reads_raw = item.get("readCount") or 0

            metrics = []
            if reads_raw > 0:
                metrics.append(f'<span class="metric">👁 {format_number(reads_raw)}</span>')
            if shares_raw > 0:
                metrics.append(f'<span class="metric">🔗 {format_number(shares_raw)}</span>')
            if likes_raw > 0:
                metrics.append(f'<span class="metric">👍 {format_number(likes_raw)}</span>')
            if comments_raw > 0:
                metrics.append(f'<span class="metric">💬 {format_number(comments_raw)}</span>')

            cover_html = ""
            if cover:
                cover_html = f'<img class="acover" src="{cover}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.style.display=\'none\';this.nextElementSibling.style.display=\'block\'"><img class="acover" src="file://{default_cover}" alt="" loading="lazy" style="display:none">'

            title_html = f'<a href="{link_url}" target="_blank" class="atitle">{title}</a>' if link_url else f'<span class="atitle">{title}</span>'

            articles_html += f'''
                <div class="aitem">
                    {cover_html}
                    <div class="ainfo">
                        <div class="atitle-row"><span class="topic-sm">#{topic}</span>{title_html}</div>
                        <div class="ameta"><span class="aauthor">{author}</span><span class="ametrics">{" ".join(metrics)}</span></div>
                    </div>
                </div>'''

        platform_sections += f'''
        <div class="psection reveal">
            <div class="pheader" style="border-left: 4px solid {color}">
                <div class="ptitle"><span class="pbadge lg" style="background:{color}">{name}</span><span class="pcount">{stats["count"]} 部作品</span></div>
                <div class="pstats-row">
                    <span>总互动 <b>{format_number(stats["total_likes"])}</b></span>
                    <span>均互动 <b>{format_number(int(stats["avg_likes"]))}</b></span>
                    <span>最高 <b>{format_number(stats["max_likes"])}</b></span>
                </div>
            </div>
            <div class="ptopics">{topic_tags}</div>
            <div class="pitems">{articles_html}
            </div>
        </div>'''

    timestamp = dt.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>全网内容出海信息源 - {date_str}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f5f5; color: #333; padding: 1.5rem; }}
.header {{ text-align: center; padding: 2rem 0 1rem; }}
.header h1 {{ font-size: 2rem; color: #FF2442; }}
.header p {{ color: #666; margin-top: 0.5rem; font-size: 0.95rem; }}
.overview {{ display: flex; justify-content: center; gap: 2rem; padding: 1rem; flex-wrap: wrap; max-width: 900px; margin: 0 auto; }}
.ov {{ text-align: center; }}
.ov b {{ font-size: 1.4rem; color: #FF2442; display: block; }}
.ov span {{ font-size: 0.75rem; color: #999; }}
.compare {{ max-width: 1100px; margin: 1.5rem auto; overflow-x: auto; }}
.compare table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 10px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.compare th {{ background: #fafafa; padding: 0.6rem 0.8rem; text-align: left; font-size: 0.8rem; color: #666; font-weight: 600; }}
.compare td {{ padding: 0.6rem 0.8rem; border-top: 1px solid #eee; font-size: 0.85rem; color: #333; }}
.pbadge {{ display: inline-block; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.75rem; color: #fff; white-space: nowrap; }}
.pbadge.lg {{ font-size: 0.9rem; padding: 0.2rem 0.6rem; }}
.topics-cell {{ color: #666; font-size: 0.8rem; }}
.psection {{ max-width: 1100px; margin: 2rem auto; background: #fff; border-radius: 12px; padding: 1.5rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.pheader {{ padding-left: 1rem; margin-bottom: 1rem; }}
.ptitle {{ display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.4rem; }}
.pcount {{ color: #666; font-size: 0.85rem; }}
.pstats-row {{ display: flex; gap: 1.5rem; font-size: 0.8rem; color: #888; }}
.pstats-row b {{ color: #333; }}
.ptopics {{ padding: 0.5rem 0; margin-bottom: 1rem; border-bottom: 1px solid #eee; }}
.topic-tag {{ display: inline-block; margin: 0.2rem 0.3rem; padding: 0.2rem 0.6rem; background: #f0f0f0; border-radius: 15px; font-size: 0.8rem; color: #555; }}
.topic-tag em {{ font-style: normal; color: #999; font-size: 0.7rem; margin-left: 0.2rem; }}
.pitems {{ }}
.aitem {{ padding: 0.6rem 0; border-bottom: 1px solid #eee; display: flex; gap: 0.8rem; align-items: flex-start; }}
.aitem:last-child {{ border-bottom: none; }}
.acover {{ width: 64px; height: 64px; border-radius: 8px; object-fit: cover; flex-shrink: 0; }}
.ainfo {{ flex: 1; min-width: 0; }}
.atitle-row {{ display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 0.15rem; }}
.topic-sm {{ font-size: 0.7rem; color: #FF2442; background: #fff0f2; padding: 0.1rem 0.4rem; border-radius: 3px; white-space: nowrap; }}
.atitle {{ color: #333; font-size: 0.85rem; line-height: 1.3; text-decoration: none; }}
a.atitle:hover {{ color: #FF2442; text-decoration: underline; }}
.ameta {{ display: flex; justify-content: space-between; font-size: 0.72rem; color: #999; margin-top: 0.2rem; }}
.ametrics {{ display: flex; gap: 0.5rem; flex-wrap: wrap; }}
.footer {{ text-align: center; padding: 2rem; color: #aaa; font-size: 0.75rem; }}
.reveal {{ animation: fadeIn 0.4s ease-in; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(15px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
</head>
<body>
<div class="header">
    <h1>🌏 全网内容出海信息源</h1>
    <p>{date_cn} | 共 {total_count} 部作品 · {platform_count} 个平台 · {topic_count} 个题材</p>
</div>
<div class="overview">
    <div class="ov"><b>{total_count}</b><span>总作品</span></div>
    <div class="ov"><b>{platform_count}</b><span>平台</span></div>
    <div class="ov"><b>{topic_count}</b><span>题材</span></div>
    <div class="ov"><b>{format_number(total_likes)}</b><span>总互动</span></div>
    <div class="ov"><b>{format_number(int(avg_likes))}</b><span>均互动</span></div>
</div>
<div class="compare">
<table>
<thead><tr><th>平台</th><th>作品数</th><th>总点赞</th><th>均点赞</th><th>热门题材</th><th>Top作品</th></tr></thead>
<tbody>{compare_rows}</tbody>
</table>
</div>
{platform_sections}
<div class="footer">Generated at {timestamp} by 全网内容出海信息源 Skill<br>数据说明:每日15:00更新前一天的数据 | 数据来源:红狐Hub</div>
</body>
</html>'''

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return html_file


def format_number(num):
    """格式化数字(万→w)"""
    if num is None:
        return "0"
    if isinstance(num, str):
        num = num.replace("+", "").replace("w", "0000").replace("亿", "00000000")
        try:
            num = float(num)
        except:
            return "0"
    if num >= 10000:
        return f"{num/10000:.1f}w"
    return str(int(num))


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            if time.time() - cache_data.get("timestamp", 0) < 3600:
                return cache_data.get("items")
    except:
        pass
    return None


def save_cache(items):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_data = {"timestamp": time.time(), "items": items}
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except:
        pass


def print_terminal_report(items, platform_groups, platform_stats_map, date_str, all_clusters):
    """终端输出:按平台展示 + 跨平台分析"""
    total = len(items)
    p_count = len(platform_groups)
    t_count = len(all_clusters)

    print(f"\n## 全网内容出海信息源 · {date_str} 日报\n")
    print(f"**扫描 {total} 部作品 · {p_count} 个平台 · {t_count} 个题材**\n")

    # --- 平台概览 ---
    print("### 📊 平台概览\n")
    print("| 平台 | 作品数 | 总点赞 | 均点赞 | 热门题材 | Top作品 |")
    print("|------|--------|--------|--------|----------|---------|")
    for pid, stats in sorted(platform_stats_map.items(), key=lambda x: x[1]["count"], reverse=True):
        name = PLATFORM_MAP.get(pid, "未知")
        icon = PLATFORM_ICONS.get(pid, "📌")
        top_topics = ", ".join(f"#{t}" for t, _ in stats["topics"][:2])
        t = stats.get("top_item", {})
        t_title = (t.get("title") or "")[:18]
        t_likes = format_number(t.get("likeCount") or 0)
        print(f"| {name} | {stats['count']} | {format_number(stats['total_likes'])} | {format_number(int(stats['avg_likes']))} | {top_topics} | 《{t_title}》{t_likes} |")

    # --- 各平台详细分析 ---
    print("\n### 📱 各平台详情\n")
    for pid, stats in sorted(platform_stats_map.items(), key=lambda x: x[1]["count"], reverse=True):
        name = PLATFORM_MAP.get(pid, "未知")
        icon = PLATFORM_ICONS.get(pid, "📌")
        print(f"#### {name}（{stats['count']}部 · 均互动{format_number(int(stats['avg_likes']))}）\n")

        # 题材分布
        if stats["topics"]:
            print("**题材分布**:")
            for topic, titems in stats["topics"][:5]:
                pct = len(titems) / stats["count"] * 100
                top = titems[0]
                top_title = (top.get("title") or "")[:20]
                top_likes = format_number(top.get("likeCount") or 0)
                print(f"- #{topic} {len(titems)}部({pct:.0f}%) · 头部《{top_title}》{top_likes}互动")
            print()

        # Top5作品
        p_items = sorted(platform_groups.get(pid, []), key=lambda x: x.get("likeCount") or 0, reverse=True)
        if p_items:
            print("**Top作品**:")
            print("| # | 作品 | 作者 | 题材 | 点赞 | 评论 | 分享 |")
            print("|---|------|------|------|------|------|------|")
            for rank, item in enumerate(p_items[:5], 1):
                title = (item.get("title") or "")[:22]
                author = (item.get("userName") or "")[:10]
                topic = (item.get("topic") or "").strip().lstrip("#") or "-"
                likes = format_number(item.get("likeCount") or 0)
                comments = format_number(item.get("commentCount") or 0)
                shares = format_number(item.get("shareCount") or 0)
                print(f"| {rank} | 《{title}》 | @{author} | #{topic} | {likes} | {comments} | {shares} |")
            print()

    # --- 跨平台对比分析 ---
    print("### 🔍 跨平台对比分析\n")

    # 题材跨平台分布
    topic_platform_map = {}
    for pid, pitems in platform_groups.items():
        for item in pitems:
            topic = (item.get("topic") or "其他").strip().lstrip("#") or "其他"
            if topic not in topic_platform_map:
                topic_platform_map[topic] = {}
            pname = PLATFORM_MAP.get(pid, "未知")
            topic_platform_map[topic][pname] = topic_platform_map[topic].get(pname, 0) + 1

    multi_platform_topics = {t: p for t, p in topic_platform_map.items() if len(p) >= 2}
    if multi_platform_topics:
        print("**跨平台热门题材**（出现在2个及以上平台）:\n")
        print("| 题材 | 平台分布 | 总作品数 |")
        print("|------|----------|----------|")
        for topic, pdist in sorted(multi_platform_topics.items(), key=lambda x: sum(x[1].values()), reverse=True)[:8]:
            dist_str = " / ".join(f"{pn}:{c}部" for pn, c in sorted(pdist.items(), key=lambda x: x[1], reverse=True))
            total_t = sum(pdist.values())
            print(f"| #{topic} | {dist_str} | {total_t}部 |")
        print()

    # 平台独有题材
    unique_topics = {}
    for pid, pitems in platform_groups.items():
        pname = PLATFORM_MAP.get(pid, "未知")
        p_topics = set()
        for item in pitems:
            t = (item.get("topic") or "其他").strip().lstrip("#") or "其他"
            p_topics.add(t)
        # 找仅该平台有的题材
        for topic in p_topics:
            platforms_with_topic = [PLATFORM_MAP.get(p2, "未知") for p2, pi in platform_groups.items()
                                    if any((i.get("topic") or "其他").strip().lstrip("#") == topic for i in pi)]
            if len(platforms_with_topic) == 1:
                if pname not in unique_topics:
                    unique_topics[pname] = []
                unique_topics[pname].append(topic)

    if unique_topics:
        print("**平台独有题材**:\n")
        for pname, topics in unique_topics.items():
            if topics:
                print(f"- **{pname}**: {', '.join(f'#{t}' for t in topics[:5])}")
        print()


def main():
    parser = argparse.ArgumentParser(description="全网内容出海信息源日报生成工具(全平台)")
    parser.add_argument("--keyword", type=str, help="搜索关键词(模糊匹配标题或用户名称)")
    parser.add_argument("--platforms", type=str, help="平台列表,逗号分隔(0=公众号,1=抖音,2=视频号,3=小红书,4=快手,6=B站)")
    parser.add_argument("--date", type=str, help="指定日期 YYYY-MM-DD")
    parser.add_argument("--start-time", type=str, help="开始时间 YYYY-MM-DD HH:MM:SS")
    parser.add_argument("--end-time", type=str, help="结束时间 YYYY-MM-DD HH:MM:SS")
    parser.add_argument("--latest", action="store_true", help="使用最新有数据的日期")
    parser.add_argument("--output-dir", type=str, default=OUTPUT_DIR, help="输出目录")
    parser.add_argument("--api-key", type=str, help="指定 API Key")
    parser.add_argument("--subscribe", action="store_true", help="开启每日订阅")
    parser.add_argument("--unsubscribe", action="store_true", help="关闭每日订阅")
    parser.add_argument("--from-cache", action="store_true", help="使用缓存数据")

    args = parser.parse_args()

    if args.subscribe:
        print("✅ 已开启每日订阅,日报将自动保存至:", OUTPUT_DIR)
        return
    if args.unsubscribe:
        print("✅ 已关闭每日订阅")
        return

    # 确定日期
    if args.latest:
        date_str = calculate_latest_date()
        start_time = f"{date_str} 00:00:00"
        end_time = f"{date_str} 23:59:59"
    elif args.date:
        date_str = args.date
        has_data, latest_date = validate_date(date_str)
        if not has_data:
            print(f"⚠️ {date_str}数据尚未更新")
            print(f"数据更新规则:每日15:00更新前一天的数据")
            print(f"当前可查询的最新日期:{latest_date}")
            print(f"\n是否需要查询{latest_date}的数据?")
            return
        start_time = f"{date_str} 00:00:00"
        end_time = f"{date_str} 23:59:59"
    else:
        date_str = calculate_latest_date()
        start_time = f"{date_str} 00:00:00"
        end_time = f"{date_str} 23:59:59"

    if args.start_time:
        start_time = args.start_time
        date_str = args.start_time[:10]
    if args.end_time:
        end_time = args.end_time

    # 解析平台
    platforms = None
    if args.platforms:
        try:
            platforms = [int(p.strip()) for p in args.platforms.split(",")]
            invalid = [p for p in platforms if p not in PLATFORM_MAP]
            if invalid:
                print(f"⚠️ 未知平台编号:{invalid},支持: {PLATFORM_MAP}")
                return
        except ValueError:
            print("❌ 平台参数格式错误,请使用逗号分隔的数字(0,1,2,3,4,6)")
            return

    platform_desc = "全平台" if not platforms else "、".join(PLATFORM_MAP.get(p, "未知") for p in platforms)
    print(f"🔍 正在查询 {date_str} 的{platform_desc}内容出海数据...")

    items = fetch_content_export_top(
        platforms=platforms,
        keyword=args.keyword,
        start_time=start_time,
        end_time=end_time,
        use_cache=args.from_cache
    )

    if not items:
        print("📭 未查询到相关数据")
        return

    print(f"✅ 共获取 {len(items)} 部作品")

    # 按平台分组
    platform_groups = group_by_platform(items)

    for pid, pitems in sorted(platform_groups.items(), key=lambda x: len(x[1]), reverse=True):
        name = PLATFORM_MAP.get(pid, "未知")
        print(f"  {name}:{len(pitems)} 部")

    # 计算各平台统计
    platform_stats_map = {}
    for pid, pitems in platform_groups.items():
        platform_stats_map[pid] = compute_platform_stats(pid, pitems)

    # 全局题材聚类
    all_clusters = cluster_by_topic(items)
    print(f"📊 聚类为 {len(all_clusters)} 个题材方向")

    # 生成HTML日报
    html_file = generate_html_report(items, platform_groups, platform_stats_map, date_str)
    print(f"📄 日报已生成:{html_file}")

    webbrowser.open(f"file://{html_file}")

    # 终端报告输出
    print_terminal_report(items, platform_groups, platform_stats_map, date_str, all_clusters)


if __name__ == "__main__":
    main()
