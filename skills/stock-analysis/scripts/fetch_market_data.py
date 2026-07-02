#!/usr/bin/env python3
"""
盘面数据采集 — 手动输入并结构化存储
=====================================
盘面数据需由用户提供或手动输入，脚本负责结构化存储为 JSON。

Usage:
    python fetch_market_data.py --manual
    python fetch_market_data.py --from-json market_data.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from common import (
    OUTPUT_DIR,
    GREEN, YELLOW, RED, CYAN, BOLD, RESET,
    info, warn, error, step,
    ensure_output_dir,
)


# ─── 手动输入盘面数据 ──────────────────────────────────────────────────────────────
def manual_input():
    """手动输入盘面数据"""
    print(f"\n{BOLD}请输入今日盘面数据：{RESET}\n")

    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "source": "manual",
        "input_time": datetime.now().isoformat(),
        "data_sources": {},
        "cross_validated": False,
    }

    data["sh_index"] = input("上证指数收盘点位（如4000.50）: ").strip()
    data["sh_change"] = input("上证涨跌幅%（如+1.5）: ").strip()
    data["sz_index"] = input("深证成指收盘点位（可选，回车跳过）: ").strip()
    data["sz_change"] = input("深证涨跌幅%（可选）: ").strip()
    data["gem_index"] = input("创业板指收盘点位（可选）: ").strip()
    data["gem_change"] = input("创业板涨跌幅%（可选）: ").strip()
    data["volume"] = input("成交额（万亿，如3.5）: ").strip()
    data["limit_up_count"] = input("涨停家数: ").strip()
    data["limit_down_count"] = input("跌停家数: ").strip()
    data["continuous_board"] = input("连板股数量（可选）: ").strip()
    data["hot_sectors"] = input("热门板块（逗号分隔）: ").strip()
    data["capital_flow"] = input("主力资金流向（如净流入/净流出金额）: ").strip()
    data["north_flow"] = input("北向资金流向（可选）: ").strip()
    data["market_sentiment"] = input("市场情绪（如：偏强/震荡/偏弱）: ").strip()
    data["notes"] = input("其他备注: ").strip()

    # 数据交叉验证
    print(f"\n{BOLD}数据交叉验证：{RESET}")
    validate = input("是否已对关键数据进行交叉验证？(y/n): ").strip().lower()
    if validate == 'y':
        data["cross_validated"] = True
        data["data_sources"]["primary"] = input("主数据来源（如：交易所官网/东方财富）: ").strip()
        data["data_sources"]["secondary"] = input("副数据来源（如：同花顺/万得）: ").strip()
        data["data_sources"]["notes"] = input("数据差异备注（可跳过）: ").strip()
    else:
        data["cross_validated"] = False
        print(f"{YELLOW}[!]{RESET} 建议对涨跌停家数、成交额等数据进行交叉验证")

    return data


def load_from_json(json_path):
    """从JSON文件加载盘面数据"""
    f = Path(json_path)
    if not f.exists():
        error(f"文件不存在：{json_path}")
        return None
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        if "date" not in data:
            data["date"] = datetime.now().strftime("%Y-%m-%d")
        data["source"] = "json_file"
        data["input_time"] = datetime.now().isoformat()
        info(f"已加载盘面数据：{f.name}")
        return data
    except Exception as e:
        error(f"读取JSON失败：{e}")
        return None


# ─── 主流程 ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="盘面数据采集 — 手动输入并结构化存储")
    parser.add_argument("--manual", action="store_true", help="手动输入盘面数据（交互式）")
    parser.add_argument("--from-json", help="从JSON文件加载盘面数据")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="输出目录")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data = None

    if args.from_json:
        data = load_from_json(args.from_json)
    elif args.manual:
        data = manual_input()
    else:
        # 默认进入手动输入模式
        print(f"{BOLD}提示：盘面数据需手动输入{RESET}")
        print(f"使用 --manual 进入交互式输入")
        print(f"使用 --from-json <file> 从JSON文件加载")
        print(f"\n也可直接提供JSON格式的盘面数据文件，脚本会结构化存储。")
        parser.print_help()
        sys.exit(0)

    if not data:
        error("未获取到盘面数据")
        sys.exit(1)

    # 保存
    today = datetime.now().strftime("%Y-%m-%d")
    f = output_dir / f"盘面数据_{today}.json"
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    info(f"盘面数据已保存：{f}")

    # 显示摘要
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  盘面数据摘要{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"  日期：{data.get('date', today)}")
    if data.get("sh_index"):
        print(f"  上证指数：{data['sh_index']}（{data.get('sh_change', '')}%）")
    if data.get("sz_index"):
        print(f"  深证成指：{data['sz_index']}（{data.get('sz_change', '')}%）")
    if data.get("gem_index"):
        print(f"  创业板指：{data['gem_index']}（{data.get('gem_change', '')}%）")
    if data.get("volume"):
        print(f"  成交额：{data['volume']}万亿")
    if data.get("limit_up_count"):
        print(f"  涨停/跌停：{data['limit_up_count']}/{data.get('limit_down_count', '?')}")
    if data.get("hot_sectors"):
        print(f"  热门板块：{data['hot_sectors']}")
    if data.get("capital_flow"):
        print(f"  资金流向：{data['capital_flow']}")
    if data.get("market_sentiment"):
        print(f"  市场情绪：{data['market_sentiment']}")
    if data.get("notes"):
        print(f"  备注：{data['notes']}")

    print(f"\n{GREEN}✓{RESET} 可用于分析专家：python scripts/analyze.py --author 财躺平 --mode daily")


if __name__ == "__main__":
    main()
