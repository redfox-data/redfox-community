#!/usr/bin/env python3
"""
小红书涨粉榜图表生成脚本
支持柱状图、折线图、组合图以及表格样式排名图
"""

import argparse
import json
import sys
from typing import List, Dict, Optional
from datetime import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import textwrap

try:
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    from matplotlib.ticker import FuncFormatter
    import numpy as np
except ImportError:
    pass


class TableChartGenerator:
    """表格样式排名图生成器（类似示例图片风格）"""
    
    # 小红书风格配色
    COLORS = {
        'title_red': '#FF2442',        # 小红书红
        'header_orange': '#FF6B35',    # 表头橙色
        'text_dark': '#333333',        # 深色文字
        'text_gray': '#666666',        # 灰色文字
        'bg_white': '#FFFFFF',         # 白色背景
        'border_gray': '#E8E8E8',      # 边框灰
        'row_alt': '#FFF8F5',          # 交替行浅橙
        'highlight_red': '#FF2442',    # 高亮红色
    }
    
    def __init__(self, font_path: Optional[str] = None):
        """初始化，尝试加载中文字体"""
        self.font_path = font_path
        self.fonts = self._load_fonts()
    
    def _load_fonts(self) -> Dict:
        """加载字体，返回不同大小的字体"""
        fonts = {}
        
        # 尝试常见中文字体
        chinese_fonts = [
            '/System/Library/Fonts/PingFang.ttc',  # macOS 苹方
            '/System/Library/Fonts/STHeiti Light.ttc',  # macOS 黑体
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',  # Linux 文泉驿
            'C:/Windows/Fonts/simhei.ttf',  # Windows 黑体
            'C:/Windows/Fonts/simsun.ttc',  # Windows 宋体
        ]
        
        font_file = self.font_path
        if not font_file:
            for f in chinese_fonts:
                try:
                    ImageFont.truetype(f, 12)
                    font_file = f
                    break
                except:
                    continue
        
        if not font_file:
            font_file = None  # 使用默认字体
        
        # 定义不同大小的字体
        sizes = {
            'title': 48,
            'subtitle': 28,
            'header': 24,
            'body': 20,
            'small': 16,
            'rank': 32,
        }
        
        for name, size in sizes.items():
            try:
                if font_file:
                    fonts[name] = ImageFont.truetype(font_file, size)
                else:
                    fonts[name] = ImageFont.load_default()
            except:
                fonts[name] = ImageFont.load_default()
        
        return fonts
    
    def format_number(self, num: int) -> str:
        """格式化数字"""
        if num >= 10000:
            return f'{num/10000:.1f}万'
        return str(num)
    
    def generate_ranking_table(
        self,
        data: List[Dict],
        title: str = "小红书涨粉榜",
        subtitle: str = "昨日涨粉最快的博主",
        output_path: str = 'ranking_table.png',
        max_rows: int = 20
    ) -> str:
        """
        生成表格样式排名图
        
        Args:
            data: 排名数据列表
            title: 大标题
            subtitle: 副标题
            output_path: 输出路径
            max_rows: 最大显示行数
            
        Returns:
            输出文件路径
        """
        if not data:
            return None
        
        # 限制行数
        data = data[:max_rows]
        
        # 图片尺寸
        width = 900
        header_height = 180
        row_height = 70
        footer_height = 60
        height = header_height + row_height * (len(data) + 1) + footer_height  # +1 for header row
        
        # 创建图片
        img = Image.new('RGB', (width, height), self.COLORS['bg_white'])
        draw = ImageDraw.Draw(img)
        
        # 绘制标题区域
        self._draw_header(draw, width, header_height, title, subtitle)
        
        # 绘制表头
        y = header_height
        self._draw_table_header(draw, width, row_height, y)
        y += row_height
        
        # 绘制数据行
        for idx, item in enumerate(data):
            is_alt = idx % 2 == 1
            self._draw_table_row(draw, width, row_height, y, item, idx + 1, is_alt)
            y += row_height
        
        # 绘制底部信息
        self._draw_footer(draw, width, footer_height, height - footer_height)
        
        # 保存图片
        img.save(output_path, 'PNG', quality=95)
        return output_path
    
    def _draw_header(self, draw: ImageDraw, width: int, height: int, title: str, subtitle: str):
        """绘制标题区域"""
        # 主标题（红色大字）
        title_font = self.fonts.get('title')
        bbox = draw.textbbox((0, 0), title, font=title_font)
        title_w = bbox[2] - bbox[0]
        x = (width - title_w) // 2
        draw.text((x, 30), title, font=title_font, fill=self.COLORS['title_red'])
        
        # 副标题（黑色粗体）
        subtitle_font = self.fonts.get('subtitle')
        bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_w = bbox[2] - bbox[0]
        x = (width - subtitle_w) // 2
        draw.text((x, 100), subtitle, font=subtitle_font, fill=self.COLORS['text_dark'])
    
    def _draw_table_header(self, draw: ImageDraw, width: int, row_height: int, y: int):
        """绘制表头"""
        # 表头背景（橙色）
        draw.rectangle([(0, y), (width, y + row_height)], fill=self.COLORS['header_orange'])
        
        # 列宽定义
        col_widths = [80, 280, 160, 160, 160]
        headers = ['排名', '达人名称', '粉丝数', '涨粉数', '涨粉率']
        
        x = 0
        header_font = self.fonts.get('header')
        for i, (header, col_w) in enumerate(zip(headers, col_widths)):
            # 文字居中
            bbox = draw.textbbox((0, 0), header, font=header_font)
            text_w = bbox[2] - bbox[0]
            text_x = x + (col_w - text_w) // 2
            text_y = y + (row_height - 24) // 2
            draw.text((text_x, text_y), header, font=header_font, fill=self.COLORS['bg_white'])
            x += col_w
    
    def _draw_table_row(self, draw: ImageDraw, width: int, row_height: int, y: int, 
                       item: Dict, rank: int, is_alt: bool):
        """绘制数据行"""
        # 交替行背景色
        if is_alt:
            draw.rectangle([(0, y), (width, y + row_height)], fill=self.COLORS['row_alt'])
        
        # 底部边框
        draw.line([(0, y + row_height), (width, y + row_height)], fill=self.COLORS['border_gray'], width=1)
        
        # 列宽定义
        col_widths = [80, 280, 160, 160, 160]
        
        # 获取数据
        name = item.get('account_name', 'Unknown')[:12]  # 限制长度
        followers = self.format_number(item.get('followers_count', 0))
        growth = self.format_number(item.get('growth_count', 0))
        rate = f"{item.get('growth_rate', 0):.2f}%"
        
        # 排名（红色圆圈或红色文字）
        rank_font = self.fonts.get('rank')
        rank_color = self.COLORS['highlight_red'] if rank <= 3 else self.COLORS['text_dark']
        bbox = draw.textbbox((0, 0), str(rank), font=rank_font)
        text_w = bbox[2] - bbox[0]
        text_x = (col_widths[0] - text_w) // 2
        text_y = y + (row_height - 32) // 2
        draw.text((text_x, text_y), str(rank), font=rank_font, fill=rank_color)
        
        # 达人名称
        x = col_widths[0]
        name_font = self.fonts.get('body')
        text_y = y + (row_height - 20) // 2
        draw.text((x + 20, text_y), name, font=name_font, fill=self.COLORS['text_dark'])
        
        # 粉丝数
        x += col_widths[1]
        bbox = draw.textbbox((0, 0), followers, font=name_font)
        text_w = bbox[2] - bbox[0]
        text_x = x + (col_widths[2] - text_w) // 2
        draw.text((text_x, text_y), followers, font=name_font, fill=self.COLORS['text_dark'])
        
        # 涨粉数（红色高亮）
        x += col_widths[2]
        bbox = draw.textbbox((0, 0), growth, font=name_font)
        text_w = bbox[2] - bbox[0]
        text_x = x + (col_widths[3] - text_w) // 2
        draw.text((text_x, text_y), growth, font=name_font, fill=self.COLORS['highlight_red'])
        
        # 涨粉率
        x += col_widths[3]
        bbox = draw.textbbox((0, 0), rate, font=name_font)
        text_w = bbox[2] - bbox[0]
        text_x = x + (col_widths[4] - text_w) // 2
        draw.text((text_x, text_y), rate, font=name_font, fill=self.COLORS['text_dark'])
    
    def _draw_footer(self, draw: ImageDraw, width: int, height: int, y: int):
        """绘制底部信息"""
        footer_font = self.fonts.get('small')
        text = "数据来源：小红书 | 统计时间：昨日"
        bbox = draw.textbbox((0, 0), text, font=footer_font)
        text_w = bbox[2] - bbox[0]
        x = (width - text_w) // 2
        draw.text((x, y + 20), text, font=footer_font, fill=self.COLORS['text_gray'])


class ChartGenerator:
    """传统图表生成器（matplotlib）"""
    
    COLORS = {
        'primary': '#FF2442',
        'secondary': '#FF6B8A',
        'accent': '#FFB8C5',
        'text': '#333333',
        'text_light': '#666666',
        'grid': '#E8E8E8',
        'background': '#FAFAFA',
    }
    
    def __init__(self, font_path: Optional[str] = None):
        self.setup_font(font_path)
        try:
            plt.style.use('seaborn-v0_8-whitegrid')
        except:
            pass
        
    def setup_font(self, font_path: Optional[str] = None):
        """设置中文字体"""
        if font_path:
            prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = prop.get_name()
        else:
            chinese_fonts = ['PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
            try:
                available_fonts = [f.name for f in fm.fontManager.ttflist]
                for font in chinese_fonts:
                    if font in available_fonts:
                        plt.rcParams['font.family'] = font
                        break
            except:
                pass
        plt.rcParams['axes.unicode_minus'] = False
    
    def format_number(self, num: int) -> str:
        """格式化数字显示"""
        if num >= 10000:
            return f'{num/10000:.1f}万'
        return str(num)
    
    def generate_bar_chart(
        self,
        data: List[Dict],
        title: str = '涨粉排行榜',
        output_path: str = 'ranking.png',
        figsize: tuple = (14, 8),
        show_values: bool = True,
        sort_by: str = 'growth_count'
    ) -> str:
        """生成柱状图"""
        if not data:
            return None
        
        names = [d.get('account_name', 'Unknown')[:10] for d in data[:20]]
        values = [d.get(sort_by, 0) for d in data[:20]]
        
        fig, ax = plt.subplots(figsize=figsize)
        fig.patch.set_facecolor(self.COLORS['background'])
        ax.set_facecolor(self.COLORS['background'])
        
        bars = ax.barh(range(len(names)), values, color=self.COLORS['primary'], 
                       edgecolor='white', linewidth=0.5)
        ax.invert_yaxis()
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names, fontsize=11)
        ax.set_xlabel('涨粉数', fontsize=12, color=self.COLORS['text'])
        ax.xaxis.set_major_formatter(FuncFormatter(lambda x, p: self.format_number(int(x))))
        
        if show_values:
            for i, (bar, val) in enumerate(zip(bars, values)):
                width = bar.get_width()
                ax.text(width + max(values) * 0.01, bar.get_y() + bar.get_height()/2,
                       self.format_number(val), ha='left', va='center', fontsize=9,
                       color=self.COLORS['text'])
        
        ax.set_title(title, fontsize=16, fontweight='bold', color=self.COLORS['text'], pad=20)
        ax.grid(axis='x', alpha=0.3, color=self.COLORS['grid'])
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        stat_date = data[0].get('stat_date', '')
        footer_text = f"数据来源：小红书 | 统计时间：{stat_date}"
        fig.text(0.99, 0.01, footer_text, ha='right', va='bottom', 
                fontsize=8, color=self.COLORS['text_light'])
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', 
                   facecolor=self.COLORS['background'])
        plt.close()
        
        return output_path


def main():
    parser = argparse.ArgumentParser(description='生成小红书涨粉榜图表')
    parser.add_argument('--type', type=str, default='table',
                       choices=['table', 'bar', 'trend'],
                       help='图表类型')
    parser.add_argument('--data', type=str, required=True,
                       help='数据文件路径(JSON)')
    parser.add_argument('--output', type=str, default='chart.png',
                       help='输出文件路径')
    parser.add_argument('--title', type=str, default='小红书涨粉榜',
                       help='图表标题')
    parser.add_argument('--subtitle', type=str, default='昨日涨粉最快的博主',
                       help='副标题')
    parser.add_argument('--font', type=str, help='中文字体路径')
    parser.add_argument('--limit', type=int, default=20, help='显示条数')
    
    args = parser.parse_args()
    
    # 加载数据
    with open(args.data, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if args.type == 'table':
        # 使用表格样式生成器
        generator = TableChartGenerator(font_path=args.font)
        output = generator.generate_ranking_table(
            data,
            title=args.title,
            subtitle=args.subtitle,
            output_path=args.output,
            max_rows=args.limit
        )
    elif args.type == 'bar':
        # 使用传统柱状图
        generator = ChartGenerator(font_path=args.font)
        output = generator.generate_bar_chart(
            data,
            title=args.title,
            output_path=args.output
        )
    else:
        print(f"Chart type '{args.type}' not yet implemented")
        sys.exit(1)
    
    if output:
        print(f"Chart saved to: {output}")
    else:
        print("Failed to generate chart")
        sys.exit(1)


if __name__ == '__main__':
    main()
