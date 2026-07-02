# Xiaohongshu Note Analyzer / xhs-note-analyzer

---

## Overview

Query the full details of any Xiaohongshu note with one click, and get multi-dimensional in-depth analysis from a professional creator's perspective — helping you quickly understand the complete picture of a note and obtain actionable optimization suggestions.

**Core Value**

- **One-stop query**: Just provide a note ID or link to get the full details — title, body text, engagement data, author info, and more — no login or manual copying required.
- **Multi-dimensional analysis**: In-depth analysis covering viral factors, title SEO, tag quality, engagement insights, cover visuals, conversion potential, and more — not just looking at data, but understanding the logic behind it.
- **Efficient batch processing**: Query multiple notes at once to meet batch analysis needs such as competitor comparison and niche research.

**Intended Users**

- 📝 **Xiaohongshu creators** — Review your own content performance and get targeted optimization suggestions.
- 🛍️ **Brand / MCN operators** — Analyze competitor note strategies and support partnership decisions.
- 📊 **Content planners** — Batch-deconstruct viral patterns and build reusable content methodologies.

---

## Features

### Core Capabilities

- **Note detail query**: Retrieve title, body text, cover image, note type, engagement data (likes/favorites/comments/shares), author info, topic tags, and more.
- **Multi-dimensional note analysis**: From a professional creator's perspective — deep analysis across topic-pain point fit, viral factor breakdown, information structure, title SEO, tag quality, engagement insights, cover visuals, and conversion potential.
- **Cover image visual analysis**: Multi-dimensional analysis of cover image visual impact, composition and color tone, text overlay effects, and more.
- **Account positioning insight**: Combined with note content and account info, infer the account's positioning direction and assess how well the note aligns with the account's overall tone.
- **Batch query**: Provide multiple note IDs or links at once to query them in a single request; individual failures won't affect the rest.
- **Data credibility notice**: When engagement data is platform-estimated, a prominent notice is shown automatically to avoid misleading decisions.

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
| Analyze a single note | "Help me analyze this Xiaohongshu note" | Query full details and perform multi-dimensional analysis |
| Query by ID | "Query Xiaohongshu note 6a23eddb000000003502a39d" | Get note data and analysis directly by ID |
| Query by link | Paste a note sharing link | Auto-extract ID and query |
| Batch query | Provide multiple note IDs or links (comma-separated) | Query multiple notes one by one, returning results for each |

### Input Methods

- **Provide ID directly**: `6a23eddb000000003502a39d`
- **Provide link**: Supports standard note links and discovery links; ID is auto-extracted
- **Batch input**: Separate multiple IDs or links with commas

> Note: Short links (xhslink.com) are not supported yet. Please provide the full link.

---

## Use Cases

| Scenario | Role | Example question | Benefit |
|----------|------|-----------------|---------|
| Competitor note analysis | Brand ops | "Analyze how this competitor note is performing" | Understand competitor content strategy and engagement |
| Own content review | Xiaohongshu creator | "Help me review this note's performance" | Evaluate post effectiveness and identify optimization directions |
| KOL partnership assessment | MCN operator | "Analyze this creator's content quality" | Support partnership decisions and reduce selection risk |
| Viral pattern research | Content planner | "Batch analyze the viral factors of these top notes" | Build reusable content creation methodologies |

---
