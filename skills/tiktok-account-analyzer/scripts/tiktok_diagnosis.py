#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TikTok 账号六维量化诊断引擎（离线评分，零接口调用）。

读取 tiktok_account_analyzer.py --save-json 保存的查询结果，按
references/diagnosis_rules.md 的规则计算六维得分、综合评分与风险预警，
输出对话用文本块；--update-analysis 将评分结果写入分析 JSON 供 HTML 报告渲染。

用法：
    python scripts/tiktok_diagnosis.py --data output/tiktok_account_latest.json
    python scripts/tiktok_diagnosis.py --data ... --update-analysis output/tiktok_account_analysis.json
"""
import argparse
import json
import math
import os
import statistics
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

BEIJING = timezone(timedelta(hours=8))
TREND_MATURE_DAYS = 3      # 近期趋势：只比较已发布满 3 天的作品
TREND_MIN_SAMPLE = 4       # 近期趋势：成熟样本最少条数
SAMPLE_MIN = 5             # CV / 集中度 / 发布频率：最少样本条数

# 账号量级分层（key, 标签, 粉丝数下限）
TIERS = (
    ("S", "超头部", 1000000),
    ("A", "头部", 100000),
    ("B", "腰部", 10000),
    ("C", "尾部", 0),
)

# 量级基准表（初始校准值，详见 references/diagnosis_rules.md，可随样本积累微调）
BENCH = {
    "S": {
        "engage": (3.0, 1.8, 0.9),              # 粉丝互动率 优秀/良好/偏低（%）
        "viral": 0.01,                          # 爆款线 = 点赞/粉丝
        "avg_views": (10000000, 1000000, 100000, 10000),   # 均播放 现象级/强传播/中等/偏弱
        "works": (100, 40, 2000),               # 作品总量 高产/正常/异常高产
        "avg_like": (200000, 80000, 15000),     # 人均获赞 高效/良好/正常
    },
    "A": {
        "engage": (5.0, 3.0, 1.5),
        "viral": 0.02,
        "avg_views": (1000000, 100000, 10000, 2000),
        "works": (400, 120, 4000),
        "avg_like": (15000, 4000, 1200),
    },
    "B": {
        "engage": (7.0, 4.5, 2.2),
        "viral": 0.05,
        "avg_views": (100000, 10000, 2000, 200),
        "works": (200, 60, 3000),
        "avg_like": (3000, 1000, 250),
    },
    "C": {
        "engage": (9.0, 5.5, 3.0),
        "viral": 0.10,
        "avg_views": (20000, 2000, 500, 50),
        "works": (60, 20, 2000),
        "avg_like": (1000, 400, 100),
    },
}

DIM_WEIGHTS = (
    ("账号基础画像", "10%"),
    ("内容生产力", "15%"),
    ("互动健康度", "30%"),
    ("内容质量", "20%"),
    ("内容趋势", "15%"),
    ("粉丝质量", "10%"),
)

GRADES = (
    (85, "优质账号", "🟢"),
    (70, "正常账号", "🟡"),
    (50, "待优化", "🟠"),
    (0, "风险账号", "🔴"),
)


def tier_of(fans: Any) -> Tuple[str, str]:
    fans = int(fans or 0)
    for key, label, low in TIERS:
        if fans >= low:
            return key, label
    return "C", "尾部"


def bench_of(tier: str) -> Dict[str, Any]:
    return BENCH[tier]


def round_half_up(value: float) -> int:
    """四舍五入（ROUND_HALF_UP），先归一到 6 位小数避免浮点误差。"""
    value = round(value + 1e-9, 6)
    return math.floor(value + 0.5)


def fmt_num(value: Any) -> str:
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return "0"


def pct(value: float, digits: int = 1) -> str:
    return f"{value:.{digits}f}%"


# ─── 数据准备 ─────────────────────────────────────────────────────────────────

def parse_generated_at(saved: Dict[str, Any]) -> Optional[int]:
    """解析 meta.generatedAt（北京时间字符串）为秒级时间戳；失败返回 None。"""
    text = str((saved.get("meta") or {}).get("generatedAt") or "").strip()
    if not text:
        return None
    for pattern in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return int(datetime.strptime(text, pattern).replace(tzinfo=BEIJING).timestamp())
        except ValueError:
            continue
    return None


def work_ts(item: Dict[str, Any]) -> Optional[int]:
    ts = item.get("publishTime")
    if ts:
        try:
            return int(ts)
        except (TypeError, ValueError):
            pass
    date = str(item.get("date") or "").strip()
    if date:
        try:
            return int(datetime.strptime(date, "%Y-%m-%d")
                       .replace(hour=12, tzinfo=BEIJING).timestamp())
        except ValueError:
            return None
    return None


def prepare(saved: Dict[str, Any]) -> Dict[str, Any]:
    profile = saved.get("profile") or {}
    items = ((saved.get("works") or {}).get("items")) or []
    fans = int(profile.get("fans") or 0)
    liked = int(profile.get("liked") or 0)
    work_count = int(profile.get("works") or 0) or len(items)

    ref_ts = parse_generated_at(saved)
    if ref_ts is None:
        ref_ts = int(datetime.now(tz=BEIJING).timestamp())
    # 作品时间晚于采集时间说明生成时间字段滞后，回退当前时间（口径与断更预警一致）
    latest = max((work_ts(it) for it in items if work_ts(it) is not None), default=0)
    if latest and latest > ref_ts:
        ref_ts = int(datetime.now(tz=BEIJING).timestamp())

    views = [int(it.get("views") or 0) for it in items]
    likes = [int(it.get("likes") or 0) for it in items]
    timestamps = [work_ts(it) for it in items]
    n = len(items)
    return {
        "profile": profile,
        "items": items,
        "fans": fans,
        "liked": liked,
        "work_count": work_count,
        "ref_ts": ref_ts,
        "views": views,
        "likes": likes,
        "timestamps": timestamps,
        "n": n,
    }


# ─── 子项计算（返回 (得分, 卷面分, 是否计入, 备注)）──────────────────────────

def sub(score: Any, full: int, note: str = "", applied: bool = True) -> Tuple[float, int, bool, str]:
    return float(score), full, applied, note


def d1_profile(ctx: Dict[str, Any]) -> List[Tuple[float, int, bool, str]]:
    profile = ctx["profile"]
    out = []
    avatar = str(profile.get("avatar") or "")
    out.append(sub(2 if avatar else 0, 2, "" if avatar else "头像缺失"))
    sig = str(profile.get("signature") or "").strip()
    if len(sig) >= 15:
        out.append(sub(3, 3, ""))
    elif sig:
        out.append(sub(1, 3, "签名过短"))
    else:
        out.append(sub(0, 3, "签名缺失"))
    area = str(profile.get("area") or "")
    out.append(sub(2 if area else 0, 2, "" if area else "地区缺失"))
    handle = str(profile.get("handle") or "")
    out.append(sub(1 if handle else 0, 1, "" if handle else "TikTok号缺失"))
    return out


def d2_productivity(ctx: Dict[str, Any]) -> List[Tuple[float, int, bool, str]]:
    b = bench_of(ctx["tier"])
    out = []
    # 作品总量
    wc = ctx["work_count"]
    high, normal, abnormal = b["works"]
    if wc >= abnormal:
        out.append(sub(4, 5, "极高产（需警惕刷量）"))
    elif wc >= high:
        out.append(sub(5, 5, "高产"))
    elif wc >= normal:
        out.append(sub(4, 5, "正常"))
    else:
        out.append(sub(2, 5, "作品偏少"))
    # 人均获赞
    if wc == 0:
        out.append(sub(0, 5, "无作品数据按最低档计分"))
    else:
        avg = ctx["liked"] / wc
        eff, good, normal_like = b["avg_like"]
        if avg >= eff:
            out.append(sub(5, 5, "高效"))
        elif avg >= good:
            out.append(sub(4, 5, "良好"))
        elif avg >= normal_like:
            out.append(sub(3, 5, "正常"))
        else:
            out.append(sub(1, 5, "低效"))
    # 发布频率
    ts = [t for t in ctx["timestamps"] if t is not None]
    if ctx["n"] == 0:
        out.append(sub(0, 5, "无作品数据按最低档计分"))
    elif ctx["n"] < SAMPLE_MIN or len(ts) < 2:
        out.append(sub(0, 5, f"样本不足 {SAMPLE_MIN} 条不计入", applied=False))
    else:
        days = max((max(ts) - min(ts)) / 86400.0, 1.0)
        freq = ctx["n"] / days
        if freq < 0.5:
            out.append(sub(2, 5, "低频"))
        elif freq < 2:
            out.append(sub(5, 5, "正常"))
        elif freq <= 3:
            out.append(sub(4, 5, "高频"))
        else:
            out.append(sub(3, 5, "极高频"))
    return out


def d3_engagement(ctx: Dict[str, Any]) -> List[Tuple[float, int, bool, str]]:
    b = bench_of(ctx["tier"])
    out = []
    # 粉丝获赞比
    if ctx["fans"] == 0:
        out.append(sub(0, 10, "粉丝数为 0 不计入", applied=False))
    else:
        ratio = ctx["liked"] / ctx["fans"]
        if ratio >= 25:
            note, score = "优质（长尾效应强）", 10
        elif ratio >= 15:
            note, score = "良好", 9
        elif ratio >= 8:
            note, score = "正常", 8
        elif ratio >= 3:
            note, score = "一般", 6
        elif ratio >= 1:
            note, score = "偏低", 3
        else:
            note, score = "极低", 1
        out.append(sub(score, 10, f"{note}（{ratio:.1f}）"))
    # 粉丝互动率
    if ctx["n"] == 0:
        out.append(sub(0, 10, "无作品数据按最低档计分"))
    elif ctx["fans"] == 0:
        out.append(sub(0, 10, "粉丝数为 0 不计入", applied=False))
    else:
        rate = (sum(ctx["likes"]) / ctx["n"] / ctx["fans"]) * 100
        excellent, good, low = b["engage"]
        if rate >= excellent:
            note, score = "优秀", 10
        elif rate >= good:
            note, score = "良好", 7
        elif rate >= low:
            note, score = "偏低", 4
        else:
            note, score = "极低", 1
        out.append(sub(score, 10, f"{note}（{pct(rate)}）"))
    # 互动结构比
    if ctx["n"] == 0:
        out.append(sub(0, 5, "无作品数据按最低档计分"))
    elif sum(ctx["likes"]) == 0:
        out.append(sub(0, 5, "点赞总数为 0 不计入", applied=False))
    else:
        comments = sum(int(it.get("comments") or 0) for it in ctx["items"])
        shares = sum(int(it.get("shares") or 0) for it in ctx["items"])
        c_ratio = comments / sum(ctx["likes"]) * 100
        s_ratio = shares / sum(ctx["likes"]) * 100
        if c_ratio >= 4 and s_ratio >= 4:
            note, score = "健康", 5
        elif c_ratio >= 3 and s_ratio >= 3:
            note, score = "较健康", 4
        elif c_ratio >= 2 or s_ratio >= 2:
            note, score = "一般", 3
        else:
            note, score = "互动单一", 2
        out.append(sub(score, 5, f"{note}（评 {pct(c_ratio)} · 转 {pct(s_ratio)}）"))
    # 作品均播放（绝对声量）
    if ctx["n"] == 0:
        out.append(sub(0, 5, "无作品数据按最低档计分"))
    else:
        avg = sum(ctx["views"]) / ctx["n"]
        phenomenon, strong, mid, weak = b["avg_views"]
        if avg >= phenomenon:
            note, score = "现象级", 5
        elif avg >= strong:
            note, score = "强传播", 4
        elif avg >= mid:
            note, score = "中等", 3
        elif avg >= weak:
            note, score = "偏弱", 2
        else:
            note, score = "微弱", 1
        out.append(sub(score, 5, f"{note}（均播放 {fmt_num(avg)}）"))
    return out


def d4_quality(ctx: Dict[str, Any]) -> List[Tuple[float, int, bool, str]]:
    b = bench_of(ctx["tier"])
    out = []
    # 爆款率
    if ctx["n"] == 0:
        out.append(sub(0, 6, "无作品数据按最低档计分"))
    else:
        line = ctx["fans"] * b["viral"]
        viral = sum(1 for v in ctx["likes"] if v > line)
        rate = viral / ctx["n"] * 100
        if rate > 10:
            note, score = "优秀", 6
        elif rate >= 5:
            note, score = "良好", 4
        elif rate > 0:
            note, score = "偏低", 3
        else:
            note, score = "无爆款", 1
        out.append(sub(score, 6, f"{note}（爆款率 {pct(rate)}）"))
    # 中位/均值偏离（按点赞）
    if ctx["n"] == 0:
        out.append(sub(0, 4, "无作品数据按最低档计分"))
    elif ctx["n"] < 3:
        out.append(sub(0, 4, f"样本不足 3 条不计入", applied=False))
    elif sum(ctx["likes"]) == 0:
        out.append(sub(0, 4, "点赞均值为 0 不计入", applied=False))
    else:
        mean = sum(ctx["likes"]) / ctx["n"]
        dev = abs(statistics.median(ctx["likes"]) - mean) / mean
        if dev < 0.2:
            note, score = "分布均匀", 4
        elif dev < 0.5:
            note, score = "轻度偏离", 3
        else:
            note, score = "严重偏离（靠爆款拉动）", 1
        out.append(sub(score, 4, f"{note}（偏离度 {dev:.2f}）"))
    # 互动稳定性 CV（按播放）
    if ctx["n"] == 0:
        out.append(sub(0, 5, "无作品数据按最低档计分"))
    elif ctx["n"] < SAMPLE_MIN:
        out.append(sub(0, 5, f"样本不足 {SAMPLE_MIN} 条不计入", applied=False))
    elif sum(ctx["views"]) == 0:
        out.append(sub(0, 5, "播放均值为 0 不计入", applied=False))
    else:
        mean = sum(ctx["views"]) / ctx["n"]
        cv = statistics.pstdev(ctx["views"]) / mean
        if cv < 0.5:
            note, score = "稳定输出", 5
        elif cv <= 1.0:
            note, score = "波动一般", 3
        else:
            note, score = "严重依赖爆款", 1
        out.append(sub(score, 5, f"{note}（CV {cv:.2f}）"))
    # 零互动占比
    if ctx["n"] == 0:
        out.append(sub(0, 5, "无作品数据按最低档计分"))
    else:
        zero = sum(1 for v in ctx["likes"] if v < 10)
        p = zero / ctx["n"] * 100
        if p < 5:
            note, score = "质量稳定", 5
        elif p < 20:
            note, score = "部分低质", 3
        else:
            note, score = "大量低质/限流", 1
        out.append(sub(score, 5, f"{note}（零互动占比 {pct(p)}）"))
    return out


def _mature_pairs(ctx: Dict[str, Any]) -> List[Tuple[int, int]]:
    """已满 3 天作品按时间升序的 (ts, views) 列表。"""
    pairs = []
    for it, ts in zip(ctx["items"], ctx["timestamps"]):
        if ts is None:
            continue
        if ctx["ref_ts"] - ts >= TREND_MATURE_DAYS * 86400:
            pairs.append((ts, int(it.get("views") or 0)))
    return sorted(pairs)


def d5_trend(ctx: Dict[str, Any]) -> List[Tuple[float, int, bool, str]]:
    out = []
    pairs = _mature_pairs(ctx)
    # 近期趋势
    if ctx["n"] == 0:
        out.append(sub(0, 5, "无作品数据按最低档计分"))
    elif len(pairs) < TREND_MIN_SAMPLE:
        out.append(sub(0, 5, f"已满 3 天作品仅 {len(pairs)} 条不计入", applied=False))
    else:
        k = max(1, len(pairs) // 3)
        early = [v for _, v in pairs[:k]]
        recent = [v for _, v in pairs[-k:]]
        early_mean = sum(early) / len(early)
        recent_mean = sum(recent) / len(recent)
        if early_mean == 0:
            out.append(sub(0, 5, "早期均播放为 0 不计入", applied=False))
        else:
            change = (recent_mean - early_mean) / early_mean * 100
            if change > 20:
                note, score = "增长期", 5
            elif change >= -20:
                note, score = "平稳期", 4
            elif change >= -50:
                note, score = "衰退期", 2
            else:
                note, score = "严重衰退", 1
            out.append(sub(score, 5, f"{note}（变化率 {change:+.0f}%）"))
    # 爆款集中度
    if ctx["n"] == 0:
        out.append(sub(0, 5, "无作品数据按最低档计分"))
    elif ctx["n"] < SAMPLE_MIN:
        out.append(sub(0, 5, f"样本不足 {SAMPLE_MIN} 条不计入", applied=False))
    elif sum(ctx["views"]) == 0:
        out.append(sub(0, 5, "播放均值为 0 不计入", applied=False))
    else:
        conc = max(ctx["views"]) / (sum(ctx["views"]) / ctx["n"])
        if conc < 3:
            note, score = "均匀分布", 5
        elif conc < 5:
            note, score = "较为均匀", 4
        elif conc < 10:
            note, score = "依赖爆款", 2
        else:
            note, score = "严重依赖单条", 1
        out.append(sub(score, 5, f"{note}（集中度 {conc:.1f} 倍）"))
    # 最新活跃度
    ts = [t for t in ctx["timestamps"] if t is not None]
    if ctx["n"] == 0:
        out.append(sub(0, 5, "无作品数据按最低档计分"))
    elif not ts:
        out.append(sub(0, 5, "作品缺发布时间不计入", applied=False))
    else:
        days = max(0.0, (ctx["ref_ts"] - max(ts)) / 86400.0)
        if days <= 3:
            note, score = "活跃", 5
        elif days <= 7:
            note, score = "正常", 4
        elif days <= 14:
            note, score = "偏沉默", 2
        else:
            note, score = "已断更", 1
        out.append(sub(score, 5, f"{note}（距最新发布 {days:.0f} 天）"))
    return out


def d6_fans(ctx: Dict[str, Any]) -> List[Tuple[float, int, bool, str]]:
    b = bench_of(ctx["tier"])
    out = []
    # 粉丝规模（由量级派生）
    tier_scores = {"S": 4, "A": 3, "B": 2, "C": 1}
    out.append(sub(tier_scores[ctx["tier"]], 4, f"{ctx['tier']} {ctx['tier_label']}"))
    # 粉丝互动比
    if ctx["n"] == 0:
        out.append(sub(0, 3, "无作品数据按最低档计分"))
    elif ctx["fans"] == 0:
        out.append(sub(0, 3, "粉丝数为 0 不计入", applied=False))
    else:
        rate = (sum(ctx["likes"]) / ctx["n"] / ctx["fans"]) * 100
        _, good, low = b["engage"]
        if rate >= good:
            note, score = "粉丝活跃", 3
        elif rate >= low:
            note, score = "粉丝一般", 2
        else:
            note, score = "粉丝不活跃", 1
        out.append(sub(score, 3, f"{note}（{pct(rate)}）"))
    # 获赞/粉丝背离
    if ctx["fans"] == 0:
        out.append(sub(0, 3, "粉丝数为 0 不计入", applied=False))
    else:
        ratio = ctx["liked"] / ctx["fans"]
        if ratio <= 50:
            note, score = "正常", 3
        elif ratio <= 100:
            note, score = "偏高", 2
        else:
            note, score = "异常高（疑似刷赞/搬运）", 1
        out.append(sub(score, 3, f"{note}（{ratio:.1f}）"))
    return out


DIM_FUNCS = (d1_profile, d2_productivity, d3_engagement, d4_quality, d5_trend, d6_fans)


def dimension_comment(items: List[Tuple[float, int, bool, str]]) -> str:
    notes = [note for _, _, applied, note in items if note and applied]
    if any(not applied for *_, applied, _ in items):
        notes.append("部分子项不计入")
    if not notes:
        return "全部子项达标"
    seen, uniq = set(), []
    for note in notes:
        key = note.split("（")[0]
        if key not in seen:
            seen.add(key)
            uniq.append(note)
    joined = "；".join(uniq)
    if len(joined) <= 40:
        return joined
    cut = joined[:40].rstrip("；")
    # 在完整分句边界截断，避免半句悬挂
    boundary = cut.rfind("；")
    return cut[:boundary] + "…" if boundary > 0 else cut + "…"


def _label(dim_name: str, idx: int, item: Tuple[float, int, bool, str]) -> str:
    """子项标签：规则文档顺序为第 idx 项；计数类子项补「（以全量数据计）」标识。"""
    labels = LABELS.get(dim_name) or []
    base = labels[idx] if idx < len(labels) else f"子项{idx + 1}"
    note = item[3]
    if "全量" in note and "全量" not in base:
        base += "（以全量数据计）"
    return base


def compute_diagnosis(saved: Dict[str, Any]) -> Dict[str, Any]:
    ctx = prepare(saved)
    tier, tier_label = tier_of(ctx["fans"])
    ctx["tier"] = tier
    ctx["tier_label"] = tier_label

    dimensions = []
    weighted_sum = 0.0
    for (name, weight), func in zip(DIM_WEIGHTS, DIM_FUNCS):
        items = func(ctx)
        applied = [it for it in items if it[2]]
        score = sum(it[0] for it in applied)
        full = sum(it[1] for it in applied)
        norm = (score / full * 100) if full else 0.0
        weighted_sum += norm * float(weight.rstrip("%")) / 100.0
        dimensions.append({
            "name": name,
            "weight": weight,
            "score": score,
            "full": full,
            "norm": round(norm, 1),
            "comment": dimension_comment(items),
            "items": [
                {"label": _label(name, i, it), "score": it[0],
                 "full": it[1], "applied": it[2], "note": it[3]}
                for i, it in enumerate(items)
            ],
        })

    total = round_half_up(weighted_sum)
    grade = next((g for g in GRADES if total >= g[0]), GRADES[-1])

    alerts = build_alerts(ctx, dimensions)

    notes = []
    if ctx["n"] == 0:
        notes.append("ⓘ 无近期作品数据：依赖作品的维度均按最低档计分，分数偏低属预期，"
                     "请核对账号是否已清空作品或停更。")
    elif ctx["n"] < SAMPLE_MIN:
        notes.append(f"ⓘ 数据置信度：返回作品仅 {ctx['n']} 条，均值型指标由少量样本决定，结论仅供参考。")
    notes.append("评分基准为 TikTok 初始校准值，随样本积累持续微调（详见 references/diagnosis_rules.md）。")

    return {
        "total": total,
        "grade": {"label": grade[1], "icon": grade[2]},
        "tier": {"key": tier, "label": tier_label, "fans": ctx["fans"]},
        "dimensions": dimensions,
        "alerts": alerts,
        "notes": notes,
    }


# 维度内子项标签（与规则文档维度表顺序一致）
LABELS = {
    "账号基础画像": ["头像", "签名", "地区", "TikTok号"],
    "内容生产力": ["作品总量", "人均获赞", "发布频率"],
    "互动健康度": ["粉丝获赞比", "粉丝互动率", "互动结构比", "作品均播放"],
    "内容质量": ["爆款率", "中位/均值偏离", "互动稳定性", "零互动占比"],
    "内容趋势": ["近期趋势", "爆款集中度", "最新活跃度"],
    "粉丝质量": ["粉丝规模", "粉丝互动比", "获赞/粉丝背离"],
}


def build_alerts(ctx: Dict[str, Any], dimensions: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    alerts: List[Dict[str, str]] = []
    b = bench_of(ctx["tier"])

    engage_rate = None
    if ctx["n"] > 0 and ctx["fans"] > 0:
        engage_rate = (sum(ctx["likes"]) / ctx["n"] / ctx["fans"]) * 100
    excellent, good, low = b["engage"]

    # 僵尸粉预警
    if engage_rate is not None and ctx["fans"] > 50000 and engage_rate < low:
        alerts.append({"icon": "🚨", "name": "僵尸粉预警", "level": "高危",
                       "detail": f"粉丝互动率 {pct(engage_rate)} 低于本量级偏低线 {pct(low)}。"})

    # 刷量预警（需成熟样本支持「近期骤降」判定）
    pairs = _mature_pairs(ctx)
    liked_fans = (ctx["liked"] / ctx["fans"]) if ctx["fans"] else 0
    trend_declining = False
    if len(pairs) >= TREND_MIN_SAMPLE:
        k = max(1, len(pairs) // 3)
        early_mean = sum(v for _, v in pairs[:k]) / k
        recent_mean = sum(v for _, v in pairs[-k:]) / k
        if early_mean > 0:
            change = (recent_mean - early_mean) / early_mean * 100
            trend_declining = change < -50
    if liked_fans > 100 and trend_declining:
        alerts.append({"icon": "🚨", "name": "刷量预警", "level": "高危",
                       "detail": f"获赞/粉丝比 {liked_fans:.0f} 超过 100 且近期互动骤降。"})

    # 衰退预警
    if len(pairs) >= TREND_MIN_SAMPLE:
        k = max(1, len(pairs) // 3)
        early_mean = sum(v for _, v in pairs[:k]) / k
        recent_mean = sum(v for _, v in pairs[-k:]) / k
        if early_mean > 0 and recent_mean < early_mean * 0.5:
            alerts.append({"icon": "⚠️", "name": "衰退预警", "level": "中危",
                           "detail": "近期成熟作品均播放不足早期的一半，内容热度明显回落。"})

    # 限流预警
    if ctx["n"] > 0:
        zero = sum(1 for v in ctx["likes"] if v < 10)
        if zero / ctx["n"] * 100 > 30:
            alerts.append({"icon": "⚠️", "name": "限流预警", "level": "中危",
                           "detail": f"零互动作品占比 {pct(zero / ctx['n'] * 100)}，超过 30%。"})

    # 断更预警
    ts = [t for t in ctx["timestamps"] if t is not None]
    if ts:
        days = max(0.0, (ctx["ref_ts"] - max(ts)) / 86400.0)
        if days > 14:
            alerts.append({"icon": "⚠️", "name": "断更预警", "level": "中危",
                           "detail": f"距最新作品发布已 {days:.0f} 天，超过 14 天。"})

    # 单条依赖预警
    if ctx["n"] > 0 and sum(ctx["views"]) > 0:
        avg = sum(ctx["views"]) / ctx["n"]
        if max(ctx["views"]) > avg * 10:
            alerts.append({"icon": "ℹ️", "name": "单条依赖预警", "level": "低危",
                           "detail": "最高播放作品超过均值的 10 倍，数据依赖单条爆款。"})

    return alerts


# ─── 文本渲染 ────────────────────────────────────────────────────────────────

def render_text(diag: Dict[str, Any]) -> str:
    lines = ["### 📐 六维量化诊断"]
    tier = diag["tier"]
    lines.append(
        f"综合评分：{diag['total']} / 100（{diag['grade']['icon']} {diag['grade']['label']}）"
        f"｜ 量级：{tier['key']} {tier['label']}（粉丝 {fmt_num(tier['fans'])}）")
    lines.append("")
    lines.append("| 维度 | 得分 | 有效满分 | 权重 | 一句话评价 |")
    lines.append("|---|---:|---:|---:|---|")
    for dim in diag["dimensions"]:
        lines.append(f"| {dim['name']} | {dim['score']:g} | {dim['full']} | {dim['weight']} | {dim['comment']} |")
    lines.append("")
    if diag["alerts"]:
        lines.append("⚠️ 风险预警")
        for alert in diag["alerts"]:
            lines.append(f"- {alert['icon']} {alert['name']}（{alert['level']}）：{alert['detail']}")
    else:
        lines.append("⚠️ 风险预警：无")
    for note in diag["notes"]:
        lines.append(f"\n{note}")
    return "\n".join(lines)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="TikTok 账号六维量化诊断（离线评分）")
    parser.add_argument("--data", required=True, help="tiktok_account_analyzer.py --save-json 保存的 JSON 路径")
    parser.add_argument("--update-analysis", default=None, metavar="PATH",
                        help="将评分结果写入分析 JSON（供 HTML 报告渲染）")
    args = parser.parse_args()

    with open(args.data, encoding="utf-8") as f:
        saved = json.load(f)

    diag = compute_diagnosis(saved)
    print(render_text(diag))

    if args.update_analysis:
        path = args.update_analysis
        try:
            with open(path, encoding="utf-8") as f:
                analysis = json.load(f)
        except (OSError, json.JSONDecodeError):
            analysis = {"viralTop3": [], "diagnosis": ""}
        analysis["scoring"] = diag
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 评分结果已写入：{path}", file=sys.stderr)


if __name__ == "__main__":
    main()
