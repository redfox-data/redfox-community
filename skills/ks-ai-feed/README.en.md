# AI Kuaishou Feed / ks-ai-feed

---

## Overview

Automatically scans Kuaishou's AI content daily, filters viral videos by play count with intelligent clustering, delivers a dark-themed visual daily report, and provides AI intelligence insights — trending topics, emerging growth signals, key creator analysis, and recommended investigation directions.

**Core Value**

- **Precise Viral Discovery**: Automatically scans Kuaishou AI trending videos by play count and engagement — no more manual searching.
- **Intelligent Topic Clustering**: Automatically identifies content directions and summarizes by category, giving you a clear breakdown of daily hot topics.
- **Multi-Dimensional Intelligence**: Delivers trending topic rankings, growth signals, creator analysis, and recommended investigation directions for deep traffic trend insights.
- **Visual Daily Report**: Dark-themed page with cover images, engagement data, and direct video links — ready for browser viewing and navigation.
- **One-Click Subscription**: Enable daily automatic generation to track Kuaishou AI content trends continuously.

**Who It's For**

- 📊 **Content Operators / Creators** — Stay on top of daily Kuaishou AI trends and quickly get content inspiration.
- 🏢 **MCNs / Brands** — Track AI content trends, identify rising creators and growth signals.
- 🔍 **Industry Researchers** — Access structured intelligence on the Kuaishou AI content ecosystem and traffic landscape.

---

## Features

### Core Capabilities

- **Viral Content Discovery**: Filters Kuaishou AI trending videos by play count and engagement, precisely identifying the day's hottest content.
- **Intelligent Topic Clustering**: Automatically detects topic directions from video content and summarizes counts and proportions by category.
- **AI Intelligence Insights**: Powered by the Intelligence Investigator methodology, generates trending topic rankings, emerging growth signals, key creators, recommended investigation directions, and cross-platform comparison suggestions.
- **Visual Daily Report**: Dark-themed page featuring video cover images, views/likes/comments, and direct video links — ready to browse.
- **One-Click Subscription**: Supports daily automatic report generation for continuous tracking without repeated manual effort.
- **Reliable Cover Image Display**: Built-in anti-leech proxy and automatic image format conversion ensure cover images load properly.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, verify its source, permitted scope, validity period, and whether it supports reset or revocation.
- Never hardcode or expose your key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Phrase | Result |
| ------ | -------------- | ------ |
| Today's Report | "Generate today's Kuaishou AI viral report" | Scans the day's trending content and outputs a visual report with intelligence insights |
| Specific Direction | "Show me what's trending in Kuaishou AI art and AI tutorials" | Focuses on your specified keywords for targeted content matching |
| Historical Review | "Pull up the Kuaishou AI report from June 10th" | Retrieves viral content and trends from a specific date |
| Enable Subscription | "Set up daily Kuaishou AI report subscription for me" | Automatically generates a daily report for continuous tracking |

### Output Example

Once the report is ready, you'll receive:

- **Category Overview Table**: Topic-clustered display of video counts, proportions, and highlights per category — quickly grasp the day's trends.
- **AI Intelligence Insights Report**: Includes emerging growth signals (early identification of potential topics), key creators (high-output, high-engagement authors), recommended investigation directions (scenarios + search keywords), and cross-platform comparison suggestions.
- **Visual Report Page**: Dark-themed, with cover images, full engagement data, and direct video links — ready for browser viewing.
- **Structured Terminal Output**: Tables displayed in the conversation summarizing categorized videos and intelligence insights.

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Daily Trend Tracking | Content Operator | "Is today's Kuaishou AI report ready?" | Quickly understand the day's AI trending content and topic distribution |
| Content Inspiration | Creator | "What AI viral videos on Kuaishou are worth referencing?" | Discover trending content angles and creative patterns |
| Creator Discovery | MCN / Brand | "Who are the active creators in the Kuaishou AI space recently?" | Identify high-engagement creators to support collaboration decisions |
| Trend Forecasting | Industry Analyst | "What new trends are emerging in Kuaishou AI content this week?" | Capture traffic opportunities and plan content direction ahead of time |

---

## Important Data Notes

- **Update Time**: Data from the previous day is updated daily at 15:00.
- **Queryable Range**: Only dates with updated data are available (yesterday and earlier); current-day data is typically unavailable.
- **When Data Is Unavailable**: If the target date's data has not been updated yet, the system will automatically notify you and ask whether to query the latest available date.
