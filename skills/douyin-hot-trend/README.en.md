# Douyin Hot Trend Tracker / douyin-hot-trend

---

## Introduction

A smart hot trend tool that tracks Douyin trending topics in real time, uncovers viral content patterns, and helps creators and operators catch hot topics and find content ideas efficiently.

**Core Value**

- Automatically updates the Douyin TOP 50 chart every hour, with heat scores and direct links at a glance
- Covers up to 30 days of historical charts so you can trace past trend shifts anytime
- Automatically generates topic opportunity analysis, title pattern breakdowns, and trend forecasts from a creator's perspective
- Supports side-by-side comparison of any two time points, clearly marking newly-entered and dropped topics
- Supports hourly or daily scheduled delivery — no manual triggering needed

**Who It's For**

- 🎬 **Short-video Creators** — Quickly lock in daily hot topics and shorten your ideation time
- 📣 **MCN Operations Teams** — Monitor platform trends centrally and guide creator content strategies efficiently
- 🏷️ **Brand Marketing Managers** — Identify leverage-worthy topics and respond to hot trends faster
- 📚 **Operations Beginners** — Learn viral title patterns and quickly build content intuition

---

## Features

### Core Functions

- **Real-Time Chart Query**: Fetch the current Douyin TOP 50 trending topics with rankings, heat scores, titles, and clickable links — refreshed every 60 minutes
- **Historical Chart Lookup**: Query up to the past 7 days or 30 days of trending data, with support for specifying an exact date
- **Chart Comparison**: Compare rankings and heat score changes between any two time points, with new entrants and dropped topics automatically flagged
- **Creator Insights Report**: After displaying the chart, automatically outputs viral topic opportunities, title pattern analysis, trend forecasts, and actionable recommendations
- **Visual Report Export**: One-click generation of a minimal-purple-style HTML page with PDF export support and clickable links for every topic
- **Scheduled Subscription Push**: Set up hourly or daily automated delivery to stay on top of trending topics without manual effort

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Register an account at [RedFoxHub](https://redfox.hk?souce=github) to obtain your `REDFOX_API_KEY`.
- Configure the device environment variable `REDFOX_API_KEY` before using this skill.
- Before providing a key, confirm its source, scope, expiration, and whether it supports reset/revocation.
- Never hardcode or expose the key in plaintext in code, prompts, logs, or output files.

---

## Usage Guide

Just describe your need in plain language — no commands to memorize.

### Quick Reference

| Intent | Example Phrase | Result |
| ------ | -------------- | ------ |
| Check real-time chart | "Douyin trending" / "Today's hot list" | Shows current TOP 20 with heat scores and links, plus a creator insights report |
| Check yesterday's chart | "Yesterday's hot list" | Retrieves all-day trending data from yesterday |
| View historical chart | "Hot list from the past 7 days" / "Past 30 days" | Traces trending topics over the selected time range |
| View a specific date | "Hot list from May 15" | Retrieves the chart for that specific date |
| Load the full chart | "Load more" / "Continue loading" | Expands from TOP 20 to the full TOP 50 |
| Compare chart changes | "Compare today's and yesterday's hot list" | Outputs differences between the two days with flagged new entrants and dropouts |
| Subscribe to updates | "Subscribe to daily hot list push" | Sets up scheduled automatic delivery every day |
| Cancel subscription | "Cancel subscription" | Stops scheduled delivery |

### Sample Output

After querying "Today's hot list", you will receive:

1. **Trending Table**: Rank, topic title, heat score, and direct links (TOP 20; expandable to 50)
2. **Creator Insights Report**:
   - 🔥 Viral Topic Opportunities (transferable topics and content angles)
   - 🎯 Title Pattern Breakdown (emotional hooks, sentence structures)
   - 📈 Trend Forecast (which topics are rising or falling)
   - 💡 Action Recommendations (executable content strategy suggestions)
3. **Visual Report**: Auto-generated HTML page with PDF export support

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Daily content ideation | Short-video Creator | "Today's hot list" | Quickly identify hot directions and get transferable topics with title formulas |
| Trend monitoring | MCN Operations | "Past 7 days hot list" | Track a week's trend shifts and inform creator content strategy |
| Brand hot-topic leverage | Brand Marketing Manager | "Compare this week's chart changes" | Spot sustained topics and plan brand content in advance |
| Operations learning | Short-video Beginner | "Today's hot list — analyze the title patterns" | Learn viral sentence structures and rapidly build content intuition |

---
