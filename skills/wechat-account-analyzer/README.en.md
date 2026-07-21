# WeChat Account Diagnostics / wechat-account-analyzer

---

## Introduction

Perform a four-dimension quantitative scoring on any WeChat Official Account, benchmark it against industry averages, and receive actionable optimization suggestions — so your operations are driven by data, not guesswork.

**Core Value**

- **Four-dimension quantitative diagnosis**: Content health, user engagement, core data performance, and operational compliance — each scored on a 100-point scale, giving you a complete picture in one go
- **Industry benchmarking**: Anchored to the RedFox index, automatically matches peer accounts in the same vertical for side-by-side comparison
- **Tiered optimization suggestions**: Urgent / Key / Ongoing three-level prioritization, with each suggestion including an expected quantitative outcome — ready to act on immediately
- **Multi-account comparison**: Diagnose multiple accounts simultaneously and generate a side-by-side comparison report

**Target Users**

- 📱 **Account owners / Content creators** — Identify weaknesses in a single diagnosis and quantify improvement directions
- 📊 **New-media operators / Brand teams** — Drive content strategy with data instead of experience-based guesswork
- 🏢 **MCN agencies** — Batch-evaluate in-house or prospective accounts to assess commercial value

---

## Features

### Core Capabilities

- **Four-dimension scoring**: Content health + User engagement + Core data + Operational compliance, producing an overall 100-point score and S/A/B/C/D/E six-tier rating
- **Recent content data summary**: A table of the last 7 days' reads, likes, comments, and "Top Reads" figures for each article
- **Tiered optimization suggestions**: Urgent / Key / Ongoing priority levels with quantified expected outcomes per suggestion
- **Peer account matching**: Automatically matches similar accounts in the same vertical for gap analysis and growth path reference
- **Multi-account comparison**: Supports multiple accounts in one request, generating parallel diagnostic reports with a cross-account summary

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain your `REDFOX_API_KEY`.
- Set `REDFOX_API_KEY` as a device environment variable before using this skill.
- Before sharing your key, confirm its source, scope, expiry, and whether it supports reset/revocation.
- Never hard-code or expose the key in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your request in natural language — no commands to memorize.

### Quick Phrase Reference

| Intent                   | Example phrase                                  | Result                                                                                |
| ------------------------ | ----------------------------------------------- | ------------------------------------------------------------------------------------- |
| Single account diagnosis | "Diagnose the WeChat account 'Shi Dian Du Shu'" | Full five-section diagnostic report with scores, suggestions, and benchmarks          |
| Multi-account comparison | "Compare 'Shi Dian Du Shu' and 'Dongjian'"      | Individual reports plus a cross-account summary table with differentiated suggestions |
| Query by account ID      | "Diagnose the account with ID 'gh_xxxxxxxx'"    | Accurate lookup by official account ID to avoid name ambiguity                        |
| Self-check               | "Show me how this account is performing"        | Diagnostic report with industry benchmark and prioritized optimization areas          |

### Output Example

After diagnosis you will receive a fixed five-section report:

**I. Account Info** — Account name (clickable), bio, follower count, and other basic details

**II. Overall Score** — Four-dimension scores + overall rating (S/A/B/C/D/E) + industry benchmark comparison

**III. Last 7 Days' Content Data** — Article titles (clickable), reads / likes / comments / Top Reads data table

**IV. Optimization Suggestions** — Urgent / Key / Ongoing three-tier suggestions, each with expected quantitative outcomes

**V. Industry Benchmark Analysis** — Automatically matched peer accounts in the same vertical for side-by-side gap analysis

---

## Use Cases

| Scenario                  | Role               | Example request                                               | Benefit                                                                              |
| ------------------------- | ------------------ | ------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Self-check & optimization | Account operator   | "Diagnose my account and find its weak spots"                 | Understand account health, quantify improvement directions, avoid blind operation    |
| Competitor benchmarking   | New-media operator | "Analyze account 'XX', check its data performance"            | Understand competitor tactics, draw on successful patterns, refine your own strategy |
| MCN batch evaluation      | MCN agency         | "Compare account A and account B"                             | Data-driven signing decisions, quantified commercial value                           |
| Content strategy planning | Content planner    | "Based on the diagnosis, what should I adjust in my content?" | Evidence-based content planning, improved overall operational efficiency             |

---

> 💼 RedFox's comprehensive database provides complete and detailed data. For procurement inquiries, visit RedFoxHub [Enterprise Services](https://redfox.hk/dashboard/enterprise) for consultation.
