# Short Video Text Extractor / video-link-extract

---

## Overview

Just drop a video link and get every word spoken in it. Whether it's lines from a trending Douyin video, tutorial voiceovers from Xiaohongshu, or livestream scripts from Kuaishou—paste a link to receive the full transcript, complete with timestamps for every sentence.

**Core Value**

- **One link, full transcript**: Paste a video share link from Douyin, Kuaishou, or Xiaohongshu and get the complete transcript automatically—no downloading or transcription software needed.
- **Millisecond-level timestamps**: Each sentence is precisely timestamped, ready for subtitle creation and content remixing.
- **Smart progress tracking**: Submit and walk away—the system polls automatically and delivers results as soon as processing is done, no manual refreshing required.
- **Clear error feedback**: Invalid links, unsupported platforms, overly long videos—every issue is explained clearly with actionable suggestions.

**Intended Users**

- 📝 **Content remix creators** — Quickly extract transcripts from viral videos, break down scripting patterns, and boost remix efficiency.
- 📊 **Operations professionals** — Analyze competitor video scripts and build reusable content frameworks.
- ✂️ **Video editors** — Grab timestamped subtitle text in one click, skipping tedious manual transcription.

---

## Features

### Core Capabilities

- **Multi-platform support**: Automatically recognizes share links from Douyin, Kuaishou, and Xiaohongshu—one tool for all major short-video platforms.
- **Speech-to-text**: Intelligently transcribes video speech with stable output even in noisy environments or with regional accents, achieving over 95% accuracy.
- **Sentence-level timestamps**: Every sentence comes with precise start and end times for quick navigation to any moment in the video.
- **Automatic progress tracking**: No manual refresh needed after submission—the system polls automatically and returns results as soon as processing completes.
- **Batch processing**: Submit multiple links at once; each is processed sequentially with a summary of all results.

### Highlights

- **Zero-barrier operation**: Paste a link and get the transcript—no downloading or transcription software required.
- **Millisecond timestamps**: Each sentence precisely marked with start and end times, ready for subtitle production.
- **Automatic progress tracking**: Smart polling fetches results automatically once processing is done.
- **Complete error explanations**: Invalid links, unsupported platforms, and other issues are clearly explained with suggested fixes.

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

Simply describe your needs in natural language—no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|---------------|--------|
| Extract video text | "Extract the text from this Douyin video for me" | Paste the link and get the full transcript automatically |
| Get timestamped subtitles | "Extract the text from this video with timestamps" | Output each sentence with start/end times, ready for subtitling |
| Analyze video scripts | "Analyze what this viral video is saying" | Get the full transcript for script structure analysis |
| Batch extraction | "Extract text from all these video links" | Process multiple links sequentially, returning results one by one |

### Output Example

After submitting a link, you'll receive three parts:

**Full Transcript** — The video text segmented by meaning, displayed directly in the conversation.

> Hello everyone, today let's talk about how to create high-quality short videos. First, lighting is crucial. Natural light is your best source—try to shoot near a window...

**Video Summary** — A 1–3 sentence overview of the video's topic and core content, helping you quickly understand what it's about.

**Sentence Details** — Generated as a standalone file; click to view a complete table of every sentence with timestamps.

---

## Use Cases

| Scenario | Role | Example question | Benefit |
|----------|------|-----------------|---------|
| Viral breakdown | Content remix creator | "Extract the text from this viral video—I want to analyze its scripting" | Quickly get the full transcript and break down hooks and pacing sentence by sentence |
| Competitive script analysis | Operations / scriptwriter | "Extract the competitor's video text to see how they pitch selling points" | Build reusable content frameworks and improve your own scripts |
| Subtitle material extraction | Video editor | "Export this video's subtitles with timecodes for me" | Millisecond timestamps ready for editing software, no manual transcription |
| Batch content archiving | Content team | "Extract text from all these links" | Submit multiple links at once with batch output for easy organization and retrieval |

---
