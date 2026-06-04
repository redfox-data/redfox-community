# Xiaohongshu Top Account

---

## Introduction

Quickly discover the most influential accounts on Xiaohongshu each day and stay on top of niche trends.

**Core Value**

Based on daily TOP 50 account data across all Xiaohongshu niches — follower growth, engagement, and growth trends — this skill helps you with topic decisions, benchmark accounts, competitor monitoring, and niche selection.

**Who It's For**

- 🎬 Content creators — See how top accounts perform in your niche and find benchmarks to learn from
- 🏢 Brands / ad buyers — Efficiently screen quality creators and evaluate partnership value
- 📦 MCN agencies / content teams — Track competitor dynamics and shape operations strategy
- 📊 Industry analysts — Get data insights and generate analysis reports

---

## Features

### Core Capabilities

- **Ranking queries**: Daily, weekly, and monthly TOP 50 account rankings; TOP 20 shown by default
- **Niche filtering**: Query across all hot niches on Xiaohongshu or drill into any of 25 track categories with fuzzy keyword matching
- **Composite score**: Weighted ranking from total followers, new followers, and new likes/saves/shares/comments — objective and credible, scored out of 100
- **HTML report generation**: Visual HTML reports with clickable account names linking to Xiaohongshu profiles; export as image or PDF
- **Subscription push**: Schedule daily, weekly, or monthly ranking updates, or subscribe by specific niche

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain your `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` as a device environment variable before using this skill.
- Before providing your key, confirm its source, available scope, validity period, and whether reset/revocation is supported.
- Do not hard-code or expose the key in plaintext in code, prompts, logs, or output files.

---

## Usage Guide

Describe what you need in plain language — no commands to memorize.

### Quick phrase reference

| Intent               | Example phrase                                            | What you get                         |
| -------------------- | --------------------------------------------------------- | ------------------------------------ |
| Daily ranking        | "What's the latest Xiaohongshu daily account ranking?"    | Latest all-niche daily TOP 20        |
| Weekly niche ranking | "How did food accounts rank on Xiaohongshu last week?"    | Latest 美味佳肴 niche weekly TOP 20  |
| Monthly ranking      | "Show me last month's beauty Xiaohongshu account ranking" | Latest 化妆美容 niche monthly TOP 20 |
| Full ranking         | "I want to see all 50 entries"                            | Full TOP 50 with report              |
| Download report      | "Generate an HTML report for this ranking"                | Visual HTML file delivered           |
| Subscribe            | "Send me daily food-niche Xiaohongshu ranking updates"    | Scheduled push task created          |

### Sample output

📊 Xiaohongshu Daily Ranking · All niches

Data date: 2026-04-28
50 accounts on the list (showing TOP 20)

💡 Ranking note: Data updates daily at 19:00 with yesterday's figures; may differ from real-time data.

📐 Ranking algorithm: Weighted from total followers, period follower growth, likes, saves, shares, and comments; max score 100

| Rank | Account (clickable) | Score | Total followers | New posts | New followers | New likes | New comments | New saves | New shares |
| :--: | ------------------- | :---: | :-------------: | :-------: | :-----------: | :-------: | :----------: | :-------: | :--------: |
| 🥇 1 | Account name        |  96   |      2.54M      |     7     |     6,919     |   246K    |     67K      |    25K    |    134K    |
| 🥈 2 | Account name        |  89   |      1.13M      |     1     |     19.1K     |    79K    |    4,787     |    22K    |   31.2K    |
|  …   | …                   |   …   |        …        |     …     |       …       |     …     |      …       |     …     |     …      |

⚡ More actions
⏺️ This ranking has 50 entries in total. View the remaining 30?

📬 Subscription
1️⃣ Subscribe to daily/weekly/monthly Xiaohongshu account ranking updates?
2️⃣ Subscribe to a specific niche?

---

## Use Cases

| Scenario                        | Role                    | Example question                                                  | Benefit                                             |
| ------------------------------- | ----------------------- | ----------------------------------------------------------------- | --------------------------------------------------- |
| Find niche benchmark accounts   | Creator / solo operator | "Which beauty accounts are doing well? Show me the daily ranking" | Quickly spot category leaders and clarify direction |
| Evaluate creator partnerships   | Brand / ad buyer        | "Who stood out in last week's Xiaohongshu fashion TOP 50?"        | Batch screening for faster partnership decisions    |
| Monitor competitor niches       | MCN / content team      | "Which food accounts gained followers fastest this week?"         | Track competitive landscape and respond quickly     |
| Generate industry reports       | Analyst / consultant    | "Generate a March Xiaohongshu tech ranking report for me"         | One-click visual HTML for sharing and presentations |
| Track ranking changes regularly | Operations team         | "Send me the latest travel weekly ranking every Monday"           | Automated ranking intelligence via subscription     |

---

## Important data notes

### Update schedule and lookback

| Ranking type | Update time                           | Lookback      |
| ------------ | ------------------------------------- | ------------- |
| Daily        | Daily 19:00 — yesterday's data        | Past 7 days   |
| Weekly       | Monday 15:00 — last week's data       | Past 3 weeks  |
| Monthly      | 2nd of month 9:00 — last month's data | Past 3 months |

### Supported niches (25)

All categories, mobility, hobbies, film & entertainment, tech, healthcare, misc, astrology & emotions, fashion, weddings, photography, education, beauty, home decor, travel, parenting, personal care, food, career, pets, bags & shoes, daily life, science, news, sports & fitness

### Composite score notes

Score is weighted: total followers (20%), new followers (20%), new likes (15%), new saves (15%), new shares (15%), new comments (15%); max 100. Uses log normalization to avoid top accounts dominating scores, making mid-tier rankings more reference-worthy.

### Data freshness

Data is not real-time. Engagement figures reflect the collection moment and may differ from live platform data.

---
