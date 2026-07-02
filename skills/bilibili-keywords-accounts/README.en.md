# Bilibili Keyword Account Search / bilibili-keywords-accounts

---

## Overview

Search for Bilibili accounts by keyword and get a list of accounts with follower counts, levels, bios, and more. Supports sorting by followers and smart categorization, helping you quickly discover and filter creators in your target niche.

**Core Value**

- **Keyword-driven**: Enter a 2–6 character keyword to instantly retrieve related Bilibili accounts—no manual one-by-one searching needed.
- **Smart categorization**: Automatically groups accounts by content niche (gaming, food, tech, etc.) for structured, efficient browsing.
- **Rich account data**: Returns follower count, level, bio, live-streaming status, and other key metrics in one query for quick account evaluation.

**Intended Users**

- 🔍 **Content ops / MCN** — Quickly discover creators in the same niche and expand collaboration resources and benchmark accounts.
- 📊 **Brands / advertisers** — Filter KOLs by niche and evaluate follower scale and account activity.
- 🎯 **Creators / researchers** — Understand the Bilibili account ecosystem and content distribution in any given field.

---

## Features

### Core Capabilities

- **Keyword search**: Search Bilibili accounts by keyword to quickly discover creators in your target niche.
- **Multi-dimensional sorting**: Sort by overall ranking or follower count to filter quality accounts from different angles.
- **Account details**: Returns follower count, level, bio, live-streaming status, and other core information.
- **AI smart categorization**: Automatically groups accounts into 12 major content categories (gaming, food, tech, etc.) for structured browsing.
- **Paginated browsing**: Flip through pages to see more accounts and expand your selection range.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe the Bilibili account niche or keywords you want to search for in natural language—no fixed commands to memorize.

### Quick Reference

| Intent                       | Example phrase                                  | Result                                                            |
| ---------------------------- | ----------------------------------------------- | ----------------------------------------------------------------- |
| Search accounts in a niche   | "Search for food-related accounts on Bilibili"  | Search by keyword, auto-categorize and display the account list   |
| Find similar creators        | "What tech review accounts are there on Bilibili" | Returns tech accounts, sorted by follower count                   |
| See more results             | "Show me more"                                  | Automatically moves to the next page and displays more accounts   |
| Broad search                 | "Search for gaming accounts"                    | Returns accounts under the gaming category with sub-niche labels  |

---

## Use Cases

| Scenario                  | Role              | Example question                                    | Benefit                                                          |
| ------------------------- | ----------------- | --------------------------------------------------- | ---------------------------------------------------------------- |
| Competitor account research | Content ops / MCN | "Search for beauty accounts on Bilibili"            | Quickly understand the distribution of top and mid-tier accounts |
| KOL screening             | Brand / advertiser | "Find me Bilibili tech accounts with lots of followers" | Sorted by follower count; quickly lock onto top accounts in the niche |
| Niche ecosystem overview  | Creator / researcher | "Are there many book-sharing accounts on Bilibili"  | Get a panoramic view of education/reading accounts and competition |
| Expand collaboration pool | MCN / business     | "Search for fitness accounts on Bilibili"           | Discover potential partners; evaluate account activity and followers |

---
