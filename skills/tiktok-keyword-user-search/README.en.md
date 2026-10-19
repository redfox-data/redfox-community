# TikTok Keyword User Search / tiktok-keyword-user-search

---

## Overview

Search TikTok users by nickname or handle, and view the following list of any specified account to analyze the profile of accounts it follows. The two capabilities can be chained together—search first, then look up the following list—all in a single conversation.

**Core Value**

- **Locate users by keyword**: Find target accounts on TikTok by nickname or handle, and view profile details such as fans, follows, total likes, works, and verification.
- **View following list**: Look up the accounts a specified user follows, and learn about the followed accounts' profiles and verification backgrounds.
- **Chained workflow**: Search to identify an account first, then look up its following list—no need to manually copy user IDs; complete both queries in one round.

**Intended Users**

- 🔍 **TikTok content researchers** — Investigate account follower counts, activity levels, and verification backgrounds to support topic selection and benchmarking.
- 📊 **Influencer screening / competitor analysis** — Batch-locate influencers by keyword, or analyze same-niche operational moves through following lists.
- 🧑‍💼 **Brands / MCNs evaluating partnerships** — Assess account fit and follow profiles to judge collaboration potential.

---

## Features

### Core Capabilities

- **Keyword user search**: Search accounts on TikTok using nickname or handle, and output a user list (with fans, follows, total likes, and works count).
- **Following list query**: Look up the accounts a specified user follows via a user ID, and output the followed accounts' nicknames, Handles, fans, works, total likes, region, and verification info.
- **Chained query**: Even if you only provide a nickname or handle, you can look up their follows; search to locate the account first, confirm, then look up its following list.
- **Filters and sorting**: Filter by follower tier (under 1K, 1K–10K, 10K–100K, 100K+) or verified-only accounts; search results are sorted by follower count descending by default.
- **Pagination**: Both search and following list support fetching more results, initiated by you on demand.

---

## API Key Acquisition & Security

- This skill requires the environment variable: `REDFOX_API_KEY`.
- `REDFOX_API_KEY` is issued by [RedFoxHub](https://redfox.hk/settings/api-keys?source=github) (`https://redfox.hk`).
- Register at [RedFoxHub](https://redfox.hk?source=github) to obtain `REDFOX_API_KEY`.
- Configure `REDFOX_API_KEY` on your device before using this skill.
- Before providing your key, confirm its source, scope, validity period, and whether it can be reset or revoked.
- Do not hard-code or expose keys in plain text in code, prompts, logs, or output files.

---

## Usage Guide

Simply describe your query in natural language—no commands to memorize.

### Quick Reference

| Intent               | Example phrase                              | Result                                                              |
| -------------------- | ------------------------------------------- | ------------------------------------------------------------------- |
| Search accounts                        | "Search TikTok users named Nanxun"             | Output candidate account list (with fans, follows, likes, works)   |
| Find a specific account             | "Help me find the account solid.guts"         | Precisely locate the account by handle                              |
| View following list                 | "Show me who this TikTok user follows"        | Output followed accounts list (with fans, works, likes, verification) |
| Chained query                       | "Look up solid.guts's following list"         | Locate the account via search, then look up its following list     |
| Filter by follower count            | "Only accounts that have 100k+ followers"      | Filter search results by follower tier                             |
| Continue to next page               | "Next page"                                   | Continue fetching more search results or earlier follow records    |

### Output Example

**Search result**:

```
keyword:`Nanxun` | offset:0 | count:3 | hasMore:1 | cursor:20
Get API Key: visit [RedFoxHub](https://redfox.hk/settings/api-keys?source=github)

| #  | Name    | Handle        | userId              | Fans | Follows | Likes  | Works |
|---:|---------|---------------|---------------------|-----:|--------:|-------|----------:|
| 1  | Nanxun  | user976316235 | 6802494138883802114 |   47 |      69 |     0 |      0 |
```

**Following list**:

```
target:`userId:6748953635118187521` | minTime:0 | count:2 | hasMore:1
Get API Key: visit [RedFoxHub](https://redfox.hk/settings/api-keys?source=github)

| #  | Name      | Handle         |   Fans | Works |     Likes | Region | Verification               |
|---:|-----------|----------------|-------:|------:|----------:|--------|------------------------|
| 1  | user12... | user120317...  | 100,404 |   143 |   227,161 | US     | -                          |
| 2  | Li Ziqi   | cnliziqi       |3,754,224|   785 |31,904,748 | US     | Original Food Vlog Creator  |
```

---

## Use Cases

| Scenario               | Role                  | Example question                                          | Benefit                                                          |
| ---------------------- | -------------------- | ----------------------------------------------- | ---------------------------------------------------------------- |
| Influencer screening   | Brand / MCN          | "Find me TikTok beauty accounts with 100k+ followers"        | Quickly lock in candidate influencers                            |
| Following analysis     | Operations / researcher | "Show me this account's following list"                      | Understand same-niche follow trends                               |
| Account research       | Content research     | "Search for AI-related users"                                | Pull related accounts for horizontal comparison                   |
| Chained query          | Influencer ops       | "Look up solid.guts's following list"                        | Complete "locate account → view follows" in one conversation      |

---