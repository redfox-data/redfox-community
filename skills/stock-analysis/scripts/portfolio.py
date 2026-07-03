#!/usr/bin/env python3
"""
组合复盘 — 按大V风格回顾持仓表现
====================================
输入持仓列表，检索大V近期文章中对各标的的观点，按大V交易框架评估组合。

Usage:
    python portfolio.py --author "财躺平" --stocks "中国卫星,航发动力,中航沈飞"
    python portfolio.py --author "格兰投研" --stocks "贵州茅台,宁德时代" --period 60
"""

import argparse
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from common import (
    ACCOUNT_IDS, STOCK_ANALYSTS, PROFILES_DIR, OUTPUT_DIR,
    GREEN, YELLOW, RED, CYAN, BOLD, RESET,
    info, warn, error, step,
    get_api_key, find_profile, detect_trading_type,
    fetch_articles_paginated, ensure_output_dir,
)


# ─── API 调用（使用 common 通用分页函数）───────────────────────────────────────────
def fetch_analyst_articles(api_key, author, days=30, count=100):
    """获取大V近期文章"""
    account = ACCOUNT_IDS.get(author, "")
    return fetch_articles_paginated(
        api_key, account, account_name=author,
        days=days, count=count, label=f"获取{author}文章",
    )


# ─── 组合分析 ──────────────────────────────────────────────────────────────────────
def analyze_portfolio(articles, stocks, author):
    """检索大V文章中对各持仓标的的观点"""
    portfolio_analysis = {
        "author": author,
        "stocks": stocks,
        "total_articles": len(articles),
        "analysis_time": datetime.now().isoformat(),
        "stock_views": {},
    }

    for stock in stocks:
        stock_info = {
            "stock": stock,
            "mentions": 0,
            "related_articles": [],
            "sentiment_keywords": [],
            "key_points": [],
        }

        # 正面/负面关键词
        positive_kw = ["看好", "加仓", "建仓", "突破", "强势", "龙头", "底部",
                       "低估", "价值", "增长", "超预期", "护城河"]
        negative_kw = ["减仓", "清仓", "止损", "破位", "弱势", "高位",
                       "套牢", "套现", "减持", "低于预期", "风险"]

        pos_count = 0
        neg_count = 0

        for a in articles:
            title = str(a.get("title", ""))
            summary = str(a.get("summary", ""))
            text = title + " " + summary

            if stock in text:
                stock_info["mentions"] += 1
                pub = str(a.get("publishTime") or a.get("publicTime") or "")[:10]
                stock_info["related_articles"].append({
                    "title": title[:60],
                    "date": pub,
                    "url": a.get("workUrl") or a.get("url") or "",
                })

                # 情绪分析
                for kw in positive_kw:
                    if kw in text:
                        pos_count += 1
                        if kw not in stock_info["sentiment_keywords"]:
                            stock_info["sentiment_keywords"].append(kw)
                for kw in negative_kw:
                    if kw in text:
                        neg_count += 1
                        if kw not in stock_info["sentiment_keywords"]:
                            stock_info["sentiment_keywords"].append(kw)

        # 情绪判定
        if pos_count > neg_count * 2:
            stock_info["sentiment"] = "看多"
        elif neg_count > pos_count * 2:
            stock_info["sentiment"] = "看空"
        elif pos_count > 0 and neg_count > 0:
            stock_info["sentiment"] = "分歧"
        elif stock_info["mentions"] == 0:
            stock_info["sentiment"] = "未提及"
        else:
            stock_info["sentiment"] = "中性"

        stock_info["pos_score"] = pos_count
        stock_info["neg_score"] = neg_count

        portfolio_analysis["stock_views"][stock] = stock_info

    return portfolio_analysis


# ─── 生成任务文件 ──────────────────────────────────────────────────────────────────
def generate_portfolio_task(author, profile, trading_type, stocks, portfolio_analysis, period):
    today = datetime.now().strftime("%Y-%m-%d")

    lines = []
    lines.append(f"# {author} 风格化组合复盘任务")
    lines.append(f"> 日期：{today}")
    lines.append(f"> 持仓标的：{', '.join(stocks)}")
    lines.append(f"> 回顾周期：近{period}天")
    lines.append(f"> ⚠️ AI 风格模拟，不构成投资建议\n")

    lines.append("## 1. 风格画像摘要\n")
    if profile:
        lines.append(f"```\n{profile[:2000]}\n```\n")
    else:
        lines.append("未找到风格画像，使用默认分析框架。\n")

    lines.append("## 2. 持仓组合分析\n")
    lines.append(f"**分析样本**：{portfolio_analysis['total_articles']} 篇{author}近期文章\n")

    stock_views = portfolio_analysis.get("stock_views", {})
    if stock_views:
        lines.append("### 各持仓标的观点摘要\n")
        lines.append("| 标的 | 提及次数 | 情绪倾向 | 正面信号 | 负面信号 | 相关文章 |")
        lines.append("|------|---------|---------|---------|---------|---------|")

        for stock, view in stock_views.items():
            pos = view.get("pos_score", 0)
            neg = view.get("neg_score", 0)
            articles_count = len(view.get("related_articles", []))
            sample = view.get("related_articles", [{}])[0].get("title", "无") if articles_count else "无"
            lines.append(f"| {stock} | {view['mentions']} | {view['sentiment']} | {pos} | {neg} | {sample[:20]} |")
        lines.append("")

    # 各标的详情
    for stock, view in stock_views.items():
        if view["mentions"] > 0:
            lines.append(f"### {stock}\n")
            lines.append(f"- 提及次数：{view['mentions']}")
            lines.append(f"- 情绪倾向：{view['sentiment']}")
            if view.get("sentiment_keywords"):
                lines.append(f"- 关键信号：{', '.join(view['sentiment_keywords'][:8])}")
            lines.append("")
            if view.get("related_articles"):
                lines.append("**相关文章：**")
                for ra in view["related_articles"][:5]:
                    lines.append(f"- [{ra['date']}] {ra['title']}")
                lines.append("")

    lines.append("## 3. 生成要求\n")
    lines.append(f"请按{author}的{'短线' if trading_type == 'short' else '长线'}交易框架，生成组合复盘报告：\n")

    if trading_type == "short":
        lines.append("- 各持仓标的的短线走势评估")
        lines.append("- 情绪周期对持仓的影响")
        lines.append("- 龙头辨识度和板块地位")
        lines.append("- 止盈/止损信号判断")
        lines.append("- 仓位调整建议\n")
    else:
        lines.append("- 各持仓标的的基本面评估")
        lines.append("- 估值水平和安全边际")
        lines.append("- 长期逻辑是否发生变化")
        lines.append("- 组合集中度和风险分散")
        lines.append("- 调仓建议\n")

    lines.append("## 4. 合规要求\n")
    lines.append("- 标注：「AI 风格模拟，不构成投资建议」")
    lines.append("- 不直接荐股，仅分析逻辑")
    lines.append("- 仅引用公开文章中的观点\n")

    lines.append(f"## 5. 输出")
    lines.append(f"保存到：`output/{author}_组合复盘_{today}.md`\n")

    return "\n".join(lines)


# ─── 主流程 ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="组合复盘 — 按大V风格回顾持仓")
    parser.add_argument("--author", required=True, help="指定大V名称")
    parser.add_argument("--stocks", required=True, help="持仓列表（逗号分隔）")
    parser.add_argument("--period", type=int, default=30, help="回顾周期（天，默认30天）")
    parser.add_argument("--api-key", help="指定API Key")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="输出目录")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    stocks = [s.strip() for s in args.stocks.split(",") if s.strip()]
    if not stocks:
        error("请提供至少一个持仓标的")
        sys.exit(1)

    # 加载画像
    step(f"加载画像：{args.author}")
    profile = find_profile(args.author)
    trading_type = detect_trading_type(profile)
    if profile:
        info(f"画像已加载，交易类型：{trading_type}")
    else:
        warn(f"未找到{args.author}的风格画像，使用默认分析")

    # 获取大V近期文章
    api_key = get_api_key(args.api_key)
    if not api_key:
        sys.exit(1)
    step(f"获取{args.author}近{args.period}天文章...")
    articles = fetch_analyst_articles(api_key, args.author, args.period, 100)

    if not articles:
        warn(f"未获取到{args.author}的文章数据")
        warn("可能原因：1) API额度不足 2) 该大V近期无文章")

    info(f"共获取 {len(articles)} 篇文章")

    # 组合分析
    step("分析持仓组合...")
    portfolio_analysis = analyze_portfolio(articles, stocks, args.author)

    # 生成任务
    task = generate_portfolio_task(args.author, profile, trading_type, stocks, portfolio_analysis, args.period)
    today = datetime.now().strftime("%Y-%m-%d")
    task_file = output_dir / f"{args.author}_组合复盘任务_{today}.md"
    task_file.write_text(task, encoding="utf-8")
    info(f"组合复盘任务已保存：{task_file}")

    # 显示摘要
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  组合复盘摘要{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"  大V：{args.author}（{trading_type}）")
    print(f"  持仓：{', '.join(stocks)}")
    print(f"  样本：{len(articles)} 篇文章")

    stock_views = portfolio_analysis.get("stock_views", {})
    if stock_views:
        print(f"\n{BOLD}各标的观点：{RESET}")
        for stock, view in stock_views.items():
            sentiment_color = GREEN if view["sentiment"] == "看多" else (RED if view["sentiment"] == "看空" else YELLOW)
            print(f"  {stock:10s} | 提及{view['mentions']:2d}次 | {sentiment_color}{view['sentiment']}{RESET}")

    print(f"\n{GREEN}✓{RESET} 任务文件：{task_file}")


if __name__ == "__main__":
    main()
