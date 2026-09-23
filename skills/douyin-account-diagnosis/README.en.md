# Douyin Account Diagnosis / douyin-account-diagnosis

---

## Overview

One-click diagnosis of your Douyin account's operational health. Simply provide an account nickname or Douyin ID to automatically fetch account profile and recent content data. Receive a quantified diagnosis across six dimensions, with a 100-point composite score, dimension breakdown, risk alerts, and optimization directions — all in a well-structured report ready within minutes.

**Core Value**

- **Full-dimensional quantification**: Covers six dimensions — account profile, content productivity, engagement health, content quality, content trends, and follower quality — leaving no blind spots.
- **Automatic risk alerts**: Six risk types (zombie followers, engagement manipulation, decline, shadow-ban, inactivity, single-hit dependency) are automatically identified and ranked by severity.
- **Ready-to-use reports**: Standard formatted output with explainable scores and verifiable conclusions, ready for team presentations, competitive analysis, or partnership evaluations.

**Intended Users**

- 📊 **Douyin operators** — Self-audit account health, identify weak spots, and get actionable optimization directions.
- 🏢 **MCNs / Brands** — Evaluate creator account quality at scale, screen for collaboration risks, and support signing decisions.
- 🔍 **Content creators** — Benchmark against competitors, identify gaps, and shape content strategy.

---

## Features

### Core Capabilities

- **One-click data retrieval**: Enter a nickname or Douyin ID to automatically pull account profile and recent content — no manual data collection needed.
- **Six-dimension quantified diagnosis**: Scores are calculated for account profile, productivity, engagement, quality, trends, and follower quality, then weighted into a composite score.
- **100-point composite scoring**: A weighted composite score with a four-tier rating (Excellent / Normal / Needs Improvement / At Risk) — understand account health at a glance.
- **Risk alerts**: Automatically detects zombie followers, engagement manipulation, decline, shadow-ban, inactivity, and single-hit dependency, with detailed data interpretation.
- **Recent content details**: All recent content with engagement data is displayed by default, with clickable titles linking directly to each piece — every conclusion is backed by evidence.

### Highlights

- **Tier-adaptive benchmarks**: thresholds are tiered by account scale (S / A / B / C). A 1.55% engagement rate counts as *good* for a 6.7M-follower account (≈100K engagements per post) but as *low* for a 50K-follower one — a single absolute threshold systematically misjudges large accounts. The reverse also holds: absolute-volume sub-items (hit rate, average engagements, total works, average likes) are tiered too, so a 4,852-engagement post is not penalised for a small account nor flattered for a huge one.
- **Output volume vs. efficiency are both comparable**: total works and average likes per work are tiered by scale as well (niche-production accounts post rarely by nature; average likes rise with scale). After relativisation, a **93.6× efficiency gap is no longer flattened by a capped score** — an S-tier boutique account and an A-tier high-volume account can finally be told apart.
- **Transparent, auditable scoring**: every score follows clear rules; the report states the benchmarks applied to that account, so the diagnosis is traceable rather than a black box.
- **Automatic alert triggering**: anomalies are detected automatically without manual monitoring, categorised by risk level; alert thresholds share the same tier lines as the scoring, so "good score but zombie-follower alert" contradictions cannot occur.
- **Insufficient data neither penalises nor rewards**: sub-items that are **mathematically degenerate** on small samples (with 2 posts the median always equals the mean; max/mean can never exceed 2×) or **mathematically undefined** (0/0 ratios when engagement is all zero, missing fields) are excluded from the denominator and renormalised, marked `(not counted)` in the report.
- **"No content" is not "no data"**: if the API returns no posts at all, the account genuinely has nothing to evaluate — a negative signal. Those sub-items are scored at their floor and **not** excluded, with a `ⓘ no recent content data` note, so an account that cleared its posts cannot inflate its score by shrinking the denominator.
- **Non-discriminating sub-items are no longer scored**: `gender`/`age` used to be scored, but a returned field is always valid, so it always scored full marks and diluted the penalties for other missing fields. It is now display-only; the account-profile dimension is scored out of 8 instead of 10.
- **Low-confidence notice**: when fewer than 5 posts are returned, an extra "ⓘ data confidence" line flags which conclusions rest on too small a sample.
- **Dirty data auto-correction**: when the crawl timestamp lags behind the newest post, activity and inactivity checks fall back to the current time and label the correction — no more "posted -77 days ago".
- **Trends are not fooled by snapshot age**: the API returns a snapshot of cumulative engagement, so newer posts necessarily show less. Trend metrics (including the decline alert) therefore compare only posts **at least 3 days old**; with too few mature posts the sub-item is excluded rather than reporting a false decline.
- **Ready-to-use reports**: standard Markdown output that can be copied directly into team docs, weekly reports, or partnership evaluation materials.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk?source=github`).
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe the account you want to diagnose in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Phrase | Result |
| ------ | -------------- | ------ |
| Diagnose by nickname | "Diagnose the Douyin account XX" | Fuzzy match by nickname and output full diagnostic report |
| Diagnose by Douyin ID | "Analyze this Douyin ID 66456544107" | Exact match by ID and output full report |
| Account health check | "Give XX a Douyin health check" | Six-dimension diagnostic report |
| Evaluate for partnership | "Evaluate if this account is worth collaborating with" | Score, rating, and risk alerts |

### Output Example

The diagnostic report includes the following sections:

- **Summary line**: Nickname + composite score + rating — understand the conclusion at a glance
- **Basic info table**: Nickname, Douyin ID, UID, follower count, content count, region, etc.
- **Six-dimension score table**: Score, max points, and one-line evaluation per dimension; weakest dimensions are bolded
- **Risk alerts**: Each alert type with specific data interpretation
- **Key findings**: Strengths and weaknesses in two groups, each with supporting data
- **Recent content details**: Publish time, likes/comments/shares/total engagement per piece; titles link directly to content
- **Optimization suggestions**: Prioritized improvement directions based on diagnostic data

---

## Use Cases

| Scenario | Role | Example Question | Benefit |
| -------- | ---- | ---------------- | ------- |
| Account self-audit | Douyin operator | "Diagnose my Douyin account for me" | Quickly identify weak spots and get actionable suggestions |
| Competitive analysis | Brand / MCN | "Analyze this competitor account's data" | Benchmark performance and develop differentiation strategies |
| Creator screening | MCN / Brand | "Evaluate if this creator is worth signing" | Data-driven quality assessment to reduce partnership risk |
| Account valuation | Investor / BD | "Check this account's follower quality and growth potential" | Quantify commercial value to support decisions |

---