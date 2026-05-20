# WeChat Official Account 100k+ Hot Article Recommendations / wechat-10w-hot

---

## Introduction

This Skill targets **WeChat Official Account articles with 100k+ reads**: it pulls ranked lists by **standard category** and time window, delivers a full **Markdown ranking** in conversation (data notes → overview table → per-item details → statistics), and generates **HTML** for **PDF** export; after pattern analysis it may guide **track subscription** (whether push is live depends on the product).

**Core value**

- **Overall ranking / by track**: Covers **23** standard categories plus **overall ranking**; commonly **TOP50** candidates, first turn often **preview** of **10** rows, then **full** on request.  
- **Data honesty**: Ranking body must come from **`fetch_hot_articles.py` stdout**—**no fabricated** articles or read counts.  
- **HTML + PDF**: WeChat-green visual style; **`--display_count`** matches rows shown in conversation; browser **html2pdf.js** export supported.  
- **Pattern review**: After the list is shown, analysis based on **real rows this run**, then optional track subscription prompt.  

**Who it’s for**

WeChat editors and operators, content leads, growth and business roles who need verifiable, shareable, printable 100k+ samples.

**Runtime**: **Python 3**; list fetch via **`scripts/fetch_hot_articles.py`** (standard-library networking); HTML via **`scripts/generate_hot_html.py`**. Trigger in natural language in an Agent with this Skill enabled.

---

## Features

### Core capabilities

- **List fetch**: `scripts/fetch_hot_articles.py` → writes **`temp_articles.json`** → **verbatim** stdout in conversation.  
- **Category and time**: Map user wording to standard **`--type`** (see **`references/category-mapping.md`**); compute **`--start_date` / `--end_date`** with **daily 18:30** sync and current clock (see **`references/time-and-date-rules.md`**).  
- **Preview vs full**: Default **`--mode preview`**, **`--limit 10`**; on “show all / 50 rows,” use **`--mode full`** and align HTML row count.  
- **Fixed cadence**: Intent → run script → pattern analysis → subscription ask → **generate HTML immediately** (do **not** wait for subscription reply) → subscription branch on next user message (see **`references/agent-workflow.md`**).  

### Highlights

- **Script output is the body**: Overview, detail blocks, and stats **must not** be reordered or dropped.  
- **18:30 cutoff**: Before vs after **18:30**, “latest available date” differs; when user “today/yesterday” ≠ actual query range, use **fixed apology copy** from **`references/time-and-date-rules.md`**.  
- **No padding**: Show fewer than 10 honestly; on empty data, suggest overall list or another category per references—**no fake** rows.  

---

## Prerequisites

### Runtime and dependencies

- **Python 3** (version per your machine; `SKILL.md` lists no extra pip deps).  
- **Suggested reading before execution** (as needed):  
  - **`references/agent-workflow.md`** — six-step flow, subscription, checklist  
  - **`references/time-and-date-rules.md`** — 18:30 / 19:30, ranges, fixed wording  
  - **`references/script-parameters-and-output.md`** — CLI, stdout layout, four-dimension analysis  
  - **`references/html-pdf-visual-spec.md`** — HTML / PDF style and commands  
  - **`references/usage-examples.md`** — overall / category / full / empty examples  
  - **`references/api-spec.md`**, **`references/category-mapping.md`** — API fields and category map  

---

## Usage guide

### How you can phrase it

| What you say | What you’ll roughly get |
| --- | --- |
| “Today’s viral hits,” “100k+ articles,” “latest viral list” | Overall intent + date range per time rules + script (often preview 10) |
| “100k+ in tech / finance / health…” | Map to standard **`--type`** + date range + script |
| “What’s hot lately / recently” | Default **last ~7 days** range (see time rules doc) |
| “Show all / 50 rows” | Same range, **`--mode full`**; HTML **`--display_count`** aligned |

### Tips

- Any ranking text **must run the script first**; do not replace stdout with hand-written content.  
- If the user only wants HTML, still **show full stdout** before generating HTML.  
- Dates, parameter tables, and output templates: **`references/`** is the single source of truth, together with **`SKILL.md`** “core execution rules.”  

---

## Use cases

| Scenario | Best for | What you get |
| --- | --- | --- |
| **Track site-wide trends** | WeChat editor | Overall-ranking 100k+ samples, pattern notes, shareable HTML |
| **Vertical topics** | Content planner | High-read articles by standard category and structured details |
| **Internal / client decks** | Content lead | Layout matching conversation + PDF-exportable page |
| **Subscription interest** | Operator | Subscription prompt after analysis; real push depends on product |

---

## Important data notes

**Sync and snapshot**

- Library syncs **daily at 18:30** for the previous day; outward copy often cites **19:30** (see script “data notes” block).  
- Display is a **snapshot at fetch time**, not live reads.  
- “Recent / latest” with no explicit date: default **last 7 days** range.  

**Time mismatch (verbatim copy)**

When user-requested time ≠ **actual queried dates**, append the matching fixed line from **`references/time-and-date-rules.md`** after “data notes” (e.g. today’s data not updated yet, yesterday not ready, max ~30-day lookback, etc.).

**Script date keywords (helper)**

`fetch_hot_articles.py` parses **`yesterday`**, **`daybeforeyesterday`**, `today`, `YYYY-MM-DD`, etc. The **Agent must still** compute **`--start_date` / `--end_date`** per 18:30 rules and range tables—not from colloquial dates alone.

---

## Notes and limitations

- This Skill is **data and layout reference**—not advice to inflate reads or break platform rules.  
- **Do not** give sample lists without running the script; **do not** show only the overview table.  
- **Pattern analysis** only after the full list is shown, and only from **this run’s script data**.  
- **HTML**: `generate_hot_html.py` **`--display_count`** must equal rows shown in conversation.  
- Artifacts such as **`temp_articles.json`** and HTML paths depend on runtime—back up if needed.  

---

## FAQ

**Q: Can I skip the script and give a few example articles?**  
A: **No.** Without script stdout, the Skill was not executed properly.

**Q: User only wants HTML, not the long text?**  
A: Still **show full stdout** first, then generate HTML.

**Q: `temp_articles.json` has 50 rows but conversation showed 10—how many in HTML?**  
A: **10**; `--display_count` follows **what was actually shown**.

**Q: Which API URL is authoritative?**  
A: **`references/api-spec.md`** and constants in `fetch_hot_articles.py`; if they differ, follow the script and fix docs.

**Q: What if there’s no data?**  
A: Report honestly per script and references; suggest another category or range—**no fabricated** articles.

---
