# Douyin Daily Hot Content Ranking / douyin-daily-hot

---

## Introduction

Daily collection of Douyin (TikTok China) works across the entire platform, delivering a daily likes TOP 50 ranking with category-based filtering and historical date lookback.

**Core Value**

- **Daily Verified Collection**: Manually collected and verified tens of thousands of Douyin works daily, ensuring ranking quality.
- **Full Category Coverage**: Supports 28 mainstream category filters, from food to gaming — one click to reach your target.
- **Historical Lookback**: Up to 30 days of historical data for easy trend review and analysis.

**Target Users**

- 📊 **Content Operations** — Quickly get hot content across categories to track platform trends.
- 🎬 **Creators / Influencers** — Understand top-performing works in your category and benchmark against hits.
- 📈 **Brands / MCNs** — Monitor competitor accounts and category rankings to optimize content and ad strategies.

---

## Features

### Core Features

- **Category-Based Filtering**: Supports 28 categories (food, ACG, gaming, automotive, etc.) plus an all-category ranking for precise targeting.
- **Historical Date Lookback**: Query rankings for any date within the past 30 days for trend review and analysis.
- **All-Category Labels**: In all-category rankings, each item shows its所属category for quick content-type identification.
- **Paginated Display**: Default TOP 20 to reduce information load; full 50 items available on explicit request.
- **Direct Work Links**: Every item title includes a clickable Douyin link to view the original work.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?souce=github) to register and obtain `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing a key, confirm its source, scope, validity period, and whether it supports reset/revocation.
- Do not hard-code or expose keys in plain text within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent              | Example Phrase                        | Result                                  |
| ------------------- | ------------------------------------- | --------------------------------------- |
| Today's ranking     | "Douyin hot list" / "Today's ranking" | Yesterday's all-category likes TOP 20   |
| By category         | "Check the food category" / "ACG hot" | Category-specific likes TOP 20          |
| Historical data     | "May 20th ranking"                    | Ranking for the specified date          |
| Full data           | "Show all" / "Show remaining 30"      | Full 50 items                           |

### Output Example

Results are presented as a Markdown table, default TOP 20:

| Rank | Title                        | Author (Followers) | Category | Collects | Comments | Shares | **Likes** | Published   |
| ---- | ---------------------------- | ------------------- | -------- | -------- | -------- | ------ | --------- | ----------- |
| 1    | [How to Make Braised Pork](link) | Food Master (10w+) | Food     | 10w+     | 10w+     | 10w+   | **10w+**  | 05-28 12:00 |

> The "Category" column is omitted when querying a specific category; item titles are clickable links to the original Douyin work.

---

## Use Cases

| Scenario           | Role                | Example Query                         | Benefit                                          |
| ------------------ | -------------------- | ------------------------------------- | ------------------------------------------------ |
| Daily trend tracking | Content Ops         | "What's hot on Douyin today?"         | Get daily all-category hits, stay on top of trends |
| Category benchmarking | Creators / Influencers | "Check the food category ranking"   | Understand category hits, benchmark top works    |
| Competitor monitoring | Brands / MCNs       | "Who's performing well in automotive?" | Monitor competitor rankings, optimize strategy   |
| Historical review   | Data Analysts        | "May 25th all-category ranking"      | Lookback historical data, analyze trend shifts   |

---

## Important Data Notes

- Data is updated daily at **06:00** with yesterday's data (T-1, meaning the latest available data is from the previous day).
- Historical lookback supports up to **30 days**.
- Engagement metrics are snapshots from the time of data ingestion and may differ from live real-time data.
- Each category returns up to **50 items**.