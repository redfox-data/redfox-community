#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书冷门账号爆款内容榜单HTML生成脚本

功能：
1. 读取API数据
2. 生成小红书风格的HTML页面
3. 支持PDF导出

使用方法：
python generate_html.py --keyword "爆款" --articles '[{"title": "...", ...}]' --insights "分析文本" --output ranking.html
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime


def get_article_html(article: dict, rank: int) -> str:
    """生成单篇笔记的HTML（参考模板风格）"""
    try:
        title = article.get("title", "无笔记标题") or "无笔记标题"
        photo_url = article.get("photoJumpUrl", "#")
        user_name = article.get("userName", "未知作者")
        user_url = article.get("userJumpUrl", "#")
        fans = article.get("fans", "0")
        desc = article.get("desc", "")

        # 获取互动数据
        like_count = article.get("useLikeCount", "0")
        collect_count = article.get("collectedCount", "0")
        comment_count = article.get("useCommentCount", "0")
        share_count = article.get("useShareCount", "0")
        interactive_count = article.get("interactiveCount", "0")

        # 生成内容分析
        analysis = generate_content_analysis(desc, title)

        # 序号样式：前三用top类
        top_class = "top" if rank <= 3 else ""

        # 互动数据HTML
        stats_html = f'''
            <div class="info-item">
                <span class="info-stat">❤️ 点赞 <span class="info-stat-value">{like_count}</span></span>
            </div>
            <div class="info-item">
                <span class="info-stat">⭐ 收藏 <span class="info-stat-value">{collect_count}</span></span>
            </div>
            <div class="info-item">
                <span class="info-stat">💬 评论 <span class="info-stat-value">{comment_count}</span></span>
            </div>
            <div class="info-item">
                <span class="info-stat">📤 分享 <span class="info-stat-value">{share_count}</span></span>
            </div>
            <div class="info-item">
                <span class="info-stat">互动总数 <span class="info-stat-value">{interactive_count}</span></span>
            </div>
        '''

        # 作者头像和粉丝数
        user_head_url = article.get("userHeadUrl", "")
        if user_head_url:
            author_html = f'<img src="{user_head_url}" class="author-avatar" alt="{user_name}">{user_name}（{fans} 粉丝）'
        else:
            author_html = f'<span class="author-avatar-placeholder"></span>{user_name}（{fans} 粉丝）'

        return f'''
            <div class="article-item">
                <div class="article-body">
                    <div class="article-rank {top_class}">{rank}</div>
                    <div class="article-content">
                        <a href="{photo_url}" target="_blank" class="article-title">{title}</a>
                        <div class="article-info">
                            <a href="{user_url}" target="_blank" class="info-source-link">
                                {author_html}
                            </a>
                            {stats_html}
                        </div>
                        <div class="article-analysis">
                            <div class="analysis-label">🔍 内容分析</div>
                            <div class="analysis-text">{analysis}</div>
                        </div>
                    </div>
                </div>
            </div>'''
    except:
        return ""


def generate_content_analysis(desc, title):
    """根据描述内容生成内容分析"""
    if not desc and not title:
        return "暂无分析"

    analysis_parts = []

    # 提取标题主题
    if title:
        analysis_parts.append(f"笔记主题围绕「{title[:30]}{'...' if len(title) > 30 else ''}」展开")

    # 从描述中提取关键信息
    if desc:
        # 提取话题标签
        import re
        tags = re.findall(r'#([^\s#]+)', desc)
        if tags:
            tag_list = "、".join(tags[:5])
            analysis_parts.append(f"内容涵盖{tag_list}等话题")

        # 判断内容类型
        if any(keyword in desc for keyword in ["穿搭", "搭配", "时尚", "潮流"]):
            content_type = "穿搭分享"
        elif any(keyword in desc for keyword in ["美食", "探店", "料理", "味道"]):
            content_type = "美食探店"
        elif any(keyword in desc for keyword in ["旅行", "景点", "打卡", "攻略"]):
            content_type = "旅行攻略"
        elif any(keyword in desc for keyword in ["护肤", "化妆", "彩妆", "保养"]):
            content_type = "美妆护肤"
        elif any(keyword in desc for keyword in ["健身", "运动", "减肥", "瑜伽"]):
            content_type = "健身运动"
        else:
            content_type = "生活分享"
        analysis_parts.append(f"属于{content_type}类型")

    # 综合效果描述
    if analysis_parts:
        analysis = "，".join(analysis_parts) + "，获得了较好的用户互动和传播效果"
    else:
        analysis = "内容吸引了用户的关注和互动"

    return analysis


def generate_html_from_template(keyword: str, articles: list, rank_date: str = "", top_n: int = 20, output: str = "./xhs_breaking_rankings.html") -> str:
    """使用模板生成HTML页面（只展示榜单数据）"""

    # 获取模板文件路径
    template_path = os.path.join(os.path.dirname(__file__), "../assets/preview-template.html")

    # 读取模板
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except Exception as e:
        print(f"错误：无法读取模板文件 {template_path}: {str(e)}", file=sys.stderr)
        return ""

    # 生成笔记列表HTML
    articles_html = ""
    for i, article in enumerate(articles[:top_n], 1):
        articles_html += get_article_html(article, i)

    # 生成更新时间：使用榜单日期，固定19:30
    if rank_date:
        try:
            dt = datetime.strptime(rank_date, "%Y-%m-%d")
            update_time = f"{dt.year}年-{dt.month:02d}-{dt.day:02d} 19:30"
        except:
            update_time = f"{rank_date} 19:30"
    else:
        dt = datetime.now()
        update_time = f"{dt.year}年-{dt.month:02d}-{dt.day:02d} 19:30"

    # 替换模板变量
    html_content = template.replace("{{KEYWORD}}", keyword)
    html_content = html_content.replace("{{TOP_N}}", str(top_n))
    html_content = html_content.replace("{{UPDATE_TIME}}", update_time)
    html_content = html_content.replace("{{ARTICLES_HTML}}", articles_html)

    # 写入输出文件
    try:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML文件已生成: {output}", file=sys.stderr)
    except Exception as e:
        print(f"错误：无法写入HTML文件 {output}: {str(e)}", file=sys.stderr)
        return ""

    return html_content


def main():
    parser = argparse.ArgumentParser(description="生成小红书冷门爆款内容HTML页面")
    parser.add_argument("--keyword", required=True, help="关键词")
    parser.add_argument("--articles", required=True, help="文章数据（JSON格式）")
    parser.add_argument("--rank_date", required=False, default="", help="榜单日期（yyyy-MM-dd格式）")
    parser.add_argument("--output", required=False, default="./xhs_breaking_rankings.html", help="输出HTML文件路径")
    parser.add_argument("--top_n", type=int, default=20, help="显示前N条数据")

    args = parser.parse_args()

    try:
        # 解析articles数据
        if isinstance(args.articles, str):
            articles = json.loads(args.articles)
        else:
            articles = args.articles

        if not isinstance(articles, list):
            print("错误：articles参数必须是JSON数组格式", file=sys.stderr)
            return 1

        # 生成HTML（只展示榜单数据）
        html_content = generate_html_from_template(
            keyword=args.keyword,
            articles=articles,
            rank_date=args.rank_date,
            top_n=args.top_n,
            output=args.output
        )

        if not html_content:
            print("错误：HTML生成失败", file=sys.stderr)
            return 1

        # 输出JSON格式的结果
        result = {
            "status": "success",
            "output_file": args.output,
            "article_count": len(articles),
            "top_n": args.top_n,
            "keyword": args.keyword
        }
        print(json.dumps(result, ensure_ascii=False))

        return 0

    except json.JSONDecodeError as e:
        print(f"错误：JSON解析失败: {str(e)}", file=sys.stderr)
        result = {
            "status": "error",
            "message": f"JSON解析失败: {str(e)}"
        }
        print(json.dumps(result, ensure_ascii=False))
        return 1
    except Exception as e:
        print(f"错误：{str(e)}", file=sys.stderr)
        result = {
            "status": "error",
            "message": str(e)
        }
        print(json.dumps(result, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
