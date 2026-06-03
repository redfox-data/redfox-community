# AI Image Generator / gpt-image2-pro

---

## Introduction

Powered by the gpt-image-2 model, generate high-quality images from text prompts — supporting both text-to-image and image-to-image, with built-in free credits ready to use.

**Core Value**

- **Ready to use**: Built-in public credits for approximately 10,000 calls — no subscription or credit card required, just paste your prompt
- **Dual-mode coverage**: Text-to-image creates from scratch; image-to-image edits based on a reference — switch with a single `--image` parameter
- **Flexible control**: Multiple sizes, formats, transparent backgrounds, and fidelity options; batch generate up to 10 images at once

**Who It's For**

- 🎨 **Designers / Creators** — Rapidly produce images and explore styles, lowering the barrier to visual creation
- 📢 **Brand / E-commerce Operators** — Batch-generate product images and transparent-background logos with a unified visual style
- 💡 **Content Planners** — Get usable visuals for articles, notes, and short videos in one step

---

## Features

### Core Capabilities

- **Text-to-image**: Enter a text prompt to generate a brand-new image
- **Image-to-image**: Upload a reference image + edit prompt to generate a new image based on the original
- **Multiple sizes**: Supports 1024×1024, 1024×1792, 1792×1024, and auto sizing
- **Batch generation**: Generate up to 10 images at once for easy comparison and selection
- **Transparent background**: Supports transparent background output in PNG / WebP format
- **Fidelity control**: Image-to-image mode supports high-fidelity (subtle tweaks) and low-fidelity (major changes) modes
- **Multi-format output**: PNG, JPEG, and WebP formats with adjustable compression

### Highlights

- **Built-in free credits**: Approximately 10,000 calls with no configuration needed
- **Zero-config start**: A public API Key is embedded in the script — no setup required for first-time use
- **Credit renewal**: When free credits run out, register at RedFoxHub to get your own Key and continue using

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?souce=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing a key, confirm its source, scope, expiration, and whether it supports reset or revocation.
- Never hard-code or expose the key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Simply describe the image you want in natural language — no commands to memorize.

### Quick Reference

| Intent                 | Example phrase                                                              | Result                                             |
| ---------------------- | --------------------------------------------------------------------------- | -------------------------------------------------- |
| Text-to-image          | "Draw me an orange cat sitting on a windowsill watching the sunset"         | Generate a brand-new image from the prompt         |
| Landscape format       | "Generate a futuristic city skyline, landscape HD"                          | Generate in landscape dimensions                   |
| Transparent background | "Create a minimalist cat logo with a transparent background"                | Output a transparent-background PNG                |
| Batch generation       | "Generate 4 flat-style icons for me"                                        | Produce 4 images at once for comparison            |
| Image-to-image edit    | "Change the cat in this image to white, and the background to a starry sky" | Upload a reference, then edit based on the prompt  |
| Style transfer         | "Transform this photo into a cyberpunk style"                               | Apply a style change to the original image         |
| Major changes          | "Turn this photo into a watercolor style and add cherry blossom elements"   | Low-fidelity mode allows substantial modifications |

### Output Example

Once generation is complete, images are automatically saved to a local directory. You'll receive results like:

**Text-to-Image Example**

Prompt: "An orange cat sitting on a windowsill watching the sunset"

→ 1 × 1024×1024 PNG image saved to `~/Downloads/QoderImages/`

**Image-to-Image Example**

Prompt: "Change the cat to white and the background to a starry sky" + reference image

→ A new image edited from the original, preserving composition while applying the requested changes

---

## Use Cases

| Scenario                 | Role                | Example question                                              | Benefit                                                                             |
| ------------------------ | ------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Rapid image creation     | Designer            | "Draw me a cyberpunk-style city nightscape"                   | Go from prompt to image instantly, shortening the journey from idea to final output |
| Product image generation | E-commerce operator | "Generate a product photo on a white background, transparent" | Produce usable transparent-background assets with a unified visual standard         |
| Image editing            | Content planner     | "Change this image's style to watercolor"                     | Quickly create variations from existing assets without starting from scratch        |
| Batch icons              | UI designer         | "Generate 6 flat-style weather icons for me"                  | Produce multiple images at once for easy comparison and selection                   |

---
