#!/usr/bin/env python3
"""
小红书涨粉榜数据导出为 Excel
"""

import argparse
import json
import sys
import os


def export_to_excel(data: list, output_path: str = None) -> str:
    """
    将榜单数据导出为 Excel 文件
    
    Args:
        data: 榜单数据列表
        output_path: 输出文件路径
        
    Returns:
        生成的 Excel 文件路径
    """
    try:
        import pandas as pd
    except ImportError:
        print("❌ 请先安装 pandas: pip install pandas openpyxl", file=sys.stderr)
        return None
    
    if not data:
        print("❌ 没有数据可导出", file=sys.stderr)
        return None
    
    # 准备数据
    rows = []
    for item in data:
        rows.append({
            '排名': item.get('ranking', 0),
            '账号名称': item.get('account_name', ''),
            '粉丝数': item.get('followers_count', 0),
            '涨粉数': item.get('growth_count', 0),
            '涨粉率(%)': item.get('growth_rate', 0),
            '类目': item.get('category', ''),
            '认证': item.get('verify_type', '') or item.get('official_cert', '')
        })
    
    # 创建 DataFrame
    df = pd.DataFrame(rows)
    
    # 生成输出路径
    if not output_path:
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"小红书涨粉榜_{timestamp}.xlsx"
    
    # 导出为 Excel
    try:
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"✅ Excel 文件已生成：{output_path}")
        
        # 尝试复制到桌面
        desktop_path = os.path.expanduser("~/Desktop")
        if os.path.exists(desktop_path):
            desktop_file = os.path.join(desktop_path, os.path.basename(output_path))
            import shutil
            shutil.copy(output_path, desktop_file)
            print(f"✅ 已复制到桌面：{desktop_file}")
        
        return output_path
    except Exception as e:
        print(f"❌ 导出失败：{e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description='小红书涨粉榜导出为 Excel')
    parser.add_argument('--data', type=str, required=True, help='JSON 数据文件路径')
    parser.add_argument('--output', type=str, help='输出 Excel 文件路径')
    
    args = parser.parse_args()
    
    # 读取 JSON 数据
    try:
        with open(args.data, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ 读取数据文件失败：{e}", file=sys.stderr)
        sys.exit(1)
    
    # 导出为 Excel
    result = export_to_excel(data, args.output)
    
    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
