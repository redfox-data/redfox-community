# WeChat Public Account Subscription Tracker / gzh-subscribe

---

## Introduction

Subscribe to competitor, peer, and favorite WeChat public accounts — auto-fetch daily posts with terminal table + HTML daily report. Built-in public API Key — ready to use out of the box.

**Core Value**

- **Inbox-style subscription**: Subscribe to up to 20 public accounts like a newsletter.
- **Daily 9 AM auto-push**: One-click scheduled task — automatically generate a daily report every morning.
- **Three-category management**: Competitor / Peer / Favorite grouping for purpose-driven display.

**Target Users**

- 📊 **Content operators** — Monitor competitor accounts and stay on top of their posting activity.
- 📝 **Self-media creators** — Track peer accounts for topic inspiration.
- 🏢 **Brands / marketing teams** — Monitor brand sentiment and follow industry leaders.

---

## Features

### Core Capabilities

- **Inbox-style subscription**: Subscribe to up to 20 public accounts by name — no WeChat ID required.
- **Daily auto-push**: One-click scheduled task — auto-fetch and generate HTML daily report at 09:00.
- **Three-category management**: "Competitor" to watch rivals, "Peer" for inspiration, "Favorite" to follow thought leaders.
- **Key metrics at a glance**: Post date, title, summary, read count, like count, and one-click original article links.
- **Dual-mode output**: Terminal table for real-time review; HTML daily report for sharing and archiving.

---

## API Key Info

A built-in public API Key provides ~**10,000 free uses** — zero configuration needed. When the quota runs out, register at [RedFoxHub](https://redfox.hk/login?source=github) for a personal API Token:

| Method | Command |
|--------|---------|
| **Environment variable** (recommended) | `export REDFOX_API_KEY=ak_your_key` |
| **CLI argument** | `python3 "$SKILL_PATH/assets/subscribe.py" fetch --api-key ak_your_key` |
| **Config file** | `echo '{"api_key":"ak_your_key"}' > ~/.qoder/apis/redfox.json` |

---

## Usage Guide

Just describe which accounts you want to subscribe to or check — no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|----------------|--------|
| Add subscription | "Subscribe me to XX account" | Add to subscription list |
| Check today's posts | "What did my subscribed accounts post today" | Terminal table of today's posts |
| Generate daily report | "Generate my public account daily report" | Create and open HTML daily report |
| Enable daily push | "Push my subscribed accounts every morning" | Install 9 AM daily scheduled task |

---

## Use Cases

| Scenario | Role | Example query | Benefit |
|----------|------|---------------|---------|
| Competitor monitoring | Content ops | "Subscribe to a few competitor accounts" | Auto-get competitor updates daily |
| Inspiration tracking | Self-media | "Follow a few accounts in my niche" | Discover topics and writing angles |
| Daily push | Brand team | "Enable daily push" | Receive daily report at 9 AM automatically |

### Notes

- Maximum 20 subscribed public accounts.
- To search articles (not subscribe), use the `gzh-search` skill instead.