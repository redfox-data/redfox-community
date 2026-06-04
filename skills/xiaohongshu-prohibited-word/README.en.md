# Xiaohongshu Prohibited Word Check / xiaohongshu-prohibited-word

---

## Introduction

Scan your copy for Xiaohongshu (Little Red Book) prohibited terms before publishing, highlight risks, and get compliant replacements plus a ready-to-post revised draft—so you can reduce throttling and takedown risk.

**Core value**

- **Flagged terms**: Hits are shown in bold in the original text so risks stand out.
- **Replacement suggestions**: Each hit comes with a context-aware alternative and a short rationale.
- **Optimized copy**: A publishable version with only the necessary swaps, ready to copy or download as plain text.
- **Long-copy batches**: Content over 3,000 characters triggers a reminder and supports batched checks with merged results.

**Who it’s for**

- 📝 **Creators / bloggers** — Pre-publish self-checks; fewer rewrites and review cycles.
- 🛍️ **Brand & e-commerce ops** — Batch-check campaigns, product pages, and promos before go-live.
- 📣 **Ads & marketing** — Screen multiple selling points and ad lines faster for compliance review.
- 🔍 **Growth & content review** — Spot-check landing pages and H5 page text for policy risk.

---

## Features

### Core capabilities

- **Paste copy**: Send note text directly for prohibited-term detection and edit guidance.
- **Upload documents**: TXT, DOC, and DOCX are read automatically—no manual copy-paste.
- **Upload images**: Text is read from note screenshots or posters, then checked (text only, not visual style).
- **Paste a link**: Provide a URL; page text is read automatically, then checked.
- **Long copy**: Best under 3,000 characters per run; longer content can be checked in batches with a combined optimized file.
- **One-click export**: A plain-text optimized draft file for download and direct use.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is provided by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before sharing a key, confirm its source, scope, validity, and whether it can be reset or revoked.
- Do not hard-code or expose keys in code, prompts, logs, or output files.

---

## How to use

Describe what you need in plain language—no fixed commands to memorize. You can say things like “Xiaohongshu prohibited words,” “note sensitive words,” “throttling terms,” or “compliant seeding copy.”

### Quick phrase guide

| Intent            | Example prompt                                                                | What you get                                    |
| ----------------- | ----------------------------------------------------------------------------- | ----------------------------------------------- |
| Check note copy   | “Check this note for prohibited words: this whitening product works so well…” | Flagged terms, replacements, and optimized copy |
| Check a document  | Upload a TXT, DOC, or DOCX file                                               | Content is read and checked automatically       |
| Check image text  | Upload a note screenshot or poster                                            | Text is extracted from the image, then checked  |
| Check a web page  | “Check this page: https://example.com/article”                                | Page text is read, then checked                 |
| Long copy options | After submitting 3,000+ characters, reply 1 / 2 / 3 per the prompt            | First chunk only, full batch check, or cancel   |

### Sample output

After a check, you receive three sections in order (illustrative):

**🔍 Prohibited word check results**

- Platform: Xiaohongshu
- Count and types of hits
- Original copy with prohibited terms in bold

**💡 Revision suggestions**

| Prohibited term | Replacement | Rationale |
| --------------- | ----------- | --------- |
| …               | …           | …         |

**✏️ Suggested optimized copy**

Full text with only prohibited terms swapped; replacements shown in bold, plus a downloadable plain-text file.

If nothing is flagged, you’ll see: no prohibited words detected—copy looks compliant ✅.

---

## Use cases

| Scenario             | Role                    | Example ask                                          | Benefit                                       |
| -------------------- | ----------------------- | ---------------------------------------------------- | --------------------------------------------- |
| Pre-publish check    | Creator / blogger       | Paste full seeding note and ask for prohibited words | Fix once, publish with more confidence        |
| Batch copy sweep     | Brand / e-commerce ops  | Upload a Word file with multiple promo drafts        | Batch detection; fewer post-launch violations |
| Ad copy screening    | Ads / marketing         | Submit selling points or ad lines one by one         | Faster compliance review and approval         |
| Page compliance spot | Growth / content review | Share a landing or H5 URL to check on-page text      | Quick page audit; lower policy risk           |

---
