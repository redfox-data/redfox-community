#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
热点数据获取脚本
从热点接口获取各平台热点数据，支持时间范围查询和关键词筛选
"""

import argparse
import json
import os
import ssl
import sys
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import tempfile

# 平台代码映射：平台代码 -> 平台名称
PLATFORM_MAP = {
    "wb": "微博",
    "dy": "抖音",
    "bz": "B站",
    "ks": "快手",
    "zh": "知乎",
    "tt": "头条",
    "bd": "百度"
}

# 平台代码到接口枚举值的映射
PLATFORM_CODE_MAP = {
    "ks": 1,   # 快手
    "dy": 2,   # 抖音
    "wb": 5,   # 微博
    "bd": 7,   # 百度
    "bz": 8,   # B站
    "zh": 9,   # 知乎
    "tt": 10   # 头条
}

# 关键词泛化映射：大词 -> 泛化词列表
KEYWORD_EXPANSION_MAP = {
    "体育": ["体育", "足球", "篮球", "运动", "健身", "奥运", "世界杯", "NBA", "CBA", "乒乓球"],
    "娱乐": ["娱乐", "明星", "电影", "电视剧", "综艺", "音乐", "八卦"],
    "科技": ["科技", "互联网", "手机", "电脑", "AI", "人工智能", "数码"],
    "财经": ["财经", "股市", "基金", "理财", "经济", "金融"],
    "社会": ["社会", "民生", "新闻", "热点", "事件"],
    "游戏": ["游戏", "电竞", "网游", "手游", "王者荣耀", "英雄联盟"],
    "汽车": ["汽车", "车", "新能源", "电动车", "特斯拉", "比亚迪"],
    "美食": ["美食", "吃", "餐厅", "菜谱", "做饭"],
    "旅游": ["旅游", "旅行", "景点", "攻略", "酒店"],
    "时尚": ["时尚", "穿搭", "美妆", "护肤", "衣服"]
}


def expand_keywords(keyword: str) -> List[str]:
    """
    对关键词进行泛化扩展

    Args:
        keyword: 用户输入的关键词

    Returns:
        扩展后的关键词列表
    """
    # 首先检查是否为大词（优先匹配）
    for big_word, expanded_words in KEYWORD_EXPANSION_MAP.items():
        if keyword == big_word or big_word in keyword:
            return expanded_words

    # 精确词不扩展（长度<=2或包含特定字符）
    if len(keyword) <= 2 or any(char in keyword for char in ["超", "联赛", "杯"]):
        return [keyword]

    # 默认不扩展
    return [keyword]


def format_hot_count(hot_count: str) -> str:
    """
    智能格式化热度值

    Args:
        hot_count: 原始热度值

    Returns:
        格式化后的热度值
    """
    if not hot_count:
        return "0"

    # 如果已经包含单位（万、亿），直接返回
    if "万" in hot_count or "亿" in hot_count:
        return hot_count

    # 尝试转换为数字
    try:
        num = int(hot_count)
        # 转换为"数字+万"格式
        wan = num // 10000
        if wan > 0:
            return f"{wan}万"
        else:
            return str(num)
    except ValueError:
        # 无法转换为数字，直接返回原值
        return hot_count


def _get_api_key() -> str:
    """从当前环境变量获取 REDFOX_API_KEY"""
    key = os.environ.get("REDFOX_API_KEY")
    if not key:
        raise SystemExit("❌ 未找到 REDFOX_API_KEY，请配置环境变量：export REDFOX_API_KEY=<你的apikey>")
    return key


def fetch_hotspot_data(
    source: str,
    platforms: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict:
    """
    从接口获取热点数据

    Args:
        source: 数据来源
        platforms: 平台代码列表（可选）
        keywords: 关键词列表（可选）
        start_date: 开始时间（可选）
        end_date: 结束时间（可选）

    Returns:
        API返回的数据字典
    """
    # API配置
    api_url = "https://redfox.hk/story/api/hotSpot/getListByPlatformWithKeyword"

    # 构建请求参数
    params = {
        "source": source
    }

    # 添加平台参数（数组）- 始终传入，即使为空数组
    platform_enums = []
    if platforms:
        for p in platforms:
            if p in PLATFORM_CODE_MAP:
                platform_enums.append(PLATFORM_CODE_MAP[p])
            else:
                print(f"警告: 不支持的平台代码 {p}", file=sys.stderr)
    params["platforms"] = platform_enums

    # 添加关键词参数（数组）- 始终传入，即使为空数组
    params["keywords"] = keywords if keywords else []

    # 添加时间参数
    if start_date:
        params["startDate"] = start_date
    if end_date:
        params["endDate"] = end_date

    # 获取 API Key
    api_key = _get_api_key()

    try:
        # 发送请求（使用 urllib，跳过 SSL 验证）
        body = json.dumps(params).encode("utf-8")
        req = urllib.request.Request(
            api_url,
            data=body,
            headers={
                "Content-Type": "application/json",
                "X-API-KEY": api_key
            },
            method="POST"
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            if resp.status != 200:
                return {
                    "status": "error",
                    "message": f"HTTP请求失败: {resp.status}",
                    "data": None
                }
            raw = resp.read()

        # 解析响应
        result = json.loads(raw.decode("utf-8"))

        # 接口返回code=2000表示成功
        if result.get("code") == 2000:
            return {
                "status": "success",
                "message": "数据获取成功",
                "data": result.get("data", {})
            }
        else:
            # 接口返回错误码
            error_msg = result.get("msg") or result.get("message") or "接口返回错误"
            return {
                "status": "error",
                "message": f"接口错误: {error_msg} (code: {result.get('code')})",
                "data": None
            }

    except Exception as e:
        err_msg = str(e)
        if "timed out" in err_msg.lower():
            return {"status": "error", "message": "请求超时", "data": None}
        if "urlopen" in err_msg.lower() or "connection" in err_msg.lower():
            return {"status": "error", "message": f"连接失败: {err_msg}", "data": None}
        return {"status": "error", "message": f"请求异常: {err_msg}", "data": None}


def process_hotspot_data(data: Dict, platform_filter: Optional[List[str]] = None) -> Dict:
    """
    处理热点数据

    Args:
        data: API返回的原始数据
        platform_filter: 平台筛选列表

    Returns:
        处理后的数据
    """
    result = {
        "total": 0,
        "platforms": {}
    }

    # 平台列表映射
    platform_list_map = {
        "bdList": "bd",
        "bzList": "bz",
        "dyList": "dy",
        "ksList": "ks",
        "ttList": "tt",
        "wbList": "wb",
        "zhList": "zh"
    }

    for list_key, platform_code in platform_list_map.items():
        # 如果指定了平台筛选，跳过不在筛选列表中的平台
        if platform_filter and platform_code not in platform_filter:
            continue

        hotspots = data.get(list_key, [])
        if hotspots:
            processed_hotspots = []
            for hotspot in hotspots:
                processed = {
                    "title": hotspot.get("title", ""),
                    "url": hotspot.get("url", ""),
                    "hotCount": format_hot_count(hotspot.get("hotCount", "0")),
                    "index": hotspot.get("index", 0),
                    "gmtCreate": hotspot.get("gmtCreate", ""),
                    "platCode": platform_code,
                    "platName": PLATFORM_MAP.get(platform_code, platform_code)
                }
                processed_hotspots.append(processed)

            result["platforms"][platform_code] = {
                "name": PLATFORM_MAP.get(platform_code, platform_code),
                "count": len(processed_hotspots),
                "hotspots": processed_hotspots
            }
            result["total"] += len(processed_hotspots)

    return result


def output_compact(result: Dict) -> str:
    """
    输出极简格式（避免数据被截断）
    末尾附带完整数据文件路径，避免重复调用接口
    """
    output_lines = []

    # 元信息
    output_lines.append(f"status: {result['status']}")
    output_lines.append(f"total: {result['total']}")
    output_lines.append(f"platforms: {len(result['platforms'])}")
    output_lines.append("")

    # 各平台概览（TOP3）
    for platform_code, platform_data in result["platforms"].items():
        output_lines.append(f"[{platform_data['name']}] {platform_data['count']}条")
        for hotspot in platform_data["hotspots"][:3]:
            output_lines.append(f"  {hotspot['index']}. {hotspot['title']} - {hotspot['hotCount']}")
        output_lines.append("")

    # 附带完整数据文件路径（一次调用搞定，禁止二次调用浪费token）
    if "dataFile" in result:
        output_lines.append(f"dataFile: {result['dataFile']}")

    return "\n".join(output_lines)


def output_json(result: Dict) -> str:
    """
    输出JSON格式
    """
    return json.dumps(result, ensure_ascii=False, indent=2)


def output_markdown(result: Dict) -> str:
    """
    输出Markdown表格格式（只输出TOP10）
    """
    output_lines = []

    for platform_code, platform_data in result["platforms"].items():
        output_lines.append(f"## {platform_data['name']}")
        output_lines.append("")
        output_lines.append("|排名|标题|热度|")
        output_lines.append("|---|---|---|")

        for hotspot in platform_data["hotspots"][:10]:
            title = hotspot["title"]
            url = hotspot["url"]
            hot_count = hotspot["hotCount"]
            index = hotspot["index"]

            # Markdown超链接格式
            title_link = f"[{title}]({url})" if url else title
            output_lines.append(f"|{index}|{title_link}|{hot_count}|")

        output_lines.append("")

    return "\n".join(output_lines)


def main():
    parser = argparse.ArgumentParser(description="获取各平台热点数据")

    parser.add_argument(
        "--source",
        default="全平台热点事件-GitHub",
        help="数据来源（默认：全平台热点事件）"
    )

    parser.add_argument(
        "--platforms",
        help="平台代码列表，逗号分隔（如：wb,dy,bz）"
    )

    parser.add_argument(
        "--keywords",
        help="关键词列表，逗号分隔（如：体育,足球）"
    )

    parser.add_argument(
        "--expand-keywords",
        action="store_true",
        help="启用关键词泛化扩展"
    )

    parser.add_argument(
        "--start-date",
        help="开始时间（格式：YYYY-MM-DD HH:MM:SS）"
    )

    parser.add_argument(
        "--end-date",
        help="结束时间（格式：YYYY-MM-DD HH:MM:SS）"
    )

    parser.add_argument(
        "--output",
        choices=["compact", "json", "markdown"],
        default="compact",
        help="输出格式（默认：compact）"
    )

    args = parser.parse_args()

    # 解析平台参数
    platforms = None
    if args.platforms:
        platforms = [p.strip() for p in args.platforms.split(",")]

    # 解析关键词参数
    keywords = None
    if args.keywords:
        raw_keywords = [k.strip() for k in args.keywords.split(",")]
        if args.expand_keywords:
            # 对每个关键词进行扩展
            expanded = []
            for k in raw_keywords:
                expanded.extend(expand_keywords(k))
            keywords = list(dict.fromkeys(expanded))  # 去重保持顺序
        else:
            keywords = raw_keywords

    # 计算默认时间范围（前一个完整小时）
    if not args.start_date or not args.end_date:
        now = datetime.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        start_time = current_hour - timedelta(hours=1)
        end_time = current_hour

        if not args.start_date:
            args.start_date = start_time.strftime("%Y-%m-%d %H:%M:%S")
        if not args.end_date:
            args.end_date = end_time.strftime("%Y-%m-%d %H:%M:%S")

    # 获取数据
    api_result = fetch_hotspot_data(
        source=args.source,
        platforms=platforms,
        keywords=keywords,
        start_date=args.start_date,
        end_date=args.end_date
    )

    if api_result["status"] == "error":
        print(json.dumps(api_result, ensure_ascii=False))
        sys.exit(1)

    # 处理数据
    result = process_hotspot_data(api_result["data"], platforms)

    # 添加元信息
    result["status"] = "success"
    result["source"] = args.source
    result["startDate"] = args.start_date
    result["endDate"] = args.end_date
    if keywords:
        result["keywords"] = keywords

    # 保存完整数据到临时文件
    temp_file = tempfile.mktemp(prefix="platforms-hotspot-data-", suffix=".json")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    result["dataFile"] = temp_file

    # 输出结果
    if args.output == "compact":
        print(output_compact(result))
    elif args.output == "json":
        print(output_json(result))
    elif args.output == "markdown":
        print(output_markdown(result))


if __name__ == "__main__":
    main()
