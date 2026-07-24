# WeChat Video Downloader / wechat-video-downloader

---

## Overview

Paste a WeChat Channels video share link and get the real download address, along with the video title and cover image for easy archiving.

**Core Value**

- **One-click retrieval**: Paste a link to get a high-definition, watermark-free direct video link with no extra steps
- **Complete metadata**: Video title and cover image are returned together for easy asset organization and search
- **Batch support**: Submit multiple links at once to boost material collection efficiency

**Intended Users**

- 🎬 **Content creators** — Quickly download WeChat Channels videos for remix and editing
- 📊 **Operations staff** — Save competitor videos for content strategy analysis
- ✂️ **Video editors** — Efficiently obtain HD source files to streamline your workflow

---

## Features

### Core Capabilities

- **Direct link resolution**: Get the real video download URL, openable in browser or downloadable locally
- **Metadata included**: Automatically returns video title and cover image, no manual note-taking needed
- **Instant results**: Results are returned immediately after submitting a link, no queueing required

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

Simply describe your needs in natural language—no commands to memorize.

### Quick Reference

| Intent | Example Phrase | Result |
| ------ | -------------- | ------ |
| Single video | "Help me parse this WeChat Channels link: https://weixin.qq.com/sph/xxxx" | Returns video title, cover image, and download URL |
| Batch parsing | "Parse these WeChat Channels links for me" and paste multiple links | Returns download info for all videos at once |
| Download video | "Download this WeChat Channels video: https://weixin.qq.com/sph/xxxx" | Provides a ready-to-use download URL |

### Output Example

After submitting a link, you'll receive results in this format:

**1. Title**: Video title
   **Cover**: [Cover Image](cover_link)
   **Download URL**: Direct video link
   **Action**: [Watch Video](direct_video_link)

> ⚠️ WeChat Channels download links are valid for approximately **5 minutes**. Please save promptly.

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Material collection | Content creator | "Download these trending WeChat Channels videos for me, I want to make a mashup" | Batch HD material acquisition, saving time |
| Competitor analysis | Operations staff | "Parse this competitor's WeChat Channels link and save the video and cover" | Quickly archive competitor content for strategy review |
| Source file retrieval | Video editor | "Download the original file of this WeChat Channels video for post-production" | Directly get watermark-free HD source files |
| Daily archiving | Self-media blogger | "Download and back up today's WeChat Channels video" | One-click archive without losing original assets |

---
