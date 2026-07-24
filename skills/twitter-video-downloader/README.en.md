# X(Twitter) Video Downloader / twitter-video-downloader

---

## Introduction

Paste an X(Twitter) video link and get a watermark-free download URL instantly. Copy it into your browser or download tool to save — both x.com and twitter.com links are supported, and you won't end up with a watermarked version.

**Core Value**

- **Paste and go**: paste a tweet link and get a video download URL right away — copy into your browser or download tool, no plugins or subscriptions needed.
- **Clean, watermark-free**: every returned video is watermark-free, ready for collecting or remixing.
- **Both domains recognized**: x.com and twitter.com links both work — mobile share links and desktop URLs alike.
- **Results at a glance**: resource type, duration, download link, cover link, and full description are all laid out clearly so you know exactly what to copy.

**Who Is It For**

- 🎬 **Creators / Editors** — quickly save video clips from X for secondary creation
- 📚 **Content Collectors** — back up favorite Twitter videos locally, safe from deleted posts
- 🔍 **Operators / Researchers** — download competitor or trending videos for analysis

---

## Features

### Core Features

- **Video Parsing**: paste an X(Twitter) video tweet link to parse out the watermark-free video download URL.
- **Complete Information**: displays resource type, duration, download link, cover link, and full description line by line without truncation.
- **Dual Domain Support**: recognizes both x.com and twitter.com links.

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
| Download an X video | "Download this video https://x.com/user/status/xxxxx" | Parses the link and returns a direct video download URL |
| Save a Twitter video | "Help me save this Twitter video" | Prompts you to paste the link, then returns the download URL |

### Output Example

After parsing, you will receive a result like:

> ✅ Parsed successfully!
>
> 📝 Description: the full tweet text shown in its entirety
>
> 🎬 Resources:
> type, duration, download link, and cover link listed one by one
>
> Copy the link into your browser or download tool to download.

---

## Use Cases

| Scenario | Role | Example | Benefit |
| -------- | ---- | ------- | ------- |
| Material collection | Editor | "Download this X video" | Get watermark-free footage straight into your editing workflow |
| Content backup | Collector | "Save this Twitter video" | Keep it locally forever, even if the original post is deleted |
| Trend analysis | Operator | "Download this viral video" | Watch offline repeatedly and break down what makes it viral |
