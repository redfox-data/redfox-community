#!/usr/bin/env python3
"""
公众号搜索爬虫 — 关键字搜索微信公众号文章
=========================================
输入关键词，实时搜索公众号文章，终端表格展示，
自动导出 CSV + 生成带搜索框的交互式 HTML 报告。

Usage:
    python3 search.py "人工智能"
    python3 search.py "AI" --count 30
    python3 search.py "大模型" --csv-only
"""

import argparse
import csv
import json
import os
import subprocess
import sys
import time
import threading
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ─── 配置 ─────────────────────────────────────────────────────────────────────────
API_URL = "https://redfox.hk/story/api/gzhData/searchArticle"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"
ENV_KEY = "X_API_KEY"
PUBLIC_API_KEY = "ak_db0e200c049b44288d46da0e758d53dd"
SOURCE = "公众号搜索爬虫-GitHub"

DEFAULT_OUTPUT_DIR = Path.home() / "Downloads" / "QoderGzhSearch"
DEFAULT_COUNT = 20
DEFAULT_PORT = 8766

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
def get_api_key(cli_key=None):
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
    return PUBLIC_API_KEY


# ─── 字段兼容（新旧 API 格式）───────────────────────────────────────────────────────
def _reads(a):
    return a.get("readCount") or a.get("clicksCount") or 0

def _likes(a):
    return a.get("likeCount") or 0

def _shares(a):
    return a.get("shareCount") or 0

def _collects(a):
    return a.get("collectCount") or 0

def _url(a):
    return a.get("workUrl") or a.get("url") or ""

def _uid(a):
    return a.get("workUuid") or a.get("uuid") or ""

def _pub_time(a):
    return a.get("publishTime") or a.get("publicTime") or ""

def _cover(a):
    return a.get("coverUrl") or ""

def _title(a):
    return a.get("title") or "无标题"

def _author(a):
    return a.get("author") or "-"

def _summary(a):
    return a.get("summary") or ""

def _account_type(a):
    return a.get("accountType") or ""


# ─── 数据获取 ──────────────────────────────────────────────────────────────────────
def fetch_articles_batch(session, keyword, offset=0, sort_type="default"):
    payload = {
        "keyword": keyword,
        "offset": offset,
        "sortType": sort_type,
        "source": SOURCE,
    }
    try:
        resp = session.post(API_URL, json=payload, timeout=15)
        result = resp.json()
    except Exception as e:
        error(f"请求失败: {e}")
        return None

    code = result.get("code")
    if code == 3108:
        warn("限频，等待 5s 后重试...")
        time.sleep(5)
        try:
            resp = session.post(API_URL, json=payload, timeout=15)
            result = resp.json()
            code = result.get("code")
        except Exception:
            return None

    if code not in (200, 2000):
        if code in (3106, 3107):
            error(f"API Key 错误 (code {code}): {result.get('msg', '')}")
        else:
            error(f"API 返回错误 (code {code}): {result.get('msg', '')}")
        return None

    data = result.get("data", {})
    articles = data.get("list", [])
    has_more = data.get("hasMore", 0)

    return {"articles": articles, "hasMore": has_more}


def fetch_articles(session, keyword, max_count=20, sort_type="default"):
    all_articles = []
    seen_ids = set()
    offset = 0
    has_more = True

    while len(all_articles) < max_count and has_more:
        batch = fetch_articles_batch(session, keyword, offset=offset, sort_type=sort_type)
        if batch is None:
            break

        new_count = 0
        for article in batch["articles"]:
            pid = _uid(article)
            if pid and pid not in seen_ids:
                seen_ids.add(pid)
                all_articles.append(article)
                new_count += 1

        has_more = batch["hasMore"] == 1
        offset += len(batch["articles"])

        if new_count == 0:
            break

        if len(all_articles) < max_count:
            time.sleep(0.3)

    return {"articles": all_articles[:max_count], "hasMore": 1 if (has_more or len(all_articles) >= max_count) else 0}


def fetch_fallback_articles(session, keyword):
    """零结果时用宽泛词 + 热门词兜底搜索"""
    candidates = set()
    if len(keyword) >= 2:
        candidates.add(keyword[:2])
    if len(keyword) >= 1:
        candidates.add(keyword[:1])
    candidates.add("AI")
    candidates.discard(keyword)

    for broad_kw in sorted(candidates, key=len, reverse=True):
        r = fetch_articles(session, broad_kw, max_count=10)
        if r and r["articles"]:
            return r["articles"]
    return []


def format_number(n):
    if n is None:
        return "0"
    if n >= 10000:
        return f"{n/10000:.1f}w"
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)


# ─── 三因子评分 ────────────────────────────────────────────────────────────────────
def score_relevance(keyword, article):
    """相关性得分 0-10：关键词在标题 > 摘要中的命中情况"""
    kw = keyword.lower().strip()
    title = (_title(article) or "").lower()
    summary = (_summary(article) or "").lower()
    if not kw:
        return 5.0
    if kw == title:
        return 10.0
    if title.startswith(kw):
        return 9.0
    if kw in title:
        return 8.0
    words = [w for w in kw.split() if len(w) >= 2]
    title_matches = sum(1 for w in words if w in title)
    if title_matches >= len(words) * 0.5 and len(words) >= 2:
        return 6.0
    if summary and kw in summary[:len(summary)//3]:
        return 5.0
    if summary and kw in summary:
        return 4.0
    if title_matches > 0:
        return 3.0
    if summary and any(w in summary for w in words):
        return 2.0
    return 1.0


def score_heat(article):
    """热度得分 0.5-3.0：基于阅读数"""
    r = _reads(article)
    if r >= 100000: return 3.0
    if r >= 50000:  return 2.5
    if r >= 10000:  return 2.0
    if r >= 5000:   return 1.5
    if r >= 1000:   return 1.0
    return 0.5


def score_freshness(article):
    """时效得分 0-2.0：基于发布时间"""
    pt = _pub_time(article)
    if not pt:
        return 0
    try:
        pub_dt = datetime.fromisoformat(pt[:19])
        days = (datetime.now() - pub_dt).days
        if days <= 7:   return 2.0
        if days <= 15:  return 1.5
        if days <= 30:  return 1.0
        if days <= 60:  return 0.5
        return 0
    except Exception:
        return 0


def calculate_score(keyword, article):
    """综合评分 = 相关性 + 热度 + 时效（满分 15）"""
    return score_relevance(keyword, article) + score_heat(article) + score_freshness(article)


# ─── 终端表格 ──────────────────────────────────────────────────────────────────────
def print_terminal_table(articles, keyword):
    if not articles:
        print(f"\n{YELLOW}[✗] 关键词 \"{keyword}\" 暂无搜索结果{RESET}")
        return

    count = len(articles)
    print(f"\n{BOLD}{'=' * 120}{RESET}")
    print(f"{BOLD}  公众号搜索爬虫 · \"{keyword}\" · 共 {count} 条结果{RESET}")
    print(f"{BOLD}{'=' * 120}{RESET}")

    header = (f"  {'序号':<4}{'标题':<26}{'作者':<12}"
              f"{'阅读':>7}{'点赞':>5}{'分享':>5}{'收藏':>5}{'发布时间':<12}{'文章链接':<36}")
    print(f"  {YELLOW}{'─' * 112}{RESET}")
    print(f"  {YELLOW}{header}{RESET}")
    print(f"  {YELLOW}{'─' * 112}{RESET}")

    for i, a in enumerate(articles, 1):
        title = _title(a)
        author = _author(a)
        reads = format_number(_reads(a))
        likes = format_number(_likes(a))
        shares = format_number(_shares(a))
        collects = format_number(_collects(a))
        pub_time = _pub_time(a)[:10] if _pub_time(a) else ""
        link = _url(a)

        display_title = title[:24] + ".." if len(title) > 26 else title
        display_author = author[:10] + ".." if len(author) > 12 else author
        display_link = link[:34] + ".." if len(link) > 36 else link

        print(f"  {i:<4}{display_title:<26}{display_author:<12}"
              f"{reads:>7}{likes:>5}{shares:>5}{collects:>5}{pub_time:<12}{display_link:<36}")

    print(f"  {YELLOW}{'─' * 112}{RESET}")

    # 分层提示
    if count <= 2:
        print(f"  {YELLOW}💡 相关结果较少 (仅 {count} 条)，建议尝试更短或更宽泛的关键词{RESET}")
    elif count <= 9:
        print(f"  {YELLOW}💡 仅找到 {count} 条结果，以下为您展示全部{RESET}")

    print()


# ─── CSV 导出 ──────────────────────────────────────────────────────────────────────
def export_csv(articles, keyword, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"公众号搜索_{keyword}_{date_str}.csv"
    filepath = output_dir / filename

    fieldnames = ["标题", "作者", "阅读数", "点赞数", "分享数", "收藏数",
                  "发布时间", "文章链接", "摘要", "公众号分类"]

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for a in articles:
            writer.writerow({
                "标题": _title(a),
                "作者": _author(a),
                "阅读数": _reads(a),
                "点赞数": _likes(a),
                "分享数": _shares(a),
                "收藏数": _collects(a),
                "发布时间": _pub_time(a),
                "文章链接": _url(a),
                "摘要": _summary(a),
                "公众号分类": _account_type(a),
            })

    return filepath


# ─── HTML 报告生成 ─────────────────────────────────────────────────────────────────
def generate_html(articles, keyword, api_key):
    template_path = Path(__file__).parent / "report_template.html"
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
    else:
        template = get_fallback_template()

    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    initial_data = json.dumps(articles, ensure_ascii=False)

    html = template
    html = html.replace("{{KEYWORD}}", keyword)
    html = html.replace("{{DATE}}", date_str)
    html = html.replace("{{TIMESTAMP}}", timestamp)
    html = html.replace("{{TOTAL_COUNT}}", str(len(articles)))
    html = html.replace("{{INITIAL_DATA}}", initial_data)
    html = html.replace("{{API_KEY}}", api_key)
    html = html.replace("{{API_URL}}", API_URL)
    html = html.replace("{{SOURCE}}", SOURCE)

    return html


def get_fallback_template():
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>公众号搜索 - {{KEYWORD}} | {{DATE}}</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
:root {
    --bg: #0a0f0a; --bg-card: #141f14; --bg-card-hover: #1a2a1a;
    --text: #e8efe8; --text-secondary: #8a9a8a; --text-muted: #556655;
    --accent: #2ECC71; --accent-glow: rgba(46,204,113,0.12);
    --accent-border: rgba(46,204,113,0.25);
    --border: rgba(255,255,255,0.05);
    --font: 'Space Grotesk', -apple-system, sans-serif;
    --radius: 12px; --radius-sm: 8px;
}
body {
    font-family: var(--font); background: var(--bg);
    color: var(--text); min-height: 100vh;
}
.main-header {
    text-align: center; padding: 2.5rem 1.5rem 1.5rem;
    max-width: 900px; margin: 0 auto; position: relative;
}
.main-header::after {
    content: ''; position: absolute; bottom: 0; left: 50%;
    transform: translateX(-50%); width: 60px; height: 2px;
    background: var(--accent); opacity: 0.5;
}
.main-header h1 { font-size: 1.6rem; font-weight: 700; color: var(--accent); }
.main-header .subtitle { color: var(--text-secondary); font-size: 0.85rem; margin-top: 0.3rem; }
.stats-bar {
    display: flex; justify-content: center; gap: 2rem;
    padding: 1rem; max-width: 600px; margin: 0 auto; flex-wrap: wrap;
}
.stat-item { text-align: center; }
.stat-value { font-size: 1.2rem; font-weight: 700; color: var(--accent); }
.stat-label { font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; }
.search-container {
    position: sticky; top: 0; z-index: 100;
    background: linear-gradient(180deg, var(--bg) 80%, transparent);
    padding: 1rem 1.5rem 1.5rem; backdrop-filter: blur(12px);
}
.search-wrapper {
    max-width: 640px; margin: 0 auto; display: flex; gap: 0.6rem;
}
.search-input {
    flex: 1; padding: 0.75rem 1.2rem;
    border: 1.5px solid var(--border); border-radius: var(--radius);
    background: #0f1a0f; color: var(--text); font-size: 0.95rem;
    font-family: var(--font); outline: none;
    transition: all 0.2s cubic-bezier(0.16,1,0.3,1);
}
.search-input:focus { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-glow); }
.search-input::placeholder { color: var(--text-muted); }
.search-info { margin-top: 0.6rem; text-align: center; font-size: 0.75rem; color: var(--text-muted); }
.results-container { max-width: 900px; margin: 0 auto; padding: 0.5rem 1.5rem 2rem; }
.results-grid { display: flex; flex-direction: column; gap: 0.5rem; }
.article-card {
    display: flex; align-items: flex-start; gap: 0.9rem;
    padding: 0.9rem 1rem; background: var(--bg-card);
    border: 1px solid var(--border); border-radius: var(--radius-sm);
    cursor: pointer; text-decoration: none; color: inherit;
    transition: all 0.15s cubic-bezier(0.16,1,0.3,1);
}
.article-card:hover {
    background: var(--bg-card-hover); border-color: var(--accent-border);
    transform: translateX(2px);
}
.card-avatar {
    width: 48px; height: 48px; min-width: 48px;
    border-radius: var(--radius-sm); overflow: hidden;
    background: var(--accent-glow); border: 1px solid var(--accent-border);
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; font-weight: 700; color: var(--accent);
    user-select: none;
}
.card-avatar img {
    width: 100%; height: 100%; object-fit: cover;
}
.card-content { flex: 1; min-width: 0; }
.card-title {
    font-size: 0.92rem; font-weight: 500; line-height: 1.45;
    margin-bottom: 0.35rem;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.card-meta {
    display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem 1rem;
    font-size: 0.75rem; color: var(--text-secondary);
}
.card-meta .author { color: #58D68D; font-weight: 500; max-width: 120px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.card-meta .pub-time { color: var(--text-muted); margin-left: auto; }
.status-message { text-align: center; padding: 3rem 1rem; color: var(--text-secondary); font-size: 0.9rem; }
.load-more-bar { display: flex; justify-content: center; padding: 1.5rem 1rem 3rem; }
.load-more-btn {
    padding: 0.65rem 2.2rem; border: 1.5px solid var(--border);
    border-radius: var(--radius); background: var(--bg-card);
    color: var(--text-secondary); font-size: 0.85rem;
    font-family: var(--font); cursor: pointer;
    transition: all 0.2s cubic-bezier(0.16,1,0.3,1);
}
.load-more-btn:hover { border-color: var(--accent-border); color: var(--accent); }
.load-more-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.footer {
    text-align: center; padding: 2rem 1rem; color: var(--text-muted);
    font-size: 0.72rem; border-top: 1px solid var(--border);
    max-width: 900px; margin: 0 auto;
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}
.article-card { animation: fadeInUp 0.3s cubic-bezier(0.16,1,0.3,1) both; }
.article-card:nth-child(1){animation-delay:0s}.article-card:nth-child(2){animation-delay:.03s}
.article-card:nth-child(3){animation-delay:.06s}.article-card:nth-child(4){animation-delay:.09s}
.article-card:nth-child(5){animation-delay:.12s}.article-card:nth-child(6){animation-delay:.15s}
.article-card:nth-child(7){animation-delay:.18s}.article-card:nth-child(8){animation-delay:.21s}
.article-card:nth-child(9){animation-delay:.24s}.article-card:nth-child(10){animation-delay:.27s}
.article-card:nth-child(n+11){animation-delay:.30s}
@media (max-width: 640px) {
    .main-header { padding: 1.5rem 1rem 1rem; }
    .article-card { padding: 0.75rem 0.8rem; gap: 0.7rem; }
    .card-title { font-size: 0.85rem; }
    .card-meta { font-size: 0.7rem; gap: 0.4rem 0.6rem; }
    .card-meta .pub-time { margin-left: 0; }
    .stats-bar { gap: 1.2rem; }
}
</style>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
<div class="main-header"><h1>公众号搜索爬虫</h1><p class="subtitle">{{DATE}} | 输入关键词实时搜索微信公众号文章</p></div>
<div class="stats-bar">
    <div class="stat-item"><div class="stat-value" id="statTotal">{{TOTAL_COUNT}}</div><div class="stat-label">结果总数</div></div>
    <div class="stat-item"><div class="stat-value" id="statKeyword">{{KEYWORD}}</div><div class="stat-label">当前关键词</div></div>
    <div class="stat-item"><div class="stat-value" id="statLoaded">{{TOTAL_COUNT}}</div><div class="stat-label">已加载</div></div>
</div>
<div class="search-container">
    <div class="search-wrapper">
        <input type="text" class="search-input" id="searchInput"
            placeholder="输入关键词搜索公众号文章..." value="{{KEYWORD}}" autofocus>
    </div>
    <div class="search-info" id="searchInfo">输入关键词后自动搜索（300ms 防抖）| 点击文章跳转原文阅读</div>
</div>
<main class="results-container">
    <div class="results-grid" id="resultsGrid"></div>
    <div class="status-message" id="statusMsg" style="display:none">搜索中...</div>
    <div class="status-message" id="emptyMsg" style="display:none;color:var(--text-muted)">暂无搜索结果，请尝试其他关键词</div>
    <div class="load-more-bar" id="loadMoreBar" style="display:none">
        <button class="load-more-btn" id="loadMoreBtn" onclick="loadMore()">加载更多结果</button>
    </div>
</main>
<footer class="footer">Generated at {{TIMESTAMP}} by 公众号搜索 Skill | Powered by redfox.hk</footer>
<script>
const API_URL = '{{API_URL}}';
const API_KEY = '{{API_KEY}}';
const SOURCE = '{{SOURCE}}';
const INITIAL_DATA = {{INITIAL_DATA}};
let currentKeyword = '{{KEYWORD}}';
let currentOffset = 0;
let hasMore = true;
let totalCount = {{TOTAL_COUNT}};
let isLoading = false;
let accumulatedArticles = [];

const resultsGrid = document.getElementById('resultsGrid');
const statusMsg = document.getElementById('statusMsg');
const emptyMsg = document.getElementById('emptyMsg');
const loadMoreBar = document.getElementById('loadMoreBar');
const loadMoreBtn = document.getElementById('loadMoreBtn');
const searchInput = document.getElementById('searchInput');
const searchInfo = document.getElementById('searchInfo');
const statTotal = document.getElementById('statTotal');
const statLoaded = document.getElementById('statLoaded');
const statKeyword = document.getElementById('statKeyword');

function formatNum(n) {
    if (n == null || n === undefined) return '0';
    n = Number(n);
    if (isNaN(n)) return '0';
    if (n >= 10000) return (n/10000).toFixed(1)+'w';
    if (n >= 1000) return (n/1000).toFixed(1)+'k';
    return String(n);
}
function escapeHTML(str) {
    const div = document.createElement('div');
    div.textContent = str || '';
    return div.innerHTML;
}
function getArticleUrl(a) { return a.workUrl || a.url || '#'; }
function getCoverUrl(a) { return a.coverUrl || ''; }
function getReadCount(a) { return a.readCount || a.clicksCount || 0; }
function getPubTime(a) { return (a.publishTime || a.publicTime || '').slice(0,10); }

function renderArticleCard(article) {
    const title = article.title || '无标题';
    const author = article.author || '未知作者';
    const reads = formatNum(getReadCount(article));
    const likes = formatNum(article.likeCount);
    const shares = formatNum(article.shareCount);
    const collects = formatNum(article.collectCount);
    const pubTime = getPubTime(article);
    const url = getArticleUrl(article);
    const cover = getCoverUrl(article);

    const card = document.createElement('a');
    card.className = 'article-card';
    card.href = url;
    card.target = '_blank';
    card.rel = 'noopener noreferrer';

    let avatarHTML;
    if (cover) {
        avatarHTML = '<img src="'+cover+'" alt="" loading="lazy">';
    } else {
        const ch = (title.replace(/[^\\w\\u4e00-\\u9fff]/g,'').trim().charAt(0)||'文');
        avatarHTML = escapeHTML(ch);
    }
    card.innerHTML = '<div class="card-avatar">'+avatarHTML+'</div>' +
        '<div class="card-content">' +
        '<div class="card-title">'+escapeHTML(title)+'</div>' +
        '<div class="card-meta">' +
        '<span class="author" title="'+escapeHTML(author)+'">'+escapeHTML(author)+'</span>' +
        '<span>👁 '+reads+'</span>' +
        '<span>👍 '+likes+'</span>' +
        '<span>📤 '+shares+'</span>' +
        '<span>⭐ '+collects+'</span>' +
        (pubTime ? '<span class="pub-time">'+pubTime+'</span>' : '') +
        '</div></div>';
    return card;
}

function renderArticles(articles, append) {
    if (!append) resultsGrid.innerHTML = '';
    articles.forEach(a => resultsGrid.appendChild(renderArticleCard(a)));
}

function updateUI() {
    statTotal.textContent = totalCount || accumulatedArticles.length;
    statLoaded.textContent = accumulatedArticles.length;
    statKeyword.textContent = currentKeyword || '-';
    loadMoreBar.style.display = hasMore ? 'flex' : 'none';
}

function setLoading(loading) {
    isLoading = loading;
    statusMsg.style.display = loading ? 'block' : 'none';
    emptyMsg.style.display = 'none';
    loadMoreBtn.disabled = loading;
}

function fetchArticlesFromAPI(keyword, offset) {
    return fetch(API_URL, {
        method: 'POST',
        headers: {'Content-Type':'application/json','X-API-KEY':API_KEY},
        body: JSON.stringify({keyword,offset,sortType:'default',source:SOURCE})
    }).then(r => r.json()).then(res => {
        if (res.code===200||res.code===2000) {
            const list = res.data.list||[];
            hasMore = res.data.hasMore===1;
            return list;
        } else {
            throw new Error(res.msg||'API error');
        }
    });
}

function doSearch() {
    const kw = searchInput.value.trim();
    if (!kw) { showEmpty(); return; }
    currentKeyword = kw;
    currentOffset = 0;
    hasMore = true;
    totalCount = 0;
    accumulatedArticles = [];
    resultsGrid.innerHTML = '';
    setLoading(true);
    updateUI();
    fetchArticlesFromAPI(kw,0).then(list => {
        if (!list||!list.length) { showEmpty(); return; }
        accumulatedArticles = list;
        currentOffset = list.length;
        renderArticles(list, false);
        setLoading(false);
        updateUI();
        searchInfo.textContent = '关键词 "'+kw+'" · 已加载 '+list.length+' 条结果';
    }).catch(e => {
        statusMsg.style.display='block'; statusMsg.textContent='搜索失败: '+e.message;
        isLoading = false;
    });
}

function loadMore() {
    if (isLoading||!hasMore) return;
    setLoading(true);
    fetchArticlesFromAPI(currentKeyword,currentOffset).then(list => {
        if (!list||!list.length) { hasMore=false; setLoading(false); updateUI(); return; }
        accumulatedArticles = accumulatedArticles.concat(list);
        currentOffset += list.length;
        renderArticles(list, true);
        setLoading(false);
        updateUI();
        searchInfo.textContent = '关键词 "'+currentKeyword+'" · 已加载 '+accumulatedArticles.length+' 条结果';
    }).catch(e => {
        statusMsg.style.display='block'; statusMsg.textContent='加载失败: '+e.message;
        isLoading = false;
    });
}

function showEmpty() {
    resultsGrid.innerHTML = '';
    statusMsg.style.display='none';
    emptyMsg.style.display='block';
    loadMoreBar.style.display='none';
    statTotal.textContent='0'; statLoaded.textContent='0';
}

let debounceTimer;
searchInput.addEventListener('input',function() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(doSearch,300);
});
searchInput.addEventListener('keydown',function(e) {
    if (e.key==='Enter') { clearTimeout(debounceTimer); doSearch(); }
});

function init() {
    if (INITIAL_DATA && INITIAL_DATA.length>0) {
        accumulatedArticles = INITIAL_DATA;
        currentOffset = INITIAL_DATA.length;
        totalCount = INITIAL_DATA.length;
        renderArticles(INITIAL_DATA, false);
        updateUI();
        statusMsg.style.display='none';
        searchInfo.textContent = '初始结果 · 共 '+INITIAL_DATA.length+' 条 | 输入新关键词自动搜索';
    } else {
        showEmpty();
        searchInfo.textContent = '输入关键词开始搜索公众号文章';
    }
}
init();
</script>
</body>
</html>'''


# ─── API 代理 HTTP 服务 ─────────────────────────────────────────────────────────────
class ProxyHTTPHandler(SimpleHTTPRequestHandler):
    api_key = PUBLIC_API_KEY

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/search":
            self._handle_search(parsed)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/search":
            self._handle_search_post()
        else:
            self.send_error(404)

    def _handle_search(self, parsed):
        params = parse_qs(parsed.query)
        keyword = params.get("keyword", [""])[0]
        offset = int(params.get("offset", ["0"])[0])
        sort_type = params.get("sortType", ["default"])[0]
        if not keyword:
            self._send_json({"code": -1, "msg": "missing keyword"})
            return
        self._do_proxy_request({"keyword": keyword, "offset": offset, "sortType": sort_type, "source": SOURCE})

    def _handle_search_post(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b"{}"
        try:
            req_data = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"code": -1, "msg": "invalid json"})
            return
        keyword = req_data.get("keyword", "")
        offset = req_data.get("offset", 0)
        sort_type = req_data.get("sortType", "default")
        if not keyword:
            self._send_json({"code": -1, "msg": "missing keyword"})
            return
        self._do_proxy_request({"keyword": keyword, "offset": offset, "sortType": sort_type, "source": SOURCE})

    def _do_proxy_request(self, payload):
        try:
            resp = requests.post(API_URL, json=payload,
                headers={"Content-Type": "application/json", "X-API-KEY": self.api_key}, timeout=15)
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

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-API-KEY")
        self.end_headers()

    def log_message(self, format, *args):
        pass


def start_server(output_dir, api_key, port=8766):
    ProxyHTTPHandler.api_key = api_key
    os.chdir(str(output_dir))
    server = HTTPServer(("127.0.0.1", port), ProxyHTTPHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    info(f"本地服务已启动: http://127.0.0.1:{port}")
    return server


# ─── 主流程 ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="公众号搜索爬虫 — 关键字搜索微信公众号文章",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 search.py "人工智能"
  python3 search.py "AI Agent" --count 30
  python3 search.py "大模型" --csv-only
  python3 search.py "AI" --no-open --output-dir ~/Desktop
        """,
    )
    parser.add_argument("keyword", nargs="?", default="", help="搜索关键词（必填）")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT, help=f"获取文章数量 (默认: {DEFAULT_COUNT})")
    parser.add_argument("--sort-type", default="default", help="排序方式: default / time (默认: default)")
    parser.add_argument("--output-dir", help=f"输出目录 (默认: ~/Downloads/QoderGzhSearch)")
    parser.add_argument("--api-key", help="API Key")
    parser.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--csv-only", action="store_true", help="仅生成 CSV 文件")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"HTTP 服务端口 (默认: {DEFAULT_PORT})")

    args = parser.parse_args()

    banner = f"""{CYAN}{BOLD}
  ╔══════════════════════════════════════════╗
  ║       公众号搜索爬虫 · GZH Crawler        ║
  ║     关键词查询 · 数据导出 · 交互报告     ║
  ╚══════════════════════════════════════════╝{RESET}
"""
    print(banner)

    if not HAS_REQUESTS:
        error("缺少 requests 库，请安装: pip3 install requests")
        sys.exit(1)

    api_key = get_api_key(cli_key=args.api_key)
    if api_key == PUBLIC_API_KEY:
        print(f"{YELLOW}╔══════════════════════════════════════════════════╗{RESET}")
        print(f"{YELLOW}║  使用内置公共 API Key                           ║{RESET}")
        print(f"{YELLOW}║  约 10000 次免费额度，用完请注册: redfox.hk     ║{RESET}")
        print(f"{YELLOW}╚══════════════════════════════════════════════════╝{RESET}\n")

    if not args.keyword:
        try:
            args.keyword = input(f"{CYAN}请输入搜索关键词: {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            sys.exit(0)
        if not args.keyword:
            error("搜索关键词不能为空")
            sys.exit(1)

    keyword = args.keyword

    if len(keyword) > 10:
        error(f"关键词长度不能超过 10 个字符（当前 {len(keyword)} 个），请精简后重试")
        sys.exit(1)

    max_count = args.count
    sort_type = args.sort_type
    output_dir = args.output_dir or str(DEFAULT_OUTPUT_DIR)
    output_dir = os.path.expanduser(output_dir)

    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "X-API-KEY": api_key})

    step(f"搜索关键词: \"{keyword}\" (最多 {max_count} 条)...")
    result = fetch_articles(session, keyword, max_count=max_count, sort_type=sort_type)

    if result is None:
        error("搜索失败，请检查网络或 API Key")
        sys.exit(1)

    articles = result["articles"]
    has_more = result["hasMore"]

    # ── 客户端排序（相关性优先、同分按阅读量降序）──
    if articles:
        articles.sort(key=lambda a: (calculate_score(keyword, a), _reads(a)), reverse=True)

    # ── 零结果处理 ──
    if not articles:
        print(f"\n{YELLOW}[✗] 抱歉，未找到与「{BOLD}{keyword}{RESET}{YELLOW}」直接相关的内容{RESET}\n")
        step("尝试搜索热门内容...")
        fallback = fetch_fallback_articles(session, keyword)
        if fallback:
            fallback.sort(key=lambda a: (calculate_score("", a), _reads(a)), reverse=True)
            info(f"为您推荐 {len(fallback)} 篇热门文章（非直接相关）：")
            print_terminal_table(fallback, keyword)
            articles = fallback
        else:
            print(f"  {YELLOW}建议:{RESET} 尝试更短的关键词（如「{keyword[:2] if len(keyword)>=2 else 'AI'}」）")
            print(f"  {YELLOW}建议:{RESET} 使用英文关键词重试")
            warn("如需搜索全量公众号内容，请访问 redfox.hk")
            sys.exit(0)

    # 表格展示（有结果时）
    if articles:
        print_terminal_table(articles, keyword)

    reads_list = [_reads(a) for a in articles]
    total_reads = sum(reads_list)
    max_reads = max(reads_list) if reads_list else 0
    print(f"  {BOLD}统计:{RESET} 共 {len(articles)} 条 (按综合评分排序) | 总阅读 {format_number(total_reads)} | "
          f"最高阅读 {format_number(max_reads)} | {'还有更多数据' if has_more else '已加载全部'}")

    step("导出 CSV ...")
    csv_path = export_csv(articles, keyword, output_dir)
    info(f"CSV 已保存: {csv_path}")

    if not args.csv_only:
        step("生成 HTML 报告 ...")
        html_content = generate_html(articles, keyword, api_key)
        date_str = datetime.now().strftime("%Y-%m-%d")
        html_filename = f"公众号搜索_{keyword}_{date_str}.html"
        html_dir = Path(output_dir)
        html_dir.mkdir(parents=True, exist_ok=True)
        html_path = html_dir / html_filename
        html_path.write_text(html_content, encoding="utf-8")
        info(f"HTML 报告已保存: {html_path}")

        server = start_server(output_dir, api_key, args.port)
        url = f"http://127.0.0.1:{args.port}/{html_filename}"

        if not args.no_open:
            step("打开浏览器...")
            try:
                subprocess.run(["open", url], check=True)
            except Exception:
                print(f"  请手动打开: {url}")

        print(f"\n{GREEN}╔══════════════════════════════════════════════════╗{RESET}")
        print(f"{GREEN}║  ✓ 搜索完成! HTML 报告: {url}{RESET}")
        print(f"{GREEN}║  按 Ctrl+C 停止本地服务                         ║{RESET}")
        print(f"{GREEN}╚══════════════════════════════════════════════════╝{RESET}\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{YELLOW}  [→] 服务已停止{RESET}")
    else:
        print(f"\n{GREEN}╔══════════════════════════════════════════════════╗{RESET}")
        print(f"{GREEN}║  ✓ 搜索完成! CSV: {csv_path}{RESET}")
        print(f"{GREEN}╚══════════════════════════════════════════════════╝{RESET}\n")


if __name__ == "__main__":
    main()
