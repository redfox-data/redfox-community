---
name: gzh-astock-top
description: A股公众号大V工具，输入日期获取A股领域公众号大V账号30个及账号数据（平均阅读、红狐指数等），同时获取每个账号最新一篇文章及文章数据。当用户提到"A股公众号"、"股市大V"、"A股账号"、"股票公众号榜单"、"A股公众号大V"时使用。
dependency:
  python:
    - 无第三方依赖（纯标准库：urllib.request, json, os, sys, argparse, datetime）
---

# A股公众号大V

## 1. 简介

A股公众号大V工具，输入日期获取A股领域30个公众号大V的账号数据与最新文章数据。帮助用户快速掌握A股领域头部公众号的运营表现和最新内容动向。

> API 请求均携带 `A股公众号大V-GitHub` 标识。使用环境变量 `REDFOX_API_KEY` 鉴权。

---

## 2. 功能特性

- **固定账号池**：覆盖19个个人大V + 30个官媒/机构，共49个A股头部公众号
- **账号数据**：获取每个账号的平均阅读数、红狐指数、账号描述等核心指标
- **当日文章**：获取每个账号在指定日期发布的最新文章，含标题、链接、阅读数、点赞、评论等互动数据
- **双分类模式**：官媒/机构 + 个人大V 两类分开展示，各类最多30个
- **AI概要**：基于文章标题自动生成1句话内容概要
- **标题跳转**：文章标题渲染为超链接，点击可跳转原文
- **订阅推送**：按序号订阅账号，每日只查订阅列表，减少API调用

---

## 3. 鉴权配置

### 获取 API Key

请前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 获取 API Key。

### 配置方式

| 方式 | 命令 |
|------|------|
| 环境变量（推荐） | `export REDFOX_API_KEY=ak_你的密钥` |
| 命令行参数 | `--api-key ak_你的密钥` |
| 配置文件 | `echo '{"api_key":"ak_你的密钥"}' > ~/.qoder/apis/redfox.json` |

---

## 4. 使用指南

### 基础使用

**Step 1 — 确认日期**：从用户输入中提取查询日期。未指定日期时默认为今天。

**Step 2 — 调用脚本**：

```bash
python3 "$SKILL_PATH/scripts/fetch_astock_accounts.py" --date <日期> --dual-category
```

- 指定日期：`--date 2026-06-15`
- 默认今天：`python3 "$SKILL_PATH/scripts/fetch_astock_accounts.py" --dual-category`
- 仅查个人大V（不分类）：`python3 "$SKILL_PATH/scripts/fetch_astock_accounts.py" --date 2026-06-15`

**⚠️ 防重复调用规则（强制）**：

- ❌ **禁止**先用 `head`/`tail` 等方式"试运行"脚本
- ❌ **禁止**在同一次查询中对同一参数多次调用脚本
- ✅ **每次查询只执行一次脚本命令**，直接读取完整输出

**Step 3 — 查看结果**：脚本返回结构化 JSON 数据，按本指南规定的展示策略输出结果。

---

### 数据展示策略

**⚠️ 强制输出规则**：

- ✅ 必须严格按照本步骤规定的格式输出
- ❌ 禁止在输出前添加任何分析或解读
- ❌ 禁止自作主张给建议或方案
- ✅ 直接读取脚本返回的 JSON 数据，按照对应策略输出

#### 前置说明（展示数据前必须告知用户）

- **数据说明**：账号数据来源于红狐API收录的公众号信息，文章数据为账号在**指定日期**发布的作品（由服务端直接筛选）。互动数据截止为入库时间，非实时数据。
- **排序说明**：账号按平均阅读数降序排列

#### 默认查询行为

- 用户未指定日期时，**默认查询当天**（如 2026-06-17）
- 默认使用 `--dual-category --count 120` 模式，同时输出官媒和大V两类
- 若用户仅说"看看A股大V"或"查查今天的"，直接运行双分类查询

#### 数据充足（accounts ≥ 10）

展示内容：

1. **时间范围说明**：告知用户查询的日期
2. 账号与文章数据表格（含AI概要列）

**Markdown表格格式**：

📅 查询日期：2026-06-17

**【官媒/机构】X 个账号**

| # | 公众号 | 平均阅读 | 红狐指数 | 最新文章 | AI概要 | 阅读 | 点赞 | 发布 |
|---|-------|---------|---------|---------|--------|------|------|------|
| 1 | 金融时报 | 3.2w | 937.1 | [重磅会议明天见](url) | 聚焦即将召开的重要经济会议，预判政策方向 | 8.3w | 109 | 06-16 |

**【个人大V】X 个账号**

| # | 公众号 | 平均阅读 | 红狐指数 | 最新文章 | AI概要 | 阅读 | 点赞 | 发布 |
|---|-------|---------|---------|---------|--------|------|------|------|
| 1 | 大红好运哥 | 7.1w | 862.0 | [太强了！！！](url) | A股强势突破，博主情绪极度乐观 | 7.2w | 1939 | 06-15 |

**格式规范**：

- 第一列为序号，从1开始递增
- 平均阅读数 ≥ 10000 时显示为 `x.xw` 格式
- **最新文章标题**：必须渲染为超链接，`[标题](workUrl)`。标题超过15字截断加 `...`。无 workUrl 时仅显示纯文本
- **AI概要**：基于文章标题，用1句话（≤30字）概括文章核心内容/观点，由AI在展示时推断生成，不依赖API
- 发布时间仅显示月-日

#### 数据不足（accounts < 10）

展示内容：

1. **时间范围说明**
2. **提示信息**："💡 当前日期仅找到 X 个A股领域大V账号，数据可能不完整"
3. 正常数据表格（含AI概要列）

#### 无数据（accounts = 0）

```
🔍 抱歉，当前日期未找到A股领域的公众号大V数据，请尝试更换日期或稍后重试。
```

**输出规则**：

- ✅ 必须直接输出上述格式内容
- ❌ 禁止添加额外的分析或建议
- ❌ 禁止解释为什么没有数据

---

## 5. 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--date` | 查询日期 YYYY-MM-DD | 今天 |
| `--api-key` | 指定 API Key | — |
| `--dual-category` | 分类模式：官媒/机构 + 个人大V 两类分别展示 | — |

---

## 5.5 订阅管理功能

### 功能说明

支持从榜单中按序号订阅官媒或大V账号，每次调用订阅推送时只查询已订阅账号的最新文章，减少不必要的API调用。

> **数据更新时间**：红狐平台每日 **07:00** 更新昨日爆款文章数据，建议 **07:30** 之后运行推送查询。

### 工作流程

```
Step 1: 运行榜单查询（--dual-category）→ 展示官媒/大V榜单（含序号）
Step 2: 用户输入序号 → 调用 manage_subscriptions.py 写入订阅
Step 3: 每日调用 fetch_subscribed_updates.py → 查询订阅账号最新文章
```

### Step 1: 展示榜单（AI触发）

当用户说"看看榜单并订阅"时：

```bash
python3 "$SKILL_PATH/scripts/fetch_astock_accounts.py" --date <日期> --dual-category
```

> 此命令同时将结果缓存至 `cache/last_dual_result.json`，供订阅时使用。

### Step 2: 添加订阅（AI根据用户序号调用）

**从官媒榜单订阅序号 1、3、5：**
```bash
python3 "$SKILL_PATH/scripts/manage_subscriptions.py" --action add --category official --indexes 1,3,5 --from-cache
```

**从大V榜单订阅序号 2、4：**
```bash
python3 "$SKILL_PATH/scripts/manage_subscriptions.py" --action add --category kol --indexes 2,4 --from-cache
```

**查看当前所有订阅：**
```bash
python3 "$SKILL_PATH/scripts/manage_subscriptions.py" --action list
```

**删除订阅（按账号名）：**
```bash
python3 "$SKILL_PATH/scripts/manage_subscriptions.py" --action remove --names 央视财经,金融时报
```

**清空某类订阅：**
```bash
python3 "$SKILL_PATH/scripts/manage_subscriptions.py" --action clear --category official
```

### Step 3: 每日推送（AI触发）

当用户说"看订阅账号更新"或"推送今日更新"时：

```bash
# 全部订阅
python3 "$SKILL_PATH/scripts/fetch_subscribed_updates.py"

# 只查官媒
python3 "$SKILL_PATH/scripts/fetch_subscribed_updates.py" --category official

# 只查大V
python3 "$SKILL_PATH/scripts/fetch_subscribed_updates.py" --category kol
```

### 订阅推送输出展示规范

脚本返回JSON，AI按以下格式展示：

**数据说明**：订阅账号最新文章数据，近7天内发布。互动数据截止入库时间，非实时。

📅 日期：2026-06-17 · 数据更新时间：每日 07:00

**【官媒/机构订阅】X 个账号**

| # | 公众号 | 最新文章 | AI概要 | 阅读 | 点赞 | 发布 |
|---|-------|---------|--------|------|------|------|
| 1 | 央视财经 | [一张电影票正在变成什么？](链接) | 聚焦电影票消费趋势与院线转型 | 2.5w | 216 | 06-16 |

**【个人大V订阅】X 个账号**

（同格式）

> 注：文章标题必须渲染为超链接 `[标题](workUrl)`；AI概要由AI基于标题推断生成；无文章数据时显示 `-`。

### 目录结构（更新）

```
gzh-astock-top/
├── SKILL.md
├── subscriptions.json          # 订阅配置（官媒/大V账号ID列表）
├── cache/
│   └── last_dual_result.json   # 最近一次双分类榜单缓存
├── scripts/
│   ├── fetch_astock_accounts.py      # 榜单查询（--dual-category 时自动缓存）
│   ├── manage_subscriptions.py       # 订阅管理（添加/删除/查看）
│   └── fetch_subscribed_updates.py   # 订阅推送（查询已订阅账号最新文章）
└── references/
    └── api_guide.md
```

---

## 6. 项目架构

### 目录结构

```
gzh-astock-top/
├── SKILL.md                          # Skill 定义与使用文档（本文件）
├── scripts/
│   └── fetch_astock_accounts.py      # 核心脚本：获取A股大V账号及文章数据
└── references/
    └── api_guide.md                  # API接口说明文档
```

### 技术栈

| 组件 | 技术 | 说明 |
| ---- | ---- | ---- |
| 运行环境 | Python 3.13+ | 纯标准库，无第三方依赖 |
| 标准库 | urllib.request, json, os, sys, argparse, datetime | HTTP请求、JSON处理、参数解析、日期计算 |
| 数据接口 | 红狐 API (Redfox) — dailyPublish 接口 | 通过 REDFOX_API_KEY 鉴权，**1次调用**获取全部数据 |
| 输出格式 | JSON (stdout) | 供 AI 解析后以 Markdown 表格展示 |

### 核心模块说明

| 模块 | 路径 | 功能 |
| ---- | ---- | ---- |
| 数据获取脚本 | `scripts/fetch_astock_accounts.py` | 调用 dailyPublish 接口，1次获取49个固定账号当日文章数据 |
| API参考文档 | `references/api_guide.md` | 详细说明接口地址、参数、返回字段 |

### 资源索引

- **核心脚本**：`scripts/fetch_astock_accounts.py` — 单次调用 dailyPublish 接口获取A股大V数据，参数：--date（可选）、--dual-category（可选）、--api-key（可选）
- **参考文档**：`references/api_guide.md` — 何时读取：需要了解接口数据格式、字段说明时

---

## 7. 常见问答

**Q: 为什么有些账号没有当日文章？**
A: dailyPublish 接口按指定日期筛选，若账号当天未发布文章则不返回，因此不同日期的结果账号数量会有差异。

**Q: 账号数量不足怎么办？**
A: 固定49个账号中，只有当日有发布文章的账号才会出现在结果中。如数量较少，可能是当天发布频率低，属正常现象。

**Q: 数据更新频率？**
A: 红狐平台每日 **07:00** 更新前一日数据，建议 07:30 后查询昨日日报。

**Q: 脚本报错怎么办？**
A: 常见原因：(1) REDFOX_API_KEY 未配置或已过期；(2) Python 版本 < 3.13；(3) 网络问题。请逐一排查。
