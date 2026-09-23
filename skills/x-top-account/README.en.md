# X (Twitter) Top Accounts / x-top-account

[中文](README.md) | **English**

---

## Introduction

Quickly discover the most influential accounts on X (Twitter) and grasp the global creator landscape.

**Core Value**
Built on daily TOP-200 influential accounts with follower, growth and cross-platform data, helping you solve benchmarking, overseas advertising, competitor monitoring and industry insight challenges.

**Target Users**

- 🌏 Global content creators — benchmark top accounts in your niche
- 🏢 Brands / overseas advertisers — screen quality creators and evaluate cross-platform value
- 📦 MCN / cross-border ops teams — track competitor dynamics
- 📊 Industry analysts — generate data-driven reports

---

## Features

- **Ranking query**: daily X influence ranking, 20 items per page, 10 pages / 200 items in total, with pagination
- **Filters**: gender (all / male / female) and 32 industry categories, with fuzzy keyword matching (e.g. "pets" → 萌宠动物; category values are passed in Chinese)
- **Influence score**: weighted evaluation of followers, engagement and impressions, out of 100
- **HTML report**: X-styled visual HTML report with clickable account links, one-click export to PDF / high-res image
- **Subscription**: daily scheduled push, combinable with gender / industry filters

---

## API Key & Security

- This skill requires the environment variable `REDFOX_API_KEY`.
- Get your key at [RedFox Hub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFox Hub](https://redfox.hk?source=github) and configure `REDFOX_API_KEY` in your environment.
- Verify the key's source, scope, validity and revocability before providing it.
- Never hardcode or expose the key in code, prompts, logs or output files.

---

## Usage Guide

Describe your need in natural language — no command syntax to memorize.

### Quick Examples

| Intent            | Example                                          | Result                              |
| ----------------- | ------------------------------------------------ | ----------------------------------- |
| Latest ranking    | "Show me the latest Twitter all-category ranking" | Page 1 (20 items) of latest date   |
| Industry ranking  | "How do pet accounts rank on Twitter?"            | 萌宠动物 (Pets) ranking              |
| Gender ranking    | "Top female beauty creators on X"                 | 时尚美妆 (Beauty) + female filter    |
| Specific date     | "Twitter ranking for Sep 20, 2026"                | Ranking of the given date          |
| Pagination        | "Show me page 2"                                  | Page 2 (20 items)                  |
| Report download   | "Generate the HTML report for this ranking"       | Visual HTML file delivered         |
| Subscription      | "Send me the pet ranking every day"               | Scheduled push task created        |

### Output Example

📈 X (Twitter) Top Accounts · All Categories · All Genders

Data date: 2026-09-21 (Page 1/10)
200 accounts ranked (20 shown on this page)

💡 Note: the ranking is updated at 9:00 AM daily for the previous day and may differ from realtime data

📐 Influence score: weighted evaluation of followers, engagement and impressions, out of 100

| Rank | Account        | Biography                  | Country | Industry              | Score | Daily Δ | X Followers | Other Platforms | Tags |
| :--: | -------------- | -------------------- | :-----: | --------------------- | :---: | :-----: | :---------: | --------------- | ---- |
| 🥇 1 | Name (link)    |  biography    |   US    | Tech & Software       | 99/100 | +1.25% | 2.2亿+      | —               | Tags |
| 🥈 2 | Name (link)    | biography       |   US    | Entertainment & Culture | 97/100 | +0.88% | 3,100w+   | YouTube 4亿+    | —    |
|  …   | …              | …                    |    …    | …                     |   …   |    …    |      …      | …               | …    |

⚡ More actions
⏺️ This ranking has 200 items in total. Continue to page 2?

📬 Subscription
1️⃣ Subscribe to the daily X (Twitter) ranking push?
2️⃣ Filters supported: gender (all / male / female) and 32 industry categories

---

## Use Cases

| Scenario                    | Role                        | Example question                              | Benefit                              |
| --------------------------- | --------------------------- | --------------------------------------------- | ------------------------------------ |
| Find benchmark accounts     | Creators / solo operators   | "Which tech accounts perform best on X?"      | Identify niche leaders quickly       |
| Evaluate creator candidates | Brands / advertisers        | "Top 20 female beauty creators?"              | Batch screening for better decisions |
| Monitor competitors         | MCN / cross-border ops      | "Any new faces on page 2 of the pet ranking?" | Track market shifts in time          |
| Industry analysis reports   | Analysts / consultants      | "HTML report for the finance ranking"         | One-click visual report for sharing  |
| Track ranking changes       | Ops teams                   | "Send me the tech ranking every day"          | Automated ranking intelligence       |

---

## Data Notes

### Update Time & Lookback

| Rule        | Description                                                    |
| ----------- | -------------------------------------------------------------- |
| Update time | 9:00 AM daily for the previous day's ranking                   |
| Lookback    | Past 7 days                                                    |
| Empty data  | Automatically falls back to the nearest available date         |

### Supported Filters

- **Gender (3)**: all, male, female
- **Industry (32)**: 全部行业 (all), 商业创业, 汽车出行, 设计创意, 航空领域, 电商零售, 教育培训, 工程运营, 娱乐文化, 环境能源, 家庭育儿, 时尚美妆, 金融投资, 美食饮品, 游戏电竞, 健康医疗, 牧场马术, 宗教信仰, 科学学术, 体育健身, 科技软件, 旅行户外, 视觉艺术, 健康生活, 居家手工, 人力职场, 公益平权, 法律法务, 市场营销, 音乐领域, 萌宠动物, 政治新闻 (category values are passed to the API in Chinese)

### Data Freshness

Data is not realtime; account metrics reflect the collection moment and may differ from live values.

---
