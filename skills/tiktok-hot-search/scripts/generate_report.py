#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TikTok热门搜索 HTML 报告生成脚本。

基于 tiktok_hot_search.py --save-json 保存的查询结果生成 HTML 报告：
含搜索条件说明、「{关键词}热门概览」（爆款视频 / 热门用户 / 热门话题 TOP3 卡片）与三类榜单表格，
支持浏览器一键导出 PDF / 高清图片。

用法：
    python generate_report.py --data output/tiktok_search_latest.json
    python generate_report.py --data ... --no-open
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
MEDALS = {1: ("🥇", "#ffd700"), 2: ("🥈", "#c0c0c0"), 3: ("🥉", "#cd7f32")}


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
.top3-title {{ font-size: 17px; font-weight: 800; margin: 22px 0 10px; }}
.top3-sub {{ font-size: 14px; font-weight: 800; color: {TK_BLACK}; margin: 16px 0 8px; }}
.top3 {{ display: flex; gap: 12px; margin-bottom: 6px; }}
.top3 .card {{
  flex: 1; border: 1px solid {TK_BORDER}; border-radius: 16px; padding: 14px 18px; background: #fff;
}}
.top3 .n {{ font-size: 13px; font-weight: 800; color: {TK_SUB}; }}
.top3 .name {{ font-size: 16px; font-weight: 800; margin: 4px 0 2px; }}
.top3 .meta {{ font-size: 12px; color: {TK_SUB}; margin-bottom: 6px; }}
.top3 .g {{ font-size: 15px; font-weight: 800; color: {TK_PINK}; }}
.top3 .p {{ font-size: 12px; color: {TK_SUB}; margin-top: 6px; line-height: 1.6; }}
.top3 .p a {{ color: {TK_BLACK}; text-decoration: none; font-weight: 700; }}
.top3 .p a:hover {{ text-decoration: underline; }}
.section-title {{ font-size: 17px; font-weight: 800; margin: 22px 0 10px; }}
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
.name a {{ color: {TK_BLACK}; text-decoration: none; font-weight: 700; }}
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
.footer {{ margin-top: 18px; color: {TK_SUB}; font-size: 12px; text-align: center; line-height: 1.8; }}
@media (max-width: 768px) {{ .stats, .top3 {{ flex-wrap: wrap; }} }}
@media print {{ .export-bar {{ display: none; }} body {{ padding: 0; }} }}
"""

VIDEO_COLS = (
    ("排名", "52px"), ("作者", "150px"), ("作品ID", "130px"), ("播放", "86px"),
    ("点赞", "86px"), ("评论", "76px"), ("分享", "76px"), ("发布时间", "90px"),
    ("内容摘要", "auto"), ("链接", "86px"),
)
USER_COLS = (
    ("排名", "52px"), ("昵称", "160px"), ("TikTok号", "130px"), ("粉丝数", "96px"),
    ("获赞总数", "96px"), ("作品数", "84px"), ("主页", "80px"),
)
TOPIC_COLS = (
    ("排名", "52px"), ("话题", "200px"), ("话题ID", "130px"), ("浏览量", "110px"),
    ("使用次数", "96px"), ("链接", "80px"),
)


def colgroup(cols):
    defs = "".join(f"<col style='width:{w};'>" for _, w in cols)
    return f"<colgroup>{defs}</colgroup>"


def thead(cols):
    cells = "".join(f"<th>{name}</th>" for name, _ in cols)
    return f"<thead><tr>{cells}</tr></thead>"


def build_video_table(items):
    rows = []
    for it in items or []:
        medal = MEDALS.get(it.get("rank"))
        rank_cell = f"<span>{medal[0]} {it['rank']}</span>" if medal else f"<span>{it['rank']}</span>"
        name = esc(it.get("name")) or "—"
        handle = esc(it.get("handle"))
        author = f"<div class='name'>{name}</div>"
        if handle:
            author += f"<div class='handle'>@{handle}</div>"
        link = it.get("shareLink") or ""
        link_cell = (f"<span class='link'><a href='{esc(link)}' target='_blank' "
                     f"rel='noopener'>打开作品</a></span>") if link else "<span class='dim'>—</span>"
        content = it.get("content") or ""
        rows.append(
            "<tr>"
            f"<td class='rank'>{rank_cell}</td>"
            f"<td>{author}</td>"
            f"<td class='workid'>{two_line_id(it.get('workId')) or '—'}</td>"
            f"<td class='num'>{fmt(it.get('views'))}</td>"
            f"<td class='num'>{fmt(it.get('likes'))}</td>"
            f"<td class='num'>{fmt(it.get('comments'))}</td>"
            f"<td class='num'>{fmt(it.get('shares'))}</td>"
            f"<td class='dim'>{esc(it.get('date')) or '—'}</td>"
            f"<td class='summary summary-clamp' title='{esc(content)}'>{esc(short(content, 120)) or '—'}</td>"
            f"<td>{link_cell}</td>"
            "</tr>")
    return (f"<div class='table-wrap'><table>{colgroup(VIDEO_COLS)}{thead(VIDEO_COLS)}"
            f"<tbody>{''.join(rows)}</tbody></table></div>")


def build_user_table(items):
    rows = []
    for it in items or []:
        medal = MEDALS.get(it.get("rank"))
        rank_cell = f"<span>{medal[0]} {it['rank']}</span>" if medal else f"<span>{it['rank']}</span>"
        name = esc(it.get("name")) or "—"
        handle = esc(it.get("handle"))
        profile = it.get("profileUrl") or ""
        name_cell = (f"<div class='name'><a href='{esc(profile)}' target='_blank' rel='noopener'>{name}</a></div>"
                     if profile else f"<div class='name'>{name}</div>")
        if handle:
            name_cell += f"<div class='handle'>@{handle}</div>"
        link_cell = (f"<span class='link'><a href='{esc(profile)}' target='_blank' "
                     f"rel='noopener'>打开主页</a></span>") if profile else "<span class='dim'>—</span>"
        rows.append(
            "<tr>"
            f"<td class='rank'>{rank_cell}</td>"
            f"<td>{name_cell}</td>"
            f"<td class='dim'>{handle or '—'}</td>"
            f"<td class='num'>{fmt(it.get('fans'))}</td>"
            f"<td class='num'>{fmt(it.get('liked'))}</td>"
            f"<td class='num'>{fmt(it.get('works'))}</td>"
            f"<td>{link_cell}</td>"
            "</tr>")
    return (f"<div class='table-wrap'><table>{colgroup(USER_COLS)}{thead(USER_COLS)}"
            f"<tbody>{''.join(rows)}</tbody></table></div>")


def build_topic_table(items):
    rows = []
    for it in items or []:
        medal = MEDALS.get(it.get("rank"))
        rank_cell = f"<span>{medal[0]} {it['rank']}</span>" if medal else f"<span>{it['rank']}</span>"
        name = esc(it.get("name")) or "—"
        link = it.get("shareLink") or ""
        name_cell = (f"<div class='name'><a href='{esc(link)}' target='_blank' rel='noopener'>{name}</a></div>"
                     if link else f"<div class='name'>{name}</div>")
        desc = it.get("description") or ""
        if desc:
            name_cell += f"<div class='summary' title='{esc(desc)}'>{esc(short(desc, 40))}</div>"
        link_cell = (f"<span class='link'><a href='{esc(link)}' target='_blank' "
                     f"rel='noopener'>打开话题</a></span>") if link else "<span class='dim'>—</span>"
        rows.append(
            "<tr>"
            f"<td class='rank'>{rank_cell}</td>"
            f"<td>{name_cell}</td>"
            f"<td class='dim'>{esc(it.get('topicId')) or '—'}</td>"
            f"<td class='num'>{fmt(it.get('views'))}</td>"
            f"<td class='num'>{fmt(it.get('usage'))}</td>"
            f"<td>{link_cell}</td>"
            "</tr>")
    return (f"<div class='table-wrap'><table>{colgroup(TOPIC_COLS)}{thead(TOPIC_COLS)}"
            f"<tbody>{''.join(rows)}</tbody></table></div>")


def build_video_cards(items):
    items = (items or [])[:3]
    cards = []
    for i, it in enumerate(items, 1):
        link = it.get("shareLink") or ""
        content = esc(short(it.get("content"), 120)) or "—"
        link_line = (f"<a href='{esc(link)}' target='_blank' rel='noopener'>打开作品 ↗</a>"
                     if link else "")
        cards.append(
            f"<div class='card'><div class='n'>TOP {i}</div>"
            f"<div class='name'>{esc(it.get('name')) or '—'}</div>"
            f"<div class='meta'>发布于 {esc(it.get('date')) or '—'} ｜ 作品 {esc(it.get('workId')) or '—'}</div>"
            f"<div class='g'>播放 {fmt(it.get('views'))}</div>"
            f"<div class='p'>点赞 {fmt(it.get('likes'))} · 评论 {fmt(it.get('comments'))} · 分享 {fmt(it.get('shares'))}</div>"
            f"<div class='p'>{content}{(' · ' + link_line) if link else ''}</div>"
            "</div>")
    return "".join(cards)


def build_user_cards(items):
    items = (items or [])[:3]
    cards = []
    for i, it in enumerate(items, 1):
        link = it.get("profileUrl") or ""
        link_line = (f"<a href='{esc(link)}' target='_blank' rel='noopener'>打开主页 ↗</a>"
                     if link else "")
        handle = esc(it.get("handle"))
        cards.append(
            f"<div class='card'><div class='n'>TOP {i}</div>"
            f"<div class='name'>{esc(it.get('name')) or '—'}</div>"
            f"<div class='meta'>@{handle or '—'}</div>"
            f"<div class='g'>粉丝 {fmt(it.get('fans'))}</div>"
            f"<div class='p'>获赞 {fmt(it.get('liked'))} · 作品 {fmt(it.get('works'))}</div>"
            f"<div class='p'>{link_line}</div>"
            "</div>")
    return "".join(cards)


def build_topic_cards(items):
    items = (items or [])[:3]
    cards = []
    for i, it in enumerate(items, 1):
        link = it.get("shareLink") or ""
        desc = esc(short(it.get("description"), 90))
        link_line = (f"<a href='{esc(link)}' target='_blank' rel='noopener'>打开话题 ↗</a>"
                     if link else "")
        cards.append(
            f"<div class='card'><div class='n'>TOP {i}</div>"
            f"<div class='name'>{esc(it.get('name')) or '—'}</div>"
            f"<div class='meta'>话题 ID {esc(it.get('topicId')) or '—'}</div>"
            f"<div class='g'>浏览 {fmt(it.get('views'))}</div>"
            f"<div class='p'>使用 {fmt(it.get('usage'))} 次</div>"
            f"<div class='p'>{desc}{(' · ' + link_line) if link else ''}</div>"
            "</div>")
    return "".join(cards)


def build_overview(saved, keyword):
    """「{关键词}热门概览」：爆款视频 / 热门用户 / 热门话题 TOP3 卡片，按现有类型输出。"""
    groups = []
    video = saved.get("video")
    if video:
        groups.append(("爆款视频 TOP3", build_video_cards(video.get("items"))))
    user = saved.get("user")
    if user:
        groups.append(("热门用户 Top3", build_user_cards(user.get("items"))))
    topic = saved.get("topic")
    if topic:
        groups.append(("热门话题 Top3", build_topic_cards(topic.get("items"))))
    blocks = []
    for title, cards in groups:
        if cards:
            blocks.append(f"<div class='top3-sub'>{title}</div><div class='top3'>{cards}</div>")
    if not blocks:
        return ""
    return (f"<div class='top3-title'>🎯 {esc(keyword)}热门概览</div>"
            + "".join(blocks))


def build_stats(saved):
    cards = []
    video = saved.get("video") or {}
    vitems = video.get("items") or []
    if vitems:
        top = max((it.get("views") or 0) for it in vitems)
        cards.append(f"<div class='stat'><div class='v'>{len(vitems)} <em>条</em></div>"
                     f"<div class='k'>热门视频 · 最高播放 {fmt(top)}</div></div>")
    user = saved.get("user") or {}
    uitems = user.get("items") or []
    if uitems:
        top = max((it.get("fans") or 0) for it in uitems)
        cards.append(f"<div class='stat'><div class='v'>{len(uitems)} <em>个</em></div>"
                     f"<div class='k'>相关账号 · 最高粉丝 {fmt(top)}</div></div>")
    topic = saved.get("topic") or {}
    titems = topic.get("items") or []
    if titems:
        total = sum((it.get("views") or 0) for it in titems)
        cards.append(f"<div class='stat'><div class='v'>{len(titems)} <em>个</em></div>"
                     f"<div class='k'>相关话题 · 本页总浏览 {fmt(total)}</div></div>")
    return f"<div class='stats'>{''.join(cards)}</div>" if cards else ""


def filters_line(meta):
    filters = meta.get("filters") or {}
    parts = [f"排序：{esc(filters.get('sortLabel'))}",
             f"发布时间：{esc(filters.get('publishLabel'))}",
             f"地区：{esc(filters.get('region'))}"]
    fans = filters.get("fans")
    parts.append(f"粉丝数：{esc(filters.get('fansLabel'))}" if fans else "粉丝数：不限制")
    parts.append("仅认证账号" if filters.get("verified") else "不限认证")
    return " ｜ ".join(parts)


def type_label(kind):
    return {"video": "热门视频", "user": "相关用户", "topic": "相关话题"}.get(kind, kind)


def report_filename(meta):
    keyword = str(meta.get("keyword") or "latest")
    safe = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", keyword).strip("_") or "latest"
    return f"TikTok热门搜索_{safe}_报告.html"


def build_html(saved):
    meta = saved.get("meta", {})
    keyword = esc(meta.get("keyword") or "")
    types = meta.get("types") or []
    type_text = "、".join(type_label(k) for k in types) or "—"
    now = meta.get("generatedAt") or ""
    img_name = report_filename(meta)[:-5] + ".png"

    sections = []
    video = saved.get("video")
    user = saved.get("user")
    topic = saved.get("topic")
    overview_html = build_overview(saved, meta.get("keyword") or "")
    if video:
        sections.append("<div class='section-title'>📊 热门视频榜</div>" + build_video_table(video.get("items")))
    if user:
        sections.append(f"<div class='section-title'>🚀 {keyword}相关作品用户榜</div>" + build_user_table(user.get("items")))
    if topic:
        sections.append(f"<div class='section-title'>💡 {keyword}相关话题榜</div>" + build_topic_table(topic.get("items")))

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc('TikTok热门搜索')} · {keyword} 报告</title>
<style>{CSS}</style>
</head>
<body>
<div class="report" id="report">
  <div class="header">
    <div class="logo">♪</div>
    <div>
      <h1>TikTok热门搜索 · 关键词 <span class="kw">{keyword}</span></h1>
      <div class="sub">查询类型：{type_text} ｜ {filters_line(meta)}<br>生成时间：{esc(now)}</div>
    </div>
  </div>

  <div class="export-bar">
    <button class="btn btn-primary" onclick="window.print()">🖨️ 导出 PDF</button>
    <button class="btn" id="downloadImgBtn" onclick="downloadAsImage()">📷 导出图片</button>
  </div>

  {build_stats(saved)}

  {overview_html}

  {''.join(sections)}

  <div class="footer">
    数据来源：红狐数据 · 生成时间 {esc(now)}<br>
    本报告支持浏览器一键导出 PDF / 高清图片
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
        print(f"\n✓ HTML 报告已自动打开: {abs_path}", file=sys.stderr)
    except Exception:
        print(f"\n✓ HTML 报告已生成: {os.path.abspath(path)}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="生成 TikTok热门搜索 HTML 报告")
    parser.add_argument("--data", required=True, help="tiktok_hot_search.py --save-json 保存的 JSON 路径")
    parser.add_argument("--output", default=None, help="HTML 输出路径")
    parser.add_argument("--no-open", action="store_true", help="生成后不自动打开浏览器")
    args = parser.parse_args()

    with open(args.data, encoding="utf-8") as f:
        saved = json.load(f)

    meta = saved.get("meta") or {}
    out = args.output or os.path.join(OUTPUT_DIR, report_filename(meta))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_html(saved))
    print(f"[INFO] HTML 报告已生成：{out}")

    if not args.no_open:
        open_in_browser(out)


if __name__ == "__main__":
    main()
