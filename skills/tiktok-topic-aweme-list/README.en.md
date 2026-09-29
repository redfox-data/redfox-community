# TikTok Topic Works Data / tiktok-topic-aweme-list

---

## Introduction

Enter a TikTok topic ID to get the works list under that topic in one go: plays, likes, comments, shares and work links presented in full, sorted by play count in descending order by default — see at a glance which works under a topic are performing best.

**Key Value**

- 🎯 **Topic-centric view**: works aggregated around a topic, showing its heat distribution at a glance
- 📊 **Complete metrics**: plays, likes, comments and shares in one table
- 🔗 **Direct links**: full clickable work links for quick verification
- ↕️ **Flexible sorting**: sort by plays, likes, comments or shares

**Who It's For**

- 🧑‍💻 **TikTok content operators** — track topic trends and catch content directions in time
- 📣 **Brands / MCNs** — evaluate topic value and spot standout works and creators
- ✍️ **Creators** — learn from top-performing works to refine topics and content strategy

---

## Features

### Core Features

- 🔍 **Topic works query**: query the works list under a topic by topic ID
- 📊 **Core metrics display**: plays, likes, comments and shares presented in a Markdown table
- 🔗 **Full work links**: complete links that open each work for easy verification
- ↕️ **Multi-dimension sorting**: sorted by plays by default; switch to likes, comments or shares
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
| Query topic works | "Check the works under topic 2525872, topic name charlidamelio" | Outputs that topic's works list (plays desc by default) |
| Specify sorting | "Sort by likes" | Switches to likes descending |
| Next page | "Next page" | Continues with the next page based on the previous cursor |
| Find topic from a work link | "Check the topic data of this video" | Extracts the topic ID from the work page first, then queries |
| View raw data | "Show the raw response" | Outputs the raw data content |

### Sample Output

After a successful query, the works list appears directly in the conversation as a Markdown table (illustrative):

> Topic: `#charlidamelio` | Works on this page: 10 | More pages: yes

| # | Author | Work ID | Plays | Likes | Comments | Shares | Work Link | Content Summary | Topic |
|---:|---|---|---:|---:|---:|---:|---|---|---|
| 1 | CreatorA / `creator_a` | `7xxxxxxxxxx` | 12,345,678 | 987,654 | 12,345 | 6,789 | [Open work](work link) | Topic work content summary… | `#charlidamelio` |
| 2 | CreatorB / `creator_b` | `7yyyyyyyyyy` | 9,876,543 | 765,432 | 9,876 | 5,432 | [Open work](work link) | Topic work content summary… | `#charlidamelio` |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Topic heat tracking | Content operator | "Which works in this challenge topic have the most plays?" | Lock onto top-performing works and catch content directions |
| Promotion reference | Brand / MCN | "Show me the well-performing works in this topic" | Discover quality works and creators to support promotion decisions |
| Topic selection reference | Creator | "Check the works data of this topic" | Learn from the topics and presentation of top works |
| Data verification | Data / research staff | "Pull the works data of this topic" | Get structured work metrics for further analysis |

---

## Important Data Notes

- Each successful query may consume credits; query as needed
- Sorted by plays in descending order by default; switch to likes, comments or shares as needed
- When a topic has many works, browse page by page following the paging hints
