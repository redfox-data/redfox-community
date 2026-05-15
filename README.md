# redfoxdata · Agent Skills

本仓库收录 **redfoxdata** 社区维护的多枚 Agent 技能（Skill），面向灵感、选题、文案创作、数据复盘等场景。技能以 `SKILL.md` 为核心，可与 Cursor、Claude Code 等支持 Agent Skills 的工具配合使用。

## 仓库结构

```text
.
├── README.md          # 本说明
├── skills/         # 中文技能（每个子目录一枚技能）
│   └── <skill-name>/
│       ├── SKILL.md
│       └── …          # 脚本、参考文档等（可选）
```

## 技能目录约定

每个技能是一个**独立子文件夹**，且至少包含：

| 文件       | 说明                                                              |
| ---------- | ----------------------------------------------------------------- |
| `SKILL.md` | 技能入口：YAML frontmatter + 正文（触发条件、步骤、约束、示例等） |

建议在 `SKILL.md` 的 frontmatter 中提供清晰元信息，便于检索与导入平台识别，例如：

```yaml
---
name: Example Skill
description: 一句话说明技能适用场景与能力边界（建议具体，避免空泛）。
---
```

可选：`references/`、`scripts/`、`assets/` 等，与 `SKILL.md` 同目录存放，保持单技能自包含、路径相对引用即可。

## 如何使用

### 本地 / Cursor

将需要的技能目录复制到你所用工具的 skills 目录（例如 Cursor 的 user skills 或项目内 `.cursor/skills/` 等，以你当前客户端文档为准），或通过客户端提供的「添加技能」入口指向该子文件夹。

### SkillHub

首先在终端执行命令安装SkillHub CLI：

```bash
curl -fsSL https://skillhub.cn/install/install.sh | bash
```

安装完成后：

```bash
skillhub install <skill-slug>
```

### Skhub（`skhub`）

```bash
skhub add <owner>/<skill-slug>
```

也可在可交互终端下从 GitHub 导入整仓后勾选技能（以官方 CLI 文档为准）：

```bash
skhub add https://github.com/<owner>/<repo>
```

### ClawHub（`clawhub`）

```bash
clawhub install <skill-slug>
```

## 参与贡献

欢迎通过 Issue / Pull Request 贡献新技能或修正现有技能。

1. Fork 本仓库
2. 在 `skills/` 下新增或修改对应子目录
3. 确保 `SKILL.md` 可独立理解、步骤可执行、依赖与风险有说明
4. 发起 Pull Request，并在描述中简要说明变更动机与适用场景

## 许可证

如无特殊说明，默认采用 **[MIT](LICENSE)**（或在此处写明你实际选择的许可证）。若某技能含第三方素材或不同许可证，请在该技能目录内单独注明。

---

**redfoxdata** — 将可重复的新媒体工作流沉淀为可分享、可演进的 Agent 技能。
