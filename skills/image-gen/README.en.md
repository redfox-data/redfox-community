# GPT - image2 / image-gen

---

## Introduction

Generate high-quality images using OpenAI's gpt-image-2 model. Supports text-to-image and image-to-image editing. Built-in public API Key — ready to use out of the box.

**Core Value**

- **Dual-mode generation**: Text-to-image + image-to-image — one tool for creation and editing.
- **Batch delivery**: Up to 10 images per run with parameterized size/format/background control.
- **Zero-config start**: Built-in public API Key (~10,000 free uses) — just start.

**Target Users**

- 🎨 **Designers / creators** — Quickly generate creative assets, logos, and illustrations.
- 📱 **Content operators** — Batch-produce images for social media and product listings.
- 💼 **Product managers** — Rapidly create prototype visuals and concept art.

---

## Features

### Core Capabilities

- **Text-to-image**: Enter a prompt and generate a brand-new image.
- **Image-to-image**: Upload a reference image + prompt to edit and regenerate (supports high/low fidelity control).
- **Batch generation**: Up to 10 images per run with custom sizes (1024x1024 / 1024x1792 / 1792x1024).
- **Multi-format output**: PNG, JPEG, WebP with transparent background support.
- **Progress display**: Auto-polls and shows generation progress in real time.

### Highlights

- **Built-in free quota**: ~10,000 uses — no subscription or credit card needed.
- **Transparent background**: One-click transparent backgrounds with PNG/WebP format.

---

## API Key Info

A built-in public API Key provides ~**10,000 free uses** — zero configuration needed. When the quota runs out, register at [RedFoxHub](https://redfox.hk/login?source=github) for a personal API Token:

| Method                                 | Command                                                                                  |
| -------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Environment variable** (recommended) | `export REDFOX_API_KEY=ak_your_key`                                                      |
| **CLI argument**                       | `python3 "$SKILL_PATH/assets/imagegen.py" "prompt" --api-key ak_your_key`                |
| **Config file**                        | `mkdir -p ~/.qoder/apis && echo '{"api_key":"ak_your_key"}' > ~/.qoder/apis/redfox.json` |

---

## Usage Guide

Describe the image you want in natural language — no command parameters to memorize.

### Quick Reference

| Intent           | Example phrase                                                   | Result                          |
| ---------------- | ---------------------------------------------------------------- | ------------------------------- |
| Text-to-image    | "Draw an orange cat sitting on a windowsill watching the sunset" | Generate a brand-new image      |
| Landscape format | "Generate a cyberpunk city skyline in landscape"                 | 1792x1024 landscape output      |
| Transparent BG   | "Generate a minimalist cat logo with transparent background"     | PNG with transparent background |
| Image-to-image   | "Change the cat to white, replace background with starry sky"    | Edit based on reference image   |
| Batch generate   | "Generate 4 flat-style icons"                                    | Output 4 images at once         |

---

## Use Cases

| Scenario              | Role            | Example query                                   | Benefit                        |
| --------------------- | --------------- | ----------------------------------------------- | ------------------------------ |
| Creative assets       | Designer        | "Draw a minimalist cat logo"                    | Quickly get design sketches    |
| Product images        | Content ops     | "Generate 3 product photos on white background" | Batch-produce consistent素材   |
| Style transfer        | Creator         | "Convert this photo to watercolor style"        | One-click style transformation |
| Concept visualization | Product manager | "Draw a smart home scene"                       | Rapid prototype concept art    |
