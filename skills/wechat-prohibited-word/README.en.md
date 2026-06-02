# WeChat Prohibited Word Checker / wechat-prohibited-word

---

## Introduction

Scan WeChat Official Account copy, files, or web pages for prohibited and sensitive wording, highlight risks, and get compliant replacement suggestions—helping you pass review safely and avoid takedowns or traffic limits.

**Core Value**

- **Fast scanning**: Powered by an official prohibited-word library covering 10+ categories including advertising law, medical aesthetics, and financial risk; hits are **bolded** in the original text.
- **Smart replacements**: Context-aware alternative phrasing and rationale for each hit—not mechanical synonym swaps.
- **Ready-to-publish copy**: A full compliant version with replacements **bolded**; copy and publish as-is.
- **Easy archiving**: Auto-generated plain-text optimized copy files for team collaboration and records.

**Who It's For**

- 📱 **WeChat operators** — Pre-publish self-checks to reduce takedowns, traffic limits, and account risks.
- ✍️ **New media editors** — Batch compliance review for multiple short pieces, faster editorial workflow.
- 🏢 **Brand / marketing teams** — Spot-check campaign landing pages and H5 copy before launch.
- 🎨 **Designers** — Catch marketing copy risks in posters and tweet screenshots early in the design phase.

---

## Features

### Core Capabilities

- **Prohibited-word scanning**: Synced with the official library in real time—covers superlatives under advertising law, banned medical/beauty claims, financial return promises, exaggerated education/training claims, and 10+ other categories.
- **Risk highlighting**: Hits are **bolded** in the source text, with a summary of word types and counts.
- **Smart replacements**: Context-aware alternative phrasing for each hit, with rationale.
- **Optimized copy generation**: Full compliant version with replacements **bolded**, preserving tone and style.

### Highlights

- **Multiple input methods**: Paste copy directly, upload TXT/DOC/DOCX files, upload images for automatic text extraction, or paste a web page URL.
- **Long-copy batch detection**: Alerts when content exceeds 3,000 characters; supports splitting at natural sentence breaks with merged results.
- **English false-match filtering**: Built-in English word recognition—substrings inside normal English words are not flagged incorrectly.
- **Data privacy**: Copy is sent to the detection service over an encrypted connection and is not stored locally.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?souce=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?souce=github) to obtain your `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing a key, confirm its source, scope, validity period, and whether reset/revocation is supported.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Describe what you need in plain language—no fixed commands to memorize. The platform is fixed to WeChat Official Accounts; no manual platform selection is required.

### Quick Phrase Reference

| Intent              | Example prompt                                                                                                      | Outcome                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| Paste copy to check | "Check this draft for prohibited words: This whitening miracle really works—you'll see results in three days"     | Hit highlights, replacement table, and optimized copy |
| Upload a file       | Upload a TXT, DOC, or DOCX file and ask for WeChat prohibited-word detection                                       | File content is read and checked automatically       |
| Upload an image     | Upload a poster or tweet screenshot and ask to check the text in the image                                         | Text is extracted from the image and checked         |
| Paste a web URL     | Provide a campaign or article URL and ask to check the page copy                                                     | Page body is fetched and checked automatically       |
| Batch pre-review    | Upload a file combining multiple short pieces and ask for a unified compliance check                               | All content is checked in batches with merged output |

### Sample Output

After detection, you receive three sections (illustrative):

**🔍 Prohibited Word Detection Results**

- ☁️**Platform**: WeChat Official Account
- **Prohibited word count**: 2
- **Word types**: Banned terms

📚 **Flagged copy:**
This whitening miracle really **works**—you'll see results in three **days**

**💡 Revision Suggestions**

| Prohibited word | Replacement              | Rationale                                                                 |
| --------------- | ------------------------ | ------------------------------------------------------------------------- |
| works           | feels quite nice to use  | "Works" is a banned term; rephrased as a conversational usage experience  |
| days            | skin tone looks brighter | Implies whitening efficacy; rephrased as an indirect visual description   |

**✏️ Suggested Optimized Copy**

This whitening miracle really **feels quite nice to use**—you'll see **skin tone looks brighter** in three days

(A downloadable plain-text optimized copy file is also generated for easy publishing and archiving.)

---

## Use Cases

| Scenario                        | Role                 | Example question                                                          | Benefit                                                          |
| ------------------------------- | -------------------- | ------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Pre-publish tweet self-check    | WeChat operator      | "Does this post contain superlatives or banned promotional language?"     | Catch compliance risks early; lower takedown risk                  |
| Batch pre-review of short copy  | New media editor     | "Run a prohibited-word check on these short pieces together"              | Check multiple pieces at once; faster editorial workflow         |
| Campaign landing page spot-check| Brand / marketing    | "Does the copy on this H5 campaign page have compliance risks?"         | Avoid reports or takedowns due to prohibited wording             |
| Poster text compliance check    | Designer             | "Do these marketing lines on the poster violate advertising law?"         | Eliminate text risks during design; reduce rework                  |

---
