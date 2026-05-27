# WeChat Fastest Growing Accounts / wechat-fastest-growing

---

## Introduction

Directly connected to the official reading growth rate rankings, browse the top public accounts by reading growth speed for any given date. Only the highest-read article per author is shown, with titles linked directly to the original post.

**Core Value**

- Ranking data comes from official APIs, displayed as-is without manual editing or reordering
- Accepts natural language date input — "latest", "yesterday", or "March 15" all work
- Optionally drill into viral article patterns and track-level strategy summaries based on real ranking data

**Who It's For**

- ✍️ WeChat Official Account operators — quickly discover the fastest-growing benchmark accounts and viral topics in your track
- 📋 Content editors — use rankings for topic review sessions and extract replicable playbooks
- 🔍 Researchers / analysts — observe track heat shifts and single-day data fluctuations

---

## Features

### Core Capabilities

- **Growth rate rankings**: Fetch reading growth rate rankings by date, output as raw Markdown table with clickable links to original articles
- **Natural language date parsing**: Supports "latest", "yesterday", "YYYY-MM-DD"; auto-falls back to the day before if yesterday's data is unavailable
- **Growth trend analysis**: Based on real ranking data, outputs a viral article analysis table (≤5 entries), a content-type analysis table (≤5 entries), and a 300–500 word summary
- **Composite score index**: Rankings include a weighted score field measuring the combined performance of reads, forwards, likes, and "Top Reads"

### Highlights

- Script output is shown verbatim — the model is not allowed to rewrite or reorder ranking content, ensuring data integrity
- Any date within the past 30 days is queryable; out-of-range requests are clearly flagged rather than fabricated

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?souce=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before using a key, confirm its source, scope, expiry, and whether it supports reset or revocation.
- Never hard-code or expose the key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
| ------ | -------------- | ------ |
| Latest rankings | `WeChat growth rankings` / `latest growth chart` | Fetches yesterday's (or most recent available) rankings and displays the raw table |
| Specific date | `Show me the growth rankings for March 15` | Fetches with `rankDate=2026-03-15` and displays verbatim |
| Trend analysis | `Which accounts grew fastest recently, and what do they have in common?` | Outputs rankings first, then two analysis tables and a summary |
| Viral vs. low-read comparison | `Compare the viral and low-read articles from one account on the list` | Analyzes topic and title differences for the same account using ranking data |

### Output Example

Query results are displayed as a raw Markdown table with columns for rank, account name (clickable), growth rate, composite score index, and more. When analysis is requested, three additional output blocks appear below the table.

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| -------- | ---- | ---------------- | ------- |
| Find benchmark accounts | Account operator | `What accounts are on today's growth chart?` | Quickly identify the fastest-growing accounts and viral topic directions |
| Topic review | Content editor | `Show the latest rankings and analyze viral article patterns` | Get viral article and content-type analysis tables to inform the next round of topics |
| Date-specific review | Analyst | `Pull the growth rankings for April 1` | Check single-day data fluctuations and click titles to verify originals |
| Track observation | Researcher | `Which accounts appear repeatedly across several days of rankings?` | Identify high-frequency accounts and track shifts in track heat |
