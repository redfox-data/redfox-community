# Xiaohongshu Portfolio Tracker / xhs-portfolio-search

---

## Overview

A real-time portfolio query tool for Xiaohongshu creators. Enter a blogger's profile link to instantly view their latest notes — **data is fetched live from the platform** — so every piece you see is freshly published. Supports paginated browsing for more historical works, plus daily/weekly/custom subscription pushes to keep you updated on a creator's full content timeline.

**Core Value**

- **Real-time data**: Every query fetches the latest works directly from the platform — no cache, no historical snapshots — ensuring data freshness.
- **Dedicated platform**: Focused exclusively on Xiaohongshu for precise, fast results — no cross-platform generalization.
- **Continuous tracking**: Supports scheduled subscription pushes so you never have to manually check for updates — new content comes straight to you.

**Intended Users**

- 📊 **Brand / MCN operators** — Track collaboration partners' or competitor accounts' publishing activity in real time.
- 📝 **Content creators** — Follow same-niche creators' full content threads for inspiration.
- 🔍 **Data analysts** — Access a creator's complete portfolio data for performance evaluation and trend analysis.

---

## Features

### Core Capabilities

- **Real-time portfolio query**: Enter a profile link or userId to instantly retrieve the latest note list — data is returned live from the platform, not cached.
- **Paginated browsing**: Browse through a creator's full history of works page by page.
- **Multi-dimensional data**: Returns complete engagement metrics including likes, favorites, comments, and shares for thorough performance assessment.
- **Scheduled subscription push**: Supports daily, weekly, or custom-time automatic query and push of new works for continuous tracking.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`)
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
| --- | --- | --- |
| Query portfolio | "Look up Xiaohongshu user 5a73c5fa4eacab4c4ccc9778's portfolio" | Get the blogger's latest notes and engagement data in real time |
| Query via link | "Check this account's notes: xiaohongshu.com/user/profile/5a73c5fa4eacab4c4ccc9778" | Auto-detect the link and return the portfolio |
| Paginate | "Next page, show me more works" | Display more historical works from the blogger |
| Daily subscription | "Subscribe to this blogger, push daily" | Auto-query and push latest works every day |
| Weekly subscription | "Push once a week" | Auto-query and push latest works weekly |
| Custom schedule | "Push every Wednesday at 2:00 PM" | Push at your specified time |

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| --- | --- | --- | --- |
| Competitor monitoring | Brand ops | "Check what this competitor has been posting lately" | Stay on top of competitor content moves and adjust strategy in time |
| Creator tracking | MCN ops | "Subscribe to this creator, push daily" | Auto-receive partner updates without manual checking |
| Niche learning | Content creator | "See what top creators in my niche posted recently" | Spot viral content trends and get creative inspiration |
| Portfolio assessment | Data analyst | "Pull all works data for this account" | Get complete engagement data to support analysis and decisions |

---
