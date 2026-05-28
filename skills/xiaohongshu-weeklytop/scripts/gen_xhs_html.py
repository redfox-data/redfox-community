#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书七日爆款笔记HTML生成器

从已获取的JSON数据文件读取数据，生成可独立打开的HTML页面。
用法：python gen_xhs_html.py --data_file <JSON数据文件> --category "分类名" --top N [--output PATH]
输出：小红书七日爆款笔记_{分类}_{时间戳}.html（与脚本同目录）

样式特性：
- 小红书风格（红色主题 #ff2442）
- 卡片式布局，多行展示
- 标题和作者在第一行，数据在第二行
- TOP3 奖牌徽章 + 左边框高亮
- 导出 PDF 功能
- 页面最大宽度 750px
"""

import json
import sys
import os
from datetime import datetime


def clean_text(text: str) -> str:
    """
    清理文本中的特殊字符，用于表格单元格显示

    清理内容：
    - 空格
    - 换行符（\r, \n）
    - URL链接
    - Image标记
    - 特殊字符（<>{}[]|\）
    """
    import re
    if not text:
        return ""

    text = str(text)
    # 移除URL
    text = re.sub(r'https?://\S+', '', text)
    # 移除Image标记
    text = re.sub(r'Image:\s*\[.*?\]', '', text)
    # 移除换行符
    text = re.sub(r'[\r\n]+', '', text)
    # 移除空格
    text = text.replace(' ', '')
    # 移除特殊字符
    text = re.sub(r'[<>{}[\]\\|]', '', text)

    return text.strip()


def load_data_from_file(data_file: str) -> list:
    """
    从JSON数据文件加载笔记数据

    支持两种格式：
    1. {"hot_list": [...]} - xhs_weekly_fetcher.py 输出格式
    2. [...] - 纯列表格式

    Args:
        data_file: JSON数据文件路径

    Returns:
        笔记数据列表
    """
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # 尝试从常见字段提取
        for key in ['hot_list', 'data', 'list', 'articles']:
            if key in data and isinstance(data[key], list):
                return data[key]
        # 如果都没有，返回空
        return []

    return []


def generate_html(hot_list: list, category: str = "综合全部", top_n: int = 20) -> str:
    """生成HTML页面 - 小红书风格

    Args:
        hot_list: 笔记数据列表
        category: 分类名称
        top_n: 显示条数，默认20

    重要：只传递实际需要展示的数据到HTML，确保统计数据与展示数据一致
    """
    fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 限制显示条数 - 必须先截取，确保统计数据准确
    top_n = min(top_n, len(hot_list), 50)  # 最大支持TOP50
    hot_list = hot_list[:top_n]

    js_data = json.dumps(hot_list, ensure_ascii=False, indent=2)

    page_title = f"小红书七日爆款笔记 - {category}"

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
            background: #f5f5f5;
            color: #333;
            line-height: 1.5;
        }}

        .page-wrap {{
            max-width: 700px;
            margin: 0 auto;
            padding: 12px 12px 24px;
        }}

        .export-bar {{
            position: sticky;
            top: 0;
            z-index: 100;
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            padding: 8px 0 10px;
        }}
        .btn-export-pdf, .btn-export-img {{
            background: #fff;
            color: #ff2442;
            border: 1.5px solid #ff2442;
            border-radius: 20px;
            padding: 6px 18px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .btn-export-pdf:hover, .btn-export-img:hover {{ background: #fff5f6; }}

        .pdf-content {{ background: transparent; }}

        .header-wrap {{
            background: linear-gradient(135deg, #ff2442 0%, #ff6b81 100%);
            border-radius: 12px;
            padding: 20px 16px;
            margin-bottom: 12px;
            color: #fff;
        }}
        .header-wrap h1 {{
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 4px;
        }}
        .header-meta {{
            font-size: 13px;
            opacity: 0.9;
        }}
        .category-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.25);
            border-radius: 10px;
            padding: 2px 10px;
            font-size: 13px;
            margin-left: 8px;
        }}

        .stats-row {{
            display: flex;
            justify-content: space-around;
            margin-top: 14px;
            padding-top: 14px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-num {{
            font-size: 20px;
            font-weight: 700;
        }}
        .stat-label {{
            font-size: 12px;
            opacity: 0.85;
            margin-top: 2px;
        }}

        .note-list {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}

        .note-card {{
            background: #fff;
            border-radius: 12px;
            padding: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
            border: 1px solid #f0f0f0;
        }}
        .note-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }}
        .note-card.top1 {{ border-left: 3px solid #ff2442; }}
        .note-card.top2 {{ border-left: 3px solid #ff6b81; }}
        .note-card.top3 {{ border-left: 3px solid #ffb3c1; }}

        .note-row1 {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 10px;
        }}
        .rank-num {{
            min-width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 700;
            color: #999;
            margin-right: 12px;
            flex-shrink: 0;
        }}

        .note-info {{
            flex: 1;
            min-width: 0;
        }}
        .note-title {{
            font-size: 16px;
            font-weight: 600;
            color: #333;
            line-height: 1.4;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
            margin-bottom: 8px;
        }}
        .note-title a {{
            color: #333;
            text-decoration: none;
        }}
        .note-title a:hover {{
            color: #ff2442;
        }}
        .author-info {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            color: #999;
        }}
        .author-avatar {{
            width: 22px;
            height: 22px;
            border-radius: 50%;
            object-fit: cover;
        }}
        .author-name {{
            color: #666;
        }}
        .fans-count {{
            color: #999;
        }}

        .note-row2 {{
            display: flex;
            flex-wrap: wrap;
            gap: 14px;
            padding-left: 48px;
            /* 48px = rank-num宽度36px + margin-right 12px，与头像边界对齐 */
        }}
        .data-item {{
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 13px;
        }}
        .data-label {{
            color: #999;
        }}
        .data-value {{
            color: #333;
            font-weight: 600;
        }}
        .data-add {{
            color: #ff2442;
            font-size: 12px;
            margin-left: 4px;
        }}

        .footer-note {{
            text-align: center;
            font-size: 12px;
            color: #bbb;
            margin-top: 16px;
            padding: 10px 0;
        }}

        @media (max-width: 600px) {{
            .page-wrap {{ padding: 8px 8px 20px; }}
            .header-wrap {{ padding: 16px 12px; }}
            .header-wrap h1 {{ font-size: 20px; }}
            .note-card {{ padding: 12px; }}
            .note-title {{ font-size: 15px; }}
            .rank-num {{ min-width: 32px; height: 32px; font-size: 16px; }}
            .note-row2 {{ gap: 10px; padding-left: 44px; margin-top: 8px; }}
            .data-item {{ font-size: 12px; }}
        }}
    </style>
</head>
<body>

<div class="page-wrap">
    <div class="export-bar">
        <button class="btn-export-img" onclick="exportImage()">导出图片</button>
        <button class="btn-export-pdf" onclick="exportPdf()">导出 PDF</button>
    </div>

    <div class="pdf-content" id="pdfContent">
        <div class="header-wrap">
            <h1>📱 小红书七日爆款笔记<span class="category-badge">{category}</span></h1>
            <div class="header-meta">更新时间：{fetch_time}</div>
            <div class="stats-row">
                <div class="stat-item">
                    <div class="stat-num" id="totalCount">--</div>
                    <div class="stat-label">笔记总数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-num" id="maxInteractive">--</div>
                    <div class="stat-label">最高互动</div>
                </div>
                <div class="stat-item">
                    <div class="stat-num" id="avgInteractive">--</div>
                    <div class="stat-label">平均互动</div>
                </div>
            </div>
        </div>

        <div class="note-list" id="noteList"></div>

        <div class="footer-note">数据来源：小红书平台 · {category} · 七日爆款笔记排行</div>
    </div>
</div>

<script>
(function() {{
    function bindCardClick() {{
        var cards = document.querySelectorAll('.note-card[data-href]');
        cards.forEach(function(card) {{
            card.addEventListener('click', function(e) {{
                if (e.target.closest('a, button')) return;
                var url = this.getAttribute('data-href');
                if (url && url !== '#') window.open(url, '_blank');
            }});
        }});
    }}
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', bindCardClick);
    }} else {{
        bindCardClick();
    }}
}})();

(function() {{
    var RAW = {js_data};

    var totalCount = RAW.length;
    var maxInteractive = 0, sumInteractive = 0;

    function parseInteractive(val) {{
        if (typeof val === 'string') {{
            if (val.indexOf('w') !== -1 || val.indexOf('W') !== -1) {{
                return parseFloat(val) * 10000;
            }} else if (val.indexOf('亿') !== -1) {{
                return parseFloat(val) * 100000000;
            }}
            return parseFloat(val) || 0;
        }}
        return val || 0;
    }}

    function fmtNum(val) {{
        if (typeof val === 'string') {{
            if (val.indexOf('w') !== -1 || val.indexOf('W') !== -1 || val.indexOf('亿') !== -1) {{
                return val;
            }}
        }}
        var n = parseInt(val) || 0;
        if (n >= 10000) {{
            return (n / 10000).toFixed(1) + 'w';
        }}
        return n.toString();
    }}

    for (var i = 0; i < RAW.length; i++) {{
        var interactive = parseInteractive(RAW[i].interactiveCount);
        if (interactive > maxInteractive) maxInteractive = interactive;
        sumInteractive += interactive;
    }}
    var avgInteractive = totalCount > 0 ? sumInteractive / totalCount : 0;

    document.getElementById('totalCount').textContent = totalCount;
    document.getElementById('maxInteractive').textContent = fmtNum(maxInteractive);
    document.getElementById('avgInteractive').textContent = fmtNum(Math.round(avgInteractive));

    var html = '';
    for (var i = 0; i < RAW.length && i < {top_n}; i++) {{
        var d = RAW[i];
        var rank = i + 1;
        var cardCls = 'note-card';

        if (rank === 1) cardCls += ' top1';
        else if (rank === 2) cardCls += ' top2';
        else if (rank === 3) cardCls += ' top3';

        var noteUrl = (d.photoJumpUrl || '#').replace(/ /g, '%20');
        var avatar = d.userHeadUrl || '';
        var userName = (d.userName || '--').replace(/ /g, '');
        var fans = (d.fans || '').replace(/ /g, '');
        var title = (d.title || '--').replace(/ /g, '');

        var interactive = (d.interactiveCount || '0').replace(/ /g, '');
        var addInteractive = (d.addInteractiveount || '0').replace(/ /g, '');
        var likeCount = (d.useLikeCount || '0').replace(/ /g, '');
        var addLikeCount = (d.addLikeCount || '0').replace(/ /g, '');
        var commentCount = (d.useCommentCount || '0').replace(/ /g, '');
        var addCommentCount = (d.addCommentCount || '0').replace(/ /g, '');
        var collected = (d.collectedCount || '0').replace(/ /g, '');
        var addCollected = (d.addCollectedCunt || '0').replace(/ /g, '');
        var shareCount = (d.useShareCount || '0').replace(/ /g, '');
        var addShareCount = (d.addShareCount || '0').replace(/ /g, '');

        var rankHtml = '';
        if (rank === 1) {{
            rankHtml = '<div class="rank-num">🥇</div>';
        }} else if (rank === 2) {{
            rankHtml = '<div class="rank-num">🥈</div>';
        }} else if (rank === 3) {{
            rankHtml = '<div class="rank-num">🥉</div>';
        }} else {{
            rankHtml = '<div class="rank-num">' + rank + '</div>';
        }}

        html += '<div class="' + cardCls + '" data-href="' + noteUrl + '">'
            + '<div class="note-row1">'
            + rankHtml
            + '<div class="note-info">'
            + '<div class="note-title"><a href="' + noteUrl + '" target="_blank" onclick="event.stopPropagation()">' + title + '</a></div>'
            + '<div class="author-info">'
            + (avatar ? '<img class="author-avatar" src="' + avatar + '" onerror="this.style.display=\\'none\\'">' : '')
            + '<span class="author-name">' + userName + '</span>'
            + (fans ? '<span class="fans-count">·' + fans + '粉丝</span>' : '')
            + '</div>'
            + '</div>'
            + '</div>'
            + '<div class="note-row2">'
            + '<div class="data-item"><span class="data-label">互动</span><span class="data-value">' + fmtNum(interactive) + '</span><span class="data-add">↑' + fmtNum(addInteractive) + '</span></div>'
            + '<div class="data-item"><span class="data-label">点赞</span><span class="data-value">' + fmtNum(likeCount) + '</span><span class="data-add">↑' + fmtNum(addLikeCount) + '</span></div>'
            + '<div class="data-item"><span class="data-label">评论</span><span class="data-value">' + fmtNum(commentCount) + '</span><span class="data-add">↑' + fmtNum(addCommentCount) + '</span></div>'
            + '<div class="data-item"><span class="data-label">收藏</span><span class="data-value">' + fmtNum(collected) + '</span><span class="data-add">↑' + fmtNum(addCollected) + '</span></div>'
            + '<div class="data-item"><span class="data-label">分享</span><span class="data-value">' + fmtNum(shareCount) + '</span><span class="data-add">↑' + fmtNum(addShareCount) + '</span></div>'
            + '</div>'
            + '</div>';
    }}

    document.getElementById('noteList').innerHTML = html;
}})();

function exportImage() {{
    var btn = document.querySelector('.btn-export-img');
    btn.textContent = '生成中...';
    btn.style.pointerEvents = 'none';

    var target = document.getElementById('pdfContent');

    html2canvas(target, {{
        scale: 2,
        useCORS: true,
        backgroundColor: '#f5f5f5',
        logging: false,
        windowWidth: target.scrollWidth,
        windowHeight: target.scrollHeight
    }}).then(function(canvas) {{
        var link = document.createElement('a');
        link.download = '小红书七日爆款笔记_' + new Date().toISOString().slice(0,10) + '.png';
        link.href = canvas.toDataURL('image/png');
        link.click();

        btn.textContent = '导出图片';
        btn.style.pointerEvents = '';
    }}).catch(function(err) {{
        alert('图片生成失败：' + err.message);
        btn.textContent = '导出图片';
        btn.style.pointerEvents = '';
    }});
}}

function exportPdf() {{
    var btn = document.querySelector('.btn-export-pdf');
    btn.textContent = '生成中...';
    btn.style.pointerEvents = 'none';

    var target = document.getElementById('pdfContent');

    html2canvas(target, {{
        scale: 2,
        useCORS: true,
        backgroundColor: '#f5f5f5',
        logging: false,
        windowWidth: target.scrollWidth,
        windowHeight: target.scrollHeight
    }}).then(function(canvas) {{
        var imgData = canvas.toDataURL('image/png', 1.0);

        // 使用横向 A4 纸
        var pdf = new jspdf.jsPDF('l', 'mm', 'a4');
        var pdfW = pdf.internal.pageSize.getWidth();
        var pdfH = pdf.internal.pageSize.getHeight();
        var margin = 8;
        var contentW = pdfW - margin * 2;
        var contentH = pdfH - margin * 2;

        // 计算图片尺寸以适应横向 A4
        var imgW = contentW;
        var imgH = (canvas.height * imgW) / canvas.width;

        // 如果高度仍然超过页面高度，按高度缩放
        if (imgH > contentH) {{
            imgH = contentH;
            imgW = (canvas.width * imgH) / canvas.height;
        }}

        // 居中显示
        var imgX = (pdfW - imgW) / 2;
        var imgY = (pdfH - imgH) / 2;

        // 所有内容在一页中
        pdf.addImage(imgData, 'PNG', imgX, imgY, imgW, imgH);

        var now = new Date();
        var dateStr = now.getFullYear() +
            String(now.getMonth()+1).padStart(2,'0') +
            String(now.getDate()).padStart(2,'0') +
            '_' +
            String(now.getHours()).padStart(2,'0') +
            String(now.getMinutes()).padStart(2,'0');

        pdf.save('小红书七日爆款笔记_' + dateStr + '.pdf');

        btn.textContent = '导出 PDF';
        btn.style.pointerEvents = '';
    }}).catch(function(err) {{
        alert('PDF 生成失败：' + err.message);
        btn.textContent = '导出 PDF';
        btn.style.pointerEvents = '';
    }});
}}
</script>

</body>
</html>'''

    # Replace js_data placeholder
    html = html.replace("{js_data}", js_data)

    return html


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='生成小红书七日爆款笔记HTML页面')
    parser.add_argument('--data_file', type=str, required=True, help='已获取的JSON数据文件路径')
    parser.add_argument('--category', type=str, default='综合全部', help='分类名称')
    parser.add_argument('--keyword', type=str, help='用户输入的关键词（仅用于兼容，不影响数据读取）')
    parser.add_argument('--output', type=str, help='输出文件路径')
    parser.add_argument('--top', type=int, default=20, help='显示条数，默认20，可设为50')

    args = parser.parse_args()

    # 检查数据文件是否存在
    if not os.path.isfile(args.data_file):
        print(f"错误：数据文件不存在 - {args.data_file}", file=sys.stderr)
        sys.exit(1)

    # 从JSON文件加载数据（不再调用API）
    print(f"从数据文件加载数据: {args.data_file}", file=sys.stderr)
    hot_list = load_data_from_file(args.data_file)

    if not hot_list:
        print("错误：数据文件为空或格式不正确", file=sys.stderr)
        sys.exit(1)

    category = args.category

    print(f"分类：{category}", file=sys.stderr)
    print(f"共加载 {len(hot_list)} 条数据，展示TOP{args.top}", file=sys.stderr)

    # 生成HTML
    html = generate_html(hot_list, category=category, top_n=args.top)

    # 确定输出路径
    if args.output:
        output_path = args.output
    else:
        # 生成唯一时间戳文件名
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_category = category.replace("/", "_").replace("\\", "_")
        filename = f"小红书七日爆款笔记_{safe_category}_{timestamp}.html"
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"已生成：{output_path}", file=sys.stderr)
    print(f"共 {len(hot_list)} 条数据，展示TOP{args.top}", file=sys.stderr)
