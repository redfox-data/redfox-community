#!/usr/bin/env python3
"""
X (Twitter) 企业家影响力榜数据抓取脚本
用法：
    python fetch_rank.py --query "给我看最新的 Twitter 企业家榜" --html
    python fetch_rank.py --date 2026-09-20 --page 2
输出：榜单 JSON（含 handle / isNew / 涨粉TOP3），--html 时自动生成报告。
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timedelta

import urllib.request
import urllib.error

API_URL = "https://redfox.hk/story/api/x/hotAccount/rankList"
SOURCE = "X企业家榜单-GitHub"  # 接口固定 source 参数
CATEGORY = "Business & Entrepreneurship"  # 接口固定请求参数，不对用户展示
UPDATE_HOUR, UPDATE_MINUTE, LOOKBACK_DAYS = 9, 0, 7
UPDATE_NOTE = "Twitter 企业家榜每日早上 9:00 更新前一日数据"

CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
          "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def _get_api_key():
    api_key = os.environ.get("REDFOX_API_KEY", "").strip()
    if api_key:
        return api_key
    print("[ERROR] 未设置 REDFOX_API_KEY 环境变量", file=sys.stderr)
    print("[HINT] 请运行: export REDFOX_API_KEY=<你的apikey>", file=sys.stderr)
    print("[HINT] 访问 https://redfox.hk/settings/api-keys?source=github 获取 API Key", file=sys.stderr)
    sys.exit(4)


def _api_post(payload, timeout=25):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-API-KEY": _get_api_key(),
    }
    req = urllib.request.Request(API_URL, data=json.dumps(payload).encode("utf-8"),
                                 headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[ERROR] HTTP {e.code}：{body[:200]}", file=sys.stderr)
        sys.exit(2)


def parse_page(text, explicit=None):
    if explicit:
        return max(1, int(explicit))
    m = re.search(r"第\s*([0-9]+|[一二三四五六七八九十])\s*页", text or "")
    if m:
        v = m.group(1)
        return CN_NUM.get(v, int(v) if v.isdigit() else 1)
    m = re.search(r"top\s*(\d+)", (text or "").lower())
    if m:
        return max(1, (int(m.group(1)) - 1) // 20 + 1)
    return 1


def parse_date(text, explicit=None):
    if explicit:
        return date.fromisoformat(explicit)
    t = text or ""
    if "前天" in t:
        return date.today() - timedelta(days=2)
    if "昨天" in t or "昨日" in t:
        return date.today() - timedelta(days=1)
    if "今天" in t or "今日" in t:
        return date.today()
    m = re.search(r"(20\d{2})\s*[-年/.]\s*(\d{1,2})\s*[-月/.]\s*(\d{1,2})", t)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    m = re.search(r"(\d{1,2})\s*[-月/.]\s*(\d{1,2})\s*日?", t)
    if m:
        return date(date.today().year, int(m.group(1)), int(m.group(2)))
    return None


def latest_rank_date():
    now = datetime.now()
    offset = 1 if (now.hour, now.minute) >= (UPDATE_HOUR, UPDATE_MINUTE) else 2
    return date.today() - timedelta(days=offset)


def fetch_page(rank_date, page):
    resp = _api_post({"pageNum": page, "rankDate": str(rank_date),
                      "gender": "all", "category": CATEGORY,
                      "source": SOURCE})
    if resp.get("code") != 2000:
        print(f"[ERROR] 接口返回异常 code={resp.get('code')} msg={resp.get('msg')}", file=sys.stderr)
        return None
    data = resp.get("data") or {}
    return data if data.get("list") else None


def resolve_date(target, page, warnings):
    today = date.today()
    if target is None:
        target = latest_rank_date()
    else:
        diff = (today - target).days
        if diff < 1:
            warnings.append("非常抱歉🙏，我们最新的是昨日的数据，将为您提供最接近您需求的昨日榜单。")
            target = latest_rank_date()
        elif diff > LOOKBACK_DAYS:
            warnings.append(f"非常抱歉🙏，目前榜单最多支持回溯「过去{LOOKBACK_DAYS}天」，我将为您查询最接近您需求的时间范围~")
            target = latest_rank_date()

    data = fetch_page(target, page)
    if data:
        return target, data
    start = latest_rank_date()
    for i in range(LOOKBACK_DAYS):
        cand = start - timedelta(days=i)
        data = fetch_page(cand, page)
        if data:
            if cand != target:
                warnings.append(f"「{target}」暂无榜单数据，已自动切换至最近可用日期 {cand}。")
            return cand, data
    return target, None


def _strip_emoji(s):
    return re.sub(r"[^\x20-\x7E一-鿿]", "", s or "").strip()


def _safe_json(s, default):
    cur = s
    for _ in range(3):
        if not isinstance(cur, str):
            break
        try:
            cur = json.loads(cur)
        except (ValueError, TypeError):
            return default
    if isinstance(default, dict) and not isinstance(cur, dict):
        return default
    if isinstance(default, list) and not isinstance(cur, list):
        return default
    return cur


def fmt_followers(n):
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "-"
    if n >= 100000000:
        return f"{n / 100000000:.1f}亿+"
    if n >= 10000:
        return f"{n // 10000:,}w+"
    return str(n)


def parse_growth_abs(s):
    """'+313.2K' -> 313200；解析失败返回 None。"""
    m = re.match(r"^([+-]?[\d.]+)\s*([KMB]?)$", str(s or "").strip(), re.IGNORECASE)
    if not m:
        return None
    mult = {"": 1, "K": 1000, "M": 1000000, "B": 1000000000}[m.group(2).upper()]
    return int(float(m.group(1)) * mult)


def handle_of(profile_url):
    m = re.search(r"twitter\.com/([^/?#]+)/?", profile_url or "")
    return m.group(1) if m else ""


def normalize_item(raw):
    badges = _safe_json(raw.get("badgesJson"), {}) or {}
    return {
        "rank": raw.get("rankNo"),
        "fullName": raw.get("fullName") or "-",
        "handle": handle_of(raw.get("profileUrl")),
        "profileUrl": raw.get("profileUrl") or "",
        "pictureUrl": raw.get("pictureUrl") or "",
        "title": raw.get("title") or "",
        "biography": raw.get("biography") or "",
        "country": raw.get("countryName") or "-",
        "countryCode": (raw.get("countryCode") or "").lower(),
        "industries": [_strip_emoji(c.get("root_name")) for c in (_safe_json(raw.get("categoriesJson"), []) or [])
                       if c.get("primary") and c.get("root_name")],
        "score": raw.get("xScore"),
        "growthPercentage": (raw.get("growthPercentage") or "").replace(" ", ""),
        "growthAbsolute": raw.get("growthAbsolute") or "",
        "growthAbsoluteNum": parse_growth_abs(raw.get("growthAbsolute")),
        "xFollowers": raw.get("xFollowerCount"),
        "xFollowersFmt": fmt_followers(raw.get("xFollowerCount")),
        "topics": badges.get("hasTopics") or "",
        "cause": badges.get("hasCause") or "",
        "isNew": False,
    }


def prev_day_names(rank_date, page):
    """取上一期同页账号名集合，用于标记 🆕 新上榜；取不到返回 None。"""
    for back in (1, 2):
        data = fetch_page(rank_date - timedelta(days=back), page)
        if data:
            return {x.get("fullName") for x in data.get("list", [])}
    return None


def main():
    parser = argparse.ArgumentParser(description="X (Twitter) 企业家影响力榜查询")
    parser.add_argument("--query", default="", help="用户原始问题（自动解析日期/页码）")
    parser.add_argument("--date", default=None, help="榜单日期 YYYY-MM-DD")
    parser.add_argument("--page", type=int, default=None, help="页码（每页 20 条）")
    parser.add_argument("--output", default=None, help="JSON 输出路径")
    parser.add_argument("--html", action="store_true", help="同时生成 HTML 报告")
    parser.add_argument("--no-new-check", action="store_true", help="跳过 🆕 新上榜标记（省一次接口调用）")
    args = parser.parse_args()

    page = parse_page(args.query, args.page)
    target = parse_date(args.query, args.date)

    warnings = []
    rank_date, data = resolve_date(target, page, warnings)
    if not data:
        print("[ERROR] 该日期暂无企业家榜数据，请更换日期后重试", file=sys.stderr)
        sys.exit(3)

    items = [normalize_item(x) for x in data.get("list", [])]

    if not args.no_new_check:
        prev = prev_day_names(rank_date, page)
        if prev is not None:
            for it in items:
                it["isNew"] = it["fullName"] not in prev

    ranked_growth = sorted([i for i in items if i.get("growthAbsoluteNum")],
                           key=lambda i: i["growthAbsoluteNum"], reverse=True)
    top_growth = [{
        "rank": i["rank"], "fullName": i["fullName"], "title": i["title"],
        "growthAbsolute": i["growthAbsolute"], "growthAbsoluteNum": i["growthAbsoluteNum"],
        "growthPercentage": i["growthPercentage"],
    } for i in ranked_growth[:3]]

    meta = {
        "rankDate": str(rank_date),
        "pageNum": data.get("pageNum", page),
        "pageSize": data.get("pageSize", 20),
        "pages": data.get("pages", 1),
        "total": data.get("total", len(items)),
        "updateNote": UPDATE_NOTE,
        "topGrowth": top_growth,
        "warnings": warnings,
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    result = {"meta": meta, "items": items}

    out_path = args.output or os.path.join(os.getcwd(), "entrepreneur_rank_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    for w in warnings:
        print(f"[WARN] {w}")
    print(f"[INFO] 数据日期：{meta['rankDate']}"
          f"｜第 {meta['pageNum']}/{meta['pages']} 页｜共 {meta['total']} 条")
    if top_growth:
        print("[INFO] 涨粉TOP3：" + "；".join(
            f"{g['fullName']} {g['growthAbsolute']}（{g['growthPercentage']}）" for g in top_growth))
    print(f"[INFO] 数据文件：{out_path}")

    if args.html:
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generate_report.py")
        subprocess.run([sys.executable, script, "--data", out_path], check=False)


if __name__ == "__main__":
    main()
