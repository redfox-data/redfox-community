# seedream 5.0 lite / seedream 5.0 lite

---

## Overview

An AI image generator based on the Volcano Engine seedream 5.0 lite model, supporting text-to-image, image-to-image, multi-image generation, and prompt optimization. Generate high-quality images with a single command.

**Core Value**

- **Text-to-Image**: Generate high-resolution images from Chinese or English descriptions
- **Image-to-Image**: Upload a reference image with a prompt for style transfer and editing
- **Multi-Image Generation**: Automatically generate multiple related images, up to 15
- **High Resolution**: Supports 2K, 3K, 4K, or custom pixel dimensions

**Who It's For**

- 🎨 **Designers** — Quickly generate high-quality illustrations, covers, and product photos
- 📱 **Social Media Creators** — Batch-generate visually consistent assets
- 🛍️ **E-commerce Sellers** — Produce product scene photos with zero photography cost

---

## Features

### Core Features

- **Text-to-Image**: Enter a prompt and seedream 5.0 lite generates a high-resolution image
- **Image-to-Image**: Upload a reference image for style transfer and editing
- **Multi-Image Generation**: `auto` mode generates multiple related images automatically
- **Prompt Optimization**: Built-in standard (high quality) and fast modes
- **High Resolution**: Supports 2K/3K/4K or custom pixel dimensions
- **Task Management**: Submit tasks and get a taskId to track progress anytime

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
| Text-to-Image | "Generate a latte on a wooden table" | Submits task and generates a high-res image |
| Image-to-Image | "Turn this photo into oil painting style [image]" | Uploads reference for style transfer |
| Multi-Image | "Generate a set of minimalist desk photos" | Batch-generates visually consistent images |
| High Resolution | "Generate a 4K ultra HD sunrise over snow mountains" | Outputs ultra-high resolution image |

---

## Use Cases

| Scenario | Role | Example Prompt | Benefit |
|----------|------|---------------|---------|
| Social media visuals | Xiaohongshu blogger | "Generate an Instagram-style coffee photo for my cover" | Quick high-quality illustrations |
| E-commerce product display | E-commerce operator | "Generate product scene photos for white earphones" | Zero photography cost, instant results |
| Creative inspiration | Designer | "Generate a cyberpunk futuristic city concept" | From idea to visual in one command |
| Multi-image content | Content marketer | "Generate a set of breakfast photos for article banners" | Batch visually consistent assets |
