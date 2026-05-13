# Xiaohongshu (RED) viral radar / xhs-explosive-content-detector

---

## Introduction

This Skill targets **brand seeding, MCN scouting, self-media creation, and content ops**: by track keyword and time window it **fetches** Xiaohongshu viral note samples, supports multi-dimensional filtering and intent-tiered output, and delivers **Markdown** and **HTML** for benchmarking and topic reviews.

**Core value**

- **Scale discovery**: Lowers manual list scraping cost within indexed dimensions (scale and definitions per workflow).  
- **Reduce top-account bias**: Combines dimensions such as low-follower viral, period high likes, single-day spike, sustained growth for better reference value.  
- **Ready to use**: Structured summary + local HTML for internal sharing and further editing.  

**Who it’s for**

Brands, MCNs, creators, and growth teams. Execution rules, dialog branches, and script details must follow **`references/core_workflow.md`**.

**Runtime**: **Python 3.8+**; **`requests>=2.28.0`** (see `SKILL.md`). Data comes from the aggregated API wired in the script; fields and filters follow the workflow and script.

---

## Features

### Core capabilities

- **Multi-dimensional viral filtering**: Combinations such as low-follower viral, period high likes, single-day spike, sustained growth (per workflow).  
- **Track alignment**: Supports about **25** mainstream content categories.  
- **Intent tiers**: Distinguishes casual browse, explicit needs, and data-driven asks; matches output granularity and sort emphasis.  
- **Recommendation reasons**: Explanations combining intent and engagement (per-item length rules in workflow).  

### Highlights

- **Flexible time window**: Last 1 / 3 / 7 / 30 days; if samples are thin, extend per workflow and state clearly.  
- **Dual output**: Markdown cards + local **HTML** (default filename rules in `SKILL.md` and script).  
- **Niche expansion**: After generic keywords, suggest niche directions—**retrieve only after user confirmation**.  

---

## Prerequisites

### Dependencies

- **Python**: 3.8 or newer.  
- **Python package**: `requests>=2.28.0`.  

```bash
pip install "requests>=2.28.0"
```

### Environment variables

| Variable | Required | Notes |
| --- | --- | --- |
| `XHS_API_PROXY` | No | Proxy URL, e.g. `http://127.0.0.1:7890` |
| `OUTPUT_PATH` | No | Directory for generated `.html`; defaults to script CWD |

**macOS (zsh)**

Append to the end of `~/.zshrc` (replace values with yours; omit whole lines for vars you don’t need):

```bash
export XHS_API_PROXY="http://127.0.0.1:7890"
export OUTPUT_PATH="/path/to/output/dir"
```

Then run:

```bash
source ~/.zshrc
```

**Windows (PowerShell)**

- **Current window only**: Takes effect immediately after run; no extra commands; lost when the window closes.

```powershell
$env:XHS_API_PROXY = "http://127.0.0.1:7890"
$env:OUTPUT_PATH = "D:\path\to\output\dir"
```

- **Persist for user**: After `setx`, the **current window will not** see the variable until you **close and reopen** the terminal (or restart the IDE).

```powershell
setx XHS_API_PROXY "http://127.0.0.1:7890"
setx OUTPUT_PATH "D:\path\to\output\dir"
```

---

## Usage guide

### How you can phrase it

| What you say | What you’ll roughly get |
| --- | --- |
| “Low-follower viral in workplace outfits for the last 7 days” | Confirm keyword and date → read workflow → run script → TOP summary and pattern notes, plus HTML path |
| “Check Xiaohongshu viral hits” (incomplete) | Ask for keyword or site-wide, date, and dimensions—don’t assume |
| “Want site-wide hot” | Empty keyword + agreed start date under parameter rules |

### Command cheat sheet (from skill root)

```bash
python scripts/fetch_xhs_trends.py --keyword <关键词> --start-date <日期>
python scripts/fetch_xhs_trends.py --keyword "" --start-date <日期>
python scripts/fetch_xhs_trends.py --keyword "减脂餐,职场穿搭,健身" --start-date <日期>
```

### Tips

- Spoken dates (e.g. “yesterday,” “last week”) must map to script-accepted formats per **`references/core_workflow.md`**.  
- **Missing params, deps, or network failure**: State error type and suggest retry or configuring `XHS_API_PROXY`.  
- **Empty data**: Report honestly—**no fabricated** titles, links, or engagement numbers.  

---

## Use cases

| Scenario | Role | Need | How to use |
| --- | --- | --- | --- |
| Cold-start topics for new accounts | Self-media creator | Need copyable viral samples from peer-level accounts | Keyword + last 7–30 days; prioritize low-follower dimension |
| Brand milestone seeding | Brand Xiaohongshu operator | Need reviewable hot topics and formats before campaigns | Category keyword search; export HTML for internal review |
| Pre-sign screening / incubation | MCN talent scout | Want high-engagement trajectory, not one-off luck | Multiple samples in a fixed window; watch sustained growth, etc. |
| Pitches and weekly reports | Content PM / planner | Client wants “trends + samples” one-pager | Structured summary + HTML; conclusions must match data window |

---

## Important data notes

- **Data truth**: Lists and numbers come from script fetches; on API errors or no data, say so honestly.  
- **Compliance and privacy**: Follow platform community rules and local law; links and excerpts follow de-identification and citation rules in the workflow.  
- **Capability boundary**: Push subscription, PDF export, etc. **only if actually implemented**; default delivery is script + HTML / Markdown (see `references/core_workflow.md`).  

---

## Notes and limitations

- **Executor**: Full flow should run in the **main Agent** to avoid duplicate requests or bypassing unified checks from sub-agents.  
- **No fabrication**: Do not invent engagement, ranks, or note metadata outside script results.  
- **Proxy and output dir**: If the network is restricted, set `XHS_API_PROXY`; for a fixed HTML directory, set `OUTPUT_PATH`.  
