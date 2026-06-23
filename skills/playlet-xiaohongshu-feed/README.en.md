# Playlet Xiaohongshu Feed / playlet-xhs-feed

---

## Introduction

Daily scanning of trending Xiaohongshu short drama content, filtering popular posts by engagement metrics, intelligently clustering by genre, and generating a visual daily report with creative insights — helping short drama creators capture the pulse of trending content.

**Core Value**

- 📊 Daily automatic scanning of Xiaohongshu short drama content, filtering trending works by engagement
- 🏷️ Intelligent genre clustering (time travel / CEO romance / rebirth / suspense, etc.), dynamically determined by content each day
- 📈 Generates a visual daily report with cover images, engagement data, and creative insights
- 🔍 Supports targeted queries by genre, creator, and time range
- 🔔 One-click subscription for automatic daily report delivery to local folder

**Who It's For**

- 🎬 Short Drama Screenwriters/Producers — Capture trending signals and improve pitch accuracy
- 📊 Short Drama Operations/MCNs — Track competitor performance and refine operational strategies
- 🔍 Content Strategists/Data Analysts — Produce structured trend reports to support content decisions

---

## Features

### Core Features

- 📊 **Trending Discovery** — Filter high-engagement short drama content from Xiaohongshu, pinpointing high-heat posts
- 🏷️ **Genre Clustering** — Auto-identify genres (time travel / CEO romance / rebirth / suspense, etc.), dynamically determined each day
- 🔍 **Smart Querying** — Query all short dramas by default, auto-expanding genres in batches when data is sparse to save API quota
- 🎯 **Custom Queries** — Target specific genres, creators, or keywords for flexible niche exploration
- 📈 **Creative Insights** — Analyze trending title patterns, genre trends, and top creator performance
- 🎨 **Visual Daily Report** — Dark-themed page with cover images, engagement data, and direct post links
- 🔔 **One-Click Subscription** — Enable daily auto-generation with reports saved to local folder

### Highlights

- ⚡ **Smart Date Detection** — Built-in 15:00 daily update rule auto-checks data availability, no manual calculation needed
- 📱 **Xiaohongshu Native** — Post links auto-generated as `xiaohongshu.com/explore/`, zero-engagement fields hidden automatically
- 🔒 **Secure & Reliable** — API Key accessed only via environment variable, hardcoding strictly prohibited

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?souce=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, verify its source, available scope, validity period, and whether reset/revocation is supported.
- Do not hardcode or expose the key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Prompt | Outcome |
|--------|---------------|---------|
| Get latest daily report | "Generate the latest Xiaohongshu short drama daily report" / "Show me short drama trends" | Fetches the latest available daily report with genre clustering and trend analysis |
| Query a historical date | "Show me the June 10 Xiaohongshu short drama report" | Generates a daily report for the specified date |
| Query by genre | "Show me time travel short drama trends" / "Check CEO romance and sweet romance genres" | Targeted genre query with automatic deduplication and clustering |
| Creative trend analysis | "Analyze recent short drama creative trends" / "What's trending in short dramas" | Outputs genre trends, title pattern analysis, top creator rankings, and cross-genre suggestions |
| Enable daily subscription | "Turn on daily short drama report subscription" | Reports auto-generated daily and saved to local folder |

### Output Example

Once the daily report is generated, you will receive:

- **📊 Genre Overview Table** — Count, share, and highlight pieces for each genre
- **🔥 Emerging Signals** — Low-volume but high-engagement potential genres
- **📝 Trending Title Patterns** — Frequent title patterns, occurrence count, and average engagement
- **👤 Top Creator Rankings** — Creator work count, total engagement, and representative pieces
- **📈 Genre Trend Report** — Detailed analysis and creative suggestions for top genres
- **🌐 Cross-Genre Suggestions** — Genre fusion trend observations

A visual report page is also generated, with cover images, engagement data, and direct post links, automatically opened in your browser.

---

## Use Cases

| Scenario | Role | Example Prompt | Benefit |
|----------|------|---------------|---------|
| Content Inspiration | Screenwriter/Producer | "Generate the latest Xiaohongshu short drama daily report" | Understand trending genres and topics to guide creative decisions |
| Competitive Monitoring | Operations/MCN | "How are CEO romance dramas performing lately" | Track competitor performance and refine strategies |
| Trend Analysis | Strategist/Analyst | "Analyze recent short drama creative trends" | Produce structured trend reports to support content strategy |

---

## Important Data Notes

- **Data Update Time**: Daily at 15:00, updating the previous day's data
- Before 15:00, the latest available date is two days prior (T-2); after 15:00, it is the previous day (T-1)
- When target date data has not yet been updated, users are prompted for confirmation before any API call
- Data source: RedFoxHub API, based on Xiaohongshu platform (platform=3)
- Data tracking: API requests include a `source` field set to `短剧小红书信息源-GitHub` for usage attribution
