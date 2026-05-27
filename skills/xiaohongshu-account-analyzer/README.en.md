# Xiaohongshu Account Analyzer

---

## Introduction

A diagnostic specialist deeply versed in Xiaohongshu account analysis, skilled at letting data speak and helping you uncover your account's real issues.

**Core Value**

From vague positioning to monetization struggles, from topic confusion to update bottlenecks — get a data-driven seven-dimension quantitative score (positioning, followers, topics, covers, viral posts, engagement, output capacity) benchmarked against industry averages, an actionable diagnostic report with optimization recommendations, and similar account suggestions.

**Who It's For**

- 📱 Xiaohongshu creators — Diagnose account health, identify issues and find optimization directions
- 📦 Content operators — Evaluate commercial value, develop account growth plans
- 🏢 Brands — Evaluate influencer partnership value, match advertising candidates
- 🔍 Competitor analysis — Compare and analyze competitor accounts, formulate competitive strategies

---

## Core Capabilities

- **Seven-dimension scoring diagnosis**: Account positioning, follower profile, topic system, cover style, viral post ability, engagement scale, update output
- **Life cycle analysis**: Evaluate account stage and growth potential based on data
- **Actionable prescription generation**: Provide implementable optimization suggestions for identified issues
- **Similar account recommendations**: Suggest 2–5 similar accounts worth learning from
- **Multi-account comparative analysis**: Compare multiple accounts side-by-side, output key differences and individual development suggestions
- **HTML visual report**: Generate a diagnostic report with image export support

---

## API key source and security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [Redfox Hub](https://redfox.hk/dashboard/keys?souce=github) (`https://redfox.hk`) for API authentication.
- Before providing the key, confirm its source, available scope, validity period, and whether reset/revocation is supported.
- Do not hard-code or expose the key in plaintext within code, prompts, logs, or output files.

---

## Prerequisites

### Register a Redfox Hub account to obtain REDFOX_API_KEY

- Get REDFOX_API_KEY (apply at [Redfox Hub](https://redfox.hk/dashboard/keys?souce=github))

### Environment variables

| Variable         | Required | Notes          |
| ---------------- | -------- | -------------- |
| `REDFOX_API_KEY` | Yes      | API access key |

**macOS (zsh)**

Append one line to the end of `~/.zshrc` (replace the value in quotes with your key):

```bash
export REDFOX_API_KEY="your_api_key_here"
```

Then run:

```bash
source ~/.zshrc
```

**Windows (PowerShell)**

- **Current terminal only**: Takes effect immediately after run, **no other commands needed**; lost when the window is closed.

```powershell
$env:REDFOX_API_KEY = "your_api_key_here"
```

- **Persist to user environment**: After running `setx`, the **current PowerShell window still won't have the variable**; you need to **close and reopen** the terminal (or restart Cursor / VS Code, etc.) for the new window to read `REDFOX_API_KEY`.

```powershell
setx REDFOX_API_KEY "your_api_key_here"
```

---

## Usage Guide

### Common Phrases Quick Reference

| Intent                    | Example phrase                                    | Result                                                                            |
| ------------------------- | ------------------------------------------------- | --------------------------------------------------------------------------------- |
| Single account diagnosis  | "Analyze Xiaohongshu account 26112666886"         | Output a complete seven-dimension diagnostic report                               |
| Multi-account comparison  | "Compare ID1 and ID2 for me"                      | Output each account's report + side-by-side comparison summary                    |
| View similar accounts     | Reply with number "1" to select a similar account | Run a full diagnosis on the selected account                                      |
| Real-time data collection | When account not found, reply "Push in 30min"     | Triggers real-time collection; auto-pushes the diagnostic report after 30 minutes |

### Input Format

**⚠️ Must provide the Xiaohongshu ID (numeric or alphanumeric), not a Chinese nickname**
![alt text](image.png)
| Valid input | Example |
| --- | --- |
| Numeric ID | `26112666886` |
| Alphanumeric ID | `Esther1218`, `abc123` |
| ❌ Invalid input | `Xiaohongshu Creator`, `Username123` |

---

## Output Example

### Single Account Diagnostic Report

**📊 Overall Score: 78/100**

| Positioning | Follower Profile | Topic System | Cover Style | Viral Ability | Engagement Scale | Update Output |
| :---------: | :--------------: | :----------: | :---------: | :-----------: | :--------------: | :-----------: |
|    8/10     |      12/15       |    11/15     |    7/10     |     12/15     |      16/20       |     12/15     |

---

**🎯 Account Positioning (8/10)**
Detailed analysis

**👥 Follower Profile & Needs (12/15)**
Detailed analysis

**📝 Topic System (11/15)**
Detailed analysis

**🖼️ Cover Style (7/10)**
Detailed analysis

**🔥 Viral Post Ability (12/15)**
Detailed analysis

**💬 Engagement Scale (16/20)**
Detailed analysis

**⚡ Update Output (12/15)**
Detailed analysis

---

**🏥 Actionable Prescription**

Based on the diagnostic results, the following optimization directions are recommended:

xxxxxxxxxxxxxxxxxxxxxxxxxxx

---

**📈 Similar Account Recommendations**

1. **[Account name](https://www.xiaohongshu.com/user/profile/xxx)**
   | Followers: 8.2w | Total engagement: 32w | Activity score: 85
   | Reason: Similar topic direction, worth learning from
   | Posting style: Steady practical content, consistent cover style
   | What to learn: Fixed update rhythm

2. **[Account name](https://www.xiaohongshu.com/user/profile/xxx)**
   | Followers: 15.6w | Total engagement: 58w | Activity score: 88
   | Reason: High content quality, high viral post rate
   | Posting style: Primarily in-depth content, high engagement rate
   | What to learn: Topic depth and engagement guidance

Reply with the number to continue analysis!

---

⚡ **HTML report generated**, click to download and view the full report

---

### Multi-Account Comparison Report

**Accounts compared**: Account A vs Account B

**📊 Comparison Overview**

| Dimension             | Account A | Account B | Difference analysis               |
| --------------------- | --------- | --------- | --------------------------------- |
| Overall score         | 78        | 72        | Account A performs better overall |
| Followers             | 12.3w     | 8.6w      | A leads in follower count         |
| Viral post rate       | 18%       | 12%       | A has stronger viral ability      |
| Weekly post frequency | 3         | 2         | A updates more consistently       |

---

**Key Differences**

- **Account A**: Clear positioning, steady practical content output, high viral post rate
- **Account B**: Diverse content but vague positioning, lower follower loyalty

**Common Issues**

- Cover style consistency needs improvement
- Topic direction could be more focused

**Development Suggestions**

- **Account A**: Maintain steady updates, try more in-depth content
- **Account B**: Clarify positioning direction, increase content verticality

---

## Use Cases

| Scenario                        | Role                    | Example question                            | Benefit                                                                    |
| ------------------------------- | ----------------------- | ------------------------------------------- | -------------------------------------------------------------------------- |
| Account self-diagnosis          | Xiaohongshu creator     | "Help me analyze my account sssss123"       | Identify issues, get optimization suggestions                              |
| Competitor account analysis     | Content operator        | "Analyze this competitor account sssss123"  | Understand competitor strengths/weaknesses, formulate competitive strategy |
| Influencer placement evaluation | Brand                   | "Evaluate this influencer sssss123's value" | Determine suitability for advertising partnership                          |
| Multi-account comparison        | Operations team         | "Compare sssss123 and sssss456 accounts"    | Side-by-side comparison, develop growth strategy                           |
| Account health check            | Self-media professional | "Check account sssss123's health"           | Quick overview of account status                                           |

---

## Important Data Notes

- **Account data scope**: Million-level Xiaohongshu account database. Rare cases may have no account data available.
- **No account data handling**: When search finds no data, the tool prompts the user to accept a push notification, which triggers real-time collection. The diagnostic report is automatically pushed after 30 minutes.
- **Analysis data scope**: Based on account data and posts from the past 7 days; updated daily with yesterday's incremental data.
- **Data discrepancy note**: Data is current as of ingestion time, not real-time; engagement may continue to grow after ingestion
