---
name: kuaishou-comment
description: 快手评论分析工具。输入作品链接即可获取一级评论数据，支持分页浏览、评论情感分析（积极/负面/需求/竞品），生成精美 HTML 报告。当用户需要查看快手作品评论、分析评论舆情、了解用户反馈时使用。触发词：快手评论、作品评论、评论查询、评论分析、评论舆情、看评论。
---

# 快手评论分析

## 📝 简介

输入快手作品链接即可获取一级评论数据，每页 20 条，支持 cursor 游标分页翻页。在对话中展示当前页全部评论及 AI 总结分析，同时生成包含当前页数据和总结的交互式 HTML 报告。

## ✨ 功能特性

| 功能模块 | 能力描述 | 核心价值 |
|---------|---------|---------|
| 评论获取 | 粘贴作品链接即可获取评论 | 实时拉取作品评论区数据 |
| 分页浏览 | 每页 20 条，cursor 游标翻页 | 逐页浏览大量评论 |
| AI 总结 | 四维情感分析（积极/负面/需求/竞品） | 快速了解评论舆情全貌 |
| 置顶标记 | 置顶评论特殊标识 | 一眼识别重要评论 |
| HTML 报告 | 深色主题交互式报告 | 离线保存/分享分析结果 |
| 合并报告 | 多页合并，超3页自动折叠 | 一次导出全部评论分析 |

## 🔑 鉴权

前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github) 获取 API Key，通过以下方式配置：

```bash
# 方式一：配置文件（如 OpenClaw 的 ~/.openclaw/openclaw.json）
{ "env": { "REDFOX_API_KEY": "ak_xxxx..." } }

# 方式二：终端环境变量
export REDFOX_API_KEY="ak_xxxx..."
```

## 🔄 工作流程

### Step 1：理解用户意图，提取 opusId

**⚠️ 核心规则：用户提供作品链接，Agent 从链接中提取 opusId。**

- 用户提供作品链接（如 `https://www.kuaishou.com/short-video/3x4ibfzs5e68yxu`），Agent 从链接中提取 opusId
- 用户也可能直接提供 opusId（如 `3x4ibfzs5e68yxu`），此时直接使用
- 若用户未提供作品链接，主动询问：「请提供快手作品链接」
- 若用户在上一轮对话中查询过某作品的数据，且本轮输入模糊（如"下一页"、"评论分析"），沿用上一轮的 opusId

### Step 2：调用评论获取脚本（自动生成 HTML）

**⚠️ 每次调用仅请求一页数据（一次 API 请求），不可擅自发起多次调用拉取多页。**

**脚本每次调用自动生成 HTML 报告**（含占位符，未回填分析数据）。终端展示与 HTML 基于**同一次 API 调用**，确保数据一致。

```bash
python3 ~/.agents/skills/kuaishou-comment/scripts/kuaishou_comment_search.py "<opusId>" [--cursor <cursor>] [--page <page>]
```

**参数说明：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `opusId` | 快手作品 opusId（必填） | — |
| `--cursor` | 游标，首页传空字符串，次页传上一页返回的 nextCursor | "" |
| `--page` | 当前页码（仅用于 HTML 文件名和输出标记） | 1 |
| `--output-dir` | HTML 输出目录 | ~/Downloads/QoderReports |

脚本返回 JSON 字段详见下方评论字段表。

> **注意：** HTML 报告此时仅含评论原始数据，分析占位符待用户确认后回填。

### Step 3：对话中展示评论数据 + AI 总结

**⚠️ 每次操作仅调用一次 API，获取一页数据。**

#### A1. 告知查询范围

> 📊 作品「**{opusId}**」共获取 **N 条**评论（第 {page} 页），以下是详细数据：

#### A2. 渲染评论表格（展示当前页全部评论）

**格式规则：**
- 评论人列只显示昵称，不展示头像、不生成超链接
- 评论内容超过 40 字截断加 ...
- 时间格式化为 MM-DD HH:MM
- 置顶评论在昵称后加 📌 标记（整行加粗）
- like_count / reply_count 数字 ≥ 10000 使用 x.xw 格式
- 每页全部展示，不得截断

#### A3. AI 评论总结（⚠️ 每次查询（含翻页）必须输出）

**首页**：基于当前页评论，四维情感分析。

**翻页后**：基于目前已获取的所有页面累计数据综合分析，标注累计总条数。

**分析前需理解快手社区文化**（老铁文化、表情符号语义、"奥利给""双击"等特有表达）。

> ## 📈 评论总结分析（基于 {total} 条评论）
>
> ### ✅ 积极评价（{positive_ratio}%）
> - {要点，引用代表评论关键词}
>
> ### ⚠️ 负面评价（{negative_ratio}%）
> - {要点}
>
> ### 💡 用户需求（{demand_ratio}%）
> - {要点}
>
> ### 🔍 竞品对比舆情（{competitor_ratio}%）
> - {仅当提及竞品时输出，否则输出「未提及竞品」}

**分析要求：**
- 每条要点引用代表评论关键词/短语
- 百分比为该类型评论占比，四类总和可能超 100%
- 必须理解快手社区文化

#### A4. 翻页提示（⚠️ 紧接在 A3 之后）

- 若 has_next 为 true：`📄 当前第 {page} 页（共 {total_fetched} 条）。回复「下一页」继续查看。`
- 若 has_next 为 false：`📄 当前第 {page} 页，已无更多数据。`

**⚠️ A1~A4 必须在同一轮输出中连续完成，不可省略任何一步。**

A4 输出完毕后，**询问用户是否需要生成 HTML 可视化报告**：

> 📊 是否需要生成 HTML 可视化报告？

**若用户确认**，根据已浏览页数选择方式：

---

#### 仅 1 页 → 单页 HTML（backfill_html.py）

HTML 文件已在 Step 2 生成，直接回填分析数据并打开：

```bash
python3 ~/.agents/skills/kuaishou-comment/scripts/backfill_html.py "<html_path>" --analysis-json '<分析JSON>'
open "<html_path>"
```

---

#### 2 页及以上 → 合并报告（consolidate_report.py）

收集所有已浏览页面的 JSON 数据，生成一份包含**全部评论和累计分析**的完整 HTML。按页码分区展示，**超过 3 页时自动折叠**，提示用户点击展开。

```bash
python3 ~/.agents/skills/kuaishou-comment/scripts/consolidate_report.py "<opusId>" \
  --pages-json '[{"page":1,"total":31,"comments":[...]},{"page":2,"total":20,"comments":[...]}]' \
  --analysis-json '<累计分析JSON>'
open "<html_path>"
```

| 参数 | 说明 |
|------|------|
| opusId | 快手作品 opusId（位置参数） |
| --pages-json | 多页数据 JSON 数组，每项含 page、total、comments |
| --analysis-json | 累计分析 JSON（字段同 backfill） |

> pages 数据从各次脚本调用输出中收集；累计分析基于 A3 翻页后综合分析。

---

**分析 JSON 字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| positive_ratio | string | 积极评价占比（纯数字，如 "62"，模板自动追加 %） |
| negative_ratio | string | 负面评价占比 |
| demand_ratio | string | 用户需求占比 |
| competitor_ratio | string | 竞品对比占比 |
| positive_summary | string | 积极评价摘要（HTML ul 格式） |
| negative_summary | string | 负面评价摘要 |
| demand_summary | string | 用户需求摘要 |
| competitor_summary | string | 竞品对比摘要 |

### Step 4：翻页处理（用户回复「下一页」等时）

1. 沿用 opusId
2. 使用上一页的 nextCursor
3. 重新调用脚本：`python3 ~/.agents/skills/kuaishou-comment/scripts/kuaishou_comment_search.py "<opusId>" --cursor "<nextCursor>" --page <page>`
4. 完整执行 A1~A4，A3 基于累计综合分析
5. A4 后询问是否需要 HTML

**翻页规则：** has_next true → 用 nextCursor 翻页；false → 已无更多。cursor 原样传递，不可修改。

### Step 5：错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 无 API Key | 提示配置 REDFOX_API_KEY |
| 作品链接无效 | 提示「未找到该作品的评论，请检查作品链接是否正确」 |
| 接口返回错误 | 显示错误码和错误信息 |
| 获取 0 条评论 | 提示「该作品暂无评论」 |
| 网络请求超时 | 提示「网络请求超时，请稍后重试」 |

---

## 📋 依赖

脚本使用 urllib（Python 标准库），无需额外安装依赖。

---

## 🎯 使用示例

**示例 1：查看指定作品的评论**
```
用户：查看快手作品 3x4ibfzs5e68yxu 的评论
助手：调用脚本 → 展示当前页 + AI总结 → 询问HTML → backfill → open
```

**示例 2：通过链接查询**
```
用户：https://www.kuaishou.com/short-video/3x4ibfzs5e68yxu 这个作品的评论怎么样
助手：提取 opusId → 调用脚本 → 展示分析 → 询问HTML
```

**示例 3：翻页后合并导出**
```
用户：下一页 → 下一页 → 生成html
助手：收集3页JSON → consolidate_report.py → 1个HTML含全部评论+折叠 → open
```
