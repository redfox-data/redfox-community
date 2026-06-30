# Bilibili Comment Analyzer / bilibili-comment

---

## Overview

Enter any Bilibili video link or BV ID to **instantly retrieve comment data**. AI automatically performs four-dimension sentiment analysis (positive / negative / demand / competitor) and generates an interactive HTML report for offline saving.

**Feature Overview**

Bilibili Comment Analyzer is an intelligent comment insight tool built for content creators, UP owners, and brand operators. It pulls first-level comments in real time via the RedFox API — 20 comments per page with pagination support. The AI deeply understands Bilibili meme culture (awsl / yyds / 爷青回 and other barrage slang) and delivers four-dimension analysis with representative comment citations, then generates a dark-themed interactive HTML report for easy saving and sharing.

**Core Value**

- **Real-time comment retrieval**: Paste a link and get the latest comments instantly — no manual scrolling through the comment section.
- **Bilibili meme culture understanding**: AI identifies barrage slang and meme context for more accurate analysis results.
- **Structured four-dimension analysis**: Positive / negative / demand / competitor layers clearly separated, each with representative comment citations to capture the core of public sentiment quickly.

**Intended Users**

- 🎬 **UP owners** — Review audience feedback and refine topic and content strategy.
- 🏢 **Brand operators** — Monitor public sentiment and detect user voices and risk signals promptly.
- 📊 **Content planners / product managers** — Mine competitor comments and research genuine user needs.

---

## Features

### Core Capabilities

- **Comment retrieval**: Enter a BV ID or video link to automatically pull first-level comments, 20 per page
- **Pagination**: Navigate with natural language — "next page", "page 3", etc. — to browse large volumes of comments progressively
- **Four-dimension AI analysis**: Positive / negative / demand / competitor sentiment analysis, each with representative comment citations and percentage breakdown
- **Pinned comment marking**: Pinned comments are specially highlighted for quick identification
- **HTML report**: Dark-themed interactive report for offline saving and sharing

### Highlights

- **Bilibili meme culture understanding**: Recognizes awsl / yyds / xswl / 爷青回 / 下次一定 and other barrage slang in their real context
- **Complete data display**: Work details (views / likes / coins / favorites / danmaku, etc.) and full comment table — no truncation
- **Encoding-safe backfill**: Intelligent encoding ensures Chinese analysis content is injected into reports without corruption

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFox Hub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFox Hub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` as a device environment variable before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your video in natural language — no fixed commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|---------------|--------|
| View video comments | "Show me the comments for BV1xx411c7mD" | Fetches page 1 comments + AI summary |
| Query via link | Paste `https://www.bilibili.com/video/BV1xx411c7mD` | Auto-extracts BV ID and retrieves comments |
| Paginate | "Next page" / "Page 3" | Reuses current video BV ID, fetches specified page |
| Generate report | "Yes" / "Generate HTML" | Backfills AI analysis, generates interactive HTML report |

### Output Example

After a successful query, you receive in sequence:

**Work Details**

> 🎬 **Video Title**
>
> UP: [Username](profile link) | Published: 2024-01-01 | Duration: 12:34
>
> ▶ 12.5w 👍 3.2w 🪙 1.8w ⭐ 2.1w 🔄 5.6k 💬 1.2k 📝 8.9k

**Comment Table** (all comments on current page)

| # | Username | Comment | 👍 | Time | IP |
|---|---------|---------|-----|------|-----|
| 1 | [Username](profile) | Comment content... | 1223 | 01-12 15:30 | Guangdong |

**Four-dimension Sentiment Analysis** (AI summary with representative citations)

**Prompt asking whether to generate an HTML visualization report**

---

## Use Cases

| Scenario | Role | Example question | Benefit |
|----------|------|-----------------|---------|
| Content review | UP owner | "How are the comments on this video?" | Quickly understand audience feedback and refine content strategy |
| Sentiment monitoring | Brand operator | "Analyze the negative comments on this video" | Detect crisis signals early and plan response |
| Competitor analysis | Content planner | "Analyze user comments on a competitor's video" | Understand competitor strengths and weaknesses to find differentiation |
| User research | Product manager | "What user needs are mentioned in the comments?" | Uncover genuine needs to guide product iteration |

---
