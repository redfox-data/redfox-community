# wechat-original-hot

---

## Introduction

Helps you quickly find original viral articles on WeChat Official Accounts, get topic inspiration, and stay on top of content trends.

**Core Value**

Continuously indexing daily original viral articles from WeChat Official Accounts, updated at 19:30 with yesterday's data. Supports queries for high-read original articles across 22 track categories and date ranges. Quickly find quality original benchmark content across tracks, easily reference trending creative approaches from peers — a one-stop solution for your daily topic research needs.

**Who It's For**

- 📝 WeChat editors / operators — Find topics and benchmarks
- 📊 Content planners — Filter original viral rankings by category
- 📈 Ops leads — Day-specific review + PDF export

---

## Core Capabilities

- **Category quick search**: Supports site-wide hot or 22 track categories, with automatic colloquial-to-standard mapping — pinpoint original viral hits
- **Flexible time filtering**: Supports date-specific queries within the past 30 days
- **One-click ranking page**: Auto-generate an HTML page exportable to PDF after each table output
- **Scheduled niche push**: Subscribe by track; daily push at 19:30 with the latest original viral data

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

| What you say                                                | What you'll roughly get                                    |
| ----------------------------------------------------------- | ---------------------------------------------------------- |
| "Latest original viral," "today's originals," "viral picks" | Overall Top 20 table + data note + subscription ask + HTML |
| "Original viral in tech / health / finance…"                | Category Top 20 + HTML                                     |
| "Original viral on May 3," "yesterday's viral"              | Date query + table + HTML                                  |
| "What's hot lately in originals"                            | Default ~7-day range Top 20                                |

### Sample Output

💡 **Data note**

Original article recommendations are updated daily at 19:30 with yesterday's data. The data below is a snapshot from fetch time and may differ from live data.

📊 **Original viral recommendations**

| #   | Author           | Title                 | Reads |
| --- | ---------------- | --------------------- | ----- |
| 1   | [Author A](link) | [Article Title](link) | 10w+  |
| 2   | [Author B](link) | [Article Title](link) | 10w+  |
| …   | …                | …                     | …     |

50 original viral articles retrieved; showing the top 20.

📬 **Subscription service**

Would you like to subscribe to a specific track? We support 22 track categories: Humanities, Knowledge, Wellness, Fashion, Food & Dining, Lifestyle, Travel, Humor, Emotions, Sports & Entertainment, Beauty, Digest, Civic News, Wealth & Finance, Tech & Digital, VC & Business, Automotive, Real Estate, Workplace, Education & Exams, Academia, Enterprise & Brand

1️⃣ Subscribe — Daily push at 19:30 with the latest original articles
2️⃣ Not now — Just this query

---

## Use Cases

| Scenario              | Role          | Example ask                              | Benefit                                         |
| --------------------- | ------------- | ---------------------------------------- | ----------------------------------------------- |
| Daily original topics | WeChat editor | "Latest original viral"                  | Latest original hot samples + shareable HTML    |
| Vertical benchmarking | Planner       | "Tech original viral"                    | Top list filtered by category                   |
| Day review            | Ops lead      | "Original viral on May 3"                | One-day original viral list + PDF               |
| Subscription          | Cadence ops   | "Subscribe to finance original articles" | Daily scheduled push of original viral articles |

---

## Important Data Notes

### Update schedule & data lookback

| Query type           | Update time                                  | Lookback range |
| -------------------- | -------------------------------------------- | -------------- |
| Original viral query | Updated daily at 19:30 with yesterday's data | Past 30 days   |

Data is a **snapshot at fetch time** and may differ from live reads

### Supported tracks (22)

Humanities, Knowledge, Wellness, Fashion, Food & Dining, Lifestyle, Travel, Humor, Emotions, Sports & Entertainment, Beauty, Digest, Civic News, Wealth & Finance, Tech & Digital, VC & Business, Automotive, Real Estate, Workplace, Education & Exams, Academia, Enterprise & Brand

---
