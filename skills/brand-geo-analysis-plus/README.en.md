# Brand GEO Analysis Plus / brand-geo-analysis-plus

---

## Overview

One skill, three perspectives: **trending hub (hub) + 30-day social media research (cn30) + AI search brand visibility (geo)**. It helps you perceive your brand's image across the Chinese internet from three layers — topic heat, real word-of-mouth, and AI answers.

**Core Value**

- **All-in-one three-layer view**: From trending charts to social discussions to AI search answers, one tool covers the entire brand perception pipeline — no tool switching needed.
- **Driven by real data**: Real-time trending data from 7 platforms + 30 days of genuine discussions from 3 social platforms + live answers from 3 AI search engines.
- **Quantifiable and measurable**: GEO composite score, mention rate, average ranking, and sentiment distribution — brand visibility in AI search is no longer a black box.
- **Report as deliverable**: Terminal quick-view tables + interactive HTML reports, ready to archive and share.

**Who It's For**

- 🏢 **Brand & marketing teams** — Understand your brand's real presence and reputation across the web, and catch negative feedback early.
- 📊 **Market & PR analysts** — Compare competitors across platforms and produce structured reports ready for citation.
- 📈 **GEO / SEO practitioners** — Quantify brand visibility in AI search and identify clear optimization directions.
- ✍️ **Content & campaign operators** — Track trending topics and mine real user discussions for a steady stream of content ideas.

---

## Features

### Core Capabilities

- **Trending hub (hub)**: Fetches real-time trending charts from 7 platforms — Baidu, Zhihu, Weibo, Douyin, Bilibili, Kuaishou, and Toutiao — automatically identifies the same event across platforms, and delivers TOP10 charts, cross-platform summaries, and trend forecasts, with lookback support for yesterday / this week / the past 30 days.
- **Social media research (cn30)**: Searches 30 days of genuine user discussions on Xiaohongshu, Douyin, and WeChat Official Accounts, compares trends across platforms, and outputs data quick views, key findings, and visualized HTML reports, with support for custom keywords and any range (1–30 days).
- **AI search visibility (geo)**: Batch-submits questions to three AI search engines — Doubao, Kimi, and DeepSeek — quantifying brand mention rate, recommendation ranking, sentiment tendency, and source citations, auto-discovers competitors and generates comparison matrices, with an interactive HTML report.
- **Full brand diagnosis**: A combined workflow across all three modules that produces a structured brand perception report from the heat, word-of-mouth, and AI answer layers, with actionable recommendations for each layer.

### Highlights

- **Three-in-one product**: One skill chains three information layers — trending → social → AI search. Use any module on its own or combine them for a full-dimensional diagnosis.
- **Deterministic scoring formula**: The GEO composite score is a weighted sum of mention rate (40%) + ranking (30%) + sentiment (30%), making results reproducible and comparable over time.
- **Dirty data auto-excluded**: Answers affected by AI platform rate limits or failures are automatically flagged and excluded from statistics, keeping mention rate and sentiment conclusions clean.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing a key, verify its source, scope, expiration, and whether it supports reset/revocation.
- Do not hardcode or expose the key in plain text within code, prompts, logs, or output files.

---

## Usage

Just describe your brand, topic, or analysis need in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Prompt | Result |
| ------ | -------------- | ------ |
| Browse trending topics | "What's trending across the web today? Which topic is worth chasing?" | TOP10 charts from 7 platforms + cross-platform summary + trend forecast |
| Research social sentiment | "How have people discussed sugar-free drinks in the last 30 days? Check Xiaohongshu, Douyin, and WeChat accounts" | Cross-platform discussion quick view + key findings + HTML report |
| Check AI search visibility | "Analyze how Genki Forest performs on Doubao, Kimi, and DeepSeek" | GEO score + mention rate / sentiment / sources + interactive report |
| Compare competitors in AI search | "Compare us and competitor A — who gets recommended more in AI search?" | Competitor comparison matrix of mention rate / ranking / sentiment |
| Full brand diagnosis | "Give me a complete perception report for brand XX" | Three-stage combined diagnosis: heat + word-of-mouth + AI answers |

### Example Output

Take AI search visibility analysis as an example. When it finishes, you receive an interactive HTML report whose executive summary looks roughly like this (illustrative):

- **Cross-platform mention rate**: 83% (Doubao 100% / Kimi 67% / DeepSeek 83%)
- **GEO composite score**: 72 / 100 (Excellent), best platform: Doubao
- **Sentiment distribution**: 70% positive / 30% neutral / 0% negative
- **Average brand ranking**: 2.3 (upper-middle of recommendation lists)
- **Top cited sources**: zhihu.com, baike.baidu.com... If your official website is not cited, that is your first GEO optimization entry point

---

## Use Cases

| Scenario | Role | Example Prompt | Benefit |
| -------- | ---- | -------------- | ------- |
| Brand PR monitoring | Brand / marketing teams | "How are people talking about our brand lately? Check Xiaohongshu and Douyin" | Heat and word-of-mouth in one view; catch negative feedback early |
| AI search optimization | GEO / SEO practitioners | "What's our mention rate in AI search? How do we improve it?" | Quantified baseline + clear optimization directions |
| Competitor analysis | Market / PR analysts | "Compare our performance vs competitors on social media and AI search" | Same-dimension competitor matrix, ready to cite in reports |
| Trend-jacking topics | Content / campaign operators | "Which trending topic is worth chasing today? Is it relevant to our niche?" | Cross-platform charts + trend forecasts, no more blind topic picks |
| New product research | Product managers | "What are users really saying about this product category in the last 30 days?" | Genuine user voices across platforms — needs and pain points at a glance |

---

## Important Data Notes

- **Trending hub (hub)**: Updated hourly; by default returns data for "the last completed hour". Supports querying yesterday's chart, this week's chart, and the past 30 days.
- **Social research (cn30)**: Defaults to the last 30 days; any range from 1 to 30 days is supported.
- **AI search (geo)**: Real-time questions, real-time analysis. AI answers may change with platform algorithms — results only reflect the state at analysis time, so periodic re-testing is recommended.

---
