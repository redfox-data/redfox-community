#!/usr/bin/env python3
"""
GEO 分析逻辑库 — 确定性分析（脚本完成）+ AI 分析模板生成

确定性分析（无需 AI）:
  - detect_mention(text, keywords) -> bool, count
  - extract_domains(sources) -> list[str]
  - aggregate_domains(results) -> dict[str, int]
  - compute_mention_rate(results, keywords, platform) -> float
  - compute_mention_matrix(results, queries, platforms, keywords) -> list[list[dict]]

AI 分析模板:
  - build_ai_analysis_template(results, brand, competitors) -> list[dict]
  - build_analysis_prompt(answer, brand, competitors) -> str
"""


# ── 确定性分析 ─────────────────────────────────────────────


def detect_mention(text, keywords):
    """检测关键词是否在文本中出现

    Args:
        text: 待检测文本
        keywords: 关键词列表（品牌名 + 别名）

    Returns:
        (mentioned: bool, count: int)
    """
    if not text:
        return False, 0
    text_lower = text.lower()
    count = 0
    for kw in keywords:
        if not kw:
            continue
        # 大小写不敏感匹配
        count += text_lower.count(kw.lower())
    return count > 0, count


def detect_all_mentions(text, brand_keywords, competitor_map):
    """检测品牌和所有竞品的提及情况

    Args:
        text: 待检测文本
        brand_keywords: 品牌关键词列表
        competitor_map: {竞品名: [关键词列表]}

    Returns:
        {
            "brand_mentioned": bool,
            "brand_mention_count": int,
            "competitor_mentions": {竞品名: int}
        }
    """
    brand_mentioned, brand_count = detect_mention(text, brand_keywords)

    competitor_mentions = {}
    for comp_name, comp_keywords in competitor_map.items():
        _, count = detect_mention(text, comp_keywords)
        competitor_mentions[comp_name] = count

    return {
        "brand_mentioned": brand_mentioned,
        "brand_mention_count": brand_count,
        "competitor_mentions": competitor_mentions,
    }


def extract_domains_from_sources(sources):
    """从引用来源列表中提取域名列表

    Args:
        sources: list[dict]，每项含 {"title", "url", "domain"}

    Returns:
        list[str]: 域名列表
    """
    domains = []
    for s in sources:
        domain = s.get("domain", "")
        if domain:
            domains.append(domain)
    return domains


def aggregate_domains(results, platform=None):
    """聚合统计引用域名频次

    Args:
        results: 搜索结果列表
        platform: 可选，限定平台

    Returns:
        dict[str, int]: {域名: 出现次数}，按频次降序
    """
    domain_count = {}
    for r in results:
        if platform and r.get("platform") != platform:
            continue
        if r.get("status") != "completed":
            continue
        for domain in extract_domains_from_sources(r.get("sources", [])):
            domain_count[domain] = domain_count.get(domain, 0) + 1

    return dict(sorted(domain_count.items(), key=lambda x: -x[1]))


def compute_mention_rate(results, keywords, platform=None):
    """计算提及率

    Args:
        results: 搜索结果列表
        keywords: 关键词列表
        platform: 可选，限定平台

    Returns:
        float: 0.0 ~ 1.0
    """
    total = 0
    mentioned = 0
    for r in results:
        if platform and r.get("platform") != platform:
            continue
        if r.get("status") != "completed":
            continue
        total += 1
        is_mentioned, _ = detect_mention(r.get("content", ""), keywords)
        if is_mentioned:
            mentioned += 1

    return mentioned / total if total > 0 else 0.0


def build_mention_matrix(results, queries, platforms, brand_keywords):
    """构建品牌提及矩阵

    Returns:
        list[list[dict]]: 矩阵 [问题数 x 平台数]
        每个单元格: {"mentioned": bool, "mention_count": int, "platform": str, "question": str}
    """
    matrix = []
    for qi, query in enumerate(queries):
        row = []
        for platform in platforms:
            # 找到对应的结果
            cell = {"mentioned": False, "mention_count": 0, "platform": platform, "question": query}
            for r in results:
                if (
                    r.get("query_index") == qi
                    and r.get("platform") == platform
                    and r.get("status") == "completed"
                ):
                    is_mentioned, count = detect_mention(r.get("content", ""), brand_keywords)
                    cell["mentioned"] = is_mentioned
                    cell["mention_count"] = count
                    break
            row.append(cell)
        matrix.append(row)
    return matrix


def compute_per_answer_analysis(results, brand_keywords, competitor_map):
    """对每份回答执行确定性分析

    Returns:
        list[dict]: 每份回答的分析结果
    """
    per_answer = []
    for r in results:
        if r.get("status") != "completed":
            per_answer.append({
                "question": r.get("question", ""),
                "query_index": r.get("query_index", 0),
                "platform": r.get("platform", ""),
                "status": r.get("status", "unknown"),
                "brand_mentioned": False,
                "brand_mention_count": 0,
                "competitor_mentions": {},
                "source_domains": [],
            })
            continue

        mentions = detect_all_mentions(
            r.get("content", ""), brand_keywords, competitor_map
        )
        domains = extract_domains_from_sources(r.get("sources", []))

        per_answer.append({
            "question": r.get("question", ""),
            "query_index": r.get("query_index", 0),
            "platform": r.get("platform", ""),
            "status": "completed",
            "brand_mentioned": mentions["brand_mentioned"],
            "brand_mention_count": mentions["brand_mention_count"],
            "competitor_mentions": mentions["competitor_mentions"],
            "source_domains": domains,
        })

    return per_answer


def compute_aggregate_metrics(per_answer, queries, platforms, brand, competitors):
    """计算聚合指标

    Returns:
        dict: 聚合指标
    """
    # 品牌提及率（分平台 + 跨平台）
    brand_mention_rate = {"overall": 0.0}
    for p in platforms:
        brand_mention_rate[p] = 0.0

    total_completed = 0
    total_mentioned = 0
    platform_stats = {p: {"total": 0, "mentioned": 0} for p in platforms}

    for ans in per_answer:
        if ans.get("status") != "completed":
            continue
        p = ans.get("platform", "")
        total_completed += 1
        platform_stats.setdefault(p, {"total": 0, "mentioned": 0})
        platform_stats[p]["total"] += 1
        if ans.get("brand_mentioned"):
            total_mentioned += 1
            platform_stats[p]["mentioned"] += 1

    brand_mention_rate["overall"] = total_mentioned / total_completed if total_completed > 0 else 0.0
    for p in platforms:
        stats = platform_stats.get(p, {"total": 0, "mentioned": 0})
        brand_mention_rate[p] = stats["mentioned"] / stats["total"] if stats["total"] > 0 else 0.0

    # 竞品提及率
    competitor_mention_rates = {}
    for comp in competitors:
        rates = {"overall": 0.0}
        for p in platforms:
            rates[p] = 0.0

        comp_total = 0
        comp_mentioned = 0
        comp_platform_stats = {p: {"total": 0, "mentioned": 0} for p in platforms}

        for ans in per_answer:
            if ans.get("status") != "completed":
                continue
            p = ans.get("platform", "")
            comp_total += 1
            comp_platform_stats.setdefault(p, {"total": 0, "mentioned": 0})
            comp_platform_stats[p]["total"] += 1
            comp_count = ans.get("competitor_mentions", {}).get(comp, 0)
            if comp_count > 0:
                comp_mentioned += 1
                comp_platform_stats[p]["mentioned"] += 1

        rates["overall"] = comp_mentioned / comp_total if comp_total > 0 else 0.0
        for p in platforms:
            stats = comp_platform_stats.get(p, {"total": 0, "mentioned": 0})
            rates[p] = stats["mentioned"] / stats["total"] if stats["total"] > 0 else 0.0
        competitor_mention_rates[comp] = rates

    # 域名统计
    domain_stats = {}
    domain_stats_by_platform = {p: {} for p in platforms}

    for ans in per_answer:
        if ans.get("status") != "completed":
            continue
        p = ans.get("platform", "")
        for domain in ans.get("source_domains", []):
            domain_stats[domain] = domain_stats.get(domain, 0) + 1
            domain_stats_by_platform.setdefault(p, {})
            domain_stats_by_platform[p][domain] = domain_stats_by_platform[p].get(domain, 0) + 1

    # 排序域名统计
    domain_stats = dict(sorted(domain_stats.items(), key=lambda x: -x[1]))
    for p in platforms:
        domain_stats_by_platform[p] = dict(
            sorted(domain_stats_by_platform.get(p, {}).items(), key=lambda x: -x[1])
        )

    return {
        "brand_mention_rate": brand_mention_rate,
        "competitor_mention_rates": competitor_mention_rates,
        "domain_stats": domain_stats,
        "domain_stats_by_platform": domain_stats_by_platform,
        "total_completed": total_completed,
        "total_mentioned": total_mentioned,
    }


# ── AI 分析模板 ─────────────────────────────────────────────


AI_ANALYSIS_SCHEMA = {
    "brand_rank": None,        # 品牌在推荐列表中的排名（未提及则为 null）
    "brand_context": "",       # 品牌被提及时的上下文摘要
    "sentiment": "",           # positive / neutral / negative
    "sentiment_reason": "",    # 情绪判断依据
    "competitors_mentioned": [],  # AI 回答中提及的竞品列表
    "competitor_details": [],   # 竞品详情: [{"name": str, "rank": int|null, "sentiment": str}]
    "key_claims": [],          # 关于品牌的关键描述列表
}


def build_ai_analysis_template(results, brand, competitors):
    """生成 AI 分析模板 JSON

    Agent 读取此模板后，对每份回答执行 AI 分析并填充字段

    Returns:
        list[dict]: 每份回答的 AI 分析模板
    """
    template = []
    for r in results:
        if r.get("status") != "completed":
            continue
        entry = {
            "question": r.get("question", ""),
            "query_index": r.get("query_index", 0),
            "platform": r.get("platform", ""),
            "brand": brand,
            "competitors": competitors,
            **AI_ANALYSIS_SCHEMA,
        }
        template.append(entry)
    return template


def build_analysis_prompt(answer_content, brand, competitors):
    """构造单份回答的 AI 分析 prompt

    Agent 读取此 prompt 后，对 AI 回答内容执行分析并输出结构化 JSON
    """
    competitors_str = "、".join(competitors) if competitors else "无"

    prompt = f"""请分析以下 AI 搜索引擎的回答内容，提取关于品牌「{brand}」的 GEO 分析信息。

## 待分析品牌
- 品牌名: {brand}
- 已知竞品: {competitors_str}

## AI 搜索引擎回答内容
---
{answer_content}
---

## 分析要求
请输出一个 JSON 对象，包含以下字段：

1. **brand_rank**: 品牌在回答的推荐列表或排名中的位置（数字）。如果回答列举了多个品牌/产品，品牌排第几位？未提及则为 null。
2. **brand_context**: 品牌被提及时的一句话上下文摘要。未提及则为空字符串。
3. **sentiment**: 回答对该品牌的整体情绪倾向。可选值: "positive"（正面/推荐/优势）、"neutral"（中性/客观描述）、"negative"（负面/劣势/不推荐）。未提及则为 "neutral"。
4. **sentiment_reason**: 情绪判断的依据，引用回答中的原文或概括原因。
5. **competitors_mentioned**: 回答中提及的所有竞品品牌名称列表（不限于已知竞品，发现新竞品也列出）。
6. **competitor_details**: 对每个被提及的竞品，提供其排名和情绪信息。格式为列表，每项含: name（竞品名）、rank（在推荐列表中的排名，无排名则为 null）、sentiment（positive/neutral/negative）。
7. **key_claims**: 关于该品牌的关键描述或评价（2-3条简短摘要）。

## 输出格式
```json
{{
  "brand_rank": null,
  "brand_context": "",
  "sentiment": "neutral",
  "sentiment_reason": "",
  "competitors_mentioned": [],
  "competitor_details": [],
  "key_claims": []
}}
```

请确保输出是合法 JSON，不要包含注释或额外文本。"""

    return prompt


def merge_analysis(deterministic, ai_analysis):
    """合并确定性分析和 AI 分析结果

    Args:
        deterministic: 确定性分析结果列表 (per_answer)
        ai_analysis: AI 分析结果列表

    Returns:
        list[dict]: 合并后的完整分析结果
    """
    # 创建 AI 分析的查找索引
    ai_map = {}
    for ai in ai_analysis:
        key = (ai.get("query_index", 0), ai.get("platform", ""))
        ai_map[key] = ai

    merged = []
    for det in deterministic:
        key = (det.get("query_index", 0), det.get("platform", ""))
        ai = ai_map.get(key, {})

        merged.append({
            # 确定性字段
            "question": det.get("question", ""),
            "query_index": det.get("query_index", 0),
            "platform": det.get("platform", ""),
            "status": det.get("status", "unknown"),
            "brand_mentioned": det.get("brand_mentioned", False),
            "brand_mention_count": det.get("brand_mention_count", 0),
            "competitor_mentions": det.get("competitor_mentions", {}),
            "source_domains": det.get("source_domains", []),
            # AI 字段
            "brand_rank": ai.get("brand_rank"),
            "brand_context": ai.get("brand_context", ""),
            "sentiment": ai.get("sentiment", "neutral"),
            "sentiment_reason": ai.get("sentiment_reason", ""),
            "ai_competitors_mentioned": ai.get("competitors_mentioned", []),
            "competitor_details": ai.get("competitor_details", []),
            "key_claims": ai.get("key_claims", []),
        })

    return merged


def compute_sentiment_distribution(merged_results, platforms):
    """计算情绪分布（分平台 + 跨平台）

    Returns:
        dict: {
            "overall": {"positive": int, "neutral": int, "negative": int},
            "doubao": {...},
            ...
        }
    """
    distribution = {"overall": {"positive": 0, "neutral": 0, "negative": 0}}
    for p in platforms:
        distribution[p] = {"positive": 0, "neutral": 0, "negative": 0}

    for r in merged_results:
        if r.get("status") != "completed":
            continue
        sentiment = r.get("sentiment", "neutral")
        if sentiment not in ("positive", "neutral", "negative"):
            sentiment = "neutral"

        distribution["overall"][sentiment] += 1
        p = r.get("platform", "")
        if p in distribution:
            distribution[p][sentiment] += 1

    return distribution


def compute_brand_avg_rank(merged_results, platforms):
    """计算品牌平均排名（在被提及的回答中）

    Returns:
        dict: {"overall": float|null, "doubao": float|null, ...}
    """
    ranks = {"overall": []}
    for p in platforms:
        ranks[p] = []

    for r in merged_results:
        if r.get("status") != "completed":
            continue
        rank = r.get("brand_rank")
        if rank is not None and isinstance(rank, (int, float)) and rank > 0:
            ranks["overall"].append(rank)
            p = r.get("platform", "")
            if p in ranks:
                ranks[p].append(rank)

    result = {}
    for key, values in ranks.items():
        result[key] = sum(values) / len(values) if values else None

    return result


def compute_competitor_metrics(merged_results, platforms, all_competitors):
    """计算每个竞品的平均排名和情绪分布

    从 AI 分析的 competitor_details 字段中提取数据
    对于在 ai_competitors_mentioned 中被提及但无显式排名的竞品，
    根据其在列表中的位置推断隐式排名

    Returns:
        dict: {
            competitor_name: {
                "avg_rank": {"overall": float|null, "doubao": ..., ...},
                "sentiment": {"overall": {"positive": int, "neutral": int, "negative": int}, ...}
            }
        }
    """
    result = {}
    for comp in all_competitors:
        ranks = {"overall": []}
        sentiment = {"overall": {"positive": 0, "neutral": 0, "negative": 0}}
        for p in platforms:
            ranks[p] = []
            sentiment[p] = {"positive": 0, "neutral": 0, "negative": 0}

        for r in merged_results:
            if r.get("status") != "completed":
                continue
            p = r.get("platform", "")
            details = r.get("competitor_details", [])
            ai_mentioned = r.get("ai_competitors_mentioned", [])

            # 先处理有显式排名的竞品
            matched_in_details = False
            got_rank = False
            for d in details:
                if not isinstance(d, dict):
                    continue
                d_name = d.get("name", "")
                if comp.lower() not in d_name.lower() and d_name.lower() not in comp.lower():
                    continue
                matched_in_details = True
                d_rank = d.get("rank")
                if d_rank is not None and isinstance(d_rank, (int, float)) and d_rank > 0:
                    ranks["overall"].append(d_rank)
                    if p in ranks:
                        ranks[p].append(d_rank)
                    got_rank = True

                d_sent = d.get("sentiment", "neutral")
                if d_sent not in ("positive", "neutral", "negative"):
                    d_sent = "neutral"
                sentiment["overall"][d_sent] += 1
                if p in sentiment:
                    sentiment[p][d_sent] += 1

            # 如果在 competitor_details 中未找到或未获取排名，从 ai_competitors_mentioned 推断
            if not got_rank:
                comp_lower = comp.lower()
                for idx, ai_name in enumerate(ai_mentioned):
                    if not isinstance(ai_name, str):
                        continue
                    if comp_lower == ai_name.lower() or comp_lower in ai_name.lower() or ai_name.lower() in comp_lower:
                        # 隐式排名: 在列表中的位置 + 1
                        implicit_rank = idx + 1
                        ranks["overall"].append(implicit_rank)
                        if p in ranks:
                            ranks[p].append(implicit_rank)
                        # 如果在details中未匹配到情感，默认中性
                        if not matched_in_details:
                            sentiment["overall"]["neutral"] += 1
                            if p in sentiment:
                                sentiment[p]["neutral"] += 1
                        break

        avg_rank = {}
        for key, values in ranks.items():
            avg_rank[key] = sum(values) / len(values) if values else None

        result[comp] = {
            "avg_rank": avg_rank,
            "sentiment": sentiment,
        }

    return result


def compute_geo_score(mention_rate, avg_rank, sentiment_dist, max_rank=10):
    """计算 GEO 综合得分 (0-100)

    加权: 提及率 40% + 排名 30% + 情绪 30%
    """
    # 提及率得分 (0-100)
    mention_score = mention_rate * 100

    # 排名得分 (0-100)，排名越靠前分越高
    if avg_rank is not None and avg_rank > 0:
        rank_score = max(0, 100 - (avg_rank - 1) * 100 / max_rank)
    else:
        rank_score = 0

    # 情绪得分 (0-100)
    total = sum(sentiment_dist.values())
    if total > 0:
        positive_ratio = sentiment_dist.get("positive", 0) / total
        negative_ratio = sentiment_dist.get("negative", 0) / total
        sentiment_score = positive_ratio * 100 - negative_ratio * 50
        sentiment_score = max(0, min(100, sentiment_score))
    else:
        sentiment_score = 50

    # 加权综合
    geo_score = mention_score * 0.4 + rank_score * 0.3 + sentiment_score * 0.3
    return round(geo_score, 1)
