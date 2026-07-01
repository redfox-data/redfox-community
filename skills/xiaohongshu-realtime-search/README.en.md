# Xiaohongshu Latest Hot Notes / xiaohongshu-realtime-search

---

## Overview

Enter a keyword and instantly find popular Xiaohongshu notes. Filter freely by sorting, time range, and note type. See title, author, likes, comments, shares, and collections at a glance, with one-click links to the original notes.

**Key Benefits**

- **Always Fresh**: Every search pulls the latest platform data — no stale cache.
- **Flexible Filtering**: Combine sorting (comprehensive / latest / most liked / most commented / most collected), time range (unlimited / 1 day / 1 week / 1 month / 1 year), and note type (all / video / text).
- **Full Pagination**: Browse through results page by page when there are many results.
- **Publish Date at a Glance**: Each note shows its publish date (YYYY-MM-DD), making it easy to assess content freshness.

**Who Is This For**

- 🔍 **Content Creators** — Find trending notes in your niche and study what's working.
- 📊 **Marketing / Data Analysts** — Quickly map out what's hot in any category on Xiaohongshu.
- 🏢 **Brands / MCNs** — Discover and evaluate potential influencer partners by engagement.
- 🛒 **E-commerce** — Search for product promotion notes in niche markets.

---

## Features

### Core Capabilities

- **Keyword Search**: Search Xiaohongshu notes by any keyword.
- **Multi-dimensional Sorting**: Comprehensive / Latest / Most liked / Most commented / Most collected — discover content by different dimensions.
- **Time Filtering**: Unlimited / 1 day / 1 week / 1 month / 1 year time ranges.
- **Type Filtering**: All / Video / Text note types for precise filtering.
- **Pagination**: Browse multiple results per page with multi-page support.
- **Subscription Push**: Subscribe to keywords for daily automated updates.

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
| Search by category | "Search A-stocks" / "Find office outfit notes" | Searches with default sorting (most liked) and time range (1 month) |
| Specify sort order | "Search weight loss meals by latest published" | Switches to latest-published sorting |
| Specify time range | "Search AIGC content from the past week" | Sets time filter to 1 week |
| Specify note type | "Search for video notes" | Only shows video-type notes |
| Combined filters | "Search fitness by most commented, 1 week, video" | Applies sort, time, and type filters |
| Browse next page | Reply "next page" after results | Auto-increments page offset, no duplicates |
| Subscribe daily | "Confirm subscription" | Creates a scheduled task to push results daily at 09:00 AM |

### Example Output

After searching, you'll see a table like this:

> 📊 Keyword "**A-stocks**" — **9 notes** found (Sort: Most liked | Time: Last 1 month | Type: All | Page 1):

| # | Title | Author | Publish Date | Likes | Comments | Collections |
|---|-------|--------|-------------|-------|----------|-------------|
| 1 | [A-stocks surge! These three stocks...](link) | 财经小能手 | 2026-06-30 | 1.2w | 305 | 8.7w |
| 2 | [Beginner's guide to A-stocks...](link) | 投资成长记 | 2026-06-30 | 8.5k | 120 | 4.5w |

> 📄 Page **1**. Reply "next page" to continue browsing.

(Pagination hint and filter switching guide at the bottom.)

---

## Use Cases

| Scenario | Role | Example | Benefit |
| -------- | ---- | ------- | ------- |
| Niche reconnaissance | Content operator | "Show me the latest office outfit notes" | Instantly understand what competitors are publishing |
| Trend-driven ideation | Creator | "Most liked weight loss meal notes in the past week" | Find high-engagement directions to ride the wave |
| Influencer discovery | MCN / Brand | "Latest makeup video notes from the past month" | Evaluate notes by engagement for campaign decisions |
| Keyword monitoring | Brand operator | "Subscribe to daily push for [brand keyword]" | Receive automatic daily updates for timely response |
