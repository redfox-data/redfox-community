# Xiaohongshu Account Diagnostics / xiaohongshu-account-analyzer

## Introduction

A Xiaohongshu account analyst who speaks with data — helping you uncover your account's real issues.

**Core Value**

From unclear positioning to monetization struggles, from topic confusion to update bottlenecks — get a data-backed seven-dimension quantitative score (positioning, followers, topics, covers, viral posts, engagement, output capacity), a diagnostic report benchmarked against industry averages, actionable optimization advice, and similar account recommendations.

**Who It's For**

- 📱 Xiaohongshu creators — Diagnose account health, find issues, and get optimization direction
- 📦 Content operations — Evaluate commercial value and plan account growth
- 🏢 Brands — Assess influencer partnership value and match ad candidates
- 🔍 Competitor analysis — Compare competitor accounts and shape competitive strategy

## Core Capabilities

- **Seven-dimension scoring**: Account positioning, follower profile, topic system, cover style, viral post ability, engagement scale, update output
- **Lifecycle analysis**: Assess account stage and growth potential from data
- **Action prescriptions**: Actionable optimization advice for identified issues
- **Similar account recommendations**: Recommend 2–5 accounts worth learning from
- **Multi-account comparison**: Side-by-side comparison with core differences and development advice
- **HTML visual report**: Diagnostic report exportable as image

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?souce=github) to obtain your `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` as a device environment variable before using this skill.
- Before providing your key, confirm its source, available scope, validity period, and whether reset/revocation is supported.
- Do not hard-code or expose the key in plaintext in code, prompts, logs, or output files.

---

## Usage Guide

### Quick phrase reference

| Intent                   | Example phrase                                | What you get                                           |
| ------------------------ | --------------------------------------------- | ------------------------------------------------------ |
| Single account diagnosis | "Analyze Xiaohongshu account 26112666886"     | Full seven-dimension diagnostic report                 |
| Multi-account comparison | "Compare and analyze ID1 and ID2"             | Report per account + horizontal comparison summary     |
| View similar accounts    | Reply with number "1" to select               | Full diagnosis for the selected account                |
| Real-time data backfill  | When account not found, reply "push in 30min" | Triggers real-time collection; report pushed in 30 min |

### Input format

**⚠️ You must provide the Xiaohongshu account ID (digits or alphanumeric), not a Chinese nickname**
![alt text](image.png)

| Valid input      | Example                              |
| ---------------- | ------------------------------------ |
| Numeric ID       | `26112666886`                        |
| Alphanumeric ID  | `Esther1218`, `abc123`               |
| ❌ Invalid input | `Xiaohongshu blogger`, `username123` |

---

## Sample output

### Single account diagnostic report

**📊 Overall score: 78/100**

| Positioning | Followers | Topics | Covers | Viral posts | Engagement | Output |
| :---------: | :-------: | :----: | :----: | :---------: | :--------: | :----: |
|    8/10     |   12/15   | 11/15  |  7/10  |    12/15    |   16/20    | 12/15  |

---

**🎯 Account positioning (8/10)**
Detailed analysis

**👥 Follower profile & needs (12/15)**
Detailed analysis

**📝 Topic system (11/15)**
Detailed analysis

**🖼️ Cover style (7/10)**
Detailed analysis

**🔥 Viral post ability (12/15)**
Detailed analysis

**💬 Engagement scale (16/20)**
Detailed analysis

**⚡ Update output (12/15)**
Detailed analysis

---

**🏥 Action prescription**

Based on the diagnosis, suggested optimization directions:

xxxxxxxxxxxxxxxxxxxxxxxxxxx

---

**📈 Similar account recommendations**

1. **[Account name](https://www.xiaohongshu.com/user/profile/xxx)**
   | Followers: 82K | Total engagement: 320K | Activity score: 85
   | Why recommended: Similar topic direction, worth learning
   | Posting traits: Stable practical content output, consistent cover style
   | What to learn: Fixed update rhythm

2. **[Account name](https://www.xiaohongshu.com/user/profile/xxx)**
   | Followers: 156K | Total engagement: 580K | Activity score: 88
   | Why recommended: High content quality, strong viral rate
   | Posting traits: In-depth content, high engagement rate
   | What to learn: Topic depth and engagement hooks

Reply with a number to continue analysis!

---

⚡ **HTML report generated** — click to download the full report

---

### Multi-account comparison report

**Compared accounts**: Account A vs Account B

**📊 Comparison overview**

| Dimension      | Account A | Account B | Difference analysis               |
| -------------- | --------- | --------- | --------------------------------- |
| Overall score  | 78        | 72        | Account A performs better overall |
| Followers      | 123K      | 86K       | A leads in follower count         |
| Viral rate     | 18%       | 12%       | A has stronger viral ability      |
| Weekly updates | 3 posts   | 2 posts   | A updates more consistently       |

---

**Core differences**

- **Account A**: Clear positioning, stable practical content output, high viral rate
- **Account B**: Diverse content but unclear positioning, lower follower stickiness

**Shared issues**

- Cover style consistency needs improvement
- Topic direction could be more focused

**Development advice**

- **Account A**: Keep stable updates, try more in-depth content
- **Account B**: Clarify positioning, improve content verticality

---

## Use Cases

| Scenario              | Role                | Example question                                 | Benefit                                        |
| --------------------- | ------------------- | ------------------------------------------------ | ---------------------------------------------- |
| Self-diagnosis        | Xiaohongshu creator | "Analyze my account sssss123"                    | Find issues and get optimization advice        |
| Competitor analysis   | Content ops         | "Analyze this competitor account sssss123"       | Understand strengths/weaknesses, plan strategy |
| Influencer evaluation | Brand               | "Evaluate this creator sssss123 for partnership" | Decide if suitable for ad collaboration        |
| Multi-account compare | Ops team            | "Compare accounts sssss123 and sssss456"         | Side-by-side comparison for growth strategy    |
| Health check          | Creator             | "Check health of account sssss123"               | Quick snapshot of account status               |

---

## Important data notes

- **Account data scope**: Million-scale Xiaohongshu account library. Occasionally an account may not be found.
- **When account data is missing**: Prompt user to accept push; triggers real-time collection. Diagnostic report auto-pushed in 30 minutes.
- **Analysis data scope**: Based on account data and posts from the past 7 days; daily update with yesterday's incremental data.
- **Data lag note**: Data cutoff is ingestion time, not real-time; engagement may continue growing after ingestion.
