# Xiaohongshu Viral Cover Designer / xiaohongshu-cover

---

## Overview

An AI cover design tool built for Xiaohongshu content creation. Based on **2000+** viral notes collected daily across the platform, it intelligently analyzes the visual patterns of viral covers in your niche and generates actionable cover designs that fit your content and platform aesthetics—boosting your note cover click-through rate.

**Core Value**

- **Real data-driven**: Grounded in 2000+ real viral notes daily, so cover designs are data-backed, not guesswork.
- **Fully automated**: From intent parsing to design generation, a 7-step standard workflow completes automatically, saving you tedious design work.
- **Three differentiated designs**: Each run delivers three distinct cover design concepts with image generation prompts, ready for production.
- **Platform-optimized**: All designs follow Xiaohongshu's 3:4 vertical cover spec (1080×1440 px), aligned with platform traffic aesthetics.

**Intended Users**

- 📝 **Xiaohongshu creators** — Stop struggling with cover design; use real viral data to boost click-through rates.
- 🛍️ **Brand / e-commerce operators** — Analyze niche visual patterns and generate brand-aligned seeding covers.
- 🏢 **MCN / content planners** — Batch-produce differentiated cover designs for multiple creators, avoiding homogenization.
- 🌱 **New creators** — Learn from low-follower high-engagement viral cases; produce professional covers from scratch.

---

## Features

### Core Capabilities

- **Smart intent parsing**: Automatically understands your creative needs, extracting content theme, type, style preference, and core keywords.
- **Viral data query**: Retrieves four-dimensional viral data: low-fan high-engagement, top-liked, single-day interaction spikes, and 7-day sustained growth.
- **AI image analysis**: Identifies text, scenes, color tones, and composition of each viral cover, then aggregates style patterns.
- **Custom design generation**: Combines your needs with viral style patterns to output three differentiated cover designs (with image generation prompts).

### Highlights

- **Data-driven**: Based on 2000+ real viral notes updated daily, so every design is grounded in evidence.
- **Fully automated**: From intent parsing to design generation, a one-click 7-step workflow completes in about 1–2 minutes.
- **Precision matching**: Smart scoring and filtering ensure recommendations are highly relevant to your needs.
- **Platform-optimized**: All designs follow Xiaohongshu's 3:4 vertical cover spec, perfectly aligned with platform aesthetics.

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

Simply describe your cover needs in natural language—no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
| ------ | -------------- | ------ |
| Design a note cover | "Help me design a fashion niche cover" | Analyzes fashion niche viral covers and generates three differentiated designs |
| Specify a sub-niche | "Design a cover for petite office outfits, Korean-style" | Precisely matches viral data by sub-niche and style preference |
| Custom time range | "Analyze beauty niche viral covers from the past 7 days" | Queries the latest viral trends within your specified time range |
| Combine with images | "[Upload image] Combine my photo with viral cover designs for a custom look" | Merges your image assets with viral cover styles for a personalized design |

### Output Example

After analysis, you will receive **three distinct cover design concepts**, each roughly containing:

**Design 1: High-Definition Product Close-Up**

📷 Visual core: A high-definition close-up centered on the product, paired with clean text labels
🖼️ Reference case: Shows a real viral cover example in this style (with title, author, engagement data)
🎨 Image prompt: Ready to use in AI image generation tools, already including the 3:4 vertical ratio requirement

---

(Three designs total, each with a different focus for easy comparison and selection.)

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| -------- | ---- | ---------------- | ------- |
| Creator cover design | Xiaohongshu fashion creator | "Design a cover for my weekly outfit roundup, Korean-style" | Skip the design grind; significantly improve cover click-through |
| Brand content marketing | Brand content operator | "Design a cover for our skincare seeding note, highlighting ingredient strengths" | Content better matches platform aesthetics; higher seeding conversion |
| MCN creator matrix ops | MCN operations manager | "Design covers for creators in beauty and fashion niches separately" | Batch-efficient output; differentiated content across the creator matrix |
| Cold-start account launch | New Xiaohongshu creator | "I just started a fashion account and don't know how to design covers" | Learn from low-follower high-engagement cases; produce professional covers from day one |

---

## Important Data Notes

- Data covers notes from yesterday to 30 days prior.
- Default query range is the past 30 days; you can specify a custom "past N days" range.
- Up to 5 keywords supported, with a combined maximum length of 200 characters.
- Some note links may not redirect directly due to Xiaohongshu risk-control policies; copy the title and search within the Xiaohongshu app instead.

---
