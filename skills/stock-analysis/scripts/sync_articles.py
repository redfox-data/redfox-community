#!/usr/bin/env python3
"""
增量文章同步 — 拉取大V近7天新文章用于蒸馏补充
==============================================
每次触发 skill 时自动调用，获取最新文章内容，
为画像增量更新提供原始素材。

接口：queryWorkList（按公众号微信号精确查询）

Usage:
    python sync_articles.py --author "财躺平"
    python sync_articles.py --author "格兰投研" --days 7 --api-key ak_xxx
"""

import argparse
import json
import re
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


# ─── 生成增量摘要 ──────────────────────────────────────────────────────────────────
def extract_article_info(article):
    """从API返回的文章数据中提取关键字段"""
    # 调试：打印文章所有字段名（仅第一篇时）
    if not getattr(extract_article_info, "_debugged", False):
        if isinstance(article, dict):
            info(f"API返回字段列表: {list(article.keys())}")
            extract_article_info._debugged = True

    title = str(article.get("title") or article.get("作品标题") or article.get("Title") or "无标题")
    pub_time = str(article.get("publishTime") or article.get("publicTime") or article.get("作品发布时间") or article.get("PublishTime") or "")[:10]

    # 尝试多种可能的正文字段名
    content = ""
    for key in ("content", "作品正文", "Content", "workContent", "body", "text", "summary_content", "digest"):
        val = article.get(key)
        if val and str(val).strip():
            content = str(val)
            break

    # 尝试多种可能的摘要字段名
    summary = ""
    for key in ("summary", "摘要", "Summary", "workSummary", "description", "desc", "abstract"):
        val = article.get(key)
        if val and str(val).strip():
            summary = str(val)
            break

    # 如果没有摘要，取正文前300字
    if not summary and content:
        summary = content[:300] + ("..." if len(content) > 300 else "")

    # 如果没有正文但有摘要，用摘要作为正文
    if not content and summary:
        content = summary

    # 如果正文和摘要都为空，用标题作为摘要（queryWorkList 列表接口不返回正文）
    if not content and not summary:
        summary = f"（列表接口未返回正文，请访问 workUrl 获取全文）标题：{title}"

    # 提取 workUrl
    work_url = str(article.get("workUrl") or article.get("sourceUrl") or article.get("url") or "")

    # 提取正文中的股票/指数关键词
    stock_patterns = [
        r'([\u4e00-\u9fa5]{2,6}(?:股份|集团|科技|电子|银行|保险|证券|汽车|医药|能源|电力|控股|实业))',
        r'((?:上证|深证|沪深|创业板|科创板|北证)[\u4e00-\u9fa5]*)',
        r'((?:茅台|五粮液|比亚迪|宁德时代|腾讯|阿里|美团|京东|小米|华为)[\u4e00-\u9fa5]*)',
        r'(\d{6})\s*(?:SH|SZ|HK|\.SH|\.SZ)',
    ]
    mentioned_stocks = set()
    for pattern in stock_patterns:
        matches = re.findall(pattern, title + " " + summary + " " + content[:1000])
        mentioned_stocks.update(matches)

    word_count = len(content) if content else 0

    return {
        "title": title,
        "date": pub_time,
        "summary": summary[:500],
        "word_count": word_count,
        "mentioned_stocks": list(mentioned_stocks)[:10],
        "content_length": len(content) if content else 0,
        "work_url": work_url,
        "has_full_content": bool(content and word_count > 0),
    }


def generate_sync_report(author, profile, articles):
    """生成增量同步报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = []

    lines.append(f"# 增量文章同步 — {author}")
    lines.append(f"> 同步日期：{today}")
    lines.append(f"> 数据来源：queryWorkList（{ACCOUNT_IDS.get(author, '未知')}）")
    lines.append(f"> 新增文章数：{len(articles)}")
    lines.append("")

    if profile:
        lines.append(f"## 当前画像信息")
        lines.append(f"- 蒸馏日期：{profile.get('蒸馏日期', '未知')}")
        lines.append(f"- 样本文章数：{profile.get('样本文章数', '未知')}")
        lines.append(f"- 置信度：{profile.get('蒸馏置信度', '未知')}")

        # 获取画像中的常提及个股
        focus = profile.get("关注图谱", {})
        existing_stocks = focus.get("常提及个股", [])
        lines.append(f"- 画像常提及个股：{', '.join(existing_stocks) if existing_stocks else '无'}")
        lines.append("")

    if not articles:
        lines.append("## 结果")
        lines.append("近7天无新文章，画像无需更新。")
        return "\n".join(lines)

    # 文章详情
    lines.append(f"## 新增文章详情（共{len(articles)}篇）\n")

    all_new_stocks = set()
    total_words = 0

    for i, art in enumerate(articles, 1):
        info_dict = extract_article_info(art)
        lines.append(f"### 文章 {i}：{info_dict['title']}")
        lines.append(f"- 发布日期：{info_dict['date']}")
        if info_dict.get('has_full_content'):
            lines.append(f"- 字数：{info_dict['word_count']}")
        else:
            lines.append(f"- 字数：0（列表接口未返回正文）")
        if info_dict.get('work_url'):
            lines.append(f"- 文章链接：{info_dict['work_url']}")
        if info_dict['mentioned_stocks']:
            lines.append(f"- 提及个股：{', '.join(info_dict['mentioned_stocks'])}")
            all_new_stocks.update(info_dict['mentioned_stocks'])
        lines.append(f"- 摘要：")
        lines.append(f"  {info_dict['summary'][:200]}")
        lines.append("")
        total_words += info_dict['word_count']

    # 增量分析
    lines.append("## 增量分析\n")

    if profile:
        # 对比新文章中出现的股票 vs 画像中已有的
        focus = profile.get("关注图谱", {})
        existing_stocks = set(focus.get("常提及个股", []))
        new_stocks = all_new_stocks - existing_stocks

        if new_stocks:
            lines.append(f"### 新出现的个股/指数（画像中未收录）")
            for s in sorted(new_stocks):
                lines.append(f"- {s}")
            lines.append("")
            lines.append(f"**建议**：如新个股在多篇新文章中反复出现，考虑加入画像「常提及个股」列表。\n")
        else:
            lines.append("### 个股覆盖情况")
            lines.append("新文章中提及的个股均已在画像中收录，无需更新。\n")

        # 字数对比（仅当有正文数据时才比较）
        existing_avg = profile.get("内容深度", {}).get("平均字数", 0)
        if isinstance(existing_avg, str):
            m = re.search(r'(\d+)', existing_avg)
            existing_avg = int(m.group(1)) if m else 0
        new_avg = total_words // len(articles) if articles else 0
        if existing_avg > 0 and new_avg > 0:
            diff_pct = ((new_avg - existing_avg) / existing_avg) * 100
            if abs(diff_pct) > 20:
                lines.append(f"### 字数变化")
                lines.append(f"- 画像平均字数：{existing_avg}字")
                lines.append(f"- 近期平均字数：{new_avg}字（{diff_pct:+.0f}%）")
                lines.append(f"**建议**：更新画像「平均字数」字段。\n")
        elif new_avg == 0:
            lines.append("### 字数变化")
            lines.append("- 列表接口未返回正文，无法对比字数。")
            lines.append("- **建议**：访问文章链接获取全文后，手动对比字数。\n")

    # 蒸馏补充指令
    lines.append("## 蒸馏补充指令\n")
    lines.append("请阅读以上新增文章，检查是否需要更新画像：")
    lines.append("1. 常提及个股是否有新增")
    lines.append("2. 标志性表达是否有新发现")
    lines.append("3. 投资体系描述是否需要调整")
    lines.append("4. 平均字数/更新频率是否需要修正")
    lines.append("5. 如无需更新，跳过；如需更新，修改对应字段")

    return "\n".join(lines)


# ─── 主流程 ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="增量文章同步")
    parser.add_argument("--author", required=True, help="大V名称")
    parser.add_argument("--days", type=int, default=7, help="拉取近N天文章（默认7）")
    parser.add_argument("--api-key", help="API Key")

    args = parser.parse_args()

    # 获取 API Key
    api_key = get_api_key(args.api_key)
    if not api_key:
        sys.exit(1)

    # 查找微信号
    account = ACCOUNT_IDS.get(args.author)
    if not account:
        error(f"未知分析师：{args.author}，可用：{', '.join(ACCOUNT_IDS.keys())}")
        sys.exit(1)

    # 加载画像（可选）
    profile, profile_path = load_profile_json(args.author)
    if profile:
        info(f"已加载画像：{args.author}")
    else:
        warn(f"未找到画像，将仅输出文章数据")

    # 拉取文章
    step(f"拉取{args.author}({account})近{args.days}天新文章...")
    articles = fetch_articles_paginated(
        api_key, account, account_name=args.author,
        days=args.days, count=50,
        label=f"获取{args.author}近{args.days}天文章",
    )

    if not articles:
        warn(f"近{args.days}天无新文章")

    # 生成报告
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    report = generate_sync_report(args.author, profile, articles)

    report_file = OUTPUT_DIR / f"{args.author}_增量同步_{today}.md"
    report_file.write_text(report, encoding="utf-8")
    info(f"同步报告已生成：{report_file}")

    # 输出摘要
    print(f"\n{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}  增量文章同步完成{RESET}")
    print(f"{'='*50}")
    print(f"  大V：{args.author}")
    print(f"  时间范围：近{args.days}天")
    print(f"  新增文章：{len(articles)} 篇")
    print(f"  报告文件：{report_file}")
    if len(articles) > 0:
        print(f"  {BOLD}→ AI 请阅读报告，判断是否需要更新画像{RESET}")
    else:
        print(f"  {GREEN}→ 无需更新画像{RESET}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
