# Cross-Platform Trending Tracker / trending-hub

## Introduction

Aggregates hot searches from Douyin, Weibo, Bilibili, Kuaishou, Zhihu, Toutiao, and Baidu in one place — no more hopping between platforms.

**Core Value**

One-click access to hot search data across 7 major platforms, updated hourly. Each platform is shown separately with up to 50 entries per platform. Filter by keyword or platform — skip the pain of checking each app one by one.

**Who It's For**

- 🔍 Competitor monitoring — View hot searches on specific platforms and track competitor dynamics
- 🎯 Topic research — Filter related hot searches by keyword to match content direction quickly
- 📊 Data analysis — Get raw hot search data across platforms for deeper analysis
- 📰 Public opinion tracking — Monitor how specific events perform in hot search across platforms

## Core Capabilities

- **All-platform hot search display**: 7 platforms shown independently, up to 50 entries each
- **Multi-platform combined queries**: Query one or multiple specified platforms
- **Keyword filtering**: Filter hot searches related to your keywords
- **Multiple time ranges**: Real-time, today, yesterday, this week, and more
- **Full ranking view**: View all 50 hot searches per platform
- **Subscription push**: Scheduled pushes for latest or yesterday's rankings

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain your `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` as a device environment variable before using this skill.
- Before providing your key, confirm its source, available scope, validity period, and whether reset/revocation is supported.
- Do not hard-code or expose the key in plaintext in code, prompts, logs, or output files.

---

## Usage Guide

### Quick phrase reference

| Intent                  | Example phrase                                             | What you get                                    |
| ----------------------- | ---------------------------------------------------------- | ----------------------------------------------- |
| All-platform hot search | "Hot ranking", "trending list", "all-platform hot search"  | TOP 10 hot searches per platform across 7 sites |
| Keyword filter          | "Show me sports-related hot searches"                      | Only hot searches containing the keyword        |
| Single platform only    | "Weibo hot search", "Douyin trends", "Bilibili hot search" | Hot searches for the specified platform only    |
| Multi-platform query    | "Weibo and Douyin hot search", "Douyin, Bilibili, Zhihu"   | Hot searches from multiple platforms at once    |
| Historical hot search   | "Yesterday's hot ranking", "yesterday's trends"            | Hot search data for the specified date          |
| Full ranking            | "Show Weibo full ranking"                                  | All 50 hot searches for that platform           |
| Daily subscription      | "Subscribe to daily push"                                  | Create a daily scheduled push task              |

### Sample output

#### 🔥 Cross-platform hot search ranking (by platform)

> **📅 Time range:** Hourly updates; hot items listed from 2026-05-21 00:00 to 2026-05-21 16:00
> **📊 Platforms:** Baidu, Weibo, Douyin, Bilibili, Kuaishou, Zhihu, Toutiao

---

#### Douyin hot search

| Rank | Hot search                        |  Heat  |
| :--: | --------------------------------- | :----: |
|  1   | [Hot video topic 1](https://...)  | 21.56M |
|  2   | [Hot video topic 2](https://...)  | 18.76M |
| ...  | ...                               |  ...   |
|  10  | [Hot video topic 10](https://...) | 6.78M  |

💡 40 more entries not shown. Reply "Show Douyin full ranking" to view all.

#### Baidu hot search

| Rank | Hot search                                         | Heat  |
| :--: | -------------------------------------------------- | :---: |
|  1   | [2026 gaokao essay topics announced](https://...)  | 9.86M |
|  2   | [Celebrity relationship announcement](https://...) | 8.75M |
|  3   | [Fuel price adjustment tonight](https://...)       | 6.54M |
|  4   | [Weather alert issued](https://...)                | 5.43M |
| ...  | ...                                                |  ...  |
|  10  | [Today's stock market](https://...)                | 2.34M |

💡 40 more entries not shown. Reply "Show Baidu full ranking" to view all.

---

#### Weibo hot search

| Rank | Hot search                  |  Heat  |
| :--: | --------------------------- | :----: |
|  1   | [Hot topic 1](https://...)  | 12.34M |
|  2   | [Hot topic 2](https://...)  | 9.87M  |
|  3   | [Hot topic 3](https://...)  | 8.76M  |
| ...  | ...                         |  ...   |
|  10  | [Hot topic 10](https://...) | 4.56M  |

💡 40 more entries not shown. Reply "Show Weibo full ranking" to view all.

---

#### Bilibili hot search

| Rank | Hot search                  | Heat  |
| :--: | --------------------------- | :---: |
|  1   | [Hot video 1](https://...)  | 5.67M |
|  2   | [Hot video 2](https://...)  | 4.32M |
| ...  | ...                         |  ...  |
|  10  | [Hot video 10](https://...) | 1.23M |

💡 40 more entries not shown. Reply "Show Bilibili full ranking" to view all.

---

📬 **Subscription push**:

- Reply "Subscribe to daily push" for scheduled daily hot ranking updates
- Reply "Subscribe to weekly push" for scheduled weekly hot summaries

---

### Single-platform query example

User says "Weibo hot search":

#### Weibo hot search

> **📅 Time range:** Hourly updates; hot items listed from 2026-05-21 15:00 to 2026-05-21 16:00
> **📊 Platforms:** Weibo

| Rank | Hot search                  |  Heat  |
| :--: | --------------------------- | :----: |
|  1   | [Hot topic 1](https://...)  | 12.34M |
|  2   | [Hot topic 2](https://...)  | 9.87M  |
| ...  | ...                         |  ...   |
|  50  | [Hot topic 50](https://...) |  890K  |

---

### Keyword filter example

User says "Show me sports-related hot searches":

#### Sports hot search

> **📅 Time range:** Hourly updates; hot items listed from 2026-05-21 00:00 to 2026-05-21 16:00
> **📊 Keyword:** Sports

| Rank | Hot search                                         | Platform |  Heat  |
| :--: | -------------------------------------------------- | :------: | :----: |
|  1   | [U20 women's football China vs Japan](https://...) |  Weibo   | 12.34M |
|  2   | [NBA playoff updates](https://...)                 |  Douyin  | 9.87M  |
|  3   | [Champions League final preview](https://...)      | Bilibili | 8.76M  |
| ...  | ...                                                |   ...    |  ...   |

---

## Use Cases

| Scenario               | Role             | Example question                          | Benefit                                          |
| ---------------------- | ---------------- | ----------------------------------------- | ------------------------------------------------ |
| Scan all platforms     | Content creator  | "What's trending today across platforms?" | Browse 7 platforms at once for topic inspiration |
| Single-platform focus  | Operator         | "What's on Weibo hot search?"             | Focus analysis on one platform's trends          |
| Keyword research       | Topic planner    | "Search workplace-related hot searches"   | Precisely match content direction                |
| Multi-platform compare | Data analyst     | "How do Douyin and Weibo trends differ?"  | Compare hot topic differences across platforms   |
| Historical lookback    | Competitor intel | "Check yesterday's hot searches"          | Analyze historical hot search performance        |
| Full ranking view      | Market research  | "Show Bilibili full hot search ranking"   | Get all 50 hot searches for that platform        |
| Scheduled tracking     | Operator         | "Push hot searches to me every morning"   | Automated tracking of trends across platforms    |

---

## Important data notes

### Data notes

- **Platforms covered**: 7 (Douyin, Weibo, Bilibili, Kuaishou, Zhihu, Toutiao, Baidu)
- **Update frequency**: Hourly; not real-time
- **Data range**: Look back up to 30 days; up to 50 hot searches per platform
