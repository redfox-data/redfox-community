---
name: tiktok-keyword-user-search
description: TikTok 账号搜索与关注列表查询工具。基于红狐数据，通过昵称或 handle 在 TikTok 上定位目标账号，查看粉丝、作品、获赞与认证等画像；也可查询指定账号关注的账号列表，分析其关注对象情况。两个能力可串联使用，先搜账号再查关注。适用于搜索 TikTok 用户、查看某账号关注了谁、调研关注对象画像等场景。触发词：TikTok搜用户、TikTok找账号、TikTok关注列表、TikTok关注了谁。
version: 1.0.0
display_name: TikTok关键词搜用户
display_name_en: TikTok Keyword User Search
description_zh: 基于红狐数据按关键词搜索TikTok用户，并查看指定账号关注的账号列表与关注对象画像
description_en: Search TikTok users by keyword and view the following list of a specified account, with profile insights on the followed accounts.
category: social-media
author: 红狐数据
---
# TikTok关键词搜用户

> 两个能力：① 按关键词搜索 TikTok 用户（可先定位目标账号的 userId）；② 按 userId / secUserId 查询用户的关注列表；两者可链式串联，一次对话完成"搜索定位 → 查关注列表"。

---

## 使用引导

### ① 关键词搜索用户（searchUser）

- **能做什么**：按昵称 / handle 搜索 TikTok 账号，返回 userId、粉丝数、关注数、获赞、作品数
- **你需要提供**：昵称或 handle 关键词；可选筛选：粉丝数区间、仅认证账号
- **触发示例**：「搜一下 TikTok 上叫南浔的用户」「帮我找 solid.guts 这个账号」
- **输出内容**：用户列表表格（序号、昵称、Handle、userId、粉丝、关注、获赞、作品）+ 翻页/链式查询引导

### ② 关注列表查询（userFollowing）

- **能做什么**：查询某个 TikTok 账号关注了哪些账号，输出关注对象画像
- **你需要提供**：该账号的纯数字 userId 或 `MS4wLjAB` 开头的 secUserId
- **触发示例**：「查 userId 6748953635118187521 的关注列表」
- **输出内容**：关注对象表格（序号、昵称、Handle、粉丝、作品、获赞、地区、认证）+ 翻页提示

### 链式查询（推荐新用户从这里开始）

只有昵称或 handle、没有 userId 时，按此流程一次对话闭环：

1. 直接说「查 solid.guts 的关注列表」→ 技能先搜索定位该账号，列出候选（含 userId、粉丝数）
2. 你确认目标（精确匹配唯一时可直接确认）→ 技能查询其关注列表并输出

### 前置凭证

需配置环境变量 `REDFOX_API_KEY`（前往 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 注册获取，格式 `ak_xxxxxxxx`）。每次成功查询可能消耗积分，默认只查一页；翻页需明确指示「下一页」；查询无结果时不改查其他目标。

---

## 触发场景

当用户提出以下需求时使用本 Skill：

**关注列表查询（userFollowing）**

- "查一下这个 TikTok 用户关注了谁"
- "TikTok 关注列表"
- "查询某账号的 following 列表"
- "分析某 TikTok 账号的关注对象"

**关键词搜索用户（searchUser）**

- "搜一下 TikTok 上叫 xxx 的用户"
- "帮我找到 solid.guts 这个账号的 ID"
- "TikTok 上做 xxx 的账号有哪些"

**链式查询**：用户只给昵称/handle 想查关注列表时，先搜索定位目标（得到 userId），确认后查其关注列表。

注意：关注列表接口只接受 `userId`（纯数字）或 `secUserId`（MS4wLjAB 开头），不接受 @handle 昵称；用户只给 handle 时先用关键词搜索定位，搜索结果无匹配时不改查其他关键词。

---

## 数据说明

### 输出内容

**关注列表（userFollowing）**

- **关注列表**：以 Markdown 表格输出，含序号、昵称、Handle、粉丝、作品、获赞、地区、认证
- **私密标注**：`isSecret=1` 的关注对象在昵称后追加"（私密）"
- **固定提醒**：输出中附带 API Key 获取提醒

**用户搜索（searchUser）**

- **用户列表**：以 Markdown 表格输出，含序号、昵称、Handle、userId、粉丝、关注、获赞、作品
- **userId 列固定输出**：供链式查询关注列表直接使用
- **筛选**：支持粉丝数区间（0~1K / 1K~10K / 10K~100K / 100K以上）与仅认证账号

### 排序与口径

- 关注列表默认按接口原始顺序输出（即关注时间从近到早）；用户指定时可按粉丝数、作品数、获赞本地降序
- 用户搜索默认按粉丝数降序输出；`--sort none` 保留接口原始相关度顺序
- 只展示接口返回的字段；接口未返回的字段（如主页地址）不构造输出，不补造头像、视频等详情信息

---

## 一键安装

### 前置条件

- Python 3.8+（仅使用标准库，无需安装额外依赖）
- 红狐数据 API Key（前往 [红狐 hub](https://redfox.hk/settings/api-keys?source=github) 注册获取）

### 安装步骤

1. 将技能文件夹放入你的 Skills 目录
2. 配置环境变量 `REDFOX_API_KEY`（配置细节详见 `references/core_workflow.md`）
3. 无需安装额外依赖，直接使用

---

## 工作流程

> 核心执行流程（意图识别、脚本调用、翻页规则、表格渲染、空结果与错误处理等）详见 `references/core_workflow.md`，Agent 执行时必须遵循该文件中的所有规则。完整字段说明见 `references/api-spec.md`。

---

## 使用指南

直接用自然语言描述查询需求，无需记忆命令。

| 意图 | 示例话术 | 效果 |
| ---- | -------- | ---- |
| 查关注列表 | 「查一下 userId 6748953635118187521 的关注列表」 | 输出关注对象列表（按关注时间倒序） |
| 搜索用户 | 「搜一下 TikTok 上叫南浔的用户」 | 输出用户列表（默认按粉丝数降序，含 userId） |
| 筛选搜索 | 「搜 xxx，只看 10 万粉以上的账号」 | 按粉丝区间筛选用户 |
| 指定排序 | 「按粉丝数排序看看他关注了哪些大号」 | 改为粉丝数降序输出 |
| 指定条数 | 「只看前 10 个关注」 | 只展示前 10 条 |
| 链式查询 | 「查 solid.guts 的关注列表」 | 先搜索定位 userId，确认后查关注列表 |
| 继续翻页 | 「下一页」 | 关注列表用返回的 `minTime` / `pageToken` 续查；用户搜索用返回的 `cursor` 续查 |

---

## 注意事项

1. **数据真实性**：所有数值均来自数据服务返回，如实展示，严禁估算或编造；接口未返回的字段（如主页地址）不构造输出
2. **查询无果不替换**：任一能力返回空列表时只输出"暂无数据"及可能原因（如关注数为 0、ID 有误、账号私密、关键词无匹配），不主动改查其他用户或关键词
3. **积分保护**：每次成功查询可能消耗积分；默认只查一页，未经用户明确要求不主动翻页；链式查询（搜索→关注列表）涉及两次独立调用，搜索结果需先向用户确认目标后再查关注列表
4. **鉴权**：首次使用需配置环境变量 `REDFOX_API_KEY`，API Key 获取与配置详见 `references/core_workflow.md`
