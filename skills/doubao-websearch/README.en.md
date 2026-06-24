# Doubao WebSearch / doubao-websearch

---

## Overview

Doubao WebSearch is an intelligent web search tool. Simply describe what you want to find out in natural language, and it will leverage Doubao's web search capability to deliver the freshest, most comprehensive answers.

**Core Value**

- Ask any question and get structured answers through automated web search
- No manual waiting — results are polled automatically and presented as soon as ready
- Answers include full text and citation sources for easy verification

**Who It's For**

- 🔍 **Information seekers** — Quickly gather real-time insights on any topic
- ✍️ **Content creators** — Find reference material and up-to-date data for writing
- 🎯 **Everyday users** — Ask whatever comes to mind without browsing through web pages

---

## Features

### Core Capabilities

- Natural language queries with intelligent web search for the latest information
- Automatic result polling with real-time progress updates
- Structured answers with source citations
- Friendly guidance for exceptions such as missing API keys, timeouts, etc.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Visit [RedFoxHub](https://redfox.hk?source=github) to register and obtain your `REDFOX_API_KEY`.
- Configure the environment variable `REDFOX_API_KEY` on your device before using this skill.
- Before providing a key, verify its source, scope, expiration, and whether it supports reset/revocation.
- Do not hardcode or expose the key in plain text within code, prompts, logs, or output files.

---

## Usage

Just describe what you need in natural language — no commands to memorize.

### Quick Reference

| Intent | Example Prompt | Result |
|--------|---------------|--------|
| Search for info | "Recommend some Father's Day gifts" | A categorized gift guide by budget and type |
| Discover local spots | "Are there any popular anime bookstores around Chengdu?" | A list of bookstores with addresses and directions |
| Knowledge Q&A | "What are the latest trends in AI agents?" | A structured industry analysis |

### Example Output

After searching "Recommend some Father's Day gifts", you'll receive something like:

> #### Under 100 CNY — Practical & Affordable
> | Gift | Budget | Best For |
> |------|--------|----------|
> | Thermos | 50-100 CNY | Dads who love tea and are often out |
> | Electric shaver | 80-100 CNY | All dads, daily essential |
>
> #### 100-500 CNY — Quality Picks
> ……
>
> When choosing a gift, practicality always comes first. Match it to your dad's habits and hobbies, and you'll find something he truly enjoys!

---

## Use Cases

| Scenario | Role | Example | Benefit |
|----------|------|---------|---------|
| Everyday search | General user | "Best phones of 2026" | Quick tiered comparison |
| Content creation | Blogger / Creator | "What's trending lately?" | Real-time topic inspiration |
| Travel planning | Travel enthusiast | "Things to do around Chengdu" | Guides with addresses and directions |
| Study & research | Student / Researcher | "How does the Transformer architecture work?" | Structured knowledge summaries |
