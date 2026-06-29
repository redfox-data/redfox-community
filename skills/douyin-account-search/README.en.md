# Douyin Account Search / douyin-account-search

---

## Overview

Enter a keyword and instantly find Douyin creator accounts. See account names, follower counts, total likes, following counts, and video counts at a glance, with one-click links to profile pages.

**Key Benefits**

- **Always Fresh**: Every search pulls the latest platform data — no stale cache.
- **Rich Data Dimensions**: View account name, followers, total likes, following count, and video count for quick influence assessment.
- **Pagination Support**: Browse through results page by page.

**Who Is This For**

- 🔍 **Content Creators** — Find creators in your niche and study their content strategies.
- 📊 **Marketing / Data Analysts** — Quickly map out which accounts dominate a category on Douyin.
- 🏢 **Brands / MCNs** — Discover and evaluate potential influencer partners by follower count.
- 🛒 **E-commerce** — Search for influencers in niche markets for product promotion.

---

## Features

### Core Capabilities

- **Keyword Search**: Search Douyin accounts by any keyword.
- **Data Display**: Shows account name, follower count, total likes, following count, and video count for quick influence assessment.
- **Profile Links**: Every result includes a clickable link to the creator's Douyin profile.
- **Pagination**: Browse multiple results per page with multi-page support.

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
| Search by category    | "Find Douyin beauty bloggers"              | Searches "beauty", displays in API order         |
| Casual natural query  | "Who are the top fitness influencers"       | Extracts "fitness", displays in API order        |
| Browse next page      | Reply "next page" after results             | Auto-increments page offset, no duplicates      |

### Example Output

After searching, you'll see a table like this:

| #   | Account Name     | Followers | Total Likes | Following | Videos | Profile Link                                      |
| --- | ---------------- | --------- | ----------- | --------- | ------ | ------------------------------------------------- |
| 1   | 赵露思           | 305.2w    | 120.0m      | 9         | 156    | [Visit Profile](https://www.douyin.com/user/xxx) |
| 2   | 小橙子           | 1.8w      | 50.3w       | 15        | 32     | [Visit Profile](https://www.douyin.com/user/xxx) |
| 3   | 甜心教主         | 7131      | 2.1w        | 42        | 8      | [Visit Profile](https://www.douyin.com/user/xxx) |

(Pagination hint at the bottom.)

---

## Use Cases

| Scenario          | Role              | Example Query                          | Benefit                                          |
| ----------------- | ----------------- | -------------------------------------- | ------------------------------------------------ |
| Influencer Search | MCN / Brand       | "Find Douyin fitness creators"         | Quickly list high-follower accounts for outreach |
| Competitor Study  | Content Creator   | "Who are the top food accounts"        | Understand follower scale and content direction  |
| Market Research   | E-commerce        | "Find parenting influencers on Douyin" | Discover promotion partners in target markets    |
| Trend Discovery   | Marketing Ops     | "Tech content creators on Douyin"      | Explore new niches and expand content strategy   |

---
