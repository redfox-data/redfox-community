# Brand Geo Analysis Plus / brand-geo-analysis-plus

---

## Introduction

One skill, three perspectives: real-time aggregated trending boards + in-depth social media research over the last 30 days + brand visibility analysis in AI search. Together they show you the full picture of how a brand or topic is perceived across the Chinese internet, from "what's trending" to "what users really say" to "what AI answers".

**Core Value**

- **Three complementary perspectives**: trending boards show what is hot right now, social media shows what real users say, and AI search shows how large models describe the brand. Combining all three prevents one-sided conclusions drawn from a single data source.
- **Conclusions, not data dumps**: trending rankings, reputation insights, GEO scores, competitor comparisons and visual reports that are ready to use.
- **Built for the Chinese internet**: platforms and metrics follow local social media conventions, for example the save-to-like ratio on Xiaohongshu as a "seeding" signal, shares on Douyin as reach, and reads on WeChat Official Accounts as attention.

**Who It's For**

- 🏢 **Brand / marketing operations** — daily reputation monitoring, competitor reputation comparison, brand AI visibility diagnosis.
- 📈 **Growth / GEO owners** — see how the brand is described by Doubao, Kimi and DeepSeek, and where to optimise.
- ✍️ **Content creators / editors** — track trending topics across platforms, decide which ones are worth riding, and find angles.
- 🔍 **Consultancies / media agencies** — produce a data-backed brand perception report for clients.

---

## Features

### Core Capabilities

- **Cross-platform trending aggregation**: covers Baidu, Zhihu, Weibo, Douyin, Bilibili, Kuaishou and Toutiao, with a per-platform TOP10 plus an overall summary.
- **Flexible time and scope**: latest (hourly), today, yesterday and this week rankings; full rankings for a single platform; keyword search where broad category words are automatically expanded into related terms.
- **Trend forecasting**: a forward-looking read on trending items to help you judge whether follow-up is worthwhile.
- **In-depth social media research over the last 30 days**: real user discussions from Xiaohongshu, Douyin and WeChat Official Accounts, delivered as a data snapshot, consolidated insights and a visual report.
- **Brand visibility in AI search**: batch queries to Doubao, Kimi and DeepSeek, producing an overall GEO score, brand mention rate, sentiment, competitor comparison and cited sources.
- **Automatic visual reports**: interactive reports for social media research and AI search analysis are generated automatically, with no extra request needed.
- **Full brand perception diagnosis**: combines the trending, reputation and AI-answer layers into one report with layer-by-layer action recommendations.

### Highlights

- **Three perspectives in one**: trending, reputation and AI answers are connected by a single tool, so one diagnosis covers the key steps of brand perception.
- **Use only what you need**: when you only want one thing, use the matching module instead of the full workflow.
- **Independent modules**: if one data source is temporarily unavailable, the other modules still deliver.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please register an account at [RedFoxHub](https://redfox.hk?source=github) to obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing a key, confirm its source, allowed scope, validity period, and whether it supports reset or revocation.
- Never hardcode or expose the key in plain text in code, prompts, logs or output files.

---

## Usage Guide

Just describe the brand, topic or trending item you care about in natural language — there are no commands to memorise.

### Common Requests

| Intent                | Example Request                                                   | What You Get                                                                 |
| --------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Check what's trending | "What is everyone talking about today?"                           | TOP10 trending boards across seven platforms plus an overall summary         |
| Look back by time     | "Yesterday's rankings", "This week's trending topics"             | Cross-platform rankings for the matching time window                         |
| Search a topic area   | "Search sports trends", "What's trending about the Super League?" | Broad category words expand into related terms; precise terms are used as-is |
| Focus on one platform | "Weibo rankings", "Show the full Bilibili list"                   | The complete ranking for that platform                                       |
| Track a brand         | "How has my brand been discussed on Xiaohongshu this month?"      | 30 days of real discussion across three social platforms + insights + report |
| See how AI rates it   | "How do Doubao and Kimi describe our brand?"                      | GEO score, mention rate, sentiment, competitor comparison, sources + report  |
| Run a full diagnosis  | "Put together a full perception report for my brand"              | One combined trending → reputation → AI report with action recommendations   |
| Keep monitoring       | "Subscribe to daily updates"                                      | Scheduled digest of trending boards and highlights                           |

### Sample Output

When you want the full picture of a brand, you receive a layered diagnosis along these lines (illustrative):

> **One-line conclusion**: The brand is actively discussed on social media with largely positive sentiment, yet its mention rate in AI search recommendation questions remains clearly low — a visibility gap.
>
> **1. Trending layer**: whether it appears in recent trending items, which platforms it covers, and its direction.
> **2. Reputation layer**: real user feedback, positive and negative signals, key discussion themes.
> **3. AI layer**: GEO score, mention rate (with a per-platform breakdown), sentiment distribution, competitor comparison, main cited sources.
> **4. Action recommendations**: whether to ride the trend, which negative feedback to address, and where to optimise GEO.

---

## Use Cases

| Scenario                         | Role                     | Example Question                                                    | Benefit                                                                |
| -------------------------------- | ------------------------ | ------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Brand reputation monitoring      | Brand / marketing ops    | "How has our brand been discussed over the past month?"             | Quickly grasp real social sentiment and positive/negative signals      |
| Competitor reputation comparison | Marketing / growth       | "Compare how A and B are received on Xiaohongshu and Douyin"        | See differences in user discussion and each side's weaknesses          |
| AI visibility diagnosis          | Brand / GEO owner        | "How would Doubao, Kimi and DeepSeek recommend products like ours?" | Quantify brand visibility in AI search and locate optimisation areas   |
| Riding trends for content        | Creator / editor         | "What's trending today that we could ride?"                         | Judge trend direction and timing, reducing wasted topic exploration    |
| Full brand diagnosis             | Brand lead / consultancy | "Put together a full perception report for my brand"                | One report and action plan covering trending, reputation and AI layers |

---

## Important Data Notes

- Trending boards update hourly and by default cover "the previous full hour"; today, yesterday and weekly boards use their respective windows.
- Social media research covers a rolling 30-day window; AI search analysis is based on live queries whose answers change over time and with model versions.
- A single AI search analysis uses a limited number of questions (typically 8–12), so it is a small-sample observation that is best cross-checked against other data.
- Brand mention detection relies on keyword matching of the brand name and aliases, so same-name brands may cause false matches; some AI platforms do not return external links, in which case an empty source list is normal and does not mean the brand website was not cited.

---
