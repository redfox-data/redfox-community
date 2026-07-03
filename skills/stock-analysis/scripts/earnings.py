#!/usr/bin/env python3
"""
财报点评 — 按大V风格解读财报
================================
输入标的名称和财报数据，按大V的分析框架和表达风格生成财报点评任务。
长线大V侧重：护城河、ROE趋势、自由现金流；
短线大V侧重：业绩超预期幅度、资金反应、短期催化。

Usage:
    python earnings.py --author "格兰投研" --stock "贵州茅台" --data earnings.json
    python earnings.py --author "财躺平" --stock "宁德时代"
    python earnings.py --author "终身黑白" --stock "招商银行" --manual
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from common import (
    STOCK_ANALYSTS, PROFILES_DIR, OUTPUT_DIR,
    GREEN, YELLOW, RED, CYAN, BOLD, RESET,
    info, warn, error, step,
    find_profile, detect_trading_type, ensure_output_dir,
)


# ─── 财报数据输入 ──────────────────────────────────────────────────────────────────
def manual_input(stock):
    """手动输入财报数据"""
    print(f"\n{BOLD}请输入{stock}财报核心数据：{RESET}\n")

    data = {"stock": stock, "source": "manual"}

    data["report_period"] = input("报告期（如：2025年年报 / 2026Q1）: ").strip()
    data["revenue"] = input("营业收入（亿元，如：1505.6）: ").strip()
    data["revenue_yoy"] = input("营收同比增速%（如：+12.5）: ").strip()
    data["net_profit"] = input("归母净利润（亿元，如：747.3）: ").strip()
    data["net_profit_yoy"] = input("净利润同比增速%（如：+15.2）: ").strip()
    data["roe"] = input("ROE%（如：30.2）: ").strip()
    data["gross_margin"] = input("毛利率%（如：91.5）: ").strip()
    data["pe"] = input("当前PE（如：28.5）: ").strip()
    data["pb"] = input("当前PB（如：8.2）: ").strip()
    data["dividend_yield"] = input("股息率%（如：2.1）: ").strip()
    data["fcf"] = input("自由现金流（亿元，如：680）: ").strip()
    data["highlights"] = input("亮点/超预期点（简述）: ").strip()
    data["risks"] = input("风险/低于预期点（简述）: ").strip()
    data["guidance"] = input("公司指引/展望（简述）: ").strip()

    return data


def load_earnings_data(data_path, stock):
    """加载财报数据JSON"""
    f = Path(data_path)
    if not f.exists():
        error(f"财报数据文件不存在：{data_path}")
        return None
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
        if "stock" not in data:
            data["stock"] = stock
        info(f"已加载财报数据：{f.name}")
        return data
    except Exception as e:
        error(f"读取财报数据失败：{e}")
        return None


# ─── 长线分析框架 ──────────────────────────────────────────────────────────────────
LONG_ANALYSIS_FRAMEWORK = """
### 长线投资者分析框架

#### 1. 生意本质
- 商业模式是否简单可理解？
- 产品/服务的护城河类型（品牌/网络效应/成本优势/转换成本）
- 竞争格局是否稳定？

#### 2. 财务质量
- ROE 趋势（连续3年 > 15%？）
- 毛利率稳定性
- 自由现金流是否充裕？
- 资产负债率是否健康？

#### 3. 成长性
- 营收增速趋势
- 净利润增速与营收增速是否匹配
- 增长驱动因素（量增/价增/新业务）

#### 4. 估值判断
- PE/PB 历史分位
- 相对增速的PEG
- 股息率吸引力

#### 5. 风险识别
- 管理层变动
- 行业政策变化
- 竞争加剧信号
"""

# ─── 短线分析框架 ──────────────────────────────────────────────────────────────────
SHORT_ANALYSIS_FRAMEWORK = """
### 短线交易者分析框架

#### 1. 业绩预期差
- 营收/净利润是否超市场预期？
- 超预期幅度（> 10% 为显著超预期）
- 市场对业绩的预期是否已充分定价？

#### 2. 资金反应预判
- 业绩公布后可能的股价反应
- 机构资金动向（是否提前布局）
- 游资可能的炒作方向

#### 3. 短期催化
- 财报中的催化事件（分红/回购/新订单/产能释放）
- 行业政策催化
- 技术面配合度

#### 4. 交易信号
- 业绩公布前后是否适合介入
- 支撑位和压力位
- 止损位设定

#### 5. 情绪判断
- 当前市场对标的的情绪（过热/冷淡/分歧）
- 业绩对情绪的边际影响
"""


# ─── 生成任务文件 ──────────────────────────────────────────────────────────────────
def generate_earnings_task(author, profile, trading_type, stock, earnings_data):
    today = datetime.now().strftime("%Y-%m-%d")

    lines = []
    lines.append(f"# {author} 风格化财报点评任务 — {stock}")
    lines.append(f"> 日期：{today}")
    lines.append(f"> 标的：{stock}")
    lines.append(f"> 交易类型：{trading_type}")
    lines.append(f"> ⚠️ AI 风格模拟，不构成投资建议\n")

    lines.append("## 1. 风格画像摘要\n")
    if profile:
        lines.append(f"```\n{profile[:2000]}\n```\n")
    else:
        lines.append("未找到风格画像，使用默认分析框架。\n")

    lines.append("## 2. 财报数据\n")
    if earnings_data:
        lines.append("| 指标 | 数值 |")
        lines.append("|------|------|")

        field_labels = {
            "report_period": "报告期",
            "revenue": "营业收入（亿元）",
            "revenue_yoy": "营收同比增速%",
            "net_profit": "归母净利润（亿元）",
            "net_profit_yoy": "净利润同比增速%",
            "roe": "ROE%",
            "gross_margin": "毛利率%",
            "pe": "PE",
            "pb": "PB",
            "dividend_yield": "股息率%",
            "fcf": "自由现金流（亿元）",
            "highlights": "亮点/超预期",
            "risks": "风险/低于预期",
            "guidance": "公司指引/展望",
        }

        for key, label in field_labels.items():
            val = earnings_data.get(key)
            if val:
                lines.append(f"| {label} | {val} |")
        lines.append("")

        # 额外字段
        for key, val in earnings_data.items():
            if key not in field_labels and key not in ("stock", "source"):
                lines.append(f"- **{key}**：{val}")
        lines.append("")
    else:
        lines.append("**未提供财报数据。**\n")
        lines.append("请用户提供以下核心数据（至少）：")
        lines.append("- 营收及同比增速")
        lines.append("- 净利润及同比增速")
        lines.append("- ROE")
        lines.append("- PE/PB\n")

    lines.append("## 3. 分析框架\n")
    if trading_type in ("long", "mixed"):
        lines.append(LONG_ANALYSIS_FRAMEWORK)
    if trading_type in ("short", "mixed"):
        lines.append(SHORT_ANALYSIS_FRAMEWORK)

    lines.append("## 4. 生成要求\n")
    lines.append(f"请按{author}的表达风格和分析框架，生成一篇财报点评文章：\n")

    if trading_type == "short":
        lines.append("- 标题突出业绩超预期/低于预期的核心信号")
        lines.append("- 开头直接给出结论（超预期还是低于预期）")
        lines.append("- 重点分析资金面可能的反应")
        lines.append("- 给出短期交易信号和操作建议")
        lines.append("- 包含风险提示\n")
    else:
        lines.append("- 标题体现长线视角（如：护城河是否加深）")
        lines.append("- 开头阐述生意本质和核心逻辑")
        lines.append("- 深入分析财务质量和成长持续性")
        lines.append("- 给出估值判断和安全边际")
        lines.append("- 包含长期风险识别\n")

    lines.append("### 风格要求")
    lines.append("- 使用大V的标志性表达")
    lines.append("- 按大V的文章结构组织")
    lines.append("- 字数参考大V平均字数\n")

    lines.append("## 5. 合规要求\n")
    lines.append("- 标注：「AI 风格模拟，不构成投资建议」")
    lines.append("- 财报数据引用需标注来源")
    lines.append("- 不直接荐股，仅分析逻辑\n")

    lines.append(f"## 6. 输出")
    lines.append(f"保存到：`output/{author}_{stock}财报_{today}.md`\n")

    return "\n".join(lines)


# ─── 主流程 ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="财报点评 — 按大V风格解读财报")
    parser.add_argument("--author", required=True, help="指定大V名称")
    parser.add_argument("--stock", required=True, help="标的名称（如：贵州茅台）")
    parser.add_argument("--data", help="财报数据JSON文件路径")
    parser.add_argument("--manual", action="store_true", help="手动输入财报数据")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="输出目录")

    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 加载画像
    step(f"加载画像：{args.author}")
    profile = find_profile(args.author)
    trading_type = detect_trading_type(profile)
    if profile:
        info(f"画像已加载，交易类型：{trading_type}")
    else:
        warn(f"未找到{args.author}的风格画像，使用默认分析")

    # 加载财报数据
    earnings_data = None
    if args.manual:
        earnings_data = manual_input(args.stock)
    elif args.data:
        earnings_data = load_earnings_data(args.data, args.stock)

    if not earnings_data and not args.manual:
        warn("未提供财报数据，可指定 --data 或使用 --manual 手动输入")
        warn("将生成空模板任务文件")

    # 生成任务
    task = generate_earnings_task(args.author, profile, trading_type, args.stock, earnings_data)
    today = datetime.now().strftime("%Y-%m-%d")
    task_file = output_dir / f"{args.author}_{args.stock}财报任务_{today}.md"
    task_file.write_text(task, encoding="utf-8")
    info(f"财报点评任务已保存：{task_file}")

    # 显示摘要
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  财报点评摘要{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"  大V：{args.author}（{trading_type}）")
    print(f"  标的：{args.stock}")
    print(f"  财报数据：{'已提供' if earnings_data else '未提供'}")

    if earnings_data:
        print(f"\n{BOLD}核心数据：{RESET}")
        for key in ["revenue", "revenue_yoy", "net_profit", "net_profit_yoy", "roe"]:
            val = earnings_data.get(key)
            if val:
                print(f"  {key}: {val}")

    print(f"\n{GREEN}✓{RESET} 任务文件：{task_file}")


if __name__ == "__main__":
    main()
