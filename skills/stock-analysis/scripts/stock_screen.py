#!/usr/bin/env python3
"""
短线选股 — 按大V交易体系筛选标的
==================================
从公众号热文中提取个股提及频率，结合大V的交易类型应用不同筛选策略。

Usage:
    python stock_screen.py --author "财躺平"
    python stock_screen.py --author "财躺平" --sector "航天"
    python stock_screen.py --author "格兰投研" --days 14 --count 100
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

from common import (
    ACCOUNT_IDS, STOCK_ANALYSTS, PROFILES_DIR, OUTPUT_DIR,
    GREEN, YELLOW, RED, CYAN, BOLD, RESET,
    info, warn, error, step,
    get_api_key, find_profile, detect_trading_type,
    fetch_articles_paginated, ensure_output_dir,
)


# ─── 赛道关键词库 ──────────────────────────────────────────────────────────────────
SECTOR_KEYWORDS = {
    "航天": ["航天", "卫星", "火箭", "商业航天", "星链", "太空"],
    "半导体": ["半导体", "芯片", "光刻", "存储", "科创", "中芯", "台积电"],
    "AI": ["AI", "人工智能", "大模型", "GPT", "Agent", "算力", "英伟达"],
    "新能源": ["新能源", "光伏", "风电", "储能", "锂电", "充电桩"],
    "金融": ["券商", "银行", "保险", "金融"],
    "消费": ["消费", "白酒", "食品", "零售", "茅台", "五粮液"],
    "医药": ["医药", "医疗", "创新药", "生物"],
    "军工": ["军工", "国防", "装备", "中航", "航发"],
    "脑机接口": ["脑机", "Neuralink"],
    "核聚变": ["核聚变", "可控核"],
    "房地产": ["房地产", "地产", "楼市"],
    "机器人": ["机器人", "人形机器人", "减速器"],
}

# 个股识别正则（中文股票名称模式）
STOCK_NAME_PATTERN = re.compile(
    r'(?:中国|中|国|华|南|北|东|西|新|大|上|深|长|广|江|浙|海|天|金|银|龙|凤|'
    r'安|宝|富|恒|嘉|美|高|万|百|千|红|蓝|绿|紫|星|光|明|达|利|通|信|科|泰|'
    r'航|发|沈|成|西|赣|鲁|闽|川|渝|鄂|湘|皖|豫|冀|辽|吉|黑)[\u4e00-\u9fff]{1,5}'
    r'(?:股份|科技|电子|集团|控股|材料|设备|能源|动力|智能|芯片|生物|药业|'
    r'化工|机械|光电|信息|通信|网络|软件|互联|新材|环保|装备|工业|精密|'
    r'电气|自动化|仪器|仪表|航空|航天|船舶|重工)'
)

# 短线筛选关注词
SHORT_SCREEN_KW = ["涨停", "连板", "龙头", "资金流入", "主力买入", "封板",
                   "竞价", "炸板", "反包", "首板", "二板", "三板", "妖股",
                   "情绪", "辨识度", "卡位", "补涨", "加速"]

# 长线筛选关注词
LONG_SCREEN_KW = ["护城河", "ROE", "净利润", "毛利率", "自由现金流", "估值",
                  "PE", "PB", "分红", "回购", "业绩增长", "核心竞争力",
                  "市场份额", "研发", "壁垒", "长期", "内在价值"]


# ─── API 调用（使用 common 通用分页函数）───────────────────────────────────────────
def fetch_hot_articles(api_key, author, days=7, count=100):
    account = ACCOUNT_IDS.get(author, "")
    return fetch_articles_paginated(
        api_key, account, account_name=author,
        days=days, count=count, label="获取热文",
    )


# ─── 选股分析 ──────────────────────────────────────────────────────────────────────
def extract_stock_mentions(articles, sector_filter=None):
    """从文章中提取个股提及"""
    stock_counter = Counter()
    stock_context = defaultdict(list)

    for a in articles:
        text = " ".join([
            str(a.get("title", "")),
            str(a.get("summary", "")),
            str(a.get("workSummary", "")),
        ])
        title = str(a.get("title", ""))

        # 提取个股名称
        matches = STOCK_NAME_PATTERN.findall(text)
        for m in matches:
            if len(m) >= 3:
                stock_counter[m] += 1
                stock_context[m].append(title[:60])

        # 也检查赛道关键词匹配（用于板块热度）
        if sector_filter:
            sector_kw = SECTOR_KEYWORDS.get(sector_filter, [])
            sector_score = sum(text.count(kw) for kw in sector_kw)
            if sector_score == 0:
                continue  # 如果指定了板块，跳过不相关的文章

    return stock_counter, stock_context


def analyze_screening(articles, trading_type, sector_filter=None):
    """按大V交易类型执行选股分析"""
    stock_counter, stock_context = extract_stock_mentions(articles, sector_filter)

    # 分析短线/长线特征
    screening_result = {
        "trading_type": trading_type,
        "sector_filter": sector_filter,
        "total_articles": len(articles),
        "analysis_time": datetime.now().isoformat(),
    }

    if trading_type in ("short", "mixed"):
        # 短线筛选：高频提及 + 板块热度
        short_scores = {}
        for stock, count in stock_counter.items():
            contexts = stock_context[stock]
            context_text = " ".join(contexts)
            short_score = count * 2  # 提及频率权重
            short_score += sum(1 for kw in SHORT_SCREEN_KW if kw in context_text)
            short_scores[stock] = short_score

        top_short = sorted(short_scores.items(), key=lambda x: x[1], reverse=True)[:15]
        screening_result["short_screen"] = [
            {"stock": s, "score": sc, "mentions": stock_counter[s],
             "sample_titles": stock_context[s][:3]}
            for s, sc in top_short
        ]

    if trading_type in ("long", "mixed"):
        # 长线筛选：基本面关键词
        long_scores = {}
        for stock, count in stock_counter.items():
            contexts = stock_context[stock]
            context_text = " ".join(contexts)
            long_score = count  # 提及频率
            long_score += sum(2 for kw in LONG_SCREEN_KW if kw in context_text)
            long_scores[stock] = long_score

        top_long = sorted(long_scores.items(), key=lambda x: x[1], reverse=True)[:15]
        screening_result["long_screen"] = [
            {"stock": s, "score": sc, "mentions": stock_counter[s],
             "sample_titles": stock_context[s][:3]}
            for s, sc in top_long
        ]

    # 板块热度
    sector_scores = defaultdict(int)
    for a in articles:
        text = str(a.get("title", "")) + " " + str(a.get("summary", ""))
        for sector, kws in SECTOR_KEYWORDS.items():
            for kw in kws:
                sector_scores[sector] += text.count(kw)
    screening_result["sector_heat"] = dict(
        sorted(sector_scores.items(), key=lambda x: x[1], reverse=True)[:10]
    )

    # 所有提及的个股排行
    screening_result["all_mentions"] = [
        {"stock": s, "count": c, "sample_titles": stock_context[s][:2]}
        for s, c in stock_counter.most_common(30)
    ]

    return screening_result


# ─── 生成任务文件 ──────────────────────────────────────────────────────────────────
def generate_screen_task(author, profile, trading_type, screening_result):
    today = datetime.now().strftime("%Y-%m-%d")

    lines = []
    lines.append(f"# {author} 风格化选股分析任务")
    lines.append(f"> 日期：{today}")
    lines.append(f"> 交易类型：{trading_type}")
    lines.append(f"> ⚠️ AI 风格模拟，不构成投资建议\n")

    lines.append("## 1. 风格画像摘要\n")
    if profile:
        lines.append(f"```\n{profile[:2000]}\n```\n")
    else:
        lines.append("未找到风格画像，使用默认分析框架。\n")

    lines.append("## 2. 选股数据\n")
    lines.append(f"**分析样本**：{screening_result['total_articles']} 篇热文")
    lines.append(f"**板块过滤**：{screening_result.get('sector_filter') or '全市场'}\n")

    # 板块热度
    sector_heat = screening_result.get("sector_heat", {})
    if sector_heat:
        lines.append("### 板块热度排行\n")
        lines.append("| 板块 | 热度分 |")
        lines.append("|------|--------|")
        for sector, score in list(sector_heat.items())[:8]:
            lines.append(f"| {sector} | {score} |")
        lines.append("")

    # 个股提及排行
    all_mentions = screening_result.get("all_mentions", [])
    if all_mentions:
        lines.append("### 个股提及频率 TOP15\n")
        lines.append("| 个股 | 提及次数 | 相关文章 |")
        lines.append("|------|---------|---------|")
        for m in all_mentions[:15]:
            titles = "、".join(m["sample_titles"][:2])
            lines.append(f"| {m['stock']} | {m['count']} | {titles} |")
        lines.append("")

    # 短线/长线选股结果
    if trading_type in ("short", "mixed"):
        short_screen = screening_result.get("short_screen", [])
        if short_screen:
            lines.append("### 短线选股信号 TOP10\n")
            lines.append("| 个股 | 综合分 | 提及次数 | 相关文章 |")
            lines.append("|------|--------|---------|---------|")
            for s in short_screen[:10]:
                titles = "、".join(s["sample_titles"][:2])
                lines.append(f"| {s['stock']} | {s['score']} | {s['mentions']} | {titles} |")
            lines.append("")

    if trading_type in ("long", "mixed"):
        long_screen = screening_result.get("long_screen", [])
        if long_screen:
            lines.append("### 长线选股信号 TOP10\n")
            lines.append("| 个股 | 综合分 | 提及次数 | 相关文章 |")
            lines.append("|------|--------|---------|---------|")
            for s in long_screen[:10]:
                titles = "、".join(s["sample_titles"][:2])
                lines.append(f"| {s['stock']} | {s['score']} | {s['mentions']} | {titles} |")
            lines.append("")

    lines.append("## 3. 生成要求\n")
    lines.append(f"请按{author}的{'短线' if trading_type == 'short' else '长线'}选股框架，生成选股分析报告：\n")

    if trading_type == "short":
        lines.append("- 聚焦短线龙头和辨识度标的")
        lines.append("- 分析情绪周期位置")
        lines.append("- 评估板块轮动节奏")
        lines.append("- 关注量价关系和资金面")
        lines.append("- 给出仓位建议和操作策略\n")
    else:
        lines.append("- 聚焦基本面质量和估值")
        lines.append("- 分析护城河和竞争优势")
        lines.append("- 评估长期成长空间")
        lines.append("- 关注财务数据和行业趋势")
        lines.append("- 给出买入逻辑和安全边际\n")

    lines.append("## 4. 合规要求\n")
    lines.append("- 标注：「AI 风格模拟，不构成投资建议」")
    lines.append("- 不直接荐股，仅分析逻辑")
    lines.append("- 区分事实与判断\n")

    lines.append(f"## 5. 输出")
    lines.append(f"保存到：`output/{author}_选股_{today}.md`\n")

    return "\n".join(lines)


# ─── 主流程 ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="大V风格化选股")
    parser.add_argument("--author", required=True, help="指定大V名称")
    parser.add_argument("--sector", help="板块过滤（可选）")
    parser.add_argument("--days", type=int, default=7, help="近N天数据（默认7天）")
    parser.add_argument("--count", type=int, default=100, help="获取文章数量（默认100）")
    parser.add_argument("--api-key", help="指定API Key")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="输出目录")

    args = parser.parse_args()

    output_dir = Path(args.output_dir) if args.output_dir != str(OUTPUT_DIR) else ensure_output_dir()
    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载画像
    step(f"加载画像：{args.author}")
    profile = find_profile(args.author)
    trading_type = detect_trading_type(profile)
    if profile:
        info(f"画像已加载，交易类型：{trading_type}")
    else:
        warn(f"未找到{args.author}的风格画像，使用默认分析")

    # 获取数据
    api_key = get_api_key(args.api_key)
    if not api_key:
        sys.exit(1)
    step(f"获取近{args.days}天热文数据...")
    articles = fetch_hot_articles(api_key, args.author, args.days, args.count)

    if not articles:
        warn("未获取到文章数据")
        warn("可使用 --sector 过滤板块或增大 --days")
        sys.exit(0)

    info(f"共获取 {len(articles)} 篇文章")

    # 选股分析
    step("执行选股分析...")
    screening_result = analyze_screening(articles, trading_type, args.sector)

    # 生成任务
    task = generate_screen_task(args.author, profile, trading_type, screening_result)
    today = datetime.now().strftime("%Y-%m-%d")
    task_file = output_dir / f"{args.author}_选股任务_{today}.md"
    task_file.write_text(task, encoding="utf-8")
    info(f"选股任务已保存：{task_file}")

    # 显示摘要
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  选股分析摘要{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"  大V：{args.author}（{trading_type}）")
    print(f"  样本：{len(articles)} 篇文章")

    mentions = screening_result.get("all_mentions", [])
    if mentions:
        print(f"\n{BOLD}个股提及 TOP10：{RESET}")
        for m in mentions[:10]:
            print(f"  - {m['stock']}（{m['count']}次）")

    sector_heat = screening_result.get("sector_heat", {})
    if sector_heat:
        print(f"\n{BOLD}板块热度 TOP5：{RESET}")
        for s, sc in list(sector_heat.items())[:5]:
            print(f"  - {s}（{sc}分）")

    print(f"\n{GREEN}✓{RESET} 任务文件：{task_file}")


if __name__ == "__main__":
    main()
