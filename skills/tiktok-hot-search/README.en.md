# TikTok Hot Search / tiktok-hot-search

---

## Introduction

Enter a keyword to get hot videos, related users and related topics on TikTok in one go: videos with plays, likes, comments, shares and work links; users with follower counts, total likes and profile links; topics with views, usage counts and topic links — one search, three types of results at a glance.

**Key Value**

- 🎯 **One input, three result types**: videos, users and topics aggregated around the same keyword for a complete search view
- 📊 **Complete metrics**: plays / likes / comments / shares + publish time for videos; followers / total likes / works for users; views / usage counts for topics
- 🔗 **Direct links**: full clickable work, profile and topic links for quick verification
- ↕️ **Flexible filters**: sorting and publish-time filters for videos; follower-range and verification filters for users

**Who It's For**

- 🧑‍💻 **TikTok content operators** — keyword-based topic research to catch content directions fast
- 📣 **Brands / MCNs** — scan competitor content and quality creators to support overseas campaign decisions
- ✍️ **Creators** — find the right topics and benchmark accounts to refine content strategy

---

## Features

### Core Features

- 🔍 **Keyword site-wide search**: search videos, users and topics at once with a single keyword
- 🎬 **Video search**: plays, likes, comments, shares and publish time; sort by plays, likes, comments or shares; publish-time filters (last 1 / 7 / 30 / 90 / 180 days)
- 👤 **User search**: follower count, total likes and works; filter by follower range and verification status
- 🏷️ **Topic search**: views, usage counts and direct topic links
- 🔗 **Full links**: complete clickable work / profile / topic links for easy verification
- 📄 **Paged browsing**: includes next-page offset info to continue on demand
- 🎯 **Top 3 viral video breakdown**: infer why videos went viral based on content and performance
- 🚀 **Top 3 creator recommendations**: follow-up reasons based on account data and keyword relevance
- 💡 **Topic trend insights**: summarize topic heat, usage trends and commercial signals
- 📑 **HTML report**: generated with every search, exportable as PDF / high-res image

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
| Search videos | "Search TikTok videos about NVIDIA" | Outputs the video list with a Top 3 viral video breakdown (plays descending by default) |
| Find accounts / creators | "Which TikTok accounts make pour-over coffee?" | Outputs the user list with Top 3 creator recommendations (followers descending by default) |
| Check a topic | "Check the cat topic data on TikTok" | Outputs the topic list with topic trend insights (views descending by default) |
| Site-wide search | "Search for camping gear" | Outputs videos, users and topics in one go, each with analysis |
| Sorting & time filter | "Sort by likes, only the last week" | Videos sorted by likes desc + publish-time filter |
| Follower filter | "Only accounts with 100k+ followers" | Users filtered by follower range |
| Next page | "Next page" | Continues with the next offset based on the previous page hints |
| Export report | "Export the report" | Provides an HTML report, exportable as PDF / high-res image |
| View raw data | "Show the raw response" | Outputs the raw data content |

### Sample Output

After a successful search, the three result sets appear directly in the conversation as Markdown tables with AI analysis blocks, and an HTML report is generated alongside (illustrative):

> Keyword: `NVIDIA` | Videos: 3 | Related users: 3 | Related topics: 3

| # | Author | Work ID | Plays | Likes | Comments | Shares | Publish Time | Work Link | Content Summary |
|---:|---|---|---:|---:|---:|---:|---|---|---|
| 1 | CreatorA / `creator_a` | `7xxxxxxxxxx` | 12,345,678 | 987,654 | 12,345 | 6,789 | 2026-10-05 | [Open work](work link) | Video content summary… |
| 2 | CreatorB / `creator_b` | `7yyyyyyyyyy` | 9,876,543 | 765,432 | 9,876 | 5,432 | 2026-10-04 | [Open work](work link) | Video content summary… |

| # | Nickname | TikTok Handle | Followers | Total Likes | Works | Profile Link |
|---:|---|---|---:|---:|---:|---|
| 1 | CreatorC | `creator_c` | 1,234,567 | 23,456,789 | 321 | [Open profile](https://www.tiktok.com/@creator_c) |

| # | Topic | Topic ID | Views | Usage Count | Topic Link |
|---:|---|---|---:|---:|---|
| 1 | `#example` | `12345` | 12,345,678,901 | 98,765 | [Open topic](topic link) |

```
🎯 Top 3 Viral Video Breakdown
1. **CreatorA** (@creator_a) published 2026-10-05 ｜ plays 12,345,678 ｜ likes 987,654
   Why it went viral (inferred): …… ｜ [Open work](work link)

🚀 Top 3 Creators Worth Following
1. **CreatorC** (@creator_c) followers 1,234,567 ｜ total likes 23,456,789 ｜ works 321
   Why follow (inferred): …… ｜ [Open profile](https://www.tiktok.com/@creator_c)

💡 Topic Trend Insights
1. **#example**
   ……

(The above is AI analysis and inference based on public data, for reference only.)
```

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Topic research | Content operator | "Search camping gear and see what's hot in the last month" | Quickly grasp trending content and topic directions |
| Creator discovery | Brand / MCN | "Which TikTok accounts make pour-over coffee? 100k+ followers only" | Lock onto partner creators by follower range |
| Competitor scan | Overseas brand | "Search our brand keyword for related hot videos" | Understand brand-related content volume and distribution |
| Topic tracking | Content operator / creator | "Check the views and usage count of the cat topic" | Evaluate topic heat and decide whether to join in |

---

## Important Data Notes

- Each successful query may consume credits; a site-wide search includes 3 data queries — query as needed
- Videos are sorted by plays descending by default; users by followers descending; topics by views descending
- When there are many results, browse page by page following the paging hints
- Profile links are generated from the TikTok handle
- Viral-video reasons, follow-up reasons and topic insights are AI analysis based on public data, clearly marked as inference and for reference only
