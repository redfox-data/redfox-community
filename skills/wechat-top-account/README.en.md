# WeChat Top Account Rankings / wechat-top-account

---

## Introduction

Instantly retrieve the TOP50 WeChat Official Account rankings by overall performance, with support for daily/weekly/monthly views and filtering across 23 vertical categories. Displays composite scores and detailed engagement metrics, with HTML visual report export and scheduled push subscriptions.

**Core Value**

- Covers 23 vertical categories with day/week/month ranking tiers, capturing the competitive landscape at a glance
- Composite scores are calculated from reads, likes, "Top Reads", and forwards — objective and quantifiable
- Beyond rankings, get three deep-dive analysis perspectives: content ecosystem, viral impact, and blue-ocean tracks

**Who It's For**

- 📱 WeChat account operators — understand top account output and engagement in your category, identify benchmarks
- 🏢 Brand marketing teams — track competitor ranking changes and adjust content strategy in time
- 📊 MCN agencies — subscribe to scheduled pushes and export visual reports for reviews and client presentations

---

## Features

### Core Capabilities

- **Multi-dimension rankings**: Query TOP50 across 23 categories by day, week, or month; keyword input auto-matches category
- **Composite scoring system**: Score calculated from reads, likes, "Top Reads", and forwards on a 100-point scale
- **Deep-dive analysis**: Three analytical perspectives — content ecosystem changes, viral impact quantification, blue-ocean track discovery
- **HTML visual reports**: Generate visual ranking pages exportable as images or PDF
- **Scheduled subscriptions**: Subscribe to daily/weekly/monthly rankings for automatic delivery at update time

### Highlights

- Daily rankings refresh at 17:30 every day, weekly every Monday at 17:30, monthly on the 3rd at 23:00 — always up to date
- Ranking tables and HTML reports share the same data source, ensuring full consistency
- Daily data available for the past 7 days, weekly for 3 weeks, monthly for 3 months; out-of-range queries auto-adjust with a notice

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?souce=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before using a key, confirm its source, scope, expiry, and whether it supports reset or revocation.
- Never hard-code or expose the key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
| ------ | -------------- | ------ |
| Query category daily rankings | `Show me the tech category daily rankings` | Outputs Tech & Digital daily TOP50 with composite scores and engagement metrics |
| Query category weekly rankings | `Top WeChat accounts in food this week` | Outputs Food & Dining weekly TOP50 with data period labeled |
| Get deep-dive analysis | Reply `1` after rankings are output | Outputs content ecosystem, viral impact, and blue-ocean track analysis based on TOP50 data |
| Generate HTML report | Reply `2` after rankings are output | Generates a visual rankings page exportable as image or PDF |
| Subscribe to scheduled push | `Subscribe to weekly rankings` | Automatically delivers the latest rankings at the corresponding update time |
| List all categories | `What categories are available?` | Lists all 23 available vertical categories |

### Output Example

Rankings are output directly as a table with columns for rank, account name (clickable), composite score, article count, total reads, lead article reads, highest reads, total likes, total "Top Reads", and total forwards. A feature prompt follows for selecting analysis, reports, or subscriptions.

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| -------- | ---- | ---------------- | ------- |
| Daily operations reference | Account operator | `Show this week's education category rankings` | Compare top account publish frequency and engagement rates to refine topics and cadence |
| Competitor tracking | Brand marketing manager | `Subscribe to finance weekly rankings` | Stay on top of competitor ranking shifts and content moves |
| Track assessment | Content entrepreneur | `Pull monthly rankings for a few candidate categories` | Compare account count and average scores to find low-competition, high-demand niches |
| Data reporting | MCN agency | `Generate an HTML report for the tech daily rankings` | Export visual charts to boost efficiency of internal reviews and client presentations |
