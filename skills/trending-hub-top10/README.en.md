# Cross-Platform Aggregated Hot Topics TOP10 / trending-hub-top10

## Introduction

Based on hourly hot topic data from Douyin, Weibo, Bilibili, Kuaishou, Zhihu, Toutiao, and Baidu, this skill intelligently identifies the same event across platforms and outputs the TOP10 hottest cross-platform trending events.

**Core Value**

Rather than simply listing each platform's hot searches separately, it aggregates multiple hot searches for the same event across platforms into one hot topic, and outputs a TOP10 ranking — so you can see what the whole internet is talking about at a glance, ideal for cross-platform matrix account operations.

**Who It's For**

- 🎯 Content creators — See the TOP10 cross-platform hot topics at a glance and lock in content direction fast
- 📦 Content operations — Aggregate and analyze hot events to understand spread patterns
- 🏢 Brand PR — Identify cross-platform hot events and evaluate communication impact
- 📊 Data analysts — Get aggregated hot topic data and analyze lifecycle trends

## Core Capabilities

- **Cross-platform event aggregation**: Intelligently merge multiple hot searches for the same event across platforms into one hot topic
- **TOP10 hot topic ranking**: Output TOP10 hot events ranked by composite heat
- **Heat trend prediction**: Predict hot topic trajectory based on heat value, time on chart, and platform coverage
- **Cross-platform discussion analysis**: Show how discussion focus differs across platforms for the same event
- **HTML visual report**: Generate polished visual reports with image export support
- **Subscription push**: Scheduled push of cross-platform TOP10 hot topics

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

| Intent                 | Example phrase                                               | What you get                              |
| ---------------------- | ------------------------------------------------------------ | ----------------------------------------- |
| Cross-platform TOP10   | "Hot ranking", "cross-platform trends", "today's hot topics" | Get TOP10 hottest cross-platform events   |
| Real-time hot topics   | "Latest trends", "real-time hot topics"                      | Get latest aggregated hot topics          |
| Yesterday's hot topics | "Yesterday's trends", "yesterday hot topics"                 | Get yesterday's TOP10 hot topics          |
| Past 7 days            | "Hot topics past 7 days", "this week's trends"               | Get aggregated hot topics for past 7 days |
| Export report          | "Export hot topic report", "generate HTML report"            | Generate visual HTML report               |
| Daily subscription     | "Subscribe to daily push"                                    | Daily scheduled TOP10 hot topic push      |

### Sample output

#### 🔥 Cross-platform hot topics ranking

> 📅 Time range: 2026-05-21 00:00 to 2026-05-21 16:00

#### TOP10 hot topics ranking

| Rank | Hot event                           | Composite heat | Platforms | Duration | Forecast |
| :--: | ----------------------------------- | :------------: | :-------: | :------: | :------: |
|  1   | U20 women's football China vs Japan |     15.92M     | 🌐🎵📰🎬  |   14h    |  🔥🔥🔥  |
|  2   | 2026 university rankings released   |     8.76M      |   📰📚    |    8h    |   🔥🔥   |
|  3   | Fuel price adjustment tonight       |     6.54M      |    🔍     |    3h    |    🔥    |
| ...  | ...                                 |      ...       |    ...    |   ...    |   ...    |

---

#### Single hot topic details

**U20 women's football China vs Japan**

| Metric             | Value                                |
| ------------------ | ------------------------------------ |
| Composite heat     | 15.92M                               |
| Platforms on chart | 4 (Weibo, Douyin, Toutiao, Kuaishou) |
| Duration           | 14h                                  |
| Peak rank          | #3                                   |

**Cross-platform discussion differences**:

- 🌐 Weibo: Fans discuss match tactics and future of women's football
- 🎵 Douyin: Match highlights spread widely; video views keep climbing
- 📰 Toutiao: In-depth analysis articles on the state of women's football
- 🎬 Kuaishou: Active fan interaction; positive comment atmosphere

**Related topics**:

- 「[China U20 women 0:2 Japan, miss final](url)」
- 「[U20 women's football China vs Japan highlights](url)」

**Overall forecast**: 🔥🔥🔥 Sports viral topic; expected to last until finals day; peak heat passed but ongoing attention

⚡ **HTML report generated**
• Click below to download the HTML report; open in browser and export as image

📬 **Subscription push**

Want to keep tracking hot topic trends?

- Reply "Subscribe to daily push" for daily TOP10 hot topic updates
- Reply "Subscribe to weekly push" for weekly hot topic summaries

---

## Use Cases

| Scenario                | Role            | Example question                                        | Benefit                                         |
| ----------------------- | --------------- | ------------------------------------------------------- | ----------------------------------------------- |
| Lock in TOP10 fast      | Content creator | "What are today's top 10 cross-platform trends?"        | See what's truly hot across the web at a glance |
| Cross-platform analysis | Content ops     | "Which topics spread across multiple platforms lately?" | Identify cross-platform viral events            |
| Trend prediction        | Data analyst    | "Which hot topics will keep trending?"                  | Predict lifecycle from multiple dimensions      |
| Historical review       | Topic planner   | "Show yesterday's TOP10 hot topics"                     | Analyze historical hot topic patterns           |
| Export and share        | Ops team        | "Export today's hot topic report"                       | Visual HTML report for easy sharing             |
| Scheduled tracking      | Content ops     | "Push hot topics to me every morning"                   | Automated TOP10 hot topic tracking              |

---

## Important data notes

### Data notes

- **Platforms covered**: 7 (Douyin, Weibo, Bilibili, Kuaishou, Zhihu, Toutiao, Baidu)
- **Update frequency**: Hourly; not real-time
- **Query range**: Look back up to 7 days of hot topic data
- **Output count**: Fixed TOP10 hot events
- This skill **does not support** keyword filtering — only outputs cross-platform TOP10 hot topics
