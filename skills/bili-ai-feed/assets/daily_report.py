#!/usr/bin/env python3
"""
B站AI信息源 — 每日热门内容聚类
====================================
每天扫描B站平台 AI 相关热门视频，自动聚类后生成 HTML 日报。

Usage:
    python3 daily_report.py
    python3 daily_report.py --keywords "AI教程,AI绘画,ChatGPT"
    python3 daily_report.py --subscribe
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ─── 配置 ─────────────────────────────────────────────────────────────────────────
API_URL = "https://redfox.hk/story/api/parseWork/queryBiliAiMsgs"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"
PUBLIC_API_KEY = "ak_1e449a28ae344cd1b7aa14ca481de8bb"
SOURCE = "B站AI信息源-GitHub"

DEFAULT_KEYWORDS = ["AI", "人工智能", "大模型", "GPT", "Agent", "AI绘画", "AI教程"]
DEFAULT_OUTPUT_DIR = Path.home() / "Downloads" / "QoderReports"
PAGE_SIZE = 200

PLIST_LABEL = "com.qoder.bili-ai-feed"
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


# ─── API Key 管理 ──────────────────────────────────────────────────────────────────
def _read_key_from_shell_configs():
    """从常见 shell 配置文件中读取 REDFOX_API_KEY 的值。"""
    shell_configs = [
        Path.home() / ".zshrc",
        Path.home() / ".bashrc",
        Path.home() / ".bash_profile",
        Path.home() / ".profile",
    ]
    pattern = re.compile(
        r'^\s*export\s+' + re.escape(ENV_KEY) + r'\s*=\s*["\']?([^"\' \n]+)["\']?',
        re.MULTILINE,
    )
    for cfg in shell_configs:
        if not cfg.exists():
            continue
        try:
            content = cfg.read_text(encoding="utf-8", errors="ignore")
            m = pattern.search(content)
            if m:
                return m.group(1).strip()
        except OSError:
            pass
    return None


def get_api_key(cli_key=None):
    """Get API key: CLI arg > env var > shell config > config file > prompt user."""
    if cli_key:
        return cli_key

    # 1. 环境变量
    env_key = os.environ.get(ENV_KEY)
    if env_key:
        return env_key

    # 2. shell 配置文件（~/.zshrc / ~/.bashrc 等）
    shell_key = _read_key_from_shell_configs()
    if shell_key:
        return shell_key

    # 3. Qoder 配置文件
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text())
            key = data.get("api_key")
            if key:
                return key
        except (json.JSONDecodeError, OSError):
            pass

    # 4. 未找到个人 Key，提示用户配置
    warn(f"未检测到 {ENV_KEY}，当前使用内置公共 Key（约 10000 次免费额度）。")
    warn("额度用完后请配置个人 API Key：")
    if sys.platform == "win32":
        print(f"  Windows PowerShell: [Environment]::SetEnvironmentVariable('{ENV_KEY}', 'ak_你的密钥', 'User')")
    else:
        print(f"  macOS/Linux (zsh):  echo 'export {ENV_KEY}=ak_你的密钥' >> ~/.zshrc && source ~/.zshrc")
        print(f"  macOS/Linux (bash): echo 'export {ENV_KEY}=ak_你的密钥' >> ~/.bashrc && source ~/.bashrc")
    print(f"  免费注册获取 Key: https://redfox.hk/login")
    print()
    return PUBLIC_API_KEY


# ─── 数据获取 ──────────────────────────────────────────────────────────────────────
def fetch_batch(session, keyword, start_time=None, end_time=None):
    """一次性获取单个关键词的全部视频数据"""
    payload = {
        "keyword": keyword,
        "pageNum": 1,
        "pageSize": PAGE_SIZE,
        "source": SOURCE,
    }
    if start_time:
        payload["startTime"] = start_time
    if end_time:
        payload["endTime"] = end_time
    try:
        resp = session.post(API_URL, json=payload, timeout=30)
        result = resp.json()
    except Exception as e:
        warn(f"请求失败 (keyword={keyword}): {e}")
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
    """多关键词一次性抓取，去重后返回视频列表"""
    articles = []
    seen_ids = set()

    for kw in keywords:
        batch = fetch_batch(session, kw, start_time=start_time, end_time=end_time)
        if not batch:
            warn(f"关键词 \"{kw}\" 暂无内容（当前仅搜索 AI 相关B站视频，更多内容请访问 redfox.hk）")
            continue

        new_count = 0
        for article in batch:
            pid = article.get("photoId", "")
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                # B站API不返回url，用photoId(BV号)拼接视频链接
                if not article.get("url") and pid:
                    article["url"] = f"https://www.bilibili.com/video/{pid}"
                articles.append(article)
                new_count += 1

        print(f"  {CYAN}[→]{RESET} 扫描: {kw} 新增{new_count}条, 累计{len(articles)}条")

        if len(articles) >= target_count:
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
    while len(final_groups) < 5 and final_groups:
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
            if len(sub_groups[best_sub]) >= 3:
                final_groups[best_sub] = sub_groups[best_sub]
                # 更新原组
                new_arts = remain
                for k, v in sub_groups.items():
                    if k != best_sub:
                        new_arts.extend(v)
                final_groups[largest_topic] = new_arts
                continue
        break  # 无法继续拆分

    # 第六步：构建输出，按条数降序
    clusters = []
    for category, arts in sorted(final_groups.items(), key=lambda x: -len(x[1])):
        # 按点赞量排序取 top 5
        sorted_arts = sorted(arts, key=lambda a: (a.get("likeCount") or 0), reverse=True)
        clusters.append({
            "category": category,
            "count": len(arts),
            "articles": sorted_arts[:5],
        })

    return clusters


# ─── AI 情报调查分析 ────────────────────────────────────────────────────────────────
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


# 按调查模式匹配
TOPIC_MODE_MAP = {
    "大模型": ("竞品情报调查", "产品竞品分析"),
    "GPT": ("竞品情报调查", "产品竞品分析"),
    "ChatGPT": ("竞品情报调查", "产品竞品分析"),
    "Agent": ("竞品情报调查", "技术趋势调查"),
    "绘画": ("竞品情报调查", "用户口碑收集"),
    "创作": ("舆情事件调查", "用户口碑收集"),
    "动画": ("竞品情报调查", "用户口碑收集"),
    "教程": ("技术趋势调查", "技术趋势调查"),
    "教学": ("技术趋势调查", "技术趋势调查"),
    "Prompt": ("技术趋势调查", "产品竞品分析"),
}


def _match_mode(topic_name):
    """根据话题名匹配调查模式"""
    for kw, (mode, scenario) in TOPIC_MODE_MAP.items():
        if kw in topic_name:
            return mode, scenario
    return "舆情事件调查", "热点事件追踪"


def _derive_findings(cluster, articles, scenario):
    """从视频数据中提取调查发现"""
    findings = []
    arts = cluster["articles"]

    # 头部内容发现
    if arts:
        top = arts[0]
        title = top.get("title", "无标题")[:40]
        likes = format_number(top.get("likeCount") or 0)
        comments = format_number(top.get("commentCount") or 0)
        findings.append({
            "dimension": "头部内容",
            "discovery": f"{title} — {likes}赞 {comments}评",
            "source": "B站视频数据",
            "credibility": "B",
        })

    # 用户关注方向
    title_kw = Counter()
    for a in arts:
        title = a.get("title", "")
        for seg in re.findall(r'[\u4e00-\u9fff]{2,4}', title):
            if seg not in STOP_WORDS and len(seg) >= 2:
                title_kw[seg] += 1
    if title_kw:
        top_kws = "、".join(kw for kw, _ in title_kw.most_common(3))
        findings.append({
            "dimension": "用户关注",
            "discovery": f"高频关键词：{top_kws}",
            "source": "标题关键词分析",
            "credibility": "C",
        })

    # 互动特征
    total_likes = sum(a.get("likeCount") or 0 for a in arts)
    total_comments = sum(a.get("commentCount") or 0 for a in arts)
    if total_likes > 0:
        comment_ratio = f"{total_comments / total_likes * 100:.1f}%" if total_likes else "0%"
        findings.append({
            "dimension": "互动特征",
            "discovery": f"总赞{format_number(total_likes)}，评论率{comment_ratio}，"
                        + ("讨论活跃" if total_comments / max(total_likes, 1) > 0.15 else "以点赞为主"),
            "source": "互动数据分析",
            "credibility": "B",
        })

    # 核心作者
    author_counter = Counter(a.get("userName", "") for a in arts if a.get("userName"))
    if author_counter:
        top_author = author_counter.most_common(1)[0]
        findings.append({
            "dimension": "核心作者",
            "discovery": f"@{top_author[0]} 贡献{top_author[1]}条作品",
            "source": "作者统计",
            "credibility": "B",
        })

    return findings


def _derive_conclusions(cluster, findings):
    """从调查发现中推导结论"""
    conclusions = []
    topic_name = cluster["category"].lstrip("#")
    arts = cluster["articles"]

    # 基于互动数据确认
    if arts:
        top_likes = arts[0].get("likeCount") or 0
        if top_likes > 50000:
            conclusions.append(("confirmed", f"{topic_name}话题有强流量表现，头部内容互动量{format_number(top_likes)}+"))

    # 基于发现提取待确认
    for f in findings:
        if f["dimension"] == "用户关注" and "高频关键词" in f["discovery"]:
            conclusions.append(("pending", f"用户关注方向需跨平台验证：{f['discovery'].replace('高频关键词：', '')}"))

    # 基于低占比高互动
    total_in_cluster = cluster["count"]
    if total_in_cluster <= 15:
        conclusions.append(("single", f"{topic_name}话题样本量较少（{total_in_cluster}条），趋势待观察"))

    if not conclusions:
        conclusions.append(("confirmed", f"{topic_name}话题内容稳定，无异常信号"))

    return conclusions


def generate_intelligence_briefing(clusters, articles):
    """基于当日聚类结果生成AI情报调查报告"""
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
        total_shares = sum(a.get("shareCount") or 0 for a in arts)
        top_authors.append({
            "name": author,
            "article_count": count,
            "total_likes": total_likes,
            "total_shares": total_shares,
        })

    # 4. 为每个TOP话题生成调查报告
    investigation_reports = []
    for cluster in clusters[:3]:
        topic_name = cluster["category"].lstrip("#")
        mode, scenario = _match_mode(topic_name)
        engines = SCENARIO_ENGINES.get(scenario, SCENARIO_ENGINES["热点事件追踪"])
        findings = _derive_findings(cluster, articles, scenario)
        conclusions = _derive_conclusions(cluster, findings)

        investigation_reports.append({
            "topic": cluster["category"],
            "mode": mode,
            "scenario": scenario,
            "engines": engines,
            "findings": findings,
            "conclusions": conclusions,
        })

    # 5. 跨平台对比建议
    cross_platform_tips = []
    for topic_info in top_topics[:3]:
        topic_name = topic_info["topic"].lstrip("#")
        cross_platform_tips.append(
            f"「{topic_name}」— 建议同步关注抖音、小红书、公众号同话题热度，"
            f"用 Baidu+WeChat+Toutiao 三引擎追踪国内全平台动态"
        )

    briefing = {
        "top_topics": top_topics,
        "emerging_topics": emerging_topics,
        "top_authors": top_authors,
        "investigation_reports": investigation_reports,
        "cross_platform_tips": cross_platform_tips,
    }

    return briefing


def print_intelligence_briefing(briefing):
    """在终端输出情报调查"""
    if not briefing:
        return

    print(f"\n{BOLD}{'='*78}{RESET}")
    print(f"{BOLD}  AI情报调查 · 深度调查指引{RESET}")
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
            print(f"    @{author['name']} — {author['article_count']}条作品, "
                  f"总赞{format_number(author['total_likes'])}, "
                  f"总分享{format_number(author['total_shares'])}")
        print()

    # 调查报告
    print(f"  {CYAN}{BOLD}【TOP话题调查报告】{RESET}")
    for report in briefing["investigation_reports"]:
        engines_str = " + ".join(report["engines"])
        print(f"    ▸ {report['topic']} — {report['mode']} | {engines_str}")
        for f in report.get("findings", []):
            print(f"      [{f['credibility']}级] {f['dimension']}: {f['discovery']}")
        for ctype, ctext in report.get("conclusions", []):
            icons = {"confirmed": "✅", "pending": "⚠️", "denied": "❌", "single": "🔍"}
            print(f"      {icons.get(ctype, '·')} {ctext}")
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
        return {"total": 0, "avg_likes": 0, "top_author": "-", "total_likes": 0}

    likes_list = [a.get("likeCount") or 0 for a in articles]
    avg_likes = sum(likes_list) // total if total > 0 else 0

    author_counter = Counter(a.get("userName", "未知") for a in articles)
    top_author = author_counter.most_common(1)[0][0] if author_counter else "-"

    total_likes = sum(a.get("likeCount") or 0 for a in articles)

    return {
        "total": total,
        "avg_likes": avg_likes,
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
    print(f"{BOLD}  B站AI信息源 · 分类视频一览{RESET}")
    print(f"{BOLD}{'='*78}{RESET}\n")

    for i, cluster in enumerate(clusters, 1):
        category = cluster["category"]
        arts = cluster["articles"]

        # 分类标题
        print(f"  {CYAN}{BOLD}【{category}】{RESET} "
              f"共 {len(arts)} 条展示 / {cluster['count']} 条总计")

        # 表头
        header = (f"  {'序号':<4}{'标题':<36}{'作者':<14}"
                  f"{'分享':>8}{'点赞':>8}{'评论':>8}")
        print(f"  {YELLOW}{'─'*76}{RESET}")
        print(f"  {YELLOW}{header}{RESET}")
        print(f"  {YELLOW}{'─'*76}{RESET}")

        for j, article in enumerate(arts, 1):
            title = article.get("title", "无标题")
            author = article.get("userName", "-")
            shares = format_number(article.get("shareCount"))
            likes = format_number(article.get("likeCount"))
            comments = format_number(article.get("commentCount"))

            # 截断过长的标题和作者
            display_title = title[:34] + ".." if len(title) > 36 else title
            display_author = author[:12] + ".." if len(author) > 14 else author

            print(f"  {j:<4}{display_title:<36}{display_author:<14}"
                  f"{shares:>8}{likes:>8}{comments:>8}")

        print()  # 分类之间空行


def generate_category_cards(clusters):
    """生成分类卡片 HTML"""
    cards_html = ""
    for i, cluster in enumerate(clusters, 1):
        articles_html = ""
        for article in cluster["articles"]:
            title = article.get("title", "无标题")
            url = article.get("url") or "#"
            author = article.get("userName", "")
            cover = article.get("coverUrl") or ""
            shares = format_number(article.get("shareCount"))
            likes = format_number(article.get("likeCount"))
            comments = format_number(article.get("commentCount"))

            cover_html = ""
            if cover:
                cover_html = f'<img class="article-cover" src="{cover}" alt="" loading="lazy" referrerpolicy="no-referrer">'

            articles_html += f'''
                <div class="article-item">
                    {cover_html}
                    <div class="article-info">
                        <a href="{url}" target="_blank" class="article-title">{title}</a>
                        <div class="article-meta">
                            <span class="author">{author}</span>
                            <span class="metrics">
                                <span class="metric">&#x1f517; {shares}</span>
                                <span class="metric">&#x1f44d; {likes}</span>
                                <span class="metric">&#x1f4ac; {comments}</span>
                            </span>
                        </div>
                    </div>
                </div>'''

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
    """生成情报调查板块 HTML"""
    if not briefing:
        return ""

    # 热度TOP话题
    topics_html = ""
    for i, topic in enumerate(briefing["top_topics"], 1):
        top_art = topic.get("top_article")
        top_title = (top_art.get("title", "-")[:50] if top_art else "-")
        top_likes = format_number(top_art.get("likeCount", 0)) if top_art else "-"
        topics_html += f'''
                <div class="intel-rank-item">
                    <span class="intel-rank-num">{i}</span>
                    <div class="intel-rank-info">
                        <span class="intel-rank-topic">{topic['topic']}</span>
                        <span class="intel-rank-detail">占比 {topic['ratio']}% · {topic['count']}条 · 头部: {top_title}</span>
                    </div>
                    <span class="intel-rank-metric">{top_likes} 点赞</span>
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
        authors_html += f'''
                <div class="intel-author-item">
                    <span class="intel-author-name">@{author['name']}</span>
                    <span class="intel-author-stats">{author['article_count']}条 · 总赞{format_number(author['total_likes'])} · 总分享{format_number(author['total_shares'])}</span>
                </div>'''

    authors_section = ""
    if authors_html:
        authors_section = f'''
        <div class="intel-subsection">
            <h4 class="intel-subtitle">核心达人</h4>
            <div class="intel-author-list">{authors_html}
            </div>
        </div>'''

    # 调查报告卡片
    reports_html = ""
    for report in briefing.get("investigation_reports", []):
        # 发现表
        findings_rows = ""
        for f in report.get("findings", []):
            cred = f["credibility"]
            cred_class = f"intel-cred-{cred.lower()}"
            findings_rows += f'''
                        <tr>
                            <td>{f['dimension']}</td>
                            <td>{f['discovery']}</td>
                            <td>{f['source']}</td>
                            <td><span class="intel-cred-badge {cred_class}">{cred}级</span></td>
                        </tr>'''

        # 结论
        conclusion_items = ""
        for ctype, ctext in report.get("conclusions", []):
            icons = {"confirmed": "✅", "pending": "⚠️", "denied": "❌", "single": "🔍"}
            css_class = {"confirmed": "intel-conclusion-confirmed", "pending": "intel-conclusion-pending",
                         "denied": "intel-conclusion-denied", "single": "intel-conclusion-single"}
            conclusion_items += f'''<li class="intel-conclusion-item {css_class.get(ctype, '')}">{icons.get(ctype, "·")} {ctext}</li>'''

        engines_str = " + ".join(report["engines"])
        scenario_tag = f'<div class="intel-report-scenario">📋 调查场景: {report.get("scenario", "")}</div>'
        reports_html += f'''
        <div class="intel-report-card reveal">
            <div class="intel-report-head">
                <span class="intel-report-topic">{report['topic']}</span>
                <span class="intel-report-mode">{report['mode']}</span>
                <span class="intel-report-engines">{engines_str}</span>
            </div>
            <div class="intel-report-body">
                {scenario_tag}
                <table class="intel-findings-table">
                    <thead><tr><th>维度</th><th>发现</th><th>来源</th><th>可信度</th></tr></thead>
                    <tbody>{findings_rows}
                    </tbody>
                </table>
                <div class="intel-conclusion-title">关键结论</div>
                <ul class="intel-conclusion-list">{conclusion_items}
                </ul>
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

    # 可信度标注规范（紧凑版）
    cred_ref_items = ""
    for level, desc in CREDIBILITY_LEVELS.items():
        cred_class = f"intel-cred-{level.lower()}"
        cred_ref_items += f'''
            <div class="intel-cred-ref-item">
                <span class="intel-cred-badge {cred_class}">{level}级</span>
                <span class="intel-cred-ref-label">{desc}</span>
            </div>'''

    html = f'''
    <div class="intelligence-section reveal">
        <div class="intel-header">
            <h2 class="intel-title">AI情报调查报告</h2>
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
                <h4 class="intel-subtitle">TOP话题调查报告</h4>
                {reports_html}
            </div>

            {cross_section}

            <div class="intel-subsection">
                <h4 class="intel-subtitle">可信度标注规范</h4>
                <div class="intel-cred-ref">{cred_ref_items}
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

    # 生成情报调查 HTML
    intelligence_html = generate_intelligence_html(briefing) if briefing else ""

    html = template
    html = html.replace("{{DATE}}", date_str)
    html = html.replace("{{DATE_CN}}", date_cn)
    html = html.replace("{{TOTAL_COUNT}}", str(stats["total"]))
    html = html.replace("{{TOPIC_COUNT}}", str(topic_count))
    html = html.replace("{{TOP_AUTHOR}}", stats["top_author"])
    html = html.replace("{{AVG_LIKES}}", format_number(stats["avg_likes"]))
    html = html.replace("{{TOTAL_LIKES}}", format_number(stats["total_likes"]))
    html = html.replace("{{CATEGORY_CARDS}}", category_cards)
    html = html.replace("{{INTELLIGENCE_SECTION}}", intelligence_html)
    html = html.replace("{{TIMESTAMP}}", timestamp)
    html = html.replace("{{API_KEY}}", api_key or PUBLIC_API_KEY)
    html = html.replace("{{SOURCE}}", SOURCE)

    return html


def get_fallback_template():
    """内置最小 HTML 模板（当模板文件缺失时使用）"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>B站AI信息源 - {{DATE}}</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, sans-serif; background: #1a1a1a; color: #e8e4df; padding: 2rem; }
.header { text-align: center; padding: 2rem 0; }
.header h1 { font-size: 2rem; color: #FB7299; }
.header p { color: #9a9590; margin-top: 0.5rem; }
.stats { display: flex; justify-content: center; gap: 2rem; padding: 1rem; margin: 1rem 0; }
.stat-item { text-align: center; }
.stat-value { font-size: 1.5rem; font-weight: bold; color: #FB7299; }
.stat-label { font-size: 0.8rem; color: #9a9590; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 1.5rem; max-width: 1200px; margin: 2rem auto; }
.category-card { background: #2d2d2d; border-radius: 12px; padding: 1.5rem; }
.card-header { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 1rem; padding-bottom: 0.8rem; border-bottom: 1px solid #3d3d3d; }
.card-number { font-size: 1.5rem; font-weight: bold; color: #FB7299; }
.card-category { flex: 1; font-size: 1.1rem; }
.card-count { color: #9a9590; font-size: 0.9rem; }
.article-item { padding: 0.6rem 0; border-bottom: 1px solid #3d3d3d; display: flex; gap: 0.8rem; }
.article-item:last-child { border-bottom: none; }
.article-cover { width: 60px; height: 60px; border-radius: 6px; object-fit: cover; flex-shrink: 0; }
.article-info { flex: 1; min-width: 0; }
.article-title { color: #e8e4df; text-decoration: none; font-size: 0.9rem; line-height: 1.4; display: block; }
.article-title:hover { color: #FB7299; }
.article-meta { display: flex; justify-content: space-between; margin-top: 0.3rem; font-size: 0.75rem; color: #9a9590; }
.metrics { display: flex; gap: 0.8rem; }
.footer { text-align: center; padding: 2rem; color: #666; font-size: 0.8rem; }
</style>
</head>
<body>
<div class="header">
    <h1>B站AI信息源</h1>
    <p>{{DATE_CN}} | 共 {{TOTAL_COUNT}} 条热门视频</p>
</div>
<div class="stats">
    <div class="stat-item"><div class="stat-value">{{TOPIC_COUNT}}</div><div class="stat-label">分类</div></div>
    <div class="stat-item"><div class="stat-value">{{TOTAL_COUNT}}</div><div class="stat-label">视频</div></div>
    <div class="stat-item"><div class="stat-value">{{AVG_READS}}</div><div class="stat-label">平均播放</div></div>
    <div class="stat-item"><div class="stat-value">{{TOTAL_LIKES}}</div><div class="stat-label">总点赞</div></div>
</div>
<div class="cards">{{CATEGORY_CARDS}}</div>
<div class="footer">Generated at {{TIMESTAMP}} by B站AI信息源 Skill</div>
</body>
</html>'''


# ─── 订阅机制 ──────────────────────────────────────────────────────────────────────
def install_subscription():
    """安装定时任务，每天自动生成日报"""
    if sys.platform == "darwin":
        PLIST_DIR.mkdir(parents=True, exist_ok=True)
        plist_path = PLIST_DIR / f"{PLIST_LABEL}.plist"

        script_path = os.path.abspath(__file__)
        log_path = str(Path.home() / "Library" / "Logs" / "qoder-bili-ai-hot-articles.log")

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
        <string>--date</string>
        <string>today</string>
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
            info("订阅成功! 每天 09:00 自动生成B站爆款日报")
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
            info("订阅成功! 每天 09:00 自动生成B站爆款日报 (crontab)")
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


# ─── 辅助函数 ─────────────────────────────────────────────────────────────
def open_in_browser(filepath):
    """在浏览器中打开 HTML 文件"""
    if sys.platform == "darwin":
        subprocess.run(["open", str(filepath)], check=False)
    elif sys.platform == "linux":
        subprocess.run(["xdg-open", str(filepath)], check=False)
    elif sys.platform == "win32":
        os.startfile(str(filepath))


# ─── 主流程 ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="B站AI信息源 — 每日热门内容聚类日报",
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
    parser.add_argument("--count", type=int, default=200, help="目标视频数 (默认: 200)")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="指定日期 YYYY-MM-DD (默认: 今天)")
    parser.add_argument("--start-time", help="自定义开始时间，格式 YYYY-MM-DD HH:MM:SS (覆盖--date推算)")
    parser.add_argument("--end-time", help="自定义结束时间，格式 YYYY-MM-DD HH:MM:SS (覆盖--date推算)")
    parser.add_argument("--output-dir", help=f"输出目录 (默认: ~/Downloads/QoderReports)")
    parser.add_argument("--api-key", help="API Key (不传则读取环境变量或内置公共 Key)")
    parser.add_argument("--subscribe", action="store_true", help="安装每日定时任务 (09:00)")
    parser.add_argument("--unsubscribe", action="store_true", help="卸载定时任务")


    args = parser.parse_args()

    # ── Banner ──
    banner = f"""{CYAN}{BOLD}
  ╔══════════════════════════════════════╗
  ║     B站AI信息源 · 日报生成      ║
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
    if api_key == PUBLIC_API_KEY:
        print(f"{YELLOW}╔══════════════════════════════════════════════════╗{RESET}")
        print(f"{YELLOW}║  使用内置公共 API Key                         ║{RESET}")
        print(f"{YELLOW}║  超出额度后请前往 www.redfox.hk 获取 Key：    ║{RESET}")
        print(f"{YELLOW}║  export REDFOX_API_KEY=ak_你的密钥                 ║{RESET}")
        print(f"{YELLOW}╚══════════════════════════════════════════════════╝{RESET}")
        print()

    # ── Session ──
    session = requests.Session()
    session.verify = True
    session.headers.update({
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    })

    # ── 时间范围推算 ──
    if args.start_time and args.end_time:
        # 用户自定义时间段，直接使用
        start_time = args.start_time
        end_time = args.end_time
    else:
        # 根据 --date 推算当天 00:00:00 ~ 24:00:00
        try:
            dt = datetime.strptime(args.date, "%Y-%m-%d")
            start_time = dt.strftime("%Y-%m-%d") + " 00:00:00"
            end_time = dt.strftime("%Y-%m-%d") + " 24:00:00"
        except ValueError:
            warn(f"日期格式错误: {args.date}，将不传时间范围")
            start_time = None
            end_time = None

    time_desc = f"时间段: {start_time} ~ {end_time}" if start_time else "时间段: 全量"

    # ── 获取视频 ──
    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    step(f"扫描热门内容，关键词: {keywords}")
    step(f"目标: {args.count} 条, {time_desc}")
    print()

    articles = fetch_articles(session, keywords, args.count, start_time=start_time, end_time=end_time)

    if not articles:
        error("未获取到任何视频")
        print(f"\n{YELLOW}  提示：当前仅搜索 AI 相关B站视频。{RESET}")
        print(f"{YELLOW}  如需搜索全量B站内容，请访问 redfox.hk{RESET}")
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

    # ── AI情报调查报告 ──
    step("正在生成AI情报调查报告...")
    briefing = generate_intelligence_briefing(clusters, articles)
    if briefing:
        info(f"情报调查完成: {len(briefing['investigation_reports'])}个调查报告")
        print_intelligence_briefing(briefing)



    # ── 生成报告 ──
    step("生成 HTML 日报...")
    html_content = generate_report(clusters, articles, args.date, api_key=api_key, briefing=briefing)

    # ── 保存文件 ──
    output_dir = Path(args.output_dir) if args.output_dir else DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"AI-B站日报_{args.date}_{datetime.now().strftime('%H%M%S')}.html"
    output_path = output_dir / filename

    output_path.write_text(html_content, encoding="utf-8")
    info(f"日报已生成: {output_path}")

    open_in_browser(output_path)
    info(f"浏览器已打开: {output_path}")

    # ── 结构化摘要（对齐固定输出模式）──
    print(f"\n{GREEN}{BOLD}✓ 完成!{RESET}")

    # 分类概览表
    total = len(articles)
    print(f"\n  {BOLD}分类概览{RESET}")
    print(f"  {'分类':<16}{'数量':>6}{'占比':>8}{'亮点'}")
    print(f"  {'─'*60}")
    for c in clusters:
        ratio = f"{c['count']/total*100:.1f}%" if total > 0 else "0%"
        # 亮点：头部视频标题截断 + 点赞
        highlight = "暂无"
        if c["articles"]:
            top = c["articles"][0]
            title = (top.get("title") or "无标题")[:20]
            likes = format_number(top.get("likeCount") or 0)
            highlight = f"{title} {likes}赞"
        print(f"  {c['category']:<16}{c['count']:>5}条{ratio:>8}  {highlight}")

    # AI情报调查报告摘要
    if briefing:
        print(f"\n  {BOLD}AI情报调查报告{RESET}")
        if briefing["emerging_topics"]:
            emerging_str = ", ".join(f"{e['topic']}({e['avg_engagement']}+互动)" for e in briefing["emerging_topics"][:3])
            print(f"  起量信号: {emerging_str}")
        if briefing["top_authors"]:
            authors_str = ", ".join(f"@{a['name']}({a['article_count']}条)" for a in briefing["top_authors"][:3])
            print(f"  核心达人: {authors_str}")
        reports_count = len(briefing['investigation_reports'])
        findings_count = sum(len(r.get('findings', [])) for r in briefing['investigation_reports'])
        print(f"  调查报告: {reports_count}个话题 / {findings_count}项发现")

    # 日报地址
    print(f"\n  {BOLD}日报地址{RESET}: {output_path}")

    print(f"\n  分类: {len(clusters)} 个")
    print(f"  视频: {len(articles)} 条")


if __name__ == "__main__":
    main()
