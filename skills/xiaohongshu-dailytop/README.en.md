# Xiaohongshu Daily Viral Notes / xiaohongshu-dailytop

---

## Introduction

Query the TOP50 Xiaohongshu notes with the highest same-day engagement growth by keyword or track, with automatic breakdown of titles, content patterns, and trends — helping creators and operators catch the traffic wave and plan the next post.

**Core Value**

- Tracks notes with the highest engagement increment today, not cumulative totals — capturing content that is actively exploding right now
- Three-dimension analysis (hot content, viral titles, top-data posts) delivered in one pass, ready to feed directly into topic planning
- Supports daily 19:30 subscription pushes to continuously track track trend changes

**Who It's For**

- ✍️ Beauty / fashion and other vertical creators — find daily benchmark notes and extract replicable title structures and content formulas
- 📢 FMCG brand operators — stay on top of today's breakout content to guide placements and seeding direction
- 🔍 MCN talent scouts — spot low-follower high-engagement breakout notes to assess account growth potential

---

## Features

### Core Capabilities

- **Single-day breakout rankings**: Fetch today's hot notes TOP50, supporting 25 vertical categories with precise matching
- **Smart pattern analysis**: Generate three-dimension reports — hot content analysis, viral title analysis, top-data post analysis
- **Multi-dimension data display**: Full presentation of total engagement, likes, comments, collects, shares, and new incremental data
- **Auto subscription push**: Subscribe to receive the latest rankings at a fixed time of 19:30 every day

### Highlights

- Input "mascara" and it auto-matches "Beauty & Makeup" — no manual category selection needed
- First output shows TOP20; reply "load more" to get the rest, with HTML synced to full data
- Ranking table and HTML page share the same data source and order — fully consistent

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
| Query today's virals | `Show me viral notes about mascara` | Auto-matches category, outputs today's breakout TOP20 + three-dimension analysis + HTML + subscription option |
| Query general hot content | `What's trending on Xiaohongshu lately?` | Uses "All" category, full four-section output |
| Query specific date | `Show beauty daily viral notes for 2026-04-20` | Queries single-day breakout rankings for the specified date and category |
| Load more | Reply "load more" | Shows TOP21 to end; HTML refreshes to full data |
| Subscribe to push | Reply `1` after output completes | Activates daily 19:30 push of Xiaohongshu daily viral notes TOP50 |

### Output Example

Each query produces four fixed sections: daily viral notes rankings → three-dimension pattern analysis → HTML visual page → subscription service options.

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| -------- | ---- | ---------------- | ------- |
| Daily viral inspiration | Beauty / fashion creator | `Show today's beauty viral notes` | Extract today's viral title structures and content patterns for the next post |
| Real-time hot topic tracking | Brand Xiaohongshu operator | `Subscribe to daily fashion breakout push` | Continuously track track changes, respond to hot topics faster |
| Rising note discovery | MCN talent scout | `What low-follower high-engagement food breakouts are there today?` | Use new engagement data increments to discover growth-stage accounts |
| Daily data review | Growth / data analyst | `Fetch today's full tech TOP50 and export HTML` | Export PDF for daily reports with a unified, archivable data source |
