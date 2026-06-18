# Short Drama - Douyin Feed / playlet-douyin-feed

---

## Overview

Short Drama - Douyin Feed is a Douyin trending content tracking tool designed for short drama creators and MCN operators. It automatically scans Douyin short drama content daily, filters trending works by likes, intelligently clusters them by genre, and generates an HTML visual report with cover images, engagement data, and creative insights.

**Core Value**

- **Daily Auto Tracking**: Data updates automatically at 15:00 each day for the previous day's content. Subscribe once and get hands-free daily reports at zero cost.
- **Smart Genre Clustering**: Built-in 6-genre keyword library (Time Travel / CEO Romance / Rebirth / Suspense / Sweet Romance / Comeback) with automatic classification of trending directions.
- **In-depth Creative Insights**: Automatically analyzes trending title patterns, top creator rankings, and emerging growth signals to support content decisions.
- **Visual Daily Report**: Dark-themed HTML report with cover images, engagement data, and direct links to works — clean and intuitive.

**Target Users**

- 🎬 **Short Drama Creators** — Track trending genres and title patterns daily to capture traffic opportunities.
- 🏢 **MCN Operators** — Monitor creator and competitor performance to improve operational efficiency.
- 📊 **Content Analysts** — Systematically analyze genre distribution and trend shifts for data-driven decisions.

---

## Features

### Core Features

- **Trend Discovery**: Scans Douyin short drama content daily, filtering popular works by likes to pinpoint high-engagement content.
- **Genre Clustering**: Intelligently identifies genres such as Time Travel, CEO Romance, Rebirth, Suspense, Sweet Romance, Comeback — classifications dynamically determined by daily content.
- **Smart Query**: Supports targeted queries by genre, creator, and keywords. Auto-expands genre scope with batch queries when data is insufficient, saving API credits.
- **Custom Query**: Specify any genre combination for targeted retrieval, flexibly covering niche short drama directions.
- **Creative Insights**: Analyzes trending title patterns, genre trends, and creator performance for deep creative pattern mining.
- **Visual Daily Report**: Dark-themed HTML report with cover images, engagement data, and direct links — auto-opens in browser.
- **One-Click Subscription**: Enable daily automatic report generation, saved locally to your folder.

### Highlights

- ⚡ **Daily Auto Update**: Previous day's data updates automatically at 15:00 — no manual effort after subscribing.
- 🏷️ **Smart Genre Clustering**: Built-in 6-genre keyword library with auto classification and dynamic expansion support.
- 📊 **Creative Trend Report**: Automatically analyzes emerging growth signals, trending title patterns, and top creator rankings.
- 🎨 **Dark-Themed HTML Report**: Cover images + engagement data + direct links — clean, intuitive, and auto-opened in browser.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please sign up at [RedFoxHub](https://redfox.hk?souce=github) to obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing an API key, verify its source, applicable scope, validity period, and whether it supports reset/revocation.
- Never hardcode or expose API keys in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Phrase | Result |
|--------|---------------|--------|
| Daily Report | "Show me today's short drama Douyin report" | Auto-checks data availability and generates the latest report |
| By Genre | "Search for time travel short dramas" | Targeted retrieval of time travel trending works with a themed report |
| Historical Date | "Show me the short drama report for June 10th" | Directly generates the report for the specified historical date |
| Multi-Genre | "Search for time travel and CEO romance short dramas" | Batch queries multiple genres with automatic deduplication |
| Trend Analysis | "What are this month's short drama trends?" | Monthly genre distribution and growth trend analysis |
| Subscribe | "Enable daily short drama report subscription for me" | Daily automatic report generation with no manual effort |

### Output Example

Each report provides:

- 📄 **HTML Visual Report**: Dark-themed, includes cover images, engagement data, and direct links — auto-opens in browser.
- 📊 **Genre Overview Table**: Work counts, percentages, and trending highlights per genre.
- 🔍 **Creative Trend Analysis**: Emerging growth signals, trending title patterns, and top creator rankings.
- 💡 **Cross-Genre Recommendations**: Genre fusion trends and collaborative creative suggestions.

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|--------------|---------|
| Topic Inspiration | Screenwriter / Director | "What genres are trending today? Analyze trending titles for me" | Capture traffic opportunities and boost hit probability |
| Operations Management | MCN Operations Director | "Who are the top creators in the time travel genre this week? How are they performing?" | Improve operational efficiency and catch market shifts |
| Trend Research | Content Analyst | "Compare engagement trends between time travel and CEO romance this month" | Form data-driven trend judgments to support decisions |
| Daily Tracking | Short Drama Enthusiast | "Enable daily subscription for me" | Track industry trends effortlessly at zero cost |

---

## Data Notes

- **Update Schedule**: Data updates daily at 15:00 for the previous day's content. Before 15:00, the latest available data is from two days ago; after 15:00, it is from yesterday.
- **Data Source**: RedFoxHub Douyin short drama content API
- **Platform Scope**: Fixed to Douyin platform short drama content only
- **Cache Policy**: Query results within 1 hour can be reused from cache to save API credits
