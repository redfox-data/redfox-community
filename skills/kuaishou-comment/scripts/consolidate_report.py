#!/usr/bin/env python3
"""
快手评论分析 - 合并报告生成脚本
将多页评论数据合并生成一份完整的 HTML 报告，
包含所有评论和累计分析。超过 3 页时自动折叠。

用法: echo '<json_array>' | python3 consolidate_report.py "<opusId>" --analysis-json '<json>'
      或: python3 consolidate_report.py "<opusId>" --pages-json '<json_array>' --analysis-json '<json>'
"""

import sys
import os
import json
import argparse
import subprocess
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PATH = os.path.join(SCRIPT_DIR, "..", "assets", "consolidate_report_template.html")


def escape_html(text: str) -> str:
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def build_comment_rows(comments: list) -> str:
    """根据评论列表生成 HTML 表格行"""
    rows = []
    for c in comments:
        is_top = c.get("is_top", False)
        row_class = ' class="top-comment"' if is_top else ""
        pin_badge = '<span class="top-badge">📌 置顶</span>' if is_top else ""

        avatar = c.get("user_avatar", "") or ""
        name = escape_html(c.get("user_name", ""))
        content = escape_html(c.get("content", ""))
        like = c.get("like_count", 0) or 0
        reply = c.get("reply_count", 0) or 0
        time_str = (c.get("create_time", "") or "")[5:16]
        ip = escape_html(c.get("ip_location", ""))

        row = (
            f'<tr{row_class}>'
            f'<td>'
            f'<div class="user-cell">'
            f'<img src="{avatar}" class="user-avatar" alt="" onerror="this.style.display=\'none\'" referrerpolicy="no-referrer">'
            f'<span class="user-name">{name}{pin_badge}</span>'
            f'</div>'
            f'</td>'
            f'<td class="content-cell">{content}</td>'
            f'<td class="num-cell">{like}</td>'
            f'<td class="num-cell">{reply}</td>'
            f'<td class="time-cell">{time_str}</td>'
            f'<td class="ip-cell">{ip}</td>'
            f'</tr>'
        )
        rows.append(row)
    return "\n".join(rows)


def build_page_sections(pages: list, max_visible: int = 3) -> tuple:
    """
    生成页面 HTML 片段和折叠切换按钮。
    pages: [{"page": 1, "total": 31, "comments": [...]}, ...]
    返回 (page_sections_html, collapse_toggle_html)
    """
    visible_count = 0
    visible_sections = []
    collapsed_sections = []

    # 过滤空页
    pages = [p for p in pages if p.get("comments") and len(p["comments"]) > 0]
    total_pages = len(pages)

    for i, p in enumerate(pages):
        page_num = p.get("page", i + 1)
        total = p.get("total", len(p.get("comments", [])))
        comments = p.get("comments", [])

        table_rows = build_comment_rows(comments)

        section_html = (
            f'<div class="page-section">'
            f'<h3>📄 第 {page_num} 页 '
            f'<span class="page-badge">{total} 条</span>'
            f'</h3>'
            f'<div class="table-wrapper">'
            f'<table class="comment-table">'
            f'<thead>'
            f'<tr>'
            f'<th style="width: 160px;">评论人</th>'
            f'<th>评论内容</th>'
            f'<th style="width: 70px; text-align: right;">👍 点赞</th>'
            f'<th style="width: 70px; text-align: right;">💬 回复</th>'
            f'<th style="width: 110px;">时间</th>'
            f'<th style="width: 80px;">IP属地</th>'
            f'</tr>'
            f'</thead>'
            f'<tbody>'
            f'{table_rows}'
            f'</tbody>'
            f'</table>'
            f'</div>'
            f'</div>'
        )

        if total_pages <= max_visible or page_num <= max_visible:
            visible_sections.append(section_html)
        else:
            collapsed_sections.append(section_html)

    sections_html = "\n".join(visible_sections)

    # 折叠区域
    if collapsed_sections:
        hidden_count = sum(
            p.get("total", len(p.get("comments", [])))
            for p in pages[max_visible:]
        )
        toggle_html = (
            f'<div class="collapse-container" id="collapseToggle">'
            f'<p style="color: var(--text-secondary); margin-bottom: 0.6rem; font-size: 0.85rem;">'
            f'⚠️ 评论页数较多，已折叠第 {max_visible + 1}-{total_pages} 页（共 {hidden_count} 条）</p>'
            f'<button class="collapse-toggle" onclick="toggleCollapsed()">'
            f'📂 展开全部评论'
            f'</button>'
            f'</div>'
            f'<div class="collapsed-pages" id="collapsedPages">'
            + "\n".join(collapsed_sections) +
            f'</div>'
        )
    else:
        toggle_html = ""

    return sections_html, toggle_html


def generate_consolidated_report(
    opus_id: str,
    pages: list,
    analysis: dict,
    output_dir: str = None,
) -> str:
    template_path = os.path.normpath(TEMPLATE_PATH)
    if not os.path.exists(template_path):
        print(f"[error] 模板文件不存在: {template_path}", file=sys.stderr)
        sys.exit(1)

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 过滤空页并合并所有评论
    pages = [p for p in pages if p.get("comments") and len(p["comments"]) > 0]
    all_comments = []
    for p in pages:
        all_comments.extend(p.get("comments", []))

    total_pages = len(pages)
    total_comments = len(all_comments)
    total_likes = sum(c.get("like_count", 0) or 0 for c in all_comments)
    now = datetime.now()

    # 生成页面区域
    page_sections, collapse_toggle = build_page_sections(pages)

    replacements = {
        "{{OPUS_ID}}": escape_html(opus_id),
        "{{DATE}}": now.strftime("%Y-%m-%d"),
        "{{TOTAL_COMMENTS}}": str(total_comments),
        "{{TOTAL_LIKES}}": str(total_likes),
        "{{TOTAL_PAGES}}": str(total_pages),
        "{{TIMESTAMP}}": now.strftime("%Y-%m-%d %H:%M:%S"),
        "{{PAGE_SECTIONS}}": page_sections,
        "{{COLLAPSE_TOGGLE}}": collapse_toggle,
        "{{POSITIVE_RATIO}}": str(analysis.get("positive_ratio", "--")),
        "{{NEGATIVE_RATIO}}": str(analysis.get("negative_ratio", "--")),
        "{{DEMAND_RATIO}}": str(analysis.get("demand_ratio", "--")),
        "{{COMPETITOR_RATIO}}": str(analysis.get("competitor_ratio", "--")),
        "{{SUMMARY_POSITIVE}}": analysis.get("positive_summary", ""),
        "{{SUMMARY_NEGATIVE}}": analysis.get("negative_summary", ""),
        "{{SUMMARY_DEMAND}}": analysis.get("demand_summary", ""),
        "{{SUMMARY_COMPETITOR}}": analysis.get("competitor_summary", ""),
    }

    for key, val in replacements.items():
        html = html.replace(key, val)

    # 添加 JavaScript 折叠逻辑
    collapse_js = """
<script>
function toggleCollapsed() {
    var collapsed = document.getElementById('collapsedPages');
    var btn = document.getElementById('collapseToggle').querySelector('.collapse-toggle');
    if (collapsed.classList.contains('visible')) {
        collapsed.classList.remove('visible');
        btn.textContent = '📂 展开全部评论';
    } else {
        collapsed.classList.add('visible');
        btn.textContent = '📁 收起';
    }
}
</script>
"""
    html = html.replace("</body>", collapse_js + "\n</body>")

    if output_dir:
        out_dir = os.path.expanduser(output_dir)
    else:
        out_dir = os.path.expanduser("~/Downloads/QoderReports")
    os.makedirs(out_dir, exist_ok=True)

    filename = f"快手评论分析_{opus_id}_全部{total_pages}页.html"
    file_path = os.path.join(out_dir, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[consolidate] 合并报告已生成: {file_path}", file=sys.stderr)
    return file_path


def main():
    parser = argparse.ArgumentParser(description="快手评论合并报告生成")
    parser.add_argument("opus_id", help="快手作品 opusId")
    parser.add_argument(
        "--pages-json", dest="pages_json", type=str, default=None,
        help='多页数据 JSON 字符串，格式: [{"page":1,"total":20,"comments":[...]},...]',
    )
    parser.add_argument(
        "--analysis-json", dest="analysis_json", type=str, default=None,
        help='累计分析数据 JSON',
    )
    parser.add_argument(
        "--output-dir", dest="output_dir", type=str, default=None,
        help="HTML 输出目录",
    )

    args = parser.parse_args()

    # 读取 pages 数据
    if args.pages_json:
        pages = json.loads(args.pages_json)
    else:
        raw = sys.stdin.read()
        pages = json.loads(raw) if raw.strip() else []

    if not pages:
        print("[error] 未提供评论数据", file=sys.stderr)
        sys.exit(1)

    # 读取分析数据
    if args.analysis_json:
        analysis = json.loads(args.analysis_json)
    else:
        analysis = {}

    html_path = generate_consolidated_report(
        opus_id=args.opus_id,
        pages=pages,
        analysis=analysis,
        output_dir=args.output_dir,
    )

    print(json.dumps({"html_path": html_path}, ensure_ascii=False))

    # 自动在浏览器中打开
    subprocess.run(["open", html_path])


if __name__ == "__main__":
    main()
