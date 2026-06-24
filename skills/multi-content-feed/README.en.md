# Content Export Information Source / multi-content-feed

---

## Overview

The Content Export Information Source is a cross-platform content export viral tracker that scans six major platforms daily — WeChat Official Accounts, Douyin, WeChat Channels, Xiaohongshu, Kuaishou, and Bilibili — for content export viral hits. It selects the Top 50 by engagement, intelligently clusters topics, and generates a visual daily report with platform tags, cover images, engagement data, and creative insights.

**Core Value**

- 📊 **One-Stop Cross-Platform Coverage**: Monitor all six platforms simultaneously — WeChat Official Accounts, Douyin, WeChat Channels, Xiaohongshu, Kuaishou, and Bilibili — no need to check each individually
- 🏷️ **Smart Topic Clustering**: Automatically categorizes topics based on data, dynamically reflecting the day's trending distribution — no manual keyword predefinition required
- 📈 **In-Depth Creative Insights**: Beyond listing viral hits, provides cross-platform variance analysis, trend predictions, and actionable recommendations
- 🎨 **Visual Daily Report**: White-themed HTML report with color-coded platform tags, cover images, and engagement data at a glance

**Target Users**

- 🎬 Content Export Creators — Pinpoint cross-platform traffic trends and improve content hit rates
- 📊 Content Export Operations / MCNs — Track competitor performance and stay on top of industry dynamics
- 📋 Content Strategists / Data Analysts — Produce structured trend reports to support content strategy decisions

---

## Features

### Core Features

- Cross-Platform Viral Discovery: Retrieve Top 50 works ranked by engagement from WeChat Official Accounts, Douyin, WeChat Channels, Xiaohongshu, Kuaishou, and Bilibili
- Intelligent Topic Clustering: Auto-categorize topics based on work topic fields, with classifications entirely data-driven
- Targeted Search: Flexible query by keyword, platform, or time range
- Visual Daily Report: White-themed HTML with color-coded platform tags, cover images, engagement data, and direct work links
- Creative Insights: Analyze content styles across platforms, cross-platform topic comparisons, and platform-specific strategies
- One-Click Subscription: Enable daily auto-generation with reports accumulating in your local folder

### Highlights

- ⚡ Smart Date Detection: Built-in data update time logic automatically checks target date availability before making requests
- 🌐 Full Platform Adaptation: Six platforms each ranked by read count or engagement; work links ready to use
- 🏷️ Platform Tags: Each work in the report displays a color-coded platform badge for instant source identification
- 🔒 Secure & Reliable: API key accessed via environment variables; hardcoding strictly prohibited

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?souce=github) to register an account and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, please verify its source, scope of use, validity period, and whether it supports reset/revocation.
- Do not hardcode or expose keys in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Phrase | Result |
|--------|---------------|--------|
| Get the latest report | "Generate today's content export daily report" / "Query the latest report" | Auto-fetches the most recent date with data, generates a full-platform report |
| Query by date | "Show the content export daily report for 2026-06-10" | Retrieves viral data for the specified historical date |
| Search by keyword | "Search for brand出海 related viral hits" | Fuzzy matches keywords across all six platforms |
| Filter by platform | "Show only Xiaohongshu and Douyin content export" | Queries only the specified platforms |
| Enable daily delivery | "Subscribe to the content export daily report" | Auto-generates daily reports to your local folder |

### Sample Output

Two parts are generated for each query:

1. **HTML Visual Report**: Includes a platform overview table, Top 8 work cards per platform (cover image + title + author + engagement data), and topic tag clouds — opens automatically in your browser
2. **Terminal Summary Report**: Data panorama table (work counts, engagement distribution, ceiling per platform), cross-platform insights, trend predictions, and action recommendations

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|---------------|---------|
| Creator Topic Inspiration | Content Export Creators | "What topics are trending in content export today?" | Pinpoint cross-platform traffic trends and improve content hit rates |
| Competitive Monitoring | Content Export Operations / MCNs | "Search the latest brand出海 viral hits" | Track competitor activity and optimize your operations strategy |
| Content Trend Analysis | Content Strategists / Data Analysts | "Analyze the weekly cross-platform content export trends" | Produce structured trend reports for content strategy decisions |

---

## Important Data Notes

- **Data Update Time**: Updated daily at 15:00 with the previous day's data
- **Coverage**: Six major platforms — WeChat Official Accounts, Douyin, WeChat Channels, Xiaohongshu, Kuaishou, Bilibili — Top 50 by engagement per platform
- **Sorting Rules**: WeChat Official Accounts sorted by read count; all other platforms sorted by engagement
- **Date Constraint**: Before 15:00, the latest available date is two days prior; after 15:00, it is the previous day. If the target date has no data, you will be prompted for confirmation first
