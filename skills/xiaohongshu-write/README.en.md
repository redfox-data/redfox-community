# Xiaohongshu Write

---

## Overview

A one-stop note generation tool purpose-built for Xiaohongshu content creation. Powered by 2,000+ viral notes collected daily across the platform, simply enter a keyword to precisely search the hottest trending notes. Through AI-powered deep analysis of viral content structures, opening hooks, information density, and engagement tactics, the tool distills core traffic-driving formulas — generating polished, platform-compliant, and ready-to-publish notes that fit Xiaohongshu's content ecosystem.

**Core Value**

- Data-driven: Built on massive real viral data across the platform — no guesswork
- Pattern extraction: Automatically analyzes title patterns, content structures, engagement hooks, and hashtag strategies from high-performing notes
- Publish-ready: Generated copy fits platform style, copy and post directly
- Style fusion: Supports incorporating your personal writing style to keep your content unique

**Who It's For**

- 🧑‍💻 Content Creators — Generate high-quality notes fast with lower creation barriers
- 📈 Brand Operators — Batch produce platform-aligned promotional copy
- 🔍 New Influencers — Learn viral patterns and find your creative direction

---

## Features

### Core Capabilities

- **Viral Note Search**: Search Xiaohongshu's trending notes by keyword and retrieve complete data including titles, engagement metrics, and author info
- **Deep Viral Pattern Analysis**: Automatically extract title patterns, content structures, emotional hooks, and hashtag strategies from high-engagement notes
- **AI Copy Generation**: Generate complete, platform-aligned, publish-ready note copy based on analysis results
- **Personal Style Fusion**: Upload your previous note content to analyze your writing habits and blend them into generated copy

### Highlights

- **2,000+ Daily Data Pool**: Continuously collected viral notes daily, covering the latest trends
- **All-in-One Workflow**: Search, analyze, and generate — all in one request, no tool switching
- **Quantified Pattern Output**: Not just copy — get the viral formula and reference note sources behind the results
- **Real-time Trend Integration**: Automatically searches latest news to incorporate into copy for timeliness and topicality

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?souce=github) to register an account and obtain your `REDFOX_API_KEY`.
- Set the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, verify its source, available scope, validity period, and whether reset/revocation is supported.
- Never hardcode or expose your API key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent                  | Example Prompt                                             | Result                                        |
| ----------------------- | ---------------------------------------------------------- | --------------------------------------------- |
| Write a note            | "Help me write a Xiaohongshu note about healthy meal prep" | Generates complete copy directly              |
| Analyze viral patterns  | "Help me analyze viral patterns for 'office outfits'"      | Outputs viral pattern analysis                |
| Find trending notes     | "Find me trending 'skincare' notes recently"               | Retrieves relevant popular content            |
| Broad topic suggestions | "Help me write a note about fashion styling"               | Recommends 10 niche sub-topics to choose from |

### Output Example

After entering "Help me write a Xiaohongshu note about healthy meal prep," you'll receive:

```
### Recommended Titles
1. 3-Day Meal Prep Plan | The Secret to Losing Weight While Eating Well
2. One Week Meal Prep Collection! Tear-Jerkingly Delicious Weight-Loss Magic
3. 5 Things You Must Eat During a Diet — The Last One is a Game Changer

### Body Content
[Complete publish-ready copy infused with viral patterns]

### Recommended Tags
#HealthyMealPrep #WeightLossRecipes #LowCalorieFood #...

### Viral Formula Source
**Referenced Viral Formula**: Number-driven titles + pain-point hook + bullet-point value + engagement closing

**Referenced Viral Notes** (listing 2-3 core reference notes with links and engagement data)
```

---

## Use Cases

| Scenario                            | Role                 | Example Prompt                                            | Benefit                                                      |
| ----------------------------------- | -------------------- | --------------------------------------------------------- | ------------------------------------------------------------ |
| Daily topic creation                | Individual blogger   | "Write a Xiaohongshu note about commute outfits"          | Rapid output based on viral patterns, reduces topic pressure |
| Viral pattern research              | Content operator     | "Analyze viral patterns in the 'skincare' category"       | Master traffic-driving tactics and optimize content strategy |
| Multi-platform content distribution | Matrix account owner | "Write a note about mom-and-baby product recommendations" | Fast batch production, boosts publishing efficiency          |
| Beginner learning                   | New influencer       | "Find trending 'food review' notes recently"              | Learn viral patterns and accelerate creative growth          |

---

## Important Data Notes

- The database only contains data from yesterday up to 30 days ago; real-time same-day content is not included
- Default query covers the most recent 7 days of viral content
- When data is insufficient, the time range automatically expands: 1 day → 3 days → 7 days → 30 days
- When the search keyword is a broad category (e.g., "fashion," "food"), 10 niche sub-topics will be suggested first for you to choose from
