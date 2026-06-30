# Deepseek Web Search / deepseek-websearch

---

## Overview

Deepseek WebSearch is an intelligent search tool with internet access. Simply describe the topic you want to explore in natural language, and it will leverage Deepseek's online capabilities to deliver the latest and most comprehensive answers.

**Core Value**

- **Real-time web search**: Break through the knowledge cutoff limitation of large models and access the latest information.
- **Automatic async processing**: Submit and receive a taskId instantly; the script polls automatically—no manual intervention required.
- **Structured result output**: Returns JSON format with answer text and source citations, easy for Agent parsing and display.

**Intended Users**

- 🔍 **Researchers / Students** — Quickly retrieve the latest academic advances and professional resources.
- 📰 **Content creators / Operators** — Track trending topics and gather creative material.
- 💻 **Developers / Tech leads** — Technical research, solution comparison, and documentation lookup.

---

## Features

### Core Capabilities

- **Async submission**: Submit search keywords and immediately receive a task ID without blocking.
- **Automatic polling**: Queries task status every 5 seconds, up to 5 minutes; outputs automatically when results are ready.
- **Real-time progress feedback**: During polling, outputs current status via stderr (queued → running → succeeded) for clear progress visibility.
- **Comprehensive error handling**: Clear prompts and handling for four exception scenarios: missing API Key, submission failure, timeout, and task failure.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`)
- Register at [RedFoxHub](https://redfox.hk?souce=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your search need in natural language—no fixed commands to memorize.

### Quick Reference

| Intent | Example phrase | Result |
|--------|---------------|--------|
| Real-time info query | "Search for today's tech news" | Calls Deepseek web search to retrieve the latest news |
| Professional knowledge lookup | "Look up the latest advances in quantum computing" | Searches and organizes the latest research in the field |
| Fact verification | "Verify whether this claim is accurate" | Cross-references via web search to confirm accuracy |
| Tech solution research | "Compare the latest features of React and Vue" | Retrieves documentation and community feedback to aid decisions |

### Output Example

After the search completes, you receive structured results including:

- **Deepseek answer text**: A detailed response to your query
- **Source citations**: Webpage links referenced in the search results for further reading

---

## Use Cases

| Scenario | Role | Example question | Benefit |
|----------|------|-----------------|---------|
| Academic research | Researcher / Student | "Search for the latest LLM papers" | Quickly access cutting-edge research and improve efficiency |
| Trending topic tracking | Creator / Operator | "Search for the latest AI hot topics" | Stay on top of industry trends and produce timely content |
| Tech solution research | Software engineer | "Compare the pros and cons of several database solutions" | Access the latest documentation and reduce selection risk |
| Fact-checking | Journalist / Content reviewer | "Verify the authenticity of this news" | Cross-verify from multiple sources to ensure accuracy |

---
