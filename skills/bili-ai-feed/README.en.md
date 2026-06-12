# Bilibili AI Feed / bili-ai-feed

---

## Overview

Daily scan of Bilibili AI-related content, filtering trending videos by likes, intelligently clustering topics, and generating a visual daily report with cover images and engagement data. Simultaneously performs AI intelligence investigations based on hot topics, using multi-engine search and cross-verification to produce structured investigation reports.

**Core Value**

- Precisely identify daily high-engagement AI videos on Bilibili — no more manual scrolling
- Intelligent clustering automatically groups topics, giving you a clear picture of the day's AI content distribution at a glance
- Multi-engine cross-verification intelligence investigations track the products, people, and sentiment behind trending topics
- One-click subscription — daily reports automatically accumulate in your local folder with no manual effort

**Who Is This For**

- 🔍 AI Content Creators — Quickly discover Bilibili AI trending topics to guide your content direction
- 📊 AI Industry Observers — Track daily AI trending shifts and topic evolution
- 🛠️ AI Product Managers — Uncover competitor dynamics, user feedback, and industry signals
- 🎯 Operations & Growth Teams — Identify high-engagement content patterns to optimize distribution strategies

---

## Features

### Core Features

- **Trending Discovery** — Filter Bilibili AI-related videos by likes to pinpoint high-engagement content
- **Intelligent Clustering** — Automatically identify topic directions (AI tutorials, LLMs, AI art, etc.); categories are dynamically determined by the day's content
- **AI Intelligence Investigation** — Based on clustered hot topics, perform four types of investigation: competitive intelligence, sentiment events, background checks, and information cross-verification
- **Visual Daily Report** — Dark-themed HTML page with cover images, engagement metrics, and direct video links
- **One-Click Subscription** — Enable automatic daily output via subscription; reports are saved locally in your designated folder

### Highlights

- 🌐 **16+ Search Engine Orchestration** — Covers Baidu, Google, DuckDuckGo, WeChat Sogou, Toutiao, and more; intelligently orchestrates engine combinations based on investigation goals
- 🔍 **Four Investigation Modes** — Competitive intelligence, sentiment events, background checks, and cross-verification to meet diverse intelligence needs
- 📊 **Credibility Annotation System** — Sources graded A–D; results annotated as Confirmed / Pending / Disproved / Single Source
- 🤖 **Fully Automated Workflow** — Scan → Cluster → Investigate → Output; one trigger delivers both a daily report and an intelligence report

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?souce=github) to register an account and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing your key, please verify its source, scope of use, validity period, and whether it supports reset/revocation.
- Never hardcode or expose the key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Prompt | Result |
|--------|---------------|--------|
| Get today's report | "Generate today's Bilibili AI daily report" | Scans AI videos, clusters topics, generates and opens the HTML report |
| Focus on specific topics | "Show me trending AI art and ChatGPT videos on Bilibili" | Focuses on specified keyword topics |
| View historical report | "Generate the Bilibili AI report for June 10" | Retrieves AI video data for a specific date |
| Enable daily subscription | "Enable daily subscription for the Bilibili AI report" | Automatically produces reports daily, saved in local folder |
| Run intelligence investigation | "Investigate that hot AI product trending on Bilibili recently" | Runs multi-engine cross-verification investigation based on report topics |

### Output Example

After running, the following outputs are automatically generated:

- **HTML Visual Report** — Dark-themed page with cover images, like/view metrics, and direct video links; saved to `~/Downloads/QoderReports/`
- **Terminal Summary Table** — Categorized video overview with proportions and highlights
- **AI Intelligence Investigation Report** — Structured report on the top 3 trending topics, including dimensional findings, sources, and credibility annotations

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|---------------|---------|
| Daily AI trend tracking | AI Content Creator | "Today's Bilibili AI daily report" | Quickly get daily trending topics and distribution |
| AI product competitive research | AI Product Manager | "What hot AI art tools are trending on Bilibili?" | Multi-engine investigation for product positioning and user feedback |
| AI sentiment monitoring | Operations Team | "What AI-related hot events are happening on Bilibili lately?" | Track sentiment trends with multi-perspective analysis |
| Creator discovery & collaboration | MCN / BD | "Which AI content creators are blowing up on Bilibili recently?" | Identify high-engagement creators to support collaboration decisions |
