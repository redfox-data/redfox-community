# Xiaohongshu Content Crawler / xiaohongshu-crawler

---

## Introduction

Crawl trending Xiaohongshu (Little Red Book) posts by keyword, with date range filtering and multiple sorting options. Returns note titles, authors, engagement metrics, and more in a structured table format. Also supports CSV and HTML visual report export for offline viewing and sharing.

**Core Value**

- **Precise content discovery**: Triple filtering by keyword, date range, and sorting to quickly find high-engagement notes.
- **Smart intent understanding**: Automatically recommends sub-categories when broad terms are used; queries site-wide trending when no keyword is provided.
- **Tiered display strategy**: Shows top 20 with pagination when data is sufficient; provides expansion suggestions when results are few; recommends related searches and trending notes when no results found.
- **One-click report export**: Supports Excel (CSV) and HTML visual reports, viewable directly in your browser.

**Ideal For**

- 📝 **Xiaohongshu Creators** — Crawl similar trending posts by topic keyword for content inspiration.
- 🛍️ **Brand / E-commerce Teams** — Competitive content research to understand trending notes and engagement in specific categories.
- 🏢 **MCN / Content Planners** — Cross-category batch crawling to plan creator matrix content direction.

---

## Features

### Core Capabilities

- **Keyword search**: Supports exact keywords, multi-keyword combinations (comma-separated), and site-wide trending queries (empty keyword).
- **Date range filtering**: Supports absolute dates, relative dates (e.g., "last 7 days"), and date ranges. Defaults to the last 30 days.
- **Multiple sorting options**: Relevance (default), Latest (by publish time), and Hottest (by engagement) — switch flexibly as needed.
- **Keyword generalization detection**: When broad terms are entered (e.g., "food", "fashion"), recommends 10 sub-categories for your selection before searching.
- **Tiered result display**: ≥ 20 results shows top 20 + pagination prompt; 1-19 results shows all + expansion suggestions; 0 results shows related searches + trending notes + trending categories.
- **Report export**: One-click generation of CSV (Excel compatible) and HTML visual reports.
- **Complete engagement data**: Each post returns saves, shares, comments, likes, publish time, and more.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing your key, verify its source, scope, validity period, and whether it supports reset/revocation.
- Never hardcode or expose your key in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe what you want to search for in natural language — no need to memorize specific commands.

### Common Phrases

| Intent | Example | Result |
| ------ | ------- | ------ |
| Search by keyword | "Crawl trending weight-loss meal posts from the past week" | Returns results sorted by relevance with keyword + last 7 days |
| Sort by popularity | "Show me the hottest fashion posts" | Sorted by engagement, highest interaction notes first |
| Broad term refinement | "Crawl food-related posts" | Recommends 10 sub-categories first, searches after your confirmation |
| Site-wide trending | "What's trending on Xiaohongshu lately" | Queries site-wide popular content with empty keyword |
| Specify date range | "Crawl skincare posts from May 20 to June 1" | Precise filtering by specified date range |
| Download reports | "Download Excel and HTML reports" | Generates CSV + HTML visual report files |

### Output Example

After a query, you'll receive a structured table like this (illustrative):

| # | Note Title | Author | Saves | Shares | Comments | Likes | Publish Time |
|---|-----------|--------|-------|--------|----------|-------|-------------|
| 1 | [Weekly Meal Prep Recipes](https://www.xiaohongshu.com/explore/xxx) | Healthy Food Expert | 1.2w | 3500 | 800 | 5.6w | 06-02 19:55 |
| 2 | [Office Worker Bento Collection](https://www.xiaohongshu.com/explore/xxx) | Foodie Worker | 8500 | 2100 | 320 | 3.2w | 06-01 12:30 |

---

## Use Cases

| Scenario | Role | Example Prompt | Benefit |
| -------- | ---- | -------------- | ------- |
| Topic research | Xiaohongshu creator | "Crawl trending petite fashion posts from the past week" | Understand content direction and engagement patterns in your niche |
| Competitive analysis | Brand operations | "Crawl sunscreen-related notes from the last 30 days, sorted by popularity" | Gain insights into category trends and user interests |
| Category exploration | MCN planner | "Show me what's trending in the food category recently" | Refine sub-categories first, then crawl for precise content opportunities |
| Data archiving | Content operations | "Download the HTML visual report after crawling" | Offline access to complete data for team sharing and review |

---
