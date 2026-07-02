#!/usr/bin/env python3
"""
蒸馏准确性校验 — 验证风格画像是否真实反映大V写作特征
=====================================================
从 API 拉取大V近期文章，与画像声明交叉比对，生成校验任务供 AI 评分。

校验逻辑：
1. 加载画像 JSON，提取可验证声明（关注个股、标志性表达、投资体系等）
2. 拉取该大V近期 N 篇文章
3. 生成校验任务文件：每篇文章配对一组校验问题
4. AI Agent 阅读任务文件，仅凭画像回答，再与文章正文比对
5. 输出准确率评分，< 80% 打回补充蒸馏

Usage:
    python validate_profile.py --author "财躺平" --sample 10
    python validate_profile.py --author "格兰投研" --sample 15 --api-key ak_xxx
"""

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

from common import (
    ACCOUNT_IDS, STOCK_ANALYSTS, PROFILES_DIR, OUTPUT_DIR,
    GREEN, YELLOW, RED, CYAN, BOLD, RESET,
    info, warn, error, step,
    get_api_key, load_profile_json,
    fetch_articles_paginated, ensure_output_dir,
)


# ─── 提取画像可验证声明 ────────────────────────────────────────────────────────────
def extract_profile_claims(profile):
    """从画像JSON中提取可验证的声明"""
    claims = {}

    # 1. 关注个股
    focus = profile.get("关注图谱", {})
    stocks = focus.get("常提及个股", [])
    claims["常提及个股"] = stocks if isinstance(stocks, list) else []

    # 2. 核心赛道
    sectors = focus.get("核心赛道", [])
    claims["核心关注赛道"] = sectors if isinstance(sectors, list) else []

    # 3. 标志性表达
    expr = profile.get("表达风格", {})
    sig_phrases = expr.get("标志性表达", [])
    claims["标志性表达"] = sig_phrases if isinstance(sig_phrases, list) else []

    # 4. 投资格言
    mottos = focus.get("投资格言", [])
    claims["投资格言"] = mottos if isinstance(mottos, list) else []

    # 5. 常用指标
    indicators = focus.get("常用指标", [])
    claims["常用分析指标"] = indicators if isinstance(indicators, list) else []

    # 6. 投资体系关键特征
    inv = profile.get("投资体系", {})
    claims["核心投资流派"] = inv.get("核心流派", "")
    claims["持仓周期"] = inv.get("持仓周期", "")
    claims["止损纪律"] = inv.get("止损纪律", "")

    # 7. 表达风格关键特征
    claims["标题风格"] = expr.get("标题风格", "")
    claims["开头模式"] = expr.get("开头模式", "")
    claims["结尾模式"] = expr.get("结尾模式", "")
    claims["语气"] = expr.get("语气", "")

    # 8. 内容深度
    depth = profile.get("内容深度", {})
    claims["平均字数"] = depth.get("平均字数", 0)
    claims["更新频率"] = depth.get("更新频率", "")

    return claims


# ─── 生成校验任务 ──────────────────────────────────────────────────────────────────
def generate_validation_task(author, profile, articles, sample_count=10):
    """生成蒸馏准确性校验任务文件"""
    claims = extract_profile_claims(profile)
    today = datetime.now().strftime("%Y-%m-%d")

    # 随机抽样文章
    if len(articles) > sample_count:
        sampled = random.sample(articles, sample_count)
    else:
        sampled = articles

    lines = []
    lines.append(f"# 蒸馏准确性校验任务 — {author}")
    lines.append(f"> 日期：{today}")
    lines.append(f"> 抽样文章数：{len(sampled)}/{len(articles)}")
    lines.append(f"> 画像置信度：{profile.get('蒸馏置信度', '未知')}")
    lines.append(f"> 样本文章数：{profile.get('样本文章数', '未知')}")
    lines.append(f"> ⚠️ AI 风格模拟，不构成投资建议\n")

    # ── 画像声明摘要 ──
    lines.append("## 一、画像声明摘要（仅凭此回答问题）\n")
    lines.append(f"```json")
    lines.append(json.dumps(claims, ensure_ascii=False, indent=2))
    lines.append(f"```\n")

    # ── 校验问题 ──
    lines.append("## 二、校验问题（请仅凭画像回答，然后再看文章验证）\n")
    lines.append("### A. 个股提及校验\n")
    lines.append("对以下每篇文章，请仅凭画像的「常提及个股」列表预测：该文章最可能提到哪些股票/指数？")
    lines.append("然后与文章实际内容比对，标注预测是否正确。\n")

    for i, art in enumerate(sampled, 1):
        title = str(art.get("title", art.get("作品标题", "未知标题")))
        pub = str(art.get("publishTime") or art.get("publicTime") or art.get("作品发布时间") or "")[:10]
        content = str(art.get("content") or art.get("作品正文") or art.get("summary") or "")
        # 截取前500字作为正文摘要
        content_preview = content[:500] if len(content) > 500 else content

        lines.append(f"#### 文章 {i}：{title}")
        lines.append(f"- 发布日期：{pub}")
        lines.append(f"- 正文摘要（前500字）：")
        lines.append(f"```")
        lines.append(content_preview)
        lines.append(f"```")
        lines.append(f"- **画像预测**：（请AI填写）该文章可能提及的个股/指数")
        lines.append(f"- **实际验证**：（请AI阅读正文后填写）文章实际提及的个股/指数")
        lines.append(f"- **判定**：✅ 命中 / ❌ 未命中 / ⚠️ 部分命中\n")

    lines.append("### B. 风格特征校验\n")
    lines.append("对以下维度，判断画像描述是否与文章实际风格一致：\n")

    style_checks = [
        ("语气一致性", f"画像描述语气为：{claims.get('语气', '未知')}。请判断文章实际语气是否匹配。"),
        ("标志性表达", f"画像标志性表达：{', '.join(claims.get('标志性表达', [])[:5])}。请检查文章中是否出现这些表达或类似表达。"),
        ("标题风格", f"画像标题风格：{claims.get('标题风格', '未知')}。请判断文章标题是否符合该描述。"),
        ("开头模式", f"画像开头模式：{claims.get('开头模式', '未知')}。请判断文章开头是否符合该描述。"),
        ("结尾模式", f"画像结尾模式：{claims.get('结尾模式', '未知')}。请判断文章结尾是否符合该描述。"),
        ("文章长度", f"画像平均字数：{claims.get('平均字数', '未知')}字。请估算文章实际字数并判断是否在±30%范围内。"),
    ]

    for name, desc in style_checks:
        lines.append(f"#### {name}")
        lines.append(f"- 校验说明：{desc}")
        lines.append(f"- **判定**：✅ 一致 / ❌ 不一致 / ⚠️ 部分一致\n")

    lines.append("### C. 投资体系校验\n")
    lines.append("综合所有抽样文章，判断画像的投资体系描述是否准确：\n")

    system_checks = [
        ("核心投资流派", claims.get("核心投资流派", "")),
        ("持仓周期", claims.get("持仓周期", "")),
        ("止损纪律", claims.get("止损纪律", "")),
    ]

    for name, desc in system_checks:
        lines.append(f"#### {name}")
        lines.append(f"- 画像描述：{desc}")
        lines.append(f"- **实际表现**：（请AI综合文章判断）")
        lines.append(f"- **判定**：✅ 准确 / ❌ 不准确 / ⚠️ 部分准确\n")

    # ── 评分模板 ──
    lines.append("## 三、评分汇总\n")
    lines.append("| 校验维度 | 总题数 | 命中数 | 准确率 |")
    lines.append("|---------|--------|--------|--------|")
    lines.append(f"| A. 个股提及 | {len(sampled)} | ? | ?% |")
    lines.append(f"| B. 风格特征 | {len(style_checks)} | ? | ?% |")
    lines.append(f"| C. 投资体系 | {len(system_checks)} | ? | ?% |")
    lines.append("| **综合** | ? | ? | **?%** |")
    lines.append("")
    lines.append("**准出标准：综合准确率 ≥ 80%**")
    lines.append("**< 80% 需补充蒸馏：仔细阅读文章正文，更新画像中不准确的字段**")
    lines.append("")
    lines.append("## 四、补充蒸馏建议（如准确率 < 80%）\n")
    lines.append("请列出画像中需要修正的具体字段和建议修正内容：\n")
    lines.append("| 字段 | 当前值 | 建议修正为 | 依据 |")
    lines.append("|------|--------|-----------|------|")

    return "\n".join(lines)


# ─── 主流程 ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="蒸馏准确性校验")
    parser.add_argument("--author", required=True, help="大V名称")
    parser.add_argument("--sample", type=int, default=10, help="抽样文章数（默认10）")
    parser.add_argument("--days", type=int, default=30, help="拉取近N天文章（默认30）")
    parser.add_argument("--api-key", help="API Key")

    args = parser.parse_args()

    # 加载画像
    profile, _ = load_profile_json(args.author)
    if not profile:
        error(f"未找到大V「{args.author}」的风格画像")
        sys.exit(1)
    info(f"已加载画像：{args.author}")

    # 获取 API Key
    api_key = get_api_key(args.api_key)
    if not api_key:
        error("蒸馏校验需要 API Key 拉取文章")
        sys.exit(1)

    # 查找微信号
    account = ACCOUNT_IDS.get(args.author)
    if not account:
        error(f"未知分析师：{args.author}，可用：{', '.join(ACCOUNT_IDS.keys())}")
        sys.exit(1)

    # 拉取文章
    step(f"拉取{args.author}({account})近{args.days}天文章...")
    articles = fetch_articles_paginated(
        api_key, account, account_name=args.author,
        days=args.days, count=max(args.sample * 3, 50),
        label=f"获取{args.author}文章",
    )

    if not articles:
        error(f"未获取到{args.author}的文章，请检查 API Key 和账号名")
        sys.exit(1)

    info(f"共获取 {len(articles)} 篇文章")

    # 生成校验任务
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    task = generate_validation_task(args.author, profile, articles, args.sample)

    task_file = OUTPUT_DIR / f"{args.author}_蒸馏校验_{today}.md"
    task_file.write_text(task, encoding="utf-8")
    info(f"校验任务已生成：{task_file}")

    # 输出摘要
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  蒸馏准确性校验任务已就绪{RESET}")
    print(f"{'='*60}")
    print(f"  大V：{args.author}")
    print(f"  画像置信度：{profile.get('蒸馏置信度', '未知')}")
    print(f"  样本文章数：{profile.get('样本文章数', '未知')}")
    print(f"  本次拉取：{len(articles)} 篇")
    print(f"  抽样校验：{min(args.sample, len(articles))} 篇")
    print(f"  任务文件：{task_file}")
    print(f"{'─'*60}")
    print(f"  {BOLD}校验流程：{RESET}")
    print(f"  1. AI 仅凭画像声明回答校验问题（不看文章正文）")
    print(f"  2. 然后阅读文章正文，比对预测与实际内容")
    print(f"  3. 计算综合准确率")
    print(f"  4. {GREEN}≥ 80% → 蒸馏通过{RESET}")
    print(f"  5. {RED}< 80% → 需补充蒸馏，更新画像{RESET}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
