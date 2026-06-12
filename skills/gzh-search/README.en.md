# WeChat Article Search Crawler / gzh-search-crawler

---

## Overview

Search WeChat public account articles by keyword, display results in a terminal table, and auto-export CSV + interactive HTML reports.

**Core Value**

- **Keyword Search**: Real-time full-database search of verified public account articles from the past 30 days
- **Smart Scoring**: Three-factor ranking (relevance + popularity + recency)
- **Multi-Format Output**: Terminal table + CSV export + interactive HTML report
- **Interactive Report**: Built-in search box, cover image display, click-to-open original articles

**Target Users**

- 🔍 **Industry Researchers** — Track industry trends, batch export data for analysis
- 📝 **Content Creators** — Discover trending topics and creative inspiration
- 🏢 **Competitive Analysts** — Monitor competitor content strategies

---

## Features

### Core Features

- **Keyword Search**: Search by any keyword (max 10 characters), real-time results
- **Smart Ranking**: Three-factor scoring (relevance + popularity + recency), ties broken by reads
- **Tiered Fallback**: Ample results → normal browsing / fewer results → broader search / zero results → trending topics
- **Terminal Table**: Title, author, reads, likes, shares, favorites, publish date, article link
- **CSV Export**: Auto-generated UTF-8 BOM CSV for data analysis
- **HTML Report**: Built-in search (300ms debounce), cover display, paginated loading

---

## API Key Acquisition & Security

- The skill uses the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the device environment variable `REDFOX_API_KEY` before using this skill.
- Before providing your key, verify its origin, scope, validity period, and whether reset/revocation is supported.
- Never hardcode or expose the key in code, prompts, logs, or output files.

---

## Usage

Just say the keyword you want to search.

### Quick Reference

| Intent | Example | Result |
|--------|---------|--------|
| Hot search | "Search AI-related public account articles" | Returns trending AI articles, ranked by score |
| Competitor analysis | "Search recent articles on LLMs" | Captures competitor content, exports CSV for analysis |
| Inspiration | "Search trending articles on Xiaohongshu operations" | Gets topic angles and writing approaches |
| Trend research | "Search 2026 economy articles from public accounts" | Batch exports data for research reports |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|--------------|---------|
| Industry tracking | Industry analyst | "What's being discussed in AI lately?" | Quick overview of industry trends |
| Competitor analysis | Content ops | "Search competitor public account articles" | Understand content strategy and viral patterns |
| Inspiration gathering | Creator | "Search trending topics on content creation" | Get track-aligned inspiration, boost efficiency |
| Trend research | Researcher | "Batch export articles on a specific topic" | CSV export for deep data analysis |
