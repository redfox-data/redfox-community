# Short Video Downloader / video-downloader

---

## Introduction

Paste a sharing link to download watermark-free videos/images from Douyin, Xiaohongshu, Kuaishou, and Bilibili. Built-in public API Key — ready to use out of the box.

**Core Value**

- **Watermark-free direct links**: The API automatically returns clean download URLs — no manual watermark removal needed.
- **Four platforms**: One tool covers Douyin, Xiaohongshu, Kuaishou, and Bilibili.
- **Zero-config start**: Built-in public API Key with ~10,000 free uses — just start.

**Target Users**

- 🎬 **Short video creators** — Download素材 for remixing and editing.
- 📱 **Content operators** — Batch-save competitor videos for analysis.
- 💾 **General users** — Save favorite videos locally for offline viewing.

---

## Features

### Core Capabilities

- **Watermark-free download**: API returns clean direct links automatically.
- **Image-text download**: Supports downloading all images from image-text posts (Xiaohongshu image-text not yet supported).
- **Cross-platform**: One tool for Douyin, Xiaohongshu, Kuaishou, and Bilibili.
- **Link auto-detection**: Supports short links, sharing links, and web URLs.
- **Progress display**: Real-time progress bar and percentage during download.
- **Multi-device compatible**: Works with both mobile sharing links and PC web URLs.

---

## API Key Info

A built-in public API Key provides ~**10,000 free uses** — zero configuration needed. When the quota runs out, register at [RedFoxHub](https://redfox.hk/login?source=github) for a personal API Token:

| Method | Command |
|--------|---------|
| **Environment variable** (recommended) | `export REDFOX_API_KEY=ak_your_key` |
| **CLI argument** | `python3 "$SKILL_PATH/assets/downloader.py" "<link>" --api-key ak_your_key` |
| **Config file** | `echo '{"api_key":"ak_your_key"}' > ~/.qoder/apis/redfox.json` |

---

## Usage Guide

Just paste a sharing link — no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|----------------|--------|
| Download Douyin video | "Download this Douyin video https://v.douyin.com/xxx" | Auto-parse and download watermark-free video |
| Download Xiaohongshu video | "Download this Xiaohongshu http://xhslink.com/o/xxx" | Download watermark-free video locally |
| Download Bilibili video | "Save this Bilibili video https://b23.tv/xxx" | Download best quality video |

### Supported Platforms & Link Formats

| Platform | Link format | Notes |
|----------|-------------|-------|
| Douyin | `https://v.douyin.com/xxxxxx/` | Mobile sharing / PC web links |
| Xiaohongshu | `http://xhslink.com/o/xxxxxx` | Short sharing links |
| Kuaishou | `https://v.kuaishou.com/xxxxxx` | Mobile sharing links |
| Bilibili | `https://b23.tv/xxxxxx` | Short sharing links |

---

## Use Cases

| Scenario | Role | Example query | Benefit |
|----------|------|---------------|---------|
| 素材 download | Video creator | "Download this Douyin video for reference" | Get watermark-free素材 for editing |
| Competitor archiving | Content ops | "Save these competitor videos" | Offline review of competitor content |
| Offline backup | General user | "Save this video locally" | Watch favorites anytime offline |

---

## Notes

- Only one link at a time — batch upload is not supported.
- Short links expire; re-copy the sharing link if parsing fails.