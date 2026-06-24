# TikTok Account Search / tiktok-account-search

---

## Overview

Enter a keyword and instantly find TikTok creator accounts, ranked by follower count from highest to lowest. See nicknames, follower counts, and bios at a glance, with one-click links to profile pages. When no results are found, you'll get 10 related keyword suggestions to keep your search going.

**Key Benefits**

- **Always Fresh**: Every search pulls the latest platform data — no stale cache.
- **Ranked by Followers**: Results are automatically sorted by follower count — top accounts always appear first.
- **Smart Keyword Expansion**: No results? The tool instantly gives you 10 related keywords to try from a different angle.
- **Pagination Support**: Browse through results page by page, 10 accounts at a time.

**Who Is This For**

- 🔍 **Content Creators** — Find creators in your niche and study their content strategies.
- 📊 **Marketing / Data Analysts** — Quickly map out which accounts dominate a category on TikTok.
- 🏢 **Brands / MCNs** — Discover and evaluate potential influencer partners by follower count.
- 🌏 **Cross-border E-commerce** — Search for influencers in overseas niche markets for promotion.

---

## Features

### Core Capabilities

- **Keyword Search**: Search TikTok accounts by any keyword, sorted by follower count.
- **Follower Ranking**: Results are auto-sorted by follower count — top accounts first.
- **Profile Links**: Every result includes a clickable link to the creator's TikTok profile.
- **Pagination**: Browse 10 results per page with multi-page support.
- **Smart Expansion**: When no results match, get 10 related keyword suggestions instantly.

### Highlights

- **Stable Pagination**: Page cursors ensure consistent, non-duplicate results across pages.
- **No Empty Hands**: Every search guarantees either results or keyword suggestions — you'll never hit a dead end.

---

## API Key Setup

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFox Hub](https://redfox.hk/settings/api-keys?source=github).
- Register at [RedFox Hub](https://redfox.hk?source=github) to obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable before using this skill.
- Verify the key's source, scope, validity period, and reset/revoke options before use.
- Never hardcode or expose the key in code, prompts, logs, or output files.

---

## How to Use

Just describe what kind of creators you're looking for in natural language.

### Quick Reference

| Intent                | Example                                    | Result                                          |
| --------------------- | ------------------------------------------ | ----------------------------------------------- |
| Search by category    | "Find TikTok beauty bloggers"              | Searches by keyword, sorts by followers   |
| Casual natural query  | "Who are the top fitness influencers"       | Extracts keyword, sorts by followers            |
| Browse next page      | Reply "next page" after results             | Auto-passes pagination cursor, no duplicates    |
| Try different keyword | View suggestions when no results, pick one  | Leverage 10 keyword expansions to keep searching |

### Example Output

After searching, you'll see a table like this:

| #   | Nickname        | TikTok ID     | Followers | Bio Summary           | Profile Link                                      |
| --- | --------------- | ------------- | --------- | --------------------- | ------------------------------------------------- |
| 1   | Meiko Montefalco | @mastermeiko  | 550.0w    | 💛 LUMEI BEAUTY ...    | [Visit Profile](https://www.tiktok.com/@mastermeiko) |
| 2   | Elizabeth Barich | @elizabethbarich | 66.4w  | Makeup brand @BARICH... | [Visit Profile](https://www.tiktok.com/@elizabethbarich) |
| 3   | 颜值社          | @saj0ad33565  | 1.6w      | 💫Beautiful Girls'... | [Visit Profile](https://www.tiktok.com/@saj0ad33565) |

(10 results per page with pagination hint at the bottom.)

---

## Use Cases

| Scenario          | Role              | Example Query                          | Benefit                                          |
| ----------------- | ----------------- | -------------------------------------- | ------------------------------------------------ |
| Influencer Search | MCN / Brand       | "Find TikTok fitness creators"         | Quickly list high-follower accounts for outreach |
| Competitor Study  | Content Creator   | "Who are the top food accounts"        | Understand follower scale and content direction  |
| Market Research   | E-commerce        | "Find parenting influencers on TikTok" | Discover promotion partners in target markets    |
| Trend Discovery   | Marketing Ops     | "Tech content creators on TikTok"      | Explore new niches and expand content strategy   |

---
