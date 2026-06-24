# A-Share Daily News / stock-feed

---

## Introduction

A one-stop A-share market sentiment research tool that simultaneously searches 17 core A-share keywords across Xiaohongshu (RED), Douyin (TikTok China), and WeChat Official Accounts. It automatically filters out non-stock content, performs cross-platform sentiment comparison, and delivers structured research reports with interactive visual dashboards.

**Core Value**

- 17 built-in A-share keywords cover all major topics — zero configuration needed
- Cross-validate real user data across three platforms to uncover differentiated signals
- Automatically filter out beauty, food, travel and other non-stock content
- Support flexible time ranges from 1 to 30 days for trend tracking

**Who Is It For**

- 📈 Retail Investors — Quickly gauge market sentiment and trending sector discussions
- 🏦 Financial Researchers — Gather cross-platform sentiment data to support analysis
- 📰 Financial Content Creators — Discover high-engagement content for topic ideation

---

## Features

### Core Capabilities

- **17-Keyword One-Click Query**: Built-in keywords like A-shares, limit-up, stock picks — no manual input needed
- **Three-Platform Data Sources**: Simultaneously pull real user discussions from Xiaohongshu, Douyin, and WeChat Official Accounts
- **Smart Content Filtering**: Automatically identify and remove non-stock/investment content for clean data
- **Cross-Platform Analysis**: Synthesize data from all three platforms into actionable sentiment insights
- **Interactive HTML Reports**: Card-based visual reports with platform filtering and data sorting
- **Flexible Time Range**: Default 7 days, customizable from 1 to 30 days for trend tracking
- **Custom Keywords**: Search by specific stocks, sectors, or concepts for targeted queries

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing a key, verify the source, scope, validity period, and whether reset/revocation is supported.
- Never hardcode or expose keys in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe what you need in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Phrases | Result |
| --- | --- | --- |
| Check latest A-share sentiment | "Show me the latest data" | Search all 17 built-in keywords across 3 platforms for the past 7 days |
| Query a specific stock | "Show me Tencent-related news" | Targeted search for Tencent stock discussions |
| Query a specific sector | "Latest news on semiconductors and chips" | Search sentiment by specified concept or sector |
| Expand time range | "Show me A-share sentiment for the past 30 days" | Search one month of data to track trend changes |
| Compare two stocks | "BYD vs Tesla sentiment comparison" | Cross-platform comparison of discussion heat and reputation |

### Output Preview

> Reports begin with a "Data Overview" section showing TOP 5 articles per platform in table format (with clickable title links, authors, and platform-specific engagement metrics), followed by core findings, actionable predictions, risk disclaimers, and an auto-generated interactive HTML report.

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| --- | --- | --- | --- |
| Post-Market Review | Retail Investor | "How's the A-share market today?" | Quickly understand daily market sentiment and hot sectors |
| Individual Stock Research | Financial Researcher | "Check CATL's sentiment" | Get cross-platform discussion heat and sentiment for a specific stock |
| Sector Tracking | Content Creator | "Latest AI sector news" | Discover high-engagement content for topic ideation |
| Trend Analysis | Institutional Investor | "A-share sentiment trends over 30 days" | Track sentiment evolution to support investment decisions |

---
