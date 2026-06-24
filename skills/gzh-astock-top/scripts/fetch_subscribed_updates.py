#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股公众号订阅更新推送脚本
====================================
查询已订阅的官媒/大V账号最新文章数据，输出推送内容。
数据更新时间：每日 07:00 更新昨日爆款文章，建议 07:30 后运行。

Usage:
    python3 fetch_subscribed_updates.py
    python3 fetch_subscribed_updates.py --category official
    python3 fetch_subscribed_updates.py --category kol
    python3 fetch_subscribed_updates.py --api-key ak_xxx

    # 单个/批量临时查询（传入 accountId，逗号分隔）
    python3 fetch_subscribed_updates.py --accounts gh_xxx
    python3 fetch_subscribed_updates.py --accounts gh_xxx,gh_yyy,gh_zzz

    # 查询后交互式询问是否订阅（需 --interactive）
    python3 fetch_subscribed_updates.py --accounts gh_xxx --interactive
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import urllib.request
import urllib.error


# ─── 配置 ─────────────────────────────────────────────────────────────────────────
ACCOUNT_QUERY_URL = "https://redfox.hk/story/api/gzhUser/query"
CONFIG_DIR = Path.home() / ".qoder" / "apis"
CONFIG_FILE = CONFIG_DIR / "redfox.json"
ENV_KEY = "REDFOX_API_KEY"
SOURCE = "A股公众号大V-GitHub"

SKILL_DIR = Path(__file__).parent.parent
SUBSCRIPTIONS_FILE = SKILL_DIR / "subscriptions.json"

DATA_UPDATE_TIME = "07:00"  # 红狐平台每日数据更新时间


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


def _http_post(url, body_dict, api_key):
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


# ─── 订阅加载 ──────────────────────────────────────────────────────────────────────
def load_subscriptions(category=None):
    """加载订阅列表，返回 {official: [...], kol: [...]}"""
    if not SUBSCRIPTIONS_FILE.exists():
        return {"official": [], "kol": []}
    try:
        data = json.loads(SUBSCRIPTIONS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"official": [], "kol": []}

    if category == "official":
        return {"official": data.get("official", []), "kol": []}
    elif category == "kol":
        return {"official": [], "kol": data.get("kol", [])}
    else:
        return {"official": data.get("official", []), "kol": data.get("kol", [])}


# ─── 账号详情查询 ──────────────────────────────────────────────────────────────────
def fetch_account_details(api_key, account_ids):
    """批量查询账号最新文章，按 accountId 查询更精准"""
    if not account_ids:
        return []

    all_accounts = []
    batch_size = 5

    for i in range(0, len(account_ids), batch_size):
        batch = account_ids[i:i + batch_size]

        body = {
            "accountIds": batch,
            "source": SOURCE,
        }

        result = _http_post(ACCOUNT_QUERY_URL, body, api_key)

        if "__http_error__" in result:
            print(f"  [!] 查询账号HTTP错误: {result['__http_error__']}", file=sys.stderr)
            continue
        if "__error__" in result:
            print(f"  [!] 查询账号异常: {result['__error__']}", file=sys.stderr)
            continue
        if result.get("code") != 2000:
            print(f"  [!] 接口返回异常码: {result.get('code')}", file=sys.stderr)
            continue

        data = result.get("data", {})
        if isinstance(data, list):
            accounts = data
        elif isinstance(data, dict):
            accounts = data.get("list", data.get("accounts", []))
            if not accounts and data.get("accountName"):
                accounts = [data]
        else:
            accounts = []

        all_accounts.extend(accounts)
        time.sleep(0.3)

    return all_accounts


# ─── 数据提取 ──────────────────────────────────────────────────────────────────────
def extract_latest_article(works):
    """提取最新文章（优先有互动数据的）"""
    if not works:
        return None
    for work in works:
        if work.get("clicksCount") is not None:
            return work
    return works[0] if works else None


def format_number(n):
    if n is None:
        return "-"
    if isinstance(n, (int, float)) and n >= 10000:
        return f"{n/10000:.1f}w"
    return str(n) if n is not None else "-"


def build_update_item(sub_entry, account_detail):
    """合并订阅配置和账号详情，构建推送条目"""
    works = account_detail.get("works", [])
    latest = extract_latest_article(works)

    item = {
        "accountName": account_detail.get("accountName", sub_entry.get("accountName")),
        "accountId": account_detail.get("accountId", sub_entry.get("accountId")),
        "avgReadCount": account_detail.get("avgReadCount"),
        "redfoxIndex": account_detail.get("redfoxIndex"),
        "latestArticle": None,
    }

    if latest:
        item["latestArticle"] = {
            "title": latest.get("title", ""),
            "workUrl": latest.get("workUrl", ""),
            "clicksCount": latest.get("clicksCount"),
            "likeCount": latest.get("likeCount"),
            "commentCount": latest.get("commentCount"),
            "publishTime": latest.get("publishTime", ""),
        }

    return item


# ─── 主流程 ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="A股公众号订阅更新推送 — 查询已订阅账号最新文章",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--category", choices=["official", "kol"],
                        help="只查询某类订阅（不传则全部，--accounts 模式下无效）")
    parser.add_argument("--accounts",
                        help="临时查询指定账号（accountId，逗号分隔），不读取订阅列表")
    parser.add_argument("--interactive", action="store_true",
                        help="--accounts 查询完成后交互式询问是否添加到订阅")
    parser.add_argument("--api-key", help="API Key（不传则读取环境变量或配置文件）")

    args = parser.parse_args()

    # ── API Key ──
    api_key = get_api_key(cli_key=args.api_key)
    if not api_key:
        print("❌ 未找到 REDFOX_API_KEY", file=sys.stderr)
        sys.exit(1)

    # ── --accounts 临时查询模式 ──
    if args.accounts:
        account_ids = [a.strip() for a in args.accounts.split(",") if a.strip()]
        if not account_ids:
            print("❌ --accounts 未传入有效 accountId", file=sys.stderr)
            sys.exit(1)

        print(f"📡 临时查询 {len(account_ids)} 个账号...", file=sys.stderr)
        details_raw = fetch_account_details(api_key, account_ids)
        details_map = {acc.get("accountId"): acc for acc in details_raw}

        results = []
        for aid in account_ids:
            detail = details_map.get(aid)
            if detail:
                results.append(build_update_item({"accountId": aid, "accountName": detail.get("accountName", aid)}, detail))
            else:
                results.append({"accountId": aid, "error": "账号未找到或查询失败"})

        output = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "mode": "临时查询（非订阅）",
            "queried": len(account_ids),
            "results": results,
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))

        # ── 交互式询问是否订阅 ──
        if args.interactive:
            found = [r for r in results if "error" not in r]
            if not found:
                print("\n⚠️  没有查到有效账号，无法添加订阅。", file=sys.stderr)
                return

            print("\n" + "─" * 50, file=sys.stderr)
            print("以下账号查询成功，是否添加到订阅？", file=sys.stderr)
            for i, item in enumerate(found, 1):
                print(f"  {i}. {item.get('accountName')}（{item.get('accountId')}）", file=sys.stderr)
            print("\n请输入要订阅的序号（逗号分隔，回车跳过）：", file=sys.stderr)
            print("  类别选项：输入前缀 o:序号 表示官媒，k:序号 表示大V，直接序号默认大V", file=sys.stderr)
            print("  示例：o:1,k:2,3  →  1号订阅官媒，2号和3号订阅大V", file=sys.stderr)

            try:
                user_input = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n已跳过订阅。", file=sys.stderr)
                return

            if not user_input:
                print("已跳过订阅。", file=sys.stderr)
                return

            # 解析输入：o:1,2 k:3 或纯数字
            official_idxs = []
            kol_idxs = []
            for token in user_input.replace("，", ",").split(","):
                token = token.strip()
                if not token:
                    continue
                if token.lower().startswith("o:"):
                    try:
                        official_idxs.append(int(token[2:]) - 1)
                    except ValueError:
                        pass
                elif token.lower().startswith("k:"):
                    try:
                        kol_idxs.append(int(token[2:]) - 1)
                    except ValueError:
                        pass
                else:
                    try:
                        kol_idxs.append(int(token) - 1)
                    except ValueError:
                        pass

            # 读取现有订阅并写入
            subs_data = {"official": [], "kol": [], "updated_at": ""}
            if SUBSCRIPTIONS_FILE.exists():
                try:
                    subs_data = json.loads(SUBSCRIPTIONS_FILE.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, OSError):
                    pass

            existing_ids = {s["accountId"] for s in subs_data.get("official", []) + subs_data.get("kol", [])}
            added = []

            for idx in official_idxs:
                if 0 <= idx < len(found):
                    item = found[idx]
                    if item["accountId"] not in existing_ids:
                        subs_data["official"].append({
                            "accountId": item["accountId"],
                            "accountName": item["accountName"],
                            "avgReadCount": item.get("avgReadCount"),
                            "redfoxIndex": item.get("redfoxIndex"),
                        })
                        existing_ids.add(item["accountId"])
                        added.append(f"{item['accountName']}（官媒）")

            for idx in kol_idxs:
                if 0 <= idx < len(found):
                    item = found[idx]
                    if item["accountId"] not in existing_ids:
                        subs_data["kol"].append({
                            "accountId": item["accountId"],
                            "accountName": item["accountName"],
                            "avgReadCount": item.get("avgReadCount"),
                            "redfoxIndex": item.get("redfoxIndex"),
                        })
                        existing_ids.add(item["accountId"])
                        added.append(f"{item['accountName']}（大V）")

            if added:
                subs_data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                SUBSCRIPTIONS_FILE.write_text(
                    json.dumps(subs_data, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                print(f"\n✅ 已订阅 {len(added)} 个账号：{', '.join(added)}", file=sys.stderr)
            else:
                print("\n⚠️  未添加任何新订阅（序号无效或已订阅）。", file=sys.stderr)
        return

    # ── 加载订阅 ──
    subs = load_subscriptions(category=args.category)
    official_list = subs.get("official", [])
    kol_list = subs.get("kol", [])
    total = len(official_list) + len(kol_list)

    if total == 0:
        output = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "dataUpdateTime": DATA_UPDATE_TIME,
            "totalSubscribed": 0,
            "message": "暂无订阅账号，请先运行榜单查询并添加订阅",
            "official": [],
            "kol": [],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    print(f"📡 查询 {total} 个已订阅账号最新文章...", file=sys.stderr)
    print(f"  ├─ 官媒/机构：{len(official_list)} 个", file=sys.stderr)
    print(f"  └─ 个人大V：{len(kol_list)} 个", file=sys.stderr)

    # ── 查询账号详情 ──
    all_ids = (
        [acc["accountId"] for acc in official_list] +
        [acc["accountId"] for acc in kol_list]
    )
    details_raw = fetch_account_details(api_key, all_ids)
    details_map = {acc.get("accountId"): acc for acc in details_raw}

    print(f"  成功获取 {len(details_raw)} 个账号详情", file=sys.stderr)

    # ── 构建推送结果 ──
    official_updates = []
    for sub in official_list:
        detail = details_map.get(sub["accountId"])
        if detail:
            official_updates.append(build_update_item(sub, detail))
        else:
            official_updates.append({
                "accountName": sub["accountName"],
                "accountId": sub["accountId"],
                "avgReadCount": sub.get("avgReadCount"),
                "redfoxIndex": sub.get("redfoxIndex"),
                "latestArticle": None,
                "error": "账号详情获取失败",
            })

    kol_updates = []
    for sub in kol_list:
        detail = details_map.get(sub["accountId"])
        if detail:
            kol_updates.append(build_update_item(sub, detail))
        else:
            kol_updates.append({
                "accountName": sub["accountName"],
                "accountId": sub["accountId"],
                "avgReadCount": sub.get("avgReadCount"),
                "redfoxIndex": sub.get("redfoxIndex"),
                "latestArticle": None,
                "error": "账号详情获取失败",
            })

    output = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "dataUpdateTime": f"每日 {DATA_UPDATE_TIME} 更新昨日数据，建议 07:30 后运行",
        "totalSubscribed": total,
        "official": official_updates,
        "kol": kol_updates,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
