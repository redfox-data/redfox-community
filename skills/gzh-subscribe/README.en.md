# WeChat Subscription Tracker / gzh-subscribe

---

## Overview

Your public account content radar. Subscribe to competitors, peers, and followed accounts — auto-fetch daily posts with clear table display and HTML daily report.

**Core Value**

- **Inbox-Style Subscription**: Subscribe to public accounts like newsletters, up to 20, name-only
- **Daily 9 AM Delivery**: One-click cron setup for automated curated daily reports
- **Three-Category Grouping**: Competitors / Peers / Favorites, organized for easy management
- **Key Metrics at a Glance**: Publish date, title, reads, likes — article link one-click away

**Target Users**

- 🏢 **Competitive Monitors** — Track competitor posts and stay informed
- 📝 **Content Creators** — Follow industry leaders for creative inspiration
- 🔍 **Researchers** — Subscribe to focused accounts for daily aggregation

---

## Features

### Core Features

- **Public Account Subscription**: Subscribe by account name (WeChat ID optional), up to 20
- **Three Categories**: Competitors / Peers / Favorites, grouped in reports
- **Daily Auto Push**: 09:00 scheduled fetch, auto-generates HTML report and opens browser
- **Terminal Table Display**: Publish date, title, summary, reads, likes in clear table format
- **Date Backtrack**: Fetch posts for a specific date to review history
- **LLM-Ready Data**: Fetched data can be used with LLMs for summary rewriting and style imitation

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

Manage your subscriptions in natural language.

### Quick Reference

| Intent | Example | Result |
|--------|---------|--------|
| Add subscription | "Subscribe to QbitAI public account" | Adds account to watchlist |
| View posts | "Fetch today's posts from my subscriptions" | Retrieves all subscribed accounts' daily posts |
| Competitor tracking | "Add XX account to competitor monitoring" | Categorized as competitor, prioritized in reports |
| View report | "Generate today's subscription daily report" | Fetches posts and generates HTML report |
| Enable push | "Push public account daily report every morning" | Installs cron job for 09:00 auto-push |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|--------------|---------|
| Morning briefing | Product manager | "What did my subscribed accounts post today?" | One-screen overview of all subscriptions |
| Competitor monitoring | Marketing ops | "What are competitor accounts posting lately?" | Track strategies, adjust responses timely |
| Inspiration gathering | Content creator | "Any new articles from industry leaders today?" | Follow top accounts for topic ideas |
| Content processing | Researcher | "Export this batch of article data for analysis" | Combine with LLMs for rewriting and style imitation |
