# Seedance2.0 / seedance-video-gen

---

## Overview

An AI video generator based on the Volcano Engine Seedance 2.0 model. Generate MP4 videos with a single command.

**Core Value**

- **Text-to-Video**: Enter Chinese or English descriptions to auto-generate MP4 videos with synchronized audio
- **Full Control**: Adjustable resolution (480p/720p), aspect ratio (7 options), and duration (4-15 seconds)
- **Image-to-Video**: Reference first-frame, last-frame, or reference images via URL

**Target Users**

- 🎬 **Short Video Creators** — Quickly generate vertical video assets for Douyin/Xiaohongshu/WeChat Channels
- 📦 **Product Managers** — Generate product concept videos for proposals and demos
- 🎨 **Creative Professionals** — Turn ideas into visual videos with natural language

---

## Features

### Core Features

- **Text-to-Video**: Enter a prompt and Seedance 2.0 generates an MP4 with synchronized audio
- **Parameter Control**: Customize resolution, aspect ratio, and video duration
- **Image-to-Video**: Reference first-frame, last-frame, or reference images via URL
- **Auto-Polling**: The script automatically waits for task completion, no manual refresh needed
- **Task Management**: Submit-only mode with taskId for later query and download

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, verify its source, available scope, validity period, and whether it supports reset/revocation.
- Do not hardcode or expose the key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe the video scene you want in natural language.

### Quick Reference

| Intent | Example | Result |
|--------|---------|--------|
| Text-to-Video | "Generate a video of an orange cat yawning on a windowsill" | Submits task, auto-generates MP4 video |
| Vertical Short Video | "Generate a vertical city nightscape video" | 9:16 aspect ratio for Douyin/Xiaohongshu |
| HD Long Video | "Generate a 720p landscape video, 10 seconds" | High-quality long-duration output |
| Image-to-Video | "Make the cat in this image blink" | Reference/first-frame/last-frame image generation |
| Query Progress | "Check the result of video task XXX" | Query and download completed video by taskId |

---

## Use Cases

| Scenario | Role | Example Prompt | Benefit |
|----------|------|---------------|---------|
| Social media creation | Short video creator | "Generate a vertical cosmetics product demo video" | Quick video asset production, lower costs |
| Product demo | Product manager | "Generate a smartwatch feature demo video" | No professional skills needed, text-to-video |
| Creative validation | Designer | "Generate a cyberpunk city nightscape" | From idea to video in one command |
| Brand marketing | Content marketer | "Generate a brand-themed background video" | Consistent visual style, higher output efficiency |
