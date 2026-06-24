#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股公众号大V数据获取脚本
====================================
使用 dailyPublish 接口按日期查询49个固定A股公众号的文章数据。

固定19个A股个人大V账号（verifyName验证通过），按日期查询时只输出有更新文章的账号。

Usage:
    python3 fetch_astock_accounts.py
    python3 fetch_astock_accounts.py --date 2026-06-15
    python3 fetch_astock_accounts.py --date 2026-06-15 --api-key ak_xxx
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error


# ─── 配置 ─────────────────────────────────────────────────────────────────────────
DAILY_PUBLISH_URL = "https://redfox.hk/story/api/gzh/search/dailyPublish"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"
SOURCE = "A股公众号大V-GitHub"

# 固定19个A股个人大V账号（verifyName验证通过，按红狐指数排序）
FIXED_PERSONAL_ACCOUNTS = [
    "好运哥2008", "雷立刚本人", "孥孥的大树", "财经作家雷立刚", "凯恩斯",
    "冷眼局中人", "毛有话说", "EarlETF", "研报号角", "齐俊杰看财经",
    "laoduo", "思哲与创富", "A股研报君", "价值成长", "唐老师笔记",
    "金成探市", "丹湖渔翁", "远行者与碎冰匠", "胡斐投资办公室",
]

# 固定30个官媒/机构账号（按平均阅读量排序）
FIXED_OFFICIAL_ACCOUNTS = [
    "大红好运哥", "央视财经", "华夏基金", "金融时报", "中国基金报",
    "沙黾农", "券商中国", "吴晓波频道", "每日经济新闻", "财联社",
    "投资界", "第一财经", "21世纪经济报道", "ETF进化论", "界面新闻",
    "中国证券报", "证券时报", "中国财经报", "第一财经资讯", "上海证券报",
    "e公司", "腾讯财经", "期货日报", "侯勃说股", "财经",
    "中新经纬", "科奖中心", "天天基金网", "投资作业本Pro", "每财网",
]



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
    return None


def _http_post(url, body_dict, api_key):
    """发送 POST JSON 请求，返回解析后的 dict"""
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": api_key,
    }
    data = json.dumps(body_dict, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        return {"__http_error__": e.code}
    except Exception as e:
        return {"__error__": str(e)}


# ─── API调用：dailyPublish 一次获取全部账号当日文章 ─────────────────────────────────
def fetch_daily_publish(api_key, account_names, target_date):
    """调用 dailyPublish 接口，一次获取所有账号在指定日期的文章数据
    
    服务端直接按日期筛选，并自带 workUrl，无需二次查询。
    
    Args:
        api_key: 红狐API Key
        account_names: 账号名列表
        target_date: 目标日期 YYYY-MM-DD
    
    Returns:
        list[dict]: 账号列表（含works文章数据）
    """
    body = {
        "date": target_date,
        "accountNames": account_names,
        "source": SOURCE,
    }
    result = _http_post(DAILY_PUBLISH_URL, body, api_key)

    if "__http_error__" in result:
        print(f"  [!] HTTP错误: {result['__http_error__']}", file=sys.stderr)
        return []
    if "__error__" in result:
        print(f"  [!] 请求异常: {result['__error__']}", file=sys.stderr)
        return []
    if result.get("code") != 2000:
        print(f"  [!] API返回错误: code={result.get('code')}, msg={result.get('msg', '')}", file=sys.stderr)
        return []

    data = result.get("data", {})
    accounts = data.get("accounts", [])
    total_articles = data.get("totalArticles", 0)
    print(f"  API返回 {len(accounts)} 个账号，共 {total_articles} 篇文章", file=sys.stderr)
    
    return accounts


# ─── 数据处理 ──────────────────────────────────────────────────────────────────────
def process_account_data(account):
    """处理单个账号数据，提取核心字段
    
    dailyPublish 接口已按日期筛选文章，works 中即为当日文章，
    且自带 workUrl，无需二次查询补全。
    """
    works = account.get("works", [])
    account_name = account.get("accountName", "-")

    # dailyPublish 已按日期筛选，取第一篇（最新的）
    latest_work = works[0] if works else None

    result = {
        "accountName": account_name,
        "accountId": account.get("accountId", "-"),
        "avgReadCount": account.get("avgReadCount", 0),
        "redfoxIndex": account.get("redfoxIndex", 0),
        "description": account.get("description", ""),
    }

    if latest_work:
        result["latestArticle"] = {
            "title": latest_work.get("title", ""),
            "workUrl": latest_work.get("workUrl", ""),
            "clicksCount": latest_work.get("clicksCount"),
            "likeCount": latest_work.get("likeCount"),
            "commentCount": latest_work.get("commentCount"),
            "publishTime": latest_work.get("publishTime", ""),
        }
    else:
        result["latestArticle"] = None

    return result


def build_output(accounts_raw, target_date, total_found, dual_category=False):
    """构建最终输出JSON
    
    dailyPublish 接口已按日期筛选，accounts_raw 中仅包含当日有文章的账号。
    dual_category模式下，将账号分为个人大V和官媒两类分别输出。
    """
    if dual_category:
        # 分类模式：使用固定账号列表
        personal_accounts = [acc for acc in accounts_raw if acc.get('accountName', '') in FIXED_PERSONAL_ACCOUNTS]
        official_accounts = [acc for acc in accounts_raw if acc.get('accountName', '') in FIXED_OFFICIAL_ACCOUNTS]

        # 处理两类账号
        personal_processed = [process_account_data(acc) for acc in personal_accounts]
        official_processed = [process_account_data(acc) for acc in official_accounts]

        # 按平均阅读数降序排序
        personal_processed.sort(key=lambda x: x.get("avgReadCount", 0) or 0, reverse=True)
        official_processed.sort(key=lambda x: x.get("avgReadCount", 0) or 0, reverse=True)

        print(f"  分类：{len(personal_processed)} 个个人大V，{len(official_processed)} 个官媒/机构账号（{target_date}有文章）", file=sys.stderr)

        output = {
            "date": target_date,
            "totalAuthorsFound": total_found,
            "fixedPersonalAccounts": len(FIXED_PERSONAL_ACCOUNTS),
            "fixedOfficialAccounts": len(FIXED_OFFICIAL_ACCOUNTS),
            "personalMedia": {
                "total": len(personal_processed),
                "accounts": personal_processed,
            },
            "officialMedia": {
                "total": len(official_processed),
                "accounts": official_processed,
            },
        }
        return output
    else:
        # 非分类模式：只保留个人大V
        personal_accounts = [acc for acc in accounts_raw if acc.get('accountName', '') in FIXED_PERSONAL_ACCOUNTS]
        processed = [process_account_data(acc) for acc in personal_accounts]
        processed.sort(key=lambda x: x.get("avgReadCount", 0) or 0, reverse=True)

        output = {
            "date": target_date,
            "total": len(processed),
            "totalAuthorsFound": total_found,
            "accounts": processed,
        }
        return output


# ─── 主流程 ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="A股公众号大V — 获取A股领域大V账号数据与最新文章",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                        help="查询日期 YYYY-MM-DD (默认: 今天)")
    parser.add_argument("--api-key", help="API Key (不传则读取环境变量或配置文件)")
    parser.add_argument("--dual-category", action="store_true",
                        help="分类模式：将账号分为官媒/机构和大V两类，各类最多30个")

    args = parser.parse_args()

    # ── API Key ──
    api_key = get_api_key(cli_key=args.api_key)
    if not api_key:
        print("❌ 未找到 REDFOX_API_KEY，请配置环境变量：export REDFOX_API_KEY=<你的apikey>", file=sys.stderr)
        sys.exit(1)

    print(f"🔍 A股公众号大V · 查询日期: {args.date}", file=sys.stderr)

    # ── 合并固定49个账号 ──
    all_authors = list(FIXED_PERSONAL_ACCOUNTS) + list(FIXED_OFFICIAL_ACCOUNTS)
    print(f"📡 查询 {len(all_authors)} 个固定账号（19个个人大V + 30个官媒）在 {args.date} 的文章...", file=sys.stderr)

    # ── 1次API调用获取全部数据 ──
    accounts_raw = fetch_daily_publish(api_key, all_authors, args.date)
    print(f"  成功获取 {len(accounts_raw)} 个账号数据", file=sys.stderr)

    # ── 构建输出 ──
    output = build_output(accounts_raw, args.date, len(all_authors), dual_category=args.dual_category)

    # ── 缓存结果供订阅管理使用 ──
    if args.dual_category:
        cache_dir = Path(__file__).parent.parent / "cache"
        cache_dir.mkdir(exist_ok=True)
        cache_file = cache_dir / "last_dual_result.json"
        try:
            cache_file.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"  ✅ 榜单已缓存至 {cache_file}", file=sys.stderr)
        except OSError as e:
            print(f"  [!] 缓存写入失败: {e}", file=sys.stderr)

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
