#!/usr/bin/env python3
"""
热点数据获取脚本
从真实API获取热点数据，支持跨平台热点聚合
输出JSON数据供智能体按output-templates.md格式化
"""

import argparse
import json
import os
import re
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# API配置
API_URL = "https://redfox.hk/story/api/hotKeyword/list"


def _get_api_key() -> str:
    """从当前环境变量获取 REDFOX_API_KEY"""
    api_key = os.environ.get("REDFOX_API_KEY")
    if not api_key:
        raise SystemExit("❌ 未找到 REDFOX_API_KEY，请配置环境变量：export REDFOX_API_KEY=<你的apikey>")
    return api_key


def fetch_from_api(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict:
    """
    从API获取热点数据

    Args:
        start_date: 开始时间（包含），格式 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS
        end_date: 结束时间（不包含），格式 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS

    Returns:
        热点数据字典
    """
    # 获取凭证
    api_key = _get_api_key()

    # 构建请求参数，自动补全时分秒
    start_date_param = None
    end_date_param = None

    if start_date:
        if len(start_date) == 10:
            start_date_param = f"{start_date} 00:00:00"
        else:
            start_date_param = start_date
    if end_date:
        if len(end_date) == 10:
            end_date_param = f"{end_date} 00:00:00"
        else:
            end_date_param = end_date

    is_realtime = False
    if not start_date_param and not end_date_param:
        is_realtime = True
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=1)
        start_date_param = one_hour_ago.strftime("%Y-%m-%d %H:00:00")
        end_date_param = now.strftime("%Y-%m-%d %H:00:00")

    try:
        # 构建请求体
        body = {"source": "全平台热搜推荐-GitHub"}
        if start_date_param:
            body["startDate"] = start_date_param
        if end_date_param:
            body["endDate"] = end_date_param

        body_bytes = json.dumps(body, ensure_ascii=False).encode("utf-8")

        # 构建请求
        req = urllib.request.Request(
            API_URL,
            data=body_bytes,
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": api_key
            },
            method="POST"
        )

        # 发送请求
        try:
            response = urllib.request.urlopen(req, timeout=15)
        except urllib.error.HTTPError as e:
            return {
                "status": "error",
                "message": f"HTTP请求失败: 状态码 {e.code}",
                "data": None
            }
        except urllib.error.URLError as e:
            if isinstance(e.reason, TimeoutError) or "timed out" in str(e.reason).lower():
                return {
                    "status": "error",
                    "message": "请求超时",
                    "data": None
                }
            return {
                "status": "error",
                "message": f"网络请求失败: {str(e.reason)}",
                "data": None
            }

        raw_data = json.loads(response.read().decode("utf-8"))

        # 检查返回码
        if raw_data.get("code") != 2000:
            return {
                "status": "error",
                "message": f"API返回错误: {raw_data.get('msg', '未知错误')}",
                "data": None
            }

        return transform_api_data(raw_data, start_date_param, end_date_param, is_realtime)

    except json.JSONDecodeError as e:
        return {
            "status": "error",
            "message": f"JSON解析失败: {str(e)}",
            "data": None
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"数据处理失败: {str(e)}",
            "data": None
        }


def transform_api_data(raw_data: Dict, start_date: Optional[str], end_date: Optional[str], is_realtime: bool = False) -> Dict:
    """
    将API返回的数据转换为output-templates.md所需的格式

    Args:
        raw_data: API返回的原始数据
        start_date: 查询开始时间
        end_date: 查询结束时间
        is_realtime: 是否为实时查询

    Returns:
        转换后的热点数据
    """
    data_list = raw_data.get("data", [])

    # 收集所有热点项（忽略接口的keyword分组）
    all_hotspots = []

    for item in data_list:
        keyword = item.get("keyword", "")
        plats = item.get("plats", [])
        hot_spot_list = item.get("hotSpotList", [])

        for spot in hot_spot_list:
            spot["source_keyword"] = keyword  # 记录来源关键词（供参考）
            # 处理标题中的空格
            if spot.get("title"):
                spot["title"] = spot["title"].replace(" ", "")
            # 处理URL中的空格（影响Markdown链接解析）
            if spot.get("url"):
                spot["url"] = spot["url"].replace(" ", "%20")
            all_hotspots.append(spot)

    # 构建返回数据
    stat_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result = {
        "status": "success",
        "stat_time": stat_time,
        "timestamp": datetime.now().isoformat(),
        "source": "api",
        "total_count": len(all_hotspots),
        "hotspots": all_hotspots
    }

    # 添加查询范围信息
    if is_realtime:
        result["query_range"] = {
            "type": "realtime",
            "start_date": start_date,
            "end_date": end_date
        }
    else:
        result["query_range"] = {
            "type": "historical",
            "start_date": start_date,
            "end_date": end_date
        }

    return result


def main():
    parser = argparse.ArgumentParser(description='获取热点数据')
    parser.add_argument('--output', type=str, default='json',
                        choices=['json', 'markdown'],
                        help='输出格式：json或markdown')
    parser.add_argument('--start-date', type=str, default=None,
                        help='开始时间（包含），格式 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS')
    parser.add_argument('--end-date', type=str, default=None,
                        help='结束时间（不包含），格式 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS')

    args = parser.parse_args()

    result = fetch_from_api(args.start_date, args.end_date)

    if args.output == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 简单的markdown格式输出（仅用于测试）
        if result["status"] == "success":
            query_type = result.get("query_range", {}).get("type", "realtime")
            print(f"# 热点数据获取成功\n")
            print(f"统计时间: {result['stat_time']}\n")
            if query_type == "historical":
                print(f"查询范围: {result['query_range']['start_date']} ~ {result['query_range']['end_date']}\n")
            print(f"热点数量: {result['total_count']}\n")
            for i, spot in enumerate(result['hotspots'][:10], 1):
                print(f"- {i}. {spot['title']} | 平台: {spot['platName']} | 热度: {spot['maxHotScore']}")
        else:
            print(f"# 错误\n{result['message']}")


if __name__ == "__main__":
    main()
