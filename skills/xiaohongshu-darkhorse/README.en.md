# Xiaohongshu Dark Horse Viral Posts / xiaohongshu-darkhorse

---

## Introduction

Give just one category or date, and it surfaces the dark-horse viral posts quietly gaining traction on Xiaohongshu: each post comes with engagement data, publish time and content analysis, plus an automatic summary of the title patterns and content traits behind the batch — so you can catch rising content directions fast.

**Key Value**

- 🏆 **Spot dark horses**: focuses on posts with standout recent engagement, regardless of follower size — often more revealing of near-term trends than top-influencer data
- 📊 **Complete data**: title, author, followers, publish time, likes, collects, comments, shares and total engagement in one table
- 💡 **Pattern distillation**: automatically breaks down title types and content theme distribution, extracting reusable writing highlights
- 🗂️ **Category & date**: 25 content categories, and rank lookup for any day within the past 30 days
- 🔔 **Subscribe & export**: daily 19:30 auto-push, plus export of a complete Xiaohongshu-style page (PDF ready)

**Who It's For**

- 📌 **Xiaohongshu creators** — discover dark-horse topics, learn viral writing and follow the trend
- 📈 **Content operators** — dark-horse posts are a flow indicator; catch rising content in time
- 📣 **MCNs / brands** — uncover potential accounts and assess their content breakout power

---

## Features

### Core Features

- 📊 **Category filter**: 25 content categories; query by category name or keyword
- 📅 **Date query**: look up the ranking for any day within the past 30 days; phrases like "yesterday" or "three days ago" also work
- 🏆 **TOP50 ranking**: sorted by total engagement descending, with likes, collects, comments and shares shown
- 💡 **Viral pattern analysis**: automatically breaks down title types and content themes, extracting reusable highlights
- 🔔 **Daily subscription**: after subscribing, the latest ranking is pushed automatically at 19:30 every day
- 📄 **File pack export**: generates a complete Xiaohongshu-style page, exportable to PDF for saving and sharing

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
| Default ranking | "Show the Xiaohongshu dark-horse viral ranking" | Outputs the all-categories ranking (latest available date by default) |
| Specify category | "Check the beauty dark-horse ranking" | Outputs that category's ranking only |
| Specify date | "Check the dark-horse ranking for 2026-09-20" | Queries the given ranking window start date |
| More results | "More" | Outputs the remaining TOP21-50 |
| Subscribe | "Subscribe" or reply "1" | Auto-pushes the latest TOP50 at 19:30 daily |
| Export file pack | Reply "2" | Generates a complete Xiaohongshu-style page, PDF ready |

### Sample Output

After a successful query, the ranking appears directly in the conversation as a Markdown table (illustrative):

| Rank | Post Info | Total Engagement | Likes | Comments | Collects | Shares | Publish Time |
|:----:|:----------|:----------------:|:-----:|:--------:|:--------:|:------:|:------------:|
| 🥇 | [Viral lipstick (III)](post link)<br>[Author](author page) (40k+ followers) | 52k | 20k+ | 979 | 5,267 | 1,115 | 08-23 09:04 |
| 🥈 | [How to pick sunscreen?](post link)<br>[Author](author page) (12k followers) | 38k | 15k | 620 | 3,900 | 880 | 08-23 14:20 |

Below the table comes the "Viral Pattern Analysis" (title trait table, content theme table, reference highlights) and a category query hint.

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Dark-horse topic discovery | Xiaohongshu creator | "Check the beauty dark-horse ranking" | Find rising content directions and follow up fast |
| Competitor dark-horse monitoring | Content operator / brand | "Check the home decor dark-horse ranking" | See accounts suddenly gaining traction and judge cooperation value |
| Viral pattern research | Content strategist | "Check the past week's trend sneakers dark-horse posts" | Compare rankings across windows to study title and theme patterns |

---

## Important Data Notes

- **Ranking type**: dark-horse viral ranking (single-day listing), not the seven-day weekly viral notes ranking; regardless of follower size, focusing on posts with standout recent engagement
- **Data update**: yesterday's data starts refreshing at 17:30 daily (before 17:30, yesterday's data is not yet generated)
- **Date scope**: any day within the past 30 days; the specified date is the window start date
- Each successful query may consume credits; unless explicitly asked, the assistant will not batch-query multiple categories