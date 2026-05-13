# WeChat Official Account viral article discovery / gzh-explosive-content-detector

---

## Introduction

This Skill targets **WeChat Official Account topic selection and creation**: it probes recent high-heat articles by keyword, filters with dimensions such as **low-follower high reads, read ranking, growth in progress, original ranking**, outputs a small set of high-quality recommendations in forms including **HTML**, and suggests **sub-track keywords** you can dig into next.

**Core value**

- **Keyword probing**: Query matching viral content by track or niche terms.  
- **Smart filtering**: From candidates, pick **at most 10** recommendations combining intent and relevance.  
- **Dual presentation**: Markdown cards + HTML grid cards for reading and sharing.  
- **Niche guidance**: After results, append about **10** niche terms for the next query round.  

**Who it’s for**

WeChat operators and editors, content creators, MCNs, and growth teams. Generic-word handling, script order, and fixed wording must follow **`references/gzh_explosive_content_workflow.md`** and **`SKILL.md`**.

**Runtime**: **Python 3**; **`requests>=2.28.0`** (see `SKILL.md` frontmatter).

---

## Features

### Core capabilities

- **Viral article discovery**: Site-wide hot list (empty keyword) and keyword queries.  
- **Time window**: Default **last 7 days**; up to about **30 days** (per script and workflow).  
- **Generic-word handling**: For broad category words, show niche suggestions first and wait for “expand / don’t expand”—**do not** run the script again in the same turn.  
- **Artifacts**: Commonly `{keyword}_爆款数据.html`; if the script outputs JSON, it can inform filtering.  

### Highlights

- **Intent first**: Prefer niche directions from the user’s wording; avoid one-shot queries with overly broad terms only.  
- **Data honesty**: Not a live snapshot; for asks like “today” or “beyond ~30 days,” use **fixed boundary wording** (see “Important data notes”).  
- **No padding**: At most 10 items; if fewer than 10, show honestly—**no fabrication**.  
- **Presentation closure**: Each item includes a recommendation reason (length and empty-phrase limits in `SKILL.md`); append niche-word guidance at the end.  

---

## Prerequisites

### Dependencies

- **Python 3** (version per your machine).  
- **Python package**: `requests>=2.28.0`.  

```bash
pip install "requests>=2.28.0"
```

---

## Usage guide

### How you can phrase it

| What you say | What you’ll roughly get |
| --- | --- |
| “What’s viral lately,” “show me site-wide hot” | Keyword `""` for site-wide hot → cards and HTML → niche track words |
| “What’s viral in workplace / emotions” (broad) | Niche list first and wait for “expand / don’t expand”—**no script this turn** |
| “Workplace communication tips,” “parenting topic ideas” | Treated as niche terms; script query can run directly |
| “xxx for the last ~15 days” | Map spoken range to `startDate = today − N days`, then query |

### Tips

- **Generic words must be asked before querying**: After niche suggestions, **stop the script for this turn** and wait for the user reply before calling again.  
- **When to pass empty keyword**: When the user gives **no track or topic** and only vaguely wants viral / hot content, pass `""` for site-wide.  
- **Empty data**: Prompt to try a hotter track keyword—**do not** force unrelated keywords or wrongly trigger the generic flow.  

---

## Use cases

| What users may ask | Assistant behavior (summary) |
| --- | --- |
| “What’s viral lately,” “show site-wide hot” | Keyword `""`, site-wide hot with default time window |
| “What’s viral in workplace / emotions” (broad) | Generic flow: niche words + wait for “expand / don’t expand” |
| “Workplace communication tips,” “parenting topics” | Treated as niche terms; script can be called directly |
| “xxx for the last ~15 days” | Map `startDate`, then query |
| “Want high likes / shares” | Intent treated as data-driven; filtering favors engagement |

---

## Important data notes

**Time and freshness**

- Engagement data is a snapshot **near fetch time** and may grow afterward.  
- Default range: **last 7 days**; if data is thin, the window may **auto-expand** and the user is informed per rules.  

**Boundary wording (must match `SKILL.md`; use verbatim when executing)**

- User mentions “today”: **「非常抱歉，今天的数据暂未更新，已为您展示最近可用的数据」**  
- User asks beyond ~30 days: **「非常抱歉，当前仅支持最近30天的数据，已为您展示最接近的数据」**  

---

## Notes and limitations

- **Data truth**: Shown content must match script results—**no fabricated** recommendation reasons or metadata.  
- **Compliance**: Follow platform and advertising rules; mind boundaries for niche suggestions and quoted body text.  
- **Scope**: Does not replace platform review; double-check before publishing.  

---

## FAQ

**Q: User only says “workplace”—can I query directly?**  
A: **No.** Run generic-word expansion first and wait for “expand / don’t expand”; no script in the same turn.

**Q: When is the keyword empty?**  
A: When the user gives **no track or topic** and only vaguely wants viral / hot, pass `""` for site-wide.

**Q: What if data is empty?**  
A: Say the keyword may be too cold and suggest a hotter track—**do not** switch to unrelated keywords or wrongly trigger generic expansion.

---

## Changelog / version notes

- **v1.1.1**: Aligned with original execution logic; restored fixed wording, filter steps, and “expand = comma-separated multi-keyword” constraints.  
- **v1.1.0**: Restructured doc; merged duplicate data and presentation notes.  
- **v1.0.0**: Viral discovery, generic-word handling, filtering, dual presentation, niche suggestions.  
