# Playlet WeChat Official Accounts Feed / playlet-wechat-feed

---

## Overview

Playlet WeChat Official Accounts Feed is a trending content tracking tool designed for short drama creators and content operators. It scans WeChat official account short drama content daily, filters popular works by read count, intelligently clusters by genre direction, and generates a visualized HTML daily report with creative trend analysis.

**Core Value**

- 🔥 Discover trending short drama articles from WeChat official accounts and pinpoint high-engagement works
- 📊 Get genre-clustered popular content at a glance to understand hotspot distribution
- 📈 Analyze trending title patterns and creative trends to uncover traffic strategies
- 🔔 Enable daily subscription for automatic report generation and intelligence system setup

**Target Users**

- ✍️ Short Drama Scriptwriters — Identify genre trends and improve topic selection accuracy
- 📱 Content Operators — Track daily short drama trends from WeChat official accounts and drive content decisions
- 🏢 MCN Agencies — Monitor industry dynamics and manage multi-account content direction
- 📝 Official Account Owners — Discover benchmark accounts and trending content to optimize creative strategies

---

## Features

### Core Features

- **Trending Discovery** — Filter popular short drama content from WeChat official accounts by read count, precisely locating high-engagement works
- **Genre Clustering** — Automatically identify genre directions (Time Travel / CEO Romance / Rebirth / Suspense / Sweet Romance / Comeback / Period Drama / War God / Historical), with daily dynamic genre classification
- **Smart Query** — Query all short drama content by default, automatically expanding genre batch queries when data is insufficient to save API quota
- **Custom Query** — Support targeted queries by genre, official account, or keywords, flexibly covering any short drama niche
- **Creative Insights** — Analyze trending title patterns, genre trends, and official account performance for in-depth creative pattern discovery
- **Visual Daily Report** — Dark-themed HTML report with cover images, engagement data, and direct article links
- **One-Click Subscription** — Automatically generate daily reports saved to local folder after activation

### Highlights

- ⚡ **Batch Query** — Query all genres at once via batch API, efficiently reducing API call count
- 🧠 **Smart Clustering** — Auto-classify into 9 genres with dynamic daily adjustment
- 💾 **Caching** — 1-hour validity to avoid duplicate requests and enable quick result review
- 📅 **Intelligent Date Check** — Automatically validate target date availability to avoid invalid calls

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, verify its source, available scope, expiration date, and whether it supports reset/revocation.
- Never hardcode or expose your API key in plain text within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Phrase | Result |
|--------|---------------|--------|
| Latest Report | "Show me today's short drama WeChat report" | Generate the latest visualized daily report |
| Query by Genre | "Short drama articles in the time travel genre", "Show me CEO romance and sweet romance content" | Get trending content in specified genres |
| Query by Time | "What are the short drama trends this month", "Short drama hits in June" | Analyze content trends over a period |
| Historical Review | "Do you have the short drama WeChat report for June 10th" | View trending data for a specific date |
| Combined Query | "Time travel genre short dramas in June" | Precisely locate specific genre + time range |
| Subscription | "Enable daily short drama report subscription" | Auto-generate and save daily reports |
| Quick Cache View | "Show me the last short drama results from cache" | Quick view without API call within 1 hour |

### Sample Output

After generating the report, the terminal outputs a genre classification table and creative trend analysis report, while a dark-themed HTML visual report is generated and automatically opened in the browser. The HTML report includes:

- Genre card layout clearly showing genre distribution
- Each article displays cover image, title, official account name, read count, likes, and comments (fields with 0 value are automatically hidden)
- Statistics panel: genre count, article count, average reads, total reads

Below is a real output example from 2026-06-15:

---

## Playlet WeChat Feed · 2026-06-15 Daily Report

**Scanned 176 trending short drama articles, clustered into 6 genre directions**

---

### Genre Overview

| Genre | Count | Share | Highlight |
|-------|-------|-------|-----------|
| #Other | 156 | 88.6% | "Value Upgrade: The 2.0 Era of Short Dramas and Celebrities" 23k reads, AI short drama tool content surging |
| #SweetRomance | 7 | 4.0% | "Hot Plant Whisper" cozy bedtime stories, avg 800+ reads, stable audience |
| #CEORomance | 6 | 3.4% | Clara transitioning to short drama actress sparks discussion, top article 4,905 reads |
| #Suspense | 3 | 1.7% | "Truth Behind Short Drama Actor's Passing" 3,801 reads, gossip content drives strong engagement |
| #TimeTravel | 3 | 1.7% | Shaanxi short drama base's million-yuan sets face cold reception, industry analysis content gains traction |
| #Historical | 1 | 0.6% | "Historical Hairstyle Prompts for Short Dramas" 1,058 reads, AI creation-assist content breaks out |

---

### Creative Trend Analysis

**I. Emerging Growth Signals**

- 🔥 **#Historical** — Only 1 article but 3.6% like rate (38 likes / 1,058 reads), AI-assisted creation tools show engagement far above average, prompt/workflow content has sustained breakout potential
- 🔥 **#Suspense** — Only 3 articles but top read at 3,801, gossip + industry insider combo titles outperform market average

**II. Trending Title Patterns**

| Pattern | Occurrences | Example | Avg Reads |
|---------|-------------|---------|-----------|
| Exclamation emotional hook (！) | 93 | "OiiOii 2.0 Major Upgrade, Short Drama E-commerce Is About to Explode..." | 1,374 |
| Question suspense hook (？) | 55 | "As Boundaries Blur, What Opportunities Exist for Actors in the 100B Short Drama Market?" | 1,325 |
| "N titles" listicle format | 13 | "5 Addictive High-Rated Short Dramas! CEO Romance, Urban Healing" | 1,072 |
| AI + tool/platform name | 15 | "700M Plays, I Found the Godly Tool Behind These AI Short Dramas!" | ~6,500 |

**III. Top Official Accounts**

No official account data available (API did not return accountName field today)

**IV. Genre Trend Report**

**Genre**: #SweetRomance
**Count**: 7 articles
**Avg Reads**: ~900
**Top Work**: "Hot Plant Whisper" by Dick Lamb (cozy sweet bedtime story) — 1,258 reads

**Genre Traits**: Sweet romance focuses on "bedtime stories," "couple avatars," and "hidden gem recommendations." Titles typically include emotional keywords like "sweet," "healing," and "happy ending." Audience stickiness is high but traffic ceiling is relatively low.
**Creative Advice**: Combine "CP-oriented" fan content and cross-genre tags (sweet romance × historical, sweet romance × time travel) for broader reach. Add completion-promise hooks like "binge-worthy," "hidden gem," or "super sweet ending" to boost clicks.

**V. #CEORomance**

**Genre**: #CEORomance
**Count**: 6 articles
**Avg Reads**: ~2,911
**Top Work**: "'Asia's Most Beautiful Woman' Clara, Rejected by Elite Family, Transitions to Short Drama Actress!" — 4,905 reads

**Genre Traits**: Today's CEO romance buzz is driven by "celebrity entering short dramas" gossip rather than traditional CEO romance plot recommendations. Contrast words like "elite family," "career switch," and "rejected" form the core traffic hooks.
**Creative Advice**: Leverage celebrity/actor news as entry points for CEO romance content. Use "identity contrast + twist" title formula (e.g., "Rejected by XX, transitions to XX"). Combine with "high-rated collection" listicles for long-tail traffic.

**VI. #Suspense**

**Genre**: #Suspense
**Count**: 3 articles
**Avg Reads**: ~2,047
**Top Work**: "Truth Behind Short Drama Actor's Passing, Angela An Returns, Minghao Hou Testing Waters..." — 3,801 reads

**Genre Traits**: Suspense content today presents as "industry gossip + truth reveals." Titles chain multiple celebrity names with suspense question marks. Anti-fraud AI micro-drama (1,718 reads) represents policy-driven content; overall count is low but per-article engagement exceeds market average.
**Creative Advice**: Suspense on WeChat works better for "insider reveals" and "truth reconstruction" non-fiction directions. Stack multiple celebrity/event names in titles for information density. Watch for "anti-fraud" and "social issues" policy trends for platform traffic boosts.

**VII. Cross-Genre Comparison**

- **#CEORomance × #SweetRomance** — Monitor "CEO sweet romance" compound tag collaborations. Today's "5 Addictive High-Rated Short Dramas! CEO Romance, Urban Healing" (2,606 reads) validates the compound genre collection format. Further audience overlap analysis recommended.
- **#AIShortDrama (hidden theme within Other) × All Genres** — Today's 38 AI short drama articles averaged 2,630 reads, far exceeding the market average of 1,994. "Production tutorials / tool reviews" combining AI tools with any genre represent a significant traffic opportunity. Creators across all genres should pay attention to AI production workflow content.

---

**Report Path**: `C:\Users\Downloads\QoderReports\短剧公众号日报_2026-06-15.html`

> Data note: Updated daily at 15:00 with previous day's data

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|--------------|---------|
| Topic Research | Scriptwriter | "What short drama genres are trending lately? Analyze time travel and rebirth for me" | Identify genre trends and improve topic selection accuracy |
| Report Tracking | Content Operator / MCN | "Enable daily report subscription to track WeChat short drama trends for me" | Build a team intelligence system and drive content decisions |
| Competitor Analysis | Brand Manager / Ad Manager | "Show me CEO romance short drama performance on WeChat in June" | Adjust promotion strategies and optimize content differentiation |
| Trend Review | Content Director / Data Analyst | "Compare this month's and last month's short drama trend changes" | Master mid-to-long-term trends and guide content strategy planning |
