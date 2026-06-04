# Xiaohongshu Title Generator & Scorer / xiaohongshu-title-score

---

## Overview

Based on continuously collected viral note data from across the platform, we analyze viral title patterns and generate 10 quality viral titles in one click; meanwhile, we score existing titles across six weighted dimensions, delivering grade ratings and optimization suggestions.

**Core Value**

- **Generate + Score dual mode**: Create new titles based on viral patterns or evaluate existing titles' viral potential—two capabilities covering the full content creation workflow.
- **Data-driven creation**: Based on real-time viral data rather than guesswork, each title comes with a match score and a reference viral link—grounded in evidence.
- **Precision without drift**: Whatever product you input, samples are aligned strictly to that direction, without expanding into unrelated categories.

**Intended Users**

- 📝 **Xiaohongshu creators** — Stop agonizing over titles; use data-driven patterns to improve click-through and exposure.
- 🛍️ **Brand / e-commerce operators** — Quickly produce multiple title options from product keywords, and score to pick the best version.
- 🏢 **MCN / content planners** — Batch proposals and title optimization in the same niche, building reusable title formulas.

---

## Features

### Core Capabilities

- **Viral title generation**: Enter a keyword, analyze real-time viral patterns first, then create 10 new titles—each with a match score, reference link, and recommendation reason.
- **Viral title scoring**: Enter an existing title and keyword, score across six weighted dimensions (topic relevance, structural compliance, benefit clarity, emotional arousal, scarcity perception, compliance safety), output a grade (S / A / B / C) with optimization suggestions.
- **Keyword precision**: Whatever product you enter, only that product form is queried, with strict form boundaries (cream ≠ spray ≠ clothing); broad category keywords first recommend sub-niches for you to confirm.
- **Smart time strategy**: When samples are insufficient, the query time range is automatically expanded (recent 1 → 3 → 7 → 30 days), without changing your core keyword.

### Highlights

- **Product form precision**: Whatever product form you enter, it is strictly limited to that scope—no expansion into unrelated categories.
- **Six-dimension scoring system**: Topic relevance, structural compliance, benefit clarity, emotional arousal, scarcity perception, compliance safety—six dimensions fully quantify a title's viral potential.
- **Dual-function mode**: Generation and scoring in one tool—create new titles or evaluate existing ones, covering the full workflow from topic selection to publication.

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

Simply describe your product, title, or evaluation need in natural language—no fixed commands to memorize.

### Quick Reference

| Intent               | Example phrase                                                   | Result                                                          |
| -------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------- |
| Titles for a product | "Help me write a few Xiaohongshu viral titles for sunscreen"    | Align samples to keywords, analyze first, then deliver 10 options |
| Score an existing title | "Score 'This sunscreen is amazing,' keyword sunscreen"        | Six-dimension weighted score + grade + optimization suggestions   |
| Broad category first | "I want beauty titles but haven't picked a direction yet"       | Recommend sub-niches first; you confirm before continuing        |

### Output Example

**Title Generation**

After analysis, you receive **10** titles, each formatted as follows:

**Title 1: 7 days of fat-loss meals! Waistline really shrunk**

📈 Match score: 9.4
🔥 Reference viral: [Scrambled eggs with lettuce for a week, waistline shrunk!](link) (engagement: 6815)
👍 Why it works: Uses a "time + result" dual promise structure, precisely hitting the "lose weight without hunger" core pain point.

---

(10 titles total, separated by dividers for easy copy and selection.)

**Title Scoring**

## "This sunscreen is amazing" - Title Scoring Report

**Grade A** - **7.8/10**

| Dimension | Score | Weight | Weighted Score |
|-----------|-------|--------|----------------|
| Topic relevance | 8 | 15% | 1.20 |
| Structural compliance | 7 | 20% | 1.40 |
| Benefit clarity | 8 | 25% | 2.00 |
| Emotional arousal | 9 | 20% | 1.80 |
| Scarcity perception | 6 | 15% | 0.90 |
| Compliance safety | 10 | 5% | 0.50 |

---

## Use Cases

| Scenario             | Role               | Example question                                               | Benefit                                                      |
| -------------------- | ------------------ | -------------------------------------------------------------- | ------------------------------------------------------------ |
| New product titles   | E-commerce / brand | "New launch—write Xiaohongshu titles highlighting ingredients" | 10 publish-ready options quickly; higher click-through       |
| Title evaluation     | Creator / editor   | "Score 'This fat-loss meal is so tasty'"                       | Quantify viral potential; get targeted optimization tips     |
| Broad category trial | New creator        | "I want beauty content but only know the broad category"       | Sub-niche first, then generate—lower trial-and-error cost    |
| Hot-trend adaptation | Content ops        | "What titles are hot in the fat-loss niche? Help me adapt"     | Turn trending patterns into titles matching your content      |

---