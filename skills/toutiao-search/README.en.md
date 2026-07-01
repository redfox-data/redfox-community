# Toutiao Trending Content Search / toutiao-search

---

## Overview

Enter a keyword and instantly find the latest Toutiao works. Sort by view count or publish time, filter by recent hours, and see all the key data at a glance — only fresh platform content, no stale cache.

**Key Benefits**

- **Always Fresh**: Every search pulls the latest platform content — only freshly published works, no stale cache.
- **Flexible Filtering**: Sort by view count or publish time, and filter by recent hours to narrow your search window.
- **Articles & Videos Covered**: Search both articles and videos in one go, with a dedicated mode to find video hits exclusively.
- **Full Pagination**: Browse through results page by page when there are many results — nothing gets missed.
- **Rich Data at a Glance**: Views, likes, comments, and reposts displayed clearly, with auto-generated CSV and interactive HTML reports ready to download.

**Who Is This For**

- 🔍 **Content Creators** — Stay on top of trending topics and hot content in your niche on Toutiao for creative inspiration.
- 📊 **Marketing / Data Analysts** — Track keyword performance and content trends across the Toutiao platform.
- 🏢 **Brands / MCNs** — Monitor competitor and industry keyword coverage, supporting strategic decisions.

---

## Features

### Core Capabilities

- **Keyword Search**: Search Toutiao's latest trending works by any keyword.
- **Dual Sort Options**: Sort by view count (`views`) or publish time (`time`) in descending order — quickly find high-performing or fresh content.
- **Time Filtering**: `--hours N` limits results to the last N hours, rejecting stale data.
- **Video-Only Mode**: `--video-only` returns only video works for targeted video hit discovery.
- **Pagination**: `--pages N` controls page count, ~10 results per page, 3 pages by default.
- **Terminal Table Output**: Title, author, views, likes, comments, reposts, publish date, and content type at a glance.
- **CSV Auto-Export**: UTF-8 BOM encoded CSV, opens directly in Excel without encoding issues.
- **Interactive HTML Report**: Dark theme, article/video labels, clickable work cards linking to originals, with in-page search.

---

## API Key Setup

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFox Hub](https://redfox.hk/settings/api-keys?source=github).
- Register at [RedFox Hub](https://redfox.hk?source=github) to obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable before using this skill.
- Verify the key's source, scope, validity period, and reset/revoke options before use.
- Never hardcode or expose the key in code, prompts, logs, or output files.

---

## How to Use

Just describe what kind of content you're looking for in natural language.

### Quick Reference

| Intent | Example | Result |
| ------ | ------- | ------ |
| Search by topic | "Search Toutiao for AI content" | Searches with default sorting (by views) and displays results |
| Specify sort order | "Search for LLM works by latest published" | Switches to publish-time sorting |
| Set time range | "Search new energy works from the last 24 hours" | Sets `--hours 24`, returns only recent content |
| Video only | "Search for product review videos" | Enables `--video-only`, returns only video works |
| Browse more pages | "Show more results" / "Next pages" | Increases `--pages` to fetch more data |
| Export data | "Export CSV" / "Generate HTML report" | Auto-generates CSV and interactive HTML report |

### Example Output

After searching, you'll see a table like this:

> 📊 Keyword "**AI**" — **30 works** found (Sort: By views | Time: Unlimited | Pages 1-3):

| # | Title | Author | Views | Likes | Comments | Reposts | Publish Date | Type |
|---|-------|--------|-------|-------|----------|---------|-------------|------|
| 1 | [Trending article title truncated to 30 chars...](link) | Author Name | 12w | 3.2k | 412 | 89 | 2026-06-30 14:30 | Article |
| 2 | [Another hot video title displayed...](link) | Another Author | 8.5w | 1.5k | 230 | 56 | 2026-06-30 12:00 | Video |

> 📄 CSV and HTML report saved to `~/Downloads/QoderToutiaoSearch/`.

(Data displayed as a terminal table, with CSV and HTML auto-saved simultaneously.)

---

## Use Cases

| Scenario | Role | Example | Benefit |
| -------- | ---- | ------- | ------- |
| Hot topic tracking | Content creator | "Search Toutiao for AI content" | Instantly grasp the latest topic trends on Toutiao |
| Viral content analysis | Marketing / Data | "Search LLM, sort by views" | Quickly find high-view hits and study viral patterns |
| Competitor monitoring | Brand operator | "Search brand keyword from the last 24 hours" | Track competitor coverage and performance on Toutiao |
| Content ideation | Creator | "Search new energy, export CSV for analysis" | Batch-collect data to discover content angles |
| Video discovery | MCN | "Search reviews, video only" | Precisely find video hits and evaluate content direction |
