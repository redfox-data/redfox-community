# WeChat 10W+ Article Recommendations / wechat-10w-hot

---

## Introduction

A WeChat Official Account 10w+ reading article recommendation tool that helps you quickly find viral articles with 10w+ reads, stay on top of top-traffic trends, and get topic inspiration.

**Core Value**

Continuously indexing 1,000+ WeChat Official Account articles with 10w+ reads daily, updated at 19:30 with yesterday's data. Pulls rankings by category and time window, delivers a complete Markdown ranking in conversation, auto-generates an HTML page exportable to PDF, and breaks down viral patterns across four dimensions — title traits, content themes, posting timing, and account characteristics. Supports queries and subscription pushes across 22 track categories — from tracking trends to benchmarking peers, a one-stop solution for your daily topic research needs.

**Who It's For**

- 📝 WeChat editors / operators — Track trends, titles, and account mix
- 📊 Content leads — Need shareable, printable ranking pages for team reviews
- 📈 Growth / business teams — Monitor competitors and niche 10w+ viral content

---

## Core Capabilities

- **Hot recommendations**: Daily update of yesterday's latest WeChat Official Account 10w+ reading article rankings
- **HTML generation**: Presents content in a polished visual layout, with export and sharing support
- **Subscription push**: When the platform supports it, subscribe to scheduled pushes for the latest hot articles

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

Describe what you need in plain language — no fixed commands to memorize.

### Quick Phrase Guide

| Intent                     | Example prompt                                | What you get                                          |
| -------------------------- | --------------------------------------------- | ----------------------------------------------------- |
| Latest 10w+ viral articles | "What are the latest 10w+ viral articles?"    | Latest available overall ranking                      |
| Niche track                | "Tech 10w+ hits from the past week"           | Category + time-window ranking                        |
| View all data              | "Show all — give me 50 entries"               | Full data in the same time window                     |
| Visual share & export      | "Generate a ranking page I can export as PDF" | Visual page based on the ranking, with export support |
| Subscribe                  | "Subscribe me to daily finance 10w+ articles" | Scheduled push of 10w+ articles after subscribing     |

### Sample Output

💡 **Data note**

10w+ viral article recommendations are updated daily at 19:30 with yesterday's data.

📊 **Article overview**

| #    | Title                                                       | Author               | Reads |
| ---- | ----------------------------------------------------------- | -------------------- | ----- |
| 🥇 1 | 5 must-know tips for new hires to quickly fit into the team | Workplace Growth Hub | 10w+  |
| 🥈 2 | 3 things you should never say in workplace communication!   | Workplace Tips       | 10w+  |
| 3    | …                                                           | …                    | …     |

📝 **Article details**

**1. [5 must-know tips for new hires to quickly fit into the team](https://mp.weixin.qq.com/s/xxx)**

📄 Author: [Workplace Growth Hub](https://open.weixin.qq.com/qr/code?username=xxx) 👀 Reads: 10w+ ⏰ Published: 2026-05-15

🔍 Content analysis: Overview… | Trend leverage… | Sharing driver… | Achieved impact…

---

📊 **Viral pattern analysis**

Title traits: …
Content themes: …
Posting timing: …
Account characteristics: …

---

📬 **Subscription service**

Would you like to subscribe to a specific track? We support 22 track categories.

1️⃣ Subscribe — Daily push at 19:30 with the latest 10w+ viral articles
2️⃣ Not now — Just this query

---

## Use Cases

| Scenario          | Role            | Example ask                                  | Benefit                                 |
| ----------------- | --------------- | -------------------------------------------- | --------------------------------------- |
| Daily trend watch | WeChat operator | "Today's viral / latest 10w+ articles"       | Fast read on top traffic and topics     |
| Competitor niche  | Content lead    | "Recent finance 10w+ hits"                   | Stay aligned in your vertical           |
| Team review       | Editorial lead  | "Export a printable viral ranking"           | Easier offline debriefs and co-creation |
| Learn patterns    | Junior editor   | "What do these viral pieces have in common?" | From gut feel to a reusable model       |

---

## Important Data Notes

### Update schedule & data lookback

| Ranking type    | Update time                                  | Lookback range |
| --------------- | -------------------------------------------- | -------------- |
| Overall ranking | Updated daily at 19:30 with yesterday's data | Past 30 days   |
| Track ranking   | Updated daily at 19:30 with yesterday's data | Past 30 days   |

### Supported tracks (22)

Humanities, Knowledge, Wellness, Fashion, Food & Dining, Lifestyle, Travel, Humor, Emotions, Sports & Entertainment, Beauty, Digest, Civic News, Wealth & Finance, Tech & Digital, VC & Business, Automotive, Real Estate, Workplace, Education & Exams, Academia, Enterprise & Brand

### Data timeliness

Data is not real-time; article engagement figures are snapshots from ingestion time and may differ from live data

---
