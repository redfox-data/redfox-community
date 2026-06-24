#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股公众号订阅管理脚本
====================================
管理官媒/大V账号订阅，支持按榜单序号添加/删除/查看订阅。

Usage:
    # 查看当前订阅
    python3 manage_subscriptions.py --action list

    # 从官媒榜单添加订阅（序号1,3,5）
    python3 manage_subscriptions.py --action add --category official --indexes 1,3,5

    # 从大V榜单添加订阅（序号2,4）
    python3 manage_subscriptions.py --action add --category kol --indexes 2,4

    # 删除订阅（按账号名）
    python3 manage_subscriptions.py --action remove --names 央视财经,金融时报

    # 清空某类订阅
    python3 manage_subscriptions.py --action clear --category official

    # 基于上次榜单数据快速添加（需先运行过 fetch_astock_accounts.py --dual-category）
    python3 manage_subscriptions.py --action add --category kol --indexes 1,2,3 --from-cache
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path


SKILL_DIR = Path(__file__).parent.parent
SUBSCRIPTIONS_FILE = SKILL_DIR / "subscriptions.json"
CACHE_FILE = SKILL_DIR / "cache" / "last_dual_result.json"


# ─── 订阅文件管理 ───────────────────────────────────────────────────────────────
def load_subscriptions():
    if not SUBSCRIPTIONS_FILE.exists():
        return {"official": [], "kol": [], "updated_at": ""}
    try:
        return json.loads(SUBSCRIPTIONS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"official": [], "kol": [], "updated_at": ""}


def save_subscriptions(data):
    data["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    SUBSCRIPTIONS_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_cache():
    """加载上次 --dual-category 运行结果"""
    if not CACHE_FILE.exists():
        return None
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ─── 动作实现 ──────────────────────────────────────────────────────────────────
def action_list(subs):
    """展示当前订阅"""
    official = subs.get("official", [])
    kol = subs.get("kol", [])
    updated = subs.get("updated_at", "未更新")

    print(f"\n📋 当前订阅列表（更新时间：{updated}）")
    print(f"\n【官媒/机构账号】共 {len(official)} 个")
    if official:
        for i, acc in enumerate(official, 1):
            print(f"  {i}. {acc['accountName']}（{acc['accountId']}）")
    else:
        print("  （暂无订阅）")

    print(f"\n【个人大V账号】共 {len(kol)} 个")
    if kol:
        for i, acc in enumerate(kol, 1):
            print(f"  {i}. {acc['accountName']}（{acc['accountId']}）")
    else:
        print("  （暂无订阅）")

    result = {
        "official": official,
        "kol": kol,
        "officialCount": len(official),
        "kolCount": len(kol),
        "updatedAt": updated,
    }
    print("\n" + json.dumps(result, ensure_ascii=False, indent=2))


def action_add(subs, category, indexes, source_accounts):
    """按序号添加订阅"""
    if category not in ("official", "kol"):
        print(f"❌ category 参数无效，只支持 official 或 kol", file=sys.stderr)
        sys.exit(1)

    existing_ids = {acc["accountId"] for acc in subs.get(category, [])}
    added = []
    skipped = []

    for idx in indexes:
        if idx < 1 or idx > len(source_accounts):
            print(f"  ⚠️ 序号 {idx} 超出范围（共{len(source_accounts)}个）", file=sys.stderr)
            continue

        acc = source_accounts[idx - 1]
        account_id = acc.get("accountId", "")
        account_name = acc.get("accountName", "")

        if account_id in existing_ids:
            skipped.append(account_name)
            continue

        entry = {
            "accountId": account_id,
            "accountName": account_name,
            "avgReadCount": acc.get("avgReadCount"),
            "redfoxIndex": acc.get("redfoxIndex"),
        }
        subs[category].append(entry)
        existing_ids.add(account_id)
        added.append(account_name)

    save_subscriptions(subs)

    category_label = "官媒/机构" if category == "official" else "个人大V"
    if added:
        print(f"✅ 已添加 {len(added)} 个{category_label}订阅：{', '.join(added)}")
    if skipped:
        print(f"ℹ️ 已跳过（已订阅）：{', '.join(skipped)}")

    result = {
        "action": "add",
        "category": category,
        "added": added,
        "skipped": skipped,
        "totalNow": len(subs[category]),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def action_remove(subs, names):
    """按账号名删除订阅"""
    removed = {"official": [], "kol": []}
    name_set = set(names)

    for cat in ("official", "kol"):
        before = subs.get(cat, [])
        after = [acc for acc in before if acc["accountName"] not in name_set]
        removed_names = [acc["accountName"] for acc in before if acc["accountName"] in name_set]
        subs[cat] = after
        removed[cat] = removed_names

    save_subscriptions(subs)

    total_removed = sum(len(v) for v in removed.values())
    if total_removed:
        print(f"✅ 已删除 {total_removed} 个订阅")
        for cat, names_list in removed.items():
            if names_list:
                label = "官媒/机构" if cat == "official" else "个人大V"
                print(f"  [{label}] {', '.join(names_list)}")
    else:
        print("ℹ️ 未找到匹配的订阅账号")

    print(json.dumps({"action": "remove", "removed": removed}, ensure_ascii=False, indent=2))


def action_clear(subs, category):
    """清空某类订阅"""
    if category not in ("official", "kol"):
        print(f"❌ category 参数无效，只支持 official 或 kol", file=sys.stderr)
        sys.exit(1)

    count = len(subs.get(category, []))
    subs[category] = []
    save_subscriptions(subs)

    label = "官媒/机构" if category == "official" else "个人大V"
    print(f"✅ 已清空 {count} 个{label}订阅")
    print(json.dumps({"action": "clear", "category": category, "cleared": count}, ensure_ascii=False, indent=2))


# ─── 主流程 ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="A股公众号订阅管理 — 管理官媒/大V账号订阅",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--action", required=True,
                        choices=["list", "add", "remove", "clear"],
                        help="操作类型：list/add/remove/clear")
    parser.add_argument("--category", choices=["official", "kol"],
                        help="账号分类：official=官媒/机构，kol=个人大V")
    parser.add_argument("--indexes", help="榜单序号，逗号分隔，如 1,3,5")
    parser.add_argument("--names", help="账号名称，逗号分隔（用于remove）")
    parser.add_argument("--from-cache", action="store_true",
                        help="从上次 --dual-category 的缓存结果中读取榜单")
    parser.add_argument("--榜单-json", dest="list_json",
                        help="直接传入榜单JSON字符串（供AI解析后调用）")

    args = parser.parse_args()
    subs = load_subscriptions()

    if args.action == "list":
        action_list(subs)
        return

    if args.action == "clear":
        if not args.category:
            print("❌ --action clear 需要指定 --category", file=sys.stderr)
            sys.exit(1)
        action_clear(subs, args.category)
        return

    if args.action == "remove":
        if not args.names:
            print("❌ --action remove 需要指定 --names", file=sys.stderr)
            sys.exit(1)
        names = [n.strip() for n in args.names.split(",") if n.strip()]
        action_remove(subs, names)
        return

    if args.action == "add":
        if not args.category:
            print("❌ --action add 需要指定 --category（official 或 kol）", file=sys.stderr)
            sys.exit(1)
        if not args.indexes:
            print("❌ --action add 需要指定 --indexes（如 1,3,5）", file=sys.stderr)
            sys.exit(1)

        try:
            indexes = [int(x.strip()) for x in args.indexes.split(",") if x.strip()]
        except ValueError:
            print("❌ --indexes 格式无效，请使用英文逗号分隔的整数，如 1,3,5", file=sys.stderr)
            sys.exit(1)

        # 获取榜单数据来源
        if args.list_json:
            try:
                source_data = json.loads(args.list_json)
            except json.JSONDecodeError:
                print("❌ --榜单-json 解析失败，请传入有效JSON", file=sys.stderr)
                sys.exit(1)
        elif args.from_cache:
            source_data = load_cache()
            if not source_data:
                print("❌ 未找到缓存数据，请先运行 fetch_astock_accounts.py --dual-category", file=sys.stderr)
                sys.exit(1)
        else:
            print("❌ --action add 需要通过 --from-cache 或 --榜单-json 指定榜单数据来源", file=sys.stderr)
            sys.exit(1)

        # 提取对应分类的账号列表
        if args.category == "official":
            source_accounts = source_data.get("officialMedia", {}).get("accounts", [])
        else:
            source_accounts = source_data.get("kolInfluencer", {}).get("accounts", [])

        if not source_accounts:
            print(f"❌ 榜单数据中未找到 {args.category} 分类账号", file=sys.stderr)
            sys.exit(1)

        action_add(subs, args.category, indexes, source_accounts)


if __name__ == "__main__":
    main()
