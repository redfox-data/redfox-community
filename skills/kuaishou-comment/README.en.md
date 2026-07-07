# Kuaishou Comment Analysis / kuaishou-comment

---

## Overview

Paste a Kuaishou video link to fetch comment data, with paginated browsing, four-dimensional sentiment analysis (positive/negative/demand/competitor), and polished visual report generation.

**Core Value**

- **Paste & View Instantly**: Drop a video link to pull comment data — likes, replies, IP locations displayed in a clean table.
- **Smart Sentiment Analysis**: Automatically categorizes comments into positive, negative, demand, and competitor types with key phrases and representative quotes for a quick read on public opinion.
- **Paginated Browsing, Deeper with Every Page**: Flip through comments page by page, with cumulative analysis across all viewed pages for a complete picture.
- **One-Click Report Export**: Generate a dark-themed interactive HTML report; multi-page comments auto-merge and collapse beyond 3 pages for easy sharing and offline access.

**Target Users**

- 🔍 **Kuaishou Creators** — Quickly gauge audience feedback on your videos and discover content opportunities.
- 📊 **Operations / Data Analysts** — Track user sentiment on Kuaishou content and measure influencer impact and audience attitudes.
- 🏢 **Brands / MCNs** — Monitor competitor comment sections and industry keyword performance to inform content strategy.

---

## Features

### Core Capabilities

- **Comment Fetching**: Paste a video link to retrieve comments with cursor-based pagination.
- **Pinned Comment Highlighting**: Top comments are visually distinguished for quick identification.
- **Four-Dimensional Analysis**: Each query outputs ratios and summaries across positive, negative, demand, and competitor categories, with cumulative analysis on page turns.
- **Visual Reports**: Single-page HTML reports for current data, auto-merged multi-page reports with smart collapse beyond 3 pages.

---

## API Key Acquisition & Security

- This skill requires the environment variable `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` as a device environment variable before using this skill.
- Before providing the key, verify its source, scope, validity period, and whether it supports reset/revocation.
- Never hardcode or expose the key in code, prompts, logs, or output files.

---

## Usage Guide

Send a Kuaishou video link or opusId in natural language — no commands to memorize.

### Quick Reference

| Intent | Example | Result |
| ------ | ------- | ------ |
| View comments | "https://www.kuaishou.com/short-video/3x4ibfzs5e68yxu — what are people saying?" | Comment table + four-dimensional sentiment analysis |
| Use video ID directly | "Check comments on video 3x4ibfzs5e68yxu" | Same as above, skip link extraction |
| Next page | "Next page" | Fetch the next page of comments with cumulative analysis |
| Export report | "Generate HTML" | Merges all browsed pages into a single complete report |

### Output Example

After querying you'll receive:

📊 **Comment Table**: All comments on the current page, including username, content, likes, replies, timestamp, and IP location.

📈 **AI Sentiment Summary**: Four-dimensional analysis with ratios, summaries, and representative comment quotes.

📄 **Pagination Hint**: If more pages are available, prompts you to reply "Next page" to continue.

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Viewer feedback | Creator | "What are people saying under my latest video?" | Quickly gauge audience reactions and engage |
| Sentiment monitoring | Brand operator | "Show me the comment sentiment on this product" | Track public opinion for data-driven decisions |
| Content ideation | Content strategist | "What are viewers discussing in trending videos?" | Mine comment sections for audience needs and topic inspiration |
| Data analysis | Data analyst | "Analyze the emotional distribution of comments on this video" | Quantify comment data into a structured report |
