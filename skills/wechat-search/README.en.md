# WeChat Search

---

## Introduction

A WeChat Official Account hot article search tool that helps you quickly find articles with reads > 5,000, gain creative inspiration, and stay on top of content trends.

**Core Value**

Continuously indexing hot articles with reads > 5,000 from WeChat Official Accounts across the web over the past 30 days, updated daily with yesterday's data. Articles are ranked by a weighted score combining relevance, popularity, and timeliness, bringing together top viral content across all categories. Quickly find quality benchmark content across industries, easily reference trending creative approaches from peers — no more scouring multiple sources for material. A one-stop solution for your daily writing reference needs.

**Who It's For**

- 🎯 Content creators — Find topic inspiration, dissect viral article structures
- 📦 WeChat operators — Track industry hot spots, shape content strategy
- 🏢 Brands / Business — Understand KOL dynamics, evaluate content marketing directions
- 📚 Self-media learners — Learn viral patterns, improve writing skills

---

## Core Capabilities

- **Precise keyword search**: Enter any keyword to query related viral WeChat Official Account articles
- **Site-wide hot recommendations**: View the most popular recent articles across the platform without a keyword
- **Smart scoring & ranking**: Weighted scoring across three dimensions — relevance (10 pts), popularity (3 pts), timeliness (2 pts), for a total of 15 pts
- **Keyword expansion**: Search results include related niche-direction recommendations to broaden topic ideas
- **Subscription push**: Subscribe to keywords for daily scheduled push notifications

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

### Common Phrases Quick Reference

| Intent                | Example phrase                                              | Result                                             |
| --------------------- | ----------------------------------------------------------- | -------------------------------------------------- |
| Search viral articles | "Help me find viral workplace articles"                     | Returns recent hot articles in the workplace track |
| Search a niche area   | "Find articles about AI startups"                           | Precisely matches niche-keyword articles           |
| Multi-track query     | "Find viral articles in workplace, emotions, and parenting" | Returns hot articles from all three tracks at once |
| View site-wide hot    | "What are the hottest articles across the platform lately"  | Shows the most popular recent articles site-wide   |
| View all results      | "Show all 50 results"                                       | Displays the complete query results                |
| Subscribe to push     | "Subscribe to workplace articles, push daily at 9 AM"       | Creates a daily scheduled push task                |

### Output Example

📅 **Query time range**: May 14 – May 21

💡 **Found 12 related articles, showing the first 10. Would you like to see all?**

| Article title                                                                                 | Author                       | Reads | Published  | Relevance | Popularity | Timeliness | **Total** |
| --------------------------------------------------------------------------------------------- | ---------------------------- | ----- | ---------- | --------- | ---------- | ---------- | --------- |
| [5 must-know tips for new hires to quickly fit into the team](https://mp.weixin.qq.com/s/xxx) | Workplace Growth Hub         | 10.0w | 2026-05-15 | 9.8       | 3.0        | 2.0        | **14.8**  |
| [3 things you should never say in workplace communication!](https://mp.weixin.qq.com/s/xxx)   | Workplace Tips               | 8.5w  | 2026-05-14 | 9.5       | 2.8        | 2.0        | **14.3**  |
| [7 meeting efficiency secrets every worker must bookmark](https://mp.weixin.qq.com/s/xxx)     | Workplace Research Institute | 6.2w  | 2026-05-13 | 9.2       | 2.5        | 1.8        | **13.5**  |
| ...                                                                                           | ...                          | ...   | ...        | ...       | ...        | ...        | ...       |

**🔤 Keyword expansion**: Work, Office worker, Workplace fashion, Workplace tips, Growth, Niche careers, Upward management, Workplace anxiety, Promotion, Financial freedom

---

📬 **Subscription service**

1️⃣ Would you like to subscribe to the current search criteria? Articles will be pushed to you on a schedule.

2️⃣ Not now

---

## Use Cases

| Scenario                | Role               | Example question                                                 | Benefit                                   |
| ----------------------- | ------------------ | ---------------------------------------------------------------- | ----------------------------------------- |
| Find topic inspiration  | Content creator    | "Help me find trending workplace articles"                       | Quickly discover topic directions         |
| Dissect viral patterns  | WeChat operator    | "Find viral emotion-category articles and analyze the structure" | Learn viral headline and content formulas |
| Industry trend analysis | Brand / Business   | "What's trending in the food track lately"                       | Understand industry KOL dynamics          |
| Multi-track scanning    | Self-media learner | "Show me the hottest articles site-wide"                         | Grasp platform-wide trending directions   |
| Scheduled tracking      | Content creator    | "Push workplace articles to me every morning"                    | Automated industry hot-spot tracking      |

---

## Important Data Notes

### Recommended hot tracks (22)

Humanities, Knowledge, Wellness, Fashion, Food, Lifestyle, Travel, Humor, Emotions, Sports & Entertainment, Beauty, Digest, Civic News, Wealth & Finance, Tech & Digital, VC & Business, Automotive, Real Estate, Workplace, Education & Exams, Academia

### Data notes

- **Data scope**: Viral articles are those with reads ≥ 5,000
- **Update schedule**: Updated daily at 7 AM with yesterday's data
- **Data timeliness**: Article engagement data is current as of ingestion time, not real-time; engagement may continue to grow after ingestion
- **Query range**: Currently supports querying data from the past 30 days

### Sorting rules

- **Keyword search**: Sorted by total score (relevance + popularity + timeliness) in descending order; total score max 15 pts
- **Site-wide hot**: Sorted by read count in descending order
- **Relevance**: How closely the article matches the keyword (max 10 pts)
- **Popularity**: The article's overall popularity performance (max 3 pts)
- **Timeliness**: The article's recency weight (max 2 pts)

### Keyword expansion rules

- When a broad category word (track keyword) is detected, niche-direction recommendations are automatically provided
- If no results are found for your keyword, it may be too niche — our inclusion threshold is reads > 5,000. Try the suggested expansion words, extend the time range, or explore other popular tracks for inspiration
