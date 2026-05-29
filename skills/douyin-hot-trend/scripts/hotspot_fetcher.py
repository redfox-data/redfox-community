#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音热榜数据获取脚本

功能：调用红狐数据热榜API获取抖音实时热点数据
接口：https://redfox.hk/story/api/hotSpot/getListByPlatform
参数：platform=2, source=抖音热榜-GitHub, startDate, endDate（可选）
方法：GET
认证：X-API-KEY（三级回退：环境变量 → shell配置文件 → 提示用户配置）
"""

import json
import os
import sys
import re
from datetime import datetime, timedelta

import requests


def get_api_key():
    """
    获取 REDFOX_API_KEY，按三级优先级回退：
    1. 从当前设备环境变量 REDFOX_API_KEY 获取
    2. 从 shell 配置文件（~/.bashrc / ~/.bash_profile / ~/.zshrc）中读取
    3. 提示用户配置

    Returns:
        str: API Key 字符串

    Raises:
        SystemExit: 未能获取到有效的 API Key
    """
    # 第一级：从环境变量获取
    api_key = os.getenv("REDFOX_API_KEY")
    if api_key and api_key.strip():
        return api_key.strip()

    # 第二级：从 shell 配置文件读取
    home = os.path.expanduser("~")
    shell_configs = [
        os.path.join(home, ".bashrc"),
        os.path.join(home, ".bash_profile"),
        os.path.join(home, ".zshrc"),
    ]
    for config_path in shell_configs:
        if os.path.isfile(config_path):
            try:
                with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                match = re.search(
                    r'export\s+REDFOX_API_KEY\s*=\s*["\']?([a-zA-Z0-9_]+)["\']?',
                    content
                )
                if match:
                    api_key = match.group(1).strip()
                    if api_key:
                        return api_key
            except Exception:
                continue

    # 第三级：提示用户配置
    error_msg = {
        "error": "缺少 REDFOX_API_KEY 配置",
        "hint": "请设置环境变量 REDFOX_API_KEY=ak_xxxxxxxx，或将其写入 shell 配置文件（~/.bashrc / ~/.bash_profile / ~/.zshrc）",
        "guide": "访问 https://redfox.hk/login 注册账号，在个人中心获取 API Key"
    }
    print(json.dumps(error_msg, ensure_ascii=False))
    sys.exit(1)


def fetch_douyin_hotspot(start_date=None, end_date=None, days=None):
    """
    获取抖音热榜数据

    使用原生 requests 发起请求，X-API-KEY 通过三级回退获取

    Args:
        start_date: 开始日期，格式 YYYY-MM-DD
        end_date: 结束日期，格式 YYYY-MM-DD
        days: 查询天数，如7表示近7天，30表示近30天

    Returns:
        None (结果直接打印到标准输出)
    """
    # 获取 API Key（三级回退）
    credential = get_api_key()

    # 构建请求URL
    url = "https://redfox.hk/story/api/hotSpot/getListByPlatform"

    # 构建请求参数
    params = {
        "platform": 2,
        "source": "抖音热榜-GitHub"
    }

    # 处理日期参数
    query_type = "实时"

    if days:
        today = datetime.now().date()
        end_date_obj = today
        start_date_obj = today - timedelta(days=days)
        params["startDate"] = start_date_obj.strftime("%Y-%m-%d")
        params["endDate"] = end_date_obj.strftime("%Y-%m-%d")
        query_type = f"近{days}天"

    if start_date and end_date:
        params["startDate"] = start_date
        params["endDate"] = end_date
        query_type = f"{start_date} 至 {end_date}"

    # 构建请求头
    headers = {
        "X-API-KEY": credential,
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)

        if response.status_code >= 400:
            raise Exception(f"HTTP请求失败: {response.status_code}, {response.text}")

        api_response = response.json()

        # 处理不同的响应格式
        if isinstance(api_response, dict):
            if "data" in api_response:
                data = api_response["data"]
            elif "list" in api_response:
                data = api_response["list"]
            else:
                data = []
        elif isinstance(api_response, list):
            data = api_response
        else:
            data = []

        # 提取并格式化热榜数据
        if isinstance(data, list):
            now = datetime.now()
            fetch_time = now.strftime("%Y-%m-%d %H:00")

            result = {
                "fetch_time": fetch_time,
                "query_type": query_type,
                "start_date": start_date,
                "end_date": end_date,
                "hot_list": []
            }
            for item in data:
                # 处理标题：去除所有空格（半角空格、全角空格、制表符、换行符等）
                title = item.get("title", "")
                if title:
                    title = ''.join(title.split())
                result["hot_list"].append({
                    "index": item.get("index"),
                    "title": title,
                    "hotCount": item.get("hotCount", ""),
                    "url": item.get("url", "")
                })
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(json.dumps([], ensure_ascii=False))

    except requests.exceptions.RequestException as e:
        error_msg = {"error": f"请求失败: {str(e)}"}
        print(json.dumps(error_msg, ensure_ascii=False))
        sys.exit(1)
    except Exception as e:
        error_msg = {"error": f"错误: {str(e)}"}
        print(json.dumps(error_msg, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='获取抖音热榜数据')
    parser.add_argument('--start-date', type=str, help='开始日期，格式 YYYY-MM-DD')
    parser.add_argument('--end-date', type=str, help='结束日期，格式 YYYY-MM-DD')
    parser.add_argument('--days', type=int, help='查询天数，如7表示近7天，30表示近30天')

    args = parser.parse_args()

    fetch_douyin_hotspot(
        start_date=args.start_date,
        end_date=args.end_date,
        days=args.days
    )
