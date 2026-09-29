#!/usr/bin/env python3
"""
X (Twitter) 订阅账号推文 Skill 核心脚本

子命令：
  fetch      拉取订阅账号推文（每日更新按日期过滤翻页 / 首次订阅拉第一页）
  following  拉取账号关注列表（订阅前探索）
  top        查询昨日热门账号榜（批量订阅推荐来源）

用法示例：
  python3 subscribe.py fetch --accounts "elonmusk,naval" --first --html
  python3 subscribe.py fetch --accounts "elonmusk,naval" --html            # 默认拉昨日
  python3 subscribe.py fetch --accounts "elonmusk" --date 2026-09-20 --html
  python3 subscribe.py following --account elonmusk            # 默认拉1页、展示前20个
  python3 subscribe.py following --account elonmusk --all      # 展示本页全部
  python3 subscribe.py top --category "科技软件" --top 20
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, time

# ─────────────────────────────────────────────────────────
# 常量与路径
# ─────────────────────────────────────────────────────────
TIMELINE_URL = "https://redfox.hk/story/api/x/userTimeline"
FOLLOWING_URL = "https://redfox.hk/story/api/x/userFollowing"
RANK_URL = "https://redfox.hk/story/api/x/hotAccount/rankList"
SOURCE = "X账号订阅-GitHub"

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_SKILL_DIR = os.path.dirname(_SCRIPT_DIR)
_ASSETS_DIR = os.path.join(_SKILL_DIR, "assets")
OUTPUT_DIR = os.path.join(_SKILL_DIR, "output")

MAX_ACCOUNTS_PER_TASK = 50   # 单个自动化任务最多账号数
MAX_ACCOUNTS_TOTAL = 100     # 总订阅上限
FIRST_MODE_LIMIT = 20        # 首次订阅每账号展示条数
FOLLOWING_DISPLAY_LIMIT = 20  # 关注列表首次最多展示条数
DEFAULT_MAX_PAGES = 5        # 每日更新每账号最多翻页数

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"


def _load_json(filename):
    with open(os.path.join(_ASSETS_DIR, filename), encoding="utf-8") as f:
        return json.load(f)


_cfg = _load_json("category_config.json")
UPDATE_HOUR = _cfg["update_rule"]["update_hour"]
UPDATE_MINUTE = _cfg["update_rule"]["update_minute"]
GENDERS = _cfg["genders"]
CATEGORIES = _cfg["categories"]
GENDER_LABELS = {g["value"]: g["zh"] for g in GENDERS}
ALL_CATEGORY_ZH = "全部行业"
CATEGORY_BY_ZH = {c["zh"]: c for c in CATEGORIES}


# ─────────────────────────────────────────────────────────
# API 客户端
# ─────────────────────────────────────────────────────────
def _get_api_key(explicit=None):
    api_key = (explicit or os.environ.get("REDFOX_API_KEY", "")).strip()
    if api_key:
        return api_key
    print(f"{RED}[ERROR] 未设置 REDFOX_API_KEY 环境变量{RESET}", file=sys.stderr)
    print("[HINT] 请运行: export REDFOX_API_KEY=<你的apikey>", file=sys.stderr)
    print("[HINT] 访问 https://redfox.hk/settings/api-keys?source=github 获取 API Key", file=sys.stderr)
    sys.exit(4)


def _api_post(url, payload, api_key, timeout=25):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "X-API-KEY": api_key,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return None, f"HTTP {e.code}: {body[:200]}"
    except urllib.error.URLError as e:
        return None, f"网络错误: {e.reason}"
    except Exception as e:  # noqa: BLE001
        return None, f"请求异常: {e}"


# ─────────────────────────────────────────────────────────
# 通用工具
# ─────────────────────────────────────────────────────────
def format_count(n):
    """89000000 -> 8,900w；210000 -> 21w；34000 -> 3.4w；1.2亿 -> 1.2亿"""
    try:
        n = int(float(str(n).replace(",", "")))
    except (ValueError, TypeError):
        return "—"
    if n >= 100_000_000:
        return f"{n / 100_000_000:.1f}亿"
    if n >= 10_000:
        w = n / 10_000
        if w >= 1000:
            return f"{w:,.0f}w"
        if w >= 100:
            return f"{w:.0f}w"
        s = f"{w:.1f}"
        return (s[:-2] if s.endswith(".0") else s) + "w"
    return f"{n:,}"


def parse_tweet_time(s):
    """解析 'Tue Sep 22 01:23:58 +0000 2026' -> aware datetime (UTC)。"""
    if not s:
        return None
    try:
        return datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y")
    except ValueError:
        return None


def to_local(dt):
    return dt.astimezone()


def extract_screen_name(text):
    """从 @handle / x.com/handle / twitter.com/handle 链接中提取 screen_name。"""
    t = (text or "").strip()
    # 1. 主页链接
    m = re.search(r"(?:x\.com|twitter\.com)/(@?[A-Za-z0-9_]{1,15})", t)
    if m:
        return m.group(1).lstrip("@")
    # 2. 文本中任意位置的 @handle（如“订阅 @elonmusk”）
    m = re.search(r"@([A-Za-z0-9_]{1,15})", t)
    if m:
        return m.group(1)
    # 3. 纯 handle
    m = re.fullmatch(r"[A-Za-z0-9_]{1,15}", t)
    if m:
        return m.group(0)
    # 4. 中英混排中紧邻中文的 handle（如“看看elonmusk关注了谁”）
    m = re.search(r"(?:^|[\u4e00-\u9fff])([A-Za-z][A-Za-z0-9_]{2,14})(?:$|[\u4e00-\u9fff])", t)
    if m:
        return m.group(1)
    return ""


def parse_accounts(raw):
    """解析逗号/空格/换行分隔的账号列表，去重保序。"""
    parts = re.split(r"[,\s，、;；]+", raw or "")
    seen, out = set(), []
    for p in parts:
        sn = extract_screen_name(p)
        if sn and sn.lower() not in seen:
            seen.add(sn.lower())
            out.append(sn)
    return out


def yesterday():
    return date.today() - timedelta(days=1)


def default_window():
    """默认时间窗口：最近一个 9:00 边界往前 24 小时（昨日 9:00 ~ 今日 9:00）。"""
    now = datetime.now().astimezone()
    today9 = now.replace(hour=9, minute=0, second=0, microsecond=0)
    end = today9 if now >= today9 else today9 - timedelta(days=1)
    return end - timedelta(days=1), end


def window_from_date(d):
    """以指定日期当天 9:00 为窗口起点，到次日 9:00 结束（用于 --date 历史查询）。"""
    start = datetime.combine(d, time(9, 0)).astimezone()
    return start, start + timedelta(days=1)


def latest_rank_date():
    """榜单每日 9:00 更新前一天数据：9 点后最新为昨日，9 点前为前日。"""
    now = datetime.now()
    updated = (now.hour, now.minute) >= (UPDATE_HOUR, UPDATE_MINUTE)
    return date.today() - timedelta(days=1 if updated else 2)


def match_category(text, explicit=None):
    if explicit:
        key = explicit.strip()
        if key in ("all", ALL_CATEGORY_ZH):
            return "all"
        if key in CATEGORY_BY_ZH:
            return key
        for c in CATEGORIES:
            if key in c["keywords"]:
                return "all" if c["zh"] == ALL_CATEGORY_ZH else c["zh"]
        print(f"{YELLOW}[WARN] 无法识别的行业分类「{explicit}」，已降级为全部行业{RESET}", file=sys.stderr)
        return "all"
    low = (text or "").lower()
    pairs = []
    for c in CATEGORIES:
        if c["zh"] == ALL_CATEGORY_ZH:
            continue
        for kw in c["keywords"]:
            pairs.append((kw.lower(), c["zh"]))
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    for kw, zh in pairs:
        if kw in low:
            return zh
    return "all"


def match_gender(text, explicit=None):
    if explicit:
        return explicit
    low = (text or "").lower()
    for g in GENDERS:
        if g["value"] == "all":
            continue
        for kw in g["keywords"]:
            if kw.lower() in low:
                return g["value"]
    return "all"


# ─────────────────────────────────────────────────────────
# 推文归一化
# ─────────────────────────────────────────────────────────
def normalize_tweet(tw, screen_name):
    dt = parse_tweet_time(tw.get("createdAt"))
    local_dt = to_local(dt) if dt else None
    tweet_id = tw.get("tweetId") or ""
    medias = tw.get("medias") or {}
    photos = (medias.get("photos") or []) if isinstance(medias, dict) else []
    photo_url = photos[0].get("url") if photos else None
    view_raw = tw.get("viewCount")
    try:
        view_n = int(str(view_raw).replace(",", "")) if view_raw not in (None, "") else 0
    except ValueError:
        view_n = 0
    like_n = tw.get("likeCount") or 0
    rt_n = tw.get("retweetCount") or 0
    reply_n = tw.get("replyCount") or 0
    quote_n = tw.get("quoteCount") or 0
    bm_n = tw.get("bookmarkCount") or 0
    return {
        "tweetId": tweet_id,
        "tweetUrl": f"https://x.com/{screen_name}/status/{tweet_id}" if tweet_id else "",
        "text": tw.get("text") or "",
        "createdAt": tw.get("createdAt") or "",
        "localTime": local_dt.strftime("%m-%d %H:%M") if local_dt else "",
        "localDate": str(local_dt.date()) if local_dt else "",
        "viewCount": view_n,
        "viewCountFmt": format_count(view_n),
        "likeCount": like_n,
        "likeCountFmt": format_count(like_n),
        "retweetCount": rt_n,
        "retweetCountFmt": format_count(rt_n),
        "replyCount": reply_n,
        "replyCountFmt": format_count(reply_n),
        "quoteCount": quote_n,
        "bookmarkCount": bm_n,
        "language": tw.get("language") or "",
        "photoUrl": photo_url,
        "isRetweet": bool(tw.get("retweetedTweet")),
        "isQuote": bool(tw.get("quoted")),
        "isSensitive": bool(tw.get("isSensitive")),
    }


# ─────────────────────────────────────────────────────────
# 智能总结（单账号高亮 + 整体总结）
# ─────────────────────────────────────────────────────────
def _engagement(t):
    return (t.get("likeCount") or 0) + (t.get("retweetCount") or 0) + (t.get("replyCount") or 0)


def build_summary(result):
    """生成事实性统计（最热账号排名）。

    语义层面的「今日主题总结 + 单账号主题/观点」由 AI 读取推文内容后写入
    `x_subscribe_ai_summary.json`，渲染 HTML 时由 generate_report.py 自动合并。
    """
    accounts = [a for a in result.get("accounts", []) if a.get("status") == "updated" and a.get("tweets")]
    if not accounts:
        return {"hasData": False}

    ranked = []
    for a in accounts:
        best = max(a["tweets"], key=_engagement) if a["tweets"] else None
        peak = _engagement(best) if best else 0
        ranked.append({
            "screenName": a["screenName"], "displayName": a["displayName"],
            "verified": bool(a.get("verified")), "tweetCount": len(a["tweets"]),
            "peak": peak, "peakTweet": best,
            "totalViews": sum(t.get("viewCount", 0) for t in a["tweets"]),
        })
    ranked.sort(key=lambda x: x["peak"], reverse=True)

    return {"hasData": True, "topAccount": ranked[0], "topAccounts": ranked[:3]}


def print_summary(result):
    s = result.get("summary") or build_summary(result)
    if not s.get("hasData"):
        return
    print("\n## 📝 总结\n")
    ta = s.get("topAccount")
    if ta and ta.get("peakTweet"):
        bt = ta["peakTweet"]
        print(f"**最热账号**：@{ta['screenName']}（{ta['displayName']}）峰值互动最高，"
              f"代表推文「{(bt.get('text') or '')[:60]}」获 {bt.get('likeCountFmt','—')} 赞 / "
              f"{bt.get('retweetCountFmt','—')} 转发 / {bt.get('viewCountFmt','—')} 浏览。")
    print("\n> 💡 今日主题与单账号观点总结由 AI 读取推文内容后写入 `x_subscribe_ai_summary.json`，"
          "渲染 HTML 时自动合并展示。")


# ─────────────────────────────────────────────────────────
# 子命令：fetch — 拉取订阅账号推文
# ─────────────────────────────────────────────────────────
def fetch_account(screen_name, target_start, target_end, first_mode, max_pages, api_key):
    """拉取单个账号推文。返回 account dict。

    target_start / target_end: 本地时区的感知 datetime，定义时间窗口（含起点、不含终点）。
    """
    acct = {
        "screenName": screen_name,
        "displayName": screen_name,
        "verified": False,
        "avatar": "",
        "followers": None,
        "profileUrl": f"https://x.com/{screen_name}",
        "status": "ok",
        "error": "",
        "hitCount": 0,
        "latestTweetDate": "",
        "tweets": [],
    }
    cursor = ""
    pages = 0
    hits = []
    latest_local_date = None

    while pages < max_pages:
        payload = {"screenName": screen_name, "source": SOURCE}
        if cursor:
            payload["cursor"] = cursor
        data, err = _api_post(TIMELINE_URL, payload, api_key)
        if err:
            acct["status"] = "error"
            acct["error"] = err
            return acct
        if data.get("code") != 2000:
            acct["status"] = "error"
            acct["error"] = f"接口异常 code={data.get('code')} msg={data.get('msg')}"
            return acct
        d = data.get("data") or {}
        user = d.get("user") or {}
        if user:
            acct["displayName"] = user.get("displayName") or acct["displayName"]
            acct["verified"] = bool(user.get("verified"))
            acct["avatar"] = user.get("avatar") or ""
            if user.get("followers") is not None:
                acct["followers"] = user.get("followers")
        timeline = d.get("timeline") or []
        if not timeline:
            if pages == 0:
                acct["status"] = "empty"
            break
        pages += 1

        if first_mode:
            # 首次订阅：直接取第一页（最多 20 条），不按时间过滤
            for tw in timeline[:FIRST_MODE_LIMIT]:
                nt = normalize_tweet(tw, screen_name)
                hits.append(nt)
                if nt["localDate"]:
                    ld = date.fromisoformat(nt["localDate"])
                    if latest_local_date is None or ld > latest_local_date:
                        latest_local_date = ld
            break

        # 每日更新模式：按「昨日 9:00 ~ 今日 9:00」时间窗口过滤 + 翻页规则
        page_dts = []
        page_hits = []
        for tw in timeline:
            nt = normalize_tweet(tw, screen_name)
            dt = parse_tweet_time(tw.get("createdAt"))
            ld = to_local(dt) if dt else None
            if ld is not None:
                page_dts.append(ld)
                if latest_local_date is None or ld.date() > latest_local_date:
                    latest_local_date = ld.date()
                if target_start <= ld < target_end:
                    page_hits.append(nt)
        hits.extend(page_hits)
        has_earlier = any(pd < target_start for pd in page_dts)
        if has_earlier:
            # 当页已包含早于窗口起点的推文 → 结束翻页
            break
        next_cursor = d.get("nextCursor") or ""
        if not next_cursor:
            break
        cursor = next_cursor

    acct["latestTweetDate"] = str(latest_local_date) if latest_local_date else ""
    acct["tweets"] = hits
    acct["hitCount"] = len(hits)

    if not first_mode:
        if hits:
            acct["status"] = "updated"
        elif latest_local_date and latest_local_date >= date.today() - timedelta(days=7):
            acct["status"] = "no_update_yesterday"
        else:
            acct["status"] = "no_update_7d"
    else:
        acct["status"] = "updated" if hits else "empty"
    return acct


def cmd_fetch(args):
    api_key = _get_api_key(args.api_key)
    accounts = parse_accounts(args.accounts)
    if not accounts:
        print(f"{RED}[ERROR] 请通过 --accounts 提供至少一个账号（@handle 或 x.com 链接）{RESET}", file=sys.stderr)
        sys.exit(1)
    if len(accounts) > MAX_ACCOUNTS_PER_TASK:
        print(f"{YELLOW}[WARN] 单任务最多 {MAX_ACCOUNTS_PER_TASK} 个账号，已截取前 {MAX_ACCOUNTS_PER_TASK} 个{RESET}", file=sys.stderr)
        accounts = accounts[:MAX_ACCOUNTS_PER_TASK]

    if args.date:
        target_start, target_end = window_from_date(date.fromisoformat(args.date))
    else:
        target_start, target_end = default_window()
    first_mode = bool(args.first)
    max_pages = 1 if first_mode else max(1, args.max_pages)

    print(f"{CYAN}[INFO] 模式：{'首次订阅' if first_mode else '每日更新'}｜时间窗口：{target_start.strftime('%Y-%m-%d %H:%M')} ~ {target_end.strftime('%Y-%m-%d %H:%M')}｜账号数：{len(accounts)}{RESET}")

    results = []
    for i, sn in enumerate(accounts, 1):
        print(f"{DIM}[{i}/{len(accounts)}] 拉取 @{sn} ...{RESET}")
        acct = fetch_account(sn, target_start, target_end, first_mode, max_pages, api_key)
        results.append(acct)
        if acct["status"] == "error":
            print(f"{RED}  ✗ 失败：{acct['error']}{RESET}")
            print(f"{YELLOW}  💡 该账号获取失败，请确认账号名是否正确（可从 X 主页链接获取 handle，"
                  f"例如 https://twitter.com/elonmusk 中的 elonmusk）{RESET}")
        else:
            print(f"{GREEN}  ✓ {acct['displayName']}：{acct['hitCount']} 条{RESET}")

    updated = [a for a in results if a["status"] == "updated"]
    no_yest = [a for a in results if a["status"] == "no_update_yesterday"]
    no_7d = [a for a in results if a["status"] == "no_update_7d"]
    errors = [a for a in results if a["status"] == "error"]
    empty = [a for a in results if a["status"] == "empty"]
    total_tweets = sum(a["hitCount"] for a in results)

    meta = {
        "mode": "first" if first_mode else "daily",
        "targetDate": target_end.date().isoformat(),
        "windowStart": target_start.strftime("%Y-%m-%d %H:%M"),
        "windowEnd": target_end.strftime("%Y-%m-%d %H:%M"),
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "totalAccounts": len(results),
        "updatedAccounts": len(updated),
        "noUpdateYesterday": len(no_yest),
        "noUpdate7d": len(no_7d),
        "errorAccounts": len(errors),
        "emptyAccounts": len(empty),
        "totalTweets": total_tweets,
    }
    result = {"meta": meta, "accounts": results}
    result["summary"] = build_summary(result)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = args.output or os.path.join(OUTPUT_DIR, "x_subscribe_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"{CYAN}[INFO] 数据文件：{out_path}{RESET}")

    if args.markdown:
        print_markdown(result)

    if args.html:
        script = os.path.join(_SCRIPT_DIR, "generate_report.py")
        subprocess.run([sys.executable, script, "--data", out_path], check=False)

    if not args.markdown and not args.html:
        print_terminal_summary(result)
    return result


def print_markdown(result):
    """输出 Markdown 格式（供 Agent 转述）。"""
    meta = result["meta"]
    accounts = result["accounts"]
    mode_label = "首次拉取" if meta["mode"] == "first" else f"时间窗口 {meta.get('windowStart', '')} ~ {meta.get('windowEnd', '')} 发帖"
    print(f"\n## 📊 订阅报告 · {mode_label}\n")
    print(f"| 项目 | 值 |")
    print(f"|------|-----|")
    print(f"| 订阅账号 | {meta['totalAccounts']} 个 |")
    print(f"| 有更新账号 | {meta['updatedAccounts']} 个 |")
    print(f"| 本次推文 | {meta['totalTweets']} 条 |")
    if meta["noUpdateYesterday"]:
        print(f"| 昨日无更新 | {meta['noUpdateYesterday']} 个 |")
    if meta["noUpdate7d"]:
        print(f"| 近7天无更新 | {meta['noUpdate7d']} 个 |")
    if meta["errorAccounts"]:
        print(f"| 拉取失败 | {meta['errorAccounts']} 个 |")

    for a in accounts:
        if a["status"] != "updated" or not a["tweets"]:
            continue
        fol = f"（粉丝: {format_count(a['followers'])}）" if a.get("followers") else ""
        verified = " ✅" if a.get("verified") else ""
        print(f"\n### ▸ {a['displayName']}{verified} @{a['screenName']}{fol}\n")
        print("| 推文摘要 | 浏览 | 点赞 | 转发 | 回复 | 发布时间 |")
        print("|---------|------|------|------|------|---------|")
        for t in a["tweets"]:
            text = t["text"].replace("|", "\\|").replace("\n", " ")
            if len(text) > 60:
                text = text[:60] + "..."
            prefix = "🔁 " if t["isRetweet"] else ("💬 " if t["isQuote"] else "")
            print(f"| {prefix}[{text}]({t['tweetUrl']}) | {t['viewCountFmt']} | {t['likeCountFmt']} "
                  f"| {t['retweetCountFmt']} | {t['replyCountFmt']} | {t['localTime']} |")

    folded_y = [a for a in accounts if a["status"] == "no_update_yesterday"]
    folded_7 = [a for a in accounts if a["status"] == "no_update_7d"]
    errs = [a for a in accounts if a["status"] == "error"]
    empt = [a for a in accounts if a["status"] == "empty"]
    if folded_y:
        print(f"\n> 昨日无更新（{len(folded_y)} 个）：" + "、".join(f"@{a['screenName']}" for a in folded_y))
    if folded_7:
        print(f"\n> 近7天无更新（{len(folded_7)} 个，已折叠）：" + "、".join(f"@{a['screenName']}" for a in folded_7))
    if empt:
        print(f"\n> 无法获取推文（{len(empt)} 个）：" + "、".join(f"@{a['screenName']}" for a in empt))
    if errs:
        print(f"\n> 拉取失败（{len(errs)} 个）：" + "、".join(f"@{a['screenName']}（{a['error'][:30]}）" for a in errs))

    print_summary(result)


def print_terminal_summary(result):
    meta = result["meta"]
    print(f"\n{BOLD}📊 拉取完成{RESET}")
    wd = f"{meta.get('windowStart', '')} ~ {meta.get('windowEnd', '')}"
    print(f"  模式：{'首次订阅' if meta['mode'] == 'first' else '每日更新'}｜时间窗口：{wd}")
    print(f"  账号：{meta['totalAccounts']} 个｜有更新：{meta['updatedAccounts']} 个｜推文：{meta['totalTweets']} 条")
    for a in result["accounts"]:
        icon = {"updated": "✓", "no_update_yesterday": "○", "no_update_7d": "◌",
                "error": "✗", "empty": "?"}.get(a["status"], "·")
        color = GREEN if a["status"] == "updated" else (RED if a["status"] == "error" else DIM)
        print(f"  {color}{icon} @{a['screenName']}（{a['displayName']}）：{a['hitCount']} 条{RESET}")

    print_summary(result)


# ─────────────────────────────────────────────────────────
# 子命令：following — 关注列表探索
# ─────────────────────────────────────────────────────────
def cmd_following(args):
    api_key = _get_api_key(args.api_key)
    screen_name = extract_screen_name(args.account)
    if not screen_name:
        print(f"{RED}[ERROR] 请提供有效的账号 handle 或主页链接{RESET}", file=sys.stderr)
        sys.exit(1)

    pages = max(1, args.pages)
    cursor = args.cursor or ""
    all_users = []
    next_cursor = ""
    more = False

    for p in range(pages):
        payload = {"screenName": screen_name, "source": SOURCE}
        if cursor:
            payload["cursor"] = cursor
        data, err = _api_post(FOLLOWING_URL, payload, api_key)
        if err:
            print(f"{RED}[ERROR] 请求失败：{err}{RESET}", file=sys.stderr)
            sys.exit(2)
        if data.get("code") != 2000:
            print(f"{RED}[ERROR] 接口异常 code={data.get('code')} msg={data.get('msg')}{RESET}", file=sys.stderr)
            print(f"{YELLOW}[HINT] 请确认账号名是否正确（可从 X 主页链接获取 handle，例如 https://twitter.com/elonmusk 中的 elonmusk）{RESET}", file=sys.stderr)
            sys.exit(2)
        d = data.get("data") or {}
        users = d.get("following") or []
        for u in users:
            all_users.append({
                "displayName": u.get("displayName") or "",
                "username": u.get("username") or "",
                "followers": u.get("followers"),
                "followersFmt": format_count(u.get("followers")),
                "description": u.get("description") or "",
                "avatar": u.get("avatar") or "",
                "profileUrl": f"https://x.com/{u.get('username')}" if u.get("username") else "",
            })
        more = bool(d.get("moreUsers"))
        next_cursor = d.get("nextCursor") or ""
        if not more or not next_cursor:
            break
        cursor = next_cursor

    out = {
        "screenName": screen_name,
        "total": len(all_users),
        "moreUsers": more,
        "nextCursor": next_cursor,
        "users": all_users,
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = args.output or os.path.join(OUTPUT_DIR, "x_following_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    total_fetched = len(all_users)
    show_all = bool(getattr(args, "all", False))
    limit = FOLLOWING_DISPLAY_LIMIT
    try:
        limit = int(getattr(args, "limit", FOLLOWING_DISPLAY_LIMIT) or FOLLOWING_DISPLAY_LIMIT)
    except (TypeError, ValueError):
        limit = FOLLOWING_DISPLAY_LIMIT
    if limit <= 0:
        limit = FOLLOWING_DISPLAY_LIMIT
    display_users = all_users if show_all else all_users[:limit]
    shown = len(display_users)

    suffix = "，已展示全部" if show_all else (f"，展示前 {shown} 个" if total_fetched > shown else "")
    print(f"\n{BOLD}👥 @{screen_name} 的关注列表（本次获取 {total_fetched} 个{suffix}）{RESET}")
    print(f"{'账号':<22}{'粉丝数':<12}{'简介'}")
    print("─" * 80)
    for u in display_users:
        desc = u["description"].replace("\n", " ")
        if len(desc) > 40:
            desc = desc[:40] + "..."
        name = f"{u['displayName']}"
        print(f"{name:<22}{u['followersFmt']:<12}{DIM}{desc}{RESET}")

    hidden = total_fetched - shown
    if hidden > 0:
        print(f"\n{CYAN}📄 本页还有 {hidden} 个未展示，回复「查看更多」展示全部（脚本加 --all）{RESET}")
    if more and next_cursor:
        print(f"{CYAN}⏭️ 还有下一页，回复「继续翻页」加载更多（脚本加 --cursor \"{next_cursor}\"）{RESET}")
    print(f"{DIM}[INFO] 数据文件：{out_path}{RESET}")
    return out


# ─────────────────────────────────────────────────────────
# 子命令：top — 昨日热门账号榜（批量订阅推荐）
# ─────────────────────────────────────────────────────────
def cmd_top(args):
    api_key = _get_api_key(args.api_key)
    category = match_category(args.query, args.category)
    gender = match_gender(args.query, args.gender)
    top_n = min(max(1, args.top), MAX_ACCOUNTS_TOTAL)
    rank_date = date.fromisoformat(args.date) if args.date else latest_rank_date()

    items = []
    pages_needed = (top_n + 19) // 20
    for page in range(1, pages_needed + 1):
        payload = {
            "pageNum": page,
            "rankDate": str(rank_date),
            "gender": gender,
            "category": category,
            "source": SOURCE,
        }
        data, err = _api_post(RANK_URL, payload, api_key)
        if err:
            print(f"{RED}[ERROR] 榜单请求失败：{err}{RESET}", file=sys.stderr)
            break
        if data.get("code") != 2000:
            print(f"{RED}[ERROR] 榜单接口异常 code={data.get('code')} msg={data.get('msg')}{RESET}", file=sys.stderr)
            break
        lst = (data.get("data") or {}).get("list") or []
        if not lst:
            break
        for raw in lst:
            profile_url = raw.get("profileUrl") or ""
            sn = extract_screen_name(profile_url)
            if not sn:
                continue
            items.append({
                "rank": raw.get("rankNo"),
                "screenName": sn,
                "fullName": raw.get("fullName") or sn,
                "profileUrl": profile_url,
                "pictureUrl": raw.get("pictureUrl") or "",
                "title": raw.get("title") or "",
                "biography": raw.get("biography") or "",
                "country": raw.get("countryName") or "",
                "xFollowers": raw.get("xFollowerCount"),
                "xFollowersFmt": format_count(raw.get("xFollowerCount")),
                "score": raw.get("xScore"),
            })
        if len(items) >= top_n:
            break

    items = items[:top_n]
    cat_label = ALL_CATEGORY_ZH if category == "all" else category
    gender_label = GENDER_LABELS.get(gender, "全部")
    out = {
        "rankDate": str(rank_date),
        "category": category,
        "categoryLabel": cat_label,
        "gender": gender,
        "genderLabel": gender_label,
        "total": len(items),
        "items": items,
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = args.output or os.path.join(OUTPUT_DIR, "x_top_accounts.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n{BOLD}📈 X 热门账号榜 · {cat_label} · {gender_label}（{rank_date}）Top {len(items)}{RESET}")
    print(f"{'排名':<6}{'账号':<24}{'handle':<18}{'粉丝数':<12}{'评分'}")
    print("─" * 80)
    for it in items:
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(it["rank"], str(it["rank"]))
        score = f"{round(float(it['score']))}/100" if it.get("score") else "—"
        print(f"{medal:<6}{it['fullName'][:20]:<24}{('@' + it['screenName'])[:16]:<18}{it['xFollowersFmt']:<12}{score}")

    handles = ",".join(it["screenName"] for it in items)
    print(f"\n{CYAN}📬 订阅提示：可订阅该榜单 Top 10/20/50，或直接订阅全部 {len(items)} 个账号{RESET}")
    print(f"{DIM}[INFO] screen_name 列表（可直接用于 fetch --accounts）：{RESET}")
    print(handles)
    print(f"{DIM}[INFO] 数据文件：{out_path}{RESET}")
    return out


# ─────────────────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="X (Twitter) 订阅账号推文工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_fetch = sub.add_parser("fetch", help="拉取订阅账号推文")
    p_fetch.add_argument("--accounts", required=True, help="账号列表，逗号分隔（@handle 或 x.com 链接）")
    p_fetch.add_argument("--date", default="", help="目标日期 YYYY-MM-DD（默认昨日）")
    p_fetch.add_argument("--first", action="store_true", help="首次订阅模式：拉第一页全部推文，不按日期过滤")
    p_fetch.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES, help="每日更新模式每账号最多翻页数（默认5）")
    p_fetch.add_argument("--markdown", action="store_true", help="输出 Markdown 格式")
    p_fetch.add_argument("--html", action="store_true", help="生成 HTML 日报")
    p_fetch.add_argument("--output", default="", help="JSON 输出路径")

    p_follow = sub.add_parser("following", help="拉取账号关注列表（订阅前探索）")
    p_follow.add_argument("--account", required=True, help="目标账号 handle 或主页链接")
    p_follow.add_argument("--pages", type=int, default=1, help="拉取页数（默认1，每页约20个）")
    p_follow.add_argument("--limit", type=int, default=FOLLOWING_DISPLAY_LIMIT, help="首次最多展示条数（默认20）")
    p_follow.add_argument("--all", action="store_true", help="展示已获取的全部账号（忽略 --limit）")
    p_follow.add_argument("--cursor", default="", help="翻页游标（从上次输出获取）")
    p_follow.add_argument("--output", default="", help="JSON 输出路径")

    p_top = sub.add_parser("top", help="查询昨日热门账号榜（批量订阅推荐）")
    p_top.add_argument("--query", default="", help="用户原始问题（自动解析行业/性别）")
    p_top.add_argument("--category", default=None, help="行业分类中文名（如 科技软件；默认全部行业）")
    p_top.add_argument("--gender", default=None, choices=["all", "male", "female"])
    p_top.add_argument("--top", type=int, default=20, help="取前 N 个账号（默认20，最多100）")
    p_top.add_argument("--date", default="", help="榜单日期 YYYY-MM-DD（默认昨日）")
    p_top.add_argument("--output", default="", help="JSON 输出路径")

    parser.add_argument("--api-key", default="", help="指定 API Key（默认读环境变量 REDFOX_API_KEY）")

    args = parser.parse_args()
    if args.command == "fetch":
        cmd_fetch(args)
    elif args.command == "following":
        cmd_following(args)
    elif args.command == "top":
        cmd_top(args)


if __name__ == "__main__":
    main()
