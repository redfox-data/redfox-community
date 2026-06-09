# seedream5.0 lite / seedream-5-lite

---

## Introduction

An AI image generation tool powered by the Volcano Ark **seedream 5.0 lite** model. Simply describe what you want in a sentence and get high-quality images — supports text-to-image, image-to-image, batch generation, and prompt optimization. Built-in free quota, ready to use out of the box.

**Core Value**

- **Zero barrier to start**: Built-in public API Key with ~**10,000 free uses** — no registration, credit card, or key configuration needed.
- **One-line image creation**: Paste a prompt and get an image instantly — no complex parameters to learn.
- **Multi-mode coverage**: Text-to-image, image-to-image, and batch generation for everything from single creative shots to bulk visual assets.

**Target Users**

- 🎨 **Designers / Illustrators** — Quickly visualize creative ideas as high-quality images.
- 📱 **Social media creators** — Batch-generate cover images, product showcases, and post visuals.
- 🛒 **E-commerce operators** — Produce consistent product scene photos with zero photography cost.
- 💡 **AI enthusiasts** — Experience the latest seedream 5.0 lite model and explore AI image generation.

---

## Features

### Core Capabilities

- **Text-to-image**: Describe in Chinese or English and get high-definition images automatically.
- **Image-to-image**: Upload a reference image with a prompt to edit and restyle the original.
- **Batch generation**: Auto mode generates multiple related images in one go (up to 15).
- **Prompt optimization**: Built-in standard (high quality) and fast modes to improve results.
- **High-resolution output**: Supports 2K / 3K / 4K ultra-HD resolution, default 2048×2048.
- **Task management**: Submit tasks to get a taskId, then check progress and results anytime.
- **Auto-polling download**: Automatically waits for task completion and downloads images with a progress bar.

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

Simply describe what you want in natural language — no commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|----------------|--------|
| Text to image | "Generate a cyberpunk-style futuristic city at night" | Auto-submit, poll, and download HD image |
| High-resolution output | "Snow mountain sunrise photo, 4K ultra HD" | Output at 4K resolution for fine detail |
| Image editing | "Replace the background with a seaside sunset" | Upload reference image and restyle accordingly |
| Batch images | "A set of fresh breakfast photos, 6 images" | Auto-generate multiple stylistically consistent images |
| Optimized prompt | "Use high-quality mode to draw a futuristic space station interior" | Enable standard prompt optimization for finer results |

### Output Example

After generation, image info and file path are displayed:

```
[✓] Model: doubao-seedream-5-0-260128, Size: 2048x2048
[✓] Generated images: 1, Tokens: 1024
[→] Downloading 1/1: image.jpeg
[████████████████████] 100%

✓ Done!
  /Users/you/Downloads/QoderImages/image.jpeg (312.5 KB)
```

---

## Use Cases

| Scenario | Role | Example query | Benefit |
|----------|------|---------------|---------|
| Social media visuals | Blogger / Content creator | "Generate an Instagram-style latte coffee photo" | From idea to image in seconds, with batch support |
| E-commerce product showcase | E-commerce / Indie seller | "White wireless earbuds on a light gray background" | High-quality product images with zero photography cost |
| Creative prototyping | UI designer / Illustrator | "Cyberpunk city, neon lights reflected on rain-soaked streets" | Idea to visual draft in one description |
| Bulk content assets | Content ops / Marketing | "A set of fresh breakfast photos, 6 images, consistent style" | Batch-generate stylistically unified visual assets |
| Style transfer | Photographer / Artist | "Convert this photo to Studio Ghibli animation style" | Natural language-driven style transfer, no editing software needed |

---
