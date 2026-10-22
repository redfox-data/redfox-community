#!/usr/bin/env python3
"""
Facebook 主页帖子批量提取脚本（红狐数据 API）
用法：
    python fetch_posts.py --query "抓取 https://www.facebook.com/Meta 的帖子"
    python fetch_posts.py --url "https://www.facebook.com/Meta"  # facebook.com/用户名 格式
    python fetch_posts.py --url "<主页URL>" --continue        # 取下一页并与历史数据合并
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API_URL = "https://redfox.hk/story/api/fb/userPosts"
API_KEY_HUB = "https://redfox.hk/settings/api-keys?source=github"
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(SKILL_DIR, "output")

_URL_RE = re.compile(
    r"(?:https?://)?(?:[\w-]+\.)*(?:facebook\.com|fb\.com)/[^\s\u3000\"'<>，。；、）】」]+",
    re.IGNORECASE,
)
_TRAIL_PUNCT = "，。；、）】」》\"'<>"


def _setup_console():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def _get_api_key():
    api_key = os.environ.get("REDFOX_API_KEY", "").strip()
    if api_key:
        return api_key
    print("[ERROR] 未设置 REDFOX_API_KEY 环境变量", file=sys.stderr)
    print("[HINT] 请运行: export REDFOX_API_KEY=<你的apikey>（PowerShell: $env:REDFOX_API_KEY=\"...\"）", file=sys.stderr)
    print(f"[HINT] 访问 {API_KEY_HUB} 获取 API Key", file=sys.stderr)
    sys.exit(4)


def _api_post(payload, timeout=30):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "REDFOX_API_KEY": _get_api_key(),
    }
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[ERROR] HTTP {e.code}: {body[:300]}", file=sys.stderr)
        return None
    except urllib.error.URLError as e:
        print(f"[ERROR] 网络请求失败: {e.reason}", file=sys.stderr)
        return None
    except (ValueError, UnicodeDecodeError) as e:
        print(f"[ERROR] 响应解析失败: {e}", file=sys.stderr)
        return None


# ─────────────────────────────────────────────────────────
# URL 解析与规范化
# ─────────────────────────────────────────────────────────
def _strip_trailing_punct(url):
    url = url.rstrip(_TRAIL_PUNCT)
    # 剥离不配对的右括号（markdown 链接包装等场景）
    while url.endswith(")") and url.count("(") < url.count(")"):
        url = url[:-1]
    return url


def extract_url_from_text(text):
    m = re.search(r"\]\((https?://[^)\s]+)\)", text or "")
    if m:
        return m.group(1)
    m = _URL_RE.search(text or "")
    if not m:
        return ""
    return _strip_trailing_punct(m.group(0))


def normalize_url(raw):
    url = _strip_trailing_punct((raw or "").strip())
    if not url:
        return ""
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
        url = "https://" + url
    url = url.split("#", 1)[0]
    # 查询参数仅保留 id（profile.php?id=xxx），去掉 fbclid/ref 等跟踪参数
    if "?" in url:
        base, qs = url.split("?", 1)
        kept = [p for p in qs.split("&") if p.split("=", 1)[0].strip().lower() == "id"]
        url = base + (("?" + "&".join(kept)) if kept else "")
    return url.rstrip("/") or url


def extract_page_id(url):
    """从 URL 中提取主页数字 ID（存在时随请求一并传入，查询更快）。"""
    m = re.search(r"[?&]id=(\d+)", url)
    if m:
        return m.group(1)
    m = re.search(r"/people/[^/]+/(\d{6,})", url)
    if m:
        return m.group(1)
    m = re.search(r"/(\d{6,})/?$", url)
    if m:
        return m.group(1)
    return ""


def _check_url_kind(url):
    low = url.lower()
    if ("story_fbid" in low or "/permalink.php" in low or "/posts/" in low
            or "/videos/" in low or "watch?v=" in low or "/watch/" in low or "/reel/" in low):
        print("[WARN] 该链接疑似单条帖子/视频链接而非主页链接，接口可能返回空数据", file=sys.stderr)


def default_output_path(url, page_id):
    if page_id:
        slug = f"page_{page_id}"
    else:
        path = urllib.parse.urlparse(url).path.strip("/")
        seg = path.split("/")[-1] if path else ""
        slug = re.sub(r"[^\w\-]", "_", seg).strip("_")[:40] or "page"
    return os.path.join(OUTPUT_DIR, f"facebook_posts_{slug}.json")


# ─────────────────────────────────────────────────────────
# 接口请求与数据归一化
# ─────────────────────────────────────────────────────────
def fetch_page(url, page_id, cursor):
    """请求单页帖子，返回 (data, err)；err 非空表示失败。"""
    payload = {"url": url, "source": "Facebook主页提取-GitHub"}
    if page_id:
        payload["pageId"] = page_id
    if cursor:
        payload["cursor"] = cursor
    resp = _api_post(payload)
    if resp is None:
        return None, "网络请求失败，请检查网络后重试"
    code = resp.get("code")
    if code == 3105:
        return None, "API Key 已被禁用或无效（code=3105），请到红狐 hub 重新生成密钥"
    if code != 2000:
        msg = resp.get("msg") or resp.get("message") or "未知错误"
        return None, f"接口返回异常 code={code} msg={msg}"
    return resp.get("data") or {}, ""


def normalize_item(raw):
    author = raw.get("author") or {}
    media_urls = raw.get("mediaUrls") or []
    return {
        "postId": str(raw.get("postId") or ""),
        "permalink": raw.get("permalink") or "",
        "caption": raw.get("caption") or "",
        "likeCount": raw.get("likeCount"),
        "commentCount": raw.get("commentCount"),
        "mediaType": raw.get("mediaType"),
        "imageUrl": raw.get("imageUrl") or "",
        "mediaUrls": [str(u) for u in media_urls if u],
        "videoUrl": raw.get("videoUrl") or "",
        "videoDuration": raw.get("videoDuration"),
        "publishedAt": raw.get("publishedAt") or "",
        "feedbackId": raw.get("feedbackId") or "",
        "author": {
            "displayName": author.get("displayName") or "",
            "id": str(author.get("id") or ""),
        },
    }


def merge_items(old_items, new_items):
    """按 postId（缺省时用 permalink）去重，发布时间倒序。"""
    merged, seen = [], set()
    for it in list(new_items) + list(old_items):
        key = it.get("postId") or it.get("permalink")
        if not key or key in seen:
            continue
        seen.add(key)
        merged.append(it)
    merged.sort(key=lambda x: (x.get("publishedAt") or ""), reverse=True)
    return merged


# ─────────────────────────────────────────────────────────
# 数据落盘与输出
# ─────────────────────────────────────────────────────────
def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def save_json(path, meta, items):
    os.makedirs(os.path.dirname(path) or OUTPUT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "items": items}, f, ensure_ascii=False, indent=2)
    return path


def build_meta(url, page_id, pages, fetched, total, has_more, token, warnings):
    return {
        "url": url,
        "pageId": page_id or "",
        "pagesFetched": pages,
        "fetchedThisRun": fetched,
        "accumulatedTotal": total,
        "hasMore": has_more,
        "paginationToken": token,
        "warnings": warnings,
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def print_summary(meta, items, out_path):
    author = ""
    if items:
        author = (items[0].get("author") or {}).get("displayName", "")
    print(f"[INFO] 主页作者: {author or '-'}")
    print(f"[INFO] 主页: {meta['url']}" + (f"（pageId: {meta['pageId']}）" if meta["pageId"] else ""))
    print(f"[INFO] 本次获取: {meta['fetchedThisRun']} 条 ｜ 累计: {meta['accumulatedTotal']} 条"
          f" ｜ 还有更多: {'是' if meta['hasMore'] else '否'}")
    if meta["pagesFetched"] > 1:
        print(f"[INFO] 翻页: {meta['pagesFetched']} 页")
    print(f"[INFO] 数据文件: {out_path}")
    for w in meta["warnings"]:
        print(f"[WARN] {w}")


def main():
    _setup_console()
    parser = argparse.ArgumentParser(description="Facebook 主页帖子批量提取")
    parser.add_argument("--query", default="", help="用户原始问题（自动识别主页URL）")
    parser.add_argument("--url", default="", help="Facebook 主页 URL")
    parser.add_argument("--cursor", default="", help="显式指定分页游标（一般用 --continue）")
    parser.add_argument("--continue", dest="cont", action="store_true",
                        help="读取上次数据文件的游标取下一页并合并")
    parser.add_argument("--output", default="", help="JSON 输出路径（默认 output/facebook_posts_<主页标识>.json）")
    args = parser.parse_args()

    raw = args.url or extract_url_from_text(args.query)
    if not raw:
        print("[ERROR] 未识别到 Facebook 主页 URL，请提供主页链接", file=sys.stderr)
        print("[HINT] 例如: https://www.facebook.com/Meta（facebook.com/用户名 格式）", file=sys.stderr)
        sys.exit(1)
    _check_url_kind(raw)
    url = normalize_url(raw)
    page_id = extract_page_id(url)
    out_path = args.output or default_output_path(url, page_id)
    warnings = []

    old_items = []
    cursor = args.cursor
    if args.cont:
        prev = load_json(out_path)
        if prev is None:
            print(f"[ERROR] 未找到上次的数据文件 {out_path}，请先执行一次提取", file=sys.stderr)
            sys.exit(3)
        old_items = prev.get("items") or []
        prev_meta = prev.get("meta") or {}
        cursor = args.cursor or prev_meta.get("paginationToken", "")
        if not cursor:
            warnings.append("已无更多数据（上次分页令牌为空）")
            meta = build_meta(url, page_id, 0, 0, len(old_items), False, "", warnings)
            save_json(out_path, meta, old_items)
            print_summary(meta, old_items, out_path)
            return

    data, err = fetch_page(url, page_id, cursor)
    if err:
        print(f"[ERROR] {err}", file=sys.stderr)
        sys.exit(2)
    new_items = [normalize_item(x) for x in data.get("items") or []]
    token = (data.get("paginationToken") or "").strip()
    has_more = bool(token)
    if not new_items and not has_more and not old_items:
        print("[ERROR] 该主页暂无可用帖子数据，请确认 URL 正确且主页为公开状态", file=sys.stderr)
        sys.exit(3)

    merged = merge_items(old_items, new_items)
    meta = build_meta(url, page_id, 1, len(new_items), len(merged), has_more, token, warnings)
    save_json(out_path, meta, merged)
    print_summary(meta, merged, out_path)


if __name__ == "__main__":
    main()
