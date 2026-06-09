# Douyin Account Subscription Tracker / douyin-subscribe

---

## Introduction

Subscribe to competitor, peer, and follow accounts via Douyin ID. Automatically fetch the latest content data every day, generate visual reports, and stay on top of Douyin trends effortlessly.

**Core Value**

- **One-click Subscribe**: Send a Douyin ID to subscribe — no complex setup, supports up to 20 accounts
- **Daily Auto-push**: Automatically fetches the latest content from subscribed accounts every day at 9:00 AM — no manual effort required
- **Visual Reports**: Auto-generates polished HTML reports with preview and sharing support — data at a glance
- **Full-spectrum Data**: Favorites, comments, shares, likes, and publish time — all key metrics covered

**Ideal For**

- 📊 **Content Operators** — Track competitor account activity and spot trending content in real time
- 🎬 **Short-video Creators** — Monitor top accounts in your niche for inspiration and data-driven insights
- 🏢 **Brands / MCNs** — Batch-manage followed accounts and receive daily content digests automatically

---

## Features

### Core Features

- **Direct Douyin ID Subscription**: Subscribe using Douyin IDs — simple and transparent
- **Daily Auto-fetch**: Automatically retrieves the latest content data every day at 9:00 AM after subscribing
- **HTML Visual Reports**: Auto-generates polished report files with data summaries and Top 5 trending content
- **Clickable Links**: Both titles and account names link directly to detail pages
- **Smart Date Strategy**: Defaults to the previous day; auto-fallback to the last 7 days if no data; also supports custom date ranges
- **Grouped Multi-account Display**: Grouped by account name, sorted by share count in descending order within each group

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?source=github) to register an account and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing your key, please verify its source, applicable scope, validity period, and whether reset/revocation is supported.
- Do not hardcode or expose your key in plaintext in code, prompts, logs, or output files.

---

## Usage Guide

Simply tell us the Douyin ID you want to subscribe to in natural language — no commands to memorize.

### Quick Reference

| Intent | Example | Result |
| ------ | ------- | ------ |
| Subscribe | "Subscribe to Fish688688" | Auto-validates and subscribes, displays latest content |
| Batch Subscribe | "Subscribe to abc123, def456, ghi789" | Subscribes to multiple accounts at once |
| View Specific Dates | "Show me content from 2026-06-01 to 2026-06-05" | Fetches historical content by date range |
| Unsubscribe | "Unsubscribe Fish688688" | Removes the account from your subscription list |

### Output Example

After subscribing, you will receive:

- **Markdown Content Table**: Grouped by account, showing favorites, comments, shares, and likes
- **HTML Visual Report**: Auto-saved to the `report/` directory, including data summaries and Top 5 trending content
- **Summary Statistics**: Standout account performance + Top 5 trending topics

---

## Use Cases

| Scenario | Role | Example Request | Benefit |
| -------- | ---- | --------------- | ------- |
| Competitor Monitoring | Content Operator | "Subscribe to competitor Douyin IDs and check their content daily" | Get daily competitor updates automatically, never miss trending content |
| Niche Tracking | Short-video Creator | "Subscribe to these top accounts and track their content" | Stay current with niche trends and gain creative inspiration |
| Batch Management | MCN / Brand | "Subscribe to all these accounts and manage them together" | Batch subscribe up to 20 accounts with automatic daily digests |
| Historical Review | Content Analyst | "Show me last week's content data for these accounts" | Query historical data with custom date ranges |

---
