# GPT-image2 / image-gen

---

## Overview

An AI image generator based on OpenAI's gpt-image-2 model, supporting text-to-image and image-to-image generation.

**Core Value**

- **Text-to-Image**: Enter a prompt to generate high-quality new images
- **Image-to-Image**: Upload a reference image with a prompt for editing
- **Batch Generation**: Up to 10 images at once, with transparent background support
- **Multi-Format**: Supports PNG, JPEG, and WebP output

**Target Users**

- 🎨 **Designers** — Quickly generate creative concepts and logo designs
- 📱 **Content Marketers** — Batch-produce image assets
- 🛍️ **E-commerce Sellers** — Generate product and scene photography

---

## Features

### Core Features

- **Text-to-Image**: Enter a prompt and gpt-image-2 generates PNG/JPEG/WebP images
- **Image-to-Image**: Upload a reference image with high/low fidelity editing
- **Batch Generation**: Up to 10 images at once, ideal for icon sets and series
- **Transparent Background**: Supports PNG/WebP transparent output
- **Multiple Sizes**: Fast tier (1024x1024 etc.) + HD tier (2048x2048 etc.)
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
| Transparent BG | "Generate a minimalist cat logo with transparent background" | Generates PNG with transparent background |
| Batch Generation | "Generate 4 flat style icons" | Generates multiple style-consistent images at once |

---

## Use Cases

| Scenario | Role | Example Prompt | Benefit |
|----------|------|---------------|---------|
| Creative visuals | Content marketer | "Generate an article cover image" | Quick high-quality illustrations |
| Logo design | Designer | "Generate a minimalist logo" | Rapid design exploration |
| Product display | E-commerce operator | "Generate a white-background product photo" | Zero photography cost |
| Style transfer | Photographer | "Turn this photo into watercolor style" | Natural language style conversion |
