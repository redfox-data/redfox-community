# Bilibili Portfolio Search / bilibili-portfolio-search

---

## Overview

Instantly query any Bilibili creator's full video catalog, sorted by play count with pagination support, to quickly understand any account's content performance.

**Core Value**

- **Real-time data**: Fetch the latest published videos directly—no caching, no historical snapshots.
- **Play count sorting**: Results are automatically sorted by play count in descending order, surfacing top performers at a glance.
- **Paginated browsing**: Cursor-based pagination lets you dive deep into a creator's entire back catalog.

**Intended Users**

- 🎬 **Content creators** — Analyze peer creators' content performance and benchmark against viral topics.
- 📊 **MCN / operations teams** — Batch-review signed creators' uploads and quickly track account output.
- 🔍 **Content researchers** — Sort by play count to efficiently identify high-impact video samples.

---

## Features

### Core Capabilities

- **UID-based precision query**: Enter a creator's UID to fetch all public uploads in real time.
- **Cursor-based pagination**: Load more videos page by page without missing a single upload.
- **Play count descending sort**: Results are automatically ranked from highest to lowest play count, prioritizing top performers.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe what you need in natural language—no commands to memorize.

### Quick Reference

| Intent               | Example phrase                                                                  | Result                                                      |
| -------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| Query video catalog  | "Look up the videos from Bilibili creator 946974"                              | Returns the creator's latest uploads, sorted by play count  |
| Query via URL        | "Check out this Bilibili account's videos: bilibili.com/space/12345"           | Automatically extracts the UID and fetches the video list   |
| Paginate             | "Next page" / "Show me more"                                                   | Automatically uses the cursor to load the next page         |

### Output Example

After a successful query, you'll see creator info and a video table:

> 📊 Creator "**SomeCreator**" (UID: 946974) has **128** videos total, showing **20** items. Here are the details:

| #   | Video Title          | Plays   | Danmaku | Duration | Published  |
| --- | -------------------- | ------- | ------- | -------- | ---------- |
| 1   | [Title Text](link)   | 1.05M   | 12K     | 15:21:04 | 2026-06-20 |
| 2   | [Title Text](link)   | 885K    | 9800    | 08:32    | 2026-06-15 |

> 📄 More videos available. Reply "next page" to continue.

---

## Use Cases

| Scenario             | Role               | Example question                                                     | Benefit                                                       |
| -------------------- | ------------------ | -------------------------------------------------------------------- | ------------------------------------------------------------- |
| Benchmark analysis   | Content creator    | "Look up this creator's videos and find which ones got the most plays" | Quickly identify top performers to benchmark topics and titles |
| Account review       | MCN / ops team     | "Show me what videos my signed creator has posted recently"          | Efficiently track creator output to support ops decisions      |
| Sample collection    | Content researcher | "Pull the video list from this Bilibili account"                     | Get high-impact video samples sorted by play count             |
| Casual browsing      | Bilibili viewer    | "How many videos has my favorite creator posted in total?"           | View the full upload history with pagination support           |

---
