# Playlet WeChat Official Accounts Feed / playlet-gzh-feed

---

## Overview

Playlet WeChat Official Accounts Feed is a trending content tracking tool designed for short drama creators and content operators. It scans WeChat official account short drama content daily, filters popular works by read count, intelligently clusters by genre direction, and generates a visualized HTML daily report with creative trend analysis.

**Core Value**

- 🔥 Discover trending short drama articles from WeChat official accounts and pinpoint high-engagement works
- 📊 Get genre-clustered popular content at a glance to understand hotspot distribution
- 📈 Analyze trending title patterns and creative trends to uncover traffic strategies
- 🔔 Enable daily subscription for automatic report generation and intelligence system setup

**Target Users**

- ✍️ Short Drama Scriptwriters — Identify genre trends and improve topic selection accuracy
- 📱 Content Operators — Track daily short drama trends from WeChat official accounts and drive content decisions
- 🏢 MCN Agencies — Monitor industry dynamics and manage multi-account content direction
- 📝 Official Account Owners — Discover benchmark accounts and trending content to optimize creative strategies

---

## Features

### Core Features

- **Trending Discovery** — Filter popular short drama content from WeChat official accounts by read count, precisely locating high-engagement works
- **Genre Clustering** — Automatically identify genre directions (Time Travel / CEO Romance / Rebirth / Suspense / Sweet Romance / Comeback / Period Drama / War God / Historical), with daily dynamic genre classification
- **Smart Query** — Query all short drama content by default, automatically expanding genre batch queries when data is insufficient to save API quota
- **Custom Query** — Support targeted queries by genre, official account, or keywords, flexibly covering any short drama niche
- **Creative Insights** — Analyze trending title patterns, genre trends, and official account performance for in-depth creative pattern discovery
- **Visual Daily Report** — Dark-themed HTML report with cover images, engagement data, and direct article links
- **One-Click Subscription** — Automatically generate daily reports saved to local folder after activation

### Highlights

- ⚡ **Batch Query** — Query all genres at once via batch API, efficiently reducing API call count
- 🧠 **Smart Clustering** — Auto-classify into 9 genres with dynamic daily adjustment
- 💾 **Caching** — 1-hour validity to avoid duplicate requests and enable quick result review
- 📅 **Intelligent Date Check** — Automatically validate target date availability to avoid invalid calls

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?souce=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, verify its source, available scope, expiration date, and whether it supports reset/revocation.
- Never hardcode or expose your API key in plain text within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Phrase | Result |
|--------|---------------|--------|
| Latest Report | "Show me today's short drama WeChat report" | Generate the latest visualized daily report |
| Query by Genre | "Short drama articles in the time travel genre", "Show me CEO romance and sweet romance content" | Get trending content in specified genres |
| Query by Time | "What are the short drama trends this month", "Short drama hits in June" | Analyze content trends over a period |
| Historical Review | "Do you have the short drama WeChat report for June 10th" | View trending data for a specific date |
| Combined Query | "Time travel genre short dramas in June" | Precisely locate specific genre + time range |
| Subscription | "Enable daily short drama report subscription" | Auto-generate and save daily reports |
| Quick Cache View | "Show me the last short drama results from cache" | Quick view without API call within 1 hour |

### Sample Output

After generating the report, the terminal outputs a genre classification table and creative trend analysis report, while a dark-themed HTML visual report is generated and automatically opened in the browser. The HTML report includes:

- Genre card layout clearly showing genre distribution
- Each article displays cover image, title, official account name, read count, likes, and shares
- Statistics panel: genre count, article count, average reads, total reads

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|--------------|---------|
| Topic Research | Scriptwriter | "What short drama genres are trending lately? Analyze time travel and rebirth for me" | Identify genre trends and improve topic selection accuracy |
| Report Tracking | Content Operator / MCN | "Enable daily report subscription to track WeChat short drama trends for me" | Build a team intelligence system and drive content decisions |
| Competitor Analysis | Brand Manager / Ad Manager | "Show me CEO romance short drama performance on WeChat in June" | Adjust promotion strategies and optimize content differentiation |
| Trend Review | Content Director / Data Analyst | "Compare this month's and last month's short drama trend changes" | Master mid-to-long-term trends and guide content strategy planning |
