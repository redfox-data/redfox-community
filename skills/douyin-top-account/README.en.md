# Douyin-Top-Account

---

## Overview

Quickly discover the most influential accounts on Douyin and stay on top of niche trends.

**Core Value**

Based on daily TOP 50 account data across all Douyin niches — covering follower growth, engagement, and growth trends — this tool helps you tackle four key challenges: content topic decisions, benchmark account discovery, competitor monitoring, and niche selection.

**Intended Users**

- 🎬 Content creators — understand top account performance in your niche, find benchmarks to learn from
- 🏢 Brand owners / ad placement teams — efficiently shortlist quality influencers and evaluate partnership value
- 📦 MCN agencies / content teams — track competitor dynamics and develop operational strategies
- 📊 Industry analysts — obtain data insights and generate analysis reports

---

## Features

### Core Capabilities

- **Ranking queries**: query daily, weekly, and monthly TOP 50 Douyin accounts; default display is TOP 20
- **Niche filtering**: supports all-category trending or precise queries across 27 content niches, with fuzzy keyword matching
- **Composite scoring**: weighted calculation based on total followers, new follower growth, and new likes/shares/comments; multi-dimensional, objective ranking out of 100
- **HTML report generation**: generates a visually styled HTML file with clickable account names linking to Douyin profiles; supports export as image or PDF
- **Subscription push**: set up scheduled auto-delivery for daily, weekly, or monthly rankings; supports niche-specific subscriptions

---

## API key source and security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [Redfox Hub](https://redfox.hk/dashboard/keys?souce=github) (`https://redfox.hk`) for API authentication.
- Before providing the key, confirm its source, available scope, validity period, and whether reset/revocation is supported.
- Do not hard-code or expose the key in plaintext within code, prompts, logs, or output files.

---

## Prerequisites

### Register a Redfox Hub account to obtain REDFOX_API_KEY

- Get REDFOX_API_KEY (apply at [Redfox Hub](https://redfox.hk/dashboard/keys?souce=github))

### Environment variables

| Variable         | Required | Notes          |
| ---------------- | -------- | -------------- |
| `REDFOX_API_KEY` | Yes      | API access key |

**macOS (zsh)**

Append one line to the end of `~/.zshrc` (replace the value in quotes with your key):

```bash
export REDFOX_API_KEY="your_api_key_here"
```

Then run:

```bash
source ~/.zshrc
```

**Windows (PowerShell)**

- **Current terminal only**: Takes effect immediately after run, **no other commands needed**; lost when the window is closed.

```powershell
$env:REDFOX_API_KEY = "your_api_key_here"
```

- **Persist to user environment**: After running `setx`, the **current PowerShell window still won't have the variable**; you need to **close and reopen** the terminal (or restart Cursor / VS Code, etc.) for the new window to read `REDFOX_API_KEY`.

```powershell
setx REDFOX_API_KEY "your_api_key_here"
```

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent               | Example phrase                                        | Result                             |
| -------------------- | ----------------------------------------------------- | ---------------------------------- |
| Daily ranking        | "What's the latest Douyin daily ranking?"             | Latest all-category daily TOP 20   |
| Niche weekly ranking | "How did food accounts rank on Douyin last week?"     | Latest food niche weekly TOP 20    |
| Monthly ranking      | "Show me last month's Douyin gaming account rankings" | Latest gaming monthly TOP 20       |
| Full ranking list    | "I want to see all 50"                                | Full TOP 50 with generated report  |
| Download report      | "Generate an HTML report for this ranking"            | Visual HTML file delivered         |
| Subscribe push       | "I want daily updates on the Douyin food ranking"     | Creates a scheduled auto-push task |

### Output Example

📊 Douyin Daily Ranking · All Categories

Data date: 2025-05-19
50 accounts on the list (showing TOP 20)

💡 Note: Data is updated daily at 17:30 with the previous day's figures; a time lag from live data exists.

📐 Composite score: weighted by total followers, new follower growth, new likes/shares/comments; full score 100:

| Rank | Account                  | Score | Total Followers | New Followers | New Likes | New Comments | New Shares |
| :--: | ------------------------ | :---: | :-------------: | :-----------: | :-------: | :----------: | :--------: |
| 🥇 1 | Account Name (clickable) |  96   |      2.54M      |     6,919     |   246K    |     67K      |    134K    |
| 🥈 2 | Account Name (clickable) |  89   |      1.13M      |      19K      |    79K    |    4,787     |    31K     |
|  …   | …                        |   …   |        …        |       …       |     …     |      …       |     …      |

⚡ More Options
⏺️ This ranking has 50 entries in total. Would you like to see the remaining 30?

📬 Subscription
1️⃣ Would you like to subscribe to the latest daily/weekly/monthly Douyin account rankings?
2️⃣ Would you like to subscribe to account performance for a specific niche?

---

## Use Cases

| Scenario                                   | Role                                  | Example Question                                                            | Benefit                                                                             |
| ------------------------------------------ | ------------------------------------- | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Find benchmark accounts in a niche         | Content creator / individual operator | "Which food accounts are performing well? Show me the latest daily ranking" | Quickly identify industry leaders and clarify content direction                     |
| Evaluate influencer partnership candidates | Brand / ad placement team             | "Which beauty accounts stood out in last week's Douyin TOP 50?"             | Batch screening for more efficient campaign decisions                               |
| Monitor competitor niche dynamics          | MCN agency / content team             | "Which gaming accounts grew the fastest this week?"                         | Stay on top of the competitive landscape and respond to market changes in real time |
| Generate industry analysis reports         | Industry analyst / consultant         | "Generate a March Douyin gaming category ranking report for me"             | One-click visual HTML, easy to share in presentations                               |
| Track account ranking changes over time    | Operations team                       | "I want the latest travel niche weekly ranking every Monday"                | Automated ranking intelligence via subscription push                                |

---

## Important Data Notes

### Update Schedule and Data Lookback

| Ranking Type | Update Time                                                     | Lookback Range |
| ------------ | --------------------------------------------------------------- | -------------- |
| Daily        | Updated at 17:30 every day with previous day's data             | Past 7 days    |
| Weekly       | Updated every Monday at 17:30 with last week's data             | Past 3 weeks   |
| Monthly      | Updated on the 2nd of each month at 9:00 with last month's data | Past 3 months  |

### Supported Niches (27)

Personal Talent, Life Vlog, Wealth & Finance, ACG/Anime, Home Decor, Education, Short Drama, Tech & Gadgets, Travel, Food, Beauty & Makeup, Animals, Parenting, Automotive, Relationships, Agriculture, Health & Medicine, Fashion & Trends, Dance & Performing Arts, Appearance & Styling, Humanities, Music, Film & TV, Fitness, Sports, Celebrity Entertainment, Gaming

### Data Freshness

Data is not updated in real time. Account engagement figures reflect the values captured at collection time and may differ from live platform data.

---
