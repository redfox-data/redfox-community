#!/usr/bin/env python3
"""
GEO 搜索调度器 — 3平台 x N问题 批量提交 + 并行轮询

用法:
    python3 geo_search.py --queries '["问题1","问题2",...]' --platforms doubao,kimi,deepseek

输出:
    output/search_results.json

环境变量:
    REDFOX_API_KEY — 红狐 API Key（必填）
"""

import sys
import os
import json
import time
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# 将 lib 目录加入搜索路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

from platforms import PLATFORMS, submit, poll, extract_result_full, is_valid_answer, API_KEY

POLL_INTERVAL = 5        # 轮询间隔（秒）
MAX_POLL_TIME = 900      # 最长等待 15 分钟（DeepSeek 深度搜索较慢）
MAX_WORKERS = 6          # 并发线程数（降低避免 Kimi 限流）
MAX_ANSWER_RETRY = 1     # 平台返回错误话术（限流/故障）时的重试次数


def main():
    parser = argparse.ArgumentParser(description="GEO 批量搜索调度器")
    parser.add_argument(
        "--queries",
        required=True,
        help='问题列表 JSON，如 \'["问题1","问题2"]\'',
    )
    parser.add_argument(
        "--platforms",
        default="doubao,kimi,deepseek",
        help="平台列表，逗号分隔（默认 doubao,kimi,deepseek）",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="输出文件路径（默认 output/search_results.json）",
    )
    args = parser.parse_args()

    # ── 前置检查 ──────────────────────────────────────────
    if not API_KEY:
        result = {
            "error": (
                "未配置 REDFOX_API_KEY 环境变量，"
                "请前往 https://redfox.hk/settings/api-keys?source=github 获取 API Key"
            )
        }
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)

    queries = json.loads(args.queries)
    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]

    for p in platforms:
        if p not in PLATFORMS:
            print(json.dumps({"error": f"未知平台: {p}，可选: {list(PLATFORMS.keys())}"}, ensure_ascii=False))
            sys.exit(1)

    total = len(queries) * len(platforms)
    output_path = args.output or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "output", "search_results.json"
    )
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    print(f"开始搜索: {len(queries)} 个问题 x {len(platforms)} 个平台 = {total} 个任务", file=sys.stderr)

    # ── Phase 1: 批量提交所有任务 ──────────────────────────
    tasks = []  # [{query, platform, query_index, task_id | error}]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_map = {}
        for qi, query in enumerate(queries):
            for platform in platforms:
                future = executor.submit(submit, platform, query)
                future_map[future] = {
                    "query": query,
                    "platform": platform,
                    "query_index": qi,
                }

        for future in as_completed(future_map):
            info = future_map[future]
            try:
                task_id = future.result()
                info["task_id"] = task_id
                print(f"  [提交] {info['platform']} Q{info['query_index']+1} -> {task_id}", file=sys.stderr)
            except Exception as e:
                info["task_id"] = None
                info["error"] = str(e)
                print(f"  [提交失败] {info['platform']} Q{info['query_index']+1} -> {e}", file=sys.stderr)
            tasks.append(info)

    submitted_ok = [t for t in tasks if t.get("task_id")]
    print(f"\n提交完成: {len(submitted_ok)}/{total} 成功，开始轮询...\n", file=sys.stderr)

    # ── Phase 2: 并行轮询所有任务 ──────────────────────────
    results = []
    pending = list(submitted_ok)
    max_attempts = MAX_POLL_TIME // POLL_INTERVAL

    for attempt in range(1, max_attempts + 1):
        if not pending:
            break

        time.sleep(POLL_INTERVAL)

        still_pending = []
        completed_this_round = 0

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_map = {}
            for task in pending:
                future = executor.submit(poll, task["platform"], task["task_id"])
                future_map[future] = task

            for future in as_completed(future_map):
                task = future_map[future]
                try:
                    raw = future.result()
                    if raw is not None:
                        # 任务完成 —— 先校验是否为真实回答
                        ex = extract_result_full(task["platform"], raw)
                        valid, reason = is_valid_answer(ex["content"])

                        if not valid:
                            retries = task.get("answer_retry", 0)
                            if retries < MAX_ANSWER_RETRY:
                                # 平台限流/故障话术，重新提交一次
                                try:
                                    task["task_id"] = submit(task["platform"], task["query"])
                                    task["answer_retry"] = retries + 1
                                    still_pending.append(task)
                                    print(
                                        f"  [重试] {task['platform']} Q{task['query_index']+1}"
                                        f" -> {reason}，已重新提交",
                                        file=sys.stderr,
                                    )
                                except Exception as e:
                                    results.append({
                                        "question": task["query"],
                                        "query_index": task["query_index"],
                                        "platform": task["platform"],
                                        "content": "",
                                        "sources": [],
                                        "status": "invalid",
                                        "error": f"{reason}；重试提交失败: {e}",
                                    })
                                    print(
                                        f"  [无效] {task['platform']} Q{task['query_index']+1}"
                                        f" -> {reason}",
                                        file=sys.stderr,
                                    )
                                continue

                            # 重试后仍无效：标记 invalid，排除出统计（不计入分母）
                            results.append({
                                "question": task["query"],
                                "query_index": task["query_index"],
                                "platform": task["platform"],
                                "content": "",
                                "sources": [],
                                "status": "invalid",
                                "error": reason,
                            })
                            completed_this_round += 1
                            print(
                                f"  [无效] {task['platform']} Q{task['query_index']+1}"
                                f" -> {reason}（已排除出统计）",
                                file=sys.stderr,
                            )
                            continue

                        entry = {
                            "question": task["query"],
                            "query_index": task["query_index"],
                            "platform": task["platform"],
                            "content": ex["content"],
                            "sources": ex["sources"],
                            "sources_available": ex["sources_available"],
                            "status": "completed",
                        }
                        if ex["sources_note"]:
                            entry["sources_note"] = ex["sources_note"]
                        results.append(entry)
                        completed_this_round += 1
                        print(f"  [完成] {task['platform']} Q{task['query_index']+1}", file=sys.stderr)
                    else:
                        still_pending.append(task)
                except Exception as e:
                    results.append({
                        "question": task["query"],
                        "query_index": task["query_index"],
                        "platform": task["platform"],
                        "content": "",
                        "sources": [],
                        "status": "failed",
                        "error": str(e),
                    })
                    print(f"  [失败] {task['platform']} Q{task['query_index']+1} -> {e}", file=sys.stderr)

        pending = still_pending
        if pending:
            print(f"  轮询 {attempt}: 本轮完成 {completed_this_round}，剩余 {len(pending)} 等待中...", file=sys.stderr)

    # 处理超时任务
    for task in pending:
        results.append({
            "question": task["query"],
            "query_index": task["query_index"],
            "platform": task["platform"],
            "content": "",
            "sources": [],
            "status": "timeout",
        })

    # 处理提交失败的任务
    for task in tasks:
        if task.get("task_id") is None:
            results.append({
                "question": task["query"],
                "query_index": task["query_index"],
                "platform": task["platform"],
                "content": "",
                "sources": [],
                "status": "submit_failed",
                "error": task.get("error", "Unknown"),
            })

    # 按 query_index + platform 排序
    platform_order = {p: i for i, p in enumerate(platforms)}
    results.sort(key=lambda r: (r.get("query_index", 0), platform_order.get(r.get("platform", ""), 99)))

    output = {
        "queries": queries,
        "platforms": platforms,
        "total_tasks": total,
        "completed": len([r for r in results if r["status"] == "completed"]),
        "invalid": len([r for r in results if r["status"] == "invalid"]),
        "failed": len([r for r in results if r["status"] not in ("completed", "invalid")]),
        "results": results,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    summary = f"\n搜索完成: {output['completed']}/{total} 条有效"
    if output["invalid"]:
        summary += f"，{output['invalid']} 条平台异常已排除"
    if output["failed"]:
        summary += f"，{output['failed']} 条失败"
    print(summary, file=sys.stderr)
    print(f"结果已保存: {output_path}", file=sys.stderr)

    # stdout 输出 JSON 供 Agent 解析
    print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
