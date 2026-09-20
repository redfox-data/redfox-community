#!/usr/bin/env python3
"""
小红书涨粉榜图片生成脚本（一键查询+生成表格图片）
"""

import argparse
import json
import sys
import os
from datetime import datetime, timedelta

# 导入查询和图表生成模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from query_rankings import RankingAPIClient
from generate_chart import TableChartGenerator


def generate_ranking_image(
    category: str = None,
    stat_type: str = 'daily',
    stat_date: str = None,
    limit: int = 20,
    output_path: str = None,
    title: str = None,
    subtitle: str = None,
    api_key: str = None
) -> str:
    """
    一键生成涨粉榜图片
    
    Args:
        category: 账号类型（如：化妆美容、穿搭、美食）
        stat_type: 统计类型（daily/weekly/monthly）
        stat_date: 统计日期（YYYY-MM-DD），None表示昨天
        limit: 返回条数（最大100）
        output_path: 输出文件路径，None则自动生成
        title: 图片标题，None则自动生成
        subtitle: 图片副标题，None则自动生成
        api_key: redfox.hk 平台 API Key，None时读取环境变量 REDFOX_API_KEY
        
    Returns:
        生成的图片路径
    """
    # 0. 校验类目
    client = RankingAPIClient(api_key=api_key)
    is_valid, error_msg = client.validate_category(category)
    if not is_valid:
        print(f"❌ {error_msg}")
        return None
    
    # 1. 查询数据
    print(f"正在查询数据...")
    data = client.query_rankings(
        category=category,
        stat_type=stat_type,
        stat_date=stat_date,
        limit=limit
    )
    
    if not data:
        print("错误：未获取到数据，请检查日期和分类参数")
        return None
    
    print(f"获取到 {len(data)} 条数据")
    
    # 2. 生成标题
    if not title:
        title = "小红书涨粉榜"
    
    if not subtitle:
        type_names = {'daily': '日榜', 'weekly': '周榜', 'monthly': '月榜'}
        type_name = type_names.get(stat_type, '榜单')
        cat_text = category if category else '全品类'
        subtitle = f"{cat_text}{type_name}TOP{limit}"
    
    # 3. 生成输出路径
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        cat_suffix = category if category else 'all'
        output_path = f"小红书涨粉榜_{cat_suffix}_{stat_type}_{timestamp}.png"
    
    # 4. 生成图片
    print(f"正在生成图片...")
    generator = TableChartGenerator()
    result = generator.generate_ranking_table(
        data=data,
        title=title,
        subtitle=subtitle,
        output_path=output_path,
        max_rows=limit
    )
    
    if result:
        print(f"图片已生成：{result}")
        # 尝试复制到桌面
        desktop_path = os.path.expanduser("~/Desktop")
        if os.path.exists(desktop_path):
            desktop_file = os.path.join(desktop_path, os.path.basename(result))
            try:
                import shutil
                shutil.copy(result, desktop_file)
                print(f"已复制到桌面：{desktop_file}")
            except Exception as e:
                print(f"复制到桌面失败：{e}")
        return result
    else:
        print("图片生成失败")
        return None


def main():
    # 支持的类目列表
    VALID_CATEGORIES = [
        '综合全部', '出行代步', '医疗保健', '休闲爱好', '综合杂项',
        '婚庆婚礼', '居家装修', '影视娱乐', '星座情感', '拍摄记录',
        '学习教育', '旅行度假', '亲子育儿', '日常生活', '科学探索',
        '数码科技', '时尚穿搭', '化妆美容', '个人护理', '美味佳肴',
        '职业发展', '宠物天地', '新闻资讯', '体育锻炼', '潮流鞋包'
    ]
    
    parser = argparse.ArgumentParser(
        description='小红书涨粉榜图片生成（一键查询+生成表格图片）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
支持的类目（共25个）：
  综合全部（默认推荐）、出行代步、医疗保健、休闲爱好、综合杂项、
  婚庆婚礼、居家装修、影视娱乐、星座情感、拍摄记录、学习教育、
  旅行度假、亲子育儿、日常生活、科学探索、数码科技、时尚穿搭、
  化妆美容、个人护理、美味佳肴、职业发展、宠物天地、新闻资讯、
  体育锻炼、潮流鞋包

示例:
  # 生成综合全部日榜TOP20图片（推荐）
  python3 generate_ranking_image.py --category 综合全部 --limit 20
  
  # 生成化妆美容类日榜TOP10图片
  python3 generate_ranking_image.py --category 化妆美容 --limit 10
  
  # 生成星座情感类周榜TOP20图片
  python3 generate_ranking_image.py --category 星座情感 --type weekly --limit 20
  
  # 生成指定日期的榜单
  python3 generate_ranking_image.py --category 综合全部 --date 2026-04-14 --limit 20
  
  # 自定义标题
  python3 generate_ranking_image.py --category 化妆美容 --title "美妆博主涨粉榜" --subtitle "4月14日涨粉最快的博主"

注意：
  - 仅支持上述25个固定类目，不支持自定义关键词
  - 单个榜单最多显示100条数据
        """
    )
    
    parser.add_argument('--category', type=str, default='综合全部',
                       help='账号类型（默认：综合全部）')
    parser.add_argument('--type', type=str, default='daily',
                       choices=['daily', 'weekly', 'monthly'],
                       help='统计类型（默认：daily）')
    parser.add_argument('--date', type=str,
                       help='统计日期(YYYY-MM-DD)，默认昨天')
    parser.add_argument('--limit', type=int, default=20,
                       help='显示条数（默认：20，最大：100）')
    parser.add_argument('--output', type=str,
                       help='输出文件路径，默认自动生成')
    parser.add_argument('--title', type=str,
                       help='图片标题，默认"小红书涨粉榜"')
    parser.add_argument('--subtitle', type=str,
                       help='图片副标题，默认自动生成')
    parser.add_argument('--api-key', type=str,
                       help='redfox.hk 平台 API Key（优先级：本参数 > 环境变量 REDFOX_API_KEY > shell 配置文件）')
    
    args = parser.parse_args()
    
    result = generate_ranking_image(
        category=args.category,
        stat_type=args.type,
        stat_date=args.date,
        limit=args.limit,
        output_path=args.output,
        title=args.title,
        subtitle=args.subtitle,
        api_key=args.api_key
    )
    
    if result:
        print(f"\n✅ 完成！图片路径：{result}")
        sys.exit(0)
    else:
        print("\n❌ 生成失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
