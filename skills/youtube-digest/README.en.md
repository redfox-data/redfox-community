# YouTube Transcript Extractor / youtube-digest

---

## Overview

Paste a YouTube video link or ID to instantly extract the transcript. Non-Chinese subtitles are automatically translated into Chinese. Results are displayed in a terminal table, saved as Markdown, and exportable to Excel.

**Core Value**

- **One-click extraction**: Drop a link and get the full transcript — no manual copying needed.
- **Auto-translation**: English or other language subtitles are automatically translated into Chinese — no extra steps required.
- **Multiple output formats**: Terminal table for quick preview, Markdown for archiving, Excel for sharing — three delivery options to choose from.

**Intended Users**

- 📝 **Content creators** — Extract competitors' video transcripts to analyze their scripts and topic strategies.
- 🎓 **Learners / researchers** — Turn tutorials, speeches, and podcasts into searchable text notes.
- 📊 **Operations / marketing teams** — Batch-extract competitor video content for rapid research and repurposing.

---

## Features

### Core Capabilities

- **Three input formats**: Full URL, `youtu.be` short link, or raw video ID — auto-detected, any format works.
- **Chinese track priority**: Prefers Chinese subtitle tracks; if unavailable, falls back to English and auto-translates to Chinese.
- **Auto-translation**: Non-Chinese subtitles are automatically translated into Chinese (powered by Google Translate, batch-merged for efficiency); add `--no-translate` to keep the original text.
- **Clean text by default**: No timestamps — just readable full text ready for AI processing; switch to timestamped version anytime with `--timestamp`.
- **Excel export**: `--excel` one-click exports xlsx (title / duration / video link / transcript), with auto-wrapping and column-width fitting.
- **Table-based delivery**: Title / duration / transcript in a clean three-column table — all info at a glance.
- **Robust retry**: Auto-incrementing delay retry on network errors or empty data; rate-limited requests auto-wait and retry.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe what you need in natural language — no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|----------------|--------|
| Extract transcript | "Extract the transcript from this video" + link | Auto-extract and translate to Chinese, displayed in a table |
| Extract with timestamps | "Give me the timestamped version" | Output `[MM:SS]` timestamps + transcript for easy video navigation |
| Export to Excel | "Export to Excel" | Generate xlsx file (title / duration / link / transcript) |
| Keep original text | "Keep the English original, no translation" | Add `--no-translate`, output subtitle original text |
| Specify language | "I only want English subtitles" | Select track by specified language priority |

### Output Example

After extraction, you'll see a table like this:

| Title | Duration | Transcript |
|-------|----------|------------|
| Rick Astley - Never Gonna Give You Up (Official Video) (4K Remaster) | 03:31 | We're no strangers to love / You know the rules and so do I / …… (full Chinese translation) |

---

## Use Cases

| Scenario | Role | Example question | Benefit |
|----------|------|------------------|---------|
| Video-to-text | Content creator | "Turn this YouTube link into a transcript" | Get a complete Chinese transcript in one step, no manual work |
| Study notes | Learner | "Extract this speech transcript and summarize it" | Quickly get searchable, editable text notes |
| Content repurposing | Operations | "Extract the English video transcript and rewrite it for my blog" | End-to-end flow from extraction to translation to rewriting |
| Competitive analysis | Marketing team | "Batch-extract transcripts from these competitor videos" | Rapidly analyze script structure and content strategy |

---
