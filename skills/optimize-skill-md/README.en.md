# SKILL.md Structural Optimizer / optimize-skill-md

---

## Introduction

A one-click tool that audits and optimizes any SKILL.md against the *Skills MD Standard Format*, covering description quality, section structure, content conciseness, and formatting consistency — making skill documentation more standardized and easier for Agents to match accurately.

**Core Value**

- **Better Descriptions**: Automatically fixes the YAML description to include third-person phrasing, WHAT + WHEN context, and trigger keywords, improving Agent trigger accuracy.
- **Clear Structure**: Enforces the standard opening sections (Introduction + Features), restructures/merges/removes empty sections for a clean document hierarchy.
- **Lower Token Cost**: Strips redundant explanations and filler text, keeping the main body within 500 lines.

**Ideal For**

- 🛠️ **Skill Developers** — Quickly bring hand-written or legacy SKILL.md files up to standard without manual checklist review.
- 📦 **Skill Maintainers** — Batch-normalize terminology, formatting, and section structure across an entire skill library.
- 🆕 **New Skill Authors** — Get structural guidance on first write, avoiding common anti-patterns.

---

## Features

### Core Capabilities

- **YAML Description Fix**: Auto-completes third-person descriptions, trigger scenarios, and trigger keywords within a 1024-character limit.
- **Section Restructuring**: Enforces the standard opening (📝 Introduction + ✨ Features), merges short sections, splits long sections, and removes empty sections.
- **Redundancy Removal**: Strips background knowledge explainers, repeated statements, and filler phrases while preserving core business rules and constraints.
- **Format Normalization**: Unifies terminology across the document, labels code blocks with language types, uses forward-slash paths, and aligns tables.
- **Progressive Refactoring**: Suggests moving detailed content to a `references/` directory when the file exceeds 500 lines, keeping the main body lean.

---

## Usage Guide

Simply describe your optimization need in natural language — no commands to memorize.

### Common Phrases

| Intent | Example Prompt | Result |
|--------|---------------|--------|
| Optimize a specific skill | "Optimize the SKILL.md for my xxx skill" | Reads the target SKILL.md, evaluates all dimensions, and outputs an optimized version |
| Check format compliance | "Check if this SKILL.md meets the standard format" | Audits each dimension and lists issues with fix suggestions |
| Fix the description field | "The description is too vague, fix it" | Rewrites in third-person + WHAT + WHEN + trigger keyword format |

---

## Use Cases

| Scenario | Role | Example Prompt | Benefit |
|----------|------|---------------|---------|
| New skill first-pass review | Skill Developer | "I just finished writing SKILL.md, check and optimize it" | Meets standards before first submission, reducing rework |
| Legacy skill batch cleanup | Skill Maintainer | "These old skills need a unified format" | Batch-aligns to standards, lifting overall library quality |
| Description field targeted fix | Skill Developer | "The description has low trigger rate, optimize it" | Adds trigger keywords, boosting Agent match accuracy |
| Documentation slimming | Skill Developer | "SKILL.md exceeds 500 lines, help me trim it" | Moves detailed content out, keeping the main body lean and manageable |

---
