# WeChat Official Account Copywriting / wechat-write

---

## Overview

Powered by the RedFox data Official Account viral radar, search for trending viral articles by keyword, extract traffic insights and key writing principles, and generate a complete, publish-ready article.

**Core Value**

- **Data-driven creation**: Viral articles from WeChat Official Accounts are continuously collected daily, so copywriting patterns are grounded in real data—not invented examples.
- **Analyze first, then write**: Complete viral pattern analysis before generating the full article, with clear patterns that are easy to understand and apply.
- **Style adaptation**: Upload personal writing samples for style analysis—vocabulary habits, tone, and expression—so the generated copy matches your voice.

**Intended Users**

- ✍️ **Official account owners** — Use viral data patterns to guide creation; say goodbye to creative blocks and inefficient trial-and-error.
- 📊 **Content operators** — Quickly search for viral articles by keyword, analyze traffic patterns, and produce high-engagement articles.
- 🏢 **MCN / brand planners** — Batch-collect viral samples in the same niche and build reusable writing formulas.

---

## Features

### Core Capabilities

- **Keyword-based viral search**: Enter product or topic keywords to search for related viral articles; supports multi-keyword combinations (up to 5).
- **Viral pattern analysis**: Breaks down viral patterns across dimensions including title structure, opening hooks, content style, engagement prompts, and high-frequency keywords.
- **Differentiation analysis**: When recommending a specific entity, automatically analyzes input, process, output, and positioning differences to anchor the copy.
- **Complete article generation**: Produces a ~1500-word, publish-ready article based on viral patterns, including recommended titles, core viewpoint, and tags.
- **Personal style integration**: Upload your everyday writing samples; the tool analyzes your style and blends it into the generated copy.

### Highlights

- **Dual-mode coverage**: Direct creation for general topics; automatic differentiation analysis for specific entity recommendations, ensuring content has clear anchors.
- **Smart time strategy**: Queries the last 7 days by default; automatically expands to 30 days when samples are insufficient, without changing your keywords.

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

Simply describe your creative need in natural language—no fixed commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|---------------|--------|
| Write an article | "Help me write a WeChat article about career changes" | Search virals by keyword, analyze patterns, then generate a complete article |
| Recommend a product | "Help me write a WeChat article recommending an AI tool" | Automatically break down differentiation advantages and generate copy around product highlights |
| Find viral articles | "What articles are trending on WeChat? Career direction" | Return a list of trending viral articles in the niche with pattern analysis |
| Blend personal style | "Here are some of my daily writings, write in this style" | Analyze your writing style and integrate it into the generated copy |

### Output Example

After analysis, you receive a complete, publish-ready article, roughly like this (illustrative):

**Recommended Titles**
1. 5 truths about career changes—no one tells you the third one
2. You don't want to change jobs—you just want to be seen

**Article Content**
[Complete publish-ready article, ~1500 words]

**Core viewpoint**: Changing jobs isn't running away—it's repricing your professional value

**Recommended Tags**
#Career #JobChange #CareerDevelopment #SalaryIncrease #Resignation

**Viral Formula Sources**
- **Title patterns**: Number-based titles are most common; questions spark curiosity
- **Opening patterns**: Personal experience openings build resonance
- **High-frequency keywords**: Job change (8), Career (6), Salary increase (4)

---

## Use Cases

| Scenario | Role | Example question | Benefit |
|----------|------|-----------------|---------|
| Daily creation | Official account owner | "Help me write a WeChat article about personal finance" | Viral patterns guide creation, boosting article engagement |
| Product recommendation | Brand / self-media | "Help me write a WeChat article recommending Tool X" | Automatic differentiation analysis; copy anchored on product highlights |
| Viral pattern research | Content operator | "Analyze recent viral article patterns in the emotional niche" | Multi-dimensional pattern breakdown across titles, openings, structure |
| Styled writing | Individual account owner | "Write a career advice piece in my usual style" | Personal style blended in for more distinctive content |

---

## Important Data Notes

- Viral article data is continuously collected and updated daily.
- Queries default to the last 7 days; automatically expands to 30 days when samples are insufficient.
- Maximum query range is the last 30 days.
