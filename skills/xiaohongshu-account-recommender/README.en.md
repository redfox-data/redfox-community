# Xiaohongshu Benchmark Accounts

---

## Overview

Quickly find Xiaohongshu accounts you can directly learn from and aspire to catch up with.

**Core Value**

Based on follower count, niche, engagement data, and content style, this tool matches you with two types of benchmark accounts: same-level benchmarks (similar follower count, directly copyable tactics) and high-level benchmarks (3–5× followers, proven models to aspire to) — each with AI-generated, conversational recommendation reasons and an operations analysis summary.

**Intended Users**

- 🎬 New creators — find same-niche benchmark accounts and quickly learn copyable tactics
- 📦 Content ops / MCN agencies — batch-screen benchmark accounts to develop content strategies
- 🏢 Brands / ad buyers — evaluate influencer partnership value and match niche KOL candidates
- 📊 Account-starters — precisely match by niche + followers + level to reduce startup uncertainty

---

## Features

### Core Capabilities

- **Dual input modes**: query by Xiaohongshu account ID directly, or filter by niche + follower count + account level
- **Same-level benchmark matching**: recommends accounts with similar follower counts and copyable playbooks, with recommendation reasons (content direction, update frequency, engagement performance, viral post examples)
- **High-level benchmark recommendations**: recommends accounts with 3–5× followers as proven, aspirational models
- **Smart mapping**: niche keywords and account levels are automatically fuzzy-matched (e.g., "cooking" → "美食/美味佳肴", "newbie" → "素人/ordinary user")
- **HTML report generation**: generates a visual HTML report with clickable account names linking to Xiaohongshu profiles; supports PDF/image export
- **Subscription push**: subscribe to daily benchmark account updates delivered at 7 PM

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/dashboard/keys?souce=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?souce=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent                      | Example phrase                                                     | Result                                                            |
| --------------------------- | ------------------------------------------------------------------ | ----------------------------------------------------------------- |
| Query by ID                 | "My Xiaohongshu ID is 27493135897, find benchmark accounts for me" | Match same-level and high-level benchmarks based on that account  |
| Filter by niche + followers | "Cooking niche, around 3K followers, recommend benchmark accounts" | Return same-follower-level benchmarks in the food niche           |
| Filter by niche + level     | "Beauty niche ordinary users, find accounts I can learn from"      | Return beauty-niche ordinary-user-level benchmarks                |
| Filter by follower range    | "Fashion niche, 1K–5K follower accounts recommended"               | Return fashion-niche accounts within the specified follower range |
| Download report             | "Generate an HTML report for these benchmark accounts"             | Visual HTML file delivered                                        |
| Subscribe push              | "Push daily food-niche benchmark accounts to me"                   | Create a 7 PM daily auto-push task                                |

### Output Example

✨ Matched 【directly copyable same-level benchmarks (10)】and【aspirational high-level benchmarks (2)】— 2 groups of benchmarks for your reference:
| Data note: data fetched at 2026-04-10; differs from live data.

👉 【Directly copyable same-level benchmarks (10)】(copy their tactics)

| Account              | Followers | Total Engagement | Recommendation Reason                                                                                     |
| -------------------- | --------- | ---------------- | --------------------------------------------------------------------------------------------------------- |
| [Account Name](link) | 3,200     | 15K              | Food tutorials, stable updates, high engagement, viral post "5-min quick breakfast…" got 23K interactions |
| [Account Name](link) | 2,800     | 8,500            | Daily vlog style, consistently updating, solid engagement foundation                                      |
| …                    | …         | …                | …                                                                                                         |

👉 【Aspirational high-level benchmarks (2)】(proven models to learn from)

| Account              | Followers | Total Engagement | Recommendation Reason                                     |
| -------------------- | --------- | ---------------- | --------------------------------------------------------- |
| [Account Name](link) | 12K       | 86K              | 12K followers, monetizable, review content, daily updates |
| …                    | …         | …                | …                                                         |

📊 **Analysis Summary**:

- Same-level benchmark avg followers: 2.9K, avg engagement: 11K
- High-level benchmark avg followers: 12K, avg engagement: 86K
- Recommended priority: high-frequency same-level accounts — learn their content cadence and topic direction

📬 **Subscription**
1️⃣ Subscribe to benchmark account push for current query conditions, updated daily at 7 PM. You can choose frequency and time~
2️⃣ Not now

---

## Use Cases

| Scenario                          | Role              | Example Question                                                       | Benefit                                                  |
| --------------------------------- | ----------------- | ---------------------------------------------------------------------- | -------------------------------------------------------- |
| Find benchmarks for a new account | New creator       | "I do food content, 3K followers, find my benchmarks"                  | Quickly find copyable operational tactics                |
| Batch-screen influencers          | Brand / ad buyer  | "Fashion niche mid-tier KOLs, recommend accounts with good engagement" | Efficiently shortlist KOL partnership candidates         |
| Develop content strategy          | Content ops / MCN | "Fitness niche 10K-follower accounts, which ones perform well?"        | Learn top-niche playbooks and optimize topic direction   |
| Get startup direction reference   | Account-starter   | "Pet niche newbie, which accounts can I learn from?"                   | Reduce startup uncertainty and clarify content direction |
| Track benchmark changes           | Ops team          | "Push daily food-niche benchmark accounts to me"                       | Automated tracking of benchmark account latest data      |

---

## Important Data Notes

### Supported Niches (25)

All Categories, Commuting, Leisure & Hobbies, Film & Entertainment, Consumer Tech, Health & Medical, General Misc, Astrology & Relationships, Fashion & Outfits, Wedding, Photography & Vlog, Education, Beauty & Makeup, Home Decor, Travel, Parenting, Personal Care, Food & Dining, Career Development, Pets, Trendy Shoes & Bags, Daily Life, Science & Discovery, News & Current Affairs, Fitness & Sports

### Data Freshness

Recommended account data comes from an API interface; the data fetch timestamp reflects the ingestion time and may differ from Xiaohongshu's live platform data.
