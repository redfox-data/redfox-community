#!/usr/bin/env python3
"""
stock-analysis 公共模块
========================
提取所有脚本共用的配置、工具函数，消除代码重复。

提供：
- 终端颜色 & 打印工具
- API 配置（queryWorkList 接口、Key 管理）
- 画像加载（JSON 格式）
- HTTP 请求封装（含状态码检查）
- STOCK_ANALYSTS 名单 + 微信号映射
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# ─── Windows 控制台 UTF-8 ──────────────────────────────────────────────────────────
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ─── 路径常量 ──────────────────────────────────────────────────────────────────────
SCRIPTS_DIR = Path(__file__).parent           # scripts/
SKILL_DIR = SCRIPTS_DIR.parent                # stock-analysis/
PROFILES_DIR = SKILL_DIR / "profiles"
OUTPUT_DIR = SKILL_DIR / "output"

# ─── API 配置 ──────────────────────────────────────────────────────────────────────
API_URL = "https://redfox.hk/story/api/gzhData/queryWorkList"
RECORD_API_URL = "https://redfox.hk/story/api/skill/record/save"
RECORD_SOURCE = "公众号股票大V蒸馏-GitHub"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"
ENV_KEY = "X_API_KEY"

STOCK_ANALYSTS = ["财躺平", "猫笔刀", "格兰投研", "投资明见", "终身黑白"]

# 分析师 → 公众号微信号映射（queryWorkList 接口用 account 字段精确定位）
ACCOUNT_IDS = {
    "财躺平": "gh_ad228eaec48a",
    "投资明见": "sinaxxm",
    "猫笔刀": "maobidao",
    "格兰投研": "gelantouyan",
    "终身黑白": "zshbtz",
}

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
    """获取 API Key：命令行 > 环境变量 > 配置文件"""
    if cli_key:
        return cli_key

    env_key = os.environ.get(ENV_KEY)
    if env_key:
        return env_key

    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8-sig"))
            key = data.get("api_key")
            if key:
                return key
        except Exception:
            pass

    error("未配置 API Key，请通过以下方式之一配置：")
    print(f"  1. 环境变量：$env:X_API_KEY=\"ak_你的密钥\"")
    print(f"  2. 配置文件：~/.qoder/apis/redfox.json")
    print(f"  3. 命令行参数：--api-key ak_你的密钥")
    print(f"\n  注册地址：https://www.redfox.hk/login")
    return None


# ─── 调用记录 ──────────────────────────────────────────────────────────────────────
def record_call(api_key, mode=None, authors=None):
    """
    向 redfox.hk 上报 skill 调用记录（fire-and-forget，失败不影响主流程）。

    Args:
        api_key: X_API_KEY
        mode: 分析模式（daily/team/sector/track/screen/portfolio/earnings/sync）
        authors: 参与分析的大V名称列表或字符串
    """
    if not api_key:
        return
    if not HAS_REQUESTS:
        return

    payload = {"source": RECORD_SOURCE}
    if mode:
        payload["mode"] = mode
    if authors:
        if isinstance(authors, list):
            payload["authors"] = ",".join(authors)
        else:
            payload["authors"] = str(authors)

    try:
        resp = requests.post(
            RECORD_API_URL,
            json=payload,
            headers={"Content-Type": "application/json", "REDFOX_API_KEY": api_key},
            timeout=5,
        )
        # 静默处理，不阻塞主流程
    except Exception:
        pass  # fire-and-forget


# ─── 画像加载 ──────────────────────────────────────────────────────────────────────
def find_profile(author):
    """查找指定分析师的风格画像（JSON 文本），优先精确匹配"""
    # 优先精确匹配
    for d in [PROFILES_DIR]:
        if not d.exists():
            continue
        for f in d.glob("*_profile.json"):
            profile_author = f.stem.replace("_profile", "")
            if author == profile_author:
                return f.read_text(encoding="utf-8")
    # 模糊匹配
    for d in [PROFILES_DIR]:
        if not d.exists():
            continue
        for f in d.glob("*_profile.json"):
            profile_author = f.stem.replace("_profile", "")
            if author in profile_author:
                warn(f"未精确匹配「{author}」，使用模糊匹配：{profile_author}")
                return f.read_text(encoding="utf-8")
    return None


def load_profile_json(author):
    """加载画像并解析为 dict，返回 (data, file_path) 或 (None, None)"""
    # 优先精确匹配
    for f in PROFILES_DIR.glob("*_profile.json"):
        profile_author = f.stem.replace("_profile", "")
        if author == profile_author:
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                return data, f
            except Exception as e:
                error(f"读取画像失败: {e}")
                return None, None
    # 模糊匹配
    for f in PROFILES_DIR.glob("*_profile.json"):
        profile_author = f.stem.replace("_profile", "")
        if author in profile_author:
            warn(f"未精确匹配「{author}」，使用模糊匹配：{profile_author}")
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                return data, f
            except Exception as e:
                error(f"读取画像失败: {e}")
                return None, None
    warn(f"未找到大V「{author}」的风格画像，将仅输出文章数据")
    return None, None


def detect_trading_type(profile):
    """从画像文本判断长线/短线"""
    if not profile:
        return "unknown"
    long_kw = ["价值投资", "护城河", "ROE", "长期持有", "估值", "自由现金流", "分红"]
    short_kw = ["涨停", "连板", "龙头", "打板", "情绪周期", "游资", "短线", "题材"]
    long_score = sum(profile.count(k) for k in long_kw)
    short_score = sum(profile.count(k) for k in short_kw)
    if short_score > long_score * 1.5:
        return "short"
    elif long_score > short_score * 1.5:
        return "long"
    return "mixed"


# ─── HTTP 请求封装 ──────────────────────────────────────────────────────────────────
def api_post(session, url, payload, timeout=20, context=""):
    """
    带 HTTP 状态码检查的 POST 请求。
    返回 (result_dict, should_continue_bool)
    - result_dict: API 返回的 JSON
    - should_continue_bool: False 表示应终止分页循环
    """
    try:
        if context:
            step(context)
        resp = session.post(url, json=payload, timeout=timeout)

        # HTTP 状态码检查
        if resp.status_code == 429:
            warn("HTTP 429 限频，等待5秒...")
            time.sleep(5)
            return None, True  # 继续重试
        elif resp.status_code == 401:
            error("HTTP 401 认证失败，请检查 API Key")
            return None, False
        elif resp.status_code == 403:
            error("HTTP 403 权限不足")
            return None, False
        elif resp.status_code >= 500:
            warn(f"HTTP {resp.status_code} 服务端错误，等待3秒重试...")
            time.sleep(3)
            return None, True
        elif resp.status_code != 200:
            warn(f"HTTP {resp.status_code} 非预期状态码")
            return None, False

        result = resp.json()
        return result, True

    except requests.exceptions.Timeout:
        warn(f"请求超时（{timeout}s）")
        return None, False
    except requests.exceptions.ConnectionError as e:
        warn(f"连接失败: {e}")
        return None, False
    except Exception as e:
        warn(f"请求异常: {e}")
        return None, False


def check_api_code(result):
    """
    检查 API 业务状态码，返回 (should_retry, should_break)
    - (True, False): 限频，应等待后重试
    - (False, True): 致命错误，应终止
    - (False, False): 正常
    """
    code = result.get("code")
    if code in (200, 2000):
        return False, False

    msg = result.get("msg", "")
    if code == 4004:
        warn("限频，等待5秒...")
        time.sleep(5)
        return True, False
    elif code in (3106, 3107):
        error(f"API错误: code={code}, msg={msg}")
        return False, True
    else:
        warn(f"API返回: code={code}, msg={msg}")
        return False, True


def extract_articles_from_data(result):
    """从 queryWorkList API 返回中提取文章列表（data.list）"""
    data_raw = result.get("data", {})
    if isinstance(data_raw, dict):
        return data_raw.get("list") or []
    elif isinstance(data_raw, list):
        return data_raw
    return []


def has_more_pages(result):
    """判断是否还有下一页（新接口 data.hasMore 字段）"""
    data_raw = result.get("data", {})
    if isinstance(data_raw, dict):
        return bool(data_raw.get("hasMore"))
    return False


def fetch_articles_paginated(api_key, account, account_name=None, days=7, count=50,
                             label=""):
    """
    通用分页拉取文章函数（queryWorkList 接口）。
    account: 公众号微信号（必填）
    account_name: 分析师名称（仅用于日志显示）
    """
    if not HAS_REQUESTS:
        error("缺少 requests 库，请执行: pip install requests")
        return []

    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "REDFOX_API_KEY": api_key})

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    payload = {
        "account": account,
        "offset": 0,
        "sortType": "_2",  # 按发布时间倒序
        "publishTimeStart": start_date.strftime("%Y-%m-%d"),
        "publishTimeEnd": end_date.strftime("%Y-%m-%d"),
        "source": RECORD_SOURCE,
    }
    if account_name:
        payload["accountName"] = account_name

    display_name = account_name or account
    all_articles = []
    fetched = 0
    consecutive_retries = 0
    MAX_CONSECUTIVE_RETRIES = 5

    while fetched < count:
        payload["offset"] = fetched

        ctx = f"{label}(offset={fetched})..." if label else f"获取{display_name}文章(offset={fetched})..."
        result, should_continue = api_post(session, API_URL, payload, context=ctx)

        if result is None:
            if not should_continue:
                break
            consecutive_retries += 1
            if consecutive_retries >= MAX_CONSECUTIVE_RETRIES:
                warn(f"连续重试 {MAX_CONSECUTIVE_RETRIES} 次仍失败，终止请求")
                break
            continue

        consecutive_retries = 0

        retry, break_now = check_api_code(result)
        if retry:
            consecutive_retries += 1
            if consecutive_retries >= MAX_CONSECUTIVE_RETRIES:
                warn(f"连续限频重试 {MAX_CONSECUTIVE_RETRIES} 次仍失败，终止请求")
                break
            continue
        if break_now:
            break

        consecutive_retries = 0

        articles = extract_articles_from_data(result)
        if not articles:
            break

        all_articles.extend(articles)
        fetched += len(articles)
        info(f"已获取 {fetched} 篇")

        # 用 hasMore 判断是否还有下一页
        if not has_more_pages(result):
            break
        time.sleep(1)

    return all_articles[:count]


def ensure_output_dir():
    """确保输出目录存在"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return OUTPUT_DIR
