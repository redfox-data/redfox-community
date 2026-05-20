# WeChat Official Account original-article rankings / wechat-original-article-king

---

## Introduction

This Skill targets **WeChat Official Account original-article rankings**: fetch **original hot articles** by category, date, or time range, show the script’s **Markdown table and notes verbatim** in conversation, and auto-generate an **HTML** list page exportable to **PDF**; optional track subscription prompt at the end (whether push is live depends on the product).

**Core value**

- **Script-sourced data**: lists must come from **`fetch_articles.py`**—**no** hand-written or fabricated titles, reads, or links.  
- **Flexible queries**: **overall ranking**, **22+ standard categories**, specific dates; colloquial “recent / latest” defaults to **last ~7 days**.  
- **Top 20 first**: commonly show **20** rows; more rows available on prompt.  
- **HTML + PDF**: WeChat-green layout; **`display_count`** matches rows shown; **html2pdf.js** single-page export.  

**Who it’s for**

WeChat editors and operators, planners, and teams who need **original viral samples** for topics and benchmarking.

**Runtime**: **Python 3** (standard library is enough); data via **`scripts/fetch_articles.py`**, pages via **`scripts/generate_hot_html.py`**. Trigger in natural language in an Agent with this Skill enabled.

---

## Features

### Core capabilities

- **Intent routing**: overall list, category, specific date, or “recent / latest” mapped to script args.  
- **stdout is the deliverable**: data notes, table, count hints, subscription ask must appear **verbatim**—no reformatting or sample data.  
- **Auto HTML**: after each table, generate the list HTML without a separate request.  
- **List only**: **no** viral pattern essays, writing advice, or rewrites.  

### Highlights

- **Clear time semantics**: library syncs **daily at 19:30** for the previous day; fixed apology copy when user dates don’t match queryable range.  
- **Category mapping**: colloquial terms (e.g. “tech”) map to standard names (e.g. “科技数码”).  
- **Sparse niches**: prompts to try another category or wider range when results are thin.  

---

## Prerequisites

### Runtime and dependencies

- **Python 3** (version per your machine; no extra pip deps declared).  
- Colloquial vs standard category names are in-package in **`references/category_mapping.md`** (for the executor; you don’t need to open it).  

---

## Usage guide

### How you can phrase it

| What you say | What you’ll roughly get |
| --- | --- |
| “Latest original viral,” “today’s originals,” “viral picks” | Overall Top 20 table + data note + subscription ask + HTML |
| “Original viral in tech / health / finance…” | Category Top 20 + HTML |
| “Original viral on May 3,” “yesterday’s viral” | Date query + table + HTML |
| “What’s hot lately in originals” | Default ~7-day range Top 20 |

### Tips

- You will **not** see script paths or source code—only results.  
- Even if you only want PDF/HTML, the **full table output** comes first.  
- After load, you may be asked if you want the latest original viral push (accept or skip).  

---

## Use cases

| Scenario | Best for | What you get |
| --- | --- | --- |
| **Daily original topics** | WeChat editor | Latest original hot table + shareable HTML |
| **Vertical benchmarking** | Planner | Top list filtered by category |
| **Day review** | Ops lead | One-day original viral list + PDF |
| **Subscription interest** | Cadence ops | Subscription options at end (product-dependent) |

---

## Important data notes

**Sync and snapshot**

- Data updates on a **daily 19:30** cadence for the prior day; display is a **snapshot at fetch time**, not live reads.  
- Unspecified dates: “recent / latest” means **last 7 days**.  
- Before vs after **19:30**, “latest available date” logic differs (computed by the script).  

**Count hint**

- If a niche returns **fewer than 10** items, output may suggest widening to ~30 days or checking the overall list (per script text).  

---

## Notes and limitations

- This Skill outputs **ranking data only**—no ghostwriting, pattern reports, or ad advice.  
- **No fabricated** authors, titles, reads, or links—script output only.  
- HTML must **match** the table shown; `display_count` aligned with row count.  
- Follow platform rules; links and account info follow script data.  

---
