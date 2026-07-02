# A-Share WeChat Official Account Influencer Rankings / gzh-astock-top

---

## Overview

The A-Share WeChat Official Account Influencer Rankings tool lets you retrieve account data and the latest article data for top WeChat official accounts in the A-share space by simply entering a date. It helps investors, content operators, and financial professionals quickly grasp the operational performance and latest content trends of leading A-share WeChat accounts.

**Core Value**

- **One-Stop Rankings**: Query data for 49 top A-share WeChat accounts in a single step, covering both official media/institutions and individual influencers
- **Multi-Dimensional Data**: Simultaneously access average read counts, RedFox Index scores, article titles, read volumes, likes, comments, and other core metrics
- **AI-Powered Summaries**: Automatically generates one-sentence key takeaways for each article, enabling quick content scanning
- **Subscription Tracking**: Subscribe to accounts of interest by index number and query only your subscribed list daily, reducing redundant searches

**Target Audience**

- 📈 Investors — Track leading opinions in the A-share space and gauge market sentiment and hot topics
- 📝 Content Operators — Study topic strategies and data performance of top accounts to refine content direction
- 📊 Financial Professionals — Monitor industry discourse and gather competitive analysis references
- 🔍 Data Analysts — Batch-export account operational data to support quantitative research and reporting

---

## Features

### Core Features

- **Rankings Query**: Query A-share WeChat account influencer rankings by date, with official media/institutions and individual influencers displayed separately — up to 30 accounts per category
- **Account Data**: Retrieve core operational metrics for each account, including average read counts, RedFox Index scores, and account descriptions
- **Daily Articles**: Access the latest articles published by each account on the specified date, including titles, links, read counts, likes, and comment counts
- **AI Content Summaries**: Automatically generate one-sentence key takeaways based on article titles for quick browsing
- **Subscription Push**: Subscribe to official media or influencer accounts by index number and query the latest article updates for all subscribed accounts in a single step

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?source=github) to register an account and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, verify its source, permitted scope, validity period, and whether it supports reset/revocation.
- Never hardcode or expose your key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Phrase | Outcome |
| ------ | -------------- | ------- |
| Query today's rankings | "Show me today's A-share influencer rankings" | Returns both official media and individual influencer rankings with account data and latest articles |
| Query a specific date | "Check the A-share account rankings for June 15" | Returns ranking data and articles for the specified date |
| View influencers only | "Show only individual influencers" | Displays only the individual influencer category |
| Subscribe to accounts | "Subscribe me to official media #1, #3, #5" | Adds the specified official media accounts to your subscription list |
| View subscriptions | "Show my subscriptions" | Displays all currently subscribed accounts |
| Daily push | "Push today's updates for my subscriptions" | Queries the latest articles for all subscribed accounts |
| Unsubscribe | "Unsubscribe from 央视财经" | Removes the specified account from your subscription list |

### Output Example

📅 Query Date: 2026-06-17

**【Official Media/Institutions】3 accounts**

| # | Account | Avg Reads | RedFox Index | Latest Article | AI Summary | Reads | Likes | Published |
|---|--------|----------|-------------|----------------|------------|-------|-------|-----------|
| 1 | 央视财经 | 48k | 1011.3 | [Breaking! 9 Ministries Release Major Stimulus](link) | Nine ministries jointly release major favorable policies | 83k | 464 | 06-16 |
| 2 | 券商中国 | 31k | 993.6 | [Late Trading Alert! Stock #601869 Hits Limit Up!](link) | Late-session unusual activity as stock hits limit-up, concept defies market | 50k | 202 | 06-16 |
| 3 | 中国基金报 | 32k | 1012.3 | [Global Black Tuesday! AI Trading 'Crash'...](link) | Global stock markets plunge, AI trading suffers severe selloff | 100k+ | 863 | 06-16 |

**【Individual Influencers】2 accounts**

| # | Account | Avg Reads | RedFox Index | Latest Article | AI Summary | Reads | Likes | Published |
|---|--------|----------|-------------|----------------|------------|-------|-------|-----------|
| 1 | 好运哥2008 | 80k | 876.6 | [Good News Is Here!!](link) | Bullish on positive stimulus impact on A-shares | 100k+ | 2859 | 06-16 |
| 2 | 孥孥的大树 | 24k | 810.8 | [Brokerages Should Learn from Cape Verde](link) | Brokerages should draw lessons from Cape Verde's development approach | 22k | 482 | 06-16 |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Daily Market Monitoring | Investor | "What are A-share influencers focusing on today?" | Quickly scan leading opinions and gauge daily market sentiment |
| Topic Research | Content Operator | "Which A-share articles were hottest this week?" | Analyze characteristics of high-read topics to refine content strategy |
| Competitive Analysis | Financial Professional | "Compare data between 券商中国 and 央视财经" | Understand competitors' operational metrics and content strategies |
| Account Tracking | Blogger | "Subscribe me to these influencers and show daily updates" | Continuously track top accounts while reducing manual searching |
| Quantitative Research | Data Analyst | "Get A-share influencer data for the past week" | Batch-export operational data to support quantitative analysis and reporting |

---

## Important Data Notes

- Account data is sourced from WeChat accounts indexed by the RedFox API, covering 49 fixed top A-share accounts (19 individual influencers + 30 official media/institutions)
- Article data consists of works published by accounts on the specified date, filtered and returned directly by the server
- Engagement data (read counts, likes, comments, etc.) reflects the time of data ingestion and is not real-time
- The RedFox platform updates the previous day's data daily at **07:00**; it is recommended to query after **07:30** for the latest daily report
- Only accounts that published articles on the given date appear in the results, so the number of accounts may vary across different dates
