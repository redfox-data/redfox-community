# AI Video Prompt Expert / video-prompt-expert

---

## Overview

Write AI video prompts with a director's mindset and generate MP4 videos instantly. Turn vague visual descriptions into precise, executable cinematography instructions that AI can faithfully render, covering 8 common scenarios from nature landscapes to sci-fi epics, with one-click API video generation.

**Core Value**

- **Prompts as cinematography instructions**: Every word is executable—no more "very sci-fi" or "moody feeling" ambiguity, AI accurately reproduces your vision
- **Write + shoot in one flow**: Call the video generation API right after finishing your prompt, auto-polling and downloading 4-15s 1080p videos without switching tools
- **Diagnosable issues**: 20+ common problems like face swapping, chaotic camera movement, and poor image quality come with concrete fix suggestions

**Intended Users**

- 🎬 **Short-form video creators** — Improve AI video quality with professional prompts, reduce trial-and-error
- 📱 **Content creators / operators** — Quickly produce multi-scenario video assets, boost content output efficiency
- 🎨 **Creative professionals** — Transform abstract ideas into precise, executable video generation instructions

---

## Features

### Core Capabilities

- **Structured prompt building**: Build prompts layer by layer—technical parameters, spatial composition, lighting design, and motion choreography—to ensure completeness and professionalism
- **@ multi-modal reference syntax**: Support first-frame locking, style reference, camera movement reference, audio sync, and subject locking with explicit material usage declarations
- **Golden formula validation**: Automatically check whether the five elements—subject + action + scene + style + mood—are complete
- **Effect diagnosis and repair**: Provide specific fix operations for common issues like character inconsistency, chaotic camera movement, and stiff motion
- **8 scenario templates**: Nature landscapes, city nightscapes, character close-ups, product showcases, pet healing, sci-fi epics, food close-ups, and animation style
- **One-click video generation**: Generate MP4 videos directly via Seedance 2.0 API after writing prompts, supporting multiple aspect ratios and resolutions

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

Simply describe the video you want in natural language, and the skill will transform it into a professional-grade prompt and generate the video directly.

### Quick Reference

| Intent | Example phrase | Result |
|--------|---------------|--------|
| New prompt | "Write me a cyberpunk city night video prompt" | Build a complete prompt layer by layer with professional methodology |
| Effect diagnosis | "The characters keep face-swapping in my video, how to fix" | Diagnose the issue and provide a concrete fix |
| Use template | "Give me a product showcase prompt template" | Output a ready-to-use template for the matching scenario |
| Generate video | "Generate a video with this prompt, 16:9, 8 seconds, 1080p" | Call the API to produce and download the video directly |

### Output Example

After prompt creation, you receive a structured professional prompt, roughly like this (illustrative):

```
16:9 widescreen, 24fps, ARRI Alexa quality, slight vignette, high contrast.
Foreground: wet asphalt reflecting neon, occupying bottom 25%. Midground: black sedan. Background: high-rise neon stretching into vanishing point.
Multi-color neon sources, pink left and cyan right, wet road mirror reflection, deep navy sky.
Camera fixed, sedan enters from left at constant speed and exits right, 8 seconds, taillights trailing red light streaks.
Cyberpunk color palette, no text, no watermarks.
```

It can be used directly for video generation or fine-tuned before generating.

---

## Use Cases

| Scenario | Role | Example question | Benefit |
|----------|------|-----------------|---------|
| Short-form video | Creator / editor | "Write me a cinematic sunset beach video prompt" | Professional prompt, high-quality video in one generation |
| Product ads | E-commerce / brand | "Product rotation showcase video prompt, premium feel" | Fast product video assets, lower production cost |
| Batch content | Content ops / MCN | "Give me a set of city night and food prompt templates" | Reuse templates for batch generation, boost output efficiency |
| Issue troubleshooting | All users | "Characters keep deforming in my video, how to fix" | Precise diagnosis with actionable fix steps |

---
