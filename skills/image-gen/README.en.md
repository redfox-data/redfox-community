# GPT-image2 / image-gen

---

## Introduction

Generate high-quality images using OpenAI's latest **gpt-image-2** model, supporting both text-to-image and image-to-image modes. Built-in free quota — just paste a prompt and go.

**Core Value**

- **Ready to use**: Built-in public API Key with ~**10,000 free uses** — no subscription or credit card required.
- **Dual-mode creation**: Text-to-image for fresh creation, image-to-image for editing based on a reference — switch with a single `--image` parameter.
- **Batch efficiency**: Generate up to 10 images at once, with transparent background and multi-format output support.

**Target Users**

- 🎨 **Designers** — Quickly generate concept art, logos, and illustration assets.
- 📱 **Content creators** — Batch-produce social media visuals and cover images.
- 🛒 **E-commerce operators** — Generate product showcases and scene photos at zero cost.
- 💡 **AI enthusiasts** — Experience the powerful image generation capabilities of the gpt-image-2 model.

---

## Features

### Core Capabilities

- **Text-to-image**: Enter a prompt to generate brand-new images from scratch.
- **Image-to-image**: Upload a reference image with a prompt to edit and restyle the original.
- **Batch generation**: Generate up to 10 images in a single run for bulk asset needs.
- **Multi-format output**: Supports PNG, JPEG, and WebP formats.
- **Transparent background**: PNG / WebP transparent output, ideal for logos and icons.
- **Fidelity control**: Image-to-image supports high / low fidelity — fine-tune or drastically restyle as you choose.
- **Multiple resolutions**: Fast tier (1024×1792, etc.) and HD tier (2048×2048, etc.) — pick what fits your needs.
- **Task management**: Submit tasks to get a taskId, then query results later.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register an account at [RedFoxHub](https://redfox.hk?source=github) to obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing a key, verify its source, scope, validity period, and whether it supports reset/revocation.
- Never hardcode or expose keys in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe the image you want in natural language — no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|----------------|--------|
| Text to image | "Draw an orange cat sitting on a windowsill watching the sunset" | Auto-submit and download the generated image |
| HD landscape | "Futuristic city skyline, landscape HD" | Generate at 1792×1024 landscape resolution |
| Transparent logo | "Minimalist cat logo, flat design, transparent background" | Output transparent PNG for design use |
| Batch generation | "A set of flat-style icons, 4 images" | Generate 4 stylistically consistent images at once |
| Reference editing | "Change the cat to white, swap the background to a starry sky" | Upload reference and edit based on the original |
| Style transfer | "Make this photo cyberpunk style, high fidelity" | High-fidelity style transfer based on reference image |

### Output Example

After generation, image info and file path are displayed:

```
[✓] Model: gpt-image-2, Size: 1024x1792
[✓] Generated images: 1
[→] Downloading 1/1: image.png
[████████████████████] 100%

✓ Done!
  /Users/you/Downloads/QoderImages/image.png (1.2 MB)
```

---

## Use Cases

| Scenario | Role | Example query | Benefit |
|----------|------|---------------|---------|
| Social media visuals | Blogger / Content creator | "Generate a product showcase with white background" | Quick high-quality visuals, with batch support |
| Logo & icon design | UI designer | "Flat-style cat logo, transparent background" | Direct transparent PNG output for design drafts |
| Product scene photos | E-commerce ops | "Wireless earbuds floating on a light gray background" | Consistent product images with zero photography cost |
| Image editing & styling | Photographer / Creator | "Swap this photo's background to a seaside sunset" | Natural language-driven image editing, no editing software needed |
| Bulk asset production | Content ops / Marketing | "A set of minimalist desk still lifes, 6 images" | Generate multiple stylistically unified visual assets at once |

---
