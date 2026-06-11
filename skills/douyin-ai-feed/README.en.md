# AI Douyin Feed / douyin-ai-feed

---

## Overview

Daily auto-scan of AI-related Douyin content, filtering the hottest posts by engagement (likes / shares / comments), intelligently clustering them into topics, and generating a beautifully styled HTML daily report with cover images, metrics, and subscription support. Your one-stop solution to stay on top of the AI scene on Douyin.

**Core Value**

- Discover the hottest AI posts on Douyin daily, saving time from manual browsing
- Auto-clustering by content topics gives you a clear picture of what's trending in AI today
- Stunning dark-themed visual daily report with cover images and engagement metrics at a glance
- Daily auto-push with archived reports — browse history anytime

**Who It's For**

- 📱 Content operators — track AI trend styles and get creative inspiration
- 🎬 AI creators — learn from trending content and understand platform dynamics
- 📊 Industry observers — monitor AI content trends for market insights

---

## Features

### Core Capabilities

- Search Douyin AI posts by keywords, filtered by engagement metrics
- Auto-detect topic directions from content tags and intelligently cluster into category cards
- Terminal table display: category + title + author + likes / shares / comments
- Generate a dark-themed visual daily report (Douyin cyan style) with cover images, metrics, direct links, and date navigation

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
| View today's AI Douyin report | "Show me today's Douyin AI report" | Fetches the hottest AI posts and generates a clustered visual report |
| Search by custom keyword | "Search Douyin for ChatGPT content" | Filters by your keyword and generates a tailored report |
| Look up a past date | "Show me Douyin AI data from June 5th" | Retrieves the historical daily report for that date |

### Sample Output

Running the skill generates a dark-themed visual daily report including:
- Header with date, category stats, average likes, and total shares
- Category cards displaying posts (cover image + title + author + engagement metrics)
- Date navigation to browse adjacent days

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|---------------|---------|
| Daily AI trend tracking | Content operator | "Today's AI Douyin report" | Automatically get daily hot content, no manual browsing |
| Competitor content analysis | AI creator | "Search Douyin for trending AI short dramas" | Understand trending styles and performance data |
| Hot topic review | Industry analyst | "Show me Douyin AI trends from June 1st" | Review historical data and analyze topic evolution |
