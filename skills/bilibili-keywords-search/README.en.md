# B站关键词实时搜索 / B站关键词实时搜索

---

## Overview

Real-time Bilibili keyword search tool that queries the latest Bilibili videos via API based on your keywords, with sorting and time range filters, returning non-cached real-time data.

**Core Value**

- **Real-time Data**: Each search calls the live API, returning the latest published videos — no cached or historical data.
- **Flexible Multi-dimensional Filtering**: Supports three sorting modes (comprehensive / newest / most liked) and four time ranges (7 / 30 / 90 days / unlimited), combinable as needed.
- **Smart Keyword Expansion**: When no results are found, automatically generates 10 related expansion keywords to help you break through search bottlenecks.
- **Paginated Browsing + Subscription Push**: Browse large result sets page by page, and subscribe to keywords for daily automatic delivery of the latest videos.

**Target Audience**

- 🔍 **Bilibili Creators** — Quickly grasp the latest trends and hot topics in your niche for content inspiration.
- 📊 **Operations / Data Analysts** — Track real-time dynamics of keyword-related content and monitor data changes.
- 🏢 **Brands / MCNs** — Monitor competitors and industry keywords for the latest video performance to support strategic decisions.



## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?souce=github) to register an account and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, please verify its source, available scope, validity period, and whether it supports reset/revocation.
- Never hardcode or expose the key in plain text within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent               | Example Phrase                                               | Result                                                 |
| -------------------- | ------------------------------------------------------------ | ------------------------------------------------------ |
| Real-time Search     | "Search Bilibili for the latest videos about AI art"        | Performs real-time keyword search, returns latest video list |
| Switch Sorting       | "Re-search by newest first"                                  | Switches to newest-first sorting to see recent uploads |
| Adjust Time Range    | "Show results from the last 30 days"                         | Adjusts time range to the last 30 days                 |
| Paginate             | "Next page"                                                  | Views the next page of search results                  |
| Subscribe to Keyword | "Confirm subscription"                                       | Creates a daily scheduled push task                    |

### Output Example

After the search completes, you will receive a complete video information table, roughly as follows:

| # | Video Title | Creator | Plays | Likes | Comments | Favorites |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | [Example Title](https://www.bilibili.com/…) | CreatorA | 10.5k | 3.2k | 8.5k | 1.8k |
| 2 | [Example Title](https://www.bilibili.com/…) | CreatorB | 8.1k | 2.1k | 5.2k | 9.6k |

The table is followed by filter switching tips and pagination guidance for quick parameter adjustments.

---

## Use Cases

| Scenario               | Role                | Example Query                                                       | Benefit                                              |
| ---------------------- | ------------------- | ------------------------------------------------------------------- | ---------------------------------------------------- |
| Trending Topic Tracking| Bilibili Creator    | "Search Bilibili for the latest AI art videos from the last 7 days"| Quickly grasp hot content in your niche for inspiration |
| Competitor Monitoring  | Brand / Operations  | "Search Bilibili for sunscreen reviews from the last 30 days, sorted by likes" | Track competitor content performance, adjust strategies |
| Topic Research         | Content Planner     | "Search Bilibili for Python tutorials without time limit"          | Understand the full landscape of a keyword to support topic decisions |
| Daily News Subscription| Data Analyst       | "Subscribe to tech frontier daily push"                            | Automatically receive the latest daily content without manual searching |

---
