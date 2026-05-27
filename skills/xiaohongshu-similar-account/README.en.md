# Xiaohongshu Similar Account

---

## Introduction

Quickly find Xiaohongshu accounts you can directly learn from and aspire to catch up with.

**Core Value**

Based on follower count, niche, engagement data, and content style, this skill matches you with two types of benchmark accounts: same-level benchmarks (similar follower count, directly copyable tactics) and high-level benchmarks (3–5× followers, proven models to aspire to) — each with AI-generated, conversational recommendation reasons and an operations analysis summary.

**Who It's For**

- 🎬 New creators — Find same-niche benchmark accounts and quickly learn copyable tactics
- 📦 Content ops / MCN agencies — Batch-screen benchmark accounts to develop content strategies
- 🏢 Brands / ad buyers — Evaluate influencer partnership value and match niche KOL candidates
- 📊 Account-starters — Precisely match by niche + followers + level to reduce startup uncertainty

---

## Features

### Core Capabilities

- **Dual input modes**: Query by Xiaohongshu account ID directly, or filter by niche + follower count + account level
- **Same-level benchmark matching**: Recommends accounts with similar follower counts and copyable playbooks, with recommendation reasons (content direction, update frequency, engagement performance, viral post examples)
- **High-level benchmark recommendations**: Recommends accounts with 3–5× followers as proven, aspirational models
- **Smart mapping**: Niche keywords and account levels are automatically fuzzy-matched (e.g., "cooking" → "美味佳肴", "newbie" → "素人")
- **HTML report generation**: Generates a visual HTML report with clickable account names linking to Xiaohongshu profiles; supports PDF/image export
- **Subscription push**: Subscribe to daily benchmark account updates delivered at 7 PM

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

Describe what you need in plain language — no commands to memorize.

### Quick phrase reference

| Intent            | Example phrase                                              | What you get                                     |
| ----------------- | ----------------------------------------------------------- | ------------------------------------------------ |
| Query by ID       | "My Xiaohongshu ID is 27493135897, find benchmark accounts" | Same-level and high-level benchmarks for that ID |
| Niche + followers | "Cooking niche, ~3000 followers, recommend benchmarks"      | Same follower tier in 美味佳肴 niche             |
| Niche + level     | "Beauty niche newbie creators, accounts I can learn from"   | 化妆美容 niche at 素人 level benchmarks          |
| Follower range    | "Fashion niche, 1000–5000 follower account recommendations" | 时尚穿搭 niche in specified follower range       |
| Download report   | "Generate an HTML report for benchmark accounts"            | Visual HTML file delivered                       |
| Subscribe         | "Push food-niche benchmark accounts to me daily"            | Daily 7 PM auto-push task created                |

### Sample output

✨ Matched **【Same-level benchmarks to copy (10)】** and **【High-level benchmarks to chase (2)】** — reference as needed:
| Data note: Data fetched on 2026-04-10; may differ from real-time platform data.

👉 **【Same-level benchmarks to copy (10)】** (directly copyable playbooks)

| Account         | Followers | Total engagement | Recommendation reason                                                                               |
| --------------- | --------- | ---------------- | --------------------------------------------------------------------------------------------------- |
| [Account](link) | 3200      | 15K              | Food tutorials, stable updates, high engagement; viral post "5-min breakfast…" got 23K interactions |
| [Account](link) | 2800      | 8500             | Daily vlog style, consistent updates, solid engagement base                                         |
| …               | …         | …                | …                                                                                                   |

👉 **【High-level benchmarks to chase (2)】** (proven models to aspire to)

| Account         | Followers | Total engagement | Recommendation reason                                            |
| --------------- | --------- | ---------------- | ---------------------------------------------------------------- |
| [Account](link) | 12K       | 86K              | 12K followers, monetization-ready, review content, daily updates |
| …               | …         | …                | …                                                                |

📊 **Analysis summary**:

- Same-level benchmarks: avg 2.9K followers, avg 11K engagement
- High-level benchmarks: avg 12K followers, avg 86K engagement
- Suggested focus: high-frequency updaters among same-level benchmarks — learn their rhythm and topics

📬 **Subscription**
1️⃣ Subscribe to benchmark pushes for your current query — daily 7 PM updates. Choose frequency and time~
2️⃣ Not now

---

## Use Cases

| Scenario                   | Role              | Example question                                         | Benefit                                     |
| -------------------------- | ----------------- | -------------------------------------------------------- | ------------------------------------------- |
| New account benchmarks     | New creator       | "I'm food niche, 3K followers, newbie — find benchmarks" | Quickly find copyable tactics               |
| Batch influencer screening | Brand / ad buyer  | "Fashion mid-tier KOLs with good engagement"             | Efficiently screen KOL ad candidates        |
| Content strategy           | Content ops / MCN | "Fitness niche 10K follower accounts doing well?"        | Learn top niche playbooks, optimize topics  |
| Account launch reference   | Account-starter   | "Pet niche newbie — accounts I can learn from?"          | Reduce startup confusion, clarify direction |
| Monitor benchmark changes  | Ops team          | "Push food-niche benchmarks to me daily"                 | Automated tracking of latest benchmark data |

---

## Important data notes

### Supported niches (25)

All categories, mobility, hobbies, film & entertainment, tech, healthcare, misc, astrology & emotions, fashion, weddings, photography, education, beauty, home decor, travel, parenting, personal care, food, career, pets, bags & shoes, daily life, science, news, sports & fitness

### Data freshness

Recommended account data comes from API; fetch time is ingestion moment — may differ from Xiaohongshu real-time data.

---
