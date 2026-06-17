#!/usr/bin/env python3
"""
AI快手信息源 — 每日热门内容聚类
====================================
每天扫描快手平台 AI 相关热门视频，自动聚类后生成 HTML 日报。

Usage:
    python3 daily_report.py
    python3 daily_report.py --keywords "AI教程,AI绘画,ChatGPT"
    python3 daily_report.py --subscribe
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import time

# Windows GBK 终端兼容：强制 stdout/stderr 使用 UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, quote

try:
    from urllib.request import Request, urlopen
    HAS_URLLIB = True
except ImportError:
    HAS_URLLIB = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ─── 配置 ─────────────────────────────────────────────────────────────────────────
API_URL = "https://redfox.hk/story/api/parseWork/queryKsAiMsgs/batch"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"
SOURCE = "AI快手信息源-GitHub"

DEFAULT_KEYWORDS = ["AI", "人工智能", "大模型", "GPT", "Agent", "AI绘画", "AI教程"]
DEFAULT_OUTPUT_DIR = Path.home() / "Downloads" / "QoderReports"
PAGE_SIZE = 200         # 每页获取200条

# 数据更新规则：每日15:00更新前一天的数据
DATA_UPDATE_HOUR = 15   # 数据更新时间（小时）
DATA_UPDATE_MINUTE = 0 # 数据更新时间（分钟）

PLIST_LABEL = "com.qoder.ks-ai-feed"
PLIST_DIR = Path.home() / "Library" / "LaunchAgents"

# ─── 终端颜色 ──────────────────────────────────────────────────────────────────────
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def info(msg):
    print(f"{GREEN}[✓]{RESET} {msg}")


def warn(msg):
    print(f"{YELLOW}[!]{RESET} {msg}")


def error(msg):
    print(f"{RED}[✗]{RESET} {msg}")


def step(msg):
    print(f"{CYAN}[→]{RESET} {msg}")


# ─── 数据可用性检查 ──────────────────────────────────────────────────────────────
def get_latest_available_date():
    """根据数据更新规则计算当前可查询的最新日期。
    
    规则：每日15:00更新前一天的数据。
    - 如果当前时间 >= 15:00，则昨天及之前的数据可用，最新可查日期为昨天
    - 如果当前时间 < 15:00，则前天及之前的数据可用，最新可查日期为前天
    """
    now = datetime.now()
    if now.hour >= DATA_UPDATE_HOUR:
        # 今日15:00后，昨天的数据已更新
        latest = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    else:
        # 今日15:00前，昨天的数据尚未更新，最新是前天
        latest = now.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=2)
    return latest.strftime("%Y-%m-%d")


def check_date_available(target_date_str):
    """检查目标日期是否已有数据可用。
    
    Returns:
        (is_available, latest_date_str) - 是否可用，最新可查日期
    """
    latest_date_str = get_latest_available_date()
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        latest_date = datetime.strptime(latest_date_str, "%Y-%m-%d")
    except ValueError:
        return False, latest_date_str
    
    return target_date <= latest_date, latest_date_str


def print_data_unavailable_notice(query_date, latest_date):
    """输出数据不可用提示文案（不自动获取数据，需用户确认）"""
    print(f"\n⚠️ **{query_date} 数据尚未更新**\n")
    print(f"数据更新规则：每日15:00更新前一天的数据")
    print(f"当前可查询的最新日期：{latest_date}\n")
    print(f"是否需要查询 {latest_date} 的数据？")


# ─── API Key 管理 ──────────────────────────────────────────────────────────────────
def get_api_key(cli_key=None):
    """Get API key: CLI arg > env var > config file."""
    if cli_key:
        return cli_key
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
    return ""


# ─── 数据获取 ──────────────────────────────────────────────────────────────────────
def fetch_batch(session, keywords, page_num, start_time=None, end_time=None):
    """批量获取多个关键词的单页视频数据"""
    payload = {
        "keywords": keywords,  # 传入关键词列表
        "pageNum": page_num,
        "pageSize": PAGE_SIZE,
        "source": SOURCE,
    }
    if start_time:
        payload["startTime"] = start_time
    if end_time:
        payload["endTime"] = end_time
    
    try:
        resp = session.post(API_URL, json=payload, timeout=30)  # 批量查询增加超时时间
        result = resp.json()
    except Exception as e:
        warn(f"批量请求失败 (page={page_num}): {e}")
        return []

    code = result.get("code")
    if code == 3108:
        warn("限频，等待 5s...")
        time.sleep(5)
        try:
            resp = session.post(API_URL, json=payload, timeout=30)
            result = resp.json()
            code = result.get("code")
        except Exception:
            return []

    if code not in (200, 2000):
        if code in (3106, 3107):
            error(f"API Key 错误 (code {code}): {result.get('msg', '')}")
        return []

    data = result.get("data", {})
    return data.get("list", [])


def fetch_articles(session, keywords, target_count, start_time=None, end_time=None):
    """批量分页获取所有关键词的数据,一次请求传入所有关键词"""
    articles = []
    seen_ids = set()

    # 一次性传入所有关键词进行批量查询
    page_num = 1
    total_fetched = 0
    
    while True:
        # 批量请求所有关键词
        page_articles = fetch_batch(session, keywords, page_num, start_time=start_time, end_time=end_time)
        
        if not page_articles:
            if page_num == 1:
                warn(f"所有关键词均暂无内容(当前仅搜索 AI 相关快手视频,更多内容请访问 redfox.hk)")
            break

        # 统计本次新增数量
        new_count = 0
        for article in page_articles:
            pid = article.get("photoId", "")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                articles.append(article)
                new_count += 1
        
        total_fetched += new_count
        
        # 输出进度
        if new_count > 0:
            print(f"  {CYAN}[→]{RESET} 第{page_num}页: 新增{new_count}条, 累计{len(articles)}条")

        # 本页无新数据或返回不足一页,说明已到底
        if new_count == 0 or len(page_articles) < PAGE_SIZE:
            break

        # 达到目标数量
        if len(articles) >= target_count:
            break

        page_num += 1

        # 安全上限:最多10页(2000条)
        if page_num > 10:
            break

    return articles


# ─── 自动聚类 ──────────────────────────────────────────────────────────────────────
STOP_WORDS = set("的了是在和与及或但对于从到被将把让给用有这那个也都还又不没"
                 "就才能会要可以怎么什么为什么怎样如何哪些多少一个一些这些那些"
                 "已经正在可能应该必须需要通过进行使用利用根据关于对于由于因为所以"
                 "虽然但是然而因此所以如果那么只要只有无论不管即使不仅而且")

# 过于宽泛的标签，聚类时跳过
GENERIC_TAGS = {"#AI", "#人工智能", "#ai", "AI", "人工智能", "#科技", "#技术",
                "#人工智能应用", "#智能", "科技", "技术"}


def extract_keywords(title):
    """从标题中提取中文关键词片段"""
    if not title:
        return []
    # 移除标点和特殊字符
    cleaned = re.sub(r'[^\u4e00-\u9fff\w]', ' ', title)
    # 提取 2-4 字中文片段
    segments = re.findall(r'[\u4e00-\u9fff]{2,4}', cleaned)
    # 过滤停用词
    keywords = [s for s in segments if not all(c in STOP_WORDS for c in s)]
    return keywords[:5]


def get_article_tags(article):
    """提取视频的所有有效标签（去除泛标签），优先 type 再 topic"""
    tags = []

    # type 字段通常更细致（如 #AI热点、#AI教程、#AI大模型）
    atype = (article.get("type") or "").strip()
    if atype:
        for t in re.split(r'[,，]+', atype):
            t = t.strip()
            if t and t not in GENERIC_TAGS:
                tags.append(t)

    # topic 字段作为补充（跳过泛标签）
    topic = (article.get("topic") or "").strip()
    if topic:
        for t in re.split(r'[,，\s]+', topic):
            t = t.strip()
            if t and t not in GENERIC_TAGS and t not in tags:
                tags.append(t)

    return tags


def cluster_articles(articles):
    """基于 type + topic 标签自动聚类，确保分类细致且至少 5 个"""
    # 第一步：为每个视频提取标签，按首个有效标签分组
    topic_groups = defaultdict(list)

    for article in articles:
        tags = get_article_tags(article)
        if tags:
            # 使用第一个非泛标签作为主分类
            topic_groups[tags[0]].append(article)
        else:
            topic_groups["其他"].append(article)

    # 第二步：如果大组过大（>20%文章），尝试拆分
    total = len(articles)
    split_threshold = max(total * 0.2, 25)
    groups_to_split = {}
    for topic, arts in list(topic_groups.items()):
        if len(arts) > split_threshold and topic != "其他":
            groups_to_split[topic] = arts

    for topic, arts in groups_to_split.items():
        del topic_groups[topic]
        # 用视频的第二标签进行二次拆分
        for article in arts:
            tags = get_article_tags(article)
            if len(tags) >= 2:
                topic_groups[tags[1]].append(article)
            else:
                topic_groups[topic].append(article)

    # 第三步：合并小组（< 3 篇）
    final_groups = {}
    small_articles = []

    for topic, arts in topic_groups.items():
        if len(arts) >= 3:
            final_groups[topic] = arts
        else:
            small_articles.extend(arts)

    # 小组视频尝试用标签匹配到已有大组
    still_orphan = []
    for article in small_articles:
        tags = get_article_tags(article)
        placed = False
        for tag in tags:
            if tag in final_groups:
                final_groups[tag].append(article)
                placed = True
                break
        if not placed:
            still_orphan.append(article)

    if still_orphan:
        if "其他" in final_groups:
            final_groups["其他"].extend(still_orphan)
        else:
            final_groups["其他"] = still_orphan

    # 第四步：对过大的组用标题关键词进一步拆分
    MAX_GROUP_SIZE = max(total * 0.3, 40)
    for _ in range(3):  # 最多拆 3 轮
        oversized = [(t, a) for t, a in final_groups.items() if len(a) > MAX_GROUP_SIZE]
        if not oversized:
            break
        for topic, arts in oversized:
            # 用标题中的高频关键词拆分
            kw_counter = Counter()
            article_kw_map = {}
            for article in arts:
                title = article.get("title", "")
                kws = extract_keywords(title)
                article_kw_map[id(article)] = kws
                for kw in kws:
                    kw_counter[kw] += 1
            # 找出频次够高的关键词作为子分类
            common_kws = [kw for kw, cnt in kw_counter.most_common(5)
                          if cnt >= 5 and kw not in topic
                          and f"#{kw}" not in GENERIC_TAGS
                          and kw not in ("人工智能", "智能", "模型", "技术", "应用")]
            if not common_kws:
                continue
            # 用第一个高频词拆出子组
            split_kw = common_kws[0]
            new_group = []
            remaining = []
            for article in arts:
                kws = article_kw_map.get(id(article), [])
                if split_kw in kws:
                    new_group.append(article)
                else:
                    remaining.append(article)
            if len(new_group) >= 5:
                final_groups[f"#{split_kw}"] = new_group
                final_groups[topic] = remaining

    # 第五步：确保至少 5 个分类（如果不够，对最大组继续拆分）
    _split_attempts = 0
    while len(final_groups) < 5 and final_groups and _split_attempts < 10:
        _split_attempts += 1
        largest_topic = max(final_groups, key=lambda k: len(final_groups[k]))
        largest_arts = final_groups[largest_topic]
        if len(largest_arts) < 6:
            break  # 最大组也太小了，无法再拆

        # 从最大组中按第二标签拆出子组
        sub_groups = defaultdict(list)
        remain = []
        for article in largest_arts:
            tags = get_article_tags(article)
            second_tag = None
            for t in tags:
                if t != largest_topic:
                    second_tag = t
                    break
            if second_tag:
                sub_groups[second_tag].append(article)
            else:
                remain.append(article)

        # 找出最大的子组拆出来
        if sub_groups:
            best_sub = max(sub_groups, key=lambda k: len(sub_groups[k]))
            # best_sub 不能与 largest_topic 同名，否则死循环
            if len(sub_groups[best_sub]) >= 3 and best_sub != largest_topic:
                final_groups[best_sub] = sub_groups[best_sub]
                # 更新原组
                new_arts = remain
                for k, v in sub_groups.items():
                    if k != best_sub:
                        new_arts.extend(v)
                final_groups[largest_topic] = new_arts
                continue
        break  # 无法继续拆分

    # 第六步：构建输出，按条数降序（过滤空分类）
    clusters = []
    for category, arts in sorted(final_groups.items(), key=lambda x: -len(x[1])):
        if not arts:  # 跳过空分类
            continue
        # 按阅读量排序取 top 5
        sorted_arts = sorted(arts, key=lambda a: (a.get("readCount") or 0), reverse=True)
        clusters.append({
            "category": category,
            "count": len(arts),
            "articles": sorted_arts[:5],
        })

    return clusters


# ─── AI 情报洞察分析 ────────────────────────────────────────────────────────────────
# 情报调查引擎配置（来自智能情报调查员 skill）
INVESTIGATION_ENGINES = {
    "Baidu": {"url": "https://www.baidu.com/s?wd={keyword}", "region": "cn", "strength": "中文生态覆盖最广"},
    "WeChat": {"url": "https://wx.sogou.com/weixin?type=2&query={keyword}", "region": "cn", "strength": "微信公众号文章"},
    "Toutiao": {"url": "https://so.toutiao.com/search?keyword={keyword}", "region": "cn", "strength": "自媒体/热点追踪"},
    "Google": {"url": "https://www.google.com/search?q={keyword}", "region": "global", "strength": "全球索引最全+高级操作符"},
    "DuckDuckGo": {"url": "https://duckduckgo.com/html/?q={keyword}", "region": "global", "strength": "无追踪+Bangs直达"},
    "Brave": {"url": "https://search.brave.com/search?q={keyword}", "region": "global", "strength": "独立索引+无偏见"},
    "Sogou": {"url": "https://sogou.com/web?query={keyword}", "region": "cn", "strength": "微信+知乎内容"},
    "Bing INT": {"url": "https://cn.bing.com/search?q={keyword}&ensearch=1", "region": "cn", "strength": "中文界面+国际结果"},
}

# 按调查场景推荐引擎组合
SCENARIO_ENGINES = {
    "产品竞品分析": ["Baidu", "Google", "WeChat", "DuckDuckGo"],
    "热点事件追踪": ["Baidu", "Toutiao", "Google", "WeChat"],
    "人物背景验证": ["Baidu", "Google", "DuckDuckGo"],
    "用户口碑收集": ["WeChat", "Toutiao", "DuckDuckGo", "Brave"],
    "技术趋势调查": ["DuckDuckGo", "Google", "Brave"],
    "市场数据验证": ["Google", "Baidu", "Bing INT"],
}

# 信源可信度分级
CREDIBILITY_LEVELS = {
    "A": "官方/政府/权威媒体",
    "B": "行业媒体/专业平台",
    "C": "社交媒体/自媒体",
    "D": "匿名/未验证来源",
}


def generate_intelligence_briefing(clusters, articles):
    """基于当日聚类结果生成AI情报洞察报告"""
    if not clusters:
        return None

    total = len(articles)

    # 1. 提取热度TOP话题
    top_topics = []
    for cluster in clusters[:5]:
        top_topics.append({
            "topic": cluster["category"],
            "count": cluster["count"],
            "ratio": round(cluster["count"] / total * 100, 1) if total > 0 else 0,
            "top_article": cluster["articles"][0] if cluster["articles"] else None,
        })

    # 2. 识别新兴起量话题（占比小但互动高）
    emerging_topics = []
    for cluster in clusters:
        if cluster["count"] < total * 0.1 and cluster["articles"]:
            avg_engagement = sum(
                (a.get("likeCount") or 0) + (a.get("commentCount") or 0)
                for a in cluster["articles"]
            ) / max(len(cluster["articles"]), 1)
            if avg_engagement > 1000:
                emerging_topics.append({
                    "topic": cluster["category"],
                    "count": cluster["count"],
                    "avg_engagement": int(avg_engagement),
                })

    # 3. 核心达人分析
    author_counter = Counter()
    author_articles = defaultdict(list)
    for article in articles:
        author = article.get("userName", "未知")
        author_counter[author] += 1
        author_articles[author].append(article)

    top_authors = []
    for author, count in author_counter.most_common(5):
        arts = author_articles[author]
        total_likes = sum(a.get("likeCount") or 0 for a in arts)
        reads_with_data = [a["readCount"] for a in arts if a.get("readCount") is not None]
        total_reads = sum(reads_with_data) if reads_with_data else None
        top_authors.append({
            "name": author,
            "article_count": count,
            "total_likes": total_likes,
            "total_reads": total_reads,
        })

    # 4. 为每个TOP话题生成推荐调查方向
    investigation_hints = []
    for topic_info in top_topics[:3]:
        topic_name = topic_info["topic"].lstrip("#")
        hints = []

        # 根据话题内容推荐调查场景
        if any(kw in topic_name for kw in ["大模型", "GPT", "ChatGPT", "大模型"]):
            hints.append({
                "scenario": "技术趋势调查",
                "engines": SCENARIO_ENGINES["技术趋势调查"],
                "keywords": [f"{topic_name} 最新进展", f"{topic_name} 技术对比", f"{topic_name} 开源项目"],
            })
            hints.append({
                "scenario": "产品竞品分析",
                "engines": SCENARIO_ENGINES["产品竞品分析"],
                "keywords": [f"{topic_name} 产品对比", f"{topic_name} 用户评价"],
            })
        elif any(kw in topic_name for kw in ["绘画", "创作", "动画"]):
            hints.append({
                "scenario": "用户口碑收集",
                "engines": SCENARIO_ENGINES["用户口碑收集"],
                "keywords": [f"{topic_name} 工具测评", f"{topic_name} 教程推荐", f"AI{topic_name} 最新工具"],
            })
        elif any(kw in topic_name for kw in ["教程", "教学"]):
            hints.append({
                "scenario": "技术趋势调查",
                "engines": SCENARIO_ENGINES["技术趋势调查"],
                "keywords": [f"AI{topic_name} 学习路线", f"{topic_name} 变现方法"],
            })
        else:
            hints.append({
                "scenario": "热点事件追踪",
                "engines": SCENARIO_ENGINES["热点事件追踪"],
                "keywords": [f"{topic_name} 最新动态", f"{topic_name} 行业趋势"],
            })

        investigation_hints.append({
            "topic": topic_info["topic"],
            "hints": hints,
        })

    # 5. 跨平台对比建议
    cross_platform_tips = []
    for topic_info in top_topics[:3]:
        topic_name = topic_info["topic"].lstrip("#")
        cross_platform_tips.append(
            f"「{topic_name}」— 建议同步关注抖音、B站、小红书同话题热度，"
            f"用 Baidu+WeChat+Toutiao 三引擎追踪国内全平台动态"
        )

    briefing = {
        "top_topics": top_topics,
        "emerging_topics": emerging_topics,
        "top_authors": top_authors,
        "investigation_hints": investigation_hints,
        "cross_platform_tips": cross_platform_tips,
    }

    return briefing


def print_intelligence_briefing(briefing):
    """在终端输出情报洞察"""
    if not briefing:
        return

    print(f"\n{BOLD}{'='*78}{RESET}")
    print(f"{BOLD}  AI情报洞察 · 深度调查指引{RESET}")
    print(f"{BOLD}{'='*78}{RESET}\n")

    # 新兴起量话题
    if briefing["emerging_topics"]:
        print(f"  {CYAN}{BOLD}【新兴起量信号】{RESET}")
        for topic in briefing["emerging_topics"]:
            print(f"    🔥 {topic['topic']} — 虽仅{topic['count']}条但均互动{topic['avg_engagement']}+，"
                  f"值得深挖")
        print()

    # 核心达人
    if briefing["top_authors"]:
        print(f"  {CYAN}{BOLD}【核心达人】{RESET}")
        for author in briefing["top_authors"]:
            reads_part = f", 总播{format_number(author['total_reads'])}" if author.get('total_reads') else ''
            print(f"    @{author['name']} — {author['article_count']}条作品, "
                  f"总赞{format_number(author['total_likes'])}{reads_part}")
        print()

    # 推荐调查方向
    print(f"  {CYAN}{BOLD}【推荐调查方向】{RESET}")
    for hint_group in briefing["investigation_hints"]:
        print(f"    ▸ {hint_group['topic']}")
        for hint in hint_group["hints"]:
            engines_str = " + ".join(hint["engines"])
            print(f"      {hint['scenario']}: {engines_str}")
            for kw in hint["keywords"][:2]:
                print(f"        → 搜索: {kw}")
    print()

    # 跨平台对比
    if briefing["cross_platform_tips"]:
        print(f"  {CYAN}{BOLD}【跨平台对比建议】{RESET}")
        for tip in briefing["cross_platform_tips"]:
            print(f"    • {tip}")
    print()



# ─── HTML 报告生成 ──────────────────────────────────────────────────────────────────
def compute_stats(articles):
    """计算统计数据"""
    total = len(articles)
    if total == 0:
        return {"total": 0, "avg_reads": None, "top_author": "-", "total_likes": 0}

    reads_with_data = [a["readCount"] for a in articles if a.get("readCount") is not None]
    avg_reads = sum(reads_with_data) // len(reads_with_data) if reads_with_data else None

    author_counter = Counter(a.get("userName", "未知") for a in articles)
    top_author = author_counter.most_common(1)[0][0] if author_counter else "-"

    total_likes = sum(a.get("likeCount") or 0 for a in articles)

    return {
        "total": total,
        "avg_reads": avg_reads,
        "top_author": top_author,
        "total_likes": total_likes,
    }


def format_number(n):
    """格式化数字: 1234 -> 1.2k"""
    if n is None:
        return "0"
    if n >= 10000:
        return f"{n/10000:.1f}w"
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


def print_article_table(clusters):
    """在终端打印分类视频表格"""
    print(f"\n{BOLD}{'='*78}{RESET}")
    print(f"{BOLD}  AI快手信息源 · 分类视频一览{RESET}")
    print(f"{BOLD}{'='*78}{RESET}\n")

    for i, cluster in enumerate(clusters, 1):
        category = cluster["category"]
        arts = cluster["articles"]

        # 分类标题
        print(f"  {CYAN}{BOLD}【{category}】{RESET} "
              f"共 {len(arts)} 条展示 / {cluster['count']} 条总计")

        # 表头
        header = (f"  {'序号':<4}{'标题':<36}{'作者':<14}"
                  f"{'播放':>8}{'点赞':>8}{'评论':>8}")
        print(f"  {YELLOW}{'─'*76}{RESET}")
        print(f"  {YELLOW}{header}{RESET}")
        print(f"  {YELLOW}{'─'*76}{RESET}")

        for j, article in enumerate(arts, 1):
            title = article.get("title", "无标题")
            author = article.get("userName", "-")
            reads = format_number(article.get("readCount")) if article.get("readCount") else "-"
            likes = format_number(article.get("likeCount"))
            comments = format_number(article.get("commentCount"))

            # 截断过长的标题和作者
            display_title = title[:34] + ".." if len(title) > 36 else title
            display_author = author[:12] + ".." if len(author) > 14 else author

            print(f"  {j:<4}{display_title:<36}{display_author:<14}"
                  f"{reads:>8}{likes:>8}{comments:>8}")

        print()  # 分类之间空行


def generate_category_cards(clusters):
    """生成分类卡片 HTML"""
    cards_html = ""
    for i, cluster in enumerate(clusters, 1):
        articles_html = ""
        for article in cluster["articles"]:
            title = article.get("title", "无标题")
            url = article.get("url") or ""
            if not url or url == "#":
                photo_id = article.get("photoId", "")
                if photo_id:
                    url = f"https://www.kuaishou.com/short-video/{photo_id}"
                else:
                    url = "#"
            author = article.get("userName", "")
            cover = article.get("coverUrl") or ""
            # 不兼容格式转换为 JPG：HEIF/HEIC、快手私有格式 kvif/kpg
            # URL 可能带 ?tag=... 查询参数，需要在 ? 前匹配后缀，而不是在字符串末尾
            cover = re.sub(r'\.(heif|heic|kvif|kpg)(?=[?#]|$)', '.jpg', cover, flags=re.IGNORECASE)
            cover = re.sub(r'/(heif|heic)/', '/jpg/', cover, flags=re.IGNORECASE)
            likes = format_number(article.get("likeCount"))
            reads_raw = article.get("readCount")
            comments = format_number(article.get("commentCount"))

            reads_metric = f'<span class="metric">&#x1f441; {format_number(reads_raw)}</span>' if reads_raw else ''
            articles_html += f'''
                <a href="{url}" target="_blank" class="article-item">
                    <div class="article-info">
                        <span class="article-title">{title}</span>
                        <div class="article-meta">
                            <span class="author">{author}</span>
                            <span class="metrics">
                                {reads_metric}
                                <span class="metric">&#x1f44d; {likes}</span>
                                <span class="metric">&#x1f4ac; {comments}</span>
                            </span>
                        </div>
                    </div>
                </a>'''

        cards_html += f'''
        <div class="category-card reveal">
            <div class="card-header">
                <span class="card-number">{i:02d}</span>
                <h3 class="card-category">{cluster["category"]}</h3>
                <span class="card-count">{cluster["count"]} 条</span>
            </div>
            <div class="card-body">{articles_html}
            </div>
        </div>'''

    return cards_html


def generate_intelligence_html(briefing):
    """生成情报洞察板块 HTML"""
    if not briefing:
        return ""

    # 热度TOP话题
    topics_html = ""
    for i, topic in enumerate(briefing["top_topics"], 1):
        top_art = topic.get("top_article")
        top_title = (top_art.get("title", "-")[:50] if top_art else "-")
        top_reads_raw = top_art.get("readCount") if top_art else None
        top_reads_metric = f'{format_number(top_reads_raw)} 播放' if top_reads_raw else ''
        topics_html += f'''
                <div class="intel-rank-item">
                    <span class="intel-rank-num">{i}</span>
                    <div class="intel-rank-info">
                        <span class="intel-rank-topic">{topic['topic']}</span>
                        <span class="intel-rank-detail">占比 {topic['ratio']}% · {topic['count']}条 · 头部: {top_title}</span>
                    </div>
                    <span class="intel-rank-metric">{top_reads_metric}</span>
                </div>'''

    # 新兴起量话题
    emerging_html = ""
    for topic in briefing.get("emerging_topics", []):
        emerging_html += f'''
                <div class="intel-emerging-item">
                    <span class="intel-emerging-badge">起量信号</span>
                    <span class="intel-emerging-topic">{topic['topic']}</span>
                    <span class="intel-emerging-detail">{topic['count']}条 · 均互动{topic['avg_engagement']}+</span>
                </div>'''

    emerging_section = ""
    if emerging_html:
        emerging_section = f'''
        <div class="intel-subsection">
            <h4 class="intel-subtitle">新兴起量信号</h4>
            <div class="intel-emerging-list">{emerging_html}
            </div>
        </div>'''

    # 核心达人
    authors_html = ""
    for author in briefing.get("top_authors", []):
        reads_part = f' · 总播{format_number(author["total_reads"])}' if author.get("total_reads") else ''
        authors_html += f'''
                <div class="intel-author-item">
                    <span class="intel-author-name">@{author['name']}</span>
                    <span class="intel-author-stats">{author['article_count']}条 · 总赞{format_number(author['total_likes'])}{reads_part}</span>
                </div>'''

    authors_section = ""
    if authors_html:
        authors_section = f'''
        <div class="intel-subsection">
            <h4 class="intel-subtitle">核心达人</h4>
            <div class="intel-author-list">{authors_html}
            </div>
        </div>'''

    # 推荐调查方向
    hints_html = ""
    for hint_group in briefing.get("investigation_hints", []):
        hint_items = ""
        for hint in hint_group["hints"]:
            engines_str = " + ".join(hint["engines"])
            kw_list = " | ".join(hint["keywords"][:2])
            hint_items += f'''
                    <div class="intel-hint-item">
                        <span class="intel-hint-scenario">{hint['scenario']}</span>
                        <span class="intel-hint-engines">{engines_str}</span>
                        <span class="intel-hint-kw">{kw_list}</span>
                    </div>'''

        hints_html += f'''
                <div class="intel-hint-group">
                    <span class="intel-hint-topic">{hint_group['topic']}</span>
                    <div class="intel-hint-items">{hint_items}
                    </div>
                </div>'''

    # 跨平台对比
    cross_html = ""
    for tip in briefing.get("cross_platform_tips", []):
        cross_html += f'<div class="intel-cross-tip">{tip}</div>'

    cross_section = ""
    if cross_html:
        cross_section = f'''
        <div class="intel-subsection">
            <h4 class="intel-subtitle">跨平台对比建议</h4>
            <div class="intel-cross-list">{cross_html}
            </div>
        </div>'''

    # 情报调查引擎表
    engine_rows = ""
    for name, info in INVESTIGATION_ENGINES.items():
        engine_rows += f'''
                    <tr>
                        <td class="intel-engine-name">{name}</td>
                        <td class="intel-engine-region">{info['region'].upper()}</td>
                        <td class="intel-engine-strength">{info['strength']}</td>
                    </tr>'''

    credibility_rows = ""
    for level, desc in CREDIBILITY_LEVELS.items():
        credibility_rows += f'''
                    <tr>
                        <td class="intel-cred-level">{level}级</td>
                        <td>{desc}</td>
                    </tr>'''

    html = f'''
    <div class="intelligence-section reveal">
        <div class="intel-header">
            <h2 class="intel-title">AI情报洞察</h2>
            <span class="intel-subtitle-badge">基于智能情报调查员 · 多源交叉验证</span>
        </div>

        <div class="intel-body">
            <div class="intel-subsection">
                <h4 class="intel-subtitle">热度TOP话题</h4>
                <div class="intel-rank-list">{topics_html}
                </div>
            </div>

            {emerging_section}

            {authors_section}

            <div class="intel-subsection">
                <h4 class="intel-subtitle">推荐调查方向</h4>
                <div class="intel-hints">{hints_html}
                </div>
            </div>

            {cross_section}

            <div class="intel-subsection">
                <h4 class="intel-subtitle">调查引擎一览</h4>
                <div class="intel-engine-table-wrap">
                    <table class="intel-engine-table">
                        <thead><tr><th>引擎</th><th>区域</th><th>优势</th></tr></thead>
                        <tbody>{engine_rows}
                        </tbody>
                    </table>
                </div>
                <div class="intel-cred-table-wrap">
                    <table class="intel-cred-table">
                        <thead><tr><th>信源级别</th><th>类型</th></tr></thead>
                        <tbody>{credibility_rows}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>'''

    return html


def generate_report(clusters, articles, date_str, api_key=None, briefing=None):
    """生成完整 HTML 报告"""
    stats = compute_stats(articles)
    topic_count = len(clusters)

    # 尝试从模板文件读取
    template_path = Path(__file__).parent / "report_template.html"
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
    else:
        warn("模板文件未找到，使用内置模板")
        template = get_fallback_template()

    # 生成日期显示
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        date_cn = f"{dt.year}年{dt.month}月{dt.day}日 星期{weekdays[dt.weekday()]}"
    except ValueError:
        date_cn = date_str

    category_cards = generate_category_cards(clusters)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 生成情报洞察 HTML
    intelligence_html = generate_intelligence_html(briefing) if briefing else ""

    html = template
    html = html.replace("{{DATE}}", date_str)
    html = html.replace("{{DATE_CN}}", date_cn)
    html = html.replace("{{TOTAL_COUNT}}", str(stats["total"]))
    html = html.replace("{{TOPIC_COUNT}}", str(topic_count))
    html = html.replace("{{TOP_AUTHOR}}", stats["top_author"])
    html = html.replace("{{AVG_READS}}", format_number(stats["avg_reads"]) if stats["avg_reads"] is not None else "-")
    html = html.replace("{{TOTAL_LIKES}}", format_number(stats["total_likes"]))
    html = html.replace("{{CATEGORY_CARDS}}", category_cards)
    html = html.replace("{{INTELLIGENCE_SECTION}}", intelligence_html)
    html = html.replace("{{TIMESTAMP}}", timestamp)
    html = html.replace("{{API_KEY}}", api_key or "")
    html = html.replace("{{SOURCE}}", SOURCE)

    return html


def get_fallback_template():
    """内置最小 HTML 模板（当模板文件缺失时使用）"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI快手信息源 - {{DATE}}</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, sans-serif; background: #1a1a1a; color: #e8e4df; padding: 2rem; }
.header { text-align: center; padding: 2rem 0; }
.header h1 { font-size: 2rem; color: #FF4906; }
.header p { color: #9a9590; margin-top: 0.5rem; }
.stats { display: flex; justify-content: center; gap: 2rem; padding: 1rem; margin: 1rem 0; }
.stat-item { text-align: center; }
.stat-value { font-size: 1.5rem; font-weight: bold; color: #FF4906; }
.stat-label { font-size: 0.8rem; color: #9a9590; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 1.5rem; max-width: 1200px; margin: 2rem auto; }
.category-card { background: #2d2d2d; border-radius: 12px; padding: 1.5rem; }
.card-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem; padding-bottom: 0.8rem; border-bottom: 1px solid #3d3d3d; }
.card-number { font-size: 1.5rem; font-weight: bold; color: #FF4906; }
.card-category { flex: 1; font-size: 1.1rem; }
.card-count { color: #9a9590; font-size: 0.9rem; }
.article-item { padding: 0.6rem 0; border-bottom: 1px solid #3d3d3d; display: block; text-decoration: none; color: inherit; cursor: pointer; }
.article-item:hover { background: #333; }
.article-item:hover .article-title { color: #FF4906; }
.article-item:last-child { border-bottom: none; }
.article-info { flex: 1; min-width: 0; }
.article-title { color: #e8e4df; font-size: 0.9rem; line-height: 1.4; display: block; transition: color 0.2s; }
.article-meta { display: flex; justify-content: space-between; margin-top: 0.3rem; font-size: 0.75rem; color: #9a9590; }
.metrics { display: flex; gap: 0.8rem; }
.footer { text-align: center; padding: 2rem; color: #666; font-size: 0.8rem; }
</style>
</head>
<body>
<div class="header">
    <h1>AI快手信息源</h1>
    <p>{{DATE_CN}} | 共 {{TOTAL_COUNT}} 条热门视频</p>
</div>
<div class="stats">
    <div class="stat-item"><div class="stat-value">{{TOPIC_COUNT}}</div><div class="stat-label">分类</div></div>
    <div class="stat-item"><div class="stat-value">{{TOTAL_COUNT}}</div><div class="stat-label">视频</div></div>
    <div class="stat-item"><div class="stat-value">{{AVG_READS}}</div><div class="stat-label">平均播放</div></div>
    <div class="stat-item"><div class="stat-value">{{TOTAL_LIKES}}</div><div class="stat-label">总点赞</div></div>
</div>
<div class="cards">{{CATEGORY_CARDS}}</div>
<div class="footer">Generated at {{TIMESTAMP}} by AI快手信息源 Skill</div>
</body>
</html>'''


# ─── 订阅机制 ──────────────────────────────────────────────────────────────────────
def install_subscription():
    """安装定时任务，每天自动生成日报"""
    if sys.platform == "darwin":
        PLIST_DIR.mkdir(parents=True, exist_ok=True)
        plist_path = PLIST_DIR / f"{PLIST_LABEL}.plist"

        script_path = os.path.abspath(__file__)
        log_path = str(Path.home() / "Library" / "Logs" / "qoder-ks-ai-hot-articles.log")

        # 传递 API Key 环境变量
        env_section = ""
        api_key = os.environ.get(ENV_KEY)
        if api_key:
            env_section = f"""
        <key>EnvironmentVariables</key>
        <dict>
            <key>{ENV_KEY}</key>
            <string>{api_key}</string>
        </dict>"""

        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{script_path}</string>
        <string>--no-open</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{log_path}</string>
    <key>StandardErrorPath</key>
    <string>{log_path}</string>
    <key>RunAtLoad</key>
    <false/>{env_section}
</dict>
</plist>'''

        plist_path.write_text(plist_content, encoding="utf-8")

        try:
            subprocess.run(["launchctl", "load", str(plist_path)], check=True, capture_output=True)
            info("订阅成功! 每天 09:00 自动生成快手爆款日报")
            info(f"日报目录: ~/Downloads/QoderReports/")
            info(f"日志: {log_path}")
            return True
        except subprocess.CalledProcessError as e:
            error(f"订阅安装失败: {e.stderr.decode()}")
            return False
    else:
        # Linux / Windows: 使用 crontab
        script_path = os.path.abspath(__file__)
        cron_line = f"0 9 * * * /usr/bin/python3 {script_path} --no-open"
        try:
            subprocess.run(
                f'(crontab -l 2>/dev/null; echo "{cron_line}") | crontab -',
                shell=True, check=True, capture_output=True
            )
            info("订阅成功! 每天 09:00 自动生成快手爆款日报 (crontab)")
            info(f"日报目录: ~/Downloads/QoderReports/")
            return True
        except subprocess.CalledProcessError:
            warn("自动配置 crontab 失败，请手动添加:")
            print(f"  {cron_line}")
            return False


def remove_subscription():
    """卸载定时任务"""
    if sys.platform == "darwin":
        plist_path = PLIST_DIR / f"{PLIST_LABEL}.plist"
        if not plist_path.exists():
            warn("未找到订阅配置，无需取消")
            return False
        try:
            subprocess.run(["launchctl", "unload", str(plist_path)], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            pass
        plist_path.unlink(missing_ok=True)
        info("已取消订阅，定时任务已移除")
        return True
    else:
        script_path = os.path.abspath(__file__)
        try:
            subprocess.run(
                f'crontab -l 2>/dev/null | grep -v "{script_path}" | crontab -',
                shell=True, check=True, capture_output=True
            )
            info("已取消订阅，crontab 任务已移除")
            return True
        except subprocess.CalledProcessError:
            warn("自动移除 crontab 失败，请手动执行: crontab -e")
            return False


# ─── API 代理 HTTP 服务 ─────────────────────────────────────────────────────────────
class ProxyHTTPHandler(SimpleHTTPRequestHandler):
    """静态文件服务 + /api/search 代理到 redfox.hk"""
    api_key = ""  # 将由 start_server 调用旹覆盖
    search_url = API_URL

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/search":
            self._handle_search(parsed)
        elif parsed.path == "/api/img":
            self._handle_img_proxy(parsed)
        else:
            super().do_GET()

    def _handle_img_proxy(self, parsed):
        """代理图片请求，绕过防盗链"""
        params = parse_qs(parsed.query)
        url = params.get("url", [""])[0]

        if not url:
            self.send_error(400, "missing url")
            return

        try:
            req = Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.kuaishou.com/",
            })
            resp = urlopen(req, timeout=10)
            content_type = resp.headers.get("Content-Type", "image/jpeg")
            data = resp.read()

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "public, max-age=86400")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(502, f"proxy error: {e}")

    def _handle_search(self, parsed):
        params = parse_qs(parsed.query)
        keyword = params.get("keyword", [""])[0]

        if not keyword:
            self._send_json({"code": -1, "msg": "missing keyword"})
            return

        payload = {
            "keyword": keyword,
            "pageNum": 1,
            "pageSize": 20,
            "source": SOURCE,
        }
        try:
            resp = requests.post(
                self.search_url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-API-KEY": self.api_key,
                },
                timeout=10,
            )
            self._send_json(resp.json())
        except Exception as e:
            self._send_json({"code": -1, "msg": str(e)})

    def _send_json(self, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass  # 静默日志


def start_server(output_dir, api_key, port=8766, latest_filename=None):
    """启动内置 HTTP 服务（静态文件 + API 代理），根路径自动重定向到最新日报"""
    import threading

    class _RedirectHandler(ProxyHTTPHandler):
        _latest = latest_filename

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path in ("/", "") and self._latest:
                self.send_response(302)
                self.send_header("Location", f"/{self._latest}")
                self.end_headers()
            else:
                super().do_GET()

    _RedirectHandler.api_key = api_key or ""
    os.chdir(str(output_dir))
    server = HTTPServer(("127.0.0.1", port), _RedirectHandler)
    t = threading.Thread(target=server.serve_forever, daemon=False)
    t.start()
    info(f"本地服务已启动: http://127.0.0.1:{port}")
    return server


# ─── 主流程 ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="AI快手信息源 — 每日热门内容聚类日报",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 daily_report.py
  python3 daily_report.py --keywords "AI教程,AI绘画,ChatGPT"
  python3 daily_report.py --subscribe
  python3 daily_report.py --unsubscribe
        """,
    )
    parser.add_argument("--keywords", default=",".join(DEFAULT_KEYWORDS),
                        help="搜索关键词，逗号分隔 (默认: AI,人工智能,大模型,GPT,Agent,AI绘画,AI教程)")
    parser.add_argument("--count", type=int, default=50, help="目标视频数 (默认: 50)")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="指定日期 YYYY-MM-DD 或日期范围 YYYY-MM-DD~YYYY-MM-DD (默认: 今天)")
    parser.add_argument("--output-dir", help=f"输出目录 (默认: ~/Downloads/QoderReports)")
    parser.add_argument("--api-key", help="API Key (不传则读取环境变量或配置文件)")
    parser.add_argument("--subscribe", action="store_true", help="安装每日定时任务 (09:00)")
    parser.add_argument("--unsubscribe", action="store_true", help="卸载定时任务")
    parser.add_argument("--no-open", action="store_true", help="不自动打开浏览器")

    args = parser.parse_args()

    # ── Banner ──
    banner = f"""{CYAN}{BOLD}
  ╔══════════════════════════════════════╗
  ║     AI快手信息源 · 日报生成          ║
  ║     每日热门内容聚类 · 爆款一网打尽   ║
  ╚══════════════════════════════════════╝{RESET}
"""
    print(banner)

    # ── 订阅/取消 ──
    if args.subscribe:
        install_subscription()
        return

    if args.unsubscribe:
        remove_subscription()
        return

    # ── 检查依赖 ──
    if not HAS_REQUESTS:
        error("缺少 requests 库，请安装: pip3 install requests")
        sys.exit(1)

    # ── API Key ──
    api_key = get_api_key(cli_key=args.api_key)
    if not api_key:
        error("未配置 API Key，请通过以下方式之一提供：")
        print(f"  1. 环境变量: export {ENV_KEY}=ak_你的密鑰")
        print(f"  2. 命令行参数: --api-key ak_你的密鑰")
        print(f"  3. 配置文件: echo '{{\"api_key\":\"ak_你的密鑰\"}}' > ~/.qoder/apis/redfox.json")
        sys.exit(1)
    # ── Session ──
    session = requests.Session()
    session.verify = True
    session.headers.update({
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    })

    # ── 日期范围推算 ──
    date_val = args.date
    if "~" in date_val:
        # 日期范围：2026-06-01~2026-06-11
        parts = date_val.split("~", 1)
        start_date = parts[0].strip()
        end_date = parts[1].strip()
    else:
        # 单日
        start_date = end_date = date_val.strip()

    try:
        dt_start = datetime.strptime(start_date, "%Y-%m-%d")
        dt_end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        error(f"日期格式错误，请使用 YYYY-MM-DD 或 YYYY-MM-DD~YYYY-MM-DD：{date_val}")
        sys.exit(1)

    # 开始时间：start_date 的0点（本地时间，字符串格式）
    start_time_str = dt_start.strftime("%Y-%m-%d 00:00:00")
    # 结束时间：end_date 当天23:59:59
    end_time_str = dt_end.strftime("%Y-%m-%d 23:59:59")

    # 日报展示日期（单日用单日，范围用范围）
    display_date = date_val if "~" in date_val else start_date

    # ── 数据可用性检查 ──
    # 检查结束日期是否已有数据（日期范围时检查结束日期，单日时检查该日期）
    is_available, latest_date = check_date_available(end_date)
    if not is_available:
        print_data_unavailable_notice(end_date, latest_date)
        sys.exit(0)

    # ── 获取视频 ──
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    step(f"扫描热门内容，关键词: {keywords}")
    step(f"目标: {args.count} 条, 日期: {display_date}")
    step(f"时间范围: {start_time_str} ~ {end_time_str} (本地时间)")
    print()

    articles = fetch_articles(session, keywords, args.count, start_time=start_time_str, end_time=end_time_str)

    if not articles:
        error("未获取到任何视频")
        sys.exit(1)

    info(f"扫描完成: {len(articles)} 条热门视频")

    # ── 自动聚类 ──
    step("正在自动聚类...")
    clusters = cluster_articles(articles)
    info(f"聚类完成: 发现 {len(clusters)} 个分类")
    for c in clusters[:10]:
        print(f"    {c['category']}: {c['count']} 条")

    # ── 终端表格展示 ──
    print_article_table(clusters)

    # ── AI情报洞察 ──
    step("正在生成AI情报洞察...")
    briefing = generate_intelligence_briefing(clusters, articles)
    if briefing:
        info(f"情报洞察完成: {len(briefing['investigation_hints'])}个推荐调查方向")
        print_intelligence_briefing(briefing)


    # ── 生成报告 ──
    step("生成 HTML 日报...")
    html_content = generate_report(clusters, articles, display_date, api_key=api_key, briefing=briefing)

    # ── 保存文件 ──
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%H%M%S")
    filename = f"AI快手日报_{display_date.replace('~', '_')}_{ts}.html"
    output_path = output_dir / filename

    output_path.write_text(html_content, encoding="utf-8")
    info(f"日报已生成: {output_path}")

    # ── 始终启动内置预览服务 ──
    server = start_server(output_dir, api_key, latest_filename=filename)
    preview_url = f"http://127.0.0.1:8766/{filename}"
    info(f"预览地址: {preview_url}")

    # ── 打开系统浏览器（--no-open 时跳过）──
    if not args.no_open:
        if sys.platform == "darwin":
            subprocess.run(["open", preview_url], check=False)
        elif sys.platform == "win32":
            os.startfile(preview_url)
        elif sys.platform == "linux":
            subprocess.run(["xdg-open", preview_url], check=False)
        info(f"浏览器已打开: {preview_url}")

    # ── 结构化摘要(严格对齐SKILL.md固定输出模式) ──
    print(f"\n{GREEN}{BOLD}✓ 完成!{RESET}")
    
    # 标题
    print(f"\n{BOLD}## AI快手信息源 · {display_date} 日报{RESET}")
    print(f"\n**扫描 {len(articles)} 条热门视频,聚类 {len(clusters)} 个分类**")
    print(f"\n---")
    
    # 分类概览表
    total = len(articles)
    print(f"\n{BOLD}### 分类概览{RESET}")
    print(f"\n| 分类 | 数量 | 占比 | 亮点 |")
    print(f"|------|------|------|------|")
    for c in clusters:
        ratio = f"{c['count']/total*100:.1f}%" if total > 0 else "0%"
        # 亮点:头部视频标题截断 + 点赞
        highlight = "暂无"
        if c["articles"]:
            top = c["articles"][0]
            title = (top.get("title") or "无标题")[:20]
            likes = format_number(top.get("likeCount") or 0)
            highlight = f"{title} {likes}赞"
        print(f"| {c['category']} | {c['count']}条 | {ratio} | {highlight} |")
    
    print(f"\n---")
    
    # AI情报洞察报告
    if briefing:
        print(f"\n{BOLD}### AI情报洞察报告{RESET}")
    
        # 一、新兴起量信号
        print(f"\n**一、新兴起量信号**")
        if briefing["emerging_topics"]:
            for topic in briefing["emerging_topics"]:
                print(f"\n- 🔥 **{topic['topic']}** — 仅{topic['count']}条但均互动{topic['avg_engagement']}+,")
        else:
            print(f"\n暂无")
    
        # 二、核心达人
        print(f"\n**二、核心达人**")
        if briefing["top_authors"]:
            print(f"\n| 达人 | 作品数 | 总赞 | 亮点 |")
            print(f"|------|--------|------|------|")
            for author in briefing["top_authors"][:5]:
                name = f"@{author['name']}"
                count = f"{author['article_count']}条"
                total_likes = format_number(author['total_likes'])
                highlight = f"总播{format_number(author['total_reads'])}" if author.get('total_reads') else '-'
                print(f"| {name} | {count} | {total_likes} | {highlight} |")
        else:
            print(f"\n暂无")
    
        # 三、推荐调查方向
        print(f"\n**三、推荐调查方向**")
        if briefing["investigation_hints"]:
            print(f"\n| 话题 | 调查场景 | 推荐引擎 | 搜索关键词 |")
            print(f"|------|---------|---------|-----------|")
            for hint_group in briefing["investigation_hints"]:
                topic_name = hint_group['topic']
                for hint in hint_group["hints"][:2]:  # 每个话题最多展示2个场景
                    engines_str = " + ".join(hint["engines"])
                    keywords_str = " / ".join(hint["keywords"][:2])
                    print(f"| {topic_name} | {hint['scenario']} | {engines_str} | {keywords_str} |")
        else:
            print(f"\n暂无")
    
        # 四、跨平台对比建议
        print(f"\n**四、跨平台对比建议**")
        if briefing["cross_platform_tips"]:
            for tip in briefing["cross_platform_tips"]:
                print(f"\n- {tip}")
        else:
            print(f"\n暂无")
    
        print(f"\n---")
    
    # 日报地址
    print(f"\n**日报地址**:{output_path}")
    if not args.no_open:
        print(f"  搜索功能: 已就绪（通过内置 API 代理）")
        print(f"  {YELLOW}提示：关闭终端后服务自动停止，HTML 文件可随时离线查阅{RESET}")


if __name__ == "__main__":
    main()
