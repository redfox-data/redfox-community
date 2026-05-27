# Trending hub top10

---

## Introduction

Based on hourly data from 7 major platforms — Douyin, Weibo, Bilibili, Kuaishou, Zhihu, Toutiao, and Baidu — intelligently identifies the same event across platforms and aggregates them into the TOP 10 hottest events across the entire web.

**Core Value**

Rather than simply listing each platform's hot searches, it merges multiple hot searches for the same event across different platforms into a single hot topic, outputting a TOP 10 hot events leaderboard. See at a glance what's trending everywhere — ideal for cross-platform matrix account operations.

**Who It's For**

- 🎯 Content creators — Spot the TOP 10 trending topics at a glance, quickly lock in content direction
- 📦 Content operators — Aggregate and analyze hot events, grasp public opinion spread patterns
- 🏢 Brand PR — Identify cross-platform hot events, evaluate communication impact
- 📊 Data analysts — Get aggregated hot topic data, analyze hot topic life cycles

---

## Core Capabilities

- **Cross-platform event aggregation**: Intelligently identifies the same event's multiple hot searches across different platforms and merges them into one hot event
- **TOP 10 hot topic ranking**: Outputs TOP 10 hot events leaderboard ranked by composite heat score
- **Heat trend prediction**: Predicts hot topic trajectory based on heat value, time on chart, and platform coverage
- **Cross-platform discussion analysis**: Shows how the same event is discussed differently across platforms
- **HTML visual report**: Generates a polished visual report with image export support
- **Subscription push service**: Scheduled push for TOP 10 cross-platform hot topics

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

| Intent                       | Example phrase                                                | Result                                         |
| ---------------------------- | ------------------------------------------------------------- | ---------------------------------------------- |
| View TOP 10 hot topics       | "Hot list", "Cross-platform hot topics", "Today's hot topics" | Get the TOP 10 hottest events across the web   |
| View real-time hot topics    | "Latest hot topics", "Real-time hot topics"                   | Get the latest aggregated hot topics           |
| View yesterday's hot topics  | "Yesterday's hot topics", "Hot topics from yesterday"         | Get yesterday's TOP 10 hot topics              |
| View past 7 days' hot topics | "Hot topics this week", "Past 7 days' hot topics"             | Get aggregated hot topics from the past 7 days |
| Export report                | "Export hot topic report", "Generate HTML report"             | Generate a visual HTML report                  |
| Subscribe to daily push      | "Subscribe to daily push"                                     | Daily scheduled push of TOP 10 hot topics      |

### Output Example

#### 🔥 Cross-Platform Hot Topic Leaderboard

> 📅 Statistics period: 2026-05-21 00:00 to 2026-05-21 16:00

#### TOP 10 Hot Topic Leaderboard

| Rank | Hot event                           | Composite heat | Platforms | Duration | Forecast |
| :--: | ----------------------------------- | :------------: | :-------: | :------: | :------: |
|  1   | U20 Women's Football China vs Japan |     15.92M     | 🌐🎵📰🎬  |   14h    |  🔥🔥🔥  |
|  2   | 2026 University Rankings Released   |     8.76M      |   📰📚    |    8h    |   🔥🔥   |
|  3   | Gas Prices Adjusted Tonight         |     6.54M      |    🔍     |    3h    |    🔥    |
| ...  | ...                                 |      ...       |    ...    |   ...    |   ...    |

---

#### Single Hot Topic Detail

**U20 Women's Football China vs Japan**

| Metric           | Value                                |
| ---------------- | ------------------------------------ |
| Composite heat   | 15.92M                               |
| Platforms listed | 4 (Weibo, Douyin, Toutiao, Kuaishou) |
| Duration         | 14h                                  |
| Highest rank     | #3                                   |

**Cross-platform discussion differences**:

- 🌐 Weibo: Users hotly debate the match, discussing women's football tactics and future development
- 🎵 Douyin: Match highlights widely shared, video views continuously climbing
- 📰 Toutiao: Primarily in-depth analytical articles, focusing on the current state of women's football
- 🎬 Kuaishou: Enthusiastic fan interaction, positive comment section atmosphere

**Related topics**:

- "[China U20 women's football 0:2 Japan, misses final](url)"
- "[U20 China vs Japan exciting moments](url)"

**Composite forecast**: 🔥🔥🔥 Sports-category viral topic, expected to last until finals day; peak heat has passed but sustained attention remains

⚡ **HTML report generated**
• Click below to download the HTML report file, viewable in browser with image export support

📬 **Subscription push service**

Want to continuously track hot topic trends?

- Reply "Subscribe to daily push" for daily scheduled TOP 10 hot topics
- Reply "Subscribe to weekly push" for weekly trending summary

---

## Use Cases

| Scenario                          | Role             | Example question                                       | Benefit                                                    |
| --------------------------------- | ---------------- | ------------------------------------------------------ | ---------------------------------------------------------- |
| Quickly lock in TOP 10 hot topics | Content creator  | "What are the top 10 hottest topics on the web today"  | See at a glance what's truly trending across the web       |
| Cross-platform hot topic analysis | Content operator | "Which hot topics recently spanned multiple platforms" | Identify hot events with cross-platform reach              |
| Hot topic trend prediction        | Data analyst     | "Predict which hot topics will persist"                | Predict hot topic life cycles based on multiple dimensions |
| Historical hot topic review       | Topic planner    | "Check yesterday's TOP 10 hot topics"                  | Analyze historical hot topic patterns                      |
| Export report for sharing         | Operations team  | "Export today's hot topic report"                      | Generate HTML visual report, easy to share                 |
| Scheduled tracking                | Content operator | "Push hot topics to me every morning"                  | Automated TOP 10 hot topic tracking                        |

---

## Important Data Notes

### Data notes

- **Platforms covered**: 7 major platforms (Douyin, Weibo, Bilibili, Kuaishou, Zhihu, Toutiao, Baidu)
- **Data update**: Updated hourly, not real-time data
- **Query range**: Supports lookback of hot topic data from the past 7 days
- **Output quantity**: Fixed output of TOP 10 hot events
- This skill **does not support** keyword filtering; it only outputs the TOP 10 hot topics across the web
