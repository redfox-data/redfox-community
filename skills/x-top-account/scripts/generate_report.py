#!/usr/bin/env python3
"""
X (Twitter) 热门账号榜 HTML 报告生成脚本
用法：
    python generate_report.py --data /path/to/x_top_account_data.json
    python generate_report.py --data data.json --output /path/to/report.html
X 平台风格（纯白底 + X 蓝 #1d9bf0），支持一键导出 PDF / 高清图片。
"""
import argparse
import html
import json
import os
import subprocess
import sys
from datetime import datetime

# X 平台视觉规范
X_BLUE = "#1d9bf0"
X_TEXT = "#0f1419"
X_SUB = "#536471"
X_BORDER = "#eff3f4"
X_HOVER = "#f7f9f9"
X_GREEN = "#00ba7c"
X_RED = "#f4212e"

# HTML 报告默认输出目录：skill 目录下的 output/（运行时自动创建）
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


def score_fmt(score):
    try:
        return f"{round(float(score))}/100"
    except (TypeError, ValueError):
        return "-"


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
.table-wrap {{
  border: 1px solid {X_BORDER}; border-radius: 16px; overflow: hidden;
  background: #fff;
}}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; }}
thead th:nth-child(1) {{ width: 56px; }}
thead th:nth-child(2) {{ width: 186px; }}
thead th:nth-child(3) {{ width: 194px; }}
thead th:nth-child(4) {{ width: 84px; }}
thead th:nth-child(5) {{ width: 128px; }}
thead th:nth-child(6) {{ width: 84px; }}
thead th:nth-child(7) {{ width: 76px; }}
thead th:nth-child(8) {{ width: 84px; }}
thead th:nth-child(9) {{ width: 150px; }}
thead th:nth-child(10) {{ width: 150px; }}
thead th {{
  background: {X_HOVER}; color: {X_SUB}; font-size: 12px; font-weight: 700;
  text-align: left; padding: 12px 10px; border-bottom: 1px solid {X_BORDER};
}}
tbody td {{ padding: 12px 10px; border-bottom: 1px solid {X_BORDER}; vertical-align: top; }}
tbody tr:last-child td {{ border-bottom: none; }}
tbody tr:hover {{ background: {X_HOVER}; }}
.rank {{ font-weight: 800; font-size: 15px; white-space: nowrap; }}
.acct {{ display: flex; align-items: center; gap: 8px; min-width: 0; max-width: 100%; }}
.acct img {{
  width: 28px; height: 28px; border-radius: 50%; object-fit: cover; flex: none;
  background: {X_BORDER};
}}
.acct a {{
  color: {X_BLUE}; text-decoration: none; font-weight: 700;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: block;
}}
.acct a:hover {{ text-decoration: underline; }}
.bio {{ max-width: 100%; color: {X_SUB}; font-size: 12px; line-height: 1.6; }}
.acct-body {{ min-width: 0; max-width: 100%; }}
.acct .t {{
  color: {X_SUB}; font-size: 12px; margin-top: 2px;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%;
}}
.bio .d {{
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}}
.ind {{ color: {X_SUB}; font-size: 12px; line-height: 1.6; word-break: break-word; }}
.score {{ font-weight: 800; white-space: nowrap; }}
.up {{ color: {X_GREEN}; font-weight: 700; white-space: nowrap; }}
.down {{ color: {X_RED}; font-weight: 700; white-space: nowrap; }}
.dim {{ color: {X_SUB}; }}
.fans {{ font-weight: 700; white-space: nowrap; }}
.nets {{ margin: 0; padding-left: 16px; color: {X_SUB}; font-size: 12px; line-height: 1.7; word-break: break-word; }}
.nets a {{ color: {X_SUB}; text-decoration: none; }}
.nets a:hover {{ color: {X_BLUE}; }}
.tags {{ color: {X_SUB}; font-size: 12px; max-width: 100%; word-break: break-word; }}
.footer {{
  margin-top: 18px; color: {X_SUB}; font-size: 12px; text-align: center; line-height: 1.8;
}}
@media (max-width: 768px) {{
  .stats {{ flex-wrap: wrap; }}
}}
@media print {{
  .export-bar {{ display: none; }}
  body {{ padding: 0; }}
  .table-wrap {{ box-shadow: none; }}
}}
"""


def build_rows(items):
    rows = []
    for it in items:
        rank = it.get("rank")
        medal = MEDALS.get(rank)
        rank_cell = f"<span>{medal[0]} {rank}</span>" if medal else f"<span class='dim'>{rank}</span>"

        name = esc(it.get("fullName"))
        url = esc(it.get("profileUrl"))
        pic = esc(it.get("pictureUrl"))
        avatar = f"<img src='{pic}' alt='' onerror=\"this.style.visibility='hidden'\">" if pic else ""
        title = esc(it.get("title"))
        acct = (f"<div class='acct'>{avatar}<div class='acct-body'>"
                f"<a href='{url}' target='_blank' rel='noopener' title='{name}'>{name}</a>"
                f"<div class='t' title='{title}'>{title or '—'}</div></div></div>")

        bio_full = esc(it.get("biography"))
        bio = f"<div class='bio'><div class='d' title='{bio_full}'>{bio_full}</div></div>"

        flag = flag_emoji(it.get("countryCode"))
        country = f"{flag} {esc(it.get('country'))}".strip()

        inds = it.get("industries") or []
        ind = esc(" / ".join(inds[:2])) if inds else "<span class='dim'>—</span>"

        nets = it.get("otherNetworks") or []
        if nets:
            lis = "".join(
                f"<li><a href='{esc(n.get('profileUrl'))}' target='_blank' rel='noopener'>"
                f"{esc(n.get('network'))} {esc(n.get('followersFmt') or n.get('followers'))}</a></li>"
                for n in nets)
            nets_cell = f"<ul class='nets'>{lis}</ul>"
        else:
            nets_cell = "<span class='dim'>—</span>"

        topics = it.get("topics") or it.get("cause") or ""
        tags = esc(topics) if topics else "<span class='dim'>—</span>"

        rows.append(
            "<tr>"
            f"<td class='rank'>{rank_cell}</td>"
            f"<td>{acct}</td>"
            f"<td>{bio}</td>"
            f"<td>{country}</td>"
            f"<td class='ind'>{ind}</td>"
            f"<td class='score'>{score_fmt(it.get('score'))}</td>"
            f"<td>{growth_html(it.get('growthPercentage'))}</td>"
            f"<td class='fans'>{esc(it.get('xFollowersFmt'))}</td>"
            f"<td>{nets_cell}</td>"
            f"<td class='tags'>{tags}</td>"
            "</tr>")
    return "\n".join(rows)


def build_html(payload):
    meta = payload.get("meta", {})
    items = payload.get("items", [])

    scores = [float(i["score"]) for i in items if i.get("score") is not None]
    avg_score = f"{sum(scores) / len(scores):.1f}" if scores else "-"
    growths = []
    for i in items:
        g = (i.get("growthPercentage") or "").replace("%", "").replace("+", "")
        try:
            growths.append((float(g), i.get("fullName")))
        except ValueError:
            pass
    top_growth = f"+{max(growths)[0]}% · {max(growths)[1]}" if growths else "-"

    rows = build_rows(items)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    img_name = esc(report_filename(meta)[:-5] + ".png")

    # 标题：X(Twitter)·{行业}·热门{性别}账号榜；行业/性别为 all 时省略对应字段
    gender_zh = {"male": "男", "female": "女"}.get(meta.get("gender", "all"), "")
    cat_part = f"·{meta.get('categoryLabel')}" if meta.get("category") != "all" else ""
    rank_part = f"热门{gender_zh}性账号榜" if gender_zh else "热门账号榜"
    h1 = f"X(Twitter){cat_part}·{rank_part}"

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
      <div class="sub">数据日期 {esc(meta.get('rankDate'))} · 第 {esc(meta.get('pageNum'))}/{esc(meta.get('pages'))} 页 · 每页 {esc(meta.get('pageSize'))} 条 · 影响力评分：结合粉丝数、互动量、曝光数等加权综合评估</div>
    </div>
  </div>

  <div class="export-bar">
    <button class="btn btn-primary" onclick="window.print()">🖨️ 导出 PDF</button>
    <button class="btn" id="downloadImgBtn" onclick="downloadAsImage()">📷 导出图片</button>
  </div>

  <div class="stats">
    <div class="stat"><div class="v">{esc(meta.get('total'))}</div><div class="k">上榜账号（总）</div></div>
    <div class="stat"><div class="v">{esc(meta.get('pageNum'))}/{esc(meta.get('pages'))}</div><div class="k">当前页 / 总页数</div></div>
    <div class="stat"><div class="v">{avg_score}</div><div class="k">本页平均影响力评分</div></div>
    <div class="stat"><div class="v" style="font-size:15px;line-height:30px;">{esc(top_growth)}</div><div class="k">本页最高日涨幅</div></div>
  </div>

  <div class="notice">
    <div>💡 <b>榜单说明</b>：{esc(meta.get('updateNote'))}，与实时数据存在差异。</div>
    <div>📐 <b>影响力评分</b>：结合粉丝数、互动量、曝光数等加权综合评估，满分 100。</div>
  </div>

  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>排名</th><th>账号名</th><th>账号简介</th><th>国家/地区</th><th>主行业</th>
          <th>影响力评分</th><th>粉丝数日涨幅</th><th>X粉丝数</th><th>其他平台粉丝数</th><th>专题标签</th>
        </tr>
      </thead>
      <tbody>
{rows}
      </tbody>
    </table>
  </div>

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


def report_filename(meta):
    """报告文件名：X账号榜_性别_分类_日期.html；all 展示为全部性别/全部分类。"""
    gender = meta.get("gender", "all")
    gender_part = "全部性别" if gender == "all" else (meta.get("genderLabel") or gender)
    category = meta.get("category", "all")
    category_part = "全部分类" if category == "all" else (meta.get("categoryLabel") or category)
    return f"X账号榜_{gender_part}_{category_part}_{meta.get('rankDate', 'latest')}.html"


def main():
    parser = argparse.ArgumentParser(description="生成 X 热门账号榜 HTML 报告")
    parser.add_argument("--data", required=True, help="fetch_rank.py 输出的 JSON 路径")
    parser.add_argument("--output", default=None, help="HTML 输出路径")
    parser.add_argument("--no-open", action="store_true", help="生成后不自动打开浏览器")
    args = parser.parse_args()

    with open(args.data, encoding="utf-8") as f:
        payload = json.load(f)
    meta = payload.get("meta", {})

    out = args.output or os.path.join(OUTPUT_DIR, report_filename(meta))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

    with open(out, "w", encoding="utf-8") as f:
        f.write(build_html(payload))
    print(f"[INFO] HTML 报告已生成：{out}")

    if not args.no_open:
        open_in_browser(out)


if __name__ == "__main__":
    main()
