# Instagram Video Downloader / instagram-video-downloader

---

## Introduction

Paste an Instagram video link and get a watermark-free download URL instantly. Both Reels and regular posts are supported — copy the link into your browser or download tool to save, and you won't end up with a watermarked version.

**Core Value**

- **Paste and go**: paste a post link and get a video download URL right away — copy into your browser or download tool, no plugins or subscriptions needed.
- **Clean, watermark-free**: every returned video is watermark-free, ready for collecting or remixing.
- **Reels and posts both recognized**: Reel short videos and regular post video links both work — mobile share links and desktop URLs alike.
- **Results at a glance**: resource type, duration, download link, cover link, and full description are all laid out clearly so you know exactly what to copy.

**Who Is It For**

- 🎬 **Creators / Editors** — quickly save video clips from IG for secondary creation
- 📚 **Content Collectors** — back up favorite Instagram videos locally, safe from deleted posts
- 🔍 **Operators / Researchers** — download competitor or trending videos for analysis

---

## Features

### Core Features

- **Video Parsing**: paste an Instagram video post link to parse out the watermark-free video download URL.
- **Complete Information**: displays resource type, duration, download link, cover link, and full description line by line without truncation.
- **Dual Format Support**: recognizes both Reel short videos and regular post video links.

---

## API Key & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Please register at [RedFoxHub](https://redfox.hk?source=github) to obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset/revoked.
- Never hardcode or expose the key in code, prompts, logs, or output files.

---

## Usage Guide

Just describe what you want in natural language — no commands to memorize.

### Quick Reference

| Intent | Example | Result |
| ------ | ------- | ------ |
| Download an IG video | "Download this video https://www.instagram.com/reel/xxxxx/" | Parses the link and returns a direct video download URL |
| Save an Instagram video | "Help me save this IG video" | Prompts you to paste the link, then returns the download URL |

### Output Example

After parsing, you will receive a result like:

> ✅ Parsed successfully!
>
> 📝 Description: the full post text shown in its entirety
>
> 🎬 Resources:
> type, duration, download link, and cover link listed one by one
>
> Copy the link into your browser or download tool to download.

---

## Use Cases

| Scenario | Role | Example | Benefit |
| -------- | ---- | ------- | ------- |
| Material collection | Editor | "Download this IG video" | Get watermark-free footage straight into your editing workflow |
| Content backup | Collector | "Save this Instagram Reel" | Keep it locally forever, even if the original post is deleted |
| Trend analysis | Operator | "Download this viral Reel" | Watch offline repeatedly and break down what makes it viral |
