# AI Xiaohongshu Feed / xiaohongshu-ai-feed

---

## Overview

Daily auto-scan of AI-related Xiaohongshu posts, filtering the hottest content by engagement (likes / shares / comments), intelligently clustering them into topics, and generating a beautifully styled HTML daily report with cover images, metrics, and subscription support. Your one-stop solution to stay on top of the AI scene on Xiaohongshu.

**Core Value**

- Discover the hottest AI posts on Xiaohongshu daily, saving time from manual browsing
- Auto-clustering by content topics gives you a clear picture of what's trending in AI today
- Stunning dark-themed visual daily report with cover images and engagement metrics at a glance
- Daily auto-push with archived reports — browse history anytime

**Who It's For**

- 📱 Content operators — track AI trend styles and get creative inspiration
- ✍️ Xiaohongshu bloggers — learn from trending content and understand platform dynamics
- 📊 Industry observers — monitor AI content trends for market insights

---

## Features

### Core Capabilities

- Search Xiaohongshu AI posts by keywords, filtered by engagement metrics
- Support time-range queries (start time inclusive, end time exclusive) for flexible historical lookback
- Auto-detect topic directions from content tags and intelligently cluster into category cards
- Terminal table display: category + title + author + likes / shares / comments
- Generate a dark-themed visual daily report (Xiaohongshu red style) with cover images, metrics, direct links, and date navigation

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and get your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing your key, verify the source, scope, validity period, and whether it supports reset/revocation.
- Never hardcode or expose your key in code, prompts, logs, or output files.

---

## Usage

Simply describe your need in natural language — no commands to memorize.

### Quick Reference

| Intent | Example | Result |
|--------|---------|--------|
| View today's AI Xiaohongshu report | "Show me today's Xiaohongshu AI report" | Fetches the hottest AI posts and generates a clustered visual report |
| Search by custom keyword | "Search Xiaohongshu for ChatGPT content" | Filters by your keyword and generates a tailored report |
| Look up a past date | "Show me Xiaohongshu AI data from June 5th" | Retrieves the historical daily report for that date |
| Time range query | "Show me Xiaohongshu AI data from June 1st to June 5th" | Flexible lookback for any time period |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|---------------|---------|
| Daily AI trend tracking | Content operator | "Today's Xiaohongshu AI report" | Automatically get daily hot content, no manual browsing |
| Competitor content analysis | Xiaohongshu blogger | "Search Xiaohongshu for trending AI tutorials" | Understand trending styles and performance data |
| Hot topic review | Industry analyst | "Show me Xiaohongshu AI trends from June 1st" | Review historical data and analyze topic evolution |
