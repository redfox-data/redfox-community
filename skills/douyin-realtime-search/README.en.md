# Douyin Realtime Search / douyin-realtime-search

---

## Introduction

Enter any keyword to instantly retrieve the latest content data from Douyin — no cached history, just what's happening right now.

**Core Value**

- Real-time results: Directly connects to Douyin's search service, reflecting the current state of the platform rather than historical archives
- Flexible filtering: Freely combine sorting (comprehensive / latest published / most liked) and time range (7 days / 30 days / 90 days / unlimited)
- Structured display: Title, author, likes, comments, shares, and collections at a glance — click any title to jump directly to the original video

**Who It's For**

- 📊 **Content operators / Strategy researchers** — Quickly grasp the real-time heat and emerging trends in any content vertical
- 🎬 **Creators / Influencers** — Stay on top of the latest content in your niche and find the right moment to publish

---

## Features

### Core Capabilities

- **Real-time Search**: Keyword-based live search for the latest Douyin works — get non-cached, real-time data.
- **Multi-dimensional Sorting**: Comprehensive / Latest / Most-liked sorting for discovering quality content by different dimensions.
- **Time Filtering**: 7-day / 30-day / 90-day / No-limit time ranges for flexible search windows.
- **Smart Expansion**: Auto-generates 10 alternative keywords when no results found, breaking through search bottlenecks.
- **Paginated Browsing**: Multi-page results for exploring large search result sets.
- **Subscription Push**: Subscribe to keywords for daily automated updates.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing your key, confirm its source, scope, expiration, and whether it supports reset/revocation.
- Never hardcode or expose your key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Just describe your need in plain language — no commands to memorize.

### Quick Reference

| Intent | Example | Effect |
| ------ | ------- | ------ |
| Search a keyword | "fitness" / "office outfits" | Searches with default sorting (comprehensive) and time range (7 days) |
| Specify sort order | "Search weight loss by latest published" | Switches to latest-published sorting |
| Specify time range | "Search AIGC content from the past 30 days" | Sets time filter to last 30 days |
| Combined filters | "Search ancient fitness by most liked, past 90 days" | Applies both sort and time filters simultaneously |
| Switch filters | "Re-search by latest published, past 30 days" | Keeps the keyword, updates filter parameters |
| Pagination | "Next page" / "Previous page" | Navigate through paginated search results |
| Subscribe daily | "Confirm subscription" | Creates a scheduled task to push results daily at 10:00 AM |

### Output Example

After a search, you'll receive results in this format:

> 📊 Keyword "**fitness**" — **9 results** found in real time (Sort: Comprehensive | Time: Last 7 days | Page 1):

| # | Title | Author | Likes | Comments | Shares | Collections |
|---|-------|--------|-------|----------|--------|-------------|
| 1 | [Liang Zi came to the base!...](link) | 健身华哥 | 61.5w | 3.5w | 33.3w | 2.2w |
| 2 | [Full-body stretching tutorial...](link) | 谭成义 | 5.0w | 677 | 8928 | 3.8w |

> 📄 Page **1**. Reply "next page" to continue browsing.

---

## Use Cases

| Scenario | Role | Example | Benefit |
| -------- | ---- | ------- | ------- |
| Niche reconnaissance | Content operator | "Show me the latest fitness content right now" | Instantly understand what competitors are publishing |
| Trend-driven ideation | Creator | "Most liked AIGC videos in the past 7 days" | Find high-engagement directions to ride the wave |
| Publish timing research | Influencer | "Latest office outfit videos in the past 30 days" | Understand posting rhythm and content density in your niche |
| Keyword monitoring | Brand operator | "Subscribe to daily push for [brand keyword]" | Receive automatic daily updates for timely response |
