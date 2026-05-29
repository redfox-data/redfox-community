#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音热榜HTML生成器

从JSON文件读取热榜数据，生成可独立打开的HTML页面。
用法：
  python gen_douyin_hot_html.py --json-file data.json --output output.html
  python gen_douyin_hot_html.py --json-file data.json --output output.html --top 50

数据来源优先级：
  1. --json-file 参数：从指定JSON文件读取（推荐，避免重复API调用）
  2. --start-date / --end-date / --days 参数：自行调用API获取（兼容旧用法）

样式特性：
- 紫色系极简风格（#6c5ce7 / #a29bfe）
- 卡片式表格（border-collapse: separate，每行独立圆角白卡）
- TOP3 奖牌徽章 + 对应色竖线边框
- 4+ 序号深灰小字
- 热度值纯紫色 #6c5ce7
- 整行点击跳转（location.href，兼容 file:// 协议）
- 导出 PDF 功能（仅截取内容区，不含按钮栏，单页 A4 自适应缩放）
- 页面最大宽度 750px
"""

import json
import sys
import os
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
    raise ValueError(
        "缺少 REDFOX_API_KEY 配置。"
        "请设置环境变量 REDFOX_API_KEY=ak_xxxxxxxx，"
        "或将其写入 shell 配置文件（~/.bashrc / ~/.bash_profile / ~/.zshrc）。"
        "访问 https://redfox.hk/login 注册账号，在个人中心获取 API Key。"
    )


def fetch_douyin_hotspot(start_date=None, end_date=None, days=None):
    """获取抖音热榜数据 - 使用原生 requests，API Key 三级回退"""
    # 获取 API Key（三级回退）
    credential = get_api_key()

    # 构建请求URL和参数
    url = "https://redfox.hk/story/api/hotSpot/getListByPlatform"
    params = {
        "platform": 2,
        "source": "抖音热榜-GitHub"
    }

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

    response = requests.get(url, params=params, headers=headers, timeout=30)

    if response.status_code >= 400:
        raise Exception(f"HTTP请求失败: {response.status_code}, {response.text}")

    api_response = response.json()

    if isinstance(api_response, dict):
        data = api_response.get("data", api_response.get("list", []))
    elif isinstance(api_response, list):
        data = api_response
    else:
        data = []

    # 处理数据：去除标题中的所有空格（半角空格、全角空格、制表符、换行符等）
    for item in data:
        if 'title' in item and item['title']:
            item['title'] = ''.join(item['title'].split())
        if 'word' in item and item['word']:
            item['word'] = ''.join(item['word'].split())

    return {
        "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "query_type": query_type,
        "hot_list": data
    }


def generate_desc(title, hot_count):
    """根据标题和热度值生成核心内容摘要（30-80字）"""
    import re

    desc = title
    hot_str = f"热度{hot_count}"

    # 核心内容生成规则 - 基于标题关键词匹配
    if any(k in title for k in ['春天', '春日', '花开', '樱花', '踏青']):
        return f"春季相关话题持续升温，用户分享春日生活美好瞬间与旅行记录，展现春日美景与生活方式，引发大量互动讨论，当前{hot_str}"
    elif any(k in title for k in ['裙摆', '穿搭', '时尚', '美妆', '妆容', '造型']):
        return f"时尚穿搭类话题火爆，博主分享穿搭技巧与造型灵感，年轻用户积极参与模仿创作，带动相关话题持续走高，当前{hot_str}"
    elif any(k in title for k in ['海洋', '科技', '技术', '突破', '创新', '研发']):
        return f"硬核科技/工业成就引发全民关注，展现中国技术实力与发展成果，网友纷纷点赞转发表达民族自豪感，当前{hot_str}"
    elif any(k in title for k in ['骑马', '公主', '古装', '汉服', 'cosplay']):
        return f"古风/角色扮演类内容走红，创作者通过特色造型吸引关注，用户参与度高，评论区互动热烈，当前{hot_str}"
    elif any(k in title for k in ['对镜', '自拍', '拍照', '镜头', '摄影']):
        return f"摄影/自拍技巧类内容广受欢迎，创作者分享实用拍摄方法，帮助普通用户提升出片质量，传播度极高，当前{hot_str}"
    elif any(k in title for k in ['出游', '旅行', '旅游', '景点', '打卡']):
        return f"旅游出行话题热度攀升，各地景点迎来游客高峰，用户分享旅行攻略与见闻，激发更多人规划行程，当前{hot_str}"
    elif any(k in title for k in ['赖清德', '弹劾', '政治', '政策', '政府', '官员']):
        return f"时政类重大事件引发全网热议，各平台讨论量激增，用户密切关注事态发展，相关分析解读视频获得高播放，当前{hot_str}"
    elif any(k in title for k in ['房价', '楼市', '房贷', '购房', '经济', 'GDP', '股市', 'A股']):
        return f"财经/民生话题牵动大众神经，专业机构与个人投资者高度关注市场动态，各类解读分析内容刷屏，当前{hot_str}"
    elif any(k in title for k in ['电影', '剧集', '开播', '定档', '综艺', '选秀', '歌手']):
        return f"影视娱乐类话题霸榜，新作品/节目上线引发追剧热潮，明星动态与剧情讨论占据热搜前列，当前{hot_str}"
    elif any(k in title for k in ['游戏', '电竞', '比赛', '战队', '选手']):
        return f"游戏/电竞赛事话题火热，职业赛事精彩操作被广泛传播，玩家社区讨论氛围活跃，相关二创内容爆发式增长，当前{hot_str}"
    elif any(k in title for k in ['美食', '做饭', '食谱', '奶茶', '探店', '餐厅']):
        return f"美食类内容持续吸睛，创作者推荐美食做法与探店体验，激发用户尝试欲望与打卡热情，评论区求教程留言众多，当前{hot_str}"
    elif any(k in title for k in ['萌宠', '猫咪', '狗狗', '动物', '可爱']):
        return f"宠物/动物类治愈系内容广受喜爱，萌宠日常视频轻松获取百万播放，用户在评论区晒出自家毛孩子照片，互动率极高，当前{hot_str}"
    elif any(k in title for k in ['健身', '减肥', '运动', '瑜伽', '瘦身']):
        return f"健康运动话题受关注度提升，健身达人分享训练计划与饮食建议，激励大批用户开启锻炼模式，跟练打卡成风潮，当前{hot_str}"
    elif any(k in title for k in ['教育', '高考', '考研', '学校', '老师', '家长']):
        return f"教育相关话题引发家长群体强烈共鸣，升学政策与学习方法的讨论热度居高不下，干货分享型内容获大量收藏，当前{hot_str}"
    elif any(k in title for k in ['恋爱', '感情', '婚姻', '分手', '相亲']):
        return f"情感婚恋话题触动年轻人共鸣，真实故事分享与情感分析视频引发深度讨论，用户在评论区倾诉经历寻求建议，当前{hot_str}"
    elif any(k in title for k in ['职场', '工资', '面试', '辞职', '老板', '打工']):
        return f"职场话题直击打工人痛点，薪资待遇、工作体验等议题引发广泛共鸣，职场经验分享内容获高收藏转发，当前{hot_str}"
    else:
        # 兜底：基于标题长度智能扩展
        return f"该话题在抖音平台引发广泛关注与讨论，大量创作者围绕此主题产出优质内容，用户互动活跃，相关视频播放量持续增长，当前{hot_str}"


def generate_html(result, top_n=20):
    """生成HTML页面 - 紫色极简风格

    Args:
        result: 热榜数据结果
        top_n: 显示条数，默认20，可设为50

    重要：只传递实际需要展示的数据到HTML，确保统计数据与展示数据一致
    """
    hot_list = result["hot_list"]
    fetch_time = result["fetch_time"]
    query_type = result["query_type"]

    # 限制显示条数 - 必须先截取，确保统计数据准确
    top_n = min(top_n, 50)  # 最大支持TOP50
    # ⚠️ 关键：只保留实际需要展示的数据，确保HTML中统计数据与展示数据一致
    hot_list = hot_list[:top_n]

    def fmt_hot_value(n):
        """格式化热度值 - 保持与表格显示一致"""
        n = int(n or 0)
        if n >= 100000000:
            return f"{n / 100000000:.1f}亿"
        if n >= 10000:
            # 保留一位小数，如 1109.6w
            return f"{n / 10000:.1f}w"
        return str(n)

    # 为每条数据生成核心内容摘要和格式化热度值
    for item in hot_list:
        # 生成核心内容摘要
        if not item.get('desc') and not item.get('excerpt'):
            title = item.get('title', '') or item.get('word', '')
            hot_count = item.get('hotCount', '') or item.get('hotValue', '0')
            item['_genDesc'] = generate_desc(title, fmt_hot_value(hot_count))

        # 格式化热度值，确保HTML显示与智能体表格一致
        hot_count = item.get('hotCount', '') or item.get('hotValue', '0')
        item['_fmtHeat'] = fmt_hot_value(hot_count)

    js_data = json.dumps(hot_list, ensure_ascii=False, indent=2)

    if query_type == "实时":
        page_title = "抖音实时热榜"
    else:
        page_title = f"抖音热榜（{query_type}）"

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'PingFang SC', sans-serif;
            background: #f0f0f5;
            color: #333;
            line-height: 1.6;
        }}

        /* ===== 页面容器 - 最大宽度750px ===== */
        .page-wrap {{
            max-width: 750px;
            margin: 0 auto;
            padding: 16px 16px 32px;
        }}

        /* ===== 导出按钮栏 - 不参与PDF导出 ===== */
        .export-bar {{
            position: sticky;
            top: 0;
            z-index: 100;
            display: flex;
            justify-content: flex-end;
            padding: 10px 0 12px;
            margin-bottom: 4px;
        }}
        .btn-export-pdf {{
            background: #fff;
            color: #6c5ce7;
            border: 1.5px solid #6c5ce7;
            border-radius: 20px;
            padding: 7px 22px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .btn-export-pdf:hover {{ background: #f8f6ff; transform: translateY(-1px); }}
        .btn-export-pdf:active {{ transform: translateY(0); }}

        /* ===== PDF内容区域 ===== */
        .pdf-content {{ background: transparent; }}

        /* ===== 头部卡片 - 紫色渐变 ===== */
        .hot-title-wrap {{
            background: linear-gradient(135deg, #6c5ce7, #a29bfe);
            border-radius: 14px;
            padding: 24px 24px 20px;
            margin-bottom: 18px;
            color: #fff;
            text-align: center;
        }}
        .hot-title-wrap h1 {{
            font-size: 22px; font-weight: 800;
            letter-spacing: 0.5px;
        }}
        .hot-update-time {{
            margin-top: 4px;
            font-size: 12.5px;
            opacity: 0.85;
        }}

        /* 统计卡片区 */
        .stats-row {{
            display: flex;
            justify-content: center;
            gap: 16px;
            margin-top: 16px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.18);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-radius: 11px;
            padding: 11px 20px;
            min-width: 95px;
            text-align: center;
        }}
        .stat-num {{ font-size: 21px; font-weight: 800; }}
        .stat-label {{ font-size: 11.5px; opacity: 0.85; margin-top: 2px; }}

        /* ===== 表格区域 ===== */
        .table-area {{ background: transparent; }}

        /* 卡片式表格 */
        .hot-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0 6px;
        }}
        .hot-table thead {{ display: none; }}

        .hot-table tbody tr {{
            background: #fff;
            border-radius: 10px;
            transition: all 0.2s ease;
            cursor: pointer;
        }}
        .hot-table tbody tr:hover {{
            transform: translateY(-1.5px);
            box-shadow: 0 6px 20px rgba(108,92,231,0.15);
        }}

        .hot-table td {{
            padding: 13px 14px;
            vertical-align: middle;
            border: none;
        }}
        .hot-table tr td:first-child {{ border-radius: 10px 0 0 10px; }}
        .hot-table tr td:last-child {{ border-radius: 0 10px 10px 0; }}

        /* 排名序号 */
        .rank-cell {{ width: 58px; text-align: center; }}

        /* TOP3 奖牌徽章 */
        .rank-badge {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 31px; height: 31px;
            border-radius: 50%;
            font-size: 14px;
            font-weight: 800;
            position: relative;
        }}
        /* TOP1 紫红 */
        .rank-badge.top1 {{
            background: linear-gradient(135deg, #e056a0, #a855f7);
            color: #fff;
            box-shadow: 0 2px 8px rgba(168,85,247,0.35);
        }}
        /* TOP2 蓝紫 */
        .rank-badge.top2 {{
            background: linear-gradient(135deg, #6c5ce7, #74b9ff);
            color: #fff;
            box-shadow: 0 2px 8px rgba(108,92,231,0.30);
        }}
        /* TOP3 浅紫 */
        .rank-badge.top3 {{
            background: linear-gradient(135deg, #a29bfe, #dfe6e9);
            color: #6c5ce7;
            box-shadow: 0 2px 8px rgba(162,155,254,0.35);
        }}
        /* 4+ 序号 */
        .rank-normal {{
            font-size: 13px;
            font-weight: 700;
            color: #555;
        }}

        /* TOP1-3 行左侧色条 + 背景色 */
        .hot-table tbody tr.row-top1 {{ background: linear-gradient(90deg, rgba(168,85,247,0.07), #fff 6%); }}
        .hot-table tbody tr.row-top2 {{ background: linear-gradient(90deg, rgba(108,92,231,0.07), #fff 6%); }}
        .hot-table tbody tr.row-top3 {{ background: linear-gradient(90deg, rgba(162,155,254,0.09), #fff 6%); }}

        .hot-table tbody tr.row-top1 > td:first-child {{ border-left: 3.5px solid #a855f7; }}
        .hot-table tbody tr.row-top2 > td:first-child {{ border-left: 3.5px solid #6c5ce7; }}
        .hot-table tbody tr.row-top3 > td:first-child {{ border-left: 3.5px solid #a29bfe; }}

        /* 标题描述 */
        .info-cell {{}}
        .topic-title-link {{
            text-decoration: none;
            display: block;
        }}
        .topic-title-link:hover .topic-title {{
            color: #6c5ce7;
        }}
        .topic-title {{
            font-size: 14.5px;
            font-weight: 650;
            color: #222;
            line-height: 1.45;
            word-break: break-all;
            transition: color 0.2s ease;
        }}
        .topic-desc {{
            font-size: 12.5px;
            color: #888;
            margin-top: 3px;
            line-height: 1.4;
            word-break: break-all;
        }}

        /* 热度值 - 纯紫色 */
        .heat-cell {{ text-align: right; white-space: nowrap; width: 110px; }}
        .heat-value {{
            font-size: 14px;
            font-weight: 800;
            color: #6c5ce7;
        }}

        /* 标签 */
        .tag {{
            display: inline-block;
            font-size: 11px;
            font-weight: 600;
            padding: 2px 9px;
            border-radius: 10px;
            margin-right: 4px;
            vertical-align: middle;
        }}
        .tag-hot {{ background: rgba(231,76,60,0.08); color: #e74c3c; }}
        .tag-new {{ background: rgba(52,152,219,0.08); color: #3498db; }}
        .tag-hot-rising {{ background: rgba(230,126,34,0.1); color: #e67e22; }}
        .tag-descend {{ background: rgba(149,165,166,0.1); color: #7f8c8d; }}
        .tag-steady {{ background: rgba(39,174,96,0.1); color: #27ae60; }}

        /* 时间标签 */
        .time-tag {{
            font-size: 11.5px;
            color: #999;
            white-space: nowrap;
        }}

        /* 底部说明 */
        .footer-note {{
            text-align: center;
            font-size: 11.5px;
            color: #bbb;
            margin-top: 20px;
            padding: 10px 0;
        }}

        @media (max-width: 480px) {{
            .page-wrap {{ padding: 10px 8px 24px; }}
            .hot-title-wrap {{ padding: 18px 16px 16px; }}
            .stats-row {{ gap: 8px; }}
            .stat-card {{ padding: 8px 14px; min-width: 75px; }}
            .stat-num {{ font-size: 18px; }}
            .hot-table td {{ padding: 10px 10px; }}
            .topic-title {{ font-size: 13.5px; }}
            .heat-value {{ font-size: 15px; }}
        }}
    </style>
</head>
<body>

<div class="page-wrap">
    <!-- 导出按钮（不包含在PDF内） -->
    <div class="export-bar">
        <button class="btn-export-pdf" onclick="exportPdf()">导出 PDF</button>
    </div>

    <!-- PDF内容区域 -->
    <div class="pdf-content" id="pdfContent">

        <!-- 头部 -->
        <div class="hot-title-wrap">
            <h1>🔥 {page_title}</h1>
            <div class="hot-update-time">更新时间：{fetch_time}</div>
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-num" id="totalCount">--</div>
                    <div class="stat-label">话题总数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-num" id="maxHeat">--</div>
                    <div class="stat-label">最高热度</div>
                </div>
                <div class="stat-card">
                    <div class="stat-num" id="avgHeat">--</div>
                    <div class="stat-label">平均热度</div>
                </div>
            </div>
        </div>

        <!-- 表格 -->
        <div class="table-area">
            <table class="hot-table">
                <thead>
                    <tr><th>排名</th><th>话题信息</th><th>热度值</th></tr>
                </thead>
                <tbody id="hotTableBody"></tbody>
            </table>
        </div>

        <div class="footer-note">数据来源：抖音 · 仅供参考</div>
    </div><!-- /pdf-content -->
</div><!-- /page-wrap -->

<script>
// 行点击跳转 - 使用 location.href 避免 file:// 下 window.open 被拦截
(function() {{
    function bindRowClick() {{
        var rows = document.querySelectorAll('.hot-table tbody tr[data-href]');
        rows.forEach(function(row) {{
            row.style.cursor = 'pointer';
            row.addEventListener('click', function(e) {{
                if (e.target.closest('button, a, .btn-export-pdf')) return;
                var url = this.getAttribute('data-href');
                if (url) window.location.href = url;
            }});
        }});
    }}
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', bindRowClick);
    }} else {{
        bindRowClick();
    }}
}})();

// 渲染热榜数据
(function() {{
    var RAW = {js_data};

    // 统计
    var totalCount = RAW.length;
    var maxH = 0, sumH = 0;
    for (var i = 0; i < RAW.length; i++) {{
        var h = parseInt(RAW[i].hotCount || RAW[i].hotValue || 0);
        if (h > maxH) maxH = h;
        sumH += h;
    }}
    var avgH = totalCount > 0 ? sumH / totalCount : 0;

    function fmtHot(n) {{
        n = parseInt(n || 0);
        if (n >= 100000000) return (n / 100000000).toFixed(1) + '亿';
        if (n >= 10000) return (n / 10000).toFixed(1) + 'w';  // 保留一位小数，如 1109.6w
        return n.toString();
    }}

    // 更新统计
    document.getElementById('totalCount').textContent = totalCount;
    document.getElementById('maxHeat').textContent = fmtHot(maxH);
    document.getElementById('avgHeat').textContent = fmtHot(Math.round(avgH));

    // 保持API返回的原始排名顺序（不重新排序）
    // ⚠️ 数据一致性要求：必须使用API返回的原始数据，禁止修改排名、热度、链接
    // RAW.sort(function(a, b) {{ return (a.index || 999) - (b.index || 999); }});

    // 渲染表格 - 显示TOP{top_n}
    // ⚠️ 每条数据的URL必须是API返回的真实链接，禁止伪造或替换
    // ⚠️ 热度值直接使用Python格式化后的值（_fmtHeat），确保与智能体表格一致
    var html = '';
    for (var i = 0; i < RAW.length && i < {top_n}; i++) {{
        var d = RAW[i];
        var rank = i + 1;
        var title = d.title || d.word || '--';
        // 直接使用Python格式化后的热度值，不再使用fmtHot函数
        var heatDisplay = d._fmtHeat || fmtHot(d.hotCount || d.hotValue || 0);
        var desc = d.desc || d.excerpt || d._genDesc || '';
        // 链接必须使用API返回的真实URL
        var url = d.url || d.schemeUrl || '#';

        // TOP3 样式类
        var rowCls = '', badgeHtml = '', tagHtml = '';

        if (rank === 1) {{
            rowCls = 'row-top1';
            badgeHtml = '<span class="rank-badge top1">🥇</span>';
            tagHtml = '<span class="tag tag-new">新</span>';
        }} else if (rank === 2) {{
            rowCls = 'row-top2';
            badgeHtml = '<span class="rank-badge top2">🥈</span>';
            tagHtml = '<span class="tag tag-hot">热</span>';
        }} else if (rank === 3) {{
            rowCls = 'row-top3';
            badgeHtml = '<span class="rank-badge top3">🥉</span>';
            tagHtml = '<span class="tag tag-hot-rising">升</span>';
        }} else {{
            badgeHtml = '<span class="rank-normal">' + rank + '</span>';
        }}

        html += '<tr class="' + rowCls + '" data-href="' + url + '">'
            + '<td class="rank-cell">' + badgeHtml + '</td>'
            + '<td class="info-cell">'
            + '<a class="topic-title-link" href="' + url + '" target="_blank" onclick="event.stopPropagation()"><div class="topic-title">' + title + '</div></a>'
            + '<div class="topic-desc">' + desc + '</div>'
            + '</td><td class="heat-cell">'
            + '<div class="heat-value">' + heatDisplay + '</div>';
        if (tagHtml) {{
            html += '<div style="margin-top:3px">' + tagHtml + '</div>';
        }}
        html += '</td></tr>';
    }}

    document.getElementById('hotTableBody').innerHTML = html;

    // 重新绑定行点击事件（动态插入后）
    var rows = document.querySelectorAll('.hot-table tbody tr[data-href]');
    rows.forEach(function(row) {{
        row.addEventListener('click', function(e) {{
            if (e.target.closest('button, a, .btn-export-pdf')) return;
            var u = this.getAttribute('data-href');
            if (u && u !== '#') window.location.href = u;
        }});
    }});
}})();

// 导出PDF - 只截取 pdfContent 区域，单页自适应A4，支持链接跳转
function exportPdf() {{
    var btn = document.querySelector('.btn-export-pdf');
    btn.textContent = '生成中...';
    btn.style.pointerEvents = 'none';

    var target = document.getElementById('pdfContent');

    // 收集所有链接信息 - 链接必须是API返回的真实URL
    var links = [];
    var rows = document.querySelectorAll('.hot-table tbody tr[data-href]');

    rows.forEach(function(row, idx) {{
        var url = row.getAttribute('data-href');
        if (url && url !== '#') {{
            links.push({{
                url: url,
                top: row.offsetTop,
                height: row.offsetHeight,
                idx: idx
            }});
        }}
    }});

    html2canvas(target, {{
        scale: 2,
        useCORS: true,
        backgroundColor: '#f0f0f5',
        logging: false,
        windowWidth: target.scrollWidth,
        windowHeight: target.scrollHeight
    }}).then(function(canvas) {{
        var imgData = canvas.toDataURL('image/png');

        var pdf = new jspdf.jsPDF('p', 'mm', 'a4');
        var pdfW = pdf.internal.pageSize.getWidth();
        var pdfH = pdf.internal.pageSize.getHeight();
        var margin = 10;
        var contentW = pdfW - margin * 2;
        var contentH = pdfH - margin * 2;

        var imgW = contentW;
        var imgH = (canvas.height * imgW) / canvas.width;

        // 计算缩放比例
        var scaleX = imgW / target.scrollWidth;
        var scaleY = imgH / target.scrollHeight;

        // 计算内容在PDF中的位置
        var imgX, imgY;
        if (imgH > contentH) {{
            imgH = contentH;
            imgW = (canvas.width * imgH) / canvas.height;
            scaleX = imgW / target.scrollWidth;
            scaleY = imgH / target.scrollHeight;
            imgX = (contentW - imgW) / 2 + margin;
            imgY = margin;
        }} else {{
            imgX = margin;
            imgY = margin;
        }}

        // 添加图片
        pdf.addImage(imgData, 'PNG', imgX, imgY, imgW, imgH);

        // 添加可点击链接注解（覆盖整行）
        // 注意：PDF阅读器对链接注解的支持不一，但这是PDF规范的标准方式
        links.forEach(function(link) {{
            // 转换坐标：HTML像素 -> PDF毫米
            var pdfY = imgY + (link.top * scaleY);
            var pdfH = Math.max(link.height * scaleY, 3); // 最小高度3mm确保可点击
            var pdfX = imgX;
            var pdfW = imgW;

            // 使用 link 方法添加链接注解
            // 这是PDF规范的标准方式，大多数现代PDF阅读器支持
            pdf.link(pdfX, pdfY, pdfW, pdfH, {{ url: link.url }});
        }});

        var now = new Date();
        var dateStr = now.getFullYear() +
            String(now.getMonth()+1).padStart(2,'0') +
            String(now.getDate()).padStart(2,'0') +
            '_' +
            String(now.getHours()).padStart(2,'0') +
            String(now.getMinutes()).padStart(2,'0');

        pdf.save('{page_title}_' + dateStr + '.pdf');

        btn.textContent = '导出 PDF';
        btn.style.pointerEvents = '';

        // 提示用户PDF链接功能
        console.log('PDF已生成，包含' + links.length + '个可点击链接');
    }}).catch(function(err) {{
        alert('PDF 生成失败：' + err.message);
        btn.textContent = '导出 PDF';
        btn.style.pointerEvents = '';
    }});
}}
</script>

</body>
</html>'''
    return html


def load_result_from_json(json_path):
    """
    从JSON文件读取热榜数据结果。
    支持两种JSON格式：
    1. 完整结果对象：{"fetch_time": "...", "query_type": "...", "hot_list": [...]}
    2. 纯数组：[{"index": 1, "title": "...", "hotCount": "...", "url": "..."}, ...]
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()

    data = json.loads(content)

    if isinstance(data, list):
        # 纯数组格式：包装成完整结果对象
        return {
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query_type": "实时",
            "hot_list": data
        }
    elif isinstance(data, dict):
        # 完整结果对象：确保有 hot_list
        if "hot_list" not in data:
            # 可能是 {"data": [...]} 或 {"list": [...]} 格式
            hot_list = data.get("data", data.get("list", []))
            return {
                "fetch_time": data.get("fetch_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "query_type": data.get("query_type", "实时"),
                "hot_list": hot_list
            }
        return data
    else:
        raise ValueError(f"不支持的JSON格式: {type(data)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='生成抖音热榜HTML页面')
    parser.add_argument('--json-file', type=str, help='从JSON文件读取热榜数据（优先使用，避免重复API调用）')
    parser.add_argument('--start-date', type=str, help='开始日期，格式 YYYY-MM-DD')
    parser.add_argument('--end-date', type=str, help='结束日期，格式 YYYY-MM-DD')
    parser.add_argument('--days', type=int, help='查询天数')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--top', type=int, default=20, help='显示条数，默认20，可设为50')

    args = parser.parse_args()

    # 数据获取：优先从JSON文件读取，其次通过API获取
    if args.json_file:
        if not os.path.isfile(args.json_file):
            print(f"❌ JSON文件不存在: {args.json_file}", file=sys.stderr)
            sys.exit(1)
        print(f"从JSON文件读取数据: {args.json_file}", file=sys.stderr)
        result = load_result_from_json(args.json_file)
    else:
        print("正在获取抖音热榜数据...", file=sys.stderr)
        result = fetch_douyin_hotspot(
            start_date=args.start_date,
            end_date=args.end_date,
            days=args.days
        )

    html = generate_html(result, top_n=args.top)

    if args.output:
        output_path = args.output
    else:
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "douyin_hot_trend.html")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ 已生成：{output_path}", file=sys.stderr)
    print(f"📊 共 {len(result['hot_list'])} 条热榜数据，展示TOP{args.top}", file=sys.stderr)
