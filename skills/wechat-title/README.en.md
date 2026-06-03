# WeChat Official Account Title Generator & Scorer / wechat-title

---

## Introduction

Generate viral WeChat Official Account titles based on trending data, or get multi-dimensional scoring and optimization suggestions for your existing titles.

**Core Value**

- **Analyze Before Creating**: First analyze viral title patterns, then output new titles — clear logic, easy to pick from.
- **Dual-Mode Delivery**: Title generation gives 10 formatted candidates at once; title scoring provides four-dimension grading with optimization direction.
- **Data-Aligned**: All title creation and scoring are based on real WeChat viral article data — no guesswork.

**Who It's For**

- 📝 **WeChat Account Owners** — Stop struggling with titles. Use data patterns to boost click-through rates and readership.
- 📊 **Content Operators / Editors** — Quickly produce multiple title candidates for A/B testing with confidence.
- 🏢 **MCNs / Brands** — Batch-propose titles within the same niche, building reusable title formulas.

---

## Features

### Core Features

- **Title Generation**: Enter a topic, keyword, or niche — the tool first analyzes viral title patterns, then creates 10 new titles, each with a match score, reference viral article link, and recommendation reason.
- **Title Scoring**: Enter an existing title — get a four-dimension evaluation (niche match, click incentive, structure compliance, viral potential) scored out of 100, with optimization suggestions and reference viral titles.
- **Smart Keyword Handling**: Broad category terms trigger a sub-direction recommendation for you to confirm first; specific terms go straight to data matching.
- **Auto Time Expansion**: When data is insufficient, the query time range is automatically expanded — your core keyword is never changed without your consent.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?souce=github) to register and obtain `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing a key, please confirm its source, scope of use, validity period, and whether it supports reset/revocation.
- Never hard-code or expose keys in plain text within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Prompt | Result |
|--------|---------------|--------|
| Generate titles for a topic | "I want to write about skincare, help me come up with some titles" | Matches viral samples by keyword, analyzes first, then outputs 10 candidates |
| Daily niche update | "Career niche, want to post about promotion strategies, give me some titles" | Pulls niche viral patterns, generates matching new titles |
| Refine a broad category | "I want to do food content, but haven't decided on a direction" | Recommends sub-directions first, then queries and generates after your confirmation |
| Catch trending topics | "What titles are trending on WeChat? Help me create a few" | Generates viral titles based on sitewide trending data |
| Score a title | "Help me evaluate this title: XXX" | Four-dimension scoring with optimization suggestions |

### Output Example

After **Title Generation**, you'll receive 10 titles in the following format (illustrative):

**Title 1: This Is the Right Way to Do Skincare**

📈 Match Score: 9.5
🔥 Reference Viral: [Viral title summary](link) (Reads: 100k+)
👍 Reason: "This is" carries a corrective tone, making readers wonder "Have I been doing it wrong?" — perfect for how-to and science articles.

---

(10 titles total, each separated by a divider for easy copying.)

After **Title Scoring**, you'll receive a four-dimension score breakdown, strength analysis, optimization suggestions, and reference viral titles.

---

## Use Cases

| Scenario | Role | Example Prompt | Benefit |
|----------|------|---------------|---------|
| Title for a new post | Account owner | "New product launch, help me write a title highlighting cost-effectiveness" | Quickly get multiple publishable candidates, boost CTR |
| Daily account update | Content operator | "Career niche, posting about promotion strategies this week, give me 10 titles" | Follow niche viral patterns, reduce topic ideation overhead |
| Exploring a broad category | New creator | "I want to do relationship content, but only know the broad category" | Sub-direction refinement before generation, lower trial-and-error cost |
| Title optimization | Editor / Director | "Score this title for me: XXX, how can I improve it" | Diagnose bottlenecks across four dimensions, optimize precisely |
| Adapt trending content | Content strategist | "What titles are trending sitewide? Help me adapt a few" | Apply trending patterns to your specific topics |

---

## Important Data Notes

- Read counts reflect the time of database entry, not real-time data. Counts may continue to grow after entry.
- The database only contains data from yesterday to 30 days ago. Same-day and 30+ day lookbacks are not currently supported.
