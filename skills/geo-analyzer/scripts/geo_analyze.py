#!/usr/bin/env python3
"""
GEO 分析编排器 — 读取搜索结果，执行确定性分析，输出分析数据

用法:
    # Step 1: 仅确定性分析（Agent 执行 AI 分析前）
    python3 geo_analyze.py --brand "品牌名" --search-results output/search_results.json

    # 可选参数
    --aliases '["别名1","别名2"]'          品牌别名
    --competitors '["竞品A","竞品B"]'       已知竞品
    --ai-analysis output/ai_analysis.json   AI 分析结果（有则合并输出完整报告数据）

输出:
    output/deterministic.json       确定性分析结果
    output/ai_analysis_template.json  AI 分析模板（供 Agent 填充）
    output/analysis_result.json     合并后的完整分析（当提供 --ai-analysis 时）
"""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from analyzer import (
    detect_all_mentions,
    extract_domains_from_sources,
    aggregate_domains,
    compute_mention_rate,
    build_mention_matrix,
    compute_per_answer_analysis,
    compute_aggregate_metrics,
    build_ai_analysis_template,
    build_analysis_prompt,
    merge_analysis,
    compute_sentiment_distribution,
    compute_brand_avg_rank,
    compute_competitor_metrics,
    compute_geo_score,
)
from platforms import PLATFORMS


def main():
    parser = argparse.ArgumentParser(description="GEO 分析编排器")
    parser.add_argument("--brand", required=True, help="品牌名称")
    parser.add_argument("--aliases", default="[]", help="品牌别名 JSON 列表")
    parser.add_argument("--competitors", default="[]", help="已知竞品 JSON 列表")
    parser.add_argument(
        "--search-results",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "search_results.json"),
        help="搜索结果 JSON 路径",
    )
    parser.add_argument(
        "--ai-analysis",
        default=None,
        help="AI 分析结果 JSON 路径（有则合并输出完整分析）",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="输出目录（默认 output/）",
    )
    args = parser.parse_args()

    # ── 解析参数 ──────────────────────────────────────────
    brand = args.brand
    aliases = json.loads(args.aliases) if args.aliases else []
    competitors = json.loads(args.competitors) if args.competitors else []

    # 品牌关键词 = 品牌名 + 别名
    brand_keywords = [brand] + aliases

    # 竞品关键词映射（默认竞品名就是关键词）
    competitor_map = {}
    for comp in competitors:
        competitor_map[comp] = [comp]

    output_dir = args.output_dir or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "output"
    )
    os.makedirs(output_dir, exist_ok=True)

    # ── 读取搜索结果 ──────────────────────────────────────
    search_path = args.search_results
    if not os.path.exists(search_path):
        print(json.dumps({"error": f"搜索结果文件不存在: {search_path}"}, ensure_ascii=False))
        sys.exit(1)

    with open(search_path, "r", encoding="utf-8") as f:
        search_data = json.load(f)

    results = search_data.get("results", [])
    queries = search_data.get("queries", [])
    platforms = search_data.get("platforms", ["doubao", "kimi", "deepseek"])

    print(f"品牌: {brand}", file=sys.stderr)
    print(f"别名: {aliases}", file=sys.stderr)
    print(f"竞品: {competitors}", file=sys.stderr)
    print(f"搜索结果: {len(results)} 条，平台: {platforms}", file=sys.stderr)

    # ── Phase 1: 确定性分析 ────────────────────────────────
    print("\n执行确定性分析...", file=sys.stderr)

    per_answer = compute_per_answer_analysis(results, brand_keywords, competitor_map)
    metrics = compute_aggregate_metrics(per_answer, queries, platforms, brand, competitors)
    mention_matrix = build_mention_matrix(results, queries, platforms, brand_keywords)

    deterministic = {
        "brand": brand,
        "aliases": aliases,
        "competitors": competitors,
        "platforms": platforms,
        "queries": queries,
        "per_answer": per_answer,
        "metrics": metrics,
        "mention_matrix": mention_matrix,
    }

    det_path = os.path.join(output_dir, "deterministic.json")
    with open(det_path, "w", encoding="utf-8") as f:
        json.dump(deterministic, f, ensure_ascii=False, indent=2)
    print(f"确定性分析已保存: {det_path}", file=sys.stderr)

    # ── Phase 2: 生成 AI 分析模板 ──────────────────────────
    ai_template = build_ai_analysis_template(results, brand, competitors)

    template_path = os.path.join(output_dir, "ai_analysis_template.json")
    with open(template_path, "w", encoding="utf-8") as f:
        json.dump(ai_template, f, ensure_ascii=False, indent=2)
    print(f"AI 分析模板已保存: {template_path}", file=sys.stderr)

    # 输出 AI 分析提示
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"AI 分析任务: 请对 {len(ai_template)} 份回答执行 AI 分析", file=sys.stderr)
    print(f"模板文件: {template_path}", file=sys.stderr)
    print(f"每份回答需填充字段: brand_rank, brand_context, sentiment,", file=sys.stderr)
    print(f"  sentiment_reason, competitors_mentioned, key_claims", file=sys.stderr)
    print(f"完成后保存为: {os.path.join(output_dir, 'ai_analysis.json')}", file=sys.stderr)
    print(f"然后重新运行本脚本添加 --ai-analysis 参数生成完整报告数据", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)

    # ── Phase 3: 合并 AI 分析（如果提供）──────────────────
    if args.ai_analysis and os.path.exists(args.ai_analysis):
        print("检测到 AI 分析结果，开始合并...", file=sys.stderr)

        with open(args.ai_analysis, "r", encoding="utf-8") as f:
            ai_data = json.load(f)

        # 合并确定性 + AI 分析
        merged = merge_analysis(per_answer, ai_data)

        # 计算需要 AI 数据的指标
        sentiment_dist = compute_sentiment_distribution(merged, platforms)
        brand_avg_rank = compute_brand_avg_rank(merged, platforms)

        # 收集所有竞品（用户指定 + AI 发现）
        all_competitors = set(competitors)
        for ai in ai_data:
            for comp in ai.get("competitors_mentioned", []):
                all_competitors.add(comp)

        # 计算竞品指标（平均排名 + 情绪分布）
        competitor_metrics = compute_competitor_metrics(merged, platforms, all_competitors)

        # 计算 GEO 综合得分
        geo_score = {}
        geo_score["overall"] = compute_geo_score(
            metrics["brand_mention_rate"]["overall"],
            brand_avg_rank["overall"],
            sentiment_dist["overall"],
        )
        for p in platforms:
            geo_score[p] = compute_geo_score(
                metrics["brand_mention_rate"].get(p, 0),
                brand_avg_rank.get(p),
                sentiment_dist.get(p, {"positive": 0, "neutral": 0, "negative": 0}),
            )

        # 计算竞品提及率（覆盖所有竞品，含 AI 发现的）
        comp_mention_rates = {}
        for comp in all_competitors:
            rates = {"overall": 0.0}
            for p in platforms:
                rates[p] = 0.0
            total_done = 0
            total_hit = 0
            p_stats = {p: {"t": 0, "h": 0} for p in platforms}
            comp_lower = comp.lower()
            for ans in merged:
                if ans.get("status") != "completed":
                    continue
                p = ans.get("platform", "")
                total_done += 1
                p_stats.setdefault(p, {"t": 0, "h": 0})
                p_stats[p]["t"] += 1
                # 确定性匹配
                det_count = ans.get("competitor_mentions", {}).get(comp, 0)
                # AI 发现匹配（模糊匹配）
                ai_mentioned = False
                if det_count == 0:
                    for ai_comp in ans.get("ai_competitors_mentioned", []):
                        if comp_lower == ai_comp.lower() or comp_lower in ai_comp.lower() or ai_comp.lower() in comp_lower:
                            ai_mentioned = True
                            break
                if det_count > 0 or ai_mentioned:
                    total_hit += 1
                    p_stats[p]["h"] += 1
            rates["overall"] = total_hit / total_done if total_done > 0 else 0.0
            for p in platforms:
                ps = p_stats.get(p, {"t": 0, "h": 0})
                rates[p] = ps["h"] / ps["t"] if ps["t"] > 0 else 0.0
            comp_mention_rates[comp] = rates

        # 竞品对比矩阵
        competitor_comparison = []
        for comp in sorted(all_competitors):
            comp_rates = comp_mention_rates.get(comp, {"overall": 0})
            comp_m = competitor_metrics.get(comp, {})
            comp_avg_rank = comp_m.get("avg_rank", {})
            comp_sent = comp_m.get("sentiment", {})
            comp_sent_overall = comp_sent.get("overall", {"positive": 0, "neutral": 0, "negative": 0})
            comp_sent_total = sum(comp_sent_overall.values())
            competitor_comparison.append({
                "name": comp,
                "mention_rate_overall": comp_rates.get("overall", 0),
                "mention_rate_doubao": comp_rates.get("doubao", 0),
                "mention_rate_kimi": comp_rates.get("kimi", 0),
                "mention_rate_deepseek": comp_rates.get("deepseek", 0),
                "avg_rank": comp_avg_rank.get("overall"),
                "positive_pct": comp_sent_overall["positive"] / comp_sent_total if comp_sent_total > 0 else 0,
                "negative_pct": comp_sent_overall["negative"] / comp_sent_total if comp_sent_total > 0 else 0,
                "sentiment_dist": comp_sent_overall,
            })

        analysis_result = {
            "brand": brand,
            "aliases": aliases,
            "competitors": competitors,
            "discovered_competitors": list(all_competitors - set(competitors)),
            "all_competitors": sorted(all_competitors),
            "platforms": platforms,
            "queries": queries,
            "per_answer": merged,
            "metrics": metrics,
            "mention_matrix": mention_matrix,
            "sentiment_distribution": sentiment_dist,
            "brand_avg_rank": brand_avg_rank,
            "geo_score": geo_score,
            "competitor_comparison": competitor_comparison,
            "competitor_metrics": competitor_metrics,
        }

        result_path = os.path.join(output_dir, "analysis_result.json")
        with open(result_path, "w", encoding="utf-8") as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        print(f"完整分析结果已保存: {result_path}", file=sys.stderr)

        # stdout 输出摘要
        summary = {
            "brand": brand,
            "geo_score": geo_score,
            "mention_rate": metrics["brand_mention_rate"],
            "sentiment": sentiment_dist,
            "avg_rank": brand_avg_rank,
            "total_competitors": len(all_competitors),
            "output": result_path,
        }
        print(json.dumps(summary, ensure_ascii=False))
    else:
        # 无 AI 分析，仅输出确定性分析摘要
        summary = {
            "brand": brand,
            "deterministic_only": True,
            "mention_rate": metrics["brand_mention_rate"],
            "total_completed": metrics["total_completed"],
            "total_mentioned": metrics["total_mentioned"],
            "top_domains": list(metrics["domain_stats"].items())[:10],
            "deterministic_output": det_path,
            "ai_template_output": template_path,
            "next_step": "请根据 ai_analysis_template.json 对每份回答执行 AI 分析，保存为 ai_analysis.json 后重新运行",
        }
        print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
