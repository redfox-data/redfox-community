#!/usr/bin/env python3
"""
X (Twitter) 企业家影响力榜 HTML 报告生成脚本
用法：
    python generate_report.py --data entrepreneur_rank_data.json
    python generate_report.py --data rank.json --tweets entrepreneur_tweets.json --no-open
列版式：排名 / 账号名(含头衔) / 关联公司·职位 / 简介 / 国家地区 / 粉丝总数 / 日涨幅 / 增长量 / 综合影响力；
附「涨粉榜 TOP3」卡片与（可选）各账号近 30 天推文完整列表。
"""
import argparse
import html
import json
import os
import subprocess
import sys
from datetime import datetime

X_BLUE = "#1d9bf0"
X_TEXT = "#0f1419"
X_SUB = "#536471"
X_BORDER = "#eff3f4"
X_HOVER = "#f7f9f9"
X_GREEN = "#00ba7c"
X_RED = "#f4212e"

_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(_SKILL_DIR, "output")
MEDALS = {1: ("🥇", "#ffd700"), 2: ("🥈", "#c0c0c0"), 3: ("🥉", "#cd7f32")}


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def flag_emoji(cc):
    cc = (cc or "").upper()
    if len(cc) != 2 or not cc.isalpha():
        return ""
    return "".join(chr(0x1F1E6 + ord(ch) - 65) for ch in cc)


def growth_html(g):
    g = (g or "").strip()
    if not g:
        return "<span class='dim'>—</span>"
    cls = "up" if g.startswith("+") else ("down" if g.startswith("-") else "dim")
    return f"<span class='{cls}'>{esc(g)}</span>"


CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: #ffffff; color: {X_TEXT};
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
  padding: 32px 16px;
}}
.report {{ max-width: 1440px; margin: 0 auto; }}
.header {{ display: flex; align-items: center; gap: 14px; margin-bottom: 6px; }}
.logo {{
  width: 44px; height: 44px; border-radius: 50%; background: {X_TEXT};
  color: #fff; font-size: 26px; font-weight: 800;
  display: flex; align-items: center; justify-content: center; flex: none;
}}
.header h1 {{ font-size: 24px; font-weight: 800; letter-spacing: .2px; }}
.header .sub {{ color: {X_SUB}; font-size: 13px; margin-top: 4px; }}
.export-bar {{ text-align: right; margin: 10px 0 14px; }}
.btn {{
  border: 1px solid {X_BORDER}; background: #fff; color: {X_BLUE};
  border-radius: 999px; padding: 8px 18px; font-size: 13px; font-weight: 700;
  cursor: pointer; margin-left: 8px;
}}
.btn-primary {{ background: {X_BLUE}; border-color: {X_BLUE}; color: #fff; }}
.btn:hover {{ opacity: .85; }}
.stats {{ display: flex; gap: 12px; flex-wrap: nowrap; margin-bottom: 16px; }}
.stat {{
  flex: 1; min-width: 150px; background: #fff; border: 1px solid {X_BORDER};
  border-radius: 16px; padding: 14px 18px;
}}
.stat .v {{ font-size: 22px; font-weight: 800; color: {X_BLUE}; }}
.stat .k {{ font-size: 12px; color: {X_SUB}; margin-top: 4px; }}
.notice {{
  background: {X_HOVER}; border: 1px solid {X_BORDER}; border-radius: 16px;
  padding: 14px 18px; font-size: 13px; color: {X_SUB}; line-height: 1.8;
  margin-bottom: 16px;
}}
.notice b {{ color: {X_TEXT}; }}
.section-title {{ font-size: 17px; font-weight: 800; margin: 22px 0 10px; }}
.top3 {{ display: flex; gap: 12px; margin-bottom: 6px; }}
.top3 .card {{
  flex: 1; border: 1px solid {X_BORDER}; border-radius: 16px; padding: 14px 18px; background: #fff;
}}
.top3 .n {{ font-size: 13px; font-weight: 800; color: {X_SUB}; }}
.top3 .name {{ font-size: 16px; font-weight: 800; margin: 4px 0 2px; }}
.top3 .pos {{ font-size: 12px; color: {X_SUB}; margin-bottom: 6px; }}
.top3 .g {{ font-size: 15px; font-weight: 800; color: {X_GREEN}; }}
.top3 .p {{ font-size: 12px; color: {X_SUB}; margin-top: 2px; }}
.t3tweets {{ margin-top: 10px; padding-top: 8px; border-top: 1px solid {X_BORDER}; }}
.t3tweets .t3h {{ font-size: 11px; font-weight: 800; color: {X_SUB}; margin-bottom: 4px; }}
.t3tweets ul {{ margin: 0; padding-left: 16px; }}
.t3tweets li {{ font-size: 12px; color: {X_SUB}; line-height: 1.6; margin-bottom: 4px; word-break: break-word; }}
.t3tweets li a {{ color: {X_BLUE}; text-decoration: none; }}
.table-wrap {{
  border: 1px solid {X_BORDER}; border-radius: 16px; overflow: hidden; background: #fff;
}}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; }}
thead th:nth-child(1) {{ width: 52px; }}
thead th:nth-child(2) {{ width: 176px; }}
thead th:nth-child(3) {{ width: 168px; }}
thead th:nth-child(4) {{ width: 210px; }}
thead th:nth-child(5) {{ width: 84px; }}
thead th:nth-child(6) {{ width: 84px; }}
thead th:nth-child(7) {{ width: 76px; }}
thead th:nth-child(8) {{ width: 84px; }}
thead th:nth-child(9) {{ width: 76px; }}
thead th {{
  background: {X_HOVER}; color: {X_SUB}; font-size: 12px; font-weight: 700;
  text-align: left; padding: 12px 10px; border-bottom: 1px solid {X_BORDER};
}}
tbody td {{ padding: 12px 10px; border-bottom: 1px solid {X_BORDER}; vertical-align: top; }}
tbody tr:last-child td {{ border-bottom: none; }}
tbody tr:hover {{ background: {X_HOVER}; }}
.rank {{ font-weight: 800; font-size: 15px; white-space: nowrap; }}
.acct {{ display: flex; align-items: center; gap: 8px; min-width: 0; max-width: 100%; }}
.acct img {{ width: 28px; height: 28px; border-radius: 50%; object-fit: cover; flex: none; background: {X_BORDER}; }}
.acct a {{
  color: {X_BLUE}; text-decoration: none; font-weight: 700;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block;
}}
.acct a:hover {{ text-decoration: underline; }}
.acct-body {{ min-width: 0; max-width: 100%; }}
.acct .t {{
  color: {X_SUB}; font-size: 12px; margin-top: 2px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;
}}
.new {{ color: {X_GREEN}; font-size: 11px; font-weight: 800; }}
.pos {{ color: {X_SUB}; font-size: 12px; line-height: 1.6; word-break: break-word; }}
.bio {{ max-width: 100%; color: {X_SUB}; font-size: 12px; line-height: 1.6; }}
.bio .d {{ display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }}
.score {{ font-weight: 800; white-space: nowrap; }}
.up {{ color: {X_GREEN}; font-weight: 700; white-space: nowrap; }}
.down {{ color: {X_RED}; font-weight: 700; white-space: nowrap; }}
.dim {{ color: {X_SUB}; }}
.fans {{ font-weight: 700; white-space: nowrap; }}
.tweets {{ margin-top: 8px; }}
.tweet-card {{ border: 1px solid {X_BORDER}; border-radius: 16px; padding: 14px 18px; margin-bottom: 12px; background: #fff; }}
.tweet-card .who {{ font-size: 14px; font-weight: 800; }}
.tweet-card .who span {{ color: {X_SUB}; font-weight: 400; font-size: 12px; }}
.tweet-card ul {{ margin: 8px 0 0; padding-left: 18px; }}
.tweet-card li {{ font-size: 12.5px; color: {X_SUB}; line-height: 1.7; margin-bottom: 6px; }}
.tweet-card li a {{ color: {X_BLUE}; text-decoration: none; }}
.footer {{ margin-top: 18px; color: {X_SUB}; font-size: 12px; text-align: center; line-height: 1.8; }}
@media (max-width: 768px) {{ .stats, .top3 {{ flex-wrap: wrap; }} }}
@media print {{ .export-bar {{ display: none; }} body {{ padding: 0; }} }}
"""


def build_rows(items):
    rows = []
    for it in items:
        rank = it.get("rank")
        medal = MEDALS.get(rank)
        rank_cell = f"<span>{medal[0]} {rank}</span>" if medal else f"<span class='dim'>{rank}</span>"
        if it.get("isNew"):
            rank_cell += " <span class='new'>🆕</span>"

        name = esc(it.get("fullName"))
        url = esc(it.get("profileUrl"))
        pic = esc(it.get("pictureUrl"))
        avatar = f"<img src='{pic}' alt='' onerror=\"this.style.visibility='hidden'\">" if pic else ""
        title = esc(it.get("title"))
        acct = (f"<div class='acct'>{avatar}<div class='acct-body'>"
                f"<a href='{url}' target='_blank' rel='noopener' title='{name}'>{name}</a>"
                f"<div class='t' title='{title}'>{title or '—'}</div></div></div>")

        bio_full = esc(it.get("biography"))
        bio = f"<div class='bio'><div class='d' title='{bio_full}'>{bio_full or '—'}</div></div>"
        flag = flag_emoji(it.get("countryCode"))
        country = f"{flag} {esc(it.get('country'))}".strip() or "—"
        growth_abs = esc(it.get("growthAbsolute")) or "<span class='dim'>—</span>"
        try:
            score = f"{round(float(it.get('score')))}"
        except (TypeError, ValueError):
            score = "-"

        rows.append(
            "<tr>"
            f"<td class='rank'>{rank_cell}</td>"
            f"<td>{acct}</td>"
            f"<td class='pos'>{title or '—'}</td>"
            f"<td>{bio}</td>"
            f"<td>{country}</td>"
            f"<td class='fans'>{esc(it.get('xFollowersFmt'))}</td>"
            f"<td>{growth_html(it.get('growthPercentage'))}</td>"
            f"<td>{growth_abs}</td>"
            f"<td class='score'>{score}</td>"
            "</tr>")
    return "\n".join(rows)


def build_top3(meta, tweets_payload):
    tops = meta.get("topGrowth") or []
    if not tops:
        return ""
    by_rank = {}
    if tweets_payload:
        for a in tweets_payload.get("accounts") or []:
            by_rank[a.get("rank")] = a
    cards = []
    for i, g in enumerate(tops, 1):
        acct = by_rank.get(g.get("rank")) or {}
        orig = [t for t in (acct.get("tweets") or []) if not t.get("isRetweet")]
        latest = orig[:3]
        if latest:
            lis = "".join(
                f"<li>{esc((t.get('text') or '')[:120])} "
                f"<a href='{esc(t.get('url'))}' target='_blank' rel='noopener'>原文</a></li>"
                for t in latest)
            tweets_html = f"<div class='t3tweets'><div class='t3h'>最新 3 条推文</div><ul>{lis}</ul></div>"
        else:
            tweets_html = "<div class='t3tweets'><div class='t3h'>最新 3 条推文</div><div class='p'>近 30 天无原创推文</div></div>"
        cards.append(
            f"<div class='card'><div class='n'>TOP {i}</div>"
            f"<div class='name'>{esc(g.get('fullName'))}</div>"
            f"<div class='pos'>{esc(g.get('title')) or '—'}</div>"
            f"<div class='g'>单日涨粉 {esc(g.get('growthAbsolute'))}</div>"
            f"<div class='p'>日涨幅 {esc(g.get('growthPercentage'))}</div>"
            f"{tweets_html}</div>")
    return ("<div class='section-title'>🚀 今日涨粉榜 TOP3（按单日新增粉丝数排序，附近 30 天最新 3 条推文）</div>"
            f"<div class='top3'>{''.join(cards)}</div>")


def build_tweets(tweets_payload):
    if not tweets_payload:
        return ""
    accounts = tweets_payload.get("accounts") or []
    if not accounts:
        return ""
    blocks = []
    for a in accounts:
        lis = []
        for t in a.get("tweets") or []:
            text = esc((t.get("text") or "")[:280])
            link = f"<a href='{esc(t.get('url'))}' target='_blank' rel='noopener'>原文</a>"
            meta_bits = f"{esc(t.get('createdAtIso'))} · 👍 {t.get('likeCount')} · 🔁 {t.get('retweetCount')}"
            lis.append(f"<li>{text}<br>{meta_bits} · {link}</li>")
        blocks.append(
            f"<div class='tweet-card'><div class='who'>{esc(a.get('fullName'))} "
            f"<span>@{esc(a.get('handle'))} · 榜内第 {esc(a.get('rank'))} 名 · 近30天 {a.get('tweetCount')} 条</span></div>"
            f"<ul>{''.join(lis)}</ul></div>")
    return ("<div class='section-title'>💬 榜内账号近 30 天推文（话题总结原文依据）</div>"
            f"<div class='tweets'>{''.join(blocks)}</div>")


def build_html(payload, tweets_payload):
    meta = payload.get("meta", {})
    items = payload.get("items", [])
    scores = [float(i["score"]) for i in items if i.get("score") is not None]
    avg_score = f"{sum(scores) / len(scores):.1f}" if scores else "-"
    tops = meta.get("topGrowth") or []
    top_line = f"{tops[0]['fullName']} {tops[0]['growthAbsolute']}" if tops else "-"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    img_name = report_filename(meta)[:-5] + ".png"
    h1 = "X(Twitter)·企业家影响力榜"

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(h1)} · {esc(meta.get('rankDate'))}</title>
<style>{CSS}</style>
</head>
<body>
<div class="report" id="report">
  <div class="header">
    <div class="logo">𝕏</div>
    <div>
      <h1>{esc(h1)}</h1>
      <div class="sub">数据日期 {esc(meta.get('rankDate'))} · 第 {esc(meta.get('pageNum'))}/{esc(meta.get('pages'))} 页 · 每页 {esc(meta.get('pageSize'))} 条</div>
    </div>
  </div>

  <div class="export-bar">
    <button class="btn btn-primary" onclick="window.print()">🖨️ 导出 PDF</button>
    <button class="btn" id="downloadImgBtn" onclick="downloadAsImage()">📷 导出图片</button>
  </div>

  <div class="stats">
    <div class="stat"><div class="v">{esc(meta.get('total'))}</div><div class="k">上榜企业家（总）</div></div>
    <div class="stat"><div class="v">{esc(meta.get('pageNum'))}/{esc(meta.get('pages'))}</div><div class="k">当前页 / 总页数</div></div>
    <div class="stat"><div class="v">{avg_score}</div><div class="k">本页平均综合影响力</div></div>
    <div class="stat"><div class="v" style="font-size:15px;line-height:30px;">{esc(top_line)}</div><div class="k">本页单日涨粉王</div></div>
  </div>

  <div class="notice">
    <div>💡 <b>榜单说明</b>：{esc(meta.get('updateNote'))}，与实时数据存在差异。</div>
    <div>📐 <b>综合影响力</b>：结合粉丝数、互动量、曝光数等加权综合评估，满分 100。</div>
  </div>

  {build_top3(meta, tweets_payload)}

  <div class="section-title">📊 企业家影响力榜</div>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>排名</th><th>账号名</th><th>关联公司/职位</th><th>简介</th><th>国家/地区</th>
          <th>粉丝总数</th><th>粉丝日涨幅</th><th>粉丝增长量</th><th>综合影响力</th>
        </tr>
      </thead>
      <tbody>
{build_rows(items)}
      </tbody>
    </table>
  </div>

  {build_tweets(tweets_payload)}

  <div class="footer">
    数据来源：红狐数据 · 生成时间 {now}<br>
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


def report_filename(meta):
    return f"X企业家榜_{meta.get('rankDate', 'latest')}_第{meta.get('pageNum', 1)}页.html"


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
    parser = argparse.ArgumentParser(description="生成 X 企业家影响力榜 HTML 报告")
    parser.add_argument("--data", required=True, help="fetch_rank.py 输出的 JSON 路径")
    parser.add_argument("--tweets", default=None, help="fetch_tweets.py 输出的推文 JSON（可选）")
    parser.add_argument("--output", default=None, help="HTML 输出路径")
    parser.add_argument("--no-open", action="store_true", help="生成后不自动打开浏览器")
    args = parser.parse_args()

    with open(args.data, encoding="utf-8") as f:
        payload = json.load(f)
    tweets_payload = None
    if args.tweets and os.path.exists(args.tweets):
        with open(args.tweets, encoding="utf-8") as f:
            tweets_payload = json.load(f)

    meta = payload.get("meta", {})
    out = args.output or os.path.join(OUTPUT_DIR, report_filename(meta))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_html(payload, tweets_payload))
    print(f"[INFO] HTML 报告已生成：{out}")

    if not args.no_open:
        open_in_browser(out)


if __name__ == "__main__":
    main()
