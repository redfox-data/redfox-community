# Xiaohongshu niche viral rankings / xhs-breaking-rankings

---

## Introduction

This Skill delivers **Xiaohongshu low-follower, high-engagement note rankings**: filter notes with **followers under 5,000 and engagement over 500** by category and date, then return a benchmark list, pattern breakdown, and a visual HTML pack—so you can spot rising hits before big creators dominate the feed.

**Core value**

- **Low-follower viral filter**: more actionable than copying mega accounts.  
- **25 categories**: colloquial keywords map to standard verticals.  
- **Auto pattern breakdown**: title traits, themes, and reusable highlights from the list.  
- **Dual output**: Markdown table + HTML file pack; **TOP 20** first, up to **TOP 50** on “show more.”  
- **Optional subscription**: daily push at a fixed time (product-dependent).  

**Who it’s for**

New creators benchmarking, brand operators tracking trends, MCN scouts, and content teams doing vertical research.

**Runtime**: **Python 3**; install **`requests>=2.28.0`** (per skill `dependency`). No Xiaohongshu account or API key required. Trigger via natural language in an Agent with this Skill enabled.

---

## Features

### Core capabilities

- **Category + date queries**: specific dates, colloquial dates (“today”), or auto date when omitted (**19:30** rule).  
- **Full deliverable**: viral table, pattern analysis, subscription prompt, and HTML pack in the expected order.  
- **Structured table**: rank, note info, total engagement, likes/comments/saves/shares, publish time.  
- **Show more**: often 20 rows first; ask for more up to **50** per query.  

### Highlights

- **Flexible dates**: `YYYY-MM-DD` or script-computed “latest available” before/after **19:30**.  
- **Low setup**: Python deps only for the main path.  
- **No silent date hopping**: if a date is empty, follow the prompt—don’t auto-switch dates without you.  

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
| “Niche viral in beauty on 2026-04-20” | That day’s list + patterns + subscription + HTML |
| “Today’s / day-before-yesterday travel niche viral” | Colloquial date resolved, then query |
| “Show more” | Remaining rows for this query (up to ~50) |
| “Subscribe” / reply **1** | Daily push (often **19:30** TOP 50, product-dependent) |
| “Unsubscribe” | Turn off daily push |

### Tips

- The Agent may ask for **date** or **category** before the first run.  
- Common criteria text: **followers &lt; 5,000, likes &gt; 500** (per run output).  
- You see formatted results, not script paths or source code.  

---

## Use cases

| Scenario | Best for | What you get |
| --- | --- | --- |
| **New creator benchmarks** | Low-follower creators | Same-niche small-account viral samples |
| **Brand trend tracking** | Brand XHS ops | Recent keywords and formats in a vertical |
| **Talent scouting** | MCN | High-engagement emerging accounts |
| **Team research** | Planner / ops | Multi-day, multi-category pattern material |

---

## Important data notes

**Filter criteria**

- Rows typically meet: **followers &lt; 5,000**, **likes &gt; 500** (per API/script; wording on output may vary).  

**Updates and dates**

- Data often updates on a **daily 19:30** cadence for the prior day.  
- **No date given**: after **19:30** → previous day; before **19:30** → two days back (script-computed).  
- Display is a snapshot at query time, not live engagement.  

---

## Notes and limitations

- Rankings and patterns are **reference only**, not a traffic guarantee.  
- Don’t auto re-query other dates when empty—confirm with you first.  
- Subscription availability and timing depend on the product.  
- Follow Xiaohongshu rules; links and accounts follow returned data.  

---
