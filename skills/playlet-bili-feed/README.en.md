# Bilibili Short Drama Info Source / 短剧-B站信息源

---

## Introduction

A Bilibili short drama viral content tracking tool that automatically scans Bilibili short drama creations daily, filters viral works by likes, intelligently clusters themes, and generates visual HTML daily reports with creative trend analysis.

**Core Value**

- 📊 **Daily Viral Rankings**: Automatically scan trending short dramas on Bilibili and precisely filter high-engagement works by likes
- 🏷️ **Intelligent Theme Clustering**: Automatically identify trending theme directions (time-travel / CEO romance / rebirth / suspense, etc.), with daily classifications dynamically determined by content
- 📈 **Creative Trend Analysis**: In-depth analysis of viral title patterns and creator performance to uncover short drama creation patterns
- 📄 **Visual Daily Report**: One-click generation of dark-themed HTML reports with lazy-loaded cover images and BV-number direct links

**Target Users**

- 📝 **Short Drama Creators** — Precisely capture Bilibili short drama traffic trends, use data to guide creative direction and boost content visibility
- 🏢 **MCN Agencies** — Track affiliated creators' short drama performance, optimize operational strategies, and discover rising talent
- 📊 **Content Operators** — Continuously monitor Bilibili short drama trends, make data-driven content decisions, and reduce trial-and-error costs

---

## Features

### Core Features

- **Viral Discovery**: Filter trending content from Bilibili short dramas by likes, precisely targeting high-engagement works
- **Theme Clustering**: Automatically identify theme directions (time-travel / CEO romance / rebirth / suspense / sweet romance / comeback, etc.), with daily classifications dynamically determined by content
- **Smart Querying**: Query all short drama content by default, automatically expand theme batch queries when data is insufficient, efficiently saving API quota
- **Custom Querying**: Support targeted queries by any theme, creator, or keyword for flexible coverage of niche directions
- **Creative Insights**: Analyze viral title patterns, theme trends, and creator performance for deep creative pattern mining
- **Visual Daily Report**: Dark-themed HTML report with card layout, displaying cover images, engagement data, and Bilibili direct links
- **One-Click Subscription**: Enable daily automatic output with `--subscribe`, reports auto-saved to local folder

### Highlights

- ⚡ **Smart Date Detection**: Built-in 15:00 update rule, automatically blocks invalid queries to avoid wasting API quota
- 🎨 **Bilibili-Style Report**: Dark theme + Bilibili blue (#00A1D6), lazy-loaded cover images, BV-number direct link navigation
- 📊 **Zero-Value Hiding**: Engagement metrics at zero are automatically hidden for a cleaner report
- 🔄 **Batch Querying**: All themes retrieved in a single batch API call, avoiding wasteful per-topic requests

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?souce=github) to register an account and obtain your `REDFOX_API_KEY`.
- Configure the device environment variable `REDFOX_API_KEY` before using this skill.
- Before providing your key, verify its source, available scope, validity period, and whether reset/revocation is supported.
- Never hardcode or expose the key in plain text within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Prompt | Result |
|--------|---------------|--------|
| Get latest report | "Check the latest Bilibili short drama daily report" | Automatically determines date availability and generates the latest viral daily report with trend analysis |
| Query historical report | "Check Bilibili short drama data for 2026-06-10" | Generates the short drama viral report for the specified date |
| Targeted theme query | "I want to see time-travel themed Bilibili short drama viral hits" | Precisely queries time-travel theme and outputs same-category viral analysis |
| Multi-theme comparison | "Check the daily report for time-travel and CEO romance short dramas" | Batch queries multiple themes and compares performance across categories |

### Output Example

After report generation, you'll see a structured analysis report in the terminal (theme overview + trend analysis + top creators), while the dark-themed HTML report automatically opens in your browser:

- **Theme Overview**: Summary table of works count, share, and viral highlights per theme
- **Trend Analysis**: Emerging growth signals, viral title pattern features, top creator leaderboard
- **Theme Reports**: Detailed characteristics and creative suggestions for the TOP 3 trending themes
- **HTML Report**: Saved locally at `~/Downloads/QoderReports/`, card layout with clickable titles linking directly to Bilibili videos

---

## Use Cases

| Scenario | Role | Example Prompt | Benefit |
|----------|------|---------------|---------|
| Topic Inspiration | Screenwriter / Director | "What short drama themes are trending on Bilibili lately?" | Understand current trending themes and viral patterns to guide creative direction |
| Content Operations | MCN Operator | "Subscribe me to the Bilibili short drama daily report" | Continuously track category dynamics and discover rising creators |
| Competitive Monitoring | Production Company | "Check the recent viral performance of time-travel themed short dramas" | Analyze competitor viral title patterns and engagement trends to reduce trial-and-error costs |
| Trend Research | Content Strategist | "Compare data between time-travel and CEO romance categories" | Data-driven content investment decisions and identify theme fusion trends |

---

## Important Data Notes

- Data is updated daily at **15:00** for the previous day's data
- Before 15:00, the latest available date is the day before yesterday (T-2); after 15:00, it is yesterday (T-1)
- When querying the latest data, the system automatically skips periods with no data without consuming API quota
- Historical date data is fixed and can be queried directly without confirmation

---
