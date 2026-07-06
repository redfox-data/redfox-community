# WeChat Investment Blogger Distiller / investor-distiller

---

## Overview

Enter a WeChat public account ID and it automatically pulls articles and distills a seven-dimensional DNA style profile — from trading systems to expression style, you get a complete analysis of the blogger. Unlike generic summaries, every conclusion is backed by original text evidence, and the profile's accuracy is automatically scored and validated, so you know exactly how reliable it is.

**Core Value**

- **Plug and Analyze**: Enter a WeChat ID to automatically pull articles and generate a complete profile, with three tiers (20/60/100) — no manual browsing required
- **Seven-Dimensional DNA**: Trading systems, stock selection logic, expression style, interaction patterns… dissect the blogger's investment DNA across seven dimensions, not just word frequency stats
- **Auto-Validated Accuracy**: Automatic three-dimensional scoring after each distillation, checking stocks/style/system item by item — you can see at a glance how accurate it is
- **Ready to Use**: Generate style-consistent stock analysis based on the profile, ready to use as reference material, each with data source annotations and disclaimers

**Target Users**

- 🧑‍💼 Investors — Quickly understand an influencer's investment style and core logic to support decision-making
- ✍️ Content Creators — Learn from influencers' expression styles and argumentation patterns to improve content quality
- 🔬 Researchers — Systematically analyze investment blogger style characteristics, supporting multi-blogger comparisons

---

## Features

### Core Capabilities

- **Plug and Analyze**: Enter a WeChat ID to automatically pull articles and generate a complete profile, with flexible 20/60/100 article tiers
- **Seven-Dimensional DNA**: From trading systems to persona DNA, dissect the blogger's investment DNA across seven dimensions — not just word frequency stats
- **Auto-Validated Quality**: Automatic scoring after each distillation, checking stocks/style/system item by item, with prompts for supplementary distillation when accuracy falls short
- **Ready to Use**: Generate style-consistent stock analysis based on the profile, ready to use as reference, each with data source annotations

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?source=github) to register an account and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, please verify the key source, available scope, validity period, and whether reset/revocation is supported.
- Never hardcode or expose your key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example | Result |
| ------ | ------- | ------ |
| Distill a blogger profile | `Distill the WeChat account zshbtz` | Automatically collects articles and generates a 7D DNA style profile |
| Specify article count | `Distill zshbtz with 100 articles` | High-precision distillation for more stable profile characteristics |
| Validate profile quality | `Validate the distilled profile for 财躺平` | Three-dimensional scoring to confirm profile accuracy |
| Style-based analysis | `Analyze CATL using 猫笔刀's style` | Generate style-consistent stock analysis based on the distilled profile |

### Output Example

After distillation, the following files are generated in the `output/` directory:

- `{blogger_name}_风格画像.md` — Complete 7D DNA style profile with original text evidence and confidence annotations
- `{blogger_name}_统计数据.json` — Structured statistical data for validation and comparison
- `{blogger_name}_校验报告_YYYYMMDD.json` — Accuracy validation report with three-dimensional scoring

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Understanding an influencer | Investor | `Distill the WeChat account 猫笔刀` | Quickly grasp the blogger's trading system and market perspective |
| Multi-blogger comparison | Researcher | `Distill 财躺平 and 投资明见, compare their styles` | Cross-reference different bloggers' investment approaches and expression styles |
| Style-based market review | Content Creator | `Write today's A-share recap in 格兰投研's style` | Generate style-consistent market commentary |
| Stock selection support | Investor | `Analyze the new energy sector from 猫笔刀's perspective` | Evaluate stocks/sectors through the blogger's analytical framework |
