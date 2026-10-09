# TikTok Keyword Topic Search / tiktok-keyword-topic-search

---

## Introduction

Enter a keyword to search TikTok topics in one go: topic name, topic ID, usage count, view count and participant count presented in full, sorted by usage count in descending order by default; enter a topic ID to keep browsing the works under that topic — see topic heat and work performance at a glance.

**Key Value**

- 🔍 **Keyword to topic**: search TikTok topics with keywords in Chinese, English, Japanese and more
- 📊 **Complete metrics**: usage count, view count, participant count and more in one table
- 🔗 **Direct links**: full clickable work links for quick verification
- 🔁 **Search-then-browse loop**: search topics → get topic ID → browse topic works, all in one flow
- ↕️ **Flexible sorting**: topics by usage/view count; works by plays/likes/comments/shares

**Who It's For**

- 🧑‍💻 **TikTok content operators** — track topic trends and catch content directions in time
- 📣 **Brands / MCNs** — evaluate topic value and spot hot topics and standout works
- ✍️ **Creators** — learn from hot topics and top works to refine topics and content strategy
- 📈 **Data / research staff** — get structured topic and work data for trend and product analysis

---

## Features

### Core Features

- 🔍 **Keyword topic search**: search TikTok topics with any keyword
- 📊 **Core metrics display**: topic name, topic ID, usage count, view count, participant count and more in a Markdown table
- 🔁 **Topic works query**: query the works list under a topic by topic ID
- ↕️ **Multi-dimension sorting**: topics sorted by usage count by default, switch to view count or participant count; works sorted by plays by default, switch to likes, comments or shares
- 📄 **Paged browsing**: includes next-page cursor info to continue on demand

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
| Search topics by keyword | "Search TikTok topics about cat" | Outputs the topic list for the keyword (usage count desc by default) |
| Browse topic works | "Check the works under topic ID 7551" | Outputs that topic's works list (plays desc by default) |
| Specify sorting | "Sort by likes" | Switches to likes descending |
| Next page | "Next page" | Continues with the next page based on the previous cursor |
| View raw data | "Show the raw response" | Outputs the raw data content |

### Sample Output

After a successful topic search, the topic list appears directly in the conversation as a Markdown table (illustrative):

> Keyword: `cat` | Topics on this page: 20 | More pages: yes

| # | Topic Name | Topic ID | Usage | Views | Participants | Challenge |
|---:|---|---|---:|---:|---:|---:|
| 1 | cat | `7551` | 12,345,678 | 987,654,321 | 123,456 | Challenge |
| 2 | cats | `5216` | 9,876,543 | 765,432,109 | 98,765 | - |

After a successful topic works query, the works list appears the same way (illustrative):

> Topic: `#cat` | Works on this page: 10 | More pages: yes

| # | Author | Work ID | Plays | Likes | Comments | Shares | Work Link | Content Summary | Topic |
|---:|---|---|---:|---:|---:|---:|---|---|---|
| 1 | CreatorA / `creator_a` | `7xxxxxxxxxx` | 12,345,678 | 987,654 | 12,345 | 6,789 | [Open work](work link) | Topic work content summary… | `#cat` |
| 2 | CreatorB / `creator_b` | `7yyyyyyyyyy` | 9,876,543 | 765,432 | 9,876 | 5,432 | [Open work](work link) | Topic work content summary… | `#cat` |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Topic heat tracking | Content operator | "Search TikTok topics about cat" | Lock onto keyword-related topics and their heat distribution |
| Hot topic discovery | Brand / MCN | "Show me the well-performing works in this topic" | Discover hot topics and quality works to support promotion decisions |
| Topic selection reference | Creator | "Check the works data of this topic" | Learn from the topics and presentation of top works |
| Data verification | Data / research staff | "Pull the works data of this topic" | Get structured topic and work metrics for further analysis |

---

## Important Data Notes

- Each successful query may consume credits; query as needed
- Topics sorted by usage count in descending order by default; switch to view count or participant count as needed
- Works sorted by plays in descending order by default; switch to likes, comments or shares as needed
- When there are many topics or works, browse page by page following the paging hints
