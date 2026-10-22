# Facebook Comment Analysis / facebook-comment

---

## Introduction

Just paste a Facebook post URL to fetch its comments and get an AI sentiment summary across four dimensions—positive / negative / demand / competitor—so you can quickly see the user feedback and overall sentiment under a post.

**Core Value**

- **One-click comment fetching**: Paste a post URL to pull its comments, no manual scrolling or copy-pasting.
- **AI sentiment summary**: Automatically organizes feedback across positive, negative, user-demand and competitor dimensions for a fast read on overall reputation.
- **Visual retention**: Results can be turned into an interactive report for offline saving, sharing and review.

**Who It's For**

- 📊 **Brands / operators** — Monitor post comment sentiment and catch negative feedback or user demands early.
- 🎬 **Content creators** — Understand real audience feedback to guide topic and content optimization.
- 🔍 **Market research / competitor analysis** — Surface competitor comparisons and user preferences from comments.
- 🤝 **MCN / influencer business teams** — Assess the comment-section reputation and engagement quality of sponsored content.

---

## Features

### Core Features

- **Comment fetching**: Paste a post URL to get its comment data, including commenter, content, likes and publish time.
- **Paginated browsing**: Page through to view large volumes of comments.
- **AI sentiment summary**: Four-dimension sentiment analysis (positive / negative / demand / competitor), each point backed by representative comment keywords.
- **Visual report**: Generates an interactive report for offline saving and sharing; multiple browsed pages can be merged into one complete report.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please go to [RedFoxHub](https://redfox.hk?source=github) to register an account and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing a key, confirm its source, available scope, validity period, and whether it supports reset/revocation.
- Never hardcode or expose keys in plaintext in code, prompts, logs or output files.

---

## Usage Guide

Just describe your need in natural language—no commands to memorize.

### Common Phrases

| Intent               | Example phrase                              | Effect                                    |
| -------------------- | ------------------------------------------- | ----------------------------------------- |
| Analyze post comments| "Analyze the comments on this post: <post URL>" | Fetch page 1 of comments with an AI summary |
| Page for more        | "Next page"                                 | Load the next page, analyzed on cumulative data |
| Generate report      | "Generate an HTML visual report"            | Output an interactive report, merging multiple pages |

### Output Example

After fetching comments, you'll first see the current page's comment table and AI summary (illustrative):

```
📊 Post "<post URL>" — N comments fetched (page 1)

| Commenter | Content                 | 👍 Likes | Time        |
|-----------|-------------------------|:-------:|------------|
| Amy       | So useful, saving this!  | 128     | 10-18 12:07 |

📈 Comment Summary Analysis (based on N comments)
✅ Positive (62%) — Most users find the content useful…
⚠️ Negative (8%) — A few report slow loading…
💡 User demand (20%) — Requests for Chinese instructions…
🔍 Competitor sentiment (—) — No competitor mentioned
```

---

## Use Cases

| Scenario              | Role                  | Example question                              | Benefit                                   |
| --------------------- | --------------------- | --------------------------------------------- | ----------------------------------------- |
| Sentiment monitoring  | Brand / operator      | "Check if there's any negative tone in the comments" | Catch negative feedback early and respond |
| User feedback capture | Product / operator    | "Analyze what users are asking for in the comments"  | Aggregate real demands to guide optimization |
| Competitor comparison | Market research       | "Do the comments mention competitors, and how?"      | Surface competitor comparisons and preferences |
| Content review        | Creator / editor      | "Analyze this viral post's comments—how did viewers react?" | Understand audience reaction, build topic experience |

---

## Important Data Notes

- Comment publish times are converted to Beijing time (UTC+8). Paging relies on the cursor from the previous page—an empty cursor means no more data.
- Sentiment ratios are the share of each comment type; one comment may fall into multiple dimensions, so the four totals may exceed 100%. The summary is AI-generated and for reference.
