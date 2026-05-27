#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书低粉爆款笔记HTML生成脚本
当用户回复"2"确认生成HTML时，由智能体调用此脚本
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

# 将scripts目录加入path以便导入主脚本中的函数
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_explosive_articles import (
    fetch_ranking_data,
    process_ranking_data,
    match_category,
    generate_html_from_template,
)


def get_latest_data_date():
    """根据当前时间计算最新数据日期"""
    now = datetime.now()
    if now.hour > 19 or (now.hour == 19 and now.minute >= 30):
        return (now - timedelta(days=1)).strftime("%Y-%m-%d")
    else:
        return (now - timedelta(days=2)).strftime("%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser(description="生成小红书低粉爆款笔记HTML文件")
    parser.add_argument("--rank_date", type=str, help="查询日期 YYYY-MM-DD")
    parser.add_argument("--keyword", type=str, default="综合全部", help="分类关键词")
    parser.add_argument("--top_n", type=int, default=50, help="HTML展示条数")
    parser.add_argument("--output", type=str, help="输出HTML文件路径")
    args = parser.parse_args()

    try:
        # 确定分类
        query_category = match_category(args.keyword) if args.keyword else "综合全部"

        # 确定日期
        rank_date = args.rank_date or get_latest_data_date()

        # 获取数据
        result = fetch_ranking_data(
            rank_date=rank_date,
            category=query_category,
            source="小红书冷门账号爆款文章-GitHub"
        )

        if result["type"] != "data":
            print(json.dumps({"status": "error", "message": "无法获取数据"}, ensure_ascii=False))
            return 1

        articles = process_ranking_data(result["data"], args.top_n)

        if not articles:
            print(json.dumps({"status": "error", "message": "无可用数据"}, ensure_ascii=False))
            return 1

        # 生成HTML文件
        import time as _time
        if args.output:
            html_output = args.output
        else:
            file_timestamp = str(int(_time.time() * 1000))
            safe_category = query_category.replace("/", "-")
            file_base = f"小红书{safe_category}低粉爆款数据_{file_timestamp}"
            html_output = f"./{file_base}.html"

        html_result = generate_html_from_template(
            keyword=query_category,
            articles=articles,
            rank_date=rank_date,
            top_n=args.top_n,
            output=html_output
        )

        if html_result:
            print(json.dumps({"status": "success", "file": html_output}, ensure_ascii=False))
            return 0
        else:
            print(json.dumps({"status": "error", "message": "HTML生成失败"}, ensure_ascii=False))
            return 1

    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
