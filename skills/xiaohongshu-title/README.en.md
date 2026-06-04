# XHS Title Suite / xiaohongshu-title

---

## Overview

Powered by daily-collected viral note data across the platform, this skill intelligently analyzes viral title patterns and generates 10 high-traffic attention-grabbing titles for you in one shot.

**Core Value**

- **Large-scale sample alignment**: Viral notes are collected continuously every day, giving your title creation a solid data foundation rather than fabricated examples or engagement numbers.
- **Analyze before write**: The skill completes a "viral title analysis" phase before outputting new titles, making the underlying patterns clear and easy to act on.
- **Batch delivery**: 10 titles in a unified format at once — each with a match score, reference link, and detailed rationale — making comparison and A/B testing straightforward.

**Who It's For**

- 📝 **Xiaohongshu creators** — Stop agonizing over titles; let data-driven patterns boost your click-through rate and reach.
- 🛍️ **Brand / e-commerce operators** — Quickly produce multiple title candidates based on product keywords and selling points.
- 🏢 **MCN / content strategists** — Batch-propose titles for the same track and build a reusable library of title frameworks.

---

## Features

### Core Capabilities

- **Keyword-driven**: Supports product keywords and topic keywords. When the input is a broad category, the skill recommends sub-directions for your confirmation before proceeding.
- **Smart time strategy**: If sample data is insufficient, the query window is automatically extended (from recent to further back) without replacing your core keyword.
- **Two-phase output**: First analyzes the structure, audience, and patterns of viral titles; then creates 10 new titles (not copies of the originals).
- **Standard delivery format**: Every title comes with a match score, a referenceable viral-note link, and detailed rationale — consistent layout for easy selection.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing your key, confirm its source, scope, expiry, and whether it supports reset/revocation.
- Never hard-code or expose the key in plain text within code, prompts, logs, or output files.

---

## Usage Guide

Just describe your product, topic, or creative need in plain language — no commands to memorize.

### Quick-Reference Phrases

| Intent                  | Example                                                                                            | What You Get                                                                |
| ----------------------- | -------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Title for a single item | "Write some viral Xiaohongshu titles for a sunscreen — key selling point: lightweight, non-greasy" | Aligns with viral samples by keyword, analyzes then outputs 10 candidates   |
| Regular track updates   | "Outfit track — want to post about fall/winter coats, give me a title set"                         | Extracts same-track patterns to iterate your title library                  |
| Broad category first    | "I want to do beauty content but haven't decided a direction yet"                                  | Recommends sub-directions for you to confirm before querying and generating |
| Riding trending topics  | "What titles are trending site-wide lately? Adapt a few for me"                                    | Applies hot patterns to your specific product and tone                      |

### Output Example

After analysis, you will receive **10 titles**. Each entry looks roughly like this (illustrative):

**Title 1: Style an oversized coat like this — even petite frames look tall**

📈 Match Score: 9.2
🔥 Reference viral note: [Original title excerpt](link) (Engagement: example)
👍 Rationale: Combines a numerical pain point with an outfit-result promise, matching the sentence structure common to high-engagement titles in this track.

---

(10 titles total, separated by dividers for easy copying and selection.)

---

## Use Cases

| Scenario              | Role                   | Example Request                                                                        | Benefit                                                                |
| --------------------- | ---------------------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| New product launch    | E-commerce / brand ops | "New product dropping — help me write XHS titles highlighting ingredients and effects" | Multiple publish-ready candidates fast, boosting click-through         |
| Ongoing account posts | Creator / content lead | "Skincare track, posting a serum review this week — give me 10 titles"                 | Sustain track viral patterns, reduce title and topic paralysis         |
| Testing a broad niche | New creator            | "Want to do beauty content but only know the broad category"                           | Narrow the direction first, then generate — lower trial-and-error cost |
| Trending remix        | Content operations     | "What titles are trending site-wide? Adapt a few I can post"                           | Translate hot patterns into your specific product and voice            |

---
