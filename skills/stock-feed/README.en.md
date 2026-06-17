# A-Share Social Media Briefs / stock-feed

---

## Introduction

Search A-share related short posts from Xiaohongshu, Douyin, and WeChat Official Accounts in one click. Built-in 17 core keywords, default 7-day data, cross-platform comparison and analysis of stock market sentiment trends.

**Core Value**

- **Zero-config launch**: 17 built-in A-share core keywords, no manual input needed, one query covers all topics.
- **Three-platform cross-validation**: Simultaneously obtain real discussion data from Xiaohongshu, Douyin, and WeChat Official Accounts, restoring the full picture of sentiment from multiple dimensions.
- **Visual delivery**: Automatically generate interactive visual reports, easy to share and archive.

**Target Users**

- 📈 **A-share investors** — Quickly grasp the trend of stock market sentiment across the web, assisting in market sentiment judgment.
- 📊 **Financial researchers** — Cross-platform comparison of retail and professional perspectives, efficiently completing sentiment research.
- 📰 **Financial media professionals** — Track intraday hot topics and topic evolution, gaining reference for story ideas and materials.

---

## Features

### Core Features

- **17-keyword one-click query**: Built-in 17 core keywords including A-share, A-share market, A-share index, limit-up, rise and fall, etc., covering all topics at once, no need to search keyword by keyword.
- **Three-platform data acquisition**: Simultaneously obtain real discussion data from Xiaohongshu, Douyin, and WeChat Official Accounts, aggregating scattered sentiment in one click.
- **Cross-platform comparison analysis**: Automatically synthesize data from all three platforms, discover differentiated trends and cross-validated signals, and output structured research reports.
- **Flexible time range**: Default 7 days, supports custom 1-30 days, adaptable for intraday tracking and weekly review.
- **Interactive visual report**: Automatically generate visual reports including data overview, key findings, and action previews, easy to share and archive.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please go to [RedFoxHub](https://redfox.hk?souce=github) to register an account and obtain `REDFOX_API_KEY`.
- Configure the device environment variable `REDFOX_API_KEY` before using this skill.
- Before providing the key, please confirm the key source, available scope, validity period, and whether it supports reset/revocation.
- It is prohibited to hard-code/expose the key in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Describe your A-share research needs in natural language directly, no need to memorize commands.

### Common Phrases Quick Reference

| Intent | Example Phrase | Result |
|--------|---------------|--------|
| One-click sentiment check | "Help me check the recent A-share market discussion heat" | Built-in 17 keywords full query, cross-platform comparison output |
| Track specific topics | "How is the semiconductor sector discussed recently" | Search by custom keywords, focus on specific sectors |
| Extend time range | "Check A-share rise and fall discussions in the past 30 days" | Support 1-30 days custom, track trend evolution |
| Compare two topics | "Compare the sentiment of limit-up and stock-picking topics" | Cross-platform comparison, output differential insights |

### Output Example

After completion, you will receive a structured research report, roughly as follows (illustrative):

**Semiconductor sector continues to strengthen** - Multi-platform discussions focus on domestic substitution and policy benefits, Xiaohongshu retail investors share trading insights, Douyin post-market interpretations see surging views. Source [Xiaohongshu@InvestorWang](link1), [Douyin@FinanceZhang](link2)

Key findings:
1. Domestic substitution topic heat rises simultaneously across all three platforms - Source [WeChat Official Account In-depth Review](link1), [Xiaohongshu@SemiconductorWatch](link2)
2. Retail investors show clear position-adding sentiment, but top influencers remind of risks - Source [Douyin@FinanceZhang](link1), [WeChat Official Account Strategy Analysis](link2)

Action preview:
- Pay attention to policy implementation pace, be cautious of divergence in short-term trading
- Avoid chasing highs, prioritize low-position catch-up directions

⚠ The above is a comprehensive social media sentiment analysis and does not constitute investment advice. Investment involves risks, enter the market with caution.

---

## Use Cases

| Scenario | Role | Example Question | Benefit |
|----------|------|-----------------|---------|
| Pre-market sentiment overview | A-share investor | "What is everyone discussing about A-shares today" | Quickly grasp market sentiment direction before opening |
| Sector-specific research | Financial researcher | "How is the sentiment for the chip sector recently" | Focus on specific sector, three-platform cross-validation |
| Weekly review | Financial media | "Help me summarize this week's A-share sentiment" | One-click structured report and visual page output |
| Track hot topic evolution | Content operator | "Check the 30-day limit-up discussion trend" | Extend timeline, discover sentiment inflection points |
