# Douyin Daily Like Surge Ranking / douyin-content-surge

---

## Overview

A daily content surge monitoring tool that tracks tens of thousands of Douyin works platform-wide, delivering a TOP50 ranking of daily new likes across 28 content categories with 30-day historical review capability.

**Core Value**

- **Platform-wide Coverage**: Tracks tens of thousands of Douyin works daily across 28 categories (Food, Gaming, Anime, Celebrity, etc.), ensuring no trending content is missed.
- **Precise Surge Data**: Daily new interactions (likes / favorites / comments / shares) displayed at a glance, separated from cumulative totals for clear growth insight.
- **Flexible Category Filtering**: Query the full platform ranking or drill into a specific category to focus on what matters to you.
- **Historical Backtracking**: Access any daily surge ranking within the past 30 days for trend review and periodic analysis.
- **Subscription Push**: Subscribe by category and time preference; the latest surge ranking is automatically pushed daily at 06:00.

**Who It's For**

- 📊 **Content Operators** — Track daily surge trends, discover potential topics and benchmark content.
- 🎬 **Short Video Creators** — Learn from surge patterns within your category to optimize content direction.
- 🏢 **MCN Agencies** — Monitor category performance at scale and shape operational strategies.
- 🔍 **Data Analysts** — Access structured surge data to support content research and reporting.

---

## Features

### Core Features

- **Multi-Category Querying**: Supports 28 categories (Drama, Food, Gaming, Anime, Celebrity, etc.) plus an all-category consolidated surge ranking.
- **Flexible Time Selection**: Query "today" (returns yesterday's latest data), a specific historical date (within 30 days), or the earliest available date.
- **TOP50 Ranking Output**: Defaults to TOP20 display; request the full 50 entries anytime. Video titles are presented as clickable Douyin links.
- **New Interaction Data**: New likes, new favorites, new comments, new shares, and publish time are clearly displayed for each entry.
- **Subscription Push**: Subscribe to daily surge rankings for any category; automatically pushed after the 06:00 daily update.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please register an account at [RedFoxHub](https://redfox.hk?souce=github) to obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing your key, verify its source, scope, validity period, and whether reset/revocation is supported.
- Never hardcode or expose keys in plain text within code, prompts, logs, or output files.

---

## How to Use

Simply describe what you need in natural language — no commands to memorize.

### Quick Reference Phrases

| Intent | Example Query | Result |
| -------- | ---------------------------- | -------- |
| Full Ranking | "Show me today's Douyin surge ranking" | Returns yesterday's all-category new likes TOP20 |
| Specific Category | "Show me the Food surge ranking" or "How's Fitness trending today?" | Returns yesterday's TOP20 for the specified category |
| Historical Date | "Give me the surge ranking for May 28" | Returns surge data for the specified date |
| Full List | "Full 50 entries for the Food surge ranking" | Returns all 50 entries for the category |
| Daily Subscription | "Subscribe me to daily Food surge rankings" | Auto-pushes latest data daily at 06:00 |

### Output Example

After querying, you'll receive a Markdown-formatted ranking with clickable video links:

📊 Douyin Daily Like Surge TOP20 (2026-06-01)

| Rank | Title | Author | Category | New Favs | New Comments | New Shares | **New Likes** | Publish Time |
|------|---------|------|------|---------|---------|---------|------------|---------|
| 1 | [Can you cut watermelon like this?](https://www.iesdouyin.com/share/video/...) | People's Daily | Food | 5.2w | 137 | 49w+ | **49w+** | 06-01 11:00 |
| 2 | [Spicy Lemon Shrimp Recipe](https://www.iesdouyin.com/share/video/...) | Cheng's Kitchen | Food | 21w+ | 4,548 | 15w+ | **28w+** | 05-28 15:00 |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | -------- | -------- | -------- |
| Daily Surge Monitoring | Content Operators | "What's on today's Douyin surge ranking?" | Quickly grasp daily trending content |
| Category Competitor Research | Short Video Creators | "What's surging in Food these days?" | Understand category patterns to improve content |
| Historical Trend Review | Data Analysts | "Show me the surge data for the last week of May" | Backtrack trends for periodic analysis |
| Daily Subscription Tracking | MCN Agencies | "Subscribe to daily Food and Gaming surge rankings" | Automatic daily delivery, no repeat queries |

---

## Important Data Notes

- **Update Time**: Daily update at 06:00 for the previous day's full data.
- **Backtrack Range**: Supports historical queries within the past 30 days.
- **Data Volume**: Up to 50 entries per category; defaults to TOP20 display.
- **Data Definition**: Surge data represents daily new interaction counts (ingestion time snapshot) and differs from cumulative totals.
