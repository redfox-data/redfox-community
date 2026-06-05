# Douyin Account Diagnosis / douyin-account-diagnosis

---

## Overview

Enter a Douyin account name or ID to receive a comprehensive diagnosis across four dimensions—account scale, content performance, operational activity, and platform index—with a **100-point quantified score** and a full diagnostic report in one click.

**Core Value**

- **Four-dimension quantified scoring**: Account scale + Content performance + Operational activity + Platform index—say goodbye to subjective judgment
- **Scoring breakdown + Diagnostic report**: Automatically generates the scoring process and a full diagnostic report with traceable data
- **Strengths / Weaknesses + Optimization suggestions**: Data-driven analysis with targeted optimization directions

**Intended Users**

- 🏢 **Brands / MCN agencies** — Replace intuition with data for science-based influencer partnership evaluation
- 📱 **Douyin creators / Self-media** — Understand your account performance and find optimization directions
- 📊 **Content operators** — Regularly monitor account health and guide publishing strategy adjustments

---

## Features

### Core Capabilities

- **Four-dimension scoring**: Account scale (35 pts) + Content performance (35 pts) + Operational activity (20 pts) + Platform index (10 pts) = 100 pts, unified standard for cross-account comparison
- **Full diagnostic report**: Automatically generates scoring breakdown + basic info / core data / comprehensive score / optimization suggestions
- **Flexible querying**: Supports fuzzy matching by nickname or exact matching by Douyin ID
- **Smart optimization suggestions**: Automatically generates strengths / weaknesses analysis and 3 optimization suggestions based on scoring data

### Highlights

- **Precise data-driven**: Based on RedFoxHub API for real data, all scores are traceable
- **Standardized scoring system**: Unified 100-point scoring standard for cross-account comparison, avoiding subjective judgment
- **Compatible with incomplete data**: Automatically uses alternative metrics when play count is unavailable, without affecting the overall score
- **Automatic category mapping**: API-returned account categories are automatically mapped to unified output names

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?souce=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply say the Douyin account you want to diagnose in natural language—no fixed commands to memorize.

### Quick Reference

| Intent | Example Phrase | Result |
|--------|----------------|--------|
| Diagnose by nickname | "Diagnose Douyin account Liangtian" | Fuzzy match nickname, generate full diagnostic report |
| Diagnose by Douyin ID | "Diagnose Douyin ID liangtian5147" | Exact match Douyin ID, generate full diagnostic report |
| Natural language trigger | "Liangtian Douyin analysis" | Auto-detect account and intent, output diagnosis results |

### Output Example

After diagnosis, you will receive a scoring breakdown followed by a full diagnostic report:

**Scoring Breakdown (illustrative)**:

```text
**Dimension 1: Account Scale (35 pts)**
+ Followers 201,242,077 (≥50M) → 22 pts
+ Total likes 18,112,283,863 (≥1B) → 8 pts
+ Likes/Followers ratio ≈ 90.0 (≥15) → 5 pts
+ **Subtotal: 35 pts (full score)**

**Overall Score: 93.0 pts — 🏆 S-tier Benchmark Account**
```

**Diagnostic Report (illustrative)**:

| Dimension | Score | Max | Score Rate |
|-----------|-------|-----|------------|
| Account Scale | 35.0 | 35 pts | 100.0% |
| Content Performance | 29.0 | 35 pts | 82.9% |
| Operational Activity | 20.0 | 20 pts | 100.0% |
| Platform Index | 10.0 | 10 pts | 100.0% |
| **Overall** | **94.0** | **100 pts** | **94.0%** |

---

## Use Cases

| Scenario | Role | Example Question | Benefit |
|----------|------|------------------|---------|
| Influencer partnership evaluation | Brand marketing manager | "Diagnose Douyin account Liangtian, check partnership value" | Replace intuition with data for science-based evaluation |
| Managed creator monitoring | MCN operator | "Help me analyze our managed creators' Douyin accounts" | Spot problem accounts early, improve management efficiency |
| Self-account optimization | Douyin creator / operator | "Analyze my Douyin ID, see what needs improvement" | Identify optimization directions, boost account performance |

---
