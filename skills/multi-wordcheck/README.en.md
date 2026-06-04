# Multi-Platform Prohibited Word Check / multi-wordcheck

---

## Introduction

A multi-platform prohibited word detection tool based on official word libraries, covering the moderation standards of WeChat Official Accounts, Xiaohongshu, and Douyin. Supports copy text, file uploads, images, and URL links as input, and outputs flagged words alongside context-aware replacement suggestions.

**Core Value**

- Three independent word libraries for three platforms — switch with a single phrase before publishing
- Goes beyond flagging: each prohibited word comes with a context-aware replacement and reason, ready to use
- Automatically generates a clean, publishable version of your copy with replacements applied — just copy and post

**Who It's For**

- ✍️ Independent creators — self-audit before publishing to reduce the risk of platform throttling or rejection
- 📢 Brand marketers / e-commerce teams — batch-check campaign copy and product detail pages to a unified compliance standard
- 🏢 MCN agencies / content review teams — standardize compliance workflows across multi-person operations

---

## Features

### Core Capabilities

- **Prohibited word flagging**: Detected words are bolded in the original text; total count and type are clearly listed
- **Context-aware replacement suggestions**: Each prohibited word gets a context-fitted replacement and reason — not a mechanical keyword swap
- **Publishable output**: Automatically generates a full replacement version of the copy with replaced terms in bold-italic, ready to copy and use
- **Multi-platform switching**: Public Accounts (default), Xiaohongshu, Douyin — three independent word libraries; just mention the platform name to switch
- **Multiple input formats**: Paste text directly, upload txt files, upload images (text extracted automatically), or paste a URL (page body extracted automatically)
- **Long-copy batch detection**: Copy over 3,000 characters prompts a batching option; supports batch detection with merged results

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before using a key, confirm its source, scope, expiry, and whether it supports reset or revocation.
- Never hard-code or expose the key in plaintext within code, prompts, logs, or output files.

---

## Usage Guide

Describe your needs in natural language — no commands to memorize.

### Quick Reference

| Intent                | Example phrase                                                  | Result                                                                                   |
| --------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Check WeChat copy     | `Check this WeChat article for prohibited words: [copy]`        | Detects against WeChat rules, outputs flagged results and replacement suggestions        |
| Switch to Xiaohongshu | `Check this Xiaohongshu post for prohibited words: [copy]`      | Switches to Xiaohongshu word library for detection                                       |
| Switch to Douyin      | `Check this Douyin script for prohibited words: [script]`       | Switches to Douyin word library for detection                                            |
| Upload file           | Directly upload a txt file or image                             | Content is read and detected automatically — no extra steps needed                       |
| Check a URL           | `Check the copy on this page: https://...`                      | Page body is extracted and checked automatically                                         |
| Long copy batching    | System automatically prompts when copy exceeds 3,000 characters | Reply `1` for first 3,000 chars / `2` for auto-batch with merged results / `3` to cancel |

### Output Example

When prohibited words are detected, results are output in three sections:

1. **Detection Results** — original text with prohibited words bolded, plus word count and type
2. **Replacement Suggestions** — table of prohibited word / replacement / reason
3. **Suggested Clean Copy** — full publishable version with replacements in bold-italic

When no prohibited words are detected, only the result section is shown: "No prohibited words detected. Copy is compliant."

---

## Use Cases

| Scenario                       | Role                   | Example question                                   | Benefit                                                                                                    |
| ------------------------------ | ---------------------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Pre-publish self-audit         | WeChat operator        | `Check this article before I send it out`          | Catch advertising law violations and false claims before mass send, reducing rejection or throttling risk  |
| Xiaohongshu post compliance    | Xiaohongshu creator    | `Xiaohongshu check: [post content]`                | Flag extreme claims and community-banned phrases, get replacement suggestions tuned to the seeding context |
| Short video script review      | Douyin editor          | `Douyin script check: [script]`                    | Screen sensitive terms and non-compliant phrasing to ensure the final video passes platform review         |
| Marketing material batch audit | Brand / e-commerce ops | `Check the copy on this landing page: https://...` | Quickly audit multiple pages for compliance and receive a unified-format detection report                  |
