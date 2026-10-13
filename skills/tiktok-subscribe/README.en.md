# TikTok Monitor Subscription Push / tiktok-subscribe

---

## Introduction

Subscribe to TikTok keywords, specific accounts and topics. Every day at 9:00, yesterday's new content (new viral videos for keywords / new works from accounts / new works in topics) is pulled automatically and compiled into an HTML daily report grouped by subscription — subscribe once, stay on top of updates every day.

**Key Value**

- 🎯 **Three kinds, one place**: keywords, accounts and topics mixed in one subscription (up to 100 items), pushed automatically at 9:00 daily
- 📊 **Complete metrics**: plays, likes, comments, shares and publish time, all sorted by plays descending
- 🧭 **No-update folding**: items with no updates yesterday / in 7 days are folded, keeping focus on what changed
- 🔗 **Direct links**: full clickable work links for quick verification
- 📈 **AI semantic summary**: today's themes plus per-item theme / viewpoint readings

**Who It's For**

- 🤝 **Brands / MCNs** — track keyword heat and creator activity to time campaigns and collaborations
- 🧑‍💻 **Content operators** — monitor competitor keywords and topic heat changes for content ideas
- ✍️ **Creators / researchers** — follow topic heat and viral patterns, accumulate content data

---

## Features

### Core Features

- 🔍 **Three subscription entries**: keywords (new videos in the last day by likes), accounts (secUserId / share link), topics (topic ID)
- ⏰ **Daily auto push**: the automation task embeds all subscribed items and runs at 9:00 every day
- 🗓️ **Time-window filtering**: filters to "yesterday 9:00 ~ today 9:00" with smart paging; supports a specific historical date
- 📊 **Full engagement metrics**: plays / likes / comments / shares / publish time, sorted by plays descending
- 📑 **HTML daily report**: TikTok-style, grouped by subscription item, exportable as PDF / high-res image
- 📈 **AI semantic summary**: today's themes + per-item theme / viewpoint readings (marked as inference)
- 😴 **No-update folding**: items with no updates yesterday / in 7 days are folded automatically

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`)
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing a key, confirm its source, scope, validity period, and whether it supports reset/revocation.
- Never hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## How to Use

Describe what you want in natural language — no commands to memorize.

### Quick Phrases

| Intent | Example | Result |
| ------ | ------- | ------ |
| Subscribe to keywords | "Subscribe to the keyword nvidia for daily new videos" | Verified and added; new viral videos pushed daily at 9:00 |
| Subscribe to an account | "Subscribe to this account" + secUserId / share link | Verified and added; new works pushed daily at 9:00 |
| Subscribe to a topic | "Subscribe to topic 2525872 for daily new works" | Verified and added; new topic works pushed daily at 9:00 |
| Pull now | "Pull my subscription daily report now" | Runs one fetch immediately and shows the results |
| Specific date | "Show my subscriptions for 2026-10-12" | Fetches with the window of the specified date |
| Unsubscribe | "Unsubscribe from nvidia" | Removes the item from the subscription list |
| Export report | "Export the report" | Provides the HTML daily report, exportable as PDF / high-res image |

### Sample Output

After a successful pull, the subscription overview, per-item work tables and AI summary appear in the conversation as Markdown, and an HTML daily report is generated alongside (illustrative):

> 📊 Subscription result ｜ This time: 1 keyword ｜ Current total: 5 / 100 items ｜ Automation: updated ✅

### ▸ Keyword「nvidia」 yesterday's new content (5)

| # | Author | Work Summary | Plays | Likes | Comments | Shares | Publish Time |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | Raina / `rainaships` | [party ended immediately #Tech...](work link) | 85,207 | 18,254 | 315 | 1,251 | 10-12 11:50 |

```
📈 AI Semantic Summary
**Today's Themes**
1. **NVIDIA heat centered on hardware tests and workplace topics**: …… (nvidia, 8 works)
**Per-Item Readings**
1. Keyword「nvidia」: theme …… ｜ viewpoint ……

(The above is AI analysis and inference based on public data, for reference only.)
```

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Keyword heat tracking | Overseas brand / operator | "Subscribe to keyword nvidia for daily new videos" | Grasp new viral videos under the keyword daily for campaigns and content ideas |
| Creator monitoring | MCN / business | "Subscribe to this account" + secUserId / share link | Watch many creators' new works and data performance at once |
| Topic heat tracking | Content operator | "Subscribe to topic 2525872 for daily new works" | Monitor new works and heat changes in the topic |
| Competitor monitoring | Overseas brand | "Subscribe to these keywords and accounts" | Subscribe once, get competitor and niche updates at 9:00 daily |

---

## Important Data Notes

- Each successful query may consume credits: keywords / topics cost 1 call per page (max 3 pages by default in daily mode); an account item returns all recent works in 1 call; the HTML report and AI summary are generated offline at zero cost
- Daily pulls cover the "yesterday 9:00 ~ today 9:00" window (local time); the API does not support time sorting, so the skill compares publish times item by item
- Works are sorted by plays descending; publish times are shown in local time
- Account subscriptions need a secUserId (starting with MS4w) or a share link with a `sec_uid=` parameter; topic subscriptions need a topic ID (ch_id)
- Keyword items only report whether there were updates yesterday; no 7-day lookback is performed (to avoid extra credit consumption)
- The AI semantic summary matches the conversation output; both are AI analysis based on public data, clearly marked as inference and for reference only
