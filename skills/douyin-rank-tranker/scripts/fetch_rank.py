#!/usr/bin/env python3
"""
抖音每日最具影响力账号榜单数据抓取脚本
用法：
    python fetch_rank.py --period day --date 2026-04-27 --category 美食
    python fetch_rank.py --query "最新抖音日榜"
    python fetch_rank.py --query "美食类周榜"
    python fetch_rank.py --query "2026年4月月榜"
"""
import argparse
import json
import os
import re
import sys
import socket
import ssl
from datetime import date, datetime, timedelta

try:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except ImportError:
    print("[ERROR] 缺少 requests 库，请先运行：pip install requests", file=sys.stderr)
    sys.exit(1)

API_URL = "https://onetotenvip.com/story/dyData/query"
API_HOST = "onetotenvip.com"
API_PATH = "/story/dyData/query"

# ─────────────────────────────────────────────────────────
# 加载外部静态配置（assets/）
# ─────────────────────────────────────────────────────────
_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets")

def _load_json(filename: str) -> dict:
    path = os.path.join(_ASSETS_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return json.load(f)

_cat_cfg    = _load_json("category_config.json")
_period_cfg = _load_json("period_config.json")

CATEGORY_MAP      = _cat_cfg["category_map"]
EXACT_CATEGORIES  = set(_cat_cfg["exact_categories"])
CAT_DISPLAY       = _cat_cfg["cat_display"]

PERIOD_MAP    = _period_cfg["period_map"]
PERIOD_LABELS = _period_cfg["period_labels"]
PERIOD_KEYS   = _period_cfg["period_keys"]
SHORT_ALIASES = _period_cfg["short_aliases"]
LONG_ALIASES  = _period_cfg["long_aliases"]
UPDATE_RULES  = _period_cfg["update_rules"]


def _ssl_post_no_sni(path: str, payload: dict, host: str, timeout: int = 15) -> dict:
    """
    使用原生 socket + ssl 发送 HTTPS 请求，禁用 SNI 绕过某些服务器限制
    """
    payload_str = json.dumps(payload)
    
    request = f"POST {path} HTTP/1.1\r\n"
    request += f"Host: {host}\r\n"
    request += f"Content-Type: application/json\r\n"
    request += f"Content-Length: {len(payload_str)}\r\n"
    request += f"Accept: application/json\r\n"
    request += f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36\r\n"
    request += f"Connection: close\r\n"
    request += f"\r\n"
    request += payload_str

    # 创建 socket 连接
    sock = socket.create_connection((host, 443), timeout=timeout)
    
    # SSL 包裹，不传 server_hostname（禁用 SNI）
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    ssl_sock = context.wrap_socket(sock, server_hostname=None)
    
    try:
        ssl_sock.sendall(request.encode())
        
        # 接收响应
        response = b""
        while True:
            try:
                data = ssl_sock.recv(4096)
                if not data:
                    break
                response += data
            except:
                break
        
        # 解析 HTTP 响应体
        response_str = response.decode("utf-8", errors="replace")
        
        # 分离 header 和 body
        if "\r\n\r\n" in response_str:
            body = response_str.split("\r\n\r\n", 1)[1]
        elif "\n\n" in response_str:
            body = response_str.split("\n\n", 1)[1]
        else:
            body = response_str
        
        return json.loads(body)
    finally:
        ssl_sock.close()
        sock.close()




def _parse_period_keyword(text: str) -> str | None:
    for p, aliases in LONG_ALIASES.items():
        for a in aliases:
            if a in text:
                return p
    for p, char in SHORT_ALIASES.items():
        for i, ch in enumerate(text):
            if ch == char:
                before = text[i - 1] if i > 0 else " "
                after = text[i + 1] if i < len(text) - 1 else " "
                # 排除日期上下文中的月/周/日（如 "04月27日"、"2026年04月"）
                if before.isdigit() or after.isdigit():
                    continue
                if not (("\u4e00" <= before <= "\u9fff") or ("\u4e00" <= after <= "\u9fff")):
                    return p
    return None


UPDATE_RULES = {
    "day":   {"label": "日榜", "update_time": "每日17:30", "window_days": 7},
    "week":  {"label": "周榜", "update_time": "每周一17:30", "window_days": 21},
    "month": {"label": "月榜", "update_time": "每月2号9点", "window_days": 70},
}

# 日期校验结果
DATE_OK        = "ok"
DATE_FUTURE    = "future"     # 查询日期为当日或未来
DATE_TOO_EARLY = "too_early" # 超出回溯窗口


def _get_date_status(target_date: date, period: str) -> str:
    """
    判断目标日期是否在可用范围内。
    返回: "ok" / "future" / "too_early"
    """
    today = date.today()
    diff = (today - target_date).days
    window = UPDATE_RULES[period]["window_days"]
    if diff < 1:
        return DATE_FUTURE
    if diff > window:
        return DATE_TOO_EARLY
    return DATE_OK


def _latest_period_label(period: str) -> str:
    """返回用于提示语的最近一期中文标签，如「昨日」「上周」「上月」"""
    return {"day": "昨日", "week": "上周", "month": "上月"}[period]


def _window_human(period: str) -> str:
    """返回用于提示语的回溯范围中文，如「过去7天」「过去3周」「过去3月」"""
    w = UPDATE_RULES[period]["window_days"]
    unit = {"day": "天", "week": "周", "month": "月"}[period]
    return f"过去{w}{unit}"


def _get_date_range(period: str, offset: int = 1) -> tuple[str, str]:
    """
    获取指定周期的日期区间。
    period: day / week / month
    offset: 往前回溯的期数，默认 1（上一期）
    
    返回: (start_date, end_date) 格式为 "YYYY-MM-DD"
    """
    today = date.today()
    
    if period == "day":
        target = today - timedelta(days=offset)
        return str(target), str(target)
    
    elif period == "week":
        # 周榜：取 offset 期前的周一至周日
        days_since_monday = today.weekday()
        this_monday = today - timedelta(days=days_since_monday)
        target_monday = this_monday - timedelta(weeks=offset)
        target_sunday = target_monday + timedelta(days=6)
        return str(target_monday), str(target_sunday)
    
    elif period == "month":
        # 月榜：取 offset 期前的月初至月末
        month_offset = offset - 1
        year = today.year
        month = today.month - month_offset
        while month <= 0:
            month += 12
            year -= 1
        first_day = date(year, month, 1)
        # 月末：下月1号减1天
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        return str(first_day), str(last_day)
    
    target = today - timedelta(days=offset)
    return str(target), str(target)


def _get_latest_date(period: str, offset: int = 1) -> date:
    """获取指定周期的基础日期（日榜=目标日，周榜/月榜=起始日期）"""
    start, end = _get_date_range(period, offset)
    return date.fromisoformat(start)


def _is_data_updated(period: str) -> bool:
    """
    判断当前时间是否已更新最新一期的数据。
    日榜 17:30 更新，周榜周一 17:30 更新，月榜每月2号 9点 更新。
    """
    now = datetime.now()
    if period == "day":
        return now.hour > 17 or (now.hour == 17 and now.minute >= 30)
    elif period == "week":
        if now.weekday() == 0:
            return now.hour > 17 or (now.hour == 17 and now.minute >= 30)
        return True
    elif period == "month":
        if now.day == 2:
            return now.hour > 9 or (now.hour == 9 and now.minute >= 0)
        elif now.day > 2:
            return True
        return False
    return True


def _get_smart_offset(period: str) -> int:
    """根据当前是否已更新，返回合适的 offset（1 或 2）"""
    return 1 if _is_data_updated(period) else 2


def _parse_date_from_text(text: str, explicit_period: str | None = None) -> tuple[date | None, str | None]:
    """
    从文本中解析日期。
    """
    today = date.today()
    # YYYY-MM-DD / YYYY年MM月DD日
    m = re.search(r"(\d{4})[年\-\/](\d{1,2})[月\-\/](\d{1,2})", text)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3))), None
        except Exception:
            pass
    
    for kw, delta, require_period in [
        ("最新", None, True),
        ("今日", 1, False), ("今天", 1, False), ("昨日", 1, False),
        ("本周", 0, False), ("这周", 0, False), ("本月", 0, False), ("这个月", 0, False),
    ]:
        if kw in text:
            base_period = explicit_period or "day"
            
            if delta is None:
                if _is_data_updated(base_period):
                    delta = 1
                else:
                    delta = 2
            
            d = _get_latest_date(base_period, offset=delta)
            return d, explicit_period
    return None, None


def match_category(keyword: str) -> tuple[str, bool]:
    """
    将用户输入的自然语言关键词映射到接口支持的赛道类型。

    匹配策略（按优先级）：
    1. 精确匹配（大小写不敏感）
    2. 全文扫描：按 key 长度降序扫描 CATEGORY_MAP，找到最长命中词
    3. 兜底返回"全部"

    返回: (category, is_certain)
    - is_certain=True 表示命中了精确或完整关键词
    - is_certain=False 表示模糊降级，提示用户结果可能不准
    """
    kw = keyword.strip()
    if not kw:
        return "全部", False

    # 1. 精确命中（大小写不敏感）
    kw_lower = kw.lower()
    for k, v in CATEGORY_MAP.items():
        if k.lower() == kw_lower:
            return v, True

    # 2. 全文扫描（长词优先，避免"电影"被"电"误匹配）
    sorted_keys = sorted(CATEGORY_MAP.keys(), key=len, reverse=True)
    best_match = None
    best_len = 0
    for k in sorted_keys:
        if k.lower() in kw_lower and len(k) > best_len:
            best_match = CATEGORY_MAP[k]
            best_len = len(k)

    if best_match:
        return best_match, True

    # 3. 反向扫描：kw 是某个 key 的子串（例如用户输入"美妆博主"，key="美妆"）
    for k in sorted_keys:
        if kw_lower in k.lower() and len(kw_lower) >= 2:
            return CATEGORY_MAP[k], True

    # 4. 兜底
    return "全部", False


# ─────────────────────────────────────────────────────────
# 综合评分计算
# ─────────────────────────────────────────────────────────
def _parse_num(val) -> float:
    """将字符串或数字转为 float，失败返回 0"""
    if val is None or val == "-" or val == "":
        return 0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s:
        return 0
    try:
        if "w" in s.lower() or "万" in s:
            return float(s.lower().replace("w", "").replace("万", "")) * 10000
        return float(s)
    except Exception:
        return 0


def calculate_scores_batch(items: list) -> list:
    """
    批量计算评分并返回归一化后的分数
    评分规则（满分100）：使用对数归一化 ln(x+1)/ln(max+1)
    - 总粉丝数：20%
    - 新增粉丝：20%
    - 新增点赞：20%
    - 新增分享：20%
    - 新增评论：20%
    """
    import math
    
    followers_list = [_parse_num(i.get("followers") or i.get("fansCount") or i.get("fans")) for i in items]
    fans_list = [_parse_num(i.get("newFans") or i.get("fansGrowth")) for i in items]
    likes_list = [_parse_num(i.get("newLikes") or i.get("likedGrowth")) for i in items]
    shares_list = [_parse_num(i.get("newShares") or i.get("sharedGrowth")) for i in items]
    comments_list = [_parse_num(i.get("newComments") or i.get("commentsGrowth")) for i in items]
    
    max_followers = max(followers_list) if followers_list else 1
    max_fans = max(fans_list) if fans_list else 1
    max_likes = max(likes_list) if likes_list else 1
    max_shares = max(shares_list) if shares_list else 1
    max_comments = max(comments_list) if comments_list else 1
    
    results = []
    for item in items:
        followers = _parse_num(item.get("followers") or item.get("fansCount") or item.get("fans"))
        fans_growth = _parse_num(item.get("newFans") or item.get("fansGrowth"))
        likes_growth = _parse_num(item.get("newLikes") or item.get("likedGrowth"))
        shares_growth = _parse_num(item.get("newShares") or item.get("sharedGrowth"))
        comments_growth = _parse_num(item.get("newComments") or item.get("commentsGrowth"))
        
        def log_norm(val, max_val):
            if val <= 0 or max_val <= 1:
                return 0
            return math.log(val + 1) / math.log(max_val + 1) * 100
        
        norm_followers = log_norm(followers, max_followers)
        norm_fans = log_norm(fans_growth, max_fans)
        norm_likes = log_norm(likes_growth, max_likes)
        norm_shares = log_norm(shares_growth, max_shares)
        norm_comments = log_norm(comments_growth, max_comments)
        
        score = (
            norm_followers * 0.20 +
            norm_fans * 0.20 +
            norm_likes * 0.20 +
            norm_shares * 0.20 +
            norm_comments * 0.20
        )
        
        item["comprehensiveScore"] = round(score, 1)
    
    return items


def fetch(period: str, rank_date_start: str, rank_date_end: str, category: str) -> list[dict]:
    """调用抖音数据接口"""
    payload = {
        "dateType": PERIOD_MAP[period],
        "rankDate": rank_date_start,  # 只传周期开始时间，服务器自行计算结束时间
        "type": category if category else "全部",
        "source": "抖音每日最具影响力账号-GitHub",
    }
    try:
        result = _ssl_post_no_sni(API_PATH, payload, API_HOST, timeout=15)
    except socket.timeout:
        print("[ERROR] 请求超时，请检查网络后重试", file=sys.stderr)
        sys.exit(2)
    except (ConnectionRefusedError, ConnectionResetError, OSError) as e:
        print(f"[ERROR] 无法连接到数据源：{e}", file=sys.stderr)
        print("[HINT] 请稍后重试，或联系管理员检查数据源 onetotenvip.com 的可用性", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError:
        print("[ERROR] 返回数据格式异常（非 JSON）", file=sys.stderr)
        sys.exit(2)

    if result.get("code") != 2000:
        msg = result.get("msg", result.get("message", "未知错误"))
        print(f"[ERROR] 接口返回错误（code={result.get('code')}）：{msg}", file=sys.stderr)
        sys.exit(3)

    return result.get("data", [])


def _fmt_num(val) -> str:
    """将数字格式化为易读形式"""
    if val is None or val == "-":
        return "-"
    try:
        n = int(val)
    except (ValueError, TypeError):
        return str(val)
    if n == 0:
        return "-"
    if n >= 100_000_000:
        return f"{n/100_000_000:.1f}亿"
    if n >= 10_000:
        return f"{n/10_000:.1f}w"
    return str(n)


def _fmt_w(val) -> str:
    """将数字格式化为 w+ 格式，如 123456 → 1235w+，支持字符串输入"""
    if val is None or val == "-" or val == "":
        return "-"
    # 如果是字符串，先尝试解析
    s = str(val).strip()
    if not s:
        return "-"
    # 处理带 w/W 的字符串，如 "1170.51w"
    if 'w' in s.lower():
        try:
            n = float(s.lower().replace('w', '')) * 10000
            w_part = int(n) // 10000
            return f"{w_part}w+"
        except (ValueError, TypeError):
            return "-"
    # 处理带 亿 的字符串
    if '亿' in s:
        try:
            n = float(s.replace('亿', '')) * 100000000
            yi_part = n / 100000000
            return f"{yi_part:.1f}亿+"
        except (ValueError, TypeError):
            return "-"
    try:
        n = int(float(s))
    except (ValueError, TypeError):
        return "-"
    if n == 0:
        return "-"
    if n >= 10_000:
        return f"{n // 10000}w+"
    return str(n)


def build_markdown_table(items: list, period_label: str, date_start: str, date_end: str,
                          cat_display: str, total: int, displayed: int | None = None,
                          fuzzy_flag: bool = False, status: str = "ok") -> str:
    """构建 Markdown 格式榜单输出
    
    Args:
        items: 要展示的数据列表
        period_label: 周期标签（如"日榜"）
        date_start: 开始日期
        date_end: 结束日期
        cat_display: 赛道显示名
        total: 数据总数
        displayed: 实际展示的条数，默认为 len(items)
        fuzzy_flag: 是否模糊匹配赛道
    """
    # 从 UPDATE_RULES 中读取更新时间
    label_to_key = {v["label"]: k for k, v in UPDATE_RULES.items()}
    period_key = label_to_key.get(period_label, "day")
    ut = UPDATE_RULES.get(period_key, {}).get("update_time", "")
    # 日期显示：格式如 "2026年04月25日"
    date_display = f"{date_start[:4]}年{date_start[5:7]}月{date_start[8:]}日"

    # 实际展示条数
    actual_displayed = displayed if displayed is not None else len(items)
    remaining = total - actual_displayed if total > actual_displayed else 0

    # 严格按照 SKILL.md 标准输出模版
    # 全品类查询显示赛道列
    is_all_category = cat_display == "全品类"

    # 榜单说明：根据周期展示更新时间
    if period_key == "day":
        update_desc = "每日17:30更新"
        window_human = "过去7天"
        latest_desc = "昨日"
    elif period_key == "week":
        update_desc = "每周一17:30更新"
        window_human = "过去3周"
        latest_desc = "上周"
    else:
        update_desc = "每月2号9点更新"
        window_human = "过去3月"
        latest_desc = "上月"

    # 超出范围时的提示
    warning_msg = ""
    if status == "future":
        warning_msg = f"非常抱歉🙏，我们最新的是{latest_desc}的数据，将为您提供最接近您需求的{latest_desc}AI热榜。"
    elif status == "too_early":
        warning_msg = f"非常抱歉🙏，目前榜单最多支持回溯「{window_human}」，我将为您查询最接近您需求的时间范围~"

    lines = [
        f"📊 抖音{period_label} · {cat_display}",
        "",
        f"数据日期：{date_display}",
        f"共 {total} 个账号上榜（展示 TOP {actual_displayed} 条）",
        "",
    ]

    # 将 warning_msg 合并到榜单说明中
    if warning_msg:
        bill_desc = f"💡 榜单说明：{warning_msg}{update_desc}，与实时数据存在差异"
    else:
        bill_desc = f"💡 榜单说明：{update_desc}，与实时数据存在差异"

    lines.extend([
        bill_desc,
        "",
        "📐 综合评分：根据总粉丝数、新增粉丝增量、新增点赞/分享/评论加权计算，满分100",
        "",
    ])

    if is_all_category:
        lines.append("| 排名 | 账号名 | 赛道 | 综合评分 | 总粉丝数 | 新增粉丝 | 新增点赞 | 新增评论 | 新增分享 |")
        lines.append("|:---:|--------|:---:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|")
    else:
        lines.append("| 排名 | 账号名 | 综合评分 | 总粉丝数 | 新增粉丝 | 新增点赞 | 新增评论 | 新增分享 |")
        lines.append("|:---:|--------|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|")

    for item in items:
        account_name = item.get('accountName', '')
        profile_url = item.get('accountLink') or item.get('profileUrl', '')

        # 排名：1-3 使用 emoji
        rank = item.get('accountRanking') or item.get('rank', '-')
        if rank == 1:
            rank_str = "🥇 1"
        elif rank == 2:
            rank_str = "🥈 2"
        elif rank == 3:
            rank_str = "🥉 3"
        else:
            rank_str = str(rank)

        score = item.get('comprehensiveScore', '-')

        # 粉丝数格式化为 w+
        followers_raw = item.get('fansCount') or item.get('followers') or '-'
        followers = _fmt_w(followers_raw) if followers_raw != '-' else '-'

        new_fans = _fmt_w(item.get('fansGrowth') or item.get('newFans'))
        new_likes = _fmt_w(item.get('likedGrowth') or item.get('newLikes'))
        new_comments = _fmt_w(item.get('commentsGrowth') or item.get('newComments'))
        new_shares = _fmt_w(item.get('sharedGrowth') or item.get('newShares'))

        # 账号名转为可点击链接
        if profile_url:
            account_display = f"[{account_name}]({profile_url})"
        else:
            account_display = account_name

        if is_all_category:
            account_category = item.get('category', '-')
            lines.append(
                f"| {rank_str} | {account_display} | {account_category} | {score} | {followers} | "
                f"{new_fans} | {new_likes} | {new_comments} | {new_shares} |"
            )
        else:
            lines.append(
                f"| {rank_str} | {account_display} | {score} | {followers} | "
                f"{new_fans} | {new_likes} | {new_comments} | {new_shares} |"
            )

    # 追加更多操作和订阅服务
    remaining = total - actual_displayed
    cats = "个人才艺、生活vlog、财富理财、二次元、居家装修、学习教育、小剧场、数码科技、旅行、美食、化妆美容、动物、亲子、汽车、情感、三农、健康医学、潮流风尚、舞蹈才艺、颜值造型、人文、音乐、影视、身体锻炼、体育、明星娱乐、游戏"
    lines.extend([
        "",
        "⚡ **更多操作**",
        "",
        f"⏺️ 本次榜单完整共 **{total}** 条数据，是否需要查看剩余 **{remaining}** 条？",
        "",
        "📬 订阅服务",
        "",
        f"1️⃣ 是否需要订阅每日/周/月的抖音账号最新排名？",
        "",
        f"2️⃣ 是否需要订阅具体赛道的账号表现？我们支持：{cats}",
        "",
    ])

    return "\n".join(lines)


def to_normalized_json(items: list, period: str, date_start: str, date_end: str,
                       category: str) -> dict:
    """转换为规范化 JSON 结构"""

    def parse_inter(s) -> int:
        if not s:
            return 0
        s = str(s).strip()
        if "w" in s.lower():
            try:
                return int(float(s.lower().replace("w", "")) * 10000)
            except Exception:
                return 0
        try:
            return int(s)
        except Exception:
            return 0

    # 批量计算评分并按评分降序排序
    scored_items = calculate_scores_batch(items)
    
    normalized_list = []
    for item in scored_items:
        score = item.get("comprehensiveScore", 0)
        normalized_list.append({
            "rank": item.get("accountRanking") or item.get("rank"),
            "accountName": item.get("accountName", ""),
            "category": item.get("category") or category or "全部",
            "comprehensiveScore": score,
            "followers": item.get("fansCount") or item.get("followers") or None,
            "newNoteCount": item.get("newNoteCount") or 0,
            "newFans": item.get("fansGrowth") or item.get("newFans") or None,
            "newLikes": item.get("likedGrowth") or item.get("newLikes") or None,
            "newComments": item.get("commentsGrowth") or item.get("newComments") or None,
            "newShares": item.get("sharedGrowth") or item.get("newShares") or None,
            "newInteraction": parse_inter(item.get("newInteractionCount", "0")),
            "profileUrl": item.get("accountLink") or item.get("profileUrl", ""),
        })
    
    # 按综合评分降序排序
    normalized_list.sort(key=lambda x: x.get("comprehensiveScore", 0), reverse=True)
    
    # 更新排序后的排名
    for i, item in enumerate(normalized_list):
        item["rank"] = i + 1

    date_display = date_start if date_start == date_end else f"{date_start}至{date_end}"
    
    return {
        "period": period,
        "date": date_display,
        "dateStart": date_start,
        "dateEnd": date_end,
        "category": category,
        "total": len(normalized_list),
        "list": normalized_list,
    }


def parse_natural_query(query: str) -> dict:
    text = query.strip()
    result = {
        "period": "day",
        "date_start": str(_get_latest_date("day")),
        "date_end": str(_get_latest_date("day")),
        "category": "全部",
        "category_fuzzy": False,
        "warning": "",
        "date_fallback": False,
    }

    # 1. 解析周期
    period = _parse_period_keyword(text)
    if period:
        result["period"] = period
    else:
        period = "day"
        result["period"] = period

    # 2. 解析日期
    found_date, _ = _parse_date_from_text(text, explicit_period=period)
    smart_offset = _get_smart_offset(period)
    if found_date:
        start, end = _get_date_range(period, offset=smart_offset)
        # 如果用户指定了具体日期，则使用该日期作为区间
        result["date_start"] = str(found_date)
        result["date_end"] = str(found_date)
        result["date_explicit"] = True
    else:
        start, end = _get_date_range(period, offset=smart_offset)
        result["date_start"] = start
        result["date_end"] = end
        result["date_explicit"] = False

    # 3. 日期有效性校验
    target_date = date.fromisoformat(result["date_start"])
    status = _get_date_status(target_date, period)
    period_label_latest = _latest_period_label(period)
    window_human = _window_human(period)

    if status == DATE_FUTURE:
        # 当日或未来日期 → 切换至最近一期，并给出指定提示语
        off = _get_smart_offset(period)
        start, end = _get_date_range(period, offset=off)
        result["warning"] = (
            f"非常抱歉🙏，我们最新的是{period_label_latest}的数据，"
            f"将为您提供最接近您需求的{period_label_latest}AI热榜。"
        )
        result["date_start"] = start
        result["date_end"] = end
        result["date_fallback"] = True

    elif status == DATE_TOO_EARLY:
        # 超出回溯范围 → 切换至窗口内最近一期
        off = _get_smart_offset(period)
        start, end = _get_date_range(period, offset=off)
        result["warning"] = (
            f"非常抱歉🙏，目前榜单最多支持回溯「{window_human}」，"
            f"我将为您查询最接近您需求的时间范围~"
        )
        result["date_start"] = start
        result["date_end"] = end
        result["date_fallback"] = True

    else:
        # DATE_OK → 日期合法，无需处理；显式指定时也尊重用户选择
        pass

    # 4. 赛道匹配：直接对原始文本全文扫描，不做粗糙的正则剔除
    # 先剔除时间/周期相关的噪声词，避免干扰
    noise = r"(今日|今天|昨日|昨天|本周|这周|上周|本月|这个月|上个月|最新|最近|" \
            r"抖音|榜单|排行榜|排名|榜|日榜|周榜|月榜|查询|给我|看看|想要|要看|帮我)"
    kw = re.sub(noise, "", text)
    matched_type, fuzzy = match_category(kw)
    result["category"] = matched_type
    result["category_fuzzy"] = fuzzy

    return result


# ─────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="抖音每日最具影响力账号榜单抓取")
    parser.add_argument("--query", "-q", type=str, default="",
                        help="自然语言查询，如：最新美食周榜 / 2026年4月日榜")
    parser.add_argument("--period", choices=["day", "week", "month"], default=None)
    parser.add_argument("--date", default="", help="目标日期 YYYY-MM-DD")
    parser.add_argument("--category", default="", help="赛道类型")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--output", default="", help="JSON 输出文件路径")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    args = parser.parse_args()

    # 自然语言模式
    if args.query:
        parsed = parse_natural_query(args.query)
        period = parsed["period"]
        date_start = parsed["date_start"]
        date_end = parsed["date_end"]
        category = parsed["category"]
        category_fuzzy = parsed["category_fuzzy"]
        date_explicit = parsed.get("date_explicit", False)
        if parsed["warning"]:
            print(f"\n{parsed['warning']}\n", file=sys.stderr)
        if parsed["date_fallback"]:
            print(f"[WARN] 已回退至最近可用日期：{date_start} 至 {date_end}", file=sys.stderr)
        print(f"[INFO] 解析结果 → 周期={period} 日期={date_start}至{date_end} 赛道={category}", file=sys.stderr)
    else:
        period = args.period or "day"
        if args.date:
            date_start = args.date
            date_end = args.date
            date_explicit = True
        else:
            date_start, date_end = _get_date_range(period, _get_smart_offset(period))
            date_explicit = False
        category = args.category if args.category else "全部"
        category_fuzzy = False

    # 日期有效性校验
    target_date = date.fromisoformat(date_start)
    status = _get_date_status(target_date, period)
    period_label_latest = _latest_period_label(period)
    window_human = _window_human(period)

    if status == DATE_FUTURE:
        off = _get_smart_offset(period)
        start, end = _get_date_range(period, off)
        print(
            f"\n非常抱歉🙏，我们最新的是{period_label_latest}的数据，"
            f"将为您提供最接近您需求的{period_label_latest}AI热榜。\n",
            file=sys.stderr,
        )
        date_start = start
        date_end = end
    elif status == DATE_TOO_EARLY:
        off = _get_smart_offset(period)
        start, end = _get_date_range(period, off)
        print(
            f"\n非常抱歉🙏，目前榜单最多支持回溯「{window_human}」，"
            f"我将为您查询最接近您需求的时间范围~\n",
            file=sys.stderr,
        )
        date_start = start
        date_end = end

    limit = min(args.limit, 50)
    items = fetch(period, date_start, date_end, category)
    total = len(items)
    period_label = PERIOD_LABELS.get(period, "日榜")

    cat_display = CAT_DISPLAY.get(category, category + "类")

    # 先在全部数据上计算评分并排序
    normalized_all = to_normalized_json(items, period, date_start, date_end, category)
    
    # 保存时只保存 limit 条数据，保持 JSON 与对话展示一致
    normalized_output = normalized_all.copy()
    normalized_output["list"] = normalized_all["list"][:limit]
    
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(normalized_output, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 已保存：{args.output}", file=sys.stderr)

    if args.format == "json":
        print(json.dumps(items, ensure_ascii=False, indent=2))
    else:
        # 使用前 limit 条已评分数据
        display = normalized_all["list"][:limit]
        print(build_markdown_table(display, period_label, date_start, date_end,
                                    cat_display, total, limit, category_fuzzy, status))


if __name__ == "__main__":
    main()
