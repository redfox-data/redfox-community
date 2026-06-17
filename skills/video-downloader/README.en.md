# Short Video Downloader / video-downloader

---

## Overview

Watermark-free video downloader supporting Douyin, Xiaohongshu, Kuaishou, and Bilibili. Paste a share link and download.

**Core Value**

- **Multi-Platform**: Douyin, Xiaohongshu, Kuaishou, Bilibili — one tool for all
- **Watermark-Free**: API auto-returns watermark-free direct links
- **Auto-Adaptive**: Supports short links, share links, web links, and more

**Target Users**

- 📱 **Short Video Users** — Save favorite watermark-free videos locally with one click
- ✂️ **Content Creators** — Download assets for editing and remixing
- 💾 **Data Archivers** — Offline backup of bookmarked content

---

## Features

### Core Features

- **Watermark-Free Download**: API auto-returns watermark-free direct links for video and image posts
- **Cross-Platform**: One tool covers Douyin, Xiaohongshu, Kuaishou, and Bilibili
- **Auto-Adaptive Links**: Supports short links, share links, web links, and more
- **Progress Display**: Real-time progress bar with percentage during download
- **Smart Naming**: Auto-uses video title as filename

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, verify its source, available scope, validity period, and whether it supports reset/revocation.
- Do not hardcode or expose the key in plaintext within code, prompts, logs, or output files.

---

## Usage

Paste a video share link to download.

### Quick Reference

| Intent | Example | Result |
|--------|---------|--------|
| Download Douyin | "Download this Douyin video [link]" | Parses link, downloads watermark-free MP4 |
| Download Xiaohongshu | "Download this Xiaohongshu video [link]" | Parses Xiaohongshu share link and downloads |
| Download Bilibili | "Download this Bilibili video [link]" | Downloads Bilibili video in best quality |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|--------------|---------|
| Watermark-free save | General user | "Download this Douyin video without watermark" | One-click watermark-free HD video |
| Content remixing | Creator | "Download these videos as editing assets" | Get watermark-free assets for remixing |
| Offline backup | Collector | "Download all my bookmarked videos" | Offline backup of favorite content |
