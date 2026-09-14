# GPT-image2 / image-gen

---

## Overview

An AI image generator based on OpenAI's gpt-image-2 model, supporting text-to-image and image-to-image generation.

**Core Value**

- **Text-to-Image**: Enter a prompt to generate high-quality new images
- **Image-to-Image**: Upload up to 2 reference images with a prompt for editing
- **Batch Generation**: Up to 4 images per call (new interface limit)
- **Fine-grained Control**: Aspect ratio (16:9 / 9:16 / 1:1, 13 options) + resolution tier (1k / 2k / 4k)

**Target Users**

- 🎨 **Designers** — Quickly generate creative concepts and logo designs
- 📱 **Content Marketers** — Batch-produce image assets
- 🛍️ **E-commerce Sellers** — Generate product and scene photography

---

## Features

### Core Features

- **Text-to-Image**: Enter a prompt and gpt-image-2 generates PNG images
- **Image-to-Image**: Upload up to 2 reference images for editing
- **Batch Generation**: Up to 4 images per call, ideal for icon sets and series
- **Aspect Ratio**: 1:1 / 3:2 / 2:3 / 4:3 / 3:4 / 5:4 / 4:5 / 16:9 / 9:16 / 2:1 / 1:2 / 21:9 / 9:21
- **Resolution Tier**: 1k (fast) / 2k (default) / 4k (high quality, slower)
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

Simply describe the image you want in natural language.

### Quick Reference

| Intent | Example | Result |
|--------|---------|--------|
| Text-to-Image | "Generate an image of an orange cat looking at the sunset" | Submits task and generates a high-quality image |
| Image-to-Image | "Turn this photo into cyberpunk style" | Uploads reference for style transfer |
| Portrait Cover | "Generate a 3:4 portrait cover for social media" | Uses --size 3:4 for vertical composition |
| Batch Generation | "Generate 4 flat style icons" | Generates multiple style-consistent images at once |

---

## Use Cases

| Scenario | Role | Example Prompt | Benefit |
|----------|------|---------------|---------|
| Creative visuals | Content marketer | "Generate an article cover image" | Quick high-quality illustrations |
| Logo design | Designer | "Generate a minimalist logo" | Rapid design exploration |
| Product display | E-commerce operator | "Generate a 4:3 product photo" | Zero photography cost |
| Style transfer | Photographer | "Turn this photo into watercolor style" | Natural language style conversion |
