# Cultural Tourism Douyin Feed / cultural-tourism-douyin-feed

---

## Overview

Search Douyin for trending cultural tourism content, ranked by likes with automatic topic clustering. Generates a polished HTML visual report with time range filtering and daily subscription support.

**Core Value**

- **Full Coverage**: 200 entries per query, comprehensive data for the cultural tourism niche.
- **Smart Clustering**: Auto-categorized by `type/topic` tags, giving you a clear view of each segment.
- **Polished Reports**: Dark-themed HTML with card grids and cover images, full-text search support.
- **Daily Subscription**: Set up auto-delivery of daily reports with no manual repetition.

**Who It's For**

- 📱 **Content Operators / Social Media Managers** — Track daily cultural tourism hotspots and find content inspiration.
- 🏨 **Scenic Spot / Tourism Professionals** — Monitor competitor activity and visitor feedback for marketing decisions.
- 📊 **Tourism Researchers** — Track cultural tourism trends and gather primary data.

---

## Features

### Core Features

- **Keyword Search**: Precise search by scenic spot, city, or topic; also supports empty keywords for full-scope cultural tourism content.
- **Time Filtering**: Filter by date range for flexible data windows.
- **Auto Clustering**: 200 entries automatically grouped by topic tags to reduce noise and highlight key themes.
- **Visual Report**: Dark-themed HTML report with card grids and cover images for a polished presentation.
- **Daily Subscription**: Use `--subscribe` for scheduled auto-delivery without manual repetition.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing the key, verify its source, scope, expiration, and whether it supports reset/revocation.
- Do not hardcode or expose the key in code, prompts, logs, or output files.

---

## How to Use

Just describe what you need in natural language — no commands to memorize.

### Quick Reference

| Intent | Example | Result |
| ------ | ------- | ------ |
| Latest trending content | "Show me the latest Douyin cultural tourism hits" | Pulls all popular cultural tourism content with category stats and a report |
| Search specific location | "What's trending about Jiuzhaigou on Douyin?" | Precise keyword search for high-engagement content |
| Past 7 days data | "Show me the past 7 days of Douyin cultural tourism data" | Date-range query showing trend changes |
| Daily subscription | "Subscribe to the Douyin cultural tourism daily report" | Scheduled auto-fetch of latest data |

### Sample Output

After execution, you'll receive:

📌 Data note: Data updates daily at 5 PM for the previous day

| Category | Count |
| -------- | ----- |
| Scenic Spots | 23 |
| Travel Guides | 22 |
| ... | ... |

N entries across N categories. Full data and clickable links available in the HTML report.

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Daily hotspot tracking | Content Operator | "Show me the latest Douyin cultural tourism hits" | Get today's trending cultural tourism content and topics |
| Competitive analysis | Scenic Spot Marketer | "What's trending about the Forbidden City on Douyin?" | Understand competitors' content strategies and user engagement |
| Tourism research | Researcher | "Show me the past 7 days of Douyin cultural tourism data" | Gather recent cultural tourism trend data |
| Automated daily report | Team Manager | "Subscribe to the Douyin cultural tourism daily report" | Daily auto-delivery keeps the team in sync |
