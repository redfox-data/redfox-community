# GPT-image2 / image-gen

---

## Overview

AI image generator based on OpenAI gpt-image-2 model. Supports text-to-image and image-to-image. Built-in public API key, ready to use.

**Core Value**

- **Text-to-Image**: Input prompts to generate brand new high-quality images
- **Image-to-Image**: Upload reference image + prompt for editing and regeneration
- **Batch Generation**: Up to 10 images at once, supports transparent backgrounds
- **Zero Barrier**: Built-in ~10,000 free credits, paste a prompt and go

**Target Users**

- 🎨 **Designers** — Quickly generate creative concepts and logo designs
- 📱 **Content Operators** — Batch produce visual assets
- 🛍️ **E-commerce Sellers** — Generate product display and scene images

---

## Features

### Core Features

- **Text-to-Image**: Input prompts, gpt-image-2 generates PNG/JPEG/WebP images
- **Image-to-Image**: Upload reference image with high/low fidelity editing
- **Batch Generation**: Up to 10 images, ideal for icon sets and series graphics
- **Transparent Background**: PNG/WebP transparent background output
- **Multiple Sizes**: Fast tier (1024x1024 etc.) + HD tier (2048x2048 etc.)
- **Task Management**: Submit-only mode with taskId for later query and download

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

Describe the image you want in natural language.

### Quick Reference

| Intent | Example | Result |
|--------|---------|--------|
| Text-to-image | "Generate an orange cat looking out at sunset" | Submits task, generates high-quality image |
| Image-to-image | "Turn this photo into cyberpunk style" | Uploads reference for style transfer |
| Transparent background | "Generate a minimalist cat logo, transparent bg" | Generates PNG with transparent background |
| Batch generation | "Generate 4 flat-style icons" | Multiple style-consistent images at once |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|--------------|---------|
| Creative graphics | Content ops | "Generate an article cover image" | Fast high-quality visual production |
| Logo design | Designer | "Generate a minimalist logo" | Quickly validate multiple design directions |
| Product display | E-commerce ops | "Generate a white-background product photo" | Zero photography cost product images |
| Style transfer | Photographer | "Turn this photo into watercolor style" | Natural language-driven style conversion |
