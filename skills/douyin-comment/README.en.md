# Douyin Comment Search / douyin-comment

---

## Overview

Paste a Douyin video link to pull up its comment data. AI automatically analyzes praise, complaints, needs, and competitor discussions. Supports paginated browsing and exports a polished HTML report for saving or sharing.

**Core Value**

- **Simple & instant**: Just drop a video link — no commands, no parameters, results in seconds.
- **Fresh content, no lag**: Every request pulls the latest comments directly from the platform, no stale caches.
- **AI reads the comments for you**: Automatically identifies praise, complaints, user needs, and competitor mentions across four categories, distilling key takeaways so you don't have to scroll through everything.
- **Unlimited pagination**: 20 comments per page, flip through as many as you like — even huge comment sections are no problem.
- **Shareable polished reports**: Dark-themed HTML report with data analysis and raw comments in one view, perfect for saving or forwarding to colleagues.

**Who It's For**

- 🔍 Douyin Creators — Quickly gauge audience reactions to your videos and find content optimization opportunities.
- 📊 Operations / Data Analysts — Track comment section sentiment dynamics and quantify user emotion shifts.
- 🏢 Brands / MCNs — Monitor competitor video comment trends to inform ad placement and content strategy.
- 🛒 E-commerce / Live-shopping — Analyze user needs and competitor mentions in product video comments to refine sales pitches.

---

## Features

### Core Features

- **Link extraction**: Paste a Douyin video link directly — the video ID is extracted automatically, no manual steps needed.
- **Comment retrieval**: Fetches top-level comments, 20 per page displayed in reverse chronological order.
- **AI-powered analysis**: Four-dimensional sentiment summary (positive / negative / user needs / competitor comparison) with awareness of Douyin meme culture.
- **Paginated browsing**: Flip through page by page, easily covering large comment sections.
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
| Search by link | "What are the comments like on https://www.douyin.com/video/7131700643076623629" | Automatically extracts video ID, fetches comments and displays analysis |
| Search by video ID | "Show me the comments on Douyin video 7131700643076623629" | Fetches comment data and presents analysis summary |
| Flip to next page | "Next page" | Loads subsequent comments and continues analysis |
| Export report | "Generate HTML" | Exports the current page's comment data and analysis as a polished HTML report |

### Sample Output

Here's what you'll receive:

📊 Video **7131700643076623629** — **20** comments fetched (Page 1), details below:

| # | Commenter | Comment | 👍 | 💬 | Time | IP |
|---|-----------|---------|----|----|------|-----|
| 1 | avatar username | This video is amazing... | 1223 | 213 | 02-12 15:30 | Guangdong |
| 2 | avatar username | Learned so much... | 856 | 45 | 02-12 14:20 | Beijing |
| … | … | … | … | … | … | … |

📈 Comment analysis summary covering four dimensions: positive feedback / negative feedback / user needs / competitor comparison.

📄 Currently on Page 1 (20 comments). Reply "next page" to continue.

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Content feedback analysis | Douyin Creator | "Check the comments on this video for me" | Quickly understand real audience sentiment and identify content improvements |
| Comment sentiment monitoring | Brand Operator | "Analyze the sentiment of this video's comments" | Automatically identify positive / negative / demand discussions and quantify sentiment distribution |
| Competitor comment research | MCN / Marketing | "See what people are saying in this competitor's comments" | Grasp competitor comment section focus and user preferences |
| Live-shopping performance evaluation | E-commerce Operator | "Analyze user needs in this product video's comments" | Extract purchase intent and competitor mentions to optimize conversion scripts |
