# Xiaohongshu Low-Follower Viral Notes / xiaohongshu-lowtop

---

## Introduction

Focused on uncovering high-engagement notes from accounts with fewer than 5,000 followers on Xiaohongshu, helping you find replicable topic ideas and writing styles from the most authentic user preference signals.

**Core Value**

- Low-follower viral notes reflect genuine user interest more purely than top-KOL data — the purest signal of content quality
- Every note comes with full engagement data, plus automatic breakdown of title patterns and content characteristics
- Supports daily subscriptions at 19:30 and HTML file export (PDF-ready) in Xiaohongshu's visual style

**Who It's For**

- 📌 Xiaohongshu creators — find topic inspiration, study title techniques, and track track trends
- 📌 Content ops / brand teams — low-follower viral notes are the most authentic user preference signal, more reliable than big-KOL data
- 📌 MCN agencies — discover rising creators and assess content trends

---

## Features

### Core Capabilities

- **Category filtering**: Covers 25 content categories from General Hot to Parenting — query by category name or keyword
- **TOP50 rankings**: Sorted by total engagement, each note shows likes, collects, comments, and shares
- **Viral pattern analysis**: Automatically breaks down title types and content topic distribution, extracting reusable writing insights
- **Daily subscription push**: Subscribe to receive the latest rankings automatically at 19:30 every day
- **File export**: Generates a full Xiaohongshu-style page exportable as PDF for easy archiving and sharing

### Data Criteria

Query scope: follower count below 5,000, note like count above 500

Each note includes: title, author, follower count, publish date, likes, comments, collects, shares, total engagement

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
| Query category low-follower virals | `Show me low-follower viral notes in beauty` | Fetches beauty category TOP50, outputs ranking table and viral pattern analysis |
| Query specific date | `Low-follower home décor virals on April 20` | Queries the specified date for that category |
| Subscribe to daily push | Reply "subscribe" on the results page | Automatically receives the latest rankings at 19:30 every day |
| Export file package | Reply `2` on the results page | Generates a full Xiaohongshu-style page exportable as PDF |

### Output Example

Results are delivered in sequence: viral notes table (sorted by engagement) → viral pattern analysis (title types + content topic distribution) → function entry (subscribe / export / load more).

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| -------- | ---- | ---------------- | ------- |
| Daily topic inspiration | Xiaohongshu creator | `Show low-follower virals in beauty` | Browse TOP50 topics and use viral analysis to quickly find replicable titles and writing approaches |
| Competitor content monitoring | Content ops | `Check low-follower home décor virals regularly` | Track content topic shifts and title pattern changes to spot emerging topic directions |
| Viral pattern research | Content strategy analyst | `Query the same category over multiple days` | Compare title type ratios across dates; export file packages for analysis reports |
| Rising creator discovery | MCN agency | `What low-follower high-engagement food notes are there?` | Identify small accounts breaking through with strong content |
