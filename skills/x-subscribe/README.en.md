# X (Twitter) Subscribed Account Tweets / x-subscribe

---

## Overview

Keep a close watch on the X (Twitter) celebrity accounts you follow. Every day it automatically rounds up what they posted from 9:00 yesterday to 9:00 today (the last 24 hours) — no more manually scrolling through each feed one by one.

**Core Value**
Subscribe to Twitter celebrity accounts (from three sources: ranking-board recommendations, user-specified handles, or following-list exploration). At 9:00 AM every day it automatically pulls the tweets those accounts posted from 9:00 yesterday to 9:00 today (the last 24 hours) and generates a grouped HTML daily report. It solves three pain points: overseas brands evaluating KOL collaboration windows, MCNs tracking dozens of celebrity accounts at once, and creators following top accounts' posting cadence.

**Target Users**

- 🌏 Overseas brands / media buyers — auto-summarize candidate KOLs' activity from yesterday to gauge collaboration timing
- 📦 MCN / talent agencies — batch subscription + a single report covering dozens of celebrity accounts
- ✍️ Content creators / researchers — track top accounts' posting cadence and viral content; timeline reports are easy to benchmark against

---

## Features

### Core Capabilities

- **Three subscription entries**: batch-subscribe from ranking boards (Top 10/20/50), subscribe by specified @handle, or explore a following list then subscribe
- **Daily auto-push**: account handles are embedded in the automation task; tweets from the last 24 hours (9:00 yesterday ~ 9:00 today) are pulled automatically at 9:00 AM with zero manual effort
- **Time-window pagination**: the API does not support time-based sorting, so the Skill paginates with cursor internally and filters to the "9:00 yesterday ~ 9:00 today" window
- **HTML daily report**: X-platform style (white background + X blue), tweets grouped by account in a timeline, with one-click export to PDF / high-resolution image
- **Engagement data**: views / likes / retweets / replies / post time at a glance, with retweets and quotes auto-tagged
- **AI semantic summary**: AI reads tweet content to distill "today's themes" (what the tweets are actually about, by real count) + each account's "theme / viewpoint"
- **Fold inactive accounts**: accounts with no updates yesterday / in the past 7 days are folded with a notice

---

## API Key & Security

- This skill requires the environment variable `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [Redfox hub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [Redfox hub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing a key, confirm its source, scope, validity period, and whether it supports reset/revocation.
- Never hard-code or expose keys in plain text within code, prompts, logs, or output files.

---

## Usage Guide

Just describe your needs in natural language — no need to memorize any command format.

### Common Phrases

| Intent | Example phrase | Effect |
| ------ | -------------- | ------ |
| Batch-subscribe from board | "Subscribe to the Top 20 of the Tech & Software board" | Query yesterday's board → extract accounts → verify → write into the daily 9:00 task |
| Subscribe specified account | "Subscribe to @elonmusk" | Verify account → append to subscription list → show latest activity immediately |
| Explore following list | "Show me who elonmusk follows" | Paginate followed accounts (name/followers/bio) for picking |
| View yesterday's report | "What did my X subscriptions post yesterday" | Pull all subscribed accounts' tweets from yesterday + HTML report |
| Specific date | "Check subscribed accounts' tweets on Sep 20" | Filter and pull by the given date |
| Unsubscribe | "Unsubscribe @naval" | Remove the account from the automation task |

### Output Example

📊 Subscription Result

| Item | Value |
|------|-------|
| Subscribed this time | 20 (Tech & Software board Top 20, 2 already-subscribed skipped) |
| Total subscriptions | 45 / 100 |
| Automation task | Updated ✅ runs automatically at 9:00 daily |
| First pull | Latest activity of each account shown below |

▸ Elon Musk (Followers: 240M)

| Tweet summary | Views | Likes | Retweets | Replies | Post time |
|---------------|-------|-------|----------|---------|-----------|
| Starship Flight 12 launch tomorrow... | 89M | 1.2M | 210K | 34K | 09-19 08:30 |

(remaining accounts shown in turn, 20 tweets each by default; the following 12 accounts had no updates in the past 7 days and are folded)

AI semantic summary (distilled from tweet content, not word frequency):
- Today's theme summary: what the tweets are actually about, as many themes as the content warrants
- Per-account summary: each account's main theme today + viewpoint/stance

---

## Use Cases

| Scenario | Role | Example ask | Benefit |
| -------- | ---- | ----------- | ------- |
| Evaluate KOL collaboration window | Overseas brand / buyer | "Subscribe to these candidate influencers and see what they post daily" | Auto-summarize yesterday's activity to seize collaboration timing |
| Batch-track celebrity activity | MCN / agency | "Subscribe to the top 30 accounts of the tech board" | A single report covers dozens of accounts, saving time and effort |
| Track top accounts' posting cadence | Content creator | "Subscribe to @mkbhd to see his viral tweets" | Timeline reports are easy to benchmark against |
| Explore following lists to find targets | Researcher | "Show me who Musk follows, pick a few to subscribe" | Discover quality accounts from a celebrity's following chain |

---

## Important Data Notes

### Subscription & Push Rules

| Rule | Description |
| ---- | ----------- |
| Push time | Runs automatically at 9:00 AM daily |
| Data scope | Pulls tweets posted by subscribed accounts from **9:00 yesterday to 9:00 today** (last 24 hours, local time zone) |
| Subscription limit | Up to 100 accounts total; at most 50 per automation task |
| Storage | Account handles are embedded directly in the automation command — no local file storage |

### Ranking-Board Subscription Source

- The ranking-board subscription always queries **yesterday's** hot-account board (updated with the previous day's data at 9:00 daily, lookback up to 7 days)
- Supports gender (all/male/female) and 32 industry-category filters, serving as the recommendation source for batch subscription
