# Dongchedi Works Keyword Search / dongchedi-work-search

---

## Introduction

Enter a brand, model, vehicle series or any keyword to search related works on Dongchedi in one go: title, author, plays, likes, comments, publish time and work link presented in full, sorted by play count in descending order by default — see at a glance which related works are trending and how content is moving.

**Key Value**

- 🔍 **Keyword direct search**: search Dongchedi works by brand, model or vehicle series keywords
- 📊 **Complete metrics**: title, author, plays, likes, comments and publish time in one table
- 🔗 **Direct links**: full clickable work links for quick verification
- 🎬 **Optional content type**: supports "All" and "Video" content types
- ↕️ **Flexible sorting**: sorted by plays by default; switch to likes, comments or time

**Who It's For**

- 🚗 **Auto industry professionals** — quickly retrieve model-related works and track content heat and reputation trends
- 📣 **Brands / MCNs** — monitor how a brand or vehicle series performs on Dongchedi
- ✍️ **Content creators** — learn from trending model works to refine topics and content strategy

---

## Features

### Core Features

- 🔍 **Keyword works search**: search Dongchedi works by brand, model or vehicle series keywords
- 🎬 **Content type filter**: supports "All" and "Video" types, "All" by default
- 📊 **Core metrics display**: title, author, plays, likes, comments and publish time presented in a Markdown table
- 🔗 **Full work links**: complete links that open each work for easy verification
- 📄 **Flexible paging**: sorted by plays in descending order by default; browse more pages or limit the count as needed

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
| Keyword search | "Search Dongchedi works about Zhijie" | Outputs the works list for the keyword (plays desc by default) |
| Videos only | "Search Dongchedi Xiaomi SU7 videos" | Outputs video-type works only |
| Limit count | "Check Dongchedi Chengdu Auto Show content, show top 10" | Shows the first 10 entries only |
| Specify sorting | "Sort by likes" | Switches to likes descending |
| Next page | "Next page" | Outputs the next 20 entries |

### Sample Output

After a successful query, the works list appears directly in the conversation as a Markdown table (illustrative):

> Keyword: `智界` | Content type: All | Works on this page: 10 | More pages: yes

| # | Title | Author | Work ID | Plays | Likes | Comments | Publish Time | Work Link |
|---:|---|---|---|---:|---:|---:|---|---|
| 1 | Zhijie xxx test drive experience… | CreatorA / `author_a` | `71xxxxxxxx` | 1,234,567 | 12,345 | 1,234 | 2026-09-01 10:30 | [Open work](work link) |
| 2 | Zhijie yyy in-depth review… | CreatorB / `author_b` | `71yyyyyyyy` | 987,654 | 9,876 | 876 | 2026-09-02 14:00 | [Open work](work link) |

### Keyword Guidance

- Keep keywords to 6 characters or fewer; 2 characters works best (for example `零跑`, `智界`). Long compound phrases are more likely to time out.
- Split a long phrase into shorter terms and search them separately: start with the brand or series (for example `零跑`), then search the model if needed (for example `T03`).
- Search one keyword at a time. Multiple keywords separated by spaces or commas (for example `零跑 智界`, `零跑,智界`) are not supported in a single query.

When a query fails (timeout, network error, or task submission failure), it retries automatically in this order, at most twice:

1. Remove all spaces and retry, for example `零跑 T03` → `零跑T03`.
2. If that still fails, shorten to a single entity, for example `零跑T03` → `零跑` (prefer the brand or series; a letter-or-number model such as `T03` can be kept as the model term).
3. If both retries fail, the failure reason and the keywords already tried are shown, and no further retry is made.

Notes:

- A successful response with no works only shows "no data". Other keywords are not searched automatically.
- Separate keywords divided by spaces or commas are not merged or substituted. Choose one keyword and search again.

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Model content research | Auto professional | "What content is there about Zhijie on Dongchedi?" | Quickly grasp the heat and content trends of model-related works |
| Video material discovery | Content creator | "Search Dongchedi Xiaomi SU7 videos" | Quickly locate model-related video works |
| Brand content monitoring | Brand / MCN | "Check Dongchedi Chengdu Auto Show content" | Understand brand content performance during the show |
| Car-buying reference | Car buyer / enthusiast | "Show me videos about Zunjie" | View works and reviews of the model of interest in one place |

---

## Important Data Notes

- Each successful query may consume credits; query as needed
- Sorted by plays in descending order by default; switch to likes, comments, time or original order as needed
- When a search returns no results, only "no data" is shown and other keywords are not searched automatically. Automatic retry follows Keyword Guidance only when the query fails (timeout, network error, or task submission failure).
