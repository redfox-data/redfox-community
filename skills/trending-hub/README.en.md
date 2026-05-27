# Trending-Hub

---

## Introduction

Aggregates hot search trends from 7 platforms — Douyin, Weibo, Bilibili, Kuaishou, Zhihu, Toutiao, and Baidu — so you don't have to check them one by one.

**Core Value**

One-click access to hot search data across 7 major platforms, updated hourly. Each platform is displayed independently with up to 50 trending items. Supports filtering by keyword or platform — say goodbye to the hassle of checking each platform separately.

**Who It's For**

- 🔍 Competitor monitoring — Check specific platform hot searches to understand competitor dynamics
- 🎯 Topic research — Filter relevant hot searches by keyword to quickly match topic directions
- 📊 Data analysis — Get raw hot search data across platforms for in-depth analysis
- 📰 Public sentiment tracking — Monitor how specific events trend across different platforms

---

## Core Capabilities

- **Cross-platform hot search display**: 7 major platforms shown independently, up to 50 trending items each
- **Multi-platform combined queries**: Query a single platform or multiple specified platforms at once
- **Precise keyword filtering**: Filter hot searches by keyword
- **Multiple time ranges**: Supports real-time, today, yesterday, this week, and more
- **Full leaderboard view**: Each platform can display all 50 hot search items
- **Subscription push service**: Scheduled push for latest/yesterday's hot lists

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

| Variable | Required | Notes |
| --- | --- | --- |
| `REDFOX_API_KEY` | Yes | API access key |

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

| Intent | Example phrase | Result |
| --- | --- | --- |
| View cross-platform hot searches | "Hot list", "Trending", "Cross-platform hot searches" | Shows TOP 10 hot searches for each of the 7 platforms |
| Keyword filtering | "Show me sports-related hot searches" | Only displays hot searches containing the keyword |
| Specific platform only | "Weibo hot search", "Douyin trending", "Bilibili hot search" | Only shows hot searches for the specified platform |
| Multi-platform combined query | "Weibo and Douyin hot searches", "Douyin, Bilibili, Zhihu trending" | Shows hot searches from multiple platforms simultaneously |
| View historical hot searches | "Yesterday's hot list", "Yesterday's hot searches" | Views hot search data for a specified date |
| View full leaderboard | "Show full Weibo leaderboard" | Outputs all 50 hot search items for that platform |
| Subscribe to daily push | "Subscribe to daily push" | Creates a daily scheduled push task |

### Output Example

#### 🔥 Cross-Platform Hot Search Leaderboard (by platform)

> **📅 Statistics period:** Updated hourly; trending items listed between 2026-05-21 00:00 and 2026-05-21 16:00
> **📊 Platforms covered:** Baidu, Weibo, Douyin, Bilibili, Kuaishou, Zhihu, Toutiao

---

#### Douyin Hot Search

| Rank | Hot search | Heat |
|:---:|------|:---:|
| 1 | [Popular video topic 1](https://...) | 21.56M |
| 2 | [Popular video topic 2](https://...) | 18.76M |
| ... | ... | ... |
| 10 | [Popular video topic 10](https://...) | 6.78M |

💡 40 more items available for this platform. Reply "View full Douyin leaderboard" to see all data.

#### Baidu Hot Search

| Rank | Hot search | Heat |
|:---:|------|:---:|
| 1 | [2026 gaokao essay topics announced](https://...) | 9.86M |
| 2 | [Celebrity announces relationship](https://...) | 8.75M |
| 3 | [Gas prices adjusted tonight](https://...) | 6.54M |
| 4 | [Weather alert issued](https://...) | 5.43M |
| ... | ... | ... |
| 10 | [Today's stock market update](https://...) | 2.34M |

💡 40 more items available for this platform. Reply "View full Baidu leaderboard" to see all data.

---

#### Weibo Hot Search

| Rank | Hot search | Heat |
|:---:|------|:---:|
| 1 | [Trending topic 1](https://...) | 12.34M |
| 2 | [Trending topic 2](https://...) | 9.87M |
| 3 | [Trending topic 3](https://...) | 8.76M |
| ... | ... | ... |
| 10 | [Trending topic 10](https://...) | 4.56M |

💡 40 more items available for this platform. Reply "View full Weibo leaderboard" to see all data.

---

#### Bilibili Hot Search

| Rank | Hot search | Heat |
|:---:|------|:---:|
| 1 | [Popular video 1](https://...) | 5.67M |
| 2 | [Popular video 2](https://...) | 4.32M |
| ... | ... | ... |
| 10 | [Popular video 10](https://...) | 1.23M |

💡 40 more items available for this platform. Reply "View full Bilibili leaderboard" to see all data.

---

📬 **Subscription push**:
- Reply "Subscribe to daily push" for daily scheduled hot list delivery
- Reply "Subscribe to weekly push" for weekly trending summary delivery

---

### Specific Platform Query Example

User says "Weibo hot search":

#### Weibo Hot Search

> **📅 Statistics period:** Updated hourly; trending items listed between 2026-05-21 15:00 and 2026-05-21 16:00
> **📊 Platforms covered:** Weibo

| Rank | Hot search | Heat |
|:---:|------|:---:|
| 1 | [Trending topic 1](https://...) | 12.34M |
| 2 | [Trending topic 2](https://...) | 9.87M |
| ... | ... | ... |
| 50 | [Trending topic 50](https://...) | 0.89M |

---

### Keyword Filtering Example

User says "Show me sports-related hot searches":

#### Sports Hot Search

> **📅 Statistics period:** Updated hourly; trending items listed between 2026-05-21 00:00 and 2026-05-21 16:00
> **📊 Keyword:** Sports

| Rank | Hot search | Platform | Heat |
|:---:|------|:---:|:---:|
| 1 | [U20 women's football China vs Japan](https://...) | Weibo | 12.34M |
| 2 | [NBA playoffs update](https://...) | Douyin | 9.87M |
| 3 | [Champions League final preview](https://...) | Bilibili | 8.76M |
| ... | ... | ... | ... |

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| --- | --- | --- | --- |
| Cross-platform scanning | Content creator | "Check today's hot searches across platforms" | Browse 7 platforms' hot searches in one click, find topic inspiration |
| Specific platform analysis | Operator | "See what's trending on Weibo" | Focus on analyzing a single platform's hot spots |
| Keyword research | Topic planner | "Search for workplace-related hot searches" | Precisely match topic directions |
| Multi-platform comparison | Data analyst | "What's the difference between Douyin and Weibo hot searches" | Compare hot topic differences across platforms |
| Historical data lookback | Competitor analysis | "Check yesterday's hot searches" | Analyze historical hot search performance |
| Full leaderboard viewing | Market research | "Show full Bilibili hot search leaderboard" | Get all 50 hot search items for that platform |
| Scheduled tracking | Operator | "Push hot searches to me every morning" | Automated cross-platform hot spot tracking |

---

## Important Data Notes

### Data notes

- **Platforms covered**: 7 major platforms (Douyin, Weibo, Bilibili, Kuaishou, Zhihu, Toutiao, Baidu)
- **Data update**: Updated hourly, not real-time
- **Data range**: Supports lookback of hot searches from the past 30 days; up to 50 hot search items per platform
