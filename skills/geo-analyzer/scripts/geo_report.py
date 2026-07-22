#!/usr/bin/env python3
"""
GEO 报告生成器 — 读取分析结果，生成交互式 HTML 报告

用法:
    python3 geo_report.py --analysis output/analysis_result.json

    # 可选: 附带原始搜索结果（用于原始回答存档模块）
    --search-results output/search_results.json

输出:
    output/geo_report.html
"""

import sys
import os
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from report_template import generate_html


def main():
    parser = argparse.ArgumentParser(description="GEO 报告生成器")
    parser.add_argument(
        "--analysis",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "analysis_result.json"),
        help="分析结果 JSON 路径",
    )
    parser.add_argument(
        "--search-results",
        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "search_results.json"),
        help="搜索结果 JSON 路径（可选，用于原始回答存档）",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="输出 HTML 路径（默认 output/geo_report.html）",
    )
    args = parser.parse_args()

    # ── 读取分析结果 ──────────────────────────────────────
    if not os.path.exists(args.analysis):
        print(json.dumps({"error": f"分析结果文件不存在: {args.analysis}"}, ensure_ascii=False))
        sys.exit(1)

    with open(args.analysis, "r", encoding="utf-8") as f:
        analysis = json.load(f)

    # ── 读取搜索结果（可选）────────────────────────────────
    search_results = None
    if os.path.exists(args.search_results):
        with open(args.search_results, "r", encoding="utf-8") as f:
            search_results = json.load(f)

    # ── 生成 HTML ────────────────────────────────────────
    print("正在生成 HTML 报告...", file=sys.stderr)
    html_content = generate_html(analysis, search_results)

    # ── 写入文件 ─────────────────────────────────────────
    output_path = args.output or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "output", "geo_report.html"
    )
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"报告已生成: {output_path}", file=sys.stderr)

    # stdout 输出摘要
    brand = analysis.get("brand", "")
    geo_score = analysis.get("geo_score", {})
    summary = {
        "brand": brand,
        "output": output_path,
        "geo_score": geo_score,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
