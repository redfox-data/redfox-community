#!/usr/bin/env python3
"""
视频号视频下载 - API 调用脚本
输入视频号分享链接，解析出真实下载地址
"""

import os
import sys
import json
import requests

# 修复 Windows 控制台 GBK 输出问题
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ============================================================
# 配置
# ============================================================

API_URL = "https://redfox.hk/story/api/parseWork/videoDownload/sph"
REQUEST_TIMEOUT = 30

ERROR_MAP = {
    "视频链接不能为空": "请提供视频号链接",
    "视频链接解析失败": "链接解析失败，请确认是有效的视频号分享链接",
    "不支持的平台": "请提供视频号链接（weixin.qq.com/sph/...）",
    "未获取到视频地址": "未能解析到视频地址，请确认链接是视频类型",
    "系统繁忙，请稍后重试": "当前使用人数较多，请稍后重试",
}

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
# 核心函数
# ============================================================


def parse_video_download(video_url: str) -> dict:
    payload = {"url": video_url, "source": "视频号视频下载-GitHub"}

    try:
        resp = requests.post(API_URL, headers=HEADERS, json=payload, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        return {"success": False, "reason": "请求超时，请稍后重试"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "reason": "网络连接异常，请检查网络后重试"}
    except requests.RequestException as e:
        return {"success": False, "reason": f"请求失败：{e}"}

    if resp.status_code != 200:
        return {"success": False, "reason": f"HTTP 错误：{resp.status_code}"}

    if not resp.text.strip():
        return {"success": False, "reason": "接口返回空内容，请稍后重试"}

    try:
        data = resp.json()
    except json.JSONDecodeError:
        return {"success": False, "reason": "接口返回非 JSON 内容（可能触发限流），请稍后重试"}

    code = data.get("code")
    if code not in (200, 2000):
        msg = data.get("msg", "未知错误")
        user_msg = ERROR_MAP.get(msg, msg)
        return {"success": False, "reason": user_msg}

    result = data.get("data", {})
    title = result.get("title", "") or result.get("desc", "")
    cover = result.get("cover", "")
    video_url_result = result.get("videoUrl", "")

    # fallback: 从 resources 数组取 downloadUrl
    if not video_url_result:
        resources = result.get("resources", [])
        if resources and isinstance(resources, list):
            video_url_result = resources[0].get("downloadUrl", "")

    if not video_url_result:
        return {"success": False, "reason": "未获取到视频下载地址"}

    return {"success": True, "title": title, "cover": cover, "videoUrl": video_url_result}


def batch_parse(urls: list) -> list:
    results = []
    total = len(urls)
    for idx, url in enumerate(urls, 1):
        result = parse_video_download(url.strip())
        result["input_url"] = url.strip()
        result["index"] = idx
        results.append(result)
    return results


# ============================================================
# 命令行入口
# ============================================================


def main():
    if len(sys.argv) < 2:
        print("用法：python parse_video_download.py <视频号链接>")
        print("示例：python parse_video_download.py \"https://weixin.qq.com/sph/xxxxxx\"")
        sys.exit(1)

    urls = sys.argv[1:]
    results = batch_parse(urls)

    # 输出 JSON 供 Agent 格式化
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
