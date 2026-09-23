#!/usr/bin/env python3
"""
X (Twitter) 热门账号榜数据抓取脚本
用法：
    python fetch_rank.py --query "给我2026年4月25日的Twitter全品类日榜"
    python fetch_rank.py --query "宠物类女博主榜单" --page 2 --html
    python fetch_rank.py --date 2026-09-20 --gender female --category "萌宠动物"
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

# ─────────────────────────────────────────────────────────
# 加载外部静态配置（assets/）
# ─────────────────────────────────────────────────────────
_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")
_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(_SKILL_DIR, "output")  # 数据与报告统一落盘 output/，不污染 skill 根目录


def _load_json(filename):
    with open(os.path.join(_ASSETS_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


_cfg = _load_json("category_config.json")
UPDATE_HOUR = _cfg["update_rule"]["update_hour"]
UPDATE_MINUTE = _cfg["update_rule"]["update_minute"]
LOOKBACK_DAYS = _cfg["update_rule"]["lookback_days"]
UPDATE_NOTE = _cfg["update_rule"]["update_note"]
GENDERS = _cfg["genders"]
CATEGORIES = _cfg["categories"]

GENDER_LABELS = {g["value"]: g["zh"] for g in GENDERS}
ALL_CATEGORY_ZH = "全部行业"
CATEGORY_BY_ZH = {c["zh"]: c for c in CATEGORIES}

CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
          "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}


def _get_api_key():
    """从环境变量 REDFOX_API_KEY 获取 API Key。"""
    api_key = os.environ.get("REDFOX_API_KEY", "").strip()
    if api_key:
        return api_key
    print("[ERROR] 未设置 REDFOX_API_KEY 环境变量", file=sys.stderr)
    print("[HINT] 请运行: export REDFOX_API_KEY=<你的apikey>", file=sys.stderr)
    print("[HINT] 访问 https://redfox.hk/settings/api-keys?source=github 获取 API Key", file=sys.stderr)
    sys.exit(4)


def _api_post(payload, timeout=20):
    """使用原生 urllib 发送 HTTPS POST 请求，携带 X-API-KEY 鉴权。"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-API-KEY": _get_api_key(),
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[ERROR] HTTP {e.code}：{body[:200]}", file=sys.stderr)
        sys.exit(2)


# ─────────────────────────────────────────────────────────
# 自然语言解析：性别 / 行业 / 日期 / 页码
# ─────────────────────────────────────────────────────────
def match_gender(text, explicit=None):
    if explicit:
        return explicit
    low = (text or "").lower()
    for g in GENDERS:  # 配置中 female 先于 male，避免"女"被"男"误吞
        if g["value"] == "all":
            continue
        for kw in g["keywords"]:
            if kw.lower() in low:
                return g["value"]
    return "all"


def match_category(text, explicit=None):
    """返回接口 category 传参值："all" 或行业中文名。"""
    if explicit:
        key = explicit.strip()
        if key in ("all", ALL_CATEGORY_ZH):
            return "all"
        if key in CATEGORY_BY_ZH:
            return key
        for c in CATEGORIES:  # 支持传匹配关键词
            if key in c["keywords"]:
                return "all" if c["zh"] == ALL_CATEGORY_ZH else c["zh"]
        print(f"[WARN] 无法识别的行业分类「{explicit}」，已降级为全部行业", file=sys.stderr)
        return "all"
    low = (text or "").lower()
    pairs = []
    for c in CATEGORIES:
        if c["zh"] == ALL_CATEGORY_ZH:
            continue
        for kw in c["keywords"]:
            pairs.append((kw.lower(), c["zh"]))
    pairs.sort(key=lambda p: len(p[0]), reverse=True)  # 长词优先
    for kw, zh in pairs:
        if kw in low:
            return zh
    return "all"


def parse_page(text, explicit=None):
    if explicit:
        return max(1, int(explicit))
    m = re.search(r"第\s*([0-9]+|[一二三四五六七八九十])\s*页", text or "")
    if m:
        v = m.group(1)
        return CN_NUM.get(v, int(v) if v.isdigit() else 1)
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


# ─────────────────────────────────────────────────────────
# 日期计算与容错回退
# ─────────────────────────────────────────────────────────
def latest_rank_date():
    """每日早上 9:00 更新前一天榜单：9 点后最新为昨日，9 点前为前日。"""
    now = datetime.now()
    updated = (now.hour, now.minute) >= (UPDATE_HOUR, UPDATE_MINUTE)
    offset = 1 if updated else 2
    return date.today() - timedelta(days=offset)


def fetch_page(rank_date, gender, category, page):
    """请求单页榜单，返回 data dict；无数据或失败返回 None。"""
    payload = {
        "pageNum": page,
        "rankDate": str(rank_date),
        "gender": gender,
        "category": category,
        "source": "X账号榜-GitHub",
    }
    resp = _api_post(payload)
    if resp.get("code") != 2000:
        print(f"[ERROR] 接口返回异常 code={resp.get('code')} msg={resp.get('msg')}", file=sys.stderr)
        return None
    data = resp.get("data") or {}
    if not data.get("list"):
        return None
    return data


def resolve_date(target, gender, category, page, warnings):
    """校验目标日期并容错回退到最近可用日期。"""
    today = date.today()
    if target is None:
        target = latest_rank_date()
    else:
        diff = (today - target).days
        if diff < 1:
            warnings.append("非常抱歉🙏，我们最新的是昨日的数据，将为您提供最接近您需求的昨日热榜。")
            target = latest_rank_date()
        elif diff > LOOKBACK_DAYS:
            warnings.append(f"非常抱歉🙏，目前榜单最多支持回溯「过去{LOOKBACK_DAYS}天」，我将为您查询最接近您需求的时间范围~")
            target = latest_rank_date()

    data = fetch_page(target, gender, category, page)
    if data:
        return target, data

    # 目标日期暂无数据：自最新可用日期起向前扫描回退
    start = latest_rank_date()
    for i in range(LOOKBACK_DAYS):
        cand = start - timedelta(days=i)
        data = fetch_page(cand, gender, category, page)
        if data:
            if cand != target:
                warnings.append(f"「{target}」暂无榜单数据，已自动切换至最近可用日期 {cand}。")
            return cand, data
    return target, None


# ─────────────────────────────────────────────────────────
# 字段归一化
# ─────────────────────────────────────────────────────────
def _strip_emoji(s):
    return re.sub(r"[^\x20-\x7E\u4e00-\u9fff]", "", s or "").strip()


def _safe_json(s, default):
    """解析 JSON 字符串字段；兼容双重编码，类型不符时回退默认值。"""
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
    """111800000 -> 1.1亿+；31000000 -> 3,100w+；1800000 -> 180w+"""
    try:
        n = int(n)
    except (ValueError, TypeError):
        return "-"
    if n >= 100000000:
        return f"{n / 100000000:.1f}亿+"
    if n >= 10000:
        return f"{n // 10000:,}w+"
    return str(n)


def parse_count(s):
    """解析接口粉丝数字符串：4M -> 4000000；290K -> 290000；4.4M -> 4400000"""
    if not s or s == "-":
        return None
    m = re.match(r"^([\d.]+)\s*([KMB]?)$", str(s).strip(), re.IGNORECASE)
    if not m:
        return None
    mult = {"": 1, "K": 1000, "M": 1000000, "B": 1000000000}[m.group(2).upper()]
    return int(float(m.group(1)) * mult)


_NETWORK_ORDER = ["youtube", "tiktok", "instagram", "twitch", "linkedin", "facebook"]
_NETWORK_LABELS = {"youtube": "YouTube", "tiktok": "TikTok", "instagram": "Instagram",
                   "twitch": "Twitch", "linkedin": "LinkedIn", "facebook": "Facebook"}


def normalize_item(raw):
    cats = _safe_json(raw.get("categoriesJson"), [])
    industries, seen = [], set()
    for c in cats:
        if c.get("primary"):
            name = _strip_emoji(c.get("root_name"))
            if name and name not in seen:
                seen.add(name)
                industries.append(name)
    if not industries and cats:
        industries = [_strip_emoji(cats[0].get("root_name"))]

    networks = _safe_json(raw.get("networksJson"), {}) or {}
    others = []
    for key in _NETWORK_ORDER + [k for k in networks if k not in _NETWORK_ORDER]:
        v = networks.get(key)
        if not v or key == "twitter":
            continue
        fc = v.get("follower_count") or "-"
        cnt = parse_count(fc)
        others.append({
            "network": _NETWORK_LABELS.get(key, key.capitalize()),
            "followers": fc,
            "followersFmt": fmt_followers(cnt) if cnt is not None else fc,
            "profileUrl": v.get("profile_url") or "",
        })

    badges = _safe_json(raw.get("badgesJson"), {}) or {}
    growth = (raw.get("growthPercentage") or "").replace(" ", "")

    return {
        "rank": raw.get("rankNo"),
        "fullName": raw.get("fullName") or "-",
        "profileUrl": raw.get("profileUrl") or "",
        "pictureUrl": raw.get("pictureUrl") or "",
        "title": raw.get("title") or "",
        "biography": raw.get("biography") or "",
        "country": raw.get("countryName") or "-",
        "countryCode": (raw.get("countryCode") or "").lower(),
        "gender": raw.get("gender") or "",
        "industries": industries,
        "score": raw.get("xScore"),
        "growthPercentage": growth,
        "growthAbsolute": raw.get("growthAbsolute") or "",
        "xFollowers": raw.get("xFollowerCount"),
        "xFollowersFmt": fmt_followers(raw.get("xFollowerCount")),
        "otherNetworks": others,
        "topics": badges.get("hasTopics") or "",
        "cause": badges.get("hasCause") or "",
    }


def main():
    parser = argparse.ArgumentParser(description="X (Twitter) 热门账号榜查询")
    parser.add_argument("--query", default="", help="用户原始问题（自动解析日期/性别/行业/页码）")
    parser.add_argument("--date", default=None, help="榜单日期 YYYY-MM-DD")
    parser.add_argument("--gender", default=None, choices=["all", "male", "female"])
    parser.add_argument("--category", default=None, help="行业分类（中文名，如 萌宠动物；默认全部行业）")
    parser.add_argument("--page", type=int, default=None, help="页码（每页 20 条）")
    parser.add_argument("--output", default=None, help="JSON 输出路径")
    parser.add_argument("--html", action="store_true", help="同时生成 HTML 报告")
    args = parser.parse_args()

    gender = match_gender(args.query, args.gender)
    category = match_category(args.query, args.category)
    page = parse_page(args.query, args.page)
    target = parse_date(args.query, args.date)

    warnings = []
    rank_date, data = resolve_date(target, gender, category, page, warnings)
    if not data:
        print("[ERROR] 该筛选条件下暂无榜单数据，请更换日期/性别/行业后重试", file=sys.stderr)
        sys.exit(3)

    items = [normalize_item(x) for x in data.get("list", [])]
    meta = {
        "rankDate": str(rank_date),
        "gender": gender,
        "genderLabel": GENDER_LABELS.get(gender, "全部"),
        "category": category,
        "categoryLabel": ALL_CATEGORY_ZH if category == "all" else category,
        "pageNum": data.get("pageNum", page),
        "pageSize": data.get("pageSize", 20),
        "pages": data.get("pages", 1),
        "total": data.get("total", len(items)),
        "updateNote": UPDATE_NOTE,
        "warnings": warnings,
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    result = {"meta": meta, "items": items}

    out_path = args.output or os.path.join(OUTPUT_DIR, "x_top_account_data.json")
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    for w in warnings:
        print(f"[WARN] {w}")
    print(f"[INFO] 数据日期：{meta['rankDate']}｜性别：{meta['genderLabel']}｜行业：{meta['categoryLabel']}"
          f"｜第 {meta['pageNum']}/{meta['pages']} 页｜共 {meta['total']} 条")
    print(f"[INFO] 数据文件：{out_path}")

    if args.html:
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generate_report.py")
        subprocess.run([sys.executable, script, "--data", out_path], check=False)


if __name__ == "__main__":
    main()
