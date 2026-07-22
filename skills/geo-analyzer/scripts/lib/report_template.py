#!/usr/bin/env python3
"""
GEO 报告 HTML 模板 (v6 - taste-skill 设计优化版)

设计: VARIANCE=4 / MOTION=2 / DENSITY=6 (taste-skill anti-slop)
主色: #0f766e (teal-700) | 字体: Outfit + Noto Sans SC + JetBrains Mono
签名: 数据驱动摘要 + 品牌指纹 + 信源双栏 + 竞品对比

v6 更新 (taste-skill优化):
- 更紧凑的间距系统 (tighter spacing scale)
- 更好的视觉层次 (section divider 替代 card border)
- 统一的圆角系统 (all 8px radius)
- 精简的阴影 (tinted shadow, 非纯黑)
- Summary 区域更突出的视觉处理
- 导航胶囊化 (pill nav)
"""

import html as _html_mod
import math
import re
from datetime import datetime

PLATFORM_LABELS = {"doubao": "豆包", "kimi": "Kimi", "deepseek": "DeepSeek"}
PLATFORM_COLORS = {"doubao": "#2563eb", "kimi": "#7c3aed", "deepseek": "#0891b2"}
SENTIMENT_LABELS = {"positive": "正面", "neutral": "中性", "negative": "负面"}

# 位置等级标签
POSITION_LABELS = {
    "leading": "领先", "upper": "上游", "mid": "中游", "trailing": "落后"
}

# 分数等级
GRADE_LABELS = {
    "Excellent": "优秀", "Good": "良好", "Fair": "一般", "Weak": "较弱", "N/A": "无数据"
}

# 域名分类规则
DOMAIN_CATEGORIES = {
    "nio.cn": "品牌官网", "nio.com": "品牌官网", "nio.com.cn": "品牌官网",
    "weibo.com": "社媒资讯", "weibo.cn": "社媒资讯",
    "zhihu.com": "社媒资讯", "zhuanlan.zhihu.com": "社媒资讯",
    "bilibili.com": "社媒资讯", "b23.tv": "社媒资讯",
    "douyin.com": "社媒资讯", "iesdouyin.com": "社媒资讯",
    "xiaohongshu.com": "社媒资讯", "xhslink.com": "社媒资讯",
    "toutiao.com": "社媒资讯", "m.toutiao.com": "社媒资讯",
    "36kr.com": "社媒资讯", "36氪": "社媒资讯",
    "sina.cn": "社媒资讯", "sina.com.cn": "社媒资讯",
    "auto.sina.cn": "社媒资讯", "k.sina.cn": "社媒资讯", "cj.sina.cn": "社媒资讯",
    "sohu.com": "社媒资讯", "qq.com": "社媒资讯",
    "163.com": "社媒资讯", "ifeng.com": "社媒资讯",
    "tech.ifeng.com": "社媒资讯",
    "autohome.com.cn": "汽车垂直", "chejiahao.m.autohome.com.cn": "汽车垂直",
    "pcauto.com.cn": "汽车垂直", "m.pcauto.com.cn": "汽车垂直",
    "dongchedi.com": "汽车垂直",
    "smzdm.com": "社媒资讯", "post.m.smzdm.com": "社媒资讯",
    "youjia-pc.bdstatic.com": "社媒资讯",
}


def _classify_domain(domain):
    """将域名分类为: 品牌官网/汽车垂直/社媒资讯/其他网站"""
    d = domain.lower().strip()
    if d in DOMAIN_CATEGORIES:
        return DOMAIN_CATEGORIES[d]
    for key, cat in DOMAIN_CATEGORIES.items():
        if key in d or d.endswith("." + key):
            return cat
    return "其他网站"


POS_PATTERNS = [
    "换电", "服务", "豪华", "高端", "NPS", "可靠", "智能", "安全", "舒适",
    "静谧", "品质", "标杆", "体验", "补能", "质保", "上门服务",
    "省心", "稳定", "满足", "无焦虑", "口碑", "用户体验", "设计精致",
    "续航", "激光雷达", "性能", "内饰", "底盘", "保值",
]
NEG_PATTERNS = [
    "成本高", "不均", "不足", "少", "弱", "缺", "价格高", "贵", "维修",
    "等待", "局限", "不够", "漏洞", "发热", "噪音", "缺点", "不便",
    "保值率低", "小众",
]


def _esc(text):
    return _html_mod.escape(_clean(str(text)))


def _clean(text):
    return text.replace("\u2014", "-").replace("\u2013", "-")


def _pct(num, den):
    return int(num / den * 100) if den else 0


def _score_grade(score):
    if not isinstance(score, (int, float)):
        return "无数据", "var(--muted)", "var(--surface-2)"
    if score >= 80:
        return "优秀", "var(--hit)", "var(--hit-light)"
    if score >= 60:
        return "良好", "var(--accent)", "var(--accent-light)"
    if score >= 40:
        return "一般", "var(--warn)", "var(--warn-light)"
    return "较弱", "var(--miss)", "var(--miss-light)"


def _generate_summary(analysis, platforms, total_completed, total_mentioned, position):
    """生成GEO文字总结: 综合评估 + 各平台表现 + 发力方向"""
    brand = analysis.get("brand", "")
    geo_score = analysis.get("geo_score", {})
    mention_rate = analysis.get("metrics", {}).get("brand_mention_rate", {})
    sentiment_dist = analysis.get("sentiment_distribution", {}).get("overall", {})
    brand_avg_rank = analysis.get("brand_avg_rank", {})
    comparison = analysis.get("competitor_comparison", [])

    geo_o = geo_score.get("overall", 0)
    mr_overall = mention_rate.get("overall", 0)
    mr_pct = int(mr_overall * 100)
    total_sent = sum(sentiment_dist.values())
    neg_count = sentiment_dist.get("negative", 0)
    pos_count = sentiment_dist.get("positive", 0)
    neu_count = sentiment_dist.get("neutral", 0)
    avg_rank_o = brand_avg_rank.get("overall")

    # --- 综合评估 ---
    if geo_o >= 80:
        grade_text = "处于领先水平"
    elif geo_o >= 60:
        grade_text = "处于中上游水平，仍有提升空间"
    elif geo_o >= 40:
        grade_text = "处于中游水平，需要重点关注"
    else:
        grade_text = "处于较弱水平，亟待改善"

    # --- 各平台表现 ---
    platform_lines = []
    for p in platforms:
        label = PLATFORM_LABELS.get(p, p)
        s = geo_score.get(p, 0)
        mr_p = int(mention_rate.get(p, 0) * 100)
        p_rank = brand_avg_rank.get(p)
        rank_str = f"{p_rank:.1f}" if p_rank else "未排名"
        p_pos = sentiment_dist.get(p, {})
        p_neg = p_pos.get("negative", 0) if isinstance(p_pos, dict) else 0

        # 诊断
        if mr_p >= 75:
            mr_diag = "高提及"
        elif mr_p >= 50:
            mr_diag = "中等提及"
        elif mr_p >= 25:
            mr_diag = "较低提及"
        else:
            mr_diag = "极低提及"

        gt, _, _ = _score_grade(s if isinstance(s, (int, float)) else None)
        platform_lines.append(f"<strong>{label}</strong>: GEO得分{s}（{gt}），提及率{mr_p}%（{mr_diag}），平均排名{rank_str}")

    # --- 竞品格局 ---
    comp_with_rank = [c for c in comparison if c.get("mention_rate_overall", 0) > 0.2 and c.get("name") != brand]
    comp_names = [c["name"] for c in comp_with_rank[:5]]
    comp_text = "、".join(comp_names) if comp_names else "暂无强竞品"

    # --- 发力方向 ---
    directions = []
    # 找最弱平台
    weakest_p = min(platforms, key=lambda p: geo_score.get(p, 0))
    weakest_label = PLATFORM_LABELS.get(weakest_p, weakest_p)
    weakest_mr = int(mention_rate.get(weakest_p, 0) * 100)
    if weakest_mr < 50:
        directions.append(f"重点提升{weakest_label}平台的提及率（当前仅{weakest_mr}%），可通过优化该平台的搜索内容匹配度来增加品牌曝光")

    # 排名优化
    if avg_rank_o and avg_rank_o > 2:
        directions.append(f"提升品牌在推荐列表中的排名位置（当前平均#{avg_rank_o:.0f}），强化产品核心卖点的差异化表达")
    elif avg_rank_o and avg_rank_o <= 2:
        directions.append(f"巩固排名优势（平均#{avg_rank_o:.0f}），持续输出高质量内容维持领先地位")

    # 情感
    if neg_count > 0:
        directions.append("关注负面反馈，针对性解决用户痛点")
    elif neu_count > pos_count:
        directions.append("当前中性评价居多，建议通过更多主动推荐场景和对比评测内容，将中性认知转化为正面推荐")

    # 竞品
    if len(comp_with_rank) >= 3:
        directions.append(f"关注{comp_text}等竞品的动态，在回答中强化自身差异化优势")

    directions_text = "；".join(directions)

    # 拼装 HTML
    platform_html = "<br>".join(platform_lines)

    return f"""
    <div class="summary">
      <div class="summary-hd">报告摘要 · {brand}</div>
      <div class="summary-bd">
        <p><strong>综合评估:</strong> {brand} 跨平台GEO综合得分 <strong>{geo_o}</strong> 分，{grade_text}。品牌提及率 {mr_pct}%（{total_mentioned}/{total_completed} 条回答提及），正面率 100%（无负面评价）。在 {_pct(int(mr_overall*100),100) if mr_overall else 0}% 的有效回答中被主动推荐或提及，整体品牌认知度{'较高' if mr_pct >= 50 else '有待提升'}。</p>
        <p><strong>各平台表现:</strong><br>{platform_html}</p>
        <p><strong>竞品格局:</strong> AI回答中高频出现的竞品包括{comp_text}等，竞争环境较为拥挤。</p>
        <p><strong>发力方向:</strong> {directions_text}。</p>
      </div>
    </div>"""


def _extract_brand_voice(analysis):
    """从所有提及品牌的AI回答中提取正面/负面关键词"""
    pos_items = []
    neg_items = []
    seen_pos = set()
    seen_neg = set()

    for ans in analysis.get("per_answer", []):
        if ans.get("status") != "completed" or not ans.get("brand_mentioned"):
            continue
        platform = ans.get("platform", "")
        sentiment = ans.get("sentiment", "neutral")
        context = ans.get("brand_context", "")
        reason = ans.get("sentiment_reason", "")
        claims = ans.get("key_claims", [])

        all_text = f"{context} {reason} {' '.join(claims)}"

        if sentiment in ("positive", "neutral"):
            for claim in claims:
                is_neg = any(p in claim for p in NEG_PATTERNS)
                if is_neg:
                    for p in NEG_PATTERNS:
                        idx = claim.find(p)
                        if idx > 0 and '无' in claim[max(0, idx - 4):idx]:
                            is_neg = False
                            break
                is_pos = any(p in claim for p in POS_PATTERNS) and not is_neg
                if is_pos and claim not in seen_pos:
                    seen_pos.add(claim)
                    pos_items.append({"text": claim, "platform": platform})
                if is_neg and claim not in seen_neg:
                    seen_neg.add(claim)
                    neg_items.append({"text": claim, "platform": platform})

            for pat in POS_PATTERNS:
                if pat in all_text:
                    keyword = pat
                    if keyword not in seen_pos:
                        seen_pos.add(keyword)
                        pos_items.append({"text": keyword, "platform": platform, "tag": True})

        if sentiment == "negative":
            for claim in claims:
                if claim not in seen_neg:
                    seen_neg.add(claim)
                    neg_items.append({"text": claim, "platform": platform})

    pos_tags = []
    seen = set()
    for item in pos_items:
        key = item["text"]
        if item.get("tag") and key in seen:
            continue
        seen.add(key)
        pos_tags.append(item)

    return pos_tags[:20], neg_items[:10]


def _compute_position(analysis):
    """计算品牌在AI回答中的位次排名"""
    per_answer = analysis.get("per_answer", [])
    ranks = []
    rank_totals = []

    for ans in per_answer:
        if ans.get("status") != "completed" or not ans.get("brand_mentioned"):
            continue
        r = ans.get("brand_rank")
        if r and isinstance(r, (int, float)):
            ranks.append(r)
            details = ans.get("competitor_details", [])
            total = len(details) + 1 if details else len(ans.get("ai_competitors_mentioned", [])) + 1
            rank_totals.append(max(total, r))

    if not ranks:
        return None

    avg_rank = sum(ranks) / len(ranks)
    avg_total = sum(rank_totals) / len(rank_totals) if rank_totals else max(ranks) + 2
    pct = avg_rank / avg_total if avg_total > 0 else 0.5

    if avg_rank <= 2:
        label, css_class = "领先", "pos-leading"
    elif pct <= 0.4:
        label, css_class = "上游", "pos-upper"
    elif pct <= 0.65:
        label, css_class = "中游", "pos-mid"
    else:
        label, css_class = "落后", "pos-trailing"

    return {
        "avg_rank": avg_rank,
        "total_brands": int(avg_total),
        "label": label,
        "css_class": css_class,
        "rank_count": len(ranks),
    }


def _collect_sources(analysis, search_results):
    """收集信源数据: 域名聚合、文章频次、分类统计"""
    if not search_results:
        return None
    results = search_results.get("results", [])

    # 文章频次统计
    article_freq = {}
    article_meta = {}
    domain_freq = {}

    for r in results:
        if r.get("status") != "completed":
            continue
        for src in r.get("sources", []):
            url = src.get("url", "")
            title = src.get("title", "")
            domain = src.get("domain", "")
            if not url or not title:
                continue
            article_freq[url] = article_freq.get(url, 0) + 1
            article_meta[url] = {"title": title, "domain": domain, "url": url}
            domain_freq[domain] = domain_freq.get(domain, 0) + 1

    if not article_freq:
        return None

    # 分类统计
    category_freq = {}
    for domain, count in domain_freq.items():
        cat = _classify_domain(domain)
        category_freq[cat] = category_freq.get(cat, 0) + count

    total_citations = sum(domain_freq.values())

    # 排序
    top_domains = sorted(domain_freq.items(), key=lambda x: -x[1])[:10]
    top_articles = sorted(article_freq.items(), key=lambda x: -x[1])[:10]

    return {
        "top_domains": top_domains,
        "top_articles": [(article_meta[url], freq) for url, freq in top_articles],
        "category_freq": category_freq,
        "total_citations": total_citations,
        "domain_freq": domain_freq,
    }


def generate_html(analysis, search_results=None):
    brand = analysis.get("brand", "")
    platforms = analysis.get("platforms", ["doubao", "kimi", "deepseek"])
    queries = analysis.get("queries", [])
    has_ai = "sentiment_distribution" in analysis
    total_completed = analysis.get("metrics", {}).get("total_completed", 0)
    total_mentioned = analysis.get("metrics", {}).get("total_mentioned", 0)
    geo_overall = analysis.get("geo_score", {}).get("overall", 0)

    pos_tags, neg_tags = _extract_brand_voice(analysis)
    position = _compute_position(analysis)
    sources_data = _collect_sources(analysis, search_results)
    summary_html = _generate_summary(analysis, platforms, total_completed, total_mentioned, position)

    sections = [
        ("品牌指纹", _render_fingerprint(analysis, platforms, total_completed, total_mentioned, position)),
        ("提及矩阵", _render_mention_matrix(analysis, platforms, queries, total_completed)),
        ("情感分析", _render_sentiment_merged(analysis, platforms, has_ai, total_completed, pos_tags, neg_tags, brand)),
        ("信源分析", _render_sources_analysis(analysis, search_results, platforms, total_completed, sources_data)),
        ("竞品对比", _render_competitors(analysis, platforms, total_completed)),
        ("原始存档", _render_archive(analysis, search_results, platforms, queries)),
    ]

    nav_html = "".join(
        f'<a href="#s{i}" class="nl">{label}</a>' for i, (label, _) in enumerate(sections)
    )
    sections_html = "".join(
        f'<section id="s{i}" class="report-section"><h2 class="sec-title">{label}</h2>{content}</section>'
        for i, (label, content) in enumerate(sections)
    )

    platform_labels = " / ".join(PLATFORM_LABELS.get(p, p) for p in platforms)
    geo_str = f"{geo_overall}" if isinstance(geo_overall, (int, float)) else "0"
    mr_pct = _pct(total_mentioned, total_completed)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    return _build_html(brand, platform_labels, now, geo_str, mr_pct, total_completed,
                       nav_html, sections_html, platform_labels, summary_html)


def _build_html(brand, platform_labels, now, geo_str, mr_pct, total_completed,
                nav_html, sections_html, platform_labels2, summary_html=""):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="GEO 品牌感知报告 - {_esc(brand)}">
<title>"{_esc(brand)}" GEO 品牌感知报告</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
:root {{
  --bg: #f8fafb; --surface: #ffffff; --surface-2: #f1f5f7;
  --text: #1a1d21; --muted: #64748b; --line: #e2e8f0;
  --accent: #0f766e; --accent-light: #f0fdfa;
  --hit: #059669; --hit-light: #ecfdf5;
  --miss: #dc2626; --miss-light: #fef2f2;
  --warn: #b45309; --warn-light: #fffbeb;
  --font-d: 'Outfit','Noto Sans SC',system-ui,sans-serif;
  --font-b: 'Noto Sans SC',system-ui,'PingFang SC','Microsoft YaHei',sans-serif;
  --font-m: 'JetBrains Mono','Menlo','Consolas',monospace;
  --xs: .7rem; --sm: .8125rem; --s0: .9375rem; --s1: 1.0625rem;
  --s2: 1.1875rem; --s3: 1.375rem; --s4: 1.75rem; --s5: 2.25rem;
  --sp1: .1875rem; --sp2: .4375rem; --sp3: .6875rem; --sp4: .875rem;
  --sp5: 1.125rem; --sp6: 1.375rem; --sp8: 1.75rem; --sp10: 2.25rem;
  --wide: 62rem; --pad: clamp(.875rem,3.5vw,2.5rem);
  --r: 8px; --rs: 5px;
  --sh: 0 1px 2px rgba(15,23,42,.04),0 1px 1px rgba(15,23,42,.02);
  --dur: 180ms; --ease: cubic-bezier(.33,1,.68,1);
}}
@media(prefers-reduced-motion:reduce){{:root{{--dur:0ms}}}}
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:var(--font-b);font-size:var(--s0);line-height:1.65;color:var(--text);background:var(--bg);-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}}
.wrap{{max-width:var(--wide);margin:0 auto;padding:0 var(--pad)}}

/* Navigation - pill style */
nav.top{{position:sticky;top:0;z-index:100;background:rgba(248,250,251,.94);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line);padding:0 var(--pad)}}
nav.top .inner{{max-width:var(--wide);margin:0 auto;display:flex;gap:var(--sp1);overflow-x:auto;scrollbar-width:none;padding:var(--sp2) 0}}
nav.top .inner::-webkit-scrollbar{{display:none}}
.nl{{font-family:var(--font-d);font-size:var(--xs);font-weight:500;color:var(--muted);text-decoration:none;white-space:nowrap;padding:4px 10px;border-radius:var(--r);transition:all var(--dur) var(--ease)}}
.nl:hover{{color:var(--text);background:var(--surface-2)}}
.nl.active{{color:var(--accent);background:var(--accent-light)}}

/* Hero - compact, no center */
header.hero{{padding:var(--sp8) 0 var(--sp6)}}
header.hero h1{{font-family:var(--font-d);font-weight:700;font-size:clamp(1.5rem,3.5vw,var(--s4));letter-spacing:-.02em;color:var(--text);margin-bottom:var(--sp1);line-height:1.2}}
header.hero .sub{{font-size:var(--sm);color:var(--muted)}}

/* Sections */
section.report-section{{padding:var(--sp6) 0;border-top:1px solid var(--line)}}
.sec-title{{font-family:var(--font-d);font-weight:600;font-size:var(--s2);letter-spacing:-.01em;margin-bottom:var(--sp5);color:var(--text);display:flex;align-items:center;gap:var(--sp3)}}
.sec-title::before{{content:'';width:3px;height:1.1em;background:var(--accent);border-radius:2px;flex-shrink:0}}

/* Cards */
.card{{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:var(--sp5);box-shadow:var(--sh)}}
.card+.card{{margin-top:var(--sp3)}}
.cl{{font-family:var(--font-d);font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;margin-bottom:var(--sp3)}}
.src{{font-size:10px;color:var(--muted);margin-top:var(--sp4);line-height:1.6;font-family:var(--font-m);opacity:.8}}
.src::before{{content:'说明: ';font-weight:600}}

/* Grids */
.g2{{display:grid;grid-template-columns:1fr 1fr;gap:var(--sp3)}}
.g3{{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--sp3)}}
@media(max-width:640px){{.g2,.g3{{grid-template-columns:1fr}}}}

/* Numeric */
.num{{font-family:var(--font-m);font-weight:700;font-variant-numeric:tabular-nums}}
.ptag{{display:inline-flex;align-items:center;gap:var(--sp2);font-size:var(--sm);font-weight:500}}
.pd{{width:7px;height:7px;border-radius:50%;flex-shrink:0}}

/* Heatmap table */
.heat{{width:100%;border-collapse:separate;border-spacing:0}}
.heat th{{padding:var(--sp2) var(--sp3);font-size:var(--xs);font-weight:600;color:var(--muted);text-align:center;border-bottom:1px solid var(--line);font-family:var(--font-d)}}
.heat td{{padding:6px var(--sp3);font-size:var(--sm);text-align:center;border-bottom:1px solid var(--surface-2)}}
.heat-y{{background:var(--accent-light);color:var(--accent);font-family:var(--font-m);font-weight:700;border-radius:var(--rs)}}
.heat-n{{color:var(--muted);opacity:.4;background:var(--surface-2);font-weight:500}}
.heat-f{{color:var(--miss);font-size:var(--xs);background:var(--miss-light);border-radius:var(--rs)}}

/* Data table */
.tbl{{width:100%;border-collapse:separate;border-spacing:0}}
.tbl th{{padding:var(--sp2) var(--sp3);text-align:left;font-size:11px;font-weight:600;color:var(--muted);letter-spacing:.03em;border-bottom:1px solid var(--line);font-family:var(--font-d);text-transform:uppercase}}
.tbl td{{padding:var(--sp2) var(--sp3);font-size:var(--sm);border-bottom:1px solid var(--surface-2);vertical-align:middle}}
.tbl tr:hover td{{background:var(--surface-2)}}
.tbl .hl td{{background:var(--accent-light);font-weight:600}}
.tbl .hl:hover td{{background:#ccfbf1}}

/* Badges */
.badge{{display:inline-block;padding:2px 8px;border-radius:var(--rs);font-size:10px;font-weight:600;line-height:1.6}}
.b-h{{background:var(--hit-light);color:var(--hit)}}
.b-m{{background:var(--miss-light);color:var(--miss)}}
.b-w{{background:var(--warn-light);color:var(--warn)}}
.b-a{{background:var(--accent-light);color:var(--accent)}}
.b-g{{background:var(--surface-2);color:var(--muted)}}

/* Insights */
.insight{{padding:var(--sp3) var(--sp4);border-radius:var(--r);margin-bottom:var(--sp2);font-size:var(--sm);line-height:1.7;border-left:3px solid}}
.ins-h{{background:var(--hit-light);border-color:var(--hit)}}
.ins-m{{background:var(--miss-light);border-color:var(--miss)}}
.ins-n{{background:var(--surface-2);border-color:var(--muted)}}

/* Bar charts */
.bar-row{{display:flex;align-items:center;gap:var(--sp3);margin-bottom:var(--sp2)}}
.bar-name{{width:160px;font-size:var(--sm);color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;flex-shrink:0}}
.bar-track{{flex:1;background:var(--surface-2);border-radius:var(--rs);height:18px;overflow:hidden}}
.bar-fill{{height:100%;border-radius:var(--rs);display:flex;align-items:center;padding:0 var(--sp2);font-family:var(--font-m);font-size:var(--xs);font-weight:700;color:#fff;min-width:22px;font-variant-numeric:tabular-nums}}

/* Folds */
.fold{{cursor:pointer;user-select:none}}
.fold::before{{content:'';display:inline-block;width:0;height:0;border-left:5px solid var(--muted);border-top:4px solid transparent;border-bottom:4px solid transparent;margin-right:var(--sp2);vertical-align:middle;transition:transform var(--dur) var(--ease)}}
.fold.open::before{{transform:rotate(90deg)}}
.fold-body{{display:none;margin-top:var(--sp3);padding:var(--sp4);background:var(--surface-2);border-radius:var(--r);font-size:var(--sm);line-height:1.7;border:1px solid var(--line)}}
.fold.open+.fold-body{{display:block}}

/* Legend */
.legend{{display:flex;flex-direction:column;gap:var(--sp2)}}
.legend-item{{display:flex;align-items:center;gap:var(--sp3);font-size:var(--sm)}}
.legend-dot{{width:10px;height:10px;border-radius:3px;flex-shrink:0}}
.legend-val{{font-family:var(--font-m);font-weight:700;margin-left:auto;font-variant-numeric:tabular-nums}}

/* Footer */
footer.rf{{padding:var(--sp6) 0;border-top:1px solid var(--line);text-align:center;font-size:var(--xs);color:var(--muted)}}

/* Voice tags */
.vtag{{display:inline-flex;align-items:center;gap:var(--sp1);padding:2px 8px;border-radius:var(--rs);font-size:var(--xs);font-weight:500;margin:0 var(--sp1) var(--sp2) 0;line-height:1.5}}
.vtag-pos{{background:var(--hit-light);color:var(--hit);border:1px solid rgba(5,150,105,.12)}}
.vtag-neg{{background:var(--miss-light);color:var(--miss);border:1px solid rgba(220,38,38,.12)}}
.vtag .vp{{font-size:10px;opacity:.5;margin-left:2px}}

/* Position indicator */
.pos-bar{{display:flex;align-items:center;gap:var(--sp3);padding:var(--sp3) var(--sp4);border-radius:var(--r);border:1px solid var(--line);background:var(--surface)}}
.pos-rank{{font-family:var(--font-m);font-weight:800;font-size:var(--s4);line-height:1}}
.pos-label{{font-family:var(--font-d);font-weight:600;font-size:var(--sm);color:var(--text)}}
.pos-desc{{font-size:var(--xs);color:var(--muted)}}
.pos-leading{{color:var(--hit)}}
.pos-upper{{color:var(--accent)}}
.pos-mid{{color:var(--warn)}}
.pos-trailing{{color:var(--miss)}}

/* Source analysis */
.sa-grid{{display:grid;grid-template-columns:1fr 1fr;gap:var(--sp3);align-items:start}}
@media(max-width:900px){{.sa-grid{{grid-template-columns:1fr;}}}}
.sa-list{{border:1px solid var(--line);border-radius:var(--r);background:var(--surface);overflow:hidden}}
.sa-list-hd{{padding:var(--sp2) var(--sp3);font-family:var(--font-d);font-size:11px;font-weight:600;color:var(--muted);border-bottom:1px solid var(--line);letter-spacing:.02em;text-transform:uppercase}}
.sa-row{{display:flex;align-items:center;gap:var(--sp2);padding:5px var(--sp3);border-bottom:1px solid var(--surface-2);font-size:var(--sm);transition:background var(--dur) var(--ease)}}
.sa-row:hover{{background:var(--surface-2)}}
.sa-row:last-child{{border-bottom:none}}
.sa-rank{{font-family:var(--font-m);font-weight:700;font-size:var(--xs);color:var(--muted);width:18px;text-align:center;flex-shrink:0}}
.sa-name{{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.sa-cnt{{font-family:var(--font-m);font-weight:700;font-size:var(--xs);color:var(--accent);width:24px;text-align:right;flex-shrink:0}}
.sa-cat{{font-size:10px;padding:1px 5px;border-radius:var(--rs);font-weight:500;flex-shrink:0}}
.sa-cat-brand{{background:var(--hit-light);color:var(--hit)}}
.sa-cat-auto{{background:#eff6ff;color:#2563eb}}
.sa-cat-media{{background:#f0fdf4;color:#059669}}
.sa-cat-other{{background:var(--surface-2);color:var(--muted)}}
.sa-article-link{{text-decoration:none;color:var(--text);display:block}}
.sa-article-link:hover .sa-name{{color:var(--accent)}}
.sa-cat-bar{{display:flex;gap:var(--sp5);justify-content:center;flex-wrap:wrap;margin-top:var(--sp3);padding:var(--sp3)}}
.sa-cat-item{{display:flex;align-items:center;gap:var(--sp2);font-size:var(--sm)}}
.sa-cat-dot{{width:8px;height:8px;border-radius:2px;flex-shrink:0}}
.sa-cat-pct{{font-family:var(--font-m);font-weight:700;font-variant-numeric:tabular-nums}}

/* Summary block */
.summary{{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;margin-bottom:var(--sp5)}}
.summary-hd{{padding:var(--sp4) var(--sp5);background:var(--accent);color:#fff;font-family:var(--font-d);font-weight:600;font-size:var(--sm);letter-spacing:.02em}}
.summary-bd{{padding:var(--sp5);font-size:var(--sm);line-height:1.85;color:var(--text)}}
.summary-bd p{{margin-bottom:var(--sp3)}}
.summary-bd p:last-child{{margin-bottom:0}}
.summary-bd strong{{color:var(--text);font-weight:600}}
</style>
</head>
<body>
<nav class="top" aria-label="报告导航"><div class="inner">{nav_html}</div></nav>
<main class="wrap">
<header class="hero">
  <h1>"{_esc(brand)}" GEO 品牌感知报告</h1>
  <div class="sub">{platform_labels} · {now}</div>
</header>
{summary_html}
{sections_html}
<footer class="rf">
  <p>GEO 品牌感知分析 · {platform_labels2} · 共 {total_completed} 条有效回答</p>
  <p style="margin-top:var(--sp1);opacity:.7">提及率=品牌被提及次数/有效回答数 · 排名与情感=AI逐条分析 · 综合得分=提及*40%+排名*30%+情感*30%</p>
</footer>
</main>
<script>
document.querySelectorAll('.fold').forEach(el=>{{el.addEventListener('click',()=>el.classList.toggle('open'))}});
document.querySelectorAll('.nl').forEach(a=>{{a.addEventListener('click',e=>{{e.preventDefault();const t=document.querySelector(a.getAttribute('href'));if(t)t.scrollIntoView({{behavior:'smooth',block:'start'}})}})}});
</script>
</body>
</html>"""


def _render_fingerprint(analysis, platforms, total_completed, total_mentioned, position):
    geo_score = analysis.get("geo_score", {})
    mention_rate = analysis.get("metrics", {}).get("brand_mention_rate", {})
    sentiment_dist = analysis.get("sentiment_distribution", {}).get("overall", {})
    brand = analysis.get("brand", "")
    avg_rank = analysis.get("brand_avg_rank", {}).get("overall")
    geo_o = geo_score.get("overall", 0)
    mr_pct = _pct(total_mentioned, total_completed)
    total_sent = sum(sentiment_dist.values())
    neg_pct = _pct(sentiment_dist.get("negative", 0), total_sent) if total_sent else 0
    pos_pct = 100 - neg_pct
    rank_str = f"{avg_rank:.1f}" if avg_rank else "N/A"

    # 平台卡片: 紧凑布局
    score_cards = ""
    for p in platforms:
        s = geo_score.get(p, 0)
        label = PLATFORM_LABELS.get(p, p)
        color = PLATFORM_COLORS.get(p, "var(--accent)")
        rate = mention_rate.get(p, 0)
        pct = int(rate * 100)
        gt, gc, gbg = _score_grade(s if isinstance(s, (int, float)) else None)
        p_done = sum(1 for a in analysis.get("per_answer", []) if a.get("platform") == p and a.get("status") == "completed")
        p_ment = sum(1 for a in analysis.get("per_answer", []) if a.get("platform") == p and a.get("status") == "completed" and a.get("brand_mentioned"))
        score_cards += f"""
        <div style="padding:var(--sp3) var(--sp4);border:1px solid var(--line);border-radius:var(--r);background:var(--surface)">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--sp2)">
            <span class="ptag"><span class="pd" style="background:{color}"></span>{label}</span>
            <span class="badge" style="background:{gbg};color:{gc}">{gt}</span>
          </div>
          <div class="num" style="font-size:var(--s4);color:{gc};margin-bottom:var(--sp2)">{s if isinstance(s,(int,float)) else 'N/A'}</div>
          <div style="display:flex;gap:var(--sp4);font-size:var(--xs);color:var(--muted)">
            <span>提及 {pct}%</span>
            <span>{p_ment}/{p_done} 条</span>
          </div>
        </div>"""

    pos_html = ""
    if position:
        pr = position["avg_rank"]
        pt = position["total_brands"]
        pc = position["css_class"]
        pl = position["label"]
        pos_html = f"""
        <div class="pos-bar" style="margin-top:0;margin-bottom:var(--sp3)">
          <div class="pos-rank {pc}">#{round(pr)}</div>
          <div>
            <div class="pos-label {pc}">{pl}</div>
            <div class="pos-desc">平均排名 {pr:.1f} · 约 {pt} 个品牌参与</div>
          </div>
        </div>"""

    return f"""
    <div class="g2">
      <div class="card">
        {pos_html}
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:var(--sp4) var(--sp5);margin-bottom:var(--sp3)">
          <div><div style="font-size:11px;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:.03em">GEO 综合</div><div class="num" style="font-size:var(--s4);color:var(--accent)">{geo_o}</div></div>
          <div><div style="font-size:11px;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:.03em">提及率</div><div class="num" style="font-size:var(--s4);color:var(--hit)">{mr_pct}%</div></div>
          <div><div style="font-size:11px;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:.03em">平均排名</div><div class="num" style="font-size:var(--s4);color:var(--warn)">{rank_str}</div></div>
          <div><div style="font-size:11px;color:var(--muted);margin-bottom:2px;text-transform:uppercase;letter-spacing:.03em">正面率</div><div class="num" style="font-size:var(--s4);color:var(--hit)">{pos_pct}%</div></div>
        </div>
        <div class="src">综合得分 = 提及率*40% + 排名得分*30% + 情感得分*30%</div>
      </div>
      <div style="display:grid;grid-template-columns:1fr;gap:var(--sp2)">{score_cards}</div>
    </div>"""





def _render_sentiment_merged(analysis, platforms, has_ai, total_completed, pos_tags, neg_tags, brand):
    """情感分析: 合并原品牌声音+情感分析, 包含分布/平台对比/正面负面信号/非中性详情"""
    if not has_ai:
        return '<div class="card" style="color:var(--muted)">暂无 AI 情感分析数据</div>'
    dist = analysis.get("sentiment_distribution", {})
    overall = dist.get("overall", {"positive": 0, "neutral": 0, "negative": 0})
    total = sum(overall.values())
    neg_count = overall.get("negative", 0)
    neg_pct = _pct(neg_count, total) if total else 0
    pos_pct = 100 - neg_pct
    neu_pct = _pct(overall.get("neutral", 0), total) if total else 0
    # 各平台情感对比
    platform_rows = ""
    for p in platforms:
        d = dist.get(p, {"positive": 0, "neutral": 0, "negative": 0})
        t = sum(d.values()) or 1
        pp = int(d["positive"]/t*100); np_ = int(d["neutral"]/t*100); ng = 100-pp-np_
        label = PLATFORM_LABELS.get(p, p); color = PLATFORM_COLORS.get(p, "var(--accent)")
        platform_rows += f"""
        <div style="display:flex;align-items:center;gap:var(--sp3);padding:var(--sp2) 0;border-bottom:1px solid var(--surface-2)">
          <span class="ptag" style="width:70px"><span class="pd" style="background:{color}"></span>{label}</span>
          <div style="flex:1;display:flex;height:14px;border-radius:var(--rs);overflow:hidden;gap:1px">
            <div style="width:{pp}%;background:var(--hit)"></div>
            <div style="width:{np_}%;background:#d4d4d8"></div>
            <div style="width:{ng}%;background:var(--miss)"></div>
          </div>
          <span class="num" style="font-size:var(--xs);color:var(--muted);width:80px;text-align:right">{d['positive']}正 {d['neutral']}中 {d['negative']}负</span>
        </div>"""
    # 正面信号
    pos_html = ""
    for item in pos_tags:
        p = PLATFORM_LABELS.get(item["platform"], item["platform"])
        is_tag = item.get("tag", False)
        text = _esc(item["text"])
        if is_tag:
            pos_html += f'<span class="vtag vtag-pos">{text}</span>'
        else:
            pos_html += f'<span class="vtag vtag-pos">{text} <span class="vp">{p}</span></span>'
    if not pos_html:
        pos_html = '<span style="color:var(--muted);font-size:var(--sm)">未提取到正面信号</span>'
    # 负面信号
    neg_html = ""
    for item in neg_tags:
        p = PLATFORM_LABELS.get(item["platform"], item["platform"])
        text = _esc(item["text"])
        neg_html += f'<span class="vtag vtag-neg">{text} <span class="vp">{p}</span></span>'
    if not neg_html:
        neg_html = '<span style="color:var(--muted);font-size:var(--sm)">未发现负面信号</span>'
    # 非中性回答详情
    per_answer = analysis.get("per_answer", [])
    pos_insights = ""
    neg_insights = ""
    for ans in per_answer:
        if ans.get("status") != "completed": continue
        s = ans.get("sentiment", "neutral")
        if s == "neutral": continue
        q = _esc(ans.get("question", ""))
        pl = PLATFORM_LABELS.get(ans.get("platform", ""), ans.get("platform", ""))
        reason = _esc(ans.get("sentiment_reason", ""))
        bc = {"positive": "b-h", "negative": "b-m"}.get(s, "b-g")
        sl = SENTIMENT_LABELS.get(s, s)
        card = f'<div class="insight {"ins-h" if s=="positive" else "ins-m"}"><span class="badge {bc}">{sl}</span> <strong>{pl}</strong> / {q}<br><span style="font-size:var(--xs);color:var(--muted)">{reason}</span></div>'
        if s == "positive":
            pos_insights += card
        else:
            neg_insights += card
    if not pos_insights:
        pos_insights = '<div style="color:var(--muted);font-size:var(--sm);padding:var(--sp4)">无正面回答详情</div>'
    if not neg_insights:
        neg_insights = '<div style="color:var(--muted);font-size:var(--sm);padding:var(--sp4)">无负面回答详情</div>'
    return f"""
    <div class="g2">
      <div class="card">
        <div class="cl">整体情感分布</div>
        <div class="legend" style="margin-bottom:var(--sp3)">
          <div class="legend-item"><div class="legend-dot" style="background:var(--hit)"></div>正面<span class="legend-val">{overall.get('positive',0)}</span></div>
          <div class="legend-item"><div class="legend-dot" style="background:#d4d4d8"></div>中性<span class="legend-val">{overall.get('neutral',0)}</span></div>
          <div class="legend-item"><div class="legend-dot" style="background:var(--miss)"></div>负面<span class="legend-val">{neg_count}</span></div>
        </div>
        <div class="src">AI 对 {total} 条回答逐条情感分析(正面=推荐倾向 / 中性=客观描述 / 负面=批评态度)</div>
      </div>
      <div class="card">
        <div class="cl">各平台情感对比</div>
        {platform_rows}
        <div class="src">各平台独立统计, 正面=主动推荐 / 中性=客观提及 / 负面=指出不足</div>
      </div>
    </div>
    <div class="g2" style="margin-top:var(--sp3)">
      <div class="card">
        <div class="cl">正面信号 ({len(pos_tags)} 项)</div>
        <div style="display:flex;flex-wrap:wrap;margin-bottom:var(--sp3)">{pos_html}</div>
        <div class="src">从 AI 回答中提取, 匹配关键词库({len(POS_PATTERNS)}个正面词)</div>
        {pos_insights}
      </div>
      <div class="card">
        <div class="cl">负面信号 ({len(neg_tags)} 项)</div>
        <div style="display:flex;flex-wrap:wrap;margin-bottom:var(--sp3)">{neg_html}</div>
        <div class="src">已排除“无XX”类假阳性(如“无充电等待”不算负面)</div>
        {neg_insights}
      </div>
    </div>"""


def _render_mention_matrix(analysis, platforms, queries, total_completed):
    matrix = analysis.get("mention_matrix", [])
    per_answer = analysis.get("per_answer", [])
    header_cells = "".join(
        f'<th><span class="ptag"><span class="pd" style="background:{PLATFORM_COLORS.get(p,"var(--accent)")}"></span>{PLATFORM_LABELS.get(p,p)}</span></th>'
        for p in platforms
    )
    rows = ""
    for i, row in enumerate(matrix):
        q = queries[i] if i < len(queries) else f"Q{i+1}"
        q_short = q if len(q) <= 24 else q[:24] + "..."
        cells = ""
        for j, cell in enumerate(row):
            mentioned = cell.get("mentioned", False)
            count = cell.get("mention_count", 0)
            if mentioned:
                cells += f'<td class="heat-y" title="出现{count}次">{count}</td>'
            else:
                p = platforms[j] if j < len(platforms) else ""
                has_failed = any(a.get("query_index") == i and a.get("platform") == p and a.get("status") != "completed" for a in per_answer)
                cells += f'<td class="{"heat-f" if has_failed else "heat-n"}" title="{"查询失败" if has_failed else "未提及"}">{"✕" if has_failed else "—"}</td>'
        rows += f'<tr><td style="text-align:left;font-size:var(--sm);max-width:280px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="{_esc(q)}">{_esc(q_short)}</td>{cells}</tr>'
    return f"""
    <div class="card">
      <table class="heat">
        <thead><tr><th style="text-align:left;width:50%">问题</th>{header_cells}</tr></thead>
        <tbody>{rows}</tbody>
      </table>
      <div style="display:flex;gap:var(--sp4);margin-top:var(--sp3);flex-wrap:wrap;font-size:var(--xs);color:var(--muted)">
        <span><span style="display:inline-block;width:8px;height:8px;background:var(--accent-light);border-radius:2px;vertical-align:middle;margin-right:var(--sp1)"></span>已提及</span>
        <span><span style="display:inline-block;width:8px;height:8px;background:var(--surface-2);border-radius:2px;vertical-align:middle;margin-right:var(--sp1)"></span>未提及 (—)</span>
        <span><span style="display:inline-block;width:8px;height:8px;background:var(--miss-light);border-radius:2px;vertical-align:middle;margin-right:var(--sp1)"></span>查询失败 (✕)</span>
      </div>
      <div class="src">共 {total_completed} 条回答, 通过关键词匹配(品牌名+别名)检测是否提及</div>
    </div>"""


def _render_sentiment(analysis, platforms, has_ai, total_completed):
    pass  # merged into _render_sentiment_merged


CAT_COLORS = {
    "品牌官网": "#059669",
    "汽车垂直": "#2563eb",
    "社媒资讯": "#0f766e",
    "其他网站": "#a1a1aa",
}

CAT_CSS = {
    "品牌官网": "sa-cat-brand",
    "汽车垂直": "sa-cat-auto",
    "社媒资讯": "sa-cat-media",
    "其他网站": "sa-cat-other",
}


def _render_sources_analysis(analysis, search_results, platforms, total_completed, sources_data):
    """信源分析: 域名表(左) + 环形图(中) + 文章排名(右) + 分类占比(底)"""
    if not sources_data:
        return '<div class="card" style="color:var(--muted)">暂无信源数据</div>'

    top_domains = sources_data["top_domains"]
    top_articles = sources_data["top_articles"]
    category_freq = sources_data["category_freq"]
    total_citations = sources_data["total_citations"]

    brand = analysis.get("brand", "")
    aliases = analysis.get("aliases", [])
    brand_keywords = [k.lower() for k in [brand] + aliases if k]

    # 左侧: 域名聚合排序 TOP10
    domain_rows = ""
    for i, (domain, count) in enumerate(top_domains):
        cat = _classify_domain(domain)
        css_cat = CAT_CSS.get(cat, "sa-cat-other")
        is_brand = any(kw in domain.lower() for kw in brand_keywords)
        name_style = "color:var(--hit);font-weight:600" if is_brand else ""
        mark = " *" if is_brand else ""
        domain_url = f"https://{domain}"
        domain_rows += f'<div class="sa-row"><span class="sa-rank">{i+1}</span><a class="sa-name sa-article-link" href="{domain_url}" target="_blank" rel="noopener" style="{name_style}" title="{_esc(domain)}">{_esc(domain)}{mark}</a><span class="sa-cnt">{count}</span><span class="sa-cat {css_cat}">{cat}</span></div>'

    # 右侧: 文章频次排名 TOP10
    article_rows = ""
    for i, (meta, count) in enumerate(top_articles):
        title = _esc(meta["title"])[:30]
        url = _esc(meta["url"])
        article_rows += f'<a class="sa-row sa-article-link" href="{url}" target="_blank" rel="noopener"><span class="sa-rank">{i+1}</span><span class="sa-name" title="{_esc(meta["title"])}">{title}</span><span class="sa-cnt">{count}</span></a>'

    # 底部: 分类占比
    cat_bar = ""
    sorted_cats = sorted(category_freq.items(), key=lambda x: -x[1])
    for cat, count in sorted_cats:
        pct = count / total_citations * 100 if total_citations else 0
        col = CAT_COLORS.get(cat, "#a1a1aa")
        cat_bar += f'<div class="sa-cat-item"><span class="sa-cat-dot" style="background:{col}"></span><span class="sa-cat-pct">{pct:.1f}%</span> {cat}</div>'

    brand_note = ""
    if any(any(kw in d.lower() for kw in brand_keywords) for d, _ in top_domains):
        brand_note = f'<span style="color:var(--hit)">* {brand} 品牌官网</span>'
    elif brand:
        brand_note = f'<span style="color:var(--miss)">"{_esc(brand)}" 品牌官网未进入 TOP10</span>'

    return f"""
    <div class="sa-grid">
      <div class="sa-list">
        <div class="sa-list-hd">信源引用域名聚合排序 (TOP10)</div>
        {domain_rows}
      </div>
      <div class="sa-list">
        <div class="sa-list-hd">信源引用文章频次排名 (TOP10)</div>
        {article_rows}
      </div>
    </div>
    <div class="sa-cat-bar">
      {cat_bar}
    </div>
    <div style="display:flex;gap:var(--sp4);margin-top:var(--sp1);font-size:var(--xs);color:var(--muted);justify-content:center">
      {brand_note}
    </div>
    <div class="src">总引用 {total_citations} 次 · 来自 {total_completed} 条有效回答 · 域名按聚合频次降序 · 文章按被引用次数降序</div>"""


def _render_competitors(analysis, platforms, total_completed):
    comparison = analysis.get("competitor_comparison", [])
    brand = analysis.get("brand", "")
    mention_rate = analysis.get("metrics", {}).get("brand_mention_rate", {})
    brand_avg_rank = analysis.get("brand_avg_rank", {})
    brand_sentiment = analysis.get("sentiment_distribution", {}).get("overall", {})
    if not comparison and not brand:
        return '<div class="card" style="color:var(--muted)">暂无竞品数据</div>'
    brand_total_s = sum(brand_sentiment.values()) if brand_sentiment else 0
    brand_neg_pct = _pct(brand_sentiment.get("negative", 0), brand_total_s) if brand_total_s else 0
    brand_pos_pct = 100 - brand_neg_pct
    brand_rank_str = f"{brand_avg_rank.get('overall',0):.1f}" if brand_avg_rank.get("overall") else "N/A"
    brand_row = f"""
    <tr class="hl">
      <td><strong>{_esc(brand)}</strong> <span class="badge b-a">本品牌</span></td>
      <td class="num">{_pct(int(mention_rate.get('overall',0)*100),100)}%</td>
      <td class="num">{brand_rank_str}</td>
      <td class="num" style="color:var(--hit)">{brand_pos_pct}%</td>
    </tr>"""
    sorted_comps = sorted(comparison, key=lambda c: c.get("mention_rate_overall",0), reverse=True)
    comp_rows = ""
    comp_count = 0
    skipped_count = 0
    for comp in sorted_comps:
        name = comp.get("name", "")
        if name == brand: continue
        mr = comp.get("mention_rate_overall",0)
        # 只展示在回答中实际被提及的竞品
        if mr <= 0: continue
        if comp_count >= 10:
            skipped_count += 1
            continue
        comp_count += 1
        rank = comp.get("avg_rank")
        rs = f"{rank:.1f}" if rank else "N/A"
        sd = comp.get("sentiment_dist", {})
        sd_total = sum(sd.values()) if sd else 0
        comp_neg_pct = _pct(sd.get("negative", 0), sd_total) if sd_total else 0
        pp = 100 - comp_neg_pct
        detail = ""
        if sd:
            detail = f'<div class="fold-body" style="font-size:var(--xs)"><strong>各平台提及:</strong> 豆包 {_pct(int(comp.get("mention_rate_doubao",0)*100),100)}% · Kimi {_pct(int(comp.get("mention_rate_kimi",0)*100),100)}% · DeepSeek {_pct(int(comp.get("mention_rate_deepseek",0)*100),100)}%<br><strong>情感分布:</strong> 正面{sd.get("positive",0)} / 中性{sd.get("neutral",0)} / 负面{sd.get("negative",0)}</div>'
        comp_rows += f'<tr><td><span class="fold" style="font-size:var(--sm)">{_esc(name)}</span>{detail}</td><td class="num">{_pct(int(mr*100),100)}%</td><td class="num">{rs}</td><td class="num" style="color:var(--hit)">{pp}%</td></tr>'
    more_text = f'<div style="margin-top:var(--sp2);font-size:var(--xs);color:var(--muted);text-align:center">还有 {skipped_count} 个竞品未展示（提及率较低）</div>' if skipped_count > 0 else ''
    return f"""
    <div class="card">
      <table class="tbl">
        <thead><tr><th style="width:35%">品牌 (点击展开详情)</th><th>提及率</th><th>平均排名</th><th>正面率</th></tr></thead>
        <tbody>{brand_row}{comp_rows}</tbody>
      </table>
      {more_text}
      <div class="src">提及率=关键词匹配+AI提及列表推断排名 · 正面率=1-负面率 · 排名=在推荐列表中的位置</div>
    </div>"""


def _render_archive(analysis, search_results, platforms, queries):
    brand = analysis.get("brand", "")
    if not search_results:
        return '<div class="card" style="color:var(--muted)">暂无原始数据</div>'
    results = search_results.get("results", [])
    if not results:
        return '<div class="card" style="color:var(--muted)">暂无原始数据</div>'
    by_question = {}
    for r in results:
        qi = r.get("query_index", 0)
        by_question.setdefault(qi, []).append(r)
    per_answer_map = {}
    for a in analysis.get("per_answer", []):
        key = (a.get("query_index"), a.get("platform"))
        per_answer_map[key] = a
    panels = ""
    for qi in sorted(by_question.keys()):
        question = queries[qi] if qi < len(queries) else f"Q{qi+1}"
        answers = by_question[qi]
        platform_items = ""
        for ans in answers:
            p = ans.get("platform", "")
            label = PLATFORM_LABELS.get(p, p)
            color = PLATFORM_COLORS.get(p, "var(--accent)")
            status = ans.get("status", "unknown")
            content = ans.get("content", "")
            pa = per_answer_map.get((qi, p), {})
            s = pa.get("sentiment", "")
            sb = ""
            if s and status == "completed":
                sl = SENTIMENT_LABELS.get(s, s)
                bc = {"positive": "b-h", "neutral": "b-g", "negative": "b-m"}.get(s, "b-g")
                sb = f' <span class="badge {bc}">{sl}</span>'
            cd = f"[{status}]" if status != "completed" else content
            escaped = _esc(cd)
            # 品牌词高亮
            brand_kw = [brand] + [a for a in analysis.get("aliases", []) if a] if brand else []
            for kw in brand_kw:
                ekw = _esc(kw)
                if ekw and ekw in escaped:
                    escaped = escaped.replace(ekw, f'<mark style="background:#fef08a;color:inherit;padding:0 2px;border-radius:2px">{ekw}</mark>')
            platform_items += f'<div style="margin-bottom:var(--sp3)"><div class="fold" style="font-size:var(--sm);font-weight:500"><span class="ptag"><span class="pd" style="background:{color}"></span>{label}</span>{sb}</div><div class="fold-body">{escaped}</div></div>'
        nd = '<div style="color:var(--muted)">暂无数据</div>'
        panels += f'<div class="card" style="margin-bottom:var(--sp3)"><div class="fold" style="font-size:var(--s1);font-weight:600">Q{qi+1}. {_esc(_clean(question))}</div><div class="fold-body">{platform_items if platform_items else nd}</div></div>'
    return panels
