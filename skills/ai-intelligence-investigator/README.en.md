# AI Intelligence Investigator / ai-intelligence-investigator

---

## Overview

A deep intelligence investigation tool powered by 17 search engines. It automatically orchestrates search strategies, cross-validates across multiple sources to eliminate bias, and produces structured investigation reports. Covering four major scenarios—competitive analysis, public opinion monitoring, background investigations, and information verification—it follows three core principles: multi-source verification (key facts confirmed by ≥2 independent sources), engine adaptation (optimal engine selection by investigation goal), and bias elimination (cross-comparison across engines and regions).

**Core Value**

- **Multi-source cross-validation**: Key information confirmed by at least 2 independent sources, eliminating single-source bias.
- **Smart engine orchestration**: Automatically selects the optimal search engine combination based on investigation goals (Chinese sentiment, global perspective, privacy-sensitive, academic verification, etc.).
- **Quantified credibility**: ABCD four-tier source classification + ✅/⚠️/❌/🔍 multi-source verification labels, making information credibility clear at a glance.
- **Structured reports**: Four report templates—competitive analysis, public opinion events, background investigation, and information verification—delivering professional, reusable investigation results.

**Intended Users**

- 🏢 **Brands / enterprise managers** — Competitive intelligence, market trends tracking, partner background checks.
- 📊 **Analysts / researchers** — Multi-source data collection, information cross-validation, structured report generation.
- 📰 **Media / content creators** — Hot event source tracing, public opinion analysis, source verification.
- 🔒 **Legal / risk control** — Personnel background checks, litigation record screening, partnership risk assessment.

---

## Features

### Core Capabilities

- **Competitive intelligence investigation**: Multi-engine search across product features, user feedback, and market performance—outputs SWOT analysis and actionable recommendations.
- **Public opinion investigation**: Event reconstruction + multi-perspective collection + timeline rebuild, presenting a complete opinion landscape.
- **Background investigation**: Identity verification, career history tracing, professional achievement validation, risk signal screening.
- **Information cross-verification**: Source tracing → multi-source comparison → authoritative verification, delivering a confirmed/unconfirmed/refuted final determination.
- **Automatic engine orchestration**: Intelligently matches optimal search engine combinations (up to 17 engines) by investigation goal, eliminating single-engine bias.
- **Credibility grading**: ABCD four-tier source classification, with ✅Confirmed / ⚠️Unconfirmed / ❌Refuted / 🔍Single-source annotation.

### Highlights

- **17-engine breadth**: Baidu, Google, DuckDuckGo, WeChat, Toutiao, Brave, Bing INT and more—flexible combinations by region and purpose.
- **Three-principle driven**: Multi-source must-verify (≥2 independent sources), engine adaptation (smart orchestration by goal), bias elimination (cross-comparison across engines/regions).
- **Four-tier source credibility**: A-tier (official/authoritative media), B-tier (industry media), C-tier (social media), D-tier (anonymous sources)—making credibility quantifiable.
- **Four professional report templates**: Competitive intelligence, public opinion events, background investigation, and information verification—each with standardized output templates for professional, reusable results.

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

Simply describe your investigation needs in natural language—no commands or search engine syntax to memorize.

### Quick Reference

| Intent | Example phrase | Result |
| ------ | -------------- | ------ |
| Competitive investigation | "Investigate Notion's product features and user reviews for me" | 3-round search (broad → deep → cross-validation), structured competitive report |
| Opinion tracking | "Track the public opinion trends on the recent XX incident" | Event reconstruction + multi-perspective collection + timeline rebuild |
| Background check | "Check the background and industry reputation of XX company's founder" | Identity → professional verification → reputation screening |
| Information verification | "Verify whether 'Company XX received 1 billion in funding' is true" | Tracing → multi-source comparison → authoritative verification → final determination |

### Output Example

After investigation, you will receive a credibility-annotated structured report. Taking competitive intelligence as an example:

**Product positioning & overview**: Company name, product positioning, target users, pricing strategy (with source annotations)

**Feature comparison analysis**: Competitor features vs. your own, gap analysis

**User sentiment analysis**: Positive/negative feedback summary, sentiment keyword overview

**Market performance**: Funding rounds/amounts, user scale, market share (with source and A~D credibility ratings)

**SWOT analysis**: Strengths, Weaknesses, Opportunities, Threats

**Key findings & action recommendations**

---

(Every report includes source annotations and credibility ratings; key information must be confirmed by ≥2 independent sources.)

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| -------- | ---- | ---------------- | ------- |
| Competitive product research | Product manager | "Investigate Feishu's AI features and user reviews for me" | Comprehensive understanding of competitor features and sentiment; support product decisions |
| Hot event tracking | Media operator | "Trace the full story of a brand's recent PR incident" | Quickly grasp the complete event picture and opinion distribution |
| Partner due diligence | Business lead | "Check the background of a potential partner's founder" | Pre-cooperation risk screening; avoid pitfalls |
| Funding information verification | Investment analyst | "Verify a company's latest funding round and amount" | Multi-source confirmation of key data; support investment decisions |

---

## Important Data Notes

- Investigation results are based on multi-engine cross-validation; key information is marked "Confirmed" only when verified by at least 2 independent sources.
- Sources are classified into four tiers: A (official/authoritative media), B (industry media/professional platforms), C (social media/self-media), D (anonymous/unverified sources).
- Search results are affected by engine indexing timeliness; for time-sensitive investigations, use time filters (e.g., `tbs=qdr:d`).
- Investigation modes auto-adapt: Chinese sentiment prioritizes Baidu + WeChat + Toutiao; global perspective prioritizes Google + Brave + Yahoo; privacy-sensitive prioritizes DuckDuckGo + Startpage.
- All investigation results come from publicly accessible search engines; no non-public data collection is involved.

---
