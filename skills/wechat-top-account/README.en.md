# WeChat Top Accounts / wechat-top-account

---

## Introduction

Quickly access the WeChat Official Account comprehensive ranking TOP 50, helping operators and brands understand the reading and engagement data of top accounts in their niche — supporting operational benchmarking and competitor tracking.

**Core Value**

- Covers TOP 50 rankings across 23 vertical categories, with flexible switching between daily, weekly, and monthly charts
- A comprehensive scoring system based on multiple metrics including reads, likes, in-views, and shares, with a maximum score of 100
- Automatically outputs three types of in-depth analysis: content ecosystem shifts, hot topic impact, and blue-ocean niche discovery
- One-click generation of a visual report page with image and PDF export support
- Subscribe to daily, weekly, or monthly rankings for automated delivery on each update

**Who It's For**

- 📱 **WeChat Official Account Operators** — Understand top account performance in your niche to optimize topic selection and publishing cadence
- 🏢 **MCN Operations Teams** — Monitor the competitive landscape across managed accounts and generate regular data reports
- 🏷️ **Brand Marketing Managers** — Track competitor account rankings and engagement shifts to adjust content strategy
- 🚀 **Content Entrepreneurs** — Evaluate competition levels and reading demand across candidate niches to identify blue-ocean opportunities

---

## Features

### Core Functions

- **Multi-Dimensional Ranking Query**: Query TOP 50 across 23 categories by daily, weekly, or monthly chart — keywords automatically match the right category
- **Comprehensive Scoring System**: A composite score (max 100) based on post count, reads, likes, in-views, shares, and more
- **In-Depth Analysis**: Three analytical perspectives: content ecosystem changes, hot topic impact quantification, and blue-ocean niche discovery
- **Visual Report Export**: One-click generation of a visual ranking page with image and PDF export support
- **Scheduled Subscription Push**: Subscribe to daily, weekly, or monthly rankings for automatic delivery on each update cycle

### Highlights

- **Scheduled Updates**: Daily chart refreshes at 17:30, weekly chart every Monday at 17:30, monthly chart on the 3rd at 23:00
- **Controlled Lookback**: Daily charts span the past 7 days, weekly the past 3 weeks, monthly the past 3 months — out-of-range requests auto-adjust with a prompt
- **Data Consistency**: The ranking table and visual report share the same data source, with identical order and content
- **On-Demand Expansion**: The ranking table outputs directly without confirmation; analysis, reports, and subscriptions are user-initiated

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register an account at [RedFoxHub](https://redfox.hk?source=github) to obtain your `REDFOX_API_KEY`.
- Configure the device environment variable `REDFOX_API_KEY` before using this skill.
- Before providing a key, confirm its source, scope, expiration, and whether it supports reset/revocation.
- Never hardcode or expose the key in plaintext in code, prompts, logs, or output files.

---

## Usage Guide

Just describe your need in plain language — no commands to memorize.

### Quick Reference

| Intent                          | Example Phrase                         | Result                                                                                   |
| ------------------------------- | -------------------------------------- | ---------------------------------------------------------------------------------------- |
| Query daily chart by category   | "Show the tech category daily ranking" | Outputs the Tech & Digital daily TOP 50 with composite scores and engagement metrics     |
| Query weekly chart by category  | "This week's food category ranking"    | Outputs the Food & Dining weekly TOP 50 with time range noted                            |
| Query monthly chart by category | "Finance category monthly ranking"     | Outputs the Finance monthly TOP 50                                                       |
| Get in-depth analysis           | (After chart output) reply "1"         | Outputs three analysis types: content ecosystem, hot topic impact, and blue-ocean niches |
| Generate visual report          | (After chart output) reply "2"         | Generates a visual page exportable as image or PDF                                       |
| Subscribe to updates            | "Subscribe to weekly ranking"          | Sets up automated weekly delivery of the latest chart                                    |
| Subscribe to all                | "Subscribe to all"                     | Enables daily, weekly, and monthly chart subscriptions at once                           |

### Sample Output

After querying "Tech category daily ranking", you will receive:

1. **Ranking Table**: Rank, account name (clickable), composite score, post count, total reads, headline reads, peak reads, total likes, total in-views, total shares
2. **Extension Prompt**: Reply "1" for in-depth analysis, "2" for a visual report, "3" or say "Subscribe to daily/weekly/monthly" to enable scheduled delivery

---

## Use Cases

| Scenario                   | Role                    | Example Query                              | Benefit                                                                                |
| -------------------------- | ----------------------- | ------------------------------------------ | -------------------------------------------------------------------------------------- |
| Daily operations reference | Account Operator        | "Show tech category daily ranking"         | Compare posting frequency and engagement rates to benchmark and optimize topic cadence |
| Competitor tracking        | Brand Marketing Manager | "This week's FMCG category ranking"        | Track competitor ranking shifts and content direction to adjust your own strategy      |
| Niche evaluation           | Content Entrepreneur    | "Compare food and travel monthly rankings" | Assess competition levels across candidate niches and pick a blue-ocean direction      |
| Regular data reporting     | MCN Operations          | "Subscribe to monthly ranking"             | Export monthly visual reports with consistent and traceable data                       |

---

## Key Data Notes

| Chart   | Update Time                | Data Range                       |
| ------- | -------------------------- | -------------------------------- |
| Daily   | Every day at 17:30         | Yesterday's data, past 7 days    |
| Weekly  | Every Monday at 17:30      | Last week's data, past 3 weeks   |
| Monthly | 3rd of each month at 23:00 | Last month's data, past 3 months |

Covers 23 vertical categories, including Overall, Tech & Digital, Food & Dining, Finance, Education, Fashion, Health & Wellness, Emotional & Psychology, Career Development, and more. Just enter a keyword to automatically match the right category.
