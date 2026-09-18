# Xiaohongshu Video Downloader / xiaohongshu-video-downloader

---

## Introduction

Paste a Xiaohongshu (RED) video link with the `xsec_token` parameter and get a watermark-free download URL instantly. Copy it into your browser or download tool to save — both www.xiaohongshu.com web links and xhslink.com short links are supported, and you won't end up with a watermarked version.

> ⚠️ **The link must include the `xsec_token` parameter**, otherwise the Xiaohongshu API will return a link format error. Official example link:
> `https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed`

**Core Value**

- **Paste and go**: paste a video link with `xsec_token` and get a video download URL right away — copy into your browser or download tool, no plugins or subscriptions needed.
- **Clean, watermark-free**: every returned video is watermark-free, ready for collecting or remixing.
- **Both link types recognized**: www.xiaohongshu.com web links and xhslink.com short links both work — mobile share links and desktop URLs alike.
- **Batch-friendly**: paste multiple links at once — each is parsed sequentially with a success/failure summary at the end, no need to go one by one.
- **Smart validation**: links from other platforms, or links missing `xsec_token`, are detected and flagged immediately with the official example, so you don't waste a trip.
- **Results at a glance**: resource type, duration, download link, cover link, and full description are all laid out clearly so you know exactly what to copy.

**Who Is It For**

- 🎬 **Creators / Editors** — quickly save video clips from Xiaohongshu for secondary creation
- 📚 **Content Collectors** — back up favorite Xiaohongshu videos locally, safe from deleted posts
- 🔍 **Operators / Researchers** — download competitor or trending videos for analysis

---

## Features

### Core Features

- **Video Parsing**: paste a Xiaohongshu video link with the `xsec_token` parameter to parse out the watermark-free video download URL.
- **Batch Parsing**: paste multiple links at once — each is parsed sequentially with a success/failure summary at the end.
- **Smart Validation**: automatically detects Xiaohongshu video links and validates the `xsec_token` parameter — non-compliant links prompt a retry with the official example.
- **API Error Fallback**: when the Xiaohongshu API returns a link format error, the official example link is shown automatically to guide the user.
- **Complete Information**: displays resource type, duration, download link, cover link, and full description line by line without truncation.
- **Dual Link Support**: recognizes both www.xiaohongshu.com web links and xhslink.com short links (both must carry `xsec_token`).

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
| Download a Xiaohongshu video | "Download this video https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed" | Parses the link and returns a direct video download URL |
| Batch download videos | "Download these videos link1 link2 link3" (each link must carry `xsec_token`) | Parses each link sequentially and summarizes success/failure counts |
| Save a Xiaohongshu video | "Help me save this Xiaohongshu video" | Prompts you to paste the link with `xsec_token`, then returns the download URL |

### Link Format Requirement

The input link must include the `xsec_token` parameter. Otherwise, the script will report "link is missing xsec_token parameter" and show the official example.

**Official example link**:

```
https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed
```

**How to get a link with `xsec_token`**:

- PC web: open the note on the Xiaohongshu website and copy the URL from the browser address bar
- Mobile app: note page → Share → Copy Link (the copied link includes `xsec_token` by default)

### Output Example

After parsing, you will receive a result like:

> ✅ Parsed successfully!
>
> 📝 Description: the full video caption shown in its entirety
>
> 🎬 Resources:
> type, duration, download link, and cover link listed one by one
>
> Copy the link into your browser or download tool to download.
>
> ⚠️ Video download links expire in about 5 minutes — copy to your browser and download immediately!

---

## Use Cases

| Scenario | Role | Example | Benefit |
| -------- | ---- | ------- | ------- |
| Material collection | Editor | "Download this Xiaohongshu video" | Get watermark-free footage straight into your editing workflow |
| Content backup | Collector | "Save this Xiaohongshu video" | Keep it locally forever, even if the original post is deleted |
| Trend analysis | Operator | "Download this viral video" | Watch offline repeatedly and break down what makes it viral |
