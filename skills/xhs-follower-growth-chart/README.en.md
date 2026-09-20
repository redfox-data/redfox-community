# XHS Follower Growth Chart / xhs-follower-growth-chart

---

## Introduction

Want to know which Xiaohongshu accounts are gaining followers fastest? Query daily, weekly and monthly follower growth rankings across 25 categories, and generate stunning ranking images, export to Excel, or subscribe to daily push notifications.

**Core Value**

- Data is verified account by account, ensuring accuracy and reliability
- Covers 25 popular categories, from beauty and fashion to pets and careers
- Daily, weekly and monthly ranking dimensions keep you on top of platform trends
- Ranking images are ready to publish on Xiaohongshu, WeChat Official Accounts and more

**Who It's For**

- 👔 Brand managers — monitor competitors and discover KOLs
- 🏢 MCN agencies — manage creator accounts and spot underperformers early
- ✍️ Bloggers/creators — learn from peers and produce data-driven content fast
- 👀 Curious minds — just want to know who's trending

---

## Features

### Core Features

- Ranking queries: daily/weekly/monthly follower growth rankings with follower counts, growth numbers and growth rates
- Ranking image generation: create beautiful Xiaohongshu-style ranking images in one click, auto-saved to your desktop
- Data export: export ranking data to Excel in one click for your own analysis
- Scheduled push: set up daily/weekly/monthly automatic ranking delivery

### Highlights

- ⚡ Daily updates: rankings published at 7:00 PM daily, manually curated for accuracy
- 🧭 Multi-category filtering: 25 categories covering beauty, fashion, pets, careers and more
- 🎨 Beautiful images: ready to publish on Xiaohongshu, WeChat Official Accounts and more
- 📱 Multi-platform: works on Coze, SkillHub, ClawHub and more

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please go to [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing your key, verify its source, scope of use, validity period, and whether it supports reset/revocation.
- Never hardcode or expose the key in plaintext in code, prompts, logs or output files.

---

## Usage Guide

Just describe what you want in natural language — no commands to memorize.

### Quick Phrase Reference

| Intent | Example phrase | Result |
| -------- | ---------------------------- | -------- |
| Query rankings | "Show me the follower growth chart" | Returns the latest TOP20 of All Categories |
| Pick a category | "Show me the beauty category daily chart" | Returns the TOP20 for that category |
| Generate image | "Generate a ranking image" | Creates a beautiful chart and saves it to your desktop |
| Export data | "Export to Excel" | Exports ranking data to an Excel spreadsheet |
| Subscribe | "Subscribe to the daily all-categories chart" | Pushes the latest chart daily at 8:00 PM |

### Output Example

> User: Show me the follower growth chart
>
> Assistant: Querying the latest TOP20 of All Categories...
>
> 📊 **All Categories - Follower Growth TOP20**
>
> | Rank | Account | New Followers |
> |------|---------|---------------|
> | #1 | xxx | +xx万 |
> | ... | ... | ... |
>
> 💬 What else can I help with? **1️⃣ Subscribe to another category　2️⃣ Export to Excel　3️⃣ Generate a ranking image**

---

## Use Cases

| Scenario | Role | Example request | Benefit |
| -------- | -------- | -------- | -------- |
| Daily ranking push | Content operator | Subscribe to the daily all-categories chart | Stay on top of trending accounts |
| Weekly category analysis | Brand marketing manager | Push last week's astrology chart every Monday | Track niche trends and optimize campaigns |
| Monthly review | MCN agency head | Push the monthly chart on the last day | Get a full picture of the platform ecosystem |
| Competitor monitoring | Brand marketing manager | Subscribe to competitors' categories | Keep tabs on competitors in real time |
| Creator management | MCN operations | Subscribe to all managed creators' categories | Manage creators more efficiently |
| Content creation | Xiaohongshu blogger | Query rankings and generate images | Produce data-driven content fast |

---

## Important Data Notes

- Rankings are published daily at 7:00 PM; it's recommended to schedule pushes at 8:00 PM or later
- Data has a **1-day delay** (e.g., on April 20 you can access April 18's data)
- Query range limits: daily up to **30 days** back, weekly up to **8 weeks** back, monthly up to **3 months** back
- A single category chart shows up to **100** entries
- Only 25 fixed categories are supported (All Categories + 24 subcategories); custom keyword subscriptions are not supported
