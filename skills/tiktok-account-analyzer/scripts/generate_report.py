#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TikTok 账号深度分析 HTML 报告生成脚本。

基于 tiktok_account_analyzer.py --save-json 保存的查询结果生成 HTML 报告：
含账号信息卡、主页作品榜、喜欢作品榜，以及爆款作品 TOP3 拆解、六维量化诊断
（规则化离线计算）与账号诊断总结（AI 分析，与对话输出保持一致）。
分析类内容通过 --analysis 指定的 JSON 文件注入，支持浏览器一键导出 PDF / 高清图片。

用法：
    python generate_report.py --data output/tiktok_account_latest.json
    python generate_report.py --data ... --analysis output/tiktok_account_analysis.json --no-open
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
.profile-card {{
  border: 1px solid {TK_BORDER}; border-radius: 16px; padding: 18px 20px;
  background: #fff; margin-bottom: 16px;
}}
.profile-card h2 {{ font-size: 15px; font-weight: 800; margin-bottom: 12px; }}
.profile-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px 10px; }}
.pf {{ min-width: 0; }}
.pf .k {{ font-size: 12px; color: {TK_SUB}; margin-bottom: 4px; }}
.pf .v {{ font-size: 14px; font-weight: 700; word-break: break-all; line-height: 1.5; }}
.pf .v a {{ color: {TK_PINK}; text-decoration: none; font-weight: 700; }}
.pf .v a:hover {{ text-decoration: underline; }}
.pf-wide {{ grid-column: span 3; }}
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
.num {{ font-weight: 700; white-space: nowrap; }}
.dim {{ color: {TK_SUB}; }}
.summary {{ color: {TK_BLACK}; font-size: 12px; line-height: 1.6; }}
.summary-clamp {{
  display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical;
  overflow: hidden;
}}
.author {{ color: {TK_SUB}; font-size: 12px; word-break: break-all; }}
.link a {{ color: {TK_PINK}; text-decoration: none; font-weight: 700; white-space: nowrap; }}
.link a:hover {{ text-decoration: underline; }}
.empty {{ color: {TK_SUB}; font-size: 13px; padding: 6px 0; }}
.analysis-title {{ font-size: 17px; font-weight: 800; margin: 22px 0 10px; }}
.viral-cards {{ display: flex; gap: 12px; margin-bottom: 6px; }}
.viral-cards .card {{
  flex: 1; border: 1px solid {TK_BORDER}; border-radius: 16px; padding: 14px 18px; background: #fff;
}}
.card .n {{ font-size: 13px; font-weight: 800; color: {TK_SUB}; }}
.card .name {{ font-size: 15px; font-weight: 800; margin: 4px 0 2px; line-height: 1.5; }}
.card .meta {{ font-size: 12px; color: {TK_SUB}; margin-bottom: 6px; }}
.card .g {{ font-size: 15px; font-weight: 800; color: {TK_PINK}; }}
.card .p {{ font-size: 12px; color: {TK_SUB}; margin-top: 6px; line-height: 1.6; }}
.card .p a {{ color: {TK_BLACK}; text-decoration: none; font-weight: 700; }}
.card .p a:hover {{ text-decoration: underline; }}
.diagnosis-card {{
  border: 1px solid {TK_BORDER}; border-radius: 16px; padding: 16px 18px; background: #fff;
}}
.diagnosis-card .p {{ font-size: 13px; line-height: 1.9; color: {TK_BLACK}; }}
.diagnosis-card .note {{ font-size: 12px; color: {TK_SUB}; margin-top: 8px; }}
.score-hero {{
  display: flex; gap: 20px; align-items: center; border: 1px solid {TK_BORDER};
  border-radius: 16px; padding: 18px 22px; background: #fff; margin-bottom: 14px;
}}
.score-big {{ font-size: 54px; font-weight: 800; color: {TK_PINK}; line-height: 1; }}
.score-unit {{ font-size: 14px; color: {TK_SUB}; margin-top: 6px; text-align: center; }}
.grade-chip {{ font-size: 16px; font-weight: 800; }}
.tier-chip {{
  display: inline-block; border: 1px solid {TK_BORDER}; border-radius: 999px;
  padding: 4px 12px; font-size: 12px; color: {TK_SUB}; margin-left: 10px;
  vertical-align: 2px;
}}
.score-sub {{ font-size: 12px; color: {TK_SUB}; margin-top: 8px; line-height: 1.7; }}
.dim-name {{ font-weight: 700; white-space: nowrap; }}
.dim-name .w {{ color: {TK_SUB}; font-weight: 400; font-size: 12px; }}
.bar-wrap {{
  display: inline-block; width: 72px; height: 8px; background: {TK_HOVER};
  border-radius: 999px; overflow: hidden; vertical-align: middle; margin-right: 8px;
}}
.bar {{ height: 100%; background: linear-gradient(90deg, {TK_CYAN}, {TK_PINK}); border-radius: 999px; }}
.bar-pct {{ font-size: 12px; color: {TK_SUB}; vertical-align: middle; }}
.comment {{ color: {TK_SUB}; font-size: 12px; line-height: 1.6; }}
.subitems {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 14px; }}
.dim-card {{ border: 1px solid {TK_BORDER}; border-radius: 16px; padding: 14px 16px; background: #fff; }}
.dim-card-title {{ font-size: 13px; font-weight: 800; margin-bottom: 6px; }}
.dim-card-title .meta {{ color: {TK_SUB}; font-weight: 400; font-size: 12px; margin-left: 6px; }}
.subitem {{ display: flex; justify-content: space-between; align-items: baseline; gap: 8px; font-size: 12px; padding: 5px 0; border-bottom: 1px dashed {TK_BORDER}; }}
.subitem:last-child {{ border-bottom: none; }}
.sub-label {{ color: {TK_BLACK}; }}
.sub-right {{ white-space: nowrap; }}
.sub-note {{ color: {TK_SUB}; margin-right: 8px; }}
.sub-score {{ font-weight: 700; }}
.subitem.excluded .sub-label {{ color: {TK_SUB}; }}
.subitem.excluded .sub-score {{ font-weight: 400; color: {TK_SUB}; }}
.alerts {{ margin-top: 14px; }}
.alert-chip {{
  display: block; border: 1px solid; border-radius: 12px; padding: 8px 14px;
  margin-top: 8px; font-size: 12px; line-height: 1.6;
}}
.alert-chip.high {{ border-color: #fecaca; background: #fef2f2; color: #b91c1c; }}
.alert-chip.mid {{ border-color: #fed7aa; background: #fff7ed; color: #c2410c; }}
.alert-chip.low {{ border-color: #e2e8f0; background: #f8fafc; color: #475569; }}
.scoring-notes {{ font-size: 12px; color: {TK_SUB}; margin-top: 12px; line-height: 1.9; }}
.footer {{ margin-top: 18px; color: {TK_SUB}; font-size: 12px; text-align: center; line-height: 1.8; }}
@media (max-width: 768px) {{ .stats, .viral-cards {{ flex-wrap: wrap; }} .profile-grid, .subitems {{ grid-template-columns: repeat(2, 1fr); }} }}
@media print {{ .export-bar {{ display: none; }} body {{ padding: 0; }} }}
"""

WORKS_COLS = (
    ("排名", "52px"), ("发布时间", "90px"), ("作品", "auto"), ("播放", "86px"),
    ("点赞", "86px"), ("评论", "76px"), ("收藏", "76px"), ("分享", "76px"),
    ("链接", "86px"),
)
FAV_COLS = (
    ("排名", "52px"), ("发布时间", "90px"), ("作品", "auto"), ("作者", "150px"),
    ("播放", "86px"), ("点赞", "86px"), ("链接", "86px"),
)


def colgroup(cols):
    defs = "".join(f"<col style='width:{w};'>" for _, w in cols)
    return f"<colgroup>{defs}</colgroup>"


def thead(cols):
    cells = "".join(f"<th>{name}</th>" for name, _ in cols)
    return f"<thead><tr>{cells}</tr></thead>"


def build_works_table(items):
    if not items:
        return "<div class='empty'>暂无数据</div>"
    rows = []
    for it in items:
        link = it.get("shareLink") or ""
        link_cell = (f"<span class='link'><a href='{esc(link)}' target='_blank' "
                     f"rel='noopener'>打开作品</a></span>") if link else "<span class='dim'>—</span>"
        content = it.get("content") or ""
        rows.append(
            "<tr>"
            f"<td class='rank'>{it.get('rank') or '—'}</td>"
            f"<td class='dim'>{esc(it.get('date')) or '—'}</td>"
            f"<td class='summary summary-clamp' title='{esc(content)}'>{esc(short(content, 120)) or '—'}</td>"
            f"<td class='num'>{fmt(it.get('views'))}</td>"
            f"<td class='num'>{fmt(it.get('likes'))}</td>"
            f"<td class='num'>{fmt(it.get('comments'))}</td>"
            f"<td class='num'>{fmt(it.get('favorites'))}</td>"
            f"<td class='num'>{fmt(it.get('shares'))}</td>"
            f"<td>{link_cell}</td>"
            "</tr>")
    return (f"<div class='table-wrap'><table>{colgroup(WORKS_COLS)}{thead(WORKS_COLS)}"
            f"<tbody>{''.join(rows)}</tbody></table></div>")


def build_fav_table(items):
    if not items:
        return "<div class='empty'>暂无数据（该账号的喜欢列表可能已设为私密）</div>"
    rows = []
    for it in items:
        link = it.get("shareLink") or ""
        link_cell = (f"<span class='link'><a href='{esc(link)}' target='_blank' "
                     f"rel='noopener'>打开作品</a></span>") if link else "<span class='dim'>—</span>"
        content = it.get("content") or ""
        author = esc(it.get("author")) or "—"
        if it.get("authorHandle"):
            author = f"{author}<br><span class='handle'>@{esc(it.get('authorHandle'))}</span>"
        rows.append(
            "<tr>"
            f"<td class='rank'>{it.get('rank') or '—'}</td>"
            f"<td class='dim'>{esc(it.get('date')) or '—'}</td>"
            f"<td class='summary summary-clamp' title='{esc(content)}'>{esc(short(content, 120)) or '—'}</td>"
            f"<td class='author'>{author}</td>"
            f"<td class='num'>{fmt(it.get('views'))}</td>"
            f"<td class='num'>{fmt(it.get('likes'))}</td>"
            f"<td>{link_cell}</td>"
            "</tr>")
    return (f"<div class='table-wrap'><table>{colgroup(FAV_COLS)}{thead(FAV_COLS)}"
            f"<tbody>{''.join(rows)}</tbody></table></div>")


def build_viral_top3(analysis):
    analysis = analysis or {}
    items = analysis.get("viralTop3") or []
    if not items:
        return ""
    cards = []
    for it in items[:3]:
        link = it.get("link") or ""
        link_line = (f"<a href='{esc(link)}' target='_blank' rel='noopener'>打开作品 ↗</a>"
                     if link else "")
        reason = str(it.get("reason") or "").strip()
        cards.append(
            f"<div class='card'><div class='n'>TOP {it.get('rank') or '—'}</div>"
            f"<div class='name'>{esc(short(it.get('title'), 80)) or '—'}</div>"
            f"<div class='meta'>发布于 {esc(it.get('date')) or '—'}</div>"
            f"<div class='g'>播放 {fmt(it.get('plays'))} ｜ 点赞 {fmt(it.get('likes'))}</div>"
            f"<div class='p'>爆款原因推测：{esc(reason)}</div>"
            f"<div class='p'>{link_line}</div>"
            "</div>")
    return (f"<div class='analysis-title'>🎯 爆款作品 TOP3 拆解（按播放数排序）</div>"
            f"<div class='viral-cards'>{''.join(cards)}</div>")


def build_diagnosis(analysis):
    analysis = analysis or {}
    text = str(analysis.get("diagnosis") or "").strip()
    if not text:
        return ""
    return ("<div class='analysis-title'>🔍 账号诊断总结</div>"
            f"<div class='diagnosis-card'><div class='p'>{esc(text)}</div>"
            "<div class='note'>以上为基于公开数据的 AI 分析与推测，仅供参考。</div></div>")


def build_scoring(analysis):
    """六维量化诊断板块（规则化离线计算，非 AI 推测）。"""
    analysis = analysis or {}
    scoring = analysis.get("scoring") or {}
    dimensions = scoring.get("dimensions") or []
    if not dimensions:
        return ""

    total = scoring.get("total", 0)
    grade = scoring.get("grade") or {}
    tier = scoring.get("tier") or {}
    tier_text = f"{tier.get('key')} {tier.get('label')} · 粉丝 {fmt(tier.get('fans'))}"
    weight_text = "维度权重：基础画像10% · 内容生产力15% · 互动健康度30% · 内容质量20% · 内容趋势15% · 粉丝质量10%"

    hero = (
        "<div class='score-hero'>"
        "<div><div class='score-big'>" + str(total) + "</div>"
        "<div class='score-unit'>/ 100</div></div>"
        "<div>"
        f"<div><span class='grade-chip'>{esc(grade.get('icon'))} {esc(grade.get('label'))}</span>"
        f"<span class='tier-chip'>{esc(tier_text)}</span></div>"
        f"<div class='score-sub'>{weight_text}</div>"
        "</div></div>")

    dim_rows = []
    for dim in dimensions:
        norm = float(dim.get("norm") or 0)
        bar = (f"<div class='bar-wrap'><div class='bar' style='width:{min(norm, 100):.0f}%'>"
               f"</div></div><span class='bar-pct'>{norm:.1f}%</span>")
        dim_rows.append(
            "<tr>"
            f"<td class='dim-name'>{esc(dim.get('name'))}"
            f"<span class='w'>（权重 {esc(dim.get('weight'))}）</span></td>"
            f"<td class='num'>{dim.get('score'):g}</td>"
            f"<td class='num'>{dim.get('full')}</td>"
            f"<td>{bar}</td>"
            f"<td class='comment'>{esc(dim.get('comment'))}</td>"
            "</tr>")
    dim_table = ("<div class='table-wrap'><table>"
                 "<colgroup><col style='width:180px;'><col style='width:70px;'>"
                 "<col style='width:90px;'><col style='width:150px;'><col></colgroup>"
                 "<thead><tr><th>维度</th><th>得分</th><th>有效满分</th><th>得分率</th><th>一句话评价</th></tr></thead>"
                 f"<tbody>{''.join(dim_rows)}</tbody></table></div>")

    cards = []
    for dim in dimensions:
        subs = []
        for it in dim.get("items") or []:
            note = str(it.get("note") or "")
            if not it.get("applied"):
                subs.append(
                    f"<div class='subitem excluded'><span class='sub-label'>{esc(it.get('label'))}</span>"
                    f"<span class='sub-right'><span class='sub-note'>{esc(note or '不计入')}</span>"
                    "<span class='sub-score'>不计入</span></span></div>")
            else:
                note_html = f"<span class='sub-note'>{esc(note)}</span>" if note else ""
                subs.append(
                    f"<div class='subitem'><span class='sub-label'>{esc(it.get('label'))}</span>"
                    f"<span class='sub-right'>{note_html}"
                    f"<span class='sub-score'>{it.get('score'):g}/{it.get('full')}</span></span></div>")
        full_meta = f"{dim.get('score'):g}/{dim.get('full')}"
        cards.append(
            f"<div class='dim-card'><div class='dim-card-title'>{esc(dim.get('name'))}"
            f"<span class='meta'>{full_meta} 分 · 权重 {esc(dim.get('weight'))}</span></div>"
            f"{''.join(subs)}</div>")

    alerts = scoring.get("alerts") or []
    level_cls = {"高危": "high", "中危": "mid", "低危": "low"}
    if alerts:
        chips = "".join(
            f"<span class='alert-chip {level_cls.get(a.get('level'), 'low')}'>"
            f"{esc(a.get('icon'))} {esc(a.get('name'))}（{esc(a.get('level'))}）：{esc(a.get('detail'))}"
            "</span>" for a in alerts)
        alerts_html = f"<div class='alerts'><div class='section-title'>⚠️ 风险预警</div>{chips}</div>"
    else:
        alerts_html = "<div class='alerts'><div class='section-title'>⚠️ 风险预警</div>" \
                      "<div class='empty'>无</div></div>"

    notes = scoring.get("notes") or []
    notes_html = ("<div class='scoring-notes'>"
                  + "".join(f"<div>{esc(n)}</div>" for n in notes) + "</div>") if notes else ""

    return ("<div class='analysis-title'>📐 六维量化诊断（规则化离线计算）</div>"
            f"{hero}{dim_table}<div class='subitems'>{''.join(cards)}</div>"
            f"{alerts_html}{notes_html}")


def build_profile_card(profile):
    profile = profile or {}
    name = esc(profile.get("name")) or "—"
    handle = esc(profile.get("handle")) or "—"
    url = profile.get("profileUrl") or ""
    link_cell = (f"<a href='{esc(url)}' target='_blank' rel='noopener'>打开主页 ↗</a>"
                 if url else "—")

    def pf(k, v, wide=False):
        cls = "pf pf-wide" if wide else "pf"
        return f"<div class='{cls}'><div class='k'>{k}</div><div class='v'>{v}</div></div>"

    cells = [
        pf("昵称", name),
        pf("TikTok号", f"@{handle}" if handle != "—" else "—"),
        pf("粉丝数", fmt(profile.get("fans"))),
        pf("关注数", fmt(profile.get("follow"))),
        pf("获赞总数", fmt(profile.get("liked"))),
        pf("作品数", fmt(profile.get("works"))),
        pf("地区", esc(profile.get("area")) or "—"),
        pf("认证", esc(profile.get("verify")) or "—"),
        pf("签名", esc(short(profile.get("signature"), 200)) or "—", wide=True),
        pf("主页链接", link_cell),
    ]
    return ("<div class='profile-card'><h2>👤 账号基础信息</h2>"
            f"<div class='profile-grid'>{''.join(cells)}</div></div>")


def build_stats(saved):
    cards = []
    profile = saved.get("profile") or {}
    if profile:
        cards.append(f"<div class='stat'><div class='v'>{fmt(profile.get('fans'))}</div>"
                     f"<div class='k'>粉丝数</div></div>")
        cards.append(f"<div class='stat'><div class='v'>{fmt(profile.get('liked'))}</div>"
                     f"<div class='k'>获赞总数</div></div>")
        cards.append(f"<div class='stat'><div class='v'>{fmt(profile.get('works'))}</div>"
                     f"<div class='k'>作品数</div></div>")
    works = saved.get("works") or {}
    witems = works.get("items") or []
    if witems:
        top = max((it.get("views") or 0) for it in witems)
        cards.append(f"<div class='stat'><div class='v'>{len(witems)} <em>条</em></div>"
                     f"<div class='k'>主页作品（本页）· 最高播放 {fmt(top)}</div></div>")
    favorites = saved.get("favorites") or {}
    fitems = favorites.get("items") or []
    if fitems:
        top = max((it.get("views") or 0) for it in fitems)
        cards.append(f"<div class='stat'><div class='v'>{len(fitems)} <em>条</em></div>"
                     f"<div class='k'>喜欢作品（本页）· 最高播放 {fmt(top)}</div></div>")
    return f"<div class='stats'>{''.join(cards)}</div>" if cards else ""


def report_filename(saved):
    meta = saved.get("meta") or {}
    profile = saved.get("profile") or {}
    handle = str(meta.get("handle") or profile.get("handle") or "latest")
    safe = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", handle).strip("_") or "latest"
    return f"TikTok账号深度分析_{safe}_报告.html"


def build_html(saved):
    meta = saved.get("meta") or {}
    profile = saved.get("profile") or {}
    name = esc(profile.get("name")) or ""
    handle = esc(profile.get("handle")) or ""
    title_account = ""
    if name and handle:
        title_account = f"{name} (@{handle})"
    elif name or handle:
        title_account = name or f"@{handle}"
    now = meta.get("generatedAt") or ""
    img_name = report_filename(saved)[:-5] + ".png"

    works = saved.get("works") or {}
    favorites = saved.get("favorites") or {}
    wpaging = works.get("paging") or {}
    fpaging = favorites.get("paging") or {}

    works_sub = f"本页 {len(works.get('items') or [])} 条 ｜ 已拉取共 {wpaging.get('apiTotal', '-')} 条"
    fav_sub = f"本页 {len(favorites.get('items') or [])} 条 ｜ hasMore：{fpaging.get('hasMore', '-')}"

    analysis = saved.get("analysis") or {}
    has_analysis = bool(analysis.get("viralTop3") or analysis.get("diagnosis"))
    has_scoring = bool((analysis.get("scoring") or {}).get("dimensions"))

    sections = []
    if "works" in (meta.get("types") or []):
        sections.append(
            f"<div class='section-title'>📊 主页作品榜（按发布时间倒序，{works_sub}）</div>"
            + build_works_table(works.get("items")))
        sections.append(build_viral_top3(analysis))
    if "favorites" in (meta.get("types") or []):
        sections.append(
            f"<div class='section-title'>🧡 喜欢作品榜（按发布时间倒序，{fav_sub}）</div>"
            + build_fav_table(favorites.get("items")))
    sections.append(build_scoring(analysis))
    sections.append(build_diagnosis(analysis))

    if has_analysis and has_scoring:
        footer_note = ("爆款原因与账号诊断为基于公开数据的 AI 分析与推测，"
                       "六维量化诊断为规则化离线计算，仅供参考。")
    elif has_analysis:
        footer_note = "爆款原因与账号诊断为基于公开数据的 AI 分析与推测，仅供参考。"
    else:
        footer_note = "深度分析与推测结论以对话输出为准。"

    profile_html = build_profile_card(profile) if profile else ""

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>TikTok账号深度分析 · {title_account or '报告'}</title>
<style>{CSS}</style>
</head>
<body>
<div class="report" id="report">
  <div class="header">
    <div class="logo">♪</div>
    <div>
      <h1>TikTok账号深度分析 · <span class="kw">{title_account or '—'}</span></h1>
      <div class="sub">数据来源：红狐数据 · 生成时间 {esc(now)}</div>
    </div>
  </div>

  <div class="export-bar">
    <button class="btn btn-primary" onclick="window.print()">🖨️ 导出 PDF</button>
    <button class="btn" id="downloadImgBtn" onclick="downloadAsImage()">📷 导出图片</button>
  </div>

  {build_stats(saved)}

  {profile_html}

  {''.join(sections)}

  <div class="footer">
    数据来源：红狐数据 · 生成时间 {esc(now)}<br>
    {footer_note}<br>
    支持浏览器一键导出 PDF / 高清图片
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
    parser = argparse.ArgumentParser(description="生成 TikTok账号深度分析 HTML 报告")
    parser.add_argument("--data", required=True, help="tiktok_account_analyzer.py --save-json 保存的 JSON 路径")
    parser.add_argument("--analysis", default=None,
                        help="AI 分析 JSON 路径（含 viralTop3、diagnosis 与六维评分 scoring，可选）")
    parser.add_argument("--output", default=None, help="HTML 输出路径")
    parser.add_argument("--no-open", action="store_true", help="生成后不自动打开浏览器")
    args = parser.parse_args()

    with open(args.data, encoding="utf-8") as f:
        saved = json.load(f)

    if args.analysis:
        with open(args.analysis, encoding="utf-8") as f:
            saved["analysis"] = json.load(f)

    meta = saved.get("meta") or {}
    out = args.output or os.path.join(OUTPUT_DIR, report_filename(saved))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_html(saved))
    print(f"[INFO] HTML 报告已生成：{out}")

    if not args.no_open:
        open_in_browser(out)


if __name__ == "__main__":
    main()
