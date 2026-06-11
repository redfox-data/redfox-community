# China Social Media Topic Research / cn-last30days

---

## Overview

Search real discussions from Xiaohongshu (RED), Douyin (TikTok China), and WeChat Official Accounts over the past 30 days, perform cross-platform sentiment analysis, and output structured research reports with interactive HTML visualizations—helping you quickly grasp trending topics on Chinese social media.

**Core Value**

- **Three-platform perspective**: Simultaneously covers Xiaohongshu product reviews, Douyin trends, and WeChat in-depth articles to avoid single-platform bias.
- **Cross-platform comparison**: Automatically synthesizes data from all three platforms to identify differentiated trends and cross-validated conclusions.
- **Entity comparison**: Supports A vs B structured comparison analysis for brand/product decision-making.

**Intended Users**

- 📊 **Content creators** — Track multi-platform trending topics with data-driven topic selection.
- 🏢 **Brand operators** — Monitor brand sentiment across platforms to discover authentic user feedback.
- 📈 **Market researchers** — Analyze industry trends and compare competitor reputation performance.

---

## Features

### Core Capabilities

- **Three-platform data sources**: Real-time data from Xiaohongshu, Douyin, and WeChat Official Accounts for multi-dimensional sentiment perspectives.
- **Keyword research**: Supports multi-keyword combined queries (comma-separated) for flexible topic coverage.
- **Cross-platform comparison**: Automatically synthesizes three-platform data to generate insights and discover differentiated trends.
- **Entity comparison**: A vs B structured comparison analysis to support decision-making.
- **HTML reports**: Interactive visualization report generation for easy sharing and distribution.
- **Historical lookback**: Supports data from any date within the past 30 days to track trend evolution.

### Highlights

- **Pre-research mechanism**: Automatically runs WebSearch to extract trending terms before calling the engine, optimizing query strategy.
- **Smart merging**: Automatically merges related keywords into a single call to reduce API invocations.
- **Signal interpretation**: Automatic interpretation of key metrics like Xiaohongshu save/like ratio, Douyin share count, and WeChat read count.

---

## API Key Acquisition & Security

- This skill includes a built-in free public Key and works out of the box—no configuration needed.
- For higher quotas, you can obtain a personal `REDFOX_API_KEY`:
  - `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
  - Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
  - Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe the topic you want to research in natural language—no fixed commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|---------------|--------|
| Research a topic | "Research AI video tools for me" | Auto-extracts keywords, searches three platforms for 30-day data |
| Compare two brands | "Compare the reputation of Product A and Product B" | Generates A vs B structured comparison report |
| Check recent trends | "Xiaohongshu marketing trends in the last 7 days" | Sets --days 7 to focus on recent data |
| Deep research | "Deep analysis of new energy vehicle sentiment" | Increases --count to 100 for more comprehensive data |
| Generate report | "Generate an HTML visualization report" | Generates interactive HTML from JSON data |

### Output Example

After research, you'll see a report like this (illustrative):

```
🇨🇳 cn-last30days v2.0.0 · 2026-06-10

My findings:

**AI video tools continue to rise in popularity** - Tutorial content on Xiaohongshu has a save rate as high as 15%, Douyin-related video shares exceed 100k...

Key findings:
1. Text-to-video feature is most sought after - Source [WeChat: AI Frontier](article link)
2. Users prioritize generation speed over image quality - Source [Xiaohongshu @TechBlogger](note link)
3. Enterprise application demand is growing rapidly - Source [Douyin @IndustryWatch](video link)
```

---

## Use Cases

| Scenario | Role | Example question | Benefit |
|----------|------|------------------|---------|
| Topic research | Content creator | "What beauty topics are trending on Xiaohongshu lately?" | Quickly pinpoint high-engagement directions, reduce blind trial-and-error |
| Competitive monitoring | Brand operator | "Compare user feedback for Brand A and Brand B" | Discover differentiated reputation across platforms, inform strategy adjustments |
| Trend tracking | Market researcher | "Analyze new energy vehicle sentiment over the past 30 days" | Multi-platform cross-validation to grasp industry trends |
| Daily monitoring | Individual user | "Push me daily updates on AI tools research" | Subscribe once and receive automatic updates—never miss a trend |

---
