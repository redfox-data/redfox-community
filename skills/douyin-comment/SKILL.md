---
name: douyin-comment
description: 抖音评论分析工具。输入作品链接即可获取一级评论数据，支持分页浏览、评论情感分析（积极/负面/需求/竞品），生成精美 HTML 报告。当用户需要查看抖音作品评论、分析评论舆情、了解用户反馈时使用。触发词：抖音评论、作品评论、评论查询、评论分析、评论舆情、看评论。
---

# 抖音评论分析

## 📝 简介

输入抖音作品链接即可获取一级评论数据，每页 20 条，支持分页翻页。在对话中展示当前页全部评论及 AI 总结分析，同时生成包含当前页数据和总结的交互式 HTML 报告。

## ✨ 功能特性

| 功能模块 | 能力描述 | 核心价值 |
|---------|---------|---------|
| 评论获取 | 粘贴作品链接即可获取评论 | 拉取作品评论区最新数据 |
| 分页浏览 | 每页 20 条，支持翻页 | 逐页浏览大量评论 |
| AI 总结 | 四维情感分析（积极/负面/需求/竞品） | 快速了解评论舆情全貌 |
| 置顶标记 | 置顶评论特殊标识 | 一眼识别重要评论 |
| HTML 报告 | 深色主题交互式报告 | 离线保存/分享分析结果 |

## 🔑 鉴权

- 获取 API Key：前往 [红狐hub](https://redfox.hk/settings/api-keys?source=github)
- 配置方式1：写入 `~/.openclaw/openclaw.json` → `{ "env": { "REDFOX_API_KEY": "ak_xxxx..." } }`
- 配置方式2：终端执行 `export REDFOX_API_KEY="ak_xxxx..."`

## 🔄 工作流程

### Step 1：理解用户意图，提取 videoId

**⚠️ 核心规则：必须从用户输入中提取 videoId。**

- 用户可能直接提供 videoId（纯数字）
- 用户可能提供作品链接（如 `https://www.douyin.com/video/7131700643076623629`），从链接中提取 videoId
- 若用户未提供作品链接，主动询问：「请提供抖音作品链接」
- 若用户在上一轮对话中查询过某作品的数据，且本轮输入模糊（如"下一页"、"评论分析"），沿用上一轮的 videoId

### Step 2：调用评论获取脚本（自动生成 HTML）

**⚠️ 每次调用仅请求一页数据（一次 API 请求），不可擅自发起多次调用拉取多页。**

**脚本每次调用自动生成 HTML 报告**（含 `{{PLACEHOLDER}}` 占位符，未回填分析数据）。终端展示与 HTML 基于**同一次 API 调用**，确保数据一致。

```bash
python3 ~/.agents/skills/douyin-comment-search/scripts/douyin_comment_search.py "<videoId>" [--offset <offset>]
```

**参数说明：**

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `videoId` | 抖音作品 ID（必填） | — |
| `--offset` | 偏移量，每页 20 条 | `0` |
| `--output-dir` | HTML 输出目录 | `~/Downloads/QoderReports` |

**offset 与页码对应关系：**

| 页码 | offset |
|------|--------|
| 第 1 页 | 0 |
| 第 2 页 | 20 |
| 第 3 页 | 40 |
| ... | offset = (page - 1) × 20 |

脚本返回 JSON：

| 字段 | 说明 |
|------|------|
| `video_id` | 作品 ID |
| `current_page` | 当前页码 |
| `total_fetched` | 本次获取的评论数 |
| `has_next` | 是否有下一页（true/false） |
| `comments` | 评论列表 |
| `html_path` | 生成的 HTML 报告路径（含占位符，待回填） |

每条评论字段：

| 字段 | 说明 |
|------|------|
| `comment_id` | 评论 ID |
| `content` | 评论内容 |
| `like_count` | 点赞数 |
| `reply_count` | 回复数 |
| `create_time` | 评论时间 |
| `ip_location` | IP 属地 |
| `user_name` | 用户昵称 |
| `user_avatar` | 用户头像 URL |
| `user_id` | 用户 ID（用于生成主页链接） |
| `user_url` | 用户主页链接 |
| `is_top` | 是否置顶（true/false） |

> **注意：** HTML 报告此时仅含评论原始数据，分析占位符（`{{PLACEHOLDER}}`）待用户确认后回填。

### Step 3：对话中展示评论数据 + AI 总结

**⚠️ 每次操作仅调用一次 API，获取一页数据。对话展示与 HTML 报告基于同一页数据。**

#### A1. 告知查询范围

> 📊 作品「**{videoId}**」共获取 **N 条**评论（第 {page} 页），以下是详细数据：

#### A2. 渲染评论表格（展示当前页全部评论）

```markdown
| # | 评论人 | 评论内容 | 👍 | 💬 | 时间 | IP |
|---|--------|---------|----|----|------|-----|
| 1 | ![avatar](头像URL)[昵称](主页链接) | 评论内容... | 1223 | 213 | 02-12 15:30 | 广东 |
| 2 | ![avatar](头像URL)[昵称](主页链接) | 评论内容... | 856 | 45 | 02-12 14:20 | 北京 |
| ... | ... | ... | ... | ... | ... | ... |
```

**格式规则：**
- 评论人列使用 `![avatar](头像URL)[昵称](user_url)` Markdown 格式，无需设置图片尺寸
- 评论内容超过 40 字截断加 `...`
- 时间格式化为 `MM-DD HH:MM`
- 置顶评论在昵称后加 `📌` 标记（整个评论行使用 **加粗** 样式）
- `like_count` / `reply_count` 数字 ≥ 10000 使用 `x.xw` 格式
- ⚠️ 每页最多 20 条，对话中全部展示，不得截断

#### A3. AI 评论总结（⚠️ 每次查询（含翻页）必须输出）

基于当前页获取到的全部评论，进行四维情感分析。**分析前需理解抖音梗文化**（流行语、缩写、表情包语义、热门话题背景）。

> ## 📈 评论总结分析（基于 {total} 条评论）
>
> ### ✅ 积极评价（{positive_ratio}%）
> - {要点1}
> - {要点2}
> - ...
>
> ### ⚠️ 负面评价（{negative_ratio}%）
> - {要点1}
> - {要点2}
> - ...
>
> ### 💡 用户需求（{demand_ratio}%）
> - {要点1}
> - {要点2}
> - ...
>
> ### 🔍 竞品对比舆情（{competitor_ratio}%）
> - {仅当评论中提及竞品时输出，否则输出「未提及竞品」}
> - {竞品名称}：{舆情要点}

**分析要求：**
- 每条要点需引用代表评论（截取关键词/短语）
- 百分比为提及该类型评论的数量占总评论数的比例
- 积极/负面/需求/竞品四类占比总和可能超过 100%（一条评论可能同时包含多类信息）
- **必须理解抖音梗文化**：识别流行语（如"绝绝子""yyds""破防""入典"等）、表情包语义、缩写（如"xswl""awsl"）、梗的语境含义

#### A4. 翻页提示（⚠️ 紧接在 A3 之后，每次必须输出）

- 若 `has_next` 为 true：
> 📄 当前第 **{page}** 页（共 {total_fetched} 条）。回复「下一页」继续查看。

- 若 `has_next` 为 false：
> 📄 当前第 **{page}** 页，已无更多数据。

**⚠️ A1~A4 必须在同一轮输出中连续完成，不可省略任何一步。**

A4 输出完毕后，**询问用户是否需要生成 HTML 可视化报告**：

> 📊 是否需要生成 HTML 可视化报告？

**若用户回复「是」「需要」「生成」「html」等确认词**，则执行以下步骤（**无需重新调用脚本**，HTML 文件已在 Step 2 生成）：

**① 回填 AI 分析结果到 HTML**

调用 `backfill_html.py` 将 AI 分析结果回填到 HTML 中的 `{{PLACEHOLDER}}` 占位符：

```bash
python3 ~/.agents/skills/douyin-comment-search/scripts/backfill_html.py "<html_path>" --analysis-json '{
  "positive_ratio": <正整数>,
  "negative_ratio": <正整数>,
  "demand_ratio": <正整数>,
  "competitor_ratio": <正整数>,
  "positive_summary": "<ul><li>要点1</li><li>要点2</li>...</ul>",
  "negative_summary": "<ul><li>要点1</li><li>要点2</li>...</ul>",
  "demand_summary": "<ul><li>要点1</li><li>要点2</li>...</ul>",
  "competitor_summary": "<ul><li>要点1</li><li>要点2</li>...</ul>"
}'
```

**JSON 字段说明：**

| 字段 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `positive_ratio` | int | 积极评价占比（纯数字，不含%） | `45` |
| `negative_ratio` | int | 负面评价占比 | `30` |
| `demand_ratio` | int | 用户需求占比 | `15` |
| `competitor_ratio` | int | 竞品对比占比 | `15` |
| `positive_summary` | string | 积极评价摘要（HTML 格式 `<ul><li>...</li></ul>`） | 见示例 |
| `negative_summary` | string | 负面评价摘要 | 同上 |
| `demand_summary` | string | 用户需求摘要 | 同上 |
| `competitor_summary` | string | 竞品对比摘要 | 同上 |

**注意：** JSON 字符串参数包含双引号，Bash 中使用单引号包裹，内部双引号需转义 `\"`。若内容含单引号则用 stdin 方式传入：`echo '...' | python3 backfill_html.py "<html_path>"`

**② 打开 HTML 报告：**

```bash
open "<html_path>"
```

### Step 4：翻页处理（用户回复「下一页」等时）

当用户回复「下一页」「上一页」「第 N 页」时：

1. 沿用 Step 1 中提取的 videoId
2. 计算新的 offset：`(page - 1) × 20`
3. 重新调用脚本（**与 Step 2 一致，自动生成 HTML**）：`python3 .../douyin_comment_search.py "<videoId>" --offset <offset>`
4. **完整执行 Step 3 的 A1~A4**（每页独立展示 + AI 分析）
5. A4 后询问用户是否需要生成当前页 HTML（同 Step 3 末尾流程，**无需重新调用脚本**）

**翻页规则：**
- `has_next` 为 true → 当前页正好 20 条，存在下一页
- `has_next` 为 false → 当前页不足 20 条，已是最后一页

### Step 5：错误处理

| 错误类型 | 处理方式 |
|---------|---------|
| 无 API Key | 提示配置 REDFOX_API_KEY，给出配置指引 |
| 作品链接无效 | 提示「未找到该作品的评论，请检查作品链接是否正确」 |
| 接口返回错误 | 显示错误码和错误信息 |
| 获取 0 条评论 | 提示「该作品暂无评论」并建议检查作品是否存在或已删除 |
| 网络请求超时 | 提示「网络请求超时，请稍后重试」 |

---

## 📋 依赖

```bash
# 脚本使用 urllib（Python 标准库），无需额外安装依赖
```

---

## 🎯 使用示例

**示例 1：查看指定作品的评论**
```
用户：查看抖音作品 7131700643076623629 的评论
助手：调用脚本（自动生成HTML） → 展示全部20条 + AI总结 → 询问是否需要HTML → 用户确认 → backfill → open
```

**示例 2：通过链接查询**
```
用户：https://www.douyin.com/video/7131700643076623629 这篇的评论怎么样
助手：提取 videoId → 调用脚本 → 展示分析 → 询问是否需要HTML
```

**示例 3：翻页**
```
用户：下一页
助手：调用脚本 offset=20 → 展示第2页 + AI分析 → 询问是否需要当前页HTML
```
