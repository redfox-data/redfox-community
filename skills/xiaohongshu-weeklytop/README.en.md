# Xiaohongshu Weekly Viral Notes / xiaohongshu-weeklytop

---

## Introduction

A Xiaohongshu 7-day viral notes tool designed for creators and operators — one query delivers vertical category hot rankings and deep analysis based on the TOP50 notes from the past 7 days.

**Core Value**

- Solves the "I don't know what's trending or why" problem in topic selection — a 7-day window is more stable and reliable than a single day
- Real-time hot rankings + smart analysis + exportable HTML reports, supporting review sessions and creative decisions
- Keyword auto-matching across 25 vertical categories lowers the barrier to query

**Who It's For**

- ✍️ Xiaohongshu creators — understand what content tends to go viral in your track over the past week, and find replicable topic directions
- 📢 Brand marketing managers — monitor vertical category viral content trends to optimize placements and seeding strategies
- 🏢 MCN operations staff — provide track hot topic references for managed creators to shorten topic discussion cycles

---

## Features

### Core Capabilities

- **Recent hot rankings**: Query the past 7 days' hot notes by category, covering 25 vertical tracks to quickly grasp current traffic direction
- **7-day trend analysis**: Deep insights from multiple dimensions — popular trends, hot topics, practical value — breaking down viral content commonalities
- **Format pattern comparison**: Auto-identifies viral elements like high-quality covers, emotional resonance, practical value, and trend alignment
- **Creative suggestions**: Delivers actionable topic directions, differentiation strategies, and high-performing post breakdowns
- **Subscription push**: Daily 19:30 scheduled delivery of the latest trend analysis reports

### Highlights

- Hot ranking tables and HTML pages share the same data source and sort logic — rankings are fully consistent
- First display shows TOP20; reply "load more" to get remaining data, HTML updates to full version
- Focused on low-follower high-engagement notes, ideal for finding authentic benchmark viral samples

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before using a key, confirm its source, scope, expiry, and whether it supports reset or revocation.
- Never hard-code or expose the key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent                         | Example phrase                                   | Result                                                                                                   |
| ------------------------------ | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------- |
| Query track 7-day hot rankings | `Show me viral notes related to mascara`         | Auto-matches "Beauty & Makeup", outputs TOP20 hot rankings + 7-day analysis + HTML + subscription option |
| Query general hot content      | `What's trending on Xiaohongshu lately?`         | Uses "All" category, full four-section standard output                                                   |
| Query specific date            | `Show fashion track hot rankings for 2026-04-15` | Fetches data for the specified date                                                                      |
| Load more                      | Reply "load more"                                | Continues output from TOP21 to end; HTML regenerated as full version                                     |
| Subscribe to daily push        | Reply `1` after output completes                 | Activates daily 19:30 7-day viral notes push                                                             |

### Output Example

Each query produces four fixed sections: recent hot rankings TOP20 → 7-day viral analysis (trends + topics + format patterns) → HTML visual page → subscription service options.

---

## Use Cases

| Scenario                    | Role                    | Example question                                     | Benefit                                                                                   |
| --------------------------- | ----------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Creator topic inspiration   | New Xiaohongshu creator | `Show 7-day hot rankings in skincare`                | Quickly find replicable topic directions to lower cold-start trial-and-error costs        |
| Brand competitor monitoring | Brand marketing manager | `Query lipstick 7-day virals and export HTML`        | Grasp category content direction to optimize placement and seeding strategies             |
| Creator operations review   | MCN ops staff           | `Query fashion 7-day rankings and subscribe to push` | Break down viral title types and continuously track hot topics for creator topic planning |
| Data insights reporting     | Growth / data analyst   | `Fetch full food TOP50 and export HTML`              | Get a shareable, archivable data report to support weekly reviews and strategy sessions   |
