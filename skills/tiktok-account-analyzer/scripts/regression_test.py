#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tiktok_diagnosis.py 评分模型离线回归测试（不消耗 API 额度）。

fixtures:
  1. tests/fixtures/heyu.json —— B 腰部真实账号「1k_heyu」（5 条作品，爆款率 80%，
     近期成熟作品均播放回落 → 须触发衰退预警，且不得触发僵尸粉/限流预警）
  2. 无作品账号（内联构造）—— 依赖作品的子项一律 0 分且保留在分母
     （不因「样本不足」剔除，否则「已清空作品」账号会因分母变小而虚高）
  3. 互动全零账号（内联构造）—— 0/0 类子项（结构比/偏离/CV/集中度/趋势）
     剔除出分母；零互动占比与爆款率照常按最低档计分（回归 _cv() 均值为 0 陷阱）

用法：python3 scripts/regression_test.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tiktok_diagnosis as td  # noqa: E402

_PASS = 0
_FAIL = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global _PASS, _FAIL
    if cond:
        _PASS += 1
        print(f"  ✓ {name}")
    else:
        _FAIL += 1
        print(f"  ✗ {name}  {detail}")


def load_fixture(name: str) -> dict:
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "..", "tests", "fixtures", name)
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def dim(diag: dict, name: str) -> dict:
    return next(d for d in diag["dimensions"] if d["name"] == name)


def sub_item(diag: dict, dim_name: str, label_prefix: str) -> dict:
    d = dim(diag, dim_name)
    return next(i for i in d["items"] if i["label"].startswith(label_prefix))


def alert_names(diag: dict) -> list:
    return [a["name"] for a in diag["alerts"]]


def make_saved(profile: dict, items: list) -> dict:
    return {
        "meta": {"generatedAt": "2026-10-10 11:39:00", "types": ["profile", "works"]},
        "profile": profile,
        "works": {"items": items},
        "favorites": {"items": []},
    }


def test_heyu_real() -> None:
    print("\n[1] 真实账号 1k_heyu（B 腰部，5 条作品）")
    saved = load_fixture("heyu.json")
    diag = td.compute_diagnosis(saved)

    check("量级判定 B 腰部", diag["tier"]["key"] == "B" and diag["tier"]["label"] == "腰部",
          str(diag["tier"]))
    check("综合评分 == 79（🟡 正常账号）",
          diag["total"] == 79 and diag["grade"]["label"] == "正常账号",
          f"total={diag['total']} grade={diag['grade']}")
    check("爆款率 80.0% → 优秀 6/6",
          sub_item(diag, "内容质量", "爆款率")["score"] == 6 and
          "80.0%" in sub_item(diag, "内容质量", "爆款率")["note"])
    check("粉丝互动率 36.3% → 优秀 10/10",
          sub_item(diag, "互动健康度", "粉丝互动率")["score"] == 10)
    check("触发衰退预警（中危）",
          any(a["name"] == "衰退预警" and a["level"] == "中危" and a["icon"] == "⚠️"
              for a in diag["alerts"]),
          str(diag["alerts"]))
    check("不触发僵尸粉预警（36.3% 远高于偏低线）", "僵尸粉预警" not in alert_names(diag))
    check("不触发限流预警", "限流预警" not in alert_names(diag))
    check("无「无近期作品数据」提示", not any("无近期作品数据" in n for n in diag["notes"]))
    check("含初始基准校准提示", any("初始校准值" in n for n in diag["notes"]))


def test_no_works() -> None:
    print("\n[2] 无作品账号（works 为空，负面信号须保留在分母）")
    saved = make_saved(
        profile={"fans": 50000, "liked": 1000000, "works": 0,
                 "avatar": "https://x/a.png", "signature": "abcdefghijklmno",
                 "area": "US", "handle": "ghost"},
        items=[],
    )
    diag = td.compute_diagnosis(saved)

    for dim_name, prefix in [
        ("内容生产力", "人均获赞"), ("内容生产力", "发布频率"),
        ("互动健康度", "粉丝互动率"), ("互动健康度", "互动结构比"),
        ("互动健康度", "作品均播放"), ("内容质量", "爆款率"),
        ("内容质量", "中位/均值偏离"), ("内容质量", "互动稳定性"),
        ("内容质量", "零互动占比"), ("内容趋势", "近期趋势"),
        ("内容趋势", "爆款集中度"), ("内容趋势", "最新活跃度"),
    ]:
        it = sub_item(diag, dim_name, prefix)
        check(f"{dim_name}·{prefix} → 0 分且保留在分母（applied=True）",
              it["score"] == 0 and it["applied"],
              f"score={it['score']} applied={it['applied']} note={it['note']}")
    check("报告含「ⓘ 无近期作品数据」提示", any("无近期作品数据" in n for n in diag["notes"]))
    check("总分在风险区间", diag["total"] < 50, f"total={diag['total']}")
    check("粉丝获赞比不受作品缺失影响（20 → 良好 9/10）",
          sub_item(diag, "互动健康度", "粉丝获赞比")["score"] == 9)


def test_all_zero_engagement() -> None:
    print("\n[3] 互动全零账号（0/0 子项剔除；零互动占比/爆款率照常计分）")
    items = []
    for day in range(1, 7):
        items.append({
            "workId": f"w{day}", "content": f"作品{day}",
            "date": f"2026-09-0{day}", "publishTime": 0,
            "views": 0, "likes": 0, "comments": 0, "favorites": 0, "shares": 0,
        })
    saved = make_saved(
        profile={"fans": 2000, "liked": 0, "works": 6,
                 "avatar": "https://x/a.png", "signature": "abcdefghijklmno",
                 "area": "US", "handle": "dead"},
        items=items,
    )
    diag = td.compute_diagnosis(saved)

    for dim_name, prefix in [
        ("互动健康度", "互动结构比"),
        ("内容质量", "中位/均值偏离"), ("内容质量", "互动稳定性"),
        ("内容趋势", "近期趋势"), ("内容趋势", "爆款集中度"),
    ]:
        it = sub_item(diag, dim_name, prefix)
        check(f"{dim_name}·{prefix} 剔除出分母（applied=False）",
              not it["applied"], f"note={it['note']}")
    check("互动稳定性不得误判为「稳定输出」（CV 0/0 回归）",
          "稳定输出" not in sub_item(diag, "内容质量", "互动稳定性")["note"])
    check("零互动占比 100% → 大量低质/限流 1/5",
          sub_item(diag, "内容质量", "零互动占比")["score"] == 1 and
          "100.0%" in sub_item(diag, "内容质量", "零互动占比")["note"])
    check("爆款率 0% → 无爆款 1/6",
          sub_item(diag, "内容质量", "爆款率")["score"] == 1)
    check("触发限流预警（中危）", "限流预警" in alert_names(diag))
    check("触发断更预警（中危）", "断更预警" in alert_names(diag))
    check("不触发僵尸粉预警（粉丝 2000 < 5 万）", "僵尸粉预警" not in alert_names(diag))
    check("不触发单条依赖预警（播放全为 0）", "单条依赖预警" not in alert_names(diag))


def test_rounding() -> None:
    print("\n[4] 舍入规则（ROUND_HALF_UP，非银行家舍入）")
    check("94.5 → 95", td.round_half_up(94.5) == 95)
    check("94.4 → 94", td.round_half_up(94.4) == 94)
    check("0.5 → 1", td.round_half_up(0.5) == 1)
    check("2.0 → 2", td.round_half_up(2.0) == 2)


def main() -> None:
    print("=" * 60)
    print("tiktok_diagnosis 评分模型回归测试（离线，不消耗 API 额度）")
    test_heyu_real()
    test_no_works()
    test_all_zero_engagement()
    test_rounding()
    print("\n" + "=" * 60)
    print(f"通过 {_PASS} 项，失败 {_FAIL} 项")
    sys.exit(1 if _FAIL else 0)


if __name__ == "__main__":
    main()
