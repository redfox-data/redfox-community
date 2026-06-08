# WeChat Official Account Benchmarking Tool / wechat-similar-account

---

## Overview

A benchmark account matching tool for WeChat Official Account creators. Using a 3-tier weighted matching system (Core Fundamentals 40% + Operations & Monetization 35% + Data Characteristics 25%), it intelligently recommends peer benchmark accounts and top-tier aspirational accounts—helping creators pinpoint their niche, replicate proven strategies, and plan growth trajectories.

**Core Value**

- **Dual-group smart recommendations**: Delivers both "Peer Benchmarks" (copyable playbooks) and "Top Aspirationals" (mature models to chase) in a single query, meeting needs at every growth stage.
- **3-tier weighted matching**: Core fundamentals (niche/tags/content format/audience profile) + Operations & monetization (cadence/traffic/private domain/revenue) + Data characteristics (engagement structure/viral patterns/resource endowments)—ensuring recommendation precision.
- **7-dimension recommendation reasons**: Each recommended account comes with detailed analysis spanning viral insights, content focus, publishing cadence, engagement rate, and share rate—clear at a glance.
- **Unlisted account sync**: For accounts not yet indexed by the platform, submit the WeChat ID to trigger data synchronization, with a diagnostic report automatically pushed in about 30 minutes.

**Intended Users**

- 📝 **WeChat Official Account creators** — Find benchmark accounts in your niche to learn content strategies and operational tactics.
- 🛍️ **Brand / ad operators** — Screen high-match accounts for advertising placements and business collaborations.
- 🏢 **MCN / content teams** — Analyze niche landscapes at scale and plan differentiated directions for matrix accounts.
- 🌱 **New account launchers** — Reference peer benchmark growth paths to reduce trial-and-error costs.

---

## Features

### Core Capabilities

- **Multi-mode query**: Search by account name, account ID, or account category—also supports combined queries for precise targeting.
- **Peer benchmark recommendations**: Matches accounts with highly similar readership, niche, and content format to yours—directly reference their content strategy and operational methods.
- **Top aspirational recommendations**: Matches top-tier accounts with 3–5× your readership and mature operational models, providing growth directions to pursue.
- **7-dimension detailed analysis**: Each recommendation includes viral insights, content focus, publishing cadence, engagement rate, share rate, RedFox Index, and more.
- **Data sync submission**: For unlisted accounts, submit the WeChat ID to trigger data fetching—the platform automatically retrieves and pushes a diagnostic report.

### Highlights

- **3-tier weighted matching system**: Core fundamentals (40%) + Operations & monetization (35%) + Data characteristics (25%), covering every dimension from content positioning to revenue model.
- **Dual-group differentiated recommendations**: Peer benchmarks focus on "actionable replication"; top aspirationals focus on "directional reference"—serving different needs at different stages.
- **7-dimension personalized reasons**: From viral hits to engagement metrics, every recommended account gets a tailored analysis—not just raw data dumps.
- **No-data, no dead-end**: When no data is found, the system automatically guides you to submit a WeChat ID for sync, with results pushed in 30 minutes—ensuring every query yields an outcome.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`)
- Register at [RedFoxHub](https://redfox.hk?souce=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your query needs in natural language—no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
| ------ | -------------- | ------ |
| Search by account name | "My account is called TechFrontier, help me find benchmark accounts" | Precise name match, outputting both peer benchmarks and top aspirationals |
| Search by account ID | "Find benchmarks for account ID gh_xxx" | Precise ID-based query, same output structure |
| Explore by category | "What benchmark accounts are worth studying in the tech-digital category?" | Category-based query to explore niche landscape and benchmark accounts |
| Submit data sync | "My account isn't indexed yet, WeChat ID is kejiqianyan, sync it for me" | Submit sync request; diagnostic report auto-pushed in ~30 minutes |

### Output Example

After querying, you will receive the following structured analysis:

**Account Basic Info**

- Account name, ID, category, RedFox Index, average read count, past-7-day metrics, and other key indicators
- Recent 5 articles (title, reads, likes, comments, engagement, etc.)

**✨ Peer Benchmarks (5)**: Accounts closest to your readership level—directly reference their content strategy

| Account | RedFox Index | Avg Reads | … | Recommendation Reason |
| … | … | … | … | Multi-dimension analysis: viral insights, content focus, cadence, engagement rate, etc. |

**✨ Top Aspirationals (5)**: Top-tier accounts with 3–5× your readership—mature models to pursue

---

(When no data is found, the system automatically guides you to submit a WeChat ID for sync, ensuring every query yields a result.)

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| -------- | ---- | ---------------- | ------- |
| Account launch reference | New creator | "I just started a tech account—find me peer benchmarks at a similar stage" | Find accounts with copyable tactics at similar stages; lower launch trial-and-error costs |
| Content strategy optimization | Account operator | "My reads have plateaued lately—show me how top accounts in my niche are performing" | Analyze top aspirational content strategies to find optimization directions |
| Ad placement selection | Brand ad operator | "Find tech-digital accounts with 10k+ average reads for me" | Filter high-match accounts by niche and readership for ad placement |
| Niche landscape analysis | MCN / content team | "Analyze the parenting niche competitive landscape for me" | Understand full-niche account distribution; plan differentiated matrix account directions |

---

## Important Data Notes

- Data is sourced from the RedFox data platform; the displayed data retrieval time may differ from real-time figures.
- Recommended account metrics (reads, engagement, etc.) are based on the platform's past-7-day indexed data.
- When searching by category, the platform's classification system may differ from natural language; using a representative account name for lookup is recommended.
- For unlisted accounts, submit the WeChat ID to trigger sync; a diagnostic report will be automatically pushed in about 30 minutes.

---
