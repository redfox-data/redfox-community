#!/usr/bin/env python3
"""
豆包 WebSearch — 提交搜索查询并轮询结果

用法:
    python3 doubao_search.py "<搜索关键词>" [source标识]

环境变量:
    REDFOX_API_KEY — 红狐 API Key（必填）
"""

import os
import sys
import json
import time

import requests

API_BASE = "https://redfox.hk/story/api/doubaoSearch"
API_KEY = os.environ.get("REDFOX_API_KEY")
MAX_ATTEMPTS = 60  # 最多轮询 5 分钟
POLL_INTERVAL = 5  # 轮询间隔（秒）


def main():
    if not API_KEY:
        print(
            json.dumps(
                {
                    "error": (
                        "未配置 REDFOX_API_KEY 环境变量，"
                        "请前往 https://redfox.hk/settings/api-keys?source=github 获取 API Key"
                    )
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    if len(sys.argv) < 2:
        print(json.dumps({"error": "请提供搜索关键词"}, ensure_ascii=False))
        sys.exit(1)

    query = sys.argv[1]
    source = sys.argv[2] if len(sys.argv) > 2 else "豆包websearch-GitHub"

    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }

    # ── Step 1: 提交搜索 ──────────────────────────────────────────────
    try:
        submit_resp = requests.post(
            f"{API_BASE}/submit",
            json={"inquiry_text": query, "source": source},
            headers=headers,
            timeout=30,
        )
        submit_resp.raise_for_status()
        submit_data = submit_resp.json()
    except requests.RequestException as e:
        print(json.dumps({"error": f"提交搜索请求失败: {e}"}, ensure_ascii=False))
        sys.exit(1)

    task_id = submit_data.get("data", {}).get("taskId")
    if not task_id:
        print(
            json.dumps(
                {"error": f"提交失败，未获取到 taskId: {submit_data}"},
                ensure_ascii=False,
            )
        )
        sys.exit(1)

    print(
        f"⏳ 已提交搜索请求 (taskId: {task_id})，正在等待豆包 WebSearch 返回结果…",
        file=sys.stderr,
    )

    # ── Step 2: 轮询结果 ──────────────────────────────────────────────
    for attempt in range(1, MAX_ATTEMPTS + 1):
        time.sleep(POLL_INTERVAL)

        try:
            result_resp = requests.post(
                f"{API_BASE}/result",
                json={"taskId": task_id},
                headers=headers,
                timeout=30,
            )
            result_resp.raise_for_status()
            result_data = result_resp.json()
        except requests.RequestException as e:
            print(
                f"⚠️ 第 {attempt} 次查询结果失败: {e}，继续重试…",
                file=sys.stderr,
            )
            continue

        status = result_data.get("data", {}).get("status", "")
        if not status:
            status = result_data.get("status", "")

        if status == "completed":
            # 成功：输出最终结果到 stdout
            print(json.dumps(result_data, ensure_ascii=False))
            return

        if status == "failed":
            print(
                json.dumps(
                    {"error": f"搜索任务失败: {result_data}"}, ensure_ascii=False
                )
            )
            sys.exit(1)

        # 仍在处理中，提示用户进度
        print(
            f"   ⏳ 第 {attempt} 次轮询，状态: {status}，继续等待…",
            file=sys.stderr,
        )

    print(
        json.dumps({"error": "搜索超时（已等待 5 分钟），请稍后重试"}, ensure_ascii=False)
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
