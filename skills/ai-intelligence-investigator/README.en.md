# A-Share Intelligence Investigator / ai-intelligence-investigator

---

## Overview

A deep A-share intelligence investigation tool powered by 17 search engines. It automatically orchestrates search strategies, cross-validates across multiple sources to eliminate bias, and produces structured investigation reports. Covering five major scenarios—A-share intelligence, competitive analysis, public opinion monitoring, background investigations, and information verification—it follows three core principles: multi-source verification (key facts confirmed by ≥2 independent sources), engine adaptation (optimal engine selection by investigation goal), and bias elimination (cross-comparison across engines and regions).

**Core Value**

- **A-share intelligence investigation**: Covers listed company fundamentals, financials, industry landscape, concept heat, fund flows, announcements, research reports, and investor community sentiment—comprehensive intelligence for the A-share market.
- **Multi-source cross-validation**: Key information confirmed by at least 2 independent sources, eliminating single-source bias.
- **Smart engine orchestration**: Automatically selects the optimal search engine combination based on investigation goals (A-share intelligence, Chinese sentiment, global perspective, privacy-sensitive, academic verification, etc.).
- **Quantified credibility**: ABCD four-tier source classification + ✅/⚠️/❌/🔍 multi-source verification labels, making information credibility clear at a glance.
- **Structured reports**: Five report templates—A-share intelligence, competitive analysis, public opinion events, background investigation, and information verification—delivering professional, reusable investigation results.

**Intended Users**

- 📈 **A-share investors / retail traders** — Listed company fundamental research, industry analysis, concept trend tracking, institutional opinion aggregation.
- 🏢 **Brands / enterprise managers** — Competitive intelligence, market trends tracking, partner background checks.
- 📊 **Analysts / researchers** — Multi-source data collection, information cross-validation, structured report generation.
- 📰 **Media / content creators** — Hot event source tracing, public opinion analysis, source verification.
- 🔒 **Legal / risk control** — Personnel background checks, litigation record screening, partnership risk assessment.

---

## Features

### Core Capabilities

- **A-share intelligence investigation**: Multi-engine search across listed company financials, announcements, research reports, industry policies, fund flows, and investor community sentiment—supporting investment decision-making.
- **Competitive intelligence investigation**: Multi-engine search across product features, user feedback, and market performance—outputs SWOT analysis and actionable recommendations.
- **Public opinion investigation**: Event reconstruction + multi-perspective collection + timeline rebuild, presenting a complete opinion landscape.
- **Background investigation**: Identity verification, career history tracing, professional achievement validation, risk signal screening.
- **Information cross-verification**: Source tracing → multi-source comparison → authoritative verification, delivering a confirmed/unconfirmed/refuted final determination.
- **Automatic engine orchestration**: Intelligently matches optimal search engine combinations (up to 17 engines) by investigation goal, eliminating single-engine bias.
- **Credibility grading**: ABCD four-tier source classification, with ✅Confirmed / ⚠️Unconfirmed / ❌Refuted / 🔍Single-source annotation.

### Highlights

- **17+ engine breadth**: Baidu, Google, East Money, Tonghuashun, Xueqiu, CNINFO, Sina Finance, Securities Times, DuckDuckGo, WeChat, Toutiao, Brave, Bing INT and more—flexible combinations by region and purpose.
- **A-share specialized engines**: East Money (quotes + financials + Guba community), Tonghuashun (concepts + themes + AI Q&A), Xueqiu (investor community + KOL views), CNINFO (official announcements), Sina Finance (event-driven + sentiment monitoring), Securities Times (policy interpretation + investigative reporting).
- **Three-principle driven**: Multi-source must-verify (≥2 independent sources), engine adaptation (smart orchestration by goal), bias elimination (cross-comparison across engines/regions).
- **Four-tier source credibility**: A-tier (official/exchange/authoritative media), B-tier (financial platforms/industry media), C-tier (investor community/social media), D-tier (anonymous sources)—making credibility quantifiable.
- **Five professional report templates**: A-share intelligence, competitive intelligence, public opinion events, background investigation, and information verification—each with standardized output templates for professional, reusable results.

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
| A-share intelligence | "Investigate CATL's fundamentals and industry outlook for me" | 3-round search (fundamental scan → deep dive → cross-validation), structured A-share report |
| Competitive investigation | "Investigate Notion's product features and user reviews for me" | 3-round search (broad → deep → cross-validation), structured competitive report |
| Opinion tracking | "Track the public opinion trends on the recent XX incident" | Event reconstruction + multi-perspective collection + timeline rebuild |
| Background check | "Check the background and industry reputation of XX company's founder" | Identity → professional verification → reputation screening |
| Information verification | "Verify whether 'Company XX received 1 billion in funding' is true" | Tracing → multi-source comparison → authoritative verification → final determination |

### Output Example

After investigation, you will receive a credibility-annotated structured report. Taking A-share intelligence as an example:

**Company overview**: Full name, main business, board classification, market cap, P/E ratio (with source annotations)

**Financial performance**: Revenue, net profit, gross margin, ROE and other core metrics (with source and YoY comparison)

**Industry landscape analysis**: Market size, competitive dynamics, company positioning, policy environment, industry cycle assessment

**Concepts & themes**: Related concept heat, institutional opinion aggregation and target price range

**Fund flows**: Major capital net inflow, Northbound capital holdings, margin balance, block trades

**Sentiment monitoring**: Bull/bear views from Xueqiu/Guba, key recent announcements and impact assessment

**Risk alerts & comprehensive evaluation**

---

(Every report includes source annotations and credibility ratings; key information must be confirmed by ≥2 independent sources.)

---

## Use Cases

| Scenario | Role | Example question | Benefit |
| -------- | ---- | ---------------- | ------- |
| A-share company research | Individual investor | "Investigate Moutai's latest financials and institutional ratings for me" | Multi-dimensional understanding of listed companies to support investment decisions |
| A-share industry analysis | Industry researcher | "Analyze the competitive landscape and policy environment of the photovoltaic industry" | Quickly grasp industry overview to support research |
| Competitive product research | Product manager | "Investigate Feishu's AI features and user reviews for me" | Comprehensive understanding of competitor features and sentiment; support product decisions |
| Hot event tracking | Media operator | "Trace the full story of a brand's recent PR incident" | Quickly grasp the complete event picture and opinion distribution |
| Partner due diligence | Business lead | "Check the background of a potential partner's founder" | Pre-cooperation risk screening; avoid pitfalls |
| Funding information verification | Investment analyst | "Verify a company's latest funding round and amount" | Multi-source confirmation of key data; support investment decisions |

---

## Important Data Notes

- Investigation results are based on multi-engine cross-validation; key information is marked "Confirmed" only when verified by at least 2 independent sources.
- Sources are classified into four tiers: A (official/exchange/authoritative media), B (financial platforms/industry media), C (investor community/social media), D (anonymous/unverified sources).
- For A-share investigations: CNINFO (cninfo.com.cn), SSE (sse.com.cn), SZSE (szse.cn) are A-tier sources; East Money, Tonghuashun, Securities Times are B-tier sources; Xueqiu, Guba are C-tier sources.
- Search results are affected by engine indexing timeliness; for time-sensitive investigations, use time filters (e.g., `tbs=qdr:d`).
- Investigation modes auto-adapt: A-share intelligence prioritizes Baidu + East Money + Xueqiu + CNINFO; Chinese sentiment prioritizes Baidu + WeChat + Toutiao; global perspective prioritizes Google + Brave + Yahoo.
- All investigation results come from publicly accessible search engines; no non-public data collection is involved.
- **Disclaimer**: A-share investigation reports are based on publicly available information, for reference only, and do not constitute any investment advice. Stock markets involve risk—invest with caution.

---
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
