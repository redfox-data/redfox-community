# AI WeChat Feed / gzh-ai-feed

---

## Overview

Daily automatic scanning of AI WeChat public account articles, finding the hottest content by read count, auto-clustering into topics, and generating a styled HTML daily report.

**Core Value**

- **Hot Content Discovery**: Scans 200+ AI public account articles, ranked by read count
- **Smart Clustering**: Auto-discovers topic directions from daily content (Agent, LLM, AI Art...)
- **Visual Report**: Dark-themed HTML with cover images, metrics, article links, and date navigation
- **One-Click Subscription**: Enable daily auto-generation, reports saved locally

**Target Users**

- 📊 **AI Professionals** — Stay on top of AI WeChat content trends daily
- 📝 **Content Creators** — Discover trending topics and writing angles in the AI space
- 🔍 **Industry Researchers** — Track AI topic trends and discussion shifts

---

## Features

### Core Features

- **Daily Hot Scan**: Auto-retrieves 200+ AI public account articles, sorted by reads
- **Smart Topic Clustering**: Content-driven topic discovery, not fixed categories
- **Terminal Table Output**: Category + title + author + reads/likes/comments at a glance
- **Visual HTML Report**: Dark theme with cover images, metrics, date nav, full-database search
- **Keyword Filtering**: Custom focus directions for precise content filtering
- **Daily Subscription**: One-click cron setup for automated daily report generation

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

Describe your needs in natural language.

### Quick Reference

| Intent | Example | Result |
|--------|---------|--------|
| Today's report | "Generate today's AI public account daily report" | Auto-fetches hot articles, generates HTML report |
| Custom focus | "Focus on Agent and RAG articles" | Filters by specified keywords |
| Historical view | "Show me the AI report for May 26" | Retrieves hot content for a specific date |
| Subscribe | "Subscribe to daily AI public account reports" | Installs cron job for daily auto-generation |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|--------------|---------|
| Daily briefing | AI professional | "What's hot in AI today?" | 5-minute overview of AI content trends |
| Topic inspiration | Content writer | "What topics are trending in AI public accounts?" | Discover trending angles aligned with the buzz |
| Competitor monitoring | Content ops | "What AI content are competitors publishing?" | Track competitive dynamics, adjust strategy |
| Trend research | Industry analyst | "How have AI topics shifted this week?" | Track topic evolution, produce research reports |
