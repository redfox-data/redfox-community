# XHS Viral Title Scorer / xhs-title-scorer

---

## Introduction

Scores your Xiaohongshu (XHS) title across 6 weighted dimensions using real viral post data, and provides actionable revision suggestions to help you assess traffic potential before publishing.

**Core Value**

- Scoring is grounded in real viral data — every result is traceable, not based on gut feeling
- 6-dimension breakdown pinpoints the exact weaknesses affecting traffic
- Multi-style revision versions are ready to use, no extra brainstorming needed

**Who It's For**

- 📝 **XHS Creators** — Validate titles before publishing to reduce low-traffic posts
- 🛍️ **Brand / E-commerce Teams** — Filter out weak titles before A/B testing
- 🏢 **MCN / Content Planners** — Batch-evaluate titles and improve content efficiency

---

## Features

### Core Capabilities

- **Viral-data-driven scoring**: Extracts structure, wording, and emotional patterns from real recent viral posts in the same niche, then scores your title against those benchmarks
- **6-dimension weighted scoring**: Topic relevance, structural compliance, benefit clarity, emotional appeal, perceived scarcity, and compliance safety — combined into a 10-point weighted score
- **Grade classification**: S / A / B / C grades, each mapped to a different optimization strategy
- **Viral overlap detection**: If your title closely matches an existing viral title, it is flagged and awarded an S grade automatically
- **Multi-style revision suggestions**: A/B/C-grade results include a list of core issues, 3–5 reference viral titles, and 2–3 revised versions (informational / emotional / curiosity-driven)

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` as a device environment variable before using this skill.
- Before providing your key, verify its source, permitted scope, expiry, and whether it supports reset/revocation.
- Never hardcode or expose the key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Just describe your title and topic in plain language — no commands to memorize.

### Quick Reference

| Intent                  | Example                                                                        | Result                                                                         |
| ----------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| Score a single title    | "Score this title: 'This sunscreen is absolutely amazing', keyword: sunscreen" | Fetches sunscreen viral data, outputs 6-dimension score report and suggestions |
| Title only, no keyword  | "'Skincare tips every beginner must know' — how's this title?"                 | Automatically extracts keywords from the title and scores it                   |
| Specify topic direction | "Score 'Dressing like this in summer is so cute', topic: summer outfits"       | Scores against viral benchmarks in the summer fashion niche                    |

### Output Example

After scoring, you will receive:

**Score Report** (S / A / B / C grade + overall score + 6-dimension breakdown table)

**Optimization Suggestions** (for A/B/C grades):

- Core issues list
- 3–5 reference viral titles in the same niche (with author and engagement count)
- 2–3 revised versions (informational / emotional / curiosity-driven)

---

## Use Cases

| Scenario                   | Role             | Example                                                     | Benefit                                                                     |
| -------------------------- | ---------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------- |
| Pre-publish check          | Creator          | "Is this title good enough? Give it a score."               | Catch weaknesses early and avoid wasting distribution on low-traffic titles |
| Comparing multiple titles  | Content operator | "Score these two titles and tell me which is better."       | Use data to pick the stronger version instead of guessing                   |
| Getting revision direction | New creator      | "My title scored low — can you rewrite a few versions?"     | Receive ready-to-publish alternatives and lower the creative barrier        |
| Learning niche patterns    | MCN planner      | "While scoring, explain the viral structure in this niche." | Build niche pattern knowledge as a byproduct of the scoring process         |
