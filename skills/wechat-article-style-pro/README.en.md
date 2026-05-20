# WeChat Official Account copy rewriting / wechat-article-style-pro

---

## Introduction

This Skill targets **viral-style rewriting for WeChat Official Accounts**: treat your draft as **your own source text** and deliver a finished **title + body** in conversation (not a side comment like “here’s my rewrite for you”), tuned for high-read WeChat tone.

**Core value**

- **Viral voice**: blunt, hook-driven titles (generally **≤20 characters**), colloquial body copy, clear stance, pain points and resonance.  
- **Readable structure**: strong opening, scannable sections, closing engagement prompts, plus **5–10** topic tags.  
- **Keyword blend**: weave in **2–3** common WeChat-style keywords naturally (e.g. guide, tutorial, playbook, experience sharing—see in-package rules).  
- **Light layout**: short paragraphs, a few emojis per section, short sentences.  

**Who it’s for**

WeChat operators, editors, creators, and anyone who needs generic or campaign copy turned into “sounds like a WeChat hit” fast.

**Runtime**: **Python 3**; run **`scripts/rewrite.py`** from the skill root before rewriting (`report` fetches rule reference; `prompt` prints a local summary only). Trigger via natural language in an Agent with this Skill enabled.

---

## Features

### Core capabilities

- **Your input is the source**: output is publish-ready copy, not an edit memo.  
- **Title + body in one shot**: no back-and-forth unless you ask for a new topic.  
- **Rule-driven**: run **`python scripts/rewrite.py report`** first, then apply in-package principles and style notes.  

### Highlights

- **Punchy lines and contrast**: sharp points, contrast, rhetorical questions, parallelism.  
- **Reader-first**: “relevant to me,” “useful to me,” less empty preaching.  
- **Shareable**: core lines easy to remember and repost.  

---

## Prerequisites

### Runtime and dependencies

- **Python 3** (version per your machine; script mainly uses the standard library).  
- Run required commands from the **skill package root** (same level as `scripts/`).  

---

## Usage guide

### How you can phrase it

| What you say | What you’ll roughly get |
| --- | --- |
| “Rewrite this for WeChat style” + paste body | Script run, then new title and full text |
| “WeChat viral title + body about …” | On-topic draft; title within ~20 characters |
| “Sharper / more colloquial” | Stronger tone within viral-style rules |

### Tips

- Provide the **full draft or a clear topic** in one message when possible.  
- Output is written **as the author**, not as editorial suggestions.  
- Check title length, keywords, tags, and emojis against the delivered draft if needed.  

---

## Use cases

| Scenario | Best for | What you get |
| --- | --- | --- |
| **Campaign copy → WeChat tone** | Operator | WeChat-style title and body for the same facts |
| **Outline expansion** | Editor | Hook title and segmented publishable body |
| **Repurpose one draft** | Creator | WeChat viral voice while keeping your meaning |

---

## Notes and limitations

- This Skill is **style rewriting**, not a guarantee of read counts; verify facts and compliance before publishing.  
- Rewriting relies on script-backed rules; do not ask for “purely invented viral patterns” without running the script flow.  
- Do not fabricate data, cases, or quotes; you are responsible for source material.  
- Follow WeChat platform content rules; avoid illicit redirects and exaggerated claims.  

---
