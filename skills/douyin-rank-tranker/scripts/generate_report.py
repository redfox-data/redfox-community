#!/usr/bin/env python3
"""
抖音榜单 HTML 报告生成脚本
用法：
    python generate_report.py --data result.json --output report.html
    python generate_report.py --data result.json  # 自动命名输出文件
"""
import argparse
import json
import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────
# 赛道识别：基于账号名推断细分赛道
# ─────────────────────────────────────────────────────────

CATEGORY_INFER_RULES = [
    # 游戏类
    {"keywords": ["王者荣耀", "英雄联盟", "原神", "崩坏", "蛋仔", "阴阳师", "明日方舟", "光遇", "鸣潮"], "category": "游戏"},
    {"keywords": ["吃鸡", "和平精英", "PUBG", "LOL", "无畏契约", "CSGO", "DOTA", "Valorant"], "category": "游戏"},
    {"keywords": ["迷你世界", "我的世界", "MC", "Minecraft"], "category": "游戏"},

    # 明星/娱乐类
    {"keywords": ["official", "工作室"], "category": "官方账号"},
    {"keywords": ["爱奇艺", "优酷", "腾讯视频", "芒果TV", "Bilibili", "B站"], "category": "视频平台"},
    {"keywords": ["微博", "新浪", "凤凰网", "澎湃"], "category": "新闻媒体"},
    {"keywords": ["明星", "演员", "歌手", "偶像"], "category": "明星娱乐"},

    # 美食类细分
    {"keywords": ["美食", "吃货", "探店", "烹饪"], "category": "美食"},
    {"keywords": ["烘焙", "蛋糕", "面包", "甜品"], "category": "烘焙甜点"},

    # 旅行/户外类
    {"keywords": ["旅行", "旅游", "自驾", "露营"], "category": "旅行"},

    # 宠物类
    {"keywords": ["宠物", "猫", "狗", "萌宠", "铲屎"], "category": "动物"},

    # 时尚/穿搭类
    {"keywords": ["穿搭", "OOTD", "衣橱"], "category": "潮流风尚"},

    # 健身/运动类
    {"keywords": ["健身", "瑜伽", "减脂", "增肌", "运动"], "category": "身体锻炼"},

    # 学习/知识类
    {"keywords": ["教育", "学习", "干货", "职场", "知识"], "category": "学习教育"},

    # 科技/测评类
    {"keywords": ["数码", "手机", "电脑", "测评", "评测", "科技"], "category": "数码科技"},

    # 亲子/母婴类
    {"keywords": ["母婴", "育儿", "宝宝", "辣妈", "萌娃", "亲子"], "category": "亲子"},

    # 家居/装修类
    {"keywords": ["家居", "装修", "软装", "设计", "收纳"], "category": "居家装修"},

    # 情感/心理类
    {"keywords": ["星座", "情感", "恋爱", "心理", "塔罗"], "category": "情感"},

    # 音乐类
    {"keywords": ["音乐", "唱歌", "弹琴", "乐器"], "category": "音乐"},

    # 影视类
    {"keywords": ["影视", "娱乐", "综艺", "剧集", "电影"], "category": "影视"},

    # 舞蹈类
    {"keywords": ["舞蹈", "跳舞", "舞"], "category": "舞蹈才艺"},

    # 日常生活/Vlog
    {"keywords": ["日记", "vlog", "plog", "日常", "记录", "生活"], "category": "生活vlog"},

    # 二次元类
    {"keywords": ["二次元", "动漫", "动画", "ACG"], "category": "二次元"},

    # 健康医学类
    {"keywords": ["健康", "养生", "医疗", "医学"], "category": "健康医学"},
]


def infer_category(account_name: str) -> str:
    """根据账号名推断赛道分类"""
    combined = (account_name).lower()

    # 精确账号名匹配
    exact_account_map = {
        "王者荣耀": "游戏",
        "原神": "游戏",
        "和平精英": "游戏",
        "英雄联盟": "游戏",
        "迷你世界": "游戏",
    }
    for exact_name, cat in exact_account_map.items():
        if exact_name.lower() in combined:
            return cat

    # 规则遍历匹配
    for rule in CATEGORY_INFER_RULES:
        for kw in rule["keywords"]:
            if kw.lower() in combined:
                return rule["category"]

    return "全部"


def parse_num(val) -> int:
    """解析数字字符串"""
    if val is None or val == "-":
        return 0
    s = str(val).replace("w", "").replace("W", "").replace("+", "").strip()
    try:
        if "." in s:
            return int(float(s) * 10000)
        return int(float(s))
    except (ValueError, TypeError):
        return 0


def format_interaction(num: int) -> str:
    if num >= 100_000:
        return f"{num // 10_000}w+"
    elif num >= 10_000:
        return f"{num / 10_000:.1f}w+"
    return str(num)


def format_followers(num: int) -> str:
    if num >= 100_000_000:
        return f"{num / 100_000_000:.1f}亿"
    elif num >= 10_000:
        return f"{num / 10_000:.1f}w"
    return str(num)


PERIOD_UPDATE_RULES = {
    "day": "每日17:30",
    "week": "每周一17:30",
    "month": "每月2号9点",
}
PERIOD_LABELS = {"day": "日榜", "week": "周榜", "month": "月榜"}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>抖音{period_label} · {date}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Helvetica Neue", Arial, sans-serif;
    background: linear-gradient(135deg, #f0f4ff 0%, #fafbff 100%);
    min-height: 100vh;
    padding: 24px;
    color: #1a1a1a;
  }}
  .header {{
    text-align: center;
    margin-bottom: 32px;
  }}
  .header .logo {{
    font-size: 48px;
    margin-bottom: 8px;
  }}
  .header h1 {{
    font-size: 28px;
    font-weight: 700;
    color: #000000;
    margin-bottom: 6px;
  }}
  .header .meta {{
    font-size: 13px;
    color: #888;
  }}
  .notice {{
    background: #fff8e1;
    border-left: 4px solid #ffb300;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 24px;
    font-size: 13px;
    color: #5d4037;
  }}
  .stats-bar {{
    display: flex;
    gap: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
  }}
  .stat-card {{
    flex: 1;
    min-width: 120px;
    background: #fff;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  .stat-card .num {{
    font-size: 28px;
    font-weight: 700;
    color: #000000;
  }}
  .stat-card .label {{
    font-size: 12px;
    color: #888;
    margin-top: 4px;
  }}
  .stat-card.hidden {{ display: none; }}
  .more-hint {{
    background: linear-gradient(135deg, #fff3e0, #ffe0b2);
    border-left: 4px solid #ff9800;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 24px;
    font-size: 13px;
    color: #e65100;
    display: none;
  }}
  .more-hint.show {{ display: block; }}
  .table-wrap {{
    background: #fff;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    margin-bottom: 24px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
  }}
  thead th {{
    background: linear-gradient(135deg, #000000, #000000);
    color: #fff;
    padding: 14px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
    white-space: nowrap;
  }}
  tbody tr {{
    border-bottom: 1px solid #f5f5f5;
    transition: background 0.15s;
  }}
  tbody tr:hover {{ background: #f0f9ff; }}
  tbody tr:last-child {{ border-bottom: none; }}
  td {{
    padding: 12px 16px;
    font-size: 14px;
    vertical-align: middle;
  }}
  .rank-badge {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    font-weight: 700;
    font-size: 14px;
  }}
  .rank-1 {{ background: #FFD700; color: #5d4000; }}
  .rank-2 {{ background: #C0C0C0; color: #3d3d3d; }}
  .rank-3 {{ background: #CD7F32; color: #fff; }}
  .rank-other {{ background: #f0f0f0; color: #555; }}
  .account-name {{
    font-weight: 600;
    color: #333;
    text-decoration: none;
    cursor: pointer;
    transition: color 0.15s;
  }}
  .account-name:hover {{
    color: #000000;
    text-decoration: underline;
  }}
  .score-bar-wrap {{
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .score-bar {{
    flex: 1;
    height: 8px;
    background: #f0f0f0;
    border-radius: 4px;
    overflow: hidden;
    max-width: 100px;
  }}
  .score-fill {{
    height: 100%;
    background: linear-gradient(90deg, #000000, #000000);
    border-radius: 4px;
  }}
  .score-num {{
    font-weight: 600;
    color: #000000;
    min-width: 36px;
  }}
  .interaction {{
    font-weight: 600;
    color: #ff6b35;
  }}
  .export-bar {{
    text-align: center;
    margin-bottom: 16px;
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }}
  .btn {{
    padding: 10px 24px;
    border-radius: 24px;
    border: none;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: transform 0.1s, box-shadow 0.1s;
  }}
  .btn:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
  .btn-primary {{ background: linear-gradient(135deg, #000000, #000000); color: #fff; }}
  .btn-secondary {{ background: #fff; color: #000000; border: 2px solid #000000; }}
  .footer {{
    text-align: center;
    font-size: 12px;
    color: #bbb;
    padding: 16px;
  }}
  @media print {{
    .export-bar {{ display: none; }}
    body {{ background: #fff; padding: 0; }}
    .table-wrap {{ box-shadow: none; }}
  }}
</style>
</head>
<body>

<div class="header">
  <div class="logo">📊</div>
  <h1>抖音{period_label} · {category_label}</h1>
  <div class="meta">数据日期：{date} &nbsp;|&nbsp; {display_hint}</div>
</div>

<div class="notice">
  💡 <strong>榜单说明</strong>：{update_rule}，与实时数据存在差异。<br>
  📐 <strong>综合评分（满分100）</strong>：综合评分根据达人在抖音的 <strong>总粉丝数</strong>、周期内的 <strong>粉丝增量</strong>、<strong>点赞增量</strong>、<strong>分享增量</strong> 以及 <strong>评论增量</strong> 加权计算所得（满分100）。
</div>

<div class="stats-bar">
  <div class="stat-card"><div class="num">{displayed_count}</div><div class="label">展示条数</div></div>
  <div class="stat-card"><div class="num">{top_interaction}</div><div class="label">最高互动</div></div>
</div>

<div class="export-bar">
  <button class="btn btn-primary" onclick="window.print()">🖨️ 打印 / 导出 PDF</button>
  <button class="btn btn-secondary" id="downloadImgBtn" onclick="downloadAsImage()">📷 保存为图片</button>
</div>

<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<script>
async function downloadAsImage() {{
  const btn = document.getElementById('downloadImgBtn');
  btn.textContent = '⏳ 生成中...';
  btn.disabled = true;
  try {{
    const element = document.querySelector('.table-wrap');
    const canvas = await html2canvas(element, {{
      scale: 2,
      backgroundColor: '#ffffff',
      useCORS: true
    }});
    const link = document.createElement('a');
    link.download = '抖音榜单_{date}.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
    btn.textContent = '✅ 下载成功';
    setTimeout(() => {{
      btn.textContent = '📷 保存为图片';
      btn.disabled = false;
    }}, 2000);
  }} catch (e) {{
    alert('生成图片失败，请尝试使用浏览器截图');
    btn.textContent = '📷 保存为图片';
    btn.disabled = false;
  }}
}}
</script>

<div class="table-wrap">
<table>
  <thead>
    <tr>
      <th>排名</th>
      <th>账号名</th>
      {category_th}
      <th>综合评分</th>
      <th>总粉丝数</th>
      <th>新增粉丝</th>
      <th>新增点赞</th>
      <th>新增评论</th>
      <th>新增分享</th>
    </tr>
  </thead>
  <tbody>
{rows}
  </tbody>
</table>
</div>

<!-- 订阅服务模块（导出图片时排除） -->
<div id="subscription-section" style="margin-top: 40px; padding: 24px; background: #f8f9fa; border-radius: 12px;">
  <h3 style="margin: 0 0 16px 0; font-size: 18px; color: #333;">📬 订阅服务</h3>
  <div style="margin-bottom: 12px;">
    <div style="font-weight: 500; color: #333;">1️⃣ 是否需要订阅每日/周/月的抖音账号最新排名？</div>
  </div>
  <div>
    <div style="font-weight: 500; color: #333; margin-bottom: 8px;">2️⃣ 是否需要订阅具体赛道的账号表现？我们支持：</div>
    <div style="display: flex; flex-wrap: wrap; gap: 6px;">
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">个人才艺</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">生活vlog</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">财富理财</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">二次元</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">居家装修</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">学习教育</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">小剧场</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">数码科技</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">旅行</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">美食</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">化妆美容</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">动物</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">亲子</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">汽车</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">情感</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">三农</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">健康医学</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">潮流风尚</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">舞蹈才艺</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">颜值造型</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">人文</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">音乐</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">影视</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">身体锻炼</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">体育</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">明星娱乐</span>
      <span style="background: #e9ecef; padding: 4px 10px; border-radius: 16px; font-size: 13px;">游戏</span>
    </div>
  </div>
</div>

</body>
</html>"""

# 全品类行模板（带赛道列）
ROW_TEMPLATE_CAT = """    <tr>
      <td><span class="rank-badge {rank_class}">{rank}</span></td>
      <td><a href="{profile_url}" target="_blank" class="account-name" title="点击查看抖音主页">{account_name}</a></td>
      <td class="category">{category}</td>
      <td><span class="score">{score}</span></td>
      <td>{followers}</td>
      <td class="interaction">{new_fans}</td>
      <td class="interaction">{new_likes}</td>
      <td class="interaction">{new_comments}</td>
      <td class="interaction">{new_shares}</td>
    </tr>"""

# 非全品类行模板（无赛道列）
ROW_TEMPLATE = """    <tr>
      <td><span class="rank-badge {rank_class}">{rank}</span></td>
      <td><a href="{profile_url}" target="_blank" class="account-name" title="点击查看抖音主页">{account_name}</a></td>
      <td><span class="score">{score}</span></td>
      <td>{followers}</td>
      <td class="interaction">{new_fans}</td>
      <td class="interaction">{new_likes}</td>
      <td class="interaction">{new_comments}</td>
      <td class="interaction">{new_shares}</td>
    </tr>"""


def _fmt_num(val) -> str:
    """格式化数字"""
    if val is None or val == "-" or val == "":
        return "-"
    if isinstance(val, str):
        return val if val.strip() else "-"
    try:
        n = int(val)
        if n == 0:
            return "-"
        return format_followers(n)
    except (TypeError, ValueError):
        return str(val) if val else "-"


def generate_html(data: dict, output_path: str):
    """生成 HTML 报告"""
    items = data.get("list", [])
    period = data.get("period", "day")
    date_start = data.get("dateStart", data.get("date", ""))
    date_end = data.get("dateEnd", date_start)
    category = data.get("category", "全部")
    total = data.get("total", len(items))

    # 实际展示的条数
    displayed_count = len(items)

    if date_start == date_end:
        date_display = date_start
    else:
        date_display = f"{date_start} 至 {date_end}"

    period_label = PERIOD_LABELS.get(period, "日榜")

    CAT_DISPLAY = {
        "全部": "全品类", "化妆美容": "美妆类", "美食": "美食类",
        "旅行": "旅行类", "数码科技": "科技类", "游戏": "游戏类",
        "健康医学": "健康类", "亲子": "亲子类", "身体锻炼": "运动类",
        "学习教育": "教育类", "动物": "动物类", "潮流风尚": "时尚类",
        "居家装修": "家居类", "影视": "影视类", "音乐": "音乐类",
        "舞蹈才艺": "舞蹈类", "明星娱乐": "娱乐类", "体育": "体育类",
        "情感": "情感类", "财富理财": "理财类", "二次元": "二次元类",
        "小剧场": "小剧场类", "汽车": "汽车类", "三农": "三农类",
        "人文": "人文类", "颜值造型": "颜值类", "个人才艺": "才艺类",
        "生活vlog": "生活类",
    }
    cat_display = CAT_DISPLAY.get(category, category + "类")
    is_all_category = (category == "全部")
    
    # 表头：全品类时添加赛道列
    if is_all_category:
        category_th = '<th>赛道</th>'
    else:
        category_th = ''

    # 榜单说明：根据周期展示更新时间
    if period == "day":
        update_rule = "每日17:30更新"
        window_human = "过去7天"
        latest_desc = "昨日"
    elif period == "week":
        update_rule = "每周一17:30更新"
        window_human = "过去3周"
        latest_desc = "上周"
    else:
        update_rule = "每月2号9点更新"
        window_human = "过去3月"
        latest_desc = "上月"

    # 超出范围时的提示
    warning_text = ""
    if data.get("status") == "future":
        warning_text = f'非常抱歉🙏，我们最新的是{latest_desc}的数据，将为您提供最接近您需求的{latest_desc}热榜。'
    elif data.get("status") == "too_early":
        warning_text = f'非常抱歉🙏，目前榜单最多支持回溯「{window_human}」，我将为您查询最接近您需求的时间范围~'

    # 合并 warning 到榜单说明
    if warning_text:
        update_rule_full = f'{warning_text}{update_rule}'
    else:
        update_rule_full = update_rule

    # 统计
    max_interaction = 0
    for item in items:
        likes = parse_num(item.get('newLikes') or item.get('likedGrowth'))
        comments = parse_num(item.get('newComments') or item.get('commentsGrowth'))
        shares = parse_num(item.get('newShares') or item.get('sharedGrowth'))
        interaction = likes + comments + shares
        if interaction > max_interaction:
            max_interaction = interaction

    # 生成行
    rows = []
    for item in items:
        rank = item.get('rank', '-')
        rank_class = f"rank-{rank}" if rank in [1, 2, 3] else "rank-other"

        account_name = item.get('accountName', '')
        profile_url = item.get('profileUrl', '')

        score = item.get('comprehensiveScore', '-')
        if isinstance(score, (int, float)) and score > 0:
            score = int(score)

        followers = _fmt_num(item.get('followers') or item.get('fansCount'))
        new_fans = _fmt_num(item.get('newFans') or item.get('fansGrowth'))
        new_likes = _fmt_num(item.get('newLikes') or item.get('likedGrowth'))
        new_comments = _fmt_num(item.get('newComments') or item.get('commentsGrowth'))
        new_shares = _fmt_num(item.get('newShares') or item.get('sharedGrowth'))

        # 全品类时使用带赛道列的模板
        if is_all_category:
            account_category = item.get('category', '-')
            rows.append(ROW_TEMPLATE_CAT.format(
                rank_class=rank_class,
                rank=rank,
                account_name=account_name,
                profile_url=profile_url or '#',
                category=account_category,
                score=score,
                followers=followers,
                new_fans=new_fans,
                new_likes=new_likes,
                new_comments=new_comments,
                new_shares=new_shares,
            ))
        else:
            rows.append(ROW_TEMPLATE.format(
                rank_class=rank_class,
                rank=rank,
                account_name=account_name,
                profile_url=profile_url or '#',
                score=score,
                followers=followers,
                new_fans=new_fans,
                new_likes=new_likes,
                new_comments=new_comments,
                new_shares=new_shares,
            ))

    # 显示提示
    if displayed_count >= total:
        display_hint = f"共 {total} 个账号上榜"
        total_hidden_class = ""
        more_hint_class = ""
        remaining_count = 0
    else:
        display_hint = f"共 {total} 个账号上榜（展示 TOP {displayed_count} 条）"
        total_hidden_class = "hidden"
        more_hint_class = "show"
        remaining_count = total - displayed_count

    html = HTML_TEMPLATE.format(
        period_label=period_label,
        category_label=cat_display,
        date=date_display.replace(' ', '_'),
        displayed_count=displayed_count,
        total_count=total,
        total_hidden_class=total_hidden_class,
        remaining_count=remaining_count,
        more_hint_class=more_hint_class,
        display_hint=display_hint,
        update_rule=update_rule,
        top_interaction=format_interaction(max_interaction),
        category_th=category_th,
        rows="\n".join(rows),
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[INFO] HTML 报告已生成：{output_path}")


def main():
    parser = argparse.ArgumentParser(description="抖音榜单 HTML 报告生成")
    parser.add_argument("--data", "-d", required=True, help="JSON 数据文件路径")
    parser.add_argument("--output", "-o", default="", help="HTML 输出文件路径")
    parser.add_argument("--limit", type=int, default=20, help="限制展示条数，0 表示全部展示")
    args = parser.parse_args()

    with open(args.data, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 应用 limit 限制
    if args.limit > 0 and "list" in data:
        data["list"] = data["list"][:args.limit]

    # 生成文件名：赛道+周期+日期+时间戳
    if args.output:
        output_path = Path(args.output)
    else:
        import time
        date_start = data.get("dateStart", data.get("date", ""))
        category = data.get("category", "全部")
        period = data.get("period", "day")
        period_name = {"day": "日榜", "week": "周榜", "month": "月榜"}.get(period, "榜")
        date_str = date_start.replace("-", "")
        timestamp = int(time.time())
        filename = f"{category}{period_name}{date_str}_{timestamp}.html"
        output_path = Path(filename)

    generate_html(data, str(output_path))

    # 自动打开 HTML 文件
    import platform
    import subprocess
    abs_path = output_path.resolve()
    try:
        system = platform.system()
        if system == "Darwin":  # macOS
            subprocess.run(["open", str(abs_path)], check=True)
        elif system == "Windows":
            subprocess.run(["start", "", str(abs_path)], shell=True, check=True)
        else:  # Linux
            subprocess.run(["xdg-open", str(abs_path)], check=True)
        print(f"\n✓ HTML 报告已自动打开: {abs_path}", file=sys.stderr)
    except Exception as e:
        print(f"\n✓ HTML 报告已生成: {abs_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
