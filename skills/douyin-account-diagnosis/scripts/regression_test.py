#!/usr/bin/env python3
"""
评分模型回归测试 —— 不调用 API，用 tests/fixtures 下的真实抓取数据校验评分逻辑。

用法:
    python3 scripts/regression_test.py

覆盖关键场景，防止后续改规则时出现「改一处、崩一处」：
  1. S 级超头部明星号应被正确识别为优质账号（≥90），
     旧版绝对阈值会把它误判为 76 分。
  2. A 级但互动率真实异常偏低（0.07%）的账号不得被无差别抬分，
     否则说明分层基准失效、变成了整体放水。
  3. C 级尾部号（2251 粉、均互动 4852 = 粉丝数 2 倍）不得因「绝对量级小」
     被误判为互动偏弱 —— 这是修 S 级偏差时引入的反向偏差。
  4. 采集时间（crawlTime）滞后于最新作品时，「最新活跃度」必须按当前时间校正，
     不得出现「最近-77天前发布」这类负数天数。
  5. S 级超头部 papi酱：接口只返回 2 条作品时，若干子项在数学上已退化
     （中位≡均值、max/均值≤2），必须改为不计入分母，不得让账号白拿满分；
     同时「性别」字段接口不返回，不得据此扣分。
  6. 快照累计量的年龄偏差：越新的作品累计互动必然越少，直接比较会把
     「最近发布」系统性读成「衰退」。趋势类指标只能比较「已跑够时间」的作品，
     成熟样本不足时不计入分母 —— 不得输出与事实相反的衰退结论或预警。
  7. 作品总量与人均获赞必须随量级自适应：前者是「绝对计数」、后者是「绝对量级」，
     原实现都用一把绝对尺子，导致 ① 精品型明星号按日更博主的节奏被扣分、
     ② 93.6 倍的效率差被满分封顶抹平。同时必须保证排序正确 ——
     精品型 S 级号（许凯）不得低于高产型 A 级号（小边边）。
  8. 「人群标签」必须只是展示项、不影响得分。它原本是「缺失字段不计入分母」的
     计分子项，但字段一旦提供必然有效，于是恒拿满分、毫无区分度，还会稀释其他
     缺失项的扣分 —— 同样资料质量的两个账号，仅因「接口恰好返回了性别」而得分不同。
  9. 「不可计算」与「数据不足」必须分开处理：
     · 比值为 0/0（互动全零）、字段缺失 → 不计入分母（不奖不罚）；
     · 账号确实没有作品数据 → 相关子项按最低档计分，不得剔除（剔除会让
       「已清空作品」的账号因分母变小而虚高，掩盖真实风险）。
     `_cv()` 在均值为 0 时返回 0.0，会被误读成「稳定输出」，必须在调用前拦截。
"""
import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
import douyin_diagnosis as dd  # noqa: E402

FIXTURES = SKILL_ROOT / "tests" / "fixtures"

DIMS = ["profile", "productivity", "engagement", "quality", "trend", "fans"]
FN = {
    "profile": dd.diagnose_profile,
    "productivity": dd.diagnose_productivity,
    "engagement": dd.diagnose_engagement,
    "quality": dd.diagnose_quality,
    "trend": dd.diagnose_trend,
    "fans": dd.diagnose_fans,
}


def evaluate(acc):
    """返回 (总分, 各维度明细, 预警列表, 量级)。总分走与报告一致的 composite_score。"""
    diagnoses = {k: FN[k](acc) for k in DIMS}
    rows = []
    for k in DIMS:
        score, _details, eff_max = diagnoses[k]
        norm = score / eff_max * 100 if eff_max else 0.0
        rows.append((dd.DIM_NAMES[k], score, eff_max, dd.DIM_MAX[k], norm))
    total = dd.composite_score(diagnoses)
    return total, rows, dd.check_warnings(acc), dd.account_tier(acc.get("followerCount", 0) or 0)


def run_case(slug, expect_tier, min_score, max_score, expect_warning=None):
    path = FIXTURES / f"{slug}.json"
    acc = json.loads(path.read_text(encoding="utf-8"))
    total, rows, warns, (tier_code, tier_label) = evaluate(acc)

    print("=" * 70)
    print(f"[CASE] {slug}  {acc.get('nickname')} ({acc.get('accountId')})")
    print(f"       粉丝={dd._fmt_num(acc.get('followerCount', 0))}  "
          f"量级={tier_code} {tier_label}  作品={acc.get('awemeCount')}  "
          f"抓取作品={len(acc.get('works') or [])}")
    for name, s, eff, full, norm in rows:
        flag = "" if eff == full else f"  [有效满分{eff}/卷面{full}]"
        print(f"       {name:<10} {s:>4}/{eff:<3} 归一化{norm:>6.1f}%{flag}")
    print(f"       合计 {total}/100   预警: {warns if warns else '无'}")

    failures = []
    if tier_code != expect_tier:
        failures.append(f"量级判定 {tier_code} != 期望 {expect_tier}")
    if not (min_score <= total <= max_score):
        failures.append(f"总分 {total} 不在期望区间 [{min_score}, {max_score}]")
    if expect_warning:
        if not any(expect_warning in w for w in warns):
            failures.append(f"未触发期望预警「{expect_warning}」，实际 {warns}")
    elif warns:
        failures.append(f"期望无预警，实际 {warns}")

    if failures:
        print("       ❌ FAIL: " + "; ".join(failures))
    else:
        print("       ✅ PASS")
    print()
    return not failures


def main():
    ok = True

    # 场景1：S 级明星号 —— 旧版绝对阈值下仅得 76 分，分层后应进入优质区间
    ok &= run_case("kaisoso", expect_tier="S", min_score=90, max_score=100)

    # 场景2：A 级但互动率 0.07% 的真实异常号 —— 必须仍被识别为短板，
    #        总分不得虚高（若涨到 85+ 说明基准整体放水）
    ok &= run_case(
        "juju", expect_tier="A", min_score=65, max_score=78, expect_warning="僵尸粉预警"
    )

    # 场景3：C 级尾部号，均互动 4852（粉丝数的 2 倍）—— 不得被判「互动偏弱」
    ok &= run_case("zhongguoyiwei", expect_tier="C", min_score=82, max_score=92)

    # 场景4：S 级超头部明星号 papi酱（2828 万粉）—— 小样本退化子项修正后应进入 92+
    #        修正前 86 分：其中 -2 来自性别字段恒不可得、-5 来自 n=2 时数学退化的子项
    ok &= run_case("papijiang", expect_tier="S", min_score=92, max_score=100)

    # 场景5：单元校验 —— 小样本退化子项必须不计入分母（不得白拿满分）
    print("=" * 70)
    print("[CASE] 小样本退化子项（n=2）应不计入分母")
    deg_acc = {
        "followerCount": 1_000_000, "totalFavorited": 10_000_000,
        "awemeCount": 500, "crawlTime": "2026-09-23 10:00:00",
        "works": [
            {"diggCount": 1000, "commentCount": 10, "shareCount": 5,
             "interactiveCount": 1015, "createTime": "2026-09-21 10:00:00"},
            {"diggCount": 9000, "commentCount": 90, "shareCount": 50,
             "interactiveCount": 9140, "createTime": "2026-09-22 10:00:00"},
        ],
    }
    _, q_details, q_eff = dd.diagnose_quality(deg_acc)
    _, t_details, t_eff = dd.diagnose_trend(deg_acc)
    _, _p_details, p_eff = dd.diagnose_productivity(deg_acc)

    checks = [
        ("内容质量 有效满分须降到 11（剔除中位偏离4 + 互动稳定性5）", q_eff, 11),
        ("内容趋势 有效满分须降到 5（剔除趋势5 + 集中度5）", t_eff, 5),
        ("内容生产力 有效满分须降到 10（剔除发布频率5）", p_eff, 10),
    ]
    for desc, got, want in checks:
        mark = "✅" if got == want else "❌"
        if got != want:
            ok = False
        print(f"       {mark} {desc}：实际 {got}")

    # 被剔除的子项必须以 full==0 标记，报告才会渲染成「不计入」
    for name, dets in (("内容质量", q_details), ("内容趋势", t_details)):
        for item, _lbl, _g, full in dets:
            if item in ("中位/均值偏离", "互动稳定性", "爆款集中度") and full != 0:
                ok = False
                print(f"       ❌ {name} 的「{item}」未标记为不计入（full={full}）")
    print()

    # 场景6：单元校验 —— 人群标签必须为「仅展示不计分」项
    # 该子项原为 2 分且「接口未提供的字段不计入分母」，但字段一旦提供必然有效，
    # 于是 gained 恒等于分母、恒拿满分、毫无区分度，还会稀释其他缺失项的扣分：
    #     地域缺失 + 性别年龄可用 → (7+2)/(8+2) = 90.0%
    #     地域缺失 + 性别年龄缺失 →  7/8        = 87.5%
    # 同样的资料质量只因「接口恰好返回了性别」而得分不同，与「不为数据可得性
    # 买单」的原则相悖（该原则意味着既不该罚、也不该奖）。故改为不计分展示项，
    # 账号基础画像卷面由 10 调整为 8。
    print("=" * 70)
    print("[CASE] 人群标签不得影响账号基础画像得分")
    for label, extra in [
        ("性别与年龄均缺失", {"gender": "未知", "age": None}),
        ("仅年龄可用", {"gender": "未知", "age": 31}),
        ("两者均可用", {"gender": "男", "age": 31}),
        ("年龄为占位符「未知」", {"gender": "未知", "age": "未知"}),
    ]:
        a = {"avatarUrl": "x", "signature": "这是一段超过十五个字的账号简介内容",
             "province": "北京", "ipLocation": "北京", "accountId": "abc"}
        a.update(extra)
        sc, _d, eff = dd.diagnose_profile(a)
        good = (sc == 8 and eff == 8)
        if not good:
            ok = False
        print(f"       {'✅' if good else '❌'} {label} -> {sc}/{eff}（期望 8/8，卷面恒为 8）")

    # 反向校验：地域信息缺失时，不得因性别/年龄可用而少扣分
    a1 = {"avatarUrl": "x", "signature": "这是一段超过十五个字的账号简介内容",
          "province": None, "ipLocation": "北京", "accountId": "abc",
          "gender": "男", "age": 31}
    a2 = dict(a1, gender="未知", age=None)
    s1, _d1, e1 = dd.diagnose_profile(a1)
    s2, _d2, e2 = dd.diagnose_profile(a2)
    good = (s1 / e1) == (s2 / e2)
    if not good:
        ok = False
    print(f"       {'✅' if good else '❌'} 地域缺失时，性别年龄是否可用不影响归一化得分"
          f"（{s1}/{e1} = {s2}/{e2}）")
    print()

    # 场景7：单元校验 —— 总分按「四舍五入」而非银行家舍入
    print("=" * 70)
    print("[CASE] 综合评分舍入方式（文档约定四舍五入）")
    # 构造总分恰为 94.5 的维度组合：各维度归一化后加权求和
    # profile 1.0*0.10 + productivity 0.9*0.15 + engagement 0.8667*0.30
    #  + quality 1.0*0.20 + trend 1.0*0.15 + fans 1.0*0.10 = 94.5
    stub = {
        "profile": (8, [], 8),          # 100%
        "productivity": (9, [], 10),    # 90%
        "engagement": (26, [], 30),     # 86.667%
        "quality": (11, [], 11),        # 100%
        "trend": (5, [], 5),            # 100%
        "fans": (10, [], 10),           # 100%
    }
    got = dd.composite_score(stub)
    mark = "✅" if got == 95 else "❌"
    if got != 95:
        ok = False
    print(f"       {mark} 94.5 分 -> {got}（四舍五入应为 95，Python 内置 round 会给出 94）")
    print()

    # 场景8：单元校验 —— 均互动分档随量级自适应
    #        同样的 5000 次互动，尾部号应远高于超头部号得分
    print("=" * 70)
    print("[CASE] 作品均互动分档随量级自适应（同样 4852 次互动）")
    def _eng(followers):
        acc = {
            "followerCount": followers,
            "totalFavorited": followers * 8,
            "works": [{
                "diggCount": 4000, "commentCount": 300, "shareCount": 500,
                "interactiveCount": 4852, "createTime": "2026-09-01 10:00:00",
            }],
        }
        _, details, _ = dd.diagnose_engagement(acc)
        for name, label, s, _f in details:
            if name == "作品均互动":
                return s, label
        return None, ""

    for followers, want_min in [(2251, 4), (6768100, 1)]:
        s, label = _eng(followers)
        mark = "✅" if s >= want_min else "❌"
        if s < want_min:
            ok = False
        print(f"       {mark} {followers:>9,} 粉 -> {label} ({s}/5，期望 ≥{want_min})")
    print()

    # 场景9：单元校验 —— 采集时间滞后时活跃度不得出现负数天数
    print("=" * 70)
    print("[CASE] 采集时间滞后于作品时的活跃度校正")
    stale_acc = {
        "followerCount": 2251, "totalFavorited": 17400,
        "crawlTime": "2026-07-07 12:41:41",  # 早于下方作品时间，字段滞后
        "works": [{
            "diggCount": 3880, "commentCount": 349, "shareCount": 1825,
            "interactiveCount": 7244, "createTime": "2026-09-19 16:26:46",
        }],
    }
    _, trend_details, _ = dd.diagnose_trend(stale_acc)
    act_label = next(lbl for name, lbl, _, _ in trend_details if name == "最新活跃度")
    bad = "-" in act_label.split("天前")[0]
    if bad:
        ok = False
    print(f"       {'❌' if bad else '✅'} {act_label}  (不得出现负数天数)")
    if "校正" not in act_label:
        ok = False
        print("       ❌ 未标注「按当前时间校正」，用户无法判断数据时效")
    print()

    # 场景10：单元校验 —— 量级分档边界
    print("=" * 70)
    print("[CASE] 量级分档边界")
    borders = [
        (999, "C"), (10_000, "B"), (99_999, "B"),
        (100_000, "A"), (999_999, "A"), (1_000_000, "S"),
    ]
    for followers, expect in borders:
        got = dd.account_tier(followers)[0]
        mark = "✅" if got == expect else "❌"
        if got != expect:
            ok = False
        print(f"       {mark} {followers:>9,} 粉 -> {got} (期望 {expect})")
    print()

    # 场景11：A 级头部号，4 条作品跨 6 天，最新一条发布仅 7 小时 ——
    #         累计互动必然「越新越小」，但换算日均其实是上升的。
    #         必须①判定「近期趋势不可判定」而非「严重衰退」；②不触发衰退预警。
    ok &= run_case("xiaobianbian", expect_tier="A", min_score=88, max_score=100)

    # 场景12：单元校验 —— 快照累计量的年龄偏差不得被读成「衰退」
    print("=" * 70)
    print("[CASE] 快照年龄偏差（累计互动随作品新旧递减）不得判为衰退")
    # 构造：越新的作品累计互动越小（这正是真实的快照形态），
    # 若规则直接比较累计量，会得出「暴跌」结论 —— 属于典型的反向误判。
    snap = {
        "followerCount": 662_100, "totalFavorited": 8_059_100,
        "awemeCount": 1576, "crawlTime": "2026-09-23 02:07:35",
        "works": [
            {"diggCount": 31507, "commentCount": 589, "shareCount": 4808,
             "interactiveCount": 38513, "createTime": "2026-09-16 18:20:41"},  # 6.3 天
            {"diggCount": 26997, "commentCount": 559, "shareCount": 2656,
             "interactiveCount": 31798, "createTime": "2026-09-19 18:18:00"},  # 3.3 天
            {"diggCount": 17701, "commentCount": 316, "shareCount": 1177,
             "interactiveCount": 20150, "createTime": "2026-09-21 18:20:24"},  # 1.3 天
            {"diggCount": 15067, "commentCount": 367, "shareCount": 1456,
             "interactiveCount": 18062, "createTime": "2026-09-22 19:21:00"},  # 0.3 天
        ],
    }
    _, snap_details, snap_eff = dd.diagnose_trend(snap)
    trend_label = next(lbl for name, lbl, _, _ in snap_details if name == "近期趋势")
    snap_warns = dd.check_warnings(snap)
    bad_trend = ("暴" in trend_label or "衰退" in trend_label)
    bad_warn = any("衰退预警" in w for w in snap_warns)
    if bad_trend:
        ok = False
    if bad_warn:
        ok = False
    print(f"       {'❌' if bad_trend else '✅'} 近期趋势: {trend_label}")
    print(f"       {'❌' if bad_warn else '✅'} 预警: {snap_warns if snap_warns else '无'}"
          "  (不得出现衰退预警)")
    # 内容趋势有效满分：15 - 5（趋势，成熟样本不足）- 5（集中度，n<5）= 5
    if snap_eff != 5:
        ok = False
        print(f"       ❌ 内容趋势有效满分应为 5（趋势与集中度均剔除），实际 {snap_eff}")
    else:
        print(f"       ✅ 内容趋势有效满分 {snap_eff}（趋势 5 + 集中度 5 均已剔除，不奖不罚）")
    print()

    # 场景13：单元校验 —— 作品总量与人均获赞分档随量级自适应
    print("=" * 70)
    print("[CASE] 作品总量 / 人均获赞 分档随量级自适应")

    def _vol(followers, aweme_count):
        acc = {"followerCount": followers, "awemeCount": aweme_count,
               "totalFavorited": 0, "works": []}
        _, details, _ = dd.diagnose_productivity(acc)
        return next((s, lbl) for name, lbl, s, _f in details if name == "作品总量")

    def _avg_like(followers, avg_likes):
        acc = {"followerCount": followers, "awemeCount": 100,
               "totalFavorited": avg_likes * 100, "works": []}
        _, details, _ = dd.diagnose_productivity(acc)
        return next((s, lbl) for name, lbl, s, _f in details if name == "人均获赞")

    # 同样 100 条作品：C 级新号算高产（线 100），A 级（职业日更博主区间，
    # 线 600）只算偏少，S 级（明星/精品型，线 150）算正常 ——
    # 正是因为三类账号的生产模式不同，不能共用一把尺子。
    for followers, want in [(2_251, 5), (1_000_000, 4), (662_100, 2)]:
        s, lbl = _vol(followers, 100)
        mark = "✅" if s == want else "❌"
        if s != want:
            ok = False
        print(f"       {mark} 100 条作品 @ {followers:>9,} 粉 -> {lbl}（{s}/5，期望 {want}）")

    # 同样 1,300 次人均获赞：对 C 级是高效（线 1,000），对 A 级只是正常（线 1,200），
    # 对 S 级则属低效（线 15,000）—— 绝对量级只有放在量级坐标系里才有意义。
    for followers, want in [(2_251, 5), (662_100, 3), (1_000_000, 1)]:
        s, lbl = _avg_like(followers, 1300)
        mark = "✅" if s == want else "❌"
        if s != want:
            ok = False
        print(f"       {mark} 1,300 人均获赞 @ {followers:>9,} 粉 -> {lbl}（{s}/5，期望 {want}）")
    print()

    # 场景14：跨账号排序 —— 精品型 S 级号不得低于高产型 A 级号
    #         许凯(S)：206 条 / 人均获赞 478,631（效率型）
    #         小边边(A)：1,576 条 / 人均获赞 5,114（产量型）
    #         改革前模型对效率的 93.6 倍差异完全失明，导致「产量多 7.6 倍」
    #         单方面压过效率优势，排序倒挂。
    print("=" * 70)
    print("[CASE] 效率 vs 产量：许凯(S 精品型) 与 小边边(A 高产型) 的排序")
    ks_total, _r, _w, _t = evaluate(
        json.loads((FIXTURES / "kaisoso.json").read_text(encoding="utf-8"))
    )
    xb_total, _r2, _w2, _t2 = evaluate(
        json.loads((FIXTURES / "xiaobianbian.json").read_text(encoding="utf-8"))
    )
    ks_prod = FN["productivity"](
        json.loads((FIXTURES / "kaisoso.json").read_text(encoding="utf-8"))
    )
    xb_prod = FN["productivity"](
        json.loads((FIXTURES / "xiaobianbian.json").read_text(encoding="utf-8"))
    )
    ks_like = next(s for n, _l, s, _f in ks_prod[1] if n == "人均获赞")
    xb_like = next(s for n, _l, s, _f in xb_prod[1] if n == "人均获赞")
    print(f"       许凯    总分 {ks_total:>3}   生产力 {ks_prod[0]}/{ks_prod[2]}"
          f"   人均获赞子项 {ks_like}/5")
    print(f"       小边边  总分 {xb_total:>3}   生产力 {xb_prod[0]}/{xb_prod[2]}"
          f"   人均获赞子项 {xb_like}/5")

    if ks_total < xb_total:
        ok = False
        print("       ❌ 精品型 S 级号得分低于高产型 A 级号：效率优势未兑现，模型仍只奖励产量")
    else:
        print("       ✅ 排序正确：精品型 S 级号 ≥ 高产型 A 级号")

    if ks_like == xb_like:
        ok = False
        print(f"       ❌ 两人均获赞子项得分相同（均 {ks_like}/5）："
              "478,631 vs 5,114 的 93.6 倍效率差仍被封顶抹平")
    else:
        print(f"       ✅ 效率差已兑现：许凯 {ks_like}/5 > 小边边 {xb_like}/5")
    print()

    # 场景15：单元校验 —— 「不可计算」的子项必须不计入分母（不奖不罚），
    #         但「账号确实没有内容」不得被当成「数据不足」而免罚。
    print("=" * 70)
    print("[CASE] 不可计算子项的处理（全零互动 / 无作品数据）")

    # 15a 有作品但互动全为 0：三个比值类子项均为 0/0，必须剔除；
    #     而爆款率、零互动占比是可计算的事实，须照常按最低档计分，
    #     否则一个「互动全零」的账号会因为三处剔除而把分母做小、总分被抬高。
    zero_acc = {
        "followerCount": 1_000_000, "totalFavorited": 50_000_000, "awemeCount": 300,
        "crawlTime": "2026-09-23 10:00:00",
        "works": [{"diggCount": 0, "commentCount": 0, "shareCount": 0,
                   "interactiveCount": 0, "createTime": f"2026-09-{d:02d} 10:00:00"}
                  for d in range(5, 11)],
    }
    _, zq_det, _zq_eff = dd.diagnose_quality(zero_acc)
    zq = {n: f for n, _l, _g, f in zq_det}
    for desc, item, want in [
        ("互动稳定性应剔除（CV=0/0 不可计算，_cv() 会返回 0.0 被误读为「稳定输出」）",
         "互动稳定性", 0),
        ("中位/均值偏离应剔除（偏离度=0/0 不可计算）", "中位/均值偏离", 0),
        ("零互动占比应照常计分（100% 是可计算的事实，不得剔除）", "零互动占比", 5),
    ]:
        good = zq.get(item) == want
        if not good:
            ok = False
        print(f"       {'✅' if good else '❌'} {desc}：full={zq.get(item)}（期望 {want}）")

    _, zt_det, _zt_eff = dd.diagnose_trend(zero_acc)
    zt = {n: f for n, _l, _g, f in zt_det}
    good = zt.get("爆款集中度") == 0
    if not good:
        ok = False
    print(f"       {'✅' if good else '❌'} 爆款集中度应剔除"
          f"（max/avg=0/0 不可计算）：full={zt.get('爆款集中度')}（期望 0）")

    # 15b 无作品数据：依赖作品的子项按最低档计分（0 分），**不剔除**。
    #     若剔除，一个「已清空作品」的账号会因分母变小而白白抬高总分，
    #     掩盖掉「账号已无内容可评」这一真实风险。
    empty_acc = dict(zero_acc, works=[])
    _, eq_det, eq_eff = dd.diagnose_quality(empty_acc)
    _, _et_det, et_eff = dd.diagnose_trend(empty_acc)
    for label, got, want in [("内容质量", eq_eff, 20), ("内容趋势", et_eff, 15)]:
        good = got == want
        if not good:
            ok = False
        print(f"       {'✅' if good else '❌'} 无作品时{label}仍为满卷 {want}（子项不剔除）：实际 {got}")
    names_ok = all(any(n == want for n, *_ in eq_det) for want in
                   ("爆款率", "中位/均值偏离", "互动稳定性", "零互动占比"))
    if not names_ok:
        ok = False
    print(f"       {'✅' if names_ok else '❌'} 无作品分支的子项名须与正式路径一致"
          "（原写作「中位互动」，与「中位/均值偏离」实为同一指标却两个名字）")
    print()

    print("=" * 70)
    print("回归测试结果: " + ("✅ 全部通过" if ok else "❌ 存在失败用例"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
