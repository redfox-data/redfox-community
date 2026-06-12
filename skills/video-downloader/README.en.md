# Short Video Downloader / video-downloader

---

## Overview

Watermark-free video downloader supporting Douyin, Xiaohongshu, Kuaishou, and Bilibili. Paste a share link and download. Built-in public API key, ready to use.

**Core Value**

- **Multi-Platform**: Douyin, Xiaohongshu, Kuaishou, Bilibili — one tool for all
- **Watermark-Free**: API auto-returns watermark-free direct links
- **Zero Config**: Built-in ~10,000 free credits, paste a link and go

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

- This skill comes with a built-in public API key (~10,000 free credits), ready to use.
- For personal keys: `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the device environment variable `REDFOX_API_KEY` before using this skill.
- Before providing your key, verify its origin, scope, validity period, and whether reset/revocation is supported.
- Never hardcode or expose the key in code, prompts, logs, or output files.

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
