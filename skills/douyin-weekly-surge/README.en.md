# Douyin Weekly Like Surge Ranking / douyin-weekly-surge

---

## Overview

A weekly content surge monitoring tool that tracks tens of thousands of Douyin works platform-wide, delivering a TOP50 ranking of 7-day new likes across 28 content categories with 30-day historical review capability.

**Core Value**

- **Platform-wide Coverage**: Tracks tens of thousands of Douyin works daily across 28 categories (Food, Gaming, Anime, Celebrity, etc.), ensuring no trending content is missed.
- **Precise Weekly Surge Data**: 7-day new interactions (likes / favorites / comments / shares) displayed at a glance, separated from cumulative totals for clear weekly growth insight.
- **Flexible Category Filtering**: Query the full platform ranking or drill into a specific category to focus on what matters to you.
- **Historical Backtracking**: Access any 7-day surge ranking within the past 30 days for trend review and periodic analysis.
- **Subscription Push**: Subscribe by category and time preference; the latest 7-day surge ranking is automatically pushed daily at 06:00.

**Who It's For**

- 📊 **Content Operators** — Track 7-day surge trends, discover potential topics and benchmark content.
- 🎬 **Short Video Creators** — Learn from 7-day surge patterns within your category to optimize content direction.
- 🏢 **MCN Agencies** — Monitor category performance at scale and shape operational strategies.
- 🔍 **Data Analysts** — Access structured 7-day surge data to support content research and reporting.

---

## Features

### Core Features

- **Weekly Surge**: Daily TOP50 ranking by 7-day new likes — discover works with sustained weekly growth.
- **Category Filtering**: Supports 28 category filters for precise vertical-niche targeting.
- **Historical Lookback**: Up to 30 days of historical data for trend review.
- **Clickable Links**: Work titles output as hyperlinks — one click to the original Douyin video.
- **Paginated Display**: Defaults to TOP20; full TOP50 available on request.
- **Subscription Push**: Subscribe by category and time preference for automated daily updates.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please register an account at [RedFoxHub](https://redfox.hk?source=github) to obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing your key, verify its source, scope, validity period, and whether reset/revocation is supported.
- Never hardcode or expose keys in plain text within code, prompts, logs, or output files.

---

## How to Use

Simply describe what you need in natural language — no commands to memorize.

### Quick Reference Phrases

| Intent | Example Query | Result |
| -------- | ---------------------------- | -------- |
| Full Ranking | "Show me today's Douyin 7-day surge ranking" | Returns the 7-day all-category new likes TOP20 as of yesterday |
| Specific Category | "Show me the Food 7-day surge ranking" or "How's Fitness trending this week?" | Returns the 7-day TOP20 for the specified category as of yesterday |
| Historical Date | "Give me the 7-day surge ranking for May 28" | Returns 7-day surge data for the specified date |
| Full List | "Full 50 entries for the Food 7-day surge ranking" | Returns all 50 entries for the category |
| Daily Subscription | "Subscribe me to daily 7-day Food surge rankings" | Auto-pushes latest data daily at 06:00 |

### Output Example

After querying, you'll receive a Markdown-formatted ranking with clickable video links:

📊 Douyin 7-Day Like Surge TOP20 (as of 2026-06-01)

| Rank | Title | Author | Category | 7D New Favs | 7D New Comments | 7D New Shares | **7D New Likes** | Publish Time |
|------|---------|------|------|---------|---------|---------|------------|---------|
| 1 | [Can you cut watermelon like this?](https://www.iesdouyin.com/share/video/...) | People's Daily | Food | 5.2w | 137 | 49w+ | **49w+** | 06-01 11:00 |
| 2 | [Spicy Lemon Shrimp Recipe](https://www.iesdouyin.com/share/video/...) | Cheng's Kitchen | Food | 21w+ | 4,548 | 15w+ | **28w+** | 05-28 15:00 |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | -------- | -------- | -------- |
| 7-Day Surge Monitoring | Content Operators | "What's on today's Douyin 7-day surge ranking?" | Quickly grasp weekly trending content |
| Category Competitor Research | Short Video Creators | "What's surging in Food this week?" | Understand category patterns to improve content |
| Historical Trend Review | Data Analysts | "Show me the 7-day surge data for the last week of May" | Backtrack trends for periodic analysis |
| Daily Subscription Tracking | MCN Agencies | "Subscribe to daily 7-day Food and Gaming surge rankings" | Automatic daily delivery, no repeat queries |

---

## Important Data Notes

- **Update Time**: Daily update at 06:00 for the past 7-day data.
- **Backtrack Range**: Supports historical queries within the past 30 days.
- **Data Volume**: Up to 50 entries per category; defaults to TOP20 display.
- **Data Definition**: Surge data represents 7-day new interaction counts (ingestion time snapshot) and differs from cumulative totals.
