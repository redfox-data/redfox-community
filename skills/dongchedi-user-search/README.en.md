# Dongchedi User Search and Work Subscription / dongchedi-user-search

---

## Overview

Enter a keyword to instantly find users (creators) on Dongchedi — follower counts and bios at a glance. Pick the user you want, and their work list appears right away: titles, content types, reads, likes, comments, collects, and publish times. The latest 20 works are shown by default and can be expanded to the full list anytime, with a clickable link on every work. You can also subscribe to users you care about and receive their yesterday-updated works automatically every day.

**Key Benefits**

- **Two Steps to What You Need**: Search users by keyword, pick one, and pull their work list immediately — finding people and browsing content in one flow.
- **Complete Data**: User follower counts and bios, plus reads/likes/comments/collects/publish times for every work; the work list shows the latest 20 by default and can be expanded to view all.
- **Direct Links**: Clickable links for both user profiles and every work — one click to view details.
- **Pagination**: Browse candidate users page by page without missing any account.
- **Subscription Tracking**: Subscribe to a user and get their yesterday-updated works pushed automatically at 9:00 every day — never miss an update.

**Who Is This For**

- 🔍 **Content Creators** — Find benchmarking accounts in the automotive space and study their topics and performance.
- 📊 **Marketing / Data Analysts** — Map out which creators are active around a brand or vehicle model on Dongchedi.
- 🏢 **Brands / MCNs** — Screen potential automotive influencers and evaluate them by followers and work data.
- 🚗 **Automotive Professionals** — Follow your favorite car reviewers and quickly browse all their recent works.

---

## Features

### Core Capabilities

- **Keyword User Search**: Search Dongchedi users (creators) by brand name, vehicle model, or niche keyword.
- **User Info Display**: Nickname, followers, bio, user ID, and profile link in one view.
- **Work List Retrieval**: Select a user to get their work list, including title, type, reads, likes, comments, collects, and publish time; the latest 20 works are shown by default, and replying "查看全部" (view all) expands the complete list.
- **Direct Work Links**: Every work comes with a clickable link to its original page.
- **Pagination**: Browse the user list across multiple pages.
- **Subscription Push**: Subscribe to a user and receive their yesterday-updated works automatically every day at 9:00.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable before using this skill.
- Verify the key's source, scope, validity period, and reset/revoke options before use.
- Never hardcode or expose the key in code, prompts, logs, or output files.

---

## How to Use

Just describe in natural language which Dongchedi user you're looking for, or whose works you want to see — no commands to memorize.

### Quick Reference

| Intent                      | Example                                              | Result                                                          |
| --------------------------- | ---------------------------------------------------- | --------------------------------------------------------------- |
| Search users by niche       | "Find Dongchedi off-road users"                      | Searches "off-road", displays the user list                     |
| Find car reviewers          | "Who are the car review authors on Dongchedi?"       | Searches "car review", displays the user list                   |
| View a user's works         | Reply "2" or "小米公司" after the user list           | Displays that user's work list (latest 20 by default)           |
| View all works              | Reply "查看全部" after the work list                  | Continues with the remaining works until the full list is shown |
| Browse next page            | Reply "next page" after the user list                | Auto-increments the page number, continuous and non-duplicated  |
| Subscribe to updates        | Reply "订阅" after the work list                     | Pushes that user's yesterday-updated works daily at 9:00        |

### Example Output

After searching, you'll see a user list like this:

| #   | User            | Followers | Bio                                | User ID     | Profile Link                                                |
| --- | --------------- | --------- | ---------------------------------- | ----------- | ----------------------------------------------------------- |
| 1   | 小米公司        | 359.8w    | 小米公司官方信息发布账号。           | 3446334881  | [Visit Profile](https://www.dongchedi.com/user/3446334881)  |
| 2   | 小米手机        | 335.9w    | 小米手机产品官方头条号              | 3446343313  | [Visit Profile](https://www.dongchedi.com/user/3446343313)  |
| 3   | 小米车生活      | 2.7w      | 新青年汽车话题聚集地                | 66298217555 | [Visit Profile](https://www.dongchedi.com/user/66298217555) |

After selecting a user (e.g., replying "1"), their work list is displayed:

| #   | Publish Time     | Work Title                                                                                        | Type  | Reads | Likes | Comments | Collects |
| --- | ---------------- | ------------------------------------------------------------------------------------------------- | ----- | ----- | ----- | -------- | -------- |
| 1   | 2026-09-28 16:03 | [又想合资又想电动又想舒适智能——别克至境E7再推新](https://www.dcdapp.com/motor/m/feed/detail?link_source=share&group_id=7690492951143268888) | Video | 1145  | 37    | 7        | 0        |

(A pagination and selection hint appears at the bottom of the user list; the work list shows the latest 20 works by default, with a view-all prompt, a subscription hint, and a follow-up guide below.)

---

## Use Cases

| Scenario                    | Role                | Example Query                                     | Benefit                                                        |
| --------------------------- | ------------------- | ------------------------------------------------- | -------------------------------------------------------------- |
| Benchmark account research  | Content Creator     | "Find car review users on Dongchedi"              | Quickly locate niche accounts and browse their work performance |
| Influencer screening        | Brand / MCN         | "Dongchedi users related to Li Auto"              | Evaluate partnership value by followers and work data           |
| Competitor content tracking | Marketing Ops       | "What has user X published recently?"             | Keep up with a competitor's update cadence — subscribe to get yesterday's updates automatically |
| Industry content research   | Data Analyst        | "Search users and works related to BYD"           | Understand the brand's content ecosystem and creator landscape  |

---
