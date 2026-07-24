# YouTube Video Downloader / youtube-video-downloader

---

## Introduction

Paste a YouTube video link and get watermark-free download URLs instantly — returned resources may include video and audio files in various formats. Regular videos, Shorts, and short links are all supported. Copy the link into your browser or download tool to save, and you won't end up with a watermarked version.

**Core Value**

- **Paste and go**: paste a video link and get download URLs right away — video and audio resources at a glance, no plugins or subscriptions needed.
- **Clean, watermark-free**: every returned video is watermark-free, ready for collecting or remixing.
- **All formats supported**: regular videos (watch), Shorts, and short links (youtu.be) all work.
- **All resources fully displayed**: the API returns multiple resources (video files, audio files, etc.), and each download link is shown in full — pick what you need and copy directly.

**Who Is It For**

- 🎬 **Creators / Editors** — quickly save video clips from YouTube for secondary creation
- 📚 **Content Collectors** — back up favorite YouTube videos locally, safe from deleted videos
- 🔍 **Operators / Researchers** — download competitor or trending videos for analysis

---

## Features

### Core Features

- **Video Parsing**: paste a YouTube video link to parse out watermark-free video download URLs (returned resources may include video and audio files in various formats).
- **Complete Information**: displays resource type, duration, download link, and cover link for every resolution; full description shown line by line without truncation.
- **Multi-Format Support**: recognizes regular videos, Shorts, and short links (youtu.be).

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
| Download a YouTube video | "Download this video https://www.youtube.com/watch?v=xxxxx" | Parses the link and returns direct video/audio download URLs |
| Save a YouTube Short | "Help me save this Short" | Prompts you to paste the link, then returns the download URLs |

### Output Example

After parsing, you will receive a result like:

> ✅ Parsed successfully!
>
> 📝 Description: full video title and description shown
>
> 🎬 Resources (N total):
> Each resource (video file, audio file, etc.) listed one by one
> Type, duration, download link, and cover link all displayed
>
> Copy the link into your browser or download tool to download.

---

## Use Cases

| Scenario | Role | Example | Benefit |
| -------- | ---- | ------- | ------- |
| Material collection | Editor | "Download this YouTube video" | Get watermark-free footage — both video and audio files available, straight into your editing workflow |
| Content backup | Collector | "Save this YouTube Short" | Keep it locally forever, even if the original video is deleted |
| Trend analysis | Operator | "Download this viral video" | Watch offline repeatedly and break down what makes it viral |
