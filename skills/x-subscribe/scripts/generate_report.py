#!/usr/bin/env python3
"""
X (Twitter) 订阅账号推文 HTML 日报生成脚本
用法：
    python3 generate_report.py --data /path/to/x_subscribe_data.json
    python3 generate_report.py --data data.json --output /path/to/report.html
X 平台风格（纯白底 + X 蓝 #1d9bf0），按账号分组展示推文时间线，支持一键导出 PDF / 高清图片。
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

_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(_SKILL_DIR, "output")


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def format_count(n):
    """与 subscribe.py 保持一致的数字可读化。"""
    try:
        n = int(float(str(n).replace(",", "")))
    except (ValueError, TypeError):
        return "—"
    if n >= 100_000_000:
        return f"{n / 100_000_000:.1f}亿"
    if n >= 10_000:
        w = n / 10_000
        if w >= 1000:
            return f"{w:,.0f}w"
        if w >= 100:
            return f"{w:.0f}w"
        s = f"{w:.1f}"
        return (s[:-2] if s.endswith(".0") else s) + "w"
    return f"{n:,}"


CSS = f"""
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
  background: #ffffff; color: {X_TEXT};
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
    "Helvetica Neue", "PingFang SC", "Microsoft YaHei", sans-serif;
  padding: 32px 16px;
}}
.report {{ max-width: 1200px; margin: 0 auto; }}
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
.btn:disabled {{ opacity: .6; cursor: default; }}
.stats {{ display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }}
.stat {{
  flex: 1; min-width: 140px; background: #fff; border: 1px solid {X_BORDER};
  border-radius: 16px; padding: 14px 18px;
}}
.stat .v {{ font-size: 22px; font-weight: 800; color: {X_BLUE}; }}
.stat .k {{ font-size: 12px; color: {X_SUB}; margin-top: 4px; }}
.notice {{
  background: {X_HOVER}; border: 1px solid {X_BORDER}; border-radius: 16px;
  padding: 14px 18px; font-size: 13px; color: {X_SUB}; line-height: 1.8;
  margin-bottom: 20px;
}}
.notice b {{ color: {X_TEXT}; }}
.account {{
  border: 1px solid {X_BORDER}; border-radius: 16px; overflow: hidden;
  background: #fff; margin-bottom: 18px;
}}
.acct-head {{
  display: flex; align-items: center; gap: 12px; padding: 14px 18px;
  border-bottom: 1px solid {X_BORDER}; background: {X_HOVER};
}}
.avatar {{ width: 44px; height: 44px; border-radius: 50%; object-fit: cover; flex: none; background: {X_BORDER}; }}
.avatar-ph {{
  width: 44px; height: 44px; border-radius: 50%; flex: none; background: {X_BLUE};
  color: #fff; font-size: 18px; font-weight: 800;
  display: flex; align-items: center; justify-content: center;
}}
.acct-name {{ font-size: 16px; font-weight: 800; }}
.acct-name a {{ color: {X_TEXT}; text-decoration: none; }}
.acct-name a:hover {{ color: {X_BLUE}; }}
.acct-handle {{ font-size: 13px; color: {X_SUB}; margin-top: 2px; }}
.verified {{ color: {X_BLUE}; font-size: 13px; margin-left: 4px; }}
.acct-meta {{ margin-left: auto; text-align: right; font-size: 12px; color: {X_SUB}; }}
.badge-count {{
  background: {X_BLUE}; color: #fff; border-radius: 999px; padding: 2px 10px;
  font-size: 12px; font-weight: 700;
}}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; table-layout: fixed; }}
thead th {{
  background: #fff; color: {X_SUB}; font-size: 12px; font-weight: 700;
  text-align: left; padding: 10px 12px; border-bottom: 1px solid {X_BORDER};
}}
thead th:nth-child(1) {{ width: auto; }}
thead th:nth-child(2) {{ width: 76px; text-align: right; }}
thead th:nth-child(3) {{ width: 70px; text-align: right; }}
thead th:nth-child(4) {{ width: 70px; text-align: right; }}
thead th:nth-child(5) {{ width: 70px; text-align: right; }}
thead th:nth-child(6) {{ width: 96px; }}
tbody td {{ padding: 12px; border-bottom: 1px solid {X_BORDER}; vertical-align: top; }}
tbody tr:last-child td {{ border-bottom: none; }}
tbody tr:hover {{ background: {X_HOVER}; }}
.tw-text {{ line-height: 1.55; word-break: break-word; }}
.tw-text a {{ color: {X_TEXT}; text-decoration: none; }}
.tw-text a:hover {{ color: {X_BLUE}; }}
.tw-tag {{
  display: inline-block; font-size: 11px; border-radius: 4px; padding: 0 6px;
  margin-right: 6px; vertical-align: 1px;
}}
.tag-rt {{ background: #e8f5fe; color: {X_BLUE}; }}
.tag-qt {{ background: #fff4e6; color: #d97706; }}
.tw-photo {{ width: 110px; height: 68px; object-fit: cover; border-radius: 8px; margin-top: 8px; border: 1px solid {X_BORDER}; }}
.num {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
.num.v {{ color: {X_SUB}; }}
.time {{ color: {X_SUB}; white-space: nowrap; font-size: 12px; }}
.folded {{
  border: 1px solid {X_BORDER}; border-radius: 16px; padding: 14px 18px;
  background: {X_HOVER}; font-size: 13px; color: {X_SUB}; line-height: 2; margin-bottom: 18px;
}}
.folded b {{ color: {X_TEXT}; }}
.folded a {{ color: {X_BLUE}; text-decoration: none; }}
.acct-hl {{ padding: 8px 12px; font-size: 12px; color: {X_SUB}; background: {X_HOVER}; border-top: 1px solid {X_BORDER}; }}
.acct-ai {{ padding: 10px 16px; font-size: 13px; line-height: 1.7; color: {X_TEXT}; background: #fbfdff; border-bottom: 1px solid {X_BORDER}; }}
.acct-ai b {{ color: {X_BLUE}; }}
.summary {{ margin-bottom: 18px; border: 1px solid {X_BORDER}; border-radius: 16px; padding: 14px 18px; background: {X_HOVER}; }}
.summary-h {{ font-size: 16px; font-weight: 800; margin-bottom: 10px; }}
.sum-item {{ font-size: 13px; line-height: 1.85; margin-bottom: 8px; }}
.sum-sample {{ color: {X_SUB}; font-size: 12px; }}
.footer {{ text-align: center; color: {X_SUB}; font-size: 12px; margin-top: 24px; line-height: 1.8; }}
@media print {{
  body {{ padding: 0; }}
  .export-bar {{ display: none; }}
  .account {{ break-inside: avoid; }}
}}
"""

JS = """
// 依赖 html2canvas（截图）+ jsPDF（生成 PDF），均由 CDN 引入；缺失时回退到浏览器打印。
function _el(){ return document.querySelector('.report'); }
function _bar(){ return document.querySelector('.export-bar'); }
function _name(ext){
  var t=(document.title||'X订阅日报').replace(/[\\/:*?"<>|]/g,'').trim();
  return (t||'X订阅日报')+'.'+ext;
}
function _download(blob, filename){
  var a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download=filename;
  document.body.appendChild(a);
  a.click();
  setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 4000);
}
function _busy(on, pdf){
  var bar=_bar(); if(!bar) return;
  var btns=bar.querySelectorAll('.btn');
  btns.forEach(function(b){
    if(on){ b.dataset.orig=b.textContent; b.disabled=true; b.textContent=(pdf?'正在生成 PDF…':'正在生成图片…'); }
    else { if(b.dataset.orig) b.textContent=b.dataset.orig; b.disabled=false; }
  });
}
function exportImg(){
  if(typeof html2canvas==='undefined'){ alert('图片导出组件未加载（需联网），已改用打印窗口，请在其中选择「另存为 PDF」。'); window.print(); return; }
  var el=_el(), bar=_bar();
  _busy(true,false);
  if(bar) bar.style.visibility='hidden';
  setTimeout(function(){
    html2canvas(el,{scale:2,useCORS:true,allowTaint:false,backgroundColor:'#ffffff',logging:false,windowWidth:el.scrollWidth}).then(function(canvas){
      if(bar) bar.style.visibility='';
      _busy(false,false);
      canvas.toBlob(function(blob){
        if(blob){ _download(blob,_name('png')); }
        else { alert('图片生成失败，请重试。'); }
      },'image/png');
    }).catch(function(e){
      if(bar) bar.style.visibility='';
      _busy(false,false);
      console.error(e);
      alert('图片导出失败：'+e+'\\n已改用打印窗口。');
      window.print();
    });
  },60);
}
function exportPDF(){
  if(typeof html2canvas==='undefined'||typeof window.jspdf==='undefined'){ alert('PDF 导出组件未加载（需联网），已改用打印窗口，请在其中选择「另存为 PDF」。'); window.print(); return; }
  var el=_el(), bar=_bar();
  _busy(true,true);
  if(bar) bar.style.visibility='hidden';
  setTimeout(function(){
    html2canvas(el,{scale:2,useCORS:true,allowTaint:false,backgroundColor:'#ffffff',logging:false,windowWidth:el.scrollWidth}).then(function(canvas){
      if(bar) bar.style.visibility='';
      _busy(false,true);
      var jsPDF=window.jspdf.jsPDF;
      var img=canvas.toDataURL('image/jpeg',0.95);
      var pdf=new jsPDF('p','mm','a4');
      var pw=pdf.internal.pageSize.getWidth(), ph=pdf.internal.pageSize.getHeight();
      var iw=pw, ih=canvas.height*pw/canvas.width;
      var y=0, left=ih;
      while(left>0){
        pdf.addImage(img,'JPEG',0,y,iw,ih);
        left-=ph;
        if(left>0){ pdf.addPage(); y-=ph; }
      }
      pdf.save(_name('pdf'));
    }).catch(function(e){
      if(bar) bar.style.visibility='';
      _busy(false,true);
      console.error(e);
      alert('PDF 导出失败：'+e+'\\n已改用打印窗口。');
      window.print();
    });
  },60);
}
"""


def tweet_row(t):
    text = esc(t.get("text") or "")
    url = t.get("tweetUrl") or ""
    tag = ""
    if t.get("isRetweet"):
        tag = "<span class='tw-tag tag-rt'>🔁 转发</span>"
    elif t.get("isQuote"):
        tag = "<span class='tw-tag tag-qt'>💬 引用</span>"
    link = f"<a href='{esc(url)}' target='_blank'>{text}</a>" if url else text
    photo = ""
    if t.get("photoUrl"):
        photo = (f"<br><img class='tw-photo' src='{esc(t['photoUrl'])}' "
                 f"onerror=\"this.style.display='none'\" alt=''>")
    return f"""
      <tr>
        <td class="tw-text">{tag}{link}{photo}</td>
        <td class="num v">{esc(t.get('viewCountFmt', '—'))}</td>
        <td class="num">{esc(t.get('likeCountFmt', '—'))}</td>
        <td class="num">{esc(t.get('retweetCountFmt', '—'))}</td>
        <td class="num">{esc(t.get('replyCountFmt', '—'))}</td>
        <td class="time">{esc(t.get('localTime', ''))}</td>
      </tr>"""


def account_block(a, acct_summary=None):
    name = esc(a.get("displayName") or a.get("screenName"))
    handle = esc(a.get("screenName"))
    url = esc(a.get("profileUrl") or f"https://x.com/{a.get('screenName')}")
    verified = "<span class='verified'>✔</span>" if a.get("verified") else ""
    avatar = a.get("avatar")
    if avatar:
        av = f"<img class='avatar' src='{esc(avatar)}' onerror=\"this.outerHTML='<div class=\\'avatar-ph\\'>{name[:1]}</div>'\" alt=''>"
    else:
        av = f"<div class='avatar-ph'>{name[:1]}</div>"
    fol = a.get("followers")
    fol_html = f"粉丝 {esc(format_count(fol))}" if fol else ""
    rows = "".join(tweet_row(t) for t in a.get("tweets", []))
    count = a.get("hitCount", len(a.get("tweets", [])))
    tweets = a.get("tweets", [])

    # 单账号 AI 总结：该账号今日推文主要什么主题、什么观点
    ai = (acct_summary or {}).get(a.get("screenName", "").lower())
    ai_line = ""
    if ai:
        parts = []
        if ai.get("theme"):
            parts.append(f"<b>主题</b> {esc(ai['theme'])}")
        if ai.get("viewpoint"):
            parts.append(f"<b>观点</b> {esc(ai['viewpoint'])}")
        if parts:
            ai_line = f"<div class='acct-ai'>📌 今日要点　" + "　·　".join(parts) + "</div>"

    hl = ""
    if tweets:
        top_tw = max(tweets, key=lambda t: (t.get("likeCount", 0) + t.get("retweetCount", 0) + t.get("replyCount", 0)))
        hl = (f"<div class='acct-hl'>🔥 本账号共 {count} 条，最热推文获 "
              f"{esc(top_tw.get('likeCountFmt', '—'))} 赞 / {esc(top_tw.get('retweetCountFmt', '—'))} 转发 / "
              f"{esc(top_tw.get('viewCountFmt', '—'))} 浏览</div>")
    return f"""
  <div class="account">
    <div class="acct-head">
      {av}
      <div>
        <div class="acct-name"><a href="{url}" target="_blank">{name}</a>{verified}</div>
        <div class="acct-handle">@{handle}</div>
      </div>
      <div class="acct-meta">
        <span class="badge-count">{count} 条推文</span>
        <div style="margin-top:4px">{fol_html}</div>
      </div>
    </div>
    {ai_line}
    <table>
      <thead>
        <tr><th>推文摘要</th><th class="num">浏览</th><th class="num">点赞</th><th class="num">转发</th><th class="num">回复</th><th>发布时间</th></tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    {hl}
  </div>"""


def ai_summary_block(ai):
    """整体 AI 主题总结：分析推文在说什么（按实际条数，不强制 5 条）。"""
    if not ai:
        return ""
    overall = ai.get("overall") or []
    if not overall:
        return ""
    items = ""
    for i, it in enumerate(overall, 1):
        accts = "、".join(f"<a href='https://x.com/{esc(a)}' target='_blank'>@{esc(a)}</a>"
                          for a in (it.get("accounts") or []))
        cnt = it.get("tweetCount")
        meta = f"<span class='sum-sample'>涉及 {cnt} 条推文 · 账号 {accts}</span>" if cnt else f"<span class='sum-sample'>涉及账号 {accts}</span>"
        items += (f"<div class='sum-item'><b>{i}. {esc(it.get('title') or '')}</b>"
                  f"<br>{esc(it.get('summary') or '')}"
                  f"<br>{meta}</div>")
    return f"<div class='summary'><div class='summary-h'>📝 今日主题总结</div>{items}</div>"


def build_html(result):
    meta = result.get("meta", {})
    accounts = result.get("accounts", [])
    mode = meta.get("mode", "daily")
    target_date = meta.get("targetDate", "")
    window_start = meta.get("windowStart", "")
    window_end = meta.get("windowEnd", "")
    window_label = f"{window_start} ~ {window_end}" if window_start else target_date
    mode_label = "首次订阅 · 各账号最新动态" if mode == "first" else f"每日发帖日报 · {window_label}"
    generated_at = meta.get("generatedAt", "")

    updated = [a for a in accounts if a.get("status") == "updated" and a.get("tweets")]
    no_yest = [a for a in accounts if a.get("status") == "no_update_yesterday"]
    no_7d = [a for a in accounts if a.get("status") == "no_update_7d"]
    errors = [a for a in accounts if a.get("status") == "error"]
    empty = [a for a in accounts if a.get("status") == "empty"]

    stats = f"""
  <div class="stats">
    <div class="stat"><div class="v">{meta.get('totalAccounts', len(accounts))}</div><div class="k">订阅账号</div></div>
    <div class="stat"><div class="v">{meta.get('updatedAccounts', len(updated))}</div><div class="k">有更新账号</div></div>
    <div class="stat"><div class="v">{meta.get('totalTweets', 0)}</div><div class="k">本次推文</div></div>
    <div class="stat"><div class="v">{target_date}</div><div class="k">窗口截止</div></div>
  </div>"""

    blocks = "".join(account_block(a) for a in updated)
    if not updated:
        blocks = "<div class='notice'>本次拉取暂无账号更新推文。</div>"

    ai = result.get("aiSummary") or {}
    acct_map = {item.get("screenName", "").lower(): item for item in (ai.get("accounts") or [])}
    if acct_map:
        blocks = "".join(account_block(a, acct_map) for a in updated)

    folded = ""
    fold_items = []
    if no_yest:
        names = "、".join(f"<a href='https://x.com/{esc(a['screenName'])}' target='_blank'>@{esc(a['screenName'])}</a>" for a in no_yest)
        fold_items.append(f"<b>昨日无更新（{len(no_yest)} 个）</b>：{names}")
    if no_7d:
        names = "、".join(f"<a href='https://x.com/{esc(a['screenName'])}' target='_blank'>@{esc(a['screenName'])}</a>" for a in no_7d)
        fold_items.append(f"<b>近7天无更新（{len(no_7d)} 个，已折叠）</b>：{names}")
    if empty:
        names = "、".join(f"@{esc(a['screenName'])}" for a in empty)
        fold_items.append(f"<b>无法获取推文（{len(empty)} 个）</b>：{names}")
    if errors:
        names = "、".join(f"@{esc(a['screenName'])}" for a in errors)
        fold_items.append(f"<b>拉取失败（{len(errors)} 个）</b>：{names}")
    if fold_items:
        folded = "<div class='folded'>" + "<br>".join(fold_items) + "</div>"

    summary_html = ai_summary_block(ai)

    notice = (f"<b>💡 报告说明</b><br>"
              f"每日早上 9:00 自动拉取订阅账号<b>昨日 9:00 至今日 9:00（近 24 小时）</b>发布的推文"
              f"（窗口：{esc(window_label)}）；推文时间已转换为本地时区，浏览/点赞/转发/回复为拉取时刻累计值。<br>"
              f"<b>🔁 转发 vs 💬 引用</b>：转发是纯原样转发（不带自己的话），引用是转发同时附上自己的评论。<br>"
              f"<b>为什么转发的点赞/回复常为空或 0？</b> 纯转发在 X 数据模型里不是一条独立推文，而是对原推文的「转发关系」，"
              f"X 不会给转发动作本身分配独立的点赞/回复/转发计数——这些互动数据归属原作者那条推文。因此本报告里 🔁 转发的互动列多为空/0；"
              f"而 💬 引用是带评论的新推文（有独立 ID），拥有完整的浏览/点赞/转发/回复数据。")

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>X(Twitter) 订阅账号推文日报 · {esc(target_date)}</title>
<style>{CSS}</style>
</head>
<body>
<div class="report">
  <div class="header">
    <div class="logo">𝕏</div>
    <div>
      <h1>X(Twitter) 订阅账号推文日报</h1>
      <div class="sub">{esc(mode_label)} · 生成于 {esc(generated_at)}</div>
    </div>
  </div>
  <div class="export-bar">
    <button class="btn" onclick="exportPDF()">导出 PDF</button>
    <button class="btn btn-primary" onclick="exportImg()">导出高清图片</button>
  </div>
  {stats}
  <div class="notice">{notice}</div>
  {blocks}
  {folded}
  {summary_html}
  <div class="footer">
    数据来源：红狐数据 · X(Twitter) 订阅账号推文日报<br>
    本报告由 Skill 自动生成 · {esc(generated_at)}
  </div>
</div>
<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js" crossorigin="anonymous"></script>
<script>{JS}</script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="X 订阅推文 HTML 日报生成")
    parser.add_argument("--data", required=True, help="fetch 输出的 JSON 数据文件路径")
    parser.add_argument("--output", default="", help="HTML 输出路径（默认 output/ 目录）")
    parser.add_argument("--no-open", action="store_true", help="生成后不自动打开浏览器")
    args = parser.parse_args()

    with open(args.data, encoding="utf-8") as f:
        result = json.load(f)

    # 合并 AI 语义总结（若存在）：与数据文件同目录的 x_subscribe_ai_summary.json
    ai_path = os.path.join(os.path.dirname(os.path.abspath(args.data)), "x_subscribe_ai_summary.json")
    if os.path.exists(ai_path):
        try:
            with open(ai_path, encoding="utf-8") as af:
                result["aiSummary"] = json.load(af)
        except Exception:  # noqa: BLE001
            pass

    meta = result.get("meta", {})
    target_date = meta.get("targetDate", datetime.now().strftime("%Y-%m-%d"))
    mode = meta.get("mode", "daily")
    prefix = "X订阅首次拉取" if mode == "first" else "X订阅日报"
    default_name = f"{prefix}_{target_date}.html"
    out_path = args.output or os.path.join(OUTPUT_DIR, default_name)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    html_str = build_html(result)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_str)

    print(f"[INFO] HTML 报告已生成：{out_path}")
    if not args.no_open:
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", out_path], check=False)
            elif sys.platform.startswith("win"):
                os.startfile(out_path)  # type: ignore[attr-defined]
            else:
                subprocess.run(["xdg-open", out_path], check=False)
        except Exception:  # noqa: BLE001
            pass


if __name__ == "__main__":
    main()
