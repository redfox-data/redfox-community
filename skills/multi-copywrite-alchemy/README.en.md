# Distillation Writing / multi-copywrite-alchemy

---

## Overview

Analyze an author's articles, deeply reconstruct their thinking patterns and writing style, and generate a dedicated writing persona—highly consistent from thought logic to written expression.

**Core Value**

- **Full-chain style replication**: Not just mimicking vocabulary and sentence patterns, but reproducing how the author thinks and expresses—so the persona writes articles that only "that person" could write.
- **Multi-platform material access**: Supports automatic article collection from WeChat Official Accounts and Douyin; also accepts pasted text or file paths for flexible material sourcing.
- **Ready-to-use persona**: Two deliverables upon completion—a plug-and-play style prompt, and an installable local persona sub-skill.

**Intended Users**

- ✍️ **Content creators** — Admire a certain author's expression and want to acquire the same writing ability
- 📊 **Operators** — Need to consistently produce content in a unified style
- 🔍 **Style researchers** — Want to deconstruct why a certain author's writing has high distinctiveness

---

## Features

### Core Capabilities

- **Deep style reconstruction**: Not only analyzes expression habits but also extracts thinking logic—generates a persona loyal to the original author from ideas to words
- **Flexible writing modes**: The persona supports multiple writing frameworks, adapting to different article types while maintaining style
- **Quality assurance**: Automatically verifies style consistency and content accuracy before output, ensuring stable quality
- **Multi-platform material collection**: Supports automatic article retrieval from WeChat Official Accounts and Douyin; also accepts manual paste or file paths

### Highlights

- **Full-chain from thinking to writing**: Not templated keyword replacement, but understanding the author's thought process before creating—switch topics or approaches, and it still reads like that person
- **Bespoke, not generic**: Generic "de-AI" tools make articles sound like anyone; this skill makes articles sound like **that person**

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your needs in natural language—no commands to memorize.

### Quick Reference

| Intent | Example | Result |
|------|---------|------|
| Platform collection distillation | "Distill 10 articles from WeChat OA XXX for me" | Auto-collects materials, analyzes, and generates persona |
| Manual paste distillation | "Analyze the writing style of these articles" (paste text) | Directly analyzes provided text |
| Use persona to write | "Write an article about YY in XX's style" | Invokes persona, writes in that author's style |
| Update persona | "XX has new articles, update the persona" | Incrementally analyzes new articles, updates persona |

### Output Example

Upon completion, you will receive:

- **Thinking + Writing Style Prompt**: Ready to copy into any AI conversation, covering the author's thinking patterns and writing rules.
- **Writing Persona Sub-skill**: Installed locally, invocable anytime via `@author-name-style`, with support for specifying writing modes.

---

## Use Cases

| Scenario | Role | Example Question | Benefit |
|------|------|---------|------|
| Replicate a favorite author | Content creator | "Distill XX's writing style—I want to write articles like theirs" | Get a dedicated writing persona, available anytime |
| Batch produce same-style content | Operator | "Create a writing persona for me to batch produce same-style articles" | Unified style, efficient output |
| Deconstruct article distinctiveness | Researcher | "Analyze why XX's articles read with such high distinctiveness" | Receive a multi-dimensional style analysis report |
| Cross-platform material integration | Brand | "Collect XX's articles from both WeChat OA and Douyin for a complete persona" | Cross-platform merging, more comprehensive persona |

---
