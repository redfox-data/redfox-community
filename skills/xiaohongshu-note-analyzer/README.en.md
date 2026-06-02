# XHS Copywriting Score / xiaohongshu-note-analyzer

---

## Introduction

Powered by **2000+** viral notes collected daily across the platform, this skill scores your Xiaohongshu (XHS) copywriting across multiple dimensions, delivers concrete improvement suggestions, and helps you boost content quality and traffic performance.

**Core Value**

- **Real data foundation**: Every score is grounded in live viral notes retrieved on demand — not rule-of-thumb judgment — so every conclusion is traceable.
- **Four-dimension scoring**: Keyword coverage, structural completeness, timeliness, and content quality are scored individually, pinpointing weak spots at a glance.
- **Actionable improvement guidance**: Only the underperforming sections are rewritten; your original voice and style stay intact.

**Who It's For**

- 📝 **XHS Creators** — Run a quick quality check before publishing to reduce the chance of low traffic.
- 🛍️ **Brand / E-commerce Operators** — Measure how well promotional copy aligns with current viral patterns.
- 🏢 **MCN / Content Teams** — Review content at scale and establish a quantifiable copywriting quality standard.

---

## Features

### Core Capabilities

- **Keyword Coverage Analysis**: Compares your copy against high-frequency words in viral notes from the same niche to identify missing traffic keywords.
- **Structural Completeness Scoring**: Checks for key viral elements — opening hook, bulleted tips, and engagement call-to-action.
- **Timeliness Assessment**: Evaluates whether the copy connects to recent trends, seasons, or holidays to enhance contextual relevance.
- **Content Quality Evaluation**: Measures readability through tip density, layout clarity, and emoji usage.
- **Precision Optimization**: Upon confirmation, only low-scoring sections are revised — high-scoring parts remain untouched to avoid full rewrites.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?souce=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before supplying a key, confirm its source, permitted scope, expiry, and whether it can be reset or revoked.
- Never hard-code or expose the key in plain text within code, prompts, logs, or output files.

---

## Usage Guide

Just paste your XHS copy directly — no commands to memorize.

### Quick Reference

| Intent                 | Example Phrase                        | Result                                                                      |
| ---------------------- | ------------------------------------- | --------------------------------------------------------------------------- |
| Evaluate copy quality  | "Check how well this copy is written" | Four-dimension score with a detailed breakdown                              |
| Find specific problems | "What's wrong with this copy?"        | Identifies low-scoring dimensions with actionable fixes                     |
| Gauge viral potential  | "Can this copy go viral?"             | Compares against same-niche viral patterns for an objective rating          |
| Paste copy directly    | Paste the body text                   | Auto-detects topic, extracts keywords, and starts scoring                   |
| Request optimization   | "Help me improve it"                  | Outputs a rewrite guide + an improved version that keeps your original tone |

### Output Example

After scoring, you will receive a report structured as follows:

**Score**: Total XX/100 with a rating (Excellent / Good / Average / Needs Work)

**Dimension Breakdown**: Individual scores and explanations for keyword coverage, structural completeness, timeliness, and content quality

**Improvement Suggestions**: Specific, actionable advice for underperforming dimensions (provided when rating is below Excellent)

**Viral Formula Reference**: A pattern distilled from real data, e.g. "Pain-point opener + bullet tips + engagement close"

**Reference Viral Notes**: 2–3 real viral notes used in this analysis, with engagement metrics and links

---

## Use Cases

| Scenario                      | Role               | Example Request                                          | Benefit                                                    |
| ----------------------------- | ------------------ | -------------------------------------------------------- | ---------------------------------------------------------- |
| Pre-publish check             | Creator / Blogger  | "Check this restaurant review copy before I post it"     | Catch weaknesses before going live                         |
| Find improvement direction    | Operator / Editor  | "What's wrong with this copy and how do I fix it?"       | Pinpoint issues with concrete, actionable fixes            |
| Benchmark against viral notes | New creator        | "Where does my copy fall short compared to viral posts?" | Understand the gap and build a viral copywriting intuition |
| Batch quality review          | MCN / Content team | Submit copies one by one for review                      | Standardize quality benchmarks and improve team output     |
