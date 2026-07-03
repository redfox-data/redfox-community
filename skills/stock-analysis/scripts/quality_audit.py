#!/usr/bin/env python3
"""
质量审计脚本 — 校验生成内容是否符合大V风格画像
=================================================
对生成的文章进行9维质量检查，综合评分 > 70 分准出。

Usage:
    python quality_audit.py --article "output/财躺平_复盘_2026-01-15.md" --author "财躺平"
    python quality_audit.py --article "output/多V对比_2026-01-15.md"
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from common import (
    PROFILES_DIR, OUTPUT_DIR,
    GREEN, YELLOW, RED, CYAN, BOLD, RESET,
    info, warn, error, step,
    ensure_output_dir,
)

# 交易术语库
TRADING_TERMS = [
    "涨停", "跌停", "连板", "龙头", "游资", "情绪周期", "打板", "复盘", "盘面",
    "资金流向", "竞价", "龙虎榜", "妖股", "止损", "止盈", "仓位", "满仓", "清仓",
    "减仓", "加仓", "建仓", "空仓", "做多", "做空", "牛市", "熊市", "震荡",
    "放量", "缩量", "突破", "回调", "反弹", "趋势", "支撑", "压力", "均线",
    "K线", "MACD", "量价", "换手率", "成交额", "市值", "估值", "PE", "PB",
    "ROE", "护城河", "基本面", "技术面", "资金面", "消息面", "板块轮动",
]

# 盘面指标关键词
MARKET_INDICATORS = [
    "成交额", "成交量", "涨停", "跌停", "炸板", "连板", "换手率", "融资余额",
    "北向资金", "主力资金", "指数", "上证", "深证", "创业板", "科创",
]


# ─── 画像加载 ──────────────────────────────────────────────────────────────────────
from common import find_profile


def parse_profile_json(profile_text):
    """尝试将画像文本解析为JSON，返回 (profile_dict, is_json)"""
    try:
        data = json.loads(profile_text)
        return data, True
    except (json.JSONDecodeError, TypeError):
        return profile_text, False


# ─── 质量检查项 ────────────────────────────────────────────────────────────────────
def check_signature_phrases(article, profile):
    """检查标志性表达命中率"""
    phrases = []
    profile_data, is_json = parse_profile_json(profile)

    if is_json:
        # JSON格式：从 expression_style.标志性表达 中提取
        expr = profile_data.get("表达风格", {})
        sig_phrases = expr.get("标志性表达", [])
        if isinstance(sig_phrases, list):
            phrases = [p for p in sig_phrases if isinstance(p, str) and len(p) > 2]
        # 也从免责声明中提取
        disclaimer = expr.get("免责声明", "")
        if disclaimer and len(disclaimer) > 5:
            phrases.append(disclaimer)
    else:
        # 兼容旧版 markdown 格式
        table_matches = re.findall(r'\|\s*\d+\s*\|\s*(.+?)\s*\|\s*(\d+)次', profile)
        for match in table_matches:
            phrase = match[0].strip()
            if phrase and len(phrase) > 2:
                phrases.append(phrase)
        quote_matches = re.findall(r'[「"](.+?)[」"]', profile)
        for match in quote_matches:
            if len(match) > 2:
                phrases.append(match)

    # 去重
    phrases = list(dict.fromkeys(phrases))[:20]

    if not phrases:
        return {
            "name": "标志性表达命中率",
            "score": 0,
            "weight": 0.10,
            "detail": "画像中未提取到标志性表达",
            "pass": False,
        }

    # 检查命中率
    hits = 0
    hit_list = []
    for phrase in phrases:
        if phrase in article:
            hits += 1
            hit_list.append(phrase)

    hit_rate = hits / len(phrases) if phrases else 0
    passed = hit_rate > 0.40

    return {
        "name": "标志性表达命中率",
        "score": round(hit_rate * 100, 1),
        "weight": 0.10,
        "detail": f"命中 {hits}/{len(phrases)} 个标志性表达（{hit_rate:.0%}）",
        "hit_phrases": hit_list[:10],
        "pass": passed,
    }


def check_trading_system(article, profile):
    """检查交易体系覆盖度"""
    system_keywords = []
    profile_data, is_json = parse_profile_json(profile)

    if is_json:
        # JSON格式：从投资体系和市场判断中提取关键词
        inv = profile_data.get("投资体系", {})
        mkt = profile_data.get("市场判断", {})
        # 收集所有文本字段
        text_parts = []
        for key in ["核心流派", "选股逻辑", "止损纪律", "仓位管理", "持仓周期"]:
            val = inv.get(key, "")
            if isinstance(val, str):
                text_parts.append(val)
            elif isinstance(val, list):
                text_parts.extend(val)
        for key in ["研判方式", "风险偏好", "逆向思维"]:
            val = mkt.get(key, "")
            if isinstance(val, str):
                text_parts.append(val)
        # 提取中文关键词
        all_text = " ".join(text_parts)
        words = re.findall(r'[\u4e00-\u9fff]{2,6}', all_text)
        common_words = {"原文", "证据", "描述", "大V", "交易", "体系", "模式", "逻辑", "信号", "仓位", "管理"}
        system_keywords = [w for w in words if w not in common_words and len(w) >= 2][:30]
    else:
        # 兼容旧版 markdown 格式
        system_section = re.search(r'## 1\..*?(?=## 2\.|$)', profile, re.DOTALL)
        if system_section:
            text = system_section.group()
            words = re.findall(r'[\u4e00-\u9fff]{2,6}', text)
            common_words = {"原文", "证据", "描述", "大V", "交易", "体系", "模式", "逻辑", "信号", "仓位", "管理"}
            system_keywords = [w for w in words if w not in common_words and len(w) >= 2][:30]

    if not system_keywords:
        system_keywords = ["选股", "买入", "卖出", "止损", "止盈", "仓位", "龙头", "趋势", "突破", "回调"]

    # 检查覆盖度
    hits = 0
    for kw in system_keywords:
        if kw in article:
            hits += 1

    coverage = hits / len(system_keywords) if system_keywords else 0
    passed = coverage > 0.70

    return {
        "name": "交易体系覆盖度",
        "score": round(coverage * 100, 1),
        "weight": 0.10,
        "detail": f"覆盖 {hits}/{len(system_keywords)} 个交易体系关键词",
        "pass": passed,
    }


def check_article_structure(article, profile):
    """检查文章结构匹配度"""
    # 检查文章是否包含基本结构元素
    structure_elements = {
        "开头": bool(re.match(r'^#|^\*\*|^[^\n]{10,}', article.strip())),
        "正文分段": article.count('\n\n') >= 3,
        "小标题": bool(re.search(r'^##\s', article, re.MULTILINE)),
        "结尾": article.strip()[-100:].strip() != "",
        "免责声明": any(kw in article for kw in ["免责", "不构成", "投资建议", "AI风格模拟"]),
    }

    matched = sum(1 for v in structure_elements.values() if v)
    total = len(structure_elements)
    match_rate = matched / total

    passed = match_rate > 0.60

    return {
        "name": "文章结构匹配度",
        "score": round(match_rate * 100, 1),
        "weight": 0.10,
        "detail": f"匹配 {matched}/{total} 个结构元素",
        "elements": {k: "✓" if v else "✗" for k, v in structure_elements.items()},
        "pass": passed,
    }


def check_market_indicators(article):
    """检查盘面指标覆盖"""
    hits = []
    for indicator in MARKET_INDICATORS:
        if indicator in article:
            hits.append(indicator)

    coverage = len(hits) / len(MARKET_INDICATORS) if MARKET_INDICATORS else 0
    passed = coverage > 0.50

    return {
        "name": "盘面指标覆盖",
        "score": round(coverage * 100, 1),
        "weight": 0.10,
        "detail": f"覆盖 {len(hits)}/{len(MARKET_INDICATORS)} 个盘面指标",
        "hit_indicators": hits,
        "pass": passed,
    }


def check_tone_consistency(article, profile):
    """检查语气一致性"""
    # 简化版语气检测
    tone_markers = {
        "感叹句": len(re.findall(r'[！!]', article)),
        "疑问句": len(re.findall(r'[？?]', article)),
        "第一人称": len(re.findall(r'[我][们]?', article)),
        "口语化": len(re.findall(r'[吧呢啊嘛哦哈嘿]', article)),
    }

    # 从画像中提取语气特征
    profile_data, is_json = parse_profile_json(profile)
    if is_json:
        expr = profile_data.get("表达风格", {})
        tone_text = expr.get("语气", "") + " " + expr.get("文风温度", "")
    else:
        tone_section = re.search(r'语气.*?人称', profile, re.DOTALL)
        tone_text = tone_section.group() if tone_section else ""

    # 简化判断：检查文章是否有语气特征
    tone_count = sum(tone_markers.values())
    has_tone = tone_count > 5

    # 偏差计算：有语气特征得低偏差（通过），无语气特征得高偏差（不通过）
    if has_tone:
        # 语气标记充足，偏差低；语气越丰富偏差越低
        deviation = max(0.05, 0.15 - (tone_count - 5) * 0.01)
    else:
        # 语气标记不足，偏差高
        deviation = min(0.5, 0.30 + (5 - tone_count) * 0.04)

    passed = deviation <= 0.20

    return {
        "name": "语气一致性",
        "score": round((1 - deviation) * 100, 1),
        "weight": 0.10,
        "detail": f"语气标记：{tone_markers}",
        "pass": passed,
    }


def check_word_count(article, profile):
    """检查字数范围"""
    target_avg = 3000  # 默认
    profile_data, is_json = parse_profile_json(profile)

    if is_json:
        depth = profile_data.get("内容深度", {})
        avg_words = depth.get("平均字数", None)
        if avg_words and isinstance(avg_words, (int, float)):
            target_avg = int(avg_words)
    else:
        avg_match = re.search(r'平均字数[：:]\s*(\d+)', profile)
        if avg_match:
            target_avg = int(avg_match.group(1))

    # 计算文章字数（去除markdown标记）
    clean = re.sub(r'[#*`\[\](){}|>]', '', article)
    clean = re.sub(r'\n+', '', clean)
    actual_count = len(clean.strip())

    deviation = abs(actual_count - target_avg) / target_avg if target_avg > 0 else 1
    passed = deviation < 0.30

    return {
        "name": "字数范围",
        "score": round((1 - min(deviation, 1)) * 100, 1),
        "weight": 0.10,
        "detail": f"实际{actual_count}字，目标{target_avg}字（偏差{deviation:.0%}）",
        "pass": passed,
    }


def check_trading_terms(article):
    """检查交易术语覆盖"""
    hits = []
    for term in TRADING_TERMS:
        if term in article:
            hits.append(term)

    coverage = len(hits) / len(TRADING_TERMS) if TRADING_TERMS else 0
    passed = coverage > 0.50

    return {
        "name": "交易术语覆盖",
        "score": round(coverage * 100, 1),
        "weight": 0.10,
        "detail": f"覆盖 {len(hits)}/{len(TRADING_TERMS)} 个交易术语",
        "hit_terms": hits[:10],
        "pass": passed,
    }


# ─── 思维层检查（7-9） ────────────────────────────────────────────────────────────

def check_core_thinking(article, profile):
    """检查核心思维匹配度——文章是否体现了大V的分析思维框架"""
    profile_data, is_json = parse_profile_json(profile)
    if not is_json:
        return {"name": "核心思维匹配度", "score": 50, "weight": 0.15,
                "detail": "非JSON画像，跳过", "pass": True}

    inv = profile_data.get("投资体系", {})
    tools = inv.get("核心分析工具", [])
    if not tools:
        return {"name": "核心思维匹配度", "score": 0, "weight": 0.15,
                "detail": "画像中未找到核心分析工具", "pass": False}

    # 从核心分析工具中提取思维关键词
    thinking_keywords = []
    for tool in tools:
        words = re.findall(r'[\u4e00-\u9fff]{2,6}', tool)
        thinking_keywords.extend([w for w in words if len(w) >= 2])

    # 去重后取前20个
    seen = set()
    unique_kw = []
    for w in thinking_keywords:
        if w not in seen:
            seen.add(w)
            unique_kw.append(w)
    thinking_keywords = unique_kw[:20]

    if not thinking_keywords:
        return {"name": "核心思维匹配度", "score": 0, "weight": 0.15,
                "detail": "未能提取思维关键词", "pass": False}

    hits = [kw for kw in thinking_keywords if kw in article]
    coverage = len(hits) / len(thinking_keywords)
    passed = coverage > 0.60

    return {
        "name": "核心思维匹配度",
        "score": round(coverage * 100, 1),
        "weight": 0.15,
        "detail": f"思维关键词覆盖 {len(hits)}/{len(thinking_keywords)}（{coverage:.0%}）",
        "hit_phrases": hits[:10],
        "pass": passed,
    }


def check_argumentation_style(article, profile):
    """检查论证方式匹配——文章是否按大V特有的论述模式展开"""
    profile_data, is_json = parse_profile_json(profile)
    if not is_json:
        return {"name": "论证方式匹配", "score": 50, "weight": 0.15,
                "detail": "非JSON画像，跳过", "pass": True}

    author_name = profile_data.get("大V名称", "")
    expr = profile_data.get("表达风格", {})

    # 提取开头和结尾模式关键字作为论证链标记
    opening = expr.get("开头模式", "")
    closing = expr.get("结尾模式", "")
    structure = expr.get("文章结构", "")

    # 从结构描述中提取论证步骤关键词
    arg_keywords_text = f"{opening} {closing} {structure}"
    words = re.findall(r'[\u4e00-\u9fff]{2,6}', arg_keywords_text)
    common = {"原文", "证据", "描述", "文章", "固定", "开头", "结尾", "模式", "包含", "使用"}
    arg_keywords = [w for w in words if w not in common and len(w) >= 2][:10]

    if not arg_keywords:
        # 无法提取论证关键词时，检查文章是否包含分析性段落
        has_analysis = bool(re.search(r'产业链|估值|基本面|趋势|护城河|周期|逻辑', article))
        return {
            "name": "论证方式匹配",
            "score": 70 if has_analysis else 30,
            "weight": 0.15,
            "detail": "论证结构检查（启发式）" if has_analysis else "缺少分析性段落",
            "pass": has_analysis,
        }

    hits = [kw for kw in arg_keywords if kw in article]
    coverage = len(hits) / len(arg_keywords)
    passed = coverage > 0.60

    return {
        "name": "论证方式匹配",
        "score": round(coverage * 100, 1),
        "weight": 0.15,
        "detail": f"论证关键词覆盖 {len(hits)}/{len(arg_keywords)}（{coverage:.0%}）",
        "hit_phrases": hits[:10],
        "pass": passed,
    }


def check_philosophy_values(article, profile):
    """检查哲学价值观体现——文章是否融入了大V的投资哲学和价值观"""
    profile_data, is_json = parse_profile_json(profile)
    if not is_json:
        return {"name": "哲学价值观体现", "score": 50, "weight": 0.10,
                "detail": "非JSON画像，跳过", "pass": True}

    # 从投资格言中提取哲学关键词
    atlas = profile_data.get("关注图谱", {})
    mottos = atlas.get("投资格言", [])
    if not mottos:
        return {"name": "哲学价值观体现", "score": 0, "weight": 0.10,
                "detail": "画像中未找到投资格言", "pass": False}

    # 同时检查互动特征中的修心哲学/价值观字段
    interaction = profile_data.get("互动特征", {})
    philosophy_text = " ".join(mottos)

    # 取前10个格言中的关键词
    words = re.findall(r'[\u4e00-\u9fff]{2,6}', philosophy_text)
    common = {"原文", "证据", "描述", "文章"}
    philosophy_kw = [w for w in words if w not in common and len(w) >= 2][:10]

    if not philosophy_kw:
        philosophy_kw = mottos[:5]  # 直接用格言原文

    hits = 0
    hit_list = []
    for kw in philosophy_kw:
        if kw in article:
            hits += 1
            hit_list.append(kw)

    coverage = hits / len(philosophy_kw) if philosophy_kw else 0
    passed = coverage > 0.50

    return {
        "name": "哲学价值观体现",
        "score": round(coverage * 100, 1),
        "weight": 0.10,
        "detail": f"哲学格言覆盖 {hits}/{len(philosophy_kw)}（{coverage:.0%}）",
        "hit_phrases": hit_list[:10],
        "pass": passed,
    }


# ─── 合规检查 ──────────────────────────────────────────────────────────────────────

# 6条合规硬规则
COMPLIANCE_RULES = [
    {
        "id": 1,
        "name": "不承诺收益",
        "check": lambda text: not any(kw in text for kw in ["保证赚钱", "稳赚不赔", "必涨", "翻倍", "包赚"]),
        "desc": "不包含承诺性表述",
    },
    {
        "id": 2,
        "name": "不预测具体收益率",
        "check": lambda text: not re.search(r'(预计|预期|预计).{0,5}(\d+\s*%|翻倍|\d+\s*倍收益)', text),
        "desc": "不承诺具体收益率数字",
    },
    {
        "id": 3,
        "name": "不暗示内幕",
        "check": lambda text: not any(kw in text for kw in ["内幕", "消息灵通", "据我所知", "独家消息", "未公开"]),
        "desc": "不暗示有内幕信息",
    },
    {
        "id": 4,
        "name": "标注数据来源",
        "check": lambda text: any(kw in text for kw in ["公开数据", "公开信息", "市场数据", "盘面数据"]),
        "desc": "标注基于公开数据生成",
    },
    {
        "id": 5,
        "name": "标注AI模拟",
        "check": lambda text: any(kw in text for kw in ["AI风格模拟", "AI 风格模拟", "风格模拟", "不构成投资建议"]),
        "desc": "标注AI风格模拟",
    },
    {
        "id": 6,
        "name": "不极端指令",
        "check": lambda text: not any(kw in text for kw in ["全仓买入", "满仓梭哈", "赶紧全买", "清仓卖出"]),
        "desc": "不给出极端操作指令",
    },
]


def check_compliance(article):
    """合规检查 — 6条硬规则"""
    violations = []
    passes = []

    for rule in COMPLIANCE_RULES:
        if rule["check"](article):
            passes.append(rule)
        else:
            violations.append(rule)

    all_passed = len(violations) == 0

    return {
        "name": "合规检查",
        "passed_rules": [r["name"] for r in passes],
        "violations": [r["name"] for r in violations],
        "all_passed": all_passed,
        "detail": f"通过 {len(passes)}/{len(COMPLIANCE_RULES)} 条规则"
                  + (f"，违反：{', '.join(r['name'] for r in violations)}" if violations else ""),
    }


# ─── 综合评分 ──────────────────────────────────────────────────────────────────────
def run_audit(article_path, author=None):
    """执行完整质量审计"""
    article_file = Path(article_path)
    if not article_file.exists():
        error(f"文章文件不存在：{article_path}")
        return None

    article = article_file.read_text(encoding="utf-8")
    info(f"已加载文章：{article_file.name}（{len(article)} 字符）")

    profile = None
    if author:
        profile = find_profile(author)
        if profile:
            info(f"已加载画像：{author}")
        else:
            warn(f"未找到{author}的风格画像，部分检查项将使用默认值")
            profile = ""

    if not profile:
        profile = "平均字数：3000\n语气与人称\n免责声明"

    # 前置合规检查（不通过直接打回）
    step("前置检查：合规检查（6条硬规则）...")
    compliance = check_compliance(article)

    if not compliance["all_passed"]:
        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{RED}{BOLD}  ❌ 合规检查不通过 — 直接打回{RESET}")
        print(f"{BOLD}{'='*60}{RESET}\n")
        for rule_name in compliance["passed_rules"]:
            print(f"  {GREEN}✓{RESET} {rule_name}")
        for rule_name in compliance["violations"]:
            print(f"  {RED}✗{RESET} {rule_name}")
        print(f"\n  {BOLD}合规检查不通过 = 直接打回，不计算综合评分{RESET}")
        print(f"  请修改文章后重新审计。\n")

        # 保存审计报告
        report = {
            "article": str(article_file),
            "author": author or "unknown",
            "audit_time": datetime.now().isoformat(),
            "compliance": compliance,
            "total_score": 0,
            "passed": False,
            "reason": "合规检查不通过",
        }
        report_file = OUTPUT_DIR / f"质量审计_{article_file.stem}_{datetime.now().strftime('%Y%m%d')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        info(f"审计报告已保存：{report_file}")
        return 0

    info(f"合规检查通过：{compliance['detail']}")

    # 执行9项检查
    checks = []

    step("检查1：标志性表达命中率...")
    checks.append(check_signature_phrases(article, profile))

    step("检查2：交易体系覆盖度...")
    checks.append(check_trading_system(article, profile))

    step("检查3：文章结构匹配度...")
    checks.append(check_article_structure(article, profile))

    step("检查4：盘面指标覆盖...")
    checks.append(check_market_indicators(article))

    step("检查5：语气一致性...")
    checks.append(check_tone_consistency(article, profile))

    step("检查6：交易术语覆盖...")
    checks.append(check_trading_terms(article))

    step("检查7：核心思维匹配度...")
    checks.append(check_core_thinking(article, profile))

    step("检查8：论证方式匹配...")
    checks.append(check_argumentation_style(article, profile))

    step("检查9：哲学价值观体现...")
    checks.append(check_philosophy_values(article, profile))

    # 计算综合评分
    total_score = sum(c["score"] * c["weight"] for c in checks)
    passed = total_score > 70

    # 输出报告
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  质量审计报告{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

    for c in checks:
        status = f"{GREEN}✓ PASS{RESET}" if c["pass"] else f"{RED}✗ FAIL{RESET}"
        print(f"  {status} {c['name']}")
        print(f"    得分：{c['score']}/100（权重{c['weight']:.0%}）")
        print(f"    详情：{c['detail']}")
        if "hit_phrases" in c and c["hit_phrases"]:
            print(f"    命中表达：{', '.join(c['hit_phrases'][:5])}")
        if "hit_terms" in c and c["hit_terms"]:
            print(f"    命中术语：{', '.join(c['hit_terms'][:5])}")
        if "elements" in c:
            for elem, status in c["elements"].items():
                print(f"    {elem}: {status}")
        print()

    print(f"{BOLD}{'─'*60}{RESET}")
    score_color = GREEN if passed else RED
    verdict = "✅ 准出" if passed else "❌ 打回重生成"
    print(f"  {BOLD}综合评分：{score_color}{total_score:.1f}{RESET}/100")
    print(f"  {BOLD}审计结论：{score_color}{verdict}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

    # 保存审计报告
    report = {
        "article": str(article_file),
        "author": author or "unknown",
        "audit_time": datetime.now().isoformat(),
        "compliance": compliance,
        "total_score": round(total_score, 1),
        "passed": passed,
        "checks": checks,
    }

    report_file = OUTPUT_DIR / f"质量审计_{article_file.stem}_{datetime.now().strftime('%Y%m%d')}.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    info(f"审计报告已保存：{report_file}")

    return total_score


# ─── 主流程 ────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="质量审计 — 校验生成内容")
    parser.add_argument("--article", required=True, help="待审计的文章路径")
    parser.add_argument("--author", help="大V名称（用于加载画像）")

    args = parser.parse_args()

    score = run_audit(args.article, args.author)
    if score is not None:
        sys.exit(0 if score > 70 else 1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
