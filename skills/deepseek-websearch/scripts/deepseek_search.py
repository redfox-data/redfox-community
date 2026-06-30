#!/usr/bin/env python3
"""
Deepseek WebSearch — 提交搜索查询并轮询结果

用法:
    python3 deepseek_search.py "<搜索关键词>"

环境变量:
    REDFOX_API_KEY — 红狐 API Key（必填）
"""

import os
import sys
import json
import time

import requests

# Windows 控制台 UTF-8 编码修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

API_BASE = "https://redfox.hk/story/api/deepSearch"
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

    headers = {
        "REDFOX_API_KEY": API_KEY,
        "Content-Type": "application/json",
    }

    # ── Step 1: 提交搜索 ──────────────────────────────────────────────
    try:
        submit_resp = requests.post(
            f"{API_BASE}/dsSubmit",
            json={"inquiryText": query},
            headers=headers,
            timeout=30,
        )
        submit_resp.raise_for_status()
        submit_data = submit_resp.json()
    except requests.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else None
        if status_code == 502:
            print(
                json.dumps(
                    {
                        "error": (
                            "服务返回 502 错误，可能存在网络不稳定问题，"
                            "请稍后重试"
                        )
                    },
                    ensure_ascii=False,
                )
            )
        else:
            print(
                json.dumps(
                    {"error": f"提交搜索请求失败 (HTTP {status_code}): {e}"},
                    ensure_ascii=False,
                )
            )
        sys.exit(1)
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
        f"⏳ 已提交搜索请求 (taskId: {task_id})，正在等待 Deepseek WebSearch 返回结果…",
        file=sys.stderr,
    )

    # ── Step 2: 轮询结果 ──────────────────────────────────────────────
    for attempt in range(1, MAX_ATTEMPTS + 1):
        time.sleep(POLL_INTERVAL)

        try:
            result_resp = requests.post(
                f"{API_BASE}/dsResult",
                json={"taskId": task_id},
                headers=headers,
                timeout=30,
            )
            result_resp.raise_for_status()
            result_data = result_resp.json()
        except requests.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else None
            if status_code == 502:
                print(
                    f"⚠️ 第 {attempt} 次轮询遇到 502 错误（网络不稳定），继续重试…",
                    file=sys.stderr,
                )
            else:
                print(
                    f"⚠️ 第 {attempt} 次查询结果失败 (HTTP {status_code}): {e}，继续重试…",
                    file=sys.stderr,
                )
            continue
        except requests.RequestException as e:
            print(
                f"⚠️ 第 {attempt} 次查询结果失败: {e}，继续重试…",
                file=sys.stderr,
            )
            continue

        status = result_data.get("data", {}).get("status", "")

        if status in ("succeeded", "completed"):
            # 成功：输出最终结果到 stdout
            print(json.dumps(result_data, ensure_ascii=False))
            return

        if status == "failed":
            fail_reason = result_data.get("data", {}).get("failReason", "")
            print(
                json.dumps(
                    {"error": f"搜索任务失败: {fail_reason or result_data}"},
                    ensure_ascii=False,
                )
            )
            sys.exit(1)

        # 仍在处理中，提示用户进度 (queued / running)
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
