# B站AI信息源 (Bilibili AI Feed) / bili-ai-feed

---

## Introduction

Automatically scans Bilibili AI-related videos every day, discovers trending content by likes, intelligently clusters topics into a visual HTML daily report, and simultaneously conducts multi-engine AI intelligence investigations on hot topics, delivering structured investigation reports.

**Core Value**

- **Precise Trending Discovery**: Filters high-engagement AI videos from Bilibili, ensuring no important daily AI updates are missed.
- **Auto Topic Clustering**: Intelligently identifies directions such as AI tutorials, large models, and AI art — categories are determined dynamically by the day's content, no manual sorting needed.
- **In-depth Intelligence Investigation**: Automatically performs multi-search-engine cross-validation on hot topics and delivers structured reports with credibility labels.
- **One-click Visualization**: Dark-themed HTML daily report with cover images, engagement data, and video links for a clear overview of daily AI trending content.

**Target Audience**

- 🤖 **AI Content Researchers** — Stay on top of Bilibili AI trends every day without manually browsing videos.
- 📊 **Industry Intelligence Analysts** — Quickly understand AI topic trends and competitor dynamics with multi-engine investigation reports.
- 🎬 **Content Creators / Operators** — Discover trending directions and get data-driven support for content planning.

---

## Features

### Core Capabilities

- **Trending Video Discovery**: Filters high-engagement videos from Bilibili AI-related accounts by likes to pinpoint the day's hot content.
- **Smart Keyword Query**: Defaults to querying "AI"; automatically expands keywords in batch when data is insufficient, saving API quota.
- **Custom Keywords**: Supports user-specified keyword combinations (e.g., "AI art, ComfyUI") for targeted queries in specific niches.
- **Intelligent Topic Clustering**: Automatically identifies and classifies daily trending topic directions; classification is dynamically generated from actual content.
- **AI Intelligence Investigation**: Based on clustered TOP topics, executes four investigation modes — competitor, public sentiment, background check, cross-validation — with multi-engine verification to produce structured reports.
- **Visual HTML Daily Report**: Dark-themed page with cover images, engagement data, and video links; auto-opens preview after generation.
- **Daily Subscription**: Enables automatic daily report generation and cumulative local saving.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?souce=github) to register an account and obtain your `REDFOX_API_KEY`.
- Configure the device environment variable `REDFOX_API_KEY` before using this skill.
- Before providing your key, confirm the key source, scope of use, validity period, and whether reset/revocation is supported.
- Never hard-code or expose the key in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example | Result |
| ------ | ------- | ------ |
| Get latest AI daily report | "Generate today's Bilibili AI daily report" | Automatically retrieves the latest available date and generates the trending report with intelligence investigation |
| View historical report | "Check the Bilibili AI trending content for 2026-06-10" | Fetches the trending video report and topic investigation for the specified date |
| Targeted niche query | "Search for popular Bilibili videos about AI art and ComfyUI" | Queries by custom keywords, clusters results, and generates a focused report |
| Enable daily subscription | "Subscribe to the Bilibili AI daily report, auto-generate every day" | Enables subscription; reports are automatically saved to a local folder |
| Cancel subscription | "Cancel the Bilibili AI daily report subscription" | Disables daily automatic subscription |

### Output Example

After the report is generated, you will receive a structured conversation report, roughly as follows (illustrative):

**Bilibili AI Feed · 2026-06-10 Daily Report**

Scanned 200 trending videos, clustered into 5 categories

**Category Overview**

| Category | Count | Share | Highlight |
|----------|-------|-------|-----------|
| #Large Models | 68 | 34% | A video with 10k+ likes discussing new model capabilities |
| #AI Tutorials | 52 | 26% | Beginner series with steadily climbing views |

Also includes AI intelligence investigation reports for each TOP topic, with multi-engine verification conclusions and credibility labels.

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Daily AI trending tracking | AI researcher / operator | "Generate today's Bilibili AI daily report" | Quickly grasp the day's Bilibili AI trending content and dynamics |
| Competitor & topic intelligence | Industry analyst | "Check recent Bilibili trending content about large models and do an intelligence analysis" | Get structured competitor/topic reports with multi-engine cross-validation |
| Niche content discovery | Content creator | "Find popular Bilibili videos in the AI art direction recently" | Discover high-engagement content by keyword to support content planning |
| Historical data review | Content operator | "Check the Bilibili AI video trends from last Wednesday" | Review historical reports to analyze content trend changes |

---
