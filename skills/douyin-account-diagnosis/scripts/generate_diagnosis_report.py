#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音账号诊断报告生成器 v4.0
基于红狐API /story/api/dyUser/query 接口返回的数据生成标准诊断报告
四维度评估:账号体量(35分) + 内容表现(35分) + 运营活跃度(20分) + 平台指数(10分)
"""

import json
from datetime import datetime
from typing import Dict, List, Optional


    # \u8d26\u53f7\u5206\u7c7b\u6620\u5c04: API\u539f\u8bcd \u2192 \u8f93\u51fa\u65b0\u8bcd
CATEGORY_MAP = {
    "全部": "全部",
    "才艺技能": "个人才艺",
    "生活": "生活vlog",
    "财经": "财富理财",
    "二次元": "二次元",
    "家居家装": "居家装修",
    "教育培训": "学习教育",
    "剧情演绎": "小剧场",
    "科技数码": "数码科技",
    "旅游": "旅行",
    "美食": "美食",
    "美妆": "化妆美容",
    "萌宠": "动物",
    "母婴亲子": "亲子",
    "汽车": "汽车",
    "情感心理": "情感",
    "三农": "三农",
    "医疗健康": "健康医学",
    "时尚": "潮流风尚",
    "舞蹈": "舞蹈才艺",
    "颜值": "颜值造型",
    "人文社科": "人文",
    "音乐": "音乐",
    "影视综艺": "影视",
    "健身": "身体锻炼",
    "体育": "体育",
    "明星八卦": "明星娱乐",
    "游戏": "游戏",
}


def map_category(raw: str) -> str:
    """将API原词分类映射为输出新词"""
    return CATEGORY_MAP.get(raw, raw)


def format_number(num) -> str:
    """格式化数字显示"""
    if num is None:
        return "-"
    try:
        num = int(num)
    except (ValueError, TypeError):
        return str(num)
    if num >= 100000000:
        return f"{num / 100000000:.1f}亿"
    elif num >= 10000:
        return f"{num / 10000:.1f}万"
    else:
        return f"{num:,}"


class DouyinDiagnosisReportV3:
    """抖音账号诊断宗师报告生成器 v4.1 - 四维度评估体系
    账号体量(35分) + 内容表现(35分) + 运营活跃度(20分) + 平台指数(10分)
    """

    # 全角冒号常量，避免Python 3.12+源码全角标点SyntaxError
    _C = "\uff1a"

    def __init__(self, account_data: Dict):
        """
        初始化报告生成器

        Args:
            account_data: 红狐API /story/api/dyUser/query 返回的账号数据(单条)
        """
        self.data = account_data
        self.works = account_data.get("works", [])
        self.similar_accounts = account_data.get("similarAccounts", [])

    # ==================== 主入口 ====================

    def generate_report(self) -> str:
        """生成完整诊断报告,严格按固定模板输出"""
        sections = [
            self._section_scoring_breakdown(),
            self._section_data_disclaimer(),
            self._section_basic_info(),
            self._section_core_data(),
            self._section_comprehensive_score(),
            self._section_optimization(),
            self._section_footer(),
        ]
        return "\n".join(sections)

    # ==================== 章节0：评分计算明细 ====================

    @staticmethod
    def _fmt(num) -> str:
        """格式化数字显示，带千位分隔符"""
        if num is None:
            return "-"
        try:
            num = int(num)
        except (ValueError, TypeError):
            return str(num)
        return f"{num:,}"

    def _section_scoring_breakdown(self) -> str:
        """生成评分计算明细，在诊断报告之前输出"""
        follower = self.data.get("followerCount", 0) or 0
        favorited = self.data.get("totalFavorited", 0) or 0
        ratio = favorited / follower if follower > 0 else 0
        works = self.works
        n = len(works)
        aweme_count = self.data.get("awemeCount", 0) or 0
        sig = self.data.get("signature", "") or ""
        redfox_index = self.data.get("redfoxIndex")

        # ---- 维度一：账号体量(35分) ----
        follower_levels = [
            (50000000, 22, "\u22655000\u4e07"), (10000000, 19, "1000-5000\u4e07"),
            (5000000, 16, "500-1000\u4e07"), (1000000, 12, "100-500\u4e07"),
            (500000, 9, "50-100\u4e07"), (100000, 5, "10-50\u4e07"),
            (10000, 2, "1-10\u4e07"), (0, 0, "<1\u4e07"),
        ]
        s1_f = 0; cond_f = ""
        for th, sc, cond in follower_levels:
            if follower >= th:
                s1_f, cond_f = sc, cond; break

        favorited_levels = [
            (1000000000, 8, "\u226510\u4ebf"), (100000000, 6, "1-10\u4ebf"),
            (10000000, 5, "1000\u4e07-1\u4ebf"), (1000000, 3, "100-1000\u4e07"),
            (100000, 1, "10-100\u4e07"), (0, 0, "<10\u4e07"),
        ]
        s2_fav = 0; cond_fav = ""
        for th, sc, cond in favorited_levels:
            if favorited >= th:
                s2_fav, cond_fav = sc, cond; break

        ratio_levels = [
            (15, 5, "\u226515"), (10, 4, "10-15"),
            (5, 3, "5-10"), (2, 2, "2-5"), (0, 1, "<2"),
        ]
        s3_r = 0; cond_r = ""
        for th, sc, cond in ratio_levels:
            if ratio >= th:
                s3_r, cond_r = sc, cond; break
        body_sub = s1_f + s2_fav + s3_r

        # ---- 维度二：内容表现(35分) ----
        total_digg = sum(w.get("diggCount", 0) or 0 for w in works)
        total_comment = sum(w.get("commentCount", 0) or 0 for w in works)
        total_share = sum(w.get("shareCount", 0) or 0 for w in works)
        avg_digg = total_digg / n if n > 0 else 0
        avg_comment = total_comment / n if n > 0 else 0
        avg_share = total_share / n if n > 0 else 0
        spread_coeff = (total_share / total_digg * 100) if total_digg > 0 else 0

        digg_levels = [
            (1000000, 13, "\u2265100\u4e07"), (500000, 11, "50-100\u4e07"),
            (100000, 9, "10-50\u4e07"), (10000, 7, "1-10\u4e07"),
            (1000, 4, "1000-1\u4e07"), (100, 2, "100-1000"), (0, 0, "<100"),
        ]
        s1_d = 0; cond_d = ""
        for th, sc, cond in digg_levels:
            if avg_digg >= th:
                s1_d, cond_d = sc, cond; break

        comment_levels = [
            (10000, 9, "\u22651\u4e07"), (5000, 7, "5000-1\u4e07"),
            (1000, 5, "1000-5000"), (100, 3, "100-1000"),
            (10, 1, "10-100"), (0, 0, "<10"),
        ]
        s2_c = 0; cond_c = ""
        for th, sc, cond in comment_levels:
            if avg_comment >= th:
                s2_c, cond_c = sc, cond; break

        share_levels = [
            (100000, 7, "\u226510\u4e07"), (10000, 6, "1-10\u4e07"),
            (1000, 4, "1000-1\u4e07"), (100, 2, "100-1000"),
            (10, 1, "10-100"), (0, 0, "<10"),
        ]
        s3_s = 0; cond_s = ""
        for th, sc, cond in share_levels:
            if avg_share >= th:
                s3_s, cond_s = sc, cond; break

        spread_levels = [
            (15, 6, "\u226515%"), (10, 5, "10-15%"),
            (5, 4, "5-10%"), (2, 2, "2-5%"), (0, 1, "<2%"),
        ]
        s4_sp = 0; cond_sp = ""
        for th, sc, cond in spread_levels:
            if spread_coeff >= th:
                s4_sp, cond_sp = sc, cond; break
        content_sub = s1_d + s2_c + s3_s + s4_sp

        # ---- 维度三：运营活跃度(20分) ----
        freq_levels = [
            (7, 8, "\u22657\u6761"), (4, 6, "4-6\u6761"),
            (2, 4, "2-3\u6761"), (1, 2, "1\u6761"), (0, 0, "0\u6761"),
        ]
        s1_fr = 0; cond_fr = ""
        for th, sc, cond in freq_levels:
            if n >= th:
                s1_fr, cond_fr = sc, cond; break

        # 发布时段
        period_score, period_desc, golden_count = self._get_publish_period_detail()
        s2_pp = period_score

        # 账号完整度
        if sig.strip() and len(sig.strip()) > 5:
            s3_sig, sig_desc = 4, "\u7b80\u4ecb\u975e\u7a7a\u4e14>5\u5b57"
        elif sig.strip():
            s3_sig, sig_desc = 2, "\u7b80\u4ecb\u975e\u7a7a\u4f46\u22645\u5b57"
        else:
            s3_sig, sig_desc = 0, "\u7b80\u4ecb\u4e3a\u7a7a"

        aweme_levels = [
            (300, 4, "\u2265300"), (100, 3, "100-300"),
            (30, 2, "30-100"), (10, 1, "10-30"), (0, 0, "<10"),
        ]
        s4_aw = 0; cond_aw = ""
        for th, sc, cond in aweme_levels:
            if aweme_count >= th:
                s4_aw, cond_aw = sc, cond; break
        op_sub = s1_fr + s2_pp + s3_sig + s4_aw

        # ---- 维度四：平台指数(10分) ----
        if redfox_index is None:
            s1_rx, cond_rx = 0, "\u672a\u8fd4\u56de"
        else:
            redfox_levels = [
                (900, 10, "\u2265900"), (800, 8, "800-900"),
                (700, 6, "700-800"), (600, 4, "600-700"),
                (500, 2, "500-600"), (0, 0, "<500"),
            ]
            s1_rx = 0; cond_rx = ""
            for th, sc, cond in redfox_levels:
                if redfox_index >= th:
                    s1_rx, cond_rx = sc, cond; break
        platform_sub = s1_rx

        total = body_sub + content_sub + op_sub + platform_sub
        grade_icon, grade_name, grade_letter = self._get_grade(total)

        # 构建输出文本
        fmt = self._fmt
        lines = []
        lines.append(f"**维度一：账号体量（35分）**")
        lines.append(f"+ 粉丝数 {fmt(follower)}（{cond_f}）→ {s1_f}分")
        lines.append(f"+ 获赞总数 {fmt(favorited)}（{cond_fav}）→ {s2_fav}分")
        lines.append(f"+ 获赞/粉丝比 ≈ {ratio:.1f}（{cond_r}）→ {s3_r}分")
        if body_sub == 35:
            lines.append(f"+ **小计：{body_sub}分（满分）**")
        else:
            lines.append(f"+ **小计：{body_sub}分**")

        lines.append("")
        lines.append(f"**维度二：内容表现（35分）**")
        if n > 0:
            lines.append(f"+ {n}条作品：总点赞{fmt(total_digg)} / 总评论{fmt(total_comment)} / 总分享{fmt(total_share)}")
            lines.append(f"+ 平均点赞 ≈ {fmt(int(avg_digg))}（{cond_d}）→ {s1_d}分")
            lines.append(f"+ 平均评论 ≈ {fmt(int(avg_comment))}（{cond_c}）→ {s2_c}分")
            lines.append(f"+ 平均分享 ≈ {fmt(int(avg_share))}（{cond_s}）→ {s3_s}分")
            lines.append(f"+ 传播系数 ≈ {spread_coeff:.1f}%（{cond_sp}）→ {s4_sp}分")
        else:
            lines.append("+ 近7天无作品数据")
        lines.append(f"+ **小计：{content_sub}分**")

        lines.append("")
        lines.append(f"**维度三：运营活跃度（20分）**")
        lines.append(f"+ 更新频率 {n}条（{cond_fr}）→ {s1_fr}分")
        lines.append(f"+ 发布时段 {golden_count}/{n}条为黄金时段 → {s2_pp}分")
        lines.append(f"+ 账号完整度 {sig_desc} → {s3_sig}分")
        lines.append(f"+ 作品总量 {fmt(aweme_count)}（{cond_aw}）→ {s4_aw}分")
        if op_sub == 20:
            lines.append(f"+ **小计：{op_sub}分（满分）**")
        else:
            lines.append(f"+ **小计：{op_sub}分**")

        lines.append("")
        lines.append(f"**维度四：平台指数（10分）**")
        if redfox_index is not None:
            lines.append(f"+ 红狐指数 {redfox_index:.1f}（{cond_rx}）→ {s1_rx}分")
        else:
            lines.append(f"+ 红狐指数 未返回 → 0分")
        if platform_sub == 10:
            lines.append(f"+ **小计：{platform_sub}分（满分）**")
        else:
            lines.append(f"+ **小计：{platform_sub}分**")

        lines.append("")
        lines.append(f"**综合评分：{total:.1f}分 — {grade_icon} {grade_letter} {grade_name}**")

        return "\n".join(lines) + "\n"

    def _get_publish_period_detail(self):
        """获取发布时段评分详情
        Returns: (score, desc, golden_count)"""
        if not self.works:
            return 0, "\u65e0\u4f5c\u54c1\u53ef\u5224\u65ad", 0
        hours = []
        for w in self.works:
            ct = w.get("createTime", "")
            if ct:
                try:
                    hour = int(ct.split(" ")[1].split(":")[0])
                    hours.append(hour)
                except (IndexError, ValueError):
                    pass
        if not hours:
            return 0, "\u65e0\u4f5c\u54c1\u53ef\u5224\u65ad", 0
        n = len(hours)
        golden = sum(1 for h in hours if (11 <= h <= 13) or (18 <= h <= 21))
        suboptimal = sum(1 for h in hours if (7 <= h <= 9) or (21 <= h <= 23))
        if golden >= n / 2:
            return 4, "\u9ec4\u91d1\u65f6\u6bb5(11-13/18-21)", golden
        elif golden + suboptimal >= n / 2:
            return 3, "\u6b21\u4f18\u65f6\u6bb5(7-9/21-23)", golden
        else:
            return 1, "\u5176\u4ed6\u65f6\u6bb5", golden

    # ==================== 章节0b：数据说明 ====================

    def _section_data_disclaimer(self) -> str:
        nickname = self.data.get("nickname", "未知")
        return f"> 以下诊断结果是基于{nickname}上周在抖音平台发布的作品进行分析得出。\n\n"

    # ==================== 章节1：基本信息 ====================

    def _section_basic_info(self) -> str:
        nickname = self.data.get("nickname", "未知")
        account_id = self.data.get("accountId", "-")
        country = self.data.get("country", "")
        province = self.data.get("province", "")
        city = self.data.get("city", "")
        location_parts = [p for p in [country, province, city] if p]
        location = "·".join(location_parts) if location_parts else "-"
        follower_count = format_number(self.data.get("followerCount", 0))
        total_favorited = format_number(self.data.get("totalFavorited", 0))
        aweme_count = self.data.get("awemeCount", 0)
        redfox_index = self.data.get("redfoxIndex")
        redfox_display = f"{redfox_index:.1f}" if redfox_index is not None else "-"
        crawl_time = self.data.get("crawlTime", "-")
        signature = self.data.get("signature", "")
        sig_display = signature if signature and signature.strip() else "未设置"

        c = self._C
        return f"""## 📋 {nickname} - 抖音账号诊断报告

### 基本信息

| 昵称 | 抖音号 | 地域 | 粉丝数 | 获赞 | 作品数 | 红狐指数 | 数据时间 |
|------|--------|------|--------|------|--------|---------|----------|
| {nickname} | {account_id} | {location} | {follower_count} | {total_favorited} | {aweme_count} | {redfox_display} | {crawl_time} |

**简介{c}** {sig_display}

---"""

    # ==================== 章节2：核心数据 ====================

    def _section_core_data(self) -> str:
        follower_count = self.data.get("followerCount", 0)
        total_favorited = self.data.get("totalFavorited", 0)
        ratio = (total_favorited / follower_count) if follower_count > 0 else 0

        # 账号体量数据
        c = self._C
        body = (
            f"### \U0001f4ca \u6838\u5fc3\u6570\u636e\n\n"
            f"**\u8d26\u53f7\u4f53\u91cf{c}**\n"
            f"- \u7c89\u4e1d\u6570 {format_number(follower_count)} | \u83b7\u8d5e {format_number(total_favorited)} | \u83b7\u8d5e/\u7c89\u4e1d\u6bd4 {ratio:.1f}\n\n"
            f"**\u8fd17\u5929\u4f5c\u54c1({len(self.works)}\u6761){c}**"
        )
        if not self.works:
            body += "> 近7天无作品数据\n"
        else:
            # 作品表格
            header = "| # | 发布时间 | 标题 | 点赞 | 评论 | 分享 | 互动 | 传播系数 |"
            sep = "|---|---------|------|------|------|------|------|---------|"
            rows = []
            for i, w in enumerate(self.works, 1):
                title = (w.get("title") or w.get("desc") or "\u65e0\u6807\u9898")[:20]
                create_time = w.get("createTime", "-")
                if create_time and len(create_time) > 16:
                    create_time = create_time[:16]
                digg = format_number(w.get("diggCount", 0))
                comment = format_number(w.get("commentCount", 0))
                share = format_number(w.get("shareCount", 0))
                interactive = format_number(w.get("interactiveCount", 0))
                digg_count = w.get("diggCount", 0) or 0
                share_count = w.get("shareCount", 0) or 0
                spread = f"{share_count / digg_count * 100:.1f}%" if digg_count > 0 else "-"
                # \u524d3\u540d\u7528\u5956\u724c emoji\uff0c\u5176\u4f59\u7528\u6570\u5b57
                medal = {1: "\U0001f947", 2: "\U0001f948", 3: "\U0001f949"}
                rank_display = medal.get(i, str(i))
                rows.append(f"| {rank_display} | {create_time} | {title} | {digg} | {comment} | {share} | {interactive} | {spread} |")

            body += header + "\n" + sep + "\n" + "\n".join(rows) + "\n"

            # playCount非null时追加说明
            has_play = any(w.get("playCount") is not None for w in self.works)
            if has_play:
                body += '\n> playCount有值时,可追加"播放量"和"点赞率"列'

        return body + "\n---"

    # ==================== 章节3：综合评分 ====================

    def _section_comprehensive_score(self) -> str:
        # 计算四维度得分
        body_score, _ = self._score_body()
        content_score, _ = self._score_content()
        operation_score, _ = self._score_operation()
        platform_score, _ = self._score_platform()
        total = body_score + content_score + operation_score + platform_score

        # 评级
        grade_icon, grade_name, grade_letter = self._get_grade(total)

        # 得分率
        body_rate = f"{body_score / 35 * 100:.1f}%"
        content_rate = f"{content_score / 35 * 100:.1f}%"
        op_rate = f"{operation_score / 20 * 100:.1f}%"
        platform_rate = f"{platform_score / 10 * 100:.1f}%" if platform_score > 0 else "0.0%"
        total_rate = f"{total:.1f}%"

        c = self._C

        # 优势/短板（列表格式）
        advantages = self._get_advantages(body_score, content_score, operation_score, platform_score)
        weaknesses = self._get_weaknesses(body_score, content_score, operation_score, platform_score)
        adv_lines = "\n".join(f"+ {a}" for a in advantages)
        weak_lines = "\n".join(f"+ {w}" for w in weaknesses)

        return f"""### 🏆 综合评分

**总分{c}{total:.1f} / 100分** — {grade_icon} {grade_name} {grade_letter}

| 维度 | 得分 | 满分 | 得分率 |
|------|------|------|--------|
| 账号体量 | {body_score:.1f} | 35分 | {body_rate} |
| 内容表现 | {content_score:.1f} | 35分 | {content_rate} |
| 运营活跃度 | {operation_score:.1f} | 20分 | {op_rate} |
| 平台指数 | {platform_score:.1f} | 10分 | {platform_rate} |
| **综合** | **{total:.1f}** | **100分** | **{total_rate}** |

**💪 优势{c}**

{adv_lines}

**⚠️ 短板{c}**

{weak_lines}

---"""

    # ==================== 章节4：优化建议 ====================

    def _section_optimization(self) -> str:
        suggestions = self._generate_suggestions()
        items = []
        for i, (problem, advice) in enumerate(suggestions[:3], 1):
            items.append(f"{i}. **{problem}** → {advice}")
        return "### 💡 优化建议\n\n" + "\n".join(items) + "\n\n---"

    # ==================== 页脚 ====================

    def _section_footer(self) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        crawl_time = self.data.get("crawlTime", "-")
        return f"\n*诊断时间:{today} | 数据来源:红狐API `/story/api/dyUser/query` | 数据更新:{crawl_time}*"

    # ==================== 维度一：账号体量(40分) ====================

    def _score_body(self):
        """账号体量 = 粉丝数(22) + 获赞总数(8) + 获赞/粉丝比(5)
        Returns: (score, details_list)"""
        follower = self.data.get("followerCount", 0) or 0
        favorited = self.data.get("totalFavorited", 0) or 0
        ratio = favorited / follower if follower > 0 else 0
        details = []

        # 粉丝数(22分)
        follower_levels = [
            (50000000, 22, "超头部"), (10000000, 19, "头部"),
            (5000000, 16, "准头部"), (1000000, 12, "中腰部"),
            (500000, 9, "中小"), (100000, 5, "小型"),
            (10000, 2, "微型"), (0, 0, "新号"),
        ]
        s1, level = 0, ""
        for threshold, score, label in follower_levels:
            if follower >= threshold:
                s1, level = score, label
                break
        details.append(f"粉丝数 {format_number(follower)} → {s1}/22分({level})")

        # 获赞总数(8分)
        favorited_levels = [
            (1000000000, 8), (100000000, 6), (10000000, 5),
            (1000000, 3), (100000, 1), (0, 0),
        ]
        s2 = 0
        for threshold, score in favorited_levels:
            if favorited >= threshold:
                s2 = score
                break
        details.append(f"获赞总数 {format_number(favorited)} → {s2}/8分")

        # 获赞/粉丝比(5分)
        ratio_levels = [
            (15, 5, "粉丝质量极高"), (10, 4, "粉丝质量高"),
            (5, 3, "正常"), (2, 2, "偏低"), (0, 1, "极低"),
        ]
        s3, ratio_desc = 0, ""
        for threshold, score, desc in ratio_levels:
            if ratio >= threshold:
                s3, ratio_desc = score, desc
                break
        details.append(f"获赞/粉丝比 {ratio:.1f} → {s3}/5分({ratio_desc})")

        return s1 + s2 + s3, details

    # ==================== 维度二：内容表现(40分) ====================

    def _score_content(self):
        """内容表现 = 平均点赞(13) + 平均评论(9) + 平均分享(7) + 传播系数(6)
        若近7天无作品,得0分
        Returns: (score, details_list)"""
        if not self.works:
            return 0, ["近7天无作品,内容表现得0分"]

        n = len(self.works)
        total_digg = sum(w.get("diggCount", 0) or 0 for w in self.works)
        total_comment = sum(w.get("commentCount", 0) or 0 for w in self.works)
        total_share = sum(w.get("shareCount", 0) or 0 for w in self.works)

        avg_digg = total_digg / n
        avg_comment = total_comment / n
        avg_share = total_share / n
        spread_coeff = (total_share / total_digg * 100) if total_digg > 0 else 0
        details = []

        # 平均点赞数(13分)
        digg_levels = [
            (1000000, 13, "现象级"), (500000, 11, "超爆款"),
            (100000, 9, "爆款"), (10000, 7, "优秀"),
            (1000, 4, "中等"), (100, 2, "偏低"), (0, 0, "较低"),
        ]
        s1, digg_label = 0, ""
        for threshold, score, label in digg_levels:
            if avg_digg >= threshold:
                s1, digg_label = score, label
                break
        details.append(f"平均点赞数 {format_number(int(avg_digg))} → {s1}/13分({digg_label})")

        # 平均评论数(9分)
        comment_levels = [
            (10000, 9), (5000, 7), (1000, 5), (100, 3), (10, 1), (0, 0),
        ]
        s2 = 0
        for threshold, score in comment_levels:
            if avg_comment >= threshold:
                s2 = score
                break
        details.append(f"平均评论数 {format_number(int(avg_comment))} → {s2}/9分")

        # 平均分享数(7分)
        share_levels = [
            (100000, 7), (10000, 6), (1000, 4), (100, 2), (10, 1), (0, 0),
        ]
        s3 = 0
        for threshold, score in share_levels:
            if avg_share >= threshold:
                s3 = score
                break
        details.append(f"平均分享数 {format_number(int(avg_share))} → {s3}/7分")

        # 传播系数(6分)
        spread_levels = [
            (15, 6, "极强自发传播"), (10, 5, "强传播力"),
            (5, 4, "良好"), (2, 2, "中等"), (0, 1, "偏弱"),
        ]
        s4, spread_desc = 0, ""
        for threshold, score, desc in spread_levels:
            if spread_coeff >= threshold:
                s4, spread_desc = score, desc
                break
        details.append(f"传播系数 {spread_coeff:.1f}% → {s4}/6分({spread_desc})")

        return s1 + s2 + s3 + s4, details

    # ==================== 维度三：运营活跃度(20分) ====================

    def _score_operation(self):
        """运营活跃度 = 更新频率(8) + 发布时段(4) + 账号完整度(4) + 作品总量(4)
        Returns: (score, details_list)"""
        details = []

        # 更新频率(8分)
        work_count = len(self.works)
        freq_levels = [
            (7, 8, "日更"), (4, 6, "高频"),
            (2, 4, "中频"), (1, 2, "低频"), (0, 0, "停更"),
        ]
        s1, freq_desc = 0, ""
        for threshold, score, desc in freq_levels:
            if work_count >= threshold:
                s1, freq_desc = score, desc
                break
        details.append(f"更新频率 {work_count}条/7天 → {s1}/8分({freq_desc})")

        # 发布时段(4分)
        s2, period_desc = self._score_publish_period()
        details.append(f"发布时段 {period_desc} → {s2}/4分")

        # 账号完整度(4分)
        sig = self.data.get("signature", "") or ""
        if sig.strip() and len(sig.strip()) > 5:
            s3, comp_desc = 4, "简介完整(>5字)"
        elif sig.strip():
            s3, comp_desc = 2, "简介较短(<=5字)"
        else:
            s3, comp_desc = 0, "无简介"
        details.append(f"账号完整度 {comp_desc} → {s3}/4分")

        # 作品总量(4分)
        aweme_count = self.data.get("awemeCount", 0) or 0
        aweme_levels = [
            (300, 4), (100, 3), (30, 2), (10, 1), (0, 0),
        ]
        s4 = 0
        for threshold, score in aweme_levels:
            if aweme_count >= threshold:
                s4 = score
                break
        details.append(f"作品总量 {aweme_count} → {s4}/4分")

        return s1 + s2 + s3 + s4, details

    def _score_publish_period(self):
        """发布时段评分:黄金时段11-13/18-21得4分,次优7-9/21-23得3分
        Returns: (score, period_desc)"""
        if not self.works:
            return 0, "无作品可判断"
        hours = []
        for w in self.works:
            ct = w.get("createTime", "")
            if ct:
                try:
                    hour = int(ct.split(" ")[1].split(":")[0])
                    hours.append(hour)
                except (IndexError, ValueError):
                    pass
        if not hours:
            return 0, "无作品可判断"
        # 取多数时段
        golden = sum(1 for h in hours if (11 <= h <= 13) or (18 <= h <= 21))
        suboptimal = sum(1 for h in hours if (7 <= h <= 9) or (21 <= h <= 23))
        if golden >= len(hours) / 2:
            return 4, "黄金时段(11-13/18-21)"
        elif golden + suboptimal >= len(hours) / 2:
            return 3, "次优时段(7-9/21-23)"
        else:
            return 1, "其他时段"

    # ==================== 维度四：平台指数(10分) ====================

    def _score_platform(self):
        """平台指数 = 红狐指数(10)
        若API未返回redfoxIndex(值为null),得0分
        Returns: (score, details_list)"""
        redfox_index = self.data.get("redfoxIndex")
        if redfox_index is None:
            return 0, ["红狐指数 API未返回 → 0/10分"]

        # 红狐指数(10分)
        redfox_levels = [
            (900, 10, "顶级影响力"), (800, 8, "头部影响力"),
            (700, 6, "中上影响力"), (600, 4, "中等影响力"),
            (500, 2, "初级影响力"), (0, 0, "待提升"),
        ]
        s1, level = 0, ""
        for threshold, score, label in redfox_levels:
            if redfox_index >= threshold:
                s1, level = score, label
                break
        return s1, [f"红狐指数 {redfox_index:.1f} → {s1}/10分({level})"]

    # ==================== 辅助方法 ====================

    def _get_grade(self, score: float) -> tuple:
        """评级:S/A/B/C/D/E"""
        if score >= 90:
            return ("🏆", "标杆账号", "S级")
        elif score >= 80:
            return ("⭐", "优质账号", "A级")
        elif score >= 70:
            return ("✅", "健康账号", "B级")
        elif score >= 60:
            return ("📊", "中等账号", "C级")
        elif score >= 50:
            return ("⚠️", "亚健康", "D级")
        else:
            return ("❌", "问题账号", "E级")

    def _get_advantages(self, body: float, content: float, operation: float, platform: float) -> list:
        """获取1-2个核心优势"""
        items = []
        if body >= 28:
            items.append("账号体量雄厚")
        elif body >= 18:
            items.append("粉丝基础扎实")
        if content >= 28:
            items.append("内容数据突出")
        elif content >= 18:
            items.append("内容表现良好")
        if operation >= 16:
            items.append("运营节奏健康")
        if platform >= 8:
            items.append("平台指数优秀")
        elif platform >= 4:
            items.append("平台影响力良好")
        if not items:
            items.append("有基础运营框架")
        return items[:2]

    def _get_weaknesses(self, body: float, content: float, operation: float, platform: float) -> list:
        """获取1-2个核心短板"""
        items = []
        if body < 12:
            items.append("账号体量偏小")
        if content < 10:
            items.append("近期内容表现较弱")
        elif content == 0:
            items.append("近7天无作品数据")
        if operation < 8:
            items.append("运营活跃度不足")
        if platform == 0:
            items.append("无平台指数数据")
        if not items:
            items.append("整体表现均衡,持续优化即可")
        return items[:2]

    def _generate_suggestions(self) -> List[tuple]:
        """基于评分数据生成3条优化建议"""
        suggestions = []
        body, _ = self._score_body()
        content, _ = self._score_content()
        operation, _ = self._score_operation()
        platform, _ = self._score_platform()

        # 按短板优先排序
        if content == 0:
            suggestions.append(("近7天无作品更新", "恢复稳定发布节奏,建议至少周更2-3条"))
        elif content < 12:
            suggestions.append(("内容互动数据偏低", "优化视频前3秒吸引力,增加互动引导话术"))

        if body < 12:
            suggestions.append(("粉丝基数偏小", "通过热点内容+Dou+投放加速涨粉,聚焦垂直领域深耕"))
        elif body < 22:
            suggestions.append(("账号体量有提升空间", "持续产出爆款内容扩大影响力,探索跨平台引流"))

        if operation < 10:
            suggestions.append(("运营活跃度不足", "制定内容排期表保持日更或高频更新,完善账号简介"))
        elif operation < 16:
            suggestions.append(("运营节奏可优化", "聚焦黄金时段(11-13点/18-21点)发布,提升内容曝光概率"))

        if platform == 0:
            suggestions.append(("平台指数数据缺失", "持续稳定运营以积累平台指数,提升内容质量与互动率"))
        elif platform < 4:
            suggestions.append(("平台指数偏低", "提升内容质量与互动率,保持稳定更新以提升红狐指数"))

        # 至少3条
        if len(suggestions) < 3:
            suggestions.append(("持续优化方向", "深耕垂直内容建立差异化标签,开启直播增强粉丝粘性"))

        return suggestions[:3]


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 模拟范丞丞的API返回数据
    sample_data = {
        "nickname": "范丞丞",
        "avatarUrl": "https://example.com/avatar.jpg",
        "accountId": "CCHardErThAnEVER",
        "uid": "84676974127",
        "signature": "",
        "gender": "未知",
        "age": 25,
        "country": "中国",
        "province": "浙江",
        "city": "金华",
        "ipLocation": "浙江",
        "followerCount": 20366567,
        "awemeCount": 236,
        "totalFavorited": 390844290,
        "crawlTime": "2026-06-02 01:57:18",
        "redfoxIndex": 780.5,
        "works": [
            {
                "awemeId": "7481xxx1",
                "title": "新作品来了",
                "coverUrl": "https://example.com/cover1.jpg",
                "desc": "",
                "createTime": "2026-05-28 19:30:00",
                "diggCount": 2165213,
                "commentCount": 38286,
                "shareCount": 260216,
                "playCount": None,
                "interactiveCount": 2443715,
                "workUrl": "https://www.douyin.com/video/7481xxx1"
            },
            {
                "awemeId": "7481xxx2",
                "title": "日常分享",
                "coverUrl": "https://example.com/cover2.jpg",
                "desc": "",
                "createTime": "2026-05-26 12:15:00",
                "diggCount": 1222713,
                "commentCount": 33662,
                "shareCount": 87111,
                "playCount": None,
                "interactiveCount": 1343486,
                "workUrl": "https://www.douyin.com/video/7481xxx2"
            }
        ],
        "similarAccounts": []
    }

    generator = DouyinDiagnosisReportV3(sample_data)
    report = generator.generate_report()
    print(report)

    with open("douyin_diagnosis_report_v3.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n✅ 报告已保存到 douyin_diagnosis_report_v3.md")
