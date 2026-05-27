# WeChat Hot Article Search / wechat-search

## Introduction

A WeChat Official Account hot article search tool — quickly find articles with 5,000+ reads, get creative inspiration, and stay on top of content trends.

**Core Value**

Based on continuously indexed WeChat articles with 5,000+ reads from the past 30 days across the web, updated daily with yesterday's data. Weighted scoring by relevance, heat, and timeliness aggregates viral articles across all domains. Quickly find quality benchmarks in any industry and reference peer hot content ideas — no more hunting for materials across the web, a one-stop solution for daily writing reference.

**Who It's For**

- 🎯 Content creators — Find topic inspiration and break down viral article structure
- 📦 WeChat operators — Track industry trends and shape content strategy
- 🏢 Brands / business teams — Monitor industry KOL dynamics and evaluate content marketing direction
- 📚 Self-media learners — Learn viral patterns and improve writing skills

## Features

### Core Capabilities

- **Keyword search**: Query viral WeChat articles related to any keyword
- **Site-wide hot recommendations**: View recent hottest articles across WeChat without keywords
- **Smart score ranking**: Weighted by relevance (10 pts), heat (3 pts), and timeliness (2 pts) — max 15 pts total
- **Query expansion**: Related sub-topic recommendations in search results to broaden topic ideas
- **Subscription push**: Subscribe to daily scheduled pushes for keyword queries

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?souce=github) to obtain your `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` as a device environment variable before using this skill.
- Before providing your key, confirm its source, available scope, validity period, and whether reset/revocation is supported.
- Do not hard-code or expose the key in plaintext in code, prompts, logs, or output files.

---

## Usage Guide

### Quick phrase reference

| Intent                | Example phrase                                              | What you get                            |
| --------------------- | ----------------------------------------------------------- | --------------------------------------- |
| Search viral articles | "Find workplace-related viral articles for me"              | Recent hot articles in workplace niche  |
| Niche sub-topic       | "Search for AI startup articles"                            | Precisely matched sub-keyword articles  |
| Multi-niche query     | "Find viral articles in workplace, emotions, and parenting" | Hot articles from three niches at once  |
| Site-wide hot         | "What are the hottest site-wide articles lately?"           | Recent hottest articles across the site |
| View all              | "Show all 50 entries"                                       | Full query results                      |
| Subscribe             | "Subscribe to workplace articles, push daily at 9 AM"       | Create daily scheduled push task        |

### Sample output

📅 **Query time range**: May 14 – May 21

💡 **Found 12 related articles; showing first 10. View all?**

| Title                                                                                      | Author           | Reads | Published  | Relevance | Heat | Timeliness | **Total** |
| ------------------------------------------------------------------------------------------ | ---------------- | ----- | ---------- | --------- | ---- | ---------- | --------- |
| [Must-read for workplace newcomers: 5 tips to fit in fast](https://mp.weixin.qq.com/s/xxx) | Workplace Growth | 100K  | 2026-05-15 | 9.8       | 3.0  | 2.0        | **14.8**  |
| [Workplace communication: 3 sentences you must never say!](https://mp.weixin.qq.com/s/xxx) | Workplace Tips   | 85K   | 2026-05-14 | 9.5       | 2.8  | 2.0        | **14.3**  |
| [Workers must save: 7 secrets to efficient meetings](https://mp.weixin.qq.com/s/xxx)       | Workplace Lab    | 62K   | 2026-05-13 | 9.2       | 2.5  | 1.8        | **13.5**  |
| ...                                                                                        | ...              | ...   | ...        | ...       | ...  | ...        | ...       |

**🔤 Query expansion**: work, office workers, workplace outfits, workplace tips, growth, niche careers, managing up, workplace anxiety, promotion, financial freedom

---

📬 **Subscription**

1️⃣ Subscribe to articles matching your current search? Scheduled pushes after subscription.

2️⃣ Not now

---

## Use Cases

| Scenario                | Role               | Example question                                      | Benefit                                |
| ----------------------- | ------------------ | ----------------------------------------------------- | -------------------------------------- |
| Topic inspiration       | Content creator    | "What hot workplace articles are there lately?"       | Quickly get topic direction            |
| Viral pattern breakdown | WeChat operator    | "Find emotional viral articles and analyze structure" | Learn viral title and content patterns |
| Industry trend analysis | Brand / business   | "What's hot in food niche lately?"                    | Monitor industry KOL dynamics          |
| Multi-niche scan        | Self-media learner | "Show me site-wide hot articles"                      | Grasp cross-platform hot directions    |
| Scheduled tracking      | Content creator    | "Push workplace articles to me every morning"         | Automated industry trend tracking      |

---

## Important data notes

### Recommended hot niches (22)

Humanities, knowledge, wellness, fashion, food, lifestyle, travel, humor, emotions, sports & entertainment, beauty, digest, civic news, wealth & finance, tech & digital, venture & business, automotive, real estate, career, education & exams, academic

### Data notes

- **Data scope**: Viral articles are those with 5,000+ reads
- **Update time**: Daily 7:00 AM with yesterday's data
- **Data freshness**: Engagement cutoff is ingestion time, not real-time; may continue growing after ingestion
- **Query range**: Currently supports data from the past 30 days

### Ranking rules

- **Keyword search**: Sorted by total score (relevance + heat + timeliness) descending; max 15 pts
- **Site-wide hot**: Sorted by read count descending
- **Relevance**: How well the article matches the keyword (max 10 pts)
- **Heat**: Overall heat performance (max 3 pts)
- **Timeliness**: Recency weight (max 2 pts)

### Query expansion rules

- When a broad category keyword (track keyword) is detected, related sub-directions are recommended automatically
- When your keyword returns no results, it may be too niche — our indexing threshold is 5,000+ reads. Try expanded terms or a wider time range, or explore other hot niches for inspiration
