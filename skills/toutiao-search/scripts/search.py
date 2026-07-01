#!/usr/bin/env python3
"""
今日头条爆款内容查询 — 关键词搜索今日头条作品
=========================================
搜索接口：POST /toutiao/searchWork（关键词搜索列表）
详情接口：POST /toutiao/workDetail（按 opusId 获取完整数据）

Usage:
    python3 search.py "人工智能"
    python3 search.py "AI" --sort views
    python3 search.py "大模型" --hours 24 --video-only
    python3 search.py "新能源" --pages 5 --csv-only
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
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ─── 配置 ─────────────────────────────────────────────────────────────────────────
SEARCH_API = "https://redfox.hk/story/api/toutiao/searchWork"
DETAIL_API = "https://redfox.hk/story/api/toutiao/workDetail"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"
SOURCE = "今日头条爆款查询-GitHub"

DEFAULT_OUTPUT_DIR = Path.home() / "Downloads" / "QoderToutiaoSearch"
DEFAULT_PAGES = 3
DEFAULT_PORT = 8767

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
    return None


# ─── 工具函数 ─────────────────────────────────────────────────────────────────────
def ts_to_str(ts_str):
    """秒级时间戳字符串 → 可读时间"""
    try:
        ts = int(ts_str)
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return ts_str or ""

def ts_to_date(ts_str):
    try:
        ts = int(ts_str)
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return ""

def ts_to_dt(ts_str):
    try:
        ts = int(ts_str)
        return datetime.fromtimestamp(ts)
    except (ValueError, TypeError):
        return None

def format_number(n):
    if n is None:
        return "0"
    n = int(n)
    if n >= 10000:
        return f"{n/10000:.1f}w"
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)

def work_type_str(is_video):
    return "视频" if is_video else "图文"


# ─── 搜索接口 ─────────────────────────────────────────────────────────────────────
def search_works(session, keyword, offset=0):
    """调用 searchWork 接口，返回 (items, has_next)"""
    payload = {"keyword": keyword, "offset": str(offset), "source": SOURCE}
    try:
        resp = session.post(SEARCH_API, json=payload, timeout=20)
        result = resp.json()
    except Exception as e:
        error(f"搜索请求失败: {e}")
        return None, False

    code = result.get("code")
    if code not in (200, 2000):
        msg = result.get("msg", "")
        if "调用次数" in msg:
            error(f"今日调用次数已达上限: {msg}")
        else:
            error(f"搜索接口错误 (code {code}): {msg}")
        return None, False

    data = result.get("data") or []
    if not isinstance(data, list):
        return None, False

    has_next = False
    if data:
        has_next = data[0].get("hasNext", False)

    return data, has_next


# ─── 详情接口 ─────────────────────────────────────────────────────────────────────
def fetch_detail(session, opus_id):
    """调用 workDetail 接口，返回完整作品数据"""
    payload = {"opusId": str(opus_id)}
    try:
        resp = session.post(DETAIL_API, json=payload, timeout=15)
        result = resp.json()
    except Exception as e:
        return None

    code = result.get("code")
    if code not in (200, 2000):
        return None

    return result.get("data")


def fetch_details_batch(session, opus_ids, max_workers=5):
    """并发获取多个作品详情"""
    results = {}
    def _fetch(oid):
        return oid, fetch_detail(session, oid)

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_fetch, oid): oid for oid in opus_ids}
        for future in as_completed(futures):
            try:
                oid, detail = future.result()
                if detail:
                    results[oid] = detail
            except Exception:
                pass
    return results


# ─── 主搜索流程 ────────────────────────────────────────────────────────────────────
def run_search(session, keyword, max_pages=3, hours=0, video_only=False):
    """
    1. searchWork 按关键词翻页搜索
    2. 收集所有 opusId
    3. 并发调用 workDetail 获取完整数据
    4. 过滤（时间/视频）+ 排序
    """
    all_items = []
    seen_ids = set()
    offset = 0
    page = 0

    step(f"正在搜索「{keyword}」...")
    while page < max_pages:
        page += 1
        items, has_next = search_works(session, keyword, offset=offset)
        if items is None:
            break

        new_items = []
        for item in items:
            oid = item.get("opusId")
            if oid and oid not in seen_ids:
                seen_ids.add(oid)
                new_items.append(item)

        if not new_items:
            break

        all_items.extend(new_items)
        offset += 1  # searchWork 的 offset 是页码偏移（从0开始+1）

        step(f"  第 {page} 页: 获取 {len(new_items)} 条（累计 {len(all_items)} 条）")

        if not has_next:
            break
        time.sleep(0.3)

    if not all_items:
        return []

    # 并发获取详情
    opus_ids = [item.get("opusId") for item in all_items if item.get("opusId")]
    step(f"正在获取 {len(opus_ids)} 条作品详情...")
    details = fetch_details_batch(session, opus_ids, max_workers=5)
    info(f"成功获取 {len(details)} 条详情")

    # 合并搜索基础数据 + 详情数据
    merged = []
    for item in all_items:
        oid = item.get("opusId")
        detail = details.get(oid, {})
        pub_ts = item.get("publishTime", "")

        entry = {
            "opusId": oid,
            "title": detail.get("title") or item.get("title") or "无标题",
            "authorName": detail.get("authorName") or item.get("nickname") or "未知作者",
            "publishTime": detail.get("publishTime") or ts_to_str(pub_ts),
            "publishTs": pub_ts,
            "workType": detail.get("workType", False),
            "hasVideo": detail.get("hasVideo", False),
            "workUrl": detail.get("workUrl") or item.get("opusUrl") or "",
            "viewCount": detail.get("viewCount", 0),
            "likeCount": detail.get("likeCount", 0),
            "commentCount": detail.get("commentCount") or item.get("commentNum", 0),
            "repostCount": detail.get("repostCount", 0),
            "shareCount": detail.get("shareCount", 0),
            "content": detail.get("content", ""),
            "imageList": detail.get("imageList", []),
            "duration": detail.get("duration", ""),
        }
        merged.append(entry)

    # 时间过滤
    if hours > 0:
        cutoff = datetime.now() - timedelta(hours=hours)
        merged = [e for e in merged if (ts_to_dt(e["publishTs"]) or datetime.min) >= cutoff]
        if not merged:
            warn(f"最近 {hours} 小时内无相关作品")
            return []

    # 视频筛选
    if video_only:
        merged = [e for e in merged if e["workType"] or e["hasVideo"]]
        if not merged:
            warn("无视频类作品")
            return []

    return merged


# ─── 排序 ─────────────────────────────────────────────────────────────────────────
def sort_results(items, sort_by="time"):
    if sort_by == "views":
        items.sort(key=lambda e: int(e.get("viewCount", 0) or 0), reverse=True)
    else:  # time
        items.sort(key=lambda e: int(e.get("publishTs", 0) or 0), reverse=True)
    return items


# ─── 终端表格 ──────────────────────────────────────────────────────────────────────
def print_terminal_table(items, keyword, sort_by):
    if not items:
        print(f"\n{YELLOW}[✗] 关键词「{keyword}」暂无搜索结果{RESET}")
        return

    count = len(items)
    sort_label = "阅读量" if sort_by == "views" else "发布时间"
    print(f"\n{BOLD}{'=' * 130}{RESET}")
    print(f"{BOLD}  今日头条爆款查询 · 「{keyword}」· 共 {count} 条 · 按{sort_label}降序{RESET}")
    print(f"{BOLD}{'=' * 130}{RESET}")

    header = (f"  {'序号':<4}{'标题':<28}{'作者':<12}{'类型':<5}"
              f"{'阅读':>8}{'点赞':>6}{'评论':>5}{'转发':>5}{'分享':>5}{'发布时间':<14}{'链接':<38}")
    print(f"  {YELLOW}{'─' * 122}{RESET}")
    print(f"  {YELLOW}{header}{RESET}")
    print(f"  {YELLOW}{'─' * 122}{RESET}")

    for i, e in enumerate(items, 1):
        title = (e.get("title") or "无标题")[:26]
        if len(e.get("title", "")) > 26:
            title += ".."
        author = (e.get("authorName") or "-")[:10]
        if len(e.get("authorName", "")) > 10:
            author += ".."
        wtype = "视频" if (e.get("workType") or e.get("hasVideo")) else "图文"
        views = format_number(e.get("viewCount"))
        likes = format_number(e.get("likeCount"))
        comments = format_number(e.get("commentCount"))
        reposts = format_number(e.get("repostCount"))
        shares = format_number(e.get("shareCount"))
        pub = (e.get("publishTime") or "")[:16]
        url = (e.get("workUrl") or "")[:36]
        if len(e.get("workUrl", "")) > 36:
            url += ".."

        print(f"  {i:<4}{title:<28}{author:<12}{wtype:<5}"
              f"{views:>8}{likes:>6}{comments:>5}{reposts:>5}{shares:>5}{pub:<14}{url:<38}")

    print(f"  {YELLOW}{'─' * 122}{RESET}")

    if count <= 3:
        print(f"  {YELLOW}💡 相关结果较少（仅 {count} 条），建议尝试更宽泛的关键词{RESET}")

    print()


# ─── CSV 导出 ──────────────────────────────────────────────────────────────────────
def export_csv(items, keyword, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"头条搜索_{keyword}_{date_str}.csv"
    filepath = output_dir / filename

    fieldnames = ["标题", "作者", "类型", "阅读数", "点赞数", "评论数",
                  "转发数", "分享数", "发布时间", "作品链接", "正文摘要"]

    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for e in items:
            content = (e.get("content") or "")[:200]
            writer.writerow({
                "标题": e.get("title", ""),
                "作者": e.get("authorName", ""),
                "类型": work_type_str(e.get("workType") or e.get("hasVideo")),
                "阅读数": e.get("viewCount", 0),
                "点赞数": e.get("likeCount", 0),
                "评论数": e.get("commentCount", 0),
                "转发数": e.get("repostCount", 0),
                "分享数": e.get("shareCount", 0),
                "发布时间": e.get("publishTime", ""),
                "作品链接": e.get("workUrl", ""),
                "正文摘要": content,
            })

    return filepath


# ─── HTML 报告生成 ─────────────────────────────────────────────────────────────────
def generate_html(items, keyword, api_key):
    template_path = Path(__file__).parent.parent / "assets" / "report_template.html"
    if template_path.exists():
        template = template_path.read_text(encoding="utf-8")
    else:
        template = get_fallback_template()

    date_str = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    initial_data = json.dumps(items, ensure_ascii=False)

    html = template
    html = html.replace("{{KEYWORD}}", keyword)
    html = html.replace("{{DATE}}", date_str)
    html = html.replace("{{TIMESTAMP}}", timestamp)
    html = html.replace("{{TOTAL_COUNT}}", str(len(items)))
    html = html.replace("{{INITIAL_DATA}}", initial_data)
    html = html.replace("{{API_KEY}}", api_key)
    html = html.replace("{{SEARCH_API}}", SEARCH_API)
    html = html.replace("{{DETAIL_API}}", DETAIL_API)
    html = html.replace("{{SOURCE}}", SOURCE)

    return html


def get_fallback_template():
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>今日头条爆款查询 - {{KEYWORD}} | {{DATE}}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0f0a;--bg-card:#141f14;--bg-card-hover:#1a2a1a;--text:#e8efe8;
--text2:#8a9a8a;--text3:#556655;--accent:#F59E0B;--accent-glow:rgba(245,158,11,0.12);
--accent-border:rgba(245,158,11,0.25);--border:rgba(255,255,255,0.05);
--font:'Space Grotesk',-apple-system,sans-serif;--radius:12px;--radius-sm:8px}
body{font-family:var(--font);background:var(--bg);color:var(--text);min-height:100vh}
.main-header{text-align:center;padding:2.5rem 1.5rem 1.5rem;max-width:900px;margin:0 auto}
.main-header h1{font-size:1.6rem;font-weight:700;color:var(--accent)}
.main-header .subtitle{color:var(--text2);font-size:0.85rem;margin-top:0.3rem}
.search-container{position:sticky;top:0;z-index:100;background:linear-gradient(180deg,var(--bg) 80%,transparent);
padding:1rem 1.5rem 1.5rem;backdrop-filter:blur(12px)}
.search-wrapper{max-width:640px;margin:0 auto;display:flex;gap:0.6rem}
.search-input{flex:1;padding:0.75rem 1.2rem;border:1.5px solid var(--border);border-radius:var(--radius);
background:#0f1a0f;color:var(--text);font-size:0.95rem;font-family:var(--font);outline:none;transition:all 0.2s}
.search-input:focus{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent-glow)}
.results-container{max-width:900px;margin:0 auto;padding:0.5rem 1.5rem 2rem}
.results-grid{display:flex;flex-direction:column;gap:0.5rem}
.article-card{display:flex;align-items:flex-start;gap:0.9rem;padding:0.9rem 1rem;background:var(--bg-card);
border:1px solid var(--border);border-radius:var(--radius-sm);cursor:pointer;text-decoration:none;color:inherit;transition:all 0.15s}
.article-card:hover{background:var(--bg-card-hover);border-color:var(--accent-border);transform:translateX(2px)}
.card-avatar{width:48px;height:48px;min-width:48px;border-radius:var(--radius-sm);overflow:hidden;
background:var(--accent-glow);border:1px solid var(--accent-border);display:flex;align-items:center;
justify-content:center;font-size:1rem;font-weight:700;color:var(--accent);user-select:none}
.card-avatar img{width:100%;height:100%;object-fit:cover}
.card-content{flex:1;min-width:0}
.card-title{font-size:0.92rem;font-weight:500;line-height:1.45;margin-bottom:0.35rem;
display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.card-meta{display:flex;flex-wrap:wrap;align-items:center;gap:0.5rem 1rem;font-size:0.75rem;color:var(--text2)}
.card-meta .author{color:#FBBF24;font-weight:500;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.card-meta .pub-time{color:var(--text3);margin-left:auto}
.type-tag{display:inline-block;padding:0.1rem 0.4rem;border-radius:4px;font-size:0.65rem;font-weight:600}
.type-tag.video{background:rgba(239,68,68,0.15);color:#F87171;border:1px solid rgba(239,68,68,0.3)}
.type-tag.article{background:rgba(59,130,246,0.15);color:#60A5FA;border:1px solid rgba(59,130,246,0.3)}
.status-message{text-align:center;padding:3rem 1rem;color:var(--text2);font-size:0.9rem}
.load-more-bar{display:flex;justify-content:center;padding:1.5rem 1rem 3rem}
.load-more-btn{padding:0.65rem 2.2rem;border:1.5px solid var(--border);border-radius:var(--radius);
background:var(--bg-card);color:var(--text2);font-size:0.85rem;font-family:var(--font);cursor:pointer;transition:all 0.2s}
.load-more-btn:hover{border-color:var(--accent-border);color:var(--accent)}
.footer{text-align:center;padding:2rem 1rem;color:var(--text3);font-size:0.72rem;border-top:1px solid var(--border);max-width:900px;margin:0 auto}
</style>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
<div class="main-header"><h1>今日头条爆款查询</h1><p class="subtitle">{{DATE}} | 关键词搜索头条最新作品</p></div>
<div class="search-container">
<div class="search-wrapper"><input type="text" class="search-input" id="searchInput" placeholder="输入关键词搜索头条作品..." value="{{KEYWORD}}" autofocus></div>
</div>
<main class="results-container">
<div class="results-grid" id="resultsGrid"></div>
<div class="status-message" id="statusMsg" style="display:none">搜索中...</div>
<div class="load-more-bar" id="loadMoreBar" style="display:none"><button class="load-more-btn" onclick="loadMore()">加载更多</button></div>
</main>
<footer class="footer">Generated at {{TIMESTAMP}} by 今日头条爆款查询 Skill | Powered by redfox.hk</footer>
<script>
const INITIAL_DATA = {{INITIAL_DATA}};
const resultsGrid = document.getElementById('resultsGrid');
function fmt(n){if(!n)return '0';n=Number(n);if(n>=10000)return(n/10000).toFixed(1)+'w';if(n>=1000)return(n/1000).toFixed(1)+'k';return String(n)}
function esc(s){const d=document.createElement('div');d.textContent=s||'';return d.innerHTML}
function renderCard(e){
const c=document.createElement('a');c.className='article-card';c.href=e.workUrl||'#';c.target='_blank';c.rel='noopener noreferrer';
const isVideo=e.workType||e.hasVideo;const tag=isVideo?'<span class="type-tag video">视频</span>':'<span class="type-tag article">图文</span>';
const img=(e.imageList&&e.imageList[0])?`<img src="${e.imageList[0]}" alt="" loading="lazy">`:esc((e.title||'头').charAt(0));
c.innerHTML=`<div class="card-avatar">${img}</div><div class="card-content"><div class="card-title">${esc(e.title)}</div><div class="card-meta"><span class="author">${esc(e.authorName)}</span>${tag}<span>👁 ${fmt(e.viewCount)}</span><span>👍 ${fmt(e.likeCount)}</span><span>💬 ${fmt(e.commentCount)}</span><span>🔄 ${fmt(e.repostCount)}</span><span class="pub-time">${(e.publishTime||'').slice(0,16)}</span></div></div>`;
return c}
INITIAL_DATA.forEach(e=>resultsGrid.appendChild(renderCard(e)));
</script>
</body>
</html>'''


# ─── API 代理 HTTP 服务 ─────────────────────────────────────────────────────────────
class ProxyHTTPHandler(SimpleHTTPRequestHandler):
    api_key = None

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
        elif parsed.path == "/api/detail":
            self._handle_detail_post()
        else:
            self.send_error(404)

    def _handle_search(self, parsed):
        params = parse_qs(parsed.query)
        keyword = params.get("keyword", [""])[0]
        offset = params.get("offset", ["0"])[0]
        if not keyword:
            self._send_json({"code": -1, "msg": "missing keyword"})
            return
        self._do_proxy_request(SEARCH_API, {"keyword": keyword, "offset": offset, "source": SOURCE})

    def _handle_search_post(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b"{}"
        try:
            req_data = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"code": -1, "msg": "invalid json"})
            return
        keyword = req_data.get("keyword", "")
        offset = req_data.get("offset", "0")
        if not keyword:
            self._send_json({"code": -1, "msg": "missing keyword"})
            return
        self._do_proxy_request(SEARCH_API, {"keyword": keyword, "offset": str(offset), "source": SOURCE})

    def _handle_detail_post(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b"{}"
        try:
            req_data = json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"code": -1, "msg": "invalid json"})
            return
        opus_id = req_data.get("opusId", "")
        if not opus_id:
            self._send_json({"code": -1, "msg": "missing opusId"})
            return
        self._do_proxy_request(DETAIL_API, {"opusId": str(opus_id)})

    def _do_proxy_request(self, url, payload):
        try:
            resp = requests.post(url, json=payload,
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


def start_server(output_dir, api_key, port=8767):
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
        description="今日头条爆款内容查询 — 关键词搜索今日头条作品",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 search.py "人工智能"
  python3 search.py "AI" --sort views
  python3 search.py "大模型" --hours 24 --video-only
  python3 search.py "新能源" --pages 5 --csv-only
        """,
    )
    parser.add_argument("keyword", nargs="?", default="", help="搜索关键词（必填）")
    parser.add_argument("--sort", default="views", choices=["time", "views"],
                        help="排序方式: views(默认) / time")
    parser.add_argument("--hours", type=int, default=0,
                        help="限定最近 N 小时内发布（0=不限，默认 0）")
    parser.add_argument("--pages", type=int, default=DEFAULT_PAGES,
                        help=f"翻页次数（默认 {DEFAULT_PAGES}）")
    parser.add_argument("--video-only", action="store_true",
                        help="只返回视频类作品")
    parser.add_argument("--output-dir",
                        help=f"输出目录（默认 ~/Downloads/QoderToutiaoSearch）")
    parser.add_argument("--api-key", help="API Key")
    parser.add_argument("--no-open", action="store_true", help="不自动打开浏览器")
    parser.add_argument("--csv-only", action="store_true", help="仅生成 CSV 文件")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT,
                        help=f"HTTP 服务端口（默认 {DEFAULT_PORT}）")

    args = parser.parse_args()

    banner = f"""{CYAN}{BOLD}
  ╔══════════════════════════════════════════════╗
  ║     今日头条爆款查询 · Toutiao Search         ║
  ║    关键词搜索 · 实时数据 · 交互式报告        ║
  ╚══════════════════════════════════════════════╝{RESET}
"""
    print(banner)

    if not HAS_REQUESTS:
        error("缺少 requests 库，请安装: pip3 install requests")
        sys.exit(1)

    api_key = get_api_key(cli_key=args.api_key)
    if not api_key:
        print(f"{RED}╔══════════════════════════════════════════════════════╗{RESET}")
        print(f"{RED}║  未配置 API Key，请通过以下方式之一配置：            ║{RESET}")
        print(f"{RED}║                                                      ║{RESET}")
        print(f"{RED}║  export REDFOX_API_KEY=ak_你的密钥                   ║{RESET}")
        print(f"{RED}║  python3 search.py --api-key ak_你的密钥              ║{RESET}")
        print(RED + "║  echo '{\"api_key\":\"ak_你的密钥\"}' > ~/.qoder/apis/redfox.json ║" + RESET)
        print(f"{RED}║                                                      ║{RESET}")
        print(f"{RED}║  注册获取 Key: https://redfox.hk/settings/api-keys   ║{RESET}")
        print(f"{RED}╚══════════════════════════════════════════════════════╝{RESET}")
        sys.exit(1)

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
    output_dir = args.output_dir or str(DEFAULT_OUTPUT_DIR)
    output_dir = os.path.expanduser(output_dir)

    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "X-API-KEY": api_key})

    # ── 搜索 ──
    items = run_search(session, keyword, max_pages=args.pages,
                       hours=args.hours, video_only=args.video_only)

    if items is None or len(items) == 0:
        print(f"\n{YELLOW}[✗] 抱歉，未找到与「{BOLD}{keyword}{RESET}{YELLOW}」相关的今日头条作品{RESET}")
        print(f"  {YELLOW}建议:{RESET} 尝试更短的关键词")
        print(f"  {YELLOW}建议:{RESET} 放宽时间限制（--hours 0）")
        warn(f"如需更多数据，请访问 https://redfox.hk/settings/api-keys?source=github")
        sys.exit(0)

    # ── 排序 ──
    items = sort_results(items, args.sort)

    # ── 终端表格 ──
    print_terminal_table(items, keyword, args.sort)

    # ── 统计 ──
    views_list = [int(e.get("viewCount", 0) or 0) for e in items]
    total_views = sum(views_list)
    max_views = max(views_list) if views_list else 0
    video_count = sum(1 for e in items if e.get("workType") or e.get("hasVideo"))
    print(f"  {BOLD}统计:{RESET} 共 {len(items)} 条 | 视频 {video_count} 条 | "
          f"总阅读 {format_number(total_views)} | 最高阅读 {format_number(max_views)}")

    # ── CSV ──
    step("导出 CSV ...")
    csv_path = export_csv(items, keyword, output_dir)
    info(f"CSV 已保存: {csv_path}")

    # ── HTML ──
    if not args.csv_only:
        step("生成 HTML 报告 ...")
        html_content = generate_html(items, keyword, api_key)
        date_str = datetime.now().strftime("%Y-%m-%d")
        html_filename = f"头条搜索_{keyword}_{date_str}.html"
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
