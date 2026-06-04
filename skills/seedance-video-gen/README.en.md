# Seedance Video Generator / seedance-video-gen

---

## Overview

An AI video generation tool powered by the **Seedance 2.0** model from Volcengine ARK. Simply describe what you want and get an MP4 video with synchronized audio — no API setup, no whitelist application, just one command.

**Core Value**

- **Zero barrier to start**: No need to configure AK/SK or integrate ARK authentication on Volcengine — just sign up at redfox.hk and go.
- **Pay per use**: No membership, no card binding, no subscription — pay only for what you generate.
- **End-to-end automation**: From task submission and status polling to video download, everything runs in a single command.

**Intended Users**

- 🎬 **Short-video creators / social media operators** — Quickly generate vertical video assets at a fraction of the production cost.
- 💼 **Product managers / entrepreneurs** — Turn copy into video for pitches and demos without professional production skills.
- 🎨 **Designers / creatives** — Go from idea to video in one command to validate creative directions fast.
- 📚 **Educators / trainers** — Visualize abstract concepts as short clips with zero animation expertise.

---

## Features

### Core Capabilities

- **Text-to-video**: Enter a prompt in Chinese or English and automatically generate an MP4 video with synchronized audio.
- **Flexible parameter control**: Mix and match resolution (480p / 720p / 1080p), aspect ratio (7 options), and duration (4–15 seconds).
- **Built-in virtual avatars**: Reference preset virtual avatars via `asset://` URIs — no real face uploads required.
- **Automatic task management**: After submission, the task status (queued → generating → completed) is polled automatically — no manual waiting.
- **Multi-clip chaining**: Extract the last frame of one video to use as the first frame of the next for seamless scene transitions.

### Highlights

- **Synchronized audio**: Video and sound are generated together — no post-production dubbing needed.
- **Reproducible results**: Set a seed value to regenerate the same video with identical parameters.
- **Full SSL verification**: HTTPS transport with end-to-end encryption for all data.

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

Simply describe the video scene you want in natural language — no fixed commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
| --- | --- | --- |
| Basic generation | "Generate a video: an orange cat yawning on the windowsill in warm sunlight" | Default 720p, 16:9, 5-second video |
| Vertical short clip | "Generate a 9:16 vertical city night scene video" | Auto-adapts to TikTok / Xiaohongshu portrait ratio |
| HD long clip | "1080p ocean waves in slow motion, 10 seconds" | High resolution with specified duration |
| Silent video | "Brand-themed background, no audio" | Pure visuals without audio track |
| Check existing task | "Check if my previously submitted video task is done" | Polls the existing task and downloads the result |

### Output Example

Once generation is complete, you will see something like:

```
[✓] Video ready: 5s, 720p, 16:9
[✓] Token usage: 108900
[→] Downloading video: video.mp4
[✓] Done!
  ~/Downloads/QoderVideos/video.mp4 (2.5 MB)
```

The video is automatically downloaded to `~/Downloads/QoderVideos/` and ready to play.

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| --- | --- | --- | --- |
| Social media assets | Short-video creator / social operator | "Generate a vertical product showcase video for beauty" | Cut production cost from hours to minutes |
| Product demo | Product manager / entrepreneur | "Generate a smartwatch feature demo video, 1080p" | No video production skills needed — copy is the video |
| Brand content ops | Content ops / marketing | "Generate a brand-themed background video, silent" | Boost output efficiency with consistent brand visuals |
| Creative validation | Designer / creative | "Cyberpunk city at night, neon lights flickering" | Idea to video in one command |
| Education visualization | Educator / trainer | "Solar system planets orbiting the sun, 10 seconds" | Knowledge visualization with zero animation skills |

---
