#!/usr/bin/env python3
"""
公众号股票大V分析专家 — 主脚本
================================
加载大V风格画像，结合盘面数据，生成风格化分析内容。

Usage:
    python analyze.py --author "财躺平" --mode daily
    python analyze.py --mode team --authors "财躺平,格兰投研,投资明见"
    python analyze.py --author "财躺平" --mode sector --sector "航天"
    python analyze.py --author "财躺平" --mode screen --sector "半导体"
    python analyze.py --author "财躺平" --mode portfolio --stocks "中国卫星,航发动力"
    python analyze.py --author "格兰投研" --mode earnings --stock "贵州茅台"
    python analyze.py --author "财躺平" --mode sync
    python analyze.py --list-profiles
    python analyze.py --check-env
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from common import (
    SCRIPTS_DIR, SKILL_DIR, PROFILES_DIR, OUTPUT_DIR,
    STOCK_ANALYSTS,
    GREEN, YELLOW, RED, CYAN, BOLD, RESET,
    info, warn, error, step,
    ensure_output_dir, get_api_key, record_call,
)


# ─── 环境检查 ──────────────────────────────────────────────────────────────────────
def check_env():
    """检查环境"""
    info("环境检查中...")
    issues = []

    try:
        import requests
        info("requests 已就绪")
    except ImportError:
        warn("缺少 requests，正在安装...")
        os.system(f"{sys.executable} -m pip install requests")
        try:
            import requests
            info("requests 安装成功")
        except ImportError:
            error("requests 安装失败")
            issues.append("requests")

    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 检查画像目录
    profiles = find_profiles()
    if profiles:
        info(f"找到 {len(profiles)} 个风格画像：")
        for p in profiles:
            print(f"    - {p['author']}")
    else:
        warn(f"未找到任何风格画像")
        warn(f"搜索路径: {PROFILES_DIR}")
        warn(f"请确认 profiles/ 目录下有已蒸馏的风格画像文件")

    if issues:
        error(f"依赖缺失: {', '.join(issues)}")
        return False
    return True


# ─── 画像加载 ──────────────────────────────────────────────────────────────────────
def find_profiles():
    """搜索所有可用的风格画像"""
    profiles = []
    search_dirs = [PROFILES_DIR]

    for d in search_dirs:
        if not d.exists():
            continue
        for f in d.glob("*_profile.json"):
            author = f.stem.replace("_profile", "")
            profiles.append({
                "author": author,
                "path": str(f),
                "dir": str(d),
            })

    # 去重
    seen = set()
    unique = []
    for p in profiles:
        if p["author"] not in seen:
            seen.add(p["author"])
            unique.append(p)

    return unique


def load_profile(author):
    """加载指定大V的风格画像，优先精确匹配"""
    profiles = find_profiles()

    # 优先精确匹配
    for p in profiles:
        if p["author"] == author:
            try:
                content = Path(p["path"]).read_text(encoding="utf-8")
                info(f"已加载画像：{p['author']} ({p['path']})")
                return content
            except Exception as e:
                error(f"读取画像失败: {e}")
                return None

    # 模糊匹配（子串包含）
    for p in profiles:
        if author in p["author"]:
            warn(f"未精确匹配「{author}」，使用模糊匹配：{p['author']}")
            try:
                content = Path(p["path"]).read_text(encoding="utf-8")
                info(f"已加载画像：{p['author']} ({p['path']})")
                return content
            except Exception as e:
                error(f"读取画像失败: {e}")
                return None

    error(f"未找到大V「{author}」的风格画像")
    info(f"可用画像：{', '.join([p['author'] for p in profiles])}")
    return None


# ─── 盘面数据加载 ──────────────────────────────────────────────────────────────────
def load_market_data(market_data_arg=None):
    """加载盘面数据

    Args:
        market_data_arg: 可以是文件路径、日期字符串（YYYY-MM-DD）或 None
    """
    f = None
    if market_data_arg:
        p = Path(market_data_arg)
        if p.is_file():
            # 用户直接传了文件路径
            f = p
        else:
            # 按日期拼接
            f = OUTPUT_DIR / f"盘面数据_{market_data_arg}.json"
    else:
        # 找最新的盘面数据
        files = sorted(OUTPUT_DIR.glob("盘面数据_*.json"), reverse=True)
        f = files[0] if files else None

    if not f or not f.exists():
        warn("未找到盘面数据文件")
        warn("请先运行: python scripts/fetch_market_data.py --days 1")
        return None

    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        info(f"已加载盘面数据：{f.name}")
        return data
    except Exception as e:
        error(f"读取盘面数据失败: {e}")
        return None


# ─── 生成分析任务 ────────────────────────────────────────────────────────────────────
def generate_daily_task(author, profile, market_data):
    """生成单大V每日复盘任务"""
    today = datetime.now().strftime("%Y-%m-%d")

    lines = []
    lines.append(f"# {author} 风格化复盘生成任务")
    lines.append(f"> 日期：{today}")
    lines.append(f"> ⚠️ AI 风格模拟，不构成投资建议\n")

    lines.append("## 1. 风格画像摘要\n")
    lines.append("请基于以下风格画像生成复盘文章：\n")
    lines.append(f"```\n{profile[:3000]}\n```\n")

    lines.append("## 2. 盘面数据\n")
    if market_data:
        lines.append(f"```json\n{json.dumps(market_data, ensure_ascii=False, indent=2)[:3000]}\n```\n")
    else:
        lines.append("**未找到盘面数据文件。**\n")
        lines.append("请用户提供以下盘面数据（至少包含）：")
        lines.append("- 上证指数收盘点位和涨跌幅")
        lines.append("- 成交额")
        lines.append("- 涨停/跌停家数")
        lines.append("- 热门板块")
        lines.append("- 主要资金流向\n")

    lines.append("## 3. 生成要求\n")
    lines.append("请严格按照风格画像生成一篇复盘文章，要求：\n")

    lines.append("### 标题")
    lines.append("- 使用大V的标题模式")
    lines.append(f"- 参考画像中的标题模式和示例\n")

    lines.append("### 开头")
    lines.append("- 使用大V的标志性开头模板")
    lines.append(f"- 包含至少1个标志性表达\n")

    lines.append("### 正文结构")
    lines.append("- 按大V的文章结构组织内容")
    lines.append("- 包含盘面概述 → 板块分析 → 操作策略")
    lines.append("- 使用大V的交易体系框架分析")
    lines.append(f"- 包含至少3个标志性表达\n")

    lines.append("### 结尾")
    lines.append("- 使用大V的结尾模式")
    lines.append("- 包含免责声明（如大V有此习惯）\n")

    lines.append("### 合规要求")
    lines.append("- 文章开头或结尾必须标注：**「AI 风格模拟，不构成投资建议」**")
    lines.append("- 不得编造未在盘面数据中出现的具体数据")
    lines.append("- 严格区分盘面事实与交易判断\n")

    lines.append(f"## 4. 输出")
    lines.append(f"保存到：`output/{author}_复盘_{today}.md`\n")

    return "\n".join(lines)


def generate_team_task(authors, profiles_data, market_data):
    """生成多V对比任务"""
    today = datetime.now().strftime("%Y-%m-%d")

    lines = []
    lines.append(f"# 多V并行对比分析任务")
    lines.append(f"> 日期：{today}")
    lines.append(f"> 参与大V：{', '.join(authors)}")
    lines.append(f"> ⚠️ AI 风格模拟，不构成投资建议\n")

    lines.append("## 1. 盘面数据\n")
    if market_data:
        lines.append(f"```json\n{json.dumps(market_data, ensure_ascii=False, indent=2)[:2000]}\n```\n")
    else:
        lines.append("请用户提供当日盘面数据。\n")

    lines.append("## 2. 生成要求\n")
    lines.append("请为每位大V分别生成一段复盘观点，然后进行对比分析。\n")

    for author in authors:
        profile = profiles_data.get(author, "")
        lines.append(f"### {author} 的复盘观点\n")
        lines.append(f"**风格画像摘要：**\n```\n{profile[:1500]}\n```\n")
        lines.append(f"生成要求：")
        lines.append(f"- 严格按{author}的风格画像生成")
        lines.append(f"- 包含{author}的标志性表达")
        lines.append(f"- 字数控制在500-800字\n")

    lines.append("## 3. 对比分析\n")
    lines.append("在各位大V的复盘之后，生成对比分析：\n")
    lines.append("- **共识点**：各位大V都看好的方向")
    lines.append("- **分歧点**：各位大V观点不同的地方")
    lines.append("- **不同视角**：各位大V关注的维度差异\n")

    lines.append("## 4. 合规要求\n")
    lines.append("- 标注：「AI 风格模拟，不构成投资建议」")
    lines.append("- 不冒充大V本人")
    lines.append("- 不直接荐股\n")

    lines.append(f"## 5. 输出")
    lines.append(f"保存到：`output/多V对比_{today}.md`\n")

    return "\n".join(lines)


def generate_sector_task(author, profile, sector, market_data):
    """生成板块漏斗分析任务"""
    today = datetime.now().strftime("%Y-%m-%d")

    lines = []
    lines.append(f"# {author} 风格化板块分析任务 — {sector}")
    lines.append(f"> 日期：{today}")
    lines.append(f"> ⚠️ AI 风格模拟，不构成投资建议\n")

    lines.append("## 1. 风格画像摘要\n")
    lines.append(f"```\n{profile[:2000]}\n```\n")

    lines.append(f"## 2. 分析框架\n")
    lines.append(f"请按{author}的分析框架，对「{sector}」板块进行漏斗筛选：\n")

    lines.append("### 第一层：赛道识别")
    lines.append(f"- {sector}板块当前的热度")
    lines.append(f"- 催化事件和政策面")
    lines.append(f"- 市场情绪指标\n")

    lines.append("### 第二层：龙头筛选")
    lines.append(f"- {sector}板块的核心标的")
    lines.append("- 主营业务占比")
    lines.append("- 业绩确定性")
    lines.append("- 估值水平\n")

    lines.append("### 第三层：确定性评估")
    lines.append("- 哪些是确定性机会（绕不开的）")
    lines.append("- 哪些是炒作预期（资产注入等）")
    lines.append("- 哪些是真实业绩驱动\n")

    lines.append("### 第四层：操作策略")
    lines.append(f"- 按{author}的仓位管理策略")
    lines.append("- 买入/卖出信号")
    lines.append("- 风险提示\n")

    lines.append("## 3. 合规要求\n")
    lines.append("- 标注：「AI 风格模拟，不构成投资建议」")
    lines.append("- 不直接荐股，仅分析板块逻辑\n")

    lines.append(f"## 4. 输出")
    lines.append(f"保存到：`output/{author}_{sector}分析_{today}.md`\n")

    return "\n".join(lines)


def generate_track_task(author, profile, stock):
    """生成观点跟踪任务"""
    today = datetime.now().strftime("%Y-%m-%d")

    lines = []
    lines.append(f"# {author} 观点跟踪 — {stock}")
    lines.append(f"> 日期：{today}")
    lines.append(f"> ⚠️ AI 风格模拟，不构成投资建议\n")

    lines.append("## 1. 风格画像摘要\n")
    lines.append(f"```\n{profile[:1500]}\n```\n")

    lines.append(f"## 2. 跟踪目标：{stock}\n")
    lines.append(f"请从风格画像中检索{author}对「{stock}」的相关观点：\n")

    lines.append("### 历史观点")
    lines.append(f"- {author}是否提及过{stock}？")
    lines.append(f"- 如果提及，是什么时候、什么背景下？")
    lines.append(f"- 具体观点是什么？（看好/看空/中性）\n")

    lines.append("### 判断逻辑")
    lines.append(f"- {author}对{stock}的判断逻辑是什么？")
    lines.append(f"- 基于什么维度分析的？（基本面/技术面/资金面）\n")

    lines.append("### 兑现情况")
    lines.append(f"- {author}的判断是否已兑现？")
    lines.append(f"- 如果未兑现，可能的原因是什么？\n")

    lines.append("## 3. 合规要求\n")
    lines.append("- 仅引用画像中的公开观点")
    lines.append("- 不构成投资建议\n")

    lines.append(f"## 4. 输出")
    lines.append(f"保存到：`output/{author}_{stock}观点跟踪_{today}.md`\n")

    return "\n".join(lines)


# ─── 新模式入口 ────────────────────────────────────────────────────────────────────
def run_screen(author, sector=None, days=7):
    """短线选股"""
    step(f"模式：短线选股 — {author}" + (f" / {sector}" if sector else ""))
    script = SKILL_DIR / "scripts" / "stock_screen.py"
    cmd = [sys.executable, str(script), "--author", author, "--days", str(days)]
    if sector:
        cmd.extend(["--sector", sector])
    print(f"{BOLD}执行：{RESET}{' '.join(cmd)}")
    return subprocess.call(cmd)


def run_portfolio(author, stocks, period=30):
    """组合复盘"""
    step(f"模式：组合复盘 — {author} / {', '.join(stocks)}")
    script = SKILL_DIR / "scripts" / "portfolio.py"
    cmd = [sys.executable, str(script), "--author", author, "--stocks", ",".join(stocks), "--period", str(period)]
    print(f"{BOLD}执行：{RESET}{' '.join(cmd)}")
    return subprocess.call(cmd)


def run_earnings(author, stock, data_file=None, manual=False):
    """财报点评"""
    step(f"模式：财报点评 — {author} / {stock}")
    script = SKILL_DIR / "scripts" / "earnings.py"
    cmd = [sys.executable, str(script), "--author", author, "--stock", stock]
    if data_file:
        cmd.extend(["--data", data_file])
    elif manual:
        cmd.append("--manual")
    print(f"{BOLD}执行：{RESET}{' '.join(cmd)}")
    return subprocess.call(cmd)


def run_sync(author, days=7, api_key=None):
    """增量文章同步 — 拉取近N天新文章用于蒸馏补充"""
    step(f"模式：增量同步 — {author} / 近{days}天")
    script = SKILL_DIR / "scripts" / "sync_articles.py"
    cmd = [sys.executable, str(script), "--author", author, "--days", str(days)]
    if api_key:
        cmd.extend(["--api-key", api_key])
    print(f"{BOLD}执行：{RESET}{' '.join(cmd)}")
    return subprocess.call(cmd)


# ─── 主流程 ──────────────────────────────────────────────────────────────────────────
def run_daily(author, market_data_file=None):
    """单大V每日复盘"""
    step(f"模式：单大V每日复盘 — {author}")

    profile = load_profile(author)
    if not profile:
        return False

    market_data = load_market_data(market_data_file)

    task = generate_daily_task(author, profile, market_data)

    # 保存任务
    today = datetime.now().strftime("%Y-%m-%d")
    task_file = OUTPUT_DIR / f"{author}_复盘任务_{today}.md"
    task_file.write_text(task, encoding="utf-8")
    info(f"生成任务已保存：{task_file}")

    # 提示AI生成
    print()
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  复盘生成任务已就绪{RESET}")
    print(f"  画像：{author}")
    print(f"  盘面数据：{'已加载' if market_data else '未找到，需用户输入'}")
    print(f"  任务文件：{task_file}")
    print(f"  模板参考：{SKILL_DIR}/assets/article_template.md")
    print(f"  输出到：{OUTPUT_DIR}/{author}_复盘_{today}.md")
    print(f"{BOLD}{'='*60}{RESET}")

    return True


def run_team(authors_list, market_data_file=None):
    """多V并行对比"""
    step(f"模式：多V并行对比 — {', '.join(authors_list)}")

    profiles_data = {}
    for author in authors_list:
        profile = load_profile(author)
        if not profile:
            warn(f"跳过：{author}（未找到画像）")
            continue
        profiles_data[author] = profile

    if len(profiles_data) < 2:
        error("至少需要2位大V的画像才能进行对比")
        return False

    market_data = load_market_data(market_data_file)

    task = generate_team_task(authors_list, profiles_data, market_data)

    today = datetime.now().strftime("%Y-%m-%d")
    task_file = OUTPUT_DIR / f"多V对比任务_{today}.md"
    task_file.write_text(task, encoding="utf-8")
    info(f"生成任务已保存：{task_file}")

    print()
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  多V对比任务已就绪{RESET}")
    print(f"  参与大V：{', '.join(profiles_data.keys())}")
    print(f"  盘面数据：{'已加载' if market_data else '未找到，需用户输入'}")
    print(f"  任务文件：{task_file}")
    print(f"  输出到：{OUTPUT_DIR}/多V对比_{today}.md")
    print(f"{BOLD}{'='*60}{RESET}")

    return True


def run_sector(author, sector, market_data_file=None):
    """板块漏斗分析"""
    step(f"模式：板块漏斗 — {author} / {sector}")

    profile = load_profile(author)
    if not profile:
        return False

    market_data = load_market_data(market_data_file)

    task = generate_sector_task(author, profile, sector, market_data)

    today = datetime.now().strftime("%Y-%m-%d")
    task_file = OUTPUT_DIR / f"{author}_{sector}分析任务_{today}.md"
    task_file.write_text(task, encoding="utf-8")
    info(f"生成任务已保存：{task_file}")

    print()
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  板块分析任务已就绪{RESET}")
    print(f"  大V：{author}")
    print(f"  板块：{sector}")
    print(f"  任务文件：{task_file}")
    print(f"  输出到：{OUTPUT_DIR}/{author}_{sector}分析_{today}.md")
    print(f"{BOLD}{'='*60}{RESET}")

    return True


def run_track(author, stock):
    """观点跟踪"""
    step(f"模式：观点跟踪 — {author} / {stock}")

    profile = load_profile(author)
    if not profile:
        return False

    task = generate_track_task(author, profile, stock)

    today = datetime.now().strftime("%Y-%m-%d")
    task_file = OUTPUT_DIR / f"{author}_{stock}跟踪任务_{today}.md"
    task_file.write_text(task, encoding="utf-8")
    info(f"生成任务已保存：{task_file}")

    print()
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  观点跟踪任务已就绪{RESET}")
    print(f"  大V：{author}")
    print(f"  标的：{stock}")
    print(f"  任务文件：{task_file}")
    print(f"  输出到：{OUTPUT_DIR}/{author}_{stock}观点跟踪_{today}.md")
    print(f"{BOLD}{'='*60}{RESET}")

    return True


def list_profiles():
    """列出所有可用画像"""
    profiles = find_profiles()
    if not profiles:
        warn("未找到任何风格画像")
        warn(f"搜索路径: {PROFILES_DIR}")
        warn(f"请确认 profiles/ 目录下有已蒸馏的风格画像文件")
        return

    print(f"\n{BOLD}可用风格画像：{RESET}")
    for p in profiles:
        print(f"  {GREEN}✓{RESET} {p['author']}")
        print(f"    路径：{p['path']}")


def main():
    parser = argparse.ArgumentParser(description="公众号股票大V分析专家")
    parser.add_argument("--author", help="指定大V名称")
    parser.add_argument("--mode", choices=["daily", "team", "sector", "track", "screen", "portfolio", "earnings", "sync"], help="分析模式")
    parser.add_argument("--authors", help="多V对比，逗号分隔（team模式）")
    parser.add_argument("--sector", help="板块名称（sector模式）")
    parser.add_argument("--stock", help="跟踪标的（track模式）/ 财报标的（earnings模式）")
    parser.add_argument("--stocks", help="持仓列表，逗号分隔（portfolio模式）")
    parser.add_argument("--period", type=int, default=30, help="回顾周期天数（portfolio模式，默认30）")
    parser.add_argument("--data", help="财报数据JSON文件（earnings模式）")
    parser.add_argument("--manual-input", action="store_true", help="手动输入数据（earnings模式）")
    parser.add_argument("--days", type=int, default=7, help="近N天数据（screen模式，默认7）")
    parser.add_argument("--market-data", help="盘面数据文件路径")
    parser.add_argument("--api-key", help="指定API Key（sync/validate等需要API的模式）")
    parser.add_argument("--list-profiles", action="store_true", help="列出可用画像")
    parser.add_argument("--check-env", action="store_true", help="检查环境")

    args = parser.parse_args()

    if args.check_env:
        sys.exit(0 if check_env() else 1)

    if args.list_profiles:
        list_profiles()
        sys.exit(0)

    if not args.mode:
        parser.print_help()
        print(f"\n{BOLD}已知大V：{RESET} {', '.join(STOCK_ANALYSTS)}")
        print(f"{BOLD}示例：{RESET}")
        print(f"  python analyze.py --author 财躺平 --mode daily")
        print(f"  python analyze.py --mode team --authors 财躺平,格兰投研")
        print(f"  python analyze.py --author 财躺平 --mode sector --sector 航天")
        print(f"  python analyze.py --author 财躺平 --mode screen --sector 半导体")
        print(f"  python analyze.py --author 财躺平 --mode portfolio --stocks 中国卫星,航发动力")
        print(f"  python analyze.py --author 格兰投研 --mode earnings --stock 贵州茅台")
        print(f"  python analyze.py --author 财躺平 --mode sync")
        sys.exit(0)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 调用记录上报（fire-and-forget，失败不影响主流程）──
    api_key = get_api_key(args.api_key)
    if api_key:
        authors_for_record = []
        if args.mode == "team" and args.authors:
            authors_for_record = [a.strip() for a in args.authors.split(",")]
        elif args.author:
            authors_for_record = [args.author]
        record_call(api_key, mode=args.mode, authors=authors_for_record if authors_for_record else None)

    if args.mode == "daily":
        if not args.author:
            error("--mode daily 需要 --author 参数")
            sys.exit(1)
        run_daily(args.author, args.market_data)

    elif args.mode == "team":
        if not args.authors:
            error("--mode team 需要 --authors 参数（逗号分隔）")
            sys.exit(1)
        authors_list = [a.strip() for a in args.authors.split(",")]
        run_team(authors_list, args.market_data)

    elif args.mode == "sector":
        if not args.author or not args.sector:
            error("--mode sector 需要 --author 和 --sector 参数")
            sys.exit(1)
        run_sector(args.author, args.sector, args.market_data)

    elif args.mode == "track":
        if not args.author or not args.stock:
            error("--mode track 需要 --author 和 --stock 参数")
            sys.exit(1)
        run_track(args.author, args.stock)

    elif args.mode == "screen":
        if not args.author:
            error("--mode screen 需要 --author 参数")
            sys.exit(1)
        ret = run_screen(args.author, args.sector, args.days)
        if ret != 0:
            sys.exit(ret)

    elif args.mode == "portfolio":
        if not args.author or not args.stocks:
            error("--mode portfolio 需要 --author 和 --stocks 参数")
            sys.exit(1)
        stocks_list = [s.strip() for s in args.stocks.split(",") if s.strip()]
        ret = run_portfolio(args.author, stocks_list, args.period)
        if ret != 0:
            sys.exit(ret)

    elif args.mode == "earnings":
        if not args.author or not args.stock:
            error("--mode earnings 需要 --author 和 --stock 参数")
            sys.exit(1)
        ret = run_earnings(args.author, args.stock, args.data, args.manual_input)
        if ret != 0:
            sys.exit(ret)

    elif args.mode == "sync":
        if not args.author:
            error("--mode sync 需要 --author 参数")
            sys.exit(1)
        ret = run_sync(args.author, args.days, args.api_key)
        if ret != 0:
            sys.exit(ret)


if __name__ == "__main__":
    main()
