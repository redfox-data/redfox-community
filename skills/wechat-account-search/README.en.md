# WeChat Account Search / wechat-account-search

---

## Overview

Enter a keyword and instantly find WeChat Account creators. See account names, account IDs, and introductions at a glance.

**Key Benefits**

- **Always Fresh**: Every search pulls the latest platform data — no stale cache.
- **Practical Data Dimensions**: View account name, ID, and introduction for quick content positioning.
- **Pagination Support**: Browse through results page by page.

**Who Is This For**

- 🔍 **Content Creators** — Find accounts in your niche and study their content strategies.
- 📊 **Marketing / Data Analysts** — Quickly map out which accounts dominate a category on WeChat.
- 🏢 **Brands / MCNs** — Discover and evaluate potential partner accounts by field.
- 📝 **Copywriters** — Search for accounts in niche markets for topic inspiration.

---

## Features

### Core Capabilities

- **Keyword Search**: Search WeChat Official Accounts by any keyword.
- **Data Display**: Shows account name, account ID, and introduction for quick content positioning.
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

Just describe what kind of accounts you're looking for in natural language.

### Quick Reference

| Intent                | Example                                    | Result                                          |
| --------------------- | ------------------------------------------ | ----------------------------------------------- |
| Search by category    | "Find finance WeChat accounts"              | Searches "finance", displays in API order        |
| Casual natural query  | "What are the top tech accounts"            | Extracts "tech", displays in API order           |
| Browse next page      | Reply "next page" after results             | Auto-increments page, no duplicates              |

### Example Output

After searching, you'll see a table like this:

| #   | Account Name     | Account ID      | Introduction                                               |
| --- | ---------------- | --------------- | ---------------------------------------------------------- |
| 1   | [占豪](https://open.weixin.qq.com/qr/code?username=zhanhao668) | zhanhao668 | Intl. affairs, finance, philosophy — 6 years top 100...     |
| 2   | 远方青木         | YFqingmu        | Quality articles by Qingmu                                   |
| 3   | 一个坏土豆       | iamhtd          | Revitalizing with my country                                 |

(Pagination hint at the bottom.)

---

## Use Cases

| Scenario          | Role              | Example Query                          | Benefit                                          |
| ----------------- | ----------------- | -------------------------------------- | ------------------------------------------------ |
| Account Discovery | Content Creator   | "Find finance WeChat accounts"         | Quickly locate top accounts in your field        |
| Competitor Study  | Marketing Ops     | "Who are the top tech accounts"        | Understand account positioning and content       |
| Partner Search    | Brand / MCN       | "Beauty category WeChat accounts"      | Discover promotion partners in target fields     |
| Topic Inspiration | Copywriter        | "Career content WeChat accounts"       | Explore new topic directions and content ideas   |

---
