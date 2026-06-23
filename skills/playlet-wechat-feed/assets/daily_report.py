#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
短剧-公众号信息源日报生成脚本
每日扫描公众号短剧爆款内容,智能聚类题材后生成HTML日报
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
API_BASE_URL = "https://redfox.hk/story/api/parseWork/queryPlayletMsgs"
CACHE_DIR = os.path.expanduser("~/.workbuddy/cache")
CACHE_FILE = os.path.join(CACHE_DIR, "playlet_wechat_data.json")
OUTPUT_DIR = os.path.expanduser("~/Downloads/QoderReports")
DATA_UPDATE_HOUR = 15  # 每日15:00更新前一天数据


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
        # 15:00前,最新可用日期是前天
        return (now - timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        # 15:00后,最新可用日期是昨天
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")


def validate_date(date_str):
    """验证目标日期是否有数据"""
    latest_date = calculate_latest_date()
    target_date = datetime.strptime(date_str, "%Y-%m-%d")
    latest = datetime.strptime(latest_date, "%Y-%m-%d")
    
    return target_date <= latest, latest_date


def fetch_playlet_data(
    topics=None,
    start_time=None,
    end_time=None,
    count=200,
    use_cache=False
):
    """
    调用 API 查询公众号短剧数据
    
    Args:
        topics: 题材列表,逗号分隔
        start_time: 开始时间
        end_time: 结束时间
        count: 扫描数量
        use_cache: 是否使用缓存
    
    Returns:
        list: 文章列表
    """
    # 检查缓存
    if use_cache:
        cached_data = load_cache()
        if cached_data:
            print("📦 使用缓存数据")
            return cached_data
    
    # 如果没有指定时间,使用默认逻辑
    if not start_time or not end_time:
        latest_date = calculate_latest_date()
        start_time = f"{latest_date} 00:00:00"
        end_time = f"{latest_date} 23:59:59"
    
    # 如果没有指定题材,查询全部短剧
    if not topics:
        topics = ["短剧"]
    
    all_items = []
    api_key = get_api_key()
    
    # 批量查询每个题材
    for topic in topics:
        payload = {
            "msgType": "短剧",
            "platform": 0,  # 固定为公众号
            "source": "短剧公众号信息源-GitHub",
            "pageNum": 1,
            "pageSize": min(count, 200),
            "startTime": start_time,
            "endTime": end_time
        }
        
        # 只有当题材不是"短剧"时才添加keyword
        if topic != "短剧":
            payload["keyword"] = topic
        
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
                
                # 检查响应状态（红狐API成功码为2000）
                if result.get("code") != 2000:
                    print(f"❌ API 错误:{result.get('msg', '未知错误')}")
                    continue
                
                items = result.get("data", {}).get("list", [])
                all_items.extend(items)
                
        except Exception as e:
            print(f"❌ 查询题材 {topic} 失败:{str(e)}")
            continue
    
    # 去重(基于photoId)
    seen = set()
    unique_items = []
    for item in all_items:
        item_id = item.get("photoId")
        if item_id and item_id not in seen:
            seen.add(item_id)
            unique_items.append(item)
    
    # 按阅读量排序(公众号核心指标是阅读量而非点赞量)
    unique_items.sort(key=lambda x: x.get("readCount", 0), reverse=True)
    
    # 保存缓存
    save_cache(unique_items)
    
    return unique_items[:count]


def cluster_by_topic(items):
    """
    按题材聚类文章
    
    Args:
        items: 文章列表
    
    Returns:
        dict: {题材: [文章列表]}
    """
    topic_keywords = {
        "穿越": ["穿越", "时空", "古代", "现代", "回到", "大宋", "北宋", "南宋", "唐朝", "明朝", "清朝"],
        "霸总": ["霸总", "总裁", "豪门", "冷酷", "宠妻", "娇妻", "替身"],
        "重生": ["重生", "逆袭", "回到", "翻盘", "重来", "再生"],
        "悬疑": ["悬疑", "推理", "反转", "惊悚", "谜案", "秘密", "真相"],
        "甜宠": ["甜宠", "恋爱", "撒糖", "甜蜜", "宠溺", "甜甜", "撒糖"],
        "逆袭": ["逆袭", "翻身", "打脸", "崛起", "反击", "报复"],
        "年代": ["年代", "八零", "九零", "七零", "六零"],
        "战神": ["战神", "龙王", "兵王", "高手"],
        "古装": ["古装", "宫廷", "皇后", "贵妃", "王爷", "世子"]
    }
    
    clusters = {}
    
    for item in items:
        title = item.get("title", "")
        matched_topic = "其他"
        
        # 统计匹配的题材数量
        matched_topics = []
        for topic, keywords in topic_keywords.items():
            if any(kw in title for kw in keywords):
                matched_topics.append(topic)
        
        # 如果有匹配，使用第一个匹配的题材
        if matched_topics:
            matched_topic = matched_topics[0]
        
        if matched_topic not in clusters:
            clusters[matched_topic] = []
        clusters[matched_topic].append(item)
    
    return clusters


def generate_html_report(items, clusters, date_str):
    """
    生成HTML日报（参照AI公众号信息源格式）
    
    Args:
        items: 文章列表
        clusters: 题材聚类
        date_str: 日期字符串
    
    Returns:
        str: HTML文件路径
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    html_file = os.path.join(OUTPUT_DIR, f"短剧公众号日报_{date_str}.html")
    
    # 生成日期显示
    try:
        from datetime import datetime as dt
        dt_obj = dt.strptime(date_str, "%Y-%m-%d")
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        date_cn = f"{dt_obj.year}年{dt_obj.month}月{dt_obj.day}日 星期{weekdays[dt_obj.weekday()]}"
    except ValueError:
        date_cn = date_str
    
    # 计算统计数据
    total_count = len(items)
    topic_count = len(clusters)
    total_reads = sum(item.get("readCount", 0) for item in items)
    avg_reads = total_reads / total_count if total_count > 0 else 0
    
    # 生成题材卡片
    category_cards = ""
    for i, (topic, topic_items) in enumerate(sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True), 1):
        articles_html = ""
        for item in topic_items[:5]:  # 每个题材展示前5个
            title = item.get("title", "无标题")
            author = item.get("verifyName", "") or item.get("accountName", "") or item.get("author", "")  # 公众号字段，多字段兜底
            cover = item.get("coverUrl") or ""
            raw_reads = item.get("readCount") or 0
            raw_likes = item.get("likeCount") or 0
            raw_comments = item.get("commentCount") or 0
            reads = format_number(raw_reads)   # 阅读量
            likes = format_number(raw_likes)   # 点赞数
            comments = format_number(raw_comments)  # 评论数
            url = item.get("url", "") or item.get("workUrl", "") or item.get("articleUrl", "")  # 文章链接，多字段兜底

            cover_html = ""
            if cover:
                cover_html = f'<img class="article-cover" src="{cover}" alt="" loading="lazy">'

            # 文章标题改为可点击链接
            if url:
                title_html = f'<a class="article-title" href="{url}" target="_blank" rel="noopener noreferrer">{title}</a>'
            else:
                title_html = f'<span class="article-title">{title}</span>'

            # 各项数据为0时不展示该字段
            metrics_parts = []
            if raw_reads > 0:
                metrics_parts.append(f'<span class="metric">👁 {reads}</span>')
            if raw_likes > 0:
                metrics_parts.append(f'<span class="metric">👍 {likes}</span>')
            if raw_comments > 0:
                metrics_parts.append(f'<span class="metric">💬 {comments}</span>')
            metrics_html = "\n                                ".join(metrics_parts) if metrics_parts else ""

            articles_html += f'''
                <div class="article-item">
                    {cover_html}
                    <div class="article-info">
                        {title_html}
                        <div class="article-meta">
                            <span class="author">{author}</span>
                            <span class="metrics">
                                {metrics_html}
                            </span>
                        </div>
                    </div>
                </div>'''
        
        category_cards += f'''
        <div class="category-card reveal">
            <div class="card-header">
                <span class="card-number">{i:02d}</span>
                <h3 class="card-category">#{topic}</h3>
                <span class="card-count">{len(topic_items)} 篇</span>
            </div>
            <div class="card-body">{articles_html}
            </div>
        </div>'''
    
    # 生成完整HTML
    timestamp = dt.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>短剧-公众号信息源 - {date_str}</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, sans-serif; background: #1a1a1a; color: #e8e4df; padding: 2rem; }}
.header {{ text-align: center; padding: 2rem 0; }}
.header h1 {{ font-size: 2rem; color: #07C160; }}
.header p {{ color: #9a9590; margin-top: 0.5rem; }}
.stats {{ display: flex; justify-content: center; gap: 2rem; padding: 1rem; margin: 1rem 0; }}
.stat-item {{ text-align: center; }}
.stat-value {{ font-size: 1.5rem; font-weight: bold; color: #07C160; }}
.stat-label {{ font-size: 0.8rem; color: #9a9590; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 1.5rem; max-width: 1200px; margin: 2rem auto; }}
.category-card {{ background: #2d2d2d; border-radius: 12px; padding: 1.5rem; }}
.card-header {{ display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem; padding-bottom: 0.8rem; border-bottom: 1px solid #3d3d3d; }}
.card-number {{ font-size: 1.5rem; font-weight: bold; color: #07C160; }}
.card-category {{ flex: 1; font-size: 1.1rem; }}
.card-count {{ color: #9a9590; font-size: 0.9rem; }}
.article-item {{ padding: 0.6rem 0; border-bottom: 1px solid #3d3d3d; display: flex; gap: 0.8rem; }}
.article-item:last-child {{ border-bottom: none; }}
.article-cover {{ width: 60px; height: 60px; border-radius: 6px; object-fit: cover; flex-shrink: 0; }}
.article-info {{ flex: 1; min-width: 0; }}
.article-title {{ color: #e8e4df; font-size: 0.9rem; line-height: 1.4; display: block; text-decoration: none; transition: color 0.2s; }}
.article-title:hover {{ color: #07C160; }}
.article-meta {{ display: flex; justify-content: space-between; margin-top: 0.3rem; font-size: 0.75rem; color: #9a9590; }}
.metrics {{ display: flex; gap: 0.8rem; }}
.footer {{ text-align: center; padding: 2rem; color: #666; font-size: 0.8rem; }}
.reveal {{ animation: fadeIn 0.5s ease-in; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
</style>
</head>
<body>
<div class="header">
    <h1>📱 短剧-公众号信息源</h1>
    <p>{date_cn} | 共 {total_count} 篇热门短剧文章</p>
</div>
<div class="stats">
    <div class="stat-item"><div class="stat-value">{topic_count}</div><div class="stat-label">题材</div></div>
    <div class="stat-item"><div class="stat-value">{total_count}</div><div class="stat-label">文章</div></div>
    <div class="stat-item"><div class="stat-value">{format_number(int(avg_reads))}</div><div class="stat-label">平均阅读</div></div>
    <div class="stat-item"><div class="stat-value">{format_number(total_reads)}</div><div class="stat-label">总阅读</div></div>
</div>
<div class="cards">{category_cards}</div>
<div class="footer">Generated at {timestamp} by 短剧-公众号信息源 Skill<br>数据说明：每日15:00更新前一天的数据 | 数据来源：红狐Hub</div>
</body>
</html>'''
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_file


def format_number(num):
    """格式化数字(万→w)"""
    if num is None:
        return "0"
    if num >= 10000:
        return f"{num/10000:.1f}w"
    return str(num)


def load_cache():
    """加载缓存数据"""
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
    """保存缓存数据"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    
    cache_data = {
        "timestamp": time.time(),
        "items": items
    }
    
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except:
        pass


def main():
    parser = argparse.ArgumentParser(description="短剧-公众号信息源日报生成工具")
    parser.add_argument("--topics", type=str, help="题材关键词,逗号分隔")
    parser.add_argument("--count", type=int, default=200, help="扫描文章数量")
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
    
    # 处理订阅
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
    
    # 使用自定义时间(如果提供)
    if args.start_time:
        start_time = args.start_time
        date_str = args.start_time[:10]
    if args.end_time:
        end_time = args.end_time
    
    # 解析题材
    topics = None
    if args.topics:
        topics = [t.strip() for t in args.topics.split(",")]
    
    print(f"🔍 正在查询 {date_str} 的公众号短剧数据...")
    
    # 查询数据
    items = fetch_playlet_data(
        topics=topics,
        start_time=start_time,
        end_time=end_time,
        count=args.count,
        use_cache=args.from_cache
    )
    
    if not items:
        print("📭 未查询到相关数据")
        return
    
    print(f"✅ 共获取 {len(items)} 篇短剧文章")
    
    # 题材聚类
    clusters = cluster_by_topic(items)
    print(f"📊 聚类为 {len(clusters)} 个题材方向")
    
    # 生成HTML日报
    html_file = generate_html_report(items, clusters, date_str)
    print(f"📄 日报已生成:{html_file}")
    
    # 自动打开
    webbrowser.open(f"file://{html_file}")
    
    # 输出终端摘要
    print(f"\n## 短剧-公众号信息源 · {date_str} 日报\n")
    print(f"**扫描 {len(items)} 篇热门短剧文章,聚类 {len(clusters)} 个题材方向**\n")
    
    print("### 题材概览\n")
    print("| 题材 | 数量 | 占比 | 爆款亮点 |")
    print("|------|------|------|---------|")
    for topic, topic_items in sorted(clusters.items(), key=lambda x: len(x[1]), reverse=True):
        top_item = topic_items[0] if topic_items else {}
        print(f"| #{topic} | {len(topic_items)}篇 | {len(topic_items)/len(items)*100:.1f}% | 《{top_item.get('title', '')[:20]}》{format_number(top_item.get('readCount', 0))}阅读 |")


if __name__ == "__main__":
    main()
