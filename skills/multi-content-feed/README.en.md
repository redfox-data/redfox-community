# Cross-Platform Content Globalization Feed / multi-content-feed

---

## Overview

A cross-platform content globalization feed that scans trending works daily across all major platforms, selects the Top 50 by engagement, intelligently clusters them by topic, and generates a visual HTML daily report with platform labels, cover images, interaction data, and creative insights. Supports targeted queries by platform, keyword, and time range.

**Core Value**

- 📊 **All-in-One Platform Coverage**: Retrieve data from six major platforms — WeChat Official Accounts, Douyin, WeChat Channels, Xiaohongshu, Kuaishou, and Bilibili — in a single pass, no need to check each one individually.
- 🏷️ **Intelligent Topic Clustering**: Hot topics are automatically grouped based on live data, with no pre-defined keywords required, capturing the day's topic distribution dynamically.
- 📈 **Visual Daily Report**: A clean white-themed HTML page featuring color-coded platform labels, cover images, interaction metrics, and direct links to each work — clear and glanceable.
- 🔍 **Flexible Targeted Queries**: Filter by platform, search by keyword, or define a custom time range to precisely cover any niche direction.

**Who It's For**

- 🎬 **Content Globalization Creators** — Capture traffic trends across all platforms and improve topic selection hit rates.
- 📊 **Operations Teams / MCNs** — Monitor competitor activity and platform hotspots to refine operational strategies.
- 📝 **Content Planners / Data Analysts** — Produce structured trend reports to support content strategy decisions.

---

## Features

### Core Capabilities

- **Cross-Platform Trending Discovery**: Daily scans of the Top 50 works by engagement from all six platforms, pinpointing high-heat content with precision.
- **Intelligent Topic Clustering**: Topics are automatically classified from API-returned tags, with categories fully determined by the day's data — no pre-set keywords needed.
- **Visual HTML Daily Report**: A white-themed page showcasing each work with its color-coded platform badge, cover image, likes/comments/shares, and a direct link.
- **Multi-Dimensional Targeted Queries**: Defaults to all platforms; filter by keyword and platform combinations to flexibly cover any niche.
- **Creative Trend Insights**: Analyzes content styles per platform, cross-platform topic comparisons, and platform differentiation strategies for deeper creative intelligence.
- **One-Click Daily Subscription**: Once enabled, reports are automatically saved to a local folder — no manual steps required.

### Highlights

- ⚡ **Smart Date Detection**: Built-in data update time constant automatically checks whether a target date is in a valid range, preventing wasted queries and credits.
- 🌐 **Platform-Aware Sorting**: WeChat Official Accounts are sorted by read count; all other platforms by likes. Work links come directly from the data source — no manual URL construction needed.
- 🏷️ **Color-Coded Platform Badges**: The HTML report uses distinct badge colors per platform — green for WeChat, black for Douyin, orange for Channels, red for Xiaohongshu, orange for Kuaishou, blue for Bilibili — making platform identification instant.
- 🔒 **Secure by Design**: The API Key is loaded exclusively from environment variables; hardcoding is prohibited, and the data provenance is unique and traceable.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please register at [RedFoxHub](https://redfox.hk?souce=github) to obtain your `REDFOX_API_KEY`.
- Configure the device environment variable `REDFOX_API_KEY` before using this skill.
- Before providing the key, verify its source, scope of use, validity period, and whether it supports reset/revocation.
- Do not hardcode or expose the key in plain text within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Prompt | Result |
|--------|---------------|--------|
| Get latest daily report | "Generate today's content globalization daily report" | Automatically computes the latest available date and generates a Top 50 visual report across all platforms |
| Query a historical date | "Look up the content globalization daily report for June 10" | Directly retrieves trending data for the specified date |
| Search by keyword | "Search for trending works related to brand globalization" | Fuzzy-matches titles and author names, outputs Top 50 works in that direction |
| Filter by platform | "Show only Xiaohongshu and Douyin content globalization hits" | Filters to the specified platforms, focusing on core channels |
| Enable daily subscription | "Turn on my daily content globalization report subscription" | Reports are automatically saved locally — no per-use manual action needed |

### Output Example

After running, you will receive:

- **HTML Visual Daily Report**: A white-themed page with platform-specific sections showing the Top 8 trending works, including cover images, interaction data, color-coded platform badges, and direct links — automatically opens in your browser for preview.
- **Terminal Summary Analysis**: Includes three analysis sections — Data Panorama (six-platform metrics at a glance), Cross-Platform Insight (topic matrix and core observations), and Trend Assessment & Verification (with actionable recommendations).

---

## Use Cases

| Scenario | Role | Sample Prompt | Benefit |
|----------|------|---------------|---------|
| Daily topic inspiration | Content globalization creator | "Today's content globalization trending daily report" | Capture cross-platform traffic trends and boost topic selection accuracy |
| Competitor monitoring | Operations / MCN | "Search for recent brand globalization trending hits" | Track competitor performance and refine strategies in time |
| Content trend analysis | Planner / Data analyst | "Analyze recent content globalization trend shifts over the past week" | Produce structured trend reports to support content strategy decisions |
| Platform differentiation research | Multi-platform creator | "Compare Xiaohongshu vs. Douyin content globalization trending differences" | Discover platform-specific content preferences and tailor creative strategies |

---

## Key Data Notes

- Data is updated daily at **15:00** for the previous day's content.
- Before 15:00, the latest available date is the day before yesterday (T-2); after 15:00, it is yesterday (T-1).
- When the target date has no data, users must be informed and their confirmation must be obtained before invoking the data API.

---
