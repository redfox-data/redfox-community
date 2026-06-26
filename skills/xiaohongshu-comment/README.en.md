# Xiaohongshu Comment Analysis / xiaohongshu-comment

---

## Overview

Paste a Xiaohongshu note link to pull up its comment data. AI automatically analyzes praise, complaints, needs, and competitor discussions. Supports cursor-based pagination and exports a polished HTML report for saving or sharing.

**Core Value**

- **Simple & instant**: Just drop a note link — no commands, no parameters, results in seconds.
- **Fresh content, no lag**: Every request pulls the latest comments directly from the platform, no stale caches.
- **AI reads the comments for you**: Automatically identifies praise, complaints, user needs, and competitor mentions across four categories, distilling key takeaways so you don't have to scroll through everything.
- **Unlimited pagination**: 20 comments per page, cursor-based pagination — flip through as many pages as you like.
- **Shareable polished reports**: Dark-themed HTML report with data analysis and raw comments in one view, perfect for saving or forwarding to colleagues.

**Who It's For**

- 🔍 Xiaohongshu Creators — Quickly gauge audience reactions to your notes and find content optimization opportunities.
- 📊 Operations / Data Analysts — Track comment section sentiment dynamics and quantify user emotion shifts.
- 🏢 Brands / MCNs — Monitor competitor note comment trends to inform ad placement and content strategy.
- 🛒 E-commerce / Social Commerce — Analyze user needs and competitor mentions in product notes to refine recommendation copy.

---

## Features

### Core Features

- **Link extraction**: Paste a Xiaohongshu note link directly — the note ID is extracted automatically, no manual steps needed.
- **Comment retrieval**: Fetches top-level comments, 20 per page displayed in reverse chronological order.
- **AI-powered analysis**: Four-dimensional sentiment summary (positive / negative / user needs / competitor comparison) with awareness of Xiaohongshu community culture.
- **Cursor-based pagination**: Browse page by page via cursor, easily covering large comment sections.
- **Pinned comment highlight**: Pinned comments are automatically highlighted so important voices stand out.
- **Visual report**: Dark-themed HTML report with raw comment tables and AI analysis summaries, fully available offline.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing your key, verify its source, scope, validity period, and whether it supports reset/revocation.
- Do not hardcode or expose the key in plain text within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe what you need in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Phrase | Result |
| ------ | -------------- | ------ |
| Search by link | "What are the comments like on https://www.xiaohongshu.com/explore/6a2ac3020000000035022d8e" | Automatically extracts note ID, fetches comments and displays analysis |
| Search by note ID | "Show me the comments on Xiaohongshu note 6a2ac3020000000035022d8e" | Fetches comment data and presents analysis summary |
| Flip to next page | "Next page" | Loads subsequent comments via cursor and continues analysis |
| Export report | "Generate HTML" | Exports the current page's comment data and analysis as a polished HTML report |

### Sample Output

Here's what you'll receive:

📊 Note **6a2ac3020000000035022d8e** — **20** comments fetched (Page 1), details below:

| # | Commenter | Comment | 👍 | 💬 | Time | IP |
|---|-----------|---------|----|----|------|-----|
| 1 | avatar username | This looks amazing... | 1223 | 213 | 02-12 15:30 | Guangdong |
| 2 | avatar username | Bookmarked!... | 856 | 45 | 02-12 14:20 | Beijing |
| … | … | … | … | … | … | … |

📈 Comment analysis summary covering four dimensions: positive feedback / negative feedback / user needs / competitor comparison.

📄 Currently on Page 1 (20 comments). Reply "next page" to continue.

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Content feedback analysis | Xiaohongshu Creator | "Check the comments on this note for me" | Quickly understand real audience sentiment and identify content improvements |
| Comment sentiment monitoring | Brand Operator | "Analyze the sentiment of this note's comments" | Automatically identify positive / negative / demand discussions and quantify sentiment distribution |
| Competitor comment research | MCN / Marketing | "See what people are saying in this competitor's note comments" | Grasp competitor comment section focus and user preferences |
| Social commerce evaluation | E-commerce Operator | "Analyze user needs in this product note's comments" | Extract purchase intent and competitor mentions to optimize recommendation scripts |
