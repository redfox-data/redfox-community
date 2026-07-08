#!/usr/bin/env python3
"""
短视频链接提文案 - API 调用与轮询脚本
用于 短视频链接提文案 技能的自动化数据采集：提交视频链接 → 轮询等待 → 获取文案结果
"""

import os
import sys
import time
import json
import requests

# ============================================================
# 配置
# ============================================================

# 技能来源标识（所有接口调用必须携带）
SOURCE = "短视频链接提文案-GitHub"

# API 基础地址
BASE_URL = "https://redfox.hk/story/api"

# 接口路径
SUBMIT_URL = f"{BASE_URL}/parseWork/audioTextExtract/submit"
RESULT_URL = f"{BASE_URL}/parseWork/audioTextExtract/result"

# 轮询配置
POLL_INTERVAL = 4          # 轮询间隔（秒）
MAX_POLL_COUNT = 60        # 最大轮询次数（约 4 分钟）
PROGRESS_REPORT_EVERY = 5  # 每 N 次轮询输出一次进度

# ============================================================
# 鉴权
# ============================================================

API_KEY = os.environ.get("REDFOX_API_KEY")
if not API_KEY:
    print("错误：未配置 API Key。请设置环境变量 REDFOX_API_KEY")
    print("获取 API Key：https://redfox.hk/settings/api-keys?source=github")
    sys.exit(1)

HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY,
}

# ============================================================
# 状态常量
# ============================================================

STATUS_SUCCEEDED = "succeeded"
STATUS_FAILED = "failed"
PENDING_STATUSES = {"queued", "running", "uploading", "asr_processing"}

# 提交失败 - 错误信息 → 用户提示映射
SUBMIT_ERROR_MAP = {
    "视频链接不能为空": "请提供视频链接",
    "视频链接解析失败": "链接解析失败，请确认是抖音/快手/小红书的有效视频链接",
    "未获取到视频地址，可能为图文类型作品": "该链接是图文内容，没有视频可提取",
    "视频时长超过10分钟限制": "视频超过 10 分钟限制，请先裁剪后再试",
    "不支持的平台": "暂不支持该平台，目前仅支持抖音、快手、小红书",
    "视频上传任务提交失败": "视频上传失败，请稍后重试",
    "系统繁忙，请稍后重试": "当前使用人数较多，请稍后重试",
}

# 查询失败 - 错误信息 → 用户提示映射
RESULT_ERROR_MAP = {
    "任务ID不能为空": "系统内部错误，请重新提交视频链接",
    "任务不存在": "任务已过期或不存在，请重新提交视频链接",
    "无权查询该任务": "鉴权失败，请检查 API Key 是否正确",
}


# ============================================================
# 工具函数
# ============================================================

def format_timestamp(ms: int, total_duration_ms: int) -> str:
    """将毫秒时间戳转为 **分**秒 或 **时**分**秒 格式"""
    total_seconds = round(ms / 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if total_duration_ms >= 3600000:  # 总时长 ≥ 1 小时
        return f"**{hours}**时**{minutes}**分**{seconds}**秒"
    else:
        return f"**{minutes}**分**{seconds}**秒"


def format_duration(ms: int) -> str:
    """将毫秒转为 **分**秒 或 **时**分**秒 格式"""
    total_seconds = round(ms / 1000)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if ms >= 3600000:
        return f"**{hours}**时**{minutes}**分**{seconds}**秒"
    else:
        return f"**{minutes}**分**{seconds}**秒"


# ============================================================
# 核心流程
# ============================================================

def submit_task(video_url: str) -> str:
    """
    提交文案提取任务
    返回 taskId
    """
    payload = {
        "url": video_url,
        "source": SOURCE,
    }

    try:
        resp = requests.post(SUBMIT_URL, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"提交失败：网络连接异常 - {e}")
        sys.exit(1)

    data = resp.json()

    if data.get("code") not in (200, 2000):
        msg = data.get("msg", "未知错误")
        user_msg = SUBMIT_ERROR_MAP.get(msg, msg)
        print(f"提交失败：{user_msg}")
        sys.exit(1)

    task_id = data.get("data", {}).get("taskId")
    if not task_id:
        print("提交失败：未获取到任务标识")
        sys.exit(1)

    return task_id


def poll_result(task_id: str) -> dict:
    """
    轮询查询提取结果
    返回完整的 data 对象
    """
    payload = {
        "taskId": task_id,
        "source": SOURCE,
    }

    for i in range(1, MAX_POLL_COUNT + 1):
        time.sleep(POLL_INTERVAL)

        try:
            resp = requests.post(RESULT_URL, headers=HEADERS, json=payload, timeout=30)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"查询失败：网络连接异常 - {e}")
            sys.exit(1)

        data = resp.json()

        if data.get("code") not in (200, 2000):
            msg = data.get("msg", "未知错误")
            user_msg = RESULT_ERROR_MAP.get(msg, msg)
            print(f"查询失败：{user_msg}")
            sys.exit(1)

        result = data.get("data", {})
        status = result.get("status", "")

        # 成功
        if status == STATUS_SUCCEEDED:
            return result

        # 失败
        if status == STATUS_FAILED:
            fail_reason = result.get("failReason", "未知原因")
            print(f"提取失败：{fail_reason}")
            return result

        # 处理中 - 输出进度
        if i % PROGRESS_REPORT_EVERY == 0:
            elapsed = i * POLL_INTERVAL
            print(f"正在识别语音内容，请稍候…（已等待约 {elapsed} 秒）")

    # 轮询超时
    print(f"视频处理时间较长，请稍后使用任务标识 {task_id} 重新查询")
    return {"status": "timeout", "taskId": task_id}


def extract_text(video_url: str) -> dict:
    """
    完整提取流程：提交 → 轮询 → 返回结果
    """
    print(f"已提交文案提取任务，正在处理中…")

    # Step 1: 提交任务
    task_id = submit_task(video_url)

    # Step 2: 轮询结果
    result = poll_result(task_id)

    # Step 3: 格式化返回
    if result.get("status") == STATUS_SUCCEEDED:
        text = result.get("text", "")
        stamp_sents = result.get("stampSents", [])

        print(f"\n✅ 提取完成！共识别 {len(stamp_sents)} 句话")

        if stamp_sents:
            total_duration = stamp_sents[-1].get("end", 0)
            print(f"总时长 {format_duration(total_duration)}")

        return {
            "success": True,
            "text": text,
            "stamp_sents": [
                {
                    "text": s.get("textSeg", ""),
                    "start": s.get("start", 0),
                    "end": s.get("end", 0),
                    "start_fmt": format_timestamp(s.get("start", 0), total_duration),
                    "end_fmt": format_timestamp(s.get("end", 0), total_duration),
                }
                for s in stamp_sents
            ],
        }
    else:
        return {
            "success": False,
            "status": result.get("status", "unknown"),
            "reason": result.get("failReason", ""),
            "taskId": result.get("taskId", task_id),
        }


def batch_extract(urls: list) -> list:
    """
    批量提取多个视频链接的文案
    返回每个链接的结果列表
    """
    results = []
    total = len(urls)

    for idx, url in enumerate(urls, 1):
        print(f"\n--- 处理第 {idx}/{total} 个链接 ---")
        result = extract_text(url.strip())
        result["url"] = url
        results.append(result)

    # 汇总
    success_count = sum(1 for r in results if r.get("success"))
    print(f"\n--- 批量提取完成：成功 {success_count}/{total}，失败 {total - success_count}/{total} ---")

    return results


# ============================================================
# 命令行入口
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("用法：")
        print("  单链接：python fetch_audio_text.py <视频链接>")
        print("  多链接：python fetch_audio_text.py <链接1> <链接2> ...")
        print()
        print("示例：")
        print('  python fetch_audio_text.py "https://v.douyin.com/xxxxxx/"')
        sys.exit(1)

    urls = sys.argv[1:]

    if len(urls) == 1:
        result = extract_text(urls[0])
        if result.get("success"):
            print("\n完整文案：")
            print(result["text"])
            print("\n每句详情展示：")
            for i, s in enumerate(result["stamp_sents"], 1):
                print(f"  {i}. [{s['start_fmt']} - {s['end_fmt']}] {s['text']}")
    else:
        batch_extract(urls)


if __name__ == "__main__":
    main()
