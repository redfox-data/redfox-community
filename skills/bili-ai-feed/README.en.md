# AI-Bilibili Feed / bili-ai-feed

---

## Overview

A daily automated scanner for AI-related Bilibili (B站) content. It discovers viral videos by like count, intelligently clusters them into topics, and generates an HTML daily report with cover images and engagement data—then automatically triggers a multi-engine AI intelligence investigation based on trending topics, producing structured, credibility-annotated reports. Includes a built-in public API key with ~10,000 free quota—works out of the box.

**Core Value**

- **Viral discovery + smart clustering**: Daily scans of AI videos on Bilibili, filtering trending content by likes and auto-grouping into topic directions (AI tutorials, large models, AI art, etc.)—categories dynamically determined by that day's content.
- **Visual HTML daily report**: Dark-themed report with video cover images, engagement data (likes/comments/shares), and direct links—saved to a local folder and auto-opened in the browser.
- **AI intelligence investigation linkage**: Automatically triggers multi-engine intelligence investigations (competitive/opinion/personnel/verification) on the TOP 3 trending topics after report generation, producing credibility-annotated structured reports.
- **One-click subscription automation**: `--subscribe` enables daily automated output; reports accumulate in a local folder with zero manual intervention.

**Intended Users**

- 🤖 **AI practitioners / researchers** — Stay on top of daily viral AI content and topic trends on Bilibili.
- 📊 **Content operators / self-media** — Discover AI niche hotspots for content inspiration and direction.
- 📈 **Product managers / entrepreneurs** — Understand user feedback and discussion heat around AI products on Bilibili.
- 🔍 **Intelligence analysts** — Use Bilibili hotspots to trigger multi-engine cross-verification for traceable, structured intelligence.

---

## Features

### Core Capabilities

- **Viral discovery**: Screens trending content from AI-related Bilibili videos by like count, precisely pinpointing high-heat AI videos.
- **Smart clustering**: Automatically identifies topic directions (AI tutorials, large models, AI art, etc.)—categories dynamically determined by that day's content.
- **AI intelligence investigation**: Automatically executes multi-engine search + cross-validation on trending topics, deeply mining intelligence behind them.
- **Visual daily report**: Dark-themed HTML with cover images + engagement data + direct links, visually presenting daily AI hotspots.
- **One-click subscription**: `--subscribe` enables daily automated output; reports auto-accumulate in a local folder.
- **Record preservation**: Investigation reports auto-saved to the RedFox platform, supporting historical review and trend analysis.

### Highlights

- **Dual output: daily report + intelligence**: Not just displaying viral videos—also triggers AI intelligence investigations linked to clustered topics, producing credibility-annotated structured reports.
- **Auto-matching investigation modes for topics**: TOP topics are automatically matched to competitive/opinion/personnel/verification modes with optimal engine combinations executing a three-round search.
- **Works out of the box**: Built-in public API key with ~10,000 free quota—experience full functionality with zero configuration.
- **Subscription-based automation**: One-click subscription enables fully automated daily output; reports auto-accumulate locally.

---

## API Key Acquisition & Security

- This skill includes a built-in public `REDFOX_API_KEY` (~10,000 free quota); you may also use your own key.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`)
- Register at [RedFoxHub](https://redfox.hk?souce=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill (if using your own key).
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Trigger with natural language—no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
| ------ | -------------- | ------ |
| Generate today's report | "Generate today's AI-Bilibili daily report for me" | Scan AI videos → cluster → generate HTML report + intelligence investigation |
| Custom focus direction | "Focus on AI tutorials and AI art content on Bilibili" | Filter viral videos by specified keywords and generate report |
| Enable daily subscription | "Enable AI-Bilibili daily report subscription for me" | Daily auto-output; reports accumulate in local folder |
| View historical report | "Show me the AI-Bilibili report from 2026-06-10" | Review a specific date's report content |

### Output Example

Each run delivers terminal output + an HTML daily report (auto-opened in browser):

**Category overview table**: Scanning N trending videos, clustering M categories, showing counts, percentages, and top highlights per category

**AI Intelligence Investigation Report** (based on TOP 3 topics):
- 🔥 Emerging growth signals: Low-volume but high-engagement topic directions
- 👤 Key creators: Bilibili creators with the most outputs / highest likes that day
- 📊 Topic investigation reports: Investigation mode + engine combination + dimension findings table (with A~D credibility ratings)
- 🔗 Cross-platform comparison suggestions: Recommended Douyin, Xiaohongshu, and WeChat Official Account topics to track in parallel

**HTML Daily Report**: Dark-themed, video cover images + engagement data + clickable links, saved in `~/Downloads/QoderReports/`

---

### Subscription Notes

Once subscribed, the report runs daily and automatically; HTML reports accumulate in the local folder. You can cancel the subscription at any time.

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| -------- | ---- | ---------------- | ------- |
| AI hotspot tracking | AI practitioner | "Generate today's AI-Bilibili daily report" | Stay on top of daily AI viral topics and content trends on Bilibili |
| Content inspiration | Self-media operator | "Focus on the latest viral AI art videos on Bilibili" | Discover AI niche hotspots; get content inspiration and direction |
| AI product sentiment | Product manager | "Show me what people are discussing about ChatGPT on Bilibili" | Understand user feedback and discussion heat around AI products |
| Competitive intelligence | Entrepreneur | "Scan AI tool videos and run competitive analysis" | Link trending topics to multi-engine investigation; get traceable intelligence |

---

## Important Data Notes

- ~200 AI-related Bilibili videos are scanned daily; viral content is selected by likes, and topic clustering categories are dynamically determined by that day's content.
- HTML daily reports are saved in the `~/Downloads/QoderReports/` directory and auto-opened in the browser.
- Intelligence investigations are based on multi-engine cross-validation; key information is marked "Confirmed" only when verified by at least 2 independent sources.
- Sources are classified into four tiers: A (official/authoritative media), B (industry media/professional platforms), C (social media/self-media), D (anonymous/unverified sources).
- The built-in public key has ~10,000 free quota; configure your own `REDFOX_API_KEY` when exhausted.
- All data comes from publicly accessible platforms; no non-public data collection is involved.

---
