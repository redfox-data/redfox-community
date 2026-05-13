# WeChat Official Account 100k+ Hot Article Recommendations / wechat-10w-hot

---

## Introduction

This Skill targets **site-wide trending scans for WeChat Official Accounts, vertical 100k+ viral topic picks, and steady cadence references for operations**: it pulls ranked lists of **100k+ read** articles from the data source, returns a structured overview and per-item details in conversation, and can generate **HTML** in a WeChat Official Account style for browser export to **PDF** (single-page layout and no forced pagination follow the execution notes).

**Core value**

- **Overall ranking / vertical**: Supports site-wide hot lists (empty keyword) and domain-keyword queries; the backend commonly fetches **TOP50**, while the first turn may only preview the first **10** items, with full text after confirmation.  
- **Structured delivery**: Data notes → overview table → per-item details (including dimensions such as “content analysis”) → statistics; **order and block structure follow the script output for that run**, ready for topic selection and benchmarking.  
- **HTML / PDF**: In the full flow, HTML can match the number of items shown in the current conversation for sharing and archiving.  
- **Subscription prompt**: After pattern analysis, a fixed script may ask about subscribing to vertical pushes (handoff logic is defined in the in-package execution docs).  

**Who it’s for**

WeChat editors and operators, content planning and growth teams, and creators who need verifiable **100k+** article samples.

**Runtime**: Requires **Python 3**; the list-fetch script uses **`coze_workload_identity`** for requests (see `scripts/fetch_hot_articles.py`); the HTML script relies mainly on the standard library (see `scripts/generate_hot_html.py`). Triggered via natural language in an Agent client where this Skill is enabled.

---

## Features

### Core capabilities

- **Site-wide hot list (overall ranking)**: When users say things like “today’s viral hits,” “100k+,” or “latest viral list,” use date semantics such as **`daybeforeyesterday`** per package conventions for the overall list (**do not** use `yesterday` for “today / latest” overall-list scenarios).  
- **Domain queries**: Extract a domain keyword from user wording; shares the same **TOP50 + first-turn preview** pattern as the overall list; `start_date` may be a concrete date, `""` (roughly the last 30 days), or other agreed special values.  
- **Paged preview**: The first turn is commonly **preview + first 10 items**; if total rows exceed 10, you may prompt to continue; after user confirmation, use **full** mode to show everything.  
- **Artifacts**: Runs may produce **`temp_articles.json`** and **`{关键词}_热门榜单.html`** (filenames may carry semantic customizations; see actual execution).  

### Highlights

- **Output matches the script**: Lists and details in conversation should follow **`fetch_hot_articles.py` standard output** in full—avoid tables only, missing detail blocks, or rewriting fields.  
- **Pattern analysis comes last**: Viral pattern analysis should be written **after the full list is shown**, and must be based on **facts from the current list**—do not reuse example conclusions unrelated to this run.  
- **HTML row count alignment**: When generating HTML, **`--display_count`** must match the **number of items actually shown in this conversation** (e.g. 10 / 50 / actual N).  
- **Time semantics**: Spoken “today / latest” for the overall list vs. **scheduled subscription pushes** use different conventions for `daybeforeyesterday` / `yesterday` (see “Important data notes”).  

---

## Prerequisites

### Runtime and dependencies

- **Python**: Use a currently maintained version (whatever is installed on the machine).  
- **List-fetch script**: Depends on **`coze_workload_identity`** (see `import` and run notes in `scripts/fetch_hot_articles.py`).  
- **HTML script**: Mostly **Python standard library** (see `scripts/generate_hot_html.py`).  
- **Full step-by-step flow** (intent, parameter table, output templates, HTML/PDF visual rules, etc.): follow **`references/execution_workflow.md`** in the same directory; for request fields, see **`references/api-spec.md`**.  

---

## Usage guide

### How you can phrase it

| What you say | What you’ll roughly get |
| --- | --- |
| “Today’s viral hits,” “100k+,” “hot viral list” | Overall path: fetch with agreed date params; first turn often **previews first 10**, then pattern analysis and subscription prompt, and HTML generation |
| “Recommend 100k+ in the xx vertical” | Extract domain keyword; first turn also often previews **10** rows; you can expand the rest on prompt |
| “Show the next few dozen” / “show all” | After preview, **full** mode; conversation and HTML row counts align with **`--display_count`** |
| Vague phrasing like “show me what’s hot” | The assistant may ask for a domain keyword, or proceed with the overall list after consent |

### Tips

- When you need **strict step order** (including subscription wording and when to generate HTML), have the executor read **`references/execution_workflow.md`** together with the “core execution rules” in the root **`SKILL.md`**.  
- **“Today / latest” overall list** vs. **subscription pushes** use different conventions for special date values (`daybeforeyesterday` / `yesterday`); do not mix them.  
- If there is **no data** for a domain or date, report honestly and suggest a hotter domain keyword—**do not invent article rows**.  

---

## Use cases

| Scenario | Best for | What you get |
| --- | --- | --- |
| **Track site-wide trends** | WeChat editors | Same-day–scope 100k+ sample list and shareable HTML |
| **Vertical topic selection** | Content planners | High-read articles by domain keyword and structured body text usable for title teardown |
| **Client or internal dashboards** | Growth / ops leads | List layout matching conversation + a page exportable to PDF (subject to browser and html2pdf.js) |
| **Steady cadence reference** | Ops collecting subscription interest | After pattern analysis, ask about subscription with fixed wording; whether real push is enabled depends on the product |

---

## Important data notes

**Sync and snapshot**

- List refresh is commonly described as around **19:30 daily** (see the “data notes” copy at the top of the script); what you see is a **snapshot at fetch time** and may differ from live reads.  
- Coverage is commonly **about the last 30 days**; beyond that, the API or script truncates or errors per rules.  

**`start_date` semantics (must match the script and execution docs)**

| Value | Meaning (user-facing) |
| --- | --- |
| `daybeforeyesterday` | For user-initiated **overall list** “today / latest” scenarios: maps to the calendar day before yesterday as `YYYY-MM-DD` to align with library sync cadence |
| `yesterday` | **Mainly for scheduled subscription push** scenarios (distinct from overall-list “today / latest”) |
| `YYYY-MM-DD` | A single user-specified day |
| `""` | No single-day filter; domain queries often mean roughly the last 30 days |

---

## Notes and limitations

- This Skill provides **data and layout reference**—not advice to inflate reads, buy traffic, or break platform rules.  
- **Do not** fabricate lists without actually running the script; **do not** show only the table and omit detail blocks from script output.  
- **Pattern analysis** must come after the full text is shown, and must not substitute example articles from docs or old conversations for real data this run.  
- **HTML generation** in the common flow should follow the docs after the subscription question; **`--display_count`** must match how many rows were shown in the conversation.  
- Output paths and filenames (e.g. `temp_articles.json`, `*_热门榜单.html`) depend on the runtime—back up if you need to keep copies.  

---

## FAQ

**Q: When the user says “today’s viral hits,” which special value should `start_date` use?**  
A: For the overall list, use **`daybeforeyesterday`**; do not use **`yesterday`** as a stand-in for “today / latest” overall list.

**Q: How are dates chosen for subscription pushes?**  
A: For scheduled push, follow the execution doc and use **`yesterday`**, distinct from the overall-list rule above.

**Q: Can I show only the overview table and skip per-item details?**  
A: **No.** Present every block from standard script output in original order in full.

**Q: The JSON has 50 rows but the conversation only showed 10—how many rows should HTML use?**  
A: **10**; `--display_count` follows the **number of rows actually shown in the conversation**.

**Q: What if there’s no data?**  
A: Say no relevant 100k+ data was found and suggest a hotter domain keyword—**do not** fabricate articles.

---

## Changelog / version notes

- **v1.2.1**: Execution details moved to `references/execution_workflow.md`; `SKILL.md` front adds a required-reading index; `source` fixed value aligned with script defaults.  
- **v1.2.0**: Restructured doc like “WeChat viral article query” style; merged resource index and notes while keeping execution constraints and parameters.  
- **Earlier versions**: Overall vs. domain queries, preview/full, HTML+PDF, subscription prompts, etc., evolved in repo history (see commits).  
