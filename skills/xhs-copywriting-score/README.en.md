# Xiaohongshu copy scoring / xhs-copywriting-score

---

## Introduction

This Skill **scores Xiaohongshu note copy**: from your draft, it benchmarks against a large daily corpus of viral notes (the skill cites **2,000+** entries per day), scores four dimensions, and returns actionable fixes—so you can improve structure and reach without guessing.

**Core value**

- **Four dimensions**: keyword coverage, structure completeness, timeliness, content quality—**100** points each; **total = rounded average**.  
- **Data-backed**: scores must use real viral query results—**no** invented benchmarks.  
- **Fair scoring**: strong copy isn’t underscored; **90+** is “excellent” and publish-ready in tone.  
- **Optional polish**: below 90, targeted edits for **low-scoring dimensions only**, keeping your voice.  

**Who it’s for**

Creators and operators who need a quick quality check, gap analysis, or light edits without a full rewrite.

**Runtime**: **Python 3**; install **`requests>=2.28.0`**. Paste your note body or ask for a score in an Agent with this Skill enabled.

---

## Features

### Core capabilities

- **Accept body copy**: extract **1–3** topic keywords to fetch same-niche viral references.  
- **Benchmark in background**: viral patterns inform scoring—you **won’t** see the raw viral data table.  
- **Structured output**: total score and tier, dimension table, fixes or highlights, pattern summary, **2–3** reference notes with links and engagement stats.  
- **Optional optimize**: after you confirm, “how to fix” blocks (original / fix / why) then **optimized copy**.  

### Highlights

- **90 excellent bar**: at excellent tier, congrats and **no** forced “want optimization?” prompt.  
- **Body-only advice**: if you only send body copy, suggestions **don’t** cover title tweaks.  
- **Voice preserved**: no full rewrite; dimensions scored **≥70** stay intact; colloquial / meme language kept when possible.  

---

## Prerequisites

### Runtime and dependencies

- **Python 3** (version per your machine).  
- **`requests>=2.28.0`** (as declared in the skill package).  

---

## Usage guide

### How you can phrase it

| What you say | What you’ll roughly get |
| --- | --- |
| “How’s this copy?” + paste body | Four-dimension scores + breakdown + tips or highlights + references |
| “What’s wrong?” / “Can this go viral?” | Same, emphasis on deductions and fixes |
| Paste note body only | Auto scoring flow |
| “Optimize” / confirm optimization | Fix guide + full optimized body (low dimensions only) |

### Dimension cheat sheet

| Dimension | Focus |
| --- | --- |
| **Keyword coverage** | Domain hot terms present |
| **Structure** | Hook, bullets, value, engagement CTA |
| **Timeliness** | Hot topics / season / holidays |
| **Content quality** | Density, layout, emoji, tags |

### Tips

- Output starts by stating scores use real viral data.  
- If keywords mismatch the draft, keywords are adjusted and rescored.  
- You won’t see script commands, paths, or raw viral tables.  

---

## Use cases

| Scenario | Best for | What you get |
| --- | --- | --- |
| **Pre-publish check** | Solo creator | 90+ bar, missing structure elements |
| **Revision direction** | Operator | 2–3 actionable fixes on weakest dimensions |
| **Learn viral structure** | Beginner | Pattern formula + 2–3 reference notes |
| **Light polish** | Voice-sensitive author | Edits only where score &lt; 70 |

---

## Notes and limitations

- Scores depend on the viral sample fetched; thin samples may skew conservative.  
- **No** raw viral tables; reference notes must come from the query.  
- Optimization: **no** full rewrite; don’t replace your tone with generic AI phrasing.  
- Fix guidance must be concrete, not “consider improving XX.”  
- Follow Xiaohongshu content rules.  

---
