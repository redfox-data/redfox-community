# AI Kuaishou Feed / ks-ai-feed

---

## Introduction

Automatically scans Kuaishou's AI-created content every day, filters trending videos by play count, clusters them into topics, and delivers a visual HTML daily report — along with AI intelligence insights — to help creators and operations teams stay on top of AI trends on Kuaishou.

**Core Value**

- **Daily trending content at a glance**: Automatically surfaces high-play AI videos on Kuaishou, saving hours of manual browsing.
- **Smart topic clustering**: Videos are automatically grouped into topic directions, giving you a clear snapshot of the day's hot spots.
- **Deep intelligence insights**: Delivers top trending topics, emerging growth signals, key creators, and recommended investigation directions to help you spot opportunities before they peak.
- **Visual HTML report**: A dark-themed HTML daily report with cover images, engagement data, and direct video links for easy browsing and navigation.

**Target Users**

- 🎬 **AI Content Creators** — Get daily trending references from Kuaishou's AI space to eliminate blind spots in topic selection.
- 📊 **Content Operations / Growth Teams** — Stay updated on topic heat and creator performance to drive smarter content strategy.
- 🔍 **Industry Researchers** — Continuously track AI content trends on Kuaishou and build a referenceable sample library.

---

## Features

### Core Capabilities

- **Trending Discovery**: Filters AI-related hot videos on Kuaishou by play count to pinpoint high-engagement content.
- **Smart Clustering**: Automatically identifies topic directions from content, presenting daily categories clearly.
- **AI Intelligence Insights**: Covers top trending topics, emerging growth signals, key creator analysis, and recommended investigation directions for deep trend visibility.
- **Visual HTML Daily Report**: Dark-themed report with embedded cover images, engagement metrics, and direct video links supporting one-click navigation.
- **One-Click Subscription**: Enable daily automated report generation to never miss a trend.
- **Stable Cover Images**: Anti-hotlink proxy and automatic HEIF/HEIC-to-JPG conversion ensure images load reliably.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?souce=github) to register and obtain your `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` as a device environment variable before using this skill.
- Before using the key, verify its source, scope, expiry, and whether it supports reset/revocation.
- Never hardcode or expose the key in code, prompts, logs, or output files.

---

## Usage Guide

Just describe your needs in plain language — no commands to memorize.

### Quick Reference

| Intent                  | Example Phrase                                                    | Outcome                                                      |
| ----------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------ |
| Get today's AI report   | "Generate today's Kuaishou AI trending daily report"              | Scans trending videos, clusters topics, outputs HTML report and insights |
| Filter by focus area    | "Only focus on AI drawing and ChatGPT content on Kuaishou"        | Filters content by keywords and generates a targeted report  |
| View historical report  | "Show me the Kuaishou AI highlights from 2026-06-10"             | Retrieves indexed Kuaishou AI content for the specified date |
| Enable daily subscription | "Automatically generate my Kuaishou AI report every day"        | Activates subscription for daily automated report output     |

---

## Use Cases

| Scenario               | Role                     | Example Request                                                   | Benefit                                          |
| ---------------------- | ------------------------ | ----------------------------------------------------------------- | ------------------------------------------------ |
| Daily topic selection  | AI Content Creator       | "What AI topics are trending on Kuaishou today?"                  | Quickly identify high-heat directions to reduce topic selection time |
| Creator & competitor tracking | Content Ops / MCN | "Which creators stood out in Kuaishou's AI space today?"          | Get a key creator list to support collaboration and benchmarking |
| Trend forecasting      | Growth Team              | "Are there any AI topics gaining traction recently?"              | Obtain emerging growth signals to lay out content direction early |
| Historical review      | Industry Researcher      | "Check last week's overall topic distribution for Kuaishou AI content" | Review historical data and surface trend patterns |

---
