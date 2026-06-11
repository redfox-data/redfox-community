# AI WeChat Public Account Feed / gzh-ai-feed

---

## Introduction

Daily scan of AI WeChat public accounts — find the hottest articles by read count, auto-cluster into topics, and generate a styled HTML daily report. Built-in public API Key — ready to use out of the box.

**Core Value**

- **Smart clustering**: Automatically discovers trending topics — no manual categorization needed.
- **Visual daily report**: Dark-themed HTML with cover images, engagement metrics, and direct article links.
- **Zero-config start**: Built-in public API Key (~10,000 free uses) — just start.

**Target Users**

- 📰 **AI professionals** — Daily AI industry highlights, never miss important updates.
- 📊 **Content operators** — Track AI-niche viral articles to inform editorial decisions.
- 🧠 **Researchers / students** — Aggregate cutting-edge AI information, reduce filtering effort.

---

## Features

### Core Capabilities

- **Viral discovery**: Filter the hottest content from 200+ AI public account articles by read count.
- **Time range query**: Support time-range lookback (start time inclusive, end time exclusive) for flexible historical queries.
- **Smart clustering**: Auto-identify topic directions (Agent, LLM, AI art…); categories are content-driven daily.
- **Terminal table**: Category + title + author + reads/likes/comments at a glance.
- **Visual daily report**: Dark-themed HTML with cover images, engagement data, article links, and date navigation.
- **Full-database search**: Built-in search box in the report page for real-time queries across the entire article library.
- **One-click subscribe**: `--subscribe` to enable daily automated output.

---

## API Key Info

A built-in public API Key provides ~**10,000 free uses** — zero configuration needed. When the quota runs out, register at [RedFoxHub](https://redfox.hk/login?source=github) for a personal API Token:

| Method | Command |
|--------|---------|
| **Environment variable** (recommended) | `export REDFOX_API_KEY=ak_your_key` |
| **CLI argument** | `--api-key ak_your_key` |
| **Config file** | `echo '{"api_key":"ak_your_key"}' > ~/.qoder/apis/redfox.json` |

---

## Usage Guide

Just describe the AI daily report you want — no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|----------------|--------|
| Today's report | "Show me today's AI daily report" | Generate today's viral HTML report |
| Custom focus | "I care about AI Agent and RAG" | Generate report with custom keywords |
| Historical date | "Give me the AI report for May 26" | Generate report for the specified date |
| Time range | "Give me the AI report from June 1st to June 5th" | Flexible lookback for any time period |
| Subscribe | "Auto-generate an AI daily report for me every day" | Install daily scheduled task |

---

## Use Cases

| Scenario | Role | Example query | Benefit |
|----------|------|---------------|---------|
| Daily trend tracking | AI professional | "What's hot in AI today" | One report to grasp daily AI trends |
| Editorial support | Content ops | "What's trending in AI Agent" | Data-driven editorial decisions |
| Ongoing monitoring | Researcher | "Subscribe to daily AI report" | Auto-push at 9 AM — never miss a day |