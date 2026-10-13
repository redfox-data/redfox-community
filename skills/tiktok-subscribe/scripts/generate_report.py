#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TikTok 监控订阅推送 HTML 日报生成脚本。

基于 subscribe.py fetch --save-json 保存的结果生成 HTML 日报：
按订阅项分组展示作品表格（无更新订阅项折叠提示），可选合并本地 AI 总结 JSON
（不调用接口、不消耗积分），支持浏览器一键导出 PDF / 高清图片。

用法：
    python generate_report.py --data output/tiktok_subscribe_latest.json
    python generate_report.py --data ... --analysis output/tiktok_subscribe_ai_summary.json --no-open
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys

TK_BLACK = "#161823"
TK_CYAN = "#25f4ee"
TK_PINK = "#fe2c55"
TK_SUB = "#7d7d8a"
TK_BORDER = "#e8e8ee"
TK_HOVER = "#fafafa"

_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(_SKILL_DIR, "output")

KIND_LABELS = {"keyword": "关键词", "account": "账号", "topic": "话题"}


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def fmt(v):
    try:
        return f"{int(v):,}"
    except (TypeError, ValueError):
        return "0"


def short(v, limit=90):
    s = str(v if v is not None else "").strip()
    return s if len(s) <= limit else s[: limit - 3] + "…"


def two_line_id(v, per=9):
    """作品 ID 拆成两行展示，避免固定列宽下溢出。"""
    s = str(v if v is not None else "")
    if len(s) > per:
        return f"{s[:per]}<br>{s[per:]}"
    return s


CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: #ffffff; color: {TK_BLACK};
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
  padding: 32px 16px;
}}
.report {{ max-width: 1440px; margin: 0 auto; }}
.header {{ display: flex; align-items: center; gap: 14px; margin-bottom: 6px; }}
.logo {{
  width: 46px; height: 46px; border-radius: 12px; background: {TK_BLACK};
  color: {TK_CYAN}; font-size: 26px; font-weight: 800;
  display: flex; align-items: center; justify-content: center; flex: none;
}}
.header h1 {{ font-size: 24px; font-weight: 800; letter-spacing: .2px; }}
.header .kw {{ color: {TK_PINK}; }}
.header .sub {{ color: {TK_SUB}; font-size: 13px; margin-top: 5px; line-height: 1.8; }}
.export-bar {{ text-align: right; margin: 10px 0 14px; }}
.btn {{
  border: 1px solid {TK_BORDER}; background: #fff; color: {TK_PINK};
  border-radius: 999px; padding: 8px 18px; font-size: 13px; font-weight: 700;
  cursor: pointer; margin-left: 8px;
}}
.btn-primary {{ background: {TK_PINK}; border-color: {TK_PINK}; color: #fff; }}
.btn:hover {{ opacity: .85; }}
.stats {{ display: flex; gap: 12px; flex-wrap: nowrap; margin-bottom: 16px; }}
.stat {{
  flex: 1; min-width: 150px; background: #fff; border: 1px solid {TK_BORDER};
  border-radius: 16px; padding: 14px 18px;
}}
.stat .v {{ font-size: 22px; font-weight: 800; color: {TK_BLACK}; }}
.stat .v em {{ font-style: normal; color: {TK_PINK}; }}
.stat .k {{ font-size: 12px; color: {TK_SUB}; margin-top: 4px; }}
.item-title {{ font-size: 17px; font-weight: 800; margin: 24px 0 10px; }}
.item-title .tag {{
  display: inline-block; font-size: 11px; font-weight: 700; color: {TK_SUB};
  border: 1px solid {TK_BORDER}; border-radius: 999px; padding: 2px 10px;
  margin-right: 8px; vertical-align: 2px;
}}
.item-title .cnt {{ color: {TK_PINK}; }}
.fold {{
  border: 1px dashed {TK_BORDER}; border-radius: 14px; padding: 14px 18px;
  color: {TK_SUB}; font-size: 13px; background: {TK_HOVER};
}}
.fold.warn {{ border-color: #ffd3dd; color: {TK_PINK}; background: #fff5f7; }}
.table-wrap {{
  border: 1px solid {TK_BORDER}; border-radius: 16px; overflow: hidden; background: #fff;
}}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; }}
thead th {{
  background: {TK_HOVER}; color: {TK_SUB}; font-size: 12px; font-weight: 700;
  text-align: left; padding: 12px 10px; border-bottom: 1px solid {TK_BORDER};
}}
tbody td {{ padding: 12px 10px; border-bottom: 1px solid {TK_BORDER}; vertical-align: top; }}
tbody tr:last-child td {{ border-bottom: none; }}
tbody tr:hover {{ background: {TK_HOVER}; }}
.rank {{ font-weight: 800; font-size: 15px; white-space: nowrap; }}
.name {{ font-weight: 700; }}
.name a {{ color: {TK_BLACK}; text-decoration: none; }}
.name a:hover {{ text-decoration: underline; }}
.handle {{ color: {TK_SUB}; font-size: 12px; margin-top: 2px; word-break: break-all; }}
.num {{ font-weight: 700; white-space: nowrap; }}
.dim {{ color: {TK_SUB}; }}
.workid {{ word-break: break-all; color: {TK_SUB}; font-size: 12px; line-height: 1.5; }}
.summary {{ color: {TK_SUB}; font-size: 12px; line-height: 1.6; }}
.summary-clamp {{
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;
  overflow: hidden;
}}
.link a {{ color: {TK_PINK}; text-decoration: none; font-weight: 700; white-space: nowrap; }}
.link a:hover {{ text-decoration: underline; }}
.ai-title {{ font-size: 17px; font-weight: 800; margin: 26px 0 10px; }}
.ai-block {{ border: 1px solid {TK_BORDER}; border-radius: 16px; padding: 16px 18px; margin-bottom: 12px; }}
.ai-block .t {{ font-size: 14px; font-weight: 800; margin-bottom: 4px; }}
.ai-block .t .n {{ color: {TK_PINK}; margin-right: 6px; }}
.ai-block .s {{ font-size: 13px; color: {TK_SUB}; line-height: 1.8; }}
.ai-block .m {{ font-size: 12px; color: {TK_SUB}; margin-top: 6px; }}
.footer {{ margin-top: 18px; color: {TK_SUB}; font-size: 12px; text-align: center; line-height: 1.8; }}
@media (max-width: 768px) {{ .stats {{ flex-wrap: wrap; }} }}
@media print {{ .export-bar {{ display: none; }} body {{ padding: 0; }} }}
"""

WORK_COLS = (
    ("排名", "52px"), ("作者", "150px"), ("作品ID", "120px"), ("播放", "86px"),
    ("点赞", "86px"), ("评论", "76px"), ("分享", "76px"), ("发布时间", "92px"),
    ("内容摘要", "auto"), ("链接", "80px"),
)
ACCOUNT_COLS = (
    ("排名", "52px"), ("作品ID", "120px"), ("播放", "86px"), ("点赞", "86px"),
    ("评论", "76px"), ("分享", "76px"), ("发布时间", "92px"),
    ("内容摘要", "auto"), ("链接", "80px"),
)


def colgroup(cols):
    defs = "".join(f"<col style='width:{w};'>" for _, w in cols)
    return f"<colgroup>{defs}</colgroup>"


def thead(cols):
    cells = "".join(f"<th>{name}</th>" for name, _ in cols)
    return f"<thead><tr>{cells}</tr></thead>"


def build_works_table(item):
    works = item.get("works") or []
    kind = item.get("kind")
    cols = ACCOUNT_COLS if kind == "account" else WORK_COLS
    rows = []
    for idx, w in enumerate(works, 1):
        link = w.get("shareLink") or ""
        link_cell = (f"<span class='link'><a href='{esc(link)}' target='_blank' "
                     f"rel='noopener'>打开作品</a></span>") if link else "<span class='dim'>—</span>"
        content = w.get("content") or ""
        name = esc(w.get("name")) or "—"
        handle = esc(w.get("handle"))
        author_cell = f"<div class='name'>{name}</div>"
        if handle:
            author_cell += f"<div class='handle'>@{handle}</div>"
        cells = [
            f"<td class='rank'>{idx}</td>",
        ]
        if kind != "account":
            cells.append(f"<td>{author_cell}</td>")
        cells += [
            f"<td class='workid'>{two_line_id(w.get('workId')) or '—'}</td>",
            f"<td class='num'>{fmt(w.get('views'))}</td>",
            f"<td class='num'>{fmt(w.get('likes'))}</td>",
            f"<td class='num'>{fmt(w.get('comments'))}</td>",
            f"<td class='num'>{fmt(w.get('shares'))}</td>",
            f"<td class='dim'>{esc(w.get('time')) or '—'}</td>",
            f"<td class='summary summary-clamp' title='{esc(content)}'>{esc(short(content, 100)) or '—'}</td>",
            f"<td>{link_cell}</td>",
        ]
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (f"<div class='table-wrap'><table>{colgroup(cols)}{thead(cols)}"
            f"<tbody>{''.join(rows)}</tbody></table></div>")


def build_item_section(item, first):
    kind = item.get("kind")
    label = esc(item.get("label") or item.get("key") or "—")
    tag = KIND_LABELS.get(kind, kind)
    status = item.get("status")
    works = item.get("works") or []

    if status == "error":
        detail = esc(item.get("error") or "接口请求失败")
        return (f"<div class='item-title'><span class='tag'>{tag}</span>▸ {label}</div>"
                f"<div class='fold warn'>⚠️ 拉取失败：{detail}</div>")
    if status == "no_update_7d":
        return (f"<div class='item-title'><span class='tag'>{tag}</span>▸ {label}</div>"
                f"<div class='fold'>🕐 近 7 天无更新（该订阅项最近 7 天没有新内容）</div>")
    if status == "no_update_yesterday":
        return (f"<div class='item-title'><span class='tag'>{tag}</span>▸ {label}</div>"
                f"<div class='fold'>😴 昨日无更新（该订阅项昨日时间窗内无新内容）</div>")
    suffix = "最新动态" if first else "昨日新内容"
    return (f"<div class='item-title'><span class='tag'>{tag}</span>▸ {label} "
            f"{suffix} <span class='cnt'>（{len(works)} 条）</span></div>"
            + build_works_table(item))


def build_stats(saved):
    items = saved.get("items") or []
    updated = sum(1 for it in items if it.get("status") == "updated")
    total_works = sum(len(it.get("works") or []) for it in items if it.get("status") == "updated")
    folded = sum(1 for it in items if it.get("status") in ("no_update_yesterday", "no_update_7d"))
    err = sum(1 for it in items if it.get("status") == "error")
    return (
        "<div class='stats'>"
        f"<div class='stat'><div class='v'>{updated} <em>项</em></div><div class='k'>有更新订阅项</div></div>"
        f"<div class='stat'><div class='v'>{total_works} <em>条</em></div><div class='k'>时间窗内作品</div></div>"
        f"<div class='stat'><div class='v'>{folded} <em>项</em></div><div class='k'>无更新（已折叠）</div></div>"
        + (f"<div class='stat'><div class='v'>{err} <em>项</em></div><div class='k'>拉取失败</div></div>" if err else "")
        + "</div>"
    )


def build_ai_sections(analysis):
    analysis = analysis or {}
    blocks = []
    overall = analysis.get("overall") or []
    if overall:
        rows = []
        for i, item in enumerate(overall, 1):
            scope = "、".join(esc(x) for x in (item.get("items") or []))
            rows.append(
                f"<div class='ai-block'><div class='t'><span class='n'>#{i}</span>{esc(item.get('title') or '—')}</div>"
                f"<div class='s'>{esc(item.get('summary') or '')}</div>"
                f"<div class='m'>涉及：{scope} ｜ 相关作品 {item.get('workCount', 0)} 条</div></div>"
            )
        blocks.append("<div class='ai-title'>🎯 今日主题总结</div>" + "".join(rows))

    per_items = analysis.get("items") or []
    if per_items:
        rows = []
        for i, item in enumerate(per_items, 1):
            tag = KIND_LABELS.get(item.get("kind"), "")
            rows.append(
                f"<div class='ai-block'><div class='t'><span class='n'>#{i}</span>"
                f"<span class='tag'>{esc(tag)}</span>{esc(item.get('key') or '—')}</div>"
                f"<div class='s'>主题：{esc(item.get('theme') or '—')}<br>观点：{esc(item.get('viewpoint') or '—')}</div></div>"
            )
        blocks.append("<div class='ai-title'>📋 单订阅项解读</div>" + "".join(rows))

    return "".join(blocks) if blocks else ""


def report_filename(meta):
    date = str(meta.get("date") or "latest")
    if meta.get("mode") == "first":
        return f"TikTok订阅首次拉取_{date}.html"
    return f"TikTok订阅日报_{date}.html"


def build_html(saved, analysis):
    meta = saved.get("meta", {})
    first = meta.get("mode") == "first"
    date = esc(meta.get("date") or "")
    window = f"{esc(meta.get('windowStart') or '—')} ~ {esc(meta.get('windowEnd') or '—')}"
    now = meta.get("generatedAt") or ""
    img_name = report_filename(meta)[:-5] + ".png"

    items = saved.get("items") or []
    sections = "".join(build_item_section(it, first) for it in items)

    ai_html = build_ai_sections(analysis)

    mode_text = "首次拉取（最新动态）" if first else f"每日更新（时间窗 {window}）"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TikTok订阅监控日报 · {date}</title>
<style>{CSS}</style>
</head>
<body>
<div class="report" id="report">
  <div class="header">
    <div class="logo">♪</div>
    <div>
      <h1>TikTok订阅监控日报 <span class="kw">{date}</span></h1>
      <div class="sub">{mode_text} ｜ 地区：{esc(meta.get('region') or 'US')}<br>生成时间：{esc(now)}</div>
    </div>
  </div>

  <div class="export-bar">
    <button class="btn btn-primary" onclick="window.print()">🖨️ 导出 PDF</button>
    <button class="btn" id="downloadImgBtn" onclick="downloadAsImage()">📷 导出图片</button>
  </div>

  {build_stats(saved)}

  {sections}

  {ai_html}

  <div class="footer">
    数据来源：红狐数据 · 生成时间 {esc(now)}<br>
    AI 总结为基于公开数据的分析与推测，仅供参考 ｜ 本报告支持浏览器一键导出 PDF / 高清图片
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<script>
async function downloadAsImage() {{
  const btn = document.getElementById('downloadImgBtn');
  btn.disabled = true; btn.textContent = '⏳ 生成中...';
  try {{
    const canvas = await html2canvas(document.getElementById('report'), {{
      scale: 2, backgroundColor: '#ffffff', useCORS: true
    }});
    const a = document.createElement('a');
    a.download = '{img_name}';
    a.href = canvas.toDataURL('image/png');
    a.click();
  }} catch (e) {{
    alert('图片导出失败：' + e.message + '\\n可改用「导出 PDF」按钮。');
  }} finally {{
    btn.disabled = false; btn.textContent = '📷 导出图片';
  }}
}}
</script>
</body>
</html>"""


def open_in_browser(path):
    try:
        abs_path = os.path.abspath(path)
        if sys.platform == "darwin":
            subprocess.run(["open", abs_path], check=True)
        elif sys.platform.startswith("win"):
            os.startfile(abs_path)  # noqa
        else:
            subprocess.run(["xdg-open", abs_path], check=True)
        print(f"\n✓ HTML 日报已自动打开: {abs_path}", file=sys.stderr)
    except Exception:
        print(f"\n✓ HTML 日报已生成: {os.path.abspath(path)}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="生成 TikTok 订阅监控 HTML 日报")
    parser.add_argument("--data", required=True, help="subscribe.py fetch --save-json 保存的 JSON 路径")
    parser.add_argument("--analysis", default=None, help="AI 总结 JSON 路径（本地文件，不调用接口）")
    parser.add_argument("--output", default=None, help="HTML 输出路径")
    parser.add_argument("--no-open", action="store_true", help="生成后不自动打开浏览器")
    args = parser.parse_args()

    with open(args.data, encoding="utf-8") as f:
        saved = json.load(f)

    analysis = None
    if args.analysis and os.path.exists(args.analysis):
        with open(args.analysis, encoding="utf-8") as f:
            analysis = json.load(f)

    meta = saved.get("meta") or {}
    out = args.output or os.path.join(OUTPUT_DIR, report_filename(meta))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_html(saved, analysis))
    print(f"[INFO] HTML 日报已生成：{out}")

    if not args.no_open:
        open_in_browser(out)


if __name__ == "__main__":
    main()
