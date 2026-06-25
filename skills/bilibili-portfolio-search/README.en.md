# Bilibili Account Video Collection / B站搜账号下作品集

---

## Overview

Enter a Bilibili UP host's UID to retrieve all published videos in real time. Data is always fresh and supports paginated browsing through the complete list.

**Core Value**

- **Real-time data**: Each query calls a live API, returning the latest video data — never cached or historical records.
- **Spot viral hits fast**: Videos are sorted by play count in descending order, so you can instantly find the UP host's most popular content.
- **Paginated browsing**: Flip through pages of videos, even for accounts with a large catalog.

**Intended Users**

- 🔍 **Content researchers** — Quickly understand any UP host's content output and viral distribution.
- 📊 **Data analysts** — Access full video catalogs to support trend analysis.
- 🏢 **Brand / MCN** — Evaluate KOL content quality and performance metrics to guide partnership decisions.

---

## Features

### Core Capabilities

- **UID lookup**: Enter a Bilibili UP host's UID (numeric only) to retrieve all published videos, including play count, danmaku count, comment count, favorites, and other key metrics.
- **Play count sorting**: Results are automatically sorted by play count in descending order for quick identification of viral content.
- **Paginated browsing**: Browse more videos page by page, with 20 results per page, to handle large catalogs.
- **Complete video info**: Each video includes title, play count, danmaku count, comment count, favorites, duration, publish date, video link, and cover image.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?souce=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe what you need in natural language — no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
| ------ | -------------- | ------ |
| View UP host's videos | "Show me the Bilibili video list for UID 946974" | Retrieve all videos in real time, sorted by play count |
| Browse more | "Next page" | Automatically paginate to show more videos |
| Query by nickname | "What videos does 老番茄 have on Bilibili?" | Prompt to provide the UID (numeric ID from the UP host's profile URL) |

### Output Example

After a successful query, you'll receive a video list like this (illustrative):

> 📊 UP host "**老番茄**" (UID: 946974) has **320** videos in total. Showing **20** below:
>
> | # | Title | Plays | Danmaku | Duration | Published |
> | --- | --- | --- | --- | --- | --- |
> | 1 | [Some viral video title](https://www.bilibili.com/video/BV1xx) | 10.52M | 125K | 15:21 | 2026-06-20 |
>
> 📄 More videos available. Reply "next page" to continue.

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| -------- | ---- | ---------------- | ------- |
| Competitive analysis | Content researcher | "Show me UID 946974's video list — I want to study their content strategy" | Quickly grasp a competitor's content output and viral patterns |
| Data research | Data analyst | "Pull this UP host's video data, sorted by play count" | Access full catalog data for trend and performance analysis |
| KOL evaluation | Brand / MCN | "Evaluate this Bilibili UP host's video performance" | Understand a KOL's content quality and metrics to guide partnerships |

---
