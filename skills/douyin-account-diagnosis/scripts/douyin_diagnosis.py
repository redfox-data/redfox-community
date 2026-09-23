#!/usr/bin/env python3
"""
抖音账号诊断工具
用于「抖音账号诊断」技能的数据获取、六维度评分与报告生成。
通过红狐(RedFox) API 获取抖音账号数据，进行六维度诊断分析并输出报告。

用法: python douyin_diagnosis.py <抖音昵称或抖音号> [--api-key <你的API Key>]
API Key 优先级: 命令行 --api-key > 环境变量 REDFOX_API_KEY
"""

import os
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import statistics

# ============================================================
# API 配置
# ============================================================
API_URL = "https://redfox.hk/story/api/dyUser/queryData"

# 技能来源标识（所有接口调用必须携带）
SOURCE = "抖音账号诊断-workbuddy"


def resolve_api_key(cli_key=None):
    """解析使用的 API Key：命令行参数 > 环境变量 REDFOX_API_KEY。未配置则返回 None。"""
    return cli_key or os.environ.get("REDFOX_API_KEY") or None


def require_api_key(cli_key=None):
    """解析 API Key；未配置时输出引导信息并退出。"""
    api_key = resolve_api_key(cli_key)
    if api_key:
        return api_key
    print("[错误] 未配置 API Key")
    print("[hint] 获取: https://redfox.hk/settings/api-keys?source=github")
    print("[hint] 配置: export REDFOX_API_KEY=ak_xxxxxxxx")
    print("[hint] 或: python douyin_diagnosis.py <账号> --api-key ak_xxxxxxxx")
    sys.exit(1)

# ============================================================
# 工具函数
# ============================================================

def query_account(keyword, api_key):
    """调用红狐API查询抖音账号数据。keyword 可为昵称或抖音号。"""
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key,
    }
    # 优先用 accountIds（精确匹配），若含中文则用 accountNames（模糊匹配）
    if _is_chinese(keyword):
        payload_key = "accountNames"
    else:
        payload_key = "accountIds"
    # 请求体必须携带 source 字段（技能来源标识）
    payload = json.dumps({payload_key: [keyword], "source": SOURCE}).encode("utf-8")
    req = urllib.request.Request(API_URL, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("code") == 2000 and result.get("data"):
                return result["data"][0]
            elif result.get("code") == 3201:
                print("[错误] API积分不足，请前往 https://redfox.hk/?source=github 充值。")
                return None
            else:
                print(f"[错误] API返回异常: code={result.get('code')}, msg={result.get('msg', '')}")
                return None
    except urllib.error.URLError as e:
        print(f"[错误] 网络请求失败: {e}")
        return None
    except Exception as e:
        print(f"[错误] {e}")
        return None


def _is_chinese(s):
    return any("\u4e00" <= ch <= "\u9fff" for ch in s)


def _parse_dt(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def _safe_div(a, b):
    if not b or b == 0:
        return 0.0
    return a / b


def _work_age_days(work, ref_time):
    """作品从发布到参考时间已过去的整天数。时间缺失返回 -1（视为未成熟）。"""
    t = _parse_dt(work.get("createTime", ""))
    if not t or not ref_time:
        return -1.0
    return (ref_time - t).total_seconds() / 86400.0


def _trend_ref_time(works, crawl_time):
    """趋势类指标共用的参考时间：采集时间滞后于作品时回退当前时间。

    与「最新活跃度」保持同一套逻辑，避免用早于作品的采集时间去算"过去多久"。
    """
    times = [_parse_dt(w.get("createTime", "")) for w in works]
    times = [t for t in times if t]
    if not times:
        return crawl_time
    latest = max(times)
    if not crawl_time or crawl_time < latest:
        return datetime.now()
    return crawl_time


# 接口对「未提供」的字段会返回占位值，"未知"/空串一律视为未提供。
_PLACEHOLDER = {"", "未知", "null", "None", "N/A"}


def _field_provided(value):
    """判断接口是否真的提供了该字段（占位值视为未提供）。

    注意：无法区分「创作者未填写」与「接口不返回」。实测 gender 在 4/4 账号上
    均为"未知"，判断为接口不返回，故不据此扣分——宁可放过，不冤枉账号。
    """
    if value is None:
        return False
    return str(value).strip() not in _PLACEHOLDER


def _fmt_num(n):
    """数字格式化，大数加万/亿后缀。"""
    if n is None:
        return "N/A"
    if n >= 100_000_000:
        return f"{n / 100_000_000:.2f}亿"
    if n >= 10_000:
        return f"{n / 10_000:.2f}万"
    return str(n)


def _cv(values):
    """变异系数 = 标准差 / 均值。

    注意：均值为 0 时返回 0.0，与「真的完全稳定」取值相同，调用方
    必须先自行排除「全部为 0」的情形，不能直接拿 0.0 当作「稳定」。
    """
    if len(values) < 2:
        return 0.0
    m = statistics.mean(values)
    if m == 0:
        return 0.0
    return statistics.stdev(values) / m


# ============================================================
# 账号量级分层 —— 所有互动类基准随量级自适应
# ------------------------------------------------------------
# 抖音的互动指标与粉丝体量强负相关：同样是「单条 10 万次互动」，
# 对 5 万粉的账号是 200% 的爆款，对 670 万粉的账号只是 1.5% 的日常。
# 因此互动率、爆款线等基准必须按量级分档，不能用一套绝对阈值同时
# 评判尾部和超头部账号，否则会系统性低估大号。
# ============================================================

TIER_LEVELS = [
    ("S", "超头部", 1_000_000),
    ("A", "头部", 100_000),
    ("B", "腰部", 10_000),
    ("C", "尾部", 0),
]


def account_tier(followers):
    """按粉丝数返回账号量级 (code, label)。"""
    for code, label, floor in TIER_LEVELS:
        if followers >= floor:
            return code, label
    return "C", "尾部"


# 各量级「粉丝互动率」基准线 (满分线, 良好线, 偏低线)，单位 %。
# 体量越大自然互动率越低，故基准随量级递减。
ENGAGEMENT_BENCH = {
    "S": (2.0, 1.2, 0.6),
    "A": (4.0, 2.5, 1.2),
    "B": (6.0, 4.0, 2.0),
    "C": (8.0, 5.0, 2.5),
}

# 各量级「爆款」判定线：单条点赞数 / 粉丝数，单位 %。
# 超头部号「点赞超过粉丝数 10%」几乎不可能达成，故按量级下调。
HIT_BENCH = {"S": 1.0, "A": 2.0, "B": 5.0, "C": 10.0}

# 各量级「单条作品平均互动量」分档线 (现象级, 强传播, 中等, 偏弱)，单位：次。
# 绝对量级必须与账号体量匹配，否则会重演「用一套阈值评判所有量级」的错误：
# 同样是 5 千次互动，对 2251 粉的尾部号是粉丝数的 2 倍（超预期），
# 对 676 万粉的超头部号只是日常水平的零头（不合格）。
INTERACTION_BENCH = {
    "S": (1_000_000, 100_000, 10_000, 500),
    "A": (200_000, 20_000, 2_000, 200),
    "B": (50_000, 5_000, 500, 50),
    "C": (10_000, 1_000, 200, 20),
}

# 各量级「作品总量」分档线 (高产线, 正常线, 异常高产线)，单位：条。
#
# 为什么也要分层：作品条数是「绝对计数」类指标，不同量级账号的生产模式完全不同。
# 高量级账号以明星/演员/精品制作为主，单条生产成本极高，产量天然偏低；
# A 级区间聚集了大量职业化日更博主，产量期望最高；B/C 级多为个人号与新号。
# 拿一把绝对尺子同时量这两类号，等于要求演员按日更博主的节奏产出。
#
# 实测样本的「作品数 / 粉丝数」印证了这一分层：
#   中国一味(C) 16/2251 = 0.711%   桔桔(A) 4424/44.42万 = 0.996%
#   小边边(A) 1576/66.21万 = 0.238%   许凯(S) 206/676.81万 = 0.003%
#   papi酱(S) 536/2828.77万 = 0.002%
# 即体量越大，单位粉丝对应的作品数越少——故不能按同一把尺子扣分。
VOLUME_BENCH = {
    "S": (150, 60, 3000),
    "A": (600, 200, 6000),
    "B": (300, 100, 5000),
    "C": (100, 30, 3000),
}

# 各量级「人均获赞」分档线 (高效线, 良好线, 正常线)，单位：次。
#
# 人均获赞 = 获赞总量 / 作品数，即「单条作品平均拿到多少赞」。
# 它与量级强正相关（粉丝越多、单条触达基数越大），故基准随量级**递增**——
# 方向与互动率类指标相反（后者随量级递减）。
#
# 为什么必须相对化：原实现用绝对线（≥1000 即满分），导致
#   许凯(S) 478,631 与 小边边(A) 5,114 都拿满分 → 93.6 倍的效率差被完全抹平，
#   而作品数落后 7.6 倍却照常扣分，形成「只奖励量、对效率失明」的不对称。
# 相对化后，同样是 5,114 次人均获赞：对 A 级只算「良好」，对 C 级则是「高效」——
# 因为 C 级账号 1,086 次（中国一味）已属远超预期。
AVG_LIKE_BENCH = {
    "S": (200_000, 80_000, 15_000),
    "A": (15_000, 4_000, 1_200),
    "B": (3_000, 1_000, 250),
    "C": (1_000, 400, 100),
}

# 样本充分性门槛：接口返回的作品条数少于此值时，凡「依赖样本推算」的子项
# 一律不计入分母（不奖不罚），避免账号为「接口没给足数据」买单或白拿分。
# 背景：接口常只返回 2–3 条作品，此时多个子项在数学上已退化——
#   · 中位/均值偏离：n=2 时中位数恒等于均值，偏离度恒为 0 → 必然满分
#   · 爆款集中度：max/avg ∈ [1, n]，n=2 时永远 <3 倍 → 必然满分（无法触及"依赖爆款"档）
#   · 互动稳定性 CV：2 点样本的离散度无统计意义，且会与集中度结论互相矛盾
#   · 发布频率：用「返回条数 / 样本时间窗」推算，窗口只有几天时只是两条之间的间隔倒数
SAMPLE_MIN = 5

# 「中位/均值偏离」退化更早：n=2 时中位数恒等于均值，故只需 n>=3 即可判别
MEDIAN_SAMPLE_MIN = 3

# 趋势类指标（近期趋势 / 衰退预警 / 刷量预警的"近期骤降"）的样本门槛与作品年龄门槛。
#
# 背景：接口只给「截至采集时刻的累计互动量」这一张快照，而抖音的互动累积是
# 次线性的，且高度集中在发布后最初几小时。因此样本里越新的作品，累计量必然越少。
# 直接拿不同年龄作品的累计量做「近期 vs 早期」比较，会把「最近发布」系统性
# 误判成「衰退」——年龄差多大，假的跌幅就有多大。
#
# 实测（账号 小边边同志，采集于 2026-09-23 02:07）：
#   最老一条 6.3 天 / 38,513 累计  →  日均 6,094
#   最新一条 0.3 天 / 18,062 累计  →  日均 64,507
#   累计量看「暴跌 53%、严重衰退」，换算日均实为「上涨 10 倍」——结论完全相反。
#
# 故趋势比较只纳入「已跑够时间」的作品；剩余成熟样本不足时，该子项不计入分母
# （不奖不罚），而不是拿未成熟的作品给出错误的衰退结论。
TREND_MATURE_DAYS = 3
TREND_MIN_SAMPLE = 4


# ============================================================
# 维度1: 账号基础画像 (10分)
# ============================================================

def diagnose_profile(acc):
    score = 0
    details = []
    # 卷面 8 分：头像2 + 简介3 + 地域2 + 抖音号1
    # （性别/年龄仅作信息展示，不参与计分，见下方「人群标签」说明）
    effective_max = 8

    # 头像 (2分)
    avatar = acc.get("avatarUrl", "")
    if avatar:
        score += 2
        details.append(("头像", "已设置", 2, 2))
    else:
        details.append(("头像", "未设置", 0, 2))

    # 简介 (3分)
    sig = acc.get("signature", "") or ""
    if len(sig) >= 15:
        score += 3
        details.append(("简介", f"{len(sig)}字，内容完整", 3, 3))
    elif len(sig) > 0:
        score += 1
        details.append(("简介", f"仅{len(sig)}字，偏短", 1, 3))
    else:
        details.append(("简介", "空简介", 0, 3))

    # 地域信息完整度 (2分)
    # 注意：不再要求 province == ipLocation。明星号常驻剧组/异地工作，
    # 机构号由团队代运营，注册地与 IP 属地不一致属行业常态，不应据此扣分。
    province = acc.get("province", "") or ""
    ip_loc = acc.get("ipLocation", "") or ""
    if province and ip_loc:
        score += 2
        details.append(("地域信息完整度", f"{province} / IP({ip_loc})，信息完整", 2, 2))
    elif province or ip_loc:
        score += 1
        details.append(("地域信息完整度", f"仅{'省份' if province else 'IP属地'}有值，信息不全", 1, 2))
    else:
        details.append(("地域信息完整度", "地域信息缺失", 0, 2))

    # 人群标签 (不计分，仅信息展示)
    #
    # 该子项原为 2 分，且「接口未提供的字段不计入分母」。但接口一旦提供了字段，
    # 取值必然有效（不存在「提供了但无效」的情况），于是 gained 恒等于分母 full ——
    # 子项恒定拿满，毫无区分度；更糟的是它会**稀释其他缺失项的扣分**：
    #   A：地域缺失(1/2) + 性别年龄可用  → (7+2)/(8+2) = 90.0%
    #   B：地域缺失(1/2) + 性别年龄缺失  →  7/8        = 87.5%
    # 两者资料质量完全相同，A 却仅因「接口恰好返回了性别」而得分更高，
    # 与「账号不为数据可得性买单」的原则相悖（该原则意味着既不该罚、也不该奖）。
    #
    # 故改为**不计分的展示项**：既保留数据完整度信息供人工判断，
    # 又不再影响任何账号的得分。账号基础画像卷面分相应由 10 调整为 8。
    gender = acc.get("gender", "")
    age = acc.get("age")
    avail = int(_field_provided(gender)) + int(_field_provided(age))
    detail_str = f"性别={gender if _field_provided(gender) else '未知'}, " \
                 f"年龄={age if _field_provided(age) else '未知'}"
    detail_str += f"（接口提供 {avail}/2，仅展示不计分）"
    details.append(("人群标签", detail_str, 0, 0))

    # 账号ID完整度 (1分)
    account_id = acc.get("accountId", "")
    if account_id:
        score += 1
        details.append(("抖音号", account_id, 1, 1))
    else:
        details.append(("抖音号", "未设置", 0, 1))

    return score, details, effective_max


# ============================================================
# 维度2: 内容生产力 (15分)
# ============================================================

def diagnose_productivity(acc):
    score = 0
    details = []
    effective_max = 15
    aweme_count = acc.get("awemeCount", 0) or 0
    total_favorited = acc.get("totalFavorited", 0) or 0
    works = acc.get("works", []) or []
    tier = account_tier(acc.get("followerCount", 0) or 0)[0]

    # 作品总量 (5分) —— 门槛随量级自适应，见 VOLUME_BENCH
    v_high, v_normal, v_over = VOLUME_BENCH[tier]
    if aweme_count >= v_over:
        s = 4
        label = f"{aweme_count}，极高产(超{v_over}条，需警惕刷量)"
    elif aweme_count >= v_high:
        s = 5
        label = f"{aweme_count}，高产({tier}级线{v_high}条)"
    elif aweme_count >= v_normal:
        s = 4
        label = f"{aweme_count}，正常({tier}级线{v_normal}条)"
    else:
        s = 2
        label = f"{aweme_count}，偏少(低于{tier}级线{v_normal}条)"
    score += s
    details.append(("作品总量", label, s, 5))

    # 人均获赞 (5分) —— 门槛随量级自适应，见 AVG_LIKE_BENCH
    avg_likes = _safe_div(total_favorited, aweme_count)
    l_high, l_good, l_normal = AVG_LIKE_BENCH[tier]
    if avg_likes >= l_high:
        s = 5
        label = f"{avg_likes:,.0f}，高效({tier}级线{l_high:,})"
    elif avg_likes >= l_good:
        s = 4
        label = f"{avg_likes:,.0f}，良好({tier}级线{l_good:,})"
    elif avg_likes >= l_normal:
        s = 3
        label = f"{avg_likes:,.0f}，正常({tier}级线{l_normal:,})"
    else:
        s = 1
        label = f"{avg_likes:,.0f}，低效(低于{l_normal:,})"
    score += s
    details.append(("人均获赞", label, s, 5))

    # 发布频率 (5分)
    # 用「返回样本条数 / 样本时间窗」推算。注意该指标只反映样本窗口内的更新节奏，
    # 样本过少时窗口只有几天，推算结果实际是「最后两条之间的间隔倒数」，不代表账号产能，
    # 故 n < SAMPLE_MIN 时不计入分母。
    if len(works) < SAMPLE_MIN:
        details.append(("发布频率", f"仅返回{len(works)}条作品，样本不足，不计入分母", 0, 0))
        effective_max -= 5
    else:
        times = sorted([_parse_dt(w.get("createTime", "")) for w in works if _parse_dt(w.get("createTime", ""))])
        if len(times) >= 2:
            span_days = (times[-1] - times[0]).total_seconds() / 86400
            if span_days == 0:
                span_days = 1
            freq = len(works) / span_days
            if freq < 0.5:
                s = 2
                label = f"日均{freq:.2f}条，低频"
            elif freq <= 2:
                s = 5
                label = f"日均{freq:.2f}条，正常"
            elif freq <= 3:
                s = 4
                label = f"日均{freq:.2f}条，高频"
            else:
                s = 3
                label = f"日均{freq:.2f}条，极高频"
            score += s
            details.append(("发布频率", f"{label}（样本窗{span_days:.0f}天）", s, 5))
        else:
            details.append(("发布频率", "时间数据不足，不计入分母", 0, 0))
            effective_max -= 5

    return score, details, effective_max


# ============================================================
# 维度3: 互动健康度 (30分)
# ============================================================

def diagnose_engagement(acc):
    score = 0
    details = []
    effective_max = 30
    followers = acc.get("followerCount", 0) or 0
    total_favorited = acc.get("totalFavorited", 0) or 0
    works = acc.get("works", []) or []
    tier, tier_label = account_tier(followers)

    # 粉丝获赞比 (10分) —— 逐档平滑，消除原「5~20 一刀切」造成的评分跳变
    fan_like_ratio = _safe_div(total_favorited, followers)
    if fan_like_ratio >= 25:
        s, label = 10, f"{fan_like_ratio:.2f}，优质(长尾效应强)"
    elif fan_like_ratio >= 15:
        s, label = 9, f"{fan_like_ratio:.2f}，良好"
    elif fan_like_ratio >= 8:
        s, label = 8, f"{fan_like_ratio:.2f}，正常"
    elif fan_like_ratio >= 3:
        s, label = 6, f"{fan_like_ratio:.2f}，一般"
    elif fan_like_ratio >= 1:
        s, label = 3, f"{fan_like_ratio:.2f}，偏低"
    else:
        s, label = 1, f"{fan_like_ratio:.2f}，极低"
    score += s
    details.append(("粉丝获赞比", label, s, 10))

    # 粉丝互动率 (10分) —— 基准随账号量级自适应（核心修正）
    if works and followers > 0:
        avg_inter = statistics.mean([w.get("interactiveCount", 0) or 0 for w in works])
        engagement_rate = _safe_div(avg_inter, followers) * 100
        full, good, low = ENGAGEMENT_BENCH[tier]
        if engagement_rate >= full:
            s = 10
            label = f"{engagement_rate:.2f}%，优秀({tier_label}基准≥{full}%)"
        elif engagement_rate >= good:
            s = 7
            label = f"{engagement_rate:.2f}%，良好({tier_label}基准≥{good}%)"
        elif engagement_rate >= low:
            s = 4
            label = f"{engagement_rate:.2f}%，偏低({tier_label}基准≥{low}%)"
        else:
            s = 1
            label = f"{engagement_rate:.2f}%，极低({tier_label}基准<{low}%)"
        score += s
        details.append(("粉丝互动率", label, s, 10))
    elif followers <= 0:
        # 有作品但粉丝数为 0：比值的分母缺失，不可计算 → 不计入分母
        details.append(("粉丝互动率", "粉丝数为 0，比率不可计算，不计入分母", 0, 0))
        effective_max -= 10
    else:
        # 无近期作品：账号没有可评估的内容表现，按最低档计分。
        # 「无作品数据」与「样本不足」是两回事——后者是数据存在但不可靠，故不计入
        # 分母；此处是账号确实没有内容可评，属于负面信号，应与同维度其余
        # 「无作品数据」子项口径一致（均为 0 分），不能一处给 0、一处给中性 3 分。
        details.append(("粉丝互动率", "无作品数据，无法计算", 0, 10))

    # 互动结构比 (5分) —— 放宽门槛
    # 超头部号评论/转发被体量稀释，原「评论>5% 且 分享>5%」门槛过窄，
    # 会误判健康的结构为「一般」。
    if works:
        total_digg = sum(w.get("diggCount", 0) or 0 for w in works)
        total_comment = sum(w.get("commentCount", 0) or 0 for w in works)
        total_share = sum(w.get("shareCount", 0) or 0 for w in works)
        if total_digg > 0:
            comment_ratio = total_comment / total_digg * 100
            share_ratio = total_share / total_digg * 100
            ratio_text = f"赞:评:转 = 100:{comment_ratio:.1f}:{share_ratio:.1f}"
            if comment_ratio >= 4 and share_ratio >= 4:
                s, label = 5, f"{ratio_text}，健康"
            elif comment_ratio >= 3 and share_ratio >= 3:
                s, label = 4, f"{ratio_text}，较健康"
            elif comment_ratio >= 2 or share_ratio >= 2:
                s, label = 3, f"{ratio_text}，一般"
            else:
                s, label = 2, f"{ratio_text}，互动单一"
            score += s
            details.append(("互动结构比", label, s, 5))
        else:
            # 分子分母同时为 0（赞/评/转全为 0），比值在数学上不存在，
            # 即不可计算 → 不计入分母。该情形已由「零互动占比」与「爆款率」
            # 充分反映，此处再记 0 分属于对同一事实的重复扣分。
            details.append(("互动结构比", "点赞总数为 0，结构比不可计算，不计入分母", 0, 0))
            effective_max -= 5
    else:
        details.append(("互动结构比", "无作品数据", 0, 5))

    # 作品均互动 (5分)
    # 修正：原实现用 followerCount×3% 作基准，与上一项「粉丝互动率」计算的
    # 是同一个比率(avg_inter/followers)，等于把同一指标计了两遍、共占15/30分。
    # 改为衡量「绝对传播量级」，与互动率形成互补：
    # 互动率看粉丝黏性，绝对量级看单条声量。
    if works:
        avg_inter = statistics.mean([w.get("interactiveCount", 0) or 0 for w in works])
        shown = _fmt_num(int(avg_inter))
        # 分档线随量级自适应（见 INTERACTION_BENCH），避免尾部号因绝对量级小被误判
        b_epic, b_strong, b_mid, b_weak = INTERACTION_BENCH[tier]
        if avg_inter >= b_epic:
            s, label = 5, f"均{shown}互动，现象级(超头部/头部基准)"
        elif avg_inter >= b_strong:
            s, label = 4, f"均{shown}互动，强传播"
        elif avg_inter >= b_mid:
            s, label = 3, f"均{shown}互动，中等"
        elif avg_inter >= b_weak:
            s, label = 2, f"均{shown}互动，偏弱"
        else:
            s, label = 1, f"均{shown}互动，微弱"
        score += s
        details.append(("作品均互动", label, s, 5))
    else:
        details.append(("作品均互动", "无作品数据", 0, 5))

    return score, details, effective_max


# ============================================================
# 维度4: 内容质量 (20分)
# ============================================================

def diagnose_quality(acc):
    score = 0
    details = []
    effective_max = 20
    followers = acc.get("followerCount", 0) or 0
    works = acc.get("works", []) or []
    tier, tier_label = account_tier(followers)

    if not works:
        # 无近期作品 → 无内容表现可言，四个子项均按最低档（0 分）计。
        # 子项名必须与下方正式路径完全一致（原实现此处写作「中位互动」，
        # 与别处的「中位/均值偏离」不符，会导致报告出现两个不同名字的同一指标）。
        details.append(("爆款率", "无作品数据", 0, 6))
        details.append(("中位/均值偏离", "无作品数据", 0, 4))
        details.append(("互动稳定性", "无作品数据", 0, 5))
        details.append(("零互动占比", "无作品数据", 0, 5))
        return 0, details, effective_max

    digg_counts = [w.get("diggCount", 0) or 0 for w in works]
    inter_counts = [w.get("interactiveCount", 0) or 0 for w in works]

    # 爆款率 (6分) —— 爆款线随量级自适应（核心修正）
    # 原规则统一要求「点赞 > 粉丝数×10%」：670 万粉的账号需单条破 67 万赞
    # 才算爆款，实际上超头部号几乎不可能达成，会导致爆款率恒为 0。
    # 改为按量级设定点赞率线（S 级 1%、A 级 2%、B 级 5%、C 级 10%）。
    hit_line = HIT_BENCH[tier]
    threshold = followers * hit_line / 100
    hits = sum(1 for d in digg_counts if d > threshold)
    hit_rate = hits / len(works) * 100
    if hit_rate > 10:
        s = 6
        label = f"{hit_rate:.1f}%，优秀(爆款线={tier_label}粉丝×{hit_line}%)"
    elif hit_rate > 5:
        s = 4
        label = f"{hit_rate:.1f}%，良好(爆款线={tier_label}粉丝×{hit_line}%)"
    elif hit_rate > 0:
        s = 3
        label = f"{hit_rate:.1f}%，偏低(爆款线={tier_label}粉丝×{hit_line}%)"
    else:
        s = 1
        label = f"{hit_rate:.1f}%，无爆款(爆款线={tier_label}粉丝×{hit_line}%)"
    score += s
    details.append(("爆款率", label, s, 6))

    # 中位互动 vs 均值偏离 (4分)
    # 何时不计入分母：n=2 时中位数恒等于均值，偏离度恒为 0 → 必然满分、无法区分好坏。
    # 注意原实现的 n<2 分支给 2/4，属于「样本不足反而白拿分」，一并改为不计入。
    if len(digg_counts) < MEDIAN_SAMPLE_MIN:
        details.append(("中位/均值偏离",
                        f"仅{len(digg_counts)}条作品，中位数恒等于均值，无法区分，不计入分母", 0, 0))
        effective_max -= 4
    else:
        med = statistics.median(digg_counts)
        avg = statistics.mean(digg_counts)
        if avg > 0:
            deviation = abs(med - avg) / avg
            if deviation < 0.2:
                s = 4
                label = f"中位{_fmt_num(int(med))} vs 均值{_fmt_num(int(avg))}，分布均匀"
            elif deviation < 0.5:
                s = 3
                label = f"中位{_fmt_num(int(med))} vs 均值{_fmt_num(int(avg))}，轻度偏离"
            else:
                s = 1
                label = f"中位{_fmt_num(int(med))} vs 均值{_fmt_num(int(avg))}，严重偏离(靠爆款拉动)"
            score += s
            details.append(("中位/均值偏离", label, s, 4))
        else:
            # 点赞全为 0 → 偏离度 = 0/0，在数学上不存在，不计入分母。
            # 与「互动结构比」同理，该事实已由「零互动占比」「爆款率」反映。
            details.append(("中位/均值偏离", "点赞总数为 0，偏离度不可计算，不计入分母", 0, 0))
            effective_max -= 4

    # 互动稳定性 (5分) - 变异系数
    # 何时不计入分母：n < SAMPLE_MIN 时 CV 由极少数样本决定，无统计意义，
    # 且实测会与「爆款集中度」给出相反结论（本例 CV 判"严重依赖爆款"、
    # 集中度判"均匀分布"），两个指标互相打架时不能采信任一。
    if len(inter_counts) < SAMPLE_MIN:
        details.append(("互动稳定性",
                        f"仅{len(inter_counts)}条作品，离散度无统计意义，不计入分母", 0, 0))
        effective_max -= 5
    elif statistics.mean(inter_counts) <= 0:
        # 互动全为 0：CV = 标准差/均值 = 0/0，不可计算。注意 `_cv()` 在均值为 0 时
        # 返回 0.0，与「真正稳定」的取值无法区分，会把这个账号误判成「稳定输出 5/5」，
        # 故必须在调用前先拦截。
        details.append(("互动稳定性", "互动总数为 0，变异系数不可计算，不计入分母", 0, 0))
        effective_max -= 5
    else:
        cv = _cv(inter_counts)
        if cv < 0.5:
            s = 5
            label = f"CV={cv:.2f}，稳定输出"
        elif cv < 1.0:
            s = 3
            label = f"CV={cv:.2f}，波动一般"
        else:
            s = 1
            label = f"CV={cv:.2f}，严重依赖爆款"
        score += s
        details.append(("互动稳定性", label, s, 5))

    # 零互动占比 (5分)
    zero_count = sum(1 for d in digg_counts if d < 10)
    zero_rate = zero_count / len(works) * 100
    if zero_rate < 5:
        s = 5
        label = f"{zero_rate:.1f}%，质量稳定"
    elif zero_rate < 20:
        s = 3
        label = f"{zero_rate:.1f}%，部分低质"
    else:
        s = 1
        label = f"{zero_rate:.1f}%，大量低质/限流"
    score += s
    details.append(("零互动占比", label, s, 5))

    return score, details, effective_max


# ============================================================
# 维度5: 内容趋势 (15分)
# ============================================================

def diagnose_trend(acc):
    score = 0
    details = []
    works = acc.get("works", []) or []
    crawl_time = _parse_dt(acc.get("crawlTime", ""))
    # 有效满分：数据不足的指标不计入分母，避免账号为「接口没给数据」买单
    effective_max = 15

    if not works:
        details.append(("近期趋势", "无作品数据", 0, 5))
        details.append(("爆款集中度", "无作品数据", 0, 5))
        details.append(("最新活跃度", "无作品数据", 0, 5))
        return 0, details, effective_max

    # 按时间排序
    sorted_works = sorted(works, key=lambda w: _parse_dt(w.get("createTime", "")) or datetime.min)

    # 近期趋势 (5分) - 最近30% vs 最早30%
    n = len(sorted_works)
    aweme_count = acc.get("awemeCount", 0) or 0

    # 只比较「已跑够时间」的作品：接口给的是一张累计量的快照，
    # 越新的作品累计时间越短、累计量必然越少，直接比较会把「最近发布」
    # 误判成「衰退」。详见 TREND_MATURE_DAYS 处的说明。
    trend_ref = _trend_ref_time(sorted_works, crawl_time)
    mature = [w for w in sorted_works if _work_age_days(w, trend_ref) >= TREND_MATURE_DAYS]

    if len(mature) >= TREND_MIN_SAMPLE:
        m = len(mature)
        early = mature[:max(1, m // 3)]
        recent = mature[-(max(1, m // 3)):]
        early_avg = statistics.mean([w.get("interactiveCount", 0) or 0 for w in early])
        recent_avg = statistics.mean([w.get("interactiveCount", 0) or 0 for w in recent])
        if early_avg <= 0:
            # 早期均互动为 0 → 变化率 = Δ/0，不可计算 → 不计入分母（同 0/0 原则）
            effective_max -= 5
            details.append(("近期趋势", "早期作品互动为 0，变化率不可计算，不计入分母", 0, 0))
        else:
            change = (recent_avg - early_avg) / early_avg * 100
            if change > 20:
                s = 5
                label = f"近期上升{change:.0f}%，增长期"
            elif change > -20:
                s = 4
                label = f"近期变化{change:+.0f}%，平稳期"
            elif change > -50:
                s = 2
                label = f"近期下降{abs(change):.0f}%，衰退期"
            else:
                s = 1
                label = f"近期暴跌{abs(change):.0f}%，严重衰退"
            score += s
            details.append(("近期趋势", label, s, 5))
    else:
        # 成熟样本不足：不奖不罚，也不给出可能反向的结论。
        effective_max -= 5
        details.append((
            "近期趋势",
            f"已满{TREND_MATURE_DAYS}天的作品仅{len(mature)}条（返回{n}条/共{aweme_count}条），"
            f"快照下趋势不可判定，不计入分母",
            0, 0,
        ))

    # 爆款集中度 (5分)
    # 两种情形不计入分母：
    #   ① 集中度 = max/avg，数学上恒 ∈ [1, n]。样本只有 2 条时永远 < 3 倍、
    #      必然拿到「均匀分布」满分——它根本无法触及「依赖爆款」档，属于
    #      「无法区分好坏却给满分」的退化子项。
    #   ② 互动全为 0 时 max/avg = 0/0，比值在数学上不存在（该事实已由
    #      「零互动占比」反映，此处再记 0 分属重复扣分）。
    inter_counts = [w.get("interactiveCount", 0) or 0 for w in works]
    if len(inter_counts) < SAMPLE_MIN:
        details.append(("爆款集中度",
                        f"仅{len(inter_counts)}条作品，max/均值≤{len(inter_counts)}倍，无法区分，不计入分母", 0, 0))
        effective_max -= 5
    elif statistics.mean(inter_counts) <= 0:
        details.append(("爆款集中度", "互动总数为 0，集中度不可计算，不计入分母", 0, 0))
        effective_max -= 5
    else:
        max_inter = max(inter_counts)
        avg_inter = statistics.mean(inter_counts)
        concentration = max_inter / avg_inter
        if concentration < 3:
            s = 5
            label = f"最大/均值={concentration:.1f}倍，均匀分布"
        elif concentration < 5:
            s = 4
            label = f"最大/均值={concentration:.1f}倍，较为均匀"
        elif concentration < 10:
            s = 2
            label = f"最大/均值={concentration:.1f}倍，依赖爆款"
        else:
            s = 1
            label = f"最大/均值={concentration:.1f}倍，严重依赖单条"
        score += s
        details.append(("爆款集中度", label, s, 5))

    # 最新活跃度 (5分)
    latest_time = _parse_dt(sorted_works[-1].get("createTime", ""))
    if latest_time:
        # 参考时间取账号采集时间，但若采集时间早于最新作品（基础信息字段滞后，
        # 如 crawlTime=2026-07-07 而作品已更新到 2026-09-21），该字段不可信，
        # 回退到当前时间，避免算出负数天数被误判为「活跃」。
        stale = bool(crawl_time) and crawl_time < latest_time
        ref_time = datetime.now() if (not crawl_time or stale) else crawl_time
        days_since = max(0, (ref_time - latest_time).days)
        if days_since <= 3:
            s = 5
            label = f"最近{days_since}天前发布，活跃"
        elif days_since <= 7:
            s = 4
            label = f"最近{days_since}天前发布，正常"
        elif days_since <= 14:
            s = 2
            label = f"最近{days_since}天前发布，偏沉默"
        else:
            s = 1
            label = f"最近{days_since}天前发布，已断更"
        if stale:
            label += "（采集时间滞后，按当前时间校正）"
        score += s
        details.append(("最新活跃度", label, s, 5))
    else:
        # 作品缺 createTime → 活跃天数不可计算。这是「字段缺失」而非「账号没内容」，
        # 按不奖不罚原则不计入分母（原实现给中性 3/5，口径与其余字段缺失处理不一致）。
        effective_max -= 5
        details.append(("最新活跃度", "作品时间缺失，活跃天数不可计算，不计入分母", 0, 0))

    return score, details, effective_max


# ============================================================
# 维度6: 粉丝质量 (10分)
# ============================================================

def diagnose_fans(acc):
    score = 0
    details = []
    effective_max = 10
    followers = acc.get("followerCount", 0) or 0
    total_favorited = acc.get("totalFavorited", 0) or 0
    works = acc.get("works", []) or []
    tier, tier_label = account_tier(followers)

    # 粉丝规模 (4分) —— 直接由量级派生，避免与 TIER_LEVELS 重复定义同一组粉丝数门槛
    # （重复定义一旦改动漏改一处，量级判定与粉丝规模得分就会互相矛盾）
    s = {"S": 4, "A": 3, "B": 2, "C": 1}[tier]
    score += s
    details.append(("粉丝规模", f"{_fmt_num(followers)}，{tier_label}", s, 4))

    # 粉丝互动比 (3分) —— 同样改用量级自适应基准
    if works and followers > 0:
        avg_inter = statistics.mean([w.get("interactiveCount", 0) or 0 for w in works])
        fan_eng = _safe_div(avg_inter, followers) * 100
        _, good, low = ENGAGEMENT_BENCH[tier]
        if fan_eng >= good:
            s = 3
            label = f"{fan_eng:.2f}%，粉丝活跃({tier_label}基准≥{good}%)"
        elif fan_eng >= low:
            s = 2
            label = f"{fan_eng:.2f}%，粉丝一般({tier_label}基准≥{low}%)"
        else:
            s = 1
            label = f"{fan_eng:.2f}%，粉丝不活跃({tier_label}基准<{low}%)"
        score += s
        details.append(("粉丝互动比", label, s, 3))
    elif followers <= 0:
        details.append(("粉丝互动比", "粉丝数为 0，比率不可计算，不计入分母", 0, 0))
        effective_max -= 3
    else:
        # 无作品数据：与「粉丝互动率」同口径，按最低档计分而非给中性分
        details.append(("粉丝互动比", "无作品数据，无法计算", 0, 3))

    # 获赞/粉丝背离 (3分)
    ratio = _safe_div(total_favorited, followers)
    if ratio > 100:
        s = 1
        label = f"获赞/粉丝={ratio:.1f}，异常高(疑似刷赞/搬运)"
    elif ratio > 50:
        s = 2
        label = f"获赞/粉丝={ratio:.1f}，偏高"
    elif ratio > 0:
        s = 3
        label = f"获赞/粉丝={ratio:.1f}，正常"
    else:
        s = 1
        label = "数据异常"
    score += s
    details.append(("获赞/粉丝背离", label, s, 3))

    return score, details, effective_max


# ============================================================
# 预警检测
# ============================================================

def check_warnings(acc):
    warnings = []
    followers = acc.get("followerCount", 0) or 0
    total_favorited = acc.get("totalFavorited", 0) or 0
    works = acc.get("works", []) or []
    tier, tier_label = account_tier(followers)

    # 僵尸粉预警阈值与「粉丝互动率」评分基准保持同一套量级线，
    # 避免出现「互动率被判定为良好、却又触发僵尸粉预警」的自相矛盾。
    if works and followers > 50000:
        avg_inter = statistics.mean([w.get("interactiveCount", 0) or 0 for w in works])
        rate = _safe_div(avg_inter, followers) * 100
        _, _, low = ENGAGEMENT_BENCH[tier]
        if rate < low:
            warnings.append(
                f"僵尸粉预警: 粉丝互动率 {rate:.2f}% < {low}%（{tier_label}基准）且粉丝数 > 5万"
            )

    # 趋势类预警（刷量骤降 / 衰退）与「近期趋势」共用同一份成熟样本，
    # 避免出现「评分判定为平稳、预警却报衰退」的自相矛盾，
    # 以及把「最近才发布、累计量天然偏少」误读为骤降。详见 TREND_MATURE_DAYS 说明。
    _ref = _trend_ref_time(works, _parse_dt(acc.get("crawlTime", "")))
    mature_works = sorted(
        [w for w in works if _work_age_days(w, _ref) >= TREND_MATURE_DAYS],
        key=lambda w: _parse_dt(w.get("createTime", "")) or datetime.min,
    )
    declining = False
    if len(mature_works) >= TREND_MIN_SAMPLE:
        m = len(mature_works)
        _early_avg = statistics.mean(
            [w.get("interactiveCount", 0) or 0 for w in mature_works[:max(1, m // 3)]])
        _recent_avg = statistics.mean(
            [w.get("interactiveCount", 0) or 0 for w in mature_works[-(max(1, m // 3)):]])
        if _early_avg > 0:
            declining = _recent_avg < _early_avg * 0.5

    ratio = _safe_div(total_favorited, followers)
    if ratio > 100 and declining:
        warnings.append("刷量预警: 获赞/粉丝比 > 100 且近期互动骤降")

    if declining:
        warnings.append("衰退预警: 近期作品均互动 < 早期的 50%（仅基于已满"
                        f"{TREND_MATURE_DAYS}天的 {len(mature_works)} 条作品）")

    zero_count = sum(1 for w in works if (w.get("diggCount", 0) or 0) < 10)
    if works and zero_count / len(works) > 0.3:
        warnings.append("限流预警: 零互动占比 > 30%")

    crawl_time = _parse_dt(acc.get("crawlTime", ""))
    if works:
        latest = max(_parse_dt(w.get("createTime", "")) or datetime.min for w in works)
        # 与「最新活跃度」保持同一套参考时间逻辑：采集时间滞后于作品时回退当前时间
        if latest != datetime.min:
            ref_time = datetime.now() if (not crawl_time or crawl_time < latest) else crawl_time
            if (ref_time - latest).days > 14:
                warnings.append("断更预警: 最新作品距数据采集时间 > 14 天")

    inter_counts = [w.get("interactiveCount", 0) or 0 for w in works]
    if inter_counts:
        max_inter = max(inter_counts)
        avg_inter = statistics.mean(inter_counts)
        if avg_inter > 0 and max_inter / avg_inter > 10:
            warnings.append("单条依赖预警: 最大爆款互动 > 均值的 10 倍")

    return warnings


# ============================================================
# 报告生成
# ============================================================

WEIGHTS = {
    "profile": 0.10,
    "productivity": 0.15,
    "engagement": 0.30,
    "quality": 0.20,
    "trend": 0.15,
    "fans": 0.10,
}

DIM_NAMES = {
    "profile": "账号基础画像",
    "productivity": "内容生产力",
    "engagement": "互动健康度",
    "quality": "内容质量",
    "trend": "内容趋势",
    "fans": "粉丝质量",
}

DIM_MAX = {
    "profile": 8,
    "productivity": 15,
    "engagement": 30,
    "quality": 20,
    "trend": 15,
    "fans": 10,
}


def composite_score(diagnoses):
    """由各维度 (score, details, effective_max) 计算综合评分。

    综合评分 = Σ(维度得分 / 维度有效满分 × 100 × 维度权重)，按文档约定四舍五入取整。
    统一在此实现，避免报告与测试各写一套导致口径漂移。
    """
    total = 0.0
    for key in ("profile", "productivity", "engagement", "quality", "trend", "fans"):
        score, _details, eff_max = diagnoses[key]
        total += _safe_div(score, eff_max) * 100 * WEIGHTS[key]
    # Python 内置 round() 为银行家舍入（四舍六入五成双），在 .5 边界偏低，
    # 与「四舍五入」的中文约定不符，故显式用 ROUND_HALF_UP；
    # 先把累计浮点误差归一到 6 位小数，避免 94.499999 被误判为 94。
    return int(Decimal(str(round(total, 6))).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def generate_report(acc):
    lines = []
    lines.append("=" * 60)
    lines.append("               抖音账号诊断报告")
    lines.append("=" * 60)

    # 基本信息
    lines.append("")
    lines.append("【基本信息】")
    lines.append(f"  昵称:     {acc.get('nickname', 'N/A')}")
    lines.append(f"  抖音号:   {acc.get('accountId', 'N/A')}")
    lines.append(f"  UID:      {acc.get('uid', 'N/A')}")
    lines.append(f"  粉丝数:   {_fmt_num(acc.get('followerCount', 0))}")
    lines.append(f"  作品数:   {_fmt_num(acc.get('awemeCount', 0))}")
    lines.append(f"  获赞总数: {_fmt_num(acc.get('totalFavorited', 0))}")
    lines.append(f"  地区:     {(acc.get('province') or '')}{(acc.get('city') or '') or 'N/A'}")
    lines.append(f"  IP属地:   {acc.get('ipLocation', 'N/A')}")
    tier_code, tier_label = account_tier(acc.get("followerCount", 0) or 0)
    lines.append(f"  账号量级: {tier_code} 级 {tier_label}")
    lines.append(f"  数据时间: {acc.get('crawlTime', 'N/A')}")

    # 执行诊断
    diagnoses = {
        "profile": diagnose_profile(acc),
        "productivity": diagnose_productivity(acc),
        "engagement": diagnose_engagement(acc),
        "quality": diagnose_quality(acc),
        "trend": diagnose_trend(acc),
        "fans": diagnose_fans(acc),
    }

    # 各维度明细
    lines.append("")
    lines.append("【维度评分明细】")
    for key in ["profile", "productivity", "engagement", "quality", "trend", "fans"]:
        score, details, effective_max = diagnoses[key]
        lines.append("")
        suffix = "" if effective_max == DIM_MAX[key] else f" [有效满分{effective_max}，满分{DIM_MAX[key]}]"
        lines.append(f"  {DIM_NAMES[key]} ({score}/{effective_max}){suffix}")
        for item_name, desc, gained, full in details:
            if full == 0:
                lines.append(f"    [-----] {item_name}: {desc} (不计入)")
                continue
            bar = "+" * gained + "-" * (full - gained)
            lines.append(f"    [{bar}] {item_name}: {desc} ({gained}/{full})")

    # 综合评分（统一由 composite_score 计算，避免与测试各写一套导致口径漂移）
    lines.append("")
    lines.append("=" * 60)
    total_score = composite_score(diagnoses)
    if total_score >= 85:
        grade = "优质账号"
        emoji = "🟢"
    elif total_score >= 70:
        grade = "正常账号"
        emoji = "🟡"
    elif total_score >= 50:
        grade = "待优化"
        emoji = "🟠"
    else:
        grade = "风险账号"
        emoji = "🔴"
    lines.append(f"  综合诊断评分: {total_score}/100  {emoji} {grade}")
    lines.append("=" * 60)

    # 样本置信度提示
    # 样本过少的子项虽已剔除出分母，但**保留下来的均值型指标**（粉丝互动率、
    # 作品均互动、爆款率等）仍由极少数样本决定，必须提示复核，
    # 避免使用者把「2 条作品的结论」当成账号全貌。
    works_conf = acc.get("works", []) or []
    if not works_conf:
        lines.append("")
        lines.append(
            f"  ⓘ 无近期作品数据：接口未返回任何作品（账号标注共 {acc.get('awemeCount', 0)} 条）。"
            "互动健康度 / 内容质量 / 内容趋势 中依赖作品的子项均按最低档计分，"
            "分数偏低属预期，请先核对账号是否已清空作品、注销或长期停更。"
        )
    elif len(works_conf) < SAMPLE_MIN:
        lines.append("")
        lines.append(
            f"  ⓘ 数据置信度：接口仅返回 {len(works_conf)} 条作品"
            f"（账号共 {acc.get('awemeCount', 0)} 条），"
            "互动健康度 / 内容质量中的均值型指标基于过小样本，结论仅供参考。"
        )

    # 预警
    warnings = check_warnings(acc)
    if warnings:
        lines.append("")
        lines.append("【风险预警】")
        for w in warnings:
            lines.append(f"  ⚠ {w}")
    else:
        lines.append("")
        lines.append("【风险预警】无")

    # 近期作品（必须输出项）
    works = acc.get("works", []) or []
    lines.append("")
    lines.append("【近期作品详情】")
    if works:
        sorted_works = sorted(works, key=lambda w: _parse_dt(w.get("createTime", "")) or datetime.min, reverse=True)
        lines.append(f"  共 {len(sorted_works)} 条近期作品")
        lines.append("")
        for i, w in enumerate(sorted_works, 1):
            t = w.get("createTime", "N/A")
            d = w.get("diggCount", 0)
            c = w.get("commentCount", 0)
            s = w.get("shareCount", 0)
            inter = w.get("interactiveCount", 0)
            desc = (w.get("desc", "") or w.get("title", ""))[:60]
            url = w.get("workUrl", "")
            lines.append(f"  {i}. [{t}] 赞{d} 评{c} 转{s} 总{inter}")
            lines.append(f"     {desc}")
            lines.append(f"     {url}")
    else:
        lines.append("  无作品数据")

    lines.append("")
    lines.append("-" * 60)
    full, good, low = ENGAGEMENT_BENCH[tier_code]
    lines.append(
        f"  评分基准: 按「{tier_code} 级 {tier_label}」自适应 —— "
        f"互动率 优秀≥{full}% / 良好≥{good}% / 偏低≥{low}%；"
        f"爆款线=粉丝×{HIT_BENCH[tier_code]}%"
    )
    lines.append("  数据来源: 红狐RedFox API (https://redfox.hk/?source=github)")
    lines.append("-" * 60)

    return "\n".join(lines)


# ============================================================
# 主入口
# ============================================================

def main():
    args = sys.argv[1:]
    cli_key = None
    if "--api-key" in args:
        idx = args.index("--api-key")
        if idx + 1 < len(args):
            cli_key = args[idx + 1]
            args = args[:idx] + args[idx + 2:]
        else:
            print("[错误] --api-key 参数后需要提供密钥值")
            sys.exit(1)

    if not args:
        print("用法: python douyin_diagnosis.py <抖音昵称或抖音号> [--api-key <你的API Key>]")
        print("示例: python douyin_diagnosis.py 桔桔的茶园小动物")
        print("示例: python douyin_diagnosis.py xiaojuju8")
        sys.exit(1)

    keyword = args[0]
    print(f"正在查询抖音账号: {keyword} ...")

    acc = query_account(keyword, require_api_key(cli_key))
    if not acc:
        print("未查询到该抖音账号信息")
        print(f"- 抖音号 {keyword} 不存在或已被注销")
        print("- 抖音号输入有误 — 请核对是否区分大小写，是否为正确的抖音号（非 UID、非昵称）")
        print("- 尚未收录 — 当前仅收录了粉丝数≧1万的账号")
        print("- 申请收录 — 如需收录请发送邮件至 redfoxdata@proton.me，申请通过后可进行每日定时数据追踪与分析")
        sys.exit(1)

    report = generate_report(acc)
    print(report)


if __name__ == "__main__":
    main()
