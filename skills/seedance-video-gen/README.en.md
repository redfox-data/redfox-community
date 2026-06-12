# Seedance2.0 / seedance-video-gen

---

## Overview

AI video generator based on ByteDance Volcano Engine Seedance 2.0 model. One command to generate MP4 videos. Built-in public API key, ready to use.

**Core Value**

- **Text-to-Video**: Input Chinese or English descriptions, auto-generates MP4 with synchronized audio
- **Parameter Control**: Resolution (480p/720p/1080p), aspect ratio (7 options), duration (4-15s)
- **Zero Barrier**: Built-in ~10,000 free credits, no configuration needed

**Target Users**

- 🎬 **Short Video Creators** — Quickly generate vertical video assets for TikTok/Xiaohongshu/Channels
- 📦 **Product Managers** — Generate product concept videos for proposals and demos
- 🎨 **Creative Professionals** — Turn ideas into visual videos with natural language

---

## Features

### Core Features

- **Text-to-Video**: Input prompts, Seedance 2.0 generates MP4 with synced audio
- **Parameter Control**: Customize resolution, aspect ratio, and duration
- **Virtual Avatars**: Reference preset virtual avatars, no real face uploads needed
- **Auto Polling**: Script automatically waits for task completion
- **Task Management**: Submit-only mode with taskId for later query and download

---

## API Key Acquisition & Security

- This skill comes with a built-in public API key (~10,000 free credits), ready to use.
- For personal keys: `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the device environment variable `REDFOX_API_KEY` before using this skill.
- Before providing your key, verify its origin, scope, validity period, and whether reset/revocation is supported.
- Never hardcode or expose the key in code, prompts, logs, or output files.

---

## Usage

Describe the video you want in natural language.

### Quick Reference

| Intent | Example | Result |
|--------|---------|--------|
| Text-to-video | "Generate a video of an orange cat yawning on a windowsill" | Submits task, auto-generates MP4 |
| Vertical short video | "Generate a vertical city night scene video" | 9:16 ratio for TikTok/Xiaohongshu |
| High-res long video | "Generate a 1080p landscape video, 10 seconds" | High quality, longer duration output |
| Check progress | "Check the result of video task XXX" | Query by taskId and download completed video |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|--------------|---------|
| Social media creation | Short video creator | "Generate a vertical beauty product demo video" | Fast video asset production, lower costs |
| Product demo | Product manager | "Generate a smartwatch feature demo video" | No professional video skills needed |
| Creative validation | Designer | "Generate a cyberpunk city night scene" | Idea to video in a single command |
| Brand operations | Content ops | "Generate a brand-themed background video" | Unified visual style, boosted output efficiency |
