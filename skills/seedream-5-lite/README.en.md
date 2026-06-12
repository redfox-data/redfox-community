# seedream 5.0 lite / seedream 5.0 lite

---

## Overview

AI image generator based on ByteDance Volcano Engine seedream 5.0 lite model. Supports text-to-image, image-to-image, batch generation, and prompt optimization. One command to generate high-quality images. Built-in public API key, ready to use.

**Core Value**

- **Text-to-Image**: Input Chinese or English descriptions to generate HD images
- **Image-to-Image**: Upload reference image + prompt for style transfer and editing
- **Batch Generation**: Auto-generate multiple related images, up to 15
- **Zero Barrier**: Built-in ~10,000 free credits, no configuration needed

**Target Users**

- 🎨 **Designers** — Quickly generate high-quality graphics, covers, and product shots
- 📱 **Social Media Operators** — Batch produce visually consistent assets
- 🛍️ **E-commerce Sellers** — Zero photography cost, fast product scene generation

---

## Features

### Core Features

- **Text-to-Image**: Input prompts, seedream 5.0 lite auto-generates HD images
- **Image-to-Image**: Upload reference image for editing and style transfer
- **Batch Generation**: `auto` mode generates multiple related images
- **Prompt Optimization**: Built-in standard (high quality) and fast modes
- **High Resolution**: Support for 2K/3K/4K or custom pixel dimensions
- **Task Management**: Submit-only mode with taskId for later query

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
| Text-to-image | "Generate a latte on a wooden table" | Submits task, generates HD image |
| Image-to-image | "Turn this photo into oil painting style [image]" | Uploads reference for style transfer |
| Batch generation | "Generate a set of minimalist desk still life images" | Batch generates style-consistent images |
| High resolution | "Generate a 4K ultra-HD mountain sunrise" | Outputs ultra-high resolution image |

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
|----------|------|--------------|---------|
| Social media graphics | Xiaohongshu blogger | "Generate an Instagram-style coffee photo for cover" | Fast high-quality graphic production |
| E-commerce product shots | E-commerce ops | "Generate a product scene for white earphones" | Zero photography cost, fast output |
| Creative validation | Designer | "Generate a cyberpunk future city concept" | Idea to visual in a single command |
| Batch content ops | Content ops | "Generate a set of breakfast photos for article graphics" | Batch produce style-consistent visuals |
