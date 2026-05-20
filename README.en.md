<p align="right">
  <a href="https://github.com/redfox-data/redfox-community/blob/main/README.md">中文</a>
  English
</p>

# redfoxdata · Agent Skills

This repository hosts **Agent Skills** maintained by the **redfoxdata** community for inspiration, topic research, copywriting, and data review workflows. Each skill is centered on `SKILL.md` and works with tools that support Agent Skills, such as Cursor and Claude Code.

## Repository layout

```text
.
├── README.md          # Chinese README
├── README.en.md       # This file (English)
├── skills/            # One skill per subdirectory
│   └── <skill-name>/
│       ├── SKILL.md
│       └── …          # Optional scripts, references, assets
```

## Skill directory conventions

Each skill lives in its **own subdirectory** and must include at least:

| File       | Purpose                                                                   |
| ---------- | ------------------------------------------------------------------------- |
| `SKILL.md` | Skill entry: YAML frontmatter + body (triggers, steps, constraints, etc.) |

We recommend clear frontmatter in `SKILL.md` for discovery and platform import, for example:

```yaml
---
name: Example Skill
description: One sentence on when to use the skill and what it does (be specific).
---
```

Optional folders such as `references/`, `scripts/`, and `assets/` may sit next to `SKILL.md`; keep each skill self-contained and use relative paths.

## How to use

### Local / Cursor

Copy the skill folder you need into your client’s skills directory (e.g. Cursor user skills or project `.cursor/skills/`—follow your client’s docs), or point the client’s “Add skill” flow at that subdirectory.

### skills cli

Run the following in an interactive terminal (you can copy as-is):

```bash
npx skills init // install skills cli
npx skills add redfox-data/redfox-community
```

Follow the prompts to install skills into a specific agent folder or globally.

### SkillHub

Open SkillHub and install by searching for the **Chinese display name** of the skill under `skills/`:

https://skillhub.cn/skills

**Search examples:** `公众号爆款文章查询` or `抖音每日最具影响力账号`

### ClawHub (`clawhub`)

Browse and install from the official redfox-data profile on ClawHub:

https://clawhub.ai/user/redfox-data

## Contributing

Issues and pull requests are welcome for new skills or fixes.

1. Fork this repository
2. Add or edit a subdirectory under `skills/`
3. Ensure `SKILL.md` stands alone, steps are actionable, and dependencies/risks are documented
4. Open a pull request with a short note on motivation and use cases

## License

Unless stated otherwise, the default license is **[MIT](LICENSE)** (or replace with your chosen license here). If a skill bundles third-party assets or another license, note it inside that skill’s directory.

---

**redfoxdata** — Turn repeatable new-media workflows into shareable, evolvable Agent skills.
