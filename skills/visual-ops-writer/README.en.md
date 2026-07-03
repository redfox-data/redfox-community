# Visual Ops Writer / visual-ops-writer

---

## Overview

A full-pipeline operations article tool covering everything from topic selection, writing, and illustration to quality checks. **Rewrite** any article by learning its style, **generate** promotional long-form content for a Skill, or **auto-illustrate** existing text — all with images included and ready to publish.

**Core Value**

- **Three scenarios, one tool**: Link rewriting, product promotion, and article illustration — the three highest-frequency content creation scenarios, all covered.
- **Text + image delivery**: Articles and images are generated together and saved as a complete, ready-to-use file — not a half-finished draft.
- **Built-in quality**: Every article goes through 9 quality checks automatically, with a report included — ready to publish.

**Intended Users**

- 📝 **Content operators** — Produce style-matched articles and promotional content from writing to illustration, all in one go.
- 🛍️ **Brand / skill developers** — Auto-generate promotional long-form articles aligned with actual product capabilities.
- 🏢 **Bloggers / editors** — Smart image placement for existing articles, no manual planning needed.

---

## Features

### Core Capabilities

- **Link rewrite**: Provide any article link to automatically fetch its content and images, learn the style and structure, then produce a new article from a different angle with equivalent quality. Image styles match the originals — ideal for competitive analysis and content benchmarking.
- **Skill promo**: Provide a Skill file path or name to auto-parse product capabilities and fetch the latest info from the target site, generating a promotional long-form article aligned with actual product features. Images use the RedFox illustrator style for visual and content consistency.
- **Add images**: Provide complete article text to automatically analyze structure by section semantics and word density, intelligently determine image placement and count, then batch-generate consistent illustrations. Perfect for when you've finished writing but don't want to manually find images.
- **Automated quality check**: Every article goes through 9 quality checks after generation (title length, section count, table count, word count, FAQ count, prohibited words, paragraph length, information density, etc.) with a JSON report output.

### Writing Capabilities

- **Auto article type matching**: Three templates — tool promotion, methodology, and crisis response — automatically selected based on topic
- **Reader persona adaptation**: Supports individual creators and team/enterprise reader profiles with automatic expression adjustment
- **Tone options**: Direct & candid / Professional & rigorous / Casual & conversational — three tones to choose from
- **Word count control**: Customizable word count range (default 2000-3000 words), or adaptive to original article length

### Illustration Capabilities

- **Style transfer**: In link rewrite mode, original images serve as visual references; new content is generated with consistent style
- **Semantic matching**: Images automatically match illustrator poses to section content (welcoming, analyzing, thinking, operating)
- **Smart sectioning**: Auto-determines image placement by H2 sections + word density, skipping positions unsuitable for images
- **Adjustable count**: 0-5 image limit, or fully auto-decided by the system

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`)
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|---------------|--------|
| Link rewrite | "Rewrite this article in my product's voice, keep the style" | Learn the original style and structure, generate a new article with matching images |
| Skill promo | "Write a promotional article for this Skill" | Auto-generate a capability-aligned promotional long-form article with images |
| Add images | "Add images to this article" | Smart analysis of article structure, auto-determine image placement and generate |
| Competitive analysis | "Analyze this article's approach, write one from a different angle" | Learn the structure and style of great content, produce differentiated output |

### Output

After generation, you receive:

1. **Complete article**: Saved as `article.md` with title, body text, and images (embedded in corresponding sections)
2. **Quality report**: `validation_report.json` with 9 quality check results
3. **Full text in chat**: Article displayed directly in the conversation
4. **Feedback node**: Adjust any section or image by specifying the direction

---

## Use Cases

| Scenario | Role | Example question | Benefit |
|----------|------|-----------------|----------|
| Style-matched rewrite | Content operator | "Rewrite this article, keep the style but switch to my product" | Quickly produce high-quality articles with consistent style, skip the blank-page phase |
| Skill promotion | Skill developer | "Write a promotional article for this Skill" | Auto-generate capability-aligned promotional content — words match features |
| Article illustration | Blogger / editor | "Add images to this article" | Smart image placement without manual planning |
| Competitive analysis | Brand operator | "Analyze this article's approach, write one from a different angle" | Learn great content structure and style, produce differentiated output |

---
