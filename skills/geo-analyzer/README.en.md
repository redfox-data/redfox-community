# GEO Analyzer / geo-analyzer

---

## Overview

GEO Analyzer is a brand AI search visibility analysis tool. It automatically submits the same questions to three AI search engines — Doubao, Kimi, and DeepSeek — then detects brand mention rates, sentiment tendencies, source citations, and competitor comparisons, generating an interactive HTML report.

**Core Value**

- Enter a brand name and category to auto-generate test questions and batch-submit them across three AI platforms
- No manual testing needed — parallel polling runs in the background, results ready in 3-5 minutes
- Delivers a complete GEO score, mention rate matrix, sentiment distribution, and competitor comparison at a glance

**Who It's For**

- 📊 **Brand marketers** — Understand brand exposure and reputation in AI search, shape GEO optimization strategy
- 🎯 **Product managers** — Compare competitor performance in AI answers, uncover differentiation opportunities
- 📝 **Content operators** — Identify high-frequency citation sources, optimize content placement for better brand visibility

---

## Features

### Core Capabilities

- Auto-generates 5 category-relevant test questions (recommendation / comparison / evaluation / scenario), with support for custom questions
- Batch-submits N questions × 3 AI platforms with parallel polling, up to 8 minutes max wait
- Deterministic analysis: brand mention rate (cross-platform + per-platform), source domain aggregation, mention matrix heatmap
- AI deep analysis: brand ranking position, sentiment tendency (positive / neutral / negative), competitor comparison matrix
- GEO composite score (0-100): mention rate 40% + ranking 30% + sentiment 30% weighted calculation
- Interactive HTML report: anchor navigation, brand fingerprint, mention matrix, sentiment analysis, source analysis, competitor comparison, raw archive

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing a key, verify its source, scope, expiration, and whether it supports reset/revocation.
- Do not hardcode or expose the key in plain text within code, prompts, logs, or output files.

---

## Usage

Just describe what you need in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Prompt | Result |
|--------|---------------|--------|
| Analyze brand AI visibility | "Analyze how Genki Forest performs in AI search" | Auto-generates questions, batch-searches 3 platforms, delivers full GEO report |
| Custom question testing | "Test DJI's AI search performance with these 5 questions" | Uses your custom question list for batch search |
| Competitor comparison | "Compare NIO, Li Auto, and XPeng in AI search" | Delivers competitor matrix with per-platform mention rates and sentiment |

### Example Output

After analyzing "Genki Forest" in the sugar-free beverage category, you'll receive a report summary like:

> **Report Summary · Genki Forest**
>
> **Overall Assessment:** Genki Forest's cross-platform GEO composite score is **72**, mid-to-upper tier. Brand mention rate 80% (mentioned in 12/15 answers), positive rate 75%.
>
> **Platform Breakdown:**
> **Doubao**: GEO score 80 (Good), mention rate 100%, avg. rank #2.3
> **Kimi**: GEO score 68 (Good), mention rate 80%, avg. rank #3.1
> **DeepSeek**: GEO score 68 (Good), mention rate 60%, avg. rank #2.8
>
> **Action Items:** Prioritize improving DeepSeek mention rate (currently only 60%); address negative feedback with targeted pain-point solutions.

---

## Use Cases

| Scenario | Role | Example Prompt | Benefit |
|----------|------|---------------|---------|
| Brand diagnosis | Brand marketing lead | "Analyze our brand's AI search performance" | Full GEO score, per-platform mention rates, and sentiment distribution |
| Competitor benchmarking | Product manager | "Compare brand A vs. B and C in AI search visibility" | Competitor matrix revealing differentiation opportunities |
| Source strategy | Content operator | "Which websites do AI search engines cite for our category?" | TOP10 citation domains to guide content placement |
| Ongoing monitoring | Brand PR team | "Track our brand's GEO changes weekly" | Track GEO score trends, respond to reputation shifts promptly |
