#!/usr/bin/env python3
"""
HTML报告生成脚本
从structured_report.json读取智能体已分析好的结构化热点数据，填充HTML模板生成报告

【核心原则】
本脚本只负责模板渲染，不进行任何数据分析或事件识别：
- 不识别热点事件（由智能体完成）
- 不计算热度值（由智能体完成）
- 不生成趋势预测（由智能体完成）
- 只读取JSON数据，填充模板，输出HTML

这确保HTML报告与对话输出完全一致，因为数据来源相同。
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, List


def get_platform_class(platform_name: str) -> str:
    """获取平台对应的CSS类名"""
    platform_map = {
        "微博": "weibo",
        "抖音": "douyin",
        "知乎": "zhihu",
        "B站": "bilibili",
        "快手": "kuaishou",
        "头条": "toutiao",
        "百度": "baidu"
    }
    return platform_map.get(platform_name, "weibo")


def get_platform_emoji(platform_name: str) -> str:
    """获取平台对应的emoji"""
    emoji_map = {
        "微博": "🌐",
        "抖音": "🎵",
        "知乎": "📚",
        "B站": "📺",
        "快手": "🎬",
        "头条": "📰",
        "百度": "🔍"
    }
    return emoji_map.get(platform_name, "📍")


def get_hot_score_value(hot_score_str: str) -> int:
    """将热度字符串（如'938万'）转换为数值"""
    try:
        return int(hot_score_str.replace("万", "")) * 10000
    except (ValueError, AttributeError):
        return 0


def get_rank_header_class(rank: int, hot_score_str: str) -> str:
    """根据排名和热度获取卡片头部样式类名"""
    hot_score = get_hot_score_value(hot_score_str)
    if rank == 1:
        return "rank-1-header"
    elif rank == 2:
        return "rank-2-header"
    elif rank == 3:
        return "rank-3-header"
    elif hot_score >= 10000000:
        return "rank-hot"
    elif hot_score >= 5000000:
        return "rank-medium"
    else:
        return "rank-normal"


def get_rank_badge_class(rank: int) -> str:
    """获取排名徽章样式类名"""
    if rank == 1:
        return "rank-1"
    elif rank == 2:
        return "rank-2"
    elif rank == 3:
        return "rank-3"
    else:
        return "rank-other"


def generate_table_row(hotspot: Dict, rank: int) -> str:
    """生成TOP10表格行HTML"""
    return f'''                    <tr>
                        <td><span class="rank-badge {get_rank_badge_class(rank)}">{rank}</span></td>
                        <td><strong>{hotspot["title"]}</strong></td>
                        <td><span class="hot-score">{hotspot["hot_score"]}</span></td>
                        <td><span class="platform-count">{hotspot["platform_count"]}个</span></td>
                        <td><span class="duration">{hotspot["duration"]}</span></td>
                    </tr>'''


def generate_hotspot_card(hotspot: Dict, rank: int) -> str:
    """生成热点卡片HTML"""
    platforms = hotspot.get("platforms", [])
    discussions = hotspot.get("discussions", [])
    prediction = hotspot.get("prediction", "")
    prediction_emoji = hotspot.get("prediction_emoji", "🔥")

    # 生成平台标签
    platform_tags = ""
    for plat in platforms:
        plat_class = get_platform_class(plat)
        platform_tags += f'''                            <span class="platform-tag platform-{plat_class}">{plat}</span>\n'''

    # 构建discussions的平台索引，用于快速查找
    disc_map = {d["platform"]: d for d in discussions}

    # 生成讨论差异：必须覆盖platforms中所有在榜平台
    discussion_items = ""
    for plat in platforms:
        plat_class = get_platform_class(plat)
        if plat in disc_map:
            # 该平台有讨论数据，使用原始数据
            disc = disc_map[plat]
            focus = disc.get("focus", "")
            topics = disc.get("topics", [])

            # 构建话题链接
            topic_links = []
            for t in topics[:3]:
                title = t.get("title", "")
                url = t.get("url", "")
                if url:
                    topic_links.append(f'<a href="{url}" target="_blank">{title}</a>')
                else:
                    topic_links.append(title)
            topics_str = "、".join([f"「{t}」" for t in topic_links])

            discussion_items += f'''                        <div class="discussion-item {plat_class}">
                            <div class="discussion-platform">{get_platform_emoji(plat)} {plat}</div>
                            <div class="discussion-content">{focus}，如{topics_str}</div>
                        </div>\n'''
        else:
            # 该平台在榜但discussions中缺失，兜底补全
            discussion_items += f'''                        <div class="discussion-item {plat_class}">
                            <div class="discussion-platform">{get_platform_emoji(plat)} {plat}</div>
                            <div class="discussion-content">{plat}用户关注该事件</div>
                        </div>\n'''

    return f'''            <div class="hotspot-card">
                <div class="card-header {get_rank_header_class(rank, hotspot['hot_score'])}">
                    <span class="card-rank">{rank}</span>
                    <h3 class="card-title">{hotspot["title"]}</h3>
                    <div class="card-stats">
                        <div class="stat-item">热度：{hotspot["hot_score"]}</div>
                        <div class="stat-item">上榜平台：{hotspot["platform_count"]}个</div>
                        <div class="stat-item">持续时长：{hotspot["duration"]}</div>
                        <div class="stat-item">最高排名：TOP{hotspot["max_position"]}</div>
                    </div>
                </div>
                <div class="card-body">
                    <div class="platform-section">
                        <div class="platform-title">上榜平台</div>
                        <div class="platform-list">
{platform_tags}                        </div>
                    </div>
                    <div class="discussion-section">
                        <div class="discussion-title">跨平台讨论差异</div>
{discussion_items}                    </div>
                    <div class="prediction-section">
                        <div class="prediction-title">{prediction_emoji} 综合预测</div>
                        <div class="prediction-content">{prediction}</div>
                    </div>
                </div>
            </div>'''


def generate_html_report(data: Dict, template_path: str) -> str:
    """生成完整的HTML报告"""
    # 读取模板
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # 获取数据
    query_range = data.get("query_range", {})
    start_date = query_range.get("start_date", "")
    end_date = query_range.get("end_date", "")
    hotspots = data.get("hotspots", [])

    if not hotspots:
        return "<html><body><h1>无热点数据</h1></body></html>"

    # 生成TOP10表格内容
    table_rows = ""
    for i, hotspot in enumerate(hotspots[:10], 1):
        table_rows += generate_table_row(hotspot, i) + "\n"

    # 生成热点卡片
    cards = ""
    for i, hotspot in enumerate(hotspots[:10], 1):
        cards += generate_hotspot_card(hotspot, i) + "\n"

    # 替换模板中的占位符
    html = template.replace("{start_date}", start_date)
    html = html.replace("{end_date}", end_date)

    # 替换表格tbody
    html = html.replace(
        '''                <tbody>
                    <!-- TOP10数据填充示例：''',
        f'''                <tbody>\n{table_rows}                    <!-- '''
    )

    # 替换热点卡片区域
    html = html.replace(
        '''        <!-- 热点详情卡片 -->
        <div class="hotspot-cards">
            <!-- 热点卡片填充示例：''',
        f'''        <!-- 热点详情卡片 -->\n        <div class="hotspot-cards">\n{cards}            <!-- '''
    )

    return html


def validate_report_data(data: Dict) -> List[str]:
    """校验结构化报告数据的完整性，返回错误列表（致命错误阻断，缺失平台仅警告不阻断）"""
    errors = []
    if "query_range" not in data:
        errors.append("缺少 query_range 字段")
    if "hotspots" not in data:
        errors.append("缺少 hotspots 字段")
    else:
        hotspots = data["hotspots"]
        if len(hotspots) < 1:
            errors.append("hotspots 为空")
        for i, h in enumerate(hotspots[:10]):
            rank = i + 1
            required = ["title", "hot_score", "platform_count", "duration", "platforms", "discussions", "prediction", "prediction_emoji"]
            for field in required:
                if field not in h:
                    errors.append(f"第{rank}个热点缺少 {field} 字段")
            # 校验：discussions中的平台必须在platforms列表中（致命错误）
            if "discussions" in h and "platforms" in h:
                disc_platforms = [d["platform"] for d in h["discussions"]]
                for dp in disc_platforms:
                    if dp not in h["platforms"]:
                        errors.append(f"第{rank}个热点的讨论差异中包含未上榜平台: {dp}")
    return errors


def main():
    parser = argparse.ArgumentParser(description='生成HTML热点报告')
    parser.add_argument('--input', type=str, required=True,
                        help='结构化报告JSON文件路径（structured_report.json）')
    parser.add_argument('--output', type=str, default=None,
                        help='输出HTML文件路径，默认为热点榜报告_日期.html')

    args = parser.parse_args()

    # 从文件读取JSON数据
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(json.dumps({
            "status": "error",
            "message": f"JSON解析失败: {str(e)}",
            "output_path": None
        }, ensure_ascii=False))
        return
    except FileNotFoundError:
        print(json.dumps({
            "status": "error",
            "message": f"文件不存在: {args.input}",
            "output_path": None
        }, ensure_ascii=False))
        return
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": f"读取输入数据失败: {str(e)}",
            "output_path": None
        }, ensure_ascii=False))
        return

    # 校验数据
    errors = validate_report_data(data)
    if errors:
        print(json.dumps({
            "status": "error",
            "message": "报告数据校验失败: " + "; ".join(errors),
            "output_path": None
        }, ensure_ascii=False))
        return

    # 获取模板路径（脚本同目录下）
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "..", "assets", "report-template.html")

    # 生成HTML
    html = generate_html_report(data, template_path)

    # 确定输出路径
    if args.output:
        output_path = args.output
    else:
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_path = f"热点榜报告_{date_str}.html"

    # 写入文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(json.dumps({
        "status": "success",
        "output_path": output_path,
        "message": f"HTML报告已生成：{output_path}"
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
