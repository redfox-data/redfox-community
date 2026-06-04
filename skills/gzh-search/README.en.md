# WeChat Public Account Search Crawler / gzh-search

---

## Introduction

Search WeChat public account articles by keyword — terminal table display + CSV export + interactive HTML report. Built-in public API Key — ready to use out of the box.

**Core Value**

- **Smart scoring**: Three-factor (relevance + popularity + recency) ranking for precise content discovery.
- **Dual-format output**: Real-time terminal view + persistent CSV/HTML archival for different scenarios.
- **Zero-config start**: Built-in public API Key (~10,000 free uses) — just start.

**Target Users**

- 📊 **Content operators** — Track industry hotspots and discover viral topics.
- 🏢 **Brands / marketing teams** — Competitor content analysis and topic sentiment monitoring.
- 📝 **Self-media creators** — Gather inspiration and understand niche dynamics.

---

## Features

### Core Capabilities

- **Keyword search**: Real-time queries across the full WeChat public account article database.
- **Smart scoring**: Three-factor (relevance + popularity + recency) ranking; ties broken by read count.
- **Terminal table**: Title, author, reads, likes, shares, saves, publish time, article link.
- **CSV export**: Auto-generated UTF-8 BOM-encoded CSV.
- **Interactive HTML report**: Built-in search, cover images, click-to-open article cards.
- **Tiered response**: Full results / guided broader search / trending fallback when results are sparse.

---

## API Key Info

A built-in public API Key provides ~**10,000 free uses** — zero configuration needed. When the quota runs out, register at [RedFoxHub](https://redfox.hk/login?source=github) for a personal API Token:

| Method | Command |
|--------|---------|
| **Environment variable** (recommended) | `export REDFOX_API_KEY=ak_your_key` |
| **CLI argument** | `--api-key ak_your_key` |
| **Config file** | `echo '{"api_key":"ak_your_key"}' > ~/.qoder/apis/redfox.json` |

---

## Usage Guide

Just describe what you want to search — no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|----------------|--------|
| Search a topic | "Search AI articles on WeChat" | Return related articles table + HTML report |
| Competitor analysis | "Find articles about LLMs on public accounts" | Display sorted by composite score |
| Export data | "Search Xiaohongshu marketing articles and export CSV" | Generate CSV + HTML |
| Specify count | "Find 50 AI-related articles" | Auto-paginate to fetch more |

---

## Use Cases

| Scenario | Role | Example query | Benefit |
|----------|------|---------------|---------|
| Industry trend tracking | Content ops | "What's trending in AI on WeChat" | Understand industry dynamics |
| Competitor content analysis | Brand team | "Search competitor posts about LLMs" | Analyze competitor content strategy |
| Inspiration gathering | Self-media | "Search viral Xiaohongshu marketing articles" | Get topics and writing angles |

### Important Data Notes

- Search scope covers **mid-tier and above public accounts** with articles published in the last 30 days.
- Keyword limit: **no more than 10 characters**; you'll be prompted to shorten if exceeded.
- To search a specific account's full history, use the `gzh-subscribe` skill instead.