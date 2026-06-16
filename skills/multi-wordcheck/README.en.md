# Multi-Platform Prohibited Words Checker / multi-wordcheck

---

## Overview

A multi-platform prohibited words detection tool powered by official compliance word banks, covering the review standards of WeChat Official Accounts, Xiaohongshu (RED), and Douyin (TikTok). Supports text, file, image, and URL inputs, delivering fast flagged-word marking and context-aware replacement suggestions.

**Core Value**

- Quickly locate prohibited words in your copy before publishing to reduce the risk of content restriction, rejection, or takedown
- Get context-aware replacement suggestions instead of mechanical keyword swaps
- Receive a ready-to-publish revised version — copy and use instantly

**Who It's For**

- ✍️ Content Creators — Run quick self-checks before cross-platform publishing to lower compliance risks
- 📊 Brand Operators — Batch-scan marketing materials to maintain consistent compliance standards
- 🏢 MCN Agencies — Provide standardized content review workflows for all managed accounts
- 🔍 Content Review Teams — Augment manual review with automated screening to boost efficiency

---

## Features

### Core Capabilities

- **Flagged Word Marking**: Prohibited words in the original text are highlighted in bold for instant visibility
- **Context-Aware Replacements**: Each flagged word comes with a contextually appropriate alternative and the rationale behind the swap
- **Optimized Copy Output**: Automatically generates a revised, publishable version
- **Long-Text Batch Detection**: Automatically prompts batching for content exceeding 3,000 characters, with support for sequential batch detection and merged results
- **Multi-Platform Coverage**: Supports independent word banks for WeChat Official Accounts, Xiaohongshu, and Douyin, each tailored to the platform's review rules
- **Multi-Format Input**: Accepts pasted text, uploaded .txt files, uploaded images (text extraction), and pasted webpage URLs (body content scraping)

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?souce=github) to register an account and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing a key, verify its source, scope of use, expiration date, and whether it supports resetting or revocation.
- Never hardcode or expose keys in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Phrase | Outcome |
| ------ | -------------- | ------- |
| WeChat article check | Help me check this WeChat article for prohibited words: This product uses all-natural ingredients | Detects against WeChat rules and outputs flagged words with replacement suggestions |
| Xiaohongshu note check | Xiaohongshu, check this copy: This whitening miracle works in 3 days, money-back guarantee | Detects against Xiaohongshu rules and outputs flagged words with replacement suggestions |
| File upload check | Upload a .txt file or image and specify the target platform | Automatically extracts content and checks against the specified platform rules |
| Webpage URL check | Paste a webpage URL and the system will scrape and check the body text | Automatically scrapes page content and checks against the specified platform rules |
| Long-text batch check | System prompts automatically above 3,000 chars; reply 1 for first 3,000 chars / 2 for auto-batching | Splits at natural breakpoints, checks batch by batch, then merges results |

### Output Example

When prohibited words are detected, the output includes three sections:

🔍 **Detection Results** — Shows the platform, count and type of flagged words, with prohibited words highlighted in bold in the original text

💡 **Replacement Suggestions** — A table mapping each flagged word to its replacement and the rationale

📝 **Optimized Copy** — The revised, publishable version with replacements marked in bold italics

When no prohibited words are detected, only "No prohibited words found — content is compliant" is shown.

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Pre-publish WeChat article review | Content operator | Check this article for prohibited words | Screen for advertising law violations, false claims, and high-risk medical/pharma terms to reduce rejection or restriction |
| Xiaohongshu note compliance check | Creator | Check this Xiaohongshu note for prohibited words | Eliminate superlatives, banned claims, and community-prohibited phrasing; replacements tailored for recommendation-style content |
| Douyin short-video script screening | Scriptwriter | Check this Douyin voiceover script for prohibited words | Screen for sensitive terms and non-compliant expressions to ensure the final cut passes platform review |
| Bulk brand marketing material scan | Brand / e-commerce operator | Check all landing page URLs for prohibited words | Complete multi-page compliance screening in bulk with unified-format reports |
