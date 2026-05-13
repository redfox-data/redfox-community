# Xiaohongshu (RED) content generation / xhs-copywriter

---

## Introduction

**xhs-copywriter** targets steady Xiaohongshu output: it strings **find benchmarks → extract patterns → write the body** into one pipeline—**fetch** hot samples by keyword, distill reusable structure, then output publish-ready combinations such as title, body, and tags (counts and layout follow the runtime workflow).

**Core value**

- **Multi-dimensional samples**: Reference dimensions such as low-follower high likes, same-day likes, same-day growth, sustained growth (see `references/core_workflow.md`).  
- **From patterns to copy**: Extract points from title, opening, pacing, and engagement design, then generate full note copy.  
- **Traceable sources**: Results include reference note links and data notes (patterns can be verified).  

**Who it’s for**

Individual creators, brand operators, MCNs, and others who need steady Xiaohongshu note copy. Full steps and prohibitions are in **`references/core_workflow.md`**.

**Runtime**: **Python 3**; the fetch script is **`scripts/fetch_xhs_trends.py`** in the repo (implementation uses the standard-library network stack where applicable; if `requests` is not required, follow the script’s actual imports).

---

## Features

### Core capabilities

- **Multi-dimensional viral data**: Covers multiple list dimensions to widen sample coverage (details in workflow).  
- **Viral formula extraction**: Decompose title patterns, opening structure, pacing, engagement design; show distilled conclusions to the user, not raw giant tables.  
- **Full copy output**: Multiple suggested titles, body, tag list, and formula provenance (counts and structure per workflow).  
- **Hot-topic blending**: Where the flow allows, blend recent industry trends and hot words (per actual execution).  

### Highlights

- **Style adaptation**: You may provide short writing samples as tone reference.  
- **Low setup**: In typical deployments, main path runs via conversation + script (auth and network depend on environment).  
- **Verifiable conclusions**: Output includes reference links and data source notes.  

---

## Prerequisites

### Runtime and dependencies

- **Python 3** (version per your machine).  
- Before using **`scripts/fetch_xhs_trends.py`**, read **`references/core_workflow.md`** for parameters, display limits (e.g. `--max-items`), and rules such as not exposing raw data tables directly to the user.  

---

## Usage guide

### How you can phrase it

| What you say | What you’ll roughly get |
| --- | --- |
| “Help me write a Xiaohongshu note about summer sunscreen” | Topic confirmation → fetch & patterns → title + body + tags, etc. |
| “Find viral notes for [topic]” | Use that topic as keyword to fetch samples and show distilled conclusions |
| “Analyze viral patterns in [vertical]” | Structured pattern summary for that vertical |
| “Generate copy for [topic] direction” | Same class as “write a note”; slightly vague topic input is OK |

### Tips

- You can paste a few paragraphs you usually write so tone stays closer.  
- The workflow requires **not dumping raw viral data tables** on the user—only conclusions and usable copy.  
- If the API fails or samples are thin, say so honestly—**no fabricated** note titles or engagement numbers.  

---

## Use cases

| Scenario | Role | Need | How to use |
| --- | --- | --- | --- |
| New creator finding direction | 0-follower beginner | Don’t know what to write; big accounts feel hard to copy | Enter a vertical keyword; get imitable structure and copy |
| Daily topics + fast output | Blogger / operator | Steady weekly output; slow ideation | Each time, state the topic; get a full draft |
| Brand riding trends | Brand operator | Need seeding that fits hot topics | Trigger with product selling points; blend recent hot words (data-grounded) |
| MCN batch production | MCN team | Many accounts, differentiated | Trigger multiple topics in sequence; mind compliance and differentiated wording |
| Pattern research | Content strategy | Understand what structures work in a vertical | Ask to “analyze viral patterns in the XX vertical” |

---

## Notes and limitations

- **End-to-end**: In the standard flow the executor completes steps such as “fetch → patterns → hot words → generate”; the user drives in natural language.  
- **Data and compliance**: Content must follow Xiaohongshu community rules; avoid risky wording such as illicit redirects or false claims (human review still recommended).  
- **Raw data**: Do not spread full raw scrape tables to end users—only distilled results and usable copy.  
