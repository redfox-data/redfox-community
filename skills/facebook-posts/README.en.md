# Facebook Page Post Extractor / facebook-posts

---

## Introduction

Just provide a Facebook page URL to batch-fetch its recent posts—caption, likes, comments, image/video links, publish time and author info—presented clearly in a table, with page-by-page browsing.

**Core Value**

- **One-click fetching**: Paste a page URL to pull recent posts, no manual scrolling or note-taking.
- **Complete data**: Captions, engagement (likes / comments), image and video links, publish time and post links—all included.
- **Page-by-page browsing**: Sorted by publish time (newest first), with paging to load more posts; fetched data is automatically de-duplicated and merged.

**Who It's For**

- 🎬 **Content creators / operators** — Break down competitor page content strategies and gather topic and copywriting ideas.
- 🤝 **MCN / influencer business teams** — Quickly review a creator's work and content quality before collaboration.
- 📊 **Brands / market research** — Track account content performance for sentiment and competitor analysis.
- 📈 **Data analysts** — Batch-fetch page post data for engagement and content-pattern analysis.

---

## Features

### Core Features

- **Page post fetching**: Enter a page URL to get its recent posts, including captions, likes, comments and other engagement data plus post links.
- **Automatic link recognition**: Supports `facebook.com/username` page URLs, recognized and extracted automatically.
- **Paginated browsing**: Page through to see more posts, up to 50 per page.
- **Table presentation**: Posts are summarized in a table in the conversation for easy browsing; full fields and all media links are saved for retention.

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

| Intent             | Example phrase                                        | Effect                                  |
| ------------------ | ----------------------------------------------------- | --------------------------------------- |
| Extract page posts | "Fetch the posts from this Facebook page: <page URL>" | Get 1 page of recent posts in a table   |
| Page for more      | "Continue, next page"                                 | Load more posts, merged and de-duplicated |

### Output Example

After fetching posts, you'll receive a table summary like this (illustrative):

```
📄 Facebook Page Posts · {author name}
Page: {page URL} ｜ Data time: {fetch time}
This page: {count} posts (accumulated: {total}) ｜ More data available: {yes / no}

| No. | Publish time     | Caption summary                | ❤️ Likes | 💬 Comments | Media    | Post link   |
|:---:|-----------------|-------------------------------|:-------:|:----------:|---------|------------|
| 1   | 2026-10-18 12:07 | My boyfriend says our little… | 3,564   | 77         | 🖼️ Image×1 | [View post] |
```

---

## Use Cases

| Scenario                     | Role                    | Example question                                   | Benefit                                   |
| ---------------------------- | ----------------------- | -------------------------------------------------- | ----------------------------------------- |
| Competitor content teardown  | Content ops / planner   | "Pull this competitor page's posts, I want to study topics" | Page through posts for topic / copy / engagement analysis |
| Creator work archiving       | Blogger / fan           | "Save all posts from this page in case they're deleted"    | Fetch all posts, keeping data and media links |
| Asset sourcing for re-editing| Editor / creator        | "Pull all posts, I want to process assets by media link"   | After full fetch, batch-process by media link |
| Own-account backup           | Brand / account operator| "Regularly fetch my own page's posts for backup"           | Keep page posts locally to prevent loss   |
| Influencer due diligence     | MCN / business          | "Before collaborating, review their page's recent work"    | Quickly assess content quality and tone   |

---

## Important Data Notes

- Posts are returned newest-first, with publish time converted to Beijing time (UTC+8); up to 50 per page. Paging relies on the cursor from the previous page—an empty cursor means no more data.
- Images and videos are temporary signed links with limited validity (hours to days). Download promptly if needed, or re-fetch to obtain fresh links.
