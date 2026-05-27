# Douyin Top Account Rankings / douyin-top-account

---

## Introduction

Quickly discover the most influential accounts on Douyin and stay on top of niche trends.

**Core Value**

Based on daily TOP 50 account data across all Douyin niches — follower growth, engagement, and growth trends — this skill helps you with topic decisions, benchmark accounts, competitor monitoring, and niche selection.

**Who It's For**

- 🎬 Content creators — see how top accounts perform in your niche and find benchmarks to learn from
- 🏢 Brands / ad buyers — efficiently screen quality creators and evaluate partnership value
- 📦 MCN agencies / content teams — track competitor dynamics and shape operations strategy
- 📊 Industry analysts — get data insights and generate analysis reports

---

## Features

### Core Capabilities

- **Ranking queries**: Daily, weekly, and monthly TOP 50 account rankings; TOP 20 shown by default
- **Niche filtering**: Query across all hot niches on Douyin or drill into any of 27 track categories with fuzzy keyword matching
- **Composite score**: Weighted ranking from total followers, new followers, and new likes/shares/comments — objective and credible, scored out of 100
- **HTML report generation**: Visual HTML reports with clickable account names linking to Douyin profiles; export as image or PDF
- **Subscription push**: Schedule daily, weekly, or monthly ranking updates, or subscribe by specific niche

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

| Intent               | Example phrase                                          | What you get                       |
| -------------------- | ------------------------------------------------------- | ---------------------------------- |
| Daily ranking        | "What's the latest Douyin daily account ranking?"       | Latest all-niche daily TOP 20      |
| Weekly niche ranking | "How did food accounts rank on Douyin last week?"       | Latest food-niche weekly TOP 20    |
| Monthly ranking      | "Show me last month's gaming account ranking on Douyin" | Latest gaming-niche monthly TOP 20 |
| Full ranking         | "I want to see all 50 entries"                          | Full TOP 50 with report            |
| Download report      | "Generate an HTML report for this ranking"              | Visual HTML file delivered         |
| Subscribe            | "Send me daily food-niche Douyin ranking updates"       | Scheduled push task created        |

### Sample output

📊 Douyin Daily Ranking · All niches

Data date: 2025-05-19
50 accounts on the list (showing TOP 20)

💡 Ranking note: Data updates daily at 17:30 with yesterday's figures; may differ from real-time data.

📐 Composite score: Weighted from total followers, new followers, and new likes/shares/comments; max 100:

| Rank | Account (clickable) | Score | Total followers | New followers | New likes | New comments | New shares |
| :--: | ------------------- | :---: | :-------------: | :-----------: | :-------: | :----------: | :--------: |
| 🥇 1 | Account name        |  96   |      2.54M      |     6,919     |   246K    |     67K      |    134K    |
| 🥈 2 | Account name        |  89   |      1.13M      |     19.1K     |    79K    |    4,787     |   31.2K    |
|  …   | …                   |   …   |        …        |       …       |     …     |      …       |     …      |

⚡ More actions
⏺️ This ranking has 50 entries in total. View the remaining 30?

📬 Subscription
1️⃣ Subscribe to daily/weekly/monthly Douyin account ranking updates?
2️⃣ Subscribe to a specific niche?

---

## Use Cases

| Scenario                        | Role                    | Example question                                                | Benefit                                             |
| ------------------------------- | ----------------------- | --------------------------------------------------------------- | --------------------------------------------------- |
| Find niche benchmark accounts   | Creator / solo operator | "Which food accounts are doing well? Show me the daily ranking" | Quickly spot category leaders and clarify direction |
| Evaluate creator partnerships   | Brand / ad buyer        | "Who stood out in last week's Douyin beauty TOP 50?"            | Batch screening for faster partnership decisions    |
| Monitor competitor niches       | MCN / content team      | "Which gaming accounts gained followers fastest this week?"     | Track competitive landscape and respond quickly     |
| Generate industry reports       | Analyst / consultant    | "Generate a March Douyin gaming ranking report for me"          | One-click visual HTML for sharing and presentations |
| Track ranking changes regularly | Operations team         | "Send me the latest travel weekly ranking every Monday"         | Automated ranking intelligence via subscription     |

---

## Important data notes

### Update schedule and lookback

| Ranking type | Update time                           | Lookback      |
| ------------ | ------------------------------------- | ------------- |
| Daily        | Daily 17:30 — yesterday's data        | Past 7 days   |
| Weekly       | Monday 17:30 — last week's data       | Past 3 weeks  |
| Monthly      | 2nd of month 9:00 — last month's data | Past 3 months |

### Supported niches (27)

Personal talent, lifestyle vlog, wealth & finance, anime/2D, home decor, education, short drama, tech, travel, food, beauty, pets, parenting, automotive, relationships, agriculture, health & medicine, fashion, dance, looks & styling, humanities, music, film & TV, fitness, sports, celebrity entertainment, gaming

### Data freshness

Data is not real-time. Engagement figures reflect the collection moment and may differ from live platform data.

---
