# Xiaohongshu (RED) viral title generator / xhs-explosive-content-suite

---

## Introduction

This Skill targets creators and operators who need **higher title CTR and seeding efficiency on Xiaohongshu**: first **fetch** hot note samples by keyword, complete **“viral title analysis,”** then output **10** actionable title options in one go (fixed layout including match score, reference links, and recommendation reasons).

**Core value**

- **Data alignment**: Analysis is grounded in script-fetched samples—no invented engagement or cases.  
- **Analyze before writing**: Must output “viral title analysis” first, then new titles, with traceable patterns.  
- **Batch delivery**: 10 items in a unified layout for comparison and A/B.  

**Who it’s for**

New creators starting accounts, brand and e-commerce operators writing note titles, MCN batch proposals, etc. **Full execution details** are in **`references/core_workflow.md`** in the same directory; this file is a user-facing summary.

**Runtime**: **Python 3**; depends on **`requests>=2.28.0`** (see `SKILL.md` frontmatter). Use natural language in an Agent with this Skill enabled, together with script calls.

---

## Features

### Core capabilities

- **Keyword-driven**: Supports product words, topics, or broad categories; broad categories must go through expansion confirmation first (see usage guide).  
- **Time strategy**: If data is thin, only auto-expand the time window (last 1→3→7→30 days), **do not change the keyword**.  
- **Two-phase output**: Viral title structure analysis → then create 10 new titles (not copying originals).  
- **Fixed delivery shape**: Each item includes match score (8–10, one decimal), reference viral link, recommendation reason, and separator line, consistent with the `core_workflow` checklist.  

### Highlights

- **Clear product boundary**: Product form in user input aligns with the query keyword—do not silently expand to adjacent categories.  
- **Compliant wording**: In user-visible text avoid “crawl/scrape”; use **“fetch”** uniformly; sensitive original titles get neutral summaries.  

---

## Prerequisites

### Dependencies

- **Python**: 3.8+ recommended (per your environment).  
- **Python package**: `requests>=2.28.0` (same as `dependency.python` in `SKILL.md`).  

```bash
pip install "requests>=2.28.0"
```

---

## Usage guide

### How you can phrase it

| What you say | What you’ll roughly get |
| --- | --- |
| “Help me with a few Xiaohongshu titles for sunscreen” | Extract keyword → run script per date rules → read `关键词_爆款数据.md` → analyze first, then 10 titles |
| “Titles for beauty” (broad category) | Niche directions first, **wait** for your “expand” or “don’t expand” before querying |
| “Find inspiration from site-wide hot for titles” | Where workflow allows, empty-keyword overall path, then analysis and generation |

### Command cheat sheet (from skill root)

| Example command | Purpose |
| --- | --- |
| `python scripts/fetch_xhs_trends.py --keyword "防晒霜" --start-date 2026-04-01` | Fetch by keyword and start date; write Markdown report |
| `python scripts/fetch_xhs_trends.py --keyword "a,b,c" --start-date 2026-04-01` | Multiple keywords (comma-separated) |
| `python scripts/fetch_xhs_trends.py --keyword "" --start-date 2026-04-01` | Site-wide hot path with no track keyword (per workflow) |

### Tips

- **Order cannot be swapped**: “Viral title analysis” must come before “generate new viral titles.”  
- **Insufficient data**: Only widen the time window, not the keyword; if still insufficient after up to ~30 days, say so honestly—**no fabricated** titles, engagement, or `photoId` links.  
- **Generic words**: After the assistant gives niche suggestions, **stop and wait** for your “expand / don’t expand” reply—**do not** run a query in the same turn without waiting.  

---

## Use cases

| Scenario | Role | Need | How to use |
| --- | --- | --- | --- |
| New product titles | E-commerce / brand ops | Have selling points but not Xiaohongshu-style titles | Give product words and selling points → fetch data → analyze → 10 options |
| Daily account updates | Blogger / editor | Same vertical lacks topics and title patterns | Enter track or niche term → iterate title library from data patterns |
| Testing a broad vertical | New creator | Only thinks of broad buckets like “beauty,” “outfits” | Generic suggestions → expand or not, then query |
| Site-wide trend chasing | Operator | Wants recent site-wide hot before adapting | Site-wide per workflow → narrow to concrete creation |

---

## Notes and limitations

- **Data**: From the script’s agreed API and stored snapshots—**not live**; engagement and links follow the report—**no fiction**.  
- **Task ownership**: Full flow should run in the **main Agent** so format and order aren’t broken (see `SKILL.md`).  
- **Compliance**: Follow community and advertising norms; reference links must be traceable.  
- **Scope**: Does not replace platform review; you must still verify compliance before publishing.  
