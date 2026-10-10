# TikTok Account Deep Analysis / tiktok-account-analyzer

---

## Introduction

Enter a TikTok account (profile link / @handle / secUserId / nickname) to get account basics, profile works and liked-works insights in one go: basics with followers, total likes, region and signature; works with plays, likes, comments, favorites, shares and work links — one account, three views at a glance.

**Key Value**

- 🎯 **One input, three ways to locate**: profile links, @handles and secUserIds locate directly; nicknames / keywords list candidates for confirmation first
- 📊 **Complete metrics**: followers / following / total likes / works + region / verification / signature; works with plays / likes / comments / favorites / shares
- 📐 **Six-dimension quantitative diagnosis**: 100-point score + four-tier grade, tier-adaptive benchmarks and six risk alerts in one view
- 🧭 **Liked-works insights**: see what the account likes and which creator circles it follows
- 🔗 **Direct links**: full clickable profile and work links for quick verification

**Who It's For**

- 🤝 **Brands / MCNs** — pre-collaboration creator due diligence on data performance and content style
- 🧑‍💻 **Content operators** — break down competitor content strategy and viral patterns
- ✍️ **Creators** — benchmark-account analysis to sharpen positioning and topic direction

---

## Features

### Core Features

- 🔍 **Locate accounts multiple ways**: profile links, @handles and secUserIds locate directly; nickname / keyword searches list candidates for confirmation
- 👤 **Account basics**: nickname, TikTok handle, followers, following, total likes, works, region, verification, signature and profile link
- 📊 **Profile works board**: plays, likes, comments, favorites, shares and publish time, newest first
- 🧡 **Liked-works insights**: works the account liked, with author, plays, likes and work links
- 🔗 **Full links**: complete clickable profile / work links for easy verification
- 📄 **Paged browsing**: profile-works paging is local slicing (zero cost); liked works page by cursor
- 📐 **Six-dimension quantitative diagnosis**: profile completeness / content productivity / engagement health / content quality / content trend / fan quality — 100-point score + four-tier grade + six risk alerts (zombie followers / inflated engagement / decline / shadow-ban / inactivity / single-video dependence), tier-adaptive benchmarks, rule-based offline computation at zero credit cost
- 🎯 **Top 3 viral works breakdown**: infer why works went viral based on content and performance
- 💡 **Liked-preference insights**: summarize the content types and creator circles the account likes
- 🔍 **Account diagnosis summary**: positioning, content strategy, data performance and commercial signals
- 📑 **HTML report**: generated with every analysis, including the six-dimension quantitative diagnosis, viral-works Top 3 breakdown and diagnosis summary, exportable as PDF / high-res image

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`)
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure the `REDFOX_API_KEY` environment variable on your device before using this skill.
- Before providing a key, confirm its source, scope, validity period, and whether it supports reset/revocation.
- Never hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## How to Use

Describe what you want in natural language — no commands to memorize.

### Quick Phrases

| Intent | Example | Result |
| ------ | ------- | ------ |
| Analyze a specific account | "Analyze this account" + profile link / @handle / secUserId | Outputs account basics, profile works board and liked-works insights |
| Creator due diligence | "Run due diligence on @tomcurtainofficial" | Basics + profile works + liked works in one go, with a quantitative diagnosis and diagnosis summary |
| Find account by nickname | "Analyze the account Tom Curtain" | Lists candidate accounts for confirmation, then continues the analysis |
| Quantitative diagnosis | "Score this account" / "Is this account worth a collab?" | Outputs the six-dimension diagnosis: overall score, dimension details and risk alerts |
| Profile works only | "See what this account has posted recently" | Outputs the profile works board with a Top 3 viral works breakdown |
| Liked works only | "See what this account likes" | Outputs liked-works insights with a liked-preference reading |
| Next page | "Next page" | Continues with the next page based on the previous page hints |
| Export report | "Export the report" | Provides an HTML report, exportable as PDF / high-res image |
| View raw data | "Show the raw response" | Outputs the raw data content |

### Sample Output

After a successful analysis, the basics and both works boards appear directly in the conversation as Markdown tables with AI analysis blocks, and an HTML report is generated alongside (illustrative):

> Account: `Tom Curtain Offical` (@tomcurtainofficial) | Basics: 9 items | Profile works: 10 | Liked works: 10

| Item | Value |
| ---- | ----- |
| Nickname | Tom Curtain Offical |
| TikTok Handle | @tomcurtainofficial |
| Followers | 1,234,567 |
| Total Likes | 23,456,789 |
| Works | 321 |
| Profile Link | [Open profile](https://www.tiktok.com/@tomcurtainofficial) |

| # | Publish Time | Work | Plays | Likes | Comments | Favorites | Shares | Work Link |
|---:|---|---|---:|---:|---:|---:|---:|---|
| 1 | 2026-10-05 | Work content summary… | 1,234,567 | 98,765 | 4,321 | 2,345 | 1,234 | [Open work](work link) |
| 2 | 2026-10-04 | Work content summary… | 987,654 | 76,543 | 3,210 | 1,987 | 876 | [Open work](work link) |

| # | Publish Time | Work | Author | Plays | Likes | Work Link |
|---:|---|---|---|---:|---:|---|
| 1 | 2026-10-05 | Work content summary… | CreatorA | 5,678,901 | 456,789 | [Open work](work link) |

```
🎯 Top 3 Viral Works Breakdown
1. **Work content summary…** published 2026-10-05 ｜ plays 1,234,567 ｜ likes 98,765
   Why it went viral (inferred): …… ｜ [Open work](work link)

💡 Liked-Preference Insights
1. Content type preference: ……
2. Creator circles followed: ……
3. Link to the account's own positioning: ……

📐 Six-Dimension Quantitative Diagnosis
Overall score: 79 / 100 (🟡 Normal account) ｜ Tier: B Mid-size (followers 64,350)

| Dimension | Score | Effective Full | Weight | One-line Comment |
|---|---:|---:|---:|---|
| Profile completeness | 5 | 8 | 10% | Missing signature |
| Content productivity | 9 | 15 | 15% | Few works; efficient; low frequency |
| Engagement health | 28 | 30 | 30% | Strong long tail (31.7); excellent (36.3%)… |
| Content quality | 18 | 20 | 20% | Excellent (viral rate 80.0%); even distribution… |
| Content trend | 10 | 15 | 15% | Sharp decline; even distribution… |
| Fan quality | 8 | 10 | 10% | Tier B; active fans (36.3%)… |

⚠️ Risk Alerts
- ⚠️ Decline alert (medium): recent mature works average plays below half of the earlier ones.

🔍 Account Diagnosis Summary
……

(The above is AI analysis and inference based on public data, for reference only.)
```

---

## Use Cases

| Scenario | Role | Example Query | Benefit |
| -------- | ---- | ------------- | ------- |
| Creator due diligence | Brand / MCN | "Run due diligence on @tomcurtainofficial — worth a collab?" | Grasp followers, works data and liked preferences in one go for partnership decisions |
| Competitor breakdown | Overseas brand | "Break down our competitor's TikTok content strategy" | See competitor viral patterns and content direction |
| Benchmark analysis | Creator | "Analyze this account and see what it posted recently" | Spot benchmark topics and data performance |
| Account evaluation | Content operator | "Check this account's followers and works data" | Quickly evaluate account scale and content health |

---

## Important Data Notes

- Each successful query may consume credits; a full analysis includes at most 3 data queries (search locate + profile works + liked works) — query as needed
- The six-dimension quantitative diagnosis and the HTML report are computed / generated locally offline at zero credit cost
- Profile works and liked works are shown newest first; the viral breakdown picks Top 3 by plays descending
- Nicknames / keywords may match multiple accounts — confirm the candidate account before analyzing
- Accounts with a private liked list may return no liked works; this is reported honestly
- The viral-works breakdown and diagnosis summary in the HTML report match the conversation output; both are AI analysis based on public data, clearly marked as inference and for reference only
- The six-dimension diagnosis uses initial TikTok-calibrated benchmarks that are refined as samples accumulate
